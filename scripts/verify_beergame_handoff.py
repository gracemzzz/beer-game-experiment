"""Verify the completed handoff using local saved evidence, without model calls.

Historical absolute paths remain literal provenance.  This operational verifier
maps them to documented copies below --root; it does not rewrite frozen science,
manifests, identifiers or source files, and never reopens the old locations.
By default the receipt is printed to stdout and no existing report is changed.
"""
from __future__ import annotations

import argparse
from datetime import date as calendar_date, datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
POINTER = 'reports/LATEST_EDUCATION_DEADLINE_COLLECTION.json'
INTAKE = 'data/submissions/education_deadline_astra_20261020/INTAKE.json'
BASELINE = 'reports/software_checks/education_deadline_astra_before_20261020.json'
UNKNOWN = ('actual_reasoning_tokens', 'actual_wall_time_s',
           'full_prompt_confirmed', 'fresh_chat_confirmed')


def _assert(condition, message):
    if not condition:
        raise AssertionError(message)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inside(base, relative):
    """Resolve a stored relative path safely on Windows, macOS and Linux."""
    _assert(isinstance(relative, str) and bool(relative) and '\\' not in relative,
            'Invalid relative evidence path: '+repr(relative))
    posix, windows = PurePosixPath(relative), PureWindowsPath(relative)
    _assert(not posix.is_absolute() and not windows.is_absolute() and not windows.drive
            and '..' not in posix.parts, 'Evidence path escapes its intended directory: '+relative)
    base = Path(base).resolve()
    target = (base/relative).resolve()
    _assert(target.is_relative_to(base), 'Evidence path escapes its intended directory: '+relative)
    return target


def _dependencies(root):
    """Import the transferred implementation, with no frozen-global rebinding."""
    for folder in ('src', 'tests', 'scripts'):
        sys.path.insert(0, str(root/folder))
    scientific = importlib.import_module('beergame_study.education_deadline_cohort')
    collection = importlib.import_module('beergame_study.education_deadline_collection')
    checker = importlib.import_module('check_education_deadline_collection')
    for module in (scientific, collection, checker):
        _assert(Path(module.__file__).resolve().is_relative_to(root),
                'An imported implementation comes from outside the requested root: '+module.__name__)
    return scientific, collection, checker


def _verify_accepted(run, parent, manifest, plan, scientific, collection):
    """Check local immutable wrappers, receipts and literal response schema.

    This intentionally does not call collection.audit, load_accepted or parent_run:
    those historical entry points require the machine's original absolute path.
    The strict scientific response validator only receives the verified local
    parent.  Physical replay, when requested, is a separate independent check.
    """
    payloads, hashes = {}, {}
    expected_tasks = {task['task_id'] for task in plan['tasks']}
    _assert(len(expected_tasks) == len(plan['tasks']) == 6, 'Expected six unique fixed slots.')
    accepted = {path.stem for path in (run/'accepted').glob('*.json')}
    _assert(accepted == expected_tasks, 'Accepted collection has missing or unexpected slots.')
    for task_id in sorted(expected_tasks):
        accepted_path = _inside(run, 'accepted/'+task_id+'.json')
        entry = scientific.read(accepted_path)
        common = collection._entry_metadata(run, manifest, task_id)
        keys = tuple(common)+('raw_path', 'raw_sha256', 'source_filename', 'session_label',
                              'evidence_kind', 'full_prompt_confirmed', 'fresh_chat_confirmed',
                              'received_utc', 'status', 'payload')
        scientific._keys(entry, keys, 'Accepted record')
        raw = _inside(run, entry['raw_path'])
        _assert(raw.parent == run/'attempts' and raw.name == task_id+'_001.txt',
                'Completed collection must retain its exact first attempt: '+task_id)
        _assert(raw.with_suffix('.json').read_bytes() == accepted_path.read_bytes(),
                'Accepted record differs from immutable attempt receipt: '+task_id)
        _assert(all(entry[key] == value for key, value in common.items()) and
                entry['status'] == 'accepted' and entry['evidence_kind'] == 'model_output',
                'Accepted provenance metadata differs: '+task_id)
        for field in UNKNOWN:
            _assert(entry[field] is None, 'Unverified response metadata was marked confirmed: '+field)
        for field in ('source_filename', 'session_label', 'received_utc'):
            _assert(isinstance(entry[field], str) and bool(entry[field].strip()),
                    'Missing response metadata: '+field)
        _assert(entry['formatting_edits'] == [] and entry['api_calls'] == 0,
                'Unexpected response conversion or API classification.')
        raw_bytes = raw.read_bytes()
        _assert(_sha(raw) == entry['raw_sha256'], 'Raw response hash differs: '+task_id)
        payload = scientific.validate_response(parent, task_id, raw_bytes.decode('utf-8'))
        _assert(payload == entry['payload'], 'Accepted payload differs from exact raw response: '+task_id)
        _assert(payload['study_id'] == manifest['lineage']['parent_study_id'],
                'Original response parent ID was rewritten: '+task_id)
        payloads[task_id], hashes[task_id] = payload, entry['raw_sha256']
    _assert({path.name for path in (run/'attempts').glob('*') if path.is_file()} ==
            {task+suffix for task in expected_tasks for suffix in ('_001.txt', '_001.json')},
            'Completed collection attempt files differ from its fixed first-attempt sample.')
    return payloads, hashes


