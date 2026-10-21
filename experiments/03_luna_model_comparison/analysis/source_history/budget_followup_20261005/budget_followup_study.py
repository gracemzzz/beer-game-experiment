"""Fresh calibration and paired Beer Games for a frozen development-screen choice.

Uses the unchanged physical simulator and estimator. All scientific changes and
budgets are saved before API calls. Failed answers are retained, never fabricated.
"""
import asyncio
import json
import sys
import time
from pathlib import Path
from dataclasses import asdict

import numpy as np
import pandas as pd

from budget_model_screen import (ROOT, DIRECTORY as SCREEN_DIR, BudgetGateway, BudgetStop,
    MODELS, COMMON, CLARIFICATION, QUIZ, QUIZ_SCHEMA, QUIZ_EXPECTED, SCHEMA,
    save, sha, messages, validate_decision)
sys.path.insert(0,str(ROOT/'src'))
from beergame_study.game import BeerGame, ROLES, demand_path, continuation
from beergame_study.config import Config
from beergame_study.analysis import report

BASE=ROOT/'data/development/budget_followup_20261005'
SHORT_TOKENS=32
ADEQUATE_TOKENS=240

def calibration_cases():
    cases=[]
    for role in ROLES:
        for inv,backlog,supply,demand in [(0,8,0,8),(24,0,12,8),(0,32,16,8),
                                       (0,96,0,0),(0,96,96,0),(120,0,24,0)]:
            shared={r:12 for r in ROLES};shared[role]=inv
            state=dict(week=12,role=role,inventory=inv,backlog=backlog,supply_line=supply,
                demand=demand,received=0,shipped=0,net_inventory=inv-backlog,
                cost=.5*inv+backlog,shared_inventory=shared)
            cases.append(dict(state=state,history=[]))
    return cases

async def decision(gateway,model,prompt,state,history,cap,identity):
    case=dict(state=state,history=history);key=sha(identity)
    plan=await gateway.request(model,dict(identity,stage='plan'),messages(case,cap,'plan',prompt,identity=key),cap)
    if plan.get('refused') or not (plan.get('response_status')=='completed' or
            plan.get('response_status')=='incomplete' and plan.get('incomplete_reason')=='max_output_tokens'):
        raise BudgetStop('Preparation failed; raw response retained.')
    final=await gateway.request(model,dict(identity,stage='final'),messages(case,cap,'final',prompt,plan['text'],key),192,SCHEMA)
    try:answer=json.loads(final.get('text',''))
    except (ValueError,TypeError):answer={}
    if final.get('response_status')!='completed' or final.get('refused') or not validate_decision(answer,state):
        raise BudgetStop('Final response failed format/readback; raw response retained, no replacement order.')
    if answer['order']>100000:raise BudgetStop('Emergency scale check; no order clipping.')
    return dict(order=answer['order'],plan_tokens=plan['usage']['output_tokens'],
        final_tokens=final['usage']['output_tokens'],plan_limit=cap,
        plan_truncated=plan['response_status']=='incomplete',
        latency_s=plan.get('elapsed_s',0)+final.get('elapsed_s',0))

def prepare(stage,selected,groups,allowance,short=SHORT_TOKENS,adequate=ADEQUATE_TOKENS):
    config=asdict(Config(mode='api',stage=stage,replicate_id='budget-followup-20261005',
        model=selected['model'],groups_per_condition=groups,short_tokens=short,adequate_tokens=adequate,
        budget_usd=allowance,calibration_method='fixed',group_replacements=0))
    config.update(prompt_variant=selected['prompt'],request_interval_s=.5,
        calibration_protocol='24 mixed-scale states; fixed caps 32/240/480; new model/prompt; no percentile claim',
        cap_selection_reason='Luna development memos were uncensored at 96 tokens; reduce the short candidate prospectively, before fresh calibration and games.')
    source={p.name:sha(p.read_text()) for p in [Path(__file__),Path(__file__).with_name('budget_model_screen.py'),
        ROOT/'src/beergame_study/game.py',ROOT/'src/beergame_study/estimation.py']}
    scientific={k:v for k,v in config.items() if k!='budget_usd'}
    directory=BASE/f'{stage}_{sha(dict(config=scientific,source=source))[:12]}'
    directory.mkdir(parents=True,exist_ok=True)
    manifest=dict(protocol='budget-followup-factory-clarification-v2',config=config,rates=MODELS[selected['model']],
        source_hashes=source,screen=str(SCREEN_DIR),selection=selected,
        primary_hypotheses='H1 lower group beta; H2 higher team cost under short tokens. No outcome-driven changes.',
        prior_pilot_inclusion=False,decision_common=COMMON+(CLARIFICATION if selected['prompt']=='clarified' else ''))
    if not (directory/'manifest.json').exists():save(directory/'manifest.json',manifest)
    else:
        old=json.loads((directory/'manifest.json').read_text())
        if old['source_hashes']!=source:raise BudgetStop('Code changed; preserve run and choose new ID.')
    return directory,config

