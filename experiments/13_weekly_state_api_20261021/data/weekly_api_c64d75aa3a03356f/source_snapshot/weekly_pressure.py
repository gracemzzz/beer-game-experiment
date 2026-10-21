"""Weekly decision batches with Python-maintained physical Beer Game states.

All methods are offline. Model API transport lives in weekly_pressure_api.py.
Joint batches support descriptive framing comparisons, not human-time inference.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
from statistics import mean, variance

from .game import BeerGame, ROLES
from .batched_pressure import PROFILES, HYPOTHESES, MODELS, _probes

PROTOCOL = "weekly-pressure-state-v1"
SCHEMA = "weekly-pressure-choices-v1"
ROLE_KEYS = ("r", "w", "d", "f")
WEEKS = 24
ORDER_GUARD = 100000
STATE_COLUMNS = ("inventory", "backlog", "supply_line", "demand", "received", "shipped")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_new(path, value):
    path = Path(path)
    data = value if isinstance(value, bytes) else (
        value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refusing to replace frozen weekly evidence: " + str(path))
    else:
        with path.open("xb") as stream:
            stream.write(data)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def budget_experiment_for(run):
    """Resolve the prospectively recorded existing experiment-12 budget folder."""
    run = Path(run).resolve()
    relative = read(run / "plan.json")["budget_experiment"]
    if Path(relative).is_absolute():
        raise ValueError("The shared budget reference must be portable and relative.")
    return (run.parent.parent / relative).resolve()


def _chains(seed, phase):
    result = []
    prefix, offset, count = ("p", 10000, 1) if phase == "pilot" else ("m", 20000, WEEKS)
    for block in range(10):
        rng = random.Random(seed + offset + block * 1009)
        demands = [rng.randrange(9) for _ in range(count)]
        profiles = list(range(4))
        rng.shuffle(profiles)
        conditions = ["no_pressure", "strong_pressure"]
        rng.shuffle(conditions)
        for slot, condition in enumerate(conditions):
            result.append(dict(chain_id=f"{prefix}{block:02d}{'ab'[slot]}", block=block,
                               condition=condition, profile_ids=profiles,
                               customer_demand=demands,
                               participant_ids=[f"{prefix}{block:02d}{'ab'[slot]}_{key}" for key in ROLE_KEYS]))
    random.Random(seed + offset + 42).shuffle(result)
    return result


def task_id(model, phase, week=None):
    if phase not in ("pilot", "main", "probe"):
        raise ValueError("Unknown weekly study phase.")
    if phase == "main" and (type(week) is not int or not 1 <= week <= WEEKS):
        raise ValueError("Main week must be 1 through 24.")
    return model + (f"_w{week:02d}" if phase == "main" else "_" + phase)


def prepare(experiment: Path, budget_experiment: Path, *, label="weekly-state-80-per-model"):
    experiment, budget = Path(experiment).resolve(), Path(budget_experiment).resolve()
    ledger_path = budget / "data/api_budget.json"
    if experiment == budget or not ledger_path.is_file():
        raise ValueError("An existing separate experiment-12 shared budget ledger is required.")
    ledger = read(ledger_path)
    if ledger.get("cap_usd") != 5 or type(ledger.get("attempts")) is not dict:
        raise ValueError("Continue the existing $5 ledger; do not reset spending authority.")
    names = ("weekly_pressure.py", "weekly_pressure_api.py", "game.py", "batched_pressure.py", "batched_pressure_api.py")
    sources = {name: Path(__file__).with_name(name) for name in names}
    sources["PROTOCOL.md"] = experiment / "hypotheses/PROTOCOL.md"
    identity = dict(protocol=PROTOCOL, schema_version=SCHEMA, label=label, seed=2026102107,
                    models=list(MODELS), weeks=WEEKS, history_weeks=4,
                    chains_per_model=20, identities_per_model=80,
                    pilot_chains_per_model=20, output_caps={"pilot": 2048, "main": 2048, "probe": 4096},
                    model_settings={model: ({"reasoning": "none"} if model.startswith("gpt-") else
                                           {"thinking": "disabled", "effort": "low"}) for model in MODELS},
                    budget_experiment=os.path.relpath(budget, experiment), cap_usd=5.,
                    source_hashes={name: _sha(path) for name, path in sources.items()})
    study_id = "weekly_api_" + digest(identity)[:16]
    run = experiment / "data" / study_id
    if (run / "plan.json").exists():
        loadplan(run)
        return run
    plan = dict(identity, study_id=study_id, hypotheses=HYPOTHESES,
                chains_by_phase={phase: _chains(identity["seed"], phase) for phase in ("pilot", "main")},
                profiles=list(PROFILES), probe_states=_probes(identity["seed"] + 30500),
                initial_budget_attempts_sha256={key: digest(value) for key, value in ledger["attempts"].items()},
                expected_requests=104, expected_pilot_requests=4, expected_main_weekly_requests=96,
                expected_probe_requests=4, human_observations=0,
                primary_h1="Matched pipeline-sensitivity proxy; no structural-beta or binding-time claim.",
                primary_h2="Sum of holding plus backlog costs during exactly 24 Python-updated main weeks.",
                inference="Descriptive only; joint batches couple fictional chains/roles and do not enforce time pressure.",
                stopping="One full-size pilot, 24 weekly main batches and one probe batch per model. Per-model pilot gate; no semantic retries, missing-order fills or replacements.")
    save_new(run / "plan.json", plan)
    save_new(run / "plan.sha256", digest(plan) + "\n")
    for name, path in sources.items():
        save_new(run / "source_snapshot" / name, path.read_bytes())
    save_new(run / "source_snapshot/shared_budget_at_preparation.json", ledger_path.read_bytes())
    (run / "accepted").mkdir(parents=True, exist_ok=True)
    return run


def loadplan(run):
    run = Path(run).resolve()
    plan = read(run / "plan.json")
    if digest(plan) != (run / "plan.sha256").read_text().strip():
        raise ValueError("Frozen weekly plan changed.")
    if plan["protocol"] != PROTOCOL or plan["schema_version"] != SCHEMA or plan["study_id"] != run.name:
        raise ValueError("Weekly study identity differs.")
    for name, expected in plan["source_hashes"].items():
        if _sha(run / "source_snapshot" / name) != expected:
            raise ValueError("Weekly source snapshot changed: " + name)
        current = run.parent.parent / "hypotheses/PROTOCOL.md" if name == "PROTOCOL.md" else Path(__file__).with_name(name)
        if _sha(current) != expected:
            raise ValueError("Weekly scientific implementation changed: " + name)
    ledger = read(budget_experiment_for(run) / "data/api_budget.json")
    if ledger.get("cap_usd") != 5:
        raise ValueError("Existing shared budget cap changed.")
    for key, expected in plan["initial_budget_attempts_sha256"].items():
        if key not in ledger["attempts"] or digest(ledger["attempts"][key]) != expected:
            raise ValueError("Earlier shared-budget charge changed or disappeared.")
    return plan


def _task_base(plan, model, phase, week):
    if model not in plan["models"]:
        raise ValueError("Unplanned model.")
    selected = plan["chains_by_phase"]["pilot" if phase == "pilot" else "main"]
    ident = task_id(model, phase, week)
    return dict(schema_version=SCHEMA, study_id=plan["study_id"], task_id=ident,
                model=model, phase=phase, week=1 if phase == "pilot" else week,
                max_output_tokens=plan["output_caps"][phase], response_path=f"accepted/{ident}.json",
                chain_ids=[chain["chain_id"] for chain in selected],
                chains=[{key: chain[key] for key in ("chain_id", "block", "condition", "profile_ids", "participant_ids")}
                        for chain in selected], profiles=plan["profiles"])


def _simulate_prefix(plan, model, accepted, through_week):
    games = {chain["chain_id"]: BeerGame() for chain in plan["chains_by_phase"]["main"]}
    specs = {chain["chain_id"]: chain for chain in plan["chains_by_phase"]["main"]}
    rows = []
    for week in range(1, through_week + 1):
        task = _task_base(plan, model, "main", week)
        payload = accepted.get(task["task_id"])
        if payload is None:
            raise ValueError("Missing earlier accepted weekly batch: " + task["task_id"])
        issues = validate_response(task, payload)
        if issues:
            raise ValueError("Invalid earlier weekly batch: " + "; ".join(issues))
        for cid, game in games.items():
            spec = specs[cid]
            states = game.observe(int(spec["customer_demand"][week - 1]))
            orders = [payload["orders"][cid][key] for key in ROLE_KEYS]
            for index, state in enumerate(states):
                rows.append(dict(state, model=model, chain_id=cid, block=spec["block"], condition=spec["condition"],
                                 phase="main", order=orders[index], customer_demand=spec["customer_demand"][week - 1],
                                 participant_id=model + ":" + spec["participant_ids"][index],
                                 holding_cost=.5 * state["inventory"], backlog_cost=state["backlog"]))
            game.commit(orders)
    return games, rows


def build_task(plan, model, phase, week=None, accepted=None):
    """Build only presently observable input; never include a future demand path.

    Week one can be previewed without a pilot. API execution enforces the pilot
    gate; subsequent-week construction additionally requires all earlier choices.
    """
    accepted = {} if accepted is None else accepted
    if phase == "main" and week is None:
        raise ValueError("Specify the main decision week.")
    task = _task_base(plan, model, phase, week)
    if phase == "probe":
        _simulate_prefix(plan, model, accepted, WEEKS)
        task["probe_states"] = plan["probe_states"]
        return task
    if phase == "pilot":
        selected = plan["chains_by_phase"]["pilot"]
        games = {chain["chain_id"]: BeerGame() for chain in selected}
        earlier = []
        current_week = 1
    else:
        selected = plan["chains_by_phase"]["main"]
        games, earlier = _simulate_prefix(plan, model, accepted, week - 1)
        current_week = week
    task["states"], task["history"] = {}, {}
    for spec in selected:
        cid = spec["chain_id"]
        task["states"][cid] = games[cid].observe(int(spec["customer_demand"][current_week - 1]))
        recent = [row for row in earlier if row["chain_id"] == cid and row["week"] >= current_week - 4]
        task["history"][cid] = [
            [[row["demand"], row["order"]] for row in recent if row["week"] == previous]
            for previous in sorted({row["week"] for row in recent})
        ]
    return task


def prompt_text(task):
    conditions = {"no_pressure": "The students experience no time pressure and have ample time to consider this decision.",
                  "strong_pressure": "The students experience strong time pressure and feel they must submit this decision promptly."}
    context = {key: task[key] for key in ("schema_version", "study_id", "task_id")}
    context.update(role_order=list(ROLE_KEYS), personalities=task["profiles"], classroom_situations=conditions)
    contexts = []
    for chain in task["chains"]:
        row = dict(id=chain["chain_id"], situation=chain["condition"], personalities=chain["profile_ids"])
        if task["phase"] != "probe":
            row["state"] = [[state[key] for key in STATE_COLUMNS] for state in task["states"][chain["chain_id"]]]
            row["history"] = task["history"][chain["chain_id"]]
        contexts.append(row)
    context["chains"] = contexts
    common = """Choose Beer Game orders for the supplied fictional undergraduate business students.