def _verify_cost_phases(direct, report, scientific, checker):
    """Recompute every published cost-phase contrast from independent replay."""
    import numpy as np
    import pandas as pd

    expected = []
    chains = direct['chains'].set_index(['arm', 'repetition', 'chain_id'])
    for hypothesis in ('H2', 'H4'):
        reference, treatment, _, _ = scientific.CONTRASTS[hypothesis]
        left, right = chains.loc[reference], chains.loc[treatment]
        _assert(set(left.index) == set(right.index), 'Unmatched cost-phase chains.')
        differences = right[['cost_practice', 'cost_model', 'cost_automatic', 'total_cost']]-left[
            ['cost_practice', 'cost_model', 'cost_automatic', 'total_cost']]
        for repetition in [*sorted(left.index.get_level_values('repetition').unique()), 'overall']:
            values = differences if repetition == 'overall' else differences.loc[[repetition]]
            means = values.mean()
            expected.append(dict(hypothesis=hypothesis, repetition=str(repetition),
                matched_chain_generation_pairs=len(values),
                **{name+'_difference': float(means[name]) for name in means.index},
                automatic_difference_over_total_difference=float(means.cost_automatic/means.total_cost)
                    if means.total_cost else np.nan))
    observed = pd.read_csv(report/'results/cost_contrasts.csv', dtype={'repetition': str})
    checker._table_equal(observed, pd.DataFrame(expected), ['hypothesis', 'repetition'],
                         'Independent phase-specific cost contrasts')
    return len(expected)


