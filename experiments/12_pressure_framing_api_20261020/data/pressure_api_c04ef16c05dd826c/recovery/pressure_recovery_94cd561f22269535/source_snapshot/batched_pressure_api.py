"""Auditable API transport for the separate October 20 pressure-framing study.

No network activity on import. One shared budget covers every run, retry and
unknown-charge attempt in this experiment directory. Credentials never persist.
"""
from __future__ import annotations

import asyncio
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time

import httpx

from . import batched_pressure as study


AUTHORIZED_CAP_USD = 5.0
MAX_ATTEMPTS = 2
RATES = {
    'gpt-6-luna': dict(provider='openai', input=.10, cached=.01, output=.50),
    'gpt-5.6-luna': dict(provider='openai', input=.20, cached=.02, output=1.20),
    'gpt-5.6-sol': dict(provider='openai', input=4., cached=.40, output=20.),
    'claude-haiku-5-5': dict(provider='anthropic', input=.10, cached=.01, output=.50),
}
PRICE_DATE = '2026-10-20'
PRICE_SOURCES = {
    m: ('https://developers.openai.com/api/docs/models/' + m
        if r['provider'] == 'openai' else
        'https://platform.claude.com/docs/en/models/haiku-5-5/overview')
    for m, r in RATES.items()
}


