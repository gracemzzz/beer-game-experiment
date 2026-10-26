"""Offline three-condition website batch. No model calls and no order policy.

One batch is ONE dependent generation cluster, even though it contains 150
chains. Conditions share the chat and may contaminate one another. This is a
new exploratory design, not a replacement for the frozen separated v3 study.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import uuid

try:  # Repository use.
    from . import manual_weekly_v3 as core
except ImportError:  # The two-file upload package.
    import beergame_controller as core

SCHEMA = "manual-three-condition-batch-v5"
SLOTS = ("gpt_astra", "gpt_sol", "gpt_luna", "claude_sonnet")
CHAINS = 50
WEEKLY_PAGE = 25
PROBE_PAGE = 100
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


def sources():
    return dict(controller=core.source_sha256(),
                coordinator=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


def study_id():
    return "manual_batch_v5_" + core.digest(dict(schema=SCHEMA, sources=sources(), chains=CHAINS))[:16]


class Batch:
    def __init__(self, model_slot, batch_id=None):
        if model_slot not in SLOTS:
            raise ValueError("Unknown requested model slot")
        batch_id = batch_id or uuid.uuid4().hex
        if not isinstance(batch_id, str) or len(batch_id) != 32 or any(c not in "0123456789abcdef" for c in batch_id):
            raise ValueError("Use the automatically generated batch UUID")
        self.batch_id, self.model_slot = batch_id, model_slot
        self.seed = int(core.digest([batch_id, "demand"])[:12], 16)
        self.arm_order = list("ABC")
        random.Random(int(core.digest([batch_id, "arm_order"])[:12], 16)).shuffle(self.arm_order)
        self.games = {arm: core.WebsiteGame(
            case_id=f"MB5_{batch_id}_{arm}", arm=arm, replicate=1, chains=CHAINS,
            seed=self.seed, study_id=study_id(), provider="website-unverified",
            model="UNRECORDED", reasoning_setting="UNRECORDED") for arm in "ABC"}
        self.display_hash = None
        self.trace = []
        self.page_events = []
        self.page_offset = 0
        self.pending_choices = {}
        self.visible_ids = []

    def active_arm(self):
        return next((a for a in self.arm_order if self.games[a].phase != "complete"), None)

    def display(self):
        arm = self.active_arm()
        if arm is None:
            return dict(phase="complete", batch_id=self.batch_id, completed_conditions=3)
        game = self.games[arm]
        raw = game.display()
        is_probe = raw["phase"].startswith("probe")
        entries = raw["hypothetical_independent_decisions"] if is_probe else raw["chains"]
        page_size = PROBE_PAGE if is_probe else WEEKLY_PAGE
        page = entries[self.page_offset:self.page_offset + page_size]
        self.visible_ids = [row["probe_id"] if is_probe else row["chain_id"] for row in page]
        decision = dict(phase=raw["phase"], role_order=raw["role_order"], profiles=raw["profiles"],
                        page_index=self.page_offset // page_size + 1,
                        pages=(len(entries) + page_size - 1) // page_size,
                        requested_ids=self.visible_ids)
        if is_probe:
            columns = ["probe_id", "chain_id", "role", "profile_id", "inventory", "backlog",
                       "supply_line", "demand", "received", "shipped"]
            decision.update(probe_columns=columns + ["shared_inventory_r_w_d_f"],
                            probes=[[row[k] for k in columns] + [[row["shared_inventory"][r] for r in core.ROLES]] for row in page])
        else:
            decision.update(week=raw["week"], state_columns=raw["state_columns"],
                chain_columns=["chain_id", "profile_ids", "state_r_w_d_f", "shared_inventory_r_w_d_f", "recent_history"],
                history_columns=["week", "final_orders_r_w_d_f", "customer_demand"],
                chains=[[row["chain_id"], row["profile_ids"], row["state"],
                         [row["shared_inventory"][r] for r in core.ROLES],
                         [[h["week"], h["final_orders"], h["customer_demand"]] for h in row["history"]]] for row in page])
        if "initial_proposals" in raw:
            decision["initial_proposals"] = {ident: raw["initial_proposals"][ident] for ident in self.visible_ids}
        view = dict(batch_id=self.batch_id, condition=arm,
                    classroom_reading=EDUCATION if arm == "C" else CONTROL,
                    opportunity="initial then separate reconsideration" if arm == "A" else "initial committed",
                    completed_conditions=sum(g.phase == "complete" for g in self.games.values()),
                    decision=decision)
        self.display_hash = core.digest(view)
        return view

    def submit(self, choices):
        arm = self.active_arm()
        if arm is None or self.display_hash is None:
            raise ValueError("Receive the public display before submitting a decision")
        game = self.games[arm]
        if not isinstance(choices, dict) or set(choices) != set(self.visible_ids):
            raise ValueError("Supply exactly this page's requested IDs; other pages must wait for their display")
        is_probe = game.phase.startswith("probe")
        for value in choices.values():
            values = [value] if is_probe else value
            if not isinstance(values, list) or (not is_probe and len(values) != 4):
                raise ValueError("Each chain requires four integer orders")
            for item in values:
                if type(item) is not int or not 0 <= item <= core.ORDER_GUARD:
                    raise ValueError("Invalid order")
        clean = json.loads(json.dumps(choices))
        page_event = dict(condition=arm, phase=game.phase, week=game.week, offset=self.page_offset,
                          display_sha256=self.display_hash, choices=clean)
        self.pending_choices.update(clean)
        self.page_events.append(page_event)
        page_size = PROBE_PAGE if is_probe else WEEKLY_PAGE
        total = CHAINS * 16 if is_probe else CHAINS
        self.page_offset += len(clean)
        if self.page_offset < total:
            self.display_hash = None
            return self.display()
        all_choices = self.pending_choices
        event = dict(condition=arm, phase=game.phase, week=game.week,
                     display_sha256=self.display_hash, choices_sha256=core.digest(all_choices))
        method = {"initial": game.submit_initial, "revision": game.submit_revision,
                  "probe_initial": game.submit_probe_initial, "probe_revision": game.submit_probe_revision}[game.phase]
        method(all_choices)
        self.trace.append(event)
        self.display_hash = None
        self.page_offset = 0
        self.pending_choices = {}
        return self.display()

    def export(self, require_complete=True):
        complete = self.active_arm() is None
        if require_complete and not complete:
            raise ValueError("Incomplete batch; preserve partial data with require_complete=False")
        return dict(schema_version=SCHEMA, study_id=study_id(), source_hashes=sources(),
                    batch_id=self.batch_id, requested_model_slot=self.model_slot,
                    actual_model_label="UNRECORDED", actual_reasoning_setting="UNRECORDED",
                    seed=self.seed, arm_order=self.arm_order[:], chains_per_arm=CHAINS,
                    weeks=24, independent_generation_clusters=1, complete=complete,
                    trace=json.loads(json.dumps(self.trace)),
                    page_events=json.loads(json.dumps(self.page_events)),
                    pending_page_choices=json.loads(json.dumps(self.pending_choices)),
                    page_offset=self.page_offset,
                    page_sizes=dict(weekly=WEEKLY_PAGE, probes=PROBE_PAGE),
                    games={a: g.export(require_complete=False) for a, g in self.games.items()},
                    limitations=["All three conditions share one model context; education carryover is possible.",
                                 "One versus two decision opportunities; no enforced clock or token limit.",
                                 "Hypothetical students; no human validation; labels require user confirmation."])

    def save(self, directory="."):
        path = Path(directory) / f"{self.model_slot}_{self.batch_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.export(require_complete=False), separators=(",", ":"), allow_nan=False), encoding="utf-8")
        return str(path)


def audit(payload):
    """Replay physical games AND condition/display/choice sequence. No provenance inference."""
    if payload.get("schema_version") != SCHEMA or payload.get("study_id") != study_id() or payload.get("source_hashes") != sources():
        raise ValueError("Different or changed batch protocol/source")
    batch = Batch(payload["requested_model_slot"], payload["batch_id"])
    for key, expected in (("seed", batch.seed), ("arm_order", batch.arm_order),
                          ("chains_per_arm", CHAINS), ("weeks", 24), ("independent_generation_clusters", 1)):
        if payload.get(key) != expected:
            raise ValueError("Invalid batch field: " + key)
    if set(payload["games"]) != set("ABC"):
        raise ValueError("All three condition records must be preserved, including partial ones")
    rows = []
    for arm in "ABC":
        outcome = core.audit_export(payload["games"][arm], expected_case=dict(
            case_id=f"MB5_{batch.batch_id}_{arm}", arm=arm, replicate=1, chains=CHAINS,
            seed=batch.seed, study_id=study_id()))
        outcome.update(model=batch.model_slot, block_id=batch.batch_id,
                       condition_position=batch.arm_order.index(arm) + 1)
        rows.append(outcome)
    batch.display()
    for event in payload["page_events"]:
        batch.submit(event["choices"])
        if batch.page_events[-1] != event:
            raise ValueError("Display/submission sequence mismatch")
    replay = batch.export(require_complete=False)
    for key in ("trace", "page_sizes", "page_offset", "pending_page_choices"):
        if payload.get(key) != replay[key]:
            raise ValueError("Page/trace replay differs: " + key)
    if type(payload.get("complete")) is not bool or payload["complete"] != replay["complete"]:
        raise ValueError("Incorrect batch completion")
    for arm in "ABC":
        for key in ("initial_orders", "final_orders", "pending_initial_orders", "probe_initial", "probe_final", "complete"):
            if replay["games"][arm][key] != payload["games"][arm][key]:
                raise ValueError("Trace does not cover every recorded decision")
    return rows
