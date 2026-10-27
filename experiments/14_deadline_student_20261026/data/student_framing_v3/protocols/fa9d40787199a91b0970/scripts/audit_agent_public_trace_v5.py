"""Project visible tool records only; never export private reasoning/instructions.

The original session stays outside this repository. Encrypted message bodies are
not decrypted or represented as reviewed text. This is a mechanical trace check,
not an automatic scientific-adherence approval.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

CMD = re.compile(r'(?:"cmd"|\bcmd)\s*:\s*("(?:\\.|[^"\\])*")')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def visible_text(content):
    if isinstance(content, str):
        return content, False
    parts, encrypted = [], False
    for item in content or []:
        if not isinstance(item, dict):
            continue
        if item.get('type') in ('text', 'input_text', 'output_text'):
            parts.append(item.get('text', ''))
        elif item.get('type') == 'encrypted_content':
            encrypted = True
    return '\n'.join(parts), encrypted


def project(raw):
    public, settings, private_counts = [], [], Counter()
    for index, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line)
        except ValueError:
            private_counts['unfinished_record'] += 1
            continue
        p = event.get('payload', {})
        stamp = dict(record=index, timestamp=event.get('timestamp'))
        kind = event.get('type')
        if kind == 'session_meta':
            source = p.get('source', {})
            spawn = source.get('subagent', {}).get('thread_spawn', {}) if isinstance(source, dict) else {}
            public.append(dict(**stamp, type='session_identity', session_id=p.get('id'), agent_path=spawn.get('agent_path')))
        elif kind == 'turn_context':
            setting = dict(model=p.get('model'), effort=p.get('effort'))
            settings.append(setting)
            public.append(dict(**stamp, type='requested_client_setting', **setting))
        elif kind == 'response_item':
            typ = p.get('type')
            if typ in ('custom_tool_call', 'custom_tool_call_output', 'function_call', 'function_call_output'):
                fields = ('type', 'call_id', 'name', 'namespace', 'input', 'arguments', 'output')
                item = {k: p[k] for k in fields if k in p}
                # Collaboration messages may be encrypted at rest. Keep routing
                # metadata, never ciphertext in place of an exact prompt.
                if typ == 'function_call' and 'arguments' in item:
                    try:
                        args = json.loads(item['arguments'])
                        if isinstance(args.get('message'), str) and args['message'].startswith('gAAAA'):
                            args['message'] = '[message body encrypted in source; unavailable in this projection]'
                        item['arguments'] = json.dumps(args, ensure_ascii=False)
                    except (ValueError, TypeError, AttributeError):
                        pass
                public.append(dict(**stamp, **item))
            elif typ == 'message' and p.get('role') in ('user', 'assistant') and p.get('channel') in (None, 'commentary', 'final'):
                text, encrypted = visible_text(p.get('content'))
                public.append(dict(**stamp, type='public_message', role=p.get('role'), channel=p.get('channel'),
                                   text=text, encrypted_body_present=encrypted))
            elif typ == 'agent_message':
                text, encrypted = visible_text(p.get('content'))
                public.append(dict(**stamp, type='parent_message', author=p.get('author'), recipient=p.get('recipient'),
                                   visible_text=text, encrypted_body_present=encrypted))
            else:
                # Do not retain excluded text, summaries, instructions, internal
                # metadata or hidden reasoning in the derived artifact.
                private_counts['excluded_nonpublic_response_item'] += 1
    return public, settings, dict(private_counts)


def inspect(public, folder):
    steps = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((folder / 'steps').glob('*.json'))]
    accepted = [s for s in steps if s['action'] == 'submit']
    cursor, commands, issues, filtered, unknown, reads = 0, [], [], [], [], []
    unaccepted_submissions = []
    outputs = {e.get('call_id'): e for e in public if e['type'] == 'custom_tool_call_output'}
    for event in public:
        if event['type'] != 'custom_tool_call':
            continue
        code = event.get('input', '')
        extracted = []
        for match in CMD.finditer(code):
            try:
                extracted.append(json.loads(match.group(1)))
            except ValueError:
                issues.append(dict(record=event['record'], problem='Command could not be parsed'))
        if not extracted:
            unknown.append(dict(record=event['record'], reason='No recognized exec command'))
        for command in extracted:
            entry = dict(record=event['record'], call_id=event.get('call_id'))
            normalized = command.replace('\\', '/').lower()
            own = str(folder.resolve()).replace('\\', '/').lower()
            if ' submit --run ' in command:
                entry['kind'] = 'submit'
                match = re.search(r"@'\s*\r?\n(.*?)\r?\n'@", command, re.S)
                if not match:
                    issues.append(dict(**entry, problem='Submission is not a literal here-string'))
                else:
                    try:
                        choices = json.loads(match.group(1))
                    except ValueError:
                        choices = None
                    if cursor < len(accepted) and choices == accepted[cursor]['choices']:
                        entry['accepted_step'] = accepted[cursor]['index']
                        cursor += 1
                    else:
                        # Could be a rejected request, or an unrecognized command.
                        # Preserve for human review; never drop an accepted step.
                        unaccepted_submissions.append(dict(**entry, reason='Does not match the next accepted step'))
                    tail = command[match.end():]
                    if 'ConvertFrom-Json' in tail or 'Select-Object' in tail:
                        filtered.append(dict(**entry, public_display_transform=tail))
                if own not in normalized:
                    issues.append(dict(**entry, problem='Submission points outside its own run'))
            elif ' show --run ' in command or ' status --run ' in command:
                entry['kind'] = 'show' if ' show --run ' in command else 'status'
                if own not in normalized:
                    issues.append(dict(**entry, problem='Public query points outside its own run'))
            elif 'Get-Content' in command:
                entry['kind'] = 'read'
                reads.append(dict(**entry, command=command))
                if own not in normalized or not any(n in command for n in ('AGENT_TASK.md', 'EXACT_WEBSITE_PROMPT.md')):
                    issues.append(dict(**entry, problem='Unrecognized file read'))
            else:
                entry['kind'] = 'other'
                unknown.append(dict(**entry, command=command))
            commands.append(entry)
        output = str(outputs.get(event.get('call_id'), {}).get('output', ''))
        if 'tokens truncated' in output.lower() or 'output truncated' in output.lower():
            issues.append(dict(record=event['record'], problem='Tool output was truncated; inspect subsequent show'))
    if cursor != len(accepted):
        issues.append(dict(problem='Not every accepted choice page matched a visible literal submission', matched=cursor, accepted=len(accepted)))
    return dict(accepted_pages=len(accepted), matched_literal_submissions=cursor,
                command_counts=dict(Counter(c['kind'] for c in commands)),
                command_sequence=commands, file_reads=reads, filtered_public_displays=filtered,
                unaccepted_submissions=unaccepted_submissions, issues=issues, unrecognized_commands=unknown,
                parent_messages_with_unavailable_body=sum(e.get('encrypted_body_present', False) for e in public if e['type']=='parent_message'),
                automatic_adherence_approval=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=Path, required=True)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()
    raw = args.session.read_bytes()
    public, settings, excluded = project(raw)
    audit = inspect(public, args.run)
    audit.update(source_session_sha256=digest(raw), requested_client_settings=settings,
                 projected_public_records=len(public), excluded_counts=excluded,
                 created_utc=datetime.now(timezone.utc).isoformat())
    if args.save:
        if not json.loads((args.run / 'STATUS.json').read_text())['complete']:
            raise ValueError('Save the immutable public projection after collection finishes.')
        out = args.run / 'PUBLIC_TRANSCRIPT.jsonl'
        data = ''.join(json.dumps(e, ensure_ascii=False) + '\n' for e in public).encode('utf-8')
        audit['public_transcript_sha256'] = digest(data)
        for path, content in ((out, data), (args.run / 'TRACE_AUDIT.json', (json.dumps(audit, indent=2)+'\n').encode())):
            if path.exists() and path.read_bytes() != content:
                raise ValueError('Preserve existing provenance artifact: '+str(path))
            path.write_bytes(content)
    print(json.dumps({k:v for k,v in audit.items() if k not in ('command_sequence','file_reads','filtered_public_displays','requested_client_settings')}, indent=2))
    print('Filtered public displays:', len(audit['filtered_public_displays']))


if __name__ == '__main__':
    main()
