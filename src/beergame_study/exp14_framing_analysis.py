"""Separate offline analysis of fictional student time-pressure framing.

The 120/8-second framing is not a model runtime deadline. Every scored order is
an accepted model choice. No strict-deadline or carry-forward sample is pooled.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

from . import exp14_analysis as scoring
from . import exp14_framing as controller
from .pivot_inference_v2 import ENDPOINTS, paired_inference, holm_adjust

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/14_deadline_student_20261026"
DATA = Path("data/student_framing_v3")
ANALYSIS = Path("analysis/student_framing_v3")
REPORTS = Path("reports/student_framing_v3")
SCHEMA = "exp14-student-framing-analysis-v1"
STAGES = ("development", "main")
METRICS = tuple(dict.fromkeys(e[1] for e in ENDPOINTS))
UNITS = dict(pipeline_sensitivity="ordered cases / outstanding case", chain_total_cost="cost units / chain",
             mean_role_order_variance="order cases squared", mean_role_bullwhip="variance ratio")
read_json, write_json, sha256, fmt, mean = scoring.read_json, scoring.write_json, scoring.sha256, scoring.fmt, scoring.mean


def extract_metrics(payload, case, *, fallback_probes=(), fallback_questions=()):
    game, roles = scoring.game_metrics(payload)
    probes = scoring.scoring_bank(case, "probes", fallback_probes)
    probe, pairs, residuals, diagnostics = scoring.probe_metrics(probes, payload.get("probe_answers", {}))
    questions = scoring.scoring_bank(case, "comprehension", fallback_questions)
    knowledge, items = scoring.knowledge_metrics(questions, payload.get("comprehension_answers"))
    timing, latencies = scoring.timing_metrics(payload)
    record = dict(game, **probe, **knowledge, **timing,
                  complete_primary_endpoints=game["complete_24_weeks"] and len(payload.get("probe_answers", {})) == 32
                  and all(value is not None for value in (probe["pipeline_sensitivity"], game["chain_total_cost"],
                                                          game["mean_role_order_variance"], game["mean_role_bullwhip"])),
                  complete_pipeline_pairs=sum(p["assay_dimension"] == "pipeline" and p["complete"] for p in pairs),
                  missing_pipeline_pairs=sum(p["assay_dimension"] == "pipeline" and not p["complete"] for p in pairs),
                  complete_backlog_pairs=sum(p["assay_dimension"] == "backlog" and p["complete"] for p in pairs),
                  all_scored_choices_are_actual_model_responses=True)
    return record, dict(role_outcomes=roles, probe_pairs=pairs, probe_regression_residuals=residuals,
                        probe_diagnostics=diagnostics, knowledge_items=items, latencies=latencies)


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
                    raise ValueError("Only the separate fictional-pressure controller schema is eligible")
                if payload.get("stage") != stage or case.get("stage") != stage:
                    raise ValueError("CASE, RESULT and stage directory disagree")
                if case.get("model_runtime_limit_seconds") is not None or case.get("deadline_seconds") is not None:
                    raise ValueError("Fictional framing cannot be analyzed as a physical model deadline")
                row.update({key: payload.get(key) for key in ("case_id", "block_id", "arm", "prompt_version", "complete", "stopped",
                           "terminal_reason", "completed_weeks", "planned_weeks", "requested_model", "requested_effort",
                           "actual_model", "actual_effort", "profile_ids", "fictional_student_seconds", "model_runtime_limit_seconds")})
                row.update(case_sha256=controller.digest(case), seed=case.get("seed"), source_hashes=payload.get("source_hashes"))
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
                                                 actual_model_orders=week["orders"], observed_week_cost=week["cost"]))
                row["missing"] = payload.get("missing", {})
            except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
                row["analysis_error"] = str(error)
            runs.append(row)
    return runs, tables


def _statistics(values, allow_inference):
    if allow_inference and len(values) >= 2:
        return paired_inference(values, seed=20261026)
    return dict(n_pairs=len(values), mean_difference=mean(values), ci95_low=None, ci95_high=None,
                p_two_sided=None, test="descriptive only", randomization_draws=0)


def analyze_stage(runs, *, stage, plan=None):
    own = [row for row in runs if row["stage"] == stage]
    grouped = defaultdict(list)
    for row in own:
        grouped[(row.get("block_id"), row.get("arm"))].append(row)
    duplicates = [key for key, rows in grouped.items() if len(rows) != 1]
    index = {key: rows[0] for key, rows in grouped.items() if len(rows) == 1}
    blocks = sorted({r.get("block_id") for r in own if r.get("block_id")})
    reasons = []
    if stage == "main":
        blocks = (plan or {}).get("block_ids", [])
        if len(blocks) != 10 or len(set(blocks)) != 10:
            reasons.append("A separately frozen framing main plan with exactly ten unique assigned blocks is required")
        if not plan or plan.get("frozen") is not True or plan.get("independent_blocks_confirmed") is not True:
            reasons.append("Frozen independent fresh-context assignments are not confirmed")
        if not plan or plan.get("controller_schema") != controller.SCHEMA or not plan.get("prompt_version"):
            reasons.append("The main plan must bind the fictional-pressure schema and selected wording")
        if len(own) != 30 or any((block, arm) not in index for block in blocks for arm in "ABC"):
            reasons.append("All thirty assigned contexts are required; no preferred or replacement attempts")
        if any(block not in blocks or arm not in ("A", "B", "C") for block, arm in grouped):
            reasons.append("Unplanned main context or arm")
        if any(not r.get("replay_valid") or r.get("analysis_error") or not r.get("complete")
               or not r.get("complete_primary_endpoints") for r in own):
            reasons.append("Every main context must replay and complete its actual-response protocol and all fixed primary endpoints")
        if any(not r.get("adherence", {}).get("passed") for r in own):
            reasons.append("Passing external reviews must bind every current RESULT and CASE")
        if plan and plan.get("prompt_version") and any(r.get("prompt_version") != plan["prompt_version"] for r in own):
            reasons.append("Main wording differs from the frozen plan")
        for block in blocks:
            matched = [index.get((block, arm)) for arm in "ABC"]
            if all(matched) and (len({r.get("seed") for r in matched}) != 1
                                 or len({json.dumps(r.get("profile_ids")) for r in matched}) != 1):
                reasons.append("Matched demand seed or profile-role assignments differ within " + block)
    else:
        reasons.append("One development block is descriptive and never enters main inference")
    if duplicates:
        reasons.append("Duplicate block/arm records are retained without selecting an attempt")
    enabled = stage == "main" and not reasons
    endpoints, contrasts, prefixes = [], [], []
    for hypothesis, metric, treated, control, direction in ENDPOINTS:
        paired = {}
        for block in blocks:
            a, b = index.get((block, treated)), index.get((block, control))
            if not all(r and r.get("replay_valid") and not r.get("analysis_error") and r.get(metric) is not None for r in (a, b)):
                continue
            difference = a[metric] - b[metric]
            paired[block] = difference
            contrasts.append(dict(stage=stage, hypothesis=hypothesis, metric=metric, units=UNITS[metric], block_id=block,
                                  contrast=treated + "-" + control, treated_value=a[metric], control_value=b[metric], difference=difference,
                                  both_reviews_passed=a.get("adherence", {}).get("passed", False) and b.get("adherence", {}).get("passed", False),
                                  interpretation="full fixed main sample" if enabled else "descriptive only; no completer-only causal claim"))
        statistics = _statistics(list(paired.values()), enabled)
        value = statistics["mean_difference"]
        endpoints.append(dict(hypothesis=hypothesis, metric=metric, units=UNITS[metric], contrast=treated + "-" + control,
                              predicted_sign=direction, direction="NA" if value is None else "zero" if value == 0 else
                              "predicted" if value * direction > 0 else "opposite", **statistics))
        if stage == "main":
            for n in range(1, 11):
                requested = blocks[:n]
                complete_prefix = len(requested) == n and all(b in paired for b in requested)
                values = [paired[b] for b in requested] if complete_prefix else []
                # Prefix p-values appear only after the full fixed main gate,
                # never as an interim stop/launch/selection signal.
                prefix_stats = _statistics(values, enabled and n >= 2)
                prefixes.append(dict(hypothesis=hypothesis, metric=metric, contrast=treated + "-" + control,
                                     prefix_size=n, complete_prefix=complete_prefix, full_main_gate_passed=enabled,
                                     interpretation="fixed-order descriptive sensitivity; n=10 is primary", **prefix_stats))
    for row, adjusted in zip(endpoints, holm_adjust([r["p_two_sided"] for r in endpoints])):
        row["p_holm_family_5"] = adjusted
    complete_blocks = [block for block in blocks if all(index.get((block, arm), {}).get("complete_primary_endpoints")
                        and index.get((block, arm), {}).get("replay_valid") for arm in "ABC")]
    return dict(stage=stage, inference_enabled=enabled, gate_reasons=list(dict.fromkeys(reasons)), assigned_blocks=blocks,
                saved_contexts=len(own), complete_contexts=sum(r.get("complete") is True for r in own),
                complete_games=sum(r.get("complete_24_weeks") is True for r in own), complete_blocks=len(complete_blocks),
                endpoints=endpoints, contrasts=contrasts, prefixes=prefixes)


def input_fingerprint(experiment):
    paths = [Path(__file__), ROOT / "scripts/report_exp14_framing.py", ROOT / "src/beergame_study/exp14_framing.py",
             ROOT / "scripts/run_exp14_framing.py", ROOT / "src/beergame_study/exp14_analysis.py",
             ROOT / "src/beergame_study/exp14_deadline.py", ROOT / "src/beergame_study/pivot_inference_v2.py",
             ROOT / "src/beergame_study/manual_weekly_v3.py", ROOT / "tests/test_exp14_framing_analysis.py"]
    paths.extend((experiment / "hypotheses").glob("STUDENT_FRAMING_V3*"))
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
            raise ValueError("Framing manifest references a nonowned artifact")
        target = experiment / prefix / "history" / old["fingerprint"][:16] / source.relative_to(experiment / prefix)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError("Refusing to overwrite preserved framing publication")
        if not target.exists():
            shutil.copyfile(source, target)


def make_figures(experiment, result):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    folder = experiment / REPORTS / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    generated = []
    def save(fig, name):
        for ext in ("png", "pdf", "svg"):
            path = folder / (name + "." + ext)
            fig.savefig(path, dpi=180, bbox_inches="tight")
            generated.append(path)
        plt.close(fig)
    for stage in STAGES:
        fig, axes = plt.subplots(1, 5, figsize=(14.5, 3.7))
        for ax, endpoint in zip(axes, result[stage]["endpoints"]):
            own = [r for r in result[stage]["contrasts"] if r["hypothesis"] == endpoint["hypothesis"]]
            ax.set_title(endpoint["hypothesis"] + " " + endpoint["contrast"], fontsize=12)
            ax.set_ylabel(UNITS[endpoint["metric"]], fontsize=8)
            if own:
                values = [r["difference"] for r in own]
                ax.scatter(range(1, len(values) + 1), values, color="#4477aa", s=35)
                ax.axhline(0, color="#888888", lw=.8)
                ax.axhline(endpoint["mean_difference"], color="#aa4477", lw=1.2)
                ax.set_xlabel("Independent matched block", fontsize=8)
                ax.set_xticks(range(1, len(values) + 1))
            else:
                ax.text(.5, .55, "NA", transform=ax.transAxes, ha="center", fontsize=24, color="#777777")
                ax.text(.5, .3, "No complete paired\nendpoint observed", transform=ax.transAxes, ha="center", fontsize=9)
                ax.set(xticks=[], yticks=[])
            ax.spines[["top", "right"]].set_visible(False)
        status = "descriptive; p = NA" if stage == "development" else "fixed-sample inference" if result[stage]["inference_enabled"] else "descriptive; main inference withheld"
        fig.suptitle("Simulated student time pressure — " + stage + " contrasts (" + status + ")", fontsize=12)
        fig.tight_layout(rect=(0, 0, 1, .9))
        save(fig, stage + "_hypotheses")
    fig, axes = plt.subplots(2, 5, figsize=(14.5, 6.2))
    for column, endpoint in enumerate(result["main"]["endpoints"]):
        own = [r for r in result["main"]["prefixes"] if r["hypothesis"] == endpoint["hypothesis"]]
        for axis, field in ((axes[0, column], "mean_difference"), (axes[1, column], "p_two_sided")):
            available = [r for r in own if r[field] is not None]
            if available:
                axis.plot([r["prefix_size"] for r in available], [r[field] for r in available], marker="o", color="#4477aa")
            else:
                axis.text(.5, .5, "NA — no eligible data", transform=axis.transAxes, ha="center", fontsize=8)
            axis.set(xlim=(.7, 10.3), xticks=range(1, 11))
            axis.tick_params(labelsize=7)
            axis.spines[["top", "right"]].set_visible(False)
        axes[0, column].set_title(endpoint["hypothesis"] + " " + endpoint["contrast"])
        axes[0, column].set_ylabel("Signed mean effect", fontsize=9)
        axes[1, column].set(ylabel="Raw two-sided p", xlabel="Fixed prefix of independent blocks", ylim=(0, 1.05))
    fig.suptitle("Main fixed-order prefix sensitivity: N = 10 is primary; no significance stopping", fontsize=13)
    fig.text(.07, -.025, "Prefix p-values appear only after all ten planned blocks pass the full main gate; n < 2 is NA.\n"
             "Curves describe observed prefixes, not predicted crossings, required sample sizes, or permission to select a favorable N.", fontsize=9)
    fig.tight_layout(rect=(0, .02, 1, .92))
    save(fig, "main_chain_prefixes")
    index = folder / "README.md"
    index.write_text("# Simulated student time-pressure figures\n\n"
                     "[Development H1–H4 contrasts](development_hypotheses.png) ([PDF](development_hypotheses.pdf), [SVG](development_hypotheses.svg)). One matched block is descriptive; p-values stay NA.\n\n"
                     "[Main H1–H4 contrasts](main_hypotheses.png) ([PDF](main_hypotheses.pdf), [SVG](main_hypotheses.svg)). Each dot is a matched independent block.\n\n"
                     "[Main chain-prefix sensitivity](main_chain_prefixes.png) ([PDF](main_chain_prefixes.pdf), [SVG](main_chain_prefixes.svg)). N=10 is primary; no significance-based stopping or sample-size prediction.\n\n"
                     "NA panels contain no fabricated observations. [Current report](../REPORT.md).\n", encoding="utf-8")
    generated.append(index)
    return generated


def report_markdown(result):
    dev, main = result["development"], result["main"]
    lines = ["# Simulated student time pressure", "",
             "1. **The treatment is fictional student time-pressure framing: 120 seconds in A versus 8 seconds in B/C.** "
             "The model has no actual runtime or response-admission deadline. Every scored game order and probe answer is an accepted model choice; no defaults or carry-forward actions are used.",
             f"2. Development: {dev['saved_contexts']}/3 fresh contexts saved, {dev['complete_games']}/3 complete 24-week games, "
             f"{dev['complete_blocks']}/1 complete matched block. Development effects are descriptive; all development p-values are NA.",
             f"3. Main: {main['saved_contexts']}/30 contexts saved; **{main['complete_blocks']}/10 complete matched blocks**. "
             + ("The fixed main-sample inference gate passed." if main["inference_enabled"] else "Main hypothesis inference remains withheld until the full fixed sample and external reviews pass."),
             "4. This measures model responses to a classroom framing, not real student behavior, actual thinking time, or a verified cognitive time limit. "
             "Four roles and 24 weeks are repeated observations within a context. The independent main sample is ten matched chain blocks, not forty students.", "",
             "A receives the control reading and the 120-second student framing. B receives the same control reading and the 8-second framing. "
             "C receives the education reading and the same 8-second framing as B. All arms use one accepted choice per decision; "
             "post-task questions follow the game and 32 probes. Requested model/effort is gpt-6-astra / xhigh. Actual reported labels remain separate; temperature and hidden reasoning-token allocation are not exposed.", "",
             "[Figures](figures/README.md) | [Case outcomes](../../analysis/student_framing_v3/tables/case_outcomes.csv) | "
             "[Validation](../../analysis/student_framing_v3/VALIDATION.json)", "",
             "## Five hypothesis quantities", "",
             "| Endpoint | Plain definition and units | Contrast; predicted sign |", "|---|---|---|",
             "| H1 | How much the order falls per extra case already on the way, averaged equally over eight fixed pipeline pairs; ordered cases per outstanding case | B-A; negative |",
             "| H2 | Holding plus backlog cost across four roles and all 24 weeks; game cost units per chain | B-A; positive |",
             "| H3 | The same pipeline-response measure, comparing education with control under the 8-second student framing | C-B; positive |",
             "| H4a | Sample variance of weekly orders within each role (denominator 23), averaged over four roles; order cases squared | C-B; negative |",
             "| H4b | Role order variance divided by the chain's external-customer sample demand variance, averaged over roles; dimensionless bullwhip ratio | C-B; negative |", "",
             "Holding costs 0.5 per remaining case per week; backlog costs 1 per unfilled case per week. Partial trajectories have no complete-horizon H2/H4 estimate. "
             "H4b is undefined if customer-demand variance is zero. H4a/H4b share their numerator and are not independent confirmations. "
             "The pipeline assay is a responsiveness proxy, not an identified normative underweighting coefficient; flat answers in both pipeline and backlog assays do not establish pipeline-specific neglect.", ""]
    for stage in STAGES:
        lines.extend(["## " + stage.title() + " contrasts", "",
                      "| Test | Pairs | Signed contrast | 95% interval | Raw two-sided p | Holm 5 | Direction |",
                      "|---|---:|---:|---|---:|---:|---|"])
        for row in result[stage]["endpoints"]:
            lines.append("| " + " | ".join([row["hypothesis"] + " " + row["contrast"], str(row["n_pairs"]), fmt(row["mean_difference"]),
                         fmt(row["ci95_low"]) + " to " + fmt(row["ci95_high"]), fmt(row["p_two_sided"]), fmt(row["p_holm_family_5"]), row["direction"]]) + " |")
        lines.append("")
    lines.extend(["NA means no complete paired endpoint or inference deliberately withheld. Available-pair contrasts before the full main gate are descriptive only; "
                  "they do not justify a completer-only causal claim. Significant opposite effects, if observed in the completed main sample, remain opposite evidence.", "",
                  "## Completion, comprehension and source checks", "",
                  "| Stage / arm / block | Weeks | Pipeline pairs / 8 | Post-task score | Replay | Review |",
                  "|---|---:|---:|---:|---|---|"])
    for row in result["runs"]:
        lines.append("| " + " | ".join([" / ".join(str(row.get(k)) for k in ("stage", "arm", "block_id")), fmt(row.get("completed_weeks")),
                     fmt(row.get("complete_pipeline_pairs")) + "/8", fmt(row.get("knowledge_correct")) + "/" + fmt(row.get("knowledge_items"))
                     if row.get("knowledge_correct") is not None else "NA", "pass" if row.get("replay_valid") else "pending/fail",
                     "pass" if row.get("adherence", {}).get("passed") else "pending/fail"]) + " |")
    if not result["runs"]:
        lines.append("| No saved framing cases | NA | NA | NA | NA | NA |")
    lines.extend(["", "All readings, hypothetical states, actual choices and public transcripts remain source records. "
                  "[Pair/role diagnostics](../../analysis/student_framing_v3/tables/probe_diagnostics.csv) retain zero choices, zero slopes, extremes and separate backlog response. "
                  "[Pair slopes](../../analysis/student_framing_v3/tables/probe_pairs.csv) keep all eight fixed pipeline pairs; an absent pair makes the aggregate unavailable rather than changing its weights. "
                  "Two levels within a pair cannot identify curvature. Comprehension is scored after behavior; low scores never select individual main cases. "
                  "Recorded wall latency includes transport and scheduling and is observational, never a response-admission cutoff.", "",
                  "## Fixed main inference and prefix curves", "",
                  "Only the complete frozen ten-block main sample receives primary two-sided paired sign-flip inference, with Holm correction across five endpoints. "
                  "Pointwise 95% intervals use 10,000 paired-block bootstrap resamples and are not simultaneous intervals. "
                  "Independent symmetric/exchangeable paired differences are required by the sign-flip null. A receipt cannot establish that assumption or authenticate hidden reasoning.", "",
                  "Chain-prefix curves use the frozen order at n=1 through 10; n=10 is primary. Prefix effects use only fully available prefixes, and raw prefix p-values appear only after the entire main gate passes. "
                  "n<2 has p=NA. These are descriptive sensitivity plots, not predicted significance crossings, power estimates, or a rule to extend, stop, replace, or select a sample. "
                  "No favorable outcome, slope, direction or p-value is used for wording selection or main-case inclusion.", "",
                  "## Reproduction", "",
                  "Rebuild: `.venv/Scripts/python.exe scripts/report_exp14_framing.py`. Only data/student_framing_v3/development and data/student_framing_v3/main are read. "
                  "The strict-deadline study and unused carry-forward draft stay separate. No API requests, participant launches, fabricated missing decisions, or hidden reasoning traces are used. "
                  "Main requires STUDENT_FRAMING_V3_MAIN_PLAN.json, thirty complete replay-valid actual-response contexts and hash-bound external reviews. "
                  "[Full gate reasons and input hashes](../../analysis/student_framing_v3/VALIDATION.json).", "",
                  "Input fingerprint: `" + result["fingerprint"] + "`. Earlier generated bytes are preserved in this amendment's history folders before regeneration.", "",
                  "## Development figures", "",
                  "![Development contrasts](figures/development_hypotheses.png)", "",
                  "Each point is one matched block; NA contains no fabricated observation. All development p-values remain NA.", "",
                  "![Main contrasts](figures/main_hypotheses.png)", "",
                  "The full ten-block sample is required for primary main inference.", "",
                  "![Main fixed chain-prefix sensitivity](figures/main_chain_prefixes.png)", "",
                  "The frozen n=10 sample is primary. Curves do not predict a significant crossing or authorize a stopping change.", ""])
    return "\n".join(lines)


def make_pdf(path, markdown):
    scoring.make_pdf(path, markdown)
    from io import BytesIO
    from pypdf import PdfWriter
    document = PdfWriter(clone_from=BytesIO(path.read_bytes()))
    document.add_metadata({"/Title": "Simulated student time pressure", "/Subject": "Fictional student framing; no actual model runtime deadline"})
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
        plan_path = experiment / "hypotheses/STUDENT_FRAMING_V3_MAIN_PLAN.json"
        plan = read_json(plan_path) if plan_path.exists() else None
        if input_fingerprint(experiment)[0] == fingerprint:
            break
    else:
        raise RuntimeError("Framing inputs changed during five snapshot attempts; rerun report")
    preserve_previous(experiment, fingerprint)
    result = dict(schema_version=SCHEMA, generated_utc=datetime.now(timezone.utc).isoformat(), fingerprint=fingerprint,
                  source_and_input_hashes=hashes, controller_schema=controller.SCHEMA, model_runtime_limit_seconds=None,
                  runs=runs, development=analyze_stage(runs, stage="development"), main=analyze_stage(runs, stage="main", plan=plan),
                  human_participants=0, treatment="fictional student time-pressure framing")
    tables.update(case_outcomes=runs, development_endpoints=result["development"]["endpoints"], development_contrasts=result["development"]["contrasts"],
                  main_endpoints=result["main"]["endpoints"], main_contrasts=result["main"]["contrasts"], main_prefixes=result["main"]["prefixes"])
    for name in ("role_outcomes", "probe_pairs", "probe_regression_residuals", "probe_diagnostics", "knowledge_items", "latencies", "weeks"):
        tables.setdefault(name, [])
    generated = []
    for name, rows in sorted(tables.items()):
        path = experiment / ANALYSIS / "tables" / (name + ".csv")
        scoring.csv_write(path, rows)
        generated.append(path)
    path = experiment / ANALYSIS / "RESULTS.json"
    write_json(path, result)
    generated.append(path)
    generated.extend(make_figures(experiment, result))
    report = experiment / REPORTS / "REPORT.md"
    markdown = report_markdown(result)
    report.write_text(markdown, encoding="utf-8")
    generated.append(report)
    pdf = experiment / REPORTS / "REPORT.pdf"
    make_pdf(pdf, markdown)
    generated.append(pdf)
    for prefix, text in ((ANALYSIS, "[Results](RESULTS.json) · [Tables](tables/) · [Validation](VALIDATION.json)"),
                         (REPORTS, "[Report](REPORT.md) · [PDF](REPORT.pdf) · [Figures](figures/README.md)")):
        path = experiment / prefix / "README.md"
        path.write_text("# Simulated student time pressure\n\n" + text + "\n\nFictional student framing; no actual model runtime deadline or fallback decisions. "
                        "Rebuild with `.venv/Scripts/python.exe scripts/report_exp14_framing.py`. Prior generated bytes remain in history by fingerprint.\n", encoding="utf-8")
        generated.append(path)
    receipt = experiment / ANALYSIS / "VALIDATION.json"
    write_json(receipt, dict(schema_version=SCHEMA, fingerprint=fingerprint, source_and_input_hashes=hashes,
                            scanned_paths=[(DATA / s / "*/RESULT.json").as_posix() for s in STAGES], records=len(runs),
                            replay_valid=sum(r.get("replay_valid") is True for r in runs),
                            reviewed=sum(r.get("adherence", {}).get("passed") is True for r in runs),
                            errors=[dict(result_path=r["result_path"], replay_error=r.get("replay_error"), analysis_error=r.get("analysis_error"))
                                    for r in runs if not r.get("replay_valid") or r.get("analysis_error")],
                            main_inference_enabled=result["main"]["inference_enabled"], main_gate_reasons=result["main"]["gate_reasons"],
                            model_runtime_deadline_enforced=False, synthetic_fallbacks_used=False,
                            generated_files={p.relative_to(experiment).as_posix(): sha256(p) for p in generated}))
    generated.append(receipt)
    write_json(current, dict(schema_version=SCHEMA, fingerprint=fingerprint, report=report.relative_to(experiment).as_posix(),
                             generated_files={p.relative_to(experiment).as_posix(): sha256(p) for p in generated}))
    return result
