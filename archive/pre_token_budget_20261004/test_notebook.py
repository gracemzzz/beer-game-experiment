"""Offline checks: python test_notebook.py (no real API requests)."""
import asyncio
import ast
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

import httpx
import nbformat
import numpy as np
import pandas as pd

NOTEBOOK = Path(__file__).with_name('thoughts_reflection_experiment.ipynb')
notebook = nbformat.read(NOTEBOOK, as_version=4)
ns = {'__name__': __name__}
for cell in notebook.cells:
    if 'definitions' in cell.metadata.get('tags', []):
        exec(compile(cell.source, str(NOTEBOOK), 'exec'), ns)
for cell in notebook.cells:
    if 'analysis' in cell.metadata.get('tags', []):
        module = ast.parse(cell.source)
        module.body = [node for node in module.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        exec(compile(module, str(NOTEBOOK), 'exec'), ns)
run_cell = next(c.source for c in notebook.cells if 'run' in c.metadata.get('tags', []))
exec(run_cell.split('\nrounds, run_dir = await')[0], ns)


class NotebookTests(unittest.TestCase):
    def test_notebook_schema(self):
        nbformat.validate(notebook)

    def test_equilibrium_and_goods_conservation(self):
        game = ns['BeerGame']()
        for _ in range(20):
            states = game.observe(4)
            self.assertEqual([s['inventory'] for s in states], [12]*4)
            self.assertEqual([s['supply_line'] for s in states], [8]*4)
            self.assertEqual([s['backlog'] for s in states], [0]*4)
            game.commit([4]*4)
        rng = np.random.default_rng(7)
        for _ in range(200):
            previous_inventory = game.inventory.copy()
            previous_backlog = game.backlog.copy()
            previous_outstanding = game.outstanding.copy()
            states = game.observe(int(rng.integers(0, 100)))
            for i, s in enumerate(states):
                self.assertEqual(s['inventory'], previous_inventory[i]+s['received']-s['shipped'])
                self.assertEqual(s['backlog'], previous_backlog[i]+s['demand']-s['shipped'])
                self.assertEqual(s['supply_line'], previous_outstanding[i]-s['received'])
            orders = [int(x) for x in rng.integers(0, 150, 4)]
            game.commit(orders)  # also checks every outstanding-stock identity

    def test_shipping_and_production_delays(self):
        game = ns['BeerGame']()
        game.observe(4)
        game.commit([4, 4, 4, 20])
        for week in (2, 3):
            states = game.observe(4)
            self.assertEqual(states[3]['received'], 4)
            game.commit([4]*4)
        states = game.observe(4)
        self.assertEqual(states[3]['received'], 20)

    def test_beta_recovery_and_nonidentification(self):
        rng = np.random.default_rng(12)
        n = 150
        demand = rng.uniform(2, 20, n)
        ni = rng.uniform(-30, 70, n)
        sl = rng.uniform(0, 70, n)
        for beta in (0., .15, .65, 1.4):
            params = [.55, .4, beta, 45.]
            orders = ns['predicted_orders'](params, demand, ni, sl)
            self.assertTrue((orders == 0).any())
            frame = pd.DataFrame(dict(week=np.arange(n), demand=demand,
                                      net_inventory=ni, supply_line=sl, order=orders))
            result = ns['estimate_beta'](frame)
            self.assertAlmostEqual(result['beta'], beta, places=5)
            self.assertTrue(result['usable'], result)
        frame['order'] = 4
        self.assertFalse(ns['estimate_beta'](frame)['usable'])

    def test_hypothesis_signs_and_cluster_unit(self):
        values = {(False, 60): .2, (True, 60): .5,
                  (False, 120): .3, (True, 120): .9}
        actual = ns['contrast_values'](values)
        self.assertAlmostEqual(actual['H1_training_at_60'], .3)
        self.assertAlmostEqual(actual['H1_training_average'], .45)
        self.assertAlmostEqual(actual['H2_trained_60_minus_120'], -.4)
        self.assertAlmostEqual(actual['interaction_training_effect_120_minus_60'], .3)
        rows = []
        for (trained, deadline), beta in values.items():
            for group in range(6):
                for role in ns['ROLES']:
                    rows.append(dict(group_id=f'{trained}-{deadline}-{group}', trained=trained,
                                     deadline_s=deadline, role=role, beta=beta+group*.01,
                                     primary_eligible=True))
        fits = pd.DataFrame(rows)
        groups, contrasts = ns['hypothesis_table'](fits)
        self.assertEqual(len(groups), 24)  # not 96 roles or weeks
        self.assertTrue(contrasts.ci95_low.notna().all())
        fits.loc[0, 'primary_eligible'] = False
        groups, _ = ns['hypothesis_table'](fits)
        self.assertEqual(groups.included.sum(), 23)

    def test_prompt_isolation(self):
        standard = ns['make_messages'](ns['Condition'](False, 60), {'role': 'retailer'}, [])
        trained = ns['make_messages'](ns['Condition'](True, 120), {'role': 'retailer'}, [])
        self.assertNotIn(ns['TRAINING'], standard[0]['content'])
        self.assertIn(ns['TRAINING'], trained[0]['content'])
        self.assertIn('60 seconds', standard[0]['content'])
        self.assertNotIn('H1', trained[0]['content'])
        self.assertNotIn('DEMAND', standard[1]['content'])

    def test_actual_sdk_parsing_cache_and_refusal(self):
        async def check():
            original = ns['MODE']
            ns['MODE'] = 'api'
            calls = []
            refusal = [False]
            def handler(request):
                calls.append(json.loads(request.content))
                content = ([{'type': 'refusal', 'refusal': 'Test refusal'}] if refusal[0]
                           else [{'type': 'output_text', 'text': '{"order":7}', 'annotations': []}])
                payload = dict(id='resp_test', object='response', created_at=1, status='completed',
                               model=ns['MODEL'], output=[dict(type='message', id='msg_test',
                               status='completed', role='assistant', content=content)],
                               usage=dict(input_tokens=20, output_tokens=10, total_tokens=30,
                               input_tokens_details={'cached_tokens': 0},
                               output_tokens_details={'reasoning_tokens': 0}))
                return httpx.Response(200, json=payload)
            client = ns['AsyncOpenAI'](api_key='test-not-a-real-key', max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    cache = Path(tmp)
                    state = ns['BeerGame']().observe(4)[0]
                    condition = ns['Condition'](False, 60)
                    first = await ns['get_decision'](client, condition, state, [], {'id': 1}, cache)
                    second = await ns['get_decision'](client, condition, state, [], {'id': 1}, cache)
                    self.assertEqual(first, second)
                    self.assertEqual(first['order'], 7)
                    self.assertEqual(first['input_tokens'], 20)
                    self.assertEqual(len(calls), 1)
                    self.assertFalse(calls[0]['store'])
                    self.assertEqual(calls[0]['text']['format']['type'], 'json_schema')
                    refusal[0] = True
                    record = await ns['get_decision'](client, condition, state, [{'order': 9}], {'id': 2}, cache)
                    self.assertEqual(record['status'], 'unusable_response')
                    self.assertEqual(record['order'], 9)
            finally:
                await client.close()
                ns['MODE'] = original
        asyncio.run(check())

    def test_exhausted_credits_stop_and_explain(self):
        async def check():
            original = ns['MODE']
            ns['MODE'] = 'api'
            calls = []
            def handler(request):
                calls.append(request)
                return httpx.Response(429, json={'error': {
                    'message': 'Test account has no credits.',
                    'type': 'insufficient_quota',
                    'code': 'credit_balance_exhausted'}})
            client = ns['AsyncOpenAI'](api_key='test-not-a-real-key', max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with self.assertRaisesRegex(ns['ExperimentAPIError'], 'no prepaid credits'):
                    await ns['check_api_access'](client)
                self.assertEqual(len(calls), 1)
                with tempfile.TemporaryDirectory() as tmp:
                    args = (client, ns['Condition'](False, 60),
                            ns['BeerGame']().observe(4)[0], [], {'id': 'quota'}, Path(tmp))
                    with self.assertRaisesRegex(ns['ExperimentAPIError'], 'Add to credit balance'):
                        await ns['get_decision'](*args)
                    saved = json.loads(next(Path(tmp).glob('*.json')).read_text())
                    self.assertEqual(saved['error_code'], 'credit_balance_exhausted')
                    self.assertEqual(saved['http_status'], 429)
                    self.assertNotIn('test-not-a-real-key', json.dumps(saved))
                    before = len(calls)
                    with self.assertRaisesRegex(ns['ExperimentAPIError'], 'new REPLICATE_ID'):
                        await ns['get_decision'](*args)
                    self.assertEqual(len(calls), before)
            finally:
                await client.close()
                ns['MODE'] = original
        asyncio.run(check())

    def test_deadline_is_enforced(self):
        async def check():
            original = ns['MODE']
            ns['MODE'] = 'api'
            async def slow(**kwargs):
                await asyncio.sleep(.1)
            client = SimpleNamespace(responses=SimpleNamespace(parse=slow))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    result = await ns['get_decision'](client, ns['Condition'](False, .01),
                        ns['BeerGame']().observe(4)[0], [], {'id': 'timeout'}, Path(tmp))
                    self.assertEqual(result['status'], 'deadline_exceeded')
                    self.assertEqual(result['order'], 4)
            finally:
                ns['MODE'] = original
        asyncio.run(check())

    def test_progress_stops_before_experiment_when_credits_exhausted(self):
        async def check():
            previous = {k: ns[k] for k in ('BASE', 'MODE', 'AsyncOpenAI', 'RESUME_RUN_DIR')}
            from unittest.mock import patch
            calls = []
            clients = []
            def handler(request):
                calls.append(request)
                return httpx.Response(429, json={'error': {
                    'type': 'insufficient_quota', 'code': 'credit_balance_exhausted',
                    'message': 'No credits in this test.'}})
            def factory(**kwargs):
                client = previous['AsyncOpenAI'](**kwargs,
                    http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
                clients.append(client)
                return client
            try:
                with tempfile.TemporaryDirectory() as tmp, patch.dict(ns['os'].environ, {'OPENAI_API_KEY': 'test-key'}):
                    ns.update(BASE=Path(tmp), MODE='api', AsyncOpenAI=factory, RESUME_RUN_DIR=None)
                    (Path(tmp)/NOTEBOOK.name).write_text(NOTEBOOK.read_text())
                    with self.assertRaises(ns['ExperimentAPIError']):
                        await ns['run_experiment']()
                    progress = json.loads(next(Path(tmp).glob('results/*/progress.json')).read_text())
                    self.assertEqual(progress['phase'], 'Stopped')
                    self.assertEqual(progress['processed'], 0)
                    self.assertEqual(progress['remaining'], progress['total'])
                    self.assertEqual(progress['successful'], 0)
                    self.assertEqual(len(calls), 1)
                    self.assertTrue(clients[0].is_closed())
            finally:
                ns.update(previous)
        asyncio.run(check())

    def test_connection_recovery_preserves_successes_and_error_history(self):
        async def check():
            from unittest.mock import patch, AsyncMock
            original = ns['MODE']
            ns['MODE'] = 'api'
            failing = [True]
            calls = []
            def handler(request):
                calls.append(request)
                if failing[0]:
                    raise httpx.ConnectError('Mock network interruption', request=request)
                return httpx.Response(200, json=dict(id='resp_recovery', object='response',
                    created_at=1, status='completed', model=ns['MODEL'], output=[dict(
                    type='message', id='msg_recovery', status='completed', role='assistant',
                    content=[dict(type='output_text', text='{"order":7}', annotations=[])])]))
            client = ns['AsyncOpenAI'](api_key='test-key', max_retries=0,
                http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    cache = Path(tmp)/'requests'; cache.mkdir()
                    args = (client, ns['Condition'](False, 60), ns['BeerGame']().observe(4)[0],
                            [], {'id': 'recover'}, cache)
                    with patch.object(ns['asyncio'], 'sleep', new=AsyncMock()):
                        with self.assertRaises(ns['ExperimentAPIError']):
                            await ns['get_decision'](*args)
                    self.assertEqual(len(calls), 3)
                    failed = json.loads(next(cache.glob('*.json')).read_text())
                    self.assertEqual(len(failed['connection_attempts']), 3)
                    failing[0] = False
                    recovered = await ns['get_decision'](*args)
                    self.assertEqual(recovered['status'], 'ok')
                    self.assertTrue(recovered['recovered_after_restart'])
                    archives = list((Path(tmp)/'connection_errors').glob('*.json'))
                    self.assertEqual(len(archives), 1)
                    self.assertEqual(json.loads(archives[0].read_text()), failed)
                    before = len(calls)
                    again = await ns['get_decision'](*args)
                    self.assertEqual(again, recovered)
                    self.assertEqual(len(calls), before)
            finally:
                await client.close()
                ns['MODE'] = original
        asyncio.run(check())

    def test_connection_retry_does_not_reset_deadline(self):
        async def check():
            from openai import APIConnectionError
            original = ns['MODE']; ns['MODE'] = 'api'
            calls = []
            async def disconnected(**kwargs):
                calls.append(1)
                raise APIConnectionError(request=httpx.Request('POST','https://api.openai.com/v1/responses'))
            client = SimpleNamespace(responses=SimpleNamespace(parse=disconnected))
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    result = await ns['get_decision'](client, ns['Condition'](False, .01),
                        ns['BeerGame']().observe(4)[0], [], {'id':'deadline_retry'}, Path(tmp))
                    self.assertEqual(result['status'], 'deadline_exceeded')
                    self.assertEqual(len(calls), 1)
                    self.assertEqual(len(result['connection_attempts']), 1)
            finally:
                ns['MODE'] = original
        asyncio.run(check())

    def test_full_offline_run_resume(self):
        async def check():
            previous = {k: ns[k] for k in ('BASE', 'MODE', 'WEEKS', 'DEMAND', 'GROUPS_PER_CELL')}
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    ns.update(BASE=Path(tmp), MODE='offline', WEEKS=16,
                              DEMAND=[4]*4+[8]*12, GROUPS_PER_CELL=1)
                    (Path(tmp)/NOTEBOOK.name).write_text(NOTEBOOK.read_text())
                    first, directory = await ns['run_experiment']()
                    second, _ = await ns['run_experiment']()
                    pd.testing.assert_frame_equal(first, second)
                    self.assertEqual(len(first), 4*4*16)
                    progress = json.loads((directory/'progress.json').read_text())
                    self.assertEqual(progress['phase'], 'Complete')
                    self.assertEqual(progress['processed'], len(first))
                    self.assertEqual(progress['remaining'], 0)
                    self.assertEqual(progress['cached'], len(first))
                    self.assertEqual(progress['successful'], len(first))
                    self.assertEqual(len(list((directory/'requests').glob('*.json'))), len(first))
                    self.assertTrue((first.status == 'synthetic').all())
                    first.loc[first.index[0], 'recovered_after_restart'] = True
                    fits = ns['fit_all'](first)
                    affected = fits[fits.group_id == first.iloc[0].group_id]
                    self.assertTrue(affected.group_had_timing_recovery.all())
                    self.assertFalse(affected.primary_eligible.any())
            finally:
                ns.update(previous)
        asyncio.run(check())


if __name__ == '__main__':
    unittest.main(verbosity=2)
