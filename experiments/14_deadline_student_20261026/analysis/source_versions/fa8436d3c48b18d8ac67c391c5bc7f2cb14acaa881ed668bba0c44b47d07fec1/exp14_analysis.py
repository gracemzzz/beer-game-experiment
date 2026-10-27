"""Offline, fail-closed analysis of experiment 14's separately saved stages.

No model calls, generated decisions, source repairs, or missing-value imputation.
Main inference requires the entire fixed ten-block sample and hash-bound external
adherence reviews. Development outcomes are never pooled into main inference.
"""
from __future__ import annotations

from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import statistics
import textwrap

from . import exp14_deadline as controller
from .pivot_inference_v2 import ENDPOINTS, holm_adjust, paired_inference


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/14_deadline_student_20261026"
SCHEMA = "exp14-analysis-v1"
STAGES = ("latency", "feasibility", "main")
ROLES = tuple(controller.physics.ROLES)
MAIN_N = 10
PROBE_FIELDS = ("probe_id", "role", "inventory", "backlog", "outstanding",
                "pipeline_arrivals", "customer_demand", "recent_demand_history", "shared_inventory")
QUESTION_FIELDS = ("question_id", "question", "choices")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def mean(values):
    return statistics.fmean(values) if values else None


def fmt(value):
    if value is None:
        return "NA"
    return f"{value:.6g}" if isinstance(value, (int, float)) else str(value)


def _public(row, fields):
    value = dict(row)
    if "probe_id" not in value and "id" in value:
        value["probe_id"] = value["id"]
    if "question_id" not in value and "id" in value:
        value["question_id"] = value["id"]
    if "choices" not in value and "options" in value:
        value["choices"] = value["options"]
    return {key: value[key] for key in fields if key in value}


def scoring_bank(case, key, fallback):
    """Prefer case-frozen metadata; fallback only after exact public-field match."""
    rows = case.get(key, [])
    private_key = "pair_id" if key == "probes" else "correct_answer"
    if all(private_key in row for row in rows):
        return rows
    fields = PROBE_FIELDS if key == "probes" else QUESTION_FIELDS
    ident = fields[0]
    metadata = case.get("assay_scoring" if key == "probes" else "comprehension_scoring", {})
    if metadata and all(private_key in metadata.get(_public(row, fields).get(ident), {}) for row in rows):
        private_fields = ("pair_id", "assay_dimension") if key == "probes" else ("correct_answer", "reason")
        return [dict(_public(row, fields), **{k: v for k, v in metadata[_public(row, fields)[ident]].items()
                                            if k in private_fields}) for row in rows]
    indexed = {_public(row, fields).get(ident): row for row in fallback}
    result = []
    for row in rows:
        shown = _public(row, fields)
        candidate = indexed.get(shown.get(ident))
        if candidate is None or shown != _public(candidate, fields):
            raise ValueError("Scoring metadata is missing or does not match the exact case display")
        result.append(candidate)
    return result


def probe_metrics(probes, answers):
    """Equal-pair response slopes plus explicitly descriptive diagnostics."""
    grouped = defaultdict(list)
    for probe in probes:
        grouped[(probe["assay_dimension"], probe["pair_id"])].append(probe)
    pairs, observations, summaries = [], [], []
    for (dimension, ident), members in sorted(grouped.items()):
        if dimension not in ("pipeline", "backlog") or len(members) != 2:
            raise ValueError("Each assay pair must have two states and a known dimension")
        field = "outstanding" if dimension == "pipeline" else "backlog"
        low, high = sorted(members, key=lambda row: row[field])
        if high[field] <= low[field] or high["role"] != low["role"] or high["role"] not in ROLES:
            raise ValueError("Invalid pair contrast or role")
        # All other public fields must be held fixed, except pipeline quantity
        # and its proportional arrival schedule, or the manipulated backlog.
        held = set(PROBE_FIELDS) - {"probe_id", field}
        if dimension == "pipeline":
            held.remove("pipeline_arrivals")
            if (low[field] <= 0 or any(a * high[field] != b * low[field]
                                      for a, b in zip(low["pipeline_arrivals"], high["pipeline_arrivals"]))):
                raise ValueError("Pipeline pair changes relative timing allocation")
        if any(low.get(key) != high.get(key) for key in held):
            raise ValueError("Probe pair changes a nonmanipulated public field")
        for row in members:
            arrivals = row["pipeline_arrivals"]
            if (len(arrivals) != 3 or any(type(v) is not int or v < 0 for v in arrivals)
                    or sum(arrivals) != row["outstanding"]
                    or min(row["inventory"], row["backlog"]) < 0
                    or row["inventory"] * row["backlog"] != 0):
                raise ValueError("Probe state violates the local accounting constraints")
        low_id, high_id = low.get("probe_id", low.get("id")), high.get("probe_id", high.get("id"))
        q_low, q_high = answers.get(low_id), answers.get(high_id)
        complete = q_low is not None and q_high is not None
        delta = high[field] - low[field]
        signed = -1 if dimension == "pipeline" else 1
        slope = signed * (q_high - q_low) / delta if complete else None
        row = dict(assay_dimension=dimension, pair_id=ident, role=low["role"],
                   low_probe_id=low_id, high_probe_id=high_id, low_quantity=low[field],
                   high_quantity=high[field], delta_quantity=delta, low_order=q_low,
                   high_order=q_high, complete=complete, response_slope=slope,
                   timing_profile=",".join(fmt(v / low["outstanding"]) for v in low["pipeline_arrivals"])
                   if low["outstanding"] else "zero outstanding")
        pairs.append(row)
        if complete:
            for state, order in ((low, q_low), (high, q_high)):
                observations.append(dict(assay_dimension=dimension, pair_id=ident, role=state["role"],
                                         probe_id=state.get("probe_id", state.get("id")),
                                         quantity=state[field], order=order))
    aggregate = {}
    for dimension in ("pipeline", "backlog"):
        own = [row for row in pairs if row["assay_dimension"] == dimension]
        balanced = len(own) == 8 and all(sum(row["role"] == role for row in own) == 2 for role in ROLES)
        aggregate[dimension + "_sensitivity"] = mean([row["response_slope"] for row in own]) if (
            balanced and all(row["complete"] for row in own)) else None
        available = [row for row in own if row["complete"]]
        # Ordinary least squares with a separate intercept for every pair.
        den = sum(row["delta_quantity"] ** 2 for row in available)
        raw_beta = sum(row["delta_quantity"] * (row["high_order"] - row["low_order"])
                       for row in available) / den if den else None
        signed = -1 if dimension == "pipeline" else 1
        for obs in (r for r in observations if r["assay_dimension"] == dimension):
            pair = next(r for r in available if r["pair_id"] == obs["pair_id"])
            intercept = (pair["low_order"] + pair["high_order"]) / 2 - raw_beta * (
                pair["low_quantity"] + pair["high_quantity"]) / 2
            obs.update(pair_fixed_effect_intercept=intercept,
                       fitted_order=intercept + raw_beta * obs["quantity"],
                       residual=obs["order"] - intercept - raw_beta * obs["quantity"])
        for role in (*ROLES, "all"):
            role_pairs = [row for row in available if role == "all" or row["role"] == role]
            slopes = [row["response_slope"] for row in role_pairs]
            orders = [answers[p.get("probe_id", p.get("id"))] for p in probes
                      if p["assay_dimension"] == dimension and (role == "all" or p["role"] == role)
                      and p.get("probe_id", p.get("id")) in answers]
            summaries.append(dict(assay_dimension=dimension, role=role, complete_pairs=len(role_pairs),
                                  planned_pairs=8 if role == "all" else 2,
                                  observed_orders=len(orders),
                                  mean_response_slope=mean(slopes), min_response_slope=min(slopes) if slopes else None,
                                  max_response_slope=max(slopes) if slopes else None,
                                  sample_sd_response_slope=statistics.stdev(slopes) if len(slopes) > 1 else None,
                                  zero_slope_fraction=mean([float(v == 0) for v in slopes]),
                                  zero_order_fraction=mean([float(v == 0) for v in orders]),
                                  pair_fixed_effect_response_slope=signed * raw_beta if role == "all" and raw_beta is not None else None,
                                  diagnostic="Two levels per pair; curvature unidentified. Cross-pair heterogeneity only."))
    aggregate.update(observed_probe_orders=len(answers),
                     probe_zero_order_fraction=mean([float(v == 0) for v in answers.values()]),
                     probe_order_min=min(answers.values()) if answers else None,
                     probe_order_max=max(answers.values()) if answers else None,
                     probe_all_observed_orders_equal=len(set(answers.values())) == 1 if answers else None)
    return aggregate, pairs, observations, summaries