class BudgetStop(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def experiment_for(run):
    return Path(run).resolve().parent.parent


def payload_for(task):
    model = task['model']
    if model not in RATES:
        raise ValueError('Model not in the prospectively specified comparison.')
    schema = study.response_schema(task)
    prompt = study.prompt_text(task)
    limit = task.get('max_output_tokens', 8192 if task['phase'] == 'pilot' else 16384)
    if RATES[model]['provider'] == 'openai':
        return dict(model=model, input=[dict(role='user', content=prompt)],
                    reasoning={'effort': 'low'}, max_output_tokens=limit,
                    service_tier='default', store=False,
                    text={'format': {'type': 'json_schema', 'name': 'beer_chain',
                                     'strict': True, 'schema': schema}})
    # Use Claude's supported JSON-schema subset; the same full constraints are
    # independently enforced by study.validate_response after receipt.
    def portable(node):
        if isinstance(node, dict):
            return {k: portable(v) for k, v in node.items()
                    if k not in ('minimum', 'maximum', 'minItems', 'maxItems')}
        if isinstance(node, list):
            return [portable(v) for v in node]
        return node
    return dict(model=model, max_tokens=limit, messages=[dict(role='user', content=prompt)],
                thinking={'type': 'adaptive'},
                output_config={'effort': 'low', 'format': {
                    'type': 'json_schema', 'schema': portable(schema)}})


def reservation(model, payload):
    """Conservative input-byte bound, including schema and framing headroom."""
    r = RATES[model]
    input_bound = len(json.dumps(payload, ensure_ascii=False).encode('utf-8')) + 4096
    if input_bound > 265000:
        raise BudgetStop('Request exceeds the fixed accounting bound.')
    output_bound = payload.get('max_output_tokens', payload.get('max_tokens'))
    input_rate = r['input'] * (1.25 if r['provider'] == 'openai' else 2.)
    # The byte bound can exceed Claude's 100K-token threshold even when actual
    # text tokenization is much smaller. Reserve its 5x long-context rates in
    # that case; settle later from the measured inclusive input count.
    context_multiplier = 5 if r['provider'] == 'anthropic' and input_bound > 100000 else 1
    return context_multiplier * (input_bound * input_rate + output_bound * r['output']) / 1e6


def _usage_and_charge_unchecked(model, raw):
    if not isinstance(raw, dict):
        return None, None
    u = raw.get('usage')
    if not isinstance(u, dict) or 'output_tokens' not in u or 'input_tokens' not in u:
        return None, None
    def counts_valid(value):
        if isinstance(value, dict):
            return all(counts_valid(v) for k, v in value.items() if 'token' in k or isinstance(v, dict))
        return value is None or (type(value) is int and value >= 0)
    if not counts_valid(u) or type(u['output_tokens']) is not int or type(u['input_tokens']) is not int:
        return None, None
    r = RATES[model]
    output = int(u['output_tokens'])
    if r['provider'] == 'openai':
        inp = int(u['input_tokens'])
        details = u.get('input_tokens_details') or {}
        if not isinstance(details, dict):
            return None, None
        cached = int(details.get('cached_tokens', 0))
        # If cache writes are not itemized, reserve the extra 25% for all
        # noncached input; report this as conservative accounting, not invoice.
        writes = int(details.get('cache_write_tokens', inp - cached))
        if cached > inp or writes > inp - cached:
            return None, None
        charge = ((inp - cached) * r['input'] + cached * r['cached']
                  + writes * r['input'] * .25 + output * r['output']) / 1e6
    else:
        ordinary = int(u['input_tokens'])
        cached = int(u.get('cache_read_input_tokens', 0))
        writes = int(u.get('cache_creation_input_tokens', 0))
        creation = u.get('cache_creation') or {}
        if not isinstance(creation, dict):
            return None, None
        five = int(creation.get('ephemeral_5m_input_tokens', 0))
        hour = int(creation.get('ephemeral_1h_input_tokens', 0))
        unknown = max(0, writes - five - hour)
        inp = ordinary + cached + writes
        charge = (ordinary * r['input'] + cached * r['cached']
                  + five * r['input'] * 1.25 + (hour + unknown) * r['input'] * 2
                  + output * r['output']) / 1e6
        if inp > 100000:
            charge *= 5
    reasoning = int((u.get('output_tokens_details') or {}).get(
        'reasoning_tokens', (u.get('output_tokens_details') or {}).get('thinking_tokens', 0)))
    if reasoning > output:
        return None, None
    return dict(input_tokens=inp, cached_input_tokens=cached, output_tokens=output,
                reasoning_tokens=reasoning), charge


def usage_and_charge(model, raw):
    try:
        return _usage_and_charge_unchecked(model, raw)
    except (ValueError, TypeError, AttributeError, OverflowError, KeyError):
        return None, None


class BudgetLedger:
    def __init__(self, experiment, cap_usd=AUTHORIZED_CAP_USD):
        if not 0 < cap_usd <= AUTHORIZED_CAP_USD:
            raise ValueError('The newly authorized total is at most $5, including retries.')
        self.path = Path(experiment) / 'data' / 'api_budget.json'
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding='utf-8'))
            if self.data['cap_usd'] != cap_usd:
                raise BudgetStop('Existing cumulative cap differs; it is never silently reset.')
        else:
            self.data = dict(cap_usd=cap_usd, authorization='User specified $5 total on 2026-10-20',
                             price_date=PRICE_DATE, prices=RATES, sources=PRICE_SOURCES,
                             scope='All runs and attempts of experiment 12', attempts={})
            save(self.path, self.data)

    @property
    def spent(self):
        return sum(a['charge_usd'] for a in self.data['attempts'].values())

    def reserve(self, identity, amount, metadata):
        if not math.isfinite(amount) or amount < 0:
            raise ValueError('Reservation must be finite and nonnegative.')
        if identity in self.data['attempts']:
            raise BudgetStop('Attempt already reserved; preserve its unknown charge instead of resending.')
        if self.spent + amount > self.data['cap_usd'] + 1e-12:
            raise BudgetStop('The $5 cumulative budget cannot cover another worst-case request.')
        self.data['attempts'][identity] = dict(metadata, status='reserved',
                                              reserve_usd=amount, charge_usd=amount, created=now())
        save(self.path, self.data)

    def settle(self, identity, charge, status):
        row = self.data['attempts'][identity]
        row.update(status=status, completed=now())
        if charge is not None:
            if not math.isfinite(charge) or charge < 0:
                raise ValueError('Negative charge.')
            row['charge_usd'] = charge
        save(self.path, self.data)
        if row['charge_usd'] > row['reserve_usd'] + 1e-12:
            raise BudgetStop('Provider usage exceeded reservation; stop and review accounting.')


@contextmanager
def runner_lock(experiment):
    path = Path(experiment) / 'data' / '.api_runner.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise BudgetStop('Another runner or an interrupted-session lock exists. Inspect before resuming.')
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)


def _clean(text, keys):
    for value in keys.values():
        if value:
            text = text.replace(value, '[REDACTED_CREDENTIAL]')
    return re.sub(r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}', '[REDACTED_CREDENTIAL]', text)


def _extract(model, raw):
    if not isinstance(raw, dict):
        raise ValueError('Response must be a JSON object.')
    returned = raw.get('model', '')
    # OpenAI may return a dated snapshot of the exact requested alias. Preserve
    # that ID and require all requests for that model to use the same backend ID.
    matches = returned == model or (RATES[model]['provider'] == 'openai'
        and re.fullmatch(re.escape(model) + r'-\d{4}-\d{2}-\d{2}', returned) is not None)
    if not matches:
        raise ValueError('returned_model_mismatch')
    if RATES[model]['provider'] == 'openai':
        if raw.get('status') != 'completed':
            raise ValueError('incomplete_or_refused')
        content = [c for item in raw.get('output', []) if item.get('type') == 'message'
                   for c in item.get('content', [])]
        if any(c.get('type') == 'refusal' for c in content):
            raise ValueError('refused')
        text = ''.join(c.get('text', '') for c in content if c.get('type') == 'output_text')
    else:
        if raw.get('stop_reason') != 'end_turn':
            raise ValueError('incomplete_or_refused')
        text = ''.join(c.get('text', '') for c in raw.get('content', []) if c.get('type') == 'text')
    return json.loads(text), returned


