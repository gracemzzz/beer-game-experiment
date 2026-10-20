"""Audit the saved Astra education/deadline collection without generating data.

Recompute queueing arithmetic using the separate test implementation, compare
published tables with exact imported choices, and verify immutable provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'tests'))
from beergame_study import education_deadline_cohort as scientific
from beergame_study import education_deadline_collection as collection
from test_education_deadline_cohort import independent_physical_replay


DATE = '2026-10-20'
POINTER = ROOT/'reports/LATEST_EDUCATION_DEADLINE_COLLECTION.json'
INTAKE = ROOT/'data/submissions/education_deadline_astra_20261020/INTAKE.json'
BASELINE = ROOT/'reports/software_checks/education_deadline_astra_before_20261020.json'
DESTINATION = ROOT/'reports/software_checks/education_deadline_astra_20261020.json'
STATE_FIELDS = ('inventory', 'backlog', 'received', 'demand', 'shipped', 'supply_line', 'cost')
PHASES = ('practice', 'model', 'automatic')


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inside(base, relative):
    _assert(isinstance(relative, str) and bool(relative), 'Invalid relative evidence path.')
    path = (Path(base)/relative).resolve()
    _assert(path.is_relative_to(Path(base).resolve()), 'Evidence path escapes its intended directory: '+relative)
    return path


def _same_numbers(observed, expected, context):
    np.testing.assert_allclose(np.asarray(observed, dtype=float), np.asarray(expected, dtype=float),
                               rtol=0, atol=1e-10, equal_nan=True, err_msg=context)


def _table_equal(observed, expected, keys, context):
    _assert(set(observed.columns) == set(expected.columns), context+': table columns differ.')
    _assert(not observed.duplicated(keys).any() and not expected.duplicated(keys).any(),
            context+': duplicate comparison keys.')
    columns = sorted(expected.columns)
    left = observed.sort_values(keys).reset_index(drop=True)[columns]
    right = expected.sort_values(keys).reset_index(drop=True)[columns]
    # CSV retains nested display dictionaries as their literal text; compare the
    # same serialization without evaluating any returned text as Python code.
    for column in columns:
        if right[column].map(lambda value: isinstance(value, (dict, list, tuple))).any():
            left[column] = left[column].map(str)
            right[column] = right[column].map(str)
    pd.testing.assert_frame_equal(left, right, check_dtype=False, check_exact=False,
                                  rtol=0, atol=1e-10, obj=context)


def independent_metrics(plan, config, payloads, rounds):
    """Check every actual state and derive costs/probe scores independently.

    The independent queue implementation does not call BeerGame. Vectorized
    per-chain comparison avoids repeatedly scanning the full round table.
    """
    roles = tuple(scientific.ROLES)
    role_index = {role: index for index, role in enumerate(roles)}
    groups = dict(tuple(rounds.groupby(['task_id', 'chain_id'], sort=False)))
    specs = {chain['chain_id']: chain for chain in plan['chains']}
    task_specs = {task['task_id']: task for task in plan['tasks']}
    chain_rows, role_rows, probe_rows = [], [], []
    verified, explicit_choices = 0, 0
    weeks = config['weeks']
    for task_id, payload in payloads.items():
        task = task_specs[task_id]
        for choice in payload['chains']:
            chain_id = choice['chain_id']
            spec = specs[chain_id]
            expected = independent_physical_replay(spec['customer_demand'], choice['orders'], weeks)
            expected_frame = pd.DataFrame(expected)
            own = groups.pop((task_id, chain_id))
            own = own.assign(_role_index=own.role.map(role_index)).sort_values(['week', '_role_index'])
            _assert(len(own) == len(expected_frame), f'Independent state count: {task_id}/{chain_id}')
            _same_numbers(own[list(STATE_FIELDS)].to_numpy(), expected_frame[list(STATE_FIELDS)].to_numpy(),
                          f'Independent physical replay: {task_id}/{chain_id}')
            _same_numbers(own.week.to_numpy(), expected_frame.week.to_numpy(), 'Independent week ordering')
            _same_numbers(own._role_index.to_numpy(), expected_frame.role.to_numpy(), 'Independent role ordering')
            phase = np.where(expected_frame.week.to_numpy() <= 4, 'practice',
                             np.where(expected_frame.week.to_numpy() <= weeks, 'model', 'automatic'))
            _assert(np.array_equal(own.phase.to_numpy(), phase), 'Scoring phase assignment differs.')
            literal_orders = np.asarray([[4]*4]*4+choice['orders']+[choice['orders'][-1]]*12).reshape(-1)
            _same_numbers(own.order.to_numpy(), literal_orders, f'Explicit submitted/practice/automatic orders: {task_id}/{chain_id}')
            explicit_choices += len(choice['orders'])*4
            verified += len(expected_frame)
            common = dict(task_id=task_id, repetition=task['repetition'], arm=task['arm'], chain_id=chain_id)
            scores = []
            for index, role in enumerate(roles):
                mask = expected_frame.role.to_numpy() == index
                costs = {f'cost_{name}': float(expected_frame.loc[mask & (phase == name), 'cost'].sum())
                         for name in PHASES}
                costs['total_cost'] = sum(costs.values())
                low, high = choice['probes'][index]
                score = (low-high)/24
                scores.append(score)
                probe_rows.append(common | dict(role=role, low_order=low, high_order=high, sensitivity=score))
                role_rows.append(common | dict(role=role, **costs, sensitivity=score))
            costs = {f'cost_{name}': float(expected_frame.loc[phase == name, 'cost'].sum()) for name in PHASES}
            costs['total_cost'] = sum(costs.values())
            chain_rows.append(common | costs | dict(sensitivity=float(np.mean(scores))))
    _assert(not groups, 'Round data contains chains not present in exact original payloads.')
    return dict(chains=pd.DataFrame(chain_rows), roles=pd.DataFrame(role_rows),
                probes=pd.DataFrame(probe_rows), independently_recomputed_states=verified,
                original_model_week_orders_checked=explicit_choices)


def _compare_direct_tables(direct, saved, report):
    checks = {}
    for name, keys in [('chains', ['task_id', 'chain_id']),
                       ('roles', ['task_id', 'chain_id', 'role']),
                       ('probes', ['task_id', 'chain_id', 'role'])]:
        expected = direct[name]
        for label, observed in [('in-memory', saved[name]),
                                ('published CSV', pd.read_csv(report/'results'/(name+'.csv')))]:
            _table_equal(observed[list(expected.columns)], expected, keys, 'Independent '+name+' / '+label)
        checks[name] = len(expected)
    metrics = direct['chains'].set_index(['arm', 'repetition', 'chain_id'])
    expected_contrasts = []
    for hypothesis, (reference, treatment, metric, sign) in scientific.CONTRASTS.items():
        reference_rows = metrics.loc[reference]
        treatment_rows = metrics.loc[treatment]
        _assert(set(reference_rows.index) == set(treatment_rows.index), 'Unmatched direct hypothesis cases.')
        for repetition, chain_id in reference_rows.index:
            expected_contrasts.append(dict(hypothesis=hypothesis, repetition=int(repetition), chain_id=chain_id,
                metric=metric, reference_arm=reference, treatment_arm=treatment,
                estimate=float(treatment_rows.loc[(repetition, chain_id), metric]-
                               reference_rows.loc[(repetition, chain_id), metric]), expected_sign=sign))
    contrasts = pd.DataFrame(expected_contrasts)
    for label, observed in [('in-memory', saved['contrasts']),
                            ('published CSV', pd.read_csv(report/'results/contrasts.csv'))]:
        _table_equal(observed, contrasts, ['hypothesis', 'repetition', 'chain_id'], 'Direct contrasts / '+label)
    summary = pd.read_csv(report/'results/hypothesis_summary.csv', dtype={'repetition': str})
    expected_summary_rows = []
    for hypothesis, own in contrasts.groupby('hypothesis', sort=True):
        for repetition in [*sorted(own.repetition.unique()), 'overall']:
            values = own.estimate if repetition == 'overall' else own.loc[own.repetition == repetition, 'estimate']
            row = summary[(summary.hypothesis == hypothesis) & (summary.repetition == str(repetition))]
            _assert(len(row) == 1, 'Missing/duplicate hypothesis summary.')
            _same_numbers(row.mean_difference.iloc[0], values.mean(), 'Direct hypothesis mean')
            _assert(row.matched_chain_generation_pairs.iloc[0] == len(values), 'Hypothesis matched count differs.')
            expected_summary_rows.append(dict(hypothesis=hypothesis, repetition=str(repetition),
                                              mean_difference=float(values.mean()), matched_pairs=len(values)))
    _assert(len(summary) == len(expected_summary_rows), 'Unexpected hypothesis summary rows.')
    # Preserve every exported state, including orders, before comparing summaries.
    for name, keys in [('rounds', ['task_id', 'chain_id', 'week', 'role'])]:
        exported = pd.read_csv(report/'results'/(name+'.csv'))
        _table_equal(exported, saved[name], keys, 'Every exported '+name+' value')
    weekly = pd.read_csv(report/'results/weekly_orders.csv')
    submitted = saved['rounds'].loc[saved['rounds'].phase == 'model', weekly.columns]
    _table_equal(weekly, submitted, ['task_id', 'chain_id', 'week', 'role'],
                 'Every exported submitted weekly order')
    checks.update(contrasts=len(contrasts), hypothesis_means=expected_summary_rows,
                  exported_round_rows=len(saved['rounds']), exported_model_order_rows=len(weekly))
    return checks


def _verify_package(report):
    candidates = [report/'PACKAGE_MANIFEST.json', report/'package_manifest.json']
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    _assert(path is not None, 'Reader package manifest has not been published.')
    manifest = scientific.read(path)
    files = manifest.get('files', manifest.get('files_sha256'))
    _assert(isinstance(files, dict) and bool(files), 'Package manifest must contain relative file hashes.')
    checked = 0
    for relative, entry in files.items():
        expected = entry.get('sha256') if isinstance(entry, dict) else entry
        target = _inside(report, relative)
        _assert(target != path and target.suffix.lower() != '.zip', 'Package manifest must exclude itself and ZIP.')
        _assert(_sha(target) == expected, 'Published package hash differs: '+relative)
        checked += 1
    package = report/'Beer_Game_Astra_10s_60s_20261020.zip'
    with ZipFile(package) as archive:
        expected_names = set(files) | {path.name}
        _assert(set(archive.namelist()) == expected_names and len(archive.infolist()) == len(expected_names),
                'ZIP has missing, duplicate or unexpected members.')
        for relative in expected_names:
            _assert(archive.read(relative) == _inside(report, relative).read_bytes(),
                    'ZIP member differs from published file: '+relative)
    return dict(manifest=path.name, files_verified=checked, zip_members_verified=len(expected_names),
                zip_sha256=_sha(package))


def check(pointer=POINTER, intake_path=INTAKE, baseline_path=BASELINE):
    index = scientific.read(pointer)
    run = _inside(ROOT, index['collection_run'])
    report = _inside(ROOT, index['report_folder'])
    manifest = collection.audit(run)
    plan = scientific.read(run/'plan.json')
    _assert(manifest['study_id'] == index['collection_id'], 'Pointer collection ID differs.')
    parent_id = manifest['lineage']['parent_study_id']
    _assert(parent_id == index['parent_study_id'], 'Pointer parent study ID differs.')
    _assert(_inside(ROOT, index['report']) == report/'REPORT.md', 'Pointer report path differs.')
    _assert(manifest['config']['model_label'] == 'GPT-6 Astra' and
            manifest['config']['effort_label'] == 'extra high effort' and
            manifest['config']['collection'] == 'user_supplied', 'Reported settings were relabelled.')
    _assert(manifest['planned_config']['model_label'] == 'GPT-6' and
            manifest['planned_config']['effort_label'] == 'pro', 'Planned settings were rewritten.')
    _assert(manifest['config']['synthetic'] is False, 'Actual collection cannot contain synthetic fixtures.')
    for field in ('actual_reasoning_tokens', 'actual_wall_time_s', 'full_prompt_confirmed', 'fresh_chat_confirmed'):
        _assert(manifest[field] is None, 'Unverified collection metadata was marked confirmed: '+field)
    _assert(manifest['api_calls'] == manifest['human_observations'] == 0, 'Unexpected API/human classification.')
    status = collection.progress(run)
    _assert(len(status) == 6 and bool(status.accepted.all()), 'Actual collection is not complete at six fixed tasks.')
    _assert(len(plan['chains']) == 125 and plan['fictional_identities'] == 500 and
            manifest['config']['weeks'] == 24 and manifest['config']['repetitions'] == 2,
            'Prepared cohort dimensions differ.')
    original_parent = Path(manifest['lineage']['original_parent_path'])
    original_status = scientific.progress(original_parent)
    _assert(len(original_status) == 6 and not bool(original_status.accepted.any()),
            'Reported-settings collection was silently accepted into the original GPT-6/pro plan.')
    intake_path = Path(intake_path)
    intake = scientific.read(intake_path)
    _assert(intake['reported_model_label'] == 'GPT-6 Astra' and
            intake['reported_effort_label'] == 'extra high effort' and intake['api_calls'] == 0,
            'Intake literal settings differ.')
    _assert(intake['operator_statement'] == manifest['reported_settings']['operator_statement'],
            'Literal operator statement differs.')
    _assert(len(intake['files']) == 6, 'Expected six original supplied files.')
    payloads, hashes, seen = {}, {}, set()
    for item in intake['files']:
        task_id = item['task_id']
        _assert(task_id not in seen, 'Duplicate original task in intake.')
        seen.add(task_id)
        source = Path(item['source_path'])  # JSON decoding preserves the Unicode path.
        preserved = _inside(intake_path.parent, item['filename'])
        _assert(source.read_bytes() == preserved.read_bytes(), 'Original and preserved response bytes differ.')
        _assert(_sha(source) == _sha(preserved) == item['sha256'], 'Intake response hash differs.')
        _assert(source.stat().st_size == item['bytes'], 'Original response byte count differs.')
        entry = collection.load_accepted(run, task_id)
        raw = _inside(run, entry['raw_path'])
        _assert(raw.read_bytes() == source.read_bytes(), 'Accepted response differs from exact incoming original.')
        _assert(entry['raw_sha256'] == item['sha256'] and entry['formatting_edits'] == [],
                'Unexpected response conversion or hash mismatch.')
        _assert(entry['model_label'] == 'GPT-6 Astra' and entry['effort_label'] == 'extra high effort' and
                entry['planned_model_label'] == 'GPT-6' and entry['planned_effort_label'] == 'pro',
                'Accepted metadata silently substitutes planned settings.')
        for field in ('actual_reasoning_tokens', 'actual_wall_time_s', 'full_prompt_confirmed', 'fresh_chat_confirmed'):
            _assert(entry[field] is None, 'Unverified response metadata was marked confirmed: '+field)
        _assert(entry['api_calls'] == 0 and entry['evidence_kind'] == 'model_output', 'Unexpected evidence classification.')
        payload = entry['payload']
        _assert(payload['study_id'] == parent_id and payload['task_id'] == task_id,
                'Raw payload parent/task identifiers were rewritten.')
        payloads[task_id], hashes[task_id] = payload, item['sha256']
    _assert(seen == {task['task_id'] for task in plan['tasks']}, 'Intake does not cover every planned task.')
    file_map = scientific.read(report/'original_responses/FILE_MAP.json')
    _assert(len(file_map) == 6, 'Reader package lacks the six original response mappings.')
    _assert({(row['filename'], row['task_id'], row['sha256']) for row in file_map} ==
            {(row['filename'], row['task_id'], row['sha256']) for row in intake['files']},
            'Reader package original response mapping differs from intake.')
    for item in intake['files']:
        _assert(_sha(_inside(report/'original_responses', item['filename'])) == item['sha256'],
                'Reader package original response differs from intake.')
    tables = collection.summarize(run)
    direct = independent_metrics(plan, manifest['config'], payloads, tables['rounds'])
    _assert(direct['independently_recomputed_states'] == len(tables['rounds']) == 108000,
            'Actual independent replay must cover 108,000 role-week states.')
    _assert(direct['original_model_week_orders_checked'] == 60000 and len(tables['probes']) == 3000,
            'Actual order/probe totals differ.')
    numerical_checks = _compare_direct_tables(direct, tables, report)
    provenance = scientific.read(report/'provenance.json')
    _assert(provenance['study_id'] == run.name and provenance['accepted_responses'] == 6 and
            provenance['expected_responses'] == 6 and provenance['complete'] is True and
            provenance['api_calls'] == provenance['human_observations'] == 0, 'Report provenance differs.')
    for relative, expected in provenance['inputs_sha256'].items():
        _assert(_sha(_inside(run, relative)) == expected, 'Report input hash differs: '+relative)
    for relative, expected in provenance['outputs_sha256'].items():
        _assert(_sha(_inside(report, relative)) == expected, 'Report output hash differs: '+relative)
    package = _verify_package(report)
    baseline = scientific.read(baseline_path)['files']
    altered = [relative for relative, expected in baseline.items()
               if not _inside(ROOT, relative).exists() or _sha(_inside(ROOT, relative)) != expected]
    _assert(not altered, 'Earlier preserved files changed: '+str(altered[:10]))
    return dict(date=DATE, collection_id=run.name, parent_study_id=parent_id,
                collection_run=run.relative_to(ROOT).as_posix(), report_folder=report.relative_to(ROOT).as_posix(),
                accepted_responses=6, original_parent_accepted_responses=0,
                reported_model_label='GPT-6 Astra', reported_effort_label='extra high effort',
                planned_model_label='GPT-6', planned_effort_label='pro', collection='user_supplied',
                provider_verified=False, full_prompt_confirmed=None, fresh_chat_confirmed=None,
                actual_reasoning_tokens=None, actual_wall_time_s=None,
                original_response_sha256=hashes, original_response_bytes_verified=True,
                submitted_weekly_orders=60000, probe_pairs=3000, scalar_probe_choices=6000,
                independently_recomputed_states=direct['independently_recomputed_states'],
                checked_state_fields=list(STATE_FIELDS), direct_numeric_checks=numerical_checks,
                prior_files_verified_unchanged=len(baseline), publication_package=package,
                report_output_files_verified=len(provenance['outputs_sha256']),
                paid_api_calls=0, human_observations=0, independent_student_p_values=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-tests', action='store_true', help='Only run saved-data/provenance checks.')
    args = parser.parse_args()
    result = check()
    if args.skip_tests:
        result['offline_tests_skipped'] = True
    else:
        tested = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'tests',
                                 '-p', 'test_education_deadline*.py', '-v'], cwd=ROOT,
                                capture_output=True, encoding='utf-8')
        log = ROOT/'reports/logs/education_deadline_astra_20261020/offline_tests.log'
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(tested.stdout+tested.stderr, encoding='utf-8')
        result['offline_tests_exit_code'] = tested.returncode
        result['offline_tests_log'] = log.relative_to(ROOT).as_posix()
        if tested.returncode:
            DESTINATION.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
            print(tested.stdout+tested.stderr)
            raise SystemExit(tested.returncode)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
