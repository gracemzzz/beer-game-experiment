"""Bounded model/prompt comparison. No API call occurs on import.

Development screen only: no H1/H2 test, no replacement of inconvenient answers.
Run through notebook 02 or call run_screen(client=...) with an authenticated client.
"""
import asyncio
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study.prompts import COMMON, SCHEMA, make_messages, validate_decision
from beergame_study.game import ROLES

SOURCE_RUN = ROOT/'data/runs/game_api_8236a9c840b29d36'
DIRECTORY = ROOT/'data/development/model_screen_20261005'
MODELS = {
    'gpt-5.4-nano-2026-03-17': {'input':.20, 'cached':.02, 'output':1.25},
    'gpt-5.4-mini-2026-03-17': {'input':.75, 'cached':.075, 'output':4.50},
    'gpt-5.6-luna': {'input':.20, 'cached':.02, 'output':1.20},
}
CLARIFICATION = '''
Physical rules, applying in every round:
Demand is the NEW incoming order processed this week. Backlog is the TOTAL still
unfilled after this week's shipments, including any unfilled part of that demand.
Backlog remains owed, even when next week's new demand is zero. It incurs cost
each week until goods actually fill it. It is not canceled by a quiet week.
For the FACTORY, your order directly starts production now. There is no outside
supplier, raw-material constraint or production-capacity constraint. A production
order q placed in week t becomes available factory stock in week t+3. It does not
require an existing supply line to start, and no extra order-transmission or
downstream-shipping lag is added before that production becomes your own stock.
For the other roles, orders go to the immediate upstream role; stock shortages
there may delay shipment. Supply_line includes previous orders still unreceived;
these remain active commitments. Your action can affect future holding/backlog
costs even though it cannot change the already-processed current week.
No ordering formula or preferred quantity is supplied. Choose using the stated
team objective over future weeks as well as the automatic continuation.
'''

QUIZ_EXPECTED = dict(factory_production_receipt_week=13,
    production_requires_existing_supply_line=False,
    backlog_next_week_without_receipts=20,
    next_week_backlog_cost=20,
    zero_new_demand_cancels_backlog=False,
    current_backlog_already_includes_unfilled_current_demand=True)
QUIZ_SCHEMA = dict(type='object',properties={k:{'type':'boolean' if type(v) is bool else 'integer'}
    for k,v in QUIZ_EXPECTED.items()},required=list(QUIZ_EXPECTED),additionalProperties=False)
QUIZ = dict(task='Check physical game rules, not an ordering strategy.', questions={
    'factory_production_receipt_week':'The factory starts producing 6 cases in week 10. Which week does this production become available factory stock?',
    'production_requires_existing_supply_line':'Must the factory already have something in its supply line before it can start new production?',
    'backlog_next_week_without_receipts':'A role ends this week with inventory 0 and backlog 20. Next week it receives no goods and no new demand. What is its ending backlog?',
    'next_week_backlog_cost':'In that same next week, what is the backlog cost?',
    'zero_new_demand_cancels_backlog':'Does zero new demand cancel previously unfilled orders?',
    'current_backlog_already_includes_unfilled_current_demand':'In the supplied after-shipments observation, does backlog already include the unfilled portion of this week’s demand?'
})

def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False));temp.replace(path)

def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def cases():
    wanted=[('short','factory',21),('short','factory',29),('short','factory',31),
            ('adequate','factory',30),('adequate','factory',40),
            ('short','distributor',30),('adequate','retailer',15),('adequate','wholesaler',24)]
    old=[json.loads(p.read_text()) for p in (SOURCE_RUN/'requests').glob('*.json')]
    result=[]
    for c,role,week in wanted:
        rec=next(r for r in old if r['identity']==dict(group='b000_'+c,role=role,week=week,stage='plan'))
        payload=json.loads(rec['messages'][1]['content']);state=payload['current_state']
        result.append(dict(case_id=f'observed_{c}_{role}_{week}',source='observed development state',
            state=state,history=payload['past_rounds'],
            factory_shortage=role=='factory' and state['inventory']==state['supply_line']==0 and state['backlog']>0))
    for role,inventory,backlog,supply,demand in [('factory',0,40,0,0),('factory',48,0,0,0),
            ('distributor',0,16,32,8),('retailer',12,0,8,4)]:
        shared={r:12 for r in ROLES};shared[role]=inventory
        state=dict(week=12,role=role,inventory=inventory,backlog=backlog,supply_line=supply,
            demand=demand,received=0,shipped=0,net_inventory=inventory-backlog,
            cost=.5*inventory+backlog,shared_inventory=shared)
        result.append(dict(case_id=f'new_{role}_{inventory}_{backlog}',source='new hypothetical state',
            state=state,history=[],factory_shortage=role=='factory' and inventory==supply==0 and backlog>0))
    return result

