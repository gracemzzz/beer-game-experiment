"""Versioned high-effort transport. Imports and preparation never call an API.

The experiment-12 cumulative ledger/lock are mandatory. This implementation
does not change its historical rates or charges and never obtains credentials
from notebooks, files, tools or saved responses.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import random
import re
import time

import httpx

from . import weekly_pivot_v2 as study
from .batched_pressure_api import BudgetLedger, BudgetStop, runner_lock, _clean, now, save as _save_ledger

RATES = {
    "gpt-6-luna": dict(provider="openai", input=.1, cached=.01, output=.5),
    "gpt-6.1-sol": dict(provider="openai", input=2., cached=.1, output=10.),
    "gpt-6-astra": dict(provider="openai", input=10., cached=1., output=50.),
    "claude-sonnet-5-5": dict(provider="anthropic", input=2., cached=.1, output=10.),
}
PRICE_DATE = "2026-10-25"
SOURCE_URLS = {m: ("https://developers.openai.com/api/docs/models/" + m
    if r["provider"] == "openai" else "https://platform.claude.com/docs/en/models/sonnet-5-5/overview")
    for m, r in RATES.items()}
INPUT_BYTE_LIMIT = 30000
PREFLIGHT_LOCAL_CAP = 1.5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def freeze(path, value):
    path = Path(path)
    data = value if isinstance(value, bytes) else (
        value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refuse to overwrite frozen v2 evidence: " + path.name)
    else:
        with path.open("xb") as stream:
            stream.write(data)


def budget_status(budget_root):
    path = Path(budget_root) / "data/api_budget.json"
    if not path.is_file():
        raise BudgetStop("The existing shared ledger is required; a new ledger is prohibited.")
    ledger = read(path)
    if ledger.get("cap_usd") != 5 or not isinstance(ledger.get("attempts"), dict):
        raise BudgetStop("Continue the SAME authorized $5 cap and original attempts.")
    charges = [row.get("charge_usd") for row in ledger["attempts"].values()]
    if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in charges):
        raise BudgetStop("Invalid shared spending records.")
    spent = sum(charges)
    return dict(cap_usd=5., charged_or_reserved_usd=spent, remaining_usd=5. - spent,
                attempts=len(charges), ledger_sha256=sha(path))


def prepare(experiment, budget_root, *, blocks=40, chains_per_cluster=1):
    experiment, budget_root = Path(experiment).resolve(), Path(budget_root).resolve()
    status = budget_status(budget_root)
    expected = experiment.parent / "12_pressure_framing_api_20261020"
    if budget_root != expected.resolve():
        raise BudgetStop("Use experiment 12 as the sole shared ledger and lock owner.")
    plan = study.make_plan(blocks=blocks, chains_per_cluster=chains_per_cluster)
    dependencies = {name: Path(__file__).with_name(name) for name in
        ("weekly_pivot_v2.py", "pivot_transport_v2.py", "pivot_inference_v2.py", "game.py", "batched_pressure.py", "batched_pressure_api.py")}
    dependencies["PIVOT_V2_20261025.md"] = experiment / "hypotheses/PIVOT_V2_20261025.md"
    envelope = dict(plan=plan, source_hashes={n: sha(p) for n, p in dependencies.items()},
        rates=RATES, price_date=PRICE_DATE, price_sources=SOURCE_URLS,
        budget_experiment="../12_pressure_framing_api_20261020", cumulative_cap_usd=5.,
        prior_attempts={k: study.digest(v) for k, v in read(budget_root / "data/api_budget.json")["attempts"].items()},
        input_byte_limit=INPUT_BYTE_LIMIT, preflight_local_cap_usd=PREFLIGHT_LOCAL_CAP,
        retry_policy="No automatic retry; preserve every failure and unknown-charge reservation.",
        settings={"effort": "high", "temperature_override": None, "thinking_claude": "adaptive"})
    fingerprint = study.digest(envelope)
    # Spending receipts are not a campaign selector. Rerunning after payment
    # must resume this same sample, not create fresh pilot slots.
    identity = {k: v for k, v in envelope.items() if k != "prior_attempts"}
    run = experiment / "data" / ("pivot_v2_" + study.digest(identity)[:16])
    if (run / "envelope.json").is_file():
        existing = read(run / "envelope.json")
        if {k: v for k, v in existing.items() if k != "prior_attempts"} != identity:
            raise ValueError("Existing v2 run identity differs")
        if study.digest(existing) != (run / "fingerprint.sha256").read_text(encoding="utf-8").strip():
            raise ValueError("Existing v2 run fingerprint changed")
        return run
    freeze(run / "plan.json", plan)
    freeze(run / "envelope.json", envelope)
    freeze(run / "fingerprint.sha256", fingerprint + "\n")
    for name, path in dependencies.items():
        freeze(run / "source_snapshot" / name, path.read_bytes())
    # This is a receipt of the ledger at preparation, not a replacement ledger.
    freeze(run / "source_snapshot/budget_at_preparation.json", (budget_root / "data/api_budget.json").read_bytes())
    return run


def _portable_schema(value):
    if isinstance(value, dict):
        return {k: _portable_schema(v) for k, v in value.items()
                if k not in ("minimum", "maximum", "minItems", "maxItems")}
    return [_portable_schema(v) for v in value] if isinstance(value, list) else value


def payload_for(model, prompt, schema, cap=8192):
    if model not in RATES or type(cap) is not int or not 1 <= cap <= 8192:
        raise ValueError("Use a frozen model and positive output cap no larger than 8192.")
    if RATES[model]["provider"] == "openai":
        return dict(model=model, input=[dict(role="user", content=prompt)],
            reasoning={"effort": "high"}, max_output_tokens=cap, service_tier="default", store=False,
            text={"format": {"type": "json_schema", "name": "beer_resource_v2", "strict": True, "schema": schema}})
    return dict(model=model, messages=[dict(role="user", content=prompt)], max_tokens=cap,
        thinking={"type": "adaptive"}, output_config={"effort": "high",
            "format": {"type": "json_schema", "schema": _portable_schema(schema)}})


def reserve_amount(model, payload):
    r = RATES[model]
    bound = len(json.dumps(payload, ensure_ascii=False).encode("utf-8")) + 4096
    if bound > INPUT_BYTE_LIMIT:
        raise BudgetStop("Request exceeds the prospective input byte bound; do not silently expand it.")
    factor = 1.25 if r["provider"] == "openai" else 2.
    return (bound * r["input"] * factor + payload.get("max_output_tokens", payload.get("max_tokens")) * r["output"]) / 1e6


def measured_usage(model, raw):
    """Conservative charges, hidden reasoning included in provider output usage."""
    try:
        u, r = raw["usage"], RATES[model]
        def count(v):
            if type(v) is not int or v < 0:
                raise ValueError("Invalid provider token count")
            return v
        inp, out = count(u["input_tokens"]), count(u["output_tokens"])
        if r["provider"] == "openai":
            cached = count((u.get("input_tokens_details") or {}).get("cached_tokens", 0))
            if cached > inp:
                raise ValueError("Cached input exceeds input")
            # Cache-write pricing is conservatively reserved when not itemized.
            writes = count((u.get("input_tokens_details") or {}).get("cache_write_tokens", inp - cached))
            if writes > inp - cached:
                raise ValueError("Invalid write count")
            charge = ((inp - cached) * r["input"] + cached * r["cached"] + writes * r["input"] * .25 + out * r["output"]) / 1e6
            reasoning = count((u.get("output_tokens_details") or {}).get("reasoning_tokens", 0))
            if reasoning > out:
                raise ValueError("Reasoning count exceeds inclusive output")
        else:
            cached = count(u.get("cache_read_input_tokens", 0))
            writes = count(u.get("cache_creation_input_tokens", 0))
            # Worst supported cache creation price, also safe when not itemized.
            charge = (inp * r["input"] + cached * r["cached"] + writes * r["input"] * 2 + out * r["output"]) / 1e6
            inp += cached + writes
            reasoning = None  # Anthropic does not necessarily itemize thinking.
        return dict(input_tokens=inp, output_tokens=out, cached_input_tokens=cached,
                    reasoning_tokens=reasoning, accounting="conservative usage estimate, not invoice"), charge
    except (KeyError, TypeError, ValueError, AttributeError):
        return None, None


def extract(model, raw):
    actual = raw.get("model", "")
    if actual != model and not (RATES[model]["provider"] == "openai" and
            re.fullmatch(re.escape(model) + r"-\d{4}-\d{2}-\d{2}", actual)):
        raise ValueError("Returned model differs from requested model")
    if RATES[model]["provider"] == "openai":
        if raw.get("status") != "completed":
            raise ValueError("Incomplete generation; no decision fabricated")
        content = [c for item in raw.get("output", []) if item.get("type") == "message" for c in item.get("content", [])]
        if any(c.get("type") == "refusal" for c in content):
            raise ValueError("Refused generation")
        text = "".join(c.get("text", "") for c in content if c.get("type") == "output_text")
    else:
        if raw.get("stop_reason") != "end_turn":
            raise ValueError("Incomplete generation; no decision fabricated")
        text = "".join(c.get("text", "") for c in raw.get("content", []) if c.get("type") == "text")
    return json.loads(text), actual


def preflight_task(plan, model):
    """One joint technical response/model; never an independent treatment sample."""
    tasks = {arm: study.build_task(plan, model, plan["blocks"][0]["block_id"], arm, 1) for arm in study.ARMS}
    prompt = ("TECHNICAL FORMAT PREFLIGHT. Return a JSON object with keys A, B, C. "
        "Each value is the response object requested by its case below. These jointly generated cases are development checks, not independent observations.\n\n"
        + "\n\n".join("CASE " + arm + "\n" + study.prompt_text(task) for arm, task in tasks.items()))
    schema = dict(type="object", properties={arm: study.response_schema(task) for arm, task in tasks.items()},
                  required=list(tasks), additionalProperties=False)
    return dict(task_id=model + "__technical_preflight", model=model, phase="technical_preflight",
                cases=tasks, prompt=prompt, schema=schema, max_output_tokens=8192)


def validate_literal(task, literal):
    if task["phase"] != "technical_preflight":
        return study.validate_response(task, literal)
    if not isinstance(literal, dict) or set(literal) != set(task["cases"]):
        return ["Missing preflight case"]
    return [e for arm, case in task["cases"].items() for e in study.validate_response(case, literal[arm])]


def planning(run):
    plan, env = read(Path(run) / "plan.json"), read(Path(run) / "envelope.json")
    budget_root = Path(run).parent.parent.parent / "12_pressure_framing_api_20261020"
    preflight = []
    for model in plan["models"]:
        task = preflight_task(plan, model)
        payload = payload_for(model, task["prompt"], task["schema"])
        preflight.append(dict(model=model, reserve_usd=reserve_amount(model, payload)))
    scenarios = []
    for blocks in (10, 20, 40):
        for cap in (2048, 4096, 8192):
            # 100 calls/model/block, inclusive of the extra A opportunity and probes.
            estimate = sum(100 * blocks * (2000 * r["input"] * (1.25 if r["provider"] == "openai" else 1)
                         + cap * r["output"]) / 1e6 for r in RATES.values())
            scenarios.append(dict(independent_blocks=blocks, calls=400 * blocks, output_allowance=cap,
                assumed_input_tokens_per_call=2000, no_cache_consumed_cap_scenario_usd=estimate))
    worst = sum(100 * len(plan["blocks"]) * (INPUT_BYTE_LIMIT * r["input"] *
        (1.25 if r["provider"] == "openai" else 2) + max(plan["output_caps"].values()) * r["output"]) / 1e6 for r in RATES.values())
    return dict(budget=budget_status(budget_root), preflight=preflight,
        preflight_reserve_usd=sum(row["reserve_usd"] for row in preflight),
        full_fixed_sample_reservation_bound_usd=worst,
        scenarios=scenarios, main_authorized_with_current_budget=worst <= budget_status(budget_root)["remaining_usd"],
        warning="Cost-at-cap scenarios, not expected invoices. Pilot cannot establish significance. No-cache input-bound guard may stop a large payload.")


class Runner:
    def __init__(self, run, keys=None, *, transport=None, callback=None):
        self.run = Path(run).resolve()
        self.plan, self.envelope = read(self.run / "plan.json"), read(self.run / "envelope.json")
        if study.digest(self.envelope) != (self.run / "fingerprint.sha256").read_text(encoding="utf-8").strip():
            raise ValueError("Protocol fingerprint changed")
        if self.envelope["plan"] != self.plan:
            raise ValueError("Frozen plan changed")
        for name, expected in self.envelope["source_hashes"].items():
            path = self.run / "source_snapshot" / name
            current = Path(__file__).with_name(name) if name.endswith(".py") else self.run.parent.parent / "hypotheses" / name
            if sha(path) != expected or sha(current) != expected:
                raise ValueError("Frozen/current implementation changed; prepare a new fingerprint: " + name)
        self.budget_root = self.run.parent.parent.parent / "12_pressure_framing_api_20261020"
        budget_status(self.budget_root)
        current = read(self.budget_root / "data/api_budget.json")["attempts"]
        if any(key not in current or study.digest(current[key]) != value for key, value in self.envelope["prior_attempts"].items()):
            raise ValueError("Earlier shared spending changed")
        self.keys, self.transport, self.callback = keys or {}, transport, callback or (lambda event: None)

    def _audit_receipt(self, ident):
        directory = self.run / "attempts" / ident
        receipt = read(directory / "receipt.json")
        required = {"task.json", "prompt.txt", "schema.json", "payload.json"}
        if receipt.get("http_status") is not None:
            required.add("response.json")
        if receipt.get("accepted"):
            required.add("accepted.json")
        if set(receipt.get("files", {})) != required or {p.name for p in directory.iterdir() if p.is_file()} != required | {"receipt.json"}:
            raise ValueError("Saved attempt file inventory differs")
        for name, expected in receipt["files"].items():
            if Path(name).name != name or sha(directory / name) != expected:
                raise ValueError("Saved API evidence changed")
        if receipt.get("http_status") is not None and not receipt.get("saved_body_sanitized") and receipt.get("provider_body_sha256") != sha(directory / "response.json"):
            raise ValueError("Original provider body hash differs")
        ledger = read(self.budget_root / "data/api_budget.json")["attempts"].get(receipt["attempt_id"])
        if not ledger or abs(ledger["charge_usd"] - receipt["charge_usd"]) > 1e-12 or any(
                ledger.get(k) != v for k, v in {"run": self.run.name, "task_id": ident, "model": receipt["model"]}.items()):
            raise ValueError("Receipt/shared ledger differ")
        if ledger.get("receipt_sha256") != sha(directory / "receipt.json"):
            raise ValueError("Receipt hash differs from shared ledger")
        task = read(directory / "task.json")
        prompt = task.get("prompt") or study.prompt_text(task)
        schema = task.get("schema") or study.response_schema(task)
        payload = read(directory / "payload.json")
        if task["task_id"] != ident or task["model"] != receipt["model"] or payload != payload_for(task["model"], prompt, schema, task["max_output_tokens"]):
            raise ValueError("Frozen task/payload identity differs")
        if (directory / "prompt.txt").read_text(encoding="utf-8") != prompt or read(directory / "schema.json") != schema:
            raise ValueError("Frozen prompt/schema differs")
        if abs(reserve_amount(receipt["model"], payload) - ledger["reserve_usd"]) > 1e-12:
            raise ValueError("Saved reservation differs from frozen payload")
        if receipt.get("http_status") is not None:
            try:
                raw = read(directory / "response.json")
            except ValueError:
                raw = {}
            usage, charge = measured_usage(receipt["model"], raw)
            if receipt["http_status"] in (400, 401, 403, 404, 422, 429) and usage is None:
                charge = 0.
            if abs((ledger["reserve_usd"] if charge is None else charge) - ledger["charge_usd"]) > 1e-12:
                raise ValueError("Saved charge differs from literal provider usage")
            if receipt["accepted"]:
                literal, reported = extract(receipt["model"], raw)
                if reported != receipt["reported_model"] or validate_literal(task, literal) or literal != read(directory / "accepted.json"):
                    raise ValueError("Accepted literal/model/schema validation differs")
        return receipt

    def _submit(self, task, client, ledger, local_cap=None):
        ident, model = task["task_id"], task["model"]
        directory = self.run / "attempts" / ident
        prompt = task.get("prompt") or study.prompt_text(task)
        schema = task.get("schema") or study.response_schema(task)
        payload = payload_for(model, prompt, schema, task["max_output_tokens"])
        freeze(directory / "task.json", task)
        freeze(directory / "prompt.txt", prompt)
        freeze(directory / "schema.json", schema)
        freeze(directory / "payload.json", payload)
        if (directory / "receipt.json").exists():
            receipt = self._audit_receipt(ident)
            if receipt["accepted"]:
                literal, _ = extract(model, read(directory / "response.json"))
                if literal != read(directory / "accepted.json"):
                    raise ValueError("Accepted choices differ from literal provider response")
                return literal
            return None  # failed slots are preserved, never resent.
        attempt_id = study.digest(["weekly-pivot-v2", self.run.name, ident, payload])
        reservation = reserve_amount(model, payload)
        # A per-preflight cap counts every earlier attempt in this run.
        if local_cap is not None:
            already = sum(v["charge_usd"] for v in ledger.data["attempts"].values() if v.get("run") == self.run.name)
            if already + reservation > local_cap + 1e-12:
                raise BudgetStop("The bounded technical pilot cap cannot cover this request")
        provider = RATES[model]["provider"]
        key = self.keys.get(provider)
        if not key:
            raise ValueError("Missing " + provider + " key; enter only in the hidden notebook field")
        ledger.reserve(attempt_id, reservation, dict(run=self.run.name, experiment=self.run.parent.parent.name,
            task_id=ident, model=model, phase=task["phase"], prices=RATES[model], price_date=PRICE_DATE))
        self.callback(dict(task_id=ident, status="requesting", reserved_usd=reservation, spent_usd=ledger.spent))
        headers = ({"Authorization": "Bearer " + key} if provider == "openai" else
                   {"x-api-key": key, "anthropic-version": "2023-06-01"})
        url = "https://api.openai.com/v1/responses" if provider == "openai" else "https://api.anthropic.com/v1/messages"
        started = time.perf_counter()
        usage, charge, accepted, literal, reported, status, error = None, None, False, None, None, None, None
        provider_body_sha256, sanitized = None, False
        try:
            response = client.post(url, headers=headers, json=payload)
            status = response.status_code
            # Preserve original bytes unless the provider echoes a credential.
            # A sanitized error has a separately recorded original-body hash.
            provider_body_sha256 = hashlib.sha256(response.content).hexdigest()
            body = _clean(response.text, self.keys)
            sanitized = body != response.text
            freeze(directory / "response.json", body if sanitized else response.content)
            raw = json.loads(body)
            usage, charge = measured_usage(model, raw)
            if status in (400, 401, 403, 404, 422, 429) and usage is None:
                charge = 0.
            response.raise_for_status()
            if usage is None:
                raise ValueError("Missing/invalid usage; preserve reservation and fail the technical accounting gate")
            literal, reported = extract(model, raw)
            problems = validate_literal(task, literal)
            if problems:
                raise ValueError("; ".join(problems))
            # Do not silently change backend snapshots partway through a response stream.
            prior = [read(p) for p in (self.run / "attempts").glob("*/receipt.json")]
            known = {r["reported_model"] for r in prior if r.get("accepted") and r.get("model") == model}
            if known and known != {reported}:
                raise ValueError("Provider backend changed during this run")
            freeze(directory / "accepted.json", literal)
            accepted = True
        except Exception as exc:
            error = _clean(type(exc).__name__ + ": " + str(exc), self.keys)
        elapsed = time.perf_counter() - started
        # Unknown charges retain the whole reservation, including network failures.
        settlement_error = None
        try:
            ledger.settle(attempt_id, charge, "received" if status is not None else "unknown_charge")
        except BudgetStop as exc:
            settlement_error = exc
        files = {p.name: sha(p) for p in directory.iterdir() if p.is_file() and p.name != "receipt.json"}
        receipt = dict(task_id=ident, model=model, reported_model=reported, accepted=accepted,
            attempt_id=attempt_id, http_status=status, usage=usage, charge_usd=ledger.data["attempts"][attempt_id]["charge_usd"],
            reserve_usd=reservation, elapsed_seconds=elapsed, requested_effort="high", error=error, files=files,
            provider_body_sha256=provider_body_sha256, saved_body_sanitized=sanitized, completed=now())
        freeze(directory / "receipt.json", receipt)
        ledger.data["attempts"][attempt_id]["receipt_sha256"] = sha(directory / "receipt.json")
        _save_ledger(ledger.path, ledger.data)
        if settlement_error:
            raise settlement_error
        self.callback(dict(task_id=ident, status="accepted" if accepted else "failed", elapsed_seconds=elapsed, spent_usd=ledger.spent))
        return literal if accepted else None

    def run_preflight(self):
        tasks = [preflight_task(self.plan, model) for model in self.plan["models"]]
        with runner_lock(self.budget_root):
            Runner(self.run)  # Recheck frozen sources and prior charges while holding the shared lock.
            ledger = BudgetLedger(self.budget_root)
            # All four technical requests must fit before the first purchase.
            pending = [t for t in tasks if not (self.run / "attempts" / t["task_id"] / "receipt.json").exists()]
            if any(not self.keys.get(RATES[t["model"]]["provider"]) for t in pending):
                raise ValueError("Both provider keys are required before the first pending purchase")
            reserve = sum(reserve_amount(t["model"], payload_for(t["model"], t["prompt"], t["schema"])) for t in pending)
            already = sum(v["charge_usd"] for v in ledger.data["attempts"].values() if v.get("run") == self.run.name)
            if reserve + ledger.spent > 5 + 1e-12 or reserve + already > PREFLIGHT_LOCAL_CAP + 1e-12:
                raise BudgetStop("All remaining technical pilot slots must fit both spending guards before launch")
            with httpx.Client(transport=self.transport, timeout=180.) as client:
                return {t["model"]: self._submit(t, client, ledger, PREFLIGHT_LOCAL_CAP) is not None for t in tasks}

    def run_games(self):
        """Development games only; never starts an unfunded fixed-size sample."""
        estimate = planning(self.run)
        if estimate["full_fixed_sample_reservation_bound_usd"] > estimate["budget"]["remaining_usd"] + 1e-12:
            raise BudgetStop("The full fixed sample exceeds remaining authorization. No main calls made. See cost scenarios.")
        if not self.plan.get("development_only"):
            raise ValueError("This implementation has not been approved as a literal-time confirmatory protocol")
        accepted = {}
        for path in (self.run / "attempts").glob("*/receipt.json"):
            receipt = self._audit_receipt(path.parent.name)
            if receipt["accepted"] and "__technical_preflight" not in receipt["task_id"]:
                literal, _ = extract(receipt["model"], read(path.parent / "response.json"))
                if literal != read(path.parent / "accepted.json"):
                    raise ValueError("Literal choices changed")
                accepted[receipt["task_id"]] = literal
        with runner_lock(self.budget_root):
            Runner(self.run)
            ledger = BudgetLedger(self.budget_root)
            # Repeat the whole fixed-sample check under the same shared lock.
            if estimate["full_fixed_sample_reservation_bound_usd"] + ledger.spent > 5 + 1e-12:
                raise BudgetStop("The locked shared ledger cannot fund the full fixed sample")
            with httpx.Client(transport=self.transport, timeout=180.) as client:
                for block in self.plan["blocks"]:
                    failed = set()
                    for week in range(1, study.WEEKS + 1):
                        pairs = [(m, a) for m in self.plan["models"] for a in study.ARMS]
                        random.Random(self.plan["seed"] + week + int(block["block_id"][1:]) * 101).shuffle(pairs)
                        for model, arm in pairs:
                            if (model, arm) in failed:
                                continue
                            for phase in (("initial", "revision") if arm == "A" else ("initial",)):
                                task = study.build_task(self.plan, model, block["block_id"], arm, week, phase, accepted)
                                value = self._submit(task, client, ledger)
                                if value is None:
                                    failed.add((model, arm)); break
                                accepted[task["task_id"]] = value
                    for model in self.plan["models"]:
                        for arm in study.ARMS:
                            if (model, arm) in failed:
                                continue
                            for phase in (("probe", "probe_revision") if arm == "A" else ("probe",)):
                                task = study.build_task(self.plan, model, block["block_id"], arm, phase=phase, accepted=accepted)
                                value = self._submit(task, client, ledger)
                                if value is None:
                                    break
                                accepted[task["task_id"]] = value
        return export_outcomes(self.run, accepted)


def export_outcomes(run, accepted):
    run = Path(run)
    plan = read(run / "plan.json")
    rows = [study.block_outcomes(plan, m, b["block_id"], a, accepted)
            for m in plan["models"] for b in plan["blocks"] for a in study.ARMS]
    signature = study.digest(rows)[:12]
    output = run.parent.parent / "analysis" / run.name / signature
    output.mkdir(parents=True, exist_ok=True)
    freeze(output / "outcomes.json", rows)
    columns = ["model", "block_id", "arm", "complete", "weeks", "chains_in_cluster", "pipeline_sensitivity",
               "chain_total_cost", "mean_role_order_variance", "mean_role_bullwhip"]
    import io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    freeze(output / "block_outcomes.csv", stream.getvalue())
    inference_plan = dict(schema_version="pivot-inference-plan-v2", models=plan["models"],
        block_ids=[b["block_id"] for b in plan["blocks"]], weeks=24, sweep_sizes=[10, 20, 40],
        source_kind="model_observations", provenance_verified=False,
        collection_kind=plan["collection_kind"], development_only=plan["development_only"],
        independent_blocks_confirmed=True,
        interpretation="Development resource-opportunity analogue, not a literal human binding-time study")
    freeze(output / "inference_plan.json", inference_plan)
    return output
