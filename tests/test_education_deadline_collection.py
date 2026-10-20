"""Synthetic-only checks for reported settings and immutable parent lineage.

The adapter must preserve the originally submitted scientific payload while
recording the user's later settings report truthfully. These fixtures do not
validate a provider identity, time intervention, or substantive hypothesis.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study import education_deadline_cohort as core
from beergame_study import education_deadline_collection as collection
from beergame_study.education_deadline_report import build_report


MODEL = 'GPT-6 Astra'
EFFORT = 'extra high effort'
STATEMENT = "I'm using gpt 6-astra extra high effort"


def file_bytes(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in Path(folder).rglob('*') if p.is_file()}


class ReportedSettingsCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.cfg = core.Config(students=16, repetitions=2, synthetic=True,
                               label='reported-settings-software-check')
        self.parent = core.prepare(self.cfg, root=self.root)
        self.parent_before = file_bytes(self.parent)
        self.run = collection.prepare_collection(self.parent, model_label=MODEL,
            effort_label=EFFORT, operator_statement=STATEMENT, date='2026-10-20', root=self.root)
        self.tasks = core.read(self.parent/'plan.json')['tasks']
        self.sequence = 0

    def tearDown(self):
        self.temporary.cleanup()

    def payload(self, task_id):
        return json.loads(core.synthetic_response(self.parent, task_id))

    def submit(self, task_id, payload=None, raw=None, **overrides):
        self.sequence += 1
        path = self.root/f'original_reply_{self.sequence}.json'
        data = raw if raw is not None else json.dumps(
            self.payload(task_id) if payload is None else payload).encode('utf-8')
        path.write_bytes(data)
        options = dict(session_label='synthetic-reported-settings-check',
                       evidence_kind='synthetic_test')
        options.update(overrides)
        return collection.import_response(self.run, task_id, path, **options)

    def test_truthful_settings_separate_fingerprint_and_parent_unchanged(self):
        manifest = collection.audit(self.run)
        self.assertEqual(manifest['config']['model_label'], MODEL)
        self.assertEqual(manifest['config']['effort_label'], EFFORT)
        self.assertEqual(manifest['config']['collection'], 'user_supplied')
        self.assertEqual(manifest['planned_config']['model_label'], 'GPT-6')
        self.assertEqual(manifest['planned_config']['effort_label'], 'pro')
        reported = manifest['reported_settings']
        self.assertEqual(reported['operator_statement'], STATEMENT)
        self.assertEqual(reported['verification'], 'user_reported_not_provider_verified')
        self.assertIs(reported['reported_after_response_generation'], True)
        self.assertEqual(reported['report_date'], '2026-10-20')
        self.assertNotEqual(self.run, self.parent)
        self.assertEqual(manifest['lineage']['parent_study_id'], self.parent.name)
        self.assertEqual(collection.prepare_collection(self.parent, model_label=MODEL,
            effort_label=EFFORT, operator_statement=STATEMENT, date='2026-10-20', root=self.root), self.run)
        # A literal API-style token is a different report, not an alias for the
        # user's wording or for the frozen plan's Pro label.
        another = collection.prepare_collection(self.parent, model_label=MODEL,
            effort_label='xhigh', operator_statement=STATEMENT, date='2026-10-20', root=self.root)
        self.assertNotEqual(another, self.run)
        self.assertEqual(self.parent_before, file_bytes(self.parent))

    def test_original_bytes_original_ids_and_unknown_provenance_retained(self):
        task_id = self.tasks[0]['task_id']
        payload = self.payload(task_id)
        raw = ('\r\n```json\r\n'+json.dumps(payload, indent=2)+'\r\n```\r\n ').encode('utf-8')
        entry = self.submit(task_id, raw=raw)
        self.assertEqual(entry['model_label'], MODEL)
        self.assertEqual(entry['effort_label'], EFFORT)
        self.assertEqual(entry['planned_model_label'], 'GPT-6')
        self.assertEqual(entry['planned_effort_label'], 'pro')
        self.assertEqual(entry['parent_study_id'], self.parent.name)
        self.assertEqual(entry['payload']['study_id'], self.parent.name)
        self.assertEqual(entry['payload']['task_id'], task_id)
        self.assertIsNone(entry['full_prompt_confirmed'])
        self.assertIsNone(entry['fresh_chat_confirmed'])
        self.assertIsNone(entry['actual_reasoning_tokens'])
        self.assertIsNone(entry['actual_wall_time_s'])
        self.assertEqual(entry['api_calls'], 0)
        self.assertEqual((self.run/entry['raw_path']).read_bytes(), raw)
        self.assertEqual(entry['raw_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(collection.load_accepted(self.run, task_id)['payload'], payload)
        self.assertEqual(self.parent_before, file_bytes(self.parent))

    def test_confirmation_values_and_synthetic_evidence_are_not_invented(self):
        task_id = self.tasks[0]['task_id']
        with self.assertRaises(ValueError):
            self.submit(task_id, evidence_kind='model_output')
        with self.assertRaises(ValueError):
            self.submit(task_id, full_prompt_confirmed='yes')
        with self.assertRaises(ValueError):
            self.submit(task_id, fresh_chat_confirmed='yes')
        entry = self.submit(task_id, full_prompt_confirmed=True, fresh_chat_confirmed=False)
        self.assertIs(entry['full_prompt_confirmed'], True)
        self.assertIs(entry['fresh_chat_confirmed'], False)

    def test_stale_payload_ids_rejected_and_exact_attempt_retained(self):
        task_id = self.tasks[0]['task_id']
        payload = self.payload(task_id)
        payload['study_id'] = 'stale-study-id'
        raw = json.dumps(payload, indent=2).encode('utf-8')
        with self.assertRaises(ValueError):
            self.submit(task_id, raw=raw)
        attempts = list((self.run/'attempts').glob('*.txt'))
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].read_bytes(), raw)
        self.assertEqual(core.read(attempts[0].with_suffix('.json'))['status'], 'rejected')
        self.assertFalse(collection.progress(self.run).accepted.any())
        self.assertEqual(self.parent_before, file_bytes(self.parent))

    def test_accepted_output_cannot_be_replaced_and_raw_tamper_rejected(self):
        task_id = self.tasks[0]['task_id']
        entry = self.submit(task_id)
        locked = collection.accepted_path(self.run, task_id).read_bytes()
        changed = self.payload(task_id)
        changed['chains'][0]['orders'][0][0] += 1
        with self.assertRaises(ValueError):
            self.submit(task_id, changed)
        self.assertEqual(collection.accepted_path(self.run, task_id).read_bytes(), locked)
        raw_path = self.run/entry['raw_path']
        raw_path.write_bytes(raw_path.read_bytes()+b' ')
        with self.assertRaises(ValueError):
            collection.load_accepted(self.run, task_id)

    def test_receipt_and_coherent_actual_setting_tamper_rejected(self):
        task_id = self.tasks[0]['task_id']
        entry = self.submit(task_id)
        accepted = collection.accepted_path(self.run, task_id)
        receipt = (self.run/entry['raw_path']).with_suffix('.json')
        original = accepted.read_bytes()
        changed = copy.deepcopy(entry)
        changed['model_label'] = 'GPT-6'
        accepted.write_text(json.dumps(changed), encoding='utf-8')
        with self.assertRaises(ValueError):
            collection.load_accepted(self.run, task_id)
        # Matching the duplicate receipt still cannot mislabel observed settings.
        receipt.write_bytes(accepted.read_bytes())
        with self.assertRaises(ValueError):
            collection.load_accepted(self.run, task_id)
        accepted.write_bytes(original)
        receipt.write_bytes(original)
        collection.load_accepted(self.run, task_id)

    def test_lineage_and_frozen_parent_prompt_tamper_rejected(self):
        manifest_path = self.run/'manifest.json'
        original = manifest_path.read_bytes()
        manifest = core.read(manifest_path)
        manifest['lineage']['parent_study_id'] = 'different-parent'
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaises(ValueError):
            collection.audit(self.run)
        manifest_path.write_bytes(original)
        parent_copy = collection.parent_run(self.run)
        prompt = parent_copy/'prompts'/(self.tasks[0]['task_id']+'.txt')
        saved_prompt = prompt.read_bytes()
        prompt.write_bytes(saved_prompt+b' ')
        with self.assertRaises(ValueError):
            collection.audit(self.run)
        prompt.write_bytes(saved_prompt)
        collection.audit(self.run)
        self.assertEqual(self.parent_before, file_bytes(self.parent))

    def test_partial_pairs_remain_missing_and_repeats_reuse_identities(self):
        by_arm = {t['arm']: t for t in self.tasks if t['repetition'] == 1}
        self.submit(by_arm['a60_control']['task_id'])
        self.assertTrue(collection.summarize(self.run)['contrasts'].empty)
        self.submit(by_arm['b10_control']['task_id'])
        tables = collection.summarize(self.run)
        self.assertEqual(set(tables['contrasts'].hypothesis), {'H1', 'H2'})
        self.assertEqual(len(tables['contrasts']), 8)
        self.assertEqual(set(tables['contrasts'].repetition), {1})
        self.assertEqual(tables['rounds'].participant_id.nunique(), 16)
        self.assertEqual(int(collection.progress(self.run).accepted.sum()), 2)

    def test_all_six_payloads_reproduce_frozen_core_metrics_exactly(self):
        reference = core.prepare(self.cfg, root=self.root/'reference')
        self.assertEqual(reference.name, self.parent.name)
        for task in self.tasks:
            task_id = task['task_id']
            payload = self.payload(task_id)
            value = {'a60_control': 4, 'b10_control': 8, 'c10_education': 2}[task['arm']]
            for chain_index, chain in enumerate(payload['chains']):
                chain['orders'] = [[value+(week+role+chain_index+task['repetition']) % 3
                                    for role in range(4)] for week in range(self.cfg.weeks-4)]
                chain['probes'] = [[8+value+role, value] for role in range(4)]
            raw = json.dumps(payload, separators=(',', ':')).encode('utf-8')
            self.submit(task_id, raw=raw)
            source = self.root/(task_id+'_reference.json')
            source.write_bytes(raw)
            core.import_response(reference, task_id, source, model_label=self.cfg.model_label,
                effort_label=self.cfg.effort_label, session_label='synthetic-reference',
                confirm_full_prompt=True, evidence_kind='synthetic_test')
        observed, expected = collection.summarize(self.run), core.summarize(reference)
        for name in ('rounds', 'probes', 'roles', 'chains', 'contrasts'):
            with self.subTest(table=name):
                pd.testing.assert_frame_equal(observed[name], expected[name])
        self.assertEqual(len(observed['rounds']), 6*16*36)
        self.assertEqual(len(observed['contrasts']), 32)
        self.assertEqual(observed['rounds'].participant_id.nunique(), 16)
        self.assertTrue(collection.progress(self.run).accepted.all())
        self.assertEqual(self.parent_before, file_bytes(self.parent))

    def test_report_discloses_observed_planned_and_post_collection_settings(self):
        self.submit(self.tasks[0]['task_id'])
        output = self.root/'reported_collection_publication'
        result = build_report(self.run, output, backend=collection)
        self.assertEqual(result['accepted_responses'], 1)
        text = (output/'REPORT.md').read_text(encoding='utf-8')
        self.assertIn(MODEL, text)
        self.assertIn(EFFORT, text)
        self.assertIn('GPT-6', text)
        self.assertIn('pro', text.lower())
        self.assertIn('planned', text.lower())
        self.assertIn('after', text.lower())
        self.assertIn('verif', text.lower())
        imports = pd.read_csv(output/'results/imports.csv')
        self.assertEqual(imports.model_label.tolist(), [MODEL])
        self.assertEqual(imports.effort_label.tolist(), [EFFORT])
        # The default report path continues to accept the original frozen core.
        old_output = self.root/'planned_parent_publication'
        old = build_report(self.parent, old_output)
        self.assertEqual(old['accepted_responses'], 0)
        self.assertNotIn(MODEL, (old_output/'REPORT.md').read_text(encoding='utf-8'))
        self.assertEqual(self.parent_before, file_bytes(self.parent))


if __name__ == '__main__':
    unittest.main()
