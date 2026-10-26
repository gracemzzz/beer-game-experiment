"""Add prospectively numbered agent contexts; no API or model calls."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study.manual_batch_analysis_v5 import freeze, sha, verify_manifest

EXP = ROOT / 'experiments/13_weekly_state_api_20261021'
BASE = EXP / 'data/assistant_v5_20261025'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--replicate', type=int, required=True)
    p.add_argument('--model', choices=['gpt_astra', 'gpt_sol', 'gpt_luna'], required=True)
    args = p.parse_args()
    if not 2 <= args.replicate <= 10:
        raise ValueError('This extension prepares attempted contexts 2 through 10 only.')
    verify_manifest(EXP / 'data/manual_batch_v5_614dfdfeb3f15acf')
    plan = BASE / 'REPLICATION_AMENDMENT_01.json'
    if not plan.exists():
        freeze(plan, dict(created_utc=datetime.now(timezone.utc).isoformat(),
            parent_collection_plan_sha256=sha(BASE/'COLLECTION_PLAN.json'),
            reason='User requests more fresh agent contexts and live sample-size statistics.',
            target_attempted_contexts_per_model=10, models=['gpt_astra','gpt_sol','gpt_luna'],
            prefixes=[1,2,5,10], chains_per_condition_per_context=50, weeks=24, conditions=['A','B','C'],
            rationale='Fixed first replication stage within the v5 maximum; chosen without inspecting completed three-condition contrasts.',
            scientific_prompt_and_physics='Unchanged frozen v5; same requested models and high effort.',
            operational_clarification='Read the entire public display without filtering. This was already required; repeated explicitly in new task wrappers.',
            first_wave='Retained, reviewed by the same criteria; failures remain in the attempt count.',
            stopping_rule='Ten attempted fresh contexts per model, regardless of signs or p-values. No replacement of unfavorable, failed, or excluded runs.',
            inference='Fresh context is the unit. Eligibility requires literal choices, complete public state exposure and trace review. Missing/failed attempts remain visible.',
            analysis='Exploratory two-sided paired context contrasts, Holm family 20, pointwise intervals. No sequential significance guarantee.',
            api_requests=0, funding='No charge to the shared API ledger; agent service usage is separate.'))
    source = BASE / args.model / 'run001'
    target = BASE / args.model / f'run{args.replicate:03d}'
    if target.exists():
        raise ValueError('Prepared context exists; resume it, never replace it.')
    original = json.loads((source/'CASE.json').read_text(encoding='utf-8'))
    case = dict(original)
    case.update(case_id=f'AGENTV5_{args.model.upper()}_R{args.replicate:03d}', batch_id=uuid.uuid4().hex,
                replication_amendment_sha256=sha(plan), attempt_number=args.replicate)
    for helper in source.joinpath('helper').glob('*.py'):
        freeze(target/'helper'/helper.name,helper.read_bytes())
    freeze(target/'CASE.json',case)
    freeze(target/'EXACT_WEBSITE_PROMPT.md',(source/'EXACT_WEBSITE_PROMPT.md').read_bytes())
    task=(source/'AGENT_TASK.md').read_text(encoding='utf-8').replace(str(source),str(target)).replace(original['case_id'],case['case_id'])
    task=task.replace('at least 8000','at least 10000')
    task+='''\nDISPLAY REQUIREMENT: Read the complete public JSON returned by every transport call. Do not pipe it through Select-Object, ConvertFrom-Json projections, or any filter that removes inventory, pipeline, role, history, profile, shared-state or instruction fields. If the output truncates, call show again with a sufficient output limit before choosing. Preserve zero or unchanged choices when appropriate; no outcome direction is requested.\n'''
    freeze(target/'AGENT_TASK.md',task.encode())
    launch=(f'You are an isolated participant, not a repository maintainer. Read and follow {target / "AGENT_TASK.md"} and its specified EXACT_WEBSITE_PROMPT.md. '
            'Those are your complete task instructions apart from platform rules. Do not inspect other project files, source, reports, private state or other runs. '
            'Use the provided local transport for one literal-choice page per model/tool interaction, reading every complete public display without filtering. '
            'Complete the prepared 50-chain-per-condition, 24-week, three-condition case; preserve partial if blocked. '
            'No API calls, extra agents, automatic ordering policy, outcome analysis or manufacture. Report the RESULT path and deviations honestly.')
    continuation=(f'Resume the SAME prepared run at {target} using show. Follow AGENT_TASK.md and the exact prompt unchanged. '
                  'Continue literal choices page by page, reading COMPLETE public displays with max_output_tokens at least 10000; no output filtering, policy code, private/source access, restarts or analysis. '
                  'Complete all remaining weeks and probes, or report the saved checkpoint if the turn limit intervenes. This continuation remains the same context, not another replicate.')
    freeze(target/'LAUNCH_MESSAGE.txt',launch.encode())
    freeze(target/'CONTINUATION_MESSAGE.txt',continuation.encode())
    driver=ROOT/'scripts/run_manual_agent_v5.py'
    subprocess.run([sys.executable,'-X','utf8',str(driver),'init','--run',str(target)],capture_output=True,check=True)
    print(json.dumps(dict(folder=str(target),launch_message=launch,requested_model=case['requested_model'],requested_effort=case['requested_effort'])))


if __name__ == '__main__':
    main()
