import importlib.util
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("human_planning", ROOT / "scripts/plan_human_study.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HumanStudyPlanningTests(unittest.TestCase):
    def test_both_cues_are_needed_to_identify_gap(self):
        for mode, expected in [("optimal", (1, 1, 0)),
                               ("ignore", (1, 0, 1)),
                               ("half", (.5, .5, 0))]:
            df = module.stock_states()
            df["order"] = (df.demand-df.inventory-df.pipeline if mode == "optimal"
                           else df.demand-df.inventory if mode == "ignore"
                           else (df.demand-df.inventory-df.pipeline)/2)
            got = module.estimate_stock_weights(df)
            np.testing.assert_allclose([got["k_inventory"], got["k_pipeline"], got["gap"]],
                                       expected, atol=1e-10)

    def test_missing_duplicate_or_off_design_is_not_filled(self):
        df = module.stock_states()
        df["order"] = df.benchmark_order
        with self.assertRaises(ValueError):
            module.estimate_stock_weights(df.iloc[:-1])
        duplicate = df.copy()
        duplicate.iloc[-1] = duplicate.iloc[0]
        with self.assertRaises(ValueError):
            module.estimate_stock_weights(duplicate)
        df.loc[0, "inventory"] = 999
        with self.assertRaises(ValueError):
            module.estimate_stock_weights(df)

    def test_gap_example_and_weak_denominator(self):
        df = module.stock_states()
        df["order"] = 22-.75*df.inventory-.25*df.pipeline
        got = module.estimate_stock_weights(df)
        self.assertAlmostEqual(got["gap"], .5)
        self.assertAlmostEqual(got["relative_pipeline_weight_descriptive"], 1/3)
        df["order"] = 4
        got = module.estimate_stock_weights(df)
        self.assertIsNone(got["relative_pipeline_weight_descriptive"])

    def test_backlog_not_double_counted(self):
        state = module.week_end(2, 5, 3, 4)
        self.assertEqual(state, dict(shipped=5, inventory=0, backlog=4))
        self.assertEqual(state["inventory"]-state["backlog"], (2-5)+3-4)

    def test_variance_is_within_role_not_pooled(self):
        orders = np.array([[1, 101, 201, 301], [3, 103, 203, 303]])
        inv = np.zeros_like(orders)
        back = np.ones_like(orders)
        got = module.chain_metrics(orders, inv, back, [1, 3])
        self.assertEqual(got["mean_order_variance"], 2)
        self.assertEqual(got["bullwhip_ratio"], 1)
        self.assertEqual(got["total_cost"], 8)
        self.assertIsNone(module.chain_metrics(orders, inv, back, [2, 2])["bullwhip_ratio"])

    def test_h5_normative_weight_changes(self):
        for r in module.routine_states().query("phase == 'transfer'").itertuples():
            self.assertEqual(module.routine_persistence(r.old_benchmark, r.inventory,
                                                        r.early_pipeline, r.late_pipeline), 1)
            self.assertEqual(module.routine_persistence(r.new_benchmark, r.inventory,
                                                        r.early_pipeline, r.late_pipeline), 0)
            self.assertLess(module.routine_persistence(r.new_benchmark+4, r.inventory,
                                                       r.early_pipeline, r.late_pipeline), 0)

    def test_power_matches_type_one_and_sample_boundary(self):
        self.assertAlmostEqual(module.contrast_power(10, 0, .65), module.ALPHA)
        simple = module.required_size(lambda k: module.contrast_power(k, .5, .65))
        interaction = module.required_size(lambda k: module.contrast_power(k, .5, 1.3))
        self.assertEqual(simple, 38)
        self.assertEqual(interaction, 71)
        self.assertLess(module.contrast_power(simple-1, .5, .65), .8)
        self.assertGreaterEqual(module.contrast_power(simple, .5, .65), .8)
        self.assertLess(module.contrast_power(10, .5, 1.3),
                        module.contrast_power(10, .5, .65))

    def test_large_noncentrality_has_finite_power(self):
        for k, effect, variance in [(10, 10, .65), (97, .5, .65), (200, .8, .65)]:
            got = module.contrast_power(k, effect, variance)
            self.assertTrue(np.isfinite(got))
            self.assertGreater(got, .95)
            self.assertLessEqual(got, 1)


if __name__ == "__main__":
    unittest.main()
