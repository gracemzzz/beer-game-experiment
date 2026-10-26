"""Offline, separately versioned resource-opportunity Beer Game development.

An independent block is the analysis unit. Chains sharing one response are a
cluster, not additional independent observations. Arm A has one initial and one
revision request; B and C have one initial request. This is an actual decision
opportunity manipulation, not a measured human deadline. Nothing here calls an
API, chooses a result, or replaces missing model decisions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
from statistics import mean, variance

from .game import BeerGame, ROLES
from .batched_pressure import PROFILES

PROTOCOL = "weekly-resource-opportunity-v2-development"
SCHEMA = "weekly-resource-orders-v2"
WEEKS = 24
ARMS = ("A", "B", "C")
ROLE_KEYS = ("r", "w", "d", "f")
ORDER_GUARD = 100000  # Hidden technical circuit breaker, never a suggested order.
STATE_COLUMNS = ("inventory", "backlog", "supply_line", "demand", "received", "shipped")
DEFAULT_MODELS = ("gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra", "claude-sonnet-5-5")

# Deliberately matched in word count. Neither text supplies target decisions,
# response distributions, effect directions, regression coefficients, or answers.
EDUCATION = (
    "Classroom reading: Understanding supply-chain dynamics. "
    "A supply chain links businesses through orders and physical deliveries. "
    "An order is a request for goods; it is not an immediate receipt. "
    "Outstanding replenishment orders are requests already placed but not yet received. "
    "They can include goods in transit and quantities awaiting upstream fulfillment. "
    "Repeatedly responding to one shortage can create several requests before any delivery arrives. "
    "Later arrivals can therefore reflect decisions made in earlier weeks. "
    "Each business observes incoming requests from its customer, which can differ from final customer purchases. "
    "Changes in these requests can propagate through successive businesses and interact with delivery delays. "
    "Shared information helps participants distinguish current physical stock, customer obligations, and previously requested replenishment. "
    "This reading explains relationships; it does not prescribe an ordering rule."
)
CONTROL = (
    "Classroom reading: Understanding business record keeping. "
    "A business maintains records that describe activities in an organized manner. "
    "A document is an entry about an event; it supports later review. "
    "Business records are materials already created and retained for future reference. "
    "They can include forms on paper and entries in electronic systems. "
    "Consistently describing each event can make several documents easier to locate during a review. "
    "Later readers can therefore understand records prepared in earlier reporting periods. "
    "Each business maintains records for activities, which can differ from another business's documents. "
    "Differences in these records can reflect departmental responsibilities and interact with local filing practices. "
    "Clear organization helps participants distinguish document titles, responsible employees, and previously recorded information. "
    "This reading explains documentation; it does not prescribe an ordering rule."
)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def source_hashes():
    """Actual current bytes, not a claim to match historical line-ending hashes."""
    return {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("weekly_pivot_v2.py", "game.py", "batched_pressure.py")}


def make_plan(*, blocks=40, chains_per_cluster=1, models=DEFAULT_MODELS,
              seed=2026102501, output_caps=None, collection_kind="development"):
    """Prepare a prospective development plan without creating files or API calls."""
    if type(blocks) is not int or blocks < 1:
        raise ValueError("blocks must be a positive integer")
    if type(chains_per_cluster) is not int or chains_per_cluster < 1:
        raise ValueError("chains_per_cluster must be a positive integer")
    if type(seed) is not int or not models or len(set(models)) != len(models):
        raise ValueError("A fixed integer seed and unique model labels are required")
    if not all(isinstance(model, str) and model for model in models):
        raise ValueError("Model labels must be nonempty strings")
    if collection_kind not in ("development", "heldout"):
        raise ValueError("Collection kind must be development or heldout")
    if len(CONTROL.split()) != len(EDUCATION.split()):
        raise ValueError("Lecture word counts must match")
    caps = {"initial": 8192, "revision": 8192, "probe": 8192, "probe_revision": 8192}
    if output_caps is not None:
        if set(output_caps) != set(caps):
            raise ValueError("Specify all four request-phase output caps")
        caps.update(output_caps)
    if not all(type(value) is int and value > 0 for value in caps.values()):
        raise ValueError("Output caps must be positive integers")
    specs = []
    for index in range(blocks):
        chains = []
        for slot in range(chains_per_cluster):
            rng = random.Random(seed + 100003 * index + 1013 * slot)
            profiles = list(range(len(PROFILES)))
            rng.shuffle(profiles)
            chains.append({"chain_id": f"c{slot + 1:03d}", "profile_ids": profiles,
                           "customer_demand": [rng.randrange(9) for _ in range(WEEKS)]})
        specs.append({"block_id": f"b{index + 1:04d}", "chains": chains})
    identity = dict(protocol=PROTOCOL, schema_version=SCHEMA, seed=seed, weeks=WEEKS,
                    blocks=specs, models=list(models), chains_per_cluster=chains_per_cluster,
                    profiles=list(PROFILES), arms=list(ARMS), output_caps=caps,
                    requested_effort="high", temperature=None, history_weeks=4,
                    lectures={"control": CONTROL, "causal_education": EDUCATION},
                    lecture_word_counts={"control": len(CONTROL.split()), "causal_education": len(EDUCATION.split())},
                    arm_spec={"A": {"lecture": "control", "opportunities": 2},
                              "B": {"lecture": "control", "opportunities": 1},
                              "C": {"lecture": "causal_education", "opportunities": 1}},
                    source_hashes=source_hashes(),
                    inference_unit="independently generated model/block/arm response stream; matched block contrast",
                    construct="decision-opportunity resource analogue, not literal binding time pressure",
                    collection_kind=collection_kind, development_only=collection_kind == "development",
                    human_observations=0)
    identity["study_id"] = "weekly_pivot_v2_" + digest(identity)[:16]
    identity["expected_requests"] = len(models) * blocks * (4 * WEEKS + 4)
    identity["expected_weekly_requests"] = len(models) * blocks * 4 * WEEKS
    identity["expected_probe_requests"] = len(models) * blocks * 4
    return identity


def _block(plan, block_id):
    matches = [row for row in plan["blocks"] if row["block_id"] == block_id]
    if len(matches) != 1:
        raise ValueError("Unknown or duplicated block")
    return matches[0]


def task_id(model, block_id, arm, week=None, phase="initial"):
    if arm not in ARMS or phase not in ("initial", "revision", "probe", "probe_revision"):
        raise ValueError("Unknown arm or phase")
    if phase in ("initial", "revision"):
        if type(week) is not int or not 1 <= week <= WEEKS:
            raise ValueError("Weekly decisions require week 1 through 24")
        suffix = f"w{week:02d}_{phase}"
    else:
        if week is not None:
            raise ValueError("Probes are not a game week")
        suffix = phase
    return f"{model}__{block_id}__{arm}__{suffix}"


def _base(plan, model, block_id, arm, week, phase):
    if model not in plan["models"]:
        raise ValueError("Unplanned model")
    spec = _block(plan, block_id)
    ident = task_id(model, block_id, arm, week, phase)
    if phase in ("revision", "probe_revision") and plan["arm_spec"][arm]["opportunities"] != 2:
        raise ValueError("This arm has no revision opportunity")
    return dict(schema_version=SCHEMA, study_id=plan["study_id"], task_id=ident,
                model=model, block_id=block_id, arm=arm, week=week, phase=phase,
                max_output_tokens=plan["output_caps"][phase],
                chain_ids=[row["chain_id"] for row in spec["chains"]],
                profiles=plan["profiles"],
                lecture=plan["lectures"][plan["arm_spec"][arm]["lecture"]],
                chains=[{key: row[key] for key in ("chain_id", "profile_ids")} for row in spec["chains"]])


def _accepted_payload(task, accepted):
    payload = accepted.get(task["task_id"])
    if payload is None:
        raise ValueError("Missing accepted decision: " + task["task_id"])
    problems = validate_response(task, payload)
    if problems:
        raise ValueError("Invalid accepted decision: " + "; ".join(problems))
    return payload


def _final_payload(plan, model, block_id, arm, week, accepted):
    initial = _base(plan, model, block_id, arm, week, "initial")
    payload = _accepted_payload(initial, accepted)
    if plan["arm_spec"][arm]["opportunities"] == 2:
        final = _base(plan, model, block_id, arm, week, "revision")
        payload = _accepted_payload(final, accepted)
    return payload


def replay_prefix(plan, model, block_id, arm, accepted, through_week):
    """Rebuild only committed past weeks; absent decisions are a hard error."""
    if type(through_week) is not int or not 0 <= through_week <= WEEKS:
        raise ValueError("Invalid replay prefix")
    _base(plan, model, block_id, arm, 1, "initial")
    specs = _block(plan, block_id)["chains"]
    games = {spec["chain_id"]: BeerGame() for spec in specs}
    rows = []
    for week in range(1, through_week + 1):
        payload = _final_payload(plan, model, block_id, arm, week, accepted)
        for spec in specs:
            cid = spec["chain_id"]
            states = games[cid].observe(int(spec["customer_demand"][week - 1]))
            for index, state in enumerate(states):
                rows.append(dict(state, model=model, block_id=block_id, arm=arm,
                                 chain_id=cid, customer_demand=spec["customer_demand"][week - 1],
                                 order=payload["orders"][cid][index]))
            games[cid].commit(payload["orders"][cid])
    return games, rows


def _probe_states(plan, model, block_id, arm):
    """Matched hypothetical states; backlog 40 avoids prescribing positive actions."""
    cases = []
    for chain in _block(plan, block_id)["chains"]:
        for role_index, role in enumerate(ROLES):
            for backlog in (40, 64):
                for supply_line in (8, 32):
                    shared = {key: 12 for key in ROLES}
                    shared[role] = 0
                    cases.append(dict(chain_id=chain["chain_id"], role=role,
                                      profile_id=chain["profile_ids"][role_index],
                                      inventory=0, backlog=backlog, supply_line=supply_line,
                                      demand=8, received=4, shipped=4, shared_inventory=shared))
    seed = int(digest([plan["seed"], model, block_id, arm, "probe-order"])[:16], 16)
    random.Random(seed).shuffle(cases)
    return [dict(probe_id=f"p{index + 1:03d}", **state) for index, state in enumerate(cases)]


def build_task(plan, model, block_id, arm, week=None, phase="initial", accepted=None):
    """Make an isolated request with current states and four past weeks only.

    Revision requests contain exactly the same physical state as the initial
    request and its accepted first proposal. They do not advance the game.
    Requests never contain other arms, models, future demand, or the game end.
    """
    accepted = {} if accepted is None else accepted
    task = _base(plan, model, block_id, arm, week, phase)
    if phase in ("probe", "probe_revision"):
        replay_prefix(plan, model, block_id, arm, accepted, WEEKS)
        task["probes"] = _probe_states(plan, model, block_id, arm)
        if phase == "probe_revision":
            initial = _base(plan, model, block_id, arm, None, "probe")
            initial["probes"] = task["probes"]
            task["initial_decisions"] = _accepted_payload(initial, accepted)["decisions"]
        return task
    games, rows = replay_prefix(plan, model, block_id, arm, accepted, week - 1)
    task["states"], task["history"] = {}, {}
    for spec in _block(plan, block_id)["chains"]:
        cid = spec["chain_id"]
        task["states"][cid] = games[cid].observe(int(spec["customer_demand"][week - 1]))
        recent = [row for row in rows if row["chain_id"] == cid and row["week"] >= week - plan["history_weeks"]]
        task["history"][cid] = [
            {"week": previous, "demand_order_by_role": [[row["demand"], row["order"]]
                                                       for row in recent if row["week"] == previous]}
            for previous in sorted({row["week"] for row in recent})]
    if phase == "revision":
        initial = _base(plan, model, block_id, arm, week, "initial")
        task["initial_orders"] = _accepted_payload(initial, accepted)["orders"]
    return task


def response_schema(task):
    """Strict provider-neutral JSON schema, without the hidden numerical guard."""
    properties = {key: {"type": "string", "const": task[key]}
                  for key in ("schema_version", "study_id", "task_id")}
    if task["phase"] in ("probe", "probe_revision"):
        key = "decisions"
        entries = {row["probe_id"]: {"type": "integer", "minimum": 0} for row in task["probes"]}
    else:
        key = "orders"
        entries = {cid: {"type": "array", "items": {"type": "integer", "minimum": 0},
                         "minItems": 4, "maxItems": 4} for cid in task["chain_ids"]}
    properties[key] = {"type": "object", "properties": entries, "required": list(entries),
                       "additionalProperties": False}
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}


def validate_response(task, payload):
    """Reject malformed/missing data, including booleans; accept zero orders."""
    if not isinstance(payload, dict):
        return ["Response must be a JSON object"]
    probe = task["phase"] in ("probe", "probe_revision")
    field = "decisions" if probe else "orders"
    errors = []
    expected_keys = {"schema_version", "study_id", "task_id", field}
    if set(payload) != expected_keys:
        errors.append("Unexpected or missing response keys")
    for key in ("schema_version", "study_id", "task_id"):
        if payload.get(key) != task[key]:
            errors.append("Mismatched " + key)
    decisions = payload.get(field)
    ids = [row["probe_id"] for row in task["probes"]] if probe else task["chain_ids"]
    if not isinstance(decisions, dict) or set(decisions) != set(ids):
        errors.append("Decisions must cover every requested ID exactly once")
        return errors
    for ident, value in decisions.items():
        values = [value] if probe else value
        if not isinstance(values, list) or (not probe and len(values) != 4):
            errors.append("Each chain requires exactly four orders")
            continue
        if any(type(order) is not int or not 0 <= order <= ORDER_GUARD for order in values):
            errors.append("Invalid integer order or technical circuit breaker exceeded: " + ident)
    return errors


def prompt_text(task):
    """Exact human-readable prompt; all arms use one identical question format."""
    context = {key: task[key] for key in ("schema_version", "study_id", "task_id")}
    context["role_order"] = list(ROLE_KEYS)
    context["profiles"] = task["profiles"]
    if task["phase"] in ("probe", "probe_revision"):
        context["hypothetical_independent_decisions"] = task["probes"]
        if "initial_decisions" in task:
            context["initial_proposals"] = task["initial_decisions"]
        instruction = "For each hypothetical independent situation, choose that student's replenishment order. These are separate situations, not extra game weeks."
        example = dict(schema_version=SCHEMA, study_id=task["study_id"], task_id=task["task_id"],
                       decisions={row["probe_id"]: "nonnegative integer" for row in task["probes"]})
    else:
        context["week"] = task["week"]
        context["state_columns"] = list(STATE_COLUMNS)
        context["chains"] = [dict(chain_id=row["chain_id"], profile_ids=row["profile_ids"],
                                  state=[[state[key] for key in STATE_COLUMNS]
                                         for state in task["states"][row["chain_id"]]],
                                  shared_inventory=task["states"][row["chain_id"]][0]["shared_inventory"],
                                  history=task["history"][row["chain_id"]]) for row in task["chains"]]
        if "initial_orders" in task:
            context["initial_proposals"] = task["initial_orders"]
        instruction = "Choose one replenishment order for each student in the current week."
        example = dict(schema_version=SCHEMA, study_id=task["study_id"], task_id=task["task_id"],
                       orders={cid: ["retailer integer", "wholesaler integer", "distributor integer", "factory integer"]
                               for cid in task["chain_ids"]})
    revision = ("This is one additional opportunity to reconsider the accepted initial proposals shown below. "
                "The physical state and information have not changed. You may retain or revise any proposal.\n"
                if task["phase"] in ("revision", "probe_revision") else "")
    return (
        "Simulate the decisions of fictional second-year business students at the University at Buffalo in an American university classroom. "
        "These are hypothetical students, not real respondents or estimates from student data. "
        "Use each supplied ordinary-coursework profile consistently, without assuming it implies any particular ordering rule. "
        "Represent plausible student judgments using the information and reading below. Do not aim for a particular experimental result.\n\n"
        "Game rules: Roles are retailer, wholesaler, distributor, factory (r,w,d,f). Orders and cases are nonnegative whole numbers. "
        "Customer orders move one role upstream for the next week; physical shipments take two weeks to reach the next downstream role. "
        "Factory production ordered now arrives three weeks later. Backlog already includes current unmet demand and carries forward. "
        "Supply line means all your replenishment orders outstanding after this week's receipt. "
        "All roles' current inventory is shared. Holding cost is 0.5 per case per week; backlog cost is 1 per case per week. "
        "The classroom objective is to minimize the team's cumulative holding and backlog costs over the continuing game. "
        "Future customer demand is unknown. Python has already processed this week's receipts and shipments. "
        "Submit only ordering decisions; do not calculate replacement physical states.\n\n"
        + task["lecture"] + "\n\n" + revision + instruction + "\n"
        "Return exactly one JSON object with the keys and requested IDs shown in the output template. "
        "Replace each integer description with your chosen integer. Do not include explanations or Markdown fences.\n\n"
        "INPUT\n" + json.dumps(context, ensure_ascii=False, separators=(",", ":"))
        + "\n\nOUTPUT TEMPLATE\n" + json.dumps(example, ensure_ascii=False, separators=(",", ":")))


def probe_sensitivity(task, payload):
    """Mean (order_at_pipeline_8 - order_at_pipeline_32)/24; descriptive proxy."""
    errors = validate_response(task, payload)
    if errors:
        raise ValueError("; ".join(errors))
    pairs = {}
    for state in task["probes"]:
        pairs.setdefault((state["chain_id"], state["role"], state["backlog"]), {})[state["supply_line"]] = payload["decisions"][state["probe_id"]]
    return mean((orders[8] - orders[32]) / 24 for orders in pairs.values())


def backlog_sensitivity(task, payload):
    """Mean (order_at_backlog_64 - order_at_backlog_40)/24, holding pipeline fixed."""
    errors = validate_response(task, payload)
    if errors:
        raise ValueError("; ".join(errors))
    pairs = {}
    for state in task["probes"]:
        pairs.setdefault((state["chain_id"], state["role"], state["supply_line"]), {})[state["backlog"]] = payload["decisions"][state["probe_id"]]
    return mean((orders[64] - orders[40]) / 24 for orders in pairs.values())


def block_outcomes(plan, model, block_id, arm, accepted):
    """Return one cluster-level row; incomplete data remain explicitly missing."""
    _base(plan, model, block_id, arm, 1, "initial")
    row = dict(model=model, block_id=block_id, arm=arm, complete=False, probe_complete=False, weeks=0,
               chains_in_cluster=plan["chains_per_cluster"], pipeline_sensitivity=None,
               backlog_sensitivity=None, probe_zero_order_fraction=None, game_zero_order_fraction=None,
               chain_total_cost=None, cluster_total_cost=None,
               mean_role_order_variance=None, mean_role_bullwhip=None,
               undefined_bullwhip_roles=None, missing_tasks=[], missing_probes=[])
    through_week = 0
    for week in range(1, WEEKS + 1):
        phases = ("initial", "revision") if arm == "A" else ("initial",)
        missing = [task_id(model, block_id, arm, week, phase) for phase in phases
                   if task_id(model, block_id, arm, week, phase) not in accepted]
        if missing:
            row["missing_tasks"].extend(missing)
            break
        _final_payload(plan, model, block_id, arm, week, accepted)
        through_week = week
    row["weeks"] = through_week
    if through_week < WEEKS:
        return row
    _, rows = replay_prefix(plan, model, block_id, arm, accepted, WEEKS)
    chain_costs, order_variances, bullwhip = [], [], []
    for spec in _block(plan, block_id)["chains"]:
        chain_rows = [state for state in rows if state["chain_id"] == spec["chain_id"]]
        chain_costs.append(sum(state["cost"] for state in chain_rows))
        denominator = variance(spec["customer_demand"])
        for role in ROLES:
            numerator = variance([state["order"] for state in chain_rows if state["role"] == role])
            order_variances.append(numerator)
            bullwhip.append(numerator / denominator if denominator > 0 else None)
    row["cluster_total_cost"] = sum(chain_costs)
    row["chain_total_cost"] = mean(chain_costs)
    row["complete"] = True
    row["game_zero_order_fraction"] = mean(state["order"] == 0 for state in rows)
    row["mean_role_order_variance"] = mean(order_variances)
    row["undefined_bullwhip_roles"] = sum(value is None for value in bullwhip)
    # Do not silently average around undefined roles/zero demand denominators.
    row["mean_role_bullwhip"] = mean(bullwhip) if all(value is not None for value in bullwhip) else None
    phases = ("probe", "probe_revision") if arm == "A" else ("probe",)
    for phase in phases:
        ident = task_id(model, block_id, arm, None, phase)
        if ident not in accepted:
            row["missing_probes"].append(ident)
    if row["missing_probes"]:
        return row
    task = build_task(plan, model, block_id, arm, phase="probe", accepted=accepted)
    payload = _accepted_payload(task, accepted)
    if arm == "A":
        task = build_task(plan, model, block_id, arm, phase="probe_revision", accepted=accepted)
        payload = _accepted_payload(task, accepted)
    row["pipeline_sensitivity"] = probe_sensitivity(task, payload)
    row["backlog_sensitivity"] = backlog_sensitivity(task, payload)
    row["probe_zero_order_fraction"] = mean(value == 0 for value in payload["decisions"].values())
    row["probe_complete"] = True
    return row
