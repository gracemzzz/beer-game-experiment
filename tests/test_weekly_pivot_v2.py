"""Offline invariants for the new resource-opportunity engine; fixtures are synthetic."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import weekly_pivot_v2 as study


class WeeklyPivotEngineTests(unittest.TestCase):
    def setUp(self):
        self.plan = study.make_plan(blocks=2, models=("test-model",))
        self.model = "test-model"
        self.block = "b0001"

    def response(self, task, *, value=4):
        result = {key: task[key] for key in ("schema_version", "study_id", "task_id")}
        if task["phase"] in ("probe", "probe_revision"):
            # Synthetic known-slope fixture, never used as model observations.
            result["decisions"] = {state["probe_id"]: state["backlog"] + 8 - state["supply_line"]
                                   for state in task["probes"]}
        else:
            result["orders"] = {cid: [value] * 4 for cid in task["chain_ids"]}
        return result

    def collect(self, arm="B", *, weeks=24, probes=True, value=4):
        accepted = {}
        for week in range(1, weeks + 1):
            phases = ("initial", "revision") if arm == "A" else ("initial",)
            for phase in phases:
                task = study.build_task(self.plan, self.model, self.block, arm, week, phase, accepted)
                accepted[task["task_id"]] = self.response(task, value=value)
        if probes and weeks == 24:
            phases = ("probe", "probe_revision") if arm == "A" else ("probe",)
            for phase in phases:
                task = study.build_task(self.plan, self.model, self.block, arm, phase=phase, accepted=accepted)
                accepted[task["task_id"]] = self.response(task)
        return accepted

    def test_plan_fingerprints_design_and_repeats_without_mutation(self):
        self.assertEqual(self.plan, study.make_plan(blocks=2, models=(self.model,)))
        self.assertEqual(self.plan["expected_requests"], 200)
        self.assertEqual(self.plan["expected_weekly_requests"], 192)
        self.assertEqual(self.plan["lecture_word_counts"], {"control": 127, "causal_education": 127})
        heldout = study.make_plan(blocks=2, models=(self.model,), collection_kind="heldout")
        self.assertNotEqual(heldout["study_id"], self.plan["study_id"])
        self.assertFalse(heldout["development_only"])
        changed = study.make_plan(blocks=2, chains_per_cluster=2, models=(self.model,))
        self.assertNotEqual(changed["study_id"], self.plan["study_id"])
        self.assertEqual(changed["expected_requests"], 200)  # Batched chains do not create replication.
        for kwargs in ({"blocks": True}, {"chains_per_cluster": 0}, {"collection_kind": "main"}):
            with self.assertRaises(ValueError):
                study.make_plan(**kwargs)

    def test_future_demand_does_not_enter_current_prompt(self):
        task = study.build_task(self.plan, self.model, self.block, "B", 1)
        future_changed = copy.deepcopy(self.plan)
        future_changed["blocks"][0]["chains"][0]["customer_demand"][1:] = [99999] * 23
        future = study.build_task(future_changed, self.model, self.block, "B", 1)
        self.assertEqual(study.prompt_text(task), study.prompt_text(future))
        self.assertNotIn("customer_demand", study.prompt_text(task))
        self.assertNotIn("100000", study.prompt_text(task))
        self.assertNotIn("maxItems", study.prompt_text(task))
        self.assertNotIn("24 weeks", study.prompt_text(task))

    def test_revision_does_not_advance_and_initial_is_not_committed(self):
        initial = study.build_task(self.plan, self.model, self.block, "A", 1)
        accepted = {initial["task_id"]: self.response(initial, value=99)}
        revision = study.build_task(self.plan, self.model, self.block, "A", 1, "revision", accepted)
        self.assertEqual(initial["states"], revision["states"])
        self.assertEqual(initial["history"], revision["history"])
        self.assertEqual(revision["initial_orders"], {"c001": [99] * 4})
        with self.assertRaisesRegex(ValueError, "Missing accepted decision"):
            study.build_task(self.plan, self.model, self.block, "A", 2, accepted=accepted)
        accepted[revision["task_id"]] = self.response(revision, value=0)
        final_games, rows = study.replay_prefix(self.plan, self.model, self.block, "A", accepted, 1)
        self.assertEqual([row["order"] for row in rows], [0] * 4)
        self.assertEqual(final_games["c001"].week, 1)
        self.assertFalse(final_games["c001"].awaiting)
        with self.assertRaisesRegex(ValueError, "no revision"):
            study.build_task(self.plan, self.model, self.block, "B", 1, "revision")

    def test_separate_arms_never_expose_each_others_responses(self):
        b = self.collect("B", weeks=1, probes=False, value=0)
        b_next = study.build_task(self.plan, self.model, self.block, "B", 2, accepted=b)
        a = self.collect("A", weeks=1, probes=False, value=99999)
        isolated = study.build_task(self.plan, self.model, self.block, "B", 2, accepted={**b, **a})
        self.assertEqual(study.prompt_text(b_next), study.prompt_text(isolated))
        a_initial = study.build_task(self.plan, self.model, self.block, "A", 1)
        b_initial = study.build_task(self.plan, self.model, self.block, "B", 1)
        self.assertEqual(a_initial["states"], b_initial["states"])
        self.assertEqual(a_initial["lecture"], b_initial["lecture"])

    def test_validation_preserves_zero_but_never_fills_missing_orders(self):
        task = study.build_task(self.plan, self.model, self.block, "B", 1)
        payload = self.response(task, value=0)
        self.assertEqual(study.validate_response(task, payload), [])
        for value in (False, -1, 1.5, 100001):
            changed = copy.deepcopy(payload)
            changed["orders"]["c001"][0] = value
            self.assertTrue(study.validate_response(task, changed))
        del payload["orders"]["c001"]
        self.assertTrue(study.validate_response(task, payload))
        with self.assertRaisesRegex(ValueError, "Invalid accepted decision"):
            study.replay_prefix(self.plan, self.model, self.block, "B", {task["task_id"]: payload}, 1)
        self.assertNotIn("maximum", str(study.response_schema(task)))

    def test_cost_variance_and_zero_denominator_are_not_fabricated(self):
        self.plan["blocks"][0]["chains"][0]["customer_demand"] = [4] * 24
        accepted = self.collect("B", probes=False)
        row = study.block_outcomes(self.plan, self.model, self.block, "B", accepted)
        self.assertTrue(row["complete"])
        self.assertFalse(row["probe_complete"])
        self.assertEqual(row["weeks"], 24)
        self.assertEqual(row["chain_total_cost"], 576)
        self.assertEqual(row["cluster_total_cost"], 576)
        self.assertEqual(row["mean_role_order_variance"], 0)
        self.assertIsNone(row["mean_role_bullwhip"])
        self.assertEqual(row["undefined_bullwhip_roles"], 4)
        self.assertEqual(row["game_zero_order_fraction"], 0)
        self.assertIsNone(row["pipeline_sensitivity"])
        self.assertEqual(len(row["missing_probes"]), 1)
        self.assertFalse(row["missing_tasks"])

    def test_orthogonal_probes_and_diagnostics_match_known_synthetic_slopes(self):
        for arm in ("A", "B", "C"):
            accepted = self.collect(arm)
            task = study.build_task(self.plan, self.model, self.block, arm, phase="probe", accepted=accepted)
            self.assertEqual(len(task["probes"]), 16)
            combinations = {(state["role"], state["backlog"], state["supply_line"]) for state in task["probes"]}
            self.assertEqual(len(combinations), 16)
            row = study.block_outcomes(self.plan, self.model, self.block, arm, accepted)
            self.assertTrue(row["complete"])
            self.assertTrue(row["probe_complete"])
            self.assertEqual(row["pipeline_sensitivity"], 1)
            self.assertEqual(row["backlog_sensitivity"], 1)
            self.assertEqual(row["probe_zero_order_fraction"], 0)
            self.assertIsNotNone(row["mean_role_bullwhip"])

    def test_incomplete_games_have_no_projected_cost_or_filled_weeks(self):
        accepted = self.collect("B", weeks=2, probes=False)
        row = study.block_outcomes(self.plan, self.model, self.block, "B", accepted)
        self.assertEqual(row["weeks"], 2)
        self.assertFalse(row["complete"])
        self.assertIsNone(row["chain_total_cost"])
        self.assertIsNone(row["mean_role_order_variance"])
        with self.assertRaisesRegex(ValueError, "Missing accepted decision"):
            study.build_task(self.plan, self.model, self.block, "B", phase="probe", accepted=accepted)


if __name__ == "__main__":
    unittest.main()
