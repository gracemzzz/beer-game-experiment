"""Bounded technical recovery for experiment 12, without editing frozen originals.

The original logical chain/task IDs are retained verbatim. A separate amendment
ID, source snapshots and frozen HTTP payloads identify the changed generation
procedure; original accepted pilots are referenced, never relabelled or resent.
No request occurs on import or preparation.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from statistics import mean
import time

import httpx

from . import batched_pressure as study
from . import batched_pressure_api as original
from .batched_pressure_api import (BudgetLedger, BudgetStop, MAX_ATTEMPTS, RATES,
    AUTHORIZED_CAP_USD, now, save, digest, reservation, usage_and_charge, runner_lock,
    _clean, _extract)

VERSION = 'pressure-technical-recovery-v1'
FAILED_MODELS = ('gpt-6-luna', 'claude-haiku-5-5')
INHERITED_MODELS = ('gpt-5.6-luna', 'gpt-5.6-sol')

STATE_TRACKING_APPENDIX = """STATE-TRACKING CHECK
Keep physical inventory, backlog and outstanding orders as three separate
quantities for each role. Initialize inventory=[12,12,12,12], backlog=[0,0,0,0],
outstanding=[12,12,12,12], next upstream incoming orders=[4,4,4], and delivery
queues=[[4,4],[4,4],[4,4],[4,4,4]], with the next receipt first. Each week:
(1) Remove the first entry from EACH delivery queue; add those receipts to
inventory and subtract them from outstanding.
(2) Incoming demand is [customer demand, prior retailer order, prior wholesaler
order, prior distributor order], using the initial upstream incoming orders in week 1.
(3) For EACH role compute owed=old_backlog+incoming_demand,
shipment=min(inventory,owed), inventory=inventory-shipment,
backlog=owed-shipment. Complete these calculations for all four roles.
(4) Append each upstream role's shipment to its downstream role's delivery queue.
(5) Record any requested checkpoint now: these four inventory values are
remaining physical stock, not outstanding orders or pipeline.
(6) Choose the four orders; add them to outstanding, set next week's upstream
incoming orders to the first three orders, and append the factory's production
order to its own delivery queue. Repeat using the updated state.
A new order does not add physical stock today. Calculate checkpoints from the
full preceding ledger and submitted orders; do not substitute typical inventory
values. This is physical bookkeeping only and prescribes no ordering strategy.
"""
CLAUDE_COMPLETION_APPENDIX = """COMPLETION REQUIREMENT
Return the complete requested JSON within the available output allowance. Keep
internal planning concise and allow enough output space for every required
chain, order row, probe and checkpoint. Do not spend the entire allowance on
planning. Follow the exact schema without an explanatory preamble. These output
instructions apply equally to both classroom situations and prescribe no orders.
"""


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inside(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Recovery reference must stay inside the experiment.')
    target = (Path(root) / relative).resolve()
    if not target.is_relative_to(Path(root).resolve()):
        raise ValueError('Recovery reference escapes the experiment.')
    return target


def experiment_for(recovery):
    return Path(recovery).resolve().parents[3]


def parent_run(recovery):
    recovery = Path(recovery).resolve()
    manifest = study.read(recovery / 'manifest.json')
    return _inside(experiment_for(recovery), manifest['parent_run'])


def amended_payload(task):
    payload = original.payload_for(task)
    if task['model'] == 'gpt-6-luna':
        payload['reasoning'] = {'effort': 'medium'}
        payload['max_output_tokens'] = 16384 if task['phase'] == 'pilot' else 32768
        payload['input'][0]['content'] += '\n\n' + STATE_TRACKING_APPENDIX
    elif task['model'] == 'claude-haiku-5-5':
        payload['max_tokens'] = 32768 if task['phase'] == 'pilot' else 65536
        payload['messages'][0]['content'] += '\n\n' + CLAUDE_COMPLETION_APPENDIX
    return payload


def prepare(parent):
    """Freeze one bounded amendment after the documented two technical failures."""
    parent = Path(parent).resolve()
    experiment = parent.parent.parent
    existing = sorted((parent / 'recovery').glob('*/manifest.json'))
    if existing:
        if len(existing) != 1:
            raise ValueError('Multiple recovery amendments require explicit review.')
        load(existing[0].parent)
        return existing[0].parent
    plan = study.loadplan(parent)
    status = study.read(parent / 'api_status.json')
    tasks = {t['task_id']: t for t in plan['tasks']}
    pilots = [t for t in plan['tasks'] if t['phase'] == 'pilot']
    if len(pilots) != 4 or len(plan['tasks']) != 8:
        raise ValueError('Recovery requires the original four-model eight-slot plan.')
    inherited = {}
    for task in pilots:
        row = status['tasks'].get(task['task_id'], {})
        accepted = parent / task['response_path']
        if task['model'] in INHERITED_MODELS:
            if row.get('status') != 'accepted' or not accepted.is_file():
                raise ValueError('The two successful original pilots must remain accepted.')
            if _sha(accepted) != row.get('accepted_sha256'):
                raise ValueError('Inherited pilot bytes differ.')
            if study.validate_response(task, study.read(accepted)):
                raise ValueError('Inherited pilot no longer passes strict validation.')
            inherited[task['task_id']] = dict(model=task['model'],
                path=accepted.relative_to(experiment).as_posix(), sha256=_sha(accepted),
                returned_model=row['returned_model'], origin='original_accepted_pilot')
        elif task['model'] in FAILED_MODELS:
            if row.get('status') not in ('invalid', 'failed') or accepted.exists():
                raise ValueError('Only the two failed pilot slots can receive this amendment.')
        else:
            raise ValueError('Unexpected model.')
    if any((parent / t['response_path']).exists() or
           status['tasks'].get(t['task_id'], {}).get('status') == 'accepted'
           for t in plan['tasks'] if t['phase'] == 'main'):
        raise ValueError('This amendment must be prepared before any main data.')
    paths = [parent / 'plan.json', parent / 'plan.sha256', parent / 'api_status.json']
    paths += [parent / t['response_path'] for t in pilots if t['model'] in INHERITED_MODELS]
    paths += sorted((experiment / 'raw' / parent.name).rglob('*'))
    parent_files = {p.relative_to(experiment).as_posix(): _sha(p)
                    for p in paths if p.is_file()}
    if not any('/raw/' in '/' + p for p in parent_files):
        raise ValueError('Original provider attempts must be retained.')
    ledger_path = experiment / 'data/api_budget.json'
    ledger = study.read(ledger_path)
    if ledger['cap_usd'] != 5:
        raise ValueError('Recovery must share the existing $5 experiment budget.')
    sources = {name: Path(__file__).with_name(name) for name in
               ('batched_pressure_recovery.py', 'batched_pressure.py',
                'batched_pressure_api.py', 'game.py')}
    amendment = experiment / 'hypotheses/RECOVERY_20261021.md'
    settings = {}
    new_payloads = {}
    for task in plan['tasks']:
        if task['task_id'] in inherited:
            continue
        payload = amended_payload(task)
        new_payloads[task['task_id']] = payload
        settings.setdefault(task['model'], {})[task['phase']] = dict(
            effort=(payload.get('reasoning') or payload.get('output_config') or {}).get('effort'),
            max_output_tokens=payload.get('max_output_tokens', payload.get('max_tokens')),
            prompt_revision=('physical_ledger_appendix' if task['model'] == 'gpt-6-luna' else
                             'concise_completion_appendix' if task['model'] == 'claude-haiku-5-5' else 'original'),
            reasoning_mode=payload.get('thinking', payload.get('reasoning')))
    for task in pilots:
        if task['task_id'] in inherited:
            settings[task['model']]['pilot'] = dict(effort='low', max_output_tokens=8192,
                                                   prompt_revision='original', inherited=True)
    identity = dict(version=VERSION, parent_run=parent.relative_to(experiment).as_posix(),
        parent_study_id=plan['study_id'], parent_plan_sha256=_sha(parent / 'plan.json'),
        amendment_path=amendment.relative_to(experiment).as_posix(), amendment_sha256=_sha(amendment),
        parent_files_sha256=parent_files, inherited_pilots=inherited,
        source_hashes={name: _sha(path) for name, path in sources.items()},
        payload_hashes={key: digest(value) for key, value in new_payloads.items()},
        settings_by_model=settings,
        failed_pilot_diagnoses={t['model']: status['tasks'][t['task_id']]
                                for t in pilots if t['model'] in FAILED_MODELS},
        initial_budget_attempts_sha256={key: digest(value) for key, value in ledger['attempts'].items()},
        initial_budget_snapshot_sha256=_sha(ledger_path),
        authorized_total_usd=5., new_pilot_generations=2, new_main_generations=4,
        max_technical_attempts_per_generation=2,
        notes=[
            'User requested a bounded technical fix after the first pilots; this is a post-pilot amendment.',
            'Original task, chain and response IDs remain literal parent IDs; this amendment ID identifies changed prompts/settings separately.',
            'Two successful original pilots are inherited by exact hash, not regenerated.',
            'No original failure is deleted, repaired, relabelled accepted, or substituted with fabricated orders.',
            'Only two failed pilot generations are reattempted once; no semantic retry loop or outcome-based replacement.',
            'All four strict pilot checks must pass before any of the four main generations.',
            'GPT-6 Luna receives neutral physical bookkeeping and medium effort; Claude keeps adaptive low effort with a larger completion allowance.',
            'Provider-specific recovery settings limit model-only causal comparisons; both pressure conditions within each model use the same revised request.',
            'Original failures and recovery costs remain inside the same cumulative $5 ledger.',
        ])
    recovery_id = 'pressure_recovery_' + study.digest(identity)[:16]
    recovery = parent / 'recovery' / recovery_id
    manifest = dict(identity, recovery_id=recovery_id,
                    new_task_ids=list(new_payloads), inherited_task_ids=list(inherited))
    study.save_new(recovery / 'manifest.json', manifest)
    study.save_new(recovery / 'manifest.sha256', study.digest(manifest) + '\n')
    for name, path in sources.items():
        study.save_new(recovery / 'source_snapshot' / name, path.read_bytes())
    study.save_new(recovery / 'source_snapshot/RECOVERY_20261021.md', amendment.read_bytes())
    study.save_new(recovery / 'source_snapshot/parent_budget_at_preparation.json', ledger_path.read_bytes())
    for key, payload in new_payloads.items():
        study.save_new(recovery / 'payloads' / (key + '.json'), payload)
        prompt = (payload.get('input') or payload.get('messages'))[0]['content']
        study.save_new(recovery / 'prompts' / (key + '.txt'), prompt)
    (recovery / 'accepted').mkdir(parents=True, exist_ok=True)
    return recovery


def load(recovery):
    recovery = Path(recovery).resolve()
    manifest = study.read(recovery / 'manifest.json')
    if study.digest(manifest) != (recovery / 'manifest.sha256').read_text().strip():
        raise ValueError('Frozen recovery manifest changed.')
    identity = {k: v for k, v in manifest.items()
                if k not in ('recovery_id', 'new_task_ids', 'inherited_task_ids')}
    if manifest['version'] != VERSION or recovery.name != 'pressure_recovery_' + study.digest(identity)[:16]:
        raise ValueError('Recovery identity differs.')
    experiment = experiment_for(recovery)
    parent = _inside(experiment, manifest['parent_run'])
    if recovery.parent.parent != parent:
        raise ValueError('Recovery is not nested under its recorded parent.')
    plan = study.loadplan(parent)
    if (_sha(_inside(experiment, manifest['amendment_path'])) != manifest['amendment_sha256'] or
            _sha(recovery / 'source_snapshot/RECOVERY_20261021.md') != manifest['amendment_sha256']):
        raise ValueError('Frozen recovery protocol changed.')
    for name, expected in manifest['source_hashes'].items():
        if _sha(recovery / 'source_snapshot' / name) != expected or _sha(Path(__file__).with_name(name)) != expected:
            raise ValueError('Frozen recovery implementation changed: ' + name)
    for relative, expected in manifest['parent_files_sha256'].items():
        if _sha(_inside(experiment, relative)) != expected:
            raise ValueError('Original evidence changed during recovery: ' + relative)
    ledger = study.read(experiment / 'data/api_budget.json')
    if _sha(recovery / 'source_snapshot/parent_budget_at_preparation.json') != manifest['initial_budget_snapshot_sha256']:
        raise ValueError('Original budget snapshot changed.')
    if ledger['cap_usd'] != 5:
        raise ValueError('Recovery cumulative budget changed.')
    for key, expected in manifest['initial_budget_attempts_sha256'].items():
        if digest(ledger['attempts'].get(key)) != expected:
            raise ValueError('Original API charge or reservation changed.')
    tasks = {t['task_id']: t for t in plan['tasks']}
    if set(manifest['new_task_ids']) | set(manifest['inherited_task_ids']) != set(tasks):
        raise ValueError('Recovery slots differ from the fixed parent sample.')
    for key, expected in manifest['payload_hashes'].items():
        payload = study.read(recovery / 'payloads' / (key + '.json'))
        if digest(payload) != expected or payload != amended_payload(tasks[key]):
            raise ValueError('Frozen recovery request changed: ' + key)
        prompt = (payload.get('input') or payload.get('messages'))[0]['content']
        if (recovery / 'prompts' / (key + '.txt')).read_text() != prompt:
            raise ValueError('Frozen recovery prompt changed: ' + key)
    return manifest


def estimate(recovery):
    recovery = Path(recovery).resolve()
    manifest = load(recovery)
    tasks = {t['task_id']: t for t in study.loadplan(parent_run(recovery))['tasks']}
    result = []
    for model in study.MODELS:
        own = [tasks[k] for k in manifest['new_task_ids'] if tasks[k]['model'] == model]
        result.append(dict(model=model, pilot_calls=sum(t['phase'] == 'pilot' for t in own),
            main_calls=sum(t['phase'] == 'main' for t in own),
            first_attempt_reservation_ceiling_usd=sum(reservation(model,
                study.read(recovery / 'payloads' / (t['task_id'] + '.json'))) for t in own),
            note='Six new bounded slots; inherited pilots cost nothing again. Existing charges remain in the shared $5 ledger.'))
    return result


class Runner:
    def __init__(self, recovery, keys=None, *, transport=None, concurrency=4,
                 callback=None, retry_delay=2.):
        self.run = Path(recovery).resolve()
        self.manifest = load(self.run)
        self.experiment = experiment_for(self.run)
        self.parent = parent_run(self.run)
        self.plan = study.loadplan(self.parent)
        self.keys = keys or {}
        self.transport = transport
        self.semaphore = asyncio.Semaphore(concurrency)
        self.callback = callback or (lambda progress: None)
        self.retry_delay = retry_delay
        self.raw = self.run / 'raw'
        self.status_path = self.run / 'api_status.json'
        self.status = (study.read(self.status_path) if self.status_path.exists() else
                       dict(tasks={}, returned_models=study.read(self.parent / 'api_status.json')['returned_models'], started=now()))
        for key, entry in self.manifest['inherited_pilots'].items():
            self.status['tasks'].setdefault(key, dict(status='accepted', model=entry['model'],
                phase='pilot', accepted_sha256=entry['sha256'], returned_model=entry['returned_model'],
                inherited=True, origin=entry['path']))
        self.ledger = None
        self.client = None

    def accepted_path(self, task):
        inherited = self.manifest['inherited_pilots'].get(task['task_id'])
        return (_inside(self.experiment, inherited['path']) if inherited else
                self.run / task['response_path'])

    def payload(self, task):
        if task['task_id'] not in self.manifest['new_task_ids']:
            raise ValueError('Inherited pilots must never be sent again.')
        return study.read(self.run / 'payloads' / (task['task_id'] + '.json'))

    def progress(self):
        rows = list(self.status['tasks'].values())
        accepted = sum(r['status'] == 'accepted' for r in rows)
        failed = sum(r['status'] in ('invalid', 'failed', 'interrupted') for r in rows)
        skipped = sum(r['status'] == 'pilot_blocked' for r in rows)
        done = accepted + failed + skipped
        out = dict(total=8, accepted=accepted, failed=failed, skipped=skipped,
            inherited=2, new_planned_calls=6, done=done, remaining=8-done,
            charged_or_reserved_usd=self.ledger.spent if self.ledger else 0,
            cap_usd=5., tasks=self.status['tasks'])
        self.status['progress'] = {k: v for k, v in out.items() if k != 'tasks'}
        save(self.status_path, self.status)
        self.callback(out)
        return out

    async def task(self, task):
        key = task['task_id']
        previous = self.status['tasks'].get(key)
        if previous and previous['status'] in ('accepted', 'invalid', 'failed', 'interrupted'):
            if previous['status'] == 'accepted':
                path = self.accepted_path(task)
                if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != previous['accepted_sha256']:
                    raise ValueError('Accepted response missing or changed; cannot resume.')
            return previous
        model = task['model']
        provider = RATES[model]['provider']
        if not self.keys.get(provider):
            return dict(status='missing_key')
        payload = self.payload(task)
        payload_hash = digest(payload)
        result = None
        async with self.semaphore:
            for number in range(1, MAX_ATTEMPTS + 1):
                attempt_id = digest(['recovery', self.run.name, key, payload_hash, number])
                record_path = self.raw / model / task['phase'] / (key + '_attempt' + str(number) + '.json')
                if attempt_id in self.ledger.data['attempts']:
                    # An interrupted task never silently repurchases uncertain work.
                    result = dict(status='interrupted', reason='prior_attempt_requires_review', attempt_id=attempt_id)
                    break
                try:
                    self.ledger.reserve(attempt_id, reservation(model, payload),
                        dict(run=self.run.name, task_id=key, phase=task['phase'], model=model))
                except BudgetStop as exc:
                    result = dict(status='budget_stopped', reason=str(exc))
                    break
                record = dict(task_id=key, model=model, phase=task['phase'], attempt=number,
                              payload=payload, payload_sha256=payload_hash, started=now(), status='pending')
                save(record_path, record)
                self.status['tasks'][key] = dict(status='running', model=model, phase=task['phase'])
                self.progress()
                started = time.monotonic()
                retry = False
                wait = self.retry_delay
                try:
                    if provider == 'openai':
                        endpoint = 'https://api.openai.com/v1/responses'
                        headers = {'Authorization': 'Bearer ' + self.keys[provider]}
                    else:
                        endpoint = 'https://api.anthropic.com/v1/messages'
                        headers = {'x-api-key': self.keys[provider], 'anthropic-version': '2023-06-01'}
                    response = await self.client.post(endpoint, headers=headers, json=payload)
                    original = response.text
                    safe = _clean(original, self.keys)
                    body_path = record_path.with_suffix('.response.txt')
                    body_path.parent.mkdir(parents=True, exist_ok=True)
                    body_path.write_bytes(response.content if safe == original else safe.encode('utf-8'))
                    record.update(http_status=response.status_code, response_file=body_path.name,
                                  response_sha256=hashlib.sha256(safe.encode()).hexdigest(),
                                  credentials_redacted=safe != original)
                    try:
                        raw = json.loads(safe)
                    except ValueError:
                        raw = {}
                    usage, charge = usage_and_charge(model, raw)
                    if response.status_code in (400, 401, 403, 404, 422, 429) and usage is None:
                        charge = 0.0  # No generation was accepted on these HTTP errors.
                    record['usage'] = usage
                    record['response'] = raw
                    self.ledger.settle(attempt_id, charge, 'received')
                    if response.status_code != 200:
                        result = dict(status='failed', reason='http_' + str(response.status_code))
                        retry = response.status_code in (408, 429, 500, 502, 503, 504)
                        if response.status_code == 429:
                            retry = retry and 'insufficient_quota' not in safe
                        try:
                            wait = max(wait, float(response.headers.get('retry-after', 0)))
                        except ValueError:
                            pass
                    else:
                        try:
                            if usage is None:
                                raise ValueError('missing_or_invalid_usage')
                            payload_out, returned = _extract(model, raw)
                            prior_model = self.status['returned_models'].get(model)
                            if prior_model and prior_model != returned:
                                raise ValueError('model_alias_changed_during_study')
                            self.status['returned_models'][model] = returned
                            issues = study.validate_response(task, payload_out)
                            if issues:
                                result = dict(status='invalid', reason='response_validation', issues=issues)
                            else:
                                accepted = self.accepted_path(task)
                                if accepted.exists():
                                    raise ValueError('Refuse to overwrite an accepted file.')
                                save(accepted, payload_out)
                                result = dict(status='accepted', returned_model=returned,
                                    accepted_sha256=hashlib.sha256(accepted.read_bytes()).hexdigest())
                        except (ValueError, TypeError, KeyError) as exc:
                            reason = str(exc) if str(exc) in ('returned_model_mismatch', 'model_alias_changed_during_study',
                                'incomplete_or_refused', 'refused', 'missing_or_invalid_usage') else type(exc).__name__
                            result = dict(status='invalid', reason=reason)
                except httpx.TransportError as exc:
                    self.ledger.settle(attempt_id, None, 'unknown_charge')
                    result = dict(status='failed', reason=type(exc).__name__)
                    retry = True
                except BudgetStop as exc:
                    result = dict(status='failed', reason='accounting_stop', details=str(exc))
                except asyncio.CancelledError:
                    self.ledger.settle(attempt_id, None, 'interrupted_unknown_charge')
                    record.update(status='interrupted', elapsed_s=time.monotonic() - started)
                    save(record_path, record)
                    self.status['tasks'][key] = dict(status='interrupted', model=model, phase=task['phase'])
                    self.progress()
                    raise
                finally:
                    record['elapsed_s'] = time.monotonic() - started
                    if result:
                        record.update(result)
                    save(record_path, record)
                if retry and number < MAX_ATTEMPTS:
                    self.status['tasks'][key] = dict(status='retry_wait', model=model, phase=task['phase'])
                    self.progress()
                    await asyncio.sleep(wait)
                    continue
                break
        result.update(model=model, phase=task['phase'])
        self.status['tasks'][key] = result
        self.progress()
        return result

    async def execute(self, phase='all'):
        if phase not in ('all', 'pilot', 'main'):
            raise ValueError('phase must be pilot, main, or all')
        with runner_lock(self.experiment):
            load(self.run)
            self.ledger = BudgetLedger(self.experiment)
            self.progress()
            async with httpx.AsyncClient(transport=self.transport,
                    timeout=httpx.Timeout(600., connect=30.)) as client:
                self.client = client
                if phase in ('all', 'pilot'):
                    await asyncio.gather(*(self.task(t) for t in self.plan['tasks']
                                           if t['phase'] == 'pilot'))
                if phase in ('all', 'main'):
                    passed = all(self.status['tasks'].get(t['task_id'], {}).get('status') == 'accepted'
                                 for t in self.plan['tasks'] if t['phase'] == 'pilot')
                    if passed:
                        await asyncio.gather(*(self.task(t) for t in self.plan['tasks'] if t['phase'] == 'main'))
                    else:
                        for task in self.plan['tasks']:
                            if task['phase'] == 'main':
                                self.status['tasks'].setdefault(task['task_id'], dict(
                                    status='pilot_blocked', model=task['model'], phase='main'))
            self.client = None
        return self.progress()


def analyze(recovery):
    """Analyze inherited and amended responses with the unchanged strict science."""
    recovery = Path(recovery).resolve()
    manifest = load(recovery)
    parent = parent_run(recovery)
    experiment = experiment_for(recovery)
    plan = study.loadplan(parent)
    execution_path = recovery / 'api_status.json'
    execution = study.read(execution_path) if execution_path.exists() else {'tasks': {}}
    task_status, chains, rounds, probes = [], [], [], []
    for task in plan['tasks']:
        inherited = manifest['inherited_pilots'].get(task['task_id'])
        path = (_inside(experiment, inherited['path']) if inherited else recovery / task['response_path'])
        status = {key: task[key] for key in ('task_id', 'model', 'phase')}
        status.update(status='missing', issues=[], origin='inherited_parent' if inherited else 'amendment')
        if path.exists():
            if not inherited:
                accepted_record = execution.get('tasks', {}).get(task['task_id'], {})
                if (accepted_record.get('status') != 'accepted' or
                        accepted_record.get('accepted_sha256') != _sha(path)):
                    raise ValueError('Recovered accepted response lacks matching immutable receipt: ' + task['task_id'])
            try:
                payload = study.read(path)
                issues = study.validate_response(task, payload)
            except (ValueError, TypeError, KeyError, AssertionError, OverflowError) as exc:
                issues = [type(exc).__name__ + ': ' + str(exc)]
            status.update(status='invalid' if issues else 'accepted', issues=issues)
            if not issues:
                specs = {c['chain_id']: c for c in task['chains']}
                for chain in payload['chains']:
                    metrics, own_rounds, own_probes = study.task_metrics(specs[chain['chain_id']], chain)
                    chains.append(metrics)
                    rounds.extend(own_rounds)
                    probes.extend(own_probes)
        task_status.append(status)
    hypotheses, contrasts, model_status = [], [], []
    for model in study.MODELS:
        own = [r for r in chains if r['model'] == model]
        pilot_count = sum(r['phase'] == 'pilot' for r in own)
        main = [r for r in own if r['phase'] == 'main']
        model_status.append(dict(model=model, accepted_pilot=pilot_count, expected_pilot=2,
            accepted_main=len(main), expected_main=20, complete=pilot_count == 2 and len(main) == 20,
            accepted_pilot_responses=int(pilot_count == 2), accepted_main_responses=int(len(main) == 20),
            inference_available=False))
        lookup = {(r['block'], r['condition']): r for r in main}
        for name, metric, sign in (('H1', 'sensitivity', -1), ('H2', 'total_cost', 1)):
            differences = []
            for block in range(10):
                if (block, 'no_pressure') not in lookup or (block, 'strong_pressure') not in lookup:
                    continue
                low, high = lookup[block, 'no_pressure'], lookup[block, 'strong_pressure']
                difference = high[metric] - low[metric]
                differences.append(difference)
                contrasts.append(dict(model=model, hypothesis=name, block=block, metric=metric,
                    no_pressure=low[metric], strong_pressure=high[metric], difference=difference))
            effect = mean(differences) if differences else None
            hypotheses.append(dict(model=model, hypothesis=name, metric=metric, expected_sign=sign,
                paired_blocks=len(differences), mean_strong_minus_no=effect,
                descriptive_direction=('unavailable' if effect is None else 'zero' if effect == 0 else
                                       'predicted' if sign*effect > 0 else 'opposite'),
                p_raw=None, p_holm_8=None, paired_bootstrap_95=None, inference_available=False,
                literal_binding_time_test=False))
    original_limitations = study.analyze(parent)['limitations']
    return dict(study_id=manifest['recovery_id'], parent_study_id=plan['study_id'],
        hypotheses=hypotheses, contrasts=contrasts, chains=chains, rounds=rounds, probes=probes,
        task_status=task_status, model_status=model_status,
        limitations=original_limitations + manifest['notes'],
        recovery_metadata={key: manifest[key] for key in ('recovery_id', 'parent_run',
            'inherited_pilots', 'settings_by_model', 'failed_pilot_diagnoses', 'notes')})
