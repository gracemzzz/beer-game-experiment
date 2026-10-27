"""Numerical and fail-closed checks; every response fixture here is SYNTHETIC."""
import copy
import json
from pathlib import Path
import statistics
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import exp14_analysis as analysis


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.probes = analysis.read_json(analysis.EXPERIMENT / "prompts/probes.json")

    def test_pair_slopes_have_prespecified_sign_units_and_weights(self):
        # Researcher-authored linear response fixtures, never model observations.
        answers = {p["probe_id"]: 100 - p["outstanding"] // 2 + 2 * p["backlog"] for p in self.probes}
        metrics, pairs, residuals, summaries = analysis.probe_metrics(self.probes, answers)
        self.assertEqual(metrics["pipeline_sensitivity"], .5)
        self.assertEqual(metrics["backlog_sensitivity"], 2)
        self.assertEqual(len(pairs), 16)
        self.assertEqual(len(residuals), 32)
        self.assertTrue(all(abs(r["residual"]) < 1e-10 for r in residuals))
        self.assertTrue(all(r["mean_response_slope"] == (.5 if r["assay_dimension"] == "pipeline" else 2) for r in summaries))

    def test_missing_pair_does_not_silently_reweight_primary_endpoint(self):
        answers = {p["probe_id"]: 7 for p in self.probes}
        missing = next(p for p in self.probes if p["assay_dimension"] == "pipeline")
        del answers[missing["probe_id"]]
        metrics, pairs, _, summaries = analysis.probe_metrics(self.probes, answers)
        self.assertIsNone(metrics["pipeline_sensitivity"])
        self.assertEqual(metrics["backlog_sensitivity"], 0)
        self.assertEqual(sum(p["complete"] for p in pairs), 15)
        self.assertTrue(metrics["probe_all_observed_orders_equal"])
        self.assertEqual(next(r for r in summaries if r["assay_dimension"] == "pipeline" and r["role"] == "all")["observed_orders"], 15)

    def test_private_case_scoring_survives_no_current_bank(self):
        public = [{key: p[key] for key in analysis.PROBE_FIELDS} for p in self.probes]
        scoring = {p["probe_id"]: {key: p[key] for key in ("pair_id", "assay_dimension")} for p in self.probes}
        self.assertEqual(analysis.scoring_bank(dict(probes=public, assay_scoring=scoring), "probes", []), self.probes)
        altered = copy.deepcopy(public)
        altered[0]["inventory"] += 1
        with self.assertRaises(ValueError):
            analysis.scoring_bank(dict(probes=altered), "probes", self.probes)

    def test_complete_horizon_variance_and_prefix_cost_are_distinct(self):
        weeks = [dict(week=w + 1, customer_demand=w % 9, orders=[w, 2 * w, 3 * w, 0],
                      roles=[dict(inventory=2, backlog=0, supply_line=3)] * 4) for w in range(24)]
        metrics, roles = analysis.game_metrics(dict(planned_weeks=24, weeks=weeks))
        v = statistics.variance(range(24))
        d = statistics.variance([w % 9 for w in range(24)])
        self.assertEqual(metrics["chain_total_cost"], 96)
        self.assertEqual(metrics["mean_role_order_variance"], 14 * v / 4)
        self.assertAlmostEqual(metrics["mean_role_bullwhip"], 14 * v / (4 * d))
        self.assertEqual(roles[0]["final_observed_outstanding_after_order"], 26)
        partial, _ = analysis.game_metrics(dict(planned_weeks=24, weeks=weeks[:3]))
        self.assertEqual(partial["completed_prefix_cost"], 12)
        for key in ("chain_total_cost", "mean_role_order_variance", "mean_role_bullwhip"):
            self.assertIsNone(partial[key])
        for row in weeks:
            row["customer_demand"] = 4
        zero, _ = analysis.game_metrics(dict(planned_weeks=24, weeks=weeks))
        self.assertIsNone(zero["mean_role_bullwhip"])

    def test_main_fixed_sample_gate_and_exact_sign_flip_holm(self):
        blocks = [f"m{i:03d}" for i in range(1, 11)]
        plan = dict(block_ids=blocks, frozen=True, independent_blocks_confirmed=True, prompt_version="V1")
        rows = []
        for block in blocks:
            for arm in "ABC":
                rows.append(dict(stage="main", block_id=block, arm=arm, prompt_version="V1", seed=int(block[1:]),
                                 profile_ids=[0, 1, 2, 3], replay_valid=True, full_behavior_complete=True,
                                 complete_24_weeks=True, adherence=dict(passed=True), pipeline_sensitivity={"A":2,"B":1,"C":3}[arm],
                                 chain_total_cost={"A":10,"B":20,"C":15}[arm],
                                 mean_role_order_variance={"A":3,"B":4,"C":2}[arm],
                                 mean_role_bullwhip={"A":1.5,"B":2,"C":1}[arm]))
        full = analysis.main_analysis(rows, plan)
        self.assertTrue(full["eligible"])
        self.assertEqual(full["complete_matched_blocks"], 10)
        for endpoint in full["endpoints"]:
            self.assertEqual(endpoint["n_pairs"], 10)
            self.assertEqual(endpoint["p_two_sided"], 2 / 1024)
            self.assertEqual(endpoint["p_holm_family_5"], 10 / 1024)
            self.assertEqual(endpoint["direction"], "predicted")
        incomplete = analysis.main_analysis(rows[:-1], plan)
        self.assertFalse(incomplete["eligible"])
        self.assertEqual(incomplete["complete_matched_blocks"], 9)
        self.assertTrue(all(r["p_two_sided"] is None for r in incomplete["endpoints"]))
        self.assertEqual(incomplete["endpoints"][0]["n_pairs"], 10)
        rows[0]["adherence"]["passed"] = False
        self.assertFalse(analysis.main_analysis(rows, plan)["eligible"])

    def test_adherence_needs_exact_hashes_and_every_review_check(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            path = folder / "ADHERENCE_REVIEW.json"
            review = dict(passed=True, result_sha256="result", case_sha256="case", full_public_context_reviewed=True,
                          fresh_context_confirmed=True, literal_model_choices_confirmed=True, fixed_requested_settings_confirmed=True)
            analysis.write_json(path, review)
            self.assertTrue(analysis.adherence_review(folder, "result", "case")["passed"])
            self.assertFalse(analysis.adherence_review(folder, "different", "case")["passed"])
            review["fresh_context_confirmed"] = False
            analysis.write_json(path, review)
            self.assertFalse(analysis.adherence_review(folder, "result", "case")["passed"])

    def test_stages_never_pool_and_one_pair_has_no_pvalue(self):
        row = dict(stage="main", block_id="m001", arm="A", replay_valid=True, pipeline_sensitivity=1)
        other = dict(row, arm="B", pipeline_sensitivity=2)
        development = [dict(row, stage="feasibility"), dict(other, stage="feasibility")]
        result = analysis.main_analysis([row, other, *development], None)
        self.assertEqual(result["observed_contexts"], 2)
        self.assertEqual(result["endpoints"][0]["n_pairs"], 1)
        self.assertEqual(result["endpoints"][0]["mean_difference"], 1)
        self.assertIsNone(result["endpoints"][0]["p_two_sided"])

    def test_history_keeps_prior_generated_bytes_before_rebuild(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            report = folder / "reports/REPORT.md"
            report.parent.mkdir()
            report.write_bytes(b"ORIGINAL REPORT\r\n")
            original = report.read_bytes()
            analysis.write_json(folder / "analysis/CURRENT.json", dict(fingerprint="a" * 64,
                                generated_files={"reports/REPORT.md": analysis.sha256(report)}))
            analysis.preserve_previous(folder, "b" * 64)
            report.write_bytes(b"NEW REPORT\n")
            preserved = folder / "reports/history" / ("a" * 16) / "REPORT.md"
            self.assertEqual(preserved.read_bytes(), original)
            with self.assertRaises(ValueError):
                analysis.preserve_previous(folder, "c" * 64)


if __name__ == "__main__":
    unittest.main()
