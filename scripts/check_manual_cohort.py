"""Offline 500-identity replay, figure export, notebook cells and paste callbacks."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

import nbformat

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from beergame_study.manual_cohort import (CohortConfig,prepare,read,synthetic_response,import_response,
                                        progress,replay,audit)
from beergame_study.manual_cohort_report import build_report


def forbidden(*args,**kwargs):
    raise AssertionError('API construction is forbidden in this software check.')


def main():
    checks=ROOT/'reports/software_checks'
    checks.mkdir(exist_ok=True)
    log=io.StringIO()
    old_hashes={}
    for run_id in ('claude_api_fd5533fef5828d96','economy_api_a80275c58f2c07e0'):
        folder=ROOT/'data/runs'/run_id
        old_hashes.update({str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in folder.rglob('*') if p.is_file()})
    with patch('openai.OpenAI',side_effect=forbidden),patch('openai.AsyncOpenAI',side_effect=forbidden),\
         patch('anthropic.Anthropic',side_effect=forbidden),patch('anthropic.AsyncAnthropic',side_effect=forbidden):
        run=prepare(CohortConfig(students=500,batch_students=100,study_label='software-only-500-check',synthetic=True))
        plan=read(run/'plan.json')
        for stage in ('initial','revision'):
            for b in plan['batches']:
                path=run/'accepted'/f"{b['batch_id']}_{stage}.json"
                if path.exists():continue
                obj=json.loads(synthetic_response(run,b['batch_id'],stage))
                if stage=='revision':
                    for chain in obj['chains']:
                        chain['orders']=[[q+(i%2) for q in row] for i,row in enumerate(chain['orders'])]
                        chain['probes']=[[8,3]]*4
                import_response(run,b['batch_id'],stage,json.dumps(obj),model_label='GPT-6 Astra',
                                effort_label='high',session_label=f"synthetic-{b['batch_id']}-{stage}",
                                evidence_kind='synthetic_test',confirm_full_prompt=True)
        result=build_report(run)
        assert result['complete'] and len(result['rounds'])==36000
        assert len(result['rounds'][result['rounds'].phase=='model'])==20000
        assert len(result['tables']['contrasts'])==125
        assert result['tables']['hypotheses'].p_value.isna().all()
        assert len(result['images'])==6
        for name in result['images']:
            for ext in ('png','pdf'):assert (result['folder']/f'{name}.{ext}').stat().st_size>1000
        nb=nbformat.read(ROOT/'notebooks/06_manual_cohort_simulation.ipynb',as_version=4)
        nbformat.validate(nb)
        ns={'__name__':'__notebook_software_check__'}
        cells=[c.source for c in nb.cells if c.cell_type=='code']
        with tempfile.TemporaryDirectory() as temporary,redirect_stdout(log),patch('IPython.display.display'):
            for index,source in enumerate(cells):
                if index==1:
                    source = '\n'.join('EXISTING_RUN = None' if line.startswith('EXISTING_RUN =') else line for line in source.splitlines())
                    # Keep test data out of the operator's real plan. No on-disk notebook edit.
                    real_prepare=prepare
                    def test_prepare(config):
                        config=CohortConfig(students=4,batch_students=4,synthetic=True,study_label='notebook-control')
                        return real_prepare(config,root=Path(temporary))
                    ns['prepare']=test_prepare
                    real_import=import_response
                    def test_import(*args,**kwargs):
                        kwargs['evidence_kind']='synthetic_test'
                        return real_import(*args,**kwargs)
                    ns['import_response']=test_import
                exec(compile(source,f'notebook06-cell-{index}','exec'),ns)
            for stage in ('initial','revision'):
                # Recreate next-prompt and paste form cells, then exercise the actual button callback.
                exec(cells[3],ns);exec(cells[4],ns)
                assert ns['captured_task']['stage']==stage
                ns['response_box'].value=synthetic_response(ns['RUN'],'b0001',stage)
                ns['session_box'].value=f'notebook-software-{stage}'
                ns['confirm_box'].value=True
                ns['save_button'].click()
                assert bool(progress(ns['RUN'])[stage].all()),log.getvalue()
                assert ns['save_button'].disabled
            exec(cells[6],ns);exec(cells[7],ns)
            assert ns['RESULT']['complete']
        unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in old_hashes.items())
        assert unchanged
    payload=dict(status='passed',api_calls=0,synthetic_run=str(run),software_report=str(result['report']),
                 fictional_identities=500,chain_pairs=125,physical_role_states=36000,weekly_orders=20000,
                 figures=6,png_and_pdf=True,notebook_code_cells=len(cells),paste_callbacks=2,
                 previous_api_raw_files_unchanged=len(old_hashes),hypothesis_inference='withheld as designed')
    (checks/'manual_cohort_20261017.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    (checks/'manual_cohort_notebook_20261017.log').write_text(log.getvalue(),encoding='utf-8')
    print(json.dumps(payload,indent=2))


if __name__=='__main__':main()
