"""Prospective API pressure-framing study; importing/preparing never calls a model.

One request generates the complete twenty-chain cohort for one model. Joint
generation supports descriptive framing contrasts, not independent-chain tests.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import random
from statistics import mean

from .game import BeerGame, ROLES

PROTOCOL = "batched-pressure-api-v1"
SCHEMA = "batched-pressure-chain-v1"
MODELS = ("gpt-6-luna", "gpt-5.6-luna", "gpt-5.6-sol", "claude-haiku-5-5")
CONDITIONS = ("no_pressure", "strong_pressure")
WEEKS = 24
CHECKPOINTS = (1, 12, 24)
RULE_ANSWERS = {
    "backlog_includes_current_unfilled_demand": True,
    "factory_order_week_7_arrival_week": 10,
    "three_week_backlog_cost": 15,
}
HYPOTHESES = {
    "H1": "Within an information-sharing environment, a binding decision-time constraint increases the underweighting of outstanding replenishment orders relative to adequate decision time.",
    "H2": "Supply chains operating under a binding decision-time constraint incur higher cumulative total inventory-holding and backlog costs than supply chains operating with adequate decision time.",
}
PROFILES = (
    "Organized and emotionally steady in ordinary coursework.",
    "Organized and concerned by uncertainty in ordinary coursework.",
    "Flexible and emotionally steady in ordinary coursework.",
    "Flexible and concerned by uncertainty in ordinary coursework.",
)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_new(path, value):
    """Create immutable evidence; permit only exact repeat writes."""
    path = Path(path)
    data = value if isinstance(value, bytes) else (
        value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refusing to replace frozen evidence: " + str(path))
    else:
        with path.open("xb") as stream:
            stream.write(data)


def _probes(seed):
    """Orthogonal backlog/pipeline states; pair mappings are analysis metadata."""
    rng = random.Random(seed)
    cases = []
    for role in ROLES:
        for backlog in (8, 24):
            for supply_line in (8, 32):
                shared = {r: 12 for r in ROLES}
                shared[role] = 0
                cases.append(dict(role=role, week=12, demand=8, received=4, shipped=4,
                                  inventory=0, backlog=backlog, net_inventory=-backlog,
                                  supply_line=supply_line, awaiting_dispatch=0,
                                  deliveries_due=[supply_line//2, supply_line//2] + ([0] if role == "factory" else []),
                                  shared_inventory=shared))
    rng.shuffle(cases)
    return [dict(probe_id=f"x{i:02d}", **case) for i, case in enumerate(cases)]


def _tasks(study_id, seed):
    tasks = []
    probe_bank = _probes(seed + 30500)
    for phase, blocks, offset in (("pilot", 1, 10000), ("main", 10, 20000)):
        for block in range(blocks):
            rng = random.Random(seed + offset + block * 1009)
            demands = [rng.randrange(9) for _ in range(WEEKS)]
            profile_order = list(range(4))
            rng.shuffle(profile_order)
            # Assignment to distinct chain slots is frozen before any generation.
            assigned = list(CONDITIONS)
            rng.shuffle(assigned)
            probes = list(probe_bank)
            random.Random(seed + offset + block * 1013).shuffle(probes)
            for model_index, model in enumerate(MODELS):
                # Alternate which condition is requested first across blocks/models.
                order = CONDITIONS if (block + model_index) % 2 == 0 else tuple(reversed(CONDITIONS))
                for condition in order:
                    slot = assigned.index(condition)
                    chain_id = f"{phase}_b{block:02d}_c{slot}"
                    task_id = f"{model}_{phase}_b{block:02d}_{condition}"
                    task = dict(schema_version=SCHEMA, study_id=study_id, task_id=task_id,
                                model=model, phase=phase, block=block, condition=condition,
                                chain_id=chain_id, chain_slot=slot, weeks=WEEKS,
                                participant_ids=[f"{model}_{chain_id}_{r}" for r in ROLES],
                                profiles=[PROFILES[i] for i in profile_order],
                                customer_demand=demands, probes=probes,
                                checkpoints=list(CHECKPOINTS), response_path=f"accepted/{task_id}.json",
                                prompt_path=f"prompts/{study_id}/{model}/{phase}/{task_id}.txt",
                                schema_path=f"prompts/{study_id}/{model}/{phase}/{task_id}.schema.json")
                    tasks.append(task)
    cohorts = []
    for phase in ("pilot", "main"):
        for model_index, model in enumerate(MODELS):
            own = [t for t in tasks if t["model"] == model and t["phase"] == phase]
            task_id = f"{model}_{phase}"
            random.Random(seed + model_index * 37 + (1 if phase == "pilot" else 2)).shuffle(own)
            for chain in own:
                chain["task_id"] = task_id
                for key in ("response_path", "prompt_path", "schema_path"):
                    chain.pop(key)
            cohorts.append(dict(schema_version=SCHEMA, study_id=study_id, task_id=task_id,
                                model=model, phase=phase, chains=own, effort="low",
                                max_output_tokens=8192 if phase == "pilot" else 16384,
                                response_path=f"accepted/{task_id}.json",
                                prompt_path=f"prompts/{study_id}/{model}/{phase}/{task_id}.txt",
                                schema_path=f"prompts/{study_id}/{model}/{phase}/{task_id}.schema.json"))
    return cohorts


def prepare(experiment: Path, cap_usd=5.0, label="pressure-framing-80-per-model") -> Path:
    """Freeze four pilot and four complete-cohort requests before API use."""
    experiment = Path(experiment).resolve()
    if type(cap_usd) not in (int, float) or not 0 < cap_usd <= 5:
        raise ValueError("This campaign is authorized for at most $5 total, including pilot/retries.")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("A nonempty study label is required.")
    sources = {"batched_pressure.py": Path(__file__),
               "batched_pressure_api.py": Path(__file__).with_name("batched_pressure_api.py"),
               "game.py": Path(__file__).with_name("game.py"),
               "PROTOCOL.md": experiment / "hypotheses/PROTOCOL.md"}
    identity = dict(protocol=PROTOCOL, schema_version=SCHEMA, label=label,
                    seed=2026102003, cap_usd=float(cap_usd), models=list(MODELS),
                    effort="low", output_caps={"pilot": 8192, "main": 16384}, weeks=WEEKS,
                    main_chains_per_model=20, main_identities_per_model=80,
                    source_hashes={name: hashlib.sha256(path.read_bytes()).hexdigest()
                                   for name, path in sources.items()})
    study_id = "pressure_api_" + digest(identity)[:16]
    run = experiment / "data" / study_id
    tasks = _tasks(study_id, identity["seed"])
    plan = dict(identity, study_id=study_id, hypotheses=HYPOTHESES, tasks=tasks,
                expected_pilot_requests=4, expected_main_requests=4,
                human_observations=0, pilot_in_primary_sample=False,
                primary_cost="Exactly 24 model-decision weeks; no practice or automatic continuation.",
                primary_h1="Mean matched-state pipeline sensitivity, a proxy rather than structural beta.",
                intervention="Imagined classroom pressure, not enforced time or compute.",
                pilot_gate="All four disjoint two-chain pilot responses must pass strict schema, rules and all physical inventory readbacks before any main request. No outcome-direction, variability or significance gate.",
                stopping="Fixed four pilot and four main slots; no semantic retries or replacements; retain incomplete/invalid attempts. Transport retries require the same request and shared budget reservation.",
                inference="Descriptive only. All twenty chains and both conditions are jointly generated in one response per model. No p-values, inferential confidence intervals or independent-chain/human claims.")
    save_new(run / "plan.json", plan)
    save_new(run / "plan.sha256", digest(plan) + "\n")
    for name, path in sources.items():
        save_new(run / "source_snapshot" / name, path.read_bytes())
    for task in tasks:
        save_new(experiment / task["prompt_path"], prompt_text(task))
        save_new(experiment / task["schema_path"], response_schema(task))
    (run / "accepted").mkdir(parents=True, exist_ok=True)
    return run


def loadplan(run):
    run = Path(run)
    plan = read(run / "plan.json")
    if (run / "plan.sha256").read_text().strip() != digest(plan):
        raise ValueError("Frozen study plan changed.")
    if plan.get("protocol") != PROTOCOL or plan.get("schema_version") != SCHEMA:
        raise ValueError("Unsupported study protocol/schema.")
    for name, expected in plan["source_hashes"].items():
        if hashlib.sha256((run / "source_snapshot" / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Frozen source snapshot changed: " + name)
    for name in ("batched_pressure.py", "batched_pressure_api.py", "game.py"):
        if hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() != plan["source_hashes"][name]:
            raise ValueError("Scientific implementation changed; prepare a new run: " + name)
    experiment = run.parent.parent
    for task in plan["tasks"]:
        if (experiment / task["prompt_path"]).read_text(encoding="utf-8") != prompt_text(task):
            raise ValueError("Frozen prompt changed: " + task["task_id"])
        if read(experiment / task["schema_path"]) != response_schema(task):
            raise ValueError("Frozen response schema changed: " + task["task_id"])
    return plan


def prompt_text(task):
    pressure = {
        "no_pressure": "The students experience no time pressure. They have ample time to consider each decision before submitting it.",
        "strong_pressure": "The students experience strong time pressure. They feel they must submit each decision promptly before their decision opportunity closes.",
    }
    context = {key: task[key] for key in ("schema_version", "study_id", "task_id")}
    context["probe_states"] = task["chains"][0]["probes"]
    context["inventory_checkpoint_weeks"] = list(CHECKPOINTS)
    context["chains"] = [dict({key: chain[key] for key in ("chain_id", "participant_ids", "profiles",
                                                          "customer_demand")},
                               probe_order=[p["probe_id"] for p in chain["probes"]],
                               classroom_situation=pressure[chain["condition"]]) for chain in task["chains"]]
    context["role_order"] = list(ROLES)
    return """Generate the Beer Game choices of the supplied fictional undergraduate cohort.
