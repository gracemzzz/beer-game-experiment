"""Network-free tests of the new shared-budget provider transport.

Tiny stub study payloads isolate accounting, retry and resume behavior from the
separately tested Beer Game scientific schema. HTTP uses MockTransport only.
"""
import asyncio
import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study import batched_pressure_api as api


MODELS = tuple(api.RATES)
FAKE_KEYS = {'openai': 'fake-openai-only', 'anthropic': 'fake-anthropic-only'}


def tasks_for(run_name='run_one'):
    return [dict(task_id=model + '_' + phase, model=model, phase=phase,
                 response_path='accepted/' + model + '_' + phase + '.json',
                 study_id=run_name, chains=[{}, {}] if phase == 'pilot' else [{}] * 20)
            for phase in ('pilot', 'main') for model in MODELS]


def sent_payload(request):
    return json.loads(request.content)


def sent_task(request):
    body = sent_payload(request)
    return json.loads((body.get('input') or body.get('messages'))[0]['content'])


def provider_reply(request, *, text=None, returned_model=None, usage=None):
    body = sent_payload(request)
    model = body['model']
    answer = json.dumps({'valid': True}) if text is None else text
    meter = dict(input_tokens=100, output_tokens=200) if usage is None else usage
    if api.RATES[model]['provider'] == 'openai':
        return dict(model=returned_model or model, status='completed', usage=meter,
                    output=[dict(type='message', content=[dict(type='output_text', text=answer)])])
    return dict(model=returned_model or model, stop_reason='end_turn', usage=meter,
                content=[dict(type='text', text=answer)])


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_cap_covers_prior_runs_and_inflight_reservations(self):
        first = api.BudgetLedger(self.root)
        first.reserve('run1-call1', 4.7, {'run': 'run_one'})
        resumed = api.BudgetLedger(self.root)
        self.assertAlmostEqual(resumed.spent, 4.7)
        with self.assertRaises(api.BudgetStop):
            resumed.reserve('run2-call1', .31, {'run': 'run_two'})
        resumed.reserve('run2-call2', .3, {'run': 'run_two'})
        self.assertAlmostEqual(api.BudgetLedger(self.root).spent, 5.)

    def test_settling_unknown_usage_preserves_full_reservation(self):
        ledger = api.BudgetLedger(self.root)
        ledger.reserve('call1', .4, {})
        ledger.settle('call1', None, 'unknown_charge')
        self.assertAlmostEqual(api.BudgetLedger(self.root).spent, .4)
        with self.assertRaises(api.BudgetStop):
            api.BudgetLedger(self.root).reserve('call1', .4, {})

    def test_changing_existing_cap_is_rejected(self):
        api.BudgetLedger(self.root)
        with self.assertRaises(api.BudgetStop):
            api.BudgetLedger(self.root, cap_usd=4.)
        with self.assertRaises(ValueError):
            api.BudgetLedger(self.root, cap_usd=5.01)

    def test_charge_above_reservation_is_retained_and_stops(self):
        ledger = api.BudgetLedger(self.root)
        ledger.reserve('call1', .2, {})
        with self.assertRaises(api.BudgetStop):
            ledger.settle('call1', .25, 'received')
        self.assertAlmostEqual(api.BudgetLedger(self.root).spent, .25)

    def test_invalid_reservations_do_not_create_credit(self):
        ledger = api.BudgetLedger(self.root)
        for amount in (-1., float('nan'), float('inf')):
            with self.subTest(amount=amount), self.assertRaises((ValueError, api.BudgetStop)):
                ledger.reserve(str(amount), amount, {})
        self.assertEqual(ledger.spent, 0.)

    def test_negative_or_nonfinite_usage_never_lowers_budget(self):
        for usage in [dict(input_tokens=-100, output_tokens=1),
                      dict(input_tokens=1, output_tokens=-100),
                      dict(input_tokens=1, output_tokens=10,
                           input_tokens_details={'cached_tokens': 100}),
                      dict(input_tokens=float('nan'), output_tokens=10)]:
            with self.subTest(usage=usage):
                try:
                    meter, charge = api.usage_and_charge(MODELS[0], {'usage': usage})
                except (ValueError, TypeError):
                    continue
                self.assertIsNone(meter)
                self.assertIsNone(charge)

    def test_claude_long_context_threshold_counts_cached_and_written_input(self):
        model = 'claude-haiku-5-5'
        rate = api.RATES[model]
        at_boundary = dict(input_tokens=99990, output_tokens=100,
                           cache_read_input_tokens=5, cache_creation_input_tokens=5,
                           cache_creation={'ephemeral_5m_input_tokens': 5})
        usage, charged = api.usage_and_charge(model, {'usage': at_boundary})
        expected = (99990 * rate['input'] + 5 * rate['cached'] +
                    5 * rate['input'] * 1.25 + 100 * rate['output']) / 1e6
        self.assertEqual(usage['input_tokens'], 100000)
        self.assertAlmostEqual(charged, expected)
        above = dict(at_boundary, cache_read_input_tokens=6)
        usage, charged = api.usage_and_charge(model, {'usage': above})
        self.assertEqual(usage['input_tokens'], 100001)
        self.assertAlmostEqual(charged, 5 * (expected + rate['cached'] / 1e6))

    def test_long_context_reservation_covers_output_as_well_as_input_uplift(self):
        model = 'claude-haiku-5-5'
        payload = {'model': model, 'messages': [{'role': 'user', 'content': 'a' * 100000}],
                   'max_tokens': 16384}
        reserve = api.reservation(model, payload)
        _, charged = api.usage_and_charge(model, {'usage': {
            'input_tokens': 100001, 'output_tokens': 16384}})
        self.assertGreaterEqual(reserve, charged)
        self.assertGreater(reserve, 5 * 16384 * api.RATES[model]['output'] / 1e6)


class RunnerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.experiment = Path(self.temporary.name).resolve()
        self.run = self.experiment / 'data' / 'run_one'
        self.run.mkdir(parents=True)
        self.plan = {'tasks': tasks_for()}
        for name, replacement in [
            ('loadplan', lambda run: copy.deepcopy(self.plan)),
            ('prompt_text', lambda task: json.dumps(task)),
            ('response_schema', lambda task: {'type': 'object', 'properties': {
                'valid': {'type': 'boolean'}}, 'required': ['valid'], 'additionalProperties': False}),
            ('validate_response', lambda task, value: [] if value == {'valid': True} else ['Invalid fixture'])
        ]:
            active = patch.object(api.study, name, replacement)
            active.start()
            self.addCleanup(active.stop)
        self.requests = []

    def transport(self, handler=None):
        def send(request):
            self.requests.append(request)
            return handler(request) if handler else httpx.Response(200, json=provider_reply(request))
        return httpx.MockTransport(send)

    def runner(self, handler=None, *, run=None, keys=None, callback=None):
        return api.Runner(run or self.run, keys=FAKE_KEYS if keys is None else keys,
                          transport=self.transport(handler), retry_delay=0,
                          concurrency=4, callback=callback)

    async def test_all_eight_fixed_tasks_finish_and_resume_without_calls_or_rebilling(self):
        progress = await self.runner().execute('all')
        self.assertEqual(len(self.requests), 8)
        self.assertEqual((progress['accepted'], progress['failed'], progress['remaining']), (8, 0, 0))
        original = (self.experiment / 'data/api_budget.json').read_bytes()
        resumed = await self.runner().execute('all')
        self.assertEqual(len(self.requests), 8)
        self.assertEqual(resumed['accepted'], 8)
        self.assertEqual((self.experiment / 'data/api_budget.json').read_bytes(), original)

    async def test_separate_run_uses_same_cumulative_ledger(self):
        first = await self.runner().execute('pilot')
        second_run = self.experiment / 'data/run_two'
        second_run.mkdir()
        second = await self.runner(run=second_run).execute('pilot')
        self.assertEqual(len(self.requests), 8)
        self.assertAlmostEqual(second['charged_or_reserved_usd'], 2 * first['charged_or_reserved_usd'])
        self.assertEqual(len(api.BudgetLedger(self.experiment).data['attempts']), 8)

    async def test_budget_exhaustion_prevents_http_calls(self):
        ledger = api.BudgetLedger(self.experiment)
        ledger.reserve('older_run', 5., {'run': 'older_run'})
        result = await self.runner().execute('pilot')
        self.assertEqual(len(self.requests), 0)
        self.assertEqual(result['charged_or_reserved_usd'], 5.)
        self.assertTrue(all(t['status'] == 'budget_stopped' for t in result['tasks'].values()))

    async def test_missing_keys_never_issue_http_or_reserve_money(self):
        result = await self.runner(keys={}).execute('all')
        self.assertEqual(self.requests, [])
        self.assertEqual(result['accepted'], 0)
        self.assertEqual(result['remaining'], 8)
        self.assertEqual(api.BudgetLedger(self.experiment).spent, 0.)

    async def test_invalid_json_is_retained_once_and_never_retried(self):
        def handler(request):
            text = '{unparseable' if sent_task(request)['model'] == MODELS[0] else None
            return httpx.Response(200, json=provider_reply(request, text=text))
        result = await self.runner(handler).execute('all')
        self.assertEqual(len(self.requests), 4)
        self.assertEqual(result['accepted'], 3)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['skipped'], 4)
        self.assertEqual(result['remaining'], 0)
        await self.runner(handler).execute('all')
        self.assertEqual(len(self.requests), 4)
        raw = list((self.experiment / 'raw').rglob('*.response.txt'))
        self.assertEqual(len(raw), 4)
        self.assertTrue(any('{unparseable' in p.read_text() for p in raw))

    async def test_single_bad_rules_or_readback_pilot_blocks_all_main_models(self):
        def handler(request):
            text = json.dumps({'valid': False}) if sent_task(request)['model'] == MODELS[-1] else None
            return httpx.Response(200, json=provider_reply(request, text=text))
        result = await self.runner(handler).execute('all')
        self.assertEqual(len(self.requests), 4)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['skipped'], 4)
        self.assertTrue(all(sent_task(r)['phase'] == 'pilot' for r in self.requests))

    async def test_main_waits_for_all_requested_models_including_missing_provider_key(self):
        result = await self.runner(keys={'openai': FAKE_KEYS['openai']}).execute('all')
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(result['accepted'], 3)
        self.assertTrue(all(sent_task(r)['phase'] == 'pilot' for r in self.requests))

    async def test_returned_model_mismatch_is_rejected_after_one_call(self):
        def handler(request):
            return httpx.Response(200, json=provider_reply(request, returned_model='wrong-model'))
        result = await self.runner(handler).execute('pilot')
        self.assertEqual(len(self.requests), 4)
        self.assertEqual(result['failed'], 4)
        self.assertTrue(all(t['reason'] == 'returned_model_mismatch' for t in result['tasks'].values()))
        self.assertEqual(list((self.run / 'accepted').glob('*.json')), [])

    async def test_alias_snapshot_change_between_pilot_and_main_is_rejected(self):
        def handler(request):
            task = sent_task(request)
            returned = task['model']
            if returned == MODELS[0]:
                returned += '-2026-10-01' if task['phase'] == 'pilot' else '-2026-10-20'
            return httpx.Response(200, json=provider_reply(request, returned_model=returned))
        result = await self.runner(handler).execute('all')
        self.assertEqual(len(self.requests), 8)
        self.assertEqual(result['accepted'], 7)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['tasks'][MODELS[0] + '_main']['reason'], 'model_alias_changed_during_study')

    async def test_transport_retry_counts_and_reserves_unknown_first_charge(self):
        counts = {}
        def handler(request):
            task = sent_task(request)
            key = task['task_id']
            counts[key] = counts.get(key, 0) + 1
            if task['model'] == MODELS[0] and counts[key] == 1:
                raise httpx.ReadTimeout('timed out', request=request)
            return httpx.Response(200, json=provider_reply(request))
        result = await self.runner(handler).execute('pilot')
        self.assertEqual(len(self.requests), 5)
        self.assertEqual(result['accepted'], 4)
        attempts = api.BudgetLedger(self.experiment).data['attempts'].values()
        unknown = [a for a in attempts if a['status'] == 'unknown_charge']
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]['charge_usd'], unknown[0]['reserve_usd'])
        self.assertGreater(unknown[0]['charge_usd'], 0.)

    async def test_repeated_technical_failure_stops_at_two_attempts(self):
        def handler(request):
            raise httpx.ConnectError('temporary connection failure', request=request)
        result = await self.runner(handler).execute('all')
        self.assertEqual(len(self.requests), 8)
        self.assertEqual(result['failed'], 4)
        self.assertEqual(result['skipped'], 4)
        for row in api.BudgetLedger(self.experiment).data['attempts'].values():
            self.assertEqual(row['charge_usd'], row['reserve_usd'])
        await self.runner(handler).execute('all')
        self.assertEqual(len(self.requests), 8)

    async def test_rate_limit_retries_are_counted_but_quota_exhaustion_is_not_retried(self):
        counts = {}
        def handler(request):
            task = sent_task(request)
            key = task['task_id']
            counts[key] = counts.get(key, 0) + 1
            if task['model'] == MODELS[0] and counts[key] == 1:
                return httpx.Response(429, json={'error': {'code': 'rate_limit_exceeded'}})
            if task['model'] == MODELS[1]:
                return httpx.Response(429, json={'error': {'code': 'insufficient_quota'}})
            return httpx.Response(200, json=provider_reply(request))
        result = await self.runner(handler).execute('pilot')
        self.assertEqual(len(self.requests), 5)
        self.assertEqual(result['accepted'], 3)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(counts[MODELS[1] + '_pilot'], 1)
        attempts = api.BudgetLedger(self.experiment).data['attempts'].values()
        self.assertEqual(sum(a['charge_usd'] == 0 for a in attempts), 2)

    async def test_prior_reserved_attempt_is_not_resent_after_interruption(self):
        task = self.plan['tasks'][0]
        payload = api.payload_for(task)
        attempt_id = api.digest([self.run.name, task['task_id'], api.digest(payload), 1])
        ledger = api.BudgetLedger(self.experiment)
        reserve = api.reservation(task['model'], payload)
        ledger.reserve(attempt_id, reserve, {'run': self.run.name, 'task_id': task['task_id']})
        result = await self.runner().execute('pilot')
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(result['tasks'][task['task_id']]['status'], 'interrupted')
        self.assertEqual(api.BudgetLedger(self.experiment).data['attempts'][attempt_id]['charge_usd'], reserve)

    async def test_scalar_provider_body_is_invalid_without_aborting_other_pilots(self):
        def handler(request):
            if sent_task(request)['model'] == MODELS[0]:
                return httpx.Response(200, json=['unexpected', 'list'])
            return httpx.Response(200, json=provider_reply(request))
        result = await self.runner(handler).execute('pilot')
        self.assertEqual(len(self.requests), 4)
        self.assertEqual((result['accepted'], result['failed']), (3, 1))

    async def test_credentials_are_redacted_even_when_provider_echoes_them(self):
        def handler(request):
            return httpx.Response(400, json={'error': {'message': ' '.join(FAKE_KEYS.values())}})
        result = await self.runner(handler).execute('pilot')
        self.assertEqual(result['failed'], 4)
        response_files = list((self.experiment / 'raw').rglob('*.response.txt'))
        self.assertEqual(len(response_files), 4)
        for path in self.experiment.rglob('*'):
            if path.is_file():
                value = path.read_text()
                for key in FAKE_KEYS.values():
                    self.assertNotIn(key, value)
        self.assertTrue(all('[REDACTED_CREDENTIAL]' in p.read_text() for p in response_files))

    async def test_progress_accounts_for_finished_and_remaining_fixed_slots(self):
        observations = []
        result = await self.runner(callback=lambda p: observations.append({
            k: p[k] for k in ('total', 'accepted', 'failed', 'skipped', 'done', 'remaining')})).execute('all')
        self.assertTrue(observations)
        for point in observations:
            self.assertEqual(point['total'], 8)
            self.assertEqual(point['done'], point['accepted'] + point['failed'] + point['skipped'])
            self.assertEqual(point['remaining'], 8 - point['done'])
        self.assertEqual(result['accepted'], 8)
        self.assertEqual(result['remaining'], 0)

    async def test_accepted_file_tamper_blocks_resume_before_new_http(self):
        await self.runner().execute('pilot')
        first = self.run / self.plan['tasks'][0]['response_path']
        first.write_text('{"changed": true}')
        with self.assertRaisesRegex(ValueError, 'missing or changed'):
            await self.runner().execute('pilot')
        self.assertEqual(len(self.requests), 4)


class FullCohortIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_cohort_schema_physics_all_eight_calls_and_cached_resume(self):
        """Use synthetic software fixtures only, never generated observations."""
        with tempfile.TemporaryDirectory() as directory:
            experiment = Path(directory).resolve()
            protocol = experiment / 'hypotheses/PROTOCOL.md'
            protocol.parent.mkdir(parents=True)
            protocol.write_bytes((ROOT / 'experiments/12_pressure_framing_api_20261020'
                                  / 'hypotheses/PROTOCOL.md').read_bytes())
            run = api.study.prepare(experiment)
            plan = api.study.loadplan(run)
            tasks = {(t['model'], t['phase']): t for t in plan['tasks']}
            fixtures = {key: api.study.synthetic_fixture(task) for key, task in tasks.items()}
            calls = []

            def handle(request):
                payload = sent_payload(request)
                cap = payload.get('max_output_tokens', payload.get('max_tokens'))
                phase = 'pilot' if cap == 8192 else 'main'
                key = (payload['model'], phase)
                calls.append(key)
                return httpx.Response(200, json=provider_reply(request, text=json.dumps(fixtures[key])))

            first = await api.Runner(run, keys=FAKE_KEYS, transport=httpx.MockTransport(handle),
                                     retry_delay=0).execute('all')
            self.assertEqual(first['accepted'], 8)
            self.assertEqual(first['remaining'], 0)
            self.assertEqual(len(calls), 8)
            self.assertEqual([p for _, p in calls[:4]], ['pilot'] * 4)
            self.assertEqual([p for _, p in calls[4:]], ['main'] * 4)
            order_count = 0
            for task in plan['tasks']:
                accepted = json.loads((run / task['response_path']).read_text())
                self.assertEqual(api.study.validate_response(task, accepted), [])
                order_count += sum(len(chain['orders']) * 4 for chain in accepted['chains'])
            self.assertEqual(order_count, 8448)
            before = (experiment / 'data/api_budget.json').read_bytes()
            second = await api.Runner(run, keys=FAKE_KEYS, transport=httpx.MockTransport(handle),
                                      retry_delay=0).execute('all')
            self.assertEqual(second['accepted'], 8)
            self.assertEqual(len(calls), 8)
            self.assertEqual((experiment / 'data/api_budget.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
