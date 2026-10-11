"""Audit correction of hypothetical shipment fields; retain the original calibration.

No change to game prompts, orders, thresholds or simulator. Exactly 12 decisions
are rechecked (4 affected states x 3 caps), with an additional $0.03 cap.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from budget_model_screen import ROOT, BudgetGateway, save
from budget_followup_study import decision
from run_budget_followup import CAMPAIGN

DIRECTORY=ROOT/'data/development/calibration_metadata_recheck_20261005'

async def run(client):
    if (DIRECTORY/'result.json').exists():
        return json.loads((DIRECTORY/'result.json').read_text())
    campaign=json.loads(CAMPAIGN.read_text());original=Path(campaign['calibration_dir'])
    old=pd.read_csv(original/'calibration.csv');choice=campaign['selected']
    original_cases={}
    for path in (original/'requests').glob('*.json'):
        record=json.loads(path.read_text());identity=record['identity']
        if identity.get('stage')=='plan' and identity.get('calibration')=='short':
            payload=json.loads(record['messages'][1]['content'])
            original_cases[identity['item']]=dict(state=payload['current_state'],history=payload['past_rounds'])
    affected=[]
    for i,c in sorted(original_cases.items()):
        s=c['state']
        if s['inventory']>0 and s['demand']>0 and s['shipped']==0:
            s['shipped']=s['demand'];affected.append((i,c))
    assert len(affected)==4
    DIRECTORY.mkdir(parents=True,exist_ok=True)
    manifest=dict(reason='Four hypothetical positive-stock/no-backlog states had shipped=0 despite positive processed demand. Correct shipped to that demand; all other fields unchanged.',
        original_calibration=str(original),selection=choice,affected_items=[i for i,c in affected],
        max_additional_cost_usd=.03,decision_count=12,
        interpretation='Post hoc input-metadata sensitivity check. Original calibration and game data remain unchanged. No selection on hypotheses.')
    save(DIRECTORY/'manifest.json',manifest)
    gateway=BudgetGateway(client,DIRECTORY,.03,interval_s=.5);rows=[]
    def refresh():save(DIRECTORY/'progress.json',dict(phase='running',requests_done=gateway.finished,
        remaining_requests=24-gateway.finished,estimated_cost_usd=gateway.charged,allowance_usd=.03))
    gateway.callback=refresh
    for screen,cap in [('short',32),('adequate',240),('benchmark',480)]:
        for i,c in affected:
            r=await decision(gateway,choice['model'],choice['prompt'],c['state'],[],cap,
                dict(calibration_metadata_recheck=screen,item=i,role=c['state']['role']))
            rows.append(dict(screen=screen,item=i,role=c['state']['role'],**r))
            pd.DataFrame(rows).to_csv(DIRECTORY/'rechecked_decisions.csv',index=False)
    replacement=pd.DataFrame(rows)
    merged=pd.concat([old[~old.item.isin([i for i,c in affected])],replacement],ignore_index=True)
    merged.to_csv(DIRECTORY/'calibration_with_corrected_metadata.csv',index=False)
    summary=merged.groupby('screen').agg(mean_tokens=('plan_tokens','mean'),
        truncated_fraction=('plan_truncated','mean'),mean_order=('order','mean'))
    pivot=merged.pivot(index='item',columns='screen',values='order')
    difference=float(np.median(abs(pivot.adequate-pivot.benchmark)))
    passed=bool(summary.loc['short','truncated_fraction']>=.2 and summary.loc['adequate','truncated_fraction']<=.05
        and summary.loc['adequate','mean_tokens']>summary.loc['short','mean_tokens'] and difference<=4)
    summary.to_csv(DIRECTORY/'summary.csv')
    save(DIRECTORY/'result.json',dict(passed=passed,median_absolute_adequate_benchmark_difference=difference,
        additional_cost_usd=gateway.charged,original_preserved=True))
    save(DIRECTORY/'progress.json',dict(phase='complete',requests_done=gateway.finished,remaining_requests=0,
        estimated_cost_usd=gateway.charged,allowance_usd=.03))
    return dict(passed=passed,additional_cost_usd=gateway.charged)
