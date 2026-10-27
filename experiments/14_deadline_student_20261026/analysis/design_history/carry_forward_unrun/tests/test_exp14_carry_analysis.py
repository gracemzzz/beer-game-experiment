"""Synthetic numerical fixtures only; no participant/model/API collection."""
from datetime import datetime, timedelta, timezone
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import exp14_carry_analysis as analysis
from beergame_study import exp14_carry as controller
from beergame_study import exp14_analysis as scoring


def point(seconds):
    return dict(monotonic_ns=round(seconds * 1e9),
                utc=(datetime(2026, 10, 26, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat())


def make_case():
    probes = scoring.read_json(analysis.EXPERIMENT / "prompts/probes.json")
    questions = scoring.read_json(analysis.EXPERIMENT / "prompts/comprehension.json")
    case = dict(schema_version=controller.SCHEMA, timeout_policy=controller.POLICY,
                probe_timeout_policy=controller.PROBE_POLICY,
                case_id="SYNTHETIC-CARRY-ANALYSIS", block_id="fixture-block", arm="A", stage="development", prompt_version="V1",
                seed=1420001, weeks=24, deadline_seconds=2, source_hashes=controller.source_hashes(),
                probes=[{k: p[k] for k in scoring.PROBE_FIELDS} for p in probes],
                assay_scoring={p["probe_id"]: {k: p[k] for k in ("pair_id", "assay_dimension")} for p in probes},
                comprehension=[{k: q[k] for k in scoring.QUESTION_FIELDS} for q in questions],
                comprehension_scoring={q["question_id"]: {k: q[k] for k in ("correct_answer", "reason")} for q in questions},
                actual_model="SYNTHETIC SOFTWARE FIXTURE", actual_effort="SYNTHETIC SOFTWARE FIXTURE")
    return case


def complete_fixture(*, expire_game=False, expire_probes=False, stop_after_weeks=None):
    case = make_case()
    state = controller.CarryCase(case, clock=point(0))
    tick = 10
    while state.phase() != "complete":
        if stop_after_weeks is not None and len(state.weeks) == stop_after_weeks:
            break
        shown = state.show(point(tick))
        phase = shown["phase"]
        if (phase == "game" and expire_game) or (phase == "probes" and expire_probes):
            state.check_expiry(point(tick + 3))
        else:
            if phase == "game":
                week = shown["week"]
                choices = [4 + week % 3, 7, 8 + week % 2, 0]
            elif phase == "probes":
                choices = {p["probe_id"]: 100 - p["outstanding"] // 2 + 2 * p["backlog"] for p in shown["probes"]}
            else:
                choices = {k: v["correct_answer"] for k, v in case["comprehension_scoring"].items()}
            result = state.submit(json.dumps(choices), shown["decision_id"], received=point(tick + 1))
            if not result["accepted"]:
                raise AssertionError(result)
        tick += 10
    payload = state.export()
    controller.audit_result(payload, case)
    metrics, tables = analysis.extract_metrics(payload, case)
    return case, payload, metrics, tables


class CarryAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actor = complete_fixture()
        cls.probe_fallback = complete_fixture(expire_probes=True)
        cls.game_fallback = complete_fixture(expire_game=True)

    def row(self, fixture, arm="A", block="fixture-block", stage="development"):
        case, payload, metrics, _ = fixture
        return dict(metrics, stage=stage, case_id="SYNTHETIC-" + block + arm, block_id=block, arm=arm,
                    prompt_version="V1", seed=1420001, profile_ids=payload["profile_ids"],
                    replay_valid=True, analysis_error=None, adherence=dict(passed=True))

    def test_role_fallback_gives_complete_policy_assay_but_no_actor_assay(self):
        _, payload, metrics, tables = self.probe_fallback
        self.assertTrue(metrics["procedure_complete"])
        self.assertTrue(metrics["applied_probe_answers_complete"])
        self.assertFalse(metrics["all_actor_responses_complete"])
        self.assertEqual(metrics["applied_probe_choices"], 32)
        self.assertEqual(metrics["accepted_actor_probe_choices"], 0)
        self.assertEqual(metrics["fallback_probe_choices"], 32)
        self.assertEqual(metrics["pipeline_sensitivity"], 0)
        self.assertEqual(metrics["backlog_sensitivity"], 0)
        self.assertIsNone(metrics["actor_pipeline_sensitivity"])
        self.assertEqual(metrics["actor_missing_pipeline_pairs"], 8)
        policy_pairs = [p for p in tables["probe_pairs"] if p["estimand"] == "applied_policy"]
        self.assertEqual(len(policy_pairs), 16)
        self.assertTrue(all(p["fallback_fraction"] == 1 for p in policy_pairs))
        self.assertTrue(all(p["fallback_fraction"] == 1 for p in tables["probe_answer_sources_by_role"]))
        self.assertEqual(len(payload["decisions"]), 25)  # 24 game packets + one quiz, no invented probe packets.

    def test_game_fallback_policy_variance_is_not_actor_variance(self):
        _, payload, metrics, _ = self.game_fallback
        self.assertEqual(metrics["fallback_weeks"], 24)
        self.assertEqual(metrics["accepted_actor_order_fraction"], 0)
        self.assertEqual(metrics["expired_actor_order_count"], 96)
        self.assertTrue(metrics["physical_game_complete"])
        self.assertFalse(metrics["all_actor_responses_complete"])
        self.assertEqual(metrics["policy_mean_role_order_variance"], 0)
        self.assertEqual(metrics["policy_mean_role_bullwhip"], 0)
        self.assertEqual(metrics["chain_total_cost"], sum(w["cost"] for w in payload["weeks"]))
        self.assertEqual(metrics["actor_pipeline_sensitivity"], .5)
        self.assertEqual(metrics["actor_backlog_sensitivity"], 2)

    def test_prefix_never_becomes_full_horizon_policy_outcome(self):
        _, _, metrics, _ = complete_fixture(stop_after_weeks=12)
        self.assertEqual(metrics["unresolved_game_weeks"], 12)
        self.assertEqual(metrics["accepted_actor_order_fraction"], .5)
        self.assertEqual(metrics["fallback_weeks"], 0)
        self.assertIsNone(metrics["policy_chain_total_cost"])
        self.assertIsNone(metrics["policy_mean_role_order_variance"])
        self.assertIsNone(metrics["policy_mean_role_bullwhip"])
        self.assertIsNone(metrics["pipeline_sensitivity"])

    def test_one_development_block_has_signed_policy_contrasts_but_no_p(self):
        rows = [self.row(self.actor, "A"), self.row(self.probe_fallback, "B"), self.row(self.actor, "C")]
        result = analysis.contrast_analysis(rows, stage="development")
        self.assertEqual(result["endpoints"][0]["mean_difference"], -.5)
        self.assertEqual(result["endpoints"][2]["mean_difference"], .5)
        self.assertTrue(all(r["n_pairs"] == 1 for r in result["endpoints"]))
        self.assertTrue(all(r["p_two_sided"] is None and r["p_holm_family_5"] is None for r in result["endpoints"]))

    def test_coverage_gate_applies_to_pilot_launch_not_assigned_main_cases(self):
        rule = dict(actor_coverage_gate=dict(minimum_game_fraction=.75, minimum_probe_fraction=.75, scope="each_development_case"),
                    development=dict(block_id="fixture-block"))
        rows = [self.row(self.actor, arm) for arm in "ABC"]
        self.assertTrue(analysis.development_readiness(rows, rule)["qualified"])
        rows[1] = self.row(self.probe_fallback, "B")
        self.assertFalse(analysis.development_readiness(rows, rule)["qualified"])
        blocks = [f"c2m{i:03d}" for i in range(1, 11)]
        plan = dict(block_ids=blocks, frozen=True, independent_blocks_confirmed=True, prompt_version="V1",
                    controller_schema=controller.SCHEMA, timeout_policy=controller.POLICY,
                    probe_timeout_policy=controller.PROBE_POLICY, **rule)
        main = [self.row(self.probe_fallback if arm == "B" else self.actor, arm, block, "main") for block in blocks for arm in "ABC"]
        result = analysis.contrast_analysis(main, stage="main", plan=plan)
        self.assertTrue(result["inference_enabled"], result["reasons"])
        self.assertEqual(result["endpoints"][0]["p_two_sided"], 2 / 1024)
        main.pop()
        incomplete = analysis.contrast_analysis(main, stage="main", plan=plan)
        self.assertFalse(incomplete["inference_enabled"])
        self.assertTrue(all(r["p_two_sided"] is None for r in incomplete["endpoints"]))

    def test_loading_is_separate_and_validates_new_source_and_review(self):
        case, payload, _, _ = self.actor
        with tempfile.TemporaryDirectory() as directory:
            experiment = Path(directory)
            old = experiment / "data/feasibility/old/RESULT.json"
            old.parent.mkdir(parents=True)
            old.write_bytes(b"HISTORICAL BYTES\r\n")
            folder = experiment / analysis.DATA / "development/synthetic"
            folder.mkdir(parents=True)
            analysis.write_json(folder / "CASE.json", case)
            analysis.write_json(folder / "RESULT.json", payload)
            analysis.write_json(folder / "ADHERENCE_REVIEW.json", dict(passed=True, result_sha256=analysis.sha256(folder / "RESULT.json"),
                                case_sha256=controller.digest(case), full_public_context_reviewed=True, fresh_context_confirmed=True,
                                literal_model_choices_confirmed=True, fixed_requested_settings_confirmed=True))
            rows, _ = analysis.load_runs(experiment)
            self.assertEqual(len(rows), 1)
            self.assertTrue(rows[0]["replay_valid"])
            self.assertTrue(rows[0]["adherence"]["passed"])
            self.assertEqual(rows[0]["pipeline_sensitivity"], .5)
            self.assertEqual(old.read_bytes(), b"HISTORICAL BYTES\r\n")

    def test_carry_history_preserves_old_bytes_in_its_own_subtree(self):
        with tempfile.TemporaryDirectory() as directory:
            experiment = Path(directory)
            target = experiment / analysis.REPORTS / "REPORT.md"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"ORIGINAL CARRY\r\n")
            analysis.write_json(experiment / analysis.ANALYSIS / "CURRENT.json", dict(fingerprint="a" * 64,
                                generated_files={target.relative_to(experiment).as_posix(): analysis.sha256(target)}))
            analysis.preserve_previous(experiment, "b" * 64)
            history = experiment / analysis.REPORTS / "history" / ("a" * 16) / "REPORT.md"
            self.assertEqual(history.read_bytes(), b"ORIGINAL CARRY\r\n")
            target.write_bytes(b"CHANGED\n")
            self.assertEqual(history.read_bytes(), b"ORIGINAL CARRY\r\n")


if __name__ == "__main__":
    unittest.main()