def game_metrics(result):
    weeks = result.get("weeks", [])
    complete = len(weeks) == 24 and result.get("planned_weeks") == 24
    orders = [v for row in weeks for v in row["orders"]]
    holding = sum(.5 * role["inventory"] for row in weeks for role in row["roles"])
    backlog = sum(role["backlog"] for row in weeks for role in row["roles"])
    demand_variance = statistics.variance([row["customer_demand"] for row in weeks]) if complete else None
    role_rows = []
    for index, role in enumerate(ROLES):
        values = [row["orders"][index] for row in weeks]
        variance = statistics.variance(values) if complete else None
        last = weeks[-1]["roles"][index] if weeks else {}
        role_rows.append(dict(role=role, complete_24_weeks=complete, observed_weeks=len(weeks),
                              weekly_sample_order_variance=variance,
                              bullwhip=variance / demand_variance if complete and demand_variance > 0 else None,
                              order_min=min(values) if values else None, order_max=max(values) if values else None,
                              zero_order_fraction=mean([float(v == 0) for v in values]),
                              final_observed_inventory=last.get("inventory"), final_observed_backlog=last.get("backlog"),
                              final_observed_outstanding_after_order=last.get("supply_line", last.get("outstanding", 0)) + values[-1]
                              if values else None))
    return dict(complete_24_weeks=complete, chain_total_cost=holding + backlog if complete else None,
                complete_holding_cost=holding if complete else None,
                complete_backlog_cost=backlog if complete else None,
                completed_prefix_cost=holding + backlog, observed_holding_cost=holding, observed_backlog_cost=backlog,
                customer_demand_sample_variance=demand_variance,
                mean_role_order_variance=mean([row["weekly_sample_order_variance"] for row in role_rows]) if complete else None,
                mean_role_bullwhip=mean([row["bullwhip"] for row in role_rows]) if complete and demand_variance > 0 else None,
                game_zero_order_fraction=mean([float(v == 0) for v in orders]),
                game_order_min=min(orders) if orders else None, game_order_max=max(orders) if orders else None), role_rows


