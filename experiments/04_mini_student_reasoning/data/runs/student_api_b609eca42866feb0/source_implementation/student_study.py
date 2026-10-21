"""Versioned student-persona feasibility campaign; imports never make paid calls."""
import asyncio
import json
import random
import shutil
import statistics
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .game import BeerGame, ROLES, continuation, demand_path
from .reasoning_protocol import (
    Gateway, ReasoningConfig, PROTOCOL, RATES, ORDER_SCHEMA, digest, save,
    make_messages, decide, rules_messages, rules_result, screen_caps, StudyStopped,
    RULES_SCHEMA, RULE_ANSWERS,
)

ROOT = Path(__file__).resolve().parents[2]


def exact_request_record(record, path, config):
    fields = ('protocol', 'identity', 'messages', 'limit', 'schema', 'requested_model',
              'reasoning', 'mode', 'config_fingerprint')
    specification = {name: record.get(name) for name in fields}
    key = digest(specification)
    return (record.get('protocol') == PROTOCOL
            and record.get('reasoning') == {'effort': config.effort}
            and record.get('timeout_s') == config.timeout_s
            and record.get('identity', {}).get('cap') == record.get('limit')
            and record.get('request_key') == key
            and path.stem in (key, key+'_retry_1', key+'_retry_2'))


def calibration_cases():
    """Fixed hypothetical states; never taken from the new game's outcomes."""
    result = []
    for role in ROLES:
        for inventory, backlog, supply, demand in (
            (12, 0, 12, 4), (0, 8, 0, 8), (24, 0, 12, 8),
            (0, 32, 16, 8), (0, 96, 0, 0), (120, 0, 24, 0),
        ):
            shared = {r: 12 for r in ROLES}
            shared[role] = inventory
            state = dict(week=12, role=role, inventory=inventory, backlog=backlog,
                         supply_line=supply, demand=demand, received=0, shipped=0,
                         net_inventory=inventory-backlog, cost=.5*inventory+backlog,
                         shared_inventory=shared)
            if inventory > 0 and backlog == 0 and demand > 0:
                state.update(received=demand, shipped=demand)
            result.append(dict(state=state, history=[]))
    return result


def validate_state_repair(original, corrected):
    """Only the declared receipt/shipment placeholder correction is permitted."""
    if not isinstance(original, list) or len(original) != len(corrected):
        raise StudyStopped('Calibration state-bank size differs.')
    changed = []
    for item, (old, new) in enumerate(zip(original, corrected)):
        expected = json.loads(json.dumps(old))
        state = expected['state']
        if (state['inventory'] > 0 and state['backlog'] == 0 and state['demand'] > 0
                and state['received'] == 0 and state['shipped'] == 0):
            state.update(received=state['demand'], shipped=state['demand'])
        if expected != new:
            raise StudyStopped('State repair may change only the declared receipt/shipment placeholders.')
        if old != new:
            changed.append(item)
    return changed


