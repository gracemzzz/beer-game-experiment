"""Package a completed deadline study for readers; preserve the scientific evidence."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from beergame_study.deadline_cohort import audit, load_accepted, progress, read, save_new
from beergame_study.game import ROLES


FIGURES = [
    ('hypothesis_levels', 'H1, H2 and H3', 'Lines join the same team and generation across deadlines; black diamonds show means.'),
    ('effect_and_repeat_variation', 'Deadline differences versus ordinary repeat variation', 'Absolute differences have no direction. Black diamonds show means, not significance tests.'),
    ('bullwhip_by_role', 'Bullwhip by supply-chain role', 'A ratio above 1 means orders vary more than customer demand.'),
    ('cost_phases', 'Where costs come from', 'Practice and automatic continuation are scoring-rule actions; only the model phase contains submitted decisions.'),
    ('example_chain', 'One team across both deadlines and rounds', 'This is the first team in the fixed plan, not an example selected for its results.'),
    ('all_orders', 'Every submitted weekly order', 'Each row is a role trajectory; the two panels use the same color scale.'),
]
TABLES = ['hypotheses', 'batches', 'chains', 'roles', 'contrasts', 'repeat_variation',
          'choice_changes', 'quality', 'probes', 'rounds']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--analysis', required=True)
    parser.add_argument('--label', default='final', help='Use a new label to version a changed publication package.')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{12}', args.analysis):
        raise ValueError('Specify the saved 12-character analysis signature.')
    if not re.fullmatch(r'final(?:_[A-Za-z0-9-]+)?', args.label):
        raise ValueError('Use final or a version label such as final_v2.')
    run = args.run.resolve()
    if run.name != 'deadline_cohort_2800524c9b2e0729' or args.analysis != 'daa53a7e838a':
        raise ValueError('This publication package is pinned to the completed 18 October website study.')
    root = run.parents[2]
    manifest = audit(run)
    plan = read(run / 'plan.json')
    if not progress(run).accepted.all():
        raise ValueError('This final package requires a complete collection.')
    report_folder = root / 'reports' / run.name
    source = report_folder / 'analysis' / args.analysis
    provenance = read(source / 'provenance.json')
    current = {p.relative_to(run).as_posix(): sha(p.read_bytes())
               for p in run.rglob('*') if p.is_file() and 'inbox' not in p.parts}
    assert provenance['inputs_sha256'] == current
    assert provenance['imported_responses'] == plan['expected_responses']
    target = report_folder / args.label
    files = {}
    source_hashes = {}

    def put(name, data):
        raw = data.encode('utf-8') if isinstance(data, str) else data
        save_new(target / name, raw)
        files[name] = sha(raw)

    def copy(name, path):
        raw = path.read_bytes()
        put(name, raw)
        source_hashes[path.relative_to(root).as_posix()] = sha(raw)

    for name in TABLES:
        copy('results/' + name + '.csv', source / (name + '.csv'))
    copy('results/RESULTS.xlsx', source / 'RESULTS.xlsx')
    for name, _, _ in FIGURES:
        for ext in ('png', 'pdf'):
            copy(f'plots/{name}.{ext}', source / f'{name}.{ext}')

    # Explicitly separate model-submitted orders from the 32,000 scoring-rule rows.
    rounds = pd.read_csv(source / 'rounds.csv')
    columns = ['task_id', 'batch_id', 'generation', 'condition', 'chain_id', 'role',
               'profile_id', 'week', 'order', 'customer_demand']
    orders = rounds.loc[rounds.phase == 'model', columns].copy()
    orders.insert(4, 'deadline_seconds', orders.condition.map({'brief': 10, 'ample': 180}))
    orders.insert(6, 'fictional_student_id', orders.chain_id + '_' + orders.role)
    order_keys = ['task_id', 'chain_id', 'week', 'role']
    orders = orders.sort_values(order_keys).reset_index(drop=True)
    assert not orders.duplicated(order_keys).any()
    expected = []
    metadata = []
    prompt_blocks = []
    prompt_index = []
    for index, task in enumerate(plan['tasks'], start=1):
        tid = task['task_id']
        entry = load_accepted(run, tid)
        raw_prompt = (run / 'prompts' / (tid + '.txt')).read_bytes()
        assert sha(raw_prompt) == entry['prompt_sha256']
        prompt = raw_prompt.decode('utf-8')
        assert prompt.endswith('\n') and '```' not in prompt
        seconds = 10 if task['condition'] == 'brief' else 180
        heading = f"{index:02d}. {tid}"
        prompt_index.append(f"| {index} | `{tid}` | {task['generation']} | {seconds} seconds |\n")
        prompt_blocks.append(f"## {heading}\n\nBatch {task['batch_id']}; round {task['generation']}; {seconds}-second scenario. Generates 25 teams' weekly orders and matched-state answers.\n\n```text\n" + prompt + '```\n\n')
        metadata.append(dict(study_id=run.name, task_id=tid, batch_id=task['batch_id'],
            generation=task['generation'], condition=task['condition'], deadline_seconds=seconds,
            model_label=entry['model_label'], reasoning_mode_label=entry['effort_label'],
            settings_source='user-reported UI; not independently verified',
            prompt_sha256=entry['prompt_sha256'], response_sha256=entry['raw_sha256'],
            raw_response_repository_path=(run / entry['raw_path']).relative_to(root).as_posix(),
            received_utc=entry['received_utc']))
        for chain in entry['payload']['chains']:
            for week, quantities in enumerate(chain['orders'], start=5):
                for role, quantity in zip(ROLES, quantities):
                    expected.append(dict(task_id=tid, chain_id=chain['chain_id'], week=week, role=role, order=quantity))
    expected = pd.DataFrame(expected).set_index(order_keys).sort_index()
    pd.testing.assert_frame_equal(orders.set_index(order_keys)[['order']].sort_index(), expected)
    put('results/weekly_orders.csv', orders.to_csv(index=False))
    put('results/task_provenance.csv', pd.DataFrame(metadata).to_csv(index=False))

    prompts = ('# Exact collection prompts\n\n'
        'All 20 frozen prompts, in planned collection order. Each box contains the complete prompt text, including the assigned profiles, demand paths and output schema. No text inside a box has been summarized or changed.\n\n'
        '**Recorded model/mode:** GPT-6 / Pro, as reported by the user. These were manual website chats, not API calls. Actual backend, mode, full-prompt submission and fresh-chat execution were not independently verified. Prompt hashes match the accepted-response records.\n\n'
        'Rounds 1 and 2 repeat the same assignments in separate chats; neither prompt contains previous answers. Brief means 10 seconds and ample means 180 seconds in the fictional student scenario. These are not measured model deadlines.\n\n'
        '| Order | Task | Round | Scenario |\n| ---: | --- | ---: | --- |\n'
        + ''.join(prompt_index) + '\n' + ''.join(prompt_blocks))
    put('EXACT_PROMPTS.md', prompts)
    extracted = re.findall(r'```text\n(.*?)```', prompts, flags=re.S)
    assert len(extracted) == len(metadata)
    for text, meta in zip(extracted, metadata):
        assert sha(text.encode('utf-8')) == meta['prompt_sha256']

    findings_path = report_folder / 'FINDINGS.md'
    findings = findings_path.read_text(encoding='utf-8').split('[Full report with six plots]')[0].rstrip()
    findings = findings.replace('# Completed Beer Game study: what we found', '# Beer Game deadline study — final report', 1)
    source_hashes[findings_path.relative_to(root).as_posix()] = sha(findings_path.read_bytes())
    findings += '\n\n## Plots\n\nAll six figures are copied without alteration from the completed analysis. Dots and repeated trajectories are generated observations, not independent human samples.\n\n'
    for i, (name, title, caption) in enumerate(FIGURES, start=1):
        findings += f'### {i}. {title}\n\n{caption}\n\n![{title}](plots/{name}.png)\n\n[Download PDF](plots/{name}.pdf).\n\n'
    findings += '[Exact prompts](EXACT_PROMPTS.md) · [Extracted results and field guide](results/README.md) · [Excel workbook](results/RESULTS.xlsx).\n'
    put('REPORT.md', findings)

    put('README.md', '''# Beer Game deadline study — final package

**Completed 18 October 2026.** 20 responses, 500 fictional identities, 40,000 submitted weekly orders. Recorded model/mode: user-reported GPT-6 / Pro.

| What you need | Open this |
| --- | --- |
| Report and all six plots | [REPORT.md](REPORT.md) |
| Every exact prompt, one box per task | [EXACT_PROMPTS.md](EXACT_PROMPTS.md) |
| Extracted results and column meanings | [results/README.md](results/README.md) |
| Excel results | [RESULTS.xlsx](results/RESULTS.xlsx) |
| Only the model's weekly orders | [weekly_orders.csv](results/weekly_orders.csv) |

**Main finding:** H1 points in its predicted direction in both rounds. H2 points the other way. H3 changes direction between rounds and is opposite overall. Same-deadline repeats vary substantially. These are descriptive model-generated scenarios; fictional deadlines are not enforced thinking time and the personas were not validated against real students.

The report displays all six plots. Their PNG and PDF files are in `plots/`. Exact prompts include all profiles, demand paths and the output format. Results retain all valid decisions, including zero orders.

The package can be read without Python or an API key. Extract the entire ZIP together so report images and links work. In the original repository, `notebooks/07_deadline_cohort_rerun.ipynb` provides 125 interactive team charts: run sections 1–4, then 7–8.

Source run: `deadline_cohort_2800524c9b2e0729`; analysis: `daa53a7e838a`. Original JSON replies and scientific source snapshots remain under `data/runs/` in the repository. [Provenance and file hashes](results/provenance.json) identify the package's sources. No new responses, analysis rules or API calls were added by packaging.
''')
    put('results/README.md', '''# Extracted results

Start with **[RESULTS.xlsx](RESULTS.xlsx)** for the ten original analysis sheets, or **[weekly_orders.csv](weekly_orders.csv)** for just the 40,000 model-submitted decisions. CSVs open in Excel, Python or R. CSV copies of the original tables and the workbook are byte-identical to the completed analysis.

| File / Excel sheet | Rows | Meaning |
| --- | ---: | --- |
| `weekly_orders.csv` (CSV only) | 40,000 | One submitted order per task, team, role and week; excludes practice/continuation |
| `hypotheses` | 3 | Overall H1/H2/H3 means and brief-minus-ample differences |
| `batches` | 10 | One paired comparison per batch and round |
| `chains` | 500 | Team outcomes for each condition and round |
| `roles` | 2,000 | Role outcomes for each condition and round |
| `contrasts` | 250 | Matched team/round differences between deadlines |
| `repeat_variation` | 250 | Round 1 minus round 2 under the same deadline |
| `choice_changes` | 20 | Counts and magnitudes of changed orders |
| `quality` | 4 | Order counts, zeros, largest orders and distinct paths |
| `probes` | 2,000 | Matched-state order pairs used for H1 |
| `rounds` | 72,000 | Python-replayed states for model, practice and automatic weeks |
| `task_provenance.csv` (CSV only) | 20 | Task, reported settings, source paths and prompt/response hashes |

## Main columns

- `task_id`: identifies one complete model reply. `b0001_g02_ample` means batch 1, second generation, 180-second scenario.
- `condition`: `brief` = 10 seconds; `ample` = 180 seconds. `generation` means repeated round 1 or 2.
- `chain_id`: one four-role team. `role`: retailer, wholesaler, distributor or factory. `profile_id`: assigned fictional personality.
- `fictional_student_id`: an export label formed from team + role; it identifies the same fictional identity across deadlines and rounds, not a real person.
- `week`: submitted choices cover weeks 5–24. `order`: the model's integer order. `customer_demand`: the supplied customer-demand path, not a generated student response.
- `phase` in `rounds`: `practice` = weeks 1–4; `model` = weeks 5–24; `automatic` = weeks 25–36. Only `model` orders were generated. Inventory, backlog, shipments and cost were calculated by Python.
- `sensitivity`: H1 = (probe order with 8 dispatched cases minus order with 32) / 24. `bullwhip`: H3 = sample variance of orders / sample variance of customer demand.
- `cost`: H2 full scored team/role cost. `model_cost` and `automatic_cost` separate the two main scoring phases; `practice_cost` is also included in the total.
- Deadline contrasts are **brief minus ample**. Same-deadline repeat contrasts are **round 1 minus round 2**. Do not mix them.

Blank p-value/interval cells mean inference was deliberately withheld, not zero. Repeated trajectories and rows within a generated batch are not independent human observations. Raw accepted JSONs remain in the repository; `task_provenance.csv` points to their preserved original text. [File hashes and provenance](provenance.json).
''')

    package_manifest = dict(package_version=1, study_id=run.name, analysis_signature=args.analysis,
        model_label=manifest['config']['model_label'], mode_label=manifest['config']['effort_label'],
        setting_verification='user-reported UI only', accepted_responses=len(metadata),
        fictional_identities=plan['fictional_identities'], model_orders=len(orders),
        source_artifacts_sha256=source_hashes, raw_run_inputs_sha256=current,
        packaged_files_sha256=files.copy(), api_calls=0)
    put('results/provenance.json', json.dumps(package_manifest, indent=2, allow_nan=False) + '\n')
    for name, digest in files.items():
        assert sha((target / name).read_bytes()) == digest
    for path in target.rglob('*.md'):
        content = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
        for link in re.findall(r'\]\(([^)]+)\)', content):
            assert (path.parent / link).exists(), (path, link)

    # Deterministic ZIP; rerunning may only reproduce identical files.
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo('Beer_Game_Deadline_20261018/' + name, (2026, 10, 18, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (target / name).read_bytes())
    zipped = output.getvalue()
    suffix = '' if args.label == 'final' else '_' + args.label
    zip_path = report_folder / ('Beer_Game_Deadline_20261018' + suffix + '.zip')
    save_new(zip_path, zipped)
    with zipfile.ZipFile(io.BytesIO(zipped)) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(files)
        for name, digest in files.items():
            assert sha(archive.read('Beer_Game_Deadline_20261018/' + name)) == digest
    audit(run)
    after = {p.relative_to(run).as_posix(): sha(p.read_bytes())
             for p in run.rglob('*') if p.is_file() and 'inbox' not in p.parts}
    assert after == current
    checks = dict(status='passed', package=str(target), zip=str(zip_path), zip_sha256=sha(zipped),
        exact_prompt_boxes=len(extracted), direct_raw_orders_checked=len(expected),
        workbook_sheets=len(pd.ExcelFile(target / 'results/RESULTS.xlsx').sheet_names),
        figure_pairs=len(FIGURES), packaged_files=len(files), raw_files_unchanged=len(current),
        links='passed', archive_contents='passed', api_calls=0)
    (root / 'reports/software_checks' / (run.name + '_package.json')).write_text(
        json.dumps(checks, indent=2), encoding='utf-8')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
