"""Publish saved reported-settings responses; never generate model decisions."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study import education_deadline_collection as collection
from beergame_study.education_deadline_cohort import read, save_new
from beergame_study.education_deadline_report import build_report


def table(frame, columns):
    if frame.empty:
        return '_No eligible observations._\n'
    def show(value):
        if isinstance(value, float):
            return f'{value:.6f}'
        return str(value).replace('|', '/')
    return ('| '+' | '.join(columns)+' |\n| '+' | '.join(['---']*len(columns))+' |\n'+
            ''.join('| '+' | '.join(show(row[col]) for col in columns)+' |\n'
                    for row in frame.to_dict('records')))


def publish():
    pointer = read(ROOT/'reports/LATEST_EDUCATION_DEADLINE_COLLECTION.json')
    run = ROOT/pointer['collection_run']
    output = ROOT/pointer['report_folder']
    manifest = collection.audit(run)
    intake = read(run/'intake/INTAKE.json')
    result = build_report(run, output, backend=collection)
    tables = result['tables']
    model_rows = tables['rounds'].loc[tables['rounds'].phase == 'model']
    columns = ['task_id', 'repetition', 'arm', 'deadline_seconds', 'lecture_id', 'chain_id',
               'participant_id', 'profile_id', 'role', 'week', 'order', 'customer_demand']
    weekly_orders = model_rows[columns]
    save_new(output/'results/weekly_orders.csv', weekly_orders.to_csv(index=False, lineterminator='\n'))
    prompt_sections = ['# Six original prompts\n\nThese are unchanged parent task texts. The parent specified GPT-6 / Pro; '
                       'the received collection is reported as GPT-6 Astra / extra high effort. The settings amendment '
                       'was recorded after the responses were collected.\n\n']
    for task in read(run/'plan.json')['tasks']:
        path = run/'prompts'/(task['task_id']+'.txt')
        save_new(output/'prompts'/path.name, path.read_bytes())
        prompt_sections.append(f"## {task['task_id']}\n\n```text\n{path.read_text(encoding='utf-8')}```\n\n")
    save_new(output/'EXACT_PROMPTS.md', ''.join(prompt_sections))
    mapping = []
    for item in intake['files']:
        accepted = collection.load_accepted(run, item['task_id'])
        data = (run/accepted['raw_path']).read_bytes()
        if hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError('Accepted original does not match received file: '+item['filename'])
        save_new(output/'original_responses'/item['filename'], data)
        mapping.append(dict(filename=item['filename'], task_id=item['task_id'], sha256=item['sha256']))
    save_new(output/'original_responses/FILE_MAP.json', mapping)
    save_new(output/'SETTINGS_AMENDMENT.md',
             (run/'amendments/EDUCATION_DEADLINE_SETTINGS_20261020.md').read_bytes())
    save_new(output/'collection_manifest.json', (run/'manifest.json').read_bytes())
    save_new(output/'parent_manifest.json', (collection.parent_run(run)/'manifest.json').read_bytes())
    save_new(output/'plan.json', (run/'plan.json').read_bytes())
    overall = tables['hypothesis_summary'].loc[tables['hypothesis_summary'].repetition.astype(str) == 'overall']
    summaries = tables['outcome_summary'].loc[tables['outcome_summary'].repetition.astype(str) == 'overall']
    findings = f'''# Collected responses: GPT-6 Astra / extra high effort

**Received 20 October 2026: {result['accepted_responses']}/6 complete responses accepted without conversion.** Each contains 125 chains / 500 fictional identities. Together they contain **{len(weekly_orders):,} submitted weekly orders**, **{len(tables['probes']):,} matched-state probe pairs**, and **{len(tables['rounds']):,} physically replayed role-week states**. The same identities repeat across cases and generations; this is not a sample of 3,000 independent people.

The reported settings are **GPT-6 Astra / extra high effort**. The original statement was: "I'm using gpt 6-astra extra high effort". Actual provider identity, interface, compute, full-prompt use, fresh-chat isolation and generation code were not independently verified. The frozen parent plan specified GPT-6 / Pro, so the actual reported settings are recorded through a new collection fingerprint and exact parent-prompt lineage. This amendment is recorded after collection. No response IDs or original bytes were changed, and these observations are not pooled with the earlier assistant pilot. [Settings amendment](SETTINGS_AMENDMENT.md).

## Observed case means

A = 60 seconds / control. B = 10 seconds / identical control. C = 10 seconds / causal reading. Both time values describe the fictional students, not enforced model computation. The matched readings contain 254 words each, rather than a delivered 20-minute lecture.

'''+table(summaries, ['arm', 'sensitivity', 'total_cost', 'cost_model', 'cost_automatic'])+'''
## H1-H4 descriptive contrasts

H1 is B-A sensitivity (predicted negative); H2 is B-A total cost (predicted positive). H3 is C-B sensitivity (predicted positive); H4 is C-B total cost (predicted negative). Sensitivity is the existing matched-state pipeline-responsiveness proxy, not an identified structural underweighting coefficient. Full cost includes four practice, twenty model and twelve automatic continuation weeks. Model-only costs are separately reported.

'''+table(overall, ['hypothesis', 'mean_difference', 'direction'])+'''
These directions describe this fixed set of generated outputs. They do not establish statistically significant treatment effects or confirm the literal human-time hypotheses. There are two response-level generations per case; jointly generated chain rows do not provide independent student replications. The [full report](REPORT.md) shows each repetition, same-case variation, changed orders and the cost-phase contrasts. The saved ABC/ACB task order provides partial order balance; actual execution order and concurrency were not verified.

No new model calls, paid API runs, prompt changes, favorable-effect filters or additional sampling were used for this analysis. All six source files, including compact response5.json, passed the same exact schema and replay checks. No serialization or generation source was supplied, so JSON validity cannot establish that choices were generated without a scripted policy.

[Excel results](results/RESULTS.xlsx) · [Only submitted weekly orders](results/weekly_orders.csv) · [All exact prompts](EXACT_PROMPTS.md) · [Original responses](original_responses/FILE_MAP.json).
'''
    save_new(output/'FINDINGS.md', findings)
    readme = f'''# Completed six-response collection

**GPT-6 Astra / extra high effort**, as reported by the user on 20 October 2026. All six files are accepted unchanged.

- [Short findings](FINDINGS.md)
- [Full report and plots](REPORT.md)
- [Excel workbook](results/RESULTS.xlsx)
- [60,000 submitted weekly orders](results/weekly_orders.csv)
- [Six exact prompts](EXACT_PROMPTS.md)
- [Original response file mapping](original_responses/FILE_MAP.json)
- [Settings amendment](SETTINGS_AMENDMENT.md)
- [Complete download](Beer_Game_Astra_10s_60s_20261020.zip)

Collection: `{run.name}`. Parent prepared study: `{manifest['lineage']['parent_study_id']}`. Original payload IDs remain linked to the parent. Earlier raw evidence, prepared prompts and preflight/publication packages are preserved.

The reported setting differs from the parent's GPT-6 / Pro plan and is not equated to Pro or an API effort enum. This collection uses a separate fingerprint. Deadline wording is fictional, pipeline sensitivity is a proxy, and model-generated identities are not independent human observations. No statistical-significance claim is made. No further response is required for this fixed six-task sample.

Reproduce from `D:\\beergame`:

```powershell
.\\.venv\\Scripts\\python.exe -X utf8 scripts/report_education_deadline_collection.py
.\\.venv\\Scripts\\python.exe -X utf8 scripts/check_education_deadline_collection.py
```

Both commands use saved files and make no model/API calls. A differing publication must be archived before replacement.
'''
    save_new(output/'README.md', readme)
    package_files = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob('*')
                     if p.is_file() and p.name not in ('PACKAGE_MANIFEST.json', 'Beer_Game_Astra_10s_60s_20261020.zip')}
    package_manifest = dict(date='2026-10-20', collection_id=run.name,
        source_collection=pointer['collection_run'], human_observations=0, api_calls=0,
        export_implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        files_sha256={name: hashlib.sha256(data).hexdigest() for name, data in sorted(package_files.items())})
    save_new(output/'PACKAGE_MANIFEST.json', package_manifest)
    package_files['PACKAGE_MANIFEST.json'] = (output/'PACKAGE_MANIFEST.json').read_bytes()
    buffer = io.BytesIO()
    with ZipFile(buffer, 'w', compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(package_files.items()):
            info = ZipInfo(name, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
    destination = output/'Beer_Game_Astra_10s_60s_20261020.zip'
    save_new(destination, buffer.getvalue())
    print(json.dumps(dict(collection_id=run.name, accepted_responses=result['accepted_responses'],
        weekly_orders=len(weekly_orders), probe_pairs=len(tables['probes']), replayed_states=len(tables['rounds']),
        report=str(output/'REPORT.md'), package=str(destination)), indent=2))
    print(overall[['hypothesis', 'mean_difference', 'direction']].to_string(index=False))
    return result


if __name__ == '__main__':
    publish()
