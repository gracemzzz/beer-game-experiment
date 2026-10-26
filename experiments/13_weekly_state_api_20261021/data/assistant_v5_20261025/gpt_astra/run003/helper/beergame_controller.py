"""Standalone website-chat Beer Game controller, development protocol v3.

Upload this exact file to a code-enabled website chat and import WebsiteGame.
Python updates physical states only; every order must be supplied explicitly by
the model. Arm A has an additional display-and-revision opportunity. B and C
commit their first decisions. Tool timestamps describe controller calls, not
verified model thinking time or a binding human deadline.

The physical engine is a standard-library derivation of this project's game.py.
No third-party packages, repository imports, API keys, or API calls are needed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
from statistics import mean, variance
import time

PROTOCOL = "manual-weekly-tool-opportunity-v3-development"
SCHEMA = "manual-weekly-tool-trajectories-v3"
WEEKS = 24
ORDER_GUARD = 100000  # Technical validity guard, never an ordering suggestion.
ROLES = ("retailer", "wholesaler", "distributor", "factory")
ROLE_KEYS = ("r", "w", "d", "f")
STATE_COLUMNS = ("inventory", "backlog", "supply_line", "demand", "received", "shipped")
PROFILES = (
    "Organized and emotionally steady in ordinary coursework.",
    "Organized and concerned by uncertainty in ordinary coursework.",
    "Flexible and emotionally steady in ordinary coursework.",
    "Flexible and concerned by uncertainty in ordinary coursework.",
)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def source_sha256():
    """Hash the actual uploaded helper bytes; not an authentication signature."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def write_standalone(path):
    """Export an exact-byte uploadable helper; refuse to overwrite other bytes."""
    target = Path(path)
    data = Path(__file__).read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_bytes() != data:
            raise ValueError("Refusing to replace a different controller snapshot")
    else:
        with target.open("xb") as stream:
            stream.write(data)
    return hashlib.sha256(data).hexdigest()


def _utc():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _integer(value, name, low=0, high=None):
    if type(value) is not int or value < low or (high is not None and value > high):
        raise ValueError("Invalid " + name)
    return value


class _PhysicalGame:
    """Exact list-based physical counterpart of the existing numpy BeerGame."""

    def __init__(self):
        self.inventory = [12] * 4
        self.backlog = [0] * 4
        self.delivery = [[4, 4] for _ in range(3)] + [[4, 4, 4]]
        self.incoming = [4] * 3
        self.outstanding = [12] * 4
        self.week = 0
        self.awaiting = False

    def observe(self, customer_demand):
        if self.awaiting:
            raise ValueError("Commit the current week before observing another")
        _integer(customer_demand, "customer demand")
        self.week += 1
        receipts = [queue.pop(0) for queue in self.delivery]
        demand = [customer_demand] + self.incoming
        shipped = []
        for index in range(4):
            self.inventory[index] += receipts[index]
            self.outstanding[index] -= receipts[index]
            owed = self.backlog[index] + demand[index]
            quantity = min(self.inventory[index], owed)
            self.inventory[index] -= quantity
            self.backlog[index] = owed - quantity
            shipped.append(quantity)
        for index in range(3):
            self.delivery[index].append(shipped[index + 1])
        self.awaiting = True
        shared = dict(zip(ROLES, self.inventory))
        return [dict(week=self.week, role=role, demand=demand[index], received=receipts[index],
                     shipped=shipped[index], inventory=self.inventory[index], backlog=self.backlog[index],
                     net_inventory=self.inventory[index] - self.backlog[index],
                     supply_line=self.outstanding[index],
                     cost=.5 * self.inventory[index] + self.backlog[index], shared_inventory=shared.copy())
                for index, role in enumerate(ROLES)]

    def commit(self, orders):
        if not self.awaiting:
            raise ValueError("Observe before committing")
        if not isinstance(orders, list) or len(orders) != 4:
            raise ValueError("Four literal integer orders are required")
        for order in orders:
            _integer(order, "order", high=ORDER_GUARD)
        self.outstanding = [quantity + order for quantity, order in zip(self.outstanding, orders)]
        self.incoming = orders[:3]
        self.delivery[3].append(orders[3])
        self.awaiting = False
        for index in range(3):
            if self.outstanding[index] != sum(self.delivery[index]) + self.backlog[index + 1] + orders[index]:
                raise ValueError("Physical conservation failed")
        if self.outstanding[3] != sum(self.delivery[3]):
            raise ValueError("Factory conservation failed")


