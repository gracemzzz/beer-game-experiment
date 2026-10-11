"""Single-call, fixed-effort Beer Game protocol; importing performs no API work.

This protocol is separate from the historical memo/final-answer experiment. A
token allowance covers *all* generated tokens, including hidden reasoning. An
invalid answer is never resubmitted. Its mechanical continuation order is
flagged, and its trajectory is unsuitable for confirmatory outcome claims.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


MODEL = "gpt-5.4-mini-2026-03-17"
PROTOCOL = "hypothetical-student-fixed-high-single-call-v1"
RATES = {"input": 0.75, "cached": 0.075, "output": 4.50}  # USD / 1M tokens
ORDER_SCHEMA = {
    "type": "object",
    "properties": {"order": {"type": "integer", "minimum": 0}},
    "required": ["order"],
    "additionalProperties": False,
}
RULES_SCHEMA = {
    "type": "object",
    "properties": {
        "backlog_includes_current_unfilled_demand": {"type": "boolean"},
        "factory_order_week_7_arrival_week": {"type": "integer"},
        "three_week_backlog_cost": {"type": "number"},
    },
    "required": ["backlog_includes_current_unfilled_demand", "factory_order_week_7_arrival_week", "three_week_backlog_cost"],
    "additionalProperties": False,
}
RULE_ANSWERS = {
    "backlog_includes_current_unfilled_demand": True,
    "factory_order_week_7_arrival_week": 10,
    "three_week_backlog_cost": 15,
}

COMMON = """Act as a hypothetical second-year undergraduate business student at
the University at Buffalo, an American university, playing a classroom Beer Game.
You have received the rules below and have no specialized inventory-management
training beyond ordinary undergraduate business study. Make the choice you think
this hypothetical student would make while trying to do well in the game. This is
a fictional role, not a claim to be an actual student. Do not invent personal
traits, demographic stereotypes, or deliberate mistakes. No particular cognitive
bias or pattern of orders is requested.

The four positions are retailer, wholesaler, distributor, and factory. Your goal
is to minimize the team's total inventory holding and backlog costs over the
game. Each case in inventory costs $0.50 per week; each case still backlogged costs
$1.00 per week. There is no sales revenue, order fee, bulk discount, or reward for
ordering a large amount. All quantities are cases and each round is one week.
Your only decision is how many cases to order from your supplier, or to put into
production if you are the factory. Submit one nonnegative integer. Zero is a
legitimate choice. There is no displayed maximum or suggested order amount.

The current state is AFTER this week's deliveries and automatic shipments and
BEFORE your new order. Inventory is the available stock remaining after those
shipments. Backlog is all unfilled demand remaining after those shipments: it
already includes any unfilled part of this week's demand. Do not add the current
demand to backlog again. Backlog persists until supplied; it is not lost sales.
Supply_line is all previously ordered cases you have not yet received, including
goods in transit and orders waiting at a supplier. It is not available stock.
Orders cannot be canceled. A new order cannot change this week's completed
shipments or cost. Non-factory orders reach the supplier next week; physical
shipment then takes two weeks, so the earliest receipt is week t+3 for an order
placed in week t. Shortages can delay receipt further. Factory production ordered
in week t arrives in week t+3, not week t+2. The factory can start new production
even when its inventory and supply line are zero. There is no outside supplier,
raw-material constraint, or production-capacity constraint in this game.

