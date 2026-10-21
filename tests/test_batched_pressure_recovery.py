"""Bounded recovery checks on temporary synthetic provider records only."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study import batched_pressure as study
from beergame_study import batched_pressure_api as api
from beergame_study import batched_pressure_recovery as recovery

KEYS = {'openai': 'fake-openai-recovery', 'anthropic': 'fake-anthropic-recovery'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def request_task_id(body):
    schema = (body.get('text', {}).get('format') or body['output_config']['format'])['schema']
    return schema['properties']['task_id']['enum'][0]


def response(body, payload, *, truncated=False):
    model = body['model']
    usage = {'input_tokens': 500, 'output_tokens': 1200}
    if api.RATES[model]['provider'] == 'openai':
        return dict(model=model, status='completed', usage=usage,
                    output=[{'type': 'message', 'content': [
                        {'type': 'output_text', 'text': json.dumps(payload)}]}])
    if truncated:
        usage = {'input_tokens': 500, 'output_tokens': 8192,
                 'output_tokens_details': {'reasoning_tokens': 8192}}
        return dict(model=model, stop_reason='max_tokens', usage=usage,
                    content=[{'type': 'thinking', 'thinking': 'Synthetic unfinished test fixture.'}])
    return dict(model=model, stop_reason='end_turn', usage=usage,
                content=[{'type': 'text', 'text': json.dumps(payload)}])


class RecoveryTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.experiment = Path(self.temporary.name).resolve()
        for name in ('PROTOCOL.md', 'RECOVERY_20261021.md'):
            target = self.experiment / 'hypotheses' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / 'experiments/12_pressure_framing_api_20261020/hypotheses' / name).read_bytes())
        self.parent = study.prepare(self.experiment)
        self.plan = study.loadplan(self.parent)
        self.tasks = {t['task_id']: t for t in self.plan['tasks']}
        self.original_calls = []
        self.calls = []

        def original_handler(request):
            body = json.loads(request.content)
            task = self.tasks[request_task_id(body)]
            self.original_calls.append(task['task_id'])
            fixture = study.synthetic_fixture(task)
            if task['model'] == 'gpt-6-luna':
                fixture['chains'][0]['inventory_checkpoints'][1]['inventories'][0] += 1
            return httpx.Response(200, json=response(body, fixture,
                truncated=task['model'] == 'claude-haiku-5-5'))

        await api.Runner(self.parent, keys=KEYS, retry_delay=0,
                         transport=httpx.MockTransport(original_handler)).execute('all')
        self.original_files = {p: sha(p) for base in (self.parent, self.experiment / 'raw')
                               for p in base.rglob('*') if p.is_file()}
        self.original_charge = api.BudgetLedger(self.experiment).spent
        self.amendment = recovery.prepare(self.parent)

    def valid_handler(self, request):
        body = json.loads(request.content)
        task_id = request_task_id(body)
        self.calls.append(task_id)
        return httpx.Response(200, json=response(body, study.synthetic_fixture(self.tasks[task_id])))

    def runner(self, handler=None):
        return recovery.Runner(self.amendment, keys=KEYS, retry_delay=0,
                               transport=httpx.MockTransport(handler or self.valid_handler))

    def assert_originals_unchanged(self):
        self.assertTrue(all(sha(path) == before for path, before in self.original_files.items()))

    async def test_only_two_failed_pilots_are_new_then_four_main_and_no_rebilling(self):
        progress = await self.runner().execute('all')
        self.assertEqual(len(self.original_calls), 4)
        self.assertEqual(len(self.calls), 6)
        self.assertEqual(set(self.calls[:2]), {'gpt-6-luna_pilot', 'claude-haiku-5-5_pilot'})
        self.assertEqual(set(self.calls[2:]), {m + '_main' for m in study.MODELS})
        self.assertEqual((progress['accepted'], progress['failed'], progress['remaining']), (8, 0, 0))
        self.assertEqual(progress['inherited'], 2)
        self.assertGreater(progress['charged_or_reserved_usd'], self.original_charge)
        self.assertEqual(len(api.BudgetLedger(self.experiment).data['attempts']), 10)
        before = (self.experiment / 'data/api_budget.json').read_bytes()
        same_amendment = recovery.prepare(self.parent)
        self.assertEqual(same_amendment, self.amendment)
        await self.runner().execute('all')
        self.assertEqual(len(self.calls), 6)
        self.assertEqual((self.experiment / 'data/api_budget.json').read_bytes(), before)
        self.assert_originals_unchanged()
        self.assertEqual(len(list((self.parent / 'accepted').glob('*.json'))), 2)

    async def test_exact_recovery_settings_and_frozen_payloads(self):
        manifest = recovery.load(self.amendment)
        self.assertEqual(len(manifest['new_task_ids']), 6)
        self.assertEqual(len(manifest['inherited_pilots']), 2)
        for task in self.plan['tasks']:
            if task['model'] in recovery.INHERITED_MODELS and task['phase'] == 'pilot':
                self.assertFalse((self.amendment / 'payloads' / (task['task_id'] + '.json')).exists())
                continue
            payload = study.read(self.amendment / 'payloads' / (task['task_id'] + '.json'))
            if task['model'] == 'gpt-6-luna':
                self.assertEqual(payload['reasoning']['effort'], 'medium')
                self.assertEqual(payload['max_output_tokens'], 16384 if task['phase'] == 'pilot' else 32768)
                self.assertIn(recovery.STATE_TRACKING_APPENDIX, payload['input'][0]['content'])
                self.assertNotIn('[28,10,12,12]', payload['input'][0]['content'])
            elif task['model'] == 'claude-haiku-5-5':
                self.assertEqual(payload['thinking'], {'type': 'adaptive'})
                self.assertEqual(payload['output_config']['effort'], 'low')
                self.assertEqual(payload['max_tokens'], 32768 if task['phase'] == 'pilot' else 65536)
            else:
                self.assertEqual(payload, api.payload_for(task))
        self.assertEqual(sum(r['pilot_calls'] for r in recovery.estimate(self.amendment)), 2)
        self.assertEqual(sum(r['main_calls'] for r in recovery.estimate(self.amendment)), 4)
        self.assert_originals_unchanged()

    async def test_second_semantic_failure_stops_without_replacement_or_main_calls(self):
        def bad(request):
            body = json.loads(request.content)
            task_id = request_task_id(body)
            self.calls.append(task_id)
            fixture = study.synthetic_fixture(self.tasks[task_id])
            if body['model'] == 'gpt-6-luna':
                fixture['chains'][0]['inventory_checkpoints'][2]['inventories'][0] += 1
            return httpx.Response(200, json=response(body, fixture))
        progress = await self.runner(bad).execute('all')
        self.assertEqual(len(self.calls), 2)
        self.assertEqual((progress['accepted'], progress['failed'], progress['skipped']), (3, 1, 4))
        self.assertFalse((self.amendment / 'accepted/gpt-6-luna_pilot.json').exists())
        self.assertEqual(recovery.prepare(self.parent), self.amendment)
        await self.runner(bad).execute('all')
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(len(list((self.parent / 'recovery').glob('*/manifest.json'))), 1)
        self.assert_originals_unchanged()

    async def test_transport_retry_retains_unknown_charge_and_same_payload(self):
        count = {}
        received = {}
        def flaky(request):
            body = json.loads(request.content)
            key = request_task_id(body)
            self.calls.append(key)
            count[key] = count.get(key, 0) + 1
            received.setdefault(key, []).append(body)
            if key == 'gpt-6-luna_pilot' and count[key] == 1:
                raise httpx.ReadTimeout('test interruption', request=request)
            return httpx.Response(200, json=response(body, study.synthetic_fixture(self.tasks[key])))
        result = await self.runner(flaky).execute('pilot')
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(result['accepted'], 4)
        self.assertEqual(received['gpt-6-luna_pilot'][0], received['gpt-6-luna_pilot'][1])
        unknown = [v for v in api.BudgetLedger(self.experiment).data['attempts'].values()
                   if v['status'] == 'unknown_charge']
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]['charge_usd'], unknown[0]['reserve_usd'])
        self.assert_originals_unchanged()

    async def test_original_budget_spend_remains_cumulative_and_blocks_network_at_cap(self):
        ledger = api.BudgetLedger(self.experiment)
        ledger.reserve('separate_authorized_reservation', 5 - ledger.spent, {'run': 'other'})
        result = await self.runner().execute('pilot')
        self.assertEqual(self.calls, [])
        self.assertEqual(result['charged_or_reserved_usd'], 5.)
        self.assertEqual(result['accepted'], 2)
        self.assert_originals_unchanged()

    async def test_saved_amendment_or_original_evidence_tamper_blocks_before_http(self):
        payload = self.amendment / 'payloads/gpt-6-luna_pilot.json'
        before = payload.read_bytes()
        changed = json.loads(before)
        changed['max_output_tokens'] = 999
        payload.write_text(json.dumps(changed))
        with self.assertRaisesRegex(ValueError, 'request changed'):
            self.runner()
        self.assertEqual(self.calls, [])
        payload.write_bytes(before)
        retained = self.parent / 'accepted/gpt-5.6-luna_pilot.json'
        retained.write_bytes(retained.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'Original evidence changed'):
            self.runner()
        self.assertEqual(self.calls, [])

    async def test_analysis_excludes_failed_originals_and_retains_recovery_provenance(self):
        before = recovery.analyze(self.amendment)
        self.assertEqual(sum(r['accepted_pilot_responses'] for r in before['model_status']), 2)
        self.assertTrue(all(r['mean_strong_minus_no'] is None for r in before['hypotheses']))
        await self.runner().execute('all')
        result = recovery.analyze(self.amendment)
        self.assertEqual(len(result['rounds']), 8448)
        self.assertEqual(len([r for r in result['rounds'] if r['phase'] == 'main']), 7680)
        self.assertEqual(len(result['chains']), 88)
        self.assertTrue(all(r['p_raw'] is None for r in result['hypotheses']))
        self.assertEqual(len(result['recovery_metadata']['inherited_pilots']), 2)
        self.assertEqual(set(result['recovery_metadata']['failed_pilot_diagnoses']), set(recovery.FAILED_MODELS))
        self.assertEqual(sum(r['accepted_main_responses'] for r in study.analyze(self.parent)['model_status']), 0)
        self.assert_originals_unchanged()

    async def test_missing_keys_leave_both_recovery_pilots_unpurchased(self):
        before = (self.experiment / 'data/api_budget.json').read_bytes()
        result = await recovery.Runner(self.amendment, keys={}, retry_delay=0,
            transport=httpx.MockTransport(self.valid_handler)).execute('all')
        self.assertEqual(self.calls, [])
        self.assertEqual(result['accepted'], 2)
        self.assertEqual(result['remaining'], 2)
        self.assertEqual((self.experiment / 'data/api_budget.json').read_bytes(), before)

    async def test_source_snapshot_and_valid_response_tamper_cannot_change_reports(self):
        snapshot = self.amendment / 'source_snapshot/batched_pressure_recovery.py'
        original = snapshot.read_bytes()
        snapshot.write_bytes(original + b'\n')
        with self.assertRaisesRegex(ValueError, 'implementation changed'):
            recovery.load(self.amendment)
        snapshot.write_bytes(original)
        await self.runner().execute('all')
        accepted = self.amendment / 'accepted/gpt-6-luna_main.json'
        value = json.loads(accepted.read_text())
        value['chains'][0]['probes'][0]['order'] += 1
        self.assertEqual(study.validate_response(self.tasks['gpt-6-luna_main'], value), [])
        accepted.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'matching immutable receipt'):
            recovery.analyze(self.amendment)

    async def test_recovery_report_shows_inherited_pilots_and_total_prior_spend(self):
        from beergame_study.batched_pressure_report import build_report
        result = build_report(self.parent, recovery=self.amendment)
        text = result['report'].read_text()
        self.assertIn('2/4 pilot responses accepted', text)
        self.assertIn('Two previously accepted GPT-5.6 pilots are reused', text)
        self.assertIn('medium effort', text)
        self.assertAlmostEqual(result['charged_or_reserved_usd'], self.original_charge)
        self.assertFalse((self.amendment / 'api_status.json').exists())


if __name__ == '__main__':
    unittest.main()