class WebsiteGame:
    """One independent chat/arm/block, containing a dependent cluster of chains.

    Call display() and supply literal choices for each opportunity. An initial
    proposal in arm A does not advance the physical game. A new display() call
    is required before its revision. Keeping an initial proposal is permitted.
    """

    def __init__(self, case_id, arm, replicate, chains=10, *, seed=20261025,
                 provider="website", model="UNRECORDED", reasoning_setting="UNRECORDED", study_id=None):
        if not isinstance(case_id, str) or not case_id or arm not in ("A", "B", "C"):
            raise ValueError("A nonempty case_id and arm A, B, or C are required")
        _integer(replicate, "replicate", low=1)
        _integer(chains, "chains", low=1)
        _integer(seed, "seed")
        if not all(isinstance(value, str) and value for value in (provider, model, reasoning_setting)):
            raise ValueError("Record the provider, displayed model label, and selected reasoning setting")
        self.case_id, self.arm, self.replicate, self.chains, self.seed = case_id, arm, replicate, chains, seed
        self.metadata = dict(provider=provider, model=model, reasoning_setting=reasoning_setting,
                             source="user-reported website labels; provider API identifier unknown")
        self.controller_sha256 = source_sha256()
        self.study_id = study_id or "manual_weekly_v3_" + digest(dict(protocol=PROTOCOL,
                                    controller_sha256=self.controller_sha256, seed=seed, chains=chains, weeks=WEEKS))[:16]
        if not isinstance(self.study_id, str) or not self.study_id:
            raise ValueError("study_id must be a nonempty string")
        self.chain_ids = [f"c{index + 1:03d}" for index in range(chains)]
        self.games = {cid: _PhysicalGame() for cid in self.chain_ids}
        self._rng, self.profile_ids = {}, {}
        for index, cid in enumerate(self.chain_ids):
            rng = random.Random(seed + 100003 * (replicate - 1) + 1013 * index)
            profile_ids = list(range(4))
            rng.shuffle(profile_ids)
            self.profile_ids[cid] = profile_ids
            self._rng[cid] = rng
        self.week = 1
        self.phase = "initial"
        self._states = None
        self._initial = None
        self._shown = None
        self._display_utc = None
        self._display_clock = None
        self._current_demands = None
        self._probes = None
        self._probe_initial = None
        self._probe_final = None
        self.initial_orders, self.final_orders, self.realized_demand, self.state_hashes = [], [], [], []
        self.events, self.rows = [], []

    def _current_states(self):
        if self._states is None:
            self._current_demands = {cid: self._rng[cid].randrange(9) for cid in self.chain_ids}
            self._states = {cid: self.games[cid].observe(self._current_demands[cid]) for cid in self.chain_ids}
        return self._states

    def _probe_bank(self):
        if self._probes is None:
            cases = []
            for cid in self.chain_ids:
                for role_index, role in enumerate(ROLES):
                    for backlog in (40, 64):
                        for pipeline in (8, 32):
                            shared = dict(zip(ROLES, [12] * 4))
                            shared[role] = 0
                            cases.append(dict(chain_id=cid, role=role, profile_id=self.profile_ids[cid][role_index],
                                              inventory=0, backlog=backlog, supply_line=pipeline,
                                              demand=8, received=4, shipped=4, shared_inventory=shared))
            rng = random.Random(int(digest([self.seed, self.replicate, self.arm, "probe-order"])[:16], 16))
            rng.shuffle(cases)
            self._probes = [dict(probe_id=f"p{index + 1:03d}", **state) for index, state in enumerate(cases)]
        return self._probes

    def display(self):
        """Return only observable current information. Never display future demand."""
        if self.phase == "complete":
            return dict(case_id=self.case_id, phase="complete", completed_weeks=WEEKS,
                        instruction="All decisions received. Call export() and return its JSON unchanged.")
        common = dict(case_id=self.case_id, phase=self.phase, role_order=list(ROLE_KEYS), profiles=list(PROFILES))
        if self.phase.startswith("probe"):
            common["hypothetical_independent_decisions"] = json.loads(json.dumps(self._probe_bank()))
            if self.phase == "probe_revision":
                common["initial_proposals"] = self._probe_initial.copy()
        else:
            states = self._current_states()
            common.update(week=self.week, state_columns=list(STATE_COLUMNS), chains=[
                dict(chain_id=cid, profile_ids=self.profile_ids[cid][:],
                     state=[[state[key] for key in STATE_COLUMNS] for state in states[cid]],
                     shared_inventory=states[cid][0]["shared_inventory"].copy(),
                     history=[dict(week=index + 1, final_orders=orders[self.chain_ids.index(cid)][:],
                                   customer_demand=self.realized_demand[index][self.chain_ids.index(cid)])
                              for index, orders in enumerate(self.final_orders)
                              if index >= len(self.final_orders) - 4])
                for cid in self.chain_ids])
            if self.phase == "revision":
                common["initial_proposals"] = {cid: choices[:] for cid, choices in self._initial.items()}
        # Repeated display calls do not reset the measurement start time.
        if self._shown != self.phase:
            self._shown = self.phase
            self._display_utc, self._display_clock = _utc(), time.monotonic()
        return common

    def _require(self, phase):
        if self.phase != phase:
            raise ValueError("Expected controller phase " + self.phase + ", not " + phase)
        if self._shown != phase:
            raise ValueError("Call display() for this opportunity before supplying literal decisions")

    def _choices(self, choices, probes=False):
        ids = [state["probe_id"] for state in self._probe_bank()] if probes else self.chain_ids
        if not isinstance(choices, dict) or set(choices) != set(ids):
            raise ValueError("Supply every requested ID exactly once; missing decisions are never filled")
        clean = {}
        for ident in ids:
            values = [choices[ident]] if probes else choices[ident]
            if not isinstance(values, list) or (not probes and len(values) != 4):
                raise ValueError("Each chain requires a list of four literal orders")
            for value in values:
                _integer(value, "order", high=ORDER_GUARD)
            clean[ident] = values[0] if probes else values[:]
        return clean

    def _record(self, choices, probes=False):
        state = self._probe_bank() if probes else self._current_states()
        self.events.append(dict(phase=self.phase, week=None if probes else self.week,
                                state_sha256=digest(state), choices_sha256=digest(choices),
                                display_utc=self._display_utc, submit_utc=_utc(),
                                controller_elapsed_seconds=max(0., time.monotonic() - self._display_clock)))
        self._shown = None

    def submit_initial(self, choices):
        self._require("initial")
        clean = self._choices(choices)
        self._record(clean)
        self._initial = clean
        if self.arm == "A":
            self.phase = "revision"
        else:
            self._commit(clean)
        return self._status()

    def submit_revision(self, choices):
        self._require("revision")
        if self.arm != "A":
            raise ValueError("This arm has no revision opportunity")
        clean = self._choices(choices)
        self._record(clean)
        self._commit(clean)
        return self._status()

    def _commit(self, choices):
        states = self._current_states()
        self.initial_orders.append([self._initial[cid][:] for cid in self.chain_ids])
        self.final_orders.append([choices[cid][:] for cid in self.chain_ids])
        self.realized_demand.append([self._current_demands[cid] for cid in self.chain_ids])
        self.state_hashes.append(digest(states))
        for cid in self.chain_ids:
            self.rows.extend(dict(state, chain_id=cid, order=choices[cid][index],
                                  customer_demand=self._current_demands[cid]) for index, state in enumerate(states[cid]))
            self.games[cid].commit(choices[cid])
        self._states, self._initial, self._current_demands = None, None, None
        self.week += 1
        self.phase = "probe_initial" if self.week > WEEKS else "initial"

    def submit_probe_initial(self, choices):
        self._require("probe_initial")
        clean = self._choices(choices, probes=True)
        self._record(clean, probes=True)
        self._probe_initial = clean
        if self.arm == "A":
            self.phase = "probe_revision"
        else:
            self._probe_final = clean
            self.phase = "complete"
        return self._status()

    def submit_probe_revision(self, choices):
        self._require("probe_revision")
        if self.arm != "A":
            raise ValueError("This arm has no revision opportunity")
        clean = self._choices(choices, probes=True)
        self._record(clean, probes=True)
        self._probe_final = clean
        self.phase = "complete"
        return self._status()

    def _status(self):
        return dict(case_id=self.case_id, next_phase=self.phase, completed_weeks=len(self.final_orders),
                    next_step="export" if self.phase == "complete" else "display")

    def export(self, require_complete=True):
        """Return literal choices plus consistency evidence; no predicted decisions."""
        if require_complete and self.phase != "complete":
            raise ValueError("Collection is incomplete; no missing choices will be fabricated")
        result = dict(schema_version=SCHEMA, protocol=PROTOCOL, study_id=self.study_id,
                      controller_source_sha256=self.controller_sha256, case_id=self.case_id, arm=self.arm,
                      replicate=self.replicate, block_id=f"b{self.replicate:04d}", seed=self.seed,
                      chains=self.chains, weeks=WEEKS, model_metadata=self.metadata.copy(),
                      chain_ids=self.chain_ids[:], profile_ids=self.profile_ids,
                      role_order=list(ROLE_KEYS), initial_orders=self.initial_orders, final_orders=self.final_orders,
                      realized_customer_demand=self.realized_demand, state_sha256_by_week=self.state_hashes,
                      probe_initial=self._probe_initial, probe_final=self._probe_final,
                      pending_initial_orders=self._initial if self.phase == "revision" else None,
                      events=self.events, complete=self.phase == "complete", completed_weeks=len(self.final_orders),
                      timing_interpretation="Controller-call intervals only; not verified model thinking time or binding deadlines.",
                      provenance_interpretation="Replay verifies internal consistency. External tool transcript is required to verify separate model/tool iterations.")
        # Return an independent JSON-safe copy, so downstream edits cannot mutate the controller.
        return json.loads(json.dumps(result, allow_nan=False))