def timing_metrics(result):
    rows = []
    opened = {e["display"]["decision_id"]: e["display"] for e in result.get("events", [])
              if e.get("kind") == "display_opened"}
    for event in result.get("events", []):
        if event.get("kind") not in ("submission_accepted", "submission_rejected"):
            continue
        display = opened.get(event.get("decision_id"), {})
        clock = display.get("deadline_clock", {})
        duration = event.get("elapsed_seconds")
        limit = clock.get("deadline_seconds")
        rows.append(dict(decision_id=event.get("decision_id"), phase=display.get("phase", "unknown"),
                         accepted=event.get("accepted"), elapsed_seconds=duration, deadline_seconds=limit,
                         on_time=duration <= limit if duration is not None and limit is not None else None,
                         rejection_reason=event.get("rejection_reason")))
    summary = {}
    for phase in ("game", "probes", "comprehension"):
        shown = [r for r in opened.values() if r.get("phase") == phase]
        accepted = [r for r in rows if r["phase"] == phase and r["accepted"]]
        elapsed = sorted(r["elapsed_seconds"] for r in accepted if r["elapsed_seconds"] is not None)
        summary.update({phase + "_opened": len(shown), phase + "_accepted": len(accepted),
                        phase + "_accepted_per_opened": len(accepted) / len(shown) if shown else None,
                        phase + "_median_seconds": statistics.median(elapsed) if elapsed else None,
                        phase + "_max_seconds": max(elapsed) if elapsed else None,
                        phase + "_p90_seconds": elapsed[max(0, math.ceil(.9 * len(elapsed)) - 1)] if elapsed else None})
    timed = [d for d in opened.values() if d.get("deadline_clock", {}).get("deadline_seconds") is not None]
    accepted_timed = sum(r["accepted"] and r["on_time"] is True for r in rows)
    summary.update(timed_displays_opened=len(timed), timed_displays_accepted_on_time=accepted_timed,
                   accepted_on_time_per_timed_display=accepted_timed / len(timed) if timed else None,
                   late_submission_events=sum(r["on_time"] is False for r in rows),
                   rejected_submission_events=sum(not r["accepted"] for r in rows))
    return summary, rows


def knowledge_metrics(questions, answers):
    rows = [dict(question_id=q.get("question_id", q.get("id")), answer=(answers or {}).get(q.get("question_id", q.get("id"))),
                 correct_answer=q["correct_answer"], reason=q.get("reason", "")) for q in questions]
    for row in rows:
        row["correct"] = row["answer"] == row["correct_answer"] if row["answer"] is not None else None
    answered = [r for r in rows if r["answer"] is not None]
    return dict(knowledge_answered=len(answered), knowledge_items=len(rows),
                knowledge_correct=sum(r["correct"] for r in answered) if answered else None,
                knowledge_fraction_correct=mean([float(r["correct"]) for r in answered])), rows


def adherence_review(folder, result_hash, case_hash):
    path = folder / "ADHERENCE_REVIEW.json"
    if not path.exists():
        return dict(passed=False, status="external review missing")
    raw = path.read_bytes()
    try:
        review = json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeError) as error:
        return dict(passed=False, status="unreadable external review: " + str(error))
    matches = review.get("result_sha256") == result_hash and review.get("case_sha256") == case_hash
    required = ("full_public_context_reviewed", "fresh_context_confirmed", "literal_model_choices_confirmed", "fixed_requested_settings_confirmed")
    passed = review.get("passed") is True and matches and all(review.get(key) is True for key in required)
    return dict(passed=passed, status="passed and hash-bound" if passed else "failed, incomplete or hash mismatch",
                review_sha256=hashlib.sha256(raw).hexdigest(), checks={key: review.get(key) for key in required})


def load_runs(experiment):
    fallback_probes = read_json(experiment / "prompts/probes.json") if (experiment / "prompts/probes.json").exists() else []
    fallback_questions = read_json(experiment / "prompts/comprehension.json") if (experiment / "prompts/comprehension.json").exists() else []
    runs, tables = [], defaultdict(list)
    for stage in STAGES:
        for path in sorted((experiment / "data" / stage).glob("*/RESULT.json")):
            result_bytes = path.read_bytes()
            result_hash = hashlib.sha256(result_bytes).hexdigest()
            record = dict(stage=stage, run_directory=path.parent.name, result_sha256=result_hash,
                          result_path=path.relative_to(experiment).as_posix(), replay_valid=False, analysis_error=None)
            try:
                payload, case = json.loads(result_bytes.decode("utf-8-sig")), read_json(path.parent / "CASE.json")
                record.update({key: payload.get(key) for key in ("case_id", "block_id", "arm", "prompt_version", "complete", "stopped",
                              "terminal_reason", "completed_weeks", "planned_weeks", "completed_probe_pages", "planned_probe_pages",
                              "comprehension_complete", "requested_model", "requested_effort", "actual_model", "actual_effort")})
                record.update(case_sha256=controller.digest(case), seed=case.get("seed"), profile_ids=payload.get("profile_ids"),
                              deadline_seconds=case.get("deadline_seconds"), phase_deadline_seconds=case.get("phase_deadline_seconds", {}))
                if payload.get("stage") != stage or case.get("stage") != stage:
                    raise ValueError("Stage directory, CASE and RESULT disagree")
                try:
                    audit = controller.audit_result(payload, case)
                    record["replay_valid"] = audit["valid"]
                    record["replay_error"] = None
                except (ValueError, KeyError, TypeError, IndexError) as error:
                    record["replay_error"] = str(error)
                record["adherence"] = adherence_review(path.parent, result_hash, record["case_sha256"])
                game, roles = game_metrics(payload)
                probes = scoring_bank(case, "probes", fallback_probes)
                probe, pairs, residuals, diagnostics = probe_metrics(probes, payload.get("probe_answers", {}))
                questions = scoring_bank(case, "comprehension", fallback_questions)
                knowledge, items = knowledge_metrics(questions, payload.get("comprehension_answers"))
                timing, latencies = timing_metrics(payload)
                record.update(game, **probe, **knowledge, **timing)
                record["full_behavior_complete"] = game["complete_24_weeks"] and len(payload.get("probe_answers", {})) == 32 and probe["pipeline_sensitivity"] is not None and probe["backlog_sensitivity"] is not None
                metadata = {k: record.get(k) for k in ("stage", "run_directory", "case_id", "block_id", "arm", "prompt_version", "replay_valid")}
                for name, rows in (("role_outcomes", roles), ("probe_pairs", pairs), ("probe_regression_residuals", residuals),
                                   ("probe_diagnostics", diagnostics), ("knowledge_items", items), ("latencies", latencies)):
                    tables[name].extend(dict(metadata, **row) for row in rows)
                for week in payload.get("weeks", []):
                    tables["weeks"].append(dict(metadata, week=week["week"], customer_demand=week["customer_demand"],
                                                 observed_week_cost=week["cost"], **dict(zip(ROLES, week["orders"]))))
                record["missing"] = payload.get("missing", {})
            except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
                record["analysis_error"] = str(error)
                record["full_behavior_complete"] = False
            runs.append(record)
    return runs, tables


