"""Offline portability checks on copied evidence, with no new observations.

The small history fixture verifies local path mapping and rejection behavior.
The release integration check separately verifies the complete historical
baseline and independently replays all 108,000 recorded role-week states.
"""
from contextlib import contextmanager
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study import education_deadline_cohort as scientific
from beergame_study import education_deadline_collection as collection

spec = importlib.util.spec_from_file_location('beergame_handoff_verifier_test',
                                            ROOT/'scripts/verify_beergame_handoff.py')
portable = importlib.util.module_from_spec(spec)
spec.loader.exec_module(portable)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class HandoffPortabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)/'移転した 作業 folder'
        cls.root.mkdir()
        cls.pointer = scientific.read(ROOT/'reports/LATEST_EDUCATION_DEADLINE_COLLECTION.json')
        cls.collection_run = cls.root/cls.pointer['collection_run']
        shutil.copytree(ROOT/cls.pointer['collection_run'], cls.collection_run)
        cls.manifest = scientific.read(cls.collection_run/'manifest.json')
        cls.parent = cls.collection_run/cls.manifest['lineage']['snapshot_relative_path']
        cls.plan = scientific.read(cls.collection_run/'plan.json')
        directories = [
            'src', 'config/student_profiles', 'docs/education_deadline_20261019',
            'data/runs/'+cls.manifest['lineage']['parent_study_id'],
            'data/submissions/education_deadline_astra_20261020', cls.pointer['report_folder'],
        ]
        for relative in directories:
            target = cls.root/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(ROOT/relative, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        files = [portable.POINTER, 'scripts/verify_beergame_handoff.py',
                 'scripts/check_education_deadline_collection.py',
                 'tests/test_education_deadline_cohort.py',
                 'docs/EDUCATION_DEADLINE_PROTOCOL_20261019.md']
        for relative in files:
            target = cls.root/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/relative, target)
        # This deliberately pared history fixture is not the production 15,013
        # file baseline. The release integration check verifies that full map.
        cls.history = cls.root/'portability_fixture_preserved_evidence.bin'
        cls.history.write_bytes(b'An explicitly test-only preserved control.\r\n')
        baseline = cls.root/portable.BASELINE
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_text(json.dumps({'files': {
            cls.history.relative_to(cls.root).as_posix(): sha(cls.history.read_bytes())
        }}), encoding='utf-8')

    def replace(self, path, data):
        path = Path(path)
        original = path.read_bytes()
        self.addCleanup(path.write_bytes, original)
        path.write_bytes(data)

    @contextmanager
    def local_reads_only(self):
        """Fail if a portable evidence check consults any original machine path."""
        read_bytes, read_text = Path.read_bytes, Path.read_text
        root = self.root.resolve()

        def check(path):
            resolved = Path(path).resolve()
            if not resolved.is_relative_to(root):
                raise AssertionError('Attempted nonportable external read: '+str(path))

        def local_bytes(path, *args, **kwargs):
            check(path)
            return read_bytes(path, *args, **kwargs)

        def local_text(path, *args, **kwargs):
            check(path)
            return read_text(path, *args, **kwargs)

        with patch.object(Path, 'read_bytes', local_bytes), patch.object(Path, 'read_text', local_text), \
                patch.object(collection, 'audit', side_effect=AssertionError('Frozen audit consulted original paths')), \
                patch.object(collection, 'load_accepted', side_effect=AssertionError('Frozen loader consulted original paths')), \
                patch.object(collection, 'parent_run', side_effect=AssertionError('Frozen parent resolver was called')):
            yield

    def accepted(self):
        return portable._verify_accepted(self.collection_run, self.parent, self.manifest, self.plan,
                                         scientific, collection)

    def first_entry(self):
        task_id = self.plan['tasks'][0]['task_id']
        path = self.collection_run/'accepted'/(task_id+'.json')
        return path, scientific.read(path)

    def test_relative_mapping_preserves_unicode_spaces_and_nested_names(self):
        relative = '資料 and files/response one.json'
        self.assertEqual(portable._inside(self.root, relative), (self.root/relative).resolve())
        self.assertTrue(portable._inside(self.root, 'data/collections').is_relative_to(self.root.resolve()))

    def test_relative_mapping_rejects_absolute_paths_and_traversal_on_all_hosts(self):
        invalid = ('../outside.json', 'sub/../../outside.json', '..\\outside.json',
                   'sub\\..\\..\\outside.json', 'D:\\beergame\\data\\original.json',
                   'D:/beergame/data/original.json', '/outside.json',
                   '\\\\server\\share\\outside.json', '', None)
        for relative in invalid:
            with self.subTest(relative=relative), self.assertRaises((AssertionError, ValueError)):
                portable._inside(self.root, relative)

    def test_all_six_original_payloads_verify_using_only_relocated_local_paths(self):
        before = (self.collection_run/'manifest.json').read_bytes()
        # These original provenance strings remain untouched. The guarded read
        # context makes relying on their still-existing D: files fail the test.
        self.assertTrue(self.manifest['lineage']['original_parent_path'].startswith('D:'))
        with self.local_reads_only():
            payloads, hashes = self.accepted()
        self.assertEqual(len(payloads), 6)
        self.assertEqual(len(hashes), 6)
        self.assertEqual(sum(len(c['orders'])*4 for p in payloads.values() for c in p['chains']), 60000)
        self.assertEqual(sum(len(c['probes']) for p in payloads.values() for c in p['chains']), 3000)
        self.assertTrue(all(p['study_id'] == self.manifest['lineage']['parent_study_id']
                            for p in payloads.values()))
        self.assertEqual((self.collection_run/'manifest.json').read_bytes(), before)

    def test_tampered_original_raw_bytes_block_verification(self):
        _, entry = self.first_entry()
        raw = self.collection_run/entry['raw_path']
        self.replace(raw, raw.read_bytes()+b' ')
        with self.local_reads_only(), self.assertRaises((AssertionError, ValueError)):
            self.accepted()

    def test_mismatched_receipt_blocks_verification(self):
        accepted, entry = self.first_entry()
        changed = copy.deepcopy(entry)
        changed['session_label'] = 'altered receipt'
        self.replace(accepted, json.dumps(changed).encode('utf-8'))
        with self.local_reads_only(), self.assertRaises((AssertionError, ValueError)):
            self.accepted()

    def test_coherent_reported_settings_tamper_blocks_verification(self):
        accepted, entry = self.first_entry()
        changed = copy.deepcopy(entry)
        changed['model_label'] = 'GPT-6'
        altered = json.dumps(changed).encode('utf-8')
        self.replace(accepted, altered)
        self.replace((self.collection_run/entry['raw_path']).with_suffix('.json'), altered)
        with self.local_reads_only(), self.assertRaises((AssertionError, ValueError)):
            self.accepted()

    def test_rewritten_payload_study_id_is_not_accepted_as_relocation(self):
        accepted, entry = self.first_entry()
        changed = copy.deepcopy(entry)
        changed['payload']['study_id'] = self.manifest['study_id']
        raw = json.dumps(changed['payload']).encode('utf-8')
        changed['raw_sha256'] = sha(raw)
        altered = json.dumps(changed).encode('utf-8')
        self.replace(self.collection_run/entry['raw_path'], raw)
        self.replace(accepted, altered)
        self.replace((self.collection_run/entry['raw_path']).with_suffix('.json'), altered)
        with self.local_reads_only(), self.assertRaises((AssertionError, ValueError)):
            self.accepted()

    def test_changed_local_prompt_does_not_fall_back_to_original_drive(self):
        task_id = self.plan['tasks'][0]['task_id']
        prompt = self.collection_run/'prompts'/(task_id+'.txt')
        self.replace(prompt, prompt.read_bytes()+b' ')
        with self.local_reads_only(), self.assertRaises((AssertionError, ValueError)):
            self.accepted()

    def test_main_verifier_accepts_relocated_copies_and_discloses_scope(self):
        receipt = portable.verify(self.root, full_replay=False)
        self.assertIs(receipt['verified'], True)
        self.assertEqual(Path(receipt['root']), self.root.resolve())
        self.assertEqual(receipt['accepted_responses'], 6)
        self.assertEqual(receipt['original_parent_accepted_responses'], 0)
        self.assertEqual(receipt['submitted_weekly_orders'], 60000)
        self.assertEqual(receipt['prior_files_verified_unchanged'], 1)
        self.assertIs(receipt['historical_external_paths_rechecked'], False)
        self.assertIs(receipt['independent_replay_performed'], False)
        self.assertEqual(receipt['independently_recomputed_states'], 0)
        self.assertTrue(receipt['skipped_checks'])
        self.assertEqual(receipt['paid_api_calls'], 0)
        self.assertIs(receipt['frozen_files_modified'], False)
        self.assertEqual(receipt['historical_original_parent_path'],
                         self.manifest['lineage']['original_parent_path'])

    def test_main_verifier_blocks_changed_preserved_evidence(self):
        self.replace(self.history, self.history.read_bytes()+b'changed')
        with self.assertRaisesRegex(AssertionError, 'Earlier preserved file differs'):
            portable.verify(self.root, full_replay=False)

    def test_main_verifier_blocks_changed_published_table(self):
        csv = self.root/self.pointer['report_folder']/'results/hypothesis_summary.csv'
        self.replace(csv, csv.read_bytes()+b'changed publication\n')
        with self.assertRaisesRegex(AssertionError, 'Publication output hash differs'):
            portable.verify(self.root, full_replay=False)

    def test_main_verifier_blocks_changed_fingerprint(self):
        manifest_path = self.collection_run/'manifest.json'
        altered = copy.deepcopy(self.manifest)
        altered['lineage']['original_parent_path'] = 'Q:\\old machine\\changed parent'
        self.replace(manifest_path, json.dumps(altered).encode('utf-8'))
        with self.assertRaisesRegex(AssertionError, 'collection fingerprint differs'):
            portable.verify(self.root, full_replay=False)

    def test_main_verifier_blocks_pointer_escape_before_loading_evidence(self):
        pointer_path = self.root/portable.POINTER
        changed = copy.deepcopy(self.pointer)
        changed['collection_run'] = '../outside-collection'
        self.replace(pointer_path, json.dumps(changed).encode('utf-8'))
        with self.assertRaisesRegex(AssertionError, 'Evidence path escapes'):
            portable.verify(self.root, full_replay=False)

    def test_main_verifier_checks_optional_transfer_manifest(self):
        transferred = self.root/'portability_fixture_transfer_only.bin'
        manifest = self.root/'HANDOFF_FILES_SHA256.json'
        self.addCleanup(transferred.unlink, missing_ok=True)
        self.addCleanup(manifest.unlink, missing_ok=True)
        transferred.write_bytes(b'A separate transfer-integrity control.\n')
        manifest.write_text(json.dumps({'files_sha256': {
            transferred.name: sha(transferred.read_bytes())
        }}), encoding='utf-8')
        receipt = portable.verify(self.root, full_replay=False)
        self.assertIs(receipt['transfer_manifest_present'], True)
        self.assertEqual(receipt['transfer_files_verified'], 1)
        transferred.write_bytes(b'A corrupted transfer-only control.\n')
        with self.assertRaisesRegex(AssertionError, 'Transferred file differs'):
            portable.verify(self.root, full_replay=False)


if __name__ == '__main__':
    unittest.main()