Each chain has four students, one at each role. Each has introductory business knowledge,
no previous Beer Game experience and no specialist inventory training. The supplied
personality describes ordinary coursework, not an ordering strategy. Each student
tries to minimize the team's cumulative inventory-holding and backlog costs.
Use the same assigned identity throughout. Do not invent demographic characteristics,
deliberate mistakes, a target pattern, or artificial differences between students.
Identical choices and zero orders are allowed.

CLASSROOM SITUATIONS
Each chain's input states its own classroom situation. Apply that situation to
all four students in that chain. Track chains separately; one chain's choices
are not information available to another chain. Each situation describes a
fictional student's experience. It does not impose or measure
actual model computation time, a deadline, or psychological pressure.
All chains and situations are nevertheless visible to this single generator.

PHYSICAL RULES
Role order is retailer, wholesaler, distributor, factory. Each week, each role
orders a nonnegative integer number of cases; the factory starts production.
There is no revenue, production charge, ordering fee, bulk discount or capacity
limit. Holding cost is $0.50 per remaining case per week; backlog cost is $1 per
unfilled case per week. No preferred order quantity or maximum is supplied.

Initially every role has inventory 12, backlog 0 and 12 outstanding cases.
Retailer, wholesaler and distributor each have deliveries [4,4] due in the next
two weeks and 4 previously ordered cases awaiting upstream dispatch. Factory
production completions are [4,4,4]. Upstream incoming orders initially equal 4.
All 24 displayed weeks require student choices; there are no practice or extra
scoring weeks. The exact supplied customer-demand path is used without changes.

