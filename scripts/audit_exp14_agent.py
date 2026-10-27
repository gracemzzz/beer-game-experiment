"""Privacy-preserving public procedure projection for completed/stopped exp14 cases.

This mechanical review is not scientific approval. A researcher must inspect the
record and separately save a hash-bound ADHERENCE_REVIEW.json.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import ast
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_agent_public_trace_v5 import project,CMD


def objects(value,depth=0):
    if depth>12:return []
    if isinstance(value,str):
        value=value.strip()
        if not value.startswith(('{','[')):return []
        try:decoded=json.loads(value)
        except (ValueError,TypeError):
            try:decoded=ast.literal_eval(value)
            except (ValueError,SyntaxError,TypeError):return []
        return objects(decoded,depth+1)
    if isinstance(value,list):return [r for x in value for r in objects(x,depth+1)]
    if isinstance(value,dict):
        found=[value] if 'case_id' in value and ('display_sha256' in value or 'accepted' in value) else []
        return found+[r for x in value.values() for r in objects(x,depth+1)]
    return []


def audit(public,folder):
    raw=json.loads((folder/'RESULT.json').read_text(encoding='utf-8'))
    canonical={e['display']['decision_id']:e['display'] for e in raw['events'] if e['kind']=='display_opened'}
    accepted={d['decision_id']:d for d in raw['decisions']}
    outputs={e.get('call_id'):e for e in public if e['type'] in ('custom_tool_call_output','function_call_output')}
    shown=set();matches=[];issues=[];reads=[];unknown=[];calls=[]
    own=str(folder.resolve()).replace('\\','/').lower()
    for e in public:
        if e['type'] not in ('custom_tool_call','function_call'):continue
        text=e.get('input',e.get('arguments',''))
        commands=[json.loads(m.group(1)) for m in CMD.finditer(text)]
        if e.get('name')=='exec_command':
            try:commands=[json.loads(text)['cmd']]
            except (ValueError,KeyError):pass
        if not commands:
            if e.get('name') not in ('send_message','wait'):unknown.append(dict(record=e['record'],name=e.get('name')))
            continue
        returned=objects(outputs.get(e.get('call_id'),{}).get('output'))
        for command in commands:
            entry=dict(record=e['record'],command=command)
            normalized=command.replace('\\','/').lower()
            if own not in normalized:issues.append(dict(record=e['record'],problem='Command outside own prepared run',command=command))
            if 'Get-Content' in command:
                reads.append(entry)
                if not any(n in command for n in ('AGENT_TASK.md','EXACT_PROMPT.md')):issues.append(dict(record=e['record'],problem='Unexpected file read'))
            elif ' submit ' in command:
                ident=re.search(r'--decision-id\s+[\'\"]?([0-9a-f]+)',command)
                literal=re.search(r"@'\r?\n(.*?)\r?\n'@",command,re.S)
                successful=[x for x in returned if x.get('accepted') is True]
                if successful:
                    try:
                        did=ident.group(1);choices=json.loads(literal.group(1))
                        assert did in accepted and choices==accepted[did]['choices']
                        assert any(x.get('decision_id')==did for x in successful)
                        assert did in shown
                        matches.append(dict(decision_id=did,record=e['record'],full_display_seen=True))
                    except (AssertionError,AttributeError,ValueError,TypeError):issues.append(dict(record=e['record'],problem='Accepted input/display/decisionID mismatch'))
            elif ' show ' not in command and ' status ' not in command:unknown.append(entry)
            if any(p in command for p in ('ConvertFrom-Json','Select-Object','Where-Object')):
                issues.append(dict(record=e['record'],problem='Public-display filter detected'))
            if any(p in command for p in ('Array.from','Object.fromEntries','.fill(','foreach','for (','for(')):
                issues.append(dict(record=e['record'],problem='Possible generated choices; inspect code'))
            for item in returned:
                did=item.get('decision_id')
                if 'display_sha256' in item and did in canonical and item==canonical[did]:shown.add(did)
            calls.append(entry)
    if set(accepted)!={m['decision_id'] for m in matches} or len(matches)!=len(accepted):
        issues.append(dict(problem='Not all accepted literal decisions matched full public displays'))
    return dict(accepted_decisions=len(accepted),matched_public_literal_decisions=len(matches),
        full_displays_seen=len(shown),issues=issues,file_reads=reads,unrecognized_calls=unknown,
        commands=calls,matches=matches,parent_message_headers=sum(e['type']=='parent_message' for e in public),
        automatic_scientific_approval=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--session',type=Path,required=True)
    parser.add_argument('--run',type=Path,required=True);args=parser.parse_args()
    raw=args.session.read_bytes();public,settings,excluded=project(raw)
    data=''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in public).encode('utf-8')
    result=audit(public,args.run)
    result.update(created_utc=datetime.now(timezone.utc).isoformat(),requested_settings=settings,
        result_sha256=hashlib.sha256((args.run/'RESULT.json').read_bytes()).hexdigest(),
        transcript_sha256=hashlib.sha256(data).hexdigest(),source_session_sha256=hashlib.sha256(raw).hexdigest(),
        excluded_nonpublic_counts=excluded)
    for path,value in [(args.run/'PUBLIC_TRANSCRIPT.jsonl',data),
        (args.run/'PUBLIC_PROCEDURE_REVIEW.json',(json.dumps(result,indent=2)+'\n').encode('utf-8'))]:
        if path.exists():raise FileExistsError(path)
        path.write_bytes(value)
    print(json.dumps({k:v for k,v in result.items() if k not in ('commands','matches','file_reads','requested_settings')},indent=2))
