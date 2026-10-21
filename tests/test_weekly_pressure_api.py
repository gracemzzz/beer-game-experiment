"""Offline HTTP tests; every provider result is an explicitly synthetic fixture."""
import asyncio
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study import weekly_pressure as study
from beergame_study import weekly_pressure_api as api

KEYS = {'openai': 'fake-openai-weekly-secret', 'anthropic': 'fake-anthropic-weekly-secret'}
PRIOR = .3404859


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def request_id(body):
    schema = (body.get('text', {}).get('format') or body['output_config']['format'])['schema']
    return schema['properties']['task_id']['enum'][0]


def response(body, choices, *, model=None):
    model = model or body['model']
    usage = {'input_tokens': 500, 'output_tokens': 800}
    if api.RATES[body['model']]['provider'] == 'openai':
        return dict(model=model, status='completed', usage=usage,
                    output=[{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(choices)}]}])
    return dict(model=model, stop_reason='end_turn', usage=usage,
                content=[{'type': 'text', 'text': json.dumps(choices)}])


class WeeklyApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name).resolve()
        self.experiment, self.budget = root / '13_weekly', root / '12_previous'
        protocol = self.experiment / 'hypotheses/PROTOCOL.md'
        protocol.parent.mkdir(parents=True)
        protocol.write_bytes((ROOT / 'experiments/13_weekly_state_api_20261021/hypotheses/PROTOCOL.md').read_bytes())
        ledger = api.BudgetLedger(self.budget)
        ledger.reserve('earlier_approved_experiment', PRIOR, {'model': 'previous', 'run': 'preserved'})
        ledger.settle('earlier_approved_experiment', PRIOR, 'received')
        self.prior = dict(ledger.data['attempts']['earlier_approved_experiment'])
        self.run = study.prepare(self.experiment, self.budget)
        self.plan = study.loadplan(self.run)
        self.calls, self.progress = [], []

    def task_for(self, body):
        return json.loads((self.run / 'requests' / request_id(body) / 'task.json').read_text())

    def valid(self, request):
        body = json.loads(request.content)
        self.calls.append(body)
        task = self.task_for(body)
        return httpx.Response(200, json=response(body, study.synthetic_fixture(task)))

    def runner(self, handler=None, **kwargs):
        return api.Runner(self.run, keys=kwargs.pop('keys', KEYS), retry_delay=0,
                          callback=self.progress.append,
                          transport=httpx.MockTransport(handler or self.valid), **kwargs)

    async def test_full_104_requests_replay_provenance_settings_and_free_resume(self):
        result = await self.runner().execute('all')
        self.assertEqual(len(self.calls), 104)
        self.assertEqual((result['total'], result['accepted'], result['failed'], result['blocked'], result['remaining']),
                         (104, 104, 0, 0, 0))
        choices = api.audit_saved(self.run)
        self.assertEqual(len(choices), 104)
        self.assertEqual(len(await asyncio.to_thread(api.audit_saved, self.run)), 104)
        for model in self.plan['models']:
            ids = [request_id(body) for body in self.calls if body['model'] == model]
            self.assertEqual(ids, [key for key, _, _ in api._slots(model)])
        for body in self.calls:
            task = self.task_for(body)
            cap = 4096 if task['phase'] == 'probe' else 2048
            if body['model'].startswith('gpt-'):
                self.assertEqual(body['reasoning'], {'effort': 'none'})
                self.assertEqual(body['max_output_tokens'], cap)
                self.assertFalse(body['store'])
            else:
                self.assertEqual(body['thinking'], {'type': 'disabled'})
                self.assertEqual(body['output_config']['effort'], 'low')
                self.assertEqual(body['max_tokens'], cap)
            self.assertNotIn('temperature', body)
            self.assertEqual(len(task['chain_ids']), 20)
        analysis = study.analyze(self.run)
        self.assertEqual(len(analysis['rounds']), 4 * 20 * 4 * 24)
        self.assertEqual(len(analysis['chains']), 80)
        self.assertEqual(len(analysis['hypotheses']), 8)
        ledger_before = (self.budget / 'data/api_budget.json').read_bytes()
        accepted_before = {p: sha(p) for p in (self.run / 'accepted').glob('*.json')}
        self.assertEqual(study.prepare(self.experiment, self.budget), self.run)
        await self.runner().execute('all')
        self.assertEqual(len(self.calls), 104)
        self.assertEqual((self.budget / 'data/api_budget.json').read_bytes(), ledger_before)
        self.assertTrue(all(sha(p) == h for p, h in accepted_before.items()))
        self.assertEqual(api.BudgetLedger(self.budget).data['attempts']['earlier_approved_experiment'], self.prior)
        self.assertFalse((self.experiment / 'data/api_budget.json').exists())
        for path in self.experiment.rglob('*'):
            if path.is_file():
                data = path.read_bytes()
                self.assertTrue(all(secret.encode() not in data for secret in KEYS.values()))
        self.assertTrue(all(p['done'] + p['remaining'] == 104 for p in self.progress))

    async def test_missing_keys_and_main_without_pilot_make_no_http_requests(self):
        result = await self.runner(keys={}).execute('all')
        self.assertEqual(self.calls, [])
        self.assertEqual(result['remaining'], 104)
        await self.runner().execute('main')
        self.assertEqual(self.calls, [])
        self.assertEqual(api.BudgetLedger(self.budget).spent, PRIOR)
        self.assertEqual(len(api.estimate(self.run)), 4)

    async def test_one_failed_pilot_blocks_only_that_model_and_no_semantic_retry(self):
        def handler(request):
            body = json.loads(request.content)
            self.calls.append(body)
            task = self.task_for(body)
            choices = study.synthetic_fixture(task)
            if body['model'] == 'gpt-6-luna':
                choices['orders'].pop(task['chain_ids'][0])
            return httpx.Response(200, json=response(body, choices))
        result = await self.runner(handler).execute('all')
        self.assertEqual(len(self.calls), 79)
        self.assertEqual((result['accepted'], result['failed'], result['blocked'], result['remaining']), (78, 1, 25, 0))
        await self.runner(handler).execute('all')
        self.assertEqual(len(self.calls), 79)
        self.assertEqual(len(api.audit_saved(self.run)), 78)

    async def test_failed_second_week_keeps_verified_prefix_and_blocks_future(self):
        def handler(request):
            body = json.loads(request.content)
            self.calls.append(body)
            task = self.task_for(body)
            choices = study.synthetic_fixture(task)
            if task['task_id'] == 'gpt-6-luna_w02':
                choices['orders'][task['chain_ids'][0]]['r'] = True
            return httpx.Response(200, json=response(body, choices))
        result = await self.runner(handler, concurrency=1).execute('all')
        self.assertEqual(len(self.calls), 81)
        self.assertEqual((result['accepted'], result['failed'], result['blocked']), (80, 1, 23))
        data = study.analyze(self.run)
        own = next(row for row in data['model_status'] if row['model'] == 'gpt-6-luna')
        self.assertEqual(own['accepted_weeks'], 1)
        for chain in data['chains']:
            if chain['model'] == 'gpt-6-luna':
                self.assertIsNone(chain['total_cost'])

    async def test_bounded_transport_retry_retains_unknown_charge_and_identical_payload(self):
        counts = {}
        def handler(request):
            body = json.loads(request.content)
            key = request_id(body)
            self.calls.append(body)
            counts[key] = counts.get(key, 0) + 1
            if key == 'gpt-6-luna_pilot' and counts[key] == 1:
                raise httpx.ReadTimeout('synthetic timeout', request=request)
            return httpx.Response(200, json=response(body, study.synthetic_fixture(self.task_for(body))))
        result = await self.runner(handler).execute('pilot')
        self.assertEqual((len(self.calls), result['accepted']), (5, 4))
        attempts = [b for b in self.calls if request_id(b) == 'gpt-6-luna_pilot']
        self.assertEqual(attempts[0], attempts[1])
        unknown = [v for v in api.BudgetLedger(self.budget).data['attempts'].values() if v['status'] == 'unknown_charge']
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]['charge_usd'], unknown[0]['reserve_usd'])
        await self.runner(handler).execute('pilot')
        self.assertEqual(len(self.calls), 5)

    async def test_rate_limit_retries_but_quota_does_not_and_keys_are_redacted(self):
        counts = {}
        def handler(request):
            body = json.loads(request.content)
            key = request_id(body)
            counts[key] = counts.get(key, 0) + 1
            self.calls.append(body)
            if body['model'] == 'gpt-6-luna' and counts[key] == 1:
                return httpx.Response(429, json={'error': {'code': 'rate_limit_exceeded'}})
            if body['model'] == 'gpt-5.6-luna':
                return httpx.Response(429, json={'error': {'code': 'insufficient_quota', 'message': KEYS['openai']}})
            return httpx.Response(200, json=response(body, study.synthetic_fixture(self.task_for(body))))
        result = await self.runner(handler).execute('pilot')
        self.assertEqual(counts['gpt-6-luna_pilot'], 2)
        self.assertEqual(counts['gpt-5.6-luna_pilot'], 1)
        self.assertEqual((result['accepted'], result['failed'], result['blocked']), (3, 1, 25))
        for p in (self.experiment / 'raw').rglob('*'):
            if p.is_file():
                self.assertNotIn(KEYS['openai'].encode(), p.read_bytes())

    async def test_invalid_json_wrong_model_and_invalid_usage_are_terminal(self):
        def handler(request):
            body = json.loads(request.content)
            self.calls.append(body)
            value = response(body, study.synthetic_fixture(self.task_for(body)))
            if body['model'] == 'gpt-6-luna':
                value['output'][0]['content'][0]['text'] = '{broken'
            elif body['model'] == 'gpt-5.6-luna':
                value['model'] = 'gpt-6-luna'
            elif body['model'] == 'gpt-5.6-sol':
                value['usage']['input_tokens'] = -1
            return httpx.Response(200, json=value)
        result = await self.runner(handler).execute('pilot')
        self.assertEqual(len(self.calls), 4)
        self.assertEqual((result['accepted'], result['failed'], result['blocked']), (1, 3, 75))
        sol = next(v for v in api.BudgetLedger(self.budget).data['attempts'].values() if v.get('model') == 'gpt-5.6-sol')
        self.assertEqual(sol['charge_usd'], sol['reserve_usd'])

    async def test_shared_budget_stops_all_before_http_and_preserves_prior_charge(self):
        ledger = api.BudgetLedger(self.budget)
        ledger.reserve('other_authorized_work', 5 - ledger.spent, {'run': 'elsewhere'})
        result = await self.runner().execute('all')
        self.assertEqual(self.calls, [])
        self.assertEqual((result['accepted'], result['blocked'], result['remaining']), (0, 104, 0))
        self.assertEqual(result['charged_or_reserved_usd'], 5)
        self.assertEqual(api.BudgetLedger(self.budget).data['attempts']['earlier_approved_experiment'], self.prior)

    async def test_existing_pending_attempt_is_never_resent(self):
        model = self.plan['models'][0]
        task = study.build_task(self.plan, model, 'pilot', week=1)
        body = api.payload_for(task)
        identity = api.digest(['weekly-pressure', self.run.name, task['task_id'], api.digest(body), 1])
        ledger = api.BudgetLedger(self.budget)
        ledger.reserve(identity, api.reservation(model, body), {'model': model, 'run': self.run.name})
        result = await self.runner().execute('pilot')
        self.assertEqual(len(self.calls), 3)
        self.assertFalse(any(body['model'] == model for body in self.calls))
        self.assertEqual((result['accepted'], result['failed'], result['blocked']), (3, 1, 25))
        self.assertEqual(api.BudgetLedger(self.budget).data['attempts'][identity]['status'], 'reserved')

    async def test_new_charge_rollback_or_edit_rejected_before_resume_or_report(self):
        before = (self.budget / 'data/api_budget.json').read_bytes()
        await self.runner().execute('pilot')
        path = self.budget / 'data/api_budget.json'
        valid = path.read_bytes()
        path.write_bytes(before)
        with self.assertRaisesRegex(ValueError, 'Shared ledger is missing'):
            api.audit_saved(self.run)
        with self.assertRaisesRegex(ValueError, 'Shared ledger is missing'):
            await self.runner().execute('all')
        self.assertEqual(len(self.calls), 4)
        changed = json.loads(valid)
        row = next(v for key, v in changed['attempts'].items() if key != 'earlier_approved_experiment')
        row['charge_usd'] = 0
        path.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, 'charge differs'):
            api.audit_saved(self.run)
        path.write_bytes(valid)
        self.assertEqual(len(api.audit_saved(self.run)), 4)
        malformed = json.loads(valid)
        malformed['attempts']['unrelated_bad_row'] = dict(charge_usd=-1, reserve_usd=0)
        path.write_text(json.dumps(malformed))
        with self.assertRaisesRegex(api.BudgetStop, 'finite and nonnegative'):
            self.runner()
        path.write_bytes(valid)

    async def test_two_transport_failures_stop_model_and_never_retry_on_resume(self):
        def handler(request):
            body = json.loads(request.content)
            self.calls.append(body)
            if body['model'] == 'gpt-6-luna':
                raise httpx.ConnectError('synthetic unavailable', request=request)
            return httpx.Response(200, json=response(body, study.synthetic_fixture(self.task_for(body))))
        result = await self.runner(handler).execute('pilot')
        self.assertEqual(len(self.calls), 5)
        self.assertEqual((result['accepted'], result['failed'], result['blocked']), (3, 1, 25))
        self.assertEqual(len(api.audit_saved(self.run)), 3)
        await self.runner(handler).execute('pilot')
        self.assertEqual(len(self.calls), 5)

    async def test_accepted_raw_request_and_mirror_tampering_reject_before_any_http(self):
        await self.runner().execute('pilot')
        record = json.loads((self.run / 'api_status.json').read_text())['tasks']['gpt-6-luna_pilot']
        receipt = self.experiment / record['record_path']
        body_path = receipt.parent / json.loads(receipt.read_text())['response_file']
        paths = [self.run / 'accepted/gpt-6-luna_pilot.json', receipt, body_path,
                 self.run / 'requests/gpt-6-luna_pilot/prompt.txt',
                 self.experiment / 'prompts' / self.run.name / 'gpt-6-luna_pilot.txt']
        for path in paths:
            original = path.read_bytes()
            path.write_bytes(original + b' ')
            with self.assertRaises(ValueError):
                await self.runner().execute('all')
            self.assertEqual(len(self.calls), 4)
            path.write_bytes(original)
        self.assertEqual(len(api.audit_saved(self.run)), 4)

    async def test_missing_budget_prior_charge_and_source_tampering_fail_closed(self):
        ledger_path = self.budget / 'data/api_budget.json'
        original = ledger_path.read_bytes()
        ledger = json.loads(original)
        ledger['attempts']['earlier_approved_experiment']['charge_usd'] = 0
        ledger_path.write_text(json.dumps(ledger))
        with self.assertRaisesRegex(ValueError, 'Earlier shared-budget charge'):
            self.runner()
        ledger_path.write_bytes(original)
        ledger_path.unlink()
        with self.assertRaises((ValueError, FileNotFoundError, api.BudgetStop)):
            self.runner()
        self.assertFalse(ledger_path.exists())
        ledger_path.write_bytes(original)
        snapshot = self.run / 'source_snapshot/weekly_pressure_api.py'
        snapshot.write_bytes(snapshot.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'source snapshot changed'):
            self.runner()
        self.assertEqual(self.calls, [])

    async def test_unexpected_worker_failure_drains_inflight_before_unlock(self):
        first_started = asyncio.Event()
        second_finished = asyncio.Event()
        async def handler(request):
            body = json.loads(request.content)
            self.calls.append(body)
            if body['model'] == 'gpt-6-luna':
                first_started.set()
                await asyncio.sleep(.02)
                raise RuntimeError('synthetic local failure')
            await first_started.wait()
            await asyncio.sleep(.05)
            self.assertTrue((self.budget / 'data/.api_runner.lock').exists())
            second_finished.set()
            return httpx.Response(200, json=response(body, study.synthetic_fixture(self.task_for(body))))
        with self.assertRaisesRegex(RuntimeError, 'synthetic local failure'):
            await self.runner(handler, concurrency=2).execute('all')
        self.assertTrue(second_finished.is_set())
        self.assertEqual(len(self.calls), 2)
        self.assertFalse((self.budget / 'data/.api_runner.lock').exists())
        status = json.loads((self.run / 'api_status.json').read_text())
        self.assertEqual(status['tasks']['gpt-6-luna_pilot']['status'], 'interrupted')
        self.assertEqual(status['tasks']['gpt-5.6-luna_pilot']['status'], 'accepted')
        pending = [v for v in api.BudgetLedger(self.budget).data['attempts'].values() if v['status'] == 'interrupted_unknown_charge']
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['charge_usd'], pending[0]['reserve_usd'])


if __name__ == '__main__':
    unittest.main()
