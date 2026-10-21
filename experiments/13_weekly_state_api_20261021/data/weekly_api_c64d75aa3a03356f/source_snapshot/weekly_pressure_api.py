"""Weekly state-supplied API runner with shared experiment-12 budget accounting.

Import and estimates make no requests. Accepted responses are verified against
original provider bytes and frozen request files before state replay or resume.
"""
from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import time

import httpx

from . import weekly_pressure as study
from .batched_pressure_api import (BudgetLedger, BudgetStop, MAX_ATTEMPTS, RATES,
    now, save, digest, reservation, usage_and_charge, runner_lock, _clean, _extract)

SETTINGS = dict(checked_date='2026-10-21', openai_reasoning_effort='none',
    anthropic_thinking='disabled', anthropic_effort='low',
    weekly_output_cap=2048, probe_output_cap=4096,
    interpretation='Completion settings are identical across pressure conditions, not the pressure manipulation.')


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inside(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Evidence reference must be relative and stay inside its root.')
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('Evidence reference escapes its root.')
    return path


def _new(path, value):
    path = Path(path)
    data = (value if isinstance(value, str) else json.dumps(value, indent=2,
            ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Refuse to overwrite frozen request evidence: ' + str(path))
    else:
        with path.open('xb') as stream:
            stream.write(data)


def payload_for(task):
    model = task['model']
    if model not in RATES:
        raise ValueError('Unexpected model.')
    prompt, schema = study.prompt_text(task), study.response_schema(task)
    limit = task.get('max_output_tokens', 4096 if task['phase'] == 'probe' else 2048)
    if RATES[model]['provider'] == 'openai':
        return dict(model=model, input=[dict(role='user', content=prompt)],
            reasoning={'effort': 'none'}, max_output_tokens=limit, service_tier='default', store=False,
            text={'format': {'type': 'json_schema', 'name': 'weekly_beer_choices', 'strict': True, 'schema': schema}})
    return dict(model=model, messages=[dict(role='user', content=prompt)], max_tokens=limit,
        thinking={'type': 'disabled'}, output_config={'effort': 'low',
            'format': {'type': 'json_schema', 'schema': schema}})


def _existing_budget(root):
    path = Path(root) / 'data/api_budget.json'
    if not path.is_file():
        raise BudgetStop('The existing experiment-12 cumulative ledger is required; no replacement budget is created.')
    ledger = json.loads(path.read_text(encoding='utf-8'))
    if ledger.get('cap_usd') != 5 or not isinstance(ledger.get('attempts'), dict):
        raise BudgetStop('The existing shared ledger must retain its $5 cap and prior attempts.')
    for row in ledger['attempts'].values():
        if not isinstance(row, dict) or any(type(row.get(field)) not in (int, float) or
                not math.isfinite(row[field]) or row[field] < 0 for field in ('charge_usd', 'reserve_usd')):
            raise BudgetStop('Shared ledger charges and reservations must be finite and nonnegative.')
    return ledger


def _slots(model, weeks=24):
    return [(model + '_pilot', 'pilot', 1)] + [
        (model + f'_w{week:02d}', 'main', week) for week in range(1, weeks + 1)] + [
        (model + '_probe', 'probe', None)]


def request_files(run, task, payload, *, create):
    """Freeze/verify the exact state, prompt, schema and actual provider payload."""
    directory = Path(run) / 'requests' / task['task_id']
    values = {'task.json': task, 'payload.json': payload,
              'schema.json': study.response_schema(task), 'prompt.txt': study.prompt_text(task)}
    mirrors = {Path(run).parent.parent / 'prompts' / Path(run).name / (task['task_id'] + '.txt'): values['prompt.txt'],
               Path(run).parent.parent / 'prompts' / Path(run).name / (task['task_id'] + '.schema.json'): values['schema.json']}
    if create:
        for name, value in values.items():
            _new(directory / name, value)
        for path, value in mirrors.items():
            _new(path, value)
        _new(directory / 'request.json', dict(task_id=task['task_id'], payload_sha256=digest(payload),
            files_sha256={name: _sha(directory / name) for name in values}))
    manifest = json.loads((directory / 'request.json').read_text())
    if manifest.get('task_id') != task['task_id'] or manifest.get('payload_sha256') != digest(payload):
        raise ValueError('Frozen request identity differs.')
    if set(manifest.get('files_sha256', {})) != set(values):
        raise ValueError('Frozen request inventory differs.')
    for name, value in values.items():
        path = directory / name
        if _sha(path) != manifest['files_sha256'][name]:
            raise ValueError('Frozen request bytes changed: ' + name)
        observed = path.read_text() if name.endswith('.txt') else json.loads(path.read_text())
        if observed != value:
            raise ValueError('Rebuilt request differs from its frozen state: ' + name)
    for path, value in mirrors.items():
        source = directory / ('prompt.txt' if path.suffix == '.txt' else 'schema.json')
        if not path.is_file() or path.read_bytes() != source.read_bytes():
            raise ValueError('Prompt-folder mirror changed: ' + path.name)
    return manifest


class Runner:
    def __init__(self, run, keys=None, *, transport=None, concurrency=2, callback=None, retry_delay=2.):
        self.run = Path(run).resolve()
        self.plan = study.loadplan(self.run)
        self.experiment = self.run.parent.parent
        self.budget_root = study.budget_experiment_for(self.run)
        _existing_budget(self.budget_root)
        self.keys, self.transport = keys or {}, transport
        if type(concurrency) is not int or not 1 <= concurrency <= 2:
            raise ValueError('Use at most two simultaneous model workers.')
        self.concurrency = concurrency
        self.model_semaphore = None
        self.callback = callback or (lambda p: None)
        self.retry_delay = retry_delay
        self.status_path = self.run / 'api_status.json'
        self.status = (json.loads(self.status_path.read_text()) if self.status_path.exists()
                       else dict(tasks={}, models={}, returned_models={}, attempts={}, started=now()))
        self.allowed = {key for model in self.plan['models'] for key, _, _ in _slots(model)}
        if set(self.status['tasks']) - self.allowed:
            raise ValueError('Saved progress contains unexpected tasks.')
        self.ledger = self.client = None
        self.stop = None
        self.stop_reason = 'shared_budget_stop'
        self.raw = self.experiment / 'raw' / self.run.name

    def _audit_attempts(self):
        """Reconcile every purchased attempt with immutable raw evidence."""
        ledger = _existing_budget(self.budget_root)
        entries = self.status.get('attempts', {})
        paths = {p.resolve() for p in self.raw.rglob('*.json')}
        expected = {_inside(self.experiment, r['record_path']) for r in entries.values()}
        if paths != expected:
            raise ValueError('API attempt inventory differs from saved progress; inspect interrupted work.')
        for identity, entry in entries.items():
            path = _inside(self.experiment, entry['record_path'])
            if _sha(path) != entry.get('record_sha256'):
                raise ValueError('API attempt receipt changed.')
            record = json.loads(path.read_text())
            payload = record['payload']
            key, model = record['task_id'], record['model']
            payload_hash = digest(payload)
            expected_id = digest(['weekly-pressure', self.run.name, key, payload_hash, record['attempt']])
            if (identity != expected_id or record['attempt_id'] != identity or
                    record['payload_sha256'] != payload_hash or key not in self.allowed or
                    record['attempt'] not in (1, 2)):
                raise ValueError('API attempt identity differs.')
            task = json.loads((self.run / 'requests' / key / 'task.json').read_text())
            if task.get('task_id') != key or task.get('model') != model:
                raise ValueError('API attempt frozen task differs.')
            request_files(self.run, task, payload, create=False)
            charged = ledger['attempts'].get(identity)
            if not charged or any(charged.get(k) != value for k, value in
                    dict(run=self.run.name, task_id=key, phase=record['phase'],
                         model=model, experiment=self.experiment.name).items()):
                raise ValueError('Shared ledger is missing or changed for a purchased weekly attempt.')
            reserved = reservation(model, payload)
            if abs(charged['reserve_usd'] - reserved) > 1e-12:
                raise ValueError('Weekly attempt reservation changed.')
            expected_charge = None
            if 'response_file' in record:
                body = path.parent / record['response_file']
                if body.parent.resolve() != path.parent.resolve() or _sha(body) != record['response_sha256']:
                    raise ValueError('Original provider response bytes changed.')
                try:
                    raw = json.loads(body.read_text())
                except ValueError:
                    raw = {}
                usage, expected_charge = usage_and_charge(model, raw)
                if record.get('http_status') in (400, 401, 403, 404, 422, 429) and usage is None:
                    expected_charge = 0.
            if expected_charge is None:
                expected_charge = reserved
            if abs(charged['charge_usd'] - expected_charge) > 1e-12:
                raise ValueError('Shared weekly charge differs from original provider usage or unknown-charge reservation.')

    def progress(self):
        rows = list(self.status['tasks'].values())
        accepted = sum(r['status'] == 'accepted' for r in rows)
        failed = sum(r['status'] in ('invalid', 'failed', 'interrupted') for r in rows)
        blocked = sum(r['status'] in ('blocked', 'budget_blocked') for r in rows)
        done = accepted + failed + blocked
        out = dict(total=len(self.allowed), accepted=accepted, failed=failed, blocked=blocked,
            skipped=blocked, done=done, remaining=len(self.allowed)-done,
            charged_or_reserved_usd=(self.ledger.spent if self.ledger else
                sum(v['charge_usd'] for v in _existing_budget(self.budget_root)['attempts'].values())),
            cap_usd=5., tasks=self.status['tasks'], models=self.status['models'])
        self.status['progress'] = {k: v for k, v in out.items() if k not in ('tasks', 'models')}
        save(self.status_path, self.status)
        self.callback(out)
        return out

    def _audit_accepted(self, task):
        row = self.status['tasks'][task['task_id']]
        accepted = self.run / task['response_path']
        if not accepted.is_file() or _sha(accepted) != row.get('accepted_sha256'):
            raise ValueError('Accepted weekly response missing or changed: ' + task['task_id'])
        payload = payload_for(task)
        request_files(self.run, task, payload, create=False)
        record_path = _inside(self.experiment, row['record_path'])
        if _sha(record_path) != row.get('record_sha256'):
            raise ValueError('Accepted API attempt receipt changed.')
        record = json.loads(record_path.read_text())
        if record.get('status') != 'accepted' or record.get('payload_sha256') != digest(payload):
            raise ValueError('Accepted API receipt identity differs.')
        body_path = record_path.parent / record['response_file']
        if body_path.parent.resolve() != record_path.parent.resolve() or _sha(body_path) != record['response_sha256']:
            raise ValueError('Original provider response bytes changed.')
        original_payload, returned_model = _extract(task['model'], json.loads(body_path.read_text()))
        value = json.loads(accepted.read_text())
        if (value != original_payload or returned_model != row.get('returned_model') or
                returned_model != self.status['returned_models'].get(task['model'])):
            raise ValueError('Accepted choices differ from their original provider response.')
        if study.validate_response(task, value):
            raise ValueError('Accepted response no longer passes validation.')
        return value

    def _restore_model(self, model):
        accepted = {}
        for key, phase, week in _slots(model):
            row = self.status['tasks'].get(key, {})
            if row.get('status') == 'accepted':
                if phase != 'pilot' and model + '_pilot' not in accepted:
                    raise ValueError('Accepted weekly response has no accepted model pilot.')
                task = study.build_task(self.plan, model, phase, week=week, accepted=accepted)
                accepted[key] = self._audit_accepted(task)
            elif (self.run / 'accepted' / (key + '.json')).exists():
                raise ValueError('Accepted file has no matching completed receipt; inspect interrupted work.')
        return accepted

    def _block_future(self, model, after_key, reason):
        after = after_key is None
        for key, phase, week in _slots(model):
            if key == after_key:
                after = True
                continue
            if after and self.status['tasks'].get(key, {}).get('status') not in ('accepted', 'invalid', 'failed', 'interrupted'):
                self.status['tasks'][key] = dict(status='budget_blocked' if reason == 'shared_budget_stop' else 'blocked',
                    reason=reason, model=model, phase=phase, week=week)

    async def _request(self, task):
        key, model, phase = task['task_id'], task['model'], task['phase']
        old = self.status['tasks'].get(key, {})
        if old.get('status') in ('invalid', 'failed', 'interrupted'):
            return old
        provider = RATES[model]['provider']
        if not self.keys.get(provider):
            return dict(status='missing_key')
        if self.stop.is_set():
            return dict(status='budget_stopped')
        payload = payload_for(task)
        request_files(self.run, task, payload, create=True)
        payload_hash = digest(payload)
        result = None
        for number in range(1, MAX_ATTEMPTS + 1):
            result = None
            if self.stop.is_set():
                return dict(status='budget_stopped')
            attempt_id = digest(['weekly-pressure', self.run.name, key, payload_hash, number])
            record_path = self.raw / model / phase / (key + '_attempt' + str(number) + '.json')
            if attempt_id in self.ledger.data['attempts']:
                result = dict(status='interrupted', reason='prior_attempt_requires_review', attempt_id=attempt_id)
                break
            try:
                self.ledger.reserve(attempt_id, reservation(model, payload),
                    dict(run=self.run.name, task_id=key, phase=phase, model=model,
                         experiment=self.experiment.name))
            except BudgetStop as exc:
                self.stop.set()
                return dict(status='budget_stopped', reason=str(exc))
            record = dict(task_id=key, model=model, phase=phase, week=task.get('week'), attempt=number,
                attempt_id=attempt_id, payload=payload, payload_sha256=payload_hash,
                started=now(), status='pending')
            save(record_path, record)
            self.status.setdefault('attempts', {})[attempt_id] = dict(
                record_path=record_path.relative_to(self.experiment).as_posix(), record_sha256=_sha(record_path))
            self.status['tasks'][key] = dict(status='running', model=model, phase=phase, week=task.get('week'))
            self.progress()
            retry, wait = False, self.retry_delay
            started = time.monotonic()
            try:
                endpoint = 'https://api.openai.com/v1/responses' if provider == 'openai' else 'https://api.anthropic.com/v1/messages'
                headers = ({'Authorization': 'Bearer ' + self.keys[provider]} if provider == 'openai' else
                           {'x-api-key': self.keys[provider], 'anthropic-version': '2023-06-01'})
                response = await self.client.post(endpoint, headers=headers, json=payload)
                safe = _clean(response.text, self.keys)
                body_path = record_path.with_suffix('.response.txt')
                body_path.write_bytes(response.content if safe == response.text else safe.encode())
                record.update(http_status=response.status_code, response_file=body_path.name,
                    response_sha256=_sha(body_path), credentials_redacted=safe != response.text)
                try:
                    raw = json.loads(safe)
                except ValueError:
                    raw = {}
                usage, charge = usage_and_charge(model, raw)
                if response.status_code in (400, 401, 403, 404, 422, 429) and usage is None:
                    charge = 0.
                record.update(response=raw, usage=usage)
                self.ledger.settle(attempt_id, charge, 'received')
                if response.status_code != 200:
                    result = dict(status='failed', reason='http_' + str(response.status_code))
                    retry = response.status_code in (408, 429) or 500 <= response.status_code <= 599
                    if response.status_code == 429:
                        error = raw.get('error', {}) if isinstance(raw, dict) else {}
                        kind = str(error.get('code', '') or error.get('type', '')).lower() if isinstance(error, dict) else ''
                        if any(word in kind for word in ('quota', 'billing', 'credit', 'spend')):
                            retry = False
                    try:
                        wait = max(wait, float(response.headers.get('retry-after', 0)))
                    except ValueError:
                        pass
                else:
                    try:
                        if usage is None:
                            raise ValueError('missing_or_invalid_usage')
                        value, returned = _extract(model, raw)
                        if self.status['returned_models'].get(model, returned) != returned:
                            raise ValueError('model_alias_changed_during_study')
                        self.status['returned_models'][model] = returned
                        issues = study.validate_response(task, value)
                        if issues:
                            result = dict(status='invalid', reason='response_validation', issues=issues)
                        else:
                            accepted = self.run / task['response_path']
                            if accepted.exists():
                                raise ValueError('Refuse to overwrite an accepted response.')
                            _new(accepted, value)
                            result = dict(status='accepted', returned_model=returned,
                                accepted_sha256=_sha(accepted), attempt_id=attempt_id)
                    except (ValueError, TypeError, KeyError) as exc:
                        allowed = ('returned_model_mismatch', 'model_alias_changed_during_study',
                                   'incomplete_or_refused', 'refused', 'missing_or_invalid_usage')
                        result = dict(status='invalid', reason=str(exc) if str(exc) in allowed else type(exc).__name__)
            except httpx.TransportError as exc:
                self.ledger.settle(attempt_id, None, 'unknown_charge')
                result = dict(status='failed', reason=type(exc).__name__)
                retry = True
            except BudgetStop as exc:
                self.stop.set()
                result = dict(status='failed', reason='accounting_stop', details=str(exc))
            except asyncio.CancelledError:
                self.ledger.settle(attempt_id, None, 'interrupted_unknown_charge')
                record.update(status='interrupted', elapsed_s=time.monotonic()-started)
                save(record_path, record)
                self.status['attempts'][attempt_id] = dict(
                    record_path=record_path.relative_to(self.experiment).as_posix(), record_sha256=_sha(record_path))
                self.status['tasks'][key] = dict(status='interrupted', model=model, phase=phase, week=task.get('week'))
                self.progress()
                raise
            except Exception as exc:
                # Unexpected local failures leave the charge reserved and stop
                # sibling workers before any more requests are purchased.
                self.ledger.settle(attempt_id, None, 'interrupted_unknown_charge')
                result = dict(status='interrupted', reason=type(exc).__name__)
                self.status['tasks'][key] = dict(result, model=model, phase=phase, week=task.get('week'))
                self.progress()
                raise
            finally:
                record.update(elapsed_s=time.monotonic()-started)
                if result:
                    record.update(result)
                save(record_path, record)
                self.status['attempts'][attempt_id] = dict(
                    record_path=record_path.relative_to(self.experiment).as_posix(), record_sha256=_sha(record_path))
            if retry and number < MAX_ATTEMPTS and not self.stop.is_set():
                self.status['tasks'][key] = dict(status='retry_wait', model=model, phase=phase, week=task.get('week'))
                self.progress()
                await asyncio.sleep(wait)
                continue
            if result and result['status'] == 'accepted':
                result.update(record_path=record_path.relative_to(self.experiment).as_posix(), record_sha256=_sha(record_path))
            break
        result.update(model=model, phase=phase, week=task.get('week'))
        self.status['tasks'][key] = result
        self.progress()
        return result

    async def _model(self, model, phase, accepted):
        async with self.model_semaphore:
            if self.stop.is_set():
                return
            self.status['models'][model] = 'running'
            for key, task_phase, week in _slots(model):
                if phase == 'pilot' and task_phase != 'pilot':
                    break
                if key in accepted:
                    continue
                if phase == 'main' and task_phase == 'pilot':
                    self.status['models'][model] = 'needs_pilot'
                    return
                task = study.build_task(self.plan, model, task_phase, week=week, accepted=accepted)
                result = await self._request(task)
                if result['status'] == 'accepted':
                    accepted[key] = self._audit_accepted(task)
                elif result['status'] == 'missing_key':
                    self.status['models'][model] = 'missing_key'
                    return
                elif result['status'] == 'budget_stopped':
                    self.stop.set()
                    self.status['models'][model] = 'budget_stopped'
                    return
                else:
                    self.status['models'][model] = 'stopped_on_' + key
                    self._block_future(model, key, 'prior_model_response_failed')
                    self.progress()
                    return
            self.status['models'][model] = 'complete' if model + '_probe' in accepted else 'pilot_complete'
            self.progress()

    async def execute(self, phase='all'):
        if phase not in ('all', 'pilot', 'main'):
            raise ValueError('phase must be pilot, main, or all')
        self.stop = asyncio.Event()
        self.model_semaphore = asyncio.Semaphore(self.concurrency)
        with runner_lock(self.budget_root):
            study.loadplan(self.run)
            _existing_budget(self.budget_root)
            self.ledger = BudgetLedger(self.budget_root)
            self._audit_attempts()
            # Verify every saved prefix before any model can make a new request.
            prefixes = {model: self._restore_model(model) for model in self.plan['models']}
            self.progress()
            async def worker(model):
                try:
                    return await self._model(model, phase, prefixes[model])
                except BaseException:
                    self.stop_reason = 'runner_error'
                    self.stop.set()
                    raise
            try:
                async with httpx.AsyncClient(transport=self.transport, timeout=httpx.Timeout(180., connect=30.)) as client:
                    self.client = client
                    outcomes = await asyncio.gather(*(worker(model) for model in self.plan['models']), return_exceptions=True)
                    # Drain active workers while the client and shared lock remain open.
                    for outcome in outcomes:
                        if isinstance(outcome, BaseException):
                            raise outcome
            finally:
                self.client = None
                if self.stop.is_set():
                    for model in self.plan['models']:
                        self._block_future(model, None, self.stop_reason)
                    self.progress()
        return self.progress()


def audit_saved(run):
    """Read-only provenance audit and verified choices, without keys or HTTP."""
    runner = Runner(run)
    runner._audit_attempts()
    accepted = {}
    for model in runner.plan['models']:
        accepted.update(runner._restore_model(model))
    return accepted


def estimate(run):
    """Offline full-study sizing scenarios, not forecasts of model choices or bills.

    Ordinary sizing uses fixed seeded integer orders 0..12. Stress sizing changes
    state/history text to eight-digit quantities solely to bound message length.
    Actual requests are separately reserved against the shared cap before sending.
    """
    run = Path(run).resolve()
    plan = study.loadplan(run)
    budget_root = study.budget_experiment_for(run)
    ledger = _existing_budget(budget_root)
    prototype = plan['models'][0]
    accepted, ordinary, stress = {}, [], []
    rng = random.Random(10212026)
    for week in range(1, 25):
        task = study.build_task(plan, prototype, 'main', week=week, accepted=accepted)
        fixture = study.synthetic_fixture(task)
        for choices in fixture['orders'].values():
            for role in choices:
                choices[role] = rng.randrange(13)
        accepted[task['task_id']] = fixture
        ordinary.append(task)
        enlarged = copy.deepcopy(task)
        for states in enlarged['states'].values():
            for state in states:
                for field in study.STATE_COLUMNS:
                    state[field] = 99999999
        for cid, history in enlarged['history'].items():
            enlarged['history'][cid] = [[[99999999, 99999999] for _ in week_rows] for week_rows in history]
        stress.append(enlarged)
    probe = study.build_task(plan, prototype, 'probe', accepted=accepted)

    def cost(task, model):
        task = dict(task, model=model,
            task_id=study.task_id(model, task['phase'], task['week'] if task['phase'] == 'main' else None))
        task['response_path'] = 'accepted/' + task['task_id'] + '.json'
        return reservation(model, payload_for(task))

    rows = []
    for model in plan['models']:
        task = study.build_task(plan, model, 'pilot', week=1, accepted={})
        one = reservation(model, payload_for(task))
        rows.append(dict(model=model, pilot_calls=1, weekly_calls=24, probe_calls=1,
            planned_calls=26, total_calls=26, first_pilot_reservation_usd=one,
            first_attempt_reservation_ceiling_usd=one + sum(cost(t, model) for t in ordinary) + cost(probe, model),
            stressed_input_reservation_usd=one + sum(cost(t, model) for t in stress) + cost(probe, model),
            note='Full 26-call first-attempt sizing only, not remaining work or predicted invoices. Ordinary states use synthetic random 0..12 orders; eight-digit stress is input-size substitution, not a valid trajectory. Retries cost extra and every actual request remains subject to the shared cap.',
            existing_shared_spend_usd=sum(v['charge_usd'] for v in ledger['attempts'].values()), cap_usd=5.))
    return rows
