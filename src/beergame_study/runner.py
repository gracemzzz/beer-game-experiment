import asyncio, json, time, hashlib
from pathlib import Path
from dataclasses import asdict
import numpy as np
import pandas as pd
from .config import PROTOCOL, RATES
from .compatibility import decision_fingerprint, calibration_code_compatible
from .game import BeerGame, ROLES, demand_path, continuation, calibration_states
from .prompts import make_messages, rules_messages, validate_decision, SCHEMA, RULES, RULE_ANSWERS
from .api import Gateway, StudyStopped, GroupFailed, digest, save


def run_directory(root,config):
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}
    return Path(root)/'data/runs'/f'{config.stage}_{config.mode}_{digest(dict(config=config.scientific(),code=hashes,protocol=PROTOCOL))[:16]}'

async def collect(tasks):
    tasks=[asyncio.create_task(t) for t in tasks]
    results=await asyncio.gather(*tasks,return_exceptions=True)
    # Drain in-flight requests before propagating; preserve charges/checkpoints.
    for result in results:
        if isinstance(result,BaseException):raise result
    return results

async def decision(gateway,state,history,budget,identity):
    key=digest(identity)  # opaque label avoids revealing the condition name in task text
    # Offline decisions use the SAME deterministic rule in both conditions. No fabricated treatment effect.
    q=max(0,int(round(state['demand']+.35*(24-state['net_inventory']-.65*state['supply_line']))))
    plan=await gateway.request(dict(identity,stage='plan'),make_messages(state,history,budget,'plan',identity=key),
        budget,synthetic=f'Provisional order: {q}. Synthetic policy; not GPT reasoning.')
    if plan.get('refused') or (plan['response_status']!='completed' and
        not (plan['response_status']=='incomplete' and plan.get('incomplete_reason')=='max_output_tokens')):
        raise GroupFailed('Preparation refused or failed; raw response preserved.')
    # A truncated preparation is an intended deadline outcome. Never buy a fresh plan.
    answer=dict(order=q,**{'observed_'+k:state[k] for k in ('demand','inventory','backlog','supply_line')})
    final=await gateway.request(dict(identity,stage='final'),make_messages(state,history,budget,'final',plan['text'],key),
        gateway.config.final_tokens,SCHEMA,json.dumps(answer))
    try:answer=json.loads(final['text'])
    except (ValueError,TypeError):raise GroupFailed('Final response is not valid JSON; no fabricated order.')
    if final['response_status']!='completed' or final.get('refused') or not validate_decision(answer,state):
        raise GroupFailed('Final response failed format/readback checks; group recorded as failed.')
    if answer['order']>gateway.config.emergency_order_limit:
        raise StudyStopped('Emergency scale check: order exceeds 100,000. Raw order retained, game not mutated. Review protocol.')
    return dict(order=answer['order'],plan_tokens=plan['usage']['output_tokens'],
        final_tokens=final['usage']['output_tokens'],plan_truncated=plan['response_status']=='incomplete',
        plan_limit=budget,latency_s=plan['elapsed_s']+final['elapsed_s'])


