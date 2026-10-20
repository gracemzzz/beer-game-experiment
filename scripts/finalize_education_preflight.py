"""Publish the bounded assistant preflight from saved replies only; no model calls."""
from __future__ import annotations

import ast
import hashlib
import io
import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study import education_deadline_cohort as study
from education_deadline_workflow import OUTPUT, PREFLIGHT, report


def literal_source_check(source, payload):
    """Inspect optional source text without executing model-returned programs."""
    result = dict(source_present=source.exists(), explicit_chain_records_matched=0,
                  source_sha256=None, source_executed_by_importer=False)
    if not source.exists():
        return result
    data = source.read_bytes()
    result['source_sha256'] = hashlib.sha256(data).hexdigest()
    try:
        tree = ast.parse(data.decode('utf-8'))
    except (SyntaxError, UnicodeDecodeError) as exc:
        result['source_parse_error'] = str(exc)
        return result
    literal_chains = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            try:
                value = ast.literal_eval(node)
            except (ValueError, TypeError):
                continue
            if isinstance(value, dict) and set(value) == {'chain_id', 'orders', 'probes'}:
                if value['chain_id'] in literal_chains and literal_chains[value['chain_id']] != value:
                    raise ValueError('Conflicting literal chain records in serialization source.')
                literal_chains[value['chain_id']] = value
        # A complete literal JSON string is also a lossless serialization source.
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.lstrip().startswith('{'):
            try:
                candidate = json.loads(node.value)
            except ValueError:
                continue
            if isinstance(candidate, dict):
                for chain in candidate.get('chains', []):
                    if isinstance(chain, dict) and set(chain) == {'chain_id', 'orders', 'probes'}:
                        literal_chains[chain['chain_id']] = chain
    matched = sum(literal_chains.get(chain['chain_id']) == chain for chain in payload['chains'])
    result['explicit_chain_records_matched'] = matched
    result['expected_chain_records'] = len(payload['chains'])
    result['all_output_choices_have_matching_literal_records'] = matched == len(payload['chains'])
    # This is a source inspection, not proof of internal decision chronology or human fidelity.
    return result