def audit_export(payload, *, expected_case=None, expected_source_sha256=None):
    """Strict replay and one cluster-level row; does not authenticate a transcript.

    expected_case may bind any top-level identity fields to a prepared manifest.
    Website model/reasoning names remain user-reported. Timestamps never prove
    literal thinking duration. No statistical independence is inferred here.
    """
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA or payload.get("protocol") != PROTOCOL:
        raise ValueError("Unknown manual controller schema or protocol")
    expected = source_sha256() if expected_source_sha256 is None else expected_source_sha256
    if payload.get("controller_source_sha256") != expected:
        raise ValueError("Controller source hash differs from the prepared snapshot")
    for key, value in (expected_case or {}).items():
        if payload.get(key) != value:
            raise ValueError("Prepared case identity differs: " + key)
    metadata = payload.get("model_metadata")
    if not isinstance(metadata, dict):
        raise ValueError("Reported model metadata is required")
    game = WebsiteGame(payload["case_id"], payload["arm"], payload["replicate"], payload["chains"],
                       seed=payload["seed"], provider=metadata["provider"], model=metadata["model"],
                       reasoning_setting=metadata["reasoning_setting"], study_id=payload["study_id"])
    initial, final = payload.get("initial_orders"), payload.get("final_orders")
    if not isinstance(initial, list) or not isinstance(final, list) or len(initial) != len(final) or len(final) > WEEKS:
        raise ValueError("Initial/final weekly arrays are incomplete or invalid")
    for index, (first, last) in enumerate(zip(initial, final)):
        if not isinstance(first, list) or not isinstance(last, list) or len(first) != game.chains or len(last) != game.chains:
            raise ValueError("Weekly arrays must contain every chain")
        game.display()
        game.submit_initial(dict(zip(game.chain_ids, first)))
        if game.arm == "A":
            game.display()
            game.submit_revision(dict(zip(game.chain_ids, last)))
        elif first != last:
            raise ValueError("A restricted arm cannot revise its initial orders")
    if payload.get("pending_initial_orders") is not None:
        if game.arm != "A" or len(final) >= WEEKS:
            raise ValueError("Unexpected pending initial proposal")
        game.display()
        game.submit_initial(payload["pending_initial_orders"])
    if payload.get("probe_initial") is not None:
        if len(final) != WEEKS:
            raise ValueError("Probes cannot precede the complete game")
        game.display()
        game.submit_probe_initial(payload["probe_initial"])
        if game.arm == "A" and payload.get("probe_final") is not None:
            game.display()
            game.submit_probe_revision(payload["probe_final"])
        elif game.arm != "A" and payload.get("probe_final") != payload["probe_initial"]:
            raise ValueError("A restricted arm cannot revise its probe choices")
    elif payload.get("probe_final") is not None:
        raise ValueError("Final probes have no initial decisions")
    rebuilt = game.export(require_complete=False)
    for key in ("chain_ids", "profile_ids", "role_order", "realized_customer_demand", "state_sha256_by_week",
                "completed_weeks", "complete", "block_id", "weeks"):
        if payload.get(key) != rebuilt[key]:
            raise ValueError("Replay differs: " + key)
    events = payload.get("events")
    if not isinstance(events, list) or len(events) != len(rebuilt["events"]):
        raise ValueError("Missing or extra controller events")
    for actual, replayed in zip(events, rebuilt["events"]):
        if not isinstance(actual, dict):
            raise ValueError("Malformed controller event")
        for key in ("phase", "week", "state_sha256", "choices_sha256"):
            if actual.get(key) != replayed[key]:
                raise ValueError("Controller event replay differs: " + key)
        elapsed = actual.get("controller_elapsed_seconds")
        if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not 0 <= elapsed < float("inf"):
            raise ValueError("Invalid controller interval")
        for key in ("display_utc", "submit_utc"):
            try:
                parsed = datetime.fromisoformat(actual[key])
                if parsed.tzinfo is None:
                    raise ValueError("Timestamp lacks a timezone")
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError("Malformed controller timestamp") from error
        if datetime.fromisoformat(actual["submit_utc"]) < datetime.fromisoformat(actual["display_utc"]):
            raise ValueError("Submission precedes its display")
    outcome = dict(model=metadata["model"], provider=metadata["provider"], reasoning_setting=metadata["reasoning_setting"],
                   case_id=game.case_id, arm=game.arm, block_id=f"b{game.replicate:04d}", replicate=game.replicate,
                   chains_in_cluster=game.chains, complete=len(final) == WEEKS, weeks=len(final),
                   probe_complete=game._probe_final is not None, chain_total_cost=None, cluster_total_cost=None,
                   mean_role_order_variance=None, mean_role_bullwhip=None, undefined_bullwhip_roles=None,
                   pipeline_sensitivity=None, backlog_sensitivity=None, game_zero_order_fraction=None,
                   probe_zero_order_fraction=None, trace_authenticated=False)
    if len(final) == WEEKS:
        costs, order_variances, bullwhips = [], [], []
        for index, cid in enumerate(game.chain_ids):
            chain_rows = [row for row in game.rows if row["chain_id"] == cid]
            costs.append(sum(row["cost"] for row in chain_rows))
            demand_variance = variance([demand[index] for demand in game.realized_demand])
            for role in ROLES:
                order_variance = variance([row["order"] for row in chain_rows if row["role"] == role])
                order_variances.append(order_variance)
                bullwhips.append(order_variance / demand_variance if demand_variance > 0 else None)
        outcome.update(chain_total_cost=mean(costs), cluster_total_cost=sum(costs),
                       mean_role_order_variance=mean(order_variances),
                       mean_role_bullwhip=mean(bullwhips) if all(value is not None for value in bullwhips) else None,
                       undefined_bullwhip_roles=sum(value is None for value in bullwhips),
                       game_zero_order_fraction=mean(row["order"] == 0 for row in game.rows))
    if game._probe_final is not None:
        pipeline_pairs, backlog_pairs = {}, {}
        for state in game._probe_bank():
            order = game._probe_final[state["probe_id"]]
            pipeline_pairs.setdefault((state["chain_id"], state["role"], state["backlog"]), {})[state["supply_line"]] = order
            backlog_pairs.setdefault((state["chain_id"], state["role"], state["supply_line"]), {})[state["backlog"]] = order
        outcome.update(pipeline_sensitivity=mean((pair[8] - pair[32]) / 24 for pair in pipeline_pairs.values()),
                       backlog_sensitivity=mean((pair[64] - pair[40]) / 24 for pair in backlog_pairs.values()),
                       probe_zero_order_fraction=mean(value == 0 for value in game._probe_final.values()))
    return outcome
