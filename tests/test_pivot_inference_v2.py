"""Explicit synthetic controls for offline inference; never study observations."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import pivot_inference_v2 as subject


def plan(n=10, models=("synthetic_model",)):
    return dict(schema_version=subject.PLAN_SCHEMA, models=list(models),
                block_ids=[f"block_{i:03d}" for i in range(n)], weeks=24,
                sweep_sizes=[10, 20, 40], source_kind="synthetic_software_control",
                provenance_verified=False, independent_blocks_confirmed=True,
                bootstrap_resamples=1000, monte_carlo_resamples=2000, seed=17)


def controls(config, direction=1):
    """Known-effect synthetic three-arm blocks, already aggregated over chains."""
    rows = []
    for model in config["models"]:
        for index, block in enumerate(config["block_ids"]):
            for arm in subject.ARMS:
                d = direction * {"A": 0, "B": 1, "C": 0}[arm]
                rows.append(dict(model=model, block_id=block, arm=arm, complete=True, weeks=24,
                                 chains_in_cluster=4, pipeline_sensitivity=10 - d,
                                 chain_total_cost=100 + index + d,
                                 mean_role_order_variance=20 + d,
                                 mean_role_bullwhip=5 + d))
    return rows


class PairedMathTests(unittest.TestCase):
    def test_exact_known_constant_nonzero_and_zero_controls(self):
        result = subject.paired_inference([1] * 10, bootstrap_resamples=1000)
        self.assertEqual(result["p_two_sided"], 2 / 1024)
        self.assertEqual(result["mean_difference"], 1)
        self.assertEqual((result["ci95_low"], result["ci95_high"]), (1, 1))
        self.assertEqual(result["test"], "exact_paired_sign_flip")
        zero = subject.paired_inference([0] * 5, bootstrap_resamples=1000)
        self.assertEqual(zero["p_two_sided"], 1)
        self.assertEqual(zero["ci95_low"], 0)
        self.assertIsNone(subject.paired_inference([])["p_two_sided"])
        large = subject.paired_inference([1e308] * 10, bootstrap_resamples=1000)
        self.assertEqual(large["mean_difference"], 1e308)
        self.assertEqual(large["ci95_high"], 1e308)

    def test_monte_carlo_is_deterministic_and_two_sided_symmetric(self):
        plus = subject.paired_inference([1] * 20, seed=99, bootstrap_resamples=1000, monte_carlo_resamples=2000)
        minus = subject.paired_inference([-1] * 20, seed=99, bootstrap_resamples=1000, monte_carlo_resamples=2000)
        again = subject.paired_inference([1] * 20, seed=99, bootstrap_resamples=1000, monte_carlo_resamples=2000)
        self.assertEqual(plus, again)
        self.assertEqual(plus["p_two_sided"], minus["p_two_sided"])
        self.assertGreater(plus["p_two_sided"], 0)
        self.assertEqual(plus["test"], "monte_carlo_paired_sign_flip")
        for value in ([float("nan")], [float("inf")], [[1, 2]]):
            with self.assertRaises(ValueError):
                subject.paired_inference(value)

    def test_holm_retains_missing_family_positions(self):
        self.assertEqual(subject.holm_adjust([.01, .04, .03, None, 1]), [.05, .12, .12, None, 1])
        with self.assertRaises(ValueError):
            subject.holm_adjust([-1])


class BlockAnalysisTests(unittest.TestCase):
    def test_known_effects_have_correct_contrasts_and_only_ten_units(self):
        config = plan()
        result = subject.analyze(config, controls(config))
        self.assertEqual(len(result["primary"]), 5)
        for row in result["primary"]:
            self.assertEqual(row["n_pairs"], 10)
            self.assertEqual(row["matched_treated_chains"], 40)
            self.assertEqual(row["matched_control_chains"], 40)
            self.assertEqual(row["direction"], "predicted")
            self.assertEqual(row["statistical_pattern"], "significant_predicted_direction")
            self.assertFalse(row["used_in_scientific_findings"])
            self.assertEqual(row["inference_status"], "synthetic_control_only")
        self.assertFalse(result["chains_are_independent_observations"])
        self.assertIn("Synthetic software controls", subject.report_markdown(result))

    def test_opposite_significant_effects_are_not_called_support(self):
        config = plan()
        result = subject.analyze(config, controls(config, direction=-1))
        self.assertTrue(all(r["direction"] == "opposite" for r in result["primary"]))
        self.assertTrue(all(r["statistical_pattern"] == "significant_opposite_direction" for r in result["primary"]))

    def test_development_model_observations_cannot_be_promoted_to_heldout_findings(self):
        config = plan()
        config.update(source_kind="model_observations", collection_kind="development", development_only=True)
        result = subject.analyze(config, controls(config))
        self.assertTrue(all(not row["used_in_scientific_findings"] for row in result["primary"]))
        self.assertTrue(all(row["inference_status"] == "development_only" for row in result["primary"]))
        self.assertIn("excluded from heldout", subject.report_markdown(result))
        with self.assertRaises(ValueError):
            subject.validate_plan({**config, "collection_kind": "heldout"})

    def test_missing_rows_and_partial_games_have_endpoint_specific_denominators(self):
        config = plan()
        rows = controls(config)
        rows = [r for r in rows if not (r["block_id"] == "block_000" and r["arm"] == "A")]
        for row in rows:
            if row["block_id"] == "block_001" and row["arm"] == "B":
                row.update(complete=False, weeks=12)
        result = subject.analyze(config, rows)
        indexed = {r["hypothesis"]: r for r in result["primary"]}
        self.assertEqual(indexed["H1"]["n_pairs"], 8)
        self.assertEqual(indexed["H2"]["n_pairs"], 8)
        self.assertEqual(indexed["H3"]["n_pairs"], 9)
        self.assertFalse(indexed["H1"]["planned_sample_complete"])
        self.assertFalse(result["all_planned_rows_received"])
        self.assertEqual(result["complete_game_cluster_arm_rows"], 28)
        self.assertEqual(result["partial_game_cluster_arm_rows"], 1)
        self.assertEqual(result["unobserved_game_cluster_arm_rows"], 0)
        self.assertEqual(result["missing_csv_rows"], 1)
        self.assertEqual(len(result["missing_cluster_arm_rows"]), 1)
        config["pipeline_probe_independent_of_game_completion"] = True
        result2 = subject.analyze(config, rows)
        indexed2 = {r["hypothesis"]: r for r in result2["primary"]}
        self.assertEqual(indexed2["H1"]["n_pairs"], 9)
        self.assertEqual(indexed2["H3"]["n_pairs"], 10)
        self.assertEqual(indexed2["H2"]["n_pairs"], 8)

    def test_all_planned_placeholders_are_zero_collected_games(self):
        config = plan()
        placeholders = controls(config)
        for row in placeholders:
            row.update(complete=False, weeks=0)
            row.update({metric: None for metric in subject.METRICS})
        result = subject.analyze(config, placeholders)
        self.assertEqual(result["supplied_csv_rows"], 30)
        self.assertTrue(result["all_planned_rows_received"])
        self.assertEqual(result["missing_csv_rows"], 0)
        self.assertEqual(result["complete_game_cluster_arm_rows"], 0)
        self.assertEqual(result["unobserved_game_cluster_arm_rows"], 30)
        self.assertEqual(result["partial_game_cluster_arm_rows"], 0)
        self.assertFalse(result["all_planned_games_complete"])
        self.assertFalse(result["all_primary_endpoint_samples_complete"])
        self.assertTrue(all(row["n_pairs"] == 0 and row["p_two_sided"] is None for row in result["primary"]))
        report = subject.report_markdown(result)
        self.assertIn("Completed 24-week games: 0/30", report)
        self.assertIn("unobserved games (zero weeks): 30", report)
        self.assertIn("placeholder rows are not collected model responses", report)

    def test_zero_variance_undefined_bullwhip_stays_missing(self):
        config = plan()
        rows = controls(config)
        for row in rows:
            row["mean_role_bullwhip"] = None
        result = subject.analyze(config, rows)
        h4b = result["primary"][-1]
        self.assertEqual(h4b["n_pairs"], 0)
        self.assertIsNone(h4b["p_two_sided"])
        self.assertIsNone(h4b["p_holm_within_model_5"])

    def test_refuses_duplicate_unplanned_nonfinite_and_partial_complete_inputs(self):
        config = plan()
        good = controls(config)
        bads = [good + [good[0]], [{**good[0], "arm": "D"}], [{**good[0], "block_id": "unplanned"}],
                [{**good[0], "chain_total_cost": float("nan")}], [{**good[0], "weeks": 23}],
                [{**good[0], "mean_role_order_variance": -1}], [{**good[0], "chains_in_cluster": 0}],
                [{**good[0], "complete": "yes"}]]
        for bad in bads:
            with self.subTest(bad=bad[0]):
                with self.assertRaises(ValueError):
                    subject.analyze(config, bad)

    def test_fixed_sweeps_preserve_order_and_twenty_endpoint_family(self):
        config = plan(20, models=("s1", "s2", "s3", "s4"))
        rows = controls(config)
        result = subject.analyze(config, rows)
        self.assertEqual(len(result["primary"]), 20)
        self.assertEqual(len(result["sweeps"]), 40)
        self.assertEqual(result["sweep_sizes_not_planned"], [40])
        prefix10 = [r for r in result["sweeps"] if r["analysis"] == "prefix_10"]
        self.assertTrue(all(r["matched_block_ids"] == config["block_ids"][:10] for r in prefix10))
        self.assertTrue(all(r["p_holm_across_models_20"] is not None for r in result["primary"]))
        prefix20 = [r for r in result["sweeps"] if r["analysis"] == "prefix_20"]
        for primary, sweep in zip(result["primary"], prefix20):
            for key in ("p_two_sided", "ci95_low", "ci95_high", "p_holm_within_model_5", "p_holm_across_models_20"):
                self.assertEqual(primary[key], sweep[key])
        # A model absent from supplied observations keeps its uncollected rows;
        # the full four-model adjustment is unavailable, not silently shrunk.
        result2 = subject.analyze(config, [r for r in rows if r["model"] != "s4"])
        self.assertTrue(all(r["p_holm_across_models_20"] is None for r in result2["primary"]))
        with self.assertRaises(ValueError):
            subject.validate_plan({**config, "sweep_sizes": [5, 10]})
        with self.assertRaises(ValueError):
            subject.validate_plan({**config, "bootstrap_resamples": "1000"})

    def test_provenance_flag_is_only_caller_assertion_and_cli_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            config = plan()
            config.update(source_kind="model_observations", provenance_verified=True)
            pp, cp, out = base / "PLAN.json", base / "INPUT.csv", base / "analysis"
            pp.write_text(json.dumps(config), encoding="utf-8")
            with cp.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=subject.REQUIRED_COLUMNS)
                writer.writeheader()
                writer.writerows(controls(config))
            loaded, rows, evidence = subject.load_inputs(pp, cp)
            self.assertEqual(evidence["provenance_status"], "caller_assertion_only")
            self.assertFalse(evidence["raw_api_lineage_independently_verified_by_this_module"])
            spec = importlib.util.spec_from_file_location("pivot_cli_test", ROOT / "scripts/analyze_pivot_v2.py")
            cli = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cli)
            result = cli.main(["--plan", str(pp), "--input", str(cp), "--output", str(out)])
            before = (out / "ANALYSIS.json").read_bytes()
            cli.main(["--plan", str(pp), "--input", str(cp), "--output", str(out)])
            self.assertEqual((out / "ANALYSIS.json").read_bytes(), before)
            config["seed"] += 1
            pp.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaises(ValueError):
                cli.main(["--plan", str(pp), "--input", str(cp), "--output", str(out)])
            self.assertEqual((out / "ANALYSIS.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