def main():
    plan = study.read(PREFLIGHT/'PLAN.json')
    receipts = []
    for slot in plan['slots']:
        run = ROOT/slot['run']
        response = ROOT/slot['response_path']
        source = ROOT/slot['serialization_path']
        if not response.exists():
            raise ValueError('Bounded preflight output has not arrived: '+str(response))
        locked = study.accepted_path(run, slot['task_id'])
        status, reason = 'rejected', None
        try:
            if locked.exists():
                entry = study.load_accepted(run, slot['task_id'])
                if hashlib.sha256(response.read_bytes()).hexdigest() != entry['raw_sha256']:
                    raise ValueError('Preflight source no longer matches accepted original.')
            else:
                entry = study.import_response(run, slot['task_id'], response,
                    model_label='current-assistant-inherited', effort_label='inherited',
                    session_label='isolated-'+slot['category']+'-'+slot['task_id'],
                    confirm_full_prompt=True)
            status = entry['status']
            literal = literal_source_check(source, entry['payload'])
        except ValueError as exc:
            reason = str(exc)
            literal = dict(source_present=source.exists(), source_executed_by_importer=False)
        receipts.append(dict(category=slot['category'], task_id=slot['task_id'],
            response_sha256=hashlib.sha256(response.read_bytes()).hexdigest(),
            response_bytes=response.stat().st_size, status=status, reason=reason,
            source_inspection=literal))
    index = plan['index']
    pilot = report(ROOT/index['pilot_run'], OUTPUT/'pilot')
    capacity = report(ROOT/index['capacity_run'], OUTPUT/'capacity_check')
    summary = study.read(OUTPUT/'pilot/provenance.json')
    import pandas as pd
    hypotheses = pd.read_csv(OUTPUT/'pilot/results/hypothesis_summary.csv')
    overall = hypotheses[hypotheses.repetition.astype(str) == 'overall']
    lines = []
    for row in overall.to_dict('records'):
        value = row['mean_difference']
        shown = 'missing' if pd.isna(value) else f'{value:+.6f}'
        lines.append(f"| {row['hypothesis']} | {shown} | {row['direction']} |")
    accepted_pilot = sum(r['category'] == 'pilot' and r['status'] == 'accepted' for r in receipts)
    accepted_capacity = sum(r['category'] == 'capacity' and r['status'] == 'accepted' for r in receipts)
    capacity_record = next(r for r in receipts if r['category'] == 'capacity')
    literal_records = capacity_record['source_inspection'].get('explicit_chain_records_matched', 0)
    limits = [dict(paired_independent_generation_blocks=r, total_case_responses=3*r,
                   minimum_one_sided_exact_p=1/(2**r), minimum_two_sided_exact_p=min(1, 2/(2**r)))
              for r in (2, 4, 6, 7, 8, 16)]
    limits_csv = pd.DataFrame(limits).to_csv(index=False, lineterminator='\n')
    study.save_new(OUTPUT/'replication_limits.csv', limits_csv)
    capacity_sentence = (f'The one scheduled full-cohort technical reply passed import and physical replay: **125 chains, 500 identities, '
        f'10,000 weekly orders and 1,000 scalar probe choices**. Its serialization source has matching explicit literal records for '
        f'**{literal_records}/125 chains**. This demonstrates one complete file under the inherited assistant backend; '
        'it does not establish the capacity or tool availability of the user\'s website selection.' if accepted_capacity else
        'The scheduled full-cohort technical reply failed validation/replay. Preserve the failure and treat full-size delivery as unverified; '
        'do not claim the six full-cohort website tasks have been demonstrated feasible.')
    text = '''# Preflight findings: 19 October 2026

The supplied reflection has been read. The new package preserves the earlier four-role, four-personality game structure and 500 fictional identities, while changing the deadline descriptions to 10 and 60 seconds and adding a causal-reading/control comparison. It is a separate model simulation, not a substitute for the reflection's timed human experiment.

**Three cases, each covering all 125 chains:** A = 60s/control; B = 10s/control; C = 10s/causal education. One generation takes three prompts. The frozen website plan repeats every case once, for **six fresh-chat prompts**. Download each reply as JSON and return the six files together or in one ZIP. No manual extraction of student decisions is needed. [Start guide and all six prompts](START_HERE.md), [prompt ZIP](Beer_Game_10s_60s_Prompts.zip).

## Results before website collection

'''+f'''The fixed small pilot received **{accepted_pilot}/6 accepted first-attempt responses**, with four chains / 16 identities per response. All attempts are retained. This is an unpaid, isolated assistant pilot under inherited settings, not verified GPT-6 / Pro website execution. Its two generations give these descriptive mean contrasts:

| Hypothesis | Mean contrast | Observed direction |
| --- | ---: | --- |
'''+ '\n'.join(lines)+f'''

H1 is B-A pipeline sensitivity; H2 is B-A full holding/backlog cost; H3 is C-B sensitivity; H4 is C-B full cost. The signs are observations, not acceptance criteria or confirmation of human hypotheses. [All pilot results, repeat changes and cost phases](pilot/REPORT.md), [Excel](pilot/results/RESULTS.xlsx).

{capacity_sentence} [Capacity report](capacity_check/REPORT.md).

The bounded check comprised exactly six small-cohort outputs and this one full-cohort output. Its technical run has three prepared case slots, but the other two were prospectively outside this capacity check; there is no missing treatment comparison to infer from it. Conditions were dispatched as fresh isolated assistant contexts, with some tasks running concurrently. No parent hypotheses, competing answers or prior replies were included. The saved two-block task order is A-B-C followed by A-C-B: it changes B/C order but leaves A first, so it is not complete counterbalancing. Actual overlapped execution is also distinct from this dispatch order. The frozen scheduling rule covers all six permutations only over six blocks, beyond this fixed sample. Instructions requested direct explicit choices; the available literal sources are inspected without execution. JSON/schema/replay checks do not verify the model's internal decision process, human persona validity or chronological information isolation. The website run remains a separate collection.

## Why this does not promise significance

The 125 chains in a jointly generated answer cannot be assumed independent participants. Six answers provide only two response-level generations per case. Even assuming independent exchangeable paired generations, the smallest two-sided exact sign-flip p-value with two contrasts is **0.50**; the one-sided minimum is **0.25**. These are mathematical resolution limits, not tests applied to the pilot.

With four planned tests, a conservative threshold is 0.05/4 = 0.0125. At least eight paired response-level blocks (24 case responses) are needed even to permit a two-sided exact p-value below that threshold; this is not a power guarantee or a recommendation to extend the observed pilot. [Replication resolution table](replication_limits.csv). Significance would require a separately planned design with enough independent generation or human replication and justified assumptions. An automated runner can reduce manual work while keeping many independent calls; new paid execution would need a separate authorized cap and accounting.

The readings are matched at 254 words each. They do not deliver a 20-minute lecture or establish that a pretrained model learned the causal material. Ten/sixty-second wording does not impose actual model compute or verify binding/adequate time. The H1/H3 matched-state slope remains a pipeline-sensitivity proxy, not an identified structural underweighting coefficient. These limitations prevent this package from literally confirming all four stated human-time hypotheses.

Prompts were frozen before any preflight outputs. No favorable-effect filter, significance-based prompt revision, additional trial, rejected-result replacement, or paid API call was used. Preserve the complete pilot, capacity output and website plan. [Full protocol](DESIGN.md), [software/provenance verification](../software_checks/education_deadline_20261019.json).

The reflection's human design remains the route to literal tests: calibrate and record actual decision times, randomize chains, deliver matched instruction sessions, and prespecify an identified underweighting measure and chain-level cost analysis. The present package addresses the user's requested low-copy model preflight.

Sources: [OpenAI file creation documentation](https://developers.openai.com/api/docs/guides/tools-code-interpreter), [Hurlbert on experimental replication](https://doi.org/10.2307/1942661), [ASA on complete statistical reporting](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf). The application of replication concerns to jointly generated model rows is the methodological judgment used here.
'''
    study.save_new(OUTPUT/'PREFLIGHT_FINDINGS.md', text)
    study.save_new(PREFLIGHT/'CHECKS.json', dict(receipts=receipts, fixed_attempts=7,
        accepted_pilot_responses=accepted_pilot, accepted_capacity_responses=accepted_capacity,
        outcome_selection=False, paid_api_calls=0, human_observations=0,
        pilot_analysis_signature=summary['analysis_signature']))
    # A review bundle includes the prompts and all resulting reader-facing preflight outputs.
    buffer = io.BytesIO()
    paths = [p for p in OUTPUT.rglob('*') if p.is_file() and p.name != 'Beer_Game_10s_60s_Review.zip']
    with ZipFile(buffer, 'w', compression=ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            info = ZipInfo(path.relative_to(OUTPUT).as_posix(), date_time=(2026, 10, 19, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
        evidence = {'preflight_evidence/PLAN.json': PREFLIGHT/'PLAN.json',
                    'preflight_evidence/CHECKS.json': PREFLIGHT/'CHECKS.json',
                    'preflight_evidence/ORCHESTRATION.json': PREFLIGHT/'ORCHESTRATION.json'}
        for slot in plan['slots']:
            prefix = 'preflight_evidence/'+slot['category']+'/'+slot['task_id']
            evidence[prefix+'_prompt.txt'] = ROOT/slot['run']/'prompts'/(slot['task_id']+'.txt')
            evidence[prefix+'_response.json'] = ROOT/slot['response_path']
            source = ROOT/slot['serialization_path']
            if source.exists():
                evidence[prefix+'_serialization.py'] = source
        for name, path in sorted(evidence.items()):
            info = ZipInfo(name, date_time=(2026, 10, 19, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    study.save_new(OUTPUT/'Beer_Game_10s_60s_Review.zip', buffer.getvalue())
    print(json.dumps(dict(accepted_pilot_responses=accepted_pilot,
        accepted_capacity_responses=accepted_capacity, findings=str(OUTPUT/'PREFLIGHT_FINDINGS.md')), indent=2))


if __name__ == '__main__':
    main()
