"""Reproducible paired Beer Games with shared initial choices and revision budgets."""
from __future__ import annotations

import asyncio
import json
import math
import shutil
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .economy_protocol import (EconomyConfig, COMMON, PROTOCOL, calibration_bank, demand_schedule,
                               display_state, manipulation_screen, messages, selected_order,
                               supply_line_probes)
from .economy_transport import Gateway
from .game import BeerGame, ROLES
from .student_profiles import PROFILE_IDS, profiles, assignment
from .reasoning_protocol import (ORDER_SCHEMA, RULES_SCHEMA, RULE_ANSWERS,
                                 StudyStopped, decide, digest, save)

from .economy_pricing import RATES, PRICING_URL, cost_envelope, CALIBRATION_CAP_USD

ROOT = Path(__file__).resolve().parents[2]
LEGACY_SPEND = 5.19360675
SOURCE_NAMES = ('economy_protocol.py', 'economy_transport.py', 'economy_study.py',
                'economy_report.py', 'economy_pricing.py', 'student_profiles.py', 'game.py', 'reasoning_protocol.py', 'estimation.py')


def source_paths():
    return {**{name: Path(__file__).with_name(name) for name in SOURCE_NAMES},
            **{'profiles/'+key+'.json': ROOT/'config/student_profiles'/(key+'.json') for key in PROFILE_IDS}}


def source_hashes():
    return {name: digest(path.read_text(encoding='utf-8')) for name, path in source_paths().items()}


def prepare(config, root=ROOT, calibration_only=False, calibration_run=None):
    config.validate()
    hashes = source_hashes()
    calibration_source = str(Path(calibration_run).resolve()) if calibration_run else None
    run_id = digest(dict(config=config.scientific(), sources=hashes, calibration_source=calibration_source))[:16]
    directory = Path(root)/'data/runs'/f'economy_{config.mode}_{run_id}'
    directory.mkdir(parents=True, exist_ok=True)
    manifest = dict(protocol=PROTOCOL, config=asdict(config), source_hashes=hashes,
                    fingerprint=config.fingerprint(), created_utc=datetime.now(timezone.utc).isoformat(),
                    common_prompt=COMMON, student_profiles=profiles(), order_schema=ORDER_SCHEMA, rates=RATES, calibration_source=calibration_source,
                    calibration_bank=calibration_bank(config.seed), probes=supply_line_probes(),
                    temperature='omitted; model default held constant in every condition',
                    initial_choice_coupling='Within a block/week/role only, identical complete prompts share one initial draw. Never share across independent blocks.',
                    treatment='Initial submission only versus initial submission plus one high-effort revision of at most 8192 generated tokens.',
                    hypotheses={'H1_sensitivity': 'Short has lower negative order response per extra pipeline case in matched probes (mechanism proxy, not dynamic beta).',
                                'H2_cost': 'Short has higher complete chain cost.',
                                'H3_bullwhip': 'Short has higher mean role order/customer-demand variance ratio over decision weeks; primary outcome.'},
                    missing_policy='Missing initial choice or technical error stops; only token-exhausted revision retains its valid same-state initial submission.',
                    analysis='Independent paired blocks; fixed family H1/H2/H3; paired t intervals/tests with Holm, exploratory until justified power plan. No inference below 8 pairs.',
                    human_data='None. Four fictional profiles, not sampled or validated students.',
                    pricing_note='Conservative Flex estimate: all uncached input charged at cache-write rate .0625 per million; ordinary input rate is .05. Output .25; cached reads .005. Unknown or non-Flex outcomes reserve/charge standard rates; no automatic standard fallback.',
                    pricing_source=PRICING_URL, cost_envelope=cost_envelope(config),
                    calibration_cost_cap_usd=CALIBRATION_CAP_USD,
                    model_version_note='Official API ID gpt-6-luna; no dated snapshot is published. Requested and returned IDs must match; long-term alias drift remains a reproducibility limitation.')
    path = directory/'manifest.json'
    if path.exists():
        old = json.loads(path.read_text(encoding='utf-8'))
        if old['fingerprint'] != config.fingerprint() or old['source_hashes'] != hashes or old['config']['campaign_id'] != config.campaign_id:
            raise StudyStopped('Run identity mismatch. Use a new replicate; do not overwrite evidence.')
    else:
        save(path, manifest)
        folder = directory/'source_implementation'
        folder.mkdir(exist_ok=True)
        for name, source in source_paths().items():
            (folder/name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, folder/name)
    return directory