def prepare(config, output_root=None, calibration_parent=None, *, calibration_only=False, calibration_reuse=None,
            recheck_rejections=False, correct_calibration_states=False):
    config.validate()
    paths = [Path(__file__), Path(__file__).with_name('reasoning_protocol.py'),
             Path(__file__).with_name('student_report.py'),
             Path(__file__).with_name('game.py'), Path(__file__).with_name('estimation.py')]
    hashes = {p.name: digest(p.read_text(encoding='utf-8')) for p in paths}
    scientific = config.scientific()
    execution_scope = 'calibration' if calibration_only else ('game' if calibration_reuse else 'campaign')
    run_id = digest(dict(config=scientific, source=hashes, execution_scope=execution_scope,
                         calibration_source=calibration_reuse))[:16]
    directory = Path(output_root or ROOT/'data/runs') / f'student_{config.mode}_{run_id}'
    directory.mkdir(parents=True, exist_ok=True)
    manifest = dict(protocol=PROTOCOL, config=asdict(config), source_hashes=hashes,
                    calibration_only=calibration_only, execution_scope=execution_scope,
                    explicit_access_recheck_after_external_change=recheck_rejections,
                    calibration_state_correction=correct_calibration_states,
                    rates=RATES, created_utc=datetime.now(timezone.utc).isoformat(),
                    calibration_cases=calibration_cases(),
                    calibration_order_seed=config.seed,
                    question_template=make_messages(calibration_cases()[0]['state'], []),
                    order_schema=ORDER_SCHEMA,
                    interpretation='LLM feasibility pilot, not independent human students or a powered confirmatory study.',
                    missed_decision_policy='Repeat last valid submitted order; initial value 4. Flag every fallback. No correctness retries.',
                    failed_screen_policy='Diagnostic games use the largest candidate and reference caps; no claim of validated token treatment.',
                    sample_planning='Select up to configured chain pairs by calibration token costs before game outcomes; 15% forecast margin and common onboarding reservations.',
                    independence='Separate four-agent chains; weekly decisions and API calls are not independent participants.')
    path = directory/'manifest.json'
    if path.exists():
        old = json.loads(path.read_text(encoding='utf-8'))
        if old['source_hashes'] != hashes or old['config'].get('model') != config.model:
            raise StudyStopped('Scientific settings or source changed; use a new run.')
    else:
        save(path, manifest)
    snapshots = directory/'source_implementation'
    snapshots.mkdir(exist_ok=True)
    for source in paths:
        target = snapshots/source.name
        if not target.exists():
            shutil.copy2(source, target)
    if calibration_parent:
        parent = Path(calibration_parent)
        if parent.resolve() == directory.resolve():
            raise StudyStopped('Calibration parent must be a different preserved run.')
        imported = []
        reused, excluded = [], []
        bank = calibration_cases()
        parent_manifest = json.loads((parent/'manifest.json').read_text(encoding='utf-8'))
        parent_bank = parent_manifest['calibration_cases']
        changed_items = []
        if parent_bank != bank:
            if not correct_calibration_states:
                raise StudyStopped('Calibration states differ; explicit restricted state repair is required.')
            changed_items = validate_state_repair(parent_bank, bank)
        inherited_path = parent/'calibration_import.json'
        inherited = json.loads(inherited_path.read_text(encoding='utf-8')).get('correction', {}) if inherited_path.exists() else {}
        original_bank = inherited.get('original_calibration_cases', parent_bank)
        if inherited:
            changed_items = validate_state_repair(original_bank, bank)
        allowed_caps = set(config.candidate_caps) | {config.reference_tokens}
        cache = directory/'requests'
        cache.mkdir(exist_ok=True)
        for path in (parent/'requests').glob('*.json'):
            record = json.loads(path.read_text(encoding='utf-8'))
            identity = record.get('identity', {})
            item = identity.get('item')
            if identity.get('stage') != 'calibration' or type(item) is not int or not 0 <= item < len(bank):
                raise StudyStopped('Only compatible calibration calls can be imported.')
            compatible = (record.get('requested_model') == config.model
                          and record.get('requested_effort') == config.effort
                          and record.get('config_fingerprint') == config.fingerprint()
                          and (record.get('messages') == make_messages(parent_bank[item]['state'], [])
                               or (path.name in inherited.get('excluded_request_files', [])
                                   and record.get('messages') == make_messages(original_bank[item]['state'], [])))
                          and record.get('schema') == ORDER_SCHEMA
                          and record.get('limit') in allowed_caps
                          and exact_request_record(record, path, config)
                          and record.get('status') != 'pending')
            if not compatible:
                raise StudyStopped('Calibration import failed exact prompt/model/effort/cap/cache compatibility.')
            target = cache/path.name
            if not target.exists():
                shutil.copy2(path, target)
            elif target.read_bytes() != path.read_bytes():
                raise StudyStopped('Calibration import would overwrite a different request record.')
            imported.append(path.name)
            if record['messages'] == make_messages(bank[item]['state'], []):
                reused.append(path.name)
            else:
                excluded.append(path.name)
        save(directory/'calibration_import.json', dict(parent=str(parent.resolve()),
             parent_manifest=parent_manifest,
             imported_records=imported, reused_records=reused, originals_unchanged=True,
             correction=(dict(fields=['received', 'shipped'], changed_items=changed_items,
                              original_calibration_cases=original_bank,
                              excluded_request_files=excluded, reused_request_files=reused,
                              reason='Post-shipment positive inventory and fulfilled demand require consistent receipts and shipments; corrected before game outcomes.')
                         if changed_items else {}),
             compatibility='Exact rendered prompts, model, effort, caps, schema and scientific config fingerprint.',
             budget='Imported charges/reservations remain in the new local $10 ledger; they are not purchased again.'))
    return directory


