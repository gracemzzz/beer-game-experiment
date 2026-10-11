"""Versioned student-persona feasibility campaign; imports never make paid calls."""
import asyncio
import json
import random
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
            result.append(dict(state=state, history=[]))
    return result


def prepare(config, output_root=None):
    config.validate()
    paths = [Path(__file__), Path(__file__).with_name('reasoning_protocol.py'),
             Path(__file__).with_name('student_report.py'),
             Path(__file__).with_name('game.py'), Path(__file__).with_name('estimation.py')]
    hashes = {p.name: digest(p.read_text(encoding='utf-8')) for p in paths}
    scientific = config.scientific()
    run_id = digest(dict(config=scientific, source=hashes))[:16]
    directory = Path(output_root or ROOT/'data/runs') / f'student_{config.mode}_{run_id}'
    directory.mkdir(parents=True, exist_ok=True)
    manifest = dict(protocol=PROTOCOL, config=asdict(config), source_hashes=hashes,
                    rates=RATES, created_utc=datetime.now(timezone.utc).isoformat(),
                    calibration_cases=calibration_cases(),
                    calibration_order_seed=config.seed,
                    question_template=make_messages(calibration_cases()[0]['state'], []),
                    order_schema=ORDER_SCHEMA,
                    interpretation='LLM feasibility pilot, not independent human students or a powered confirmatory study.',
                    missed_decision_policy='Repeat last valid submitted order; initial value 4. Flag every fallback. No correctness retries.',
                    failed_screen_policy='Full diagnostic games use predeclared 2048/8192 caps; no claim of validated token treatment.',
                    independence='Separate four-agent chains; weekly decisions and API calls are not independent participants.')
    path = directory/'manifest.json'
    if path.exists():
        old = json.loads(path.read_text(encoding='utf-8'))
        if old['source_hashes'] != hashes or old['config'].get('model') != config.model:
            raise StudyStopped('Scientific settings or source changed; use a new run.')
    else:
        save(path, manifest)
    return directory


def record_metrics(record):
    usage = record.get('usage') or {}
    total = usage.get('output_tokens')
    reasoning = usage.get('reasoning_tokens')
    return dict(output_tokens=total, reasoning_tokens=reasoning,
                nonreasoning_tokens=max(0, total-reasoning) if total is not None and reasoning is not None else None,
                usage_observed=bool(record.get('usage_observed')),
                token_limit=record.get('limit', 0), elapsed_s=record.get('elapsed_s', 0))


async def run_campaign(config=None, client=None, output_root=None):
    """Frozen calibration then independent, paired diagnostic games, with reports."""
    config = config or ReasoningConfig()
    directory = prepare(config, output_root)
    gateway = Gateway(directory, config, client)
    cases = calibration_cases()
    caps = list(config.candidate_caps) + [config.reference_tokens]
    rows, tail, cal_rows, cal_records, rule_checks = [], [], [], [], []
    planned = len(cases)*len(caps) + 2*config.groups_per_condition*4*(config.weeks-config.warmup_weeks+1)
    progress = dict(phase='running', mode=config.mode, planned_requests=planned,
                    groups_complete=0, planned_groups=2*config.groups_per_condition,
                    decisions=0, fallback_decisions=0, stage='calibration')

    def refresh():
        progress.update(estimated_charged_or_reserved_usd=gateway.charged,
                        budget_usd=config.budget_usd,
                        requests_done=gateway.finished,
                        cached_requests=gateway.cached,
                        remaining_requests=max(0, planned-gateway.finished),
                        decisions=sum(r['phase']=='agent' for r in rows),
                        fallback_decisions=sum(bool(r.get('fallback')) for r in rows),
                        updated_utc=datetime.now(timezone.utc).isoformat())
        save(directory/'progress.json', progress)

    def persist_games():
        if rows:
            pd.DataFrame(rows).to_csv(directory/'rounds.csv', index=False)
        if tail:
            pd.DataFrame(tail).to_csv(directory/'continuation.csv', index=False)
        refresh()

    refresh()
    gateway.callback = refresh
    try:
        jobs = [(item, cap) for item in range(len(cases)) for cap in caps]
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
        passed = bool(recommendation.get('passed', recommendation.get('manipulation_screen_passed', False)))
        short = recommendation.get('short_tokens') if passed else config.short_tokens
        adequate = recommendation.get('adequate_tokens') if passed else config.adequate_tokens
        if not isinstance(short, int) or not isinstance(adequate, int):
            raise StudyStopped('Calibration recommendation lacks valid caps.')
        selection = dict(short_tokens=short, adequate_tokens=adequate, calibration_passed=passed,
                         interpretation='feasibility pilot' if passed else 'engineering diagnostic: failed or synthetic calibration',
                         diagnostic_caps_predeclared=dict(short=config.short_tokens, adequate=config.adequate_tokens))
        save(directory/'selection.json', selection)
        progress['stage'] = 'onboarding'
        refresh()
        # All roles receive identical high-effort factual checks before any game choices.
        identities = [(block, condition, role) for block in range(config.groups_per_condition)
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
        for block in range(config.groups_per_condition):
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