def main_analysis(runs, plan):
    main = [row for row in runs if row["stage"] == "main"]
    reasons = []
    block_ids = plan.get("block_ids", []) if plan else []
    if len(block_ids) != MAIN_N or len(set(block_ids)) != MAIN_N:
        reasons.append("Frozen MAIN_PLAN.json with exactly ten unique block_ids is missing or invalid")
        block_ids = []
    if not plan or plan.get("independent_blocks_confirmed") is not True:
        reasons.append("Independent fresh-context block assignment is not confirmed in the frozen plan")
    if not plan or plan.get("frozen") is not True:
        reasons.append("Main plan is not marked frozen")
    if not plan or plan.get("prompt_version") not in ("V1", "V2"):
        reasons.append("The selected V1/V2 wording is not frozen in the main plan")
    index, duplicates = {}, []
    for row in main:
        key = (row.get("block_id"), row.get("arm"))
        if key in index:
            duplicates.append(key)
        index[key] = row
    if duplicates:
        reasons.append("Duplicate main block/arm slots; no replacement or preferred attempt selected")
    if any(b not in block_ids or a not in ("A", "B", "C") for b, a in index):
        reasons.append("Main records include an unplanned block or arm")
    assigned = [(b, a) for b in block_ids for a in "ABC"]
    missing = [dict(block_id=b, arm=a) for b, a in assigned if (b, a) not in index]
    full_blocks = []
    for block in block_ids:
        own = [index.get((block, arm)) for arm in "ABC"]
        if all(row and row.get("replay_valid") and row.get("full_behavior_complete") for row in own):
            full_blocks.append(block)
    if len(full_blocks) != MAIN_N:
        reasons.append("All ten assigned A/B/C blocks have not completed replay-valid 24-week games and all probes")
    if any(not row.get("adherence", {}).get("passed") for row in main) or len(main) != 30:
        reasons.append("Thirty passing external adherence reviews bound to current RESULT and CASE hashes are required")
    if plan and plan.get("prompt_version") and any(row.get("prompt_version") != plan["prompt_version"] for row in main):
        reasons.append("A main prompt version differs from the frozen selected version")
    for block in block_ids:
        own = [index.get((block, arm)) for arm in "ABC"]
        if all(own) and (len({row.get("seed") for row in own}) != 1 or len({json.dumps(row.get("profile_ids")) for row in own}) != 1):
            reasons.append("Matched seed or persona-role assignment differs within block " + block)
    metric_names = tuple(dict.fromkeys(e[1] for e in ENDPOINTS))
    if any(any(row.get(metric) is None for metric in metric_names) for row in main):
        reasons.append("One or more fixed main endpoints are unavailable")
    eligible = not reasons
    endpoint_rows, contrasts = [], []
    for hypothesis, metric, treated, control, expected in ENDPOINTS:
        diffs = []
        # Descriptive available pairs are retained without p-values when the
        # fixed-sample gate fails. They are never presented as a causal result.
        candidates = block_ids or sorted({r.get("block_id") for r in main if r.get("block_id")})
        for block in candidates:
            left, right = index.get((block, treated)), index.get((block, control))
            if duplicates or not all(r and r.get("replay_valid") and r.get(metric) is not None for r in (left, right)):
                continue
            delta = left[metric] - right[metric]
            diffs.append(delta)
            contrasts.append(dict(hypothesis=hypothesis, metric=metric, block_id=block, contrast=treated + "-" + control,
                                  treated_value=left[metric], control_value=right[metric], difference=delta,
                                  interpretation="fixed main sample" if eligible else "descriptive available pair; no causal claim"))
        stats = paired_inference(diffs, seed=20261026) if eligible and len(diffs) >= 2 else dict(
            n_pairs=len(diffs), mean_difference=mean(diffs), ci95_low=None, ci95_high=None, p_two_sided=None,
            test="withheld: fixed main sample/provenance gate" if not eligible else "unavailable: fewer than two pairs", randomization_draws=0)
        estimate = stats["mean_difference"]
        direction = "unavailable" if estimate is None else "zero" if estimate == 0 else "predicted" if estimate * expected > 0 else "opposite"
        endpoint_rows.append(dict(hypothesis=hypothesis, metric=metric, contrast=treated + "-" + control,
                                  expected_sign=expected, direction=direction, **stats))
    for row, adjusted in zip(endpoint_rows, holm_adjust([r["p_two_sided"] for r in endpoint_rows])):
        row["p_holm_family_5"] = adjusted
        row["statistical_pattern"] = "inference withheld" if adjusted is None else (
            "no statistically detectable difference" if adjusted > .05 else "significant " + row["direction"] + " direction")
    return dict(eligible=eligible, gate_reasons=list(dict.fromkeys(reasons)), planned_blocks=MAIN_N,
                assigned_block_ids=block_ids, observed_contexts=len(main), complete_matched_blocks=len(full_blocks),
                full_block_ids=full_blocks, complete_24week_contexts=sum(bool(r.get("complete_24_weeks")) for r in main),
                complete_behavior_contexts=sum(bool(r.get("full_behavior_complete")) for r in main),
                missing_contexts=missing, endpoints=endpoint_rows, contrasts=contrasts)


