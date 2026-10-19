"""Independently reconcile a saved deadline run and its exports, without model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study.deadline_cohort import audit,read,load_accepted,accepted_path,progress
from beergame_study.deadline_cohort_report import build_report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args();run=args.run.resolve();root=run.parents[2]
    before={p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}
    m=audit(run);plan=read(run/'plan.json')
    from beergame_study.hypothesis_alignment import STUDY, build_report as aligned_report, source_folder
    result=aligned_report(run) if run.name==STUDY and (root/'reports/CURRENT_BEER_GAME/results/provenance.json').exists() else build_report(run)
    rounds=result['rounds'];tables=result.get('legacy_tables',result['tables'])
    workbook=result.get('workbook',result['folder']/'RESULTS.xlsx')
    specs={c['chain_id']:c for c in plan['chains']};direct=[];orders=0;probe_pairs=0;normalizations=0
    for task in plan['tasks']:
        if not accepted_path(run,task['task_id']).exists():continue
        entry=load_accepted(run,task['task_id']);normalizations+=bool(entry['formatting_edits'])
        for c in entry['payload']['chains']:
            q=np.asarray(c['orders']);p=np.asarray(c['probes']);orders+=q.size;probe_pairs+=len(p)
            demand=np.asarray(specs[c['chain_id']]['customer_demand'][4:]);denominator=float(np.var(demand,ddof=1))
            f=rounds[(rounds.task_id==task['task_id']) & (rounds.chain_id==c['chain_id'])]
            expected=.5*f.inventory+f.backlog
            np.testing.assert_array_equal(f.cost,expected)
            direct.append(dict(generation=task['generation'],condition=task['condition'],chain_id=c['chain_id'],
                sensitivity=float(np.mean((p[:,0]-p[:,1])/24)),cost=float(expected.sum()),
                bullwhip=float(np.mean(np.var(q,axis=0,ddof=1)/denominator)) if denominator>0 else np.nan))
    direct=pd.DataFrame(direct)
    if not direct.empty:
        assert len(rounds)==len(direct)*4*(m['config']['weeks']+12)
        actual=tables['hypotheses'].set_index('hypothesis') if not tables['hypotheses'].empty else None
        for hypothesis,metric in [('H1','sensitivity'),('H2','cost'),('H3','bullwhip')]:
            pivot=direct.pivot(index=['generation','chain_id'],columns='condition',values=metric)
            if set(pivot.columns)!={'brief','ample'}:continue
            pivot=pivot.dropna();difference=pivot.brief-pivot.ample
            if actual is not None:
                row=actual.loc[hypothesis]
                np.testing.assert_allclose(row.brief,pivot.brief.mean(),equal_nan=True,rtol=1e-12)
                np.testing.assert_allclose(row.ample,pivot.ample.mean(),equal_nan=True,rtol=1e-12)
                np.testing.assert_allclose(row.brief_minus_ample,difference.mean(),equal_nan=True,rtol=1e-12)
                assert int(row.defined_chain_generation_pairs)==len(difference)
            contrast=tables['contrasts'].set_index(['generation','chain_id']).loc[pivot.index,metric+'_difference']
            np.testing.assert_allclose(contrast,difference,rtol=1e-12)
        assert tables['hypotheses'][['p_value','ci_lower','ci_upper']].isna().all().all() if not tables['hypotheses'].empty else True
        for name,expected in tables.items():
            if name=='hypotheses' and 'legacy_tables' in result:
                expected=result['tables']['hypotheses']
            # Generation labels in this sheet are strings ("1", "2", "1-2").
            # A partial study containing only "1" otherwise gets inferred as int.
            exported=pd.read_excel(workbook,sheet_name=name,
                dtype={'generation':str} if name=='choice_changes' else None)
            if expected.empty:
                assert exported.empty;continue
            expected=expected.copy()
            for column in expected:
                if expected[column].isna().all():expected[column]=np.nan
            pd.testing.assert_frame_equal(exported,expected,check_dtype=False,atol=1e-10,rtol=1e-10)
        assert len(pd.read_excel(workbook,sheet_name='rounds'))==len(rounds)
        assert len(pd.read_excel(workbook,sheet_name='probes'))==probe_pairs
    for name in result['images']:
        assert (result['folder']/(name+'.png')).read_bytes().startswith(b'\x89PNG')
        assert (result['folder']/(name+'.pdf')).read_bytes().startswith(b'%PDF')
    after={p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in run.rglob('*') if p.is_file()}
    assert before==after;audit(run)
    record=dict(status='passed',run=str(run),complete=result['complete'],accepted_responses=int(progress(run).accepted.sum()),
        fictional_identities=plan['fictional_identities'],generation_trajectories=len(direct)*4,
        weekly_orders=orders,probe_pairs=probe_pairs,replayed_role_states=len(rounds),raw_files_unchanged=len(before),
        normalized_responses=normalizations,figures=len(result['images']),workbook_sheets=10 if not rounds.empty else 0,
        direct_sensitivity_and_supplementary_bullwhip='passed',holding_backlog_cost_identity='passed',p_values_withheld=True,api_calls=0,report=str(result['report']))
    if 'legacy_tables' in result:
        record.update(hypotheses=4,education_effects_missing=True,source_report=str(source_folder(root)/'REPORT.md'),hypothesis_framework='user-H1-H4-post-collection-v1')
    path=root/'reports/software_checks'/(run.name+'_audit.json');path.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record,indent=2))
    if not tables['hypotheses'].empty:
        print(result['tables']['hypotheses'].to_string(index=False));print(tables['choice_changes'].to_string(index=False))

if __name__=='__main__':main()