def messages(case,cap,stage,prompt,notes='',identity=''):
    msg=make_messages(case['state'],case['history'],cap,stage,notes,identity)
    if prompt=='clarified':msg[0]['content']+=CLARIFICATION
    return msg

def design():
    return dict(protocol='budget-model-feasibility-v1',models=MODELS,
        prompts={'original':COMMON,'clarified':COMMON+CLARIFICATION},caps=[96,240],final_cap=192,
        cases=cases(),quiz=QUIZ,quiz_schema=QUIZ_SCHEMA,quiz_repeats=2,
        screen_allowance_usd=.45,campaign_new_allowance_usd=2.40,
        prior_current_study_spend_usd=.37203635,
        reasoning='none',retries='transport only, at most two retries; no correctness retries',
        eligibility=['Both factual quizzes correct','All 24 final responses valid',
                     'Adequate allowance: positive production in all four empty-pipeline factory shortage cases',
                     'No order above the existing emergency threshold'],
        selection='Among eligible models choose lowest input/output prices; within model prefer clarified if eligible. Never select on H1/H2 direction or significance.',
        limitations='Development states include failures selected from pilot 02; not a generalization test. Short shortage behavior is reported but does not determine selection. No game p-values.',
        source_run=SOURCE_RUN.name)

class BudgetStop(RuntimeError):pass