def qualification(runs):
    groups = defaultdict(list)
    for row in runs:
        if row["stage"] != "main":
            groups[(row["stage"], row.get("prompt_version"), row.get("arm"))].append(row)
    rows = []
    for (stage, version, arm), values in sorted(groups.items(), key=lambda x: str(x[0])):
        opened = sum(r.get("timed_displays_opened", 0) for r in values)
        accepted = sum(r.get("timed_displays_accepted_on_time", 0) for r in values)
        row = dict(stage=stage, prompt_version=version, arm=arm, attempts=len(values),
                   complete_cases=sum(r.get("complete") is True for r in values),
                   complete_24week_games=sum(r.get("complete_24_weeks") is True for r in values),
                   complete_case_fraction=mean([float(r.get("complete") is True) for r in values]),
                   replay_valid_cases=sum(r.get("replay_valid") is True for r in values),
                   reviewed_cases=sum(r.get("adherence", {}).get("passed") is True for r in values),
                   timed_displays_opened=opened, accepted_on_time=accepted,
                   on_time_per_timed_display=accepted / opened if opened else None,
                   mean_knowledge_fraction=mean([r["knowledge_fraction_correct"] for r in values if r.get("knowledge_fraction_correct") is not None]),
                   selection_basis="Display/adherence, completion, timing and knowledge only; no hypothesis effects or p-values")
        for phase in ("game", "probes"):
            row[phase + "_mean_case_median_seconds"] = mean([r[phase + "_median_seconds"] for r in values if r.get(phase + "_median_seconds") is not None])
            row[phase + "_max_seconds"] = max([r[phase + "_max_seconds"] for r in values if r.get(phase + "_max_seconds") is not None], default=None)
        rows.append(row)
    return rows


def csv_write(path, rows, default_columns=("status",)):
    columns = list(dict.fromkeys(key for row in rows for key in row)) or list(default_columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def input_fingerprint(experiment):
    paths = [Path(__file__), ROOT / "scripts/report_exp14.py", ROOT / "src/beergame_study/pivot_inference_v2.py",
             ROOT / "src/beergame_study/exp14_deadline.py", ROOT / "scripts/run_exp14_agent.py",
             ROOT / "src/beergame_study/manual_weekly_v3.py"]
    for sub in ("hypotheses", "prompts"):
        paths.extend(p for p in (experiment / sub).glob("*") if p.is_file())
    for stage in STAGES:
        for filename in ("RESULT.json", "CASE.json", "ADHERENCE_REVIEW.json"):
            paths.extend((experiment / "data" / stage).glob("*/" + filename))
    hashes = {(p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)): sha256(p)
              for p in sorted(set(paths)) if p.is_file()}
    return controller.digest(hashes), hashes


def preserve_previous(experiment, fingerprint):
    manifest = experiment / "analysis/CURRENT.json"
    if not manifest.exists():
        return
    prior = read_json(manifest)
    if prior.get("fingerprint") == fingerprint:
        return
    label = prior["fingerprint"][:16]
    for name in [*prior.get("generated_files", {}), "analysis/CURRENT.json"]:
        path = experiment / name
        if not path.is_file():
            continue
        parts = Path(name).parts
        if parts[0] not in ("analysis", "reports") or "history" in parts:
            raise ValueError("Prior manifest contains a nonowned output")
        target = experiment / parts[0] / "history" / label / Path(*parts[1:])
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != path.read_bytes():
            raise ValueError("Historical report collision; refusing to overwrite prior bytes")
        if not target.exists():
            shutil.copyfile(path, target)


def make_figures(experiment, result, tables):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    folder = experiment / "reports/figures"
    folder.mkdir(parents=True, exist_ok=True)
    generated, entries = [], []
    def save(fig, name):
        for extension in ("png", "pdf"):
            path = folder / (name + "." + extension)
            fig.savefig(path, dpi=170, bbox_inches="tight")
            generated.append(path)
        plt.close(fig)
    counts = list(range(1, MAIN_N + 1))
    minima = [2 ** (1 - n) for n in counts]
    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    ax.plot(counts, minima, marker="o", label=r"Exact two-sided minimum: $2/2^n$")
    ax.plot(counts, [min(1, 5 * p) for p in minima], marker="s", label=r"First Holm threshold comparison: $\min(1,5p_{min})$")
    ax.axhline(.05, color="gray", linestyle="--", label="0.05 reference")
    ax.set(yscale="log", xticks=counts, xlabel="Independent nonzero matched chain-block contrasts (n)",
           ylabel="Mathematically attainable p-value", title="Planning calculation only - no observed effect or power claim")
    ax.legend(fontsize=8)
    fig.subplots_adjust(bottom=.28)
    fig.text(.1, .015, "Ties or zero differences can raise the minimum. The full five-endpoint Holm family is retained.\n"
             "n = 1 has no inferential test in this protocol. Main N is fixed at ten; no significance-driven extension.", fontsize=8)
    save(fig, "planning_minimum_p")
    entries.append("[Planning: minimum attainable p](planning_minimum_p.png) ([PDF](planning_minimum_p.pdf)). Exact sign-flip mathematics, not observations or estimated power. The orange curve is five times the minimum raw p (capped at one), the smallest possible adjusted p for the first Holm rank.")
    dev = [r for r in result["runs"] if r["stage"] != "main"]
    if dev:
        labels = [r["stage"] + "/" + r["run_directory"] for r in dev]
        fig, ax = plt.subplots(figsize=(8, max(3.5, .36 * len(dev))))
        ax.barh(labels, [r.get("completed_weeks", 0) or 0 for r in dev], color="#4477aa")
        ax.set(xlabel="Observed accepted game weeks; a prefix is not a 24-week outcome", xlim=(0, 24),
               title="Development completion only - excluded from main inference")
        save(fig, "development_completion")
        entries.append("[Development completion](development_completion.png) ([PDF](development_completion.pdf)). Actual saved attempts, including stopped prefixes; no imputation.")
    latencies = [r for r in tables.get("latencies", []) if r["stage"] != "main" and r["accepted"] and r["elapsed_seconds"] is not None]
    if latencies:
        groups = defaultdict(list)
        for row in latencies:
            groups[(row["stage"], row["prompt_version"], row["arm"], row["phase"])].append(row["elapsed_seconds"])
        labels, values = zip(*[("/".join(str(v) for v in key), value) for key, value in sorted(groups.items())])
        fig, ax = plt.subplots(figsize=(8, max(3.8, .38 * len(labels))))
        for i, value in enumerate(values):
            ax.scatter(value, [i] * len(value), s=13, alpha=.5, color="#228833")
        ax.set(yticks=range(len(labels)), yticklabels=labels, xlabel="Display-open to complete accepted payload (seconds)",
               title="Observed development latencies - transport and scheduling included")
        save(fig, "development_latency")
        entries.append("[Development latency](development_latency.png) ([PDF](development_latency.pdf)). Every saved accepted submission; rejected and late events remain in the latency CSV.")
    if result["main"]["eligible"]:
        fig, axes = plt.subplots(1, 5, figsize=(15, 4))
        for ax, endpoint in zip(axes, result["main"]["endpoints"]):
            own = [r for r in result["main"]["contrasts"] if r["hypothesis"] == endpoint["hypothesis"]]
            ax.scatter(range(1, len(own) + 1), [r["difference"] for r in own], color="#4477aa")
            ax.axhline(0, color="gray", lw=.8)
            ax.axhline(endpoint["mean_difference"], color="#cc6677", label="mean")
            ax.set(title=endpoint["hypothesis"] + " " + endpoint["contrast"], xlabel="Matched block", ylabel=endpoint["metric"])
        fig.suptitle("Held-out fixed ten-block contrasts; units and inference in REPORT.md")
        fig.tight_layout()
        save(fig, "main_matched_contrasts")
        entries.append("[Held-out matched contrasts](main_matched_contrasts.png) ([PDF](main_matched_contrasts.pdf)). Ten independent paired context contrasts per endpoint; each dot is one block.")
    else:
        entries.append("Held-out H1-H4 figures are withheld: " + "; ".join(result["main"]["gate_reasons"]) + ". See [current status](../REPORT.md).")
    index = folder / "README.md"
    index.write_text("# Current experiment 14 figures\n\n" + "\n\n".join(entries) + "\n\nSource tables: [analysis/tables](../../analysis/tables/). Prior figure bytes are preserved under reports/history by input fingerprint.\n", encoding="utf-8")
    generated.append(index)
    return generated


