"""Reproducible full reports and incomplete-run exports using synthetic calls only."""
import asyncio
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_student_hypothesis_report import build_report, resolve_report_run
from beergame_study import student_study, student_report
from beergame_study.reasoning_protocol import ReasoningConfig


class HypothesisExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        config = ReasoningConfig(mode='offline', stage='game', weeks=20,
            groups_per_condition=1, replicate_id='full-hypothesis-export-check')
        with patch.object(student_study, 'ROOT', self.root), \
                patch('beergame_study.student_report.build_report'), \
                patch('openai.AsyncOpenAI', side_effect=AssertionError('Paid calls forbidden')):
            self.run = asyncio.run(student_study.run_campaign(config))
        self.prepare_original_summary()

    def tearDown(self):
        self.temporary.cleanup()

    def prepare_original_summary(self):
        with patch.object(student_report, '_plots', return_value=[]), \
                patch.object(student_report, '_docx'), patch.object(student_report, '_workbook'):
            student_report.build_report(self.run)

    def evidence_hashes(self):
        return {str(p.relative_to(self.run)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in self.run.rglob('*') if p.is_file() and 'hypothesis_analysis' not in p.parts}

    def test_word_excel_and_csv_agree_and_preserve_raw_evidence(self):
        before = self.evidence_hashes()
        with patch('openai.AsyncOpenAI', side_effect=AssertionError('Paid calls forbidden')):
            output = build_report(self.run, reports_root=self.root/'reports')
        self.assertEqual(before, self.evidence_hashes())
        self.assertEqual(output.parent, self.root/'reports')
        self.assertFalse((self.run/'hypothesis_analysis').exists())
        self.assertEqual(resolve_report_run(output/'REPORT.md'), self.run)
        pointer = json.loads((self.root/'reports/LATEST_STUDENT_HYPOTHESIS_REPORT.json').read_text())
        self.assertEqual(Path(pointer['word_report']), output/'Student_Pilot_Report.docx')
        self.assertTrue(all(Path(p).is_file() for p in (self.root/'reports/LATEST_REPORT.txt').read_text().splitlines()))
        hypotheses = pd.read_csv(output / 'hypotheses.csv')
        workbook = pd.read_excel(output / 'DETAILS.xlsx', sheet_name='hypotheses')
        pd.testing.assert_frame_equal(hypotheses, workbook, check_dtype=False)
        self.assertTrue(hypotheses[['p_raw', 'p_holm', 'ci_lower', 'ci_upper']].isna().all().all())
        text = (output / 'REPORT.md').read_text(encoding='utf-8')
        self.assertIn('SYNTHETIC SOFTWARE BENCHMARK', text)
        self.assertIn('Paired chain-block contrasts', text)
        self.assertIn('Inference prerequisites', text)
        doc = Document(output / 'Student_Pilot_Report.docx')
        self.assertEqual(len(doc.inline_shapes), 2)
        self.assertGreaterEqual(len(doc.tables), 10)
        manifest = json.loads((output / 'analysis_manifest.json').read_text())
        self.assertEqual(manifest['paid_api_calls'], 0)
        self.assertTrue(manifest['input_evidence_unchanged'])
        self.assertEqual(manifest['analysis_summary']['planned_pairs'], 1)
        self.assertTrue(manifest['calibration_evidence']['file_sha256'])
        self.assertEqual(output, build_report(self.run, update_pointer=False, reports_root=self.root/'reports'))
        previous = json.loads((output/'analysis_manifest.json').read_text())['analysis_fingerprint']
        old_files = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
        with patch('build_student_hypothesis_report.VERSION', 'report-layout-revision-test'):
            self.assertEqual(output, build_report(self.run, reports_root=self.root/'reports'))
        archived = self.root/'reports/archive/analysis_versions'/self.run.name/previous[:16]
        self.assertTrue(archived.is_dir())
        self.assertEqual(old_files, {p.relative_to(archived): p.read_bytes() for p in archived.rglob('*') if p.is_file()})
        self.assertEqual(before, self.evidence_hashes())

    def test_partial_scoring_keeps_observations_and_withholds_full_cost_contrast(self):
        tail = pd.read_csv(self.run / 'continuation.csv')
        tail = tail[~((tail.group_id == 'b000_adequate') & (tail.week >= 31))]
        tail.to_csv(self.run / 'continuation.csv', index=False)
        progress = json.loads((self.run / 'progress.json').read_text())
        progress['phase'] = 'stopped'
        (self.run / 'progress.json').write_text(json.dumps(progress))
        self.prepare_original_summary()
        output = build_report(self.run, update_pointer=False, reports_root=self.root/'reports')
        hypotheses = pd.read_csv(output / 'hypotheses.csv').set_index('hypothesis')
        self.assertEqual(hypotheses.loc['H2', 'complete_pairs'], 0)
        self.assertTrue(pd.isna(hypotheses.loc['H2', 'estimate']))
        groups = pd.read_csv(output / 'groups.csv').set_index('group_id')
        self.assertTrue(pd.isna(groups.loc['b000_adequate', 'total_scored_cost']))
        self.assertGreater(groups.loc['b000_adequate', 'total_observed_cost'], 0)
        text = (output / 'REPORT.md').read_text(encoding='utf-8')
        self.assertIn('Saved run status: stopped', text)
        self.assertNotIn('both chains scored 156', text)


if __name__ == '__main__':
    unittest.main()
