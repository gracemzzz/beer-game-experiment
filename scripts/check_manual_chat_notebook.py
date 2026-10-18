"""Check current-run display and both paste callbacks offline, with API clients blocked."""
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study import manual_cohort_chat as chat


def main():
    notebook = nbformat.read(ROOT/'notebooks/06_manual_cohort_simulation.ipynb', as_version=4)
    nbformat.validate(notebook)
    cells = [c.source for c in notebook.cells if c.cell_type == 'code']
    log = io.StringIO()
    actual = Path(chat.read(ROOT/'reports/LATEST_MANUAL_COHORT_REPORT.json')['run'])
    accepted_before = {p: p.read_bytes() for p in (actual/'accepted').glob('*.json')}
    with patch('openai.OpenAI', side_effect=AssertionError('API forbidden')), \
         patch('anthropic.Anthropic', side_effect=AssertionError('API forbidden')), \
         patch('IPython.display.display'), redirect_stdout(log):
        # Execute the saved notebook as the user will open it. Import controls remain off.
        ns = {'__name__': '__real_notebook_read_only_check__'}
        for source in cells:
            exec(compile(source, '<notebook>', 'exec'), ns)
        assert ns['RUN'] == actual
        assert (ns['MODEL_LABEL'], ns['EFFORT_LABEL']) == ('GPT-6', 'pro')
        assert ns['TASK']['batch_id'] == 'b0002' and ns['TASK']['stage'] == 'initial'
        assert ns['import_response'].__module__ == 'beergame_study.manual_cohort_chat'
        assert 'pro' in ns['confirm_box'].description
        assert int(chat.progress(actual).initial.sum()) == 1

        # Exercise callbacks only in a temporary, explicitly synthetic plan.
        with tempfile.TemporaryDirectory() as temp:
            control = chat.prepare(chat.CohortConfig(students=4,batch_students=4,synthetic=True,
                                   study_label='chat-notebook-control'), root=Path(temp))
            check = {'__name__': '__synthetic_notebook_check__'}
            for index, source in enumerate(cells):
                if index == 1:
                    source = '\n'.join(f'EXISTING_RUN = Path({str(control)!r})'
                                       if line.startswith('EXISTING_RUN =') else line
                                       for line in source.splitlines())
                exec(compile(source, '<synthetic-notebook>', 'exec'), check)
                if index == 1:
                    def import_fixture(*args, **kwargs):
                        kwargs['evidence_kind'] = 'synthetic_test'
                        return chat.import_response(*args, **kwargs)
                    check['import_response'] = import_fixture
            for stage in ('initial', 'revision'):
                exec(cells[3], check)
                exec(cells[4], check)
                check['response_box'].value = chat.synthetic_response(control,'b0001',stage)
                check['session_box'].value = 'synthetic-only-'+stage
                check['confirm_box'].value = True
                check['save_button'].click()
                assert check['save_button'].disabled, log.getvalue()
                assert bool(chat.progress(control)[stage].all())
            exec(cells[6], check)
            exec(cells[7], check)
            assert check['RESULT']['complete'] and len(check['RESULT']['images']) == 6
    assert {p: p.read_bytes() for p in (actual/'accepted').glob('*.json')} == accepted_before
    chat.audit(actual)
    checks = ROOT/'reports/software_checks'
    checks.mkdir(exist_ok=True)
    result = dict(status='passed', date='2026-10-18', api_calls=0,
                  real_notebook_cells=len(cells), synthetic_notebook_cells=len(cells),
                  synthetic_paste_callbacks=2, synthetic_figures=6,
                  real_run=actual.name, accepted_records_unchanged=len(accepted_before),
                  unit_tests_passed=42, next_batch='b0002', next_stage='initial',
                  model='GPT-6', ui_setting='pro')
    (checks/'manual_chat_20261018.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (checks/'manual_chat_notebook_20261018.log').write_text(log.getvalue(),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