async def collect(tasks):
    result=await asyncio.gather(*tasks,return_exceptions=True)
    for r in result:
        if isinstance(r,BaseException):raise r
    return result

async def calibrate(client,selected,allowance=.30):
    directory,config=prepare('calibration',selected,1,allowance)
    gateway=BudgetGateway(client,directory,allowance,interval_s=.5);start=time.monotonic()
    progress=dict(phase='running',mode='api',planned_requests=144,planned_decisions=72,groups_complete=0)
    rows=[]
    def refresh():
        progress.update(requests_done=gateway.finished,remaining_requests=max(0,144-gateway.finished),
            cached=gateway.cached,estimated_cost_usd=gateway.charged,allowance_usd=allowance,
            elapsed_s=time.monotonic()-start,decisions=len(rows))
        save(directory/'progress.json',progress)
    gateway.callback=refresh
    try:
        for label,cap in [('short',SHORT_TOKENS),('adequate',ADEQUATE_TOKENS),('benchmark',2*ADEQUATE_TOKENS)]:
            for i,case in enumerate(calibration_cases()):
                r=await decision(gateway,selected['model'],selected['prompt'],case['state'],[],cap,
                    dict(calibration=label,item=i,role=case['state']['role']))
                rows.append(dict(screen=label,item=i,role=case['state']['role'],**r))
                pd.DataFrame(rows).to_csv(directory/'calibration.csv',index=False)
        f=pd.DataFrame(rows);summary=f.groupby('screen').agg(mean_tokens=('plan_tokens','mean'),
            truncated_fraction=('plan_truncated','mean'),mean_order=('order','mean')).reset_index()
        pivot=f.pivot(index='item',columns='screen',values='order')
        difference=float(np.median(abs(pivot.adequate-pivot.benchmark)));by=summary.set_index('screen')
        passed=bool(by.loc['short','truncated_fraction']>=.2 and by.loc['adequate','truncated_fraction']<=.05
            and by.loc['adequate','mean_tokens']>by.loc['short','mean_tokens'] and difference<=4)
        summary.to_csv(directory/'calibration_summary.csv',index=False)
        save(directory/'calibration_recommendation.json',dict(short_tokens=SHORT_TOKENS,adequate_tokens=ADEQUATE_TOKENS,benchmark_tokens=2*ADEQUATE_TOKENS,
            median_absolute_adequate_benchmark_order_difference=difference,manipulation_screen_passed=passed,
            mode='api',method='Prospectively fixed caps; fresh mixed-scale feasibility states; no reference percentiles'))
        progress['phase']='complete';refresh()
        return directory
    except BaseException as exc:
        progress.update(phase='stopped',reason=str(exc) if isinstance(exc,BudgetStop) else type(exc).__name__);raise
    finally:refresh()