For each week, first receive the next due delivery and subtract it from outstanding
orders. Next observe incoming demand: customer demand for the retailer, or the
downstream role's preceding-week order for other roles. Ship min(available stock,
old backlog + new demand). Remaining inventory and backlog are then nonnegative;
current backlog already includes unfilled current demand and persists. Assess
that week's holding/backlog costs. Observe the decision display and submit orders.
Each new order is added to outstanding orders and reaches the upstream supplier
next week. A supplier's shipment takes two weeks to arrive downstream, so the
earliest receipt of an order made at t is t+3, later if the supplier has shortages.
Factory production started at t arrives at t+3 without any additional supplier
or raw-material delay. Outstanding orders cannot be canceled. A new order cannot
change today's shipment, inventory or backlog.

At each decision, a student can use its current local state, own earlier rounds,
and all four current inventories. Other roles' orders/backlogs and future demand
are unavailable to that student. You see the complete path and horizon for data
generation; do not intentionally give future information to the fictional student.
Generating the entire chain jointly cannot enforce true information isolation.
Track the four evolving states using the stated rules. The inventory checkpoints
refer to the moment after that week's receipts and shipments, before its orders.

SEPARATE STATE QUESTIONS
The shared probe_states bank defines sixteen hypothetical displays. For EACH
chain, answer every display in that chain's probe_order. Independently choose one order for its stated role and
assigned student in the same classroom situation. These hypothetical displays do
not inherit any chain history or earlier probe decision. Use only the displayed
state. The deliveries_due list gives future arrivals starting next week; awaiting
dispatch is separate. Return each neutral probe ID exactly once.

