"""Reported-settings lineage for responses to frozen education/deadline prompts.

The original prompt IDs remain in every response.  This separate collection
records the user's subsequently reported backend without modifying a prepared
study, its scientific implementation, or any submitted choice.  It makes no
model calls and applies no outcome-based acceptance criterion.
"""
from __future__ import annotations

from datetime import date as calendar_date, datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import education_deadline_cohort as scientific

ROOT = scientific.ROOT
PROTOCOL = 'education-deadline-reported-settings-lineage-v1'
SCHEMA = scientific.SCHEMA
PREFIX = 'education_deadline_observed_'
SOURCE_NAME = 'education_deadline_collection.py'
REPORTED_STATEMENT = "I'm using gpt 6-astra extra high effort"
read = scientific.read
save_new = scientific.save_new
digest = scientific.digest


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name+' must be a nonempty literal string.')
    return value


def _parent_files(parent):
    """Only prospectively prepared inputs; responses never enter the identity."""
    parent = Path(parent)
    manifest = read(parent/'manifest.json')
    plan = read(parent/'plan.json')
    names = ['manifest.json', 'plan.json']
    names.extend('source_implementation/'+name for name in manifest['sources'])
    for task in plan['tasks']:
        names.extend('prompts/'+task['task_id']+suffix for suffix in ('.txt', '.sha256'))
    return {name: (parent/name).read_bytes() for name in sorted(names)}


def prepare_collection(parent_run, *, model_label='GPT-6 Astra',
                       effort_label='extra high effort',
                       operator_statement=REPORTED_STATEMENT, date='2026-10-20', root=ROOT):
    """Freeze an observed-settings collection before examining outcome metrics.

    This is an after-response provenance amendment, not a retrospectively changed
    scientific treatment.  Actual provider identity, tokens, elapsed time, full
    prompt use and fresh-chat use remain unverified unless separately supplied.
    """
    parent = Path(parent_run).resolve()
    original = scientific.audit(parent)
    for name, value in (('model_label', model_label), ('effort_label', effort_label),
                        ('operator_statement', operator_statement)):
        _nonempty(value, name)
    if calendar_date.fromisoformat(date).isoformat() != date:
        raise ValueError('Use an ISO report date.')
    if original['config']['collection'] != 'chat_ui':
        raise ValueError('Reported settings lineage requires a prepared chat_ui parent.')
    prepared = _parent_files(parent)
    snapshot = 'prepared_parent/'+original['study_id']
    lineage = dict(parent_study_id=original['study_id'],
                   original_parent_path=str(parent), snapshot_relative_path=snapshot,
                   parent_inputs_sha256={name: _sha(data) for name, data in prepared.items()})
    reported = dict(model_label=model_label, effort_label=effort_label,
                    operator_statement=operator_statement, report_date=date,
                    verification='user_reported_not_provider_verified',
                    reported_after_response_generation=True, collection_interface=None)
    config = original['config'] | dict(model_label=model_label, effort_label=effort_label,
                                       collection='user_supplied')
    source = Path(__file__).read_bytes()
    identity = dict(protocol=PROTOCOL, config=config, planned_config=original['config'],
                    reported_settings=reported, lineage=lineage,
                    adapter_source_sha256=_sha(source))
    collection_id = PREFIX+digest(identity)[:16]
    run = Path(root)/'data/collections'/collection_id
    manifest = identity | dict(study_id=collection_id, schema_version=SCHEMA,
                               plan_sha256=original['plan_sha256'], profiles=original['profiles'],
                               human_observations=0, api_calls=0,
                               actual_reasoning_tokens=None, actual_wall_time_s=None,
                               full_prompt_confirmed=None, fresh_chat_confirmed=None)
    for name, data in prepared.items():
        save_new(run/snapshot/name, data)
    # The unaltered parent plan and prompts are convenient report inputs.  The
    # payload study ID intentionally remains the parent ID, not this collection ID.
    save_new(run/'plan.json', prepared['plan.json'])
    for name, data in prepared.items():
        if name.startswith('prompts/'):
            save_new(run/name, data)
    save_new(run/'source_implementation'/SOURCE_NAME, source)
    save_new(run/'manifest.json', manifest)
    (run/'inbox').mkdir(parents=True, exist_ok=True)
    audit(run)
    return run


def _identity(manifest):
    return {key: manifest[key] for key in ('protocol', 'config', 'planned_config',
                                          'reported_settings', 'lineage', 'adapter_source_sha256')}


