"""Verify saved follow-up replies and replay every physical game state, without API calls."""
import ast
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import scipy
import sys

from run_budget_followup import ROOT, CAMPAIGN
from budget_model_screen import messages, validate_decision, sha, SCHEMA
from budget_followup_study import BeerGame, ROLES, demand_path, continuation
from beergame_study.analysis import game_tables

def audit():
    campaign=json.loads(CAMPAIGN.read_text());directory=Path(campaign['game_dir'])
    progress=json.loads((directory/'progress.json').read_text());assert progress['phase']=='complete'
    manifest=json.loads((directory/'manifest.json').read_text());config=manifest['config']
    frame=pd.read_csv(directory/'rounds.csv');tail=pd.read_csv(directory/'continuation.csv')
    candidate=pd.read_csv(directory/'all_candidate_rounds.csv')
    key=['group_id','week','role']
    pd.testing.assert_frame_equal(frame.sort_values(key).reset_index(drop=True),candidate.sort_values(key).reset_index(drop=True))
    paths=list((directory/'requests').glob('*.json'))
    records=[json.loads(p.read_text()) for p in paths]
    success=[r for r in records if r['status']=='ok']
    index={}
    for r in success:
        i=r['identity'];k=(i['group'],i['role'],i.get('week'),i['stage'])
        if i['stage']!='rules':assert k not in index
        index[k]=r
        assert not r.get('refused') and r['usage']['reasoning_tokens']==0
        assert r['usage']['output_tokens']<=r['limit']
        assert r['response']['usage']['output_tokens']==r['usage']['output_tokens']
        assert r['response']['usage']['input_tokens']==r['usage']['input_tokens']
        text=''.join(c.get('text','') for o in r['response'].get('output',[]) if o.get('type')=='message'
                     for c in o.get('content',[]) if c.get('type')=='output_text')
        assert text==r['text']
    decisions=0;states_checked=0;tail_checked=0
    for gid,g in frame.groupby('group_id'):
        game=BeerGame();history=[[] for _ in ROLES];cond=g.condition.iloc[0]
        cap=config['short_tokens'] if cond=='short' else config['adequate_tokens']
        for week,demand in enumerate(demand_path(40),1):
            states=game.observe(demand);orders=[]
            for ri,state in enumerate(states):
                row=g[(g.week==week)&(g.role==state['role'])].iloc[0]
                for name,value in state.items():
                    got=ast.literal_eval(row[name]) if name=='shared_inventory' else row[name]
                    assert got==value,(gid,week,name)
                states_checked+=1;order=int(row.order);orders.append(order)
                if week<=4:assert order==4
                else:
                    ident=dict(group=gid,role=state['role'],week=week);case=dict(state=state,history=history[ri])
                    plan=index[(gid,state['role'],week,'plan')];final=index[(gid,state['role'],week,'final')]
                    assert plan['messages']==messages(case,cap,'plan',config['prompt_variant'],identity=sha(ident))
                    assert final['messages']==messages(case,cap,'final',config['prompt_variant'],plan['text'],sha(ident))
                    assert plan['limit']==cap and final['limit']==192 and final['schema']==SCHEMA
                    answer=json.loads(final['text']);assert validate_decision(answer,state) and answer['order']==order
                    assert row.plan_tokens==plan['usage']['output_tokens'] and row.final_tokens==final['usage']['output_tokens']
                    assert bool(row.plan_truncated)==(plan['response_status']=='incomplete')
                    if row.plan_truncated:assert plan['incomplete_reason']=='max_output_tokens'
                    decisions+=1
                history[ri].append({name:(order if name=='order' else state[name]) for name in
                    ('week','demand','inventory','backlog','supply_line','order','shared_inventory')})
            game.commit(orders)
        for state in continuation(game,demand,12):
            row=tail[(tail.group_id==gid)&(tail.role==state['role'])&(tail.week==state['week'])].iloc[0]
            for name,value in state.items():
                got=ast.literal_eval(row[name]) if name=='shared_inventory' else row[name]
                assert got==value,(gid,'tail',name)
            tail_checked+=1
    for name,df in zip(('role_metrics','beta_fits','group_outcomes','hypotheses'),game_tables(frame,tail,config,True,False)):
        saved=pd.read_csv(directory/(name+'.csv'))
        for c in df:
            if pd.api.types.is_numeric_dtype(df[c]):
                assert np.allclose(df[c].to_numpy(float),saved[c].to_numpy(float),equal_nan=True),(name,c)
    assert decisions==config['groups_per_condition']*288
    assert decisions==progress['decisions']
    assert abs(sum(r['charge_usd'] for r in records)-progress['estimated_cost_usd'])<1e-9
    result=dict(game_directory=str(directory),verified_agent_decisions=decisions,
        verification_python=sys.version.split()[0],numpy_version=np.__version__,scipy_version=scipy.__version__,
        replayed_game_state_rows=states_checked,replayed_continuation_state_rows=tail_checked,
        successful_saved_responses=len(success),other_saved_attempts=len(records)-len(success),
        observed_returned_models=sorted({r['response']['model'] for r in success}),
        no_paid_audit_calls=True,evidence_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    out=ROOT/'reports/budget_followup_20261005';out.mkdir(parents=True,exist_ok=True)
    (out/'game_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='evidence_sha256'},indent=2))

if __name__=='__main__':audit()