def campaign_allowance(config, directory, root):
    """The original $10 authorization spans the old pilot and all new v2/v3 runs.

    A different campaign explicitly configured by the user has its own cap.
    The exclusive campaign lock prevents two live workers spending concurrently.
    """
    if config.mode != 'api' or config.campaign_id != '20261011':
        return config, 0.0
    other = LEGACY_SPEND
    for manifest_path in (Path(root)/'data/runs').glob('*_api_*/manifest.json'):
        if manifest_path.parent.resolve() == directory.resolve():
            continue
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('protocol') in ('student-high-anytime-revision-v2', 'student-high-economy-revision-v3') and manifest['config']['campaign_id'] == config.campaign_id:
            other += sum(json.loads(p.read_text(encoding='utf-8')).get('charge_usd', 0)
                         for p in (manifest_path.parent/'requests').glob('*.json'))
    remaining_local_cap = min(config.budget_usd, 10.0-other, 2.95-(other-LEGACY_SPEND))
    if remaining_local_cap <= 0:
        raise StudyStopped('The existing campaign or revised-experiment allowance is exhausted.')
    return replace(config, budget_usd=remaining_local_cap), other


async def gather_checked(*tasks):
    """Wait for all reserved in-flight work before writing a partial report."""
    results = await asyncio.gather(*tasks, return_exceptions=True)
    errors = [v for v in results if isinstance(v, BaseException)]
    if errors:
        raise errors[0]
    return results


async def initial_call(gateway, state, history, identity):
    return await gateway.request(identity | {'phase': 'initial'}, messages(state, history),
                                 gateway.config.initial_tokens, synthetic=json.dumps({'order': state['demand']}))


async def revision_call(gateway, state, history, initial, identity):
    first = decide(initial)
    if not first.valid:
        raise StudyStopped('No valid current-state initial submission; no substitute order.')
    return await gateway.request(identity | {'phase': 'revision'}, messages(state, history, first.order),
                                 gateway.config.revision_tokens, synthetic=json.dumps({'order': state['demand']}))


async def paired_choices(gateway, states, histories, identity):
    """Common random draw for identical inputs; otherwise separate calls.

    State equality is checked on the exact complete message, not just inventory.
    Pair/block is in the cache key, preserving independent simulation replications.
    """
    identical = messages(states[0], histories[0]) == messages(states[1], histories[1])
    if identical:
        first = await initial_call(gateway, states[0], histories[0], identity | {'condition': 'shared'})
        starts = [first, first]
    else:
        starts = await gather_checked(*(initial_call(gateway, s, h, identity | {'condition': c})
                                        for s, h, c in zip(states, histories, ('short', 'adequate'))))
    # Validate both initials before buying another generation.
    for first in starts:
        selected_order(first)
    revised = await revision_call(gateway, states[1], histories[1], starts[1], identity | {'condition': 'adequate'})
    return [selected_order(starts[0]) | {'shared_initial': identical},
            selected_order(starts[1], revised) | {'shared_initial': identical}]


def load_calibration(parent, config):
    """Verify the exact fixed bank and raw calls; no repeated calibration charges."""
    parent = Path(parent).resolve()
    manifest = json.loads((parent/'manifest.json').read_text(encoding='utf-8'))
    if (manifest['protocol'] != PROTOCOL or manifest['common_prompt'] != COMMON
            or manifest['source_hashes'] != source_hashes() or manifest['calibration_bank'] != calibration_bank(config.seed)):
        raise StudyStopped('Calibration protocol, scientific source, or bank differs. Recalibrate the new protocol.')
    for field in ('model', 'effort', 'mode', 'initial_tokens', 'revision_tokens', 'timeout_s'):
        if manifest['config'][field] != getattr(config, field):
            raise StudyStopped('Calibration incompatible: '+field)
    records = [json.loads(p.read_text(encoding='utf-8')) for p in (parent/'requests').glob('*.json')]
    rows = []
    for case in calibration_bank(config.seed):
        chosen = {}
        for phase in ('initial', 'revision'):
            matches = [r for r in records if r['identity'] == dict(stage='calibration', item=case['case_id'], phase=phase)
                       and r.get('status') == 'ok']
            if len(matches) != 1:
                raise StudyStopped('Calibration lacks exactly one measured response per required phase.')
            record = matches[0]
            fields = ('protocol', 'identity', 'messages', 'limit', 'schema', 'requested_model', 'reasoning', 'mode', 'config_fingerprint', 'service_tier')
            expected_messages = messages(case['state'], case['history'], decide(chosen['initial']).order if phase == 'revision' else None)
            if (record['request_key'] != digest({k: record[k] for k in fields})
                    or record['messages'] != expected_messages or record['requested_model'] != config.model
                    or record['reasoning'] != {'effort': 'high'} or record['config_fingerprint'] != manifest['fingerprint']
                    or record['limit'] != getattr(config, phase+'_tokens') or record['schema'] != ORDER_SCHEMA
                    or (config.mode == 'api' and (not record.get('usage_observed') or record.get('synthetic')))):
                raise StudyStopped('Calibration raw provenance mismatch.')
            chosen[phase] = record
        first, revised = chosen['initial'], chosen['revision']
        rows.append(dict(case_id=case['case_id'], split=case['split'], history_length=len(case['history']),
                         initial_valid=decide(first).valid, revision_valid=decide(revised).valid,
                         initial_output_tokens=first['usage']['output_tokens'], initial_reasoning_tokens=first['usage']['reasoning_tokens'],
                         revision_output_tokens=revised['usage']['output_tokens'], revision_reasoning_tokens=revised['usage']['reasoning_tokens'],
                         initial_charge_usd=first['charge_usd'], revision_charge_usd=revised['charge_usd']))
    return rows