class BudgetGateway:
    def __init__(self,client,directory,allowance=.45,callback=None,interval_s=1.0):
        self.client=client;self.directory=Path(directory);self.cache=self.directory/'requests'
        self.cache.mkdir(parents=True,exist_ok=True)
        self.allowance=allowance;self.callback=callback or (lambda:None)
        self.charged=sum(json.loads(p.read_text()).get('charge_usd',0.) for p in self.cache.glob('*.json'))
        self.sem=asyncio.Semaphore(3);self.lock=asyncio.Lock();self.next_start=0.;self.cooldown=0.;self.interval_s=interval_s
        self.disabled=set();self.finished=0;self.cached=0

    async def request(self,model,identity,msg,limit,schema=None):
        if model in self.disabled:return {'status':'unavailable','text':'','usage':{}}
        rates=MODELS[model]
        key=sha(dict(model=model,identity=identity,messages=msg,limit=limit,schema=schema))
        for attempt in range(3):
            path=self.cache/f'{key}_{attempt}.json'
            if path.exists():
                r=json.loads(path.read_text())
                if r['status']=='transient':continue
                if r['status']=='pending':raise BudgetStop('Unresolved request reservation; review before retrying.')
                if r['status'] not in ('ok','unavailable'):raise BudgetStop('Saved API/protocol failure requires review.')
                if r['status']=='unavailable':self.disabled.add(model)
                self.finished+=1;self.cached+=1;return r
            async with self.sem:
                if model in self.disabled:return {'status':'unavailable','text':'','usage':{}}
                while True:
                    async with self.lock:
                        delay=max(self.next_start,self.cooldown)-time.monotonic()
                        if delay<=0:self.next_start=time.monotonic()+self.interval_s;break
                    await asyncio.sleep(min(delay,1.))
                # UTF-8 bytes + schema/overhead is conservative for these text-only inputs.
                input_margin=1.25 if model=='gpt-5.6-luna' else 1.
                reserve=((len(json.dumps(msg).encode())+len(json.dumps(schema).encode())+2048)*rates['input']*input_margin+limit*rates['output'])/1e6
                if self.charged+reserve>self.allowance:
                    raise BudgetStop(f'Local cap ${self.allowance:.2f}; charged/reserved ${self.charged:.4f}.')
                self.charged+=reserve;started=time.monotonic()
                r=dict(model=model,identity=identity,messages=msg,limit=limit,schema=schema,
                    status='pending',charge_usd=reserve,created_utc=datetime.now(timezone.utc).isoformat())
                save(path,r);self.callback()
                try:
                    kwargs=dict(model=model,input=msg,reasoning={'effort':'none'},max_output_tokens=limit,store=False)
                    if schema:kwargs['text']={'format':{'type':'json_schema','name':'answer','strict':True,'schema':schema}}
                    response=await self.client.responses.create(**kwargs)
                    raw=response.model_dump(mode='json');u=raw.get('usage') or {}
                    usage=dict(input_tokens=u.get('input_tokens',0),output_tokens=u.get('output_tokens',0),
                        cached_input_tokens=(u.get('input_tokens_details') or {}).get('cached_tokens',0),
                        reasoning_tokens=(u.get('output_tokens_details') or {}).get('reasoning_tokens',0))
                    if u:
                        charge=((usage['input_tokens']-usage['cached_input_tokens'])*rates['input']+
                            usage['cached_input_tokens']*rates['cached']+usage['output_tokens']*rates['output'])/1e6
                        # Luna docs bill cache writes at 1.25x. Conservatively reserve a 25% input uplift
                        # until its raw usage exposes an unambiguous cache-write breakdown.
                        if model=='gpt-5.6-luna':charge+=usage['input_tokens']*rates['input']*.25/1e6
                        self.charged+=charge-reserve;r['charge_usd']=charge
                    text=''.join(c.get('text','') for o in raw.get('output',[]) if o.get('type')=='message'
                        for c in o.get('content',[]) if c.get('type')=='output_text')
                    refused=any(c.get('type')=='refusal' for o in raw.get('output',[]) for c in o.get('content',[]))
                    r.update(status='ok',response_status=raw.get('status'),usage=usage,text=text,
                        refused=refused,incomplete_reason=(raw.get('incomplete_details') or {}).get('reason'),
                        response=raw,elapsed_s=time.monotonic()-started)
                    save(path,r)
                    if usage['reasoning_tokens'] or usage['output_tokens']>limit:
                        r['status']='protocol_error';save(path,r)
                        raise BudgetStop('Unexpected reasoning/output usage; preserve evidence and stop.')
                    self.finished+=1;return r
                except BudgetStop:raise
                except Exception as exc:
                    http=getattr(exc,'status_code',None);body=getattr(exc,'body',{}) or {}
                    err=body.get('error',body) if isinstance(body,dict) else {}
                    code=err.get('code') or err.get('type')
                    transient=(http in (408,409,500,502,503,504) or http==429 and code in ('rate_limit_exceeded','rate_limit_error')
                               or type(exc).__name__ in ('APIConnectionError','APITimeoutError'))
                    unavailable=http==404 or http==403 and code in ('model_not_found','model_access_denied')
                    if http in (400,401,403,404,429):self.charged-=reserve;r['charge_usd']=0.
                    r.update(status='unavailable' if unavailable else ('transient' if transient else 'api_error'),
                        error_type=type(exc).__name__,http_status=http,error_code=code,text='',usage={})
                    save(path,r)
                    if unavailable:self.disabled.add(model);self.finished+=1;return r
                    if not transient or attempt==2:raise BudgetStop(f'API stopped: {type(exc).__name__}; HTTP {http}; {code}') from None
                    headers=getattr(getattr(exc,'response',None),'headers',{}) or {}
                    try:retry_after=float(headers.get('retry-after',0))
                    except (TypeError,ValueError):retry_after=0.
                    self.cooldown=max(self.cooldown,time.monotonic()+max(retry_after,min(60,2**(attempt+1))))
                finally:self.callback()
        raise BudgetStop('Saved transport attempts exhausted.')