OUTPUT
Return only one complete JSON object matching the supplied schema, containing
every supplied chain exactly once. Do not return
costs, statistical results, explanations, programming code, or claims about an
experiment. For EACH chain, supply exactly 24 rows of four literal nonnegative
integer orders in role order, exactly 16 probe choices, and all three inventory
checkpoints. No
Booleans, strings, decimals, nulls, ellipses or omitted choices as order values.
Answer these three common factual questions ONCE in root-level rules: Does current backlog already
include this week's unfilled demand? When does factory production begun in week 7
arrive? What is the cost of five backlogged cases at the end of each of three weeks?
Use a JSON Boolean for the first answer and integers for the other two. Keep all
supplied identifiers unchanged. Set complete true only for a complete response.
Never replace omitted choices with an aggregate description or invented results.

FROZEN INPUT DATA
""" + json.dumps(context, separators=(",", ":"), ensure_ascii=False) + "\n"


def response_schema(task):
    integer = {"type": "integer", "minimum": 0}
    def obj(properties):
        return dict(type="object", properties=properties, required=list(properties), additionalProperties=False)
    def fixed(value):
        return dict(type="string", enum=[value])
    def arr(item, n):
        return dict(type="array", items=item, minItems=n, maxItems=n)
    chain = obj(dict(
        chain_id={"type": "string", "enum": [c["chain_id"] for c in task["chains"]]},
        orders=arr(arr(integer, 4), WEEKS),
        probes=arr(obj(dict(probe_id={"type": "string", "enum": [f"x{i:02d}" for i in range(16)]},
                            order=integer)), 16),
        inventory_checkpoints=arr(obj(dict(week={"type": "integer", "enum": list(CHECKPOINTS)},
                                           inventories=arr(integer, 4))), 3),
    ))
    return obj(dict(
        schema_version=fixed(SCHEMA), study_id=fixed(task["study_id"]),
        task_id=fixed(task["task_id"]),
        rules=obj(dict(backlog_includes_current_unfilled_demand={"type": "boolean"},
                       factory_order_week_7_arrival_week={"type": "integer"},
                       three_week_backlog_cost={"type": "integer"})),
        chains=arr(chain, len(task["chains"])),
        complete={"type": "boolean", "enum": [True]},
    ))


def _replay_chain(task, payload):
    """Independently calculate physical accounting; no API and no extra weeks."""
    game, rows = BeerGame(), []
    common = {key: task[key] for key in ("task_id", "model", "phase", "block", "condition", "chain_id")}
    for week, (demand, orders) in enumerate(zip(task["customer_demand"], payload["orders"]), 1):
        states = game.observe(int(demand))
        for index, state in enumerate(states):
            rows.append(dict(state, **common, order=orders[index], customer_demand=demand,
                             participant_id=task["participant_ids"][index],
                             holding_cost=0.5 * state["inventory"], backlog_cost=state["backlog"]))
        game.commit(orders)
    return rows


def _validate_chain(task, payload):
    """Return all relevant technical issues; invalid choices are never repaired."""
    issues = []
    required = {"schema_version", "study_id", "task_id", "chain_id", "rules", "orders",
                "probes", "inventory_checkpoints", "complete"}
    if type(payload) is not dict or set(payload) != required:
        return ["Root fields must match the exact schema."]
    for key in ("schema_version", "study_id", "task_id", "chain_id"):
        if payload[key] != task[key]:
            issues.append("Wrong " + key)
    if payload["complete"] is not True:
        issues.append("Response is incomplete.")
    rules = payload["rules"]
    if (type(rules) is not dict or set(rules) != set(RULE_ANSWERS) or rules != RULE_ANSWERS or
            type(rules.get("backlog_includes_current_unfilled_demand")) is not bool or
            type(rules.get("factory_order_week_7_arrival_week")) is not int or
            type(rules.get("three_week_backlog_cost")) is not int):
        issues.append("Factual rule comprehension or types failed.")
    orders = payload["orders"]
    valid_orders = (type(orders) is list and len(orders) == WEEKS and
                    all(type(row) is list and len(row) == 4 and
                        all(type(q) is int and 0 <= q <= 100000 for q in row) for row in orders))
    if not valid_orders:
        issues.append("Expected 24 four-integer order rows; technical safety ceiling 100000, no clipping.")
    probes = payload["probes"]
    valid_probes = (type(probes) is list and len(probes) == 16 and
                    all(type(p) is dict and set(p) == {"probe_id", "order"} and
                        type(p["probe_id"]) is str and type(p["order"]) is int and
                        0 <= p["order"] <= 100000 for p in probes))
    if not valid_probes or Counter(p["probe_id"] for p in probes) != Counter(p["probe_id"] for p in task["probes"]):
        issues.append("Missing/duplicate/unknown probe IDs or invalid probe choices.")
    checkpoints = payload["inventory_checkpoints"]
    valid_checks = (type(checkpoints) is list and len(checkpoints) == 3 and
                    all(type(p) is dict and set(p) == {"week", "inventories"} and
                        type(p["week"]) is int and type(p["inventories"]) is list and len(p["inventories"]) == 4 and
                        all(type(q) is int and q >= 0 for q in p["inventories"]) for p in checkpoints))
    if not valid_checks or Counter(p["week"] for p in checkpoints) != Counter(CHECKPOINTS):
        issues.append("Inventory checkpoints must include weeks 1, 12 and 24 exactly once.")
    elif valid_orders:
        rows = _replay_chain(task, payload)
        for checkpoint in checkpoints:
            expected = [row["inventory"] for row in rows if row["week"] == checkpoint["week"]]
            if checkpoint["inventories"] != expected:
                issues.append(f"Physical inventory readback mismatch at week {checkpoint['week']}.")
    return issues


def validate_response(task, payload):
    """Validate the whole cohort without repairing or dropping any chain."""
    required = {"schema_version", "study_id", "task_id", "rules", "chains", "complete"}
    if type(payload) is not dict or set(payload) != required:
        return ["Root fields must match the exact cohort schema."]
    issues = []
    for key in ("schema_version", "study_id", "task_id"):
        if payload[key] != task[key]:
            issues.append("Wrong " + key)
    if payload["complete"] is not True:
        issues.append("Response is incomplete.")
    chains = payload["chains"]
    expected_keys = {"chain_id", "orders", "probes", "inventory_checkpoints"}
    if (type(chains) is not list or len(chains) != len(task["chains"]) or
            any(type(c) is not dict or set(c) != expected_keys or type(c["chain_id"]) is not str for c in chains)):
        return issues + ["Wrong chain count, fields or chain ID types."]
    if Counter(c["chain_id"] for c in chains) != Counter(c["chain_id"] for c in task["chains"]):
        return issues + ["Missing, duplicate or unknown chain IDs."]
    specs = {c["chain_id"]: c for c in task["chains"]}
    for chain in chains:
        wrapped = dict(chain, schema_version=payload["schema_version"], study_id=payload["study_id"],
                       task_id=payload["task_id"], rules=payload["rules"], complete=payload["complete"])
        issues.extend(chain["chain_id"] + ": " + message for message in _validate_chain(specs[chain["chain_id"]], wrapped))
    return issues


def replay(task, payload):
    """Flatten physical accounting for all chains in one cohort reply."""
    specs = {c["chain_id"]: c for c in task["chains"]}
    return [row for chain in payload["chains"] for row in _replay_chain(specs[chain["chain_id"]], chain)]


def synthetic_fixture(task):
    """Return an explicitly synthetic software fixture, NEVER write live evidence.

    All roles mechanically order their incoming demand, independent of framing;
    the fixed probe policy is only an arithmetic test. Callers must keep this in
    temporary/software-check directories and label outputs as synthetic.
    """
    chains = []
    for spec in task["chains"]:
        game, orders, checkpoints = BeerGame(), [], []
        for week, demand in enumerate(spec["customer_demand"], 1):
            states = game.observe(int(demand))
            choices = [state["demand"] for state in states]
            if week in CHECKPOINTS:
                checkpoints.append(dict(week=week, inventories=[state["inventory"] for state in states]))
            orders.append(choices)
            game.commit(choices)
        probes = [dict(probe_id=p["probe_id"], order=max(0, 8 + p["backlog"] - p["supply_line"]))
                  for p in spec["probes"]]
        chains.append(dict(chain_id=spec["chain_id"], orders=orders, probes=probes,
                           inventory_checkpoints=checkpoints))
    return dict(schema_version=SCHEMA, study_id=task["study_id"], task_id=task["task_id"],
                rules=RULE_ANSWERS.copy(), chains=chains, complete=True)


def task_metrics(task, payload):
    """Metrics for one chain specification and its submitted choice object."""
    rows = _replay_chain(task, payload)
    choices = {p["probe_id"]: p["order"] for p in payload["probes"]}
    probe_rows = [dict(p, order=choices[p["probe_id"]], task_id=task["task_id"], model=task["model"],
                       phase=task["phase"], block=task["block"], condition=task["condition"]) for p in task["probes"]]
    lookup = {(p["role"], p["backlog"], p["supply_line"]): p["order"] for p in probe_rows}
    sensitivity = mean((lookup[role, backlog, 8] - lookup[role, backlog, 32]) / 24
                       for role in ROLES for backlog in (8, 24))
    backlog_response = mean((lookup[role, 24, supply] - lookup[role, 8, supply]) / 16
                            for role in ROLES for supply in (8, 32))
    metrics = {key: task[key] for key in ("task_id", "model", "phase", "block", "condition", "chain_id")}
    metrics.update(total_cost=sum(r["cost"] for r in rows),
                   holding_cost=sum(r["holding_cost"] for r in rows),
                   backlog_cost=sum(r["backlog_cost"] for r in rows),
                   sensitivity=sensitivity, backlog_response=backlog_response,
                   relative_probe_weight=sensitivity/backlog_response if abs(backlog_response) >= .02 else None,
                   relative_probe_weight_usable=abs(backlog_response) >= .02,
                   zero_orders=sum(r["order"] == 0 for r in rows),
                   min_order=min(r["order"] for r in rows), max_order=max(r["order"] for r in rows),
                   final_inventory=sum(r["inventory"] for r in rows if r["week"] == WEEKS),
                   final_backlog=sum(r["backlog"] for r in rows if r["week"] == WEEKS),
                   final_supply_line=sum(r["supply_line"] + r["order"] for r in rows if r["week"] == WEEKS))
    return metrics, rows, probe_rows


def analyze(run):
    """Descriptive only: each model supplies one jointly generated main reply."""
    run = Path(run)
    plan = loadplan(run)
    task_status, chains, rounds, probes = [], [], [], []
    for task in plan["tasks"]:
        path = run / task["response_path"]
        status = {key: task[key] for key in ("task_id", "model", "phase")}
        status.update(status="missing", issues=[])
        if path.exists():
            try:
                payload = read(path)
                issues = validate_response(task, payload)
            except (ValueError, TypeError, KeyError, AssertionError, OverflowError) as exc:
                issues = [type(exc).__name__ + ": " + str(exc)]
            status.update(status="invalid" if issues else "accepted", issues=issues)
            if not issues:
                specs = {c["chain_id"]: c for c in task["chains"]}
                for chain in payload["chains"]:
                    metrics, own_rounds, own_probes = task_metrics(specs[chain["chain_id"]], chain)
                    chains.append(metrics)
                    rounds.extend(own_rounds)
                    probes.extend(own_probes)
        task_status.append(status)
    hypotheses, contrasts, model_status = [], [], []
    for mi, model in enumerate(MODELS):
        own = [row for row in chains if row["model"] == model]
        pilot_count = sum(row["phase"] == "pilot" for row in own)
        main = [row for row in own if row["phase"] == "main"]
        complete = pilot_count == 2 and len(main) == 20
        model_status.append(dict(model=model, accepted_pilot=pilot_count, expected_pilot=2,
                                 accepted_main=len(main), expected_main=20, complete=complete,
                                 accepted_pilot_responses=int(pilot_count == 2),
                                 accepted_main_responses=int(len(main) == 20), inference_available=False))
        lookup = {(row["block"], row["condition"]): row for row in main}
        for name, metric, sign in (("H1", "sensitivity", -1), ("H2", "total_cost", 1)):
            differences = []
            for block in range(10):
                if (block, "no_pressure") not in lookup or (block, "strong_pressure") not in lookup:
                    continue
                low, high = lookup[block, "no_pressure"], lookup[block, "strong_pressure"]
                difference = high[metric] - low[metric]
                differences.append(difference)
                contrasts.append(dict(model=model, hypothesis=name, block=block, metric=metric,
                                      no_pressure=low[metric], strong_pressure=high[metric], difference=difference))
            effect = mean(differences) if differences else None
            hypotheses.append(dict(model=model, hypothesis=name, metric=metric,
                                   expected_sign=sign, paired_blocks=len(differences),
                                   mean_strong_minus_no=effect,
                                   descriptive_direction=("unavailable" if effect is None else "zero" if effect == 0 else
                                                          "predicted" if sign*effect > 0 else "opposite"),
                                   p_raw=None,
                                   p_holm_8=None,
                                   paired_bootstrap_95=None,
                                   inference_available=False,
                                   literal_binding_time_test=False))
    return dict(study_id=plan["study_id"], hypotheses=hypotheses, contrasts=contrasts,
                chains=chains, rounds=rounds, probes=probes, task_status=task_status,
                model_status=model_status,
                limitations=["Pressure is imagined framing; no binding deadline or token contrast is enforced.",
                             "All four roles and future demand are jointly visible to the trajectory generator.",
                             "Pipeline sensitivity and relative probe weight are proxies, not original structural beta.",
                             "All twenty chains and both conditions share one generation per model; no independent-chain p-values or confidence intervals; human observations=0.",
                             "Seeing both classroom situations in one response permits cross-condition contamination and comparisons by the generator.",
                             "Checkpoint agreement supports three inventory calculations, not every internal decision or state.",
                             "The 24-week primary cost omits liabilities after the horizon; terminal state is reported separately."])
