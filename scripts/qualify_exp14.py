"""Freeze latency-only deadline calibration and feasibility gates; no outcome tuning."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json
import math
import random
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from beergame_study.exp14_deadline import audit_result,source_hashes,digest
from prepare_exp14 import development_plan,freeze,material_hashes,analysis_hashes,EXP


def valid_review(folder,result,case):
    path=folder/'ADHERENCE_REVIEW.json'
    if not path.exists():return False
    r=json.loads(path.read_text(encoding='utf-8'))
    return r.get('result_sha256')==hashlib.sha256((folder/'RESULT.json').read_bytes()).hexdigest() and r.get('case_sha256')==digest(case) and all(r.get(k) is True for k in ['passed','full_public_context_reviewed','fresh_context_confirmed','literal_model_choices_confirmed','fixed_requested_settings_confirmed'])


def calibrate(version):
    plan=development_plan();values={'game':[],'probes':[]};evidence=[]
    for block in plan['latency_blocks']:
        folder=EXP/'data/latency'/f'{version.lower()}_{block}_a'
        case=json.loads((folder/'CASE.json').read_text(encoding='utf-8'))
        result=json.loads((folder/'RESULT.json').read_text(encoding='utf-8'))
        if not result['complete'] or not valid_review(folder,result,case):raise ValueError('Reference case incomplete or unreviewed')
        audit_result(result,case)
        for d in result['decisions']:
            if d['phase'] in values:values[d['phase']].append(d['elapsed_seconds'])
        evidence.append(dict(folder=str(folder.relative_to(EXP)),result_sha256=hashlib.sha256((folder/'RESULT.json').read_bytes()).hexdigest()))
    deadlines={'A':{},'restricted':{}};checks={}
    for phase,times in values.items():
        short=math.ceil(float(np.quantile(times,.75,method='linear'))*10)/10
        long=math.ceil(max(30,max(times)*3)*10)/10
        deadlines['A'][phase]=long;deadlines['restricted'][phase]=short
        checks[phase]=dict(n=len(times),median_seconds=float(np.median(times)),max_seconds=max(times),
                           fraction_reference_over_restricted=sum(t>short for t in times)/len(times),
                           restricted_to_adequate_ratio=short/long)
    order={}
    for block in plan['feasibility_blocks']:
        arms=list('ABC');random.Random('exp14-feasibility-'+version+block).shuffle(arms);order[block]=arms
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),prompt_version=version,
                 rule=plan['deadline_rule'],deadlines=deadlines,reference_checks=checks,evidence=evidence,
                 hypothesis_outcomes_used_for_calibration=False,feasibility_launch_order=order,
                 source_hashes=source_hashes(),material_hashes=material_hashes())
    path=EXP/f'hypotheses/CALIBRATION_{version}.json';freeze(path,receipt)
    print(json.dumps(receipt,indent=2));return receipt


def gate(version,freeze_main=False):
    calibration=json.loads((EXP/f'hypotheses/CALIBRATION_{version}.json').read_text(encoding='utf-8'))
    plan=development_plan();checks=[]
    for block in plan['feasibility_blocks']:
        for arm in 'ABC':
            folder=EXP/'data/feasibility'/f'{version.lower()}_{block}_{arm.lower()}'
            passed=False;reason='not collected';score=None
            if (folder/'RESULT.json').exists():
                result=json.loads((folder/'RESULT.json').read_text(encoding='utf-8'));case=json.loads((folder/'CASE.json').read_text(encoding='utf-8'))
                audit_result(result,case)
                passed=result['complete'] and valid_review(folder,result,case)
                reason='complete/reviewed' if passed else result.get('terminal_reason') or 'incomplete/unreviewed'
                answers=result.get('comprehension_answers')
                score=(sum(answers.get(k)==v['correct_answer'] for k,v in case['comprehension_scoring'].items())/len(case['comprehension_scoring'])) if answers is not None else None
                if passed and arm=='C' and (score is None or score<.75):passed=False;reason='education comprehension missing or below prospective threshold'
            checks.append(dict(block=block,arm=arm,passed=passed,reason=reason,comprehension_score=score))
    timing_ok=all(v['fraction_reference_over_restricted']>=.20 and v['restricted_to_adequate_ratio']<1
                  for v in calibration['reference_checks'].values())
    passed=all(c['passed'] for c in checks) and timing_ok
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),prompt_version=version,qualification_passed=passed,
                 timing_reference_check_passed=timing_ok,checks=checks,selection_uses_hypothesis_signs_or_p_values=False)
    # Gate records are snapshots; retain every earlier attempt rather than overwrite.
    key=digest(receipt)[:16];freeze(EXP/f'analysis/qualification/{version}_{key}.json',receipt)
    if freeze_main:
        if not passed:raise ValueError('Main remains blocked: feasibility/deadline/knowledge gate did not pass')
        if version=='V2':
            prior=list((EXP/'analysis/qualification').glob('V1_*.json'))
            if not prior or any(json.loads(p.read_text(encoding='utf-8'))['qualification_passed'] for p in prior):
                raise ValueError('V1-first prospective selection order must be respected')
        orders={}
        for block in plan['main_blocks']:
            arms=list('ABC');random.Random('exp14-main-'+block).shuffle(arms);orders[block]=arms
        main=dict(created_utc=datetime.now(timezone.utc).isoformat(),frozen=True,qualification_passed=True,
                  prompt_version=version,independent_blocks_confirmed=True,
                  block_ids=plan['main_blocks'],chain_contexts_per_arm=10,weeks=24,
                  source_hashes=source_hashes(),material_hashes=material_hashes(),
                  analysis_hashes=analysis_hashes(),
                  deadlines=calibration['deadlines'],launch_orders=orders,qualification_receipt=key,
                  stage='held-out main; no development reuse',stopping='All ten assigned blocks; no replacement/extension based on outcomes',
                  tests=5,multiplicity='Holm5',api_requests=0)
        freeze(EXP/'hypotheses/MAIN_PLAN.json',main)
    print(json.dumps(receipt,indent=2));return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['calibrate','gate']);p.add_argument('--version',choices=['V1','V2'],required=True)
    p.add_argument('--freeze-main',action='store_true');args=p.parse_args()
    calibrate(args.version) if args.action=='calibrate' else gate(args.version,args.freeze_main)
