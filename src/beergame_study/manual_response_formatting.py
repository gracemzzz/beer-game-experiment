"""Operational JSON type conversion; never modifies frozen scientific sources or orders."""
import hashlib
import json
import re
from pathlib import Path

from .manual_cohort_chat import parse_response


def normalize_rule_types(raw):
    """Convert unambiguous quoted rule answers, preserving every other character.

    Does not consult the correct-answer key. Wrong answers remain wrong and must
    still be rejected by the frozen validator. No order/probe conversion is allowed.
    """
    payload = parse_response(raw)
    rules = payload.get('rules')
    if not isinstance(rules, dict):
        raise ValueError('Missing rules object.')
    converted, edits = raw, []
    for key, value in rules.items():
        if type(value) is not str:
            continue
        if key == 'backlog_includes_current_unfilled_demand' and value.lower() in ('yes', 'no', 'true', 'false'):
            new = value.lower() in ('yes', 'true')
        elif key == 'factory_order_week_7_arrival_week' and re.fullmatch(r'(?:[Ww]eek )?[0-9]+', value):
            new = int(value.split(' ')[-1])
        elif key == 'three_week_backlog_cost' and re.fullmatch(r'\$?[0-9]+', value):
            new = int(value.removeprefix('$'))
        else:
            raise ValueError('Ambiguous rule text; no automatic conversion: '+key)
        pattern = r'(' + re.escape(json.dumps(key)) + r'\s*:\s*)' + re.escape(json.dumps(value))
        converted, count = re.subn(pattern, lambda match: match.group(1)+json.dumps(new), converted)
        if count != 1:
            raise ValueError('Rule field was not uniquely represented.')
        edits.append(dict(field='rules.'+key, before=value, after=new))
    if not edits:
        raise ValueError('No rule type conversion is needed.')
    after = parse_response(converted)
    assert {k:v for k,v in after.items() if k!='rules'} == {k:v for k,v in payload.items() if k!='rules'}
    return converted, edits


def build_report(run, *, fit_beta=False):
    """Append transformation disclosure to the frozen v2 report; no metric changes."""
    from .manual_cohort_chat_report import build_report as frozen_report
    run = Path(run)
    notes = []
    for path in sorted((run/'normalization').glob('*.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        for key in ('original', 'derived'):
            data = (run/record[key+'_path']).read_bytes()
            if hashlib.sha256(data).hexdigest() != record[key+'_sha256']:
                raise ValueError('Formatting provenance hash mismatch: '+key)
        original = (run/record['original_path']).read_bytes().decode('utf-8')
        derived = (run/record['derived_path']).read_bytes().decode('utf-8')
        reproduced, edits = normalize_rule_types(original)
        if reproduced != derived or edits != record['edits']:
            raise ValueError('Formatting transformation cannot be reproduced.')
        accepted = json.loads((run/'accepted'/f"{record['batch_id']}_{record['stage']}.json").read_text(encoding='utf-8'))
        if accepted['raw_sha256'] != record['derived_sha256']:
            raise ValueError('Accepted response differs from documented derivative.')
        notes.append(f"- **{record['batch_id']} {record['stage']}:** {len(edits)} rule-answer JSON types were "
                     "converted mechanically after receipt. The original response is retained as a rejected "
                     "format attempt; the accepted text is an explicitly documented derivative. "
                     "All orders, probes and other text are unchanged. No model retry or additional deliberation occurred.")
    result = frozen_report(run, fit_beta=fit_beta)
    if notes:
        disclosure = ('\n## Response formatting provenance\n\n'+'\n'.join(notes)+'\n\n'
                      'This format-only exception was documented after receiving the affected response. '
                      'It preserves the supplied answer meanings, without substituting correct answers. '
                      'Original/derived files, hashes and the exact edits are recorded under the run’s '
                      '`normalization/` directory. It is not another model generation.\n')
        path = result['report']
        path.write_text(path.read_text(encoding='utf-8')+disclosure, encoding='utf-8')
    return result