async def run_screen(client,directory=DIRECTORY,allowance=.45):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    planned=design();planned['screen_allowance_usd']=allowance
    manifest=directory/'design.json'
    if manifest.exists():
        if json.loads(manifest.read_text())!=planned:raise BudgetStop('Design differs: use a new folder, not an overwritten screen.')
    else:save(manifest,planned)
    total=len(MODELS)*2*(2+len(planned['cases'])*4);started=time.monotonic()
    gateway=BudgetGateway(client,directory,allowance)
    progress=dict(phase='running',planned_requests=total)
    def refresh():
        progress.update(requests_done=gateway.finished,cached=gateway.cached,
            estimated_charged_or_reserved_usd=gateway.charged,allowance_usd=allowance,
            remaining_requests=0 if progress['phase']=='complete' else max(0,total-gateway.finished),
            skipped_requests=max(0,total-gateway.finished) if progress['phase']=='complete' else 0,
            elapsed_s=time.monotonic()-started)
        save(directory/'progress.json',progress)
    gateway.callback=refresh;rows=[];quiz_rows=[]
    async def candidate(model,prompt):
        for repeat in range(2):
            msg=[{'role':'system','content':COMMON+(CLARIFICATION if prompt=='clarified' else '')},
                 {'role':'user','content':json.dumps(QUIZ)}]
            result=await gateway.request(model,dict(prompt=prompt,stage='quiz',repeat=repeat),msg,256,QUIZ_SCHEMA)
            try:answer=json.loads(result.get('text',''))
            except ValueError:answer={}
            quiz_rows.append(dict(model=model,prompt=prompt,repeat=repeat,
                passed=answer==QUIZ_EXPECTED and result.get('response_status')=='completed',
                status=result['status'],answer=answer))
            save(directory/'quizzes.json',quiz_rows)
            if result['status']=='unavailable':return
        for case in planned['cases']:
            for cap in planned['caps']:
                identity=dict(prompt=prompt,case_id=case['case_id'],cap=cap)
                plan=await gateway.request(model,dict(identity,stage='plan'),
                    messages(case,cap,'plan',prompt,identity=sha(identity)),cap)
                allowed_plan=plan.get('response_status')=='completed' or (plan.get('response_status')=='incomplete'
                    and plan.get('incomplete_reason')=='max_output_tokens')
                final=await gateway.request(model,dict(identity,stage='final'),
                    messages(case,cap,'final',prompt,plan.get('text',''),sha(identity)),192,SCHEMA)
                try:answer=json.loads(final.get('text',''))
                except ValueError:answer={}
                valid=(allowed_plan and not plan.get('refused') and final.get('response_status')=='completed'
                    and not final.get('refused') and validate_decision(answer,case['state']) and answer['order']<=100000)
                rows.append(dict(model=model,prompt=prompt,case_id=case['case_id'],cap=cap,
                    role=case['state']['role'],factory_shortage=case['factory_shortage'],valid=bool(valid),
                    order=answer.get('order'),memo_tokens=plan.get('usage',{}).get('output_tokens',0),
                    truncated=plan.get('response_status')=='incomplete',plan_text=plan.get('text',''),
                    final_text=final.get('text','')))
                pd.DataFrame(rows).to_csv(directory/'decisions.csv',index=False)
    try:
        # Sequential candidate starts make availability failures cheap; cases remain paced.
        for model in MODELS:
            for prompt in ('original','clarified'):
                if model not in gateway.disabled:await candidate(model,prompt)
        progress['phase']='complete'
    except BaseException as exc:
        progress.update(phase='stopped',reason=str(exc) if isinstance(exc,BudgetStop) else type(exc).__name__)
        raise
    finally:refresh()
    return summarize(directory)

def summarize(directory=DIRECTORY):
    directory=Path(directory);df=pd.read_csv(directory/'decisions.csv')
    quiz=json.loads((directory/'quizzes.json').read_text());summary=[]
    for model in MODELS:
        for prompt in ('original','clarified'):
            a=df[(df.model==model)&(df.prompt==prompt)];q=[r for r in quiz if r['model']==model and r['prompt']==prompt]
            short=a[a.cap==96];adequate=a[a.cap==240]
            needed=adequate[adequate.factory_shortage]
            passed=len(q)==2 and all(r['passed'] for r in q) and len(a)==24 and a.valid.all() and len(needed)==4 and (needed.order>0).all()
            summary.append(dict(model=model,prompt=prompt,eligible=bool(passed),
                quizzes_correct=sum(r['passed'] for r in q),valid_decisions=int(a.valid.sum()),
                adequate_factory_shortage_zeros=int((needed.order==0).sum()),
                short_factory_shortage_zeros=int((short[short.factory_shortage].order==0).sum()),
                short_mean_tokens=float(short.memo_tokens.mean()) if len(short) else None,
                adequate_mean_tokens=float(adequate.memo_tokens.mean()) if len(adequate) else None,
                short_truncation=float(short.truncated.mean()) if len(short) else None,
                adequate_truncation=float(adequate.truncated.mean()) if len(adequate) else None))
    eligible=[s for s in summary if s['eligible']]
    eligible.sort(key=lambda s:(MODELS[s['model']]['input'],MODELS[s['model']]['output'],s['prompt']!='clarified'))
    selected=eligible[0] if eligible else None
    result=dict(selected=selected,candidates=summary,
        conclusion='Development screen only. Selection was based on feasibility, never H1/H2 results.',
        spend=json.loads((directory/'progress.json').read_text())['estimated_charged_or_reserved_usd'])
    save(directory/'selection.json',result);pd.DataFrame(summary).to_csv(directory/'summary.csv',index=False)
    return result


if __name__=='__main__':
    print(json.dumps(design(),indent=2))
