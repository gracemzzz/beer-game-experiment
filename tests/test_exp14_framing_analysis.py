"""Synthetic numerical and isolation tests; no participant or API requests."""
from datetime import datetime, timedelta, timezone
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import exp14_framing_analysis as analysis
from beergame_study import exp14_framing as controller
from beergame_study import exp14_analysis as scoring


def point(seconds):
    return dict(monotonic_ns=round(seconds * 1e9),
                utc=(datetime(2026, 10, 26, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat())


def fixture(*, weeks_to_submit=24):
    probes = scoring.read_json(analysis.EXPERIMENT / "prompts/probes.json")
    questions = scoring.read_json(analysis.EXPERIMENT / "prompts/comprehension.json")
    case = dict(schema_version=controller.SCHEMA, case_id="SYNTHETIC-FRAMING-ANALYSIS", block_id="fixture", arm="B",
                stage="development", prompt_version="V3", seed=1440001, weeks=24, fictional_student_seconds=8,
                model_runtime_limit_seconds=None, deadline_seconds=None, source_hashes=controller.source_hashes(),
                probes=[{k: p[k] for k in scoring.PROBE_FIELDS} for p in probes],
                assay_scoring={p["probe_id"]: {k: p[k] for k in ("pair_id", "assay_dimension")} for p in probes},
                comprehension=[{k: q[k] for k in scoring.QUESTION_FIELDS} for q in questions],
                comprehension_scoring={q["question_id"]: {k: q[k] for k in ("correct_answer", "reason")} for q in questions},
                actual_model="SYNTHETIC SOFTWARE FIXTURE", actual_effort="SYNTHETIC SOFTWARE FIXTURE")
    state = controller.FramingCase(case, clock=point(0))
    tick = 10000
    while state.phase() != "complete":
        if weeks_to_submit < 24 and len(state.weeks) == weeks_to_submit:
            break
        shown = state.show(point(tick))
        if shown["phase"] == "game":
            w = shown["week"]
            choices = [w % 9, 4, w % 4, 0]
        elif shown["phase"] == "probes":
            choices = {p["probe_id"]: 100 - p["outstanding"] // 2 + 2 * p["backlog"] for p in shown["probes"]}
        else:
            choices = {key: value["correct_answer"] for key, value in case["comprehension_scoring"].items()}
        ack = state.submit(json.dumps(choices), shown["decision_id"], received=point(tick + 1000))
        if not ack["accepted"]:
            raise AssertionError(ack)
        tick += 10000
    payload = state.export()
    controller.audit_result(payload, case)
    return case, payload


class FramingAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case, cls.payload = fixture()

    def test_actual_choices_score_after_elapsed_time_exceeds_fictional_seconds(self):
        metrics, tables = analysis.extract_metrics(self.payload, self.case)
        self.assertTrue(metrics["complete_primary_endpoints"])
        self.assertEqual(metrics["pipeline_sensitivity"], .5)
        self.assertEqual(metrics["backlog_sensitivity"], 2)
        self.assertEqual(metrics["chain_total_cost"], sum(w["cost"] for w in self.payload["weeks"]))
        self.assertEqual(metrics["knowledge_correct"], 4)
        self.assertEqual(len(self.payload["decisions"]), 33)
        self.assertEqual(metrics["game_median_seconds"], 1000)
        self.assertIsNone(metrics["accepted_on_time_per_timed_display"])
        self.assertTrue(all(r["deadline_seconds"] is None for r in tables["latencies"]))

    def test_no_full_horizon_outcome_or_default_for_unanswered_prefix(self):
        case, payload = fixture(weeks_to_submit=5)
        metrics, _ = analysis.extract_metrics(payload, case)
        self.assertFalse(metrics["complete_primary_endpoints"])
        self.assertIsNone(metrics["chain_total_cost"])
        self.assertIsNone(metrics["mean_role_order_variance"])
        self.assertIsNone(metrics["pipeline_sensitivity"])
        self.assertEqual(payload["missing"]["weeks"], list(range(6, 25)))
        self.assertEqual(len(payload["decisions"]), 5)

    def main_rows(self):
        blocks = [f"c3m{i:03d}" for i in range(1, 11)]
        plan = dict(block_ids=blocks, controller_schema=controller.SCHEMA, frozen=True,
                    independent_blocks_confirmed=True, prompt_version="V3")
        rows = []
        for block in blocks:
            for arm in "ABC":
                rows.append(dict(stage="main", block_id=block, arm=arm, prompt_version="V3", seed=int(block[3:]),
                                 profile_ids=[0, 1, 2, 3], replay_valid=True, analysis_error=None, complete=True,
                                 complete_primary_endpoints=True, complete_24_weeks=True, adherence=dict(passed=True),
                                 pipeline_sensitivity={"A":2,"B":1,"C":3}[arm], chain_total_cost={"A":10,"B":20,"C":15}[arm],
                                 mean_role_order_variance={"A":3,"B":4,"C":2}[arm], mean_role_bullwhip={"A":1.5,"B":2,"C":1}[arm]))
        return plan, rows

    def test_main_fixed_sample_holm_and_prefix_gate(self):
        plan, rows = self.main_rows()
        result = analysis.analyze_stage(rows, stage="main", plan=plan)
        self.assertTrue(result["inference_enabled"], result["gate_reasons"])
        self.assertEqual(result["complete_blocks"], 10)
        self.assertTrue(all(r["p_two_sided"] == 2 / 1024 and r["p_holm_family_5"] == 10 / 1024 for r in result["endpoints"]))
        self.assertTrue(all(r["p_two_sided"] is None for r in result["prefixes"] if r["prefix_size"] == 1))
        self.assertTrue(all(r["p_two_sided"] == .5 for r in result["prefixes"] if r["prefix_size"] == 2))
        partial = analysis.analyze_stage(rows[:-1], stage="main", plan=plan)
        self.assertFalse(partial["inference_enabled"])
        self.assertEqual(partial["endpoints"][0]["n_pairs"], 10)
        self.assertTrue(all(r["p_two_sided"] is None for r in partial["endpoints"] + partial["prefixes"]))

    def test_development_one_pair_is_descriptive_and_stays_separate(self):
        plan, rows = self.main_rows()
        dev = [dict(r, stage="development") for r in rows[:3]]
        result = analysis.analyze_stage(dev + rows, stage="development")
        self.assertEqual(result["saved_contexts"], 3)
        self.assertTrue(all(r["n_pairs"] == 1 and r["p_two_sided"] is None for r in result["endpoints"]))
        self.assertEqual(result["endpoints"][0]["mean_difference"], -1)

    def test_loader_ignores_strict_and_carry_samples_and_checks_reviews(self):
        with tempfile.TemporaryDirectory() as directory:
            experiment = Path(directory)
            for relative in ("data/feasibility/old/RESULT.json", "data/carry_forward_v2/development/old/RESULT.json"):
                old = experiment / relative
                old.parent.mkdir(parents=True)
                old.write_bytes(b"UNCHANGED HISTORICAL BYTES\r\n")
            folder = experiment / analysis.DATA / "development/synthetic"
            folder.mkdir(parents=True)
            analysis.write_json(folder / "CASE.json", self.case)
            analysis.write_json(folder / "RESULT.json", self.payload)
            analysis.write_json(folder / "ADHERENCE_REVIEW.json", dict(passed=True, result_sha256=analysis.sha256(folder / "RESULT.json"),
                                case_sha256=controller.digest(self.case), full_public_context_reviewed=True, fresh_context_confirmed=True,
                                literal_model_choices_confirmed=True, fixed_requested_settings_confirmed=True))
            rows, _ = analysis.load_runs(experiment)
            self.assertEqual(len(rows), 1)
            self.assertTrue(rows[0]["replay_valid"])
            self.assertTrue(rows[0]["adherence"]["passed"])
            self.assertIsNone(rows[0]["model_runtime_limit_seconds"])

    def test_history_uses_framing_subtree_and_preserves_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            experiment = Path(directory)
            report = experiment / analysis.REPORTS / "REPORT.md"
            report.parent.mkdir(parents=True)
            report.write_bytes(b"ORIGINAL FRAMING\r\n")
            analysis.write_json(experiment / analysis.ANALYSIS / "CURRENT.json", dict(fingerprint="a" * 64,
                                generated_files={report.relative_to(experiment).as_posix(): analysis.sha256(report)}))
            analysis.preserve_previous(experiment, "b" * 64)
            self.assertEqual((experiment / analysis.REPORTS / "history" / ("a" * 16) / "REPORT.md").read_bytes(), b"ORIGINAL FRAMING\r\n")


if __name__ == "__main__":
    unittest.main()
