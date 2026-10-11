"""Prospective initial-choice / extra-deliberation protocol, 11 October 2026.

The treatment is an additional revision opportunity, not a smaller allowance on
the initial decision. Every scored action must come from a valid current-state
model response. Legacy evidence and its source files remain unchanged.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass

import numpy as np

from .game import BeerGame, ROLES
from .reasoning_protocol import MODEL, ORDER_SCHEMA, digest, decide, StudyStopped
from .student_profiles import profiles, PROFILE_IDS

PROTOCOL = 'student-high-anytime-revision-v2'
TASK = 'How many cases do you order this week? Return the integer in the order field.'
COMMON = '''You are a hypothetical second-year undergraduate business student at
the University at Buffalo taking part in a classroom Beer Game. You have ordinary
introductory business knowledge and have not previously played this game. Make
the decisions you would submit in this role, trying to minimize the team's total
inventory holding and backlog costs. This is a fictional participant. Do not
invent personal characteristics, deliberate mistakes, or a particular bias.
Your participant_profile supplies your consistent personality and background.
Use that same fictional profile throughout the game, without inventing other traits.

The positions are retailer, wholesaler, distributor and factory. Each week you
order cases from your supplier; the factory instead starts production. Submit a
nonnegative integer. Zero is allowed. There is no suggested quantity or maximum.
Inventory costs $0.50 per case per week and backlog costs $1 per case per week.
There is no sales revenue, ordering fee, bulk discount or production capacity limit.

Your display is after this week's deliveries and automatic shipments, before
your new order. Backlog already contains all unfilled current and previous demand
and persists until supplied. Inventory is remaining available stock. Outstanding
orders cannot be canceled and are not inventory. Deliveries_due lists cases
already dispatched, arriving next week then the following week; for the factory
these are production completions. Awaiting_dispatch lists your other outstanding
cases still awaiting shipment. These are separate quantities, not extra demand.
A new order reaches the supplier next week and shipment takes two more weeks;
earliest arrival is week t+3, with further delays when the supplier has shortages.
Factory production started in week t arrives in week t+3 even when current stock
and outstanding production are zero. A new order cannot change today's shipments.

You see all positions' remaining inventories, your local state, and your own
previous rounds. Other positions' orders and backlogs and future customer demand
are hidden. There is no communication or outside tool use. Initially each position
has 12 cases and the flow is 4 cases per week. The first four practice rounds
automatically order 4. Thereafter, end-customer demand is drawn independently
each week: integers 0 through 8 are equally likely. Everyone knows this
distribution, but future draws are hidden and only the retailer observes current
end-customer demand directly. The last decision week is not disclosed. After decisions
end, 12 automatic weeks are scored with customer demand held at its last value
and each position's order held at its own last submitted quantity.

Submit a current choice first. If a revision opportunity is provided, you may
keep or change that choice. Your latest completed submission for this same week
is the order that will be placed. An unfinished revision leaves that submission
in force. Return only the structured order.'''


@dataclass(frozen=True)
class AnytimeConfig:
    mode: str = 'offline'
    replicate_id: str = 'anytime-pilot-01'
    model: str = MODEL
    effort: str = 'high'
    weeks: int = 32
    groups_per_condition: int = 1
    initial_tokens: int = 16384
    revision_tokens: int = 8192
    calibration_cases_per_split: int = 8
    seed: int = 20261011
    timeout_s: float = 180.0
    budget_usd: float = 4.80
    concurrency: int = 4
    request_interval_s: float = 1.0
    campaign_id: str = '20261011'

    def validate(self):
        if self.mode not in ('offline', 'api') or self.model != MODEL or self.effort != 'high':
            raise ValueError('Use offline/api, the pinned model, and high effort.')
        if type(self.weeks) is not int or self.weeks < 24 or (self.weeks - 4) % 4:
            raise ValueError('Use at least 24 weeks and a multiple of four decision weeks after practice.')
        for name in ('groups_per_condition', 'seed'):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(name + ' must be a positive integer.')
        if self.initial_tokens != 16384 or self.revision_tokens != 8192 or self.calibration_cases_per_split != 8:
            raise ValueError('v2 fixes initial/revision caps at 16384/8192 and two eight-case feasibility splits.')
        if not math.isfinite(self.budget_usd) or self.budget_usd <= 0:
            raise ValueError('An explicit positive finite dollar cap is required.')
        if not 1 <= self.concurrency <= 8 or not math.isfinite(self.request_interval_s) or self.request_interval_s < 0:
            raise ValueError('Invalid concurrency/pacing.')
        if self.timeout_s != 180 or not self.replicate_id or not self.campaign_id:
            raise ValueError('Use the common 180-second technical timeout and nonempty identities.')
        return self

    def scientific(self):
        return {k: v for k, v in asdict(self).items()
                if k not in ('budget_usd', 'concurrency', 'request_interval_s', 'campaign_id')}

    def fingerprint(self):
        return digest(dict(protocol=PROTOCOL, config=self.scientific(), prompt=COMMON,
                           question=TASK, schema=ORDER_SCHEMA, profiles=profiles(), demand='iid-discrete-uniform-0-8-v1',
                           tail='12-weeks-repeat-last-order', measurement='post-practice-common-window-v1'))


def demand_schedule(weeks, seed):
    """Known stationary distribution; draws frozen before calls and paired.

    No rejection sampling for a desired effect or variance: an exceptional
    constant finite path would have an undefined bullwhip outcome.
    """
    rng = np.random.default_rng(seed)
    return [4]*4 + [int(x) for x in rng.integers(0, 9, size=weeks-4)]


def display_state(game, state):
    i = ROLES.index(state['role'])
    deliveries = list(map(int, game.delivery[i]))
    waiting = int(state['supply_line'] - sum(deliveries))
    if waiting < 0 or len(deliveries) != 2:
        raise AssertionError('Post-shipment pipeline decomposition failed.')
    return {k: v for k, v in state.items() if k not in ('supply_line', 'net_inventory', 'cost')} | {
        'deliveries_due': deliveries, 'awaiting_dispatch': waiting}


def messages(state, history, previous_order=None):
    profile_id = state.get('profile_id', PROFILE_IDS[0])
    payload = dict(task=TASK, participant_profile=profiles()[profile_id], past_rounds=history,
                   current_state={k: v for k, v in state.items() if k != 'profile_id'})
    if previous_order is not None:
        payload.update(submitted_order=previous_order,
                       opportunity='You have one opportunity to reconsider. Keep or change your submitted order.')
    return [{'role': 'system', 'content': COMMON},
            {'role': 'user', 'content': json.dumps(payload, separators=(',', ':'), allow_nan=False)}]


def selected_order(initial, revision=None):
    first = decide(initial)
    if not first.valid:
        raise StudyStopped('Initial current-week decision missing; no order was substituted. Partial evidence saved.')
    selected, source, reason = first.order, 'initial', 'no_revision_opportunity'
    if revision is not None:
        updated = decide(revision)
        if updated.valid:
            selected, source, reason = updated.order, 'revision', 'completed_revision'
        elif (revision.get('status') == 'ok' and revision.get('response_status') == 'incomplete'
              and revision.get('incomplete_reason') == 'max_output_tokens'):
            reason = 'revision_budget_exhausted_initial_submission_retained'
        else:
            raise StudyStopped('Revision had a technical/protocol failure; stopped instead of calling it token pressure.')
    return dict(order=selected, initial_order=first.order, order_source=source,
                decision_status=reason, fallback=False,
                initial_request_key=initial['request_key'],
                revision_request_key=revision['request_key'] if revision else None,
                selected_request_key=(revision if source == 'revision' else initial)['request_key'],
                total_output_tokens=sum((r.get('usage') or {}).get('output_tokens', 0)
                                        for r in (initial, revision) if r),
                total_reasoning_tokens=sum((r.get('usage') or {}).get('reasoning_tokens', 0)
                                           for r in (initial, revision) if r))


def calibration_bank(seed=20261011):
    """Physically replayed early/middle/late histories; disjoint development/holdout.

    Policies generate scenarios only; no desired API outcomes enter this bank.
    """
    cases = []
    for split, offset in [('development', 700), ('holdout', 1700)]:
        for scenario in range(2):
            game, histories = BeerGame(), [[] for _ in ROLES]
            targets = [5, 10, 19, 28] if scenario == 0 else [8, 15, 24, 31]
            for week, demand in enumerate(demand_schedule(32, seed + offset + scenario), 1):
                states = game.observe(demand)
                shown = [display_state(game, s) for s in states]
                for role_index, target in enumerate(targets):
                    if week == target:
                        cases.append(dict(case_id=f'{split}-{scenario}-{ROLES[role_index]}', split=split,
                                          state=shown[role_index] | {'profile_id': PROFILE_IDS[(role_index+scenario)%4]},
                                          history=list(histories[role_index])))
                orders = [4] * 4 if week <= 4 else [
                    max(0, int(s['demand'] + (0.5 if scenario else 0.2) * (12 - s['net_inventory'])))
                    for s in states]
                for i in range(4):
                    histories[i].append(shown[i] | {'order': orders[i]})
                game.commit(orders)
    return cases


def supply_line_probes():
    """Matched hypothetical one-shot states, separate from dynamic game history.

    Pipeline differs by 24; all other displayed quantities stay constant.
    This estimates order sensitivity, not the legacy dynamic beta parameter.
    """
    cases = []
    for role in ROLES:
        for level, deliveries in [('low', [4, 4]), ('high', [16, 16])]:
            shared = {r: 12 for r in ROLES}
            shared[role] = 0
            state = dict(week=12, role=role, demand=8, received=4, shipped=4,
                         inventory=0, backlog=8, shared_inventory=shared,
                         deliveries_due=deliveries, awaiting_dispatch=0)
            cases.append(dict(case_id=f'{role}-{level}', role=role, level=level, state=state, history=[]))
    return cases


def manipulation_screen(rows, synthetic=False):
    """Fixed caps, no search on orders, costs, sensitivity, or significance."""
    checks = []
    for split in ('development', 'holdout'):
        own = [r for r in rows if r['split'] == split]
        initial = [r['initial_output_tokens'] for r in own]
        total = [r['initial_output_tokens'] + r['revision_output_tokens'] for r in own]
        ratio = float(np.median(initial) / np.median(total)) if total and np.median(total) > 0 else None
        passed = (len(own) == 8 and all(r['initial_valid'] for r in own)
                  and all(r['initial_reasoning_tokens'] > 0 and r['revision_reasoning_tokens'] > 0 for r in own)
                  and sum(r['revision_valid'] for r in own) >= 7
                  and ratio is not None and ratio <= .75
                  and all(r['initial_output_tokens'] < .9 * 16384 for r in own))
        checks.append(dict(split=split, n=len(own), initial_valid=sum(r['initial_valid'] for r in own),
                           revision_valid=sum(r['revision_valid'] for r in own),
                           median_initial_to_total_ratio=ratio, passed=bool(passed)))
    return dict(passed=bool(not synthetic and all(c['passed'] for c in checks)),
                synthetic=synthetic, splits=checks,
                interpretation='Small feasibility screen, not human validation or a whole-game reliability guarantee.')
