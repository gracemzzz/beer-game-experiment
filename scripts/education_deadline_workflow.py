"""Prepare, import and report the separate 10s/60s + education study, offline."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study import education_deadline_cohort as study

OUTPUT = ROOT/'reports/EDUCATION_DEADLINE_10S_60S'
PREFLIGHT = ROOT/'data/development/education_deadline_preflight_20261019'


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def prepare(output=OUTPUT):
    output = Path(output)
    website = study.prepare(study.Config())
    pilot = study.prepare(study.Config(students=16, seed=2026101902,
        label='fixed-small-assistant-preflight', collection='isolated_assistant',
        model_label='current-assistant-inherited', effort_label='inherited'))
    capacity = study.prepare(study.Config(repetitions=1, seed=2026101903,
        label='single-full-cohort-capacity-check', collection='isolated_assistant',
        model_label='current-assistant-inherited', effort_label='inherited'))
    index = dict(date='2026-10-19', protocol=study.PROTOCOL,
        website_run=relative(website), pilot_run=relative(pilot), capacity_run=relative(capacity),
        website_tasks=6, fictional_identities_per_case=500, independent_human_observations=0,
        pilot_collection_slots=[t['task_id'] for t in study.read(pilot/'plan.json')['tasks']],
        capacity_collection_slots=[study.read(capacity/'plan.json')['tasks'][0]['task_id']],
        paid_api_calls=0, inference='Descriptive; no significance guarantee or student-level p-values.')
    study.save_new(output/'PLAN_INDEX.json', index)
    study.save_new(ROOT/'reports/LATEST_EDUCATION_DEADLINE_PLAN.json',
        dict(index=relative(output/'PLAN_INDEX.json'), website_run=relative(website),
             start_here=relative(output/'START_HERE.md')))
    tasks = study.read(website/'plan.json')['tasks']
    task_table = '\n'.join(f"| {i} | `{task['task_id']}` | {task['deadline_seconds']} s | {task['lecture_id']} | [Prompt](prompts/{task['task_id']}.txt) |"
                           for i, task in enumerate(tasks, 1))
    start = f'''# New 10-second / 60-second Beer Game prompts

This is a separate prepared study. The completed report remains in `reports/CURRENT_BEER_GAME/`.

Each prompt covers **all 500 fictional identities in 125 chains**. Three cases cover H1-H4: 60s/control, 10s/control, and 10s/causal education. Two independent generations mean **six fresh chats**, rather than twenty. The same identities are matched across cases; they are not additional people. There are 60,000 submitted weekly orders across six complete replies.

1. Open a fresh chat with the same user-reported **GPT-6 / Pro** selection for each task. Check that the selected chat can produce downloadable files; availability on your exact selection is unverified.
2. Copy the entire task text below. Alternatively, attach its `.txt` file and say: "Read the attached task file as my request and complete that one task. Return the complete downloadable JSON file."
3. Download the complete response JSON. Name it after the task, such as `r01_a60_control.json`. If tools were used, also save the serialization source or transcript. The model should choose the explicit orders; code should track physical state or save them, rather than invent missing decisions using a policy.
4. Repeat with the next task in a fresh chat, without earlier responses. Keep failures and incomplete files too. Do not ask for a better effect or replace an unfavorable result.
5. Return the six files here together, or put them in one folder/ZIP. I can import and report them together; no manual extraction of individual chains is needed. Downloadable delivery avoids copying long answer text, but does not guarantee completion.

| Order | Task | Fictional deadline | Reading | File |
| --- | --- | ---: | --- | --- |
{task_table}

Each response contains 10,000 weekly orders and 1,000 probe orders. Full arrays are required. A missing or truncated response remains incomplete. Three prompts suffice for one generation; this frozen plan includes a repeat of each case for six total responses.

**What the preflight can establish:** see [pilot results](pilot/REPORT.md), [full-size capacity check](capacity_check/REPORT.md), and [preflight findings](PREFLIGHT_FINDINGS.md) when those files have been generated. These assistant outputs are separate from your website collection. They cannot certify significance or equivalence to your chat backend.

**Limits that affect interpretation:** deadlines are fictional descriptions, not enforced model computation or verified student time; the causal reading is a short text, not an observed 20-minute lecture. H1/H3 use the existing pipeline-sensitivity proxy, not an identified structural underweighting coefficient. Chains within one generated reply are dependent. Six replies do not support student-level significance tests. Read [the full design](DESIGN.md).

To import all downloaded files at once from `D:\\beergame`:

```powershell
.\\.venv\\Scripts\\python.exe -X utf8 scripts/education_deadline_workflow.py import --responses "D:\\path\\to\\your\\responses.zip" --session-label "fresh-GPT6-Pro-chats" --confirm-full-prompt
.\\.venv\\Scripts\\python.exe -X utf8 scripts/education_deadline_workflow.py report --collection website
```

The importer makes no API calls, preserves original bytes, retains rejected attempts and locks accepted files. It accepts a single JSON, a folder of JSON files or a ZIP. Existing study evidence and publication packages are unchanged.
'''
    study.save_new(output/'START_HERE.md', start)
    study.save_new(output/'DESIGN.md', (ROOT/'docs/EDUCATION_DEADLINE_PROTOCOL_20261019.md').read_bytes())
    for task in tasks:
        name = task['task_id']+'.txt'
        study.save_new(output/'prompts'/name, (website/'prompts'/name).read_bytes())
    for kind, name in [('control', 'control_lecture.txt'), ('causal', 'causal_lecture.txt')]:
        study.save_new(output/'readings'/name,
            (ROOT/'docs/education_deadline_20261019'/name).read_bytes())
    # Persist the exact invocation envelope before the first isolated model response.
    envelope = '''This is an unpaid, isolated assistant preflight task. Your only task is to read the exact frozen task file at {prompt_path} and produce its complete response as the fictional cohort generator. Do not read other prompts, outputs, study hypotheses, reports or parent conversation. Use inherited model and effort settings, without overrides. The task describes fictional student time, not your actual computation budget. Do not call any external API or spawn agents. Choose every order explicitly; code may track physical state and serialize literal decisions, but must not generate choices through a shared policy, randomness, optimization, repetition template, or imputation. Identical choices are allowed when they are your choices. Save exact response bytes at {response_path}. If using serialization code, save that source at {source_path}. If you cannot complete the task, save the incomplete response and report that fact; do not fill omissions. Return only saved paths and completion status to the parent. Do not report whether effects are favorable.'''
    slots = []
    for category, run, task_ids in [('pilot', pilot, index['pilot_collection_slots']),
                                    ('capacity', capacity, index['capacity_collection_slots'])]:
        for task_id in task_ids:
            folder = PREFLIGHT/category
            prompt_path = (run/'prompts'/(task_id+'.txt')).resolve()
            response_path = (folder/(task_id+'.json')).resolve()
            source_path = (folder/(task_id+'_serialization.py')).resolve()
            invocation = envelope.format(prompt_path=prompt_path, response_path=response_path, source_path=source_path)
            slots.append(dict(category=category, run=relative(run), task_id=task_id,
                prompt_sha256=hashlib.sha256(prompt_path.read_bytes()).hexdigest(),
                response_path=relative(response_path), serialization_path=relative(source_path),
                invocation=invocation, fork_turns='none', model_override=None, effort_override=None))
    study.save_new(PREFLIGHT/'PLAN.json', dict(index=index, slots=slots,
        stopping='Exactly six small-cohort responses plus the first full-cohort case; no favorable-effect gate or further trials.',
        independence='Fresh isolated assistant contexts; inherited backend, not verified equivalent to website GPT-6 / Pro.'))
    package_files = [output/'START_HERE.md', output/'DESIGN.md', output/'PLAN_INDEX.json']
    package_files += sorted((output/'prompts').glob('*.txt'))+sorted((output/'readings').glob('*.txt'))
    buffer = io.BytesIO()
    with ZipFile(buffer, 'w', compression=ZIP_DEFLATED) as archive:
        for path in package_files:
            info = ZipInfo(path.relative_to(output).as_posix(), date_time=(2026, 10, 19, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    study.save_new(output/'Beer_Game_10s_60s_Prompts.zip', buffer.getvalue())
    return index


def response_files(path):
    path = Path(path)
    if path.is_dir():
        return [(p.name, p.read_bytes()) for p in sorted(path.glob('*.json'))]
    if path.suffix.lower() == '.zip':
        with ZipFile(path) as archive:
            return [(Path(info.filename).name, archive.read(info)) for info in archive.infolist()
                    if not info.is_dir() and info.filename.lower().endswith('.json')]
    return [(path.name, path.read_bytes())]


def import_files(run, response_path, *, session_label, confirm_full_prompt):
    run = Path(run)
    manifest = study.audit(run)
    if confirm_full_prompt is not True or not isinstance(session_label, str) or not session_label.strip():
        raise ValueError('Confirm the full frozen prompt and record a session label before importing.')
    config = manifest['config']
    expected = {t['task_id'] for t in study.read(run/'plan.json')['tasks']}
    original = Path(response_path)
    if original.is_file() and original.suffix.lower() == '.zip':
        data = original.read_bytes()
        study.save_new(run/'submissions'/(hashlib.sha256(data).hexdigest()+'.zip'), data)
    entries = []
    seen = set()
    for filename, data in response_files(original):
        # Preserve every incoming reply before parsing or checking an occupied slot.
        # A protocol failure is still evidence, including duplicate/replacement attempts.
        incoming_hash = hashlib.sha256(data).hexdigest()
        study.save_new(run/'submissions'/(incoming_hash+'.json'), data)
        # Determine which immutable slot to use; no payload repair or code execution.
        try:
            obj = study.parse_response(data.decode('utf-8'))
            task_id = obj.get('task_id')
        except (ValueError, UnicodeDecodeError, AttributeError):
            task_id = None
        if not isinstance(task_id, str) or task_id not in expected:
            task_id = Path(filename).stem
        if task_id not in expected:
            study.save_new(run/'unassigned_submissions'/(hashlib.sha256(data).hexdigest()+'.txt'), data)
            raise ValueError('Cannot identify task for '+filename+'; original retained in unassigned_submissions.')
        if task_id in seen:
            raise ValueError('Duplicate task in submitted batch: '+task_id)
        seen.add(task_id)
        locked = study.accepted_path(run, task_id)
        if locked.exists():
            existing = study.load_accepted(run, task_id)
            if hashlib.sha256(data).hexdigest() != existing['raw_sha256']:
                raise ValueError('A different reply already occupies '+task_id)
            entries.append(dict(task_id=task_id, status='already_accepted_identical'))
            continue
        with tempfile.TemporaryDirectory(prefix='beer-response-') as temporary:
            source = Path(temporary)/filename
            source.write_bytes(data)
            entry = study.import_response(run, task_id, source,
                model_label=config['model_label'], effort_label=config['effort_label'],
                session_label=session_label+'-'+task_id, confirm_full_prompt=confirm_full_prompt,
                evidence_kind='synthetic_test' if config['synthetic'] else 'model_output')
            entries.append(dict(task_id=task_id, status=entry['status']))
    if not entries:
        raise ValueError('No JSON response files found.')
    return entries


def report(run, output):
    from beergame_study.education_deadline_report import build_report
    output = Path(output)
    # Archive an earlier generated publication before replacing it with new evidence.
    if (output/'REPORT.md').exists():
        evidence = {path.relative_to(run).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in sorted(Path(run).rglob('*'))
                    if path.is_file() and 'inbox' not in path.relative_to(run).parts}
        previous = study.read(output/'provenance.json')
        implementation = Path(sys.modules[build_report.__module__].__file__)
        if (previous['analysis_signature'] == study.digest(evidence)[:16] and
                previous['report_implementation_sha256'] == hashlib.sha256(implementation.read_bytes()).hexdigest()):
            checked = build_report(run, output)
            checked['unchanged'] = True
            return checked
        archive_id = hashlib.sha256((output/'REPORT.md').read_bytes()).hexdigest()[:12]
        archive = ROOT/'reports/archive/education_deadline_20261019'/output.name/archive_id
        if not archive.exists():
            resolved = output.resolve()
            if not resolved.is_relative_to(OUTPUT.resolve()):
                raise ValueError('Report replacement must stay within the named study folder.')
            if not archive.resolve().is_relative_to((ROOT/'reports/archive/education_deadline_20261019').resolve()):
                raise ValueError('Report archive destination leaves the intended archive folder.')
            archive.parent.mkdir(parents=True, exist_ok=True)
            output.rename(archive)
        else:
            raise ValueError('Existing report archive collision; preserve both outputs for review.')
    return build_report(run, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('prepare')
    importer = commands.add_parser('import')
    importer.add_argument('--responses', type=Path, required=True)
    importer.add_argument('--run', type=Path)
    importer.add_argument('--session-label', required=True)
    importer.add_argument('--confirm-full-prompt', action='store_true')
    reporter = commands.add_parser('report')
    reporter.add_argument('--collection', choices=['website', 'pilot', 'capacity'], default='website')
    args = parser.parse_args()
    if args.command == 'prepare':
        print(json.dumps(prepare(), indent=2))
        return
    index = study.read(OUTPUT/'PLAN_INDEX.json')
    if args.command == 'import':
        run = args.run or ROOT/index['website_run']
        print(json.dumps(import_files(run, args.responses, session_label=args.session_label,
                                     confirm_full_prompt=args.confirm_full_prompt), indent=2))
    elif args.command == 'report':
        folder = 'capacity_check' if args.collection == 'capacity' else args.collection
        result = report(ROOT/index[args.collection+'_run'], OUTPUT/folder)
        print(json.dumps({key: str(result[key]) if isinstance(result[key], Path) else result[key]
                          for key in ('report', 'accepted_responses', 'analysis_signature', 'unchanged')
                          if key in result}, indent=2))


if __name__ == '__main__':
    main()