There are four students per chain: r=retailer,w=wholesaler,d=distributor,f=factory.
They have introductory business knowledge and no specialist inventory training.
Assigned personalities describe ordinary coursework, not an ordering strategy.
Each student tries to minimize its team's inventory-holding and backlog costs.
Apply the classroom situation assigned to that chain. These imagined situations
do not enforce or measure actual model time or student psychological pressure.
Do not invent demographic traits, deliberate errors, a desired group pattern or
artificial variation. Equal decisions, zero orders and unchanged orders are allowed.

Rules: holding costs $0.50 per remaining case/week; backlog costs $1 per unfilled
case/week. There is no revenue, manufacturing charge, ordering fee, bulk discount
or capacity limit. Each order is a nonnegative integer number of cases. Retailer,
wholesaler and distributor order from the next upstream role; factory orders
start production. Orders cannot be canceled. An order sent at t reaches its
supplier at t+1; dispatched stock then takes two weeks to arrive. Earliest
receipt is t+3, later if the supplier is short. Factory production arrives at
t+3, with no extra supplier or raw-material delay. A new order cannot change
today's inventory, shipment or backlog; later consequences still count.

Python maintains all physical states. Each display is AFTER this week's receipts,
shipments and cost assessment and BEFORE new orders. Current backlog already
includes unfilled current demand and persists. Outstanding orders include prior
orders not yet received; they are separate from on-hand inventory. Each student
may use its local display, its own supplied history, and all four current inventories
in its chain. Other roles' private fields and other chains are not information for
that student. The batch generator nevertheless sees the full collection; actual
information isolation cannot be enforced by this instruction. No future demand
realization is supplied. Do not coordinate decisions between chains.
"""
    if task["phase"] == "probe":
        context["probe_columns"] = ["id", "role", "backlog", "outstanding", "deliveries_due"]
        context["probes"] = [[p["probe_id"], ROLE_KEYS[ROLES.index(p["role"])], p["backlog"],
                              p["supply_line"], p["deliveries_due"]] for p in task["probe_states"]]
        instructions = """