def report_markdown(result):
    main, runs = result["main"], result["runs"]
    counts = {stage: sum(row["stage"] == stage for row in runs) for stage in STAGES}
    lines = ["# Experiment 14: current results", "",
             f"1. Held-out main sample: **{main['complete_matched_blocks']}/10 complete matched A/B/C blocks**; "
             f"{main['observed_contexts']}/30 saved main contexts ({max(0, 30-main['observed_contexts'])} not received), "
             f"and {main['complete_24week_contexts']}/30 complete 24-week games. "
             + ("The fixed-sample inference gate passed." if main["eligible"] else "Main inference is withheld until the fixed sample and provenance gates pass."),
             f"2. Development is separate: {counts['latency']} latency attempts and {counts['feasibility']} feasibility attempts. "
             "Development choices are assessed by completion, timing, display adherence and knowledge; they do not enter main hypothesis tests.",
             "3. A context controls one four-role chain. There are ten planned independent matched contrasts, not forty independent students. "
             "These are model observations under fictional classroom instructions; human participants: 0.",
             "4. Stopped prefixes, zero choices, opposite responses and failures are retained. Partial cost is not full-horizon cost; missing decisions are never filled.", "",
             "Requested model/effort: gpt-6-astra / xhigh. Actually reported labels appear per case in the outcome table; unverified labels remain unverified. "
             "Launcher temperature and reasoning-token allocation are not exposed.", "",
             "[Figures and status](figures/README.md) | [Case outcomes](../analysis/tables/case_outcomes.csv) | "
             "[Validation and exact input hashes](../analysis/VALIDATION.json)", "",
             "## Main hypotheses and quantities", "",
             "| Endpoint | Quantity and units | Contrast; predicted sign |",
             "|---|---|---|",
             "| H1 | Mean eight pipeline-pair slopes (q_lowP - q_highP)/(P_high - P_low); ordered cases per outstanding case | B-A; negative |",
             "| H2 | Total holding + backlog cost over four roles and 24 weeks; game cost units per chain | B-A; positive |",
             "| H3 | The same pipeline response proxy as H1 | C-B; positive |",
             "| H4a | Mean of four role-level sample weekly order variances (denominator 23); cases squared | C-B; negative |",
             "| H4b | Mean role order variance divided by the chain's external-customer sample demand variance; dimensionless | C-B; negative |", "",
             "Holding costs 0.5 per remaining case per week; backlog costs 1 per unfilled case per week. "
             "H4b is undefined for zero demand variance. H4a/H4b share a numerator and are not independent replications. "
             "[Role outcomes](../analysis/tables/role_outcomes.csv) include final observed inventory, backlog and outstanding after the last accepted order; consequences after week 24 are unmeasured.", "",
             "| Test | Available pairs | Mean contrast | Pointwise 95% interval | Two-sided p | Holm, family of 5 | Direction/status |",
             "|---|---:|---:|---|---:|---:|---|"]
    for row in main["endpoints"]:
        lines.append("| " + " | ".join([row["hypothesis"], str(row["n_pairs"]), fmt(row["mean_difference"]),
                     fmt(row["ci95_low"]) + " to " + fmt(row["ci95_high"]), fmt(row["p_two_sided"]),
                     fmt(row["p_holm_family_5"]), row["direction"] + "; " + row["statistical_pattern"]]) + " |")
    lines.extend(["", "NA means unavailable or deliberately withheld. Before the whole fixed sample and external reviews pass, "
                  "any available-pair effects are descriptive only; treatment-related noncompletion can bias completer comparisons. "
                  "There is no completer-only causal claim and no significance-based stopping or replacement.", ""])
    if main["gate_reasons"]:
        lines.extend(["Current gate conditions: " + "; ".join(main["gate_reasons"]) + ".", ""])
    lines.extend(["When eligible, tests reuse the separately frozen paired sign-flip implementation; the entire five-endpoint family receives Holm correction. "
                  "A significant opposite effect is reported as opposite evidence. Intervals are unadjusted paired-block percentile bootstrap intervals (10,000 resamples), not simultaneous intervals. "
                  "The sign-flip null requires independent symmetric/exchangeable paired differences; a hash receipt alone cannot verify independence or this assumption. "
                  "[Each block contrast](../analysis/tables/main_contrasts.csv).", "",
                  "## Completion, timing and knowledge checks", "",
                  "| Stage | Saved attempts | Complete cases | Complete 24-week games | Replay-valid | Passing external reviews |",
                  "|---|---:|---:|---:|---:|---:|"])
    for stage in STAGES:
        own = [r for r in runs if r["stage"] == stage]
        lines.append("| " + " | ".join([stage, str(len(own)), str(sum(r.get("complete") is True for r in own)),
                     str(sum(r.get("complete_24_weeks") is True for r in own)), str(sum(r.get("replay_valid") is True for r in own)),
                     str(sum(r.get("adherence", {}).get("passed") is True for r in own))]) + " |")
    if result["qualification"]:
        lines.extend(["", "Development qualification checks (fractions range from 0 to 1):", "",
                      "| Stage/version/arm | Complete cases | On time / timed displays | Game median (s) | Probe median (s) | Knowledge fraction |",
                      "|---|---:|---:|---:|---:|---:|"])
        for row in result["qualification"]:
            lines.append("| " + " | ".join(["/".join(str(row[k]) for k in ("stage", "prompt_version", "arm")),
                         str(row["complete_cases"]) + "/" + str(row["attempts"]), fmt(row["on_time_per_timed_display"]),
                         fmt(row["game_mean_case_median_seconds"]), fmt(row["probes_mean_case_median_seconds"]),
                         fmt(row["mean_knowledge_fraction"])]) + " |")
    lines.extend(["", "[Prompt qualification by version/stage/arm](../analysis/tables/prompt_qualification.csv) reports complete fractions, "
                  "on-time accepted responses per opened timed display, game/probe case-median and maximum latencies, and post-task knowledge. "
                  "Untimed calibration has no on-time fraction. Latencies measure display-open to complete-payload reception, including transport, scheduling and output; they are not thinking time. "
                  "A stopped case can have zero late submission events when no payload arrives. Open decisions remain pending until the controller persists their expiry.", "",
                  "[All submission timings](../analysis/tables/latencies.csv) retain rejections. "
                  "[Post-behavior item scores](../analysis/tables/knowledge_items.csv) use private answer keys; scores never exclude main cases. "
                  "The report does not automatically declare a development wording qualified or select one.", "",
                  "## Probe interpretation", "",
                  "[Pair slopes](../analysis/tables/probe_pairs.csv), [role summaries](../analysis/tables/probe_diagnostics.csv), "
                  "and [pair-fixed-effect fits/residuals](../analysis/tables/probe_regression_residuals.csv) preserve all observed responses. "
                  "The pipeline aggregate weights eight pairs equally. The backlog comparison uses (q_highB - q_lowB)/(B_high - B_low) over eight separate pairs, "
                  "also in ordered cases per backlog case. A missing pair makes the fixed aggregate unavailable. "
                  "Fixed-effect regression is supplementary and weights pair slopes by squared quantity differences; it does not replace the primary equal-pair mean.", "",
                  "Report zero-choice and zero-slope fractions, order minima/maxima, role-level slopes and cross-pair spread without deleting extremes. "
                  "Two levels per pair cannot identify curvature; cross-regime variation is a descriptive heterogeneity diagnostic. "
                  "The pipeline slope is a responsiveness proxy, not an identified normative underweighting coefficient. "
                  "Flat choices across both dimensions cannot establish pipeline-specific neglect. Known assay arrival schedules differ from uncertain gameplay fulfillment.", "",
                  "## Planning and reproducibility", "",
                  "[Minimum attainable p versus independent chain blocks](figures/planning_minimum_p.png) is a mathematical planning figure, "
                  "not observed evidence or power. With ten nonzero pairs the exact two-sided minimum is 2/1024 = 0.001953125; "
                  "zero differences/ties may raise it. The fixed N=10 sample does not promise significance.", "",
                  "Rebuild offline: `python scripts/report_exp14.py`. It scans only `data/{latency,feasibility,main}/*/RESULT.json`, "
                  "never other experiments, never an API, and never a hidden reasoning trace. It checks controller replay, exact CASE/result binding and external review receipts. "
                  "A main external `ADHERENCE_REVIEW.json` must contain `passed: true`, `result_sha256` (exact file bytes), and `case_sha256` (controller canonical digest). "
                  "Its `full_public_context_reviewed`, `fresh_context_confirmed`, `literal_model_choices_confirmed`, and `fixed_requested_settings_confirmed` checks must all be true. "
                  "`hypotheses/MAIN_PLAN.json` must freeze exactly ten `block_ids`, the selected `prompt_version`, and `independent_blocks_confirmed: true` with `frozen: true`. "
                  "Reviews must assess full-display access, literal choices, isolation and source/reading exposure without using effect direction or p-values.", "",
                  "Current input fingerprint: `" + result["fingerprint"] + "`. "
                  "Changed-input regenerations first preserve prior generated bytes under `reports/history/<fingerprint>/` and `analysis/history/<fingerprint>/`. "
                  "[Current generated-file manifest](../analysis/CURRENT.json). The local event hash chain is reproducibility evidence, not tamper-proof authentication.", ""])
    return "\n".join(lines)