def parent_run(run):
    """Return the local, hash-locked prepared parent snapshot."""
    run = Path(run)
    manifest = read(run/'manifest.json')
    relative = manifest['lineage']['snapshot_relative_path']
    expected = 'prepared_parent/'+manifest['lineage']['parent_study_id']
    if relative != expected:
        raise ValueError('Invalid prepared-parent snapshot path.')
    snapshot = (run/relative).resolve()
    if not snapshot.is_relative_to((run/'prepared_parent').resolve()):
        raise ValueError('Prepared-parent snapshot leaves collection.')
    return snapshot


def audit(run):
    """Verify this adapter, original prepared study, snapshot and exact prompts."""
    run = Path(run)
    manifest = read(run/'manifest.json')
    identity = _identity(manifest)
    if (manifest['protocol'] != PROTOCOL or manifest['schema_version'] != SCHEMA or
            run.name != PREFIX+digest(identity)[:16] or manifest['study_id'] != run.name or
            manifest.get('human_observations') != 0 or manifest.get('api_calls') != 0 or
            any(manifest.get(key) is not None for key in
                ('actual_reasoning_tokens', 'actual_wall_time_s', 'full_prompt_confirmed', 'fresh_chat_confirmed'))):
        raise ValueError('Reported-settings collection fingerprint or classification mismatch.')
    planned = manifest['planned_config']
    scientific.Config(**planned).validate()
    reported = manifest['reported_settings']
    expected_reported_keys = ('model_label', 'effort_label', 'operator_statement', 'report_date',
                              'verification', 'reported_after_response_generation', 'collection_interface')
    scientific._keys(reported, expected_reported_keys, 'Reported settings')
    for key in ('model_label', 'effort_label', 'operator_statement'):
        _nonempty(reported[key], key)
    if (calendar_date.fromisoformat(reported['report_date']).isoformat() != reported['report_date'] or
            reported['verification'] != 'user_reported_not_provider_verified' or
            reported['reported_after_response_generation'] is not True or
            reported['collection_interface'] is not None or
            planned['collection'] != 'chat_ui' or
            manifest['config'] != planned | dict(model_label=reported['model_label'],
                                                effort_label=reported['effort_label'], collection='user_supplied')):
        raise ValueError('Reported settings or original planned settings changed.')
    source_hash = manifest['adapter_source_sha256']
    if (_sha(Path(__file__).read_bytes()) != source_hash or
            _sha((run/'source_implementation'/SOURCE_NAME).read_bytes()) != source_hash):
        raise ValueError('Collection adapter source changed; prepare a new collection.')
    lineage = manifest['lineage']
    scientific._keys(lineage, ('parent_study_id', 'original_parent_path', 'snapshot_relative_path',
                                'parent_inputs_sha256'), 'Lineage')
    original = Path(lineage['original_parent_path'])
    snapshot = parent_run(run)
    for prepared in (original, snapshot):
        parent_manifest = scientific.audit(prepared)
        if (parent_manifest['study_id'] != lineage['parent_study_id'] or
                parent_manifest['config'] != planned or
                parent_manifest['profiles'] != manifest['profiles'] or
                parent_manifest['plan_sha256'] != manifest['plan_sha256']):
            raise ValueError('Prepared-parent identity changed.')
        current = {name: _sha(data) for name, data in _parent_files(prepared).items()}
        if current != lineage['parent_inputs_sha256']:
            raise ValueError('Prepared-parent input bytes changed.')
    if (run/'plan.json').read_bytes() != (snapshot/'plan.json').read_bytes():
        raise ValueError('Collection plan differs from frozen parent plan.')
    for name, expected in lineage['parent_inputs_sha256'].items():
        if name.startswith('prompts/') and _sha((run/name).read_bytes()) != expected:
            raise ValueError('Collection prompt differs from frozen parent: '+name)
    return manifest


def task_info(run, task_id):
    return scientific.task_info(parent_run(run), task_id)


def prompt_text(run, task_id):
    task_info(run, task_id)
    return (Path(run)/'prompts'/(task_id+'.txt')).read_text(encoding='utf-8')


def validate_response(run, task_id, text):
    """Use frozen-parent identifiers and strict schema without rewriting bytes."""
    return scientific.validate_response(parent_run(run), task_id, text)


def accepted_path(run, task_id):
    return Path(run)/'accepted'/(task_id+'.json')


def _confirmation(value, name):
    if value is not None and type(value) is not bool:
        raise ValueError(name+' must be True, False or None (unverified).')


