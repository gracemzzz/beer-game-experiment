"""Independent arithmetic/integrity checks for the completed framing sample."""
from pathlib import Path
from hashlib import sha256
from itertools import product
import json
import math
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_framing import audit_result, digest, source_hashes

EXP = ROOT / "experiments/14_deadline_student_20261026"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10), (a, b)


def metrics(result, case):
    assert result["complete"] and len(result["weeks"]) == 24 and len(result["probe_answers"]) == 32
    assert len(result["decisions"]) == 33
    assert all(type(q) is int and q >= 0 for w in result["weeks"] for q in w["orders"])
    assert all(type(q) is int and q >= 0 for q in result["probe_answers"].values())
    assert result["comprehension_answers"] is not None and len(result["comprehension_answers"]) == 4
    costs = sum(.5 * role["inventory"] + role["backlog"] for week in result["weeks"] for role in week["roles"])
    close(costs, result["full_game_cost"])
    variances = [statistics.variance([w["orders"][i] for w in result["weeks"]]) for i in range(4)]
    demand = statistics.variance([w["customer_demand"] for w in result["weeks"]])
    assert demand > 0
    groups = {}
    for probe in case["probes"]:
        scoring = case["assay_scoring"][probe["probe_id"]]
        if scoring["assay_dimension"] == "pipeline":
            groups.setdefault(scoring["pair_id"], []).append(probe)
    assert len(groups) == 8
    slopes = []
    for members in groups.values():
        assert len(members) == 2
        low, high = sorted(members, key=lambda p: p["outstanding"])
        slopes.append((result["probe_answers"][low["probe_id"]] - result["probe_answers"][high["probe_id"]]) /
                      (high["outstanding"] - low["outstanding"]))
    return dict(chain_total_cost=costs, mean_role_order_variance=statistics.fmean(variances),
                mean_role_bullwhip=statistics.fmean(variances) / demand,
                pipeline_sensitivity=statistics.fmean(slopes))


def exact_p(values):
    scale = max(abs(v) for v in values)
    if scale == 0:
        return 1.0
    scaled = [v / scale for v in values]
    observed = abs(sum(scaled))
    extreme = sum(abs(sum(s * v for s, v in zip(signs, scaled))) >= observed - 1e-12
                  for signs in product((-1, 1), repeat=len(scaled)))
    return extreme / (2 ** len(scaled))


def verify():
    output = read(EXP / "analysis/student_framing_v3/RESULTS.json")
    assert output["main"]["inference_enabled"] and output["main"]["complete_blocks"] == 10
    plan = read(EXP / "hypotheses/STUDENT_FRAMING_V3_MAIN_PLAN.json")
    assert plan["source_hashes"] == source_hashes()
    rows, evidence, sessions = {}, [], set()
    for block in plan["block_ids"]:
        demands, profiles = [], []
        for arm in "ABC":
            folder = EXP / "data/student_framing_v3/main" / (block + "_" + arm.lower())
            case, result = read(folder / "CASE.json"), read(folder / "RESULT.json")
            assert case["arm"] == arm and case["block_id"] == block and case["stage"] == "main"
            assert case["seed"] == 1450000 + int(block[3:])
            assert case["model_runtime_limit_seconds"] is None and case["deadline_seconds"] is None
            assert case["fictional_student_seconds"] == (120 if arm == "A" else 8)
            audit_result(result, case)
            review = read(folder / "ADHERENCE_REVIEW.json")
            assert review["passed"] and review["result_sha256"] == sha(folder / "RESULT.json")
            assert review["case_sha256"] == digest(case)
            assert review["public_transcript_sha256"] == sha(folder / "PUBLIC_TRANSCRIPT.jsonl")
            public = read(folder / "PUBLIC_PROCEDURE_REVIEW.json")
            assert not public["issues"] and not public["unrecognized_calls"]
            assert public["accepted_decisions"] == public["matched_public_literal_decisions"] == public["full_displays_seen"] == 33
            assert public["requested_settings"] and all(s == dict(model="gpt-6-astra", effort="xhigh") for s in public["requested_settings"])
            assert public["source_session_sha256"] not in sessions
            sessions.add(public["source_session_sha256"])
            independent = metrics(result, case)
            generated = next(r for r in output["runs"] if r["case_id"] == case["case_id"])
            for key, value in independent.items():
                close(value, generated[key])
            rows[(block, arm)] = independent
            demands.append([w["customer_demand"] for w in result["weeks"]])
            profiles.append(result["profile_ids"])
            evidence.append(dict(run=folder.name, result_sha256=sha(folder / "RESULT.json"),
                                 case_sha256=sha(folder / "CASE.json"), review_sha256=sha(folder / "ADHERENCE_REVIEW.json")))
        assert demands[0] == demands[1] == demands[2] and profiles[0] == profiles[1] == profiles[2]
    tests = []
    for endpoint in output["main"]["endpoints"]:
        treated, control = endpoint["contrast"].split("-")
        diffs = [rows[(block, treated)][endpoint["metric"]] - rows[(block, control)][endpoint["metric"]] for block in plan["block_ids"]]
        close(statistics.fmean(diffs), endpoint["mean_difference"])
        close(exact_p(diffs), endpoint["p_two_sided"])
        tests.append(dict(hypothesis=endpoint["hypothesis"], independent_mean=statistics.fmean(diffs), independent_raw_p=exact_p(diffs)))
    order = sorted(range(5), key=lambda i: tests[i]["independent_raw_p"])
    bound = 0.0
    for rank, index in enumerate(order):
        bound = max(bound, min(1.0, (5-rank) * tests[index]["independent_raw_p"]))
        close(bound, output["main"]["endpoints"][index]["p_holm_family_5"])
        tests[index]["independent_holm_5"] = bound
    prior = read(EXP / "analysis/DEVELOPMENT_REVIEW.json")
    for row in prior["case_records"]:
        folder = EXP / "data" / row["stage"] / row["case"]
        assert sha(folder / "RESULT.json") == row["result_sha256"]
        assert sha(folder / "CASE.json") == row["case_sha256"]
    assert sha(ROOT / "experiments/12_pressure_framing_api_20261020/data/api_budget.json") == "81f75f9fb53f87f3ef979b11f086a7ac787c15c2cf6d9b2e8acb69f6a0efa7c3"
    receipt = dict(passed=True, scope="Independent full main arithmetic and provenance checks", source_results_sha256=sha(EXP / "analysis/student_framing_v3/RESULTS.json"),
        verifier_sha256=sha(Path(__file__)), actual_main_contexts=30, matched_blocks=10,
        actual_weekly_orders=2880, actual_probe_choices=960, actual_quiz_answers=120,
        synthetic_answers=0, actual_model_timer=False, independent_endpoint_checks=tests,
        per_case_hashes=evidence, original_16_cases_unchanged=True, api_ledger_unchanged=True)
    path = EXP / "analysis/student_framing_v3/FINAL_VERIFICATION.json"
    if path.exists() and read(path) != receipt:
        old = path.parent / "verification_history" / (sha(path) + ".json")
        old.parent.mkdir(parents=True, exist_ok=True)
        if not old.exists():
            old.write_bytes(path.read_bytes())
    path.write_bytes((json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k:v for k,v in receipt.items() if k != "per_case_hashes"}, indent=2))


if __name__ == "__main__":
    verify()
