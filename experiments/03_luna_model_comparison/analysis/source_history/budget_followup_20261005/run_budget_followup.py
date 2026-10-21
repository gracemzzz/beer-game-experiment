"""One budgeted follow-up campaign. Completed phases are read, never repurchased."""
import json
from pathlib import Path
from budget_model_screen import ROOT, DIRECTORY, MODELS, BudgetStop, save
import budget_followup_study as study

CAMPAIGN=ROOT/'data/development/budget_campaign_20261005.json'

def freeze():
    if CAMPAIGN.exists():return json.loads(CAMPAIGN.read_text())
    p=json.loads((DIRECTORY/'progress.json').read_text())
    if p['phase']!='complete':raise BudgetStop('Wait for the complete fixed model screen.')
    result=json.loads((DIRECTORY/'selection.json').read_text());selected=result['selected']
    if not selected:raise BudgetStop('No eligible candidate; preserve budget and review the screen.')
    cheap=MODELS[selected['model']]['input']<=.25
    allocation=dict(selected=selected,groups_per_condition=2 if cheap else 1,
        screen=str(DIRECTORY),screen_limit_usd=.45,calibration_limit_usd=.12 if cheap else .30,
        short_tokens=study.SHORT_TOKENS,adequate_tokens=study.ADEQUATE_TOKENS,
        game_limit_usd=.90 if cheap else 1.60,new_campaign_ceiling_usd=2.40,
        known_prior_current_study_cost_usd=.37203635,
        purpose='New feasibility pilot; group count fixed before calibration and game outcomes.',
        selection_rule='Feasibility and price only; no H1/H2 directional or significance selection.',
        budget_interpretation='Conservative: $3 includes the four current-study runs; historical experiments/account balance not verified.',
        status='prepared')
    allocation['maximum_phase_limits_sum_usd']=sum(allocation[k] for k in ('screen_limit_usd','calibration_limit_usd','game_limit_usd'))
    assert allocation['maximum_phase_limits_sum_usd']<=allocation['new_campaign_ceiling_usd']
    save(CAMPAIGN,allocation);return allocation

def complete(path):
    p=Path(path)/'progress.json'
    return p.exists() and json.loads(p.read_text())['phase']=='complete'

async def run(client):
    campaign=freeze();selected=campaign['selected']
    if campaign['status']=='complete':return campaign
    if 'calibration_dir' not in campaign:
        d,_=study.prepare('calibration',selected,1,campaign['calibration_limit_usd'])
        campaign['calibration_dir']=str(d);save(CAMPAIGN,campaign)
    d=Path(campaign['calibration_dir'])
    if not complete(d):
        campaign['status']='calibrating';save(CAMPAIGN,campaign)
        await study.calibrate(client,selected,campaign['calibration_limit_usd'])
    rec=json.loads((d/'calibration_recommendation.json').read_text())
    if not rec['manipulation_screen_passed']:
        campaign.update(status='calibration_failed',conclusion='No games purchased. Do not retune for H1/H2 significance.')
        save(CAMPAIGN,campaign);return campaign
    if 'game_dir' not in campaign:
        g,_=study.prepare('game',selected,campaign['groups_per_condition'],campaign['game_limit_usd'])
        campaign['game_dir']=str(g);save(CAMPAIGN,campaign)
    g=Path(campaign['game_dir'])
    if not complete(g):
        campaign['status']='running_games';save(CAMPAIGN,campaign)
        await study.play(client,selected,d,campaign['groups_per_condition'],campaign['game_limit_usd'])
    campaign['status']='complete';save(CAMPAIGN,campaign);return campaign

def totals():
    campaign=json.loads(CAMPAIGN.read_text()) if CAMPAIGN.exists() else {}
    rows=[]
    for label,path,key in [('Model screen',str(DIRECTORY),'estimated_charged_or_reserved_usd'),
            ('Calibration',campaign.get('calibration_dir'),'estimated_cost_usd'),
            ('Games',campaign.get('game_dir'),'estimated_cost_usd'),
            ('Calibration metadata recheck',str(ROOT/'data/development/calibration_metadata_recheck_20261005'),'estimated_cost_usd')]:
        if path and (Path(path)/'progress.json').exists():
            p=json.loads((Path(path)/'progress.json').read_text())
            rows.append(dict(stage=label,cost_usd=p[key],phase=p['phase'],
                             done=p['requests_done'],left=p['remaining_requests']))
    return dict(stages=rows,new_spend_usd=sum(x['cost_usd'] for x in rows),
                known_current_study_total_usd=.37203635+sum(x['cost_usd'] for x in rows))
