"""Run notebook 07 against a selected existing run, forbidding API clients."""
import argparse
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch
import nbformat

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from beergame_study.deadline_cohort import audit,read

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args();run=args.run.resolve();os.chdir(ROOT)
    before={p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}
    nb=nbformat.read(ROOT/'notebooks/07_deadline_cohort_rerun.ipynb',as_version=4);nbformat.validate(nb)
    cells=[c.source for c in nb.cells if c.cell_type=='code'];assert len(cells)==8
    ns={'__name__':'__deadline_notebook_check__'};log=io.StringIO()
    with patch('openai.OpenAI',side_effect=AssertionError('API forbidden')),patch('anthropic.Anthropic',side_effect=AssertionError('API forbidden')),patch('IPython.display.display'),redirect_stdout(log):
        for i,source in enumerate(cells):
            exec(compile(source,f'notebook07-cell-{i}','exec'),ns)
            if i==1:
                ns['RUN']=run;ns['MANIFEST']=audit(run);ns['PLAN']=read(run/'plan.json')
                cfg=ns['MANIFEST']['config'];ns['MODEL_LABEL']=cfg['model_label'];ns['EFFORT_LABEL']=cfg['effort_label']
    assert ns['RUN']==run
    after={p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}
    assert before==after
    result=ns['RESULT'];audit(run)
    record=dict(status='passed',run=str(run),code_cells=8,raw_files_unchanged=len(before),api_calls=0,
        complete=result['complete'],figures=len(result['images']),hypotheses=len(result['tables']['hypotheses']),
        report=str(result['report']),interactive_chains=len(ns['chain_selector'].options) if 'chain_selector' in ns else 0)
    path=ROOT/'reports/software_checks'/(run.name+'_notebook.json')
    path.write_text(json.dumps(record,indent=2),encoding='utf-8')
    logs=ROOT/'reports/logs/deadline_rerun_20261018';logs.mkdir(parents=True,exist_ok=True)
    (logs/(run.name+'_notebook.log')).write_text(log.getvalue(),encoding='utf-8')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