The shared_inventory field reveals each position's current available stock. You
also see your own incoming demand, receipts, shipments, inventory, backlog,
supply line, and prior rounds. Other positions' orders and backlogs are hidden.
There is no communication or outside tool use. Initial stock is 12 per position
and the initial flow is 4 per week. The first four familiarization weeks submit
orders of 4. Future customer demand and the last decision week are not revealed.
After decisions stop, 12 automatic weeks continue with customer demand held at
its last value and each position ordering its incoming demand. Those weeks count
toward team costs. This automatic continuation is a scoring rule, not advice for
your decisions. Return only the structured order for the current round."""

TASK = "How many cases do you order this week? Return the integer in the order field."


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def save(path: str | Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


@dataclass(frozen=True)
class ReasoningConfig:
    mode: str = "offline"
    stage: str = "calibration"
    replicate_id: str = "student-high-pilot-01"
    model: str = MODEL
    effort: str = "high"
    weeks: int = 40
    warmup_weeks: int = 4
    continuation_weeks: int = 12
    groups_per_condition: int = 3
    candidate_caps: tuple[int, ...] = (512, 1024, 2048, 4096, 8192)
    reference_tokens: int = 16384
    short_tokens: int = 2048
    adequate_tokens: int = 8192
    onboarding_tokens: int = 8192
    budget_usd: float = 10.0
    concurrency: int = 4
    request_interval_s: float = 1.0
    timeout_s: float = 180.0
    seed: int = 20261011
    emergency_order_limit: int = 100000

    def validate(self) -> ReasoningConfig:
        if self.mode not in ("offline", "api") or self.stage not in ("calibration", "game"):
            raise ValueError("Use mode offline/api and stage calibration/game.")
        if self.model != MODEL or self.effort != "high":
            raise ValueError("This protocol pins the model and high reasoning effort; changing either needs a new protocol.")
        if type(self.weeks) is not int or self.weeks < 20 or self.warmup_weeks != 4 or self.continuation_weeks != 12:
            raise ValueError("Use at least 20 weeks, four familiarization weeks, and 12 continuation weeks.")
        if type(self.groups_per_condition) is not int or self.groups_per_condition < 1:
            raise ValueError("groups_per_condition must be a positive integer.")
        if not self.candidate_caps or any(type(x) is not int or x < 16 for x in self.candidate_caps):
            raise ValueError("Candidate token allowances must be integers of at least 16.")
        if tuple(sorted(set(self.candidate_caps))) != tuple(self.candidate_caps):
            raise ValueError("Candidate allowances must be unique and increasing.")
        if type(self.reference_tokens) is not int or self.reference_tokens <= max(self.candidate_caps):
            raise ValueError("The reference allowance must exceed all candidate allowances.")
        if not (16 <= self.short_tokens < self.adequate_tokens <= self.reference_tokens):
            raise ValueError("Use increasing short/adequate allowances within the reference allowance.")
        if self.onboarding_tokens != 8192 or self.emergency_order_limit != 100000:
            raise ValueError("Onboarding and the unadvertised numerical safety limit are fixed.")
        if not math.isfinite(self.budget_usd) or self.budget_usd <= 0 or not 1 <= self.concurrency <= 8:
            raise ValueError("Use a positive finite budget and concurrency between one and eight.")
        if not math.isfinite(self.timeout_s) or self.timeout_s <= 0 or not math.isfinite(self.request_interval_s) or self.request_interval_s < 0:
            raise ValueError("Timeout and pacing must be finite, with timeout positive and pacing nonnegative.")
        return self

    def scientific(self) -> dict[str, Any]:
        # timeout_s stays scientific: although it is infrastructure rather than
        # the treatment, a changed timeout could change failures and selection.
        operational = {"budget_usd", "concurrency", "request_interval_s"}
        return {k: v for k, v in asdict(self).items() if k not in operational}

    def fingerprint(self) -> str:
        return digest({"protocol": PROTOCOL, "config": self.scientific(), "prompt": COMMON, "task": TASK,
                       "order_schema": ORDER_SCHEMA, "rules_schema": RULES_SCHEMA, "rates": RATES})


def make_messages(state: Mapping[str, Any], history: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """The same question and framing at every allowance; do not disclose treatment."""
    return [{"role": "system", "content": COMMON}, {"role": "user", "content": json.dumps(
        {"task": TASK, "past_rounds": list(history), "current_state": dict(state)}, separators=(",", ":"), allow_nan=False)}]


def rules_messages(role: str) -> list[dict[str, str]]:
    task = {"task": "Answer these factual rules questions before playing.", "role": role, "questions": {
        "backlog_includes_current_unfilled_demand": "Does the displayed post-shipment backlog already include this week's unfilled demand?",
        "factory_order_week_7_arrival_week": "In which week does factory production ordered in week 7 arrive?",
        "three_week_backlog_cost": "Five cases remain backlogged at the end of each of three weeks. What is their total backlog cost?"}}
    return [{"role": "system", "content": COMMON}, {"role": "user", "content": json.dumps(task, separators=(",", ":"))}]


def rules_result(record: Mapping[str, Any]) -> dict[str, Any]:
    try:
        answer = json.loads(record.get("text", ""))
    except (TypeError, ValueError):
        answer = None
    passed = (record.get("status") == "ok" and record.get("response_status") == "completed"
              and not record.get("refused") and isinstance(answer, dict) and answer == RULE_ANSWERS
              and type(answer.get("backlog_includes_current_unfilled_demand")) is bool
              and type(answer.get("factory_order_week_7_arrival_week")) is int
              and type(answer.get("three_week_backlog_cost")) in (int, float))
    return {"passed": passed, "answer": answer, "synthetic": bool(record.get("synthetic"))}


def price(usage: Mapping[str, int]) -> float:
    input_tokens = usage.get("input_tokens", 0)
    cached = usage.get("cached_input_tokens", 0)
    output = usage.get("output_tokens", 0)
    if any(type(x) is not int or x < 0 for x in (input_tokens, cached, output)) or cached > input_tokens:
        raise ValueError("Invalid token usage.")
    return ((input_tokens - cached) * RATES["input"] + cached * RATES["cached"] + output * RATES["output"]) / 1e6


class StudyStopped(RuntimeError):
    """Spending guard, unresolved interrupted call, or fatal API configuration."""


@dataclass(frozen=True)
class Decision:
    order: int
    valid: bool
    fallback: bool
    reason: str
    submitted_order: int | None = None
    confirmatory_eligible: bool = False


def decide(record: Mapping[str, Any], last_valid_order: int = 4, emergency_order_limit: int = 100000) -> Decision:
    """Carry forward the last valid submitted order after any invalid response.

    A valid zero remains zero. There is no clipping into an order range; the
    emergency limit prevents absurd-scale arithmetic and is never in the prompt.
    """
    if type(last_valid_order) is not int or not 0 <= last_valid_order <= emergency_order_limit:
        raise ValueError("last_valid_order must be a previously valid nonnegative order.")
    reason = None
    if record.get("status") != "ok":
        reason = record.get("status", "missing_record_status")
    elif record.get("refused"):
        reason = "refused"
    elif record.get("response_status") != "completed":
        reason = "truncated" if record.get("incomplete_reason") == "max_output_tokens" else "incomplete"
    try:
        answer = json.loads(record.get("text", ""))
    except (TypeError, ValueError):
        answer = None
    order = answer.get("order") if isinstance(answer, dict) else None
    if reason is None and (not isinstance(answer, dict) or set(answer) != {"order"} or type(order) is not int or order < 0):
        reason = "malformed_order"
    if reason is None and order > emergency_order_limit:
        reason = "emergency_scale"
    if reason is not None:
        return Decision(last_valid_order, False, True, str(reason), order if type(order) is int else None, False)
    return Decision(order, True, False, "valid", order, not bool(record.get("synthetic")))


def synthetic_order(state: Mapping[str, Any]) -> int:
    """Simple demand-following software benchmark; not a human response model."""
    quantity = state["demand"]
    if type(quantity) is not int or quantity < 0:
        raise ValueError("Synthetic benchmark needs integer nonnegative demand.")
    return quantity


def create_live_client(config: ReasoningConfig) -> Any:
    """Only explicit caller action imports OpenAI or constructs a live client."""
    config.validate()
    from openai import AsyncOpenAI
    return AsyncOpenAI(max_retries=0, timeout=config.timeout_s)


class Gateway:
    """One durable request per identity and allowance, with local reservations.

    The reservation survives unknown transport outcomes and interrupted calls.
    HTTP rejections refund only when no generation is known to have occurred.
    Error records intentionally omit exception text, headers, and bodies.
    """
    def __init__(self, directory: str | Path, config: ReasoningConfig, client: Any = None, callback: Any = None):
        self.config = config.validate()
        self.directory = Path(directory)
        self.cache = self.directory / "requests"
        self.cache.mkdir(parents=True, exist_ok=True)
        self.client = client
        if client is not None and callable(getattr(client, "with_options", None)):
            self.client = client.with_options(max_retries=0, timeout=config.timeout_s)
        self.callback = callback or (lambda: None)
        self.charged = sum(json.loads(p.read_text(encoding="utf-8")).get("charge_usd", 0.0) for p in self.cache.glob("*.json"))
        self.sem = asyncio.Semaphore(config.concurrency)
        self.lock = asyncio.Lock()
        self._key_locks: dict[str, asyncio.Lock] = {}
        self.next_start = 0.0
        self.cached = 0
        self.finished = 0
        self.active = 0
        self.fatal: StudyStopped | None = None

    async def _pace(self) -> None:
        while True:
            async with self.lock:
                delay = self.next_start - time.monotonic()
                if delay <= 0:
                    self.next_start = time.monotonic() + self.config.request_interval_s
                    return
            await asyncio.sleep(min(delay, 1.0))

    def reservation(self, messages: Any, limit: int, schema: Any) -> float:
        # UTF-8 bytes overestimate typical text tokens; overhead covers request
        # wrapping. Cached-input discounts are never assumed in reservations.
        input_allowance = len(json.dumps({"input": messages, "schema": schema}, ensure_ascii=False).encode("utf-8")) + 2048
        return (input_allowance * RATES["input"] + limit * RATES["output"]) / 1e6

    async def request(self, identity: Any, messages: Any, limit: int, schema: Any = ORDER_SCHEMA, synthetic: str | None = None) -> dict[str, Any]:
        if type(limit) is not int or limit < 16 or limit > self.config.reference_tokens:
            raise ValueError("Request allowance must be an integer within the protocol reference allowance.")
        specification = {"protocol": PROTOCOL, "identity": identity, "messages": messages, "limit": limit,
                         "schema": schema, "requested_model": self.config.model, "reasoning": {"effort": self.config.effort},
                         "mode": self.config.mode, "config_fingerprint": self.config.fingerprint()}
        key = digest(specification)
        async with self._key_locks.setdefault(key, asyncio.Lock()):
            path = self.cache / (key + ".json")
            if path.exists():
                record = json.loads(path.read_text(encoding="utf-8"))
                if record["status"] == "pending":
                    raise StudyStopped("Saved pending request has unknown usage/outcome; inspect it before resuming. No request was resubmitted.")
                if record.get("fatal_error"):
                    raise StudyStopped("Saved fatal API rejection; inspect configuration. No request was resubmitted.")
                self.cached += 1
                self.finished += 1
                self.callback()
                return record
            if self.fatal:
                raise self.fatal
            record = dict(specification, request_key=key, created_utc=datetime.now(timezone.utc).isoformat(),
                          requested_effort=self.config.effort, max_retries=0, timeout_s=self.config.timeout_s)
            if self.config.mode == "offline":
                record.update(status="ok", response_status="completed", text=synthetic or "", synthetic=True,
                              returned_model=None, response=None, refused=False, incomplete_reason=None,
                              usage={"input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0,
                                     "reasoning_tokens": 0, "nonreasoning_output_tokens_proxy": 0},
                              usage_observed=False, charge_usd=0.0, elapsed_s=0.0,
                              note="SYNTHETIC software benchmark; no GPT call, hidden reasoning, or human validation.")
                save(path, record)
                self.finished += 1
                self.callback()
                return record
            async with self.sem:
                if self.client is None:
                    raise StudyStopped("An explicit live API client is required in API mode.")
                await self._pace()
                reserve = self.reservation(messages, limit, schema)
                async with self.lock:
                    if self.fatal:
                        raise self.fatal
                    if self.charged + reserve > self.config.budget_usd:
                        self.fatal = StudyStopped(f"Local cost guard: ${self.charged:.4f} charged/reserved plus ${reserve:.4f} would exceed budget ${self.config.budget_usd:.4f}.")
                        raise self.fatal
                    self.charged += reserve
                record.update(status="pending", charge_usd=reserve, reserved_usd=reserve, synthetic=False)
                save(path, record)
                start = time.monotonic()
                self.active += 1
                self.callback()
                try:
                    kwargs = {"model": self.config.model, "input": messages, "reasoning": {"effort": "high"},
                              "max_output_tokens": limit, "store": False}
                    if schema is not None:
                        kwargs["text"] = {"format": {"type": "json_schema", "name": "answer", "strict": True, "schema": schema}}
                    response = await self.client.responses.create(**kwargs)
                    raw = response.model_dump(mode="json") if hasattr(response, "model_dump") else dict(response)
                    raw_usage = raw.get("usage")
                    usage = raw_usage if isinstance(raw_usage, dict) else {}
                    output_details = usage.get("output_tokens_details") or {}
                    u = {"input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0),
                         "cached_input_tokens": (usage.get("input_tokens_details") or {}).get("cached_tokens", 0),
                         "reasoning_tokens": output_details.get("reasoning_tokens", 0)}
                    complete_usage = (all(k in usage for k in ("input_tokens", "output_tokens"))
                                      and "reasoning_tokens" in output_details)
                    valid_usage = all(type(v) is int and v >= 0 for v in u.values()) and u["reasoning_tokens"] <= u["output_tokens"] and u["cached_input_tokens"] <= u["input_tokens"]
                    u["nonreasoning_output_tokens_proxy"] = u["output_tokens"] - u["reasoning_tokens"] if valid_usage else None
                    text = "".join(c.get("text", "") for o in raw.get("output", []) if o.get("type") == "message"
                                   for c in o.get("content", []) if c.get("type") == "output_text")
                    refused = any(c.get("type") == "refusal" for o in raw.get("output", []) for c in o.get("content", []))
                    protocol_errors = []
                    if raw.get("model") != self.config.model:
                        protocol_errors.append("returned_model_mismatch")
                    if not complete_usage or not valid_usage:
                        protocol_errors.append("missing_or_invalid_usage")
                    if valid_usage and u["output_tokens"] > limit:
                        protocol_errors.append("output_exceeds_allowance")
                    record.update(status="protocol_error" if protocol_errors else "ok", response_status=raw.get("status"),
                                  returned_model=raw.get("model"), response=raw, text=text, refused=refused,
                                  incomplete_reason=(raw.get("incomplete_details") or {}).get("reason"), usage=u,
                                  usage_observed=complete_usage and valid_usage, protocol_errors=protocol_errors,
                                  elapsed_s=time.monotonic() - start)
                    if valid_usage and all(k in usage for k in ("input_tokens", "output_tokens")):
                        actual = price(u)
                        async with self.lock:
                            self.charged += actual - reserve
                        record["charge_usd"] = actual
                    save(path, record)
                    self.finished += 1
                    return record
                except asyncio.CancelledError:
                    # Persisted pending reservation remains: do not silently resend.
                    raise
                except Exception as exc:
                    http = getattr(exc, "status_code", None)
                    # Record only safe categories, never exception text or bodies.
                    category = ("authentication" if http in (401, 403) else "configuration" if http in (400, 404, 422)
                                else "rate_or_quota" if http == 429 else "server" if isinstance(http, int) and http >= 500
                                else "timeout" if "Timeout" in type(exc).__name__ else "connection" if "Connection" in type(exc).__name__
                                else "unexpected_api_error")
                    known_rejection = http in (400, 401, 403, 404, 422, 429)
                    if known_rejection:
                        async with self.lock:
                            self.charged -= reserve
                        record["charge_usd"] = 0.0
                    fatal = category in ("authentication", "configuration", "rate_or_quota")
                    record.update(status="api_error", error_category=category, http_status=http if isinstance(http, int) else None,
                                  fatal_error=fatal, usage_observed=False, response_status=None, text="", response=None,
                                  returned_model=None, usage=None, elapsed_s=time.monotonic() - start)
                    save(path, record)
                    self.finished += 1
                    if fatal:
                        self.fatal = StudyStopped(f"API rejected the call ({category}, HTTP {http}); safe provenance was saved. No retries were made.")
                        raise self.fatal from None
                    return record
                finally:
                    self.active -= 1
                    self.callback()


def screen_caps(records: Sequence[Mapping[str, Any]], candidate_caps: Sequence[int] = (512, 1024, 2048, 4096, 8192),
                reference_tokens: int = 16384, completion_threshold: float = 0.95,
                usage_contrast: float = 0.25, expected_n: int = 24) -> dict[str, Any]:
    """Prespecified feasibility screen, never selected by orders or game costs.

    Completion is a valid original answer, not a carry-forward continuation.
    A cap passes only with >=95% completion and measured positive reasoning in
    every valid call. The complete matched batch must be present. Separation
    uses all measured calls, including truncations, to avoid survivor selection.
    This small pilot is not proof of a population completion rate.
    """
    if not 0 < completion_threshold <= 1 or not 0 < usage_contrast < 1:
        raise ValueError("Screen thresholds must be proportions in their valid ranges.")
    if type(expected_n) is not int or expected_n < 1:
        raise ValueError("expected_n must be a positive integer specified before calibration.")
    caps = tuple(sorted(set(candidate_caps)))
    rows = []
    item_sets = {}
    for cap in (*caps, reference_tokens):
        items = [r for r in records if r.get("limit") == cap]
        genuine = [r for r in items if not r.get("synthetic")]
        valid = [r for r in genuine if decide(r).valid]
        measured = [r for r in genuine if r.get("usage_observed") and isinstance(r.get("usage"), Mapping)
                    and type(r["usage"].get("reasoning_tokens")) is int and r["usage"]["reasoning_tokens"] >= 0
                    and type(r["usage"].get("output_tokens")) is int
                    and 0 <= r["usage"]["reasoning_tokens"] <= r["usage"]["output_tokens"] <= cap]
        usable = [r for r in valid if r in measured and r["usage"]["reasoning_tokens"] > 0]
        # Root calibration identities use {stage, item, cap}. Only the item
        # identifies the matched scenario; the allowance must not enter its key.
        keys = [digest(r["identity"]["item"]) for r in items
                if isinstance(r.get("identity"), Mapping) and "item" in r["identity"]]
        item_sets[cap] = set(keys)
        complete_items = len(items) == expected_n and len(keys) == expected_n and len(set(keys)) == expected_n
        rate = len(valid) / len(items) if items else 0.0
        totals = [r["usage"]["output_tokens"] for r in measured]
        med = statistics.median(totals) if totals else None
        near_cap = sum(t >= 0.9 * cap for t in totals) / len(totals) if totals else None
        rows.append({"limit": cap, "n": len(items), "genuine_api_n": len(genuine), "completed_valid_n": len(valid),
                     "completion_denominator": len(items), "completion_rate": rate,
                     "positive_reasoning_n": len(usable), "measured_usage_n": len(measured),
                     "median_output_tokens": med, "near_cap_fraction": near_cap,
                     "truncated_fraction": sum(r.get("incomplete_reason") == "max_output_tokens" for r in items) / len(items) if items else None,
                     "complete_unique_items": complete_items,
                     "viable": bool(complete_items and len(genuine) == len(items) and len(measured) == len(items)
                     and rate >= completion_threshold and len(usable) == len(valid))})
    by_cap = {r["limit"]: r for r in rows}
    reference_items = item_sets[reference_tokens]
    batch_complete = all(r["complete_unique_items"] and item_sets[r["limit"]] == reference_items for r in rows)
    for row in rows:
        row["matching_reference_items"] = item_sets[row["limit"]] == reference_items
        row["viable"] = row["viable"] and batch_complete
    # A reference close to its own cap cannot establish an adequately loose
    # allowance. Require <=5% of completed reference calls within 10% of it.
    reference_ok = bool(by_cap[reference_tokens]["viable"] and
                        by_cap[reference_tokens]["near_cap_fraction"] <= 0.05)
    viable = [r for r in rows if r["limit"] in caps and r["viable"]]
    pair = None
    # Select the smallest viable low allowance, then the smallest viable high
    # allowance that creates prespecified measured usage contrast. No outcome
    # differences, bias scores, or boundary-order frequencies enter this choice.
    if reference_ok:
        for low in viable:
            for high in viable:
                if high["limit"] > low["limit"] and high["median_output_tokens"] > 0:
                    contrast = 1 - low["median_output_tokens"] / high["median_output_tokens"]
                    if contrast >= usage_contrast:
                        pair = (low, high, contrast)
                        break
            if pair:
                break
    return {"protocol": PROTOCOL, "screen_rows": rows, "reference_screen_passed": reference_ok,
            "expected_n_per_cap": expected_n, "complete_matched_batch": batch_complete,
            "manipulation_screen_passed": pair is not None,
            "short_tokens": pair[0]["limit"] if pair else None,
            "adequate_tokens": pair[1]["limit"] if pair else None,
            "median_total_output_contrast": pair[2] if pair else None,
            "completion_threshold": completion_threshold, "required_usage_contrast": usage_contrast,
            "reference_near_cap_threshold": 0.05,
            "nonbinding_cap_risk": bool(pair and pair[0]["near_cap_fraction"] == 0),
            "adequate_cap_binding_risk": bool(pair and pair[1]["near_cap_fraction"] > 0.05),
            "reference_cap_binding_risk": bool(by_cap[reference_tokens]["near_cap_fraction"] is not None
                                                and by_cap[reference_tokens]["near_cap_fraction"] > 0.05),
            "note": "Feasibility screen only. Caps are not guaranteed valid. Recheck in full games; no human-time equivalence is established. Any fallback makes that game ineligible for confirmatory outcome claims. Synthetic calls cannot validate the manipulation."}
