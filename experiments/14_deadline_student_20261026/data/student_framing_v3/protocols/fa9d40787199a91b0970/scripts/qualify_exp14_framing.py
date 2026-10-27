"""Prospective completion/provenance/knowledge gate; never select by p-values."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from beergame_study.exp14_framing import SCHEMA, audit_result, digest, source_hashes
from beergame_study.exp14_analysis import probe_metrics, scoring_bank, knowledge_metrics, adherence_review, game_metrics
from prepare_exp14_framing import EXP, MAIN_PLAN, plan, freeze, sha, materials, analysis_sources


def verify_assignment(case, arm, value):
    required = dict(arm=arm, stage="development", block_id=value["development"]["block_id"],
        seed=value["development"]["seed"], weeks=24, prompt_version=value["prompt_version"],
        plan_sha256=sha(EXP / "hypotheses/STUDENT_FRAMING_V3_PLAN.json"),
        source_hashes=value["source_hashes"], material_hashes=value["material_hashes"],
        fictional_student_seconds=value["fictional_student_seconds"][arm], model_runtime_limit_seconds=None,
        deadline_seconds=None, phase_deadline_seconds={"game": None, "probes": None})
    if any(key not in case or case[key] != expected for key, expected in required.items()):
        raise ValueError("Development CASE differs from its prospective assignment")


def gate(freeze_main=False):
    value = plan()
    rows = []
    case_ids, sessions = set(), set()
    for arm in "ABC":
        folder = EXP / "data/student_framing_v3/development" / (value["development"]["block_id"] + "_" + arm.lower())
        row = dict(arm=arm, passed=False, reason="Not collected")
        if (folder / "RESULT.json").exists():
            case = json.loads((folder / "CASE.json").read_text(encoding="utf-8"))
            result = json.loads((folder / "RESULT.json").read_text(encoding="utf-8"))
            verify_assignment(case, arm, value)
            if case["case_id"] in case_ids:
                raise ValueError("Duplicate case counted as another development context")
            case_ids.add(case["case_id"])
            audit_result(result, case)
            probe, _, _, _ = probe_metrics(scoring_bank(case, "probes", []), result.get("probe_answers", {}))
            quiz, _ = knowledge_metrics(scoring_bank(case, "comprehension", []), result.get("comprehension_answers"))
            review = adherence_review(folder, sha(folder / "RESULT.json"), digest(case))
            review_path = folder / "PUBLIC_PROCEDURE_REVIEW.json"
            if review_path.exists():
                session_hash = json.loads(review_path.read_text(encoding="utf-8")).get("source_session_sha256")
                if not session_hash or session_hash in sessions:
                    raise ValueError("Missing or duplicate independent development session")
                sessions.add(session_hash)
            else:
                review["passed"] = False
            complete = result.get("complete", False) and len(result["weeks"]) == 24 and len(result["probe_answers"]) == 32
            complete = complete and probe["pipeline_sensitivity"] is not None and probe["backlog_sensitivity"] is not None
            game, _ = game_metrics(result)
            complete = complete and all(game[name] is not None for name in ("chain_total_cost", "mean_role_order_variance", "mean_role_bullwhip"))
            knowledge = quiz["knowledge_answered"] == 4 and (arm != "C" or quiz["knowledge_fraction_correct"] >= .75)
            passed = bool(complete and knowledge and review["passed"])
            row.update(passed=passed, procedure_complete=result.get("complete", False),
                actual_weekly_orders=len(result["weeks"]) * 4, actual_probe_answers=len(result["probe_answers"]),
                knowledge_fraction=quiz["knowledge_fraction_correct"], review_passed=review["passed"],
                result_sha256=sha(folder / "RESULT.json"),
                reason="Complete actual choices, quiz and review" if passed else "Incomplete actual responses, knowledge check or review")
        rows.append(row)
    receipt = dict(schema_version="exp14-student-framing-gate-v3", created_utc=datetime.now(timezone.utc).isoformat(),
        qualification_passed=all(row["passed"] for row in rows), checks=rows,
        selection_uses_hypothesis_signs_or_p_values=False, main_plan_created=freeze_main and all(row["passed"] for row in rows))
    path = EXP / "analysis/student_framing_v3/qualification" / (digest(receipt)[:20] + ".json")
    freeze(path, receipt)
    if freeze_main:
        if not receipt["qualification_passed"]:
            raise ValueError("Main blocked by the prospectively registered completion/provenance/knowledge gate")
        orders = {}
        for block in value["main"]["block_ids"]:
            arms = list("ABC")
            random.Random("exp14-student-framing-main-" + block).shuffle(arms)
            orders[block] = arms
        frozen = dict(created_utc=datetime.now(timezone.utc).isoformat(), frozen=True, qualification_passed=True,
            block_ids=value["main"]["block_ids"], prompt_version=value["prompt_version"], independent_blocks_confirmed=True,
            controller_schema=SCHEMA, source_hashes=source_hashes(), material_hashes=materials(),
            analysis_hashes=analysis_sources(), launch_orders=orders, model_runtime_limit_seconds=None,
            fictional_student_seconds=value["fictional_student_seconds"], qualification_receipt=str(path.relative_to(EXP)).replace("\\", "/"),
            stopping="All ten assigned matched blocks; no outcome-based stopping, extension or favorable replacement",
            inference="Actual model decisions under fictional student framing; two-sided paired sign-flip and Holm5")
        freeze(MAIN_PLAN, frozen)
    print(json.dumps(receipt, indent=2))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-main", action="store_true")
    args = parser.parse_args()
    gate(args.freeze_main)