def make_pdf(path, markdown):
    """Portable text report PDF; plots have separate vector PDFs."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import re
    lines = []
    for line in markdown.splitlines():
        line = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", line).replace("**", "").replace("`", "")
        if line.startswith("|---"):
            continue
        lines.extend(textwrap.wrap(line, width=112, break_long_words=False, break_on_hyphens=False) or [""])
    with PdfPages(path, metadata={"Title": "Experiment 14 current report", "Author": "Offline experiment analysis"}) as pdf:
        for start in range(0, len(lines), 60):
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.text(.065, .955, "\n".join(lines[start:start + 60]), va="top", family="monospace", fontsize=7.1, linespacing=1.38)
            fig.text(.065, .03, "Experiment 14 | Current source: reports/REPORT.md | Page " + str(start // 60 + 1), fontsize=8)
            pdf.savefig(fig)
            plt.close(fig)


def generate_report(experiment=EXPERIMENT):
    experiment = Path(experiment).resolve()
    fingerprint, hashes = input_fingerprint(experiment)
    current = experiment / "analysis/CURRENT.json"
    if current.exists():
        prior = read_json(current)
        if prior.get("fingerprint") == fingerprint and all((experiment / name).is_file() and sha256(experiment / name) == expected
                                                          for name, expected in prior.get("generated_files", {}).items()):
            return read_json(experiment / "analysis/RESULTS.json")
    # Input snapshots can change while live contexts submit. Require one stable
    # read interval before deriving a report; later submissions belong to the
    # next fingerprint. No run file is locked, edited, or delayed by reporting.
    for _ in range(5):
        fingerprint, hashes = input_fingerprint(experiment)
        runs, tables = load_runs(experiment)
        plan_path = experiment / "hypotheses/MAIN_PLAN.json"
        plan = read_json(plan_path) if plan_path.exists() else None
        after, after_hashes = input_fingerprint(experiment)
        if fingerprint == after:
            break
    else:
        raise RuntimeError("Live inputs changed during five snapshot attempts; rerun the offline report")
    preserve_previous(experiment, fingerprint)
    result = dict(schema_version=SCHEMA, generated_utc=datetime.now(timezone.utc).isoformat(), fingerprint=fingerprint,
                  source_and_input_hashes=hashes, runs=runs, main=main_analysis(runs, plan),
                  qualification=qualification(runs), human_participants=0,
                  provenance="Controller replay and hash binding; external review is required for behavior provenance")
    tables.update(case_outcomes=runs, prompt_qualification=result["qualification"],
                  main_endpoints=result["main"]["endpoints"], main_contrasts=result["main"]["contrasts"],
                  main_missing_contexts=result["main"]["missing_contexts"],
                  planning_minimum_p=[dict(independent_nonzero_pairs=n, minimum_two_sided_p=2 ** (1 - n),
                                           first_holm_rank_minimum=min(1, 5 * 2 ** (1 - n)),
                                           status="mathematical planning only; not observed power") for n in range(1, 11)])
    for name in ("role_outcomes", "probe_pairs", "probe_regression_residuals", "probe_diagnostics", "knowledge_items", "latencies", "weeks"):
        tables.setdefault(name, [])
    generated = []
    for name, rows in sorted(tables.items()):
        path = experiment / "analysis/tables" / (name + ".csv")
        csv_write(path, rows)
        generated.append(path)
    results_path = experiment / "analysis/RESULTS.json"
    write_json(results_path, result)
    generated.append(results_path)
    generated.extend(make_figures(experiment, result, tables))
    report_path = experiment / "reports/REPORT.md"
    markdown = report_markdown(result)
    report_path.write_text(markdown, encoding="utf-8")
    generated.append(report_path)
    pdf = experiment / "reports/REPORT.pdf"
    make_pdf(pdf, markdown)
    generated.append(pdf)
    for directory, content in (("analysis", "Current results: [RESULTS.json](RESULTS.json); exact replay/input/output receipt: [VALIDATION.json](VALIDATION.json); derived tables: [tables/](tables/)."),
                               ("reports", "Current report: [REPORT.md](REPORT.md) or [REPORT.pdf](REPORT.pdf). Current figures: [figures/README.md](figures/README.md).")):
        path = experiment / directory / "README.md"
        path.write_text("# Experiment 14 " + directory + "\n\n" + content + "\n\nRebuild with `python scripts/report_exp14.py`; no API calls. Historical generated bytes are under `history/` by prior fingerprint.\n", encoding="utf-8")
        generated.append(path)
    validation = dict(schema_version=SCHEMA, fingerprint=fingerprint, source_and_input_hashes=hashes,
                      scanned_stages=list(STAGES), scanned_results=len(runs),
                      replay_valid=sum(r.get("replay_valid") is True for r in runs),
                      invalid_or_unreplayable_cases=[dict(result_path=r["result_path"], replay_error=r.get("replay_error"), analysis_error=r.get("analysis_error"))
                                                    for r in runs if not r.get("replay_valid") or r.get("analysis_error")],
                      main_gate_passed=result["main"]["eligible"], gate_reasons=result["main"]["gate_reasons"],
                      generated_artifacts_sha256={p.relative_to(experiment).as_posix(): sha256(p) for p in generated},
                      caveat="No saved model results means zero replayed cases, not an empirical validation pass. External reviews are not manufactured by this report.")
    validation_path = experiment / "analysis/VALIDATION.json"
    write_json(validation_path, validation)
    generated.append(validation_path)
    write_json(current, dict(schema_version=SCHEMA, fingerprint=fingerprint, report="reports/REPORT.md",
                             generated_files={p.relative_to(experiment).as_posix(): sha256(p) for p in generated}))
    return result