def load_calibration(parent, config):
    """Validate an immutable completed calibration before any new API calls."""
    parent = Path(parent).resolve()
    try:
        manifest = json.loads((parent/'manifest.json').read_text(encoding='utf-8'))
        progress = json.loads((parent/'progress.json').read_text(encoding='utf-8'))
        prior = manifest['config']
        if progress.get('phase') != 'complete' or manifest.get('protocol') != PROTOCOL:
            raise ValueError('Calibration source is incomplete or uses a different protocol.')
        expected_sources = {'student_study.py', 'reasoning_protocol.py', 'student_report.py', 'game.py', 'estimation.py'}
        if (set(manifest.get('source_hashes', {})) != expected_sources
                or manifest.get('question_template') != make_messages(calibration_cases()[0]['state'], [])
                or manifest.get('order_schema') != ORDER_SCHEMA
                or manifest.get('calibration_cases') != calibration_cases()):
            raise ValueError('Calibration manifest provenance is incomplete or differs from the current task.')
        for field in ('mode', 'model', 'effort', 'candidate_caps', 'reference_tokens', 'timeout_s', 'onboarding_tokens'):
            if json.dumps(prior[field]) != json.dumps(asdict(config)[field]):
                raise ValueError('Calibration settings differ: '+field)
        for name, expected in manifest['source_hashes'].items():
            if digest(Path(__file__).with_name(name).read_text(encoding='utf-8')) != expected:
                raise ValueError('Calibration source code has changed; recalibrate before new games.')
        prior_config = ReasoningConfig(**prior)
        bank = calibration_cases()
        import_path = parent/'calibration_import.json'
        correction = json.loads(import_path.read_text(encoding='utf-8')).get('correction', {}) if import_path.exists() else {}
        if correction:
            validate_state_repair(correction['original_calibration_cases'], bank)
        allowed = set(config.candidate_caps) | {config.reference_tokens}
        selected = {}
        all_records = []
        for path in (parent/'requests').glob('*.json'):
            record = json.loads(path.read_text(encoding='utf-8'))
            identity = record.get('identity', {})
            if identity.get('stage') != 'calibration':
                continue
            item, cap = identity.get('item'), identity.get('cap')
            excluded_original = (path.name in correction.get('excluded_request_files', [])
                                 and type(item) is int and 0 <= item < len(bank)
                                 and record.get('messages') == make_messages(correction['original_calibration_cases'][item]['state'], []))
            if (type(item) is not int or not 0 <= item < len(bank) or cap not in allowed
                    or record.get('limit') != cap or record.get('status') == 'pending'
                    or record.get('requested_model') != config.model
                    or record.get('requested_effort') != config.effort
                    or record.get('config_fingerprint') != prior_config.fingerprint()
                    or bool(record.get('synthetic')) != (config.mode == 'offline')
                    or record.get('schema') != ORDER_SCHEMA
                    or not exact_request_record(record, path, config)
                    or (record.get('messages') != make_messages(bank[item]['state'], []) and not excluded_original)):
                raise ValueError('Calibration raw request provenance is incompatible.')
            all_records.append((path, record))
            if excluded_original:
                continue
            suffix = path.stem.split('_retry_')
            attempt = int(suffix[1]) if len(suffix) == 2 else 0
            if (item, cap) not in selected or attempt > selected[item, cap][0]:
                selected[item, cap] = (attempt, record)
        if set(selected) != {(i, cap) for i in range(len(bank)) for cap in allowed}:
            raise ValueError('Calibration does not contain the full matched state bank.')
        records = [selected[i, cap][1] for i in range(len(bank)) for cap in sorted(allowed)]
        recommendation = screen_caps(records, config.candidate_caps, config.reference_tokens, expected_n=24)
        provenance = dict(parent=str(parent), parent_manifest_sha256=digest(manifest),
                          source_mode=config.mode, requested_model=config.model, effort=config.effort,
                          returned_models=sorted({r['returned_model'] for r in records if r.get('returned_model')}),
                          original_calibration_estimated_usd=sum(r.get('charge_usd', 0) for _, r in all_records),
                          local_budget_includes_parent_charges=False,
                          request_files=[dict(path=str(p), sha256=digest(r)) for p, r in all_records],
                          validation='Completed full matched bank; exact model, effort, prompts, schema, caps, timeout, source code and original fingerprints.')
        return records, recommendation, provenance
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise StudyStopped(str(exc) if isinstance(exc, ValueError) else 'Cannot read a compatible completed calibration.') from None


