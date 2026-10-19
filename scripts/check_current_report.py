"""Verify current H1-H4 publication, missing contrasts and preserved archives."""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study.deadline_cohort import audit, load_accepted, read
from beergame_study.hypothesis_alignment import STUDY, HYPOTHESES, FIGURES, build_report


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    folder=ROOT/'reports/CURRENT_BEER_GAME'
    run=ROOT/'data/runs'/STUDY
    audit(run)
    result=build_report(run)
    assessment=pd.read_csv(folder/'results/hypotheses.csv')
    assert assessment.hypothesis.tolist()==list(HYPOTHESES)
    assert assessment.statement.tolist()==list(HYPOTHESES.values())
    absent=assessment[assessment.hypothesis.isin(['H3','H4'])]
    assert absent[['brief_mean','ample_mean','available_proxy_difference']].isna().all().all()
    assert absent.assessment.str.startswith('Not tested:').all()
    pd.testing.assert_frame_equal(pd.read_excel(folder/'results/RESULTS.xlsx',sheet_name='hypotheses'),assessment,check_dtype=False,atol=1e-12)
    direct=[]
    for task in read(run/'plan.json')['tasks']:
        entry=load_accepted(run,task['task_id'])
        for chain in entry['payload']['chains']:
            p=np.array(chain['probes'])
            direct.append(dict(condition=task['condition'],sensitivity=np.mean((p[:,0]-p[:,1])/24)))
    direct=pd.DataFrame(direct).groupby('condition').sensitivity.mean()
    np.testing.assert_allclose(assessment.iloc[0].brief_mean,direct.brief)
    np.testing.assert_allclose(assessment.iloc[0].ample_mean,direct.ample)
    rounds=result['rounds'];cost=rounds.assign(rebuilt_cost=.5*rounds.inventory+rounds.backlog)
    np.testing.assert_array_equal(cost.rebuilt_cost,rounds.cost)
    means=cost.groupby(['condition','generation','chain_id']).rebuilt_cost.sum().groupby('condition').mean()
    np.testing.assert_allclose(assessment.iloc[1].brief_mean,means.brief)
    np.testing.assert_allclose(assessment.iloc[1].ample_mean,means.ample)
    before=read(ROOT/'reports/software_checks/hypothesis_alignment_before_20261018.json')
    for name,h in before['run_files'].items():assert sha(run/name)==h
    archive=ROOT/before['archive']
    for name,h in before['old_final_files'].items():assert sha(archive/name)==h
    assert sha(archive/'Beer_Game_Deadline_20261018.zip')==before['old_zip_sha256']
    moves=read(ROOT/'reports/software_checks/report_archive_moves_20261018.json')['moves']
    archived_files=0
    for move in moves:
        for name,h in move['files_sha256'].items():
            assert sha(ROOT/move['archived']/name)==h,(move['archived'],name)
            archived_files+=1
    links=0
    for p in [ROOT/'README.md',ROOT/'reports/README.md',ROOT/'reports/archive/README.md',ROOT/'docs/HYPOTHESES_H1_H4.md',folder/'README.md',folder/'REPORT.md',folder/'results/README.md']:
        text=re.sub(r'```.*?```','',p.read_text(encoding='utf-8'),flags=re.S)
        for link in re.findall(r'\]\(([^)]+)\)',text):
            destination=(p.parent/link).resolve()
            assert destination.exists() or destination==ROOT/'reports/software_checks/hypothesis_alignment_20261018.json',(p,link)
            links+=1
    for name,_,_ in FIGURES:
        assert (folder/'plots'/(name+'.png')).read_bytes().startswith(b'\x89PNG')
        assert (folder/'plots'/(name+'.pdf')).read_bytes().startswith(b'%PDF')
    with zipfile.ZipFile(folder/'Beer_Game_H1_H4.zip') as z:
        assert z.testzip() is None
        for name in z.namelist():
            relative=name.split('/',1)[1]
            assert hashlib.sha256(z.read(name)).hexdigest()==sha(folder/relative)
    pointer=read(ROOT/'reports/LATEST_DEADLINE_COHORT_REPORT.json')
    assert Path(pointer['report'])==folder/'REPORT.md'
    notebook=read(ROOT/'reports/software_checks'/f'{STUDY}_notebook.json')
    assert notebook['status']=='passed' and notebook['hypotheses']==4 and notebook['code_cells']==8
    audit_record=read(ROOT/'reports/software_checks'/f'{STUDY}_audit.json')
    assert audit_record['status']=='passed' and audit_record['hypotheses']==4
    status=dict(status='passed',current_report=str(folder/'REPORT.md'),hypotheses=4,
        h3_h4_effect_estimates='missing, not zero',direct_raw_sensitivity='passed',cost_identity='passed',
        raw_files_unchanged=len(before['run_files']),archived_study_folders=len(moves),
        archived_files_unchanged=archived_files,superseded_package_preserved=True,
        navigation_links_checked=links,figure_pairs=len(FIGURES),notebook_code_cells=8,
        original_prompt_and_order_checks='20 exact prompts and 40000 orders verified at publication',
        no_new_experiment=True,api_calls=0)
    path=ROOT/'reports/software_checks/hypothesis_alignment_20261018.json'
    path.write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))


if __name__=='__main__':main()
