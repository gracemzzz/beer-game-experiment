"""Prepare one isolated exp14 chain context; no provider API calls or decisions."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from beergame_study.exp14_deadline import source_hashes, digest

EXP=ROOT/'experiments/14_deadline_student_20261026'
PUBLIC_PROBE=('probe_id','role','inventory','backlog','outstanding','pipeline_arrivals',
              'customer_demand','recent_demand_history','shared_inventory')


def freeze(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=data if isinstance(data,bytes) else (json.dumps(data,indent=2,allow_nan=False)+'\n').encode('utf-8')
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('Preserve existing prepared bytes: '+str(path))
    else:path.write_bytes(raw)


def material_hashes():
    files=sorted((EXP/'prompts').glob('*'))
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}


def analysis_hashes():
    paths=[ROOT/'src/beergame_study/exp14_analysis.py',ROOT/'src/beergame_study/pivot_inference_v2.py',
           ROOT/'scripts/report_exp14.py',EXP/'hypotheses/PROTOCOL.md']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def development_plan():
    p=EXP/'hypotheses/DEVELOPMENT_PLAN.json'
    if not p.exists():
        freeze(p,dict(created_utc=datetime.now(timezone.utc).isoformat(),model='gpt-6-astra',effort='xhigh',
            temperature='not exposed; not varied',versions=['V1','V2'],latency_blocks=['l001','l002'],
            feasibility_blocks=['f001','f002'],weeks_per_development_case=4,
            latency_case_count=4,maximum_feasibility_cases=12,maximum_total_development_contexts=16,
            main_blocks=['m%03d'%n for n in range(1,11)],main_weeks=24,
            deadline_rule={'restricted':'Per phase, 75th percentile of on-time unlimited-reference latency for that wording version.',
                           'adequate':'Per phase, max(30 seconds,3*maximum unlimited-reference latency).',
                           'quantile_method':'numpy linear percentile; round upward to nearest tenth second'},
            selection_rule='Try V1 then V2, using comprehension/full-display/literal-choice/deadline feasibility only. Select first wording with both reference cases and all six feasibility cases complete, no deadline violations, no procedure failures; C comprehension >=75%. Never select using H1-H4 signs or p-values.',
            manipulation_check='Report measured deadline ratio, on-time rates, elapsed/deadline utilization and reference exceedance fraction. Deadline is objective response admission, not verified hidden thinking restriction; if restricted reference-exceedance fraction<20% in either phase or if deadlines are not shorter, do not claim a binding treatment.',
            missingness='Preserve every failed/stopped case, never replace according to outcome. Main cannot launch before qualification and freeze. Late decisions are missing, not defaults.',
            prospective=True,api_requests=0,shared_api_ledger='experiments/12_pressure_framing_api_20261020/data/api_budget.json'))
    return json.loads(p.read_text(encoding='utf-8'))


def prepare(stage,version,block,arm,phase_limits=None):
    plan=development_plan()
    if version not in plan['versions'] or arm not in 'ABC':raise ValueError('Unknown version or arm')
    prefix={'latency':'l','feasibility':'f','main':'m'}[stage]
    if not block.startswith(prefix):raise ValueError('Stage-specific block ID required')
    allowed=plan['latency_blocks'] if stage=='latency' else plan['feasibility_blocks'] if stage=='feasibility' else plan['main_blocks']
    if block not in allowed:raise ValueError('Block not prospectively planned')
    if stage=='latency' and arm!='A':raise ValueError('Unlimited latency reference uses control only')
    if stage!='latency' and not phase_limits:raise ValueError('Numeric calibrated phase limits required')
    if stage=='main':
        p=EXP/'hypotheses/MAIN_PLAN.json'
        if not p.exists():raise ValueError('Main blocked pending calibration, feasibility and protocol freeze')
        main=json.loads(p.read_text(encoding='utf-8'))
        if main['prompt_version']!=version or not main.get('qualification_passed'):raise ValueError('Main version/gate mismatch')
        if main['source_hashes']!=source_hashes() or main['material_hashes']!=material_hashes():raise ValueError('Frozen main sources/prompts changed')
        if main.get('analysis_hashes')!=analysis_hashes():raise ValueError('Frozen main scientific analysis changed')
        if phase_limits!=main['deadlines']['A' if arm=='A' else 'restricted']:raise ValueError('Main deadlines must match frozen plan')
    ident=f'{version.lower()}_{block}_{arm.lower()}'
    folder=EXP/'data'/stage/ident
    if folder.exists():raise ValueError('Prepared case exists; resume it, never reset it')
    number=int(block[1:]);seed={'latency':1401000,'feasibility':1402000,'main':1410000}[stage]+number
    bank=json.loads((EXP/'prompts/probes.json').read_text(encoding='utf-8'))
    questions=json.loads((EXP/'prompts/comprehension.json').read_text(encoding='utf-8'))
    case=dict(case_id='E14_'+digest([stage,version,block,arm,seed])[:20],block_id=block,arm=arm,stage=stage,
              prompt_version=version,seed=seed,weeks=24 if stage=='main' else 4,deadline_seconds=None,
              phase_deadline_seconds=phase_limits or {},requested_model='gpt-6-astra',requested_effort='xhigh',
              source_hashes=source_hashes(),material_hashes=material_hashes(),
              probes=[{k:p[k] for k in PUBLIC_PROBE} for p in bank],
              assay_scoring={p['probe_id']:{k:p[k] for k in ['pair_id','assay_dimension']} for p in bank},
              comprehension=[{k:q[k] for k in ['question_id','question','choices']} for q in questions],
              comprehension_scoring={q['question_id']:{k:q[k] for k in ['correct_answer','reason']} for q in questions})
    freeze(folder/'CASE.json',case)
    lecture='EDUCATION.md' if arm=='C' else 'CONTROL.md'
    prompt=(EXP/f'prompts/STUDENT_{version}.md').read_text(encoding='utf-8')+'\n\n'+(EXP/'prompts'/lecture).read_text(encoding='utf-8')
    freeze(folder/'EXACT_PROMPT.md',prompt.encode('utf-8'))
    python=ROOT/'.venv/Scripts/python.exe';transport=ROOT/'scripts/run_exp14_agent.py'
    task=f'''You are an isolated experimental decision-maker, not a project maintainer. Requested model is gpt-6-astra and effort xhigh. Read EXACT_PROMPT.md in this folder and follow it. This is one chain/four fictional student roles, not ten chains in one context. Do not inspect any other files, source, CASE, private state, scoring keys, protocols, other runs or reports. No API calls, extra agents, order policy code, loops generating decisions, or outcome analysis.

Run folder: {folder}
Python: {python}
Transport: {transport}

First read EXACT_PROMPT.md completely. For each opportunity use a separate tool call:
& '{python}' -X utf8 '{transport}' show --run '{folder}'

Read the COMPLETE returned display, including the actual deadline clock and immutable decision_id. Set max_output_tokens at least10000, without output filters. Decide the literal values yourself. For game, stdin is a JSON list of four nonnegative integer orders; for probes, a JSON dictionary of the four displayed probe_id values to integer orders; for comprehension, a dictionary of question_id values to letters. Submit using the actual current ID and your literal JSON, not the placeholders:
@'
YOUR_LITERAL_JSON
'@ | & '{python}' -X utf8 '{transport}' submit --run '{folder}' --decision-id 'CURRENT_DECISION_ID'

Submit returns acknowledgement only. After accepted:true, call show again for the next opportunity. There are no revisions. Choose only after its current full display; never precompute orders. Do not combine show and submit in one tool interaction, generate dictionaries with code, or bulk-submit future decisions. A repeated show never resets the timer. Deadline measures transport-inclusive wall time. Deliver the decision within the window; no explanatory prose or progress narration is needed while a decision is open.

If rejected, stopped, incomplete display or tool error occurs, STOP and report it honestly. No repairs, fallback or restarting. Otherwise continue through all gameweeks, all eight probe pages, then the untimed comprehension, until complete. Preserve all zero and constant choices you consider appropriate. Do not produce reasoning traces, p-values or treatment comparisons. Return RESULT.json path and observed deviations; it is a local execution record, not an authentic full transcript. Never fabricate a transcript.
'''
    freeze(folder/'AGENT_TASK.md',task.encode('utf-8'))
    launch=f'Read and follow only {folder / "AGENT_TASK.md"} and its EXACT_PROMPT.md. You are an isolated student-decision participant. Follow the local display/submit protocol until complete or terminal failure. No source/private files, policy code, other agents, API calls or analysis. Return the preserved RESULT.json path and deviations.'
    freeze(folder/'LAUNCH_MESSAGE.txt',launch.encode('utf-8'))
    subprocess.run([sys.executable,'-X','utf8',str(transport),'init','--run',str(folder)],check=True,capture_output=True)
    print(json.dumps(dict(folder=str(folder),launch_message=launch,requested_model='gpt-6-astra',requested_effort='xhigh')))
    return folder


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=['latency','feasibility','main'],required=True)
    parser.add_argument('--version',choices=['V1','V2'],required=True)
    parser.add_argument('--block',required=True)
    parser.add_argument('--arm',choices=['A','B','C'],required=True)
    parser.add_argument('--game-seconds',type=float)
    parser.add_argument('--probe-seconds',type=float)
    args=parser.parse_args()
    limits=None if args.stage=='latency' else {'game':args.game_seconds,'probes':args.probe_seconds}
    if limits and any(v is None or v<=0 for v in limits.values()):parser.error('Both calibrated limits must be positive')
    prepare(args.stage,args.version,args.block,args.arm,limits)
