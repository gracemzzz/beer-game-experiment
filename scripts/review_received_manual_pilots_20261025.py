"""Offline intake/replay of the three received Astra/ultra development pilots.

Original JSON, supplementary execution records and reported website settings
remain separate. Missing full transcripts are never replaced with fabricated
records. This script neither calls APIs nor changes scientific implementations.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import manual_weekly_v3 as controller
from beergame_study import manual_workflow_v3 as workflow

EXPERIMENT = ROOT / "experiments/13_weekly_state_api_20261021"
RUN = EXPERIMENT / "data/manual_v3_3e5479b5ae2ffc96"
SOURCES = {
    "A": RUN / "chat_runs/MW3_PILOT_A_20261025",
    "B": EXPERIMENT / "data/manual_v3_chat_MW3_PILOT_B_20261025",
    "C": EXPERIMENT / "data/manual_chat_20261025_MW3_PILOT_C_source_exposure",
}
MODEL_REPORT = dict(raw_user_statement="model: gpt 6 astra ultra", reported_model="GPT-6 Astra",
    reported_reasoning_setting="ultra", scope=["MW3_PILOT_A", "MW3_PILOT_B", "MW3_PILOT_C"],
    source="User statement in this conversation", provider_api_model_id_verified=False,
    exported_metadata_preserved="Original model and reasoning fields remain UNRECORDED; no raw file is edited.")


def csv_text(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main():
    manifest = workflow.load_manifest(RUN)
    ledger = EXPERIMENT.parent / "12_pressure_framing_api_20261020/data/api_budget.json"
    ledger_before = workflow.sha(ledger)
    inventory = []
    for arm, folder in SOURCES.items():
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                inventory.append(dict(arm=arm, relative_path=path.relative_to(ROOT).as_posix(),
                    relative_to_arm=path.relative_to(folder).as_posix(), bytes=path.stat().st_size, sha256=workflow.sha(path)))
    identity = dict(study_id=manifest["study_id"], manifest_sha256=workflow.sha(RUN / "manifest.json"),
        model_report=MODEL_REPORT, source_inventory=inventory, script_sha256=workflow.sha(__file__))
    signature = controller.digest(identity)[:12]
    received = RUN / "pilot_reviews" / signature
    analysis = EXPERIMENT / "analysis" / RUN.name / ("pilot_review_" + signature)
    report = EXPERIMENT / "reports/manual_pilot_review_20261025"
    for item in inventory:
        workflow.freeze(received / "originals" / item["arm"] / item["relative_to_arm"],
                        (ROOT / item["relative_path"]).read_bytes())
    workflow.freeze(received / "MODEL_REPORT.json", MODEL_REPORT)
    workflow.freeze(received / "SOURCE_INVENTORY.json", identity)

    outcomes = []
    for arm, folder in SOURCES.items():
        payload = workflow.read(folder / ("MW3_PILOT_" + arm + ".json"))
        case = next(c for c in manifest["cases"] if c["case_id"] == payload["case_id"])
        expected = {key: case[key] for key in ("case_id", "arm", "replicate", "chains", "seed")}
        expected["study_id"] = manifest["study_id"]
        row = controller.audit_export(payload, expected_case=expected,
            expected_source_sha256=manifest["controller_source_sha256"])
        row.update(reported_model=MODEL_REPORT["reported_model"],
            reported_reasoning_setting=MODEL_REPORT["reported_reasoning_setting"],
            collection_kind="development", replay_passed=True,
            transcript_coverage={"A": "partial_execution_record", "B": "not_supplied", "C": "not_exported_per_provenance"}[arm],
            protocol_adherence={"A": "recorded_submission_checks_pass_full_context_unknown",
                                "B": "unknown_without_transcript",
                                "C": "source_exposure_reported_in_provenance"}[arm],
            full_transcript_review_passed=False, eligible_for_heldout=False,
            changed_weekly_orders=sum(first != final for iw, fw in zip(payload["initial_orders"], payload["final_orders"])
                for ic, fc in zip(iw, fw) for first, final in zip(ic, fc)),
            changed_probe_choices=sum(payload["probe_initial"][k] != payload["probe_final"][k] for k in payload["probe_initial"]),
            weekly_choices=sum(len(ch) for week in payload["final_orders"] for ch in week),
            final_probe_choices=len(payload["probe_final"]))
        orders = [q for week in payload["final_orders"] for chain in week for q in chain]
        row.update(min_order=min(orders), max_order=max(orders))
        outcomes.append(row)
    indexed = {row["arm"]: row for row in outcomes}
    contrasts = []
    for h, metric, treated, control, expected_sign in (
        ("H1 proxy", "pipeline_sensitivity", "B", "A", -1),
        ("H2", "chain_total_cost", "B", "A", 1),
        ("H3 proxy", "pipeline_sensitivity", "C", "B", 1),
        ("H4a", "mean_role_order_variance", "C", "B", -1),
        ("H4b", "mean_role_bullwhip", "C", "B", -1)):
        value = indexed[treated][metric] - indexed[control][metric]
        contrasts.append(dict(hypothesis=h, metric=metric, contrast=treated + "-" + control,
            difference=value, direction="zero" if value == 0 else "predicted" if value * expected_sign > 0 else "opposite",
            independent_development_blocks=1, inferential_p_value="not_computed", heldout_sample=False))
    result = dict(review_id=signature, study_id=manifest["study_id"], model_report=MODEL_REPORT,
        collection_kind="development", completed_chats=3, chains_per_chat=10, total_chain_instances=30,
        fictional_role_instances=120, weekly_orders=sum(r["weekly_choices"] for r in outcomes),
        final_probe_choices=sum(r["final_probe_choices"] for r in outcomes),
        independent_matched_development_blocks=1, eligible_heldout_blocks=0, human_observations=0,
        full_context_adherence_gate_passed=False, outcomes=outcomes, contrasts=contrasts,
        c_provenance_deviation=workflow.read(SOURCES["C"] / "PROVENANCE.json")["protocol_deviation"],
        api_calls=0, ledger_sha256_before=ledger_before, ledger_sha256_after=workflow.sha(ledger))
    assert result["ledger_sha256_before"] == result["ledger_sha256_after"]
    assert result["weekly_orders"] == 2880 and result["final_probe_choices"] == 480
    for item in inventory:
        assert workflow.sha(ROOT / item["relative_path"]) == item["sha256"]
    workflow.freeze(received / "REVIEW.json", result)
    workflow.freeze(analysis / "REVIEW.json", result)
    workflow.freeze(analysis / "pilot_outcomes.csv", csv_text(outcomes))
    workflow.freeze(analysis / "descriptive_contrasts.csv", csv_text(contrasts))
    rel = lambda p: Path(__import__("os").path.relpath(p, report)).as_posix()
    lines = ["# GPT-6 Astra / ultra: three received manual pilots", "",
        "1. **All three games completed and passed independent replay:** 24 weeks × 10 chains each, 2,880 weekly orders and 480 final probe choices in total.",
        "2. **Model recorded:** GPT-6 Astra; reasoning setting ultra, as reported by the user. The original JSON metadata remains unchanged. The backend/API model is not independently verified.",
        "3. **H1/H3 show no pipeline-sensitivity difference:** all three values are 1.0. H2/H4 differences follow the predicted descriptive directions, but are not statistically established.",
        "4. **These are development pilots, one matched block—not 30 independent trials.** They stay outside the main 10/20/40-block analysis. No p-values or inferential confidence intervals are computed.",
        "5. **Protocol review remains incomplete:** A has partial execution evidence; B lacks a full transcript; C's provenance file reports controller-source exposure. Preserve all three rather than labeling them clean confirmatory observations.",
        "6. **No new API spending.** The cumulative $5 cap remains unchanged; this review made no API calls.", "",
        "## Pilot outcomes", "",
        "A = control reading + extra reconsideration; B = control reading + first decision committed; C = causal education + first decision committed.", "",
        "| Arm | Mean 24-week chain cost | Mean role order variance | Bullwhip | Pipeline sensitivity | Weekly orders changed on review |",
        "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for r in outcomes:
        lines.append(f"| {r['arm']} | {r['chain_total_cost']:.2f} | {r['mean_role_order_variance']:.4f} | {r['mean_role_bullwhip']:.4f} | {r['pipeline_sensitivity']:.4f} | {r['changed_weekly_orders']}/960 |")
    lines += ["", "Costs are game-cost units; each value averages ten dependent chains. The 120 role instances are fictional, not sampled students.", "",
        "| Hypothesis | Pilot contrast | Difference | Descriptive reading |",
        "| --- | --- | ---: | --- |"]
    for r in contrasts:
        lines.append(f"| {r['hypothesis']} | {r['contrast']} | {r['difference']:+.6f} | {r['direction']} |")
    lines += ["", "H2 is cost; H4a/b are order variance and bullwhip, not education's cost contrast. H4a/b share the order-variance numerator and do not provide independent confirmations. C's reported source exposure confounds interpretation of education effects. A changed only 3/960 weekly orders and 0/160 probes; an extra opportunity existed, but its impact was small in this pilot.", "",
        "## What the evidence establishes", "",
        "The exact case IDs, seeds, chain assignments, controller fingerprint, all weekly states, costs, literal initial/final choices, probes and event hashes replay correctly against the frozen manifest. Zero and unchanged orders were retained. Orders ranged 0–23 in A, 0–30 in B and 0–16 in C; the controller completed all games without imposing an order floor.", "",
        "A's saved request matches the frozen prompt after newline normalization. Its 50 recorded submissions contain literal choices and separate initial/revision interactions. However, its execution record explicitly omits initial setup, surrounding chat and administrative tools. B has an export and probe display only. C has an export, probe display and provenance receipt that reports source inspection before decisions; it says the full transcript was not exported. These records cannot establish complete clean-context adherence.", "",
        "The user supplied the same three folder paths when asked about transcripts. They were rechecked; no missing transcript was invented or inferred from the JSON. Provider/model labels are user-reported. Controller-call timestamps are not verified thinking time, and one versus two decision opportunities is an AI resource analogue rather than a calibrated human deadline.", "",
        "## Files and plots", "",
        f"- [Extracted arm outcomes]({rel(analysis / 'pilot_outcomes.csv')}) and [descriptive H1–H4 contrasts]({rel(analysis / 'descriptive_contrasts.csv')}).",
        f"- [Replay and provenance receipt]({rel(analysis / 'REVIEW.json')}).",
        f"- [Preserved originals and separate model report]({rel(received)}).",
        "- [Descriptive figures and captions](FIGURE_CAPTIONS.md). No error bars or p-values are attached to these pilots.", "",
        "## Next collection", "",
        "Keep these pilots as development evidence. Before a main launch, complete the transcript/adherence check and resolve the reported C source-exposure issue in a separately recorded technical check. Preserve this attempt. Do not tune prompts for significance or add the pilot to the first ten main blocks. The existing main prompts remain prepared, not collected. Large batches increase fictional headcount; independent fresh three-arm blocks determine inferential sample size.", ""]
    publication = "\n".join(lines)
    workflow.freeze(analysis / "REPORT.md", publication)
    workflow.freeze(report / "REPORT.md", publication)
    workflow.freeze(report / "LATEST.json", dict(review_id=signature, study_id=manifest["study_id"],
        analysis=analysis.relative_to(EXPERIMENT).as_posix(), receipt=received.relative_to(EXPERIMENT).as_posix(),
        model_report=MODEL_REPORT, completed_pilots=3, full_adherence_gate_passed=False, eligible_main_cases=0))
    print(json.dumps(dict(report=str(report / "REPORT.md"), analysis=str(analysis), review_id=signature,
                         replay_passed=3, original_files_unchanged=True, ledger_unchanged=True), indent=2))


if __name__ == "__main__":
    main()