class Runner:
    def __init__(self, run, keys=None, *, transport=None, concurrency=4,
                 callback=None, retry_delay=2.0):
        self.run = Path(run).resolve()
        self.experiment = experiment_for(run)
        self.plan = study.loadplan(run)
        self.keys = keys or {}
        self.transport = transport
        self.semaphore = asyncio.Semaphore(concurrency)
        self.callback = callback or (lambda progress: None)
        self.retry_delay = retry_delay
        self.raw = self.experiment / 'raw' / self.run.name
        self.status_path = self.run / 'api_status.json'
        self.status = (json.loads(self.status_path.read_text()) if self.status_path.exists()
                       else dict(tasks={}, returned_models={}, started=now()))
        self.ledger = None
        self.client = None

    def progress(self):
        rows = list(self.status['tasks'].values())
        total = len(self.plan['tasks'])
        accepted = sum(r['status'] == 'accepted' for r in rows)
        failed = sum(r['status'] in ('invalid', 'failed', 'interrupted') for r in rows)
        skipped = sum(r['status'] == 'pilot_blocked' for r in rows)
        done = accepted + failed + skipped
        out = dict(total=total, accepted=accepted, failed=failed, skipped=skipped,
                   done=done, remaining=total - done,
                   charged_or_reserved_usd=self.ledger.spent if self.ledger else 0,
                   cap_usd=AUTHORIZED_CAP_USD, tasks=self.status['tasks'])
        self.status['progress'] = out.copy()
        self.status['progress'].pop('tasks')
        save(self.status_path, self.status)
        self.callback(out)
        return out

    async def task(self, task):
        key = task['task_id']
        previous = self.status['tasks'].get(key)
        if previous and previous['status'] in ('accepted', 'invalid', 'failed', 'interrupted'):
            if previous['status'] == 'accepted':
                path = self.run / task['response_path']
                if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != previous['accepted_sha256']:
                    raise ValueError('Accepted response missing or changed; cannot resume.')
            return previous
        model = task['model']
        provider = RATES[model]['provider']
        if not self.keys.get(provider):
            return dict(status='missing_key')
        payload = payload_for(task)
        payload_hash = digest(payload)
        result = None
        async with self.semaphore:
            for number in range(1, MAX_ATTEMPTS + 1):
                attempt_id = digest([self.run.name, key, payload_hash, number])
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
                                accepted = self.run / task['response_path']
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
        tasks = self.plan['tasks']
        with runner_lock(self.experiment):
            self.ledger = BudgetLedger(self.experiment)
            self.progress()
            async with httpx.AsyncClient(transport=self.transport, timeout=httpx.Timeout(300., connect=30.)) as client:
                self.client = client
                if phase in ('all', 'pilot'):
                    await asyncio.gather(*(self.task(t) for t in tasks if t['phase'] == 'pilot'))
                if phase in ('all', 'main'):
                    pilot = [t for t in tasks if t['phase'] == 'pilot']
                    passed = (len(pilot) == 4 and {t['model'] for t in pilot} == set(RATES)
                        and all(self.status['tasks'].get(t['task_id'], {}).get('status') == 'accepted' for t in pilot))
                    eligible = set(RATES) if passed else set()
                    for t in tasks:
                        if t['phase'] == 'main' and t['model'] not in eligible and self.keys.get(RATES[t['model']]['provider']):
                            self.status['tasks'].setdefault(t['task_id'], dict(status='pilot_blocked', model=t['model'], phase='main'))
                    await asyncio.gather(*(self.task(t) for t in tasks if t['phase'] == 'main' and t['model'] in eligible))
        self.client = None
        return self.progress()


def estimate(run):
    plan = study.loadplan(run)
    rows = []
    for model in RATES:
        tasks = [t for t in plan['tasks'] if t['model'] == model]
        ceiling = sum(reservation(model, payload_for(t)) for t in tasks)
        rows.append(dict(model=model, pilot_calls=1, main_calls=1,
                         first_attempt_reservation_ceiling_usd=ceiling,
                         note='Worst-case output cap, conservative input bound; not expected spend.'))
    return rows
