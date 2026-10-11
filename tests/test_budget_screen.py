import asyncio
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from budget_model_screen import BudgetGateway, BudgetStop, cases, messages, design, MODELS

class Response:
    def __init__(self,reasoning=0):self.reasoning=reasoning
    def model_dump(self,mode):
        return dict(status='completed',output=[dict(type='message',content=[dict(type='output_text',text='ok')])],
            usage=dict(input_tokens=100,output_tokens=10,input_tokens_details=dict(cached_tokens=0),
                       output_tokens_details=dict(reasoning_tokens=self.reasoning)))

class BudgetScreenTests(unittest.IsolatedAsyncioTestCase):
    async def test_budget_blocks_before_network(self):
        with tempfile.TemporaryDirectory() as d:
            create=AsyncMock(return_value=Response());g=BudgetGateway(SimpleNamespace(responses=SimpleNamespace(create=create)),d,1e-8)
            with self.assertRaises(BudgetStop):await g.request(next(iter(MODELS)),{'i':1},[{'role':'user','content':'x'}],96)
            create.assert_not_awaited()

    async def test_cached_success_not_rebilled(self):
        with tempfile.TemporaryDirectory() as d:
            create=AsyncMock(return_value=Response());client=SimpleNamespace(responses=SimpleNamespace(create=create))
            g=BudgetGateway(client,d,.1);r=await g.request(next(iter(MODELS)),{'i':1},[{'role':'user','content':'x'}],96)
            h=BudgetGateway(client,d,.1);s=await h.request(next(iter(MODELS)),{'i':1},[{'role':'user','content':'x'}],96)
            self.assertEqual(r,s);self.assertAlmostEqual(g.charged,h.charged);self.assertEqual(create.await_count,1)

    async def test_reasoning_violation_stays_stopped_on_resume(self):
        with tempfile.TemporaryDirectory() as d:
            create=AsyncMock(return_value=Response(1));client=SimpleNamespace(responses=SimpleNamespace(create=create))
            for _ in range(2):
                g=BudgetGateway(client,d,.1)
                with self.assertRaises(BudgetStop):await g.request(next(iter(MODELS)),{'i':1},[{'role':'user','content':'x'}],96)
            self.assertEqual(create.await_count,1)

    def test_fixed_screen_does_not_reveal_expected_order(self):
        c=cases();self.assertEqual(len(c),12);self.assertEqual(sum(x['factory_shortage'] for x in c),4)
        self.assertEqual(len([x for x in c if x['source']=='new hypothetical state']),4)
        msg=messages(c[0],96,'plan','clarified')
        self.assertIn('week t+3',msg[0]['content']);self.assertNotIn('factory_shortage',msg[1]['content'])
        self.assertNotIn('eligibility',msg[1]['content'])
        self.assertEqual(design()['screen_allowance_usd'],.45)

if __name__=='__main__':unittest.main()
