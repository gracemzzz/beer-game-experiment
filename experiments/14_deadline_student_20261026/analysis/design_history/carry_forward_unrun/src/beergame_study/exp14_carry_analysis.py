"""Separate offline analysis for the user-selected carry-forward amendment.

Only carry_forward_v2 records are read. Synthetic fallback answers are policy
answers, never observed model choices. Applied and actor-only assays stay separate.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

from . import exp14_analysis as scoring
from . import exp14_carry as controller
from .pivot_inference_v2 import ENDPOINTS, holm_adjust, paired_inference


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/14_deadline_student_20261026"
ANALYSIS = Path("analysis/carry_forward_v2")
REPORTS = Path("reports/carry_forward_v2")
DATA = Path("data/carry_forward_v2")
SCHEMA = "exp14-carry-forward-analysis-v1"
MAIN_N = 10
STAGES = ("development", "main")
METRICS = tuple(dict.fromkeys(row[1] for row in ENDPOINTS))
UNITS = dict(pipeline_sensitivity="policy ordered cases / outstanding case", chain_total_cost="policy cost units / chain",
             mean_role_order_variance="policy order cases squared", mean_role_bullwhip="policy variance ratio")
read_json, write_json, sha256, fmt, mean = scoring.read_json, scoring.write_json, scoring.sha256, scoring.fmt, scoring.mean


def extract_metrics(payload, case, *, fallback_probes=(), fallback_questions=()):
    """Score applied trajectories and accepted choices as distinct quantities."""
    game, roles = scoring.game_metrics(payload)
    probes = scoring.scoring_bank(case, "probes", fallback_probes)
    applied = {key: value for key, value in payload.get("applied_probe_answers", payload.get("probe_answers", {})).items() if value is not None}
    observed = {key: value for key, value in payload.get("actor_probe_answers", {}).items() if value is not None}
    probe, pairs, residuals, diagnostics = scoring.probe_metrics(probes, applied)
    actor_probe, actor_pairs, actor_residuals, actor_diagnostics = scoring.probe_metrics(probes, observed)
    sources = payload.get("probe_answer_sources", {})
    for pair in pairs:
        pair.update(estimand="applied_policy", low_answer_source=sources.get(pair["low_probe_id"]),
                    high_answer_source=sources.get(pair["high_probe_id"]),
                    fallback_fraction=sum(sources.get(pair[key]) == "carry_forward" for key in ("low_probe_id", "high_probe_id")) / 2,
                    actor_low_order=observed.get(pair["low_probe_id"]), actor_high_order=observed.get(pair["high_probe_id"]))
    for values, label in ((residuals, "applied_policy"), (diagnostics, "applied_policy"),
                          (actor_pairs, "actor_only"), (actor_residuals, "actor_only"), (actor_diagnostics, "actor_only")):
        for row in values:
            row["estimand"] = label
    questions = scoring.scoring_bank(case, "comprehension", fallback_questions)
    knowledge, items = scoring.knowledge_metrics(questions, payload.get("comprehension_answers"))
    timing, latencies = scoring.timing_metrics(payload)
    weeks = payload.get("weeks", [])
    opportunities = payload.get("opportunities", [])
    planned_weeks = payload.get("planned_weeks", case.get("weeks", 24))
    actor_weeks = sum(row.get("action_source") == "model_on_time" for row in weeks)
    fallback_weeks = sum(row.get("action_source") == "carry_forward" for row in weeks)
    missing_game_orders = sum(sum(bool(value) for value in row.get("actor_missing_mask", row.get("missing_mask", [])))
                              for row in weeks)
    missing_probe_opportunities = [row for row in opportunities if row.get("phase") == "probes"
                                   and row.get("action_source") == "carry_forward"]
    missing_probe_ids = [p.get("probe_id", p.get("id")) for p in probes
                         if p.get("probe_id", p.get("id")) not in observed]
    probe.pop("observed_probe_orders", None)
    aggregate = dict(game, **probe, **knowledge, **timing,
                     procedure_complete=payload.get("protocol_complete", payload.get("complete", False)),
                     all_actor_responses_complete=payload.get("all_actor_responses_complete", False),
                     physical_game_complete=game["complete_24_weeks"],
                     applied_probe_answers_complete=len(applied) == len(probes) == 32,
                     actor_probe_responses_complete=len(observed) == len(probes) == 32,
                     observed_actor_week_packets=actor_weeks, planned_week_packets=planned_weeks,
                     accepted_actor_order_count=4 * actor_weeks, planned_actor_order_count=4 * planned_weeks,
                     accepted_actor_order_fraction=actor_weeks / planned_weeks if planned_weeks else None,
                     fallback_weeks=fallback_weeks,
                     fallback_week_share_applied=fallback_weeks / len(weeks) if weeks else None,
                     fallback_week_share_planned=fallback_weeks / planned_weeks if planned_weeks else None,
                     expired_actor_order_count=missing_game_orders,
                     unresolved_game_weeks=max(0, planned_weeks - len(weeks)),
                     expired_probe_pages=len(missing_probe_opportunities),
                     fallback_probe_choices=sum(value == "carry_forward" for value in sources.values()),
                     planned_probe_choices=len(probes), accepted_actor_probe_choices=len(observed),
                     accepted_actor_probe_fraction=len(observed) / len(probes) if probes else None,
                     missing_actor_probe_choices=len(missing_probe_ids), missing_actor_probe_ids=missing_probe_ids,
                     applied_probe_choices=len(applied), unapplied_probe_choices=len(probes) - len(applied),
                     fallback_probe_share_applied=sum(value == "carry_forward" for value in sources.values()) / len(applied) if applied else None,
                     complete_pipeline_pairs=sum(r["assay_dimension"] == "pipeline" and r["complete"] for r in pairs),
                     missing_pipeline_pairs=sum(r["assay_dimension"] == "pipeline" and not r["complete"] for r in pairs),
                     complete_backlog_pairs=sum(r["assay_dimension"] == "backlog" and r["complete"] for r in pairs),
                     missing_backlog_pairs=sum(r["assay_dimension"] == "backlog" and not r["complete"] for r in pairs),
                     actor_pipeline_sensitivity=actor_probe["pipeline_sensitivity"],
                     actor_backlog_sensitivity=actor_probe["backlog_sensitivity"],
                     actor_missing_pipeline_pairs=sum(r["assay_dimension"] == "pipeline" and not r["complete"] for r in actor_pairs),
                     actor_missing_backlog_pairs=sum(r["assay_dimension"] == "backlog" and not r["complete"] for r in actor_pairs),
                     outcome_interpretation="All five primary endpoints describe model plus synthetic fallback policy; actor-only assays remain separate")
    for key in METRICS:
        aggregate["policy_" + key] = aggregate[key]
    for row in roles:
        row["orders_are_applied_policy_actions"] = True
    source_rows = []
    for role in controller.physics.ROLES:
        own = [p for p in probes if p["role"] == role]
        ids = [p.get("probe_id", p.get("id")) for p in own]
        accepted = sum(ident in observed for ident in ids)
        fallback = sum(sources.get(ident) == "carry_forward" for ident in ids)
        source_rows.append(dict(role=role, planned_choices=len(ids), applied_choices=sum(ident in applied for ident in ids),
                                actor_choices=accepted, fallback_choices=fallback,
                                actor_fraction=accepted / len(ids) if ids else None,
                                fallback_fraction=fallback / len(ids) if ids else None))
    table_sets = dict(role_outcomes=roles, probe_pairs=pairs + actor_pairs, probe_regression_residuals=residuals + actor_residuals,
                      probe_diagnostics=diagnostics + actor_diagnostics, probe_answer_sources_by_role=source_rows,
                      knowledge_items=items, latencies=latencies,
                      opportunities=opportunities, applied_actions=payload.get("applied_actions", []))
    return aggregate, table_sets


def load_runs(experiment):
    probe_file, question_file = experiment / "prompts/probes.json", experiment / "prompts/comprehension.json"
    probes = read_json(probe_file) if probe_file.exists() else []
    questions = read_json(question_file) if question_file.exists() else []
    runs, tables = [], defaultdict(list)
    for stage in STAGES:
        for path in sorted((experiment / DATA / stage).glob("*/RESULT.json")):
            raw = path.read_bytes()
            row = dict(stage=stage, result_path=path.relative_to(experiment).as_posix(), run_directory=path.parent.name,
                       result_sha256=hashlib.sha256(raw).hexdigest(), replay_valid=False, replay_error=None, analysis_error=None)
            try:
                payload, case = json.loads(raw.decode("utf-8-sig")), read_json(path.parent / "CASE.json")
                if payload.get("schema_version") != controller.SCHEMA or case.get("schema_version") != controller.SCHEMA:
                    raise ValueError("Carry analysis requires the separately versioned carry schema")
                if (payload.get("timeout_policy") != controller.POLICY or case.get("timeout_policy") != controller.POLICY
                        or payload.get("probe_timeout_policy") != controller.PROBE_POLICY or case.get("probe_timeout_policy") != controller.PROBE_POLICY):
                    raise ValueError("Carry policy binding differs")
                if payload.get("stage") != stage or case.get("stage") != stage:
                    raise ValueError("CASE, RESULT and carry stage directory disagree")
                row.update({key: payload.get(key) for key in ("case_id", "block_id", "arm", "prompt_version", "complete", "stopped",
                           "terminal_reason", "completed_weeks", "planned_weeks", "requested_model", "requested_effort",
                           "actual_model", "actual_effort", "schema_version", "timeout_policy", "probe_timeout_policy", "profile_ids")})
                row.update(case_sha256=controller.digest(case), seed=case.get("seed"),
                           phase_deadline_seconds=case.get("phase_deadline_seconds", {}), source_hashes=payload.get("source_hashes"))
                try:
                    row["replay_valid"] = controller.audit_result(payload, case)["valid"]
                except (ValueError, KeyError, TypeError, IndexError, RuntimeError) as error:
                    row["replay_error"] = str(error)
                row["adherence"] = scoring.adherence_review(path.parent, row["result_sha256"], row["case_sha256"])
                metrics, extracted = extract_metrics(payload, case, fallback_probes=probes, fallback_questions=questions)
                row.update(metrics)
                metadata = {key: row.get(key) for key in ("stage", "case_id", "block_id", "arm", "prompt_version", "replay_valid")}
                for name, values in extracted.items():
                    tables[name].extend(dict(metadata, **value) for value in values)
                for week in payload.get("weeks", []):
                    tables["weeks"].append(dict(metadata, week=week["week"], customer_demand=week["customer_demand"],
                                                 action_source=week["action_source"], actor_orders=week.get("actor_orders"),
                                                 applied_orders=week["orders"], observed_week_cost=week["cost"],
                                                 actor_missing_mask=week.get("actor_missing_mask")))
                row["missing"] = payload.get("missing", {})
            except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
                row["analysis_error"] = str(error)
            runs.append(row)
    return runs, tables


def contrast_analysis(runs, *, stage, plan=None):
    """One block is descriptive; main uses only the complete fixed ten-block plan."""
    own = [r for r in runs if r["stage"] == stage]
    grouped = defaultdict(list)
    for row in own:
        grouped[(row.get("block_id"), row.get("arm"))].append(row)
    duplicates = [key for key, rows in grouped.items() if len(rows) != 1]
    index = {key: rows[0] for key, rows in grouped.items() if len(rows) == 1}
    blocks = sorted({r.get("block_id") for r in own if r.get("block_id")})
    reasons = []
    if stage == "main":
        assigned = plan.get("block_ids", []) if plan else []
        if not plan or len(assigned) != MAIN_N or len(set(assigned)) != MAIN_N:
            reasons.append("A separate frozen carry main plan with ten unique block_ids is required")
        if not plan or plan.get("frozen") is not True or plan.get("independent_blocks_confirmed") is not True:
            reasons.append("Frozen independent fresh-context assignments are not confirmed")
        if (not plan or plan.get("controller_schema") != controller.SCHEMA or plan.get("timeout_policy") != controller.POLICY
                or plan.get("probe_timeout_policy") != controller.PROBE_POLICY):
            reasons.append("The main plan must bind the carry controller schema and selected timeout policy")
        if not plan or not plan.get("prompt_version"):
            reasons.append("The selected main wording is not frozen")
        if len(own) != 30 or any((block, arm) not in index for block in assigned for arm in "ABC"):
            reasons.append("All thirty assigned contexts are required; there is no replacement or completer-only inference")
        if any(block not in assigned or arm not in ("A", "B", "C") for block, arm in grouped):
            reasons.append("Unplanned main context or arm")
        if any(not r.get("replay_valid") or r.get("analysis_error") for r in own):
            reasons.append("Every main context requires a successful carry-controller replay")
        if any(not r.get("adherence", {}).get("passed") for r in own):
            reasons.append("Every main context requires a passing hash-bound external adherence review")
        if any(not r.get("physical_game_complete") or not r.get("procedure_complete")
               or not r.get("applied_probe_answers_complete") or any(r.get(m) is None for m in METRICS) for r in own):
            reasons.append("Complete 24-week policy trajectories and all fixed applied probe endpoints are required")
        if plan and plan.get("prompt_version") and any(r.get("prompt_version") != plan["prompt_version"] for r in own):
            reasons.append("Main wording differs from the frozen plan")
        for block in assigned:
            matched = [index.get((block, arm)) for arm in "ABC"]
            if all(matched) and (len({r.get("seed") for r in matched}) != 1
                                 or len({json.dumps(r.get("profile_ids")) for r in matched}) != 1):
                reasons.append("Matched demand seed or profile-role assignment differs in " + block)
        blocks = assigned
    else:
        reasons.append("Development only: the bounded one-block pilot has no hypothesis p-values")
    if duplicates:
        reasons.append("Duplicate block/arm records are retained; no preferred attempt is selected")
    enabled = stage == "main" and not reasons
    endpoints, contrasts = [], []
    for hypothesis, metric, treated, control, sign in ENDPOINTS:
        differences = []
        for block in blocks:
            a, b = index.get((block, treated)), index.get((block, control))
            if not all(r and r.get("replay_valid") and not r.get("analysis_error") and r.get(metric) is not None for r in (a, b)):
                continue
            delta = a[metric] - b[metric]
            differences.append(delta)
            contrasts.append(dict(stage=stage, hypothesis=hypothesis, metric=metric, units=UNITS[metric], block_id=block,
                                  contrast=treated + "-" + control, treated_value=a[metric], control_value=b[metric], difference=delta,
                                  both_external_reviews_passed=a.get("adherence", {}).get("passed", False) and b.get("adherence", {}).get("passed", False),
                                  interpretation="fixed full main sample" if enabled else "descriptive only; no causal/completer claim"))
        statistics = paired_inference(differences, seed=20261026) if enabled and len(differences) >= 2 else dict(
            n_pairs=len(differences), mean_difference=mean(differences), ci95_low=None, ci95_high=None,
            p_two_sided=None, test="development descriptive only" if stage == "development" else "fixed-sample gate not passed", randomization_draws=0)
        estimate = statistics["mean_difference"]
        endpoints.append(dict(stage=stage, hypothesis=hypothesis, metric=metric, units=UNITS[metric], contrast=treated + "-" + control,
                              predicted_sign=sign, direction="NA" if estimate is None else "zero" if estimate == 0 else
                              "predicted" if sign * estimate > 0 else "opposite", **statistics))
    for row, adjusted in zip(endpoints, holm_adjust([r["p_two_sided"] for r in endpoints])):
        row["p_holm_family_5"] = adjusted
    full_blocks = [block for block in blocks if all(
        index.get((block, arm), {}).get("physical_game_complete") and index.get((block, arm), {}).get("applied_probe_answers_complete")
        and index.get((block, arm), {}).get("replay_valid") and not index.get((block, arm), {}).get("analysis_error") for arm in "ABC")]
    return dict(stage=stage, inference_enabled=enabled, reasons=list(dict.fromkeys(reasons)), assigned_blocks=blocks,
                observed_contexts=len(own), complete_physical_games=sum(r.get("physical_game_complete") is True for r in own),
                complete_actor_cases=sum(r.get("all_actor_responses_complete") is True for r in own),
                complete_primary_blocks=len(full_blocks), endpoints=endpoints, contrasts=contrasts)


def development_readiness(runs, plan):
    """Coverage is a prospective pilot launch gate, never a main-case filter."""
    rows = [r for r in runs if r["stage"] == "development"]
    rule = (plan or {}).get("actor_coverage_gate", {})
    minimum_game, minimum_probe = rule.get("minimum_game_fraction"), rule.get("minimum_probe_fraction")
    valid_rule = (type(minimum_game) in (int, float) and 0 <= minimum_game <= 1
                  and type(minimum_probe) in (int, float) and 0 <= minimum_probe <= 1
                  and rule.get("scope") == "each_development_case")
    checks = []
    for row in rows:
        coverage = valid_rule and row.get("accepted_actor_order_fraction") is not None and row.get("accepted_actor_probe_fraction") is not None
        coverage = bool(coverage and row["accepted_actor_order_fraction"] >= minimum_game and row["accepted_actor_probe_fraction"] >= minimum_probe)
        endpoints = row.get("physical_game_complete") and row.get("applied_probe_answers_complete") and all(row.get(m) is not None for m in METRICS)
        checks.append(dict(case_id=row.get("case_id"), arm=row.get("arm"), actor_coverage_passed=coverage,
                           applied_endpoints_complete=bool(endpoints), reviewed=bool(row.get("adherence", {}).get("passed")),
                           replay_valid=row.get("replay_valid") is True,
                           case_ready=bool(coverage and endpoints and row.get("procedure_complete") and row.get("replay_valid")
                                           and row.get("adherence", {}).get("passed") and not row.get("analysis_error"))))
    expected_block = (plan or {}).get("development", {}).get("block_id")
    assignments = len(rows) == 3 and {r.get("arm") for r in rows} == {"A", "B", "C"} and all(r.get("block_id") == expected_block for r in rows)
    return dict(qualified=bool(valid_rule and assignments and all(c["case_ready"] for c in checks)),
                coverage_rule=rule, rule_valid=valid_rule, assignments_complete=assignments, checks=checks,
                interpretation="Prospective development launch readiness only. Main assigned policy cases are never excluded for low actor coverage.")


def input_fingerprint(experiment):
    paths = [Path(__file__), ROOT / "scripts/report_exp14_carry.py", ROOT / "src/beergame_study/exp14_carry.py",
             ROOT / "scripts/run_exp14_carry.py", ROOT / "src/beergame_study/exp14_analysis.py",
             ROOT / "src/beergame_study/exp14_deadline.py", ROOT / "src/beergame_study/pivot_inference_v2.py",
             ROOT / "src/beergame_study/manual_weekly_v3.py", ROOT / "tests/test_exp14_carry_analysis.py"]
    paths.extend((experiment / "hypotheses").glob("CARRY_FORWARD_V2*"))
    paths.extend(p for p in (experiment / "prompts").glob("*") if p.is_file())
    for stage in STAGES:
        for filename in ("CASE.json", "RESULT.json", "ADHERENCE_REVIEW.json"):
            paths.extend((experiment / DATA / stage).glob("*/" + filename))
    hashes = {(p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)): sha256(p)
              for p in sorted(set(paths)) if p.is_file()}
    return controller.digest(hashes), hashes


def preserve_previous(experiment, fingerprint):
    path = experiment / ANALYSIS / "CURRENT.json"
    if not path.exists():
        return
    old = read_json(path)
    if old.get("fingerprint") == fingerprint:
        return
    for relative in [*old.get("generated_files", {}), (ANALYSIS / "CURRENT.json").as_posix()]:
        source = experiment / relative
        if not source.exists():
            continue
        prefix = next((p for p in (ANALYSIS, REPORTS) if source.is_relative_to(experiment / p)), None)
        if prefix is None or "history" in source.relative_to(experiment / prefix).parts:
            raise ValueError("Carry report manifest references a nonowned artifact")
        target = experiment / prefix / "history" / old["fingerprint"][:16] / source.relative_to(experiment / prefix)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError("Refusing to overwrite a preserved carry publication")
        if not target.exists():
            shutil.copyfile(source, target)


def make_figures(experiment, result):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    folder = experiment / REPORTS / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    generated = []
    def save(fig, stem):
        for ext in ("png", "pdf", "svg"):
            path = folder / (stem + "." + ext)
            fig.savefig(path, dpi=180, bbox_inches="tight")
            generated.append(path)
        plt.close(fig)
    fig, axes = plt.subplots(1, 5, figsize=(14.5, 3.8))
    for ax, endpoint in zip(axes, result["development"]["endpoints"]):
        value = endpoint["mean_difference"]
        ax.set_title(endpoint["hypothesis"] + ": " + endpoint["contrast"], fontsize=12)
        ax.set_ylabel(UNITS[endpoint["metric"]], fontsize=8)
        if value is None:
            ax.text(.5, .52, "NA", transform=ax.transAxes, ha="center", fontsize=23, color="#777777")
            ax.text(.5, .28, "Required paired endpoint\nnot observed", transform=ax.transAxes, ha="center", fontsize=9)
            ax.set(xticks=[], yticks=[])
        else:
            ax.axhline(0, color="#777777", lw=.8)
            ax.bar([0], [value], color="#4477aa", width=.45)
            limit = max(abs(value) * 1.3, .1)
            ax.set(xticks=[0], xticklabels=[f"{endpoint['n_pairs']} paired block"], ylim=(-limit, limit))
            ax.text(.5, .9, f"Contrast: {fmt(value)}", transform=ax.transAxes, ha="center", fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Carry-forward development pilot: signed contrasts only; all p-values NA", fontsize=13)
    fig.text(.08, -.035, "All five quantities are model-plus-fallback policy outcomes; synthetic answers are explicitly identified.\n"
             "One matched block does not establish a causal effect or student-level significance; earlier strict-deadline cases are excluded.", fontsize=9)
    fig.tight_layout(rect=(0, .03, 1, .91))
    save(fig, "development_hypotheses")
    dev = [r for r in result["runs"] if r["stage"] == "development"]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    if dev:
        ordered = sorted(dev, key=lambda r: (r.get("block_id", ""), r.get("arm", "")))
        labels = [r.get("arm", "?") + " / " + r.get("block_id", "?") for r in ordered]
        xs = list(range(len(ordered)))
        ax.bar([x - .18 for x in xs], [r.get("fallback_weeks", 0) for r in ordered], width=.36,
               color="#cc8844", label="Game weeks using carry-forward")
        ax.bar([x + .18 for x in xs], [r.get("expired_probe_pages", 0) for r in ordered], width=.36,
               color="#aa4499", label="Probe pages using role-based fallback")
        ax.set(xticks=xs, xticklabels=labels, ylabel="Resolved timeouts (counts)", ylim=(0, 24))
        ax.legend(fontsize=9)
    else:
        ax.text(.5, .5, "No carry-forward observations saved; N = 0", transform=ax.transAxes, ha="center", fontsize=12)
        ax.set(xticks=[], yticks=[])
    ax.set_title("Fallback supplies applied answers; actor coverage is tracked separately")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    save(fig, "development_timeouts")
    index = folder / "README.md"
    index.write_text("# Carry-forward v2 figures\n\n"
                     "[Five development policy contrasts](development_hypotheses.png) ([PDF](development_hypotheses.pdf), [SVG](development_hypotheses.svg)). All quantities include the selected synthetic fallback policy. NA means the required applied trajectory or paired context is not yet complete.\n\n"
                     "[Timeout counts](development_timeouts.png) ([PDF](development_timeouts.pdf), [SVG](development_timeouts.svg)). Both game and probe timeouts receive explicit fallback answers; actor absences remain flagged.\n\n"
                     "No sample-size curve or significance claim is based on this one-block pilot. [Current report](../REPORT.md).\n", encoding="utf-8")
    generated.append(index)
    return generated


def report_markdown(result):
    dev, main = result["development"], result["main"]
    rows = [r for r in result["runs"] if r["stage"] == "development"]
    missing_h = [r["hypothesis"] for r in dev["endpoints"] if r["mean_difference"] is None]
    lines = ["# Experiment 14: carry-forward policy", "",
             "1. **Selected policy: repeat the previous applied four-role order packet when a game deadline expires.** "
             "A first-week timeout uses [4, 4, 4, 4]. On a probe timeout, each scenario receives its role's last applied game order. "
             "Every resolved opportunity therefore has an applied answer. Fallback answers are labeled synthetic; valid on-time model choices are unchanged.",
             f"2. New development pilot: **{dev['complete_physical_games']}/3 complete 24-week policy games** and "
             f"**{dev['complete_actor_cases']}/3 cases with all actor responses complete**; {dev['observed_contexts']}/3 contexts saved. "
             "Finishing the physical game does not mean every model response was received.",
             "3. **All five primary quantities describe the model-plus-fallback policy.** Development contrasts are descriptive only; raw and adjusted p-values are NA. "
             + ("Unavailable paired quantities: " + ", ".join(missing_h) + "." if missing_h else "All five paired quantities are available for this one block; none is a significance finding."),
             f"4. Main: {main['observed_contexts']}/30 contexts, {main['complete_primary_blocks']}/10 complete matched primary blocks. "
             + ("The complete fixed-sample inference gate passed." if main["inference_enabled"] else
                "Main inference remains blocked until the separate frozen ten-block plan, full fixed endpoints and external reviews pass."), "",
             "A = control reading with adequate deadlines; B = the same control reading with restricted deadlines; "
             "C = education reading with the same restricted deadlines as B. This amendment uses V1: A allows 30 seconds for both phases; "
             "B/C allow 4.0 seconds per game week and 3.8 seconds per probe page, inherited from latency-only calibration. "
             "The clock includes service, transport, scheduling and output, not measured hidden thinking time. Post-task questions are untimed.", "",
             "Requested model: gpt-6-astra / xhigh, fresh isolated contexts. Actual reported labels remain separate in the case table. "
             "Temperature and reasoning-token allocation are not exposed. Human participants: 0. One matched chain block supplies one paired contrast; four roles and 24 weeks do not increase independent N.", "",
             "[Figures](figures/README.md) | [Case outcomes](../../analysis/carry_forward_v2/tables/case_outcomes.csv) | "
             "[Validation](../../analysis/carry_forward_v2/VALIDATION.json)", "",
             "## Model responses and fallback actions", "",
             "| Arm / block | Policy weeks | Actor orders / 96 | Actor game fraction | Carry weeks / applied | Actor probes / 32 | Quiz |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for row in rows:
        lines.append("| " + " | ".join([str(row.get("arm")) + " / " + str(row.get("block_id")), fmt(row.get("completed_weeks")),
                     fmt(row.get("accepted_actor_order_count")) + "/96", fmt(row.get("accepted_actor_order_fraction")),
                     fmt(row.get("fallback_weeks")) + "/" + fmt(row.get("completed_weeks")), fmt(row.get("accepted_actor_probe_choices")) + "/32",
                     fmt(row.get("knowledge_correct")) + "/" + fmt(row.get("knowledge_items")) if row.get("knowledge_correct") is not None else "NA"]) + " |")
    if not rows:
        lines.append("| No saved development cases | NA | NA | NA | NA | NA | NA |")
    lines.extend(["", "Actor fraction divides accepted actor orders by the planned 96 orders per context. Carry share uses physically applied weeks; "
                  "unresolved future weeks are reported separately in the CSV. A probe fallback repeats the last applied game order of the displayed role; "
                  "it never borrows another hypothetical scenario's answer. Quiz answers still come from the actor and remain NA until received. "
                  "[Applied actions](../../analysis/carry_forward_v2/tables/applied_actions.csv), "
                  "[all resolved opportunities](../../analysis/carry_forward_v2/tables/opportunities.csv) and "
                  "[submission timings](../../analysis/carry_forward_v2/tables/latencies.csv) keep their sources distinct.", "",
                  "## Five hypothesis quantities", "",
                  "| Endpoint | Plain definition and units | Contrast; predicted sign |",
                  "|---|---|---|",
                  "| H1 | How much the applied scenario order falls per extra case already on the way, averaged equally over eight fixed pipeline pairs; policy ordered cases per outstanding case | B-A; negative |",
                  "| H2 | Four-role total holding plus backlog cost over 24 weeks under model choices plus carry-forward; policy cost units per chain | B-A; positive |",
                  "| H3 | The same applied-policy pipeline response measure, comparing education with control under restricted deadlines | C-B; positive |",
                  "| H4a | Sample variance of the 24 applied weekly orders within each role (denominator 23), averaged over four roles; policy order cases squared | C-B; negative |",
                  "| H4b | Role order variance divided by the same chain's external-customer sample demand variance, then averaged over roles; policy bullwhip ratio | C-B; negative |", "",
                  "All H1-H4 quantities measure the model-plus-fallback policy. A smaller order variance can arise mechanically when an earlier order is repeated; "
                  "a zero pipeline slope can arise mechanically when the same role's game order answers both hypothetical scenarios. Neither identifies pure actor cognition. "
                  "Holding costs 0.5 per remaining case per week; backlog costs 1 per unfilled case per week. A prefix has no full 24-week H2/H4 outcome. "
                  "Zero customer-demand variance makes H4b undefined. H4a/H4b share a numerator and are not independent confirmations.", "",
                  "## Development contrasts", "",
                  "| Test | Pairs | Signed contrast | Units | Raw p | Holm 5 | Direction |",
                  "|---|---:|---:|---|---:|---:|---|"])
    for row in dev["endpoints"]:
        lines.append("| " + " | ".join([row["hypothesis"] + " " + row["contrast"], str(row["n_pairs"]), fmt(row["mean_difference"]), row["units"],
                     fmt(row["p_two_sided"]), fmt(row["p_holm_family_5"]), row["direction"]]) + " |")
    lines.extend(["", "The primary pipeline aggregate uses all eight fixed applied-answer pairs with equal weight. "
                  "The separate actor-only aggregate requires all eight pairs of accepted actor answers; otherwise it is NA, without reweighting or using defaults. "
                  "[Pair slopes](../../analysis/carry_forward_v2/tables/probe_pairs.csv) and "
                  "[role/zero-response diagnostics](../../analysis/carry_forward_v2/tables/probe_diagnostics.csv) also show the separate eight-pair backlog response assay. "
                  "Pipeline response is a proxy, not an identified normative underweighting coefficient; flat choices in both assays do not establish pipeline-specific neglect. "
                  "Two levels per pair cannot identify curvature. Quiz scores are manipulation checks, never inclusion rules based on low performance.", "",
                  "| Arm | Policy pipeline slope | Actor-only pipeline slope | Actor pairs absent / 8 | Probe fallback fraction |",
                  "|---|---:|---:|---:|---:|"])
    for row in rows:
        lines.append("| " + " | ".join([str(row.get("arm")), fmt(row.get("pipeline_sensitivity")), fmt(row.get("actor_pipeline_sensitivity")),
                     fmt(row.get("actor_missing_pipeline_pairs")) + "/8", fmt(row.get("fallback_probe_share_applied"))]) + " |")
    if not rows:
        lines.append("| No saved development cases | NA | NA | NA | NA |")
    rule = result["development_readiness"]["coverage_rule"]
    lines.extend(["", "[Fallback fractions by role](../../analysis/carry_forward_v2/tables/probe_answer_sources_by_role.csv) "
                  "and the pair table distinguish actor and synthetic answers at each source. Late raw submissions remain in the record and never overwrite an applied answer.", "",
                  "## Development readiness", "",
                  "Current readiness: **" + ("qualified" if result["development_readiness"]["qualified"] else "not qualified") + "**. "
                  + (f"The prospective launch gate requires at least {100 * rule['minimum_game_fraction']:g}% accepted actor game orders and "
                     f"{100 * rule['minimum_probe_fraction']:g}% accepted actor probe choices in every development case, plus complete applied endpoints and reviews. "
                     if result["development_readiness"]["rule_valid"] else "The prospective actor-coverage gate has not yet been frozen in the saved plan. ")
                  + "This gate is checked before launching a new main sample. Once main cases are assigned, low actor coverage is reported as a diagnostic; "
                  "it never removes assigned cases or valid complete policy contrasts.", "",
                  "## Main status and provenance", "",
                  "A main test requires exactly ten matched independent blocks, all thirty assigned contexts, complete 24-week policy trajectories, all fixed primary endpoints "
                  "and passing external reviews bound to exact RESULT bytes and the canonical CASE digest. Synthetic game and probe fallbacks are valid components of the selected policy outcome. "
                  "No actor-coverage threshold excludes assigned main cases; low coverage instead limits cognitive interpretation. "
                  "Use the separately frozen CARRY_FORWARD_V2_MAIN_PLAN.json, never the earlier strict-deadline plan. "
                  "Tests, when eligible, use two-sided paired sign flips with a five-endpoint Holm family and unadjusted paired-block bootstrap intervals. "
                  "The independent symmetric/exchangeable paired-null assumption remains necessary; ten blocks do not guarantee significance. "
                  "Missing or opposite results are retained; no significance-driven extension, replacement or prompt selection is allowed.", ""])
    if main["inference_enabled"]:
        lines.extend(["| Main test | Paired blocks | Main contrast | 95% interval | Raw p | Holm 5 |",
                      "|---|---:|---:|---|---:|---:|"])
        for row in main["endpoints"]:
            lines.append("| " + " | ".join([row["hypothesis"], str(row["n_pairs"]), fmt(row["mean_difference"]),
                         fmt(row["ci95_low"]) + " to " + fmt(row["ci95_high"]), fmt(row["p_two_sided"]), fmt(row["p_holm_family_5"])]) + " |")
        lines.append("")
    lines.extend(["This report reads only data/carry_forward_v2/development and data/carry_forward_v2/main. "
                  "The original sixteen strict-deadline cases remain separate and unchanged. Public transcript review is operator-attested evidence, not provider authentication or a hidden reasoning trace. "
                  "No participant or API requests are made by this analysis.", "",
                  "Rebuild: `.venv/Scripts/python.exe scripts/report_exp14_carry.py`. "
                  "[Exact source/data hashes and validation](../../analysis/carry_forward_v2/VALIDATION.json). Input fingerprint: `" + result["fingerprint"] + "`. "
                  "Previous generated bytes are preserved in this amendment's history folders before regeneration.", "",
                  "## Development figures", "",
                  "![Five development hypothesis contrasts](figures/development_hypotheses.png)", "",
                  "NA is an unavailable paired applied-policy endpoint, not a zero effect. All five quantities include synthetic fallback answers. All pilot p-values remain NA.", "",
                  "![Timeout counts](figures/development_timeouts.png)", "",
                  "Game fallback weeks and probe fallback pages are different opportunities; each probe page supplies four applied answers while retaining the actor-missing flag.", ""])
    return "\n".join(lines)


def make_pdf(path, markdown):
    """Reuse the established readable renderer without touching its source."""
    # This pure formatter reads only the supplied amendment Markdown and its
    # relative figures. It does not load, alter, or pool the prior study.
    scoring.make_pdf(path, markdown)
    from io import BytesIO
    from pypdf import PdfWriter
    document = PdfWriter(clone_from=BytesIO(path.read_bytes()))
    document.add_metadata({"/Title": "Experiment 14: carry-forward policy", "/Subject": "Separate model-plus-fallback policy development report"})
    with path.open("wb") as stream:
        document.write(stream)


def generate_report(experiment=EXPERIMENT):
    experiment = Path(experiment).resolve()
    fingerprint, hashes = input_fingerprint(experiment)
    current = experiment / ANALYSIS / "CURRENT.json"
    if current.exists():
        prior = read_json(current)
        if prior.get("fingerprint") == fingerprint and all((experiment / p).is_file() and sha256(experiment / p) == digest
                                                          for p, digest in prior.get("generated_files", {}).items()):
            return read_json(experiment / ANALYSIS / "RESULTS.json")
    for _ in range(5):
        fingerprint, hashes = input_fingerprint(experiment)
        runs, tables = load_runs(experiment)
        plan_path = experiment / "hypotheses/CARRY_FORWARD_V2_MAIN_PLAN.json"
        main_plan = read_json(plan_path) if plan_path.exists() else None
        development_plan_path = experiment / "hypotheses/CARRY_FORWARD_V2_PLAN.json"
        development_plan = read_json(development_plan_path) if development_plan_path.exists() else None
        if input_fingerprint(experiment)[0] == fingerprint:
            break
    else:
        raise RuntimeError("Carry inputs changed during five snapshot attempts; rerun report")
    preserve_previous(experiment, fingerprint)
    result = dict(schema_version=SCHEMA, generated_utc=datetime.now(timezone.utc).isoformat(), fingerprint=fingerprint,
                  source_and_input_hashes=hashes, controller_schema=controller.SCHEMA, timeout_policy=controller.POLICY,
                  probe_timeout_policy=controller.PROBE_POLICY,
                  runs=runs, development=contrast_analysis(runs, stage="development"),
                  development_readiness=development_readiness(runs, development_plan),
                  main=contrast_analysis(runs, stage="main", plan=main_plan), human_participants=0)
    tables.update(case_outcomes=runs, development_endpoints=result["development"]["endpoints"],
                  development_contrasts=result["development"]["contrasts"], main_endpoints=result["main"]["endpoints"],
                  main_contrasts=result["main"]["contrasts"])
    for name in ("role_outcomes", "probe_pairs", "probe_regression_residuals", "probe_diagnostics", "probe_answer_sources_by_role", "knowledge_items", "latencies",
                 "opportunities", "applied_actions", "weeks"):
        tables.setdefault(name, [])
    generated = []
    for name, rows in sorted(tables.items()):
        path = experiment / ANALYSIS / "tables" / (name + ".csv")
        scoring.csv_write(path, rows)
        generated.append(path)
    results_path = experiment / ANALYSIS / "RESULTS.json"
    write_json(results_path, result)
    generated.append(results_path)
    generated.extend(make_figures(experiment, result))
    report = experiment / REPORTS / "REPORT.md"
    markdown = report_markdown(result)
    report.write_text(markdown, encoding="utf-8")
    generated.append(report)
    pdf = experiment / REPORTS / "REPORT.pdf"
    make_pdf(pdf, markdown)
    generated.append(pdf)
    for prefix, text in ((ANALYSIS, "[Current results](RESULTS.json) · [Derived tables](tables/) · [Validation](VALIDATION.json)"),
                         (REPORTS, "[Current report](REPORT.md) · [PDF](REPORT.pdf) · [Figures](figures/README.md)")):
        path = experiment / prefix / "README.md"
        path.write_text("# Carry-forward v2\n\n" + text + "\n\nRebuild offline with `.venv/Scripts/python.exe scripts/report_exp14_carry.py`. "
                        "Earlier strict-deadline observations are excluded. Previous amendment outputs are preserved under history by input fingerprint.\n", encoding="utf-8")
        generated.append(path)
    validation = dict(schema_version=SCHEMA, fingerprint=fingerprint, source_and_input_hashes=hashes,
                      scanned_paths=[(DATA / s / "*/RESULT.json").as_posix() for s in STAGES], records=len(runs),
                      replay_valid=sum(r.get("replay_valid") is True for r in runs),
                      reviewed=sum(r.get("adherence", {}).get("passed") is True for r in runs),
                      errors=[dict(result_path=r["result_path"], replay_error=r.get("replay_error"), analysis_error=r.get("analysis_error"))
                              for r in runs if not r.get("replay_valid") or r.get("analysis_error")],
                      main_inference_enabled=result["main"]["inference_enabled"], main_gate_reasons=result["main"]["reasons"],
                      synthetic_fallbacks_are_not_model_observations=True, applied_probe_fallbacks_explicit=True,
                      actor_only_probe_answers_imputed=False, development_readiness=result["development_readiness"],
                      generated_files={p.relative_to(experiment).as_posix(): sha256(p) for p in generated})
    receipt = experiment / ANALYSIS / "VALIDATION.json"
    write_json(receipt, validation)
    generated.append(receipt)
    write_json(current, dict(schema_version=SCHEMA, fingerprint=fingerprint, report=report.relative_to(experiment).as_posix(),
                             generated_files={p.relative_to(experiment).as_posix(): sha256(p) for p in generated}))
    return result
