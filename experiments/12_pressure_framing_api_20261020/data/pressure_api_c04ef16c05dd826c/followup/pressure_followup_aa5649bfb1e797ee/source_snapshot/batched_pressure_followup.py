"""One bounded Claude follow-up, using the immutable v1 request transport.

The three accepted pilots are references. Only one revised Claude pilot and the
four still-unstarted main requests are purchasable. Import/preparation is free.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from statistics import mean

import httpx

from . import batched_pressure as study
from . import batched_pressure_recovery as previous
from .batched_pressure_api import BudgetLedger, now, save, digest, reservation, runner_lock

VERSION = 'pressure-claude-followup-v1'
CLAUDE = 'claude-haiku-5-5'
PROTOCOL_NAME = 'CLAUDE_FOLLOWUP_20261021.md'
_sha, _inside = previous._sha, previous._inside


def experiment_for(directory):
    return Path(directory).resolve().parents[3]


def parent_run(directory):
    directory = Path(directory).resolve()
    return _inside(experiment_for(directory), study.read(directory / 'manifest.json')['parent_run'])


def _payload(previous_run, task):
    payload = study.read(Path(previous_run) / 'payloads' / (task['task_id'] + '.json'))
    if task['model'] == CLAUDE:
        payload['output_config']['effort'] = 'medium'
        payload['messages'][0]['content'] += '\n\n' + previous.STATE_TRACKING_APPENDIX
    return payload


def prepare(previous_recovery):
    previous_run = Path(previous_recovery).resolve()
    previous_manifest = previous.load(previous_run)
    parent = previous.parent_run(previous_run)
    experiment = previous.experiment_for(previous_run)
    existing = sorted((parent / 'followup').glob('*/manifest.json'))
    if existing:
        if len(existing) != 1:
            raise ValueError('Multiple follow-up plans require explicit review.')
        load(existing[0].parent)
        return existing[0].parent
    previous.analyze(previous_run)  # Includes strict accepted receipt hashes.
    plan = study.loadplan(parent)
    status = study.read(previous_run / 'api_status.json')
    inherited = {}
    for task in plan['tasks']:
        row = status['tasks'].get(task['task_id'], {})
        if task['phase'] == 'main':
            if row.get('status') not in (None, 'pilot_blocked') or (previous_run / task['response_path']).exists():
                raise ValueError('Follow-up must be prepared before any main request starts.')
            continue
        if task['model'] == CLAUDE:
            if row.get('status') != 'invalid' or (previous_run / task['response_path']).exists():
                raise ValueError('This follow-up applies only to the second invalid Claude pilot.')
            continue
        origin = previous_manifest['inherited_pilots'].get(task['task_id'])
        path = _inside(experiment, origin['path']) if origin else previous_run / task['response_path']
        if row.get('status') != 'accepted' or _sha(path) != row.get('accepted_sha256'):
            raise ValueError('All three successful pilots must remain accepted with matching hashes.')
        if study.validate_response(task, study.read(path)):
            raise ValueError('An inherited pilot fails unchanged strict validation.')
        inherited[task['task_id']] = dict(model=task['model'], path=path.relative_to(experiment).as_posix(),
            sha256=_sha(path), returned_model=row['returned_model'], origin='previously_accepted_pilot',
            original_origin=(origin['origin'] if origin else previous_run.name),
            actual_settings=previous_manifest['settings_by_model'][task['model']]['pilot'])
    ledger_path = experiment / 'data/api_budget.json'
    ledger = study.read(ledger_path)
    if ledger['cap_usd'] != 5:
        raise ValueError('Follow-up retains the existing cumulative $5 cap.')
    parent_ids = {parent.name, previous_run.name}
    if any(row.get('phase') == 'main' and row.get('run') in parent_ids for row in ledger['attempts'].values()):
        raise ValueError('A main request was already reserved or sent; do not replace it.')
    predecessor_files = {p.relative_to(experiment).as_posix(): _sha(p)
                         for p in previous_run.rglob('*') if p.is_file()}
    sources = {name: Path(__file__).with_name(name) for name in
               ('batched_pressure_followup.py', 'batched_pressure_recovery.py',
                'batched_pressure.py', 'batched_pressure_api.py', 'game.py')}
    protocol = experiment / 'hypotheses' / PROTOCOL_NAME
    payloads = {t['task_id']: _payload(previous_run, t) for t in plan['tasks']
                if t['task_id'] not in inherited}
    settings = {model: dict(value) for model, value in previous_manifest['settings_by_model'].items()}
    for phase in ('pilot', 'main'):
        settings[CLAUDE][phase] = dict(settings[CLAUDE][phase], effort='medium',
            prompt_revision='concise_completion_plus_physical_ledger_appendix')
    identity = dict(version=VERSION, parent_run=parent.relative_to(experiment).as_posix(),
        parent_study_id=plan['study_id'], previous_recovery=previous_run.relative_to(experiment).as_posix(),
        predecessor_files_sha256=predecessor_files, inherited_pilots=inherited,
        source_hashes={name: _sha(path) for name, path in sources.items()},
        protocol_path=protocol.relative_to(experiment).as_posix(), protocol_sha256=_sha(protocol),
        payload_hashes={key: digest(value) for key, value in payloads.items()},
        settings_by_model=settings, failed_pilot_diagnoses={CLAUDE: status['tasks'][CLAUDE + '_pilot']},
        initial_budget_attempts_sha256={key: digest(value) for key, value in ledger['attempts'].items()},
        initial_budget_snapshot_sha256=_sha(ledger_path), authorized_total_usd=5.,
        new_pilot_generations=1, new_main_generations=4, max_technical_attempts_per_generation=2,
        notes=[
            'This prospective technical amendment follows an invalid Claude inventory readback; the earlier output cap failure and both raw attempts remain preserved.',
            'Three successful pilots are reused by exact reference and hash, with their original settings and provenance.',
            'Claude keeps adaptive thinking and 32,768/65,536 output caps, adds neutral physical bookkeeping, and changes effort from low to medium for both classroom conditions.',
            'GPT-6 and both GPT-5.6 main payloads are unchanged from the first recovery plan.',
            'Exactly one further Claude pilot generation and four still-unstarted main generations are scheduled; no semantic retries, replacements or outcome-direction gate.',
            'All four strict pilot validations remain required before main collection.',
            'Original logical task/chain IDs remain unchanged; the separate follow-up ID and frozen payloads identify this amendment.',
            'All previous spending, uncertain charges and any technical retries remain inside the same experiment-wide $5 ledger.',
            'The fixed request transport is inherited unchanged from recovery v1; no module globals are monkeypatched.',
            'Provider-specific settings limit causal model comparisons. Imagined pressure and jointly generated chains still do not establish human-time or independent-participant effects.',
        ])
    followup_id = 'pressure_followup_' + study.digest(identity)[:16]
    directory = parent / 'followup' / followup_id
    manifest = dict(identity, recovery_id=followup_id, followup_id=followup_id,
                    new_task_ids=list(payloads), inherited_task_ids=list(inherited))
    study.save_new(directory / 'manifest.json', manifest)
    study.save_new(directory / 'manifest.sha256', study.digest(manifest) + '\n')
    for name, path in sources.items():
        study.save_new(directory / 'source_snapshot' / name, path.read_bytes())
    study.save_new(directory / 'source_snapshot' / PROTOCOL_NAME, protocol.read_bytes())
    study.save_new(directory / 'source_snapshot/parent_budget_at_preparation.json', ledger_path.read_bytes())
    for key, payload in payloads.items():
        study.save_new(directory / 'payloads' / (key + '.json'), payload)
        study.save_new(directory / 'prompts' / (key + '.txt'),
                       (payload.get('input') or payload.get('messages'))[0]['content'])
    (directory / 'accepted').mkdir(parents=True, exist_ok=True)
    return directory


def load(directory):
    directory = Path(directory).resolve()
    manifest = study.read(directory / 'manifest.json')
    if study.digest(manifest) != (directory / 'manifest.sha256').read_text().strip():
        raise ValueError('Frozen follow-up manifest changed.')
    identity = {k: v for k, v in manifest.items() if k not in
                ('recovery_id', 'followup_id', 'new_task_ids', 'inherited_task_ids')}
    if (manifest['version'] != VERSION or directory.name != 'pressure_followup_' + study.digest(identity)[:16]
            or manifest['recovery_id'] != directory.name or manifest['followup_id'] != directory.name):
        raise ValueError('Follow-up identity differs.')
    experiment = experiment_for(directory)
    parent = _inside(experiment, manifest['parent_run'])
    if directory.parent.parent != parent:
        raise ValueError('Follow-up is not nested under its recorded parent.')
    predecessor = _inside(experiment, manifest['previous_recovery'])
    previous.load(predecessor)
    previous.analyze(predecessor)
    for relative, expected in manifest['predecessor_files_sha256'].items():
        if _sha(_inside(experiment, relative)) != expected:
            raise ValueError('Predecessor evidence changed: ' + relative)
    for name, expected in manifest['source_hashes'].items():
        if _sha(directory / 'source_snapshot' / name) != expected or _sha(Path(__file__).with_name(name)) != expected:
            raise ValueError('Frozen follow-up implementation changed: ' + name)
    if (_sha(_inside(experiment, manifest['protocol_path'])) != manifest['protocol_sha256'] or
            _sha(directory / 'source_snapshot' / PROTOCOL_NAME) != manifest['protocol_sha256']):
        raise ValueError('Frozen follow-up protocol changed.')
    if _sha(directory / 'source_snapshot/parent_budget_at_preparation.json') != manifest['initial_budget_snapshot_sha256']:
        raise ValueError('Original follow-up budget snapshot changed.')
    ledger = study.read(experiment / 'data/api_budget.json')
    if ledger['cap_usd'] != 5:
        raise ValueError('Follow-up cumulative cap changed.')
    for key, expected in manifest['initial_budget_attempts_sha256'].items():
        if digest(ledger['attempts'].get(key)) != expected:
            raise ValueError('Earlier API charge or reservation changed.')
    tasks = {t['task_id']: t for t in study.loadplan(parent)['tasks']}
    if (set(manifest['new_task_ids']) | set(manifest['inherited_task_ids']) != set(tasks) or
            len(manifest['new_task_ids']) != 5 or len(manifest['inherited_task_ids']) != 3):
        raise ValueError('Follow-up slots differ from the fixed sample.')
    for key, expected in manifest['payload_hashes'].items():
        payload = study.read(directory / 'payloads' / (key + '.json'))
        if digest(payload) != expected or payload != _payload(predecessor, tasks[key]):
            raise ValueError('Frozen follow-up request changed: ' + key)
        if (directory / 'prompts' / (key + '.txt')).read_text() != (payload.get('input') or payload.get('messages'))[0]['content']:
            raise ValueError('Frozen follow-up prompt changed: ' + key)
    return manifest


def estimate(directory):
    directory = Path(directory).resolve()
    manifest = load(directory)
    tasks = {t['task_id']: t for t in study.loadplan(parent_run(directory))['tasks']}
    return [dict(model=model,
        pilot_calls=sum(tasks[k]['phase'] == 'pilot' for k in manifest['new_task_ids'] if tasks[k]['model'] == model),
        main_calls=1, first_attempt_reservation_ceiling_usd=sum(reservation(model,
            study.read(directory / 'payloads' / (key + '.json')))
            for key in manifest['new_task_ids'] if tasks[key]['model'] == model),
        note='Five new fixed slots; three accepted pilots reused without repurchase; all historical charges retained.')
        for model in study.MODELS]


class Runner(previous.Runner):
    """Reuse immutable v1 task/retry/usage logic through explicit adapter methods."""
    def __init__(self, directory, keys=None, *, transport=None, concurrency=4, callback=None, retry_delay=2.):
        self.run = Path(directory).resolve()
        self.manifest = load(self.run)
        self.experiment = experiment_for(self.run)
        self.parent = parent_run(self.run)
        self.plan = study.loadplan(self.parent)
        self.keys, self.transport = keys or {}, transport
        self.semaphore = asyncio.Semaphore(concurrency)
        self.callback = callback or (lambda value: None)
        self.retry_delay = retry_delay
        self.raw, self.status_path = self.run / 'raw', self.run / 'api_status.json'
        predecessor = _inside(self.experiment, self.manifest['previous_recovery'])
        self.status = (study.read(self.status_path) if self.status_path.exists() else dict(tasks={},
            returned_models=study.read(predecessor / 'api_status.json')['returned_models'], started=now()))
        for key, entry in self.manifest['inherited_pilots'].items():
            self.status['tasks'].setdefault(key, dict(status='accepted', model=entry['model'], phase='pilot',
                accepted_sha256=entry['sha256'], returned_model=entry['returned_model'], inherited=True,
                origin=entry['path']))
        self.ledger = self.client = None

    def progress(self):
        rows = list(self.status['tasks'].values())
        accepted = sum(r['status'] == 'accepted' for r in rows)
        failed = sum(r['status'] in ('invalid', 'failed', 'interrupted') for r in rows)
        skipped = sum(r['status'] == 'pilot_blocked' for r in rows)
        out = dict(total=len(self.plan['tasks']), accepted=accepted, failed=failed, skipped=skipped,
            inherited=len(self.manifest['inherited_task_ids']), new_planned_calls=len(self.manifest['new_task_ids']),
            done=accepted+failed+skipped, remaining=len(self.plan['tasks'])-accepted-failed-skipped,
            charged_or_reserved_usd=self.ledger.spent if self.ledger else 0., cap_usd=5., tasks=self.status['tasks'])
        self.status['progress'] = {k: v for k, v in out.items() if k != 'tasks'}
        save(self.status_path, self.status)
        self.callback(out)
        return out

    async def execute(self, phase='all'):
        if phase not in ('all', 'pilot', 'main'):
            raise ValueError('phase must be pilot, main, or all')
        with runner_lock(self.experiment):
            load(self.run)
            self.ledger = BudgetLedger(self.experiment)
            self.progress()
            async with httpx.AsyncClient(transport=self.transport, timeout=httpx.Timeout(600., connect=30.)) as client:
                self.client = client
                if phase in ('all', 'pilot'):
                    await asyncio.gather(*(self.task(t) for t in self.plan['tasks'] if t['phase'] == 'pilot'))
                if phase in ('all', 'main'):
                    passed = all(self.status['tasks'].get(t['task_id'], {}).get('status') == 'accepted'
                                 for t in self.plan['tasks'] if t['phase'] == 'pilot')
                    if passed:
                        await asyncio.gather(*(self.task(t) for t in self.plan['tasks'] if t['phase'] == 'main'))
                    else:
                        for task in self.plan['tasks']:
                            if task['phase'] == 'main':
                                self.status['tasks'].setdefault(task['task_id'], dict(status='pilot_blocked', model=task['model'], phase='main'))
            self.client = None
        return self.progress()


def analyze(directory):
    directory = Path(directory).resolve()
    manifest = load(directory)
    parent, experiment = parent_run(directory), experiment_for(directory)
    plan = study.loadplan(parent)
    status_path = directory / 'api_status.json'
    execution = study.read(status_path) if status_path.exists() else {'tasks': {}}
    task_status, chains, rounds, probes = [], [], [], []
    for task in plan['tasks']:
        inherited = manifest['inherited_pilots'].get(task['task_id'])
        path = _inside(experiment, inherited['path']) if inherited else directory / task['response_path']
        row = {key: task[key] for key in ('task_id', 'model', 'phase')}
        row.update(status='missing', issues=[], origin=inherited['path'] if inherited else manifest['followup_id'])
        if path.exists():
            receipt = inherited or execution.get('tasks', {}).get(task['task_id'], {})
            expected = receipt.get('sha256') if inherited else receipt.get('accepted_sha256')
            if _sha(path) != expected or (not inherited and receipt.get('status') != 'accepted'):
                raise ValueError('Follow-up accepted response lacks matching immutable receipt: ' + task['task_id'])
            payload = study.read(path)
            issues = study.validate_response(task, payload)
            row.update(status='invalid' if issues else 'accepted', issues=issues)
            if not issues:
                specs = {c['chain_id']: c for c in task['chains']}
                for choice in payload['chains']:
                    metrics, own_rounds, own_probes = study.task_metrics(specs[choice['chain_id']], choice)
                    chains.append(metrics); rounds.extend(own_rounds); probes.extend(own_probes)
        task_status.append(row)
    hypotheses, contrasts, model_status = [], [], []
    for model in study.MODELS:
        own = [r for r in chains if r['model'] == model]
        pilot_count = sum(r['phase'] == 'pilot' for r in own)
        main = [r for r in own if r['phase'] == 'main']
        model_status.append(dict(model=model, accepted_pilot=pilot_count, expected_pilot=2,
            accepted_main=len(main), expected_main=20, complete=pilot_count == 2 and len(main) == 20,
            accepted_pilot_responses=int(pilot_count == 2), accepted_main_responses=int(len(main) == 20), inference_available=False))
        lookup = {(r['block'], r['condition']): r for r in main}
        for name, metric, sign in (('H1', 'sensitivity', -1), ('H2', 'total_cost', 1)):
            differences = []
            for block in range(10):
                if (block, 'no_pressure') in lookup and (block, 'strong_pressure') in lookup:
                    low, high = lookup[block, 'no_pressure'], lookup[block, 'strong_pressure']
                    difference = high[metric] - low[metric]; differences.append(difference)
                    contrasts.append(dict(model=model, hypothesis=name, block=block, metric=metric,
                        no_pressure=low[metric], strong_pressure=high[metric], difference=difference))
            effect = mean(differences) if differences else None
            hypotheses.append(dict(model=model, hypothesis=name, metric=metric, expected_sign=sign,
                paired_blocks=len(differences), mean_strong_minus_no=effect,
                descriptive_direction='unavailable' if effect is None else 'zero' if effect == 0 else 'predicted' if sign*effect > 0 else 'opposite',
                p_raw=None, p_holm_8=None, paired_bootstrap_95=None, inference_available=False, literal_binding_time_test=False))
    return dict(study_id=manifest['followup_id'], parent_study_id=plan['study_id'], hypotheses=hypotheses,
        contrasts=contrasts, chains=chains, rounds=rounds, probes=probes, task_status=task_status, model_status=model_status,
        limitations=study.analyze(parent)['limitations'] + manifest['notes'],
        recovery_metadata={k: manifest[k] for k in ('recovery_id', 'followup_id', 'parent_run', 'previous_recovery',
            'inherited_pilots', 'settings_by_model', 'failed_pilot_diagnoses', 'notes')})
