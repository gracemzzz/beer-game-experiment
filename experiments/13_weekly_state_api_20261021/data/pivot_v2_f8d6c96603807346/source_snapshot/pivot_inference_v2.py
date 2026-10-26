"""Prospective paired inference for separately generated Beer Game blocks.

Offline only. Input rows are already aggregated within one generation cluster
and arm. This module checks their structure, not the underlying API provenance.
It never treats chains, roles, or weeks inside a cluster as independent samples.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np


PLAN_SCHEMA = "pivot-inference-plan-v2"
RESULT_SCHEMA = "pivot-inference-results-v2"
ARMS = ("A", "B", "C")
ENDPOINTS = (
    ("H1", "pipeline_sensitivity", "B", "A", -1),
    ("H2", "chain_total_cost", "B", "A", 1),
    ("H3", "pipeline_sensitivity", "C", "B", 1),
    ("H4a", "mean_role_order_variance", "C", "B", -1),
    ("H4b", "mean_role_bullwhip", "C", "B", -1),
)
METRICS = tuple(dict.fromkeys(e[1] for e in ENDPOINTS))
REQUIRED_COLUMNS = ("model", "block_id", "arm", "complete", "weeks", "chains_in_cluster", *METRICS)
LIMITATIONS = [
    "Independent generation blocks, not generated chains, roles, or weeks, are the inferential units.",
    "Each arm must have a separately generated response stream; separate identity labels inside a shared response do not establish independent blocks or arms.",
    "The sign-flip test assumes exchangeability under the paired null (or symmetric independent paired differences); the CSV cannot verify this design assumption.",
    "Pipeline sensitivity is an assay proxy, not an identified normative underweighting coefficient.",
    "Computational opportunity or prompted pressure is an analogue, not measured binding human decision time.",
    "The input contains caller-aggregated outcomes. This module does not replay game states or independently authenticate API response lineage.",
    "Sample-size sweeps are fixed descriptive sensitivity analyses, not additional opportunities to stop when significance appears.",
    "Available-case comparisons from an incomplete planned sample are provisional; treatment-related failures can bias complete-case contrasts.",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _integer(value, label, minimum=0):
    if type(value) is bool:
        raise ValueError(label + " must be an integer.")
    if type(value) is int:
        result = value
    elif isinstance(value, str) and value.strip().isdigit():
        result = int(value.strip())
    else:
        raise ValueError(label + " must be an integer.")
    if result < minimum:
        raise ValueError(label + " is below its allowed minimum.")
    return result


def validate_plan(plan):
    if not isinstance(plan, dict) or plan.get("schema_version") != PLAN_SCHEMA:
        raise ValueError("Use the prospectively frozen pivot-inference-plan-v2 configuration.")
    for key in ("models", "block_ids"):
        values = plan.get(key)
        if not isinstance(values, list) or not values or any(type(v) is not str or not v.strip() for v in values):
            raise ValueError(key + " must be a nonempty ordered list of identifiers.")
        if len(values) != len(set(values)):
            raise ValueError(key + " contains duplicate identifiers.")
    if plan.get("weeks") != 24 or type(plan.get("weeks")) is not int:
        raise ValueError("This protocol scores exactly 24 game weeks.")
    if plan.get("sweep_sizes") != [10, 20, 40]:
        raise ValueError("Preserve the prospectively fixed 10/20/40 block prefixes.")
    if plan.get("source_kind") not in ("model_observations", "synthetic_software_control"):
        raise ValueError("Explicitly label model observations or synthetic software controls.")
    if plan.get("collection_kind", "heldout") not in ("development", "heldout"):
        raise ValueError("collection_kind must identify development or heldout collection.")
    for key in ("provenance_verified", "independent_blocks_confirmed", "pipeline_probe_independent_of_game_completion", "development_only"):
        if key in plan and type(plan[key]) is not bool:
            raise ValueError(key + " must be a Boolean.")
    if plan.get("development_only") is True and plan.get("collection_kind") == "heldout":
        raise ValueError("Development-only observations cannot be relabeled as heldout.")
    if plan.get("aggregation", "arithmetic_mean_across_chains") != "arithmetic_mean_across_chains":
        raise ValueError("Supply arithmetic means across chains inside each block/arm.")
    for key, default in (("bootstrap_resamples", 10000), ("monte_carlo_resamples", 50000)):
        if type(plan.get(key, default)) is not int:
            raise ValueError(key + " must be a literal integer in the plan.")
        _integer(plan.get(key, default), key, 1000)
    if type(plan.get("seed", 20261025)) is not int:
        raise ValueError("seed must be a literal integer in the plan.")
    _integer(plan.get("seed", 20261025), "seed")
    return plan


def _complete(value):
    if type(value) is bool:
        return value
    if isinstance(value, str) and value.strip().lower() in ("true", "false"):
        return value.strip().lower() == "true"
    raise ValueError("complete must be a literal Boolean or true/false CSV value.")


def validate_rows(plan, rows):
    """Accept one preaggregated cluster-arm row, never duplicate chain rows."""
    validate_plan(plan)
    normalized, seen = [], set()
    for raw in rows:
        if not isinstance(raw, dict) or None in raw or set(REQUIRED_COLUMNS) - set(raw):
            raise ValueError("An input row is missing required columns.")
        row = {key: raw[key] for key in REQUIRED_COLUMNS}
        model, block, arm = row["model"], row["block_id"], row["arm"]
        if model not in plan["models"] or block not in plan["block_ids"] or arm not in ARMS:
            raise ValueError("An input row has an unplanned model, block, or arm.")
        key = (model, block, arm)
        if key in seen:
            raise ValueError("Duplicate model/block/arm; aggregate chains within their cluster before analysis.")
        seen.add(key)
        row["complete"] = _complete(row["complete"])
        row["weeks"] = _integer(row["weeks"], "weeks")
        row["chains_in_cluster"] = _integer(row["chains_in_cluster"], "chains_in_cluster", 1)
        if row["weeks"] > 24 or (row["complete"] and row["weeks"] != 24):
            raise ValueError("A complete game row must contain exactly 24 weeks.")
        for metric in METRICS:
            value = row[metric]
            if value is None or value == "":
                row[metric] = None
                continue
            if type(value) is bool:
                raise ValueError("A metric cannot be Boolean.")
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError(metric + " must be a finite number or blank.") from None
            if not math.isfinite(value) or (metric != "pipeline_sensitivity" and value < 0):
                raise ValueError(metric + " must be finite; costs and variance measures must be nonnegative.")
            row[metric] = value
        normalized.append(row)
    return normalized


def load_inputs(plan_path, csv_path):
    plan_path, csv_path = Path(plan_path), Path(csv_path)
    plan = validate_plan(json.loads(plan_path.read_text(encoding="utf-8")))
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("CSV headers are missing or duplicated.")
        rows = validate_rows(plan, list(reader))
    evidence = {"plan_sha256": sha256(plan_path), "input_csv_sha256": sha256(csv_path),
                "provenance_status": "caller_assertion_only" if plan.get("provenance_verified") else "not_verified",
                "raw_api_lineage_independently_verified_by_this_module": False}
    receipt_name = plan.get("provenance_receipt")
    if receipt_name:
        receipt_path = (plan_path.parent / receipt_name).resolve()
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("passed") is not True or any(receipt.get(k) != evidence[k] for k in ("plan_sha256", "input_csv_sha256")):
            raise ValueError("The supplied provenance receipt does not bind the exact plan and input CSV.")
        evidence.update(provenance_status="supplied_receipt_hashes_match",
                        provenance_receipt_sha256=sha256(receipt_path))
    return plan, rows, evidence


def holm_adjust(pvalues):
    """Keep the full family, conservatively retaining untested endpoints as 1."""
    values = [1.0 if p is None else float(p) for p in pvalues]
    if any(not math.isfinite(p) or not 0 <= p <= 1 for p in values):
        raise ValueError("P-values must be finite numbers in [0,1], or missing.")
    adjusted, running = [None] * len(values), 0.0
    for rank, index in enumerate(sorted(range(len(values)), key=lambda i: values[i])):
        running = max(running, min(1.0, (len(values) - rank) * values[index]))
        if pvalues[index] is not None:
            adjusted[index] = running
    return adjusted


def _seed(seed, label):
    return int.from_bytes(hashlib.sha256((str(seed) + ":" + label).encode()).digest()[:8], "big")


def paired_inference(differences, *, seed=20261025, bootstrap_resamples=10000, monte_carlo_resamples=50000):
    """Two-sided paired sign flips and percentile bootstrap of paired blocks."""
    d = np.asarray(differences, dtype=float)
    if d.ndim != 1 or not np.isfinite(d).all():
        raise ValueError("Paired differences must be a finite vector.")
    n = len(d)
    if not n:
        return dict(n_pairs=0, mean_difference=None, ci95_low=None, ci95_high=None,
                    p_two_sided=None, test="unavailable", randomization_draws=0)
    if np.all(d == 0):
        return dict(n_pairs=n, mean_difference=0.0, ci95_low=0.0, ci95_high=0.0,
                    p_two_sided=1.0, test="all_zero", randomization_draws=2 ** n if n <= 18 else 0)
    # Scaling avoids overflow from large but finite outcomes without changing
    # the test statistic ordering. Signs preserve entire paired block vectors.
    scale = float(np.max(np.abs(d)))
    scaled = d / scale
    mean_difference = float(scaled.mean()) * scale
    target = abs(float(scaled.sum()))
    tolerance = 1e-12 * max(1.0, float(np.abs(scaled).sum()))
    rng = np.random.default_rng(seed)
    exceed, draws = 0, 2 ** n if n <= 18 else int(monte_carlo_resamples)
    for start in range(0, draws, 4096):
        count = min(4096, draws - start)
        if n <= 18:
            indices = np.arange(start, start + count, dtype=np.uint64)
            signs = 2 * ((indices[:, None] >> np.arange(n, dtype=np.uint64)) & 1).astype(np.int8) - 1
        else:
            signs = rng.integers(0, 2, size=(count, n), dtype=np.int8) * 2 - 1
        exceed += int(np.count_nonzero(np.abs(signs @ scaled) >= target - tolerance))
    pvalue = exceed / draws if n <= 18 else (exceed + 1) / (draws + 1)
    bootstrap_rng = np.random.default_rng(_seed(seed, "bootstrap"))
    means = np.empty(bootstrap_resamples)
    for start in range(0, bootstrap_resamples, 4096):
        count = min(4096, bootstrap_resamples - start)
        indices = bootstrap_rng.integers(0, n, size=(count, n))
        means[start:start + count] = scaled[indices].mean(axis=1)
    low, high = np.quantile(means, [.025, .975]) * scale
    return dict(n_pairs=n, mean_difference=mean_difference, ci95_low=float(low), ci95_high=float(high),
                p_two_sided=float(pvalue), test="exact_paired_sign_flip" if n <= 18 else "monte_carlo_paired_sign_flip",
                randomization_draws=draws)


def _eligible(plan, row, metric):
    if row is None or row[metric] is None:
        return False
    if metric == "pipeline_sensitivity" and plan.get("pipeline_probe_independent_of_game_completion", False):
        return True
    return row["complete"] and row["weeks"] == 24


def _analysis(plan, rows, block_ids, label):
    indexed = {(r["model"], r["block_id"], r["arm"]): r for r in rows}
    results, contrasts = [], []
    for model in plan["models"]:
        for hypothesis, metric, treated, control, direction in ENDPOINTS:
            differences, matched, excluded, treated_values, control_values = [], [], [], [], []
            treated_chains = control_chains = 0
            for block in block_ids:
                a, b = indexed.get((model, block, treated)), indexed.get((model, block, control))
                if not (_eligible(plan, a, metric) and _eligible(plan, b, metric)):
                    excluded.append(block)
                    continue
                difference = a[metric] - b[metric]
                if not math.isfinite(difference):
                    raise ValueError("Paired subtraction overflowed; rescale outcome units before analysis.")
                matched.append(block)
                differences.append(difference)
                treated_values.append(a[metric])
                control_values.append(b[metric])
                treated_chains += a["chains_in_cluster"]
                control_chains += b["chains_in_cluster"]
                contrasts.append(dict(analysis=label, model=model, hypothesis=hypothesis, block_id=block,
                                      treated_arm=treated, control_arm=control, treated_value=a[metric],
                                      control_value=b[metric], difference=difference,
                                      treated_chains=a["chains_in_cluster"], control_chains=b["chains_in_cluster"]))
            sample_label = model + ":" + hypothesis + ":" + json.dumps(matched, separators=(",", ":"))
            stats = paired_inference(differences, seed=_seed(plan.get("seed", 20261025), sample_label),
                                     bootstrap_resamples=plan.get("bootstrap_resamples", 10000),
                                     monte_carlo_resamples=plan.get("monte_carlo_resamples", 50000))
            effect = stats["mean_difference"]
            results.append(dict(analysis=label, model=model, hypothesis=hypothesis, metric=metric,
                                contrast=treated + "-" + control, expected_sign=direction,
                                planned_blocks=len(block_ids), matched_block_ids=matched,
                                excluded_block_ids=excluded, matched_treated_chains=treated_chains,
                                matched_control_chains=control_chains,
                                planned_sample_complete=len(matched) == len(block_ids),
                                treated_mean=math.fsum(v / len(matched) for v in treated_values) if matched else None,
                                control_mean=math.fsum(v / len(matched) for v in control_values) if matched else None,
                                direction="unavailable" if effect is None else "zero" if effect == 0 else
                                "predicted" if direction * effect > 0 else "opposite", **stats))
    for model in plan["models"]:
        own = [r for r in results if r["model"] == model]
        for row, adjusted in zip(own, holm_adjust([r["p_two_sided"] for r in own])):
            row["p_holm_within_model_5"] = adjusted
    cross_model = len(plan["models"]) == 4 and set(plan["models"]) <= {r["model"] for r in rows}
    adjusted_cross = holm_adjust([r["p_two_sided"] for r in results]) if cross_model else [None] * len(results)
    for row, adjusted in zip(results, adjusted_cross):
        row["p_holm_across_models_20"] = adjusted
        p = row["p_holm_within_model_5"]
        row["statistical_pattern"] = ("unavailable" if p is None else "not_significant" if p > .05 else
                                      "significant_predicted_direction" if row["direction"] == "predicted" else
                                      "significant_opposite_direction" if row["direction"] == "opposite" else "zero")
        development = plan.get("collection_kind") == "development" or plan.get("development_only", False)
        synthetic = plan["source_kind"] == "synthetic_software_control"
        row["used_in_scientific_findings"] = not (synthetic or development)
        row["inference_status"] = ("synthetic_control_only" if synthetic else "development_only" if development else
                                   "conditional_on_verified_provenance_and_independence")
    return results, contrasts


def analyze(plan, rows, *, input_evidence=None):
    plan = validate_plan(plan)
    rows = validate_rows(plan, rows)
    primary, contrasts = _analysis(plan, rows, plan["block_ids"], "primary_fixed_sample")
    sweeps = []
    for size in plan["sweep_sizes"]:
        if size <= len(plan["block_ids"]):
            values, _ = _analysis(plan, rows, plan["block_ids"][:size], "prefix_" + str(size))
            sweeps.extend(values)
    present = {(r["model"], r["block_id"], r["arm"]) for r in rows}
    missing = [dict(model=m, block_id=b, arm=a) for m, b, a in itertools.product(plan["models"], plan["block_ids"], ARMS)
               if (m, b, a) not in present]
    expected_rows = len(plan["models"]) * len(plan["block_ids"]) * len(ARMS)
    completed_games = sum(r["complete"] for r in rows)
    unobserved_games = sum(r["weeks"] == 0 for r in rows)
    partial_games = sum(not r["complete"] and r["weeks"] > 0 for r in rows)
    return dict(schema_version=RESULT_SCHEMA, source_kind=plan["source_kind"],
                collection_kind="development" if plan.get("development_only") else plan.get("collection_kind", "heldout"),
                human_observations=0, expected_cluster_arm_rows=expected_rows,
                received_cluster_arm_rows=len(rows), supplied_csv_rows=len(rows),
                csv_record_counts_are_not_response_counts=True,
                complete_game_cluster_arm_rows=completed_games,
                unobserved_game_cluster_arm_rows=unobserved_games,
                partial_game_cluster_arm_rows=partial_games,
                missing_csv_rows=len(missing),
                all_planned_games_complete=completed_games == expected_rows,
                all_primary_endpoint_samples_complete=all(r["planned_sample_complete"] for r in primary),
                all_planned_rows_received=not missing,
                chains_are_independent_observations=False, independent_blocks_caller_confirmed=plan.get("independent_blocks_confirmed", False),
                provenance=input_evidence or {"provenance_status": "caller_assertion_only" if plan.get("provenance_verified") else "not_verified",
                                              "raw_api_lineage_independently_verified_by_this_module": False},
                primary=primary, sweeps=sweeps, contrasts=contrasts, missing_cluster_arm_rows=missing,
                sweep_sizes_not_planned=[n for n in plan["sweep_sizes"] if n > len(plan["block_ids"])],
                family_definition="Five endpoints within each model; twenty across four supplied models. Missing endpoints retain family positions.",
                confidence_intervals="Unadjusted paired-block percentile bootstrap 95% intervals; not simultaneous multiplicity-adjusted intervals.",
                sweep_interpretation="Fixed 10/20/40 prefixes; only the full prospective sample is primary. Do not select a preferred significant prefix.",
                limitations=LIMITATIONS)


def report_markdown(result):
    synthetic = result["source_kind"] == "synthetic_software_control"
    development = result["collection_kind"] == "development"
    lines = ["# Paired Beer Game block analysis", "",
             "1. " + ("Synthetic software controls only; excluded from model-study findings." if synthetic else
                       "Prompt-development model observations only; excluded from heldout hypothesis findings." if development else
                       "Conditional model-simulation analysis; human observations: 0."),
             f"2. CSV records supplied: {result['supplied_csv_rows']}/{result['expected_cluster_arm_rows']}; "
             f"missing CSV rows: {result['missing_csv_rows']}. Completed 24-week games: "
             f"{result['complete_game_cluster_arm_rows']}/{result['expected_cluster_arm_rows']}; "
             f"unobserved games (zero weeks): {result['unobserved_game_cluster_arm_rows']}; "
             f"partial games: {result['partial_game_cluster_arm_rows']}. Planned placeholder rows are not collected model responses.",
             "3. Provenance: " + result["provenance"]["provenance_status"] + "; this analysis does not authenticate raw API lineage.",
             "4. Inference uses matched independent blocks; chains, roles, and weeks inside a batch do not increase the inferential sample size.", "",
             "| Model | Test | Matched blocks | Contrast mean | 95% interval | Two-sided p | Holm 5 | Holm 20 | Direction |", 
             "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- |"]
    def fmt(value):
        return "missing" if value is None else f"{value:.6g}"
    for row in result["primary"]:
        lines.append("| " + " | ".join([row["model"].replace("|", "/"), row["hypothesis"], str(row["n_pairs"]),
                     fmt(row["mean_difference"]), fmt(row["ci95_low"]) + " to " + fmt(row["ci95_high"]),
                     fmt(row["p_two_sided"]), fmt(row["p_holm_within_model_5"]), fmt(row["p_holm_across_models_20"]), row["direction"]]) + " |")
    lines.extend(["", "Missing decisions and endpoints remain missing. Each test's matched-block count reflects only its eligible paired outcomes.",
                  "", "Opposite significant effects are not support for a directional hypothesis. Confidence intervals are unadjusted; significance uses Holm-adjusted two-sided p-values.",
                  "", result["sweep_interpretation"], "", *["- " + x for x in result["limitations"]], ""])
    return "\n".join(lines)
