import asyncio
import json
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import budget_followup_study as study
from budget_model_screen import BudgetStop, QUIZ_EXPECTED

class FakeGateway:
    bad_final=False
    def __init__(self,client,directory,allowance,**kwargs):
        self.finished=0;self.cached=0;self.charged=0.;self.callback=lambda:None
    async def request(self,model,identity,messages,limit,schema=None):
        stage=identity['stage'];self.finished+=1
        if stage=='rules':text=json.dumps(QUIZ_EXPECTED);tokens=60;status='completed'
        else:
            payload=json.loads(messages[1]['content']);state=payload['current_state']
            q=max(0,int(round(state['demand']+.35*(24-state['net_inventory']-.65*state['supply_line']))))
            if stage=='plan':
                text=f'Provisional order: {q}.';tokens=min(limit,150);status='incomplete' if limit<150 else 'completed'
            else:
                answer=dict(order=q,**{'observed_'+k:state[k] for k in ('demand','inventory','backlog','supply_line')})
                if self.bad_final:answer['observed_backlog']+=1
                text=json.dumps(answer);tokens=39;status='completed'
        self.callback()
        return dict(status='ok',response_status=status,incomplete_reason='max_output_tokens' if status=='incomplete' else None,
            refused=False,text=text,usage=dict(output_tokens=tokens),elapsed_s=0.)

class FollowupTests(unittest.IsolatedAsyncioTestCase):
    async def test_calibration_then_complete_paired_game_counts(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(study,'BASE',Path(temp)),patch.object(study,'BudgetGateway',FakeGateway),patch.object(study,'report'):
            choice=dict(model='gpt-5.4-nano-2026-03-17',prompt='clarified')
            cal=await study.calibrate(None,choice)
            r=json.loads((cal/'calibration_recommendation.json').read_text())
            self.assertTrue(r['manipulation_screen_passed'])
            game=await study.play(None,choice,cal,groups=2,allowance=.5)
            p=json.loads((game/'progress.json').read_text())
            self.assertEqual(p['groups_complete'],4);self.assertEqual(p['decisions'],576)
            self.assertEqual(p['requests_done'],1168);self.assertEqual(p['remaining_requests'],0)
            self.assertEqual(len(study.pd.read_csv(game/'rounds.csv')),640)
            self.assertEqual(len(study.pd.read_csv(game/'continuation.csv')),192)

    async def test_failed_calibration_never_starts_games(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            (d/'calibration_recommendation.json').write_text(json.dumps({'manipulation_screen_passed':False}))
            (d/'manifest.json').write_text(json.dumps({'config':{'model':'gpt-5.4-nano-2026-03-17','prompt_variant':'clarified'}}))
            with patch.object(study,'BudgetGateway') as gateway:
                with self.assertRaises(BudgetStop):await study.play(None,dict(model='gpt-5.4-nano-2026-03-17',prompt='clarified'),d,2,.5)
                gateway.assert_not_called()

    async def test_bad_readback_not_fabricated(self):
        g=FakeGateway(None,None,None);g.bad_final=True
        state=study.calibration_cases()[0]['state']
        with self.assertRaises(BudgetStop):await study.decision(g,'gpt-5.4-nano-2026-03-17','clarified',state,[],96,dict(case=0))

if __name__=='__main__':unittest.main()
