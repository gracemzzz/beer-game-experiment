"""Temporary-file reporting, CLI and notebook checks; no model calls."""
import ast
from contextlib import redirect_stdout
import importlib.util
import inspect
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study import batched_pressure as study
from beergame_study import batched_pressure_api as api
from beergame_study.batched_pressure_report import build_report


def script(name):
    specification = importlib.util.spec_from_file_location('test_' + name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def temporary_experiment(base):
    experiment = Path(base).resolve()
    protocol = experiment / 'hypotheses/PROTOCOL.md'
    protocol.parent.mkdir(parents=True, exist_ok=True)
    protocol.write_bytes((ROOT / 'experiments/12_pressure_framing_api_20261020/hypotheses/PROTOCOL.md').read_bytes())
    return experiment


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.experiment = temporary_experiment(self.temporary.name)
        self.run = study.prepare(self.experiment)
        self.plan = study.loadplan(self.run)

    def test_pending_report_has_conclusions_first_and_no_invented_findings(self):
        with patch.object(api, 'Runner', side_effect=AssertionError('Reporting must not use API')):
            published = build_report(self.run)
        text = published['report'].read_text()
        self.assertTrue(text.startswith('# Experiment 12: conclusions first'))
        self.assertIn('0/4 main responses and 0/4 pilot responses accepted', text)
        self.assertIn('No main API results have been collected', text)
        self.assertLess(text.index('1. **Collection:**'), text.index('## Design'))
        hypotheses = pd.read_csv(published['analysis'] / 'hypotheses.csv')
        self.assertEqual(len(hypotheses), 8)
        self.assertTrue(hypotheses.mean_strong_minus_no.isna().all())
        self.assertFalse(hypotheses.inference_available.any())
        self.assertEqual(published['charged_or_reserved_usd'], 0)
        self.assertFalse((self.experiment / 'data/api_budget.json').exists())
        self.assertTrue(published['workbook'].is_file())

    def test_full_synthetic_fixture_exports_every_order_without_inferential_claims(self):
        # Explicit software fixtures live only under this temporary directory.
        for task in self.plan['tasks']:
            study.save_new(self.run / task['response_path'], study.synthetic_fixture(task))
        published = build_report(self.run)
        text = published['report'].read_text()
        self.assertIn('4/4 main responses and 4/4 pilot responses accepted', text)
        self.assertIn('No p-values or inferential confidence intervals', text)
        rounds = pd.read_csv(published['analysis'] / 'rounds.csv')
        self.assertEqual(len(rounds), 8448)
        self.assertEqual(len(rounds[rounds.phase == 'main']), 7680)
        self.assertEqual((int(rounds.week.min()), int(rounds.week.max())), (1, 24))
        hypotheses = pd.read_csv(published['analysis'] / 'hypotheses.csv')
        self.assertTrue((hypotheses.descriptive_direction == 'zero').all())
        self.assertTrue(hypotheses.p_raw.isna().all())
        self.assertTrue(hypotheses.p_holm_8.isna().all())
        workbook = pd.read_excel(published['workbook'], sheet_name='rounds')
        self.assertEqual(len(workbook), 8448)
        self.assertEqual(workbook.order.tolist(), rounds.order.tolist())
        first_bytes = published['report'].read_bytes()
        repeated = build_report(self.run)
        self.assertEqual(repeated['report'], published['report'])
        self.assertEqual(repeated['report'].read_bytes(), first_bytes)

    def test_partial_data_stays_partial_and_prior_report_is_preserved(self):
        pending = build_report(self.run)
        original = pending['report'].read_bytes()
        one_main = next(t for t in self.plan['tasks'] if t['phase'] == 'main')
        study.save_new(self.run / one_main['response_path'], study.synthetic_fixture(one_main))
        partial = build_report(self.run)
        self.assertNotEqual(partial['report'], pending['report'])
        self.assertEqual(pending['report'].read_bytes(), original)
        values = partial['summary']['hypotheses']
        self.assertEqual(sum(v['mean_strong_minus_no'] is not None for v in values), 2)
        self.assertEqual(sum(v['mean_strong_minus_no'] is None for v in values), 6)
        pointer = json.loads((self.experiment / 'reports/LATEST.json').read_text())
        self.assertEqual(pointer['main_responses'], 1)
        self.assertEqual(pointer['pilot_responses'], 0)
        self.assertEqual(pointer['report'], partial['report'].relative_to(self.experiment).as_posix())

    def test_cli_default_prepares_report_without_key_input_or_api(self):
        cli = script('run_batched_pressure')
        with patch.object(sys, 'argv', ['run_batched_pressure.py', '--experiment', str(self.experiment)]), \
             patch.object(cli, 'Runner', side_effect=AssertionError('Default CLI must not use API')), \
             patch.object(cli.getpass, 'getpass', side_effect=AssertionError('Default CLI must not ask for keys')), \
             redirect_stdout(io.StringIO()) as output:
            cli.main()
        self.assertIn('Report:', output.getvalue())
        self.assertIn('Workbook:', output.getvalue())
        self.assertFalse((self.experiment / 'data/api_budget.json').exists())
        self.assertEqual(list((self.run / 'accepted').glob('*.json')), [])


class NotebookTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_default_notebook_cells_execute_without_api_or_key_prompt(self):
        with tempfile.TemporaryDirectory() as temporary:
            experiment = temporary_experiment(Path(temporary) / 'experiment')
            destination = Path(temporary) / 'RUN_EXPERIMENT.ipynb'
            builder = script('create_batched_pressure_notebook')
            with patch.object(builder, 'DESTINATION', destination), redirect_stdout(io.StringIO()):
                builder.main()
            notebook = nbformat.read(destination, as_version=4)
            nbformat.validate(notebook)
            namespace = {'__name__': '__main__'}
            code_cells = 0
            with patch.object(api, 'Runner', side_effect=AssertionError('Review notebook must not call API')), \
                 patch('getpass.getpass', side_effect=AssertionError('Review notebook must not ask for keys')), \
                 patch('IPython.display.display', return_value=None), redirect_stdout(io.StringIO()):
                for index, cell in enumerate(notebook.cells):
                    if cell.cell_type != 'code':
                        continue
                    code_cells += 1
                    compiled = compile(cell.source, f'notebook-cell-{index}', 'exec',
                                       flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
                    value = eval(compiled, namespace)
                    if inspect.isawaitable(value):
                        await value
                    if 'EXPERIMENT = ROOT /' in cell.source:
                        # Route output to a test directory after real setup/root discovery.
                        namespace['EXPERIMENT'] = experiment
            self.assertEqual(code_cells, 5)
            self.assertIs(namespace['RUN_API'], False)
            self.assertEqual(namespace['PHASE'], 'all')
            self.assertFalse((experiment / 'data/api_budget.json').exists())
            self.assertTrue((experiment / 'reports/REPORT.md').exists())
            self.assertEqual(list(namespace['run_dir'].glob('accepted/*.json')), [])
            self.assertIn('0/4 main responses', (experiment / 'reports/REPORT.md').read_text())


if __name__ == '__main__':
    unittest.main()
