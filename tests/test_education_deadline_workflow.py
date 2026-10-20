"""Offline batch-file and report checks using explicitly synthetic fixtures."""
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study import education_deadline_cohort as study
from beergame_study.education_deadline_report import build_report

spec = importlib.util.spec_from_file_location('education_workflow', ROOT/'scripts/education_deadline_workflow.py')
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run = study.prepare(study.Config(students=4, weeks=8, repetitions=1,
            label='batch-software-check', synthetic=True), root=self.root)
        self.tasks = study.read(self.run/'plan.json')['tasks']

    def tearDown(self):
        self.temporary.cleanup()

    def submit(self, source, confirm=True):
        return workflow.import_files(self.run, source, session_label='synthetic-batch',
                                     confirm_full_prompt=confirm)

    def folder(self):
        folder = self.root/'responses'
        folder.mkdir(exist_ok=True)
        for task in self.tasks:
            data = study.synthetic_response(self.run, task['task_id']).encode()+b'\r\n'
            (folder/(task['task_id']+'.json')).write_bytes(data)
        return folder

    def test_folder_batch_import_and_exact_reimport(self):
        folder = self.folder()
        result = self.submit(folder)
        self.assertEqual(len(result), 3)
        self.assertTrue(study.progress(self.run).accepted.all())
        for task in self.tasks:
            entry = study.load_accepted(self.run, task['task_id'])
            self.assertEqual((self.run/entry['raw_path']).read_bytes(),
                             (folder/(task['task_id']+'.json')).read_bytes())
        self.assertTrue(all(row['status'] == 'already_accepted_identical' for row in self.submit(folder)))

    def test_zip_same_filename_multiple_cases(self):
        source = self.root/'downloaded.zip'
        with ZipFile(source, 'w') as archive:
            for i, task in enumerate(self.tasks):
                archive.writestr(f'chat{i}/response.json', study.synthetic_response(self.run, task['task_id']))
        self.assertEqual(len(self.submit(source)), 3)
        self.assertEqual(len(list((self.run/'submissions').glob('*.zip'))), 1)

    def test_changed_response_cannot_replace_accepted(self):
        folder = self.folder()
        self.submit(folder)
        path = folder/(self.tasks[0]['task_id']+'.json')
        payload = json.loads(path.read_text())
        payload['chains'][0]['orders'][0][0] += 1
        path.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, 'different reply'):
            self.submit(folder)

    def test_conflicting_locked_single_json_retained_before_rejection(self):
        task_id = self.tasks[0]['task_id']
        source = self.root/'response.json'
        source.write_bytes(study.synthetic_response(self.run, task_id).encode('utf-8'))
        self.submit(source)
        locked_before = study.accepted_path(self.run, task_id).read_bytes()
        payload = json.loads(source.read_bytes())
        payload['chains'][0]['orders'][0][0] += 1
        changed = json.dumps(payload, indent=2).encode('utf-8')+b'\r\n'
        source.write_bytes(changed)
        with self.assertRaisesRegex(ValueError, 'different reply'):
            self.submit(source)
        saved = self.run/'submissions'/(hashlib.sha256(changed).hexdigest()+'.json')
        self.assertEqual(saved.read_bytes(), changed)
        self.assertEqual(study.accepted_path(self.run, task_id).read_bytes(), locked_before)
        self.assertEqual(len(list((self.run/'attempts').glob('*.txt'))), 1)

    def test_unidentified_submission_retained_and_confirmation_required(self):
        source = self.root/'response.json'
        source.write_bytes(b'{not complete')
        with self.assertRaisesRegex(ValueError, 'Confirm'):
            self.submit(source, confirm=False)
        self.assertFalse((self.run/'unassigned_submissions').exists())
        with self.assertRaisesRegex(ValueError, 'Cannot identify'):
            self.submit(source)
        self.assertEqual(next((self.run/'unassigned_submissions').glob('*.txt')).read_bytes(), source.read_bytes())
        saved = self.run/'submissions'/(hashlib.sha256(source.read_bytes()).hexdigest()+'.json')
        self.assertEqual(saved.read_bytes(), source.read_bytes())

    def test_unhashable_task_ids_retained_as_unassigned(self):
        source = self.root/'response.json'
        for invalid in ({'unexpected': 'mapping'}, ['unexpected', 'list']):
            with self.subTest(task_id=invalid):
                payload = json.loads(study.synthetic_response(self.run, self.tasks[0]['task_id']))
                payload['task_id'] = invalid
                raw = json.dumps(payload).encode('utf-8')
                source.write_bytes(raw)
                with self.assertRaisesRegex(ValueError, 'Cannot identify'):
                    self.submit(source)
                signature = hashlib.sha256(raw).hexdigest()
                self.assertEqual((self.run/'submissions'/(signature+'.json')).read_bytes(), raw)
                self.assertEqual((self.run/'unassigned_submissions'/(signature+'.txt')).read_bytes(), raw)
        self.assertFalse(study.progress(self.run).accepted.any())

    def test_duplicate_task_in_zip_rejected(self):
        source = self.root/'duplicate.zip'
        data = study.synthetic_response(self.run, self.tasks[0]['task_id'])
        with ZipFile(source, 'w') as archive:
            archive.writestr('first.json', data)
            archive.writestr('second.json', data)
        with self.assertRaisesRegex(ValueError, 'Duplicate task'):
            self.submit(source)
        self.assertEqual(int(study.progress(self.run).accepted.sum()), 1)

    def test_duplicate_zip_member_retained_before_slot_check(self):
        source = self.root/'duplicate-different-bytes.zip'
        first = study.synthetic_response(self.run, self.tasks[0]['task_id']).encode('utf-8')
        second = first+b'\r\n '
        with ZipFile(source, 'w') as archive:
            archive.writestr('first.json', first)
            archive.writestr('second.json', second)
        with self.assertRaisesRegex(ValueError, 'Duplicate task'):
            self.submit(source)
        for raw in (first, second):
            saved = self.run/'submissions'/(hashlib.sha256(raw).hexdigest()+'.json')
            self.assertEqual(saved.read_bytes(), raw)
        self.assertEqual(int(study.progress(self.run).accepted.sum()), 1)

    def test_partial_report_uses_real_pairs_and_deterministic_publication(self):
        path = self.root/'response.json'
        path.write_text(study.synthetic_response(self.run, self.tasks[0]['task_id']))
        self.submit(path)
        output = self.root/'report'
        result = build_report(self.run, output)
        self.assertEqual(result['accepted_responses'], 1)
        self.assertTrue(result['tables']['contrasts'].empty)
        report = (output/'REPORT.md').read_text(encoding='utf-8')
        self.assertIn('No requested case contrast is available', report)
        self.assertIn('SYNTHETIC SOFTWARE CHECK', report)
        previous = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob('*') if p.is_file()}
        build_report(self.run, output)
        self.assertEqual(previous, {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob('*') if p.is_file()})
        self.assertTrue((output/'results/RESULTS.xlsx').exists())

    def test_updated_report_archives_previous_publication_and_identical_check_is_idempotent(self):
        named = self.root/'reports/EDUCATION_DEADLINE_10S_60S'
        output = named/'website'
        with patch.object(workflow, 'ROOT', self.root), patch.object(workflow, 'OUTPUT', named):
            first = workflow.report(self.run, output)
            self.assertEqual(first['accepted_responses'], 0)
            previous = (output/'REPORT.md').read_bytes()
            source = self.root/'response.json'
            source.write_text(study.synthetic_response(self.run, self.tasks[0]['task_id']))
            self.submit(source)
            second = workflow.report(self.run, output)
            self.assertEqual(second['accepted_responses'], 1)
            archived = list((self.root/'reports/archive/education_deadline_20261019/website').glob('*/REPORT.md'))
            self.assertEqual(len(archived), 1)
            self.assertEqual(archived[0].read_bytes(), previous)
            self.assertTrue(workflow.report(self.run, output)['unchanged'])

    def test_unchanged_report_path_verifies_csv_and_complete_output_hashes(self):
        named = self.root/'reports/EDUCATION_DEADLINE_10S_60S'
        output = named/'website'
        with patch.object(workflow, 'ROOT', self.root), patch.object(workflow, 'OUTPUT', named):
            workflow.report(self.run, output)
            provenance = study.read(output/'provenance.json')
            published = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in output.rglob('*') if p.is_file() and p.name != 'provenance.json'}
            self.assertEqual(provenance['outputs_sha256'], published)
            self.assertTrue(workflow.report(self.run, output)['unchanged'])
            target = output/'results/hypothesis_summary.csv'
            target.write_bytes(target.read_bytes()+b'tampered CSV\n')
            before = {p.relative_to(output).as_posix(): p.read_bytes()
                      for p in output.rglob('*') if p.is_file()}
            with self.assertRaisesRegex(ValueError, 'differing publication'):
                workflow.report(self.run, output)
            after = {p.relative_to(output).as_posix(): p.read_bytes()
                     for p in output.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            self.assertFalse((self.root/'reports/archive').exists())

    def test_optional_serialization_syntax_failure_is_recorded_without_execution(self):
        finalizer_spec = importlib.util.spec_from_file_location(
            'education_preflight_finalizer_test', ROOT/'scripts/finalize_education_preflight.py')
        finalizer = importlib.util.module_from_spec(finalizer_spec)
        with patch.dict(sys.modules, {'education_deadline_workflow': workflow}):
            finalizer_spec.loader.exec_module(finalizer)
        source = self.root/'optional_serialization.py'
        raw = b"raise AssertionError('This source must never execute')\nbroken(\n"
        source.write_bytes(raw)
        payload = json.loads(study.synthetic_response(self.run, self.tasks[0]['task_id']))
        result = finalizer.literal_source_check(source, payload)
        self.assertTrue(result['source_present'])
        self.assertTrue(result['source_parse_error'])
        self.assertEqual(result['explicit_chain_records_matched'], 0)
        self.assertFalse(result['source_executed_by_importer'])
        self.assertEqual(result['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(source.read_bytes(), raw)

    def test_report_replacement_cannot_move_an_external_output_directory(self):
        output = self.root/'unexpected'
        build_report(self.run, output)
        source = self.root/'response.json'
        source.write_text(study.synthetic_response(self.run, self.tasks[0]['task_id']))
        self.submit(source)
        with patch.object(workflow, 'ROOT', self.root), patch.object(workflow, 'OUTPUT', self.root/'intended'):
            with self.assertRaisesRegex(ValueError, 'named study folder'):
                workflow.report(self.run, output)
        self.assertTrue((output/'REPORT.md').exists())


if __name__ == '__main__':
    unittest.main()
