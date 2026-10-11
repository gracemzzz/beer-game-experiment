import asyncio,copy,json,tempfile,unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import httpx
from openai import AsyncOpenAI
from beergame_study import Config,run,run_directory,report,software_checks
from beergame_study.game import BeerGame,ROLES,calibration_states
from beergame_study.api import Gateway,StudyStopped
from beergame_study.runner import decision
from beergame_study.prompts import SCHEMA,make_messages
from beergame_study.analysis import hypothesis_table,ratio

class Tests(unittest.TestCase):
    def test_physics_and_shared_inventory(self):
        game=BeerGame()
        for _ in range(12):
            states=game.observe(4)
            self.assertTrue(all(s['inventory']==12 and s['backlog']==0 for s in states))
            self.assertTrue(all(s['shared_inventory']==dict.fromkeys(ROLES,12) for s in states))
            game.commit([4]*4)
        before=copy.deepcopy(game.__dict__);game.observe(4)
        for invalid in (-1,True,2.5,100001):
            snap=copy.deepcopy(game.__dict__)
            with self.assertRaises(AssertionError):game.commit([invalid,4,4,4])
            self.assertEqual(game.week,snap['week'])
            np.testing.assert_equal(game.outstanding,snap['outstanding'])
        game.commit([80,4,4,4]) # 40 is no longer a ceiling

    def test_offline_checks_and_no_order_anchor(self):
        self.assertTrue(software_checks().passed.all())
        self.assertNotIn('maximum',SCHEMA['properties']['order'])
        state=calibration_states()[0]
        msgs=make_messages(state,[],64,'plan')
        self.assertNotIn('100000',json.dumps(msgs))
        self.assertNotIn('40 units',json.dumps(msgs))
        self.assertTrue(np.isnan(ratio([1,2,3],[4,4,4])))

    def test_offline_game_resume_and_reports(self):
        async def go():
            with tempfile.TemporaryDirectory() as tmp:
                c=Config(stage='game',weeks=20,request_interval_s=0)
                p=await run(tmp,c,render=False)
                f=pd.read_csv(p/'rounds.csv');tail=pd.read_csv(p/'continuation.csv')
                self.assertEqual(len(f),160);self.assertEqual(len(tail),96)
                self.assertEqual(set(f.condition),{'short','adequate'})
                a=f[f.condition=='short'].sort_values(['week','role'])
                b=f[f.condition=='adequate'].sort_values(['week','role'])
                self.assertEqual(a.order.tolist(),b.order.tolist()) # no synthetic H1/H2
                self.assertEqual(len(list((p/'requests').glob('*.json'))),264)
                again=await run(tmp,replace(c,budget_usd=2.),render=False)
                self.assertEqual(p,again)
                self.assertEqual(json.loads((p/'progress.json').read_text())['cached'],264)
                text=report(p)
                self.assertIn('SYNTHETIC',text)
                self.assertTrue(pd.read_csv(p/'hypotheses.csv').p_raw.isna().all())
                for name in ('REPORT.docx','DETAILS.xlsx','bullwhip.png'):self.assertTrue((p/name).exists())
        asyncio.run(go())

    def test_offline_calibration_is_not_live_validation(self):
        async def go():
            with tempfile.TemporaryDirectory() as tmp:
                p=await run(tmp,Config(request_interval_s=0),render=False)
                rec=json.loads((p/'calibration_recommendation.json').read_text())
                self.assertFalse(rec['manipulation_screen_passed'])
                self.assertEqual(len(pd.read_csv(p/'calibration.csv')),96)
                self.assertEqual(len(list((p/'requests').glob('*.json'))),192)
                self.assertIn('SOFTWARE',report(p))
        asyncio.run(go())

    def test_game_cannot_use_missing_or_offline_calibration(self):
        async def go():
            with tempfile.TemporaryDirectory() as tmp:
                with self.assertRaisesRegex(StudyStopped,'calibration'):
                    await run(tmp,Config(mode='api',stage='game'),render=False)
        asyncio.run(go())

    def test_h2_not_blocked_by_missing_beta(self):
        rows=[]
        for b in range(10):
            for c in ('short','adequate'):
                rows.append(dict(block=b,condition=c,group_beta=np.nan,
                    total_scored_cost=100+b+10*(c=='short')))
        config={'mode':'api','groups_per_condition':10}
        tests=hypothesis_table(pd.DataFrame(rows),config,True,False)
        self.assertTrue(np.isnan(tests.p_raw.iloc[0]))
        self.assertLess(tests.p_holm.iloc[1],.05)
        self.assertTrue(hypothesis_table(pd.DataFrame(rows),config,True,True).p_raw.isna().all())
        self.assertTrue(hypothesis_table(pd.DataFrame(rows),config,False,False).p_raw.isna().all())

    def test_api_caps_truncated_plan_and_cache(self):
        async def go():
            calls=[];state=calibration_states()[0]
            answer={'order':12,**{'observed_'+k:state[k] for k in ('demand','inventory','backlog','supply_line')}}
            def handler(request):
                payload=json.loads(request.content);calls.append(payload)
                final='text' in payload
                return httpx.Response(200,json=dict(id='resp_test',object='response',created_at=1,
                    model=Config().model,status='completed' if final else 'incomplete',
                    incomplete_details=None if final else {'reason':'max_output_tokens'},
                    output=[dict(type='message',id='msg_test',role='assistant',status='completed',
                        content=[dict(type='output_text',text=json.dumps(answer) if final else 'Provisional order: 12. Stock',annotations=[])])],
                    usage=dict(input_tokens=100,output_tokens=60 if final else 64,total_tokens=160 if final else 164,
                        input_tokens_details={'cached_tokens':0},output_tokens_details={'reasoning_tokens':0})))
            client=AsyncOpenAI(api_key='fake-local-only',max_retries=0,http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    c=Config(mode='api',request_interval_s=0)
                    g=Gateway(tmp,c,client)
                    a=await decision(g,state,[],64,{'x':1})
                    self.assertEqual(a['order'],12);self.assertTrue(a['plan_truncated'])
                    self.assertEqual([x['max_output_tokens'] for x in calls],[64,192])
                    self.assertTrue(all(x['reasoning']=={'effort':'none'} for x in calls))
                    self.assertEqual(len(calls),2)
                    resumed=Gateway(tmp,replace(c,budget_usd=2),client)
                    await decision(resumed,state,[],64,{'x':1})
                    self.assertEqual(len(calls),2)
                    self.assertAlmostEqual(g.charged,resumed.charged)
            finally:await client.close()
        asyncio.run(go())

    def test_rate_limit_quota_and_budget_guard(self):
        async def go():
            calls=[];quota=[False]
            def handler(request):
                calls.append(json.loads(request.content))
                if len(calls)==1 or quota[0]:
                    code='insufficient_quota' if quota[0] else 'rate_limit_exceeded'
                    return httpx.Response(429,headers={'retry-after':'0'},json={'error':{'code':code,'message':'fake secret never saved'}})
                return httpx.Response(200,json=dict(id='resp_x',object='response',created_at=1,model=Config().model,
                    status='completed',output=[],usage=dict(input_tokens=10,output_tokens=0,total_tokens=10)))
            client=AsyncOpenAI(api_key='fake-local-only',max_retries=0,http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    c=Config(mode='api',request_interval_s=0)
                    g=Gateway(tmp,c,client)
                    await g.request({'test':1},[],64)
                    self.assertEqual(len(calls),2)
                    self.assertEqual(calls[0],calls[1])
                    self.assertNotIn('fake secret',''.join(p.read_text() for p in (Path(tmp)/'requests').glob('*.json')))
                quota[0]=True
                with tempfile.TemporaryDirectory() as tmp:
                    with self.assertRaisesRegex(StudyStopped,'insufficient_quota'):
                        await Gateway(tmp,c,client).request({'test':2},[],64)
                self.assertEqual(len(calls),3)
                with tempfile.TemporaryDirectory() as tmp:
                    with self.assertRaisesRegex(StudyStopped,'spending'):
                        await Gateway(tmp,replace(c,budget_usd=.0000001),client).request({'test':3},[],64)
                self.assertEqual(len(calls),3)
            finally:await client.close()
        asyncio.run(go())

    def test_config_identity_and_invalid_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=Config()
            self.assertEqual(run_directory(tmp,c),run_directory(tmp,replace(c,budget_usd=2,request_interval_s=3)))
            self.assertNotEqual(run_directory(tmp,c),run_directory(tmp,replace(c,short_tokens=32)))
            with self.assertRaises(AssertionError):replace(c,short_tokens=256,adequate_tokens=64).validate()

    def test_group_replacement_is_audited_not_selected_by_orders(self):
        from beergame_study import runner
        from beergame_study.api import GroupFailed
        async def go():
            original=runner.decision
            async def injected(gateway,state,history,budget,identity):
                if identity.get('group')=='b000_short' and identity.get('week')==5:
                    raise GroupFailed('Injected invalid final answer')
                return await original(gateway,state,history,budget,identity)
            with tempfile.TemporaryDirectory() as tmp:
                with patch.object(runner,'decision',injected):
                    p=await run(tmp,Config(stage='game',weeks=20,request_interval_s=0),render=False)
                ledger=json.loads((p/'group_attempts.json').read_text())
                self.assertEqual(sum(x['status']=='failed' for x in ledger),1)
                self.assertEqual(sum(x['status']=='complete' for x in ledger),2)
                f=pd.read_csv(p/'rounds.csv')
                self.assertIn('b000_short_replacement1',set(f.group_id))
                self.assertNotIn('b000_short',set(f.group_id))
                self.assertIn('b000_short',set(pd.read_csv(p/'all_candidate_rounds.csv').group_id))
                self.assertEqual(json.loads((p/'progress.json').read_text())['remaining_requests'],0)
        asyncio.run(go())

    def test_emergency_order_is_never_clipped(self):
        from beergame_study.prompts import validate_decision
        state=calibration_states()[0]
        self.assertFalse(validate_decision([],state))
        async def go():
            class Fake:
                config=Config()
                async def request(self,identity,messages,limit,schema=None,synthetic=None):
                    answer=dict(order=100001,**{'observed_'+k:state[k] for k in ('demand','inventory','backlog','supply_line')})
                    return dict(response_status='completed',text=json.dumps(answer),usage={'output_tokens':10},elapsed_s=0)
            with self.assertRaisesRegex(StudyStopped,'Emergency scale'):
                await decision(Fake(),state,[],64,{'id':1})
        asyncio.run(go())

    def test_pending_usage_is_not_silently_retried(self):
        from beergame_study.api import digest,save
        async def go():
            with tempfile.TemporaryDirectory() as tmp:
                c=Config(mode='api',request_interval_s=0)
                key=digest(dict(identity={'x':1},messages=[],limit=64,schema=None,model=c.model))
                save(Path(tmp)/'requests'/f'{key}_0.json',dict(identity={'x':1},status='pending',charge_usd=.01))
                g=Gateway(tmp,c)
                self.assertAlmostEqual(g.charged,.01)
                with self.assertRaisesRegex(StudyStopped,'Saved unresolved'):
                    await g.request({'x':1},[],64)
        asyncio.run(go())

    def test_optional_debriefs_are_separate_from_decisions(self):
        async def go():
            with tempfile.TemporaryDirectory() as tmp:
                p=await run(tmp,Config(stage='game',weeks=20,collect_debriefs=True,request_interval_s=0),render=False)
                self.assertEqual(len(json.loads((p/'debriefs.json').read_text())),8)
                self.assertEqual(len(pd.read_csv(p/'rounds.csv')),160)
                self.assertEqual(json.loads((p/'progress.json').read_text())['requests_done'],272)
                self.assertIn('Optional debriefs',report(p))
        asyncio.run(go())

    def test_fixed_calibration_honors_caps_and_retains_reference(self):
        from beergame_study import runner
        async def go():
            with tempfile.TemporaryDirectory() as tmp:
                p=await run(tmp,Config(calibration_method='fixed',short_tokens=96,adequate_tokens=240,request_interval_s=0),render=False)
                f=pd.read_csv(p/'calibration.csv')
                self.assertEqual(len(f),72)
                self.assertEqual(f.groupby('screen').plan_limit.first().to_dict(),{'adequate':240,'benchmark':480,'short':96})
                self.assertEqual(json.loads((p/'progress.json').read_text())['requests_done'],144)
                self.assertFalse(json.loads((p/'calibration_recommendation.json').read_text())['manipulation_screen_passed'])
                parent=Path(tmp)/'parent';parent.mkdir()
                (parent/'manifest.json').write_text(json.dumps(dict(config={'mode':'api','model':Config().model},protocol=runner.PROTOCOL)))
                (parent/'progress.json').write_text(json.dumps({'phase':'complete'}))
                pd.DataFrame([dict(screen='reference',truncated_fraction=0)]).to_csv(parent/'calibration_summary.csv',index=False)
                c=Config(mode='api',calibration_method='fixed',calibration_parent=str(parent),short_tokens=96,adequate_tokens=240)
                async def fake(gateway,state,history,budget,identity):
                    return dict(order=8,plan_tokens=96 if budget==96 else 180,final_tokens=50,plan_limit=budget,plan_truncated=budget==96,latency_s=0)
                g=Gateway(p,c)
                with patch.object(runner,'decision',fake):await runner.calibrate(g,p,c)
                rec=json.loads((p/'calibration_recommendation.json').read_text())
                self.assertTrue(rec['manipulation_screen_passed'])
                self.assertEqual(rec['calibration_parent'],str(parent))
        asyncio.run(go())

    def test_onboarding_retry_persists_and_does_not_replace_groups(self):
        from beergame_study.prompts import RULES,RULE_ANSWERS,rules_messages
        from beergame_study.api import digest,save
        async def go():
            with tempfile.TemporaryDirectory() as tmp:
                c=Config(stage='game',weeks=20,request_interval_s=0)
                directory=run_directory(tmp,c)
                identity=dict(group='b000_short',role='retailer',stage='rules',rules_attempt=1)
                messages=rules_messages('retailer')
                key=digest(dict(identity=identity,messages=messages,limit=192,schema=RULES,model=c.model))
                wrong=dict(RULE_ANSWERS,objective_includes_continuation=False)
                save(directory/'requests'/f'{key}_0.json',dict(identity=identity,status='ok',response_status='completed',text=json.dumps(wrong),charge_usd=0))
                directory=await run(tmp,c,render=False)
                checks=json.loads((directory/'rules_validation.json').read_text())
                self.assertEqual(len(checks),9)
                self.assertEqual(sum(not x['passed'] for x in checks),1)
                self.assertEqual(sum(x['attempt']==2 for x in checks),1)
                ledger=json.loads((directory/'group_attempts.json').read_text())
                self.assertTrue(all(x['replacement']==0 and x['status']=='complete' for x in ledger))
                self.assertEqual(json.loads((directory/'progress.json').read_text())['requests_done'],265)
                await run(tmp,c,render=False)
                self.assertEqual(json.loads((directory/'progress.json').read_text())['cached'],265)
                self.assertEqual(len(json.loads((directory/'rules_validation.json').read_text())),9)
                self.assertIn('7/8 first attempts passed',report(directory))
        asyncio.run(go())

    def test_persistent_rules_failure_stops_before_any_order(self):
        from beergame_study.prompts import RULES,RULE_ANSWERS,rules_messages
        from beergame_study.api import digest,save
        async def go():
            with tempfile.TemporaryDirectory() as tmp:
                c=Config(stage='game',weeks=20,request_interval_s=0)
                directory=run_directory(tmp,c)
                for attempt in (1,2):
                    identity=dict(group='b000_short',role='retailer',stage='rules',rules_attempt=attempt)
                    messages=rules_messages('retailer',retry=attempt==2)
                    key=digest(dict(identity=identity,messages=messages,limit=192,schema=RULES,model=c.model))
                    save(directory/'requests'/f'{key}_0.json',dict(identity=identity,status='ok',response_status='completed',text=json.dumps(dict(RULE_ANSWERS,objective_includes_continuation=False)),charge_usd=0))
                with self.assertRaisesRegex(StudyStopped,'Onboarding rules check stopped after 2 attempts'):
                    await run(tmp,c,render=False)
                self.assertFalse((directory/'rounds.csv').exists())
                self.assertFalse((directory/'all_candidate_rounds.csv').exists())
                records=[json.loads(p.read_text()) for p in (directory/'requests').glob('*.json')]
                self.assertTrue(all(r['identity']['stage']=='rules' for r in records))
                self.assertFalse(any('replacement' in r['identity']['group'] for r in records))
                self.assertIn('objective_includes_continuation',report(directory))
        asyncio.run(go())

    def test_named_rules_fields_and_calibration_compatibility(self):
        from beergame_study.prompts import RULES,RULE_ANSWERS,rules_messages
        from beergame_study.compatibility import decision_fingerprint,calibration_code_compatible
        task=json.loads(rules_messages('retailer')[1]['content'])
        self.assertEqual(set(task['questions']),set(RULE_ANSWERS))
        self.assertIn('agent-controlled weeks +',task['rule_reminders']['score_definition'])
        self.assertNotIn('const',RULES['properties']['objective_includes_continuation'])
        with tempfile.TemporaryDirectory() as tmp:
            proof={'decision_fingerprint':decision_fingerprint(),'calibration_source_sha256':{'example':'old'}}
            (Path(tmp)/'onboarding_compatibility.json').write_text(json.dumps(proof))
            m={'source_sha256':{'example':'old'}}
            self.assertTrue(calibration_code_compatible(tmp,m))
            with patch('beergame_study.compatibility.decision_fingerprint',return_value='changed-decision-prompt'):
                self.assertFalse(calibration_code_compatible(tmp,m))
            self.assertFalse(calibration_code_compatible(tmp,{'source_sha256':{'example':'different'}}))

if __name__=='__main__':unittest.main(verbosity=2)