def record_metrics(record):
    usage = record.get('usage') or {}
    total = usage.get('output_tokens')
    reasoning = usage.get('reasoning_tokens')
    return dict(output_tokens=total, reasoning_tokens=reasoning,
                nonreasoning_tokens=max(0, total-reasoning) if total is not None and reasoning is not None else None,
                usage_observed=bool(record.get('usage_observed')),
                token_limit=record.get('limit', 0), elapsed_s=record.get('elapsed_s', 0))


async def run_campaign(config=None, client=None, output_root=None, calibration_parent=None,
                       *, calibration_only=False, calibration_run=None, on_progress=None, recheck_rejections=False,
                       correct_calibration_states=False):
    """Frozen calibration then independent, paired diagnostic games, with reports."""
    config = config or ReasoningConfig()
    config.validate()
    if calibration_run and (calibration_parent or calibration_only):
        raise StudyStopped('Select either calibration reuse for games or a calibration action.')
    external = load_calibration(calibration_run, config) if calibration_run else None
    directory = prepare(config, output_root, calibration_parent,
                        calibration_only=calibration_only,
                        calibration_reuse=external[2] if external else None,
                        recheck_rejections=recheck_rejections, correct_calibration_states=correct_calibration_states)
    gateway = Gateway(directory, config, client, recheck_rejections=recheck_rejections)
    cases = calibration_cases()
    caps = list(config.candidate_caps) + [config.reference_tokens]
    rows, tail, cal_rows, cal_records, rule_checks = [], [], [], [], []
    calibration_steps = 0 if external else len(cases)*len(caps)
    planned = calibration_steps + (0 if calibration_only else 2*config.groups_per_condition*4*(config.weeks-config.warmup_weeks+1))
    progress = dict(phase='running', mode=config.mode, planned_requests=planned,
                    calibration_only=calibration_only, run_directory=str(directory.resolve()),
                    groups_complete=0, planned_groups=2*config.groups_per_condition,
                    decisions=0, fallback_decisions=0, stage='calibration')

    def refresh():
        progress.update(estimated_charged_or_reserved_usd=gateway.charged,
                        budget_usd=config.budget_usd,
                        requests_done=gateway.finished,
                        cached_requests=gateway.cached,
                        active_requests=gateway.active,
                        completed_steps=(0 if external else len(cal_records))+len(rule_checks)+sum(r['phase']=='agent' for r in rows),
                        calibration_completed=len(cal_records),
                        calibration_expected=len(cases)*len(caps),
                        onboarding_completed=len(rule_checks),
                        remaining_requests=max(0, planned-gateway.finished),
                        decisions=sum(r['phase']=='agent' for r in rows),
                        fallback_decisions=sum(bool(r.get('fallback')) for r in rows),
                        updated_utc=datetime.now(timezone.utc).isoformat())
        save(directory/'progress.json', progress)
        save(ROOT/'reports/ACTIVE_STUDENT_RUN.json', dict(directory=str(directory.resolve()),
              progress=str((directory/'progress.json').resolve()), phase=progress['phase']))
        if on_progress:
            try:
                on_progress(dict(progress))
            except Exception as exc:
                # Rendering must not turn a received model answer into a failure.
                progress['progress_display_error'] = type(exc).__name__

    def persist_games():
        if rows:
            pd.DataFrame(rows).to_csv(directory/'rounds.csv', index=False)
        if tail:
            pd.DataFrame(tail).to_csv(directory/'continuation.csv', index=False)
        refresh()

    refresh()
    gateway.callback = refresh
    try:
        jobs = [] if external else [(item, cap) for item in range(len(cases)) for cap in caps]
        if external:
            cal_records, recommendation, provenance = external
            save(directory/'calibration_reuse.json', provenance)
            for record in cal_records:
                item = record['identity']['item']
                decision = decide(record)
                cal_rows.append(dict(item=item, role=cases[item]['state']['role'], cap=record['limit'],
                                     valid_decision=decision.valid, order=decision.order if decision.valid else None,
                                     fallback=decision.fallback, failure_reason=decision.reason,
                                     response_status=record.get('response_status'), synthetic=config.mode=='offline',
                                     **record_metrics(record)))
            pd.DataFrame(cal_rows).to_csv(directory/'calibration.csv', index=False)
        random.Random(config.seed).shuffle(jobs)
        for offset in range(0, len(jobs), config.concurrency):
            batch = jobs[offset:offset+config.concurrency]
            tasks = []
            for item, cap in batch:
                case = cases[item]
                tasks.append(gateway.request(
                    dict(stage='calibration', item=item, cap=cap),
                    make_messages(case['state'], case['history']), cap,
                    synthetic=json.dumps({'order': case['state']['demand']})))
            answers = await asyncio.gather(*tasks, return_exceptions=True)
            fatal = None
            for (item, cap), record in zip(batch, answers):
                if isinstance(record, BaseException):
                    fatal = fatal or record
                    continue
                decision = decide(record)
                cal_records.append(record)
                cal_rows.append(dict(item=item, role=cases[item]['state']['role'], cap=cap,
                                     valid_decision=decision.valid, order=decision.order if decision.valid else None,
                                     fallback=decision.fallback, failure_reason=decision.reason,
                                     response_status=record.get('response_status'),
                                     synthetic=config.mode=='offline', **record_metrics(record)))
            pd.DataFrame(cal_rows).to_csv(directory/'calibration.csv', index=False)
            refresh()
            if fatal:
                raise fatal
        recommendation = screen_caps(cal_records, config.candidate_caps, config.reference_tokens, expected_n=24)
        save(directory/'calibration_recommendation.json', recommendation)
        save(ROOT/'reports/LATEST_CALIBRATION.json', dict(directory=str((Path(calibration_run) if external else directory).resolve()),
             mode=config.mode, manipulation_screen_passed=recommendation.get('manipulation_screen_passed', False)))
        if calibration_only:
            progress.update(phase='complete', stage='calibration_complete', planned_groups=0)
            refresh()
            return directory
        passed = bool(recommendation.get('passed', recommendation.get('manipulation_screen_passed', False)))
        short = recommendation.get('short_tokens') if passed else max(config.candidate_caps)
        adequate = recommendation.get('adequate_tokens') if passed else config.reference_tokens
        if not isinstance(short, int) or not isinstance(adequate, int):
            raise StudyStopped('Calibration recommendation lacks valid caps.')
        if config.mode == 'offline':
            planned_groups = config.groups_per_condition
            pair_forecast = None
        else:
            # Cost-based sample planning precedes every game outcome. No order,
            # bullwhip coefficient, cost outcome, or significance enters it.
            selected_records = [r for r in cal_records if r['limit'] in (short, adequate) and r.get('usage_observed')]
            means = [statistics.mean(r['usage']['output_tokens'] for r in selected_records if r['limit']==cap)
                     for cap in (short, adequate)]
            projected_input = statistics.mean(r['usage']['input_tokens'] for r in selected_records) + config.weeks*35
            per_decision = (statistics.mean(means)*RATES['output'] + projected_input*RATES['input'])/1e6
            pair_forecast = (8*(config.weeks-config.warmup_weeks)*per_decision*1.15
                             + 8*config.onboarding_tokens*RATES['output']/1e6)
            planned_groups = min(config.groups_per_condition, int(max(0, config.budget_usd-gateway.charged)/pair_forecast))
        selection = dict(short_tokens=short, adequate_tokens=adequate, calibration_passed=passed,
                         interpretation='feasibility pilot' if passed else 'engineering diagnostic: failed or synthetic calibration',
                         diagnostic_caps_predeclared=dict(short=max(config.candidate_caps), adequate=config.reference_tokens),
                         groups_per_condition=planned_groups,
                         requested_max_groups_per_condition=config.groups_per_condition,
                         forecast_cost_per_pair_usd=pair_forecast,
                         sample_selection_basis='Calibration token charges with 15% forecast margin, before any game outcomes.')
        selection_path = directory/'selection.json'
        if selection_path.exists():
            frozen = json.loads(selection_path.read_text(encoding='utf-8'))
            if (frozen['short_tokens'] != short or frozen['adequate_tokens'] != adequate
                    or frozen['calibration_passed'] != passed
                    or type(frozen['groups_per_condition']) is not int
                    or not 0 <= frozen['groups_per_condition'] <= config.groups_per_condition):
                raise StudyStopped('Saved pre-game sample plan is incompatible; no plan changed after outcomes.')
            selection = frozen
            planned_groups = frozen['groups_per_condition']
        else:
            save(selection_path, selection)
        progress['planned_groups'] = 2*planned_groups
        planned = calibration_steps + 2*planned_groups*4*(config.weeks-config.warmup_weeks+1)
        progress['planned_requests'] = planned
        if planned_groups < 1:
            raise StudyStopped('Calibration completed; remaining authorized budget cannot cover one forecast full pair. No partial game purchased.')
        progress['stage'] = 'onboarding'
        refresh()
        # All roles receive identical high-effort factual checks before any game choices.
        identities = [(block, condition, role) for block in range(planned_groups)
                      for condition in ('short', 'adequate') for role in ROLES]
        for offset in range(0, len(identities), config.concurrency):
            batch = identities[offset:offset+config.concurrency]
            tasks = [gateway.request(dict(stage='rules', block=b, condition=c, role=r),
                                     rules_messages(r), config.onboarding_tokens,
                                     schema=RULES_SCHEMA, synthetic=json.dumps(RULE_ANSWERS)) for b, c, r in batch]
            records = await asyncio.gather(*tasks, return_exceptions=True)
            fatal = None
            for (b, c, r), record in zip(batch, records):
                if isinstance(record, BaseException):
                    fatal = fatal or record
                    continue
                result = rules_result(record)
                # rules_result may expose named failed fields; keep the complete result.
                ok = bool(result.get('passed')) if isinstance(result, dict) else bool(result)
                rule_checks.append(dict(block=b, condition=c, role=r, passed=ok,
                                        result=result, **record_metrics(record)))
            save(directory/'rules_checks.json', rule_checks)
            refresh()
            if fatal:
                raise fatal
        if not all(r['passed'] for r in rule_checks):
            raise StudyStopped('Factual onboarding failed; responses preserved, no games purchased.')
        progress['stage'] = 'games'
        refresh()
        # Chains share a demand schedule, but histories and states are always separate.
        chains = {}
        for block in range(planned_groups):
            for condition in ('short', 'adequate'):
                gid = f'b{block:03d}_{condition}'
                chains[gid] = dict(game=BeerGame(), history=[[] for _ in ROLES],
                                   last=[4]*4, block=block, condition=condition)
        for week, demand in enumerate(demand_path(config.weeks), 1):
            states = {gid: chain['game'].observe(demand) for gid, chain in chains.items()}
            decisions = {}
            if week > config.warmup_weeks:
                jobs = [(gid, i) for gid in chains for i in range(4)]
                # Random starts reduce systematic service-load/condition ordering differences.
                random.Random(config.seed+week).shuffle(jobs)
                for offset in range(0, len(jobs), config.concurrency):
                    batch = jobs[offset:offset+config.concurrency]
                    tasks = []
                    for gid, i in batch:
                        chain = chains[gid]
                        cap = short if chain['condition']=='short' else adequate
                        tasks.append(gateway.request(dict(stage='decision', group=gid, role=ROLES[i], week=week),
                                     make_messages(states[gid][i], chain['history'][i]), cap,
                                     synthetic=json.dumps({'order': states[gid][i]['demand']})))
                    answers = await asyncio.gather(*tasks, return_exceptions=True)
                    fatal = next((r for r in answers if isinstance(r, BaseException)), None)
                    for (gid, i), record in zip(batch, answers):
                        if isinstance(record, BaseException):
                            continue
                        decision = decide(record, last_valid_order=chains[gid]['last'][i],
                                          emergency_order_limit=config.emergency_order_limit)
                        if decision.reason == 'emergency_scale':
                            raise StudyStopped('Emergency-scale model submission preserved; game stopped without clipping the order.')
                        decisions[gid, i] = (decision, record)
                    refresh()
                    if fatal:
                        raise fatal
            for gid, chain in chains.items():
                orders = []
                for i, state in enumerate(states[gid]):
                    meta = dict(group_id=gid, block=chain['block'], condition=chain['condition'])
                    if week <= config.warmup_weeks:
                        order = 4
                        outcome = dict(phase='warmup', valid_decision=False, fallback=False, failure_reason='',
                                       output_tokens=0, reasoning_tokens=0, nonreasoning_tokens=0,
                                       usage_observed=False,
                                       token_limit=0, elapsed_s=0.)
                    else:
                        decision, record = decisions[gid, i]
                        order = decision.order
                        if decision.valid:
                            chain['last'][i] = order
                        outcome = dict(phase='agent', valid_decision=decision.valid,
                                       fallback=decision.fallback, failure_reason=decision.reason,
                                       submitted_order=decision.submitted_order,
                                       **record_metrics(record))
                    orders.append(order)
                    rows.append(dict(state, order=order, **meta, **outcome))
                    chain['history'][i].append(dict(state, order=order, fallback=outcome['fallback']))
                chain['game'].commit(orders)
            progress['current_week'] = week
            persist_games()
        for gid, chain in chains.items():
            terminal = continuation(chain['game'], demand, config.continuation_weeks)
            tail.extend(dict(row, group_id=gid, block=chain['block'], condition=chain['condition']) for row in terminal)
            progress['groups_complete'] += 1
        progress.update(phase='complete', stage='complete')
        persist_games()
    except BaseException as exc:
        progress.update(phase='stopped', reason=str(exc) if isinstance(exc, StudyStopped) else type(exc).__name__)
        persist_games()
        raise
    finally:
        from .student_report import build_report
        build_report(directory)
        (ROOT/'reports').mkdir(exist_ok=True)
        (ROOT/'reports/LATEST_REPORT.txt').write_text(str(directory/'REPORT.docx')+'\n'+str(directory/'REPORT.md')+'\n', encoding='utf-8')
    return directory