async def run_study(config=EconomyConfig(), client=None, *, root=ROOT, calibration_only=False, on_progress=None, calibration_run=None):
    root = Path(root)
    directory = prepare(config, root, calibration_only, calibration_run)
    lock = None
    lock_path = root/'data/campaigns'/f'{digest(config.campaign_id)[:16]}.lock'
    if config.mode == 'api':
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            lock = lock_path.open('x', encoding='utf-8')
            lock.write(str(directory)); lock.flush()
        except FileExistsError:
            raise StudyStopped('A live campaign lock exists. Check the running process before removing a stale lock.') from None
    try:
        config, prior = campaign_allowance(config, directory, root)
        return await _run(config, client, directory, root, prior, calibration_only, on_progress, calibration_run)
    finally:
        if lock is not None:
            lock.close()
            lock_path.unlink(missing_ok=True)


async def _run(config, client, directory, root, prior, calibration_only, on_progress, calibration_run):
    from .economy_report import build_report
    gateway = Gateway(directory, config, client)
    calibration, rows, probes = [], [], []
    state = dict(stage='calibration', phase='running', run_directory=str(directory.resolve()),
                 calibration_completed=0, calibration_expected=16, completed_steps=0,
                 planned_requests=32, current_week=0, planned_groups=0, groups_complete=0,
                 fallback_decisions=0, budget_usd=config.budget_usd, prior_campaign_spend_usd=prior,
                 calibration_budget_usd=CALIBRATION_CAP_USD)

    def progress(**updates):
        state.update(updates)
        state.update(estimated_charged_or_reserved_usd=gateway.charged,
                     campaign_charged_or_reserved_usd=prior+gateway.charged,
                     requests_done=gateway.finished, cached_requests=gateway.cached,
                     active_requests=gateway.active, updated_utc=datetime.now(timezone.utc).isoformat())
        save(directory/'progress.json', state)
        save(root/'reports/ACTIVE_ECONOMY_RUN.json', dict(run=str(directory.resolve()), progress=str((directory/'progress.json').resolve())))
        if on_progress:
            on_progress(state.copy())

    gateway.callback = progress
    progress()
    try:
        # Both fixed splits are logged before games. No tuning on order outcomes.
        if calibration_run:
            calibration = load_calibration(calibration_run, config)
            pd.DataFrame(calibration).to_csv(directory/'calibration.csv', index=False)
            save(directory/'calibration_reuse.json', dict(source=str(Path(calibration_run).resolve()),
                                                         new_calibration_calls=0, new_calibration_charges=0))
            progress(calibration_completed=16, planned_requests=0)
        for case in ([] if calibration_run else calibration_bank(config.seed)):
            ident = dict(stage='calibration', item=case['case_id'])
            first = await initial_call(gateway, case['state'], case['history'], ident)
            revised = None
            if decide(first).valid:
                revised = await revision_call(gateway, case['state'], case['history'], first, ident)
            record = dict(case_id=case['case_id'], split=case['split'], history_length=len(case['history']),
                          initial_valid=decide(first).valid, revision_valid=bool(revised and decide(revised).valid),
                          initial_output_tokens=(first.get('usage') or {}).get('output_tokens', 0),
                          initial_reasoning_tokens=(first.get('usage') or {}).get('reasoning_tokens', 0),
                          revision_output_tokens=((revised or {}).get('usage') or {}).get('output_tokens', 0),
                          revision_reasoning_tokens=((revised or {}).get('usage') or {}).get('reasoning_tokens', 0),
                          initial_charge_usd=first.get('charge_usd', 0),
                          revision_charge_usd=(revised or {}).get('charge_usd', 0))
            calibration.append(record)
            pd.DataFrame(calibration).to_csv(directory/'calibration.csv', index=False)
            progress(calibration_completed=len(calibration), completed_steps=gateway.finished)
            # Stop when a completion/headroom gate is already impossible. This
            # depends on response validity/usage, never quantities or outcomes.
            split_rows = [r for r in calibration if r['split'] == case['split']]
            impossible = (not record['initial_valid']
                          or record['initial_output_tokens'] >= .9*config.initial_tokens
                          or sum(not r['revision_valid'] for r in split_rows) >= 2)
            if config.mode == 'api' and impossible:
                save(directory/'manipulation.json', manipulation_screen(calibration))
                raise StudyStopped('Feasibility completion/headroom gate cannot pass. Stopped calibration early to avoid further charges; no games purchased.')
            if len(calibration) == 4:
                initial_median = float(np.median([r['initial_output_tokens'] for r in calibration]))
                total_median = float(np.median([r['initial_output_tokens']+r['revision_output_tokens'] for r in calibration]))
                ratio = initial_median/total_median if total_median > 0 else None
                quick_pass = (all(r['initial_valid'] and r['initial_reasoning_tokens'] > 0
                                  and r['revision_reasoning_tokens'] > 0 for r in calibration)
                              and sum(r['revision_valid'] for r in calibration) >= 3
                              and ratio is not None and ratio <= .75)
                save(directory/'quick_screen.json', dict(cases=4, median_initial_tokens=initial_median,
                     median_combined_tokens=total_median, initial_to_combined_ratio=ratio,
                     passed=bool(quick_pass), synthetic=config.mode == 'offline',
                     note='First four development cases only; not independent validation or a hypothesis test.'))
                progress(quick_screen_passed=bool(quick_pass))
                if config.mode == 'api' and not quick_pass:
                    save(directory/'manipulation.json', manipulation_screen(calibration))
                    raise StudyStopped('Four-case quick computation screen failed. Stopped before the remaining calibration and games.')

        screen = manipulation_screen(calibration, synthetic=config.mode == 'offline')
        save(directory/'manipulation.json', screen)
        if calibration_only:
            progress(stage='calibration_complete', phase='complete')
            return directory
        if config.mode == 'api' and not screen['passed']:
            raise StudyStopped('Feasibility screen failed. No games purchased; no automatic diagnostic override.')

        # Freeze the full requested sample, horizon and demand paths BEFORE outcomes.
        # Conservative forecast assumes zero shared-initial savings.
        pair_steps = (config.weeks-4)*4
        initial_mean = float(np.mean([r['initial_charge_usd'] for r in calibration]))
        revision_mean = float(np.mean([r['revision_charge_usd'] for r in calibration]))
        forecast = 1.25*((pair_steps+8)*(2*initial_mean+revision_mean) + 4*initial_mean)
        plan = dict(pairs=config.groups_per_condition, weeks=config.weeks,
                    forecast_per_pair_usd=forecast, calibration_charged_usd=gateway.charged,
                    forecast_total_remaining_usd=forecast*config.groups_per_condition,
                    paths=[demand_schedule(config.weeks, config.seed+10000+b) for b in range(config.groups_per_condition)],
                    profile_assignments=[assignment(config.seed, b) for b in range(config.groups_per_condition)],
                    unit='independent paired four-role chains; shared initial draw within pair where prompts match',
                    minimum_inference_pairs=8, power='Not powered; sample size requires a prospective effect/variance calculation.')
        plan_path = directory/'plan.json'
        if plan_path.exists():
            saved = json.loads(plan_path.read_text(encoding='utf-8'))
            if saved['pairs'] != plan['pairs'] or saved['paths'] != plan['paths']:
                raise StudyStopped('Frozen plan differs; refusing to change it.')
            plan = saved
        else:
            save(plan_path, plan)
        if (config.mode == 'api' and not (directory/'rounds.csv').exists()
                and gateway.charged + plan['forecast_total_remaining_usd'] > config.budget_usd):
            raise StudyStopped('Pre-game forecast exceeds remaining hard cap. Saved calibration; no partial game purchased. Increase an explicitly authorized cap or choose a new prospective plan.')
        progress(stage='onboarding', planned_groups=2*plan['pairs'],
                 planned_requests=(0 if calibration_run else 32)+plan['pairs']*(4+3*(pair_steps+8)), onboarding_completed=0)
        for block in range(plan['pairs']):
            # Four factual checks are shared pre-treatment screens, not human validation.
            for role_index, role in enumerate(ROLES):
                prompt = [{'role': 'system', 'content': COMMON}, {'role': 'user', 'content': json.dumps({
                    'role': role, 'participant_profile': profiles()[plan['profile_assignments'][block][role_index]], 'questions': {
                    'backlog_includes_current_unfilled_demand': 'Does current backlog already include unfilled demand from this week?',
                    'factory_order_week_7_arrival_week': 'When does factory production started in week 7 arrive?',
                    'three_week_backlog_cost': 'What is the cost of five backlogged cases at the end of each of three weeks?'}})}]
                r = await gateway.request(dict(stage='rules', block=block, role=role), prompt, config.initial_tokens,
                                          schema=RULES_SCHEMA, synthetic=json.dumps(RULE_ANSWERS))
                if r.get('status') != 'ok' or r.get('response_status') != 'completed' or json.loads(r.get('text') or 'null') != RULE_ANSWERS:
                    raise StudyStopped('Common rules screen failed; no chain replacement or corrective strategy coaching.')
                progress(onboarding_completed=state.get('onboarding_completed', 0)+1, completed_steps=gateway.finished)

            # Each pair's independent matched probes are separate from game history.
            progress(stage='probes')
            for case in supply_line_probes():
                profile_id = plan['profile_assignments'][block][ROLES.index(case['role'])]
                choices = await paired_choices(gateway, [case['state'] | {'profile_id': profile_id}]*2, [[], []],
                                               dict(stage='probe', block=block, item=case['case_id']))
                for condition, decision in zip(('short', 'adequate'), choices):
                    probes.append(dict(block=block, condition=condition, role=case['role'], profile_id=profile_id, level=case['level'], **decision))
                pd.DataFrame(probes).to_csv(directory/'probes.csv', index=False)
                progress(completed_steps=gateway.finished)

            games = [BeerGame(), BeerGame()]
            histories = [[[] for _ in ROLES] for _ in range(2)]
            last_orders = [[4]*4, [4]*4]
            progress(stage='games')
            for week, demand in enumerate(plan['paths'][block], 1):
                observed = [game.observe(demand) for game in games]
                shown = [[display_state(game, s) for s in obs] for game, obs in zip(games, observed)]
                for c in range(2):
                    for i in range(4):
                        shown[c][i]['profile_id'] = plan['profile_assignments'][block][i]
                if week <= 4:
                    choices_by_role = [[dict(order=4, order_source='fixed_practice', fallback=False)]*2 for _ in ROLES]
                else:
                    choices_by_role = await gather_checked(*(paired_choices(gateway,
                        [shown[c][i] for c in range(2)], [histories[c][i] for c in range(2)],
                        dict(stage='game', block=block, week=week, role=role)) for i, role in enumerate(ROLES)))
                for c, condition in enumerate(('short', 'adequate')):
                    orders = []
                    for i in range(4):
                        choice = choices_by_role[i][c]
                        rows.append(observed[c][i] | choice | dict(block=block, condition=condition,
                                    customer_demand=demand, profile_id=plan['profile_assignments'][block][i],
                                    phase='practice' if week <= 4 else 'model'))
                        histories[c][i].append(shown[c][i] | {'order': choice['order']})
                        orders.append(choice['order'])
                    games[c].commit(orders)
                    last_orders[c] = orders
                pd.DataFrame(rows).to_csv(directory/'rounds.csv', index=False)
                progress(current_week=week, completed_steps=gateway.finished)
            for c, condition in enumerate(('short', 'adequate')):
                for _ in range(12):
                    for s, order in zip(games[c].observe(demand), last_orders[c]):
                        rows.append(s | dict(block=block, condition=condition, customer_demand=demand,
                                             profile_id=plan['profile_assignments'][block][ROLES.index(s['role'])],
                                             phase='automatic', order=order, order_source='fixed_terminal_policy', fallback=False))
                    games[c].commit(last_orders[c])
            pd.DataFrame(rows).to_csv(directory/'rounds.csv', index=False)
            progress(groups_complete=2*(block+1))
        progress(stage='complete', phase='complete', completed_steps=gateway.finished, planned_requests=gateway.finished)
        return directory
    except StudyStopped as exc:
        progress(phase='stopped', reason=str(exc))
        return directory
    except BaseException as exc:
        # Do not persist exception strings: external exceptions can include secrets.
        progress(phase='stopped', reason='Interrupted or software error: '+type(exc).__name__)
        raise
    finally:
        build_report(directory, root=root)
