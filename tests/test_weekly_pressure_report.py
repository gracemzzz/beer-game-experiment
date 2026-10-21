"""Exercise free notebook use and partial-result reporting without network access."""
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
import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study import weekly_pressure as study
from beergame_study import weekly_pressure_api as api
from beergame_study.weekly_pressure_report import build_report


def setup_experiment(base):
    experiment = Path(base).resolve() / 'experiment13'
    protocol = experiment / 'hypotheses/PROTOCOL.md'
    protocol.parent.mkdir(parents=True, exist_ok=True)
    protocol.write_bytes((ROOT / 'experiments/13_weekly_state_api_20261021/hypotheses/PROTOCOL.md').read_bytes())
    budget = Path(base).resolve() / 'experiment12'
    (budget / 'data').mkdir(parents=True, exist_ok=True)
    # Existing campaign, not a new allowance; test only in a temporary directory.
    (budget / 'data/api_budget.json').write_text(json.dumps(dict(cap_usd=5., attempts={
        'prior-test-receipt': dict(charge_usd=.3404859, reserve_usd=.4, status='received')
    })))
    return experiment, budget


class WeeklyReportTests(unittest.TestCase):
    def test_no_data_report_preserves_prior_budget_and_does_not_invent_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            experiment, budget = setup_experiment(temporary)
            before = (budget / 'data/api_budget.json').read_bytes()
            run = study.prepare(experiment, budget)
            with patch('httpx.AsyncClient', side_effect=AssertionError('Report must not make HTTP calls')):
                report = build_report(run)
            text = report['report'].read_text()
            self.assertIn('0/4 models complete', text)
            self.assertIn('No complete hypothesis comparisons yet', text)
            self.assertIn('$0.340486', text)
            self.assertIn('$4.659514', text)
            self.assertLess(text.index('1. **Completion:**'), text.index('## Completion by model'))
            self.assertTrue(all(r['mean_strong_minus_no'] is None for r in report['summary']['hypotheses']))
            self.assertEqual((budget / 'data/api_budget.json').read_bytes(), before)
            self.assertTrue(report['workbook'].is_file())
            self.assertEqual(build_report(run)['report'], report['report'])


class WeeklyNotebookTests(unittest.IsolatedAsyncioTestCase):
    async def test_hidden_key_collection_branch_runs_pilots_and_clears_credentials(self):
        with tempfile.TemporaryDirectory() as temporary:
            experiment, budget = setup_experiment(temporary)
            specification = importlib.util.spec_from_file_location('weekly_builder_live_branch', ROOT / 'scripts/create_weekly_pressure_notebook.py')
            builder = importlib.util.module_from_spec(specification)
            specification.loader.exec_module(builder)
            destination = Path(temporary) / 'RUN_EXPERIMENT.ipynb'
            with patch.object(builder, 'DESTINATION', destination), redirect_stdout(io.StringIO()):
                builder.main()
            notebook = nbformat.read(destination, as_version=4)
            namespace = {'__name__': '__main__'}
            sent = []
            def respond(request):
                body = json.loads(request.content)
                schema = (body.get('text', {}).get('format') or body['output_config']['format'])['schema']
                ident = schema['properties']['task_id']['enum'][0]
                task = json.loads((namespace['run_dir'] / 'requests' / ident / 'task.json').read_text())
                sent.append(ident)
                choices = json.dumps(study.synthetic_fixture(task))
                usage = dict(input_tokens=500, output_tokens=800)
                if body['model'].startswith('gpt-'):
                    response = dict(model=body['model'], status='completed', usage=usage,
                                    output=[dict(type='message', content=[dict(type='output_text', text=choices)])])
                else:
                    response = dict(model=body['model'], stop_reason='end_turn', usage=usage,
                                    content=[dict(type='text', text=choices)])
                return httpx.Response(200, json=response)
            original_runner = api.Runner
            def offline_runner(*args, **kwargs):
                return original_runner(*args, **kwargs, transport=httpx.MockTransport(respond))
            with patch.object(api, 'Runner', side_effect=offline_runner), \
                 patch.dict('os.environ', {}, clear=True), \
                 patch('getpass.getpass', side_effect=['fake-hidden-openai', 'fake-hidden-anthropic']) as key_input, \
                 patch('IPython.display.display'), redirect_stdout(io.StringIO()):
                for index, cell in enumerate(notebook.cells):
                    if cell.cell_type != 'code':
                        continue
                    source = cell.source.replace('RUN_API = False', 'RUN_API = True').replace('PHASE = "all"', 'PHASE = "pilot"')
                    code = compile(source, f'weekly-paid-branch-{index}', 'exec', flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
                    value = eval(code, namespace)
                    if inspect.isawaitable(value):
                        await value
                    if 'EXPERIMENT = ROOT /' in source:
                        namespace.update(EXPERIMENT=experiment, BUDGET_EXPERIMENT=budget)
            self.assertEqual(len(sent), 4)
            self.assertTrue(all(name.endswith('_pilot') for name in sent))
            self.assertEqual(key_input.call_count, 2)
            self.assertNotIn('keys', namespace)
            self.assertEqual(namespace['runner'].keys, {})
            self.assertTrue((experiment / 'reports/REPORT.md').exists())
            for path in experiment.rglob('*'):
                if path.is_file():
                    self.assertNotIn(b'fake-hidden-openai', path.read_bytes())
                    self.assertNotIn(b'fake-hidden-anthropic', path.read_bytes())

    async def test_default_notebook_completes_without_keys_or_api(self):
        with tempfile.TemporaryDirectory() as temporary:
            experiment, budget = setup_experiment(temporary)
            specification = importlib.util.spec_from_file_location('weekly_builder', ROOT / 'scripts/create_weekly_pressure_notebook.py')
            builder = importlib.util.module_from_spec(specification)
            specification.loader.exec_module(builder)
            destination = Path(temporary) / 'RUN_EXPERIMENT.ipynb'
            with patch.object(builder, 'DESTINATION', destination), redirect_stdout(io.StringIO()):
                builder.main()
            notebook = nbformat.read(destination, as_version=4)
            namespace = {'__name__': '__main__'}
            with patch('httpx.AsyncClient', side_effect=AssertionError('Review must not make HTTP calls')), \
                 patch('getpass.getpass', side_effect=AssertionError('Review must not ask for keys')), \
                 patch('IPython.display.display'), redirect_stdout(io.StringIO()):
                for index, cell in enumerate(notebook.cells):
                    if cell.cell_type != 'code':
                        continue
                    code = compile(cell.source, f'weekly-notebook-{index}', 'exec', flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
                    value = eval(code, namespace)
                    if inspect.isawaitable(value):
                        await value
                    if 'EXPERIMENT = ROOT /' in cell.source:
                        namespace.update(EXPERIMENT=experiment, BUDGET_EXPERIMENT=budget)
            self.assertIs(namespace['RUN_API'], False)
            self.assertEqual(namespace['PHASE'], 'all')
            self.assertTrue((experiment / 'reports/REPORT.md').exists())
            self.assertFalse((namespace['run_dir'] / 'api_status.json').exists())
            self.assertEqual(list((namespace['run_dir'] / 'accepted').glob('*.json')), [])


if __name__ == '__main__':
    unittest.main()
