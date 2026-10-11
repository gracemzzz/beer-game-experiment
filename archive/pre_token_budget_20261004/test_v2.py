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
import beer_game_v2 as s


def config(**changes):
    c = dict(mode='offline', stage='diagnostics', model=s.MODEL, groups_per_cell=1,
             weeks=24, replicate_id='test', seed=314, budget_usd=2.,
             max_output_tokens=8192, timeout_s=180)
    c.update(changes)
    return c

class Tests(unittest.TestCase):
    def test_notebook_and_conservation(self):
        nbformat.validate(nbformat.read(Path(__file__).with_name('thoughts_reflection_experiment_v2.ipynb'), as_version=4))
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
                    self.assertEqual(progress['cached'],64 if stage=='diagnostics' else 4*4*25)
                    report=s.make_report(first,directory,c)
                    self.assertIn('Conclusions',report)
                    self.assertIn('SYNTHETIC',report)
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

    def test_spending_guard_before_call(self):
        async def run():
            with tempfile.TemporaryDirectory() as tmp:
                runner=s.Runner(tmp,config(mode='api',budget_usd=.001),None,render=False)
                runner.progress=s.RunProgress(1,'api',render=False)
                with self.assertRaisesRegex(s.ExperimentStopped,'Local spending guard'):
                    await runner.request(s.Condition(False,'low'),{'id':1},s.CHECK_TASK)
                self.assertEqual(len(list((Path(tmp)/'requests').glob('*.json'))),0)
        asyncio.run(run())

    def test_analysis_uses_blocks_and_withholds_selected_sample(self):
        rows=[]
        for b in range(8):
            for c in s.CONDITIONS:
                beta=.2+.01*b+.2*c.trained+.2*(c.effort=='high')*c.trained
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
            self.assertTrue((tests.p_holm<.05).all())
        def excluded_fit(f):
            return dict(beta=f.order.iloc[0],usable=f.agent_id.iloc[0]!=frame.agent_id.iloc[0])
        with patch.object(s,'estimate_beta',side_effect=excluded_fit):
            _,_,tests=s.analyze_game(frame,config(mode='api',weeks=16,groups_per_cell=8))
            self.assertTrue(tests.p_holm.isna().all())
            self.assertTrue((tests.complete_blocks==7).all())

if __name__=='__main__':
    unittest.main(verbosity=2)