async def calibrate(gateway,directory,config):
    states=calibration_states();rows=[]
    # Same hypothetical states at every allowance; independent calls, not a causal performance test.
    async def screen(label,budget):
        async def item(i,state):
            result=await decision(gateway,state,[],budget,dict(calibration=label,item=i,role=state['role']))
            return dict(screen=label,item=i,role=state['role'],inventory=state['inventory'],
                supply_line=state['supply_line'],**result)
        return await collect(item(i,state) for i,state in enumerate(states))
    reference_valid = False
    if config.calibration_method == 'percentile':
        rows.extend(await screen('reference',config.calibration_reference_tokens))
        ref=pd.DataFrame(rows)
        reference_valid=not bool(ref.plan_truncated.any())
        # Reference quantiles select candidates; a changed prompt can alter actual use.
        if config.mode=='api':
            short=max(16,int(np.floor(np.quantile(ref.plan_tokens,.25)/16)*16))
            adequate=max(short+16,int(np.ceil(np.quantile(ref.plan_tokens,.95)/16)*16))
            adequate=min(1024,adequate);short=min(short,adequate-16)
        else:short,adequate=config.short_tokens,config.adequate_tokens
    else:
        short,adequate=config.short_tokens,config.adequate_tokens
        if config.mode=='api':
            parent=Path(config.calibration_parent)
            if not config.calibration_parent or not (parent/'calibration_summary.csv').exists():
                raise StudyStopped('Fixed calibration requires its completed reference calibration folder.')
            previous=json.loads((parent/'manifest.json').read_text())
            previous_status=json.loads((parent/'progress.json').read_text())
            reference=pd.read_csv(parent/'calibration_summary.csv').set_index('screen')
            reference_valid=bool(previous['config']['mode']=='api' and previous_status['phase']=='complete'
                and previous['config']['model']==config.model and previous['protocol']==PROTOCOL
                and 'reference' in reference.index and reference.loc['reference','truncated_fraction']==0)
            if not reference_valid:
                raise StudyStopped('Parent reference calibration is incomplete, truncated or incompatible.')
    for label,budget in [('short',short),('adequate',adequate),('benchmark',2*adequate)]:
        rows.extend(await screen(label,budget))
        pd.DataFrame(rows).to_csv(directory/'calibration.csv',index=False)
    frame=pd.DataFrame(rows)
    pivot=frame.pivot(index='item',columns='screen',values='order')
    summary=frame.groupby('screen').agg(mean_tokens=('plan_tokens','mean'),
        truncated_fraction=('plan_truncated','mean'),mean_order=('order','mean')).reset_index()
    difference=float(np.median(abs(pivot.adequate-pivot.benchmark)))
    rates=summary.set_index('screen').truncated_fraction
    ready=bool(config.mode=='api' and reference_valid and rates['short']>=.20 and rates['adequate']<=.05
               and summary.set_index('screen').mean_tokens['adequate']>summary.set_index('screen').mean_tokens['short']
               and difference<=4)
    save(directory/'calibration_recommendation.json',dict(short_tokens=short,adequate_tokens=adequate,
        benchmark_tokens=2*adequate,median_absolute_adequate_benchmark_order_difference=difference,
        manipulation_screen_passed=ready,mode=config.mode,calibration_method=config.calibration_method,
        calibration_parent=config.calibration_parent,reference_screen_passed=reference_valid,
        note='Pilot thresholds, not validated psychometric cutoffs. No automatic main study.'))
    summary.to_csv(directory/'calibration_summary.csv',index=False)

async def check_rules(gateway, group_id, role, ledger, on_retry):
    """Same pre-game onboarding in both conditions. No retry adds decision tokens."""
    for attempt in range(gateway.config.rules_attempts):
        if attempt:on_retry()
        identity=dict(group=group_id,role=role,stage='rules',rules_attempt=attempt+1)
        response=await gateway.request(identity,rules_messages(role,retry=attempt>0),192,RULES,json.dumps(RULE_ANSWERS))
        try:answer=json.loads(response['text'])
        except (TypeError,ValueError):answer={}
        if not isinstance(answer,dict):answer={}
        errors=[key for key,value in RULE_ANSWERS.items() if answer.get(key)!=value]
        if set(answer)!=set(RULE_ANSWERS):errors.append('response_fields')
        if type(answer.get('order_fills_today')) is not bool or type(answer.get('objective_includes_continuation')) is not bool:
            errors.append('boolean_types')
        if response['response_status']!='completed' or response.get('refused'):errors.append('response_status')
        passed=not errors
        ledger.append(dict(group_id=group_id,role=role,attempt=attempt+1,passed=passed,
            failed_fields=errors,answer=answer))
        save(gateway.directory/'rules_validation.json',ledger)
        if passed:return
    failure=StudyStopped(f'Onboarding rules check stopped after {gateway.config.rules_attempts} attempts '
        f'for {group_id}/{role}: {", ".join(errors)}. See rules_validation.json. '
        'No game order was fabricated and no replacement group was started for this check.')
    gateway.fatal=failure
    raise failure