async def play(client,selected,calibration_dir,groups,allowance):
    recommendation=json.loads((Path(calibration_dir)/'calibration_recommendation.json').read_text())
    cm=json.loads((Path(calibration_dir)/'manifest.json').read_text())
    if not recommendation['manipulation_screen_passed']:raise BudgetStop('Calibration failed; no paid games.')
    if cm['config']['model']!=selected['model'] or cm['config']['prompt_variant']!=selected['prompt']:
        raise BudgetStop('Model/prompt mismatch with calibration.')
    directory,config=prepare('game',selected,groups,allowance)
    if json.loads((directory/'manifest.json').read_text())['source_hashes']!=cm['source_hashes']:
        raise BudgetStop('Source changed after calibration; use a fresh calibration.')
    save(directory/'calibration_provenance.json',dict(directory=str(calibration_dir),recommendation=recommendation))
    gateway=BudgetGateway(client,directory,allowance,interval_s=.5);start=time.monotonic()
    total=groups*8*(1+2*36);rows=[];tails=[];ledger=[];rules=[];completed=[]
    progress=dict(phase='rules',mode='api',groups_complete=0,planned_requests=total,planned_decisions=groups*288)
    def refresh():
        progress.update(requests_done=gateway.finished,cached=gateway.cached,planned_requests=total,remaining_requests=max(0,total-gateway.finished),
            estimated_cost_usd=gateway.charged,allowance_usd=allowance,
            elapsed_s=time.monotonic()-start,decisions=sum(r['phase']=='agent' for r in rows))
        save(directory/'progress.json',progress)
    gateway.callback=refresh
    model=selected['model'];prompt=selected['prompt']
    async def quiz(gid,role):
        nonlocal total
        for attempt in (1,2):
            task=dict(QUIZ,role=role)
            if attempt==2:
                total+=1;task['recheck']='Re-read the stated physical rules and the named questions; check each answer.'
            msg=[{'role':'system','content':COMMON+(CLARIFICATION if prompt=='clarified' else '')},
                 {'role':'user','content':json.dumps(task)}]
            r=await gateway.request(model,dict(group=gid,role=role,stage='rules',attempt=attempt),msg,256,QUIZ_SCHEMA)
            try:answer=json.loads(r.get('text',''))
            except ValueError:answer={}
            failed=[k for k,v in QUIZ_EXPECTED.items() if answer.get(k)!=v]
            passed=not failed and r.get('response_status')=='completed'
            rules.append(dict(group_id=gid,role=role,attempt=attempt,passed=passed,failed_fields=failed,answer=answer))
            save(directory/'rules_validation.json',rules)
            if passed:return
        raise BudgetStop('Fresh game rules check failed after one recheck; no replacement group started.')
    async def chain(block,condition):
        gid=f'b{block:03d}_{condition}';game=BeerGame();history=[[] for _ in ROLES];own=[]
        cap=SHORT_TOKENS if condition=='short' else ADEQUATE_TOKENS
        entry=dict(group_id=gid,block=block,condition=condition,replacement=0,status='running')
        ledger.append(entry);save(directory/'group_attempts.json',ledger)
        try:
            for week,demand in enumerate(demand_path(40),1):
                states=game.observe(demand)
                if week<=4:answers=[dict(order=4,plan_tokens=0,final_tokens=0,plan_limit=cap,plan_truncated=False,latency_s=0.) for _ in ROLES]
                else:answers=await collect(decision(gateway,model,prompt,s,history[i],cap,
                    dict(group=gid,role=s['role'],week=week)) for i,s in enumerate(states))
                game.commit([a['order'] for a in answers])
                for i,(s,a) in enumerate(zip(states,answers)):
                    row=dict(group_id=gid,block=block,condition=condition,replacement=0,
                        phase='warmup' if week<=4 else 'agent',**s,**a)
                    own.append(row);rows.append(row)
                    history[i].append(dict(week=week,demand=s['demand'],inventory=s['inventory'],backlog=s['backlog'],
                        supply_line=s['supply_line'],order=a['order'],shared_inventory=s['shared_inventory']))
                pd.DataFrame(rows).to_csv(directory/'all_candidate_rounds.csv',index=False)
                refresh()
            t=continuation(game,demand,12)
            tails.extend(dict(s,group_id=gid,block=block,condition=condition) for s in t)
            completed.extend(own);entry['status']='complete';progress['groups_complete']+=1
            pd.DataFrame(completed).to_csv(directory/'rounds.csv',index=False)
            pd.DataFrame(tails).to_csv(directory/'continuation.csv',index=False)
        except BaseException:entry['status']='stopped';raise
        finally:save(directory/'group_attempts.json',ledger)
    try:
        schedule=[(b,c) for b in range(groups) for c in ('short','adequate')]
        np.random.default_rng(20261005).shuffle(schedule)
        await collect(quiz(f'b{b:03d}_{c}',r) for b,c in schedule for r in ROLES)
        progress['phase']='running games';refresh()
        # One matched block at a time limits in-flight spending and keeps counterparts together.
        for block in range(groups):
            await collect(chain(b,c) for b,c in schedule if b==block)
        progress['phase']='complete'
    except BaseException as exc:
        progress.update(phase='stopped',reason=str(exc) if isinstance(exc,BudgetStop) else type(exc).__name__)
        raise
    finally:
        refresh();save(directory/'spending.json',dict(estimated_charged_or_reserved_usd=gateway.charged,allowance_usd=allowance))
    # Analysis uses the original prespecified fits/H1/H2 code; no outcome-based change.
    report(directory)
    return directory
