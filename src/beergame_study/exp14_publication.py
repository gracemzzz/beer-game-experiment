"""Readable publication of the CLOSED student_framing_v3 sample.

This module changes presentation only. The frozen scientific outputs, source
snapshots, inclusion decisions, raw choices and tests are never overwritten.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import statistics as st
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/14_deadline_student_20261026"
ANALYSIS = Path("analysis/student_framing_v3")
REPORTS = Path("reports")
ARCHIVE = Path("archive/before_reporting_cleanup_20261026")
ARMS = {
    "A": "120 s + control reading",
    "B": "8 s + control reading",
    "C": "8 s + causal education",
}
COLORS = {"A": "#24628A", "B": "#C16C25", "C": "#26836D"}
ROLES = ("retailer", "wholesaler", "distributor", "factory")
OUTCOMES = {
    "pipeline_sensitivity": ("Pipeline response", "order cases / outstanding case",
        "For each of 8 matched scenario pairs: (order at low outstanding quantity − order at high outstanding quantity) / (high − low outstanding quantity). Average the 8 slopes equally."),
    "chain_total_cost": ("Total holding + backlog cost", "game cost units / chain",
        "Sum (0.5 × end-of-week inventory + 1 × end-of-week backlog) across 4 roles and 24 weeks."),
    "mean_role_order_variance": ("Weekly order variance", "cases²",
        "For each role, sum the squared deviations of its 24 orders from its own mean, divide by 23, then average the 4 role variances."),
    "mean_role_bullwhip": ("Bullwhip ratio", "dimensionless ratio",
        "Within each chain, divide each role's 24-week sample order variance by the 24-week sample variance of final-consumer demand; average the 4 ratios. Then average chains. Do not divide pooled condition means."),
}
H_METRIC = dict(H1="pipeline_sensitivity", H2="chain_total_cost", H3="pipeline_sensitivity",
                H4a="mean_role_order_variance", H4b="mean_role_bullwhip")
COMPARISONS = {
    "pressure": "8 s + control reading minus 120 s + control reading",
    "education": "8 s + causal education minus 8 s + control reading",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def csv_write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                         for k, v in r.items()} for r in rows)


def number(v, digits=4):
    if v is None:
        return "Not available"
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, (int, float)):
        return f"{v:,.{digits}f}".rstrip("0").rstrip(".") if digits else f"{v:,.0f}"
    return str(v)


def table(headers, rows):
    def cell(x):
        return str(x).replace("|", "/").replace("\n", " ")
    return "\n".join(["| " + " | ".join(map(cell, headers)) + " |",
                      "|" + "|".join("---" for _ in headers) + "|",
                      *["| " + " | ".join(map(cell, row)) + " |" for row in rows]])


def close(a, b):
    if not math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError(f"Published value differs from saved calculation: {a} != {b}")


def load_evidence(experiment):
    """Validate saved sources and build explicit row-level presentation tables."""
    from .exp14_framing import audit_result
    source = experiment / ANALYSIS / "RESULTS.json"
    result = read(source)
    current = read(experiment / ANALYSIS / "CURRENT.json")
    for relative, expected in current["generated_files"].items():
        if relative.startswith(str(ANALYSIS)):
            if sha(experiment / relative) != expected:
                raise ValueError("Changed frozen analysis artifact: " + relative)
    if not result["main"]["inference_enabled"] or result["main"]["complete_blocks"] != 10:
        raise ValueError("This publication requires the closed, fully reviewed ten-block sample")
    closed = read(experiment / "data/student_framing_v3/COLLECTION_CLOSED.json")
    expected_cases = {r["run"]: r for r in closed["results"]}
    evidence = dict(result=result, runs=[], weekly=[], probes=[], quiz=[], timing=[], recall=[], raw_hashes={})
    tables = {}
    for path in (experiment / ANALYSIS / "tables").glob("*.csv"):
        with path.open(encoding="utf-8-sig") as f:
            tables[path.stem] = list(csv.DictReader(f))
    evidence["source_tables"] = tables
    for saved in result["runs"]:
        if saved["stage"] != "main":
            continue
        folder = (experiment / saved["result_path"]).parent
        raw, case = read(folder / "RESULT.json"), read(folder / "CASE.json")
        expected = expected_cases[folder.name]
        for name, key in (("RESULT.json", "result_sha256"), ("CASE.json", "case_sha256")):
            if sha(folder / name) != expected[key]:
                raise ValueError("Closed source changed: " + str(folder / name))
        if not audit_result(raw, case)["valid"]:
            raise ValueError("Physical replay failed")
        metadata = dict(block_id=saved["block_id"], arm=saved["arm"], condition=ARMS[saved["arm"]], case_id=saved["case_id"])
        for path in folder.iterdir():
            if path.is_file() and path.name in ("RESULT.json", "CASE.json", "ADHERENCE_REVIEW.json", "PUBLIC_TRANSCRIPT.jsonl"):
                evidence["raw_hashes"][path.relative_to(experiment).as_posix()] = sha(path)
        for week in raw["weeks"]:
            for i, state in enumerate(week["roles"]):
                row = dict(metadata, week=week["week"], role=ROLES[i], order=week["orders"][i],
                           customer_demand=week["customer_demand"],
                           **{k: state[k] for k in ("demand", "received", "shipped", "inventory", "backlog", "net_inventory", "supply_line", "cost")})
                row.update(holding_cost=.5 * row["inventory"], backlog_cost=row["backlog"],
                           outstanding_after_order=row["supply_line"] + row["order"],
                           shared_inventory=state["shared_inventory"])
                evidence["weekly"].append(row)
        for probe in case["probes"]:
            evidence["probes"].append(dict(metadata, **probe, **case["assay_scoring"][probe["probe_id"]],
                                            order=raw["probe_answers"][probe["probe_id"]]))
        for question in case["comprehension"]:
            key = question["question_id"]
            answer = raw["comprehension_answers"][key]
            evidence["quiz"].append(dict(metadata, **question, **case["comprehension_scoring"][key], answer=answer,
                                          correct=answer == case["comprehension_scoring"][key]["correct_answer"]))
        for decision in raw["decisions"]:
            evidence["timing"].append(dict(metadata, phase=decision["phase"], decision_id=decision["decision_id"],
                                            elapsed_seconds=decision["elapsed_seconds"], deadline_seconds=None))
        # Recall is only taken from a literal public final disclosure. No inference
        # from assigned conditions is used when the disclosure is absent.
        reported = []
        for line in (folder / "PUBLIC_TRANSCRIPT.jsonl").read_text(encoding="utf-8-sig").splitlines():
            msg = json.loads(line)
            if msg.get("type") == "public_message" and msg.get("role") == "assistant":
                text = msg.get("text", "")
                reported.extend(int(v) for v in re.findall(r"fictional_student_seconds[^\d\n]{0,20}(\d+)", text))
        recalled = reported[-1] if reported else None
        evidence["recall"].append(dict(metadata, assigned_seconds=saved["fictional_student_seconds"],
                                        recalled_seconds=recalled, correct=(recalled == saved["fictional_student_seconds"]) if recalled is not None else None))
        evidence["runs"].append(saved)
    if len(evidence["runs"]) != 30 or len(evidence["weekly"]) != 2880 or len(evidence["probes"]) != 960:
        raise ValueError("Unexpected closed sample size")
    indexed = {(r["block_id"], r["arm"]): r for r in evidence["runs"]}
    for endpoint in result["main"]["endpoints"]:
        first, second = endpoint["contrast"].split("-")
        differences = [indexed[(b, first)][endpoint["metric"]] - indexed[(b, second)][endpoint["metric"]]
                       for b in result["main"]["assigned_blocks"]]
        close(st.mean(differences), endpoint["mean_difference"])
    return evidence


def measurements(e):
    """Every substantive measurement, with explicit aggregation and A/B/C values."""
    rows = []
    def add(key, group, label, unit, formula, values, aggregation="Mean across 10 chains", mode="mean"):
        row = dict(variable=key, category=group, label=label, units=unit, calculation=formula, aggregation=aggregation)
        for arm in ARMS:
            v = list(values(arm))
            row[arm + "_n"] = len(v)
            row[arm + "_value"] = (sum(v) if mode == "sum" else min(v) if mode == "min" else max(v) if mode == "max" else st.mean(v)) if v else None
            row[arm + "_sd"] = st.stdev(v) if len(v) > 1 else None
            row[arm + "_minimum"] = min(v) if v else None
            row[arm + "_maximum"] = max(v) if v else None
        rows.append(row)
    def run_values(key):
        return lambda arm: [r[key] for r in e["runs"] if r["arm"] == arm and r.get(key) is not None]
    def observed(source, key, predicate=lambda r: True):
        return lambda arm: [r[key] for r in e[source] if r["arm"] == arm and predicate(r) and r.get(key) is not None]
    for key, (label, unit, formula) in OUTCOMES.items():
        add(key, "Primary dependent variables", label, unit, formula, run_values(key))
    for key, label, formula in (
        ("complete_holding_cost", "Inventory-holding cost", "Sum 0.5 × inventory across 4 roles and 24 weeks, per chain."),
        ("complete_backlog_cost", "Backlog cost", "Sum 1 × unfilled demand across 4 roles and 24 weeks, per chain."),
    ):
        add(key, "Cost components", label, "game cost units / chain", formula, run_values(key))
    weekly_definitions = {
        "order": ("New replenishment order", "Literal integer order chosen by the model for a role in a week."),
        "demand": ("Incoming demand at a role", "Customer demand at retailer; downstream orders arriving at each upstream role."),
        "received": ("Replenishment received", "Cases delivered to this role at the start of the current week."),
        "shipped": ("Cases shipped to downstream customer", "Cases sent to satisfy current or previously unfilled demand during the week."),
        "inventory": ("End-of-week physical inventory", "Stock remaining after receipts and shipments, before the new order."),
        "backlog": ("End-of-week unfilled demand", "Demand still waiting to be supplied after current shipments."),
        "net_inventory": ("Net inventory", "Physical inventory minus backlog, for the same role and week."),
        "supply_line": ("Outstanding replenishment before new order", "Previously ordered cases not yet received; does not include this week's new order."),
        "outstanding_after_order": ("Outstanding replenishment after new order", "Outstanding before order + current week's new order."),
        "cost": ("Weekly role cost", "0.5 × remaining inventory + 1 × backlog in this role/week."),
    }
    for key, (label, formula) in weekly_definitions.items():
        add(key, "Observed weekly game variables", label, "game cost units / role-week" if key == "cost" else "cases / role-week",
            formula, observed("weekly", key), "Mean across 960 role-week observations per condition")
    add("customer_demand", "Observed weekly game variables", "Final-consumer demand", "cases / week",
        "Exogenous customer demand, counted once per chain/week (not four times).",
        observed("weekly", "customer_demand", lambda r: r["role"] == "retailer"), "Mean across 240 chain-weeks per condition")
    add("customer_demand_sample_variance", "Observed weekly game variables", "Final-consumer demand variance", "cases²",
        "Sample variance of the 24 customer-demand values (denominator 23); the denominator used for bullwhip.", run_values("customer_demand_sample_variance"))
    for key, label, mode in (("order", "Smallest observed game order", "min"), ("order", "Largest observed game order", "max")):
        add("game_order_" + mode, "Ordering diagnostics", label, "cases", "Minimum/maximum across all 960 orders in the condition.",
            observed("weekly", key), "Overall " + mode + " across 960 orders", mode)
    add("game_zero_order_fraction", "Ordering diagnostics", "Fraction of game orders equal to zero", "proportion (0–1)",
        "Count zero orders / 96 orders in a chain; average chains. Also equals pooled count / 960 because all chains are complete.", run_values("game_zero_order_fraction"))
    for key, label in (("inventory", "Final physical inventory"), ("backlog", "Final unfilled demand"), ("outstanding_after_order", "Final outstanding replenishment")):
        add("final_" + key, "End of week 24", label, "cases / chain", "Sum this quantity across the 4 roles at week 24; then average chains.",
            lambda arm, key=key: [sum(w[key] for w in e["weekly"] if w["arm"] == arm and w["block_id"] == b and w["week"] == 24)
                                 for b in e["result"]["main"]["assigned_blocks"]])
    add("backlog_sensitivity", "Probe diagnostics", "Response to unfilled demand", "order cases / backlog case",
        "Mean of 8 separate matched-pair slopes: (order at high backlog − order at low backlog) / increase in backlog.", run_values("backlog_sensitivity"))
    for key, label, mode in (("probe_zero_order_fraction", "Fraction of probe answers equal to zero", "mean"),
                             ("probe_order_min", "Smallest probe order", "min"), ("probe_order_max", "Largest probe order", "max")):
        add(key, "Probe diagnostics", label, "proportion (0–1)" if mode == "mean" else "cases",
            "Zero probe orders / 32 per chain, averaged across chains." if mode == "mean" else "Overall minimum/maximum across 320 probe answers.",
            run_values(key), "Mean across 10 chains" if mode == "mean" else "Overall " + mode + " across 320 answers", mode)
    add("probe_all_observed_orders_equal", "Probe diagnostics", "Chains with all 32 probe answers identical", "chains",
        "Count chains whose 32 observed probe answers all have the same value.", run_values("probe_all_observed_orders_equal"), "Count across 10 chains", "sum")
    # Full diagnostic slope and regression quantities, including the unused
    # alternative weighting, remain labeled as diagnostics rather than endpoints.
    for dimension in ("pipeline", "backlog"):
        for key, label, formula in (
            ("min_response_slope", "Smallest pair response", "Minimum of the 8 pair slopes in each chain; average chain minima."),
            ("max_response_slope", "Largest pair response", "Maximum of the 8 pair slopes in each chain; average chain maxima."),
            ("sample_sd_response_slope", "SD across pair responses", "Sample SD of the 8 pair slopes in each chain (denominator 7); average chain SDs."),
            ("zero_slope_fraction", "Fraction of pairs with no response", "Number of exactly zero slopes / 8 pairs in a chain; average chains."),
            ("pair_fixed_effect_response_slope", "Regression response (diagnostic)", "Pair-intercept regression; equivalent to average pair slopes weighted by squared quantity changes. This is NOT the equal-weight primary endpoint."),
        ):
            selected = [r for r in e["source_tables"]["probe_diagnostics"] if r["stage"] == "main" and r["role"] == "all" and r["assay_dimension"] == dimension]
            add(dimension + "_" + key, "Probe diagnostics", dimension.title() + ": " + label,
                "proportion (0–1)" if key == "zero_slope_fraction" else "order cases / changed case", formula,
                lambda arm, selected=selected, key=key: [float(r[key]) for r in selected if r["arm"] == arm])
        selected = [r for r in e["source_tables"]["probe_regression_residuals"] if r["stage"] == "main" and r["assay_dimension"] == dimension]
        for key, label in (("pair_fixed_effect_intercept", "Regression intercept"), ("fitted_order", "Regression fitted order"), ("residual", "Regression residual")):
            formula = {"pair_fixed_effect_intercept": "Within each pair: mean order − raw common regression slope × mean quantity.",
                       "fitted_order": "Pair intercept + raw common regression slope × displayed quantity.",
                       "residual": "Actual probe order − regression fitted order. Mean residual can be zero by construction; inspect individual values."}[key]
            add(dimension + "_" + key, "Probe regression diagnostics", dimension.title() + ": " + label, "order cases", formula,
                lambda arm, selected=selected, key=key: [float(r[key]) for r in selected if r["arm"] == arm], "Mean across 160 probe observations per condition")
    for key, label, unit, formula in (
        ("knowledge_correct", "Correct comprehension answers", "answers / 4", "Score against the frozen four-item answer key after gameplay and probes."),
        ("knowledge_fraction_correct", "Comprehension accuracy", "proportion (0–1)", "Correct answers / answered questions; every case answered all four."),
    ):
        add(key, "Comprehension and recall", label, unit, formula, run_values(key))
    add("recall_correct", "Comprehension and recall", "Correctly recalled fictional allowance", "contexts",
        "Count literal public disclosures matching the assigned 120 or 8 seconds; absence is missing, never imputed.",
        observed("recall", "correct"), "Count of correct observed disclosures; N reports disclosures found", "sum")
    for phase, label in (("game", "Weekly order packet (4 choices)"), ("probes", "Probe packet (4 choices)"), ("comprehension", "Quiz packet (4 answers)")):
        for suffix, name, formula in (("median_seconds", "mean of per-context median elapsed times", "Median observed packet latency in each context, then mean across 10 contexts."),
                                       ("p90_seconds", "mean of per-context 90th percentiles", "Nearest-rank 90th percentile in each context (ceil(0.9 × count)), then mean across contexts."),
                                       ("max_seconds", "largest observed elapsed time", "Maximum packet latency across all 10 contexts.")):
            add(phase + "_" + suffix, "Observed response timing", label + ": " + name, "seconds / packet", formula + " Includes transport, scheduling and output; not measured thinking time.",
                run_values(phase + "_" + suffix), "Maximum across contexts" if suffix == "max_seconds" else "Mean across 10 context summaries", "max" if suffix == "max_seconds" else "mean")
    for key, label, formula in (
        ("completed_weeks", "Completed game weeks", "Number of completed weeks per chain."),
        ("observed_probe_orders", "Actual probe answers", "Count literal answers to the 32 fixed hypothetical states."),
        ("complete_pipeline_pairs", "Complete pipeline pairs", "Both orders present in each of the 8 planned pipeline pairs."),
        ("missing_pipeline_pairs", "Missing pipeline pairs", "Planned pipeline pairs missing at least one answer."),
        ("complete_backlog_pairs", "Complete backlog pairs", "Both orders present in each of the 8 backlog pairs."),
        ("knowledge_answered", "Answered quiz questions", "Number of submitted quiz answers per chain context."),
    ):
        add(key, "Completeness and procedure", label, "count / context", formula, run_values(key))
    for phase, label in (("game", "Game"), ("probes", "Probe"), ("comprehension", "Quiz")):
        for suffix, wording in (("opened", "display packets opened"), ("accepted", "packets accepted"), ("accepted_per_opened", "accepted / opened")):
            key = phase + "_" + suffix
            add(key, "Completeness and procedure", label + " " + wording, "fraction" if suffix == "accepted_per_opened" else "packets / context",
                "Count accepted or opened packets in this phase; acceptance fraction = accepted / opened. Packets contain multiple choices.", run_values(key))
    for key, label in (("timed_displays_opened", "Displays with enforced deadlines"), ("timed_displays_accepted_on_time", "Timed displays accepted on time"),
                       ("late_submission_events", "Late events recorded"), ("rejected_submission_events", "Rejected submissions")):
        add(key, "Completeness and procedure", label, "events", "Sum recorded events across 10 contexts. With no timer, zero late events does not demonstrate that decisions met the fictional allowance.",
            run_values(key), "Total across 10 contexts", "sum")
    add("accepted_on_time_per_timed_display", "Completeness and procedure", "Fraction meeting an enforced deadline", "fraction",
        "Timed accepted displays / timed displays. Undefined because there were zero timed displays.", run_values("accepted_on_time_per_timed_display"))
    for key, label in (("replay_valid", "Physical replay passed"), ("complete", "Full task completed"), ("complete_primary_endpoints", "All primary outcomes available"),
                       ("all_scored_choices_are_actual_model_responses", "All choices supplied by the model")):
        add(key, "Completeness and procedure", label, "contexts / 10", "Count contexts with this verified flag true.", run_values(key), "Count across 10 contexts", "sum")
    return rows


def outcome_means(e):
    return {a: {k: st.mean(r[k] for r in e["runs"] if r["arm"] == a) for k in OUTCOMES} for a in ARMS}


def comparison(endpoint):
    return COMPARISONS["pressure" if endpoint["hypothesis"] in ("H1", "H2") else "education"]


def prefixes(e):
    rows = []
    for n in range(1, 11):
        selected = [dict(r) for r in e["result"]["main"]["prefixes"] if r["prefix_size"] == n]
        bound = 0.
        for i in sorted(range(5), key=lambda i: selected[i]["p_two_sided"] if selected[i]["p_two_sided"] is not None else 2):
            selected[i]["p_holm_family_5_at_prefix"] = None
        if n > 1:
            for rank, i in enumerate(sorted(range(5), key=lambda i: selected[i]["p_two_sided"])):
                bound = max(bound, min(1., (5 - rank) * selected[i]["p_two_sided"]))
                selected[i]["p_holm_family_5_at_prefix"] = bound
        for r in selected:
            r.update(comparison=comparison(r), dependent_variable=OUTCOMES[r["metric"]][0], units=OUTCOMES[r["metric"]][1],
                     chains_per_condition=n, total_chain_contexts=3*n)
        rows.extend(selected)
    return rows


def make_figures(folder, e, prefix_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.ticker import MaxNLocator
    import textwrap
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "pdf.fonttype": 42})
    folder.mkdir(parents=True, exist_ok=True)
    figures, catalog = [], []
    ends = e["result"]["main"]["endpoints"]
    means = outcome_means(e)
    def keep(stem, fig, title, caption, calculation, data):
        figures.append((stem, fig))
        catalog.append(dict(file=stem, title=title, caption=caption, calculation=calculation, data=data,
                            axes=[dict(x_label=ax.get_xlabel(), y_label=ax.get_ylabel(), title=ax.get_title())
                                  for ax in fig.axes if ax.axison]))
    def heading(fig, title, subtitle):
        fig.suptitle(title, fontsize=21, fontweight="bold", x=.055, ha="left", y=.98)
        fig.text(.055, .925, subtitle, fontsize=11, color="#455665")
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    heading(fig, "What was measured in each condition?", "Main sample: 10 chains per condition; one fresh context per four-role chain; 24 game weeks.")
    for ax, (key, (name, unit, formula)) in zip(axes.flat, OUTCOMES.items()):
        for i, arm in enumerate(ARMS):
            values = [r[key] for r in e["runs"] if r["arm"] == arm]
            ax.scatter([i + (j - 4.5)*.018 for j in range(10)], values, color=COLORS[arm], s=25, alpha=.5)
            ax.scatter([i], [means[arm][key]], marker="D", color=COLORS[arm], s=90, edgecolor="white", zorder=4)
            ax.annotate(number(means[arm][key], 4 if key == "pipeline_sensitivity" else 2), (i, means[arm][key]),
                        xytext=(0, 12), textcoords="offset points", ha="center", fontsize=13, fontweight="bold")
        ax.set_title(name, loc="left", fontsize=15, fontweight="bold")
        ax.set_ylabel(name + "\n(" + unit + ")", fontsize=10)
        ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["120 seconds\nControl reading", "8 seconds\nControl reading", "8 seconds\nCausal education"], fontsize=11)
        ax.set_xlabel("Assigned fictional time allowance and reading", fontsize=10)
        ax.set_xlim(-.4, 2.4); ax.set_ylim(bottom=0); ax.margins(y=.23); ax.grid(axis="y", alpha=.14)
    fig.subplots_adjust(left=.08, right=.97, top=.85, bottom=.20, hspace=.73, wspace=.28)
    fig.text(.055, .12, "Pipeline response = average of 8 matched scenario slopes: order decrease / increase in outstanding cases.\n"
             "Total cost = sum of (0.5 × inventory + backlog) over 4 roles × 24 weeks.\n"
             "Order variance = mean of 4 within-role sample variances (24 weeks, denominator 23).\n"
             "Bullwhip = mean of role order variance / own chain's final-consumer demand variance, then mean across chains.", fontsize=10, va="top", linespacing=1.5)
    fig.text(.055, .025, "Small dots: individual chains. Diamonds and numbers: condition means. Fictional seconds; actual model runtime unrestricted.", fontsize=10, color="#455665")
    keep("01_CONDITION_VALUES", fig, "Measured outcome values by condition",
         "X: assigned fictional allowance and reading. Y: named outcome with units. Ten small dots per condition are chain values; diamonds and labels are arithmetic condition means. The plot shows levels, not treatment differences.",
         "Four unique dependent variables support five planned tests; pipeline response is used in both H1 and H3.", "CONDITION_OUTCOMES.csv")
    for kind, selected, stem, title in (
        ("pressure", ends[:2], "02_PRESSURE_COMPARISON", "Effect of the fictional time allowance"),
        ("education", ends[2:], "03_EDUCATION_COMPARISON", "Effect of causal education under the 8-second framing"),
    ):
        fig, axes = plt.subplots(1, len(selected), figsize=(16, 8))
        heading(fig, title, "Every plotted difference = " + COMPARISONS[kind] + ".")
        formulas = []
        for ax, endpoint in zip(axes, selected):
            key = endpoint["metric"]
            name, unit, formula = OUTCOMES[key]
            values = [r["difference"] for r in e["result"]["main"]["contrasts"] if r["hypothesis"] == endpoint["hypothesis"]]
            ax.scatter(range(1, 11), values, s=45, color="#337497", label="One matched block")
            ax.errorbar([12], [endpoint["mean_difference"]],
                        yerr=[[endpoint["mean_difference"] - endpoint["ci95_low"]], [endpoint["ci95_high"] - endpoint["mean_difference"]]],
                        fmt="D", color="#142F42", markersize=8, capsize=5, linewidth=2)
            ax.axhline(0, color="#77848A", linestyle="--", linewidth=1)
            ax.set_xticks([1, 3, 5, 7, 9, 10, 12]); ax.set_xticklabels(["1", "3", "5", "7", "9", "10", "Mean"])
            ax.set_xlabel("Matched chain block (1–10) and overall mean", fontsize=10)
            ax.set_ylabel("Difference in " + name.lower() + "\n(" + unit + ")", fontsize=10)
            ax.set_title(endpoint["hypothesis"] + " · " + name, fontsize=13, fontweight="bold")
            ax.text(.03, .98, "Mean difference " + f"{endpoint['mean_difference']:+.4f}" + "\nHolm-adjusted p = " + number(endpoint["p_holm_family_5"], 6),
                    transform=ax.transAxes, va="top", fontsize=10, bbox=dict(facecolor="white", alpha=.9, edgecolor="none"))
            lo, hi = ax.get_ylim(); span = max(hi-lo, .01); ax.set_ylim(lo-.08*span, hi+.32*span)
            ax.grid(axis="y", alpha=.12)
            formulas.append(endpoint["hypothesis"] + ": " + formula)
        fig.subplots_adjust(left=.08, right=.97, top=.82, bottom=.31, wspace=.40)
        wrapped = "\n".join(textwrap.fill(t, width=165) for t in formulas)
        fig.text(.055, .22, wrapped, fontsize=9.5, va="top", linespacing=1.45)
        fig.text(.055, .035, "Zero = equal outcomes. Positive = the first named condition is higher. Negative = it is lower.\n"
                 "Diamond: mean of 10 paired differences. Bar: pointwise 95% paired-block bootstrap interval. Fictional framing; no model timer.", fontsize=10, color="#455665")
        keep(stem, fig, title, "X: ten matched blocks and the overall mean. Y: difference in the named dependent variable, in its stated units. "
             "The first named condition minus the second is used in every panel. The zero line means equal outcomes; bars are pointwise 95% paired-block bootstrap intervals.",
             COMPARISONS[kind] + ". " + " ".join(formulas), "HYPOTHESIS_COMPARISONS.csv")
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    heading(fig, "How the estimated differences change as matched blocks are included", "Each point uses the first n blocks in the fixed planned order. These are nested subsets of the same completed sample.")
    for ax, endpoint in zip(axes.flat, ends):
        own = [r for r in prefix_rows if r["hypothesis"] == endpoint["hypothesis"]]
        key = endpoint["metric"]; name, unit, _ = OUTCOMES[key]
        ax.plot([r["prefix_size"] for r in own], [r["mean_difference"] for r in own], "o-", color="#24628A", linewidth=2, markersize=5)
        ax.axhline(0, color="#8A959E", ls="--", linewidth=1)
        ax.set_title(endpoint["hypothesis"] + " · " + name + "\n" + ("8 s control − 120 s control" if endpoint["hypothesis"] in ("H1", "H2") else "8 s education − 8 s control"), fontsize=12, fontweight="bold")
        ax.set_ylabel("Mean paired difference\n(" + unit + ")", fontsize=10)
        ax.set_xlabel("Matched blocks included (n)\n= n chains per condition; 3n contexts total", fontsize=10)
        ax.set_xticks([1, 2, 4, 6, 8, 10]); ax.set_xlim(.7, 10.3); ax.grid(axis="y", alpha=.13)
    axes.flat[-1].axis("off")
    axes.flat[-1].text(.02, .95, "How to read this figure\n\n1. Name the outcome in the panel title.\n2. Subtract the two named conditions.\n3. Average differences for the first n blocks.\n\nThe final planned sample is n = 10.\nEach block contains 3 separate chain contexts.\nMore weeks or roles do not increase n.\n\nThis is a description of completed data,\nnot a rule for choosing a sample size.", va="top", fontsize=12, linespacing=1.55)
    fig.subplots_adjust(left=.08, right=.97, top=.85, bottom=.16, hspace=.60, wspace=.44)
    fig.text(.055, .06, "H1/H3: mean of 8 order-decrease / outstanding-increase probe slopes. H2: 24-week total holding + backlog cost.\n"
             "H4a: mean within-role sample order variance. H4b: mean role order variance / final-consumer demand variance.\n"
             "All panels report a difference between conditions, not an absolute performance level. Fictional student time framing.", fontsize=10, linespacing=1.5)
    keep("04_SAMPLE_SIZE_EFFECTS", fig, "Observed differences by fixed block count",
         "X: n matched blocks, equivalent to n chains in each of the three conditions and 3n separate contexts in total. Y: arithmetic mean of the first n paired differences, with outcome units. Every panel names the subtraction. N=10 is the primary sample.",
         "For each endpoint and n, mean_difference(n) = sum of block differences 1 through n / n. Individual chain metrics follow the same fixed formulas as the main results.", "SAMPLE_SIZE_VALUES.csv")
    fig, ax = plt.subplots(figsize=(14, 8))
    heading(fig, "Statistical evidence across the fixed sample prefixes", "The five adjusted p-value curves coincide in these data; one line represents H1, H2, H3, H4a and H4b.")
    all_curves = [[r["p_holm_family_5_at_prefix"] for r in prefix_rows if r["hypothesis"] == h] for h in H_METRIC]
    if not all(c == all_curves[0] for c in all_curves):
        raise ValueError("Combined p-value display assumes identical curves; draw separate lines for changed evidence")
    ax.plot(range(2, 11), all_curves[0][1:], "o-", color="#24628A", lw=2, label="All five hypotheses (overlapping curves)")
    ax.axhline(.05, color="#A56524", ls="--", label="0.05 reference threshold")
    ax.annotate("Final n = 10\nAdjusted p = 0.009766", (10, all_curves[0][-1]), xytext=(.98, .52), textcoords="axes fraction", ha="right", fontsize=12,
                arrowprops=dict(arrowstyle="-", color="#77848A"))
    ax.set_xlabel("Matched blocks included (n): n chains per condition, 3n separate contexts total", fontsize=12)
    ax.set_ylabel("Holm-adjusted two-sided p-value\n(logarithmic scale; five tests at each n)", fontsize=12)
    ax.set_yscale("log"); ax.set_ylim(.005, 1.4); ax.set_xticks(range(1, 11)); ax.set_xlim(.7, 10.3)
    ax.grid(axis="y", alpha=.16); ax.legend(loc="upper right", fontsize=11)
    fig.subplots_adjust(left=.12, right=.95, top=.83, bottom=.30)
    fig.text(.055, .17, "Calculation: exact paired sign-flip test for each outcome, followed by Holm correction across five tests at each prefix.\n"
             "Each outcome has all block differences in its predicted direction, so the p-value curves are identical.\n"
             "n = 1: p unavailable. n = 10: fixed primary analysis. Earlier crossings are descriptive and were not a stopping rule.", fontsize=11, linespacing=1.5, va="top")
    keep("05_SAMPLE_SIZE_PVALUES", fig, "Adjusted p-values by fixed block count",
         "X: n matched blocks (= n chains per condition; 3n contexts total). Y: Holm-adjusted two-sided p-value on a log scale. One line represents all five coincident endpoint curves. The dashed line is 0.05, not a target used to select the sample.",
         "Exact paired sign-flip p-values for the first n block differences, adjusted together across the five preplanned endpoints. n=1 has no test; n=10 is primary.", "SAMPLE_SIZE_VALUES.csv")
    with PdfPages(folder / "ALL_FIGURES.pdf") as pdf:
        for stem, fig in figures:
            for ext in ("png", "pdf", "svg"):
                fig.savefig(folder / (stem + "." + ext), dpi=180, facecolor="white")
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)
    write_json(folder / "FIGURE_DEFINITIONS.json", catalog)
    lines = ["# Experiment 14: current figures", "", "All figures use the completed student_framing_v3 main sample. **120 s and 8 s describe fictional students; actual model runtime was unrestricted.**", "",
             "[Full report](../REPORT.md) · [Report PDF](../REPORT.pdf) · [All figures in one PDF](ALL_FIGURES.pdf) · [Tables and exact values](../tables/README.md)", ""]
    for item in catalog:
        stem = item["file"]
        lines.extend(["## " + item["title"], "", f"[PNG]({stem}.png) · [SVG]({stem}.svg) · [PDF]({stem}.pdf) · [Exact numbers](../tables/{item['data']})", "",
                      item["caption"], "", "**Calculation:** " + item["calculation"], ""])
    (folder / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return catalog


def build_tables(folder, e, measures, prefix_rows):
    folder.mkdir(parents=True, exist_ok=True)
    means = outcome_means(e)
    condition_rows = []
    for arm in ARMS:
        for key, (name, unit, formula) in OUTCOMES.items():
            values = [r[key] for r in e["runs"] if r["arm"] == arm]
            condition_rows.append(dict(arm=arm, condition=ARMS[arm], variable=key, dependent_variable=name,
                                       units=unit, mean=st.mean(values), sd_across_chains=st.stdev(values),
                                       minimum=min(values), maximum=max(values), n_chains=10, calculation=formula))
    comparisons = []
    for r in e["result"]["main"]["endpoints"]:
        first, second = r["contrast"].split("-")
        comparisons.append(dict(r, comparison=comparison(r), first_condition=ARMS[first], second_condition=ARMS[second],
                                first_condition_mean=means[first][r["metric"]], second_condition_mean=means[second][r["metric"]],
                                changed_independent_variable="Fictional time allowance: 120 to 8 seconds" if first == "B" else "Reading: control to causal education",
                                held_fixed="Control reading" if first == "B" else "Fictional time allowance: 8 seconds",
                                dependent_variable=OUTCOMES[r["metric"]][0]))
    cases = [{k: v for k, v in r.items() if k not in ("source_hashes", "adherence")} for r in e["runs"]]
    for row in cases:
        row["condition"] = ARMS[row["arm"]]
    probe_pairs = []
    for row in e["source_tables"]["probe_pairs"]:
        if row["stage"] == "main":
            probe_pairs.append(dict(row, condition=ARMS[row["arm"]]))
    role_rows = [dict(r, condition=ARMS[r["arm"]]) for r in e["source_tables"]["role_outcomes"] if r["stage"] == "main"]
    datasets = {"CONDITION_OUTCOMES": condition_rows, "ALL_MEASURED_VALUES": measures,
                "HYPOTHESIS_COMPARISONS": comparisons, "SAMPLE_SIZE_VALUES": prefix_rows,
                "CHAIN_VALUES": cases, "WEEKLY_ROLE_VALUES": e["weekly"], "ROLE_VALUES": role_rows,
                "PROBE_ANSWERS": e["probes"], "PROBE_PAIRS": probe_pairs,
                "QUIZ_ANSWERS": e["quiz"], "RESPONSE_TIMES": e["timing"], "TIME_ALLOWANCE_RECALL": e["recall"]}
    for name, rows in datasets.items():
        csv_write(folder / (name + ".csv"), rows)
    dictionary = [dict(variable=r["variable"], category=r["category"], definition=r["label"], units=r["units"],
                       calculation=r["calculation"], aggregation=r["aggregation"], values_file="ALL_MEASURED_VALUES.csv") for r in measures]
    dictionary.extend([
        dict(variable="fictional_student_seconds", category="Independent variable", definition="Assigned fictional classroom time allowance", units="seconds", calculation="A=120; B=8; C=8. Stated in the prompt; no timer enforced.", aggregation="Constant within condition", values_file="CHAIN_VALUES.csv"),
        dict(variable="assigned_reading", category="Independent variable", definition="Assigned learning material", units="category", calculation="A/B: 170-word control reading. C: 170-word causal supply-chain education.", aggregation="Constant within condition", values_file="../REPORT.md"),
        dict(variable="probe_quantity", category="Within-pair assay manipulation", definition="Outstanding replenishment or backlog shown in a probe", units="cases", calculation="The low/high quantities in PROBE_PAIRS.csv; all other displayed fields fixed, except proportionally scaled pipeline arrivals when outstanding quantity changes.", aggregation="16 specified pairs; 8 per dimension", values_file="PROBE_ANSWERS.csv"),
        dict(variable="probe_order", category="Raw dependent variable", definition="Literal model order in a hypothetical scenario", units="cases", calculation="Actual submitted nonnegative integer. Pipeline/backlog response is derived from paired orders.", aggregation="320 values per condition", values_file="PROBE_ANSWERS.csv"),
        dict(variable="pipeline_arrivals", category="Probe input", definition="Known hypothetical delivery schedule", units="cases at each of next 3 arrivals", calculation="Three-element array sums to outstanding quantity. Retains proportional timing within each pipeline pair.", aggregation="Fixed displayed values; no averaging of schedules", values_file="PROBE_ANSWERS.csv"),
        dict(variable="recent_demand_history", category="Probe input", definition="Displayed previous demand observations", units="cases", calculation="Exact ordered history array in each scenario; held fixed within a pair.", aggregation="Fixed displayed values", values_file="PROBE_ANSWERS.csv"),
        dict(variable="shared_inventory", category="Information display", definition="All four roles' physical inventories", units="cases by role", calculation="Game: same four inventory values already in WEEKLY_ROLE_VALUES for that week/chain. Probes: exact scenario dictionary.", aggregation="Displayed data; not an additional independent outcome", values_file="WEEKLY_ROLE_VALUES.csv and PROBE_ANSWERS.csv"),
    ])
    csv_write(folder / "VARIABLE_DICTIONARY.csv", dictionary)
    # Include every underlying column, distinguishing identifiers and diagnostics
    # from measured dependent variables. Original technical exports stay intact.
    field_rows = []
    field_definitions = {
        "stage": "Collection phase: development or main. Only main enters these summaries.", "case_id": "Unique saved context identifier.",
        "block_id": "Matched demand/profile block identifier; one A, one B and one C context share a block.",
        "arm": "Condition code: A=120 s control; B=8 s control; C=8 s education.", "condition": "Full condition name.",
        "role": "Retailer, wholesaler, distributor or factory; repeated within chain.", "week": "Game decision period, 1 through 24.",
        "probe_id": "Identifier of a fixed displayed hypothetical scenario.", "pair_id": "Identifier of two matched hypothetical states.",
        "assay_dimension": "Quantity varied within a probe pair: pipeline or backlog.", "question_id": "Post-task comprehension question identifier.",
        "answer": "Literal quiz answer chosen by model.", "correct_answer": "Frozen quiz key.", "correct": "Whether literal response matches the frozen key or assigned recall value.",
        "reason": "Explanation in the private scoring key; not model reasoning.", "phase": "Packet type: game, probes, or comprehension.",
        "decision_id": "Immutable displayed packet identifier.", "accepted": "Whether a submitted packet was accepted.",
        "elapsed_seconds": "Observed display-open to complete-payload reception latency, including service/transport; not thinking time.",
        "deadline_seconds": "Actual enforced deadline; null throughout this study.", "on_time": "Actual deadline comparison; undefined because there is no deadline.",
        "rejection_reason": "Technical rejection explanation if any.", "contrast": "Legacy shorthand: B-A = 8 s control minus 120 s control; C-B = 8 s education minus 8 s control.",
        "treated_value": "Outcome in first named condition of this block's subtraction.", "control_value": "Outcome in second named condition of this block's subtraction.",
        "difference": "First named condition's value minus second named condition's value in one matched block.",
        "mean_difference": "Arithmetic mean of the included matched block differences.", "n_pairs": "Number of matched block differences; not roles, questions or weeks.",
        "ci95_low": "Lower pointwise 95% paired-block bootstrap limit.", "ci95_high": "Upper pointwise 95% paired-block bootstrap limit.",
        "p_two_sided": "Exact paired sign-flip two-sided p-value; not a probability that the hypothesis is true.",
        "p_holm_family_5": "P-value adjusted across five primary tests by Holm's method.",
        "p_holm_family_5_at_prefix": "Holm adjustment across the same five tests at a fixed descriptive prefix.",
        "prefix_size": "First n planned matched blocks included in a descriptive prefix.",
        "response_slope": "Pipeline: (low-quantity order minus high-quantity order)/quantity increase. Backlog: reverse order subtraction / quantity increase.",
        "low_order": "Actual model order at the lower manipulated quantity.", "high_order": "Actual model order at the higher manipulated quantity.",
        "low_quantity": "Lower outstanding or backlog quantity in the pair.", "high_quantity": "Higher outstanding or backlog quantity in the pair.",
        "delta_quantity": "High quantity minus low quantity.", "timing_profile": "Proportions of outstanding goods arriving at successive hypothetical deliveries.",
        "quantity": "Manipulated outstanding/backlog quantity for a regression observation.", "order": "Actual model order; game or probe as specified by the source table.",
        "pair_fixed_effect_intercept": "Pair's mean order minus raw regression slope times its mean quantity.",
        "fitted_order": "Order predicted by the diagnostic pair-intercept regression.", "residual": "Actual order minus fitted order.",
        "pair_fixed_effect_response_slope": "Quantity-change-squared weighted slope diagnostic; not the equal-pair primary endpoint.",
        "weekly_sample_order_variance": "Sample variance of a role's 24 orders, denominator 23.", "bullwhip": "This role's order variance divided by its chain's final-consumer demand variance.",
        "final_observed_inventory": "This role's inventory after week-24 receipts/shipments.", "final_observed_backlog": "This role's unfilled demand after week-24 shipments.",
        "final_observed_outstanding_after_order": "This role's outstanding replenishment including its final new order.",
        "actual_model_orders": "Four literal weekly orders in retailer/wholesaler/distributor/factory order.",
        "observed_week_cost": "Sum of 4 role holding/backlog costs in this chain-week.",
        "actual_model": "Provider-authenticated model label is UNVERIFIED in these local records.",
        "actual_effort": "Provider-authenticated effort is UNVERIFIED; requested effort is xhigh.",
        "requested_model": "Requested client model gpt-6-astra, held constant.", "requested_effort": "Requested client effort xhigh, held constant.",
        "model_runtime_limit_seconds": "No actual response limit in any condition (null).",
        "completed_prefix_cost": "Observed holding/backlog cost through available weeks; equals total cost because all cases completed 24 weeks.",
        "observed_holding_cost": "Observed holding cost; equals complete_holding_cost in this complete sample.",
        "observed_backlog_cost": "Observed backlog cost; equals complete_backlog_cost in this complete sample.",
    }
    measures_by_key = {r["variable"]: r for r in dictionary}
    metadata_fields = {"result_path", "run_directory", "result_sha256", "replay_error", "analysis_error", "stopped", "terminal_reason", "planned_weeks",
                       "prompt_version", "profile_ids", "case_sha256", "seed", "source_hashes", "adherence", "missing", "interpretation", "both_reviews_passed",
                       "metric", "units", "hypothesis", "predicted_sign", "direction", "test", "randomization_draws", "complete_prefix", "full_main_gate_passed",
                       "low_probe_id", "high_probe_id", "complete", "observed_weeks", "complete_24_weeks", "planned_pairs", "complete_pairs", "observed_orders",
                       "diagnostic", "knowledge_items", "mean_response_slope", "min_response_slope", "max_response_slope", "sample_sd_response_slope", "zero_slope_fraction",
                       "zero_order_fraction", "order_min", "order_max", "customer_demand"}
    generic = {
        "mean_response_slope": "Mean of available pair slopes for the stated dimension and role (or all roles).",
        "min_response_slope": "Minimum pair slope in the stated role/dimension.", "max_response_slope": "Maximum pair slope in the stated role/dimension.",
        "sample_sd_response_slope": "Sample SD across pair slopes in the stated role/dimension.", "zero_slope_fraction": "Fraction of pair slopes exactly zero.",
        "zero_order_fraction": "Fraction of actual orders exactly zero within the stated role or assay group.",
        "order_min": "Smallest actual order within the stated role/group.", "order_max": "Largest actual order within the stated role/group.",
        "customer_demand": "External final-consumer demand for this chain-week; same path across matched conditions.",
        "complete_pairs": "Observed complete pairs in the indicated assay role/group.", "planned_pairs": "Fixed intended pairs: two per role or eight across roles.",
        "observed_orders": "Number of actual probe choices in the indicated group.", "knowledge_items": "Four planned quiz questions per context.",
    }
    field_definitions.update(generic)
    for name, values in e["source_tables"].items():
        for field in list(values[0]) if values else []:
            if field in measures_by_key:
                m = measures_by_key[field]; definition = m["definition"] + ": " + m["calculation"]; kind = m["category"]
            elif field in field_definitions:
                definition = field_definitions[field]; kind = "Raw observation, diagnostic, or identifier (see definition)"
            elif field in metadata_fields:
                definition = "Technical metadata: " + field.replace("_", " ") + ". Retained verbatim in the source export; not an additional dependent variable."
                kind = "Identifier / status / statistical metadata"
            else:
                raise ValueError("Undocumented source export field: " + name + "." + field)
            field_rows.append(dict(source_table=name + ".csv", field=field, category=kind, definition=definition,
                                   exact_values_path="../../analysis/student_framing_v3/tables/" + name + ".csv"))
    csv_write(folder / "SOURCE_FIELD_DICTIONARY.csv", field_rows)
    try:
        import pandas as pd
        with pd.ExcelWriter(folder / "ALL_VALUES.xlsx", engine="openpyxl") as writer:
            for name, rows in datasets.items():
                clean = [{k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in r.items()} for r in rows]
                pd.DataFrame(clean).to_excel(writer, sheet_name=name[:31], index=False)
            pd.DataFrame(dictionary).to_excel(writer, sheet_name="VARIABLE_DICTIONARY", index=False)
            pd.DataFrame(field_rows).to_excel(writer, sheet_name="SOURCE_FIELD_DICTIONARY", index=False)
            for sheet in writer.book.worksheets:
                sheet.freeze_panes = "A2"; sheet.auto_filter.ref = sheet.dimensions
                for col in sheet.columns:
                    letter = col[0].column_letter
                    sheet.column_dimensions[letter].width = min(48, max(13, max(len(str(c.value or "")) for c in list(col)[:100]) + 2))
    except ImportError as error:
        raise RuntimeError("Install publication requirements (pandas/openpyxl) to generate the values workbook") from error
    descriptions = {
        "CONDITION_OUTCOMES": "Actual means, SDs and ranges for the four primary measured quantities in all three conditions.",
        "ALL_MEASURED_VALUES": "All reported measurements: definition, calculation, aggregation, value, SD, range and count for each condition.",
        "HYPOTHESIS_COMPARISONS": "Full named comparisons, both condition means, signed differences, intervals and p-values.",
        "SAMPLE_SIZE_VALUES": "All exact values behind both sample-prefix figures; n means matched blocks.",
        "CHAIN_VALUES": "All 30 main contexts and their saved metrics/statuses.",
        "WEEKLY_ROLE_VALUES": "All 2,880 role-week observations, including actual orders, inventory, backlog, receipts, shipments, outstanding orders and costs.",
        "ROLE_VALUES": "All 120 role outcomes, final states and ordering diagnostics.",
        "PROBE_ANSWERS": "All 960 actual scenario answers with complete displayed state variables.",
        "PROBE_PAIRS": "All 480 matched probe pairs, exact low/high quantities, orders and slopes (240 pipeline and 240 backlog pairs).",
        "QUIZ_ANSWERS": "All 120 actual quiz answers, question text, alternatives, frozen correct answer and score.",
        "RESPONSE_TIMES": "All 990 accepted packet latencies: 720 game, 240 probe and 30 quiz packets; not thinking time.",
        "TIME_ALLOWANCE_RECALL": "Assigned seconds and literal public recall disclosures; missing remains missing.",
    }
    lines = ["# All values and variable definitions", "", "[Open the workbook](ALL_VALUES.xlsx) for all current tables in one file. [Full report](../REPORT.md).", "",
             "A = 120 s + control reading; B = 8 s + control reading; C = 8 s + causal education. These are three conditions in one study.", "",
             "[Measurement dictionary](VARIABLE_DICTIONARY.csv) · [Every original export field explained](SOURCE_FIELD_DICTIONARY.csv)", "",
             table(["File", "Rows", "What it contains"], [[f"[{name}.csv]({name}.csv)", len(datasets[name]), descriptions[name]] for name in datasets]), "",
             "The frozen technical analysis and development records remain at [analysis/student_framing_v3](../../analysis/student_framing_v3/). Only the 30 main contexts enter current condition summaries and tests."]
    (folder / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return comparisons, condition_rows, dictionary


def outcome_explanation(e, measures, comparisons):
    """Reader-facing equations and interpretation; no new scientific analysis."""
    summary = {row["variable"]: row for row in measures}
    tests = {row["hypothesis"]: row for row in comparisons}

    def values(key, digits=4):
        return "; ".join(ARMS[arm] + " = " + number(summary[key][arm + "_value"], digits) for arm in ARMS)

    example = next(row for row in e["source_tables"]["probe_pairs"]
                   if row["stage"] == "main" and row["block_id"] == "c3m001"
                   and row["arm"] == "A" and row["pair_id"] == "pipeline_01")
    dq = float(example["low_order"]) - float(example["high_order"])
    dp = float(example["high_quantity"]) - float(example["low_quantity"])
    close(dq / dp, float(example["response_slope"]))
    cost_pct = 100 * tests["H2"]["mean_difference"] / tests["H2"]["second_condition_mean"]
    holding_diff = summary["complete_holding_cost"]["B_value"] - summary["complete_holding_cost"]["A_value"]
    backlog_diff = summary["complete_backlog_cost"]["B_value"] - summary["complete_backlog_cost"]["A_value"]
    lines = [
        "## 11. Plain-language guide: what each outcome means and how it tests a hypothesis", "",
        "The measured outcomes describe decisions or game performance. The assigned fictional time allowance and reading are the independent variables. A model setting, an observed behavior, and a statistical test are different things.", "",
        "**The three conditions:** 120 seconds + control reading; 8 seconds + the same control reading; 8 seconds + causal supply-chain education. Seconds describe a fictional student's decision situation. The actual model had no enforced deadline. The pressure comparison holds the reading fixed; the education comparison holds the 8-second framing fixed.", "",
        "**How to read the equations:** q means a new order in cases of beer; P means replenishment already ordered but not received; I means physical inventory remaining; U means unfilled customer demand (backlog); D means final-consumer demand. A chain has four roles (r = 1 to 4), observed for 24 weeks (t = 1 to 24). Each condition contains ten chains. SUM means add the indicated observations. Condition values below are means across ten chains unless stated otherwise.", "",
        "### 11.1 Pipeline response: the outcome used for H1 and H3", "",
        "**Question answered:** when more beer is already on order, how much does the model reduce its NEW order? Pipeline means previously requested replenishment still outstanding, including goods in transit and orders awaiting upstream fulfillment. It is different from stock already on the shelf.", "",
        "**Measurement task:** after the 24-week game, the model answered hypothetical ordering scenarios. Eight matched pairs vary outstanding replenishment. Within each pair, inventory, backlog and the other displayed quantities stay fixed; the arrival quantities scale proportionally with the outstanding total, keeping relative arrival timing fixed. Thus the score measures response to this replenishment change. It is not a regression of ordinary game orders on outstanding orders.", "",
        "**Equation for one matched pair:** `response = (order with LOW outstanding replenishment − order with HIGH outstanding replenishment) / (HIGH outstanding quantity − LOW outstanding quantity)`.", "",
        "In symbols: `R(j) = [q_low(j) − q_high(j)] / [P_high(j) − P_low(j)]`. For a chain: `S = SUM over j=1..8 of R(j) / 8`. For a condition: `mean S = SUM of the 10 chain scores / 10`. Every pair has equal weight after dividing by its own quantity change.", "",
        "**Actual example from the saved data:** block c3m001, retailer, pipeline_01, 120 seconds + control reading:", "",
        table(["Displayed scenario", "Outstanding replenishment, cases", "Actual new order, cases"], [
            ["Low outstanding quantity", example["low_quantity"], example["low_order"]],
            ["High outstanding quantity", example["high_quantity"], example["high_order"]],
        ]), "",
        f"Calculation: ({example['low_order']} − {example['high_order']}) / ({example['high_quantity']} − {example['low_quantity']}) = {number(dq)} / {number(dp)} = **{number(dq / dp, 6)}**. The extra {number(dp)} outstanding cases led to an order {number(dq)} cases smaller: about one-third of a case less ordered per extra outstanding case. This is one observed pair; it is not the full condition mean. [Verify the actual pair](tables/PROBE_PAIRS.csv).", "",
        "**Units and interpretation:** ordered cases reduced per additional outstanding case. A score of 0 means identical orders in that pair. A positive score means the high-pipeline order is smaller; a negative score means it is larger. A score of 0.30 means an average reduction of 0.30 ordered cases per extra outstanding case over the tested changes. It is neither 30% of all orders nor a measured attention percentage, and it does not assume a linear response outside these scenarios.", "",
        "**Observed condition means:** " + values("pipeline_sensitivity", 6) + ".", "",
        f"**H1 connection:** H1 predicts that pressure increases the underweighting of outstanding orders. Its operational prediction here is LESS pipeline response under the pressure framing. The tested difference is **8 s + control minus 120 s + control = {tests['H1']['mean_difference']:+.6f}**. The observed reduction is consistent with H1's response prediction: the same extra outstanding replenishment changes the new order less under the 8-second framing.", "",
        "**What H1 does not establish:** less responsiveness is not automatically incorrect or below optimal. The study did not calculate a validated optimal response for each state, and a coefficient of 1 is not automatically the correct benchmark. A zero-order floor can also limit how much an order falls. Probes show final choices, not attention or hidden reasoning. Consequently this is evidence for the H1 responsiveness proxy, not proof of normative underweighting or an effect of a genuinely binding deadline on real students. The full literal H1 remains broader than this measurement.", "",
        f"**H3 connection:** H3 asks whether education restores pipeline responsiveness under the same pressure framing. **8 s + education minus 8 s + control = {tests['H3']['mean_difference']:+.6f}**. This supports increased response under education; the education mean is still below the 120-second control mean. It does not establish an optimal response or directly observe the model's understanding.", "",
        "### 11.2 Total holding and backlog cost: the outcome used for H2", "",
        "**Question answered:** how costly was the complete chain's operation over the 24 observed weeks? Too much stock creates holding cost; unfilled customer demand creates backlog cost. The tradeoff means simply ordering as much as possible or keeping no stock is not generally cost-free.", "",
        "**Equation:** `total chain cost = SUM over r=1..4 and t=1..24 of [0.5 × I(r,t) + 1 × U(r,t)]`. I and U are remaining inventory and backlog after that week's receipts and shipments. First add all 96 role-week costs for a chain; then average the ten chain totals in a condition.", "",
        "**Illustrative accounting example, not an experimental observation:** in one week, a retailer with 10 cases left and no backlog costs 0.5 × 10 = 5 units. A wholesaler with no stock and 3 unfilled cases costs 1 × 3 = 3 units. Together those two role-weeks contribute 8 units. Add every role and week in the same way. A case still in inventory or backlog next week can incur another weekly charge.", "",
        "**Observed condition means:** " + values("chain_total_cost", 2) + " game cost units per chain.", "",
        f"**H2 connection:** H2 predicts higher cumulative holding and backlog costs under pressure. **8 s + control minus 120 s + control = {tests['H2']['first_condition_mean']:.2f} − {tests['H2']['second_condition_mean']:.2f} = +{tests['H2']['mean_difference']:.2f}**, or **{cost_pct:.2f}% higher** relative to the 120-second control mean. This outcome directly measures the stated cost criterion and supports its predicted direction in this framing study.", "",
        "**Limits:** cost includes only holding and backlog over weeks 1–24. It excludes revenue, purchase/production charges, API spending and costs after week 24; it is not a profit measure. The education condition's lower cost is visible descriptively, but education versus control cost was not one of the five planned primary tests. H1 and H2 occurring together does not prove that reduced pipeline response caused the additional cost; that mechanism was not separately identified.", "",
        "### 11.3 Inventory-holding cost: the stock component of H2", "",
        "**Question answered:** how much cost came from carrying physical stock? **Equation:** `holding cost = 0.5 × SUM of I(r,t) over all 4 roles and 24 weeks`. Each stored case costs 0.5 game units for each week it remains. Illustrative example: 10 remaining cases cost 5 units in that role-week.", "",
        "**Observed condition means:** " + values("complete_holding_cost", 2) + " game cost units per chain.", "",
        f"**Hypothesis connection:** holding cost increased by **{holding_diff:.2f}** in 8 s + control compared with 120 s + control. This explains **{100 * holding_diff / tests['H2']['mean_difference']:.1f}% of the observed +{tests['H2']['mean_difference']:.2f} total-cost difference**. It is a decomposition of H2, not a separately tested primary hypothesis. Holding cost alone does not measure total performance: reducing inventory may increase shortages.", "",
        "### 11.4 Backlog cost: the shortage component of H2", "",
        "**Question answered:** how much cost came from customers waiting for unfilled orders? Backlog is demand owed to customers. It is different from pipeline replenishment owed to the role by its supplier. **Equation:** `backlog cost = 1 × SUM of U(r,t) over all 4 roles and 24 weeks`. Illustrative example: 3 unfilled cases cost 3 units for that role-week; if still unfilled the next week, they can be charged again.", "",
        "**Observed condition means:** " + values("complete_backlog_cost", 2) + " game cost units per chain.", "",
        f"**Hypothesis connection:** backlog cost increased by **{backlog_diff:.2f}** under 8 s + control relative to 120 s + control. The exact cost decomposition is **+{holding_diff:.2f} holding + {backlog_diff:.2f} backlog = +{tests['H2']['mean_difference']:.2f} total**. This explains the remaining part of H2's observed difference; no separate primary significance test was assigned to this component. Backlog cost is a sum of weekly unfilled quantities, not the count of unique customers or only the final week's backlog.", "",
        "### 11.5 Weekly order variance: the outcome used for H4a", "",
        "**Question answered:** how strongly do a role's orders fluctuate from week to week? The variable measures variability, not the average order size. Two order sequences can have the same mean but very different variance.", "",
        "**Equations:** for each role, `mean order(r) = SUM over t=1..24 of q(r,t) / 24`; then `V(r) = SUM over t=1..24 of [q(r,t) − mean order(r)]² / 23`. The chain score is `V_chain = [V(retailer) + V(wholesaler) + V(distributor) + V(factory)] / 4`. The condition value averages ten chain scores. The denominator is 24 − 1 = 23 because the specified statistic is sample variance. Do not pool roles before calculating it.", "",
        "**Illustrative four-week example, not study data:** orders [4, 4, 4, 4] have mean 4 and variance 0. Orders [0, 8, 0, 8] also have mean 4, but sample variance is (16 + 16 + 16 + 16) / (4 − 1) = 21.3333 cases². The actual study uses 24 weeks and divisor 23. Squaring the deviations gives the unit cases².", "",
        "**Observed condition means:** " + values("mean_role_order_variance", 4) + " cases².", "",
        f"**H4a connection:** H4a predicts that education reduces order variability under pressure. **8 s + education minus 8 s + control = {tests['H4a']['mean_difference']:+.6f} cases²**. The negative difference supports this prediction. The 120-second control value is descriptive context; H4a's planned comparison is between the two 8-second conditions.", "",
        "**Limits:** smaller variance does not necessarily mean a better ordering policy. Constant zero orders have zero variance but may create severe backlog; some variation may be an appropriate response to demand. Interpret this outcome together with total cost, actual demand and the recorded inventory/backlog. It does not directly test pipeline underweighting.", "",
        "### 11.6 Bullwhip ratio: the outcome used for H4b", "",
        "**Question answered:** are replenishment orders more variable than final-consumer demand, and by how much? This normalizes order variance against the demand variation faced by the chain.", "",
        "**Equations:** `mean demand = SUM over t=1..24 of D(t) / 24`; `V_D = SUM over t=1..24 of [D(t) − mean demand]² / 23`. For each role, `bullwhip(r) = V(r) / V_D`. The chain score averages its four role ratios, and the condition value averages ten chain scores. D is external final-consumer demand, not an upstream role's incoming orders. Calculate each chain's ratios before averaging; a ratio of pooled condition averages generally gives a different answer. A zero demand variance would make this ratio undefined.", "",
        "**Illustrative example, not study data:** if a role's order variance is 18 cases² and its chain's consumer-demand variance is 6 cases², bullwhip = 18 / 6 = 3. Its orders have three times the variance of consumer demand, not three times the average volume. Both variances have the same units, so the ratio has no unit. Above 1 means amplification; 1 means equal variance; below 1 means smoothing relative to this demand denominator.", "",
        "**Observed condition means:** " + values("mean_role_bullwhip", 4) + ". The 8-second control mean of about 2.60 describes an average variance ratio; it does not mean every role or chain has exactly that ratio.", "",
        f"**H4b connection:** H4b predicts that education reduces bullwhip under pressure. **8 s + education minus 8 s + control = {tests['H4b']['mean_difference']:+.6f}**. This supports reduced amplification. The education mean remains above 1, so amplification was reduced rather than eliminated on this aggregate measure.", "",
        "**Limits:** H4a and H4b share the same order-variance numerator, and demand paths are matched within each block. They are related views of order fluctuation, not two independent demonstrations of a mechanism. This across-role average alone does not establish that variance increases at every successive upstream stage; inspect the individual role values for that question.", "",
        "### 11.7 What the other recorded quantities tell you", "",
        "The six outcomes explained above comprise four unique primary quantities plus the two cost components. The other rows in section 5 are state descriptions, secondary behavioral measures or procedure diagnostics. Their definitions, formulas, exact values and denominators remain listed there and in the workbook. They help explain or audit the experiment; they do not each create another H1–H4 test.", "",
        table(["Recorded quantity", "Meaning and calculation", "Connection to the hypotheses"], [
            ["Orders, incoming demand, receipts and shipments", "Cases chosen, requested, received or sent in a role-week. Weekly averages use 960 role-week records per condition; final-consumer demand uses 240 chain-weeks to avoid counting it four times.", "Describe how the chain operated. A low mean order or many zeros alone does not establish pipeline neglect."],
            ["Inventory, backlog and net inventory", "I is stock remaining; U is unfilled demand; net inventory = I − U. Mean weekly states and week-24 totals answer different questions.", "Inventory and backlog generate the cost components. A final snapshot cannot substitute for cumulative H2 cost."],
            ["Outstanding replenishment before/after ordering", "P is earlier orders not yet received. Immediately after the current decision it is P + q. This is a quantity in cases; pipeline response is the change in q per change in P.", "Separates the state being reacted to from the H1/H3 behavioral response measurement."],
            ["Backlog response", "For each of eight separate backlog pairs, (order at high backlog − order at low backlog) / increase in backlog; then average pairs and chains. Means: " + values("backlog_sensitivity", 4) + ".", "Checks response to unfilled demand. It is secondary, not an alternative primary H1 test or a fixed unaffected benchmark."],
            ["Zero fractions and observed minimum/maximum orders", "Game zero fraction = number of zero orders / 96 per chain; probe zero fraction = zero answers / 32. Fractions average chains; overall extremes use the whole condition. Game zero fractions: " + values("game_zero_order_fraction", 4) + ".", "Reveal flat choices, boundaries and unusual patterns. Zero is an admissible order; its presence alone is not evidence of irrationality."],
            ["Probe-slope spread and regression diagnostics", "Minimum, maximum, sample SD and zero fraction summarize the eight pair slopes. The alternative regression response weights slopes by squared quantity changes; it differs from the equal-weight primary score. Fitted order = pair intercept + raw slope × quantity; residual = actual − fitted order.", "Check how the response varies across scenarios. Mean residual near zero can arise by construction. These are not a newly estimated optimal beta or replacement hypothesis tests."],
            ["Comprehension and allowance recall", "Quiz score = correct answers / 4; all conditions averaged 4/4. Recall counts correct literal reports of the assigned allowance; all conditions had 10/10.", "Check stated knowledge and remembered instructions. Correct answers do not prove correct gameplay, subjective pressure or an optimal decision policy."],
            ["Elapsed response times", "Observed display-to-submission packet latency. Reported medians and 90th percentiles are calculated within contexts then averaged; maximum is the largest observed latency. A packet contains four choices.", "Operational timing includes service/transport/scheduling. It is not per-student thinking time and cannot validate a binding 8-second model deadline."],
            ["Completeness, acceptance and replay", "Count submitted weeks/probes/questions and accepted/opened packets. Replay checks that recorded choices reproduce game states. All main contexts completed; there were zero enforced-deadline displays, so an on-time fraction is undefined.", "Check whether outcomes are available and accounting is consistent. Completion or replay success does not demonstrate human realism or confirm a hypothesis."],
        ]), "",
        "### 11.8 When does a result support, contradict or leave a hypothesis unresolved?", "",
        "First choose the planned outcome and the full named subtraction. For each of the ten matched blocks, subtract its two condition values. Average those ten differences, then assess uncertainty using the frozen paired analysis. The independent comparison count is ten, not 2,880 independent orders.", "",
        table(["Test", "Full comparison and prediction", "Observed mean difference", "Interpretation in this study"], [
            ["H1", COMPARISONS["pressure"] + "; pipeline response should be LOWER", f"{tests['H1']['mean_difference']:+.6f}", "Supports reduced responsiveness; normative underweighting and a binding human deadline are not established."],
            ["H2", COMPARISONS["pressure"] + "; total cost should be HIGHER", f"{tests['H2']['mean_difference']:+.2f} cost units/chain", "Supports higher cumulative cost under pressure framing."],
            ["H3", COMPARISONS["education"] + "; pipeline response should be HIGHER", f"{tests['H3']['mean_difference']:+.6f}", "Supports increased responsiveness under education."],
            ["H4a", COMPARISONS["education"] + "; order variance should be LOWER", f"{tests['H4a']['mean_difference']:+.6f} cases²", "Supports less order variability under education."],
            ["H4b", COMPARISONS["education"] + "; bullwhip should be LOWER", f"{tests['H4b']['mean_difference']:+.6f}", "Supports a lower order-to-demand variance ratio under education."],
        ]), "",
        "**Statistical evidence:** all ten block differences have the predicted sign for each endpoint. Each exact two-sided paired sign-flip test has raw p = 2/1024 = 0.001953125; adjustment across the five planned tests gives Holm p = 0.009765625. These calculations rely on the stated independent symmetric/exchangeable paired-null assumptions. The endpoint intervals and all individual differences appear in section 4 and the linked comparison table.", "",
        "**Decision rule for interpretation:** an effect in the predicted direction with statistical support is evidence supporting that operational prediction. A clearly supported opposite-direction effect contradicts that prediction in the studied setting. An imprecise or nonsignificant estimate leaves it unresolved; failure to find significance is not proof of no effect. A p-value is not the probability that the hypothesis is true. Demonstrating a negligible effect would require a prospectively justified equivalence margin and appropriate analysis, which this study did not perform.", "",
        "**Scope of the conclusions:** statistical significance does not validate an outcome's psychological meaning or establish human behavior. This experiment finds differences in an AI model's portrayal of fictional student conditions. Because actual model runtime was unrestricted and no appropriate optimal pipeline weight was identified, it cannot prove the original literal claim that binding human time pressure causes normative underweighting. The measured response and game-cost results should be reported with that distinction.", "",
        "### 11.9 Are these established research measures or measures created for this study?", "",
        "**Both, with an important distinction.** Holding cost, backlog cost, total cost and order variance are established observable performance quantities. Bullwhip as a variance ratio is established too, although the reference demand and aggregation must be specified. Supply-line underweighting is a long-studied behavioral concept; our particular eight-pair pipeline-response score is a study-specific operational measure of responsiveness. Most numbers here are outcome statistics, not parameters of a fitted behavioral model.", "",
        table(["Outcome", "Use in established research", "What is specific to experiment 14"], [
            ["Holding cost, backlog cost and total cost", "Beer-game research charges for remaining inventory and unfilled demand. Croson and Donohue (2006), experimental setup, uses holding/backlog rates of 0.50/1 per case-period. [Paper](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0436).", "Our 24-week window, exact realized paths, four-role totals and ten-chain condition means. Matching cost rates does not make studies with different horizons and rules numerically interchangeable."],
            ["Order variance", "A standard statistic used to quantify ordering fluctuations. Croson and Donohue (2006), Table 1, compares average order variance by role across information conditions. [Paper](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0436).", "Our primary summary averages four role-specific sample variances over 24 weeks. The individual role values remain available; role averaging is an explicit design choice."],
            ["Bullwhip ratio", "Chen et al. (2000), sections 2.2 and 3, measures order variance relative to demand variance and extends the analysis to multiple stages. [Paper](https://pubsonline.informs.org/doi/10.1287/mnsc.46.3.436.12069).", "Our denominator is each chain's observed final-consumer demand variance. We average within-chain role ratios, then chains. Other studies may use adjacent-stage comparisons or different time windows."],
            ["Pipeline response / supply-line underweighting", "Sterman (1989) estimates an ordering heuristic; Croson and Donohue (2006) examines supply-line underweighting, including with shared inventory information. [Sterman](https://pubsonline.informs.org/doi/10.1287/mnsc.35.3.321); [Croson and Donohue](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0436).", "Our eight controlled hypothetical pair slopes are specified in our protocol. These citations do not validate this exact probe bank, establish its optimal score, or turn its mean into a structural beta."],
            ["State variables and diagnostics", "Inventory, backlog, orders and receipts are ordinary observable game quantities. Variance, SD, minima and proportions are standard summaries.", "Our probe bank, quiz, recall check, packet-latency summaries and completeness flags are experiment-specific diagnostics. Their reproducibility does not establish a validated human time-pressure measure."],
        ]), "",
        "**Why our pipeline score is not automatically the literature's beta:** an illustrative linear rule is `new order = forecast + a × (target stock − current stock) + b × (target pipeline − current pipeline)`. If its targets and other inputs are fixed, and neither order is clipped at zero, the pair response equals b. A relative pipeline-versus-stock weight would instead be b/a when a is nonzero. Thus the same observed b can coexist with different relative weights if a changes. This is an algebraic illustration, not a fitted model or a new estimate for these agents. The current assay does not estimate the needed matched stock-response coefficient, and its backlog-response diagnostic is not automatically a substitute.", "",
        "**How to describe this study accurately:** established supply-chain cost and variability outcomes, plus a pre-specified matched-scenario measure of pipeline responsiveness. The behavior of interest has a literature foundation; the exact probe score still needs validation before being presented as a standard measure of normative underweighting. Existing statistical significance does not supply that validation.", "",
        "**Primary research references:**", "",
        "1. John D. Sterman (1989). [Modeling Managerial Behavior: Misperceptions of Feedback in a Dynamic Decision Making Experiment](https://pubsonline.informs.org/doi/10.1287/mnsc.35.3.321). Management Science 35(3), 321–339. Relevant to estimating behavioral ordering rules and supply-line response.", "",
        "2. Rachel Croson and Karen Donohue (2006). [Behavioral Causes of the Bullwhip Effect and the Observed Value of Inventory Information](https://pubsonline.informs.org/doi/10.1287/mnsc.1050.0436). Management Science 52(3), 323–336. Relevant to beer-game cost rules, order variance, inventory information and supply-line underweighting.", "",
        "3. Frank Chen, Zvi Drezner, Jennifer K. Ryan and David Simchi-Levi (2000). [Quantifying the Bullwhip Effect in a Simple Supply Chain: The Impact of Forecasting, Lead Times, and Information](https://pubsonline.informs.org/doi/10.1287/mnsc.46.3.436.12069). Management Science 46(3), 436–443. Relevant to the order-variance/demand-variance measure.", "",
    ]
    return lines


def report_markdown(e, measures, comparisons):
    means = outcome_means(e)
    def val(arm, key, digits=4):
        return number(means[arm][key], digits)
    lines = ["# Experiment 14 — student time-pressure framing", "",
        "## 1. Conclusions first", "",
        f"1. **Fictional pressure reduced pipeline response:** 120 s + control reading = **{val('A', 'pipeline_sensitivity')}**; 8 s + control reading = **{val('B', 'pipeline_sensitivity')}** ordered cases reduced per extra outstanding case. The pressure-minus-adequate difference is **−0.122830** (H1 response proxy).",
        f"2. **Fictional pressure increased total cost:** **{val('A', 'chain_total_cost', 2)} → {val('B', 'chain_total_cost', 2)}** game cost units per chain, an increase of **68.50** (H2). This comprises **60.00 additional holding cost + 8.50 additional backlog cost**.",
        f"3. **Education under the same 8-second framing increased pipeline response:** **{val('B', 'pipeline_sensitivity')} → {val('C', 'pipeline_sensitivity')}**, a difference of **+0.074115** (H3 response proxy). It did not restore the mean to the 120-second control level.",
        f"4. **Education reduced order variation and bullwhip under the 8-second framing:** order variance **{val('B', 'mean_role_order_variance')} → {val('C', 'mean_role_order_variance')} cases²** (H4a); bullwhip **{val('B', 'mean_role_bullwhip')} → {val('C', 'mean_role_bullwhip')}** (H4b).",
        "5. **All five planned comparisons have Holm-adjusted p = 0.009766 in the ten matched blocks.** These are model responses to fictional student conditions. There was no actual model timer, no human sample, and no identified optimal pipeline-weighting coefficient. H1/H3 support the measured response direction; they do not establish normative underweighting in people.", "",
        "**Read the values:** the tables show actual condition levels before their differences. A/B/C are three conditions within ONE student_framing_v3 study, not three unrelated experiments. One case of beer is the quantity unit; game cost units are not API dollars.", "",
        "[PDF of this same report](REPORT.pdf) · [All values in one workbook](tables/ALL_VALUES.xlsx) · [Figures with axis/calculation explanations](figures/README.md) · [All original export fields explained](tables/SOURCE_FIELD_DICTIONARY.csv)", "",
        "## 2. Independent variables: exactly what was changed", "",
        "There are **two assigned between-condition independent variables**: (1) the fictional student's time allowance, and (2) the reading. Neither is an observed behavioral outcome.", "",
        table(["Condition", "Independent variable 1: fictional allowance", "Independent variable 2: reading", "Actual model procedure"], [
            ["A — 120 s + control", "120 seconds per fictional student's game/probe decision", "170-word control reading", "One committed response; unrestricted actual runtime"],
            ["B — 8 s + control", "8 seconds per fictional student's game/probe decision", "Same 170-word control reading", "Same procedure and settings as A"],
            ["C — 8 s + education", "8 seconds per fictional student's game/probe decision", "170-word causal supply-chain education", "Same procedure and settings as A/B"],
        ]), "",
        "**What the readings contain:** the [control reading](../prompts/CONTROL.md) discusses ordinary business-document presentation (headings, layout and audiences). The [causal education reading](../prompts/EDUCATION.md) explains that requests and deliveries occur at different times, earlier outstanding orders can arrive together, and local requests can differ from final-consumer demand. It distinguishes inventory, customer obligations and replenishment already requested. Neither reading supplies an ordering formula or a preferred order quantity.", "",
        "The 120/8 numbers were instructions about a fictional student's classroom situation. They were **not measured response durations** and were **not enforced on the model**. Readings and the final quiz were untimed. There was no revision round in any condition. This differs from experiment 13's revision-opportunity design.", "",
        "**What each planned comparison isolates:**", "",
        table(["Question", "Exact subtraction", "Variable changed", "Held fixed"], [
            ["H1/H2: What changes under the pressure framing?", COMPARISONS["pressure"] + " (B minus A)", "120 seconds becomes 8 seconds", "Control reading"],
            ["H3/H4a/H4b: What changes with education under pressure?", COMPARISONS["education"] + " (C minus B)", "Control reading becomes causal education", "8-second framing"],
        ]), "",
        "**Sign rule:** calculate the first named condition minus the second. Positive means the first condition is higher; negative means it is lower. **A minus B reverses the sign of B minus A.** There is no 120-second education condition, so this design cannot identify a full time-by-education interaction. C minus A changes both assigned factors and is not one of the five planned comparisons.", "",
        "**Held constant:** requested GPT-6 Astra, requested extra-high (`xhigh`) effort, four supply-chain roles, 24 weeks, information-sharing displays, one submitted choice per decision, the physical game rules, and costs of 0.5 per inventory case/week and 1 per backlog case/week. Each matched block uses the same customer-demand path and role profiles in three fresh contexts. Requested settings are operator-recorded; provider-authenticated model/effort remain unverified. Temperature and hidden reasoning-token use were not measured.", "",
        "**Sample:** 10 matched blocks × 3 conditions = 30 main chain contexts; 10 chains and 40 role instances per condition. Each chain has 96 game orders, 32 probe answers and 4 quiz answers. Main totals: 2,880 game orders, 960 probe answers and 120 quiz answers. The inferential sample is 10 paired block differences, not 120 independent human participants. The separate 3-context development block is excluded from every main value below.", "",
        "## 3. Dependent variables: measured levels in all three conditions", "",
        "These are **four unique primary quantities** used in five hypothesis tests. H1 and H3 reuse the same pipeline-response measurement with different condition comparisons. Values below are arithmetic means across the ten chains in each condition.", "",
        table(["Dependent variable and unit", "120 s + control (A)", "8 s + control (B)", "8 s + education (C)"],
              [[name + " (" + unit + ")", *[number(means[a][key]) for a in ARMS]] for key, (name, unit, _) in OUTCOMES.items()]), "",
        "![Measured levels in each condition](figures/01_CONDITION_VALUES.png)", "",
        "**Figure 1:** the x-axis names the assigned allowance and reading; each y-axis names the measured outcome and unit. Small dots show ten chain values; the diamond and printed number show their mean. These are levels, not subtractions. [Exact means, SDs and ranges](tables/CONDITION_OUTCOMES.csv).", "",
        "### How each primary variable is calculated", "",
    ]
    for key, (name, unit, formula) in OUTCOMES.items():
        lines.extend(["**" + name + " — " + unit + ".** " + formula, ""])
    lines.extend([
        "**Pipeline interpretation:** a response of 0.30 means the model reduces its order by 0.30 cases per additional outstanding case, averaged over the fixed probes. Zero means unchanged orders in those pairs. The probe is a response measurement; there is no established optimal response of 1 in every displayed state. This study did not estimate a structural behavioral beta coefficient.", "",
        "**Variance interpretation:** calculate variance within each role across its 24 weeks, then average the four roles. Do not calculate variance by mixing roles or pooling all chains first. The denominator is 23 because it is a sample variance.", "",
        "**Bullwhip interpretation:** 2.60 means role orders are, on average under this calculation, about 2.60 times as variable as final-consumer demand. A ratio above 1 denotes amplification relative to that denominator. Use the external customer's demand, not each upstream role's incoming orders. H4a and H4b share the order-variance numerator; they are related measures, not independent replications.", "",
        "## 4. Comparisons with both condition values shown", "",
        "### Pressure comparison: 8 s + control reading minus 120 s + control reading", "",
    ])
    for kind in ("pressure", "education"):
        if kind == "education":
            lines.extend(["### Education comparison: 8 s + causal education minus 8 s + control reading", ""])
        own = [r for r in comparisons if (r["hypothesis"] in ("H1", "H2")) == (kind == "pressure")]
        first, second = ("B", "A") if kind == "pressure" else ("C", "B")
        lines.append(table(["Test / dependent variable", ARMS[first], ARMS[second], "First minus second", "Holm-adjusted p"],
                           [[r["hypothesis"] + ": " + r["dependent_variable"], number(r["first_condition_mean"]), number(r["second_condition_mean"]),
                             f"{r['mean_difference']:+.6f}", number(r["p_holm_family_5"], 6)] for r in own]))
        lines.append("")
    lines.extend(["**Worked cost example:** 642.95 (8 s + control) − 574.45 (120 s + control) = **+68.50 cost units per chain**. Positive means the pressure-framed condition cost more. **Worked education example:** 10.104529 (8 s + education order variance) − 17.829438 (8 s + control order variance) = **−7.724909 cases²**. Negative means education produced less variable orders in this sample.", "",
        table(["Test and comparison", "95% pointwise interval for difference", "Raw two-sided p", "Holm-adjusted p (5 tests)"],
              [[r["hypothesis"] + ": " + r["comparison"], number(r["ci95_low"], 6) + " to " + number(r["ci95_high"], 6),
                number(r["p_two_sided"], 9), number(r["p_holm_family_5"], 9)] for r in comparisons]), "",
        "Intervals use 10,000 paired-block bootstrap resamples. Tests use exact two-sided paired sign flips under independent symmetric/exchangeable paired differences; Holm correction covers the five preplanned outcomes. All ten differences have the predicted sign for every endpoint, yielding the same exact raw p = 2/1024 = 0.001953125 and adjusted p = 0.009765625. A p-value is not the probability that a hypothesis is true.", "",
        "![Pressure comparison](figures/02_PRESSURE_COMPARISON.png)", "",
        "![Education comparison](figures/03_EDUCATION_COMPARISON.png)", "",
        "**Figures 2–3:** x = matched block number 1–10; the separate Mean position summarizes all blocks. Y = the named outcome difference with units. Every figure states the full subtraction. A diamond is the mean; its bar is a pointwise 95% bootstrap interval. Zero means equal outcomes. [All comparison values](tables/HYPOTHESIS_COMPARISONS.csv).", "",
        "## 5. Every measured quantity and its condition value", "",
        "Each table below names the variable, its calculation and its aggregation. **Mean [minimum, maximum]** describes the observations being averaged; ranges are not confidence intervals. Rows labeled Count, Total, Overall minimum/maximum or Maximum use that stated operation instead of a mean. The workbook also contains SD and N for every numeric summary. 'Not available' is missing/undefined, never zero.", "",
    ])
    for category in dict.fromkeys(r["category"] for r in measures):
        own = [r for r in measures if r["category"] == category]
        lines.extend(["### " + category, ""])
        rows = []
        for r in own:
            values = []
            for a in ARMS:
                v = number(r[a+"_value"])
                if r["aggregation"].startswith("Mean") and r[a+"_minimum"] is not None and r[a+"_minimum"] != r[a+"_maximum"]:
                    v += " [" + number(r[a+"_minimum"]) + ", " + number(r[a+"_maximum"]) + "]"
                values.append(v)
            rows.append([r["label"] + " (" + r["units"] + ")", r["calculation"] + " Aggregation: " + r["aggregation"] + ".", *values])
        lines.extend([table(["Measured variable / unit", "Calculation and aggregation", "120 s + control", "8 s + control", "8 s + education"], rows), ""])
    lines.extend(["**Timing distinction:** reported elapsed times cover one packet of four choices or four quiz answers. They include transport and scheduling and cannot be interpreted as a per-person thinking duration. No observed time was used to reject an order. Null deadline variables and undefined on-time fractions are intentional.", "",
        "**Saved aliases:** because every chain completed 24 weeks, `completed_prefix_cost` equals total cost; `observed_holding_cost` equals complete holding cost; `observed_backlog_cost` equals complete backlog cost. These are duplicate representations, not extra outcomes. Shared-inventory displays repeat the four role inventories rather than creating new observations. Metadata identifiers, source hashes and status fields are documented in [the complete original-field dictionary](tables/SOURCE_FIELD_DICTIONARY.csv).", "",
        "## 6. Probe inputs and actual answers: what changed within each pair", "",
        "The probe bank has **8 pipeline pairs and 8 backlog pairs**, two pairs per role for each dimension: 16 pairs × 2 states = 32 actual answers per context. These within-pair quantity manipulations are measurement tasks, separate from the two assigned time/reading variables. Pipeline pairs change outstanding quantity and scale its arrival schedule proportionally. Backlog pairs change only backlog. Other displayed fields within a pair remain fixed.", "",
        "Each cell below gives **mean low-quantity order → mean high-quantity order; mean pair slope**, averaging the ten main contexts in that condition. The low/high quantities are cases, and all returned orders are cases. The slope is ordered cases per extra outstanding/backlog case. The mean of the eight pipeline slopes is the primary response; the mean backlog slope is diagnostic.", ""])
    pairs = [r for r in e["source_tables"]["probe_pairs"] if r["stage"] == "main"]
    for dimension in ("pipeline", "backlog"):
        lines.extend(["### " + ("Outstanding replenishment: slope = (low order − high order) / quantity increase" if dimension == "pipeline" else "Backlog: slope = (high order − low order) / quantity increase"), ""])
        pair_rows = []
        for ident in sorted({r["pair_id"] for r in pairs if r["assay_dimension"] == dimension}):
            own = [r for r in pairs if r["pair_id"] == ident]
            first = own[0]
            cells = []
            for a in ARMS:
                part = [r for r in own if r["arm"] == a]
                cells.append(number(st.mean(float(r["low_order"]) for r in part), 2) + " → " + number(st.mean(float(r["high_order"]) for r in part), 2)
                             + "; slope " + number(st.mean(float(r["response_slope"]) for r in part), 4))
            pair_rows.append([ident + " / " + first["role"], first["low_quantity"] + " → " + first["high_quantity"], *cells])
        lines.extend([table(["Pair / role", "Displayed quantity (cases)", "120 s + control", "8 s + control", "8 s + education"], pair_rows), ""])
    lines.extend(["[Every actual probe answer and full displayed state](tables/PROBE_ANSWERS.csv) includes inventory, backlog, outstanding quantity, the three-arrival schedule, customer demand, recent demand history and all four shared inventories. [Every paired slope](tables/PROBE_PAIRS.csv) identifies both scenario IDs and literal orders. No hypothetical probe has a normatively required order.", "",
        "## 7. Individual chain values and comprehension", "",
        "The following table gives all 30 main contexts. Pipeline and backlog response units are order cases per extra outstanding/backlog case. Costs are game cost units over 24 weeks; variance is cases²; bullwhip is dimensionless.", "",
        table(["Matched block / full condition", "Pipeline response", "Total cost", "Holding cost", "Backlog cost", "Order variance", "Bullwhip"],
              [[r["block_id"] + " / " + ARMS[r["arm"]], number(r["pipeline_sensitivity"]), number(r["chain_total_cost"], 2),
                number(r["complete_holding_cost"], 2), number(r["complete_backlog_cost"], 2), number(r["mean_role_order_variance"]), number(r["mean_role_bullwhip"])]
               for r in sorted(e["runs"], key=lambda r: (r["block_id"], r["arm"]))]), "",
        "The individual 2,880 weekly role observations, 960 probe answers, 120 quiz answers and 990 packet timings are supplied in [the workbook](tables/ALL_VALUES.xlsx) and [named CSV tables](tables/README.md). These preserve every value rather than asking readers to infer observations from a mean. [Role results](tables/ROLE_VALUES.csv) retain the individual retailer, wholesaler, distributor and factory outcomes.", "",
        "### Post-task comprehension: observed answers", ""])
    quiz_rows = []
    for ident in sorted({r["question_id"] for r in e["quiz"]}):
        own = [r for r in e["quiz"] if r["question_id"] == ident]; q = own[0]
        quiz_rows.append([ident + ": " + q["question"], q["correct_answer"] + ": " + q["choices"][q["correct_answer"]],
                          *[str(sum(r["correct"] for r in own if r["arm"] == a)) + "/10 correct" for a in ARMS]])
    lines.extend([table(["Measured quiz item", "Frozen correct answer", "120 s + control", "8 s + control", "8 s + education"], quiz_rows), "",
        "All main quiz responses were recorded after the behavioral tasks and did not determine case inclusion. Recall of the fictional allowance is a separate instruction-recall diagnostic, not proof of subjective pressure. Exact recall disclosures and missingness are in [TIME_ALLOWANCE_RECALL.csv](tables/TIME_ALLOWANCE_RECALL.csv).", "",
        "## 8. What the sample-size plots measure", "",
        "The horizontal axis is **n matched blocks included**, not the number of weeks or individual roles. At n=10 there are 10 chains per condition, 30 distinct chain contexts and 120 role instances. Prefixes use c3m001 through c3m00n in the planned order and overlap; they are not ten new experiments.", "",
        "![Mean effects as fixed blocks are included](figures/04_SAMPLE_SIZE_EFFECTS.png)", "",
        "**Figure 4:** each y-axis is the arithmetic mean of that panel's named condition difference for the first n blocks, with the dependent variable's units. Positive/negative retain the same subtraction rule as the full sample. The final point n=10 equals the main comparison table exactly.", "",
        "![Adjusted p-values by fixed block count](figures/05_SAMPLE_SIZE_PVALUES.png)", "",
        "**Figure 5:** y is the exact two-sided sign-flip p-value after Holm adjustment across five endpoints at each prefix, displayed on a logarithmic scale. All five curves coincide because their paired differences align in sign; the single line is labeled accordingly. n=1 has no p-value. The 0.05 line is a reference; n=10 was the fixed stopping point. Earlier threshold crossings neither estimate a required sample size nor justify selecting a smaller favorable sample. [All plotted prefix values](tables/SAMPLE_SIZE_VALUES.csv).", "",
        "## 9. Interpretation limits and source checks", "",
        "This is an AI portrayal of fictional students. The study measures changes under time/reading framing; actual model runtime was unlimited, hidden reasoning tokens were unavailable, and no human pressure, understanding or realism was validated. The same context controlled all four roles of one chain. Fresh chain/arm contexts reduce direct sharing across conditions but do not make the role instances independent people.", "",
        "The project/environment instructions were also visible to the agents and mentioned the overall design. The assigned prompt was not their sole context, and this was not a blinded study. Public reviews support visible procedure adherence; they are attributed local/operator evidence, not independent provider authentication or access to hidden reasoning. Block 6 resumed in the same contexts after an account usage interruption; prior choices and settings were retained. All ten planned blocks remain included.", "",
        "The 16 earlier strict-clock cases and the separate development block are not pooled with this main sample. Previously published reports and figures are archived byte-for-byte at [the archive index](../archive/README.md). Current numerical sources remain the unchanged [saved analysis](../analysis/student_framing_v3/RESULTS.json), [original verification receipt](../analysis/student_framing_v3/FINAL_VERIFICATION.json), [protocol](../hypotheses/STUDENT_FRAMING_V3.md) and [closed collection receipt](../data/student_framing_v3/COLLECTION_CLOSED.json).", "",
        "## 10. Files and reproduction", "",
        "Current report: `reports/REPORT.md` and `reports/REPORT.pdf`. Current figures: `reports/figures/`. Every current table and variable dictionary: `reports/tables/`. Previous publications: `archive/`. No other report set is current.", "",
        "Rebuild this publication offline from the closed records: `python scripts/report_exp14_framing.py`. The slide-export command uses the same publisher. No new participant or API calls are made. [Publication source hashes and checks](PUBLICATION.json).", "",
        "The scientific result fingerprint is `" + e["result"]["fingerprint"] + "`. This publication reformats and expands the explanation; it preserves the recorded observations, original endpoint definitions and all five test results.", ""])
    lines.extend(outcome_explanation(e, measures, comparisons))
    return "\n".join(lines)


def make_pdf(path, markdown):
    """Render the exact report text, including all values and calculations."""
    from html import escape
    from matplotlib import get_data_path
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle, Image, PageBreak
    fonts = Path(get_data_path()) / "fonts/ttf"
    for name, filename in (("Study", "DejaVuSans.ttf"), ("StudyBold", "DejaVuSans-Bold.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    pdfmetrics.registerFontFamily("Study", normal="Study", bold="StudyBold", italic="Study", boldItalic="StudyBold")
    body = ParagraphStyle("StudyBody", fontName="Study", fontSize=10, leading=14, spaceAfter=8)
    title = ParagraphStyle("StudyTitle", parent=body, fontName="StudyBold", fontSize=23, leading=29, spaceAfter=15)
    heading = ParagraphStyle("StudyHeading", parent=body, fontName="StudyBold", fontSize=15, leading=19, spaceBefore=12, spaceAfter=10, keepWithNext=True)
    sub = ParagraphStyle("StudySub", parent=heading, fontSize=12, leading=16)
    cell = ParagraphStyle("StudyCell", parent=body, fontSize=8.8, leading=12, spaceAfter=0)
    boldcell = ParagraphStyle("StudyHeadCell", parent=cell, fontName="StudyBold", textColor=colors.HexColor("#17384D"))
    doc = SimpleDocTemplate(str(path), pagesize=landscape(A4), leftMargin=34, rightMargin=34, topMargin=30, bottomMargin=36,
                            title="Experiment 14: student framing — variables, values and results", author="Beer Game study", pageCompression=1)
    def rich(text):
        value = escape(text)
        value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
        value = re.sub(r"`([^`]+)`", r"\1", value)
        return re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<link href="\2" color="#215F87"><u>\1</u></link>', value)
    def footer(canvas, document):
        canvas.saveState(); canvas.setFont("Study", 8); canvas.setFillColor(colors.HexColor("#53616B"))
        canvas.drawString(34, 18, "Experiment 14 · student_framing_v3 · Fictional student framing; 10 matched main blocks")
        canvas.drawRightString(landscape(A4)[0]-34, 18, "Page " + str(document.page)); canvas.restoreState()
    source = markdown.splitlines(); story = []; i = 0
    while i < len(source):
        line = source[i].strip(); i += 1
        if not line:
            continue
        if line.startswith("| "):
            raw = [line]
            while i < len(source) and source[i].lstrip().startswith("|"):
                raw.append(source[i].strip()); i += 1
            data = [[c.strip() for c in row.strip("|").split("|")] for row in raw if not re.fullmatch(r"[|\- :]+", row)]
            columns = len(data[0])
            if data[0][0] == "Measured variable / unit":
                weights = [.22, .42, .12, .12, .12]
            elif columns == 7:
                weights = [.31, .12, .11, .12, .11, .12, .11]
            elif columns == 5:
                weights = [.32, .25, .143, .143, .144]
            elif columns == 4:
                weights = [.4, .2, .2, .2]
            else:
                weights = [1/columns]*columns
            elements = [[Paragraph(rich(c), boldcell if n == 0 else cell) for c in row] for n, row in enumerate(data)]
            t = LongTable(elements, colWidths=[doc.width*w for w in weights], repeatRows=1, hAlign="LEFT")
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EDF3")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FA")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LINEBELOW", (0, 0), (-1, 0), .6, colors.HexColor("#ABC0CE"))]))
            story.extend([t, Spacer(1, 10)]); continue
        match = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line)
        if match:
            img = Image(str(path.parent / match.group(2)))
            scale = min(doc.width / img.imageWidth, (doc.height - 45) / img.imageHeight)
            img.drawWidth = img.imageWidth * scale; img.drawHeight = img.imageHeight * scale
            story.extend([PageBreak(), img, Spacer(1, 8)]); continue
        if line.startswith("### "):
            story.append(Paragraph(rich(line[4:]), sub))
        elif line.startswith("## "):
            section = re.match(r"## (\d+)\.", line)
            if section and int(section.group(1)) >= 2:
                story.append(PageBreak())
            story.append(Paragraph(rich(line[3:]), heading))
        elif line.startswith("# "):
            story.append(Paragraph(rich(line[2:]), title))
        else:
            story.append(Paragraph(rich(line), body))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def verify_preservation(experiment):
    receipt = read(experiment / ARCHIVE / "FILE_MAP.json")
    failures = []
    for row in receipt["files"]:
        path = ROOT / row["archived"]
        if not path.exists() or sha(path) != row["sha256"]:
            failures.append(str(path))
    for name, expected in receipt["protected_files"].items():
        if sha(ROOT / name) != expected:
            failures.append(name)
    if failures:
        raise ValueError("Historical bytes or scientific records changed: " + repr(failures))
    return dict(archived_files_verified=len(receipt["files"]), protected_files_verified=len(receipt["protected_files"]),
                raw_data_unchanged=True, hypotheses_unchanged=True, frozen_analysis_unchanged=True, api_ledger_unchanged=True)


def publish(experiment=EXPERIMENT):
    experiment = Path(experiment).resolve()
    folder = experiment / REPORTS
    if (folder / "student_framing_v3").exists():
        raise ValueError("Archive previous report layers with the documented cleanup before publishing")
    source = experiment / ANALYSIS / "RESULTS.json"
    inputs = {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__)), str(source.relative_to(ROOT)): sha(source)}
    for path in (experiment / "data/student_framing_v3").glob("main/*/RESULT.json"):
        inputs[str(path.relative_to(ROOT))] = sha(path)
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    manifest = folder / "PUBLICATION.json"
    if manifest.exists():
        old = read(manifest)
        if old["fingerprint"] == fingerprint and all((folder / p).is_file() and sha(folder / p) == h for p, h in old["artifacts"].items()):
            verify_preservation(experiment)
            return dict(report=str(folder / "REPORT.pdf"), figures=str(folder / "figures"), tables=str(folder / "tables"), cached=True)
        destination = experiment / "archive/publication_versions" / old["fingerprint"][:16]
        for name in [*old["artifacts"], "PUBLICATION.json"]:
            path = folder / name
            if path.is_file():
                target = destination / name; target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() and sha(target) != sha(path):
                    raise ValueError("Refusing to overwrite an archived publication")
                if not target.exists(): shutil.copyfile(path, target)
    evidence = load_evidence(experiment)
    measure_rows = measurements(evidence)
    prefix_rows = prefixes(evidence)
    comparisons, condition_rows, dictionary = build_tables(folder / "tables", evidence, measure_rows, prefix_rows)
    catalog = make_figures(folder / "figures", evidence, prefix_rows)
    text = report_markdown(evidence, measure_rows, comparisons)
    (folder / "REPORT.md").write_text(text, encoding="utf-8")
    make_pdf(folder / "REPORT.pdf", text)
    (folder / "README.md").write_text("# Experiment 14: the current publication\n\n"
        "1. [Read the report](REPORT.pdf) ([Markdown](REPORT.md)): conclusions first, named conditions, all measured variables and actual values.\n"
        "2. [Open all values in Excel](tables/ALL_VALUES.xlsx), or use the [CSV index and variable dictionaries](tables/README.md).\n"
        "3. [Use the figures](figures/README.md): actual condition values, named comparisons and clearly labeled sample-size diagnostics.\n\n"
        "This folder is the single current publication for student_framing_v3. Earlier strict-deadline reports and superseded student-framing publications are in [archive](../archive/README.md).\n\n"
        "Rebuild offline: `python scripts/report_exp14_framing.py`. [Checks and hashes](PUBLICATION.json).\n", encoding="utf-8")
    preservation = verify_preservation(experiment)
    if not all(math.isclose(r["first_condition_mean"]-r["second_condition_mean"], r["mean_difference"], rel_tol=1e-10, abs_tol=1e-10) for r in comparisons):
        raise ValueError("Condition means do not reconcile with paired effects")
    final_prefix = {r["hypothesis"]: r for r in prefix_rows if r["prefix_size"] == 10}
    for r in comparisons:
        close(final_prefix[r["hypothesis"]]["mean_difference"], r["mean_difference"])
        close(final_prefix[r["hypothesis"]]["p_holm_family_5_at_prefix"], r["p_holm_family_5"])
    write_json(manifest, dict(schema="exp14-readable-publication-v1", fingerprint=fingerprint,
        generated_utc=datetime.now(timezone.utc).isoformat(), inputs=inputs,
        source_scientific_fingerprint=evidence["result"]["fingerprint"],
        main_contexts=30, matched_blocks=10, measured_summary_variables=len(measure_rows),
        actual_weekly_role_rows=len(evidence["weekly"]), actual_probe_answers=len(evidence["probes"]),
        actual_quiz_answers=len(evidence["quiz"]), actual_packet_timings=len(evidence["timing"]),
        five_named_comparisons_reconciled=True, five_final_prefixes_reconciled=True,
        figures=len(catalog), no_new_model_calls=True, **preservation, raw_source_hashes=evidence["raw_hashes"],
        artifacts={p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob("*")) if p.is_file() and p != manifest}))
    return dict(report=str(folder / "REPORT.pdf"), figures=str(folder / "figures"), tables=str(folder / "tables"),
                measured_variables=len(measure_rows), main_contexts=30, cached=False)
