"""Write an attributed carry-forward development gate; never change old studies."""
from pathlib import Path
from datetime import datetime, timezone
import json
import argparse
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from beergame_study.exp14_carry import SCHEMA, POLICY, PROBE_POLICY, source_hashes, audit_result, digest
from beergame_study.exp14_analysis import probe_metrics, scoring_bank, adherence_review, knowledge_metrics
from prepare_exp14_carry import EXP, MAIN_PLAN, plan, freeze, sha, materials, analysis_sources


def gate(freeze_main=False):
    prepared = plan()
    rows = []
    for arm in "ABC":
        folder = EXP / "data/carry_forward_v2/development" / (prepared["development"]["block_id"] + "_" + arm.lower())
        row = dict(arm=arm, passed=False, reason="Not collected")
        if (folder / "RESULT.json").exists():
            case = json.loads((folder / "CASE.json").read_text(encoding="utf-8"))
            result = json.loads((folder / "RESULT.json").read_text(encoding="utf-8"))
            audit_result(result, case)
            bank = scoring_bank(case, "probes", [])
            metrics, _, _, _ = probe_metrics(bank, result.get("probe_answers", {}))
            review = adherence_review(folder, sha(folder / "RESULT.json"), digest(case))
            behavioral = len(result.get("weeks", [])) == 24 and len(result.get("probe_answers", {})) == 32
            behavioral = behavioral and metrics["pipeline_sensitivity"] is not None and metrics["backlog_sensitivity"] is not None
            game_fraction = sum(d["phase"] == "game" for d in result["decisions"]) / 24
            probe_fraction = len(result.get("actor_probe_answers", {})) / 32
            limits = prepared["actor_coverage_gate"]
            coverage = game_fraction >= limits["minimum_game_fraction"] and probe_fraction >= limits["minimum_probe_fraction"]
            questions = scoring_bank(case, "comprehension", [])
            quiz, _ = knowledge_metrics(questions, result.get("comprehension_answers"))
            knowledge = quiz["knowledge_answered"] == 4 and (arm != "C" or quiz["knowledge_fraction_correct"] >= .75)
            passed = bool(behavioral and coverage and knowledge and review["passed"] and result.get("complete", False))
            row.update(procedure_complete=result.get("complete", False), game_complete=len(result.get("weeks", [])) == 24,
                observed_probe_orders=len(result.get("probe_answers", {})), full_behavior_complete=behavioral,
                actual_game_fraction=game_fraction, actual_probe_fraction=probe_fraction,
                actor_coverage_passed=coverage, comprehension_passed=knowledge,
                review_passed=review["passed"], result_sha256=sha(folder / "RESULT.json"),
                passed=passed,
                reason="Complete reviewed policy endpoints and operational checks" if passed
                else "Incomplete policy endpoint, actor-coverage/knowledge check or procedure review")
        rows.append(row)
    receipt = dict(schema_version="exp14-carry-development-gate-v2", created_utc=datetime.now(timezone.utc).isoformat(),
        qualification_passed=all(row["passed"] for row in rows), checks=rows,
        selection_uses_hypothesis_signs_or_p_values=False, main_plan_created=False,
        statement="Every applied game/probe receives an answer; actual actor coverage and software intervention remain separately reported.")
    path = EXP / "analysis/carry_forward_v2/qualification" / (digest(receipt)[:20] + ".json")
    freeze(path, receipt)
    if freeze_main:
        if not receipt["qualification_passed"]:
            raise ValueError("Main remains blocked by the prospectively specified development gate")
        orders = {}
        for block in prepared["main"]["block_ids"]:
            arms = list("ABC")
            random.Random("exp14-carry-main-" + block).shuffle(arms)
            orders[block] = arms
        frozen = dict(created_utc=datetime.now(timezone.utc).isoformat(), frozen=True, qualification_passed=True,
            block_ids=prepared["main"]["block_ids"], prompt_version=prepared["prompt_version"],
            independent_blocks_confirmed=True, controller_schema=SCHEMA, timeout_policy=POLICY,
            probe_timeout_policy=PROBE_POLICY, source_hashes=source_hashes(), material_hashes=materials(),
            analysis_hashes=analysis_sources(), deadlines=prepared["deadlines"], launch_orders=orders,
            development_gate_path=str(path.relative_to(EXP)).replace("\\", "/"),
            actor_coverage_gate=prepared["actor_coverage_gate"], main_coverage_role="Diagnostic, never exclude an assigned low-coverage case",
            inference="All ten assigned matched chain contrasts on complete applied-policy outcomes; two-sided sign-flip and Holm5",
            stopping="All ten assigned blocks; no significance-based extension or favorable replacement")
        freeze(MAIN_PLAN, frozen)
    print(json.dumps(receipt, indent=2))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-main", action="store_true")
    args = parser.parse_args()
    gate(args.freeze_main)