def _entry_metadata(run, manifest, task_id):
    reported = manifest['reported_settings']
    planned = manifest['planned_config']
    return dict(collection_id=manifest['study_id'], parent_study_id=manifest['lineage']['parent_study_id'],
                task_id=task_id, prompt_sha256=_sha((Path(run)/'prompts'/(task_id+'.txt')).read_bytes()),
                model_label=reported['model_label'], effort_label=reported['effort_label'],
                planned_model_label=planned['model_label'], planned_effort_label=planned['effort_label'],
                operator_statement=reported['operator_statement'], settings_report_date=reported['report_date'],
                settings_verification=reported['verification'], reported_after_response_generation=True,
                actual_reasoning_tokens=None, actual_wall_time_s=None, api_calls=0, formatting_edits=[])


def import_response(run, task_id, response_path, *,
                    session_label='user-supplied response; fresh chat unverified',
                    full_prompt_confirmed=None, fresh_chat_confirmed=None, evidence_kind='model_output'):
    """Retain every schema/replay attempt; accept only exact valid payloads.

    Unknown provenance confirmations remain unknown.  Neither a favorable
    hypothesis contrast nor a statistical-significance claim is an import gate.
    """
    run = Path(run)
    manifest = audit(run)
    task, chains = task_info(run, task_id)
    if accepted_path(run, task_id).exists():
        raise ValueError('Already locked; accepted results cannot be replaced.')
    _nonempty(session_label, 'session_label')
    _confirmation(full_prompt_confirmed, 'full_prompt_confirmed')
    _confirmation(fresh_chat_confirmed, 'fresh_chat_confirmed')
    expected_kind = 'synthetic_test' if manifest['config']['synthetic'] else 'model_output'
    if evidence_kind != expected_kind:
        raise ValueError('Synthetic fixtures and model responses must stay separate.')
    response_path = Path(response_path)
    raw_bytes = response_path.read_bytes()
    attempts = list((run/'attempts').glob(task_id+'_*.txt'))
    number = max((int(path.stem.rsplit('_', 1)[1]) for path in attempts), default=0)+1
    raw = run/'attempts'/f'{task_id}_{number:03d}.txt'
    save_new(raw, raw_bytes)
    entry = _entry_metadata(run, manifest, task_id) | dict(
        raw_path=raw.relative_to(run).as_posix(), raw_sha256=_sha(raw_bytes),
        source_filename=response_path.name, session_label=session_label,
        evidence_kind=evidence_kind, full_prompt_confirmed=full_prompt_confirmed,
        fresh_chat_confirmed=fresh_chat_confirmed, received_utc=datetime.now(timezone.utc).isoformat())
    try:
        payload = validate_response(run, task_id, raw_bytes.decode('utf-8'))
    except (UnicodeDecodeError, ValueError) as exc:
        save_new(raw.with_suffix('.json'), entry | dict(status='rejected', reason=str(exc)))
        raise ValueError('Response rejected; exact original retained: '+str(exc)) from exc
    try:
        scientific._replay_payload(read(parent_run(run)/'manifest.json'), task, chains, payload)
    except (ValueError, AssertionError, OverflowError) as exc:
        save_new(raw.with_suffix('.json'), entry | dict(status='replay_failed', reason=str(exc), payload=payload))
        raise ValueError('Physical replay failed; exact original retained: '+str(exc)) from exc
    entry.update(status='accepted', payload=payload)
    save_new(raw.with_suffix('.json'), entry)
    save_new(accepted_path(run, task_id), entry)
    return entry


def load_accepted(run, task_id):
    run = Path(run)
    manifest = audit(run)
    task, chains = task_info(run, task_id)
    accepted = accepted_path(run, task_id)
    entry = read(accepted)
    raw = scientific._evidence_path(run, entry.get('raw_path'))
    if raw.with_suffix('.json').read_bytes() != accepted.read_bytes():
        raise ValueError('Accepted record differs from immutable attempt receipt.')
    common = _entry_metadata(run, manifest, task_id)
    expected_keys = tuple(common)+('raw_path', 'raw_sha256', 'source_filename', 'session_label',
                                  'evidence_kind', 'full_prompt_confirmed', 'fresh_chat_confirmed',
                                  'received_utc', 'status', 'payload')
    scientific._keys(entry, expected_keys, 'Accepted record')
    expected_kind = 'synthetic_test' if manifest['config']['synthetic'] else 'model_output'
    if (any(entry[key] != value for key, value in common.items()) or entry['status'] != 'accepted' or
            entry['evidence_kind'] != expected_kind or
            raw.name.rsplit('_', 1)[0] != task_id):
        raise ValueError('Accepted provenance metadata changed.')
    _nonempty(entry['source_filename'], 'source_filename')
    _nonempty(entry['session_label'], 'session_label')
    _nonempty(entry['received_utc'], 'received_utc')
    _confirmation(entry['full_prompt_confirmed'], 'full_prompt_confirmed')
    _confirmation(entry['fresh_chat_confirmed'], 'fresh_chat_confirmed')
    data = raw.read_bytes()
    if _sha(data) != entry['raw_sha256']:
        raise ValueError('Raw response hash mismatch.')
    if validate_response(run, task_id, data.decode('utf-8')) != entry['payload']:
        raise ValueError('Accepted payload differs from exact original response.')
    scientific._replay_payload(read(parent_run(run)/'manifest.json'), task, chains, entry['payload'])
    return entry