async def run(root,config,client=None,render=True):
    config.validate();directory=run_directory(root,config);directory.mkdir(parents=True,exist_ok=True)
    if config.mode=='api' and config.stage=='game':
        cp=Path(config.calibration_run)
        if not config.calibration_run or not (cp/'calibration_recommendation.json').is_file() or not (cp/'manifest.json').is_file():
            raise StudyStopped('Run API calibration first and set calibration_run to its folder.')
        rec=json.loads((cp/'calibration_recommendation.json').read_text())
        cm=json.loads((cp/'manifest.json').read_text())
        if not rec['manipulation_screen_passed'] or rec['mode']!='api':
            raise StudyStopped('Calibration has not demonstrated a binding/adequate contrast. Review its report before buying games.')
        if (cm['config']['model']!=config.model or cm['protocol']!=PROTOCOL or
            not calibration_code_compatible(cp,cm)):
            raise StudyStopped('Calibration model/protocol differs from the game.')
        if (config.short_tokens,config.adequate_tokens)!=(rec['short_tokens'],rec['adequate_tokens']):
            raise StudyStopped('Game token budgets must match the calibration recommendation.')
    if not (directory/'manifest.json').exists():
        save(directory/'manifest.json',dict(protocol=PROTOCOL,config=asdict(config),rates=RATES,
             decision_fingerprint=decision_fingerprint(),
             source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}))
    calibration_decisions=72 if config.calibration_method=='fixed' else 96
    started=time.monotonic();status=dict(phase='running',groups_complete=0,decisions=0,planned_decisions=(calibration_decisions if config.stage=='calibration' else
        config.groups_per_condition*8*(config.weeks-4)),mode=config.mode)
    total=2*calibration_decisions if config.stage=='calibration' else config.groups_per_condition*8*(1+2*(config.weeks-4)+int(config.collect_debriefs))
    handle=None
    if render:
        from IPython.display import display,HTML
        handle=display(HTML('Starting…'),display_id=True)
    gateway=Gateway(directory,config,client)
    def refresh():
        status.update(requests_done=gateway.finished,cached=gateway.cached,planned_requests=total,
            remaining_requests=max(0,total-gateway.finished),active=gateway.active,
            estimated_cost_usd=gateway.charged,allowance_usd=config.budget_usd,
            elapsed_s=time.monotonic()-started)
        save(directory/'progress.json',status)
        if handle:
            from html import escape
            from IPython.display import HTML
            handle.update(HTML(f'<b>{escape(status["phase"])}</b> <progress value="{gateway.finished}" max="{total}"></progress> '
                f'{gateway.finished}/{total} calls; {max(0,total-gateway.finished)} left; '
                f'{gateway.cached} cached; ${gateway.charged:.3f}/${config.budget_usd:.2f}; '
                f'{status["groups_complete"]} groups complete; active {gateway.active}'))
    gateway.callback=refresh
    async def heartbeat():
        while True:refresh();await asyncio.sleep(1)
    beat=asyncio.create_task(heartbeat());ledger=[];completed=[];partial=[];tails=[];rule_checks=[]
    try:
        if config.stage=='calibration':await calibrate(gateway,directory,config)
        else:
            def rules_retry():
                nonlocal total
                total+=1
                refresh()
            async def onboard(gid):
                await collect(check_rules(gateway,gid,role,rule_checks,rules_retry) for role in ROLES)
            async def group(block,condition):
                nonlocal total
                base=f'b{block:03d}_{condition}'
                budget=config.short_tokens if condition=='short' else config.adequate_tokens
                for replacement in range(config.group_replacements+1):
                    gid=base+(f'_replacement{replacement}' if replacement else '')
                    entry=dict(group_id=gid,block=block,condition=condition,replacement=replacement,status='running')
                    ledger.append(entry);save(directory/'group_attempts.json',ledger)
                    own=[];game=BeerGame();history=[[] for _ in ROLES]
                    try:
                        # Every original group was onboarded before any game was advanced.
                        if replacement:await onboard(gid)
                        for week,demand in enumerate(demand_path(config.weeks),1):
                            states=game.observe(demand)
                            if week<=config.warmup_weeks:
                                answers=[dict(order=4,plan_tokens=0,final_tokens=0,plan_limit=budget,plan_truncated=False,latency_s=0.) for _ in ROLES]
                            else:
                                answers=await collect(decision(gateway,state,history[i],budget,
                                    dict(group=gid,role=ROLES[i],week=week)) for i,state in enumerate(states))
                            game.commit([a['order'] for a in answers])
                            for i,(state,answer) in enumerate(zip(states,answers)):
                                row=dict(group_id=gid,block=block,condition=condition,replacement=replacement,
                                    phase='warmup' if week<=4 else 'agent',**state,**answer)
                                own.append(row);partial.append(row)
                                history[i].append(dict(week=week,demand=state['demand'],inventory=state['inventory'],
                                    backlog=state['backlog'],supply_line=state['supply_line'],order=answer['order'],shared_inventory=state['shared_inventory']))
                            pd.DataFrame(partial).to_csv(directory/'all_candidate_rounds.csv',index=False)
                        tail=continuation(game,demand,config.continuation_weeks)
                        tails.extend(dict(t,group_id=gid,block=block,condition=condition) for t in tail)
                    except GroupFailed as exc:
                        entry.update(status='failed',reason=str(exc));save(directory/'group_attempts.json',ledger)
                        if replacement==config.group_replacements:raise StudyStopped('Group replacement allowance exhausted: '+gid)
                        # Plan adjusts for requests never sent in an abandoned candidate.
                        sent=sum(1 for p in gateway.cache.glob('*.json') if json.loads(p.read_text())['identity'].get('group')==gid and json.loads(p.read_text())['status']=='ok')
                        total+=sent;refresh();continue
                    except BaseException:
                        entry['status']='stopped';save(directory/'group_attempts.json',ledger);raise
                    entry['status']='complete';completed.extend(own);status['groups_complete']+=1
                    save(directory/'group_attempts.json',ledger)
                    pd.DataFrame(completed).to_csv(directory/'rounds.csv',index=False)
                    pd.DataFrame(tails).to_csv(directory/'continuation.csv',index=False)
                    refresh();return
            schedule=[(b,c) for b in range(config.groups_per_condition) for c in ('short','adequate')]
            np.random.default_rng(config.seed).shuffle(schedule)
            status['phase']='Checking shared game rules'
            await collect(onboard(f'b{b:03d}_{c}') for b,c in schedule)
            status['phase']='Running games'
            await collect(group(b,c) for b,c in schedule)
            if config.collect_debriefs:
                async def debrief(gid,role,history_rows):
                    prompt=[{'role':'system','content':'You completed a simulated Beer Game. Provide a concise retrospective summary, not private step-by-step reasoning. Do not claim feelings or human experience. Your explanation is a self-report, not evidence of the actual cause of your decisions.'},
                        {'role':'user','content':json.dumps(dict(role=role,history=history_rows,
                            questions=['Summarize your general ordering approach.',
                            'Identify a difficult observed state and its operational challenge.',
                            'Which additional information or interface feature might help?',
                            'Did the preparation allowance constrain your written memo? State uncertainty.']))}]
                    result=await gateway.request(dict(group=gid,role=role,stage='debrief'),prompt,384,
                        synthetic='Synthetic debrief placeholder; no model explanation was collected.')
                    return dict(group_id=gid,role=role,response_status=result['response_status'],text=result['text'])
                completed_frame=pd.DataFrame(completed)
                debriefs=await collect(debrief(gid,role,a[['week','demand','inventory','backlog','supply_line','order']].to_dict('records'))
                    for (gid,role),a in completed_frame.groupby(['group_id','role']))
                save(directory/'debriefs.json',debriefs)
        status['phase']='complete'
    except (Exception,asyncio.CancelledError) as exc:
        status.update(phase='stopped',reason=str(exc) if isinstance(exc,(StudyStopped,GroupFailed)) else type(exc).__name__)
        raise
    finally:
        beat.cancel()
        try:await beat
        except asyncio.CancelledError:pass
        refresh()
        save(directory/'spending.json',dict(estimated_charged_or_reserved_usd=gateway.charged,allowance_usd=config.budget_usd))
    return directory