def verify(root=ROOT, *, full_replay=True):
    """Return a portable receipt after verifying the completed local collection.

    Calling this API against another checkout starts that checkout's verifier in
    an isolated interpreter, so already-imported modules cannot resolve back to
    the caller's old checkout.  No source/module globals are patched.
    """
    root = Path(root).resolve()
    _assert(type(full_replay) is bool, 'full_replay must be a Boolean.')
    if root != ROOT.resolve():
        script = _inside(root, 'scripts/verify_beergame_handoff.py')
        command = [sys.executable, '-X', 'utf8', str(script), '--root', str(root)]
        if not full_replay:
            command.append('--skip-replay')
        completed = subprocess.run(command, cwd=root, capture_output=True, encoding='utf-8')
        _assert(completed.returncode == 0,
                'Relocated verification failed: '+completed.stderr.strip()+completed.stdout.strip())
        return json.loads(completed.stdout)

    scientific, collection, checker = _dependencies(root)
    index = scientific.read(_inside(root, POINTER))
    run = _inside(root, index['collection_run'])
    report = _inside(root, index['report_folder'])
    manifest = scientific.read(run/'manifest.json')
    identity = collection._identity(manifest)
    _assert(manifest['protocol'] == collection.PROTOCOL and
            manifest['schema_version'] == collection.SCHEMA and
            run.name == collection.PREFIX+collection.digest(identity)[:16] ==
            manifest['study_id'] == index['collection_id'], 'Observed collection fingerprint differs.')
    _assert(manifest['api_calls'] == manifest['human_observations'] == 0,
            'Unexpected API/human classification.')
    for field in UNKNOWN:
        _assert(manifest[field] is None, 'Unverified collection metadata was marked confirmed: '+field)
    planned, actual, reported, lineage = (manifest[key] for key in
                                         ('planned_config', 'config', 'reported_settings', 'lineage'))
    scientific.Config(**planned).validate()
    scientific._keys(reported, ('model_label', 'effort_label', 'operator_statement', 'report_date',
                               'verification', 'reported_after_response_generation', 'collection_interface'),
                     'Reported settings')
    _assert(planned['model_label'] == 'GPT-6' and planned['effort_label'] == 'pro' and
            planned['collection'] == 'chat_ui' and actual == planned | dict(
                model_label='GPT-6 Astra', effort_label='extra high effort', collection='user_supplied') and
            actual['synthetic'] is False, 'Actual/planned settings were relabelled.')
    _assert(reported['model_label'] == 'GPT-6 Astra' and reported['effort_label'] == 'extra high effort' and
            reported['operator_statement'] == collection.REPORTED_STATEMENT and
            calendar_date.fromisoformat(reported['report_date']).isoformat() == reported['report_date'] and
            reported['verification'] == 'user_reported_not_provider_verified' and
            reported['reported_after_response_generation'] is True and
            reported['collection_interface'] is None, 'Reported settings classification differs.')
    _assert(index['reported_model_label'] == reported['model_label'] and
            index['reported_effort_label'] == reported['effort_label'] and
            index['reported_settings_verified'] is False and index['accepted_responses'] == 6 and
            index['paid_api_calls'] == 0, 'Current pointer settings/counts differ.')
    source_hash = manifest['adapter_source_sha256']
    _assert(_sha(Path(collection.__file__)) == source_hash ==
            _sha(run/'source_implementation'/collection.SOURCE_NAME), 'Frozen collection adapter source differs.')
    scientific._keys(lineage, ('parent_study_id', 'original_parent_path', 'snapshot_relative_path',
                               'parent_inputs_sha256'), 'Lineage')
    parent_id = lineage['parent_study_id']
    _assert(isinstance(parent_id, str) and '/' not in parent_id and '\\' not in parent_id and
            parent_id == index['parent_study_id'], 'Parent study ID differs.')
    _assert(isinstance(lineage['original_parent_path'], str) and bool(lineage['original_parent_path']),
            'Original parent provenance string is absent.')
    _assert(lineage['snapshot_relative_path'] == 'prepared_parent/'+parent_id,
            'Prepared-parent snapshot path differs.')
    parent = _inside(root, 'data/runs/'+parent_id)
    snapshot = _inside(run, lineage['snapshot_relative_path'])
    for prepared in (parent, snapshot):
        parent_manifest = scientific.audit(prepared)
        _assert(parent_manifest['study_id'] == parent_id and parent_manifest['config'] == planned and
                parent_manifest['profiles'] == manifest['profiles'] and
                parent_manifest['plan_sha256'] == manifest['plan_sha256'], 'Local parent identity differs.')
        names = {'manifest.json', 'plan.json'} | {'source_implementation/'+name for name in parent_manifest['sources']}
        parent_plan = scientific.read(prepared/'plan.json')
        names |= {'prompts/'+task['task_id']+suffix for task in parent_plan['tasks']
                  for suffix in ('.txt', '.sha256')}
        _assert(set(lineage['parent_inputs_sha256']) == names, 'Prepared-parent hash inventory differs.')
        for relative, expected in lineage['parent_inputs_sha256'].items():
            _assert(_sha(_inside(prepared, relative)) == expected, 'Local parent input hash differs: '+relative)
    _assert((run/'plan.json').read_bytes() == (snapshot/'plan.json').read_bytes(),
            'Collection plan differs from its frozen parent snapshot.')
    for relative, expected in lineage['parent_inputs_sha256'].items():
        if relative.startswith('prompts/'):
            _assert(_sha(_inside(run, relative)) == expected, 'Collection prompt differs: '+relative)
    plan = scientific.read(run/'plan.json')
    _assert(len(plan['chains']) == 125 and plan['fictional_identities'] == 500 and
            actual['weeks'] == 24 and actual['repetitions'] == 2, 'Completed cohort dimensions differ.')
    original_status = scientific.progress(parent)
    _assert(len(original_status) == 6 and not bool(original_status.accepted.any()),
            'Prepared parent must remain unchanged at 0/6.')
    _assert(not any((parent/'accepted').glob('*.json')), 'Prepared parent has unexpected accepted files.')
    _assert(_inside(root, index['report']) == report/'REPORT.md', 'Pointer report path differs.')

    payloads, hashes = _verify_accepted(run, parent, manifest, plan, scientific, collection)
    intake_path = _inside(root, INTAKE)
    intake = scientific.read(intake_path)
    _assert((run/'intake/INTAKE.json').read_bytes() == intake_path.read_bytes(),
            'Collection and local submission intake records differ.')
    _assert(intake['reported_model_label'] == reported['model_label'] and
            intake['reported_effort_label'] == reported['effort_label'] and
            intake['operator_statement'] == reported['operator_statement'] and intake['api_calls'] == 0 and
            intake['full_prompt_confirmed'] is None and intake['fresh_chat_confirmed'] is None and
            intake['source_generation_code_supplied'] is False and len(intake['files']) == 6,
            'Local intake settings/classification differs.')
    mappings, external_sources = set(), []
    for item in intake['files']:
        task_id = item['task_id']
        _assert(task_id in payloads and task_id not in {entry[1] for entry in mappings},
                'Unexpected/duplicate task in local intake.')
        preserved = _inside(intake_path.parent, item['filename'])
        entry = scientific.read(run/'accepted'/(task_id+'.json'))
        raw = _inside(run, entry['raw_path'])
        published = _inside(report/'original_responses', item['filename'])
        _assert(preserved.read_bytes() == raw.read_bytes() == published.read_bytes() and
                _sha(preserved) == item['sha256'] == hashes[task_id] and
                preserved.stat().st_size == item['bytes'], 'Local original response bytes differ: '+item['filename'])
        _assert(item['chains'] == 125 and item['weekly_orders'] == 10000 and item['probe_pairs'] == 500 and
                item['replayed_states'] == 18000 and item['schema_and_replay'] == 'pass',
                'Intake dimensions/status differ.')
        _assert(entry['source_filename'] == item['filename'], 'Original source filename differs.')
        mappings.add((item['filename'], task_id, item['sha256']))
        # A provenance string only: deliberately do not instantiate Path(source_path).
        external_sources.append(item['source_path'])
    file_map = scientific.read(report/'original_responses/FILE_MAP.json')
    _assert(len(file_map) == 6 and {(item['filename'], item['task_id'], item['sha256']) for item in file_map} == mappings,
            'Reader package response mapping differs.')
    _assert(set(hashes) == {item[1] for item in mappings}, 'Intake does not cover all accepted slots.')

    provenance = scientific.read(report/'provenance.json')
    _assert(provenance['study_id'] == run.name and provenance['accepted_responses'] == 6 and
            provenance['expected_responses'] == 6 and provenance['complete'] is True and
            provenance['api_calls'] == provenance['human_observations'] == 0, 'Publication provenance differs.')
    for relative, expected in provenance['inputs_sha256'].items():
        _assert(_sha(_inside(run, relative)) == expected, 'Publication input hash differs: '+relative)
    for relative, expected in provenance['outputs_sha256'].items():
        _assert(_sha(_inside(report, relative)) == expected, 'Publication output hash differs: '+relative)
    package = checker._verify_package(report)
    baseline = scientific.read(_inside(root, BASELINE))['files']
    _assert(isinstance(baseline, dict) and bool(baseline), 'Earlier evidence baseline is empty or invalid.')
    for relative, expected in baseline.items():
        target = _inside(root, relative)
        _assert(target.is_file() and _sha(target) == expected, 'Earlier preserved file differs: '+relative)
    transfer_manifest = root/'HANDOFF_FILES_SHA256.json'
    transfer_files_verified = None
    if transfer_manifest.exists():
        transfer_files = scientific.read(transfer_manifest)['files_sha256']
        _assert(isinstance(transfer_files, dict) and bool(transfer_files), 'Transfer file manifest is empty or invalid.')
        for relative, expected in transfer_files.items():
            target = _inside(root, relative)
            _assert(target != transfer_manifest and target.is_file() and _sha(target) == expected,
                    'Transferred file differs: '+relative)
        transfer_files_verified = len(transfer_files)

    direct, numerical_checks = None, None
    if full_replay:
        import pandas as pd
        # These are published CSV tables, not a call to collection.summarize().
        # Their state values are checked against an independent queue simulator.
        tables = {name: pd.read_csv(report/'results'/(name+'.csv')) for name in
                  ('rounds', 'chains', 'roles', 'probes', 'contrasts')}
        direct = checker.independent_metrics(plan, actual, payloads, tables['rounds'])
        _assert(direct['independently_recomputed_states'] == len(tables['rounds']) == 108000 and
                direct['original_model_week_orders_checked'] == 60000 and len(tables['probes']) == 3000,
                'Independent actual-state/order/probe totals differ.')
        numerical_checks = checker._compare_direct_tables(direct, tables, report)
        _assert(numerical_checks['contrasts'] == 1000, 'Expected 1,000 matched hypothesis contrasts.')
        numerical_checks['cost_phase_summary_rows'] = _verify_cost_phases(direct, report, scientific, checker)

    return dict(verified=True, verification_kind='portable_local_saved_evidence',
        verified_utc=datetime.now(timezone.utc).isoformat(), root=str(root),
        path_mapping_policy='Resolve repository-relative copies below root; retain historical absolute strings without reopening them.',
        collection_id=run.name, parent_study_id=parent_id,
        collection_run=run.relative_to(root).as_posix(), report_folder=report.relative_to(root).as_posix(),
        historical_external_paths_rechecked=False,
        historical_original_parent_path=lineage['original_parent_path'],
        historical_external_response_paths=external_sources,
        historical_report_source_run=provenance['source_run'],
        local_parent_path=parent.relative_to(root).as_posix(),
        local_prepared_snapshot=snapshot.relative_to(root).as_posix(),
        local_submission_intake=INTAKE,
        accepted_responses=6, original_parent_accepted_responses=0,
        reported_model_label=reported['model_label'], reported_effort_label=reported['effort_label'],
        planned_model_label=planned['model_label'], planned_effort_label=planned['effort_label'],
        provider_verified=False, full_prompt_confirmed=None, fresh_chat_confirmed=None,
        actual_reasoning_tokens=None, actual_wall_time_s=None,
        original_response_sha256=hashes, original_response_local_bytes_verified=True,
        submitted_weekly_orders=60000, probe_pairs=3000, scalar_probe_choices=6000,
        independent_replay_performed=full_replay,
        independently_recomputed_states=direct['independently_recomputed_states'] if direct else 0,
        numerical_table_source='Published CSV tables; checked against independent replay when enabled.',
        direct_numeric_checks=numerical_checks,
        prior_files_verified_unchanged=len(baseline), publication_package=package,
        transfer_manifest_present=transfer_manifest.exists(),
        transfer_files_verified=transfer_files_verified,
        report_input_files_verified=len(provenance['inputs_sha256']),
        report_output_files_verified=len(provenance['outputs_sha256']),
        skipped_checks=[] if full_replay else ['Independent physical replay and derived numerical table comparisons'],
        paid_api_calls=0, human_observations=0, independent_student_p_values=False,
        frozen_files_modified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Transferred repository root (defaults to this script\'s checkout).')
    parser.add_argument('--output', type=Path, help='Optional NEW receipt path; existing files are never overwritten.')
    parser.add_argument('--skip-replay', action='store_true', help='Check identity, provenance and bytes; explicitly skip independent numeric replay.')
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error('--output must name a new file; existing receipts are immutable.')
    result = verify(args.root, full_replay=not args.skip_replay)
    serialized = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)+'\n'
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(serialized)
    print(serialized, end='')


if __name__ == '__main__':
    main()
