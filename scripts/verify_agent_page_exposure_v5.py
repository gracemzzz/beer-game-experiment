"""Compare public tool displays and accepted literal inputs with frozen step records.

Reads only the already projected public transcript. Does not approve scientific
adherence, decrypt messages, inspect reasoning, or modify observations.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime, timezone

from audit_agent_public_trace_v5 import CMD


def displayed_states(value, depth=0):
    if depth > 12:
        return []
    if isinstance(value, str):
        value=value.strip()
        if not value.startswith(('{','[')):
            return []
        try:
            decoded=json.loads(value)
        except (ValueError,TypeError):
            try:
                decoded=ast.literal_eval(value)
            except (ValueError,SyntaxError,TypeError):
                return []
        return displayed_states(decoded,depth+1)
    if isinstance(value,list):
        return [d for item in value for d in displayed_states(item,depth+1)]
    if isinstance(value,dict):
        if 'batch_id' in value and ('decision' in value or 'phase' in value):
            return [value]
        return [d for key in ('output','text','content') if key in value
                for d in displayed_states(value[key],depth+1)]
    return []


def verify(folder):
    public=[json.loads(line) for line in (folder/'PUBLIC_TRANSCRIPT.jsonl').read_text(encoding='utf-8').splitlines()]
    steps=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((folder/'steps').glob('*.json'))]
    steps=[s for s in steps if s['action']=='submit']
    outputs={e.get('call_id'):e.get('output') for e in public if e['type']=='custom_tool_call_output'}
    current=None
    accepted=[]
    failed=[]
    issues=[]
    for e in public:
        if e['type']!='custom_tool_call':
            continue
        commands=[]
        for match in CMD.finditer(e.get('input','')):
            commands.append(json.loads(match.group(1)))
        states=displayed_states(outputs.get(e.get('call_id')))
        for command in commands:
            if ' submit --run ' not in command:
                continue
            match=re.search(r"@'\s*\r?\n(.*?)\r?\n'@",command,re.S)
            choices=json.loads(match.group(1)) if match else None
            next_step=steps[len(accepted)] if len(accepted)<len(steps) else None
            if (next_step and choices==next_step['choices'] and
                    next_step['display_after'] in states):
                full_before=(current==next_step['display_before'])
                accepted.append(dict(step=next_step['index'],public_record=e['record'],
                                     full_display_before=full_before,full_display_after=True))
                if not full_before:
                    issues.append(dict(record=e['record'],step=next_step['index'],problem='Complete current public display not observed before accepted choice'))
            else:
                failed.append(dict(record=e['record'],call_id=e.get('call_id'),
                                   has_public_game_output=bool(states)))
        if states:
            current=states[-1]
    if len(accepted)!=len(steps):
        issues.append(dict(problem='Not all accepted steps matched literal input AND successful complete public output',matched=len(accepted),saved=len(steps)))
    return dict(accepted_steps=len(steps),matched_successful_literal_steps=len(accepted),
        full_before_count=sum(x['full_display_before'] for x in accepted),issues=issues,
        failed_or_unmatched_attempts=failed,accepted_mapping=accepted,
        mechanical_full_page_exposure_passed=not issues,
        scientific_adherence_approved=False,private_reasoning_read=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--save',action='store_true')
    args=parser.parse_args()
    result=verify(args.run)
    result.update(created_utc=datetime.now(timezone.utc).isoformat(),
        result_sha256=hashlib.sha256((args.run/'RESULT.json').read_bytes()).hexdigest(),
        public_transcript_sha256=hashlib.sha256((args.run/'PUBLIC_TRANSCRIPT.jsonl').read_bytes()).hexdigest(),
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    if args.save:
        out=args.run/'PAGE_EXPOSURE_REVIEW.json'
        if out.exists():raise FileExistsError(out)
        out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('accepted_mapping','failed_or_unmatched_attempts')},indent=2))


if __name__=='__main__':main()