def progress(run):
    audit(run)
    return pd.DataFrame([task | dict(students=4*len(task['chain_ids']),
                                    accepted=accepted_path(run, task['task_id']).exists())
                         for task in read(Path(run)/'plan.json')['tasks']]).drop(columns=['chain_ids'])


def next_task(run):
    audit(run)
    for task in read(Path(run)/'plan.json')['tasks']:
        if not accepted_path(run, task['task_id']).exists():
            return task | dict(prompt=prompt_text(run, task['task_id']),
                               prompt_path=str(Path(run)/'prompts'/(task['task_id']+'.txt')))
    return None


def replay(run):
    run = Path(run)
    audit(run)
    parent_manifest = read(parent_run(run)/'manifest.json')
    rows, probes, imports = [], [], []
    for task in read(run/'plan.json')['tasks']:
        if not accepted_path(run, task['task_id']).exists():
            continue
        entry = load_accepted(run, task['task_id'])
        _, chains = task_info(run, task['task_id'])
        task_rows, task_probes = scientific._replay_payload(parent_manifest, task, chains, entry['payload'])
        rows.extend(task_rows)
        probes.extend(task_probes)
        imports.append({key: value for key, value in entry.items() if key != 'payload'})
    return pd.DataFrame(rows), pd.DataFrame(probes), imports


def summarize(run):
    """Apply the frozen scientific grouping to this separate observed collection."""
    rounds, probes, imports = replay(run)
    common = ['task_id', 'repetition', 'arm', 'deadline_seconds', 'lecture_id', 'chain_id']
    cost_columns = ['cost_practice', 'cost_model', 'cost_automatic', 'total_cost']
    contrast_columns = ['hypothesis', 'repetition', 'chain_id', 'metric', 'reference_arm', 'treatment_arm', 'estimate', 'expected_sign']
    if rounds.empty:
        return dict(rounds=rounds, probes=probes, imports=pd.DataFrame(imports),
                    roles=pd.DataFrame(columns=common+['role', 'profile_id', 'participant_id']+cost_columns+['sensitivity']),
                    chains=pd.DataFrame(columns=common+cost_columns+['sensitivity', 'automatic_cost_fraction']),
                    contrasts=pd.DataFrame(columns=contrast_columns))
    role_keys = common+['role', 'profile_id', 'participant_id']
    roles = rounds.groupby(role_keys+['phase'], sort=False)['cost'].sum().unstack('phase', fill_value=0)
    roles = roles.reindex(columns=['practice', 'model', 'automatic'], fill_value=0)
    roles.columns = ['cost_'+phase for phase in roles.columns]
    roles['total_cost'] = roles.sum(axis=1)
    roles = roles.reset_index().merge(probes[role_keys+['sensitivity']], on=role_keys, validate='one_to_one')
    chains = roles.groupby(common, sort=False)[cost_columns].sum().reset_index()
    chain_sensitivity = roles.groupby(common, sort=False)['sensitivity'].mean().reset_index()
    chains = chains.merge(chain_sensitivity, on=common, validate='one_to_one')
    chains['automatic_cost_fraction'] = np.divide(chains['cost_automatic'], chains['total_cost'],
                                                out=np.full(len(chains), np.nan), where=chains['total_cost'].to_numpy() != 0)
    contrasts = []
    for hypothesis, (reference, treatment, metric, sign) in scientific.CONTRASTS.items():
        left = chains.loc[chains.arm == reference, ['repetition', 'chain_id', metric]]
        right = chains.loc[chains.arm == treatment, ['repetition', 'chain_id', metric]]
        paired = left.merge(right, on=['repetition', 'chain_id'], suffixes=('_reference', '_treatment'), validate='one_to_one')
        for row in paired.to_dict('records'):
            contrasts.append(dict(hypothesis=hypothesis, repetition=row['repetition'], chain_id=row['chain_id'],
                                  metric=metric, reference_arm=reference, treatment_arm=treatment,
                                  estimate=row[metric+'_treatment']-row[metric+'_reference'], expected_sign=sign))
    return dict(rounds=rounds, probes=probes, imports=pd.DataFrame(imports), roles=roles, chains=chains,
                contrasts=pd.DataFrame(contrasts, columns=contrast_columns))
