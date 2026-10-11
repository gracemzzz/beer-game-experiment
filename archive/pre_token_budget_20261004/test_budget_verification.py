"""Offline and mocked API checks. Never sends live requests."""
import asyncio
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import nbformat
import numpy as np
import pandas as pd
from openai import AsyncOpenAI
import budget_verification as s


def config(**changes):
    c = dict(mode='offline', stage='diagnostics', model=s.MODEL, groups_per_cell=1,
             weeks=24, replicate_id='test', seed=314, budget_usd=2.,
             max_output_tokens=8192, timeout_s=180, effort_levels=s.EFFORT_LEVELS)
    c.update(changes)
    return c

class Tests(unittest.TestCase):
    def test_current_state_last_and_unforced_readback_with_conflicting_history(self):
        history=[dict(week=w,role='retailer',demand=4,inventory=12,backlog=0,
                      net_inventory=12,supply_line=8 if w%2 else 4,order=0) for w in range(1,37)]
        state=dict(week=37,role='retailer',demand=0,inventory=0,backlog=9,
                   net_inventory=-9,supply_line=0,cost=9.,received=0,shipped=0)
        task=dict(kind='game_decision',current_state=state)
        for condition in s.CONDITIONS:
            prompt=s.messages(condition,task,history)
            payload=json.loads(prompt[1]['content'])
            self.assertEqual(list(payload),['your_past_rounds','task'])
            self.assertEqual(payload['your_past_rounds'],history)
            self.assertEqual(payload['task']['current_state'],state)
            self.assertEqual(prompt[0]['content'],s.STANDARD+'\n\n'+
                             (s.TRAINING if condition.trained else s.CONTROL))
        schema=s.Decision.model_json_schema()
        self.assertEqual(list(schema['properties'])[-1],'order')
        # Schema still permits an incorrect copied value; application must reject it.
        answer=s.Decision(order=0,observed_demand=0,observed_inventory=0,
                          observed_backlog=9,observed_supply_line=8).model_dump()
        self.assertFalse(s.validate_answer(answer,state))
        answer['observed_supply_line']=0
        self.assertTrue(s.validate_answer(answer,state))
        self.assertEqual(set(s.CHECK_TASK['questions']),set(s.RulesCheck.model_fields))

    def test_notebook_and_conservation(self):
        nbformat.validate(nbformat.read(Path(__file__).with_name('START_HERE_verify_budget.ipynb'), as_version=4))
        game = s.BeerGame()
        rng = np.random.default_rng(123)
        for _ in range(60):
            old_i, old_b = game.inventory.copy(), game.backlog.copy()
            states = game.observe(int(rng.integers(0,20)))
            for i, state in enumerate(states):
                self.assertEqual(state['inventory'], old_i[i]+state['received']-state['shipped'])
                self.assertEqual(state['backlog'], old_b[i]+state['demand']-state['shipped'])
            game.commit([int(x) for x in rng.integers(0,40,4)])

    def test_performance_equilibrium_and_free_measurement_gate(self):
        game=s.BeerGame(); rows=[]
        for week in range(1,17):
            states=game.observe(4)
            for i,state in enumerate(states):
                rows.append(dict(state,agent_id=s.ROLES[i],group_id='equilibrium',
                                 trained=False,effort='low',order=4))
            game.commit([4]*4)
        roles,groups,conditions=s.performance_tables(pd.DataFrame(rows))
        self.assertEqual(groups.total_cost.iloc[0],384.)
        self.assertEqual(groups.backlog_cost.iloc[0],0.)
        self.assertEqual(groups.customer_cumulative_fulfillment.iloc[0],1.)
        self.assertTrue(roles.bullwhip_ratio.isna().all())
        self.assertTrue(s.measurement_self_check().passed.all())

    def test_beta_recovery_and_demand_copy_nonidentification(self):
        rng = np.random.default_rng(12)
        demand = rng.uniform(2,20,150)
        ni, sl = rng.uniform(-30,70,150), rng.uniform(0,70,150)
        frame = pd.DataFrame(dict(week=np.arange(150), demand=demand, net_inventory=ni, supply_line=sl))
        for beta in (0., .15, .65, 1.4):
            frame['order'] = s.predicted_orders([.55,.4,beta,45],demand,ni,sl)
            result = s.estimate_beta(frame)
            self.assertTrue(result['usable'], result)
            self.assertAlmostEqual(result['beta'], beta, places=5)
        frame['order'] = demand
        result = s.estimate_beta(frame)
        self.assertFalse(result['usable'])

    def test_randomization_and_multiplicity(self):
        self.assertEqual(s.signflip_pvalue(np.zeros(8)), 1.)
        self.assertAlmostEqual(s.signflip_pvalue(np.ones(8)), 2/256)
        self.assertAlmostEqual(s.signflip_pvalue(np.ones(5)), 2/32)
        self.assertEqual(s.signflip_pvalue([1,-1]*4), 1.)
        np.testing.assert_allclose(s.holm_two([.04,.01]), [.04,.02])

    def test_full_offline_screen_and_game_resume(self):
        async def run():
            with tempfile.TemporaryDirectory() as tmp:
                for stage, count in [('diagnostics',48), ('game',4*4*24)]:
                    c = config(stage=stage)
                    first, directory = await s.run_study(tmp,c,render=False)
                    second, again = await s.run_study(tmp,c,render=False)
                    pd.testing.assert_frame_equal(first,second)
                    self.assertEqual(directory,again)
                    self.assertEqual(len(first),count)
                    progress=json.loads((directory/'progress.json').read_text())
                    self.assertEqual(progress['remaining'],0)
                    self.assertEqual(progress['cached'],68 if stage=='diagnostics' else 4*4*25+4)
                    report=s.verification_report(directory,c)
                    if stage=='game':
                        self.assertTrue((directory/'verification_summary.json').exists())
                        self.assertFalse((directory/'cost_projections.csv').exists())
                    self.assertIn('conclusions',report)
                    self.assertIn('OFFLINE SOFTWARE CHECK',report)
                    self.assertEqual(json.loads((directory/'spending.json').read_text())['charged_or_reserved_usd'],0)
                    if stage=='game':
                        tests=pd.read_csv(directory/'hypothesis_tests.csv')
                        self.assertTrue(tests.p_holm.isna().all())
        asyncio.run(run())

    def test_sdk_effort_readback_cache_and_stop(self):
        async def run():
            bad=[False]
            calls=[]
            def handler(request):
                payload=json.loads(request.content)
                calls.append(payload)
                observation=dict(order=7,observed_demand=4,observed_inventory=12,
                                 observed_backlog=0,observed_supply_line=8)
                if bad[0]: observation['observed_demand']=999
                return httpx.Response(200,json=dict(id='resp_mock',object='response',created_at=1,
                    model=s.MODEL,status='completed',output=[dict(type='message',id='msg_mock',
                    role='assistant',status='completed',content=[dict(type='output_text',
                    text=json.dumps(observation),annotations=[])])],usage=dict(input_tokens=100,
                    output_tokens=250,total_tokens=350,input_tokens_details={'cached_tokens':0},
                    output_tokens_details={'reasoning_tokens':200})))
            client=AsyncOpenAI(api_key='test-not-real',max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    runner=s.Runner(tmp,config(mode='api'),client,render=False)
                    runner.progress=s.RunProgress(4,'api',render=False)
                    state=s.BeerGame().observe(4)[0]
                    args=(s.Condition(True,'high'),{'id':1},{'current_state':state},state)
                    record=await runner.request(*args)
                    cached=await runner.request(*args)
                    self.assertEqual(record,cached)
                    self.assertEqual(len(calls),1)
                    self.assertEqual(calls[0]['reasoning'],{'effort':'high'})
                    self.assertEqual(calls[0]['max_output_tokens'],8192)
                    self.assertEqual(record['usage']['reasoning_tokens'],200)
                    self.assertEqual(calls[0]['text']['format']['type'],'json_schema')
                    bad[0]=True
                    with self.assertRaisesRegex(s.ExperimentStopped,'comprehension_failed'):
                        await runner.request(s.Condition(False,'low'),{'id':2},{'current_state':state},state)
                    self.assertEqual(len(calls),2)
                    saved=[json.loads(p.read_text()) for p in (Path(tmp)/'requests').glob('*.json')]
                    self.assertTrue(any(r['status']=='comprehension_failed' for r in saved))
                    self.assertNotIn('test-not-real',json.dumps(saved))
            finally:
                await client.close()
        asyncio.run(run())

    def test_access_both_efforts_before_any_game_and_failure_report(self):
        async def run():
            calls=[]
            def handler(request):
                payload=json.loads(request.content);calls.append(payload)
                if payload['reasoning']['effort']=='low':
                    return httpx.Response(404,json={'error':{'message':'Unavailable test model',
                        'type':'invalid_request_error','code':'model_not_found'}})
                return httpx.Response(200,json=dict(id='resp_access',object='response',created_at=1,
                    model=s.MODEL,status='completed',output=[dict(type='message',id='msg_access',
                    role='assistant',status='completed',content=[dict(type='output_text',
                    text=json.dumps(dict(order=4,observed_demand=4,observed_inventory=12,observed_backlog=0,observed_supply_line=8)),annotations=[])])],usage=dict(input_tokens=100,
                    output_tokens=20,total_tokens=120,input_tokens_details={'cached_tokens':0},
                    output_tokens_details={'reasoning_tokens':0})))
            client=AsyncOpenAI(api_key='test-not-real',max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    c=config(mode='api',stage='game')
                    with self.assertRaises(s.ExperimentStopped):
                        await s.run_study(tmp,c,client=client,render=False)
                    self.assertEqual([p['reasoning']['effort'] for p in calls],['minimal','minimal','low'])
                    directory=s.latest_run(tmp,c)
                    report=s.verification_report(directory,c)
                    self.assertIn('stopped before completion',report)
                    self.assertFalse((directory/'rounds.csv').exists())
                    summary=json.loads((directory/'verification_summary.json').read_text())
                    self.assertEqual(summary['access_checks_passed'],2)
                    self.assertEqual(summary['saved_failures'],1)
                    self.assertIsNone(summary['usable_role_betas'])
            finally:
                await client.close()
        asyncio.run(run())

    def test_reasoning_exhaustion_is_distinct_from_refusal_and_never_retried(self):
        async def run():
            calls=[]
            def handler(request):
                calls.append(json.loads(request.content))
                return httpx.Response(200,json=dict(id='resp_limit',object='response',created_at=1,
                    model=s.MODEL,status='incomplete',incomplete_details={'reason':'max_output_tokens'},
                    output=[],usage=dict(input_tokens=100,output_tokens=25000,total_tokens=25100,
                    input_tokens_details={'cached_tokens':0},output_tokens_details={'reasoning_tokens':25000})))
            client=AsyncOpenAI(api_key='test-not-real',max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    runner=s.Runner(tmp,config(mode='api',max_output_tokens=25000),client,render=False)
                    runner.progress=s.RunProgress(1,'api',render=False)
                    state=s.BeerGame().observe(4)[0]
                    with self.assertRaisesRegex(s.ExperimentStopped,'OUTPUT LIMIT'):
                        await runner.request(s.Condition(True,'high'),{'kind':'game'},{'current_state':state},state)
                    self.assertEqual(len(calls),1)
                    r=json.loads(next((Path(tmp)/'requests').glob('*.json')).read_text())
                    self.assertEqual(r['status'],'output_limit_reached')
                    self.assertEqual(r['incomplete_reason'],'max_output_tokens')
                    self.assertIsNone(r['answer'])
                    self.assertAlmostEqual(r['budget_charge_usd'],.010005)
                    self.assertEqual(calls[0]['max_output_tokens'],25000)
            finally:
                await client.close()
        asyncio.run(run())

    def test_total_cost_error_blocks_all_games_and_reports_mismatch(self):
        async def run():
            decisions=[]
            def handler(request):
                payload=json.loads(request.content)
                task=json.loads(payload['input'][1]['content'])['task']
                if task.get('task')=='rules_check':
                    answer=dict(s.CHECK_ANSWERS, total_holding_cost=.5)
                else:
                    decisions.append(task)
                    state=task['current_state']
                    answer=dict(order=4, **{'observed_'+k:state[k] for k in
                        ('demand','inventory','backlog','supply_line')})
                return httpx.Response(200,json=dict(id='resp_rules',object='response',created_at=1,
                    model=s.MODEL,status='completed',output=[dict(type='message',id='msg_rules',
                    role='assistant',status='completed',content=[dict(type='output_text',
                    text=json.dumps(answer),annotations=[])])],usage=dict(input_tokens=100,
                    output_tokens=50,total_tokens=150,input_tokens_details={'cached_tokens':0},
                    output_tokens_details={'reasoning_tokens':0})))
            client=AsyncOpenAI(api_key='test-not-real',max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    c=config(mode='api',stage='game',max_concurrent_requests=8)
                    with self.assertRaisesRegex(s.ExperimentStopped,
                        'total_holding_cost: expected 4.0, received 0.5'):
                        await s.run_study(tmp,c,client=client,render=False)
                    directory=s.latest_run(tmp,c)
                    saved=[json.loads(p.read_text()) for p in (directory/'requests').glob('*.json')]
                    self.assertEqual(len(decisions),4)  # only preflights
                    self.assertFalse(any(r['identity']['kind']=='game' for r in saved))
                    self.assertIn('expected 4.0, received 0.5',s.verification_report(directory,c))
                    self.assertFalse(s.validate_answer(dict(s.CHECK_ANSWERS,total_holding_cost=.5)))
                    self.assertTrue(s.validate_answer(s.CHECK_ANSWERS))
            finally:
                await client.close()
        asyncio.run(run())

    def test_bounded_retry_recovery_costs_and_cache(self):
        async def run():
            calls=[]
            always_wrong=[False]
            def handler(request):
                payload=json.loads(request.content); calls.append(payload)
                answer=dict(s.CHECK_ANSWERS)
                if len(calls)==1 or always_wrong[0]:
                    answer['total_holding_cost']=.5
                return httpx.Response(200,json=dict(id='resp_retry',object='response',created_at=1,
                    model=s.MODEL,status='completed',output=[dict(type='message',id='msg_retry',
                    role='assistant',status='completed',content=[dict(type='output_text',
                    text=json.dumps(answer),annotations=[])])],usage=dict(input_tokens=100,
                    output_tokens=50,total_tokens=150,input_tokens_details={'cached_tokens':0},
                    output_tokens_details={'reasoning_tokens':10})))
            client=AsyncOpenAI(api_key='test-not-real',max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    c=config(mode='api',max_attempts=3)
                    runner=s.Runner(tmp,c,client,render=False)
                    runner.progress=s.RunProgress(1,'api',render=False)
                    args=(s.Condition(False,'minimal'),{'kind':'rules','id':1},s.CHECK_TASK)
                    result=await runner.request(*args)
                    self.assertEqual(len(calls),2)
                    self.assertEqual(result['attempts_used'],2)
                    self.assertEqual(result['usage']['output_tokens'],100)
                    self.assertEqual(runner.progress.remaining if hasattr(runner.progress,'remaining') else runner.progress.snapshot()['remaining'],0)
                    records=[json.loads(p.read_text()) for p in (Path(tmp)/'requests').glob('*.json')]
                    self.assertEqual({r['status'] for r in records},{'ok','comprehension_failed'})
                    self.assertAlmostEqual(runner.charged, .00005)
                    self.assertTrue(all(p['reasoning']['effort']=='minimal' for p in calls))
                    resumed=s.Runner(tmp,c,client,render=False)
                    resumed.progress=s.RunProgress(1,'api',render=False)
                    again=await resumed.request(*args)
                    self.assertEqual(len(calls),2)
                    self.assertEqual(again['usage'],result['usage'])
                    self.assertEqual(resumed.progress.cached,2)
                    always_wrong[0]=True
                    with tempfile.TemporaryDirectory() as failtmp:
                        for _ in range(2):
                            failing=s.Runner(failtmp,c,client,render=False)
                            failing.progress=s.RunProgress(1,'api',render=False)
                            with self.assertRaisesRegex(s.ExperimentStopped,'Attempts used: 3/3'):
                                await failing.request(*args)
                        self.assertEqual(len(calls),5)  # restart cannot buy three more retries
                        self.assertEqual(len(list((Path(failtmp)/'requests').glob('*.json'))),3)
            finally:
                await client.close()
        asyncio.run(run())

    def test_failed_group_replaced_with_auditable_fresh_group_and_resume(self):
        async def run():
            original=s.Runner._request
            exhaust=[False]
            async def injected(runner,condition,identity,task,state=None,history=None):
                record=await original(runner,condition,identity,task,state,history)
                if ((identity.get('group')=='b000_control_minimal' or (exhaust[0] and identity.get('group','').startswith('b000_control_minimal_replacement'))) and identity.get('week')==2):
                    record['status']='comprehension_failed'
                    record['validation_errors']={'observed_supply_line':{'expected':0,'received':8}}
                    s.atomic_json(runner.cache/(record['request_key']+'.json'),record)
                    runner.progress.successful-=1;runner.progress.errors+=1
                    raise s.AttemptFailed('Injected invalid readback',record)
                return record
            with tempfile.TemporaryDirectory() as tmp:
                c=config(stage='game',weeks=16,max_group_replacements=1,max_concurrent_requests=8)
                with patch.object(s.Runner,'_request',injected):
                    frame,directory=await s.run_study(tmp,c,render=False)
                self.assertEqual(len(frame),256)
                self.assertEqual(frame.group_id.nunique(),4)
                self.assertNotIn('b000_control_minimal',set(frame.group_id))
                self.assertIn('b000_control_minimal_replacement1',set(frame.group_id))
                ledger=json.loads((directory/'group_attempts.json').read_text())
                self.assertEqual(sum(g['status']=='failed_comprehension' for g in ledger),1)
                self.assertEqual(sum(g['status']=='complete' for g in ledger),4)
                all_rows=pd.read_csv(directory/'all_candidate_rows.csv')
                self.assertIn('b000_control_minimal',set(all_rows.group_id))
                progress=json.loads((directory/'progress.json').read_text())
                self.assertEqual(progress['remaining'],0)
                self.assertEqual(progress['group'],4)
                report=s.verification_report(directory,c)
                self.assertIn('1 failed groups',report)
                self.assertIn('p-values are withheld',report)
                resumed,_=await s.run_study(tmp,c,render=False)
                keys=['group_id','week','role']
                pd.testing.assert_frame_equal(frame.sort_values(keys).reset_index(drop=True),
                                              resumed.sort_values(keys).reset_index(drop=True))
                exhaust[0]=True
                with tempfile.TemporaryDirectory() as bounded:
                    with patch.object(s.Runner,'_request',injected):
                        with self.assertRaisesRegex(s.ExperimentStopped,'Replacement limit reached'):
                            await s.run_study(bounded,c,render=False)
                    ledger=json.loads((s.latest_run(bounded,c)/'group_attempts.json').read_text())
                    failed=[g for g in ledger if g['status']=='failed_comprehension']
                    self.assertEqual(len(failed),2)
                    self.assertFalse(any(g['replacement_index']>1 for g in ledger))
        asyncio.run(run())

    def test_rate_limit_recovery_and_quota_stop(self):
        async def run():
            calls=[]
            quota=[False]
            def handler(request):
                calls.append(json.loads(request.content))
                if len(calls)==1 or quota[0]:
                    code='insufficient_quota' if quota[0] else 'rate_limit_exceeded'
                    return httpx.Response(429,headers={'retry-after':'0'},json={'error':{
                        'code':code,'type':code,'message':'test-not-real secret must not be saved'}})
                return httpx.Response(200,json=dict(id='resp_throttle',object='response',created_at=1,
                    model=s.MODEL,status='completed',output=[dict(type='message',id='msg_throttle',
                    role='assistant',status='completed',content=[dict(type='output_text',
                    text=json.dumps(s.CHECK_ANSWERS),annotations=[])])],usage=dict(input_tokens=100,
                    output_tokens=50,total_tokens=150,input_tokens_details={'cached_tokens':0},
                    output_tokens_details={'reasoning_tokens':10})))
            client=AsyncOpenAI(api_key='test-not-real',max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                c=config(mode='api',max_transport_retries=2,retry_backoff_s=0)
                args=(s.Condition(False,'minimal'),{'kind':'rules'},s.CHECK_TASK)
                with tempfile.TemporaryDirectory() as tmp:
                    runner=s.Runner(tmp,c,client,render=False)
                    runner.progress=s.RunProgress(1,'api',render=False)
                    result=await runner.request(*args)
                    self.assertEqual(result['status'],'ok')
                    self.assertEqual(len(calls),2)
                    self.assertEqual(calls[0]['input'],calls[1]['input'])
                    self.assertEqual(runner.progress.snapshot()['remaining'],0)
                    records=[json.loads(p.read_text()) for p in (Path(tmp)/'requests').glob('*.json')]
                    self.assertTrue(any(r.get('error_code')=='rate_limit_exceeded' for r in records))
                    self.assertNotIn('test-not-real',json.dumps(records))
                    self.assertAlmostEqual(runner.charged,sum(r['budget_charge_usd'] for r in records))
                    resumed=s.Runner(tmp,c,client,render=False)
                    resumed.progress=s.RunProgress(1,'api',render=False)
                    await resumed.request(*args)
                    self.assertEqual(len(calls),2)
                quota[0]=True
                with tempfile.TemporaryDirectory() as tmp:
                    runner=s.Runner(tmp,c,client,render=False)
                    runner.progress=s.RunProgress(1,'api',render=False)
                    with self.assertRaisesRegex(s.ExperimentStopped,'insufficient_quota'):
                        await runner.request(*args)
                    self.assertEqual(len(calls),3)
            finally:
                await client.close()
        asyncio.run(run())

    def test_shared_pacing_and_classification(self):
        async def run():
            import time
            with tempfile.TemporaryDirectory() as tmp:
                runner=s.Runner(tmp,config(request_interval_s=.02),render=False)
                runner.cooldown_until=time.monotonic()+.02
                started=time.monotonic()
                await asyncio.gather(runner.wait_for_send(),runner.wait_for_send())
                self.assertGreaterEqual(time.monotonic()-started,.035)
            self.assertFalse(s.transient_error(dict(status='api_error',http_status=429)))
            self.assertTrue(s.transient_error(dict(status='api_error',http_status=429,legacy_unknown_429=True)))
            self.assertFalse(s.transient_error(dict(status='api_error',http_status=429,
                legacy_unknown_429=True,error_code='insufficient_quota')))
        asyncio.run(run())

    def test_spending_guard_before_call(self):
        async def run():
            with tempfile.TemporaryDirectory() as tmp:
                runner=s.Runner(tmp,config(mode='api',budget_usd=.001),None,render=False)
                runner.progress=s.RunProgress(1,'api',render=False)
                with self.assertRaisesRegex(s.ExperimentStopped,'Local spending guard'):
                    await runner.request(s.Condition(False,'low'),{'id':1},s.CHECK_TASK)
                self.assertEqual(len(list((Path(tmp)/'requests').glob('*.json'))),0)
        asyncio.run(run())

    def test_parallel_games_preserve_histories_and_week_barriers(self):
        async def run():
            original = s.Runner._request
            active = peak = 0
            async def delayed(runner, condition, identity, task, state=None, history=None):
                nonlocal active, peak
                active += 1
                peak = max(peak, active)
                try:
                    if identity.get('kind') == 'game':
                        self.assertEqual(len(history), identity['week']-1)
                        self.assertTrue(all(h['role'] == identity['role'] for h in history))
                    await asyncio.sleep(.001)
                    return await original(runner, condition, identity, task, state, history)
                finally:
                    active -= 1
            with tempfile.TemporaryDirectory() as tmp:
                with patch.object(s.Runner, '_request', delayed):
                    parallel, directory = await s.run_study(tmp, config(stage='game', weeks=16,
                        max_concurrent_requests=8), render=False)
                self.assertEqual(peak, 8)
                self.assertEqual(active, 0)
                serial, _ = await s.run_study(tmp, config(stage='game', weeks=16,
                    max_concurrent_requests=1), render=False)
                keys = ['group_id','week','role']
                pd.testing.assert_frame_equal(parallel.sort_values(keys).reset_index(drop=True),
                                              serial.sort_values(keys).reset_index(drop=True))
                progress = json.loads((directory/'progress.json').read_text())
                self.assertEqual(progress['group'], 4)
                self.assertEqual(progress['active_requests'], 0)
                self.assertTrue(all(w == 16 for w in progress['group_weeks'].values()))
        asyncio.run(run())

    def test_concurrent_reservations_and_failure_drain(self):
        async def run():
            calls = []
            async def handler(request):
                calls.append(json.loads(request.content))
                await asyncio.sleep(.02)
                return httpx.Response(200,json=dict(id='resp_concurrent',object='response',created_at=1,
                    model=s.MODEL,status='completed',output=[dict(type='message',id='msg_concurrent',
                    role='assistant',status='completed',content=[dict(type='output_text',
                    text=json.dumps(s.CHECK_ANSWERS),annotations=[])])],usage=dict(input_tokens=100,
                    output_tokens=20,total_tokens=120,input_tokens_details={'cached_tokens':0},
                    output_tokens_details={'reasoning_tokens':0})))
            client=AsyncOpenAI(api_key='test-not-real',max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    c=config(mode='api',max_output_tokens=25000,budget_usd=.025,max_concurrent_requests=8)
                    runner=s.Runner(tmp,c,client,render=False)
                    runner.progress=s.RunProgress(16,'api',render=False)
                    with self.assertRaisesRegex(s.ExperimentStopped,'Local spending guard'):
                        await s.collect_requests(runner.request(s.Condition(False,'low'),
                            {'id':i},s.CHECK_TASK) for i in range(16))
                    # Two full output reservations fit; the third blocks further calls.
                    self.assertEqual(len(calls),2)
                    self.assertEqual(runner.progress.active,0)
                    records=[json.loads(p.read_text()) for p in (Path(tmp)/'requests').glob('*.json')]
                    self.assertEqual(len(records),2)
                    self.assertTrue(all(r['status']=='ok' for r in records))
                    self.assertAlmostEqual(runner.charged,sum(r['budget_charge_usd'] for r in records))
                    self.assertLess(runner.charged,c['budget_usd'])
            finally:
                await client.close()
        asyncio.run(run())

    def test_analysis_uses_blocks_and_withholds_selected_sample(self):
        rows=[]
        for b in range(8):
            for c in s.CONDITIONS:
                beta=.2+.01*b+.2*c.trained+.2*(c.effort==s.EFFORT_LEVELS[1])*c.trained
                for role in s.ROLES:
                    for week in range(16):
                        group=f'{b}_{c.trained}_{c.effort}'
                        rows.append(dict(agent_id=group+'_'+role,group_id=group,block=b,
                            trained=c.trained,effort=c.effort,role=role,week=week,
                            order=beta,demand=4))
        frame=pd.DataFrame(rows)
        def fit(f):
            return dict(beta=f.order.iloc[0],usable=True)
        with patch.object(s,'estimate_beta',side_effect=fit):
            fits,groups,tests=s.analyze_game(frame,config(mode='api',weeks=16,groups_per_cell=8))
            self.assertEqual(len(groups),32)
            self.assertEqual(len(fits),128)
            self.assertTrue((tests.complete_blocks==8).all())
            self.assertAlmostEqual(tests.estimate.iloc[0],.3)
            self.assertAlmostEqual(tests.estimate.iloc[1],-.2)
            self.assertEqual(tests.hypothesis.iloc[1], 'H2_API_minimal_minus_low_trained')
            replaced=frame.assign(replacement_index=1)
            _,_,selected=s.analyze_game(replaced,config(mode='api',weeks=16,groups_per_cell=8))
            self.assertTrue(selected.p_holm.isna().all())
            self.assertTrue((tests.p_holm<.05).all())
        def excluded_fit(f):
            return dict(beta=f.order.iloc[0],usable=f.agent_id.iloc[0]!=frame.agent_id.iloc[0])
        with patch.object(s,'estimate_beta',side_effect=excluded_fit):
            _,_,tests=s.analyze_game(frame,config(mode='api',weeks=16,groups_per_cell=8))
            self.assertTrue(tests.p_holm.isna().all())
            self.assertTrue((tests.complete_blocks==7).all())

if __name__=='__main__':
    unittest.main(verbosity=2)