These are separate hypothetical state questions, without game history. For each
chain answer all sixteen displays using its assigned student's personality and
classroom situation. Every display is week12, local inventory0, incoming demand8,
received4, shipped4, awaiting dispatch0, and other three inventories12. The listed
backlog and outstanding quantities vary by display. deliveries_due starts next
week. Each display is independent of every other probe and earlier game choices.
Return root fields schema_version,study_id,task_id,probes only. probes is an object
containing EACH supplied chain ID, whose value contains EACH supplied probe ID
mapped to its integer order. All identifiers must match. Return only full JSON;
no prose, costs, state arithmetic, explanations or summary statistics.
"""
    else:
        context["week"] = task["week"]
        context["state_columns"] = list(STATE_COLUMNS)
        context["history_format"] = "oldest-to-newest weeks; each week four [incoming_demand,submitted_order] pairs in role order"
        instructions = """
For EACH chain choose its FOUR current orders, using the supplied current state.
state contains four role rows in r,w,d,f order with the specified column names.
All four current inventories are the first values of those rows. history contains
up to the last four completed weeks, in chronological and role order. Do not
generate future-week orders or recalculate the state. Return root fields
schema_version,study_id,task_id,orders only. orders is an object containing EVERY
supplied chain ID; each value contains exactly r,w,d,f mapped to integer orders.
Return only the complete JSON; no prose, costs, state arithmetic or explanations.
"""
    return common + instructions + "\nCURRENT INPUT\n" + json.dumps(context, separators=(",", ":"), ensure_ascii=False) + "\n"


def response_schema(task):
    def obj(properties):
        return dict(type="object", properties=properties, required=list(properties), additionalProperties=False)
    keys = [p["probe_id"] for p in task["probe_states"]] if task["phase"] == "probe" else ROLE_KEYS
    choice = obj({key: {"type": "integer"} for key in keys})
    field = "probes" if task["phase"] == "probe" else "orders"
    properties = {key: {"type": "string", "enum": [task[key]]} for key in ("schema_version", "study_id", "task_id")}
    properties[field] = obj({cid: {"$ref": "#/$defs/choice"} for cid in task["chain_ids"]})
    schema = obj(properties)
    schema["$defs"] = {"choice": choice}
    return schema


def validate_response(task, payload):
    field = "probes" if task["phase"] == "probe" else "orders"
    if type(payload) is not dict or set(payload) != {"schema_version", "study_id", "task_id", field}:
        return ["Wrong root fields."]
    issues = ["Wrong " + key for key in ("schema_version", "study_id", "task_id") if payload[key] != task[key]]
    values = payload[field]
    if type(values) is not dict or set(values) != set(task["chain_ids"]):
        return issues + ["Missing or extra chain IDs."]
    keys = {p["probe_id"] for p in task["probe_states"]} if task["phase"] == "probe" else set(ROLE_KEYS)
    for cid, choices in values.items():
        if type(choices) is not dict or set(choices) != set(keys):
            issues.append(cid + ": missing or extra choice IDs.")
        elif any(type(q) is not int or q < 0 or q > ORDER_GUARD for q in choices.values()):
            issues.append(cid + ": choices must be literal nonnegative integers within the technical 100000-case guard.")
    return issues


def synthetic_fixture(task):
    """Explicit offline fixture; never writes or represents a model response."""
    payload = {key: task[key] for key in ("schema_version", "study_id", "task_id")}
    if task["phase"] == "probe":
        payload["probes"] = {cid: {p["probe_id"]: max(0, 8 + p["backlog"] - p["supply_line"])
                                   for p in task["probe_states"]} for cid in task["chain_ids"]}
    else:
        payload["orders"] = {cid: {key: task["states"][cid][i]["demand"] for i, key in enumerate(ROLE_KEYS)}
                             for cid in task["chain_ids"]}
    return payload


def replay(plan, model, accepted):
    weeks = 0
    for week in range(1, WEEKS + 1):
        ident = task_id(model, "main", week)
        if ident not in accepted:
            break
        issues = validate_response(_task_base(plan, model, "main", week), accepted[ident])
        if issues:
            raise ValueError("Invalid saved weekly batch: " + "; ".join(issues))
        weeks = week
    return _simulate_prefix(plan, model, accepted, weeks)[1]


def _ratio(values, demands):
    return variance(values) / variance(demands) if len(values) >= 2 and variance(demands) > 0 else None


def analyze(run):
    run = Path(run)
    plan = loadplan(run)
    # Lazy import avoids a transport/core import cycle. This read-only audit
    # binds accepted choices to exact provider bytes and frozen dynamic inputs.
    from .weekly_pressure_api import audit_saved
    verified_payloads = audit_saved(run)
    api_status = read(run / "api_status.json") if (run / "api_status.json").exists() else {}
    records = api_status.get("tasks", {})
    all_rounds, all_chains, all_probes, statuses, model_status, hypotheses, contrasts, condition_means = [], [], [], [], [], [], [], []
    for model in MODELS:
        accepted = {}
        pilot_ok = False
        weeks_done = 0
        probe_ok = False
        sequence = [("pilot", None)] + [("main", week) for week in range(1, WEEKS + 1)] + [("probe", None)]
        for phase, week in sequence:
            ident = task_id(model, phase, week)
            entry = dict(model=model, phase=phase, week=week, task_id=ident, status="missing", reason=None, issues=[])
            path = run / "accepted" / (ident + ".json")
            if path.exists():
                try:
                    record = records.get(ident, {})
                    if record.get("status") != "accepted" or record.get("accepted_sha256") != _sha(path):
                        raise ValueError("Accepted payload lacks matching immutable API receipt.")
                    if phase != "pilot" and not pilot_ok:
                        raise ValueError("Model pilot has not been accepted.")
                    task = build_task(plan, model, phase, week, accepted)
                    payload = verified_payloads[ident]
                    issues = validate_response(task, payload)
                    if issues:
                        raise ValueError("; ".join(issues))
                    accepted[ident] = payload
                    entry["status"] = "accepted"
                    if phase == "pilot": pilot_ok = True
                    elif phase == "main": weeks_done = week
                    else: probe_ok = True
                except (ValueError, KeyError, TypeError, AssertionError) as exc:
                    entry.update(status="invalid", reason="saved_evidence_validation", issues=[str(exc)])
            elif ident in records:
                entry["status"] = records[ident].get("status", "missing")
                entry["reason"] = records[ident].get("reason")
                entry["issues"] = records[ident].get("issues", [])
            statuses.append(entry)
        rows = replay(plan, model, accepted)
        all_rounds.extend(rows)
        own_chains = []
        probe_payload = accepted.get(task_id(model, "probe"))
        for spec in plan["chains_by_phase"]["main"]:
            cid = spec["chain_id"]
            own = [row for row in rows if row["chain_id"] == cid]
            if not own:
                continue
            sensitivity = backlog_response = relative_weight = None
            if probe_payload is not None:
                choices = probe_payload["probes"][cid]
                lookup = {(p["role"], p["backlog"], p["supply_line"]): choices[p["probe_id"]] for p in plan["probe_states"]}
                sensitivity = mean((lookup[role, backlog, 8] - lookup[role, backlog, 32]) / 24
                                   for role in ROLES for backlog in (8, 24))
                backlog_response = mean((lookup[role, 24, supply] - lookup[role, 8, supply]) / 16
                                        for role in ROLES for supply in (8, 32))
                relative_weight = sensitivity / backlog_response if abs(backlog_response) >= .02 else None
                all_probes.extend(dict(p, model=model, chain_id=cid, block=spec["block"], condition=spec["condition"],
                                       order=choices[p["probe_id"]]) for p in plan["probe_states"])
            role_ratios = [_ratio([r["order"] for r in own if r["role"] == role],
                                  [r["customer_demand"] for r in own if r["role"] == role]) for role in ROLES]
            current = [r for r in own if r["week"] == weeks_done]
            observed = sum(r["cost"] for r in own)
            metric = dict(model=model, chain_id=cid, block=spec["block"], condition=spec["condition"],
                          weeks_observed=weeks_done, complete=weeks_done == WEEKS,
                          total_cost=observed if weeks_done == WEEKS else None, observed_cost_partial=observed,
                          holding_cost=sum(r["holding_cost"] for r in own), backlog_cost=sum(r["backlog_cost"] for r in own),
                          sensitivity=sensitivity, backlog_response=backlog_response, relative_probe_weight=relative_weight,
                          zero_orders=sum(r["order"] == 0 for r in own), min_order=min(r["order"] for r in own),
                          max_order=max(r["order"] for r in own), final_inventory=sum(r["inventory"] for r in current),
                          final_backlog=sum(r["backlog"] for r in current),
                          final_supply_line=sum(r["supply_line"] + r["order"] for r in current),
                          bullwhip=mean(role_ratios) if all(r is not None for r in role_ratios) else None)
            metric.update({"bullwhip_" + role: value for role, value in zip(ROLES, role_ratios)})
            own_chains.append(metric)
        all_chains.extend(own_chains)
        model_status.append(dict(model=model, accepted_pilot_responses=int(pilot_ok), expected_pilot_responses=1,
                                 accepted_weeks=weeks_done, expected_weeks=WEEKS,
                                 accepted_probe_responses=int(probe_ok), expected_probe_responses=1,
                                 complete=pilot_ok and weeks_done == WEEKS and probe_ok,
                                 accepted_main_responses=weeks_done, inference_available=False))
        for condition in ("no_pressure", "strong_pressure"):
            group = [r for r in own_chains if r["condition"] == condition]
            condition_means.append(dict(model=model, condition=condition, chains=len(group), weeks_observed=weeks_done,
                                        total_cost=mean(r["total_cost"] for r in group) if group and weeks_done == WEEKS else None,
                                        sensitivity=mean(r["sensitivity"] for r in group) if group and probe_ok else None,
                                        observed_cost_partial=mean(r["observed_cost_partial"] for r in group) if group else None))
        indexed = {(r["block"], r["condition"]): r for r in own_chains}
        for name, metric, direction in (("H1", "sensitivity", -1), ("H2", "total_cost", 1)):
            diffs = []
            for block in range(10):
                a, b = indexed.get((block, "no_pressure")), indexed.get((block, "strong_pressure"))
                if a is None or b is None or a[metric] is None or b[metric] is None:
                    continue
                difference = b[metric] - a[metric]
                diffs.append(difference)
                contrasts.append(dict(model=model, hypothesis=name, block=block, metric=metric,
                                      no_pressure=a[metric], strong_pressure=b[metric], difference=difference))
            effect = mean(diffs) if diffs else None
            hypotheses.append(dict(model=model, hypothesis=name, metric=metric, expected_sign=direction,
                                   paired_blocks=len(diffs), mean_strong_minus_no=effect,
                                   descriptive_direction="unavailable" if effect is None else "zero" if effect == 0 else
                                   "predicted" if direction * effect > 0 else "opposite",
                                   p_raw=None, p_holm_8=None, paired_bootstrap_95=None,
                                   inference_available=False, literal_binding_time_test=False))
    return dict(study_id=plan["study_id"], model_status=model_status, hypotheses=hypotheses, contrasts=contrasts,
                chains=all_chains, rounds=all_rounds, probes=all_probes, task_status=statuses,
                condition_means=condition_means, limitations=[
                    "Pressure is fictional framing; actual time or reasoning resources do not differ by condition.",
                    "All current roles/chains appear in a shared batch, so private information isolation and chain independence are not enforced.",
                    "H1 is a matched-state sensitivity proxy, not the original structural beta or a human cognitive measurement.",
                    "Only full 24-week chains contribute primary H2; partial accrued costs are separately labeled.",
                    "Final commitments after week24 are displayed but subsequent costs are outside the primary horizon.",
                    "Human observations=0. No p-values, independent-chain confidence intervals or hypothesis-proof claims."])
