"""Scientific/state tests for weekly batches; temporary synthetic fixtures only."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import weekly_pressure as study
from beergame_study.batched_pressure_api import BudgetLedger


class WeeklyPressureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.experiment = self.root / "experiments/13_weekly"
        self.budget = self.root / "experiments/12_original"
        (self.experiment / "hypotheses").mkdir(parents=True)
        shutil.copyfile(ROOT / "experiments/13_weekly_state_api_20261021/hypotheses/PROTOCOL.md",
                        self.experiment / "hypotheses/PROTOCOL.md")
        ledger = BudgetLedger(self.budget)
        ledger.reserve("prior_paid_run", .34, {"run": "earlier_actual_study"})
        ledger.settle("prior_paid_run", .34, "received")
        self.run = study.prepare(self.experiment, self.budget)
        self.plan = study.loadplan(self.run)
        self.model = self.plan["models"][0]

    def full_model(self, model=None, *, weeks=24, probes=True):
        model = model or self.model
        accepted = {}
        task = study.build_task(self.plan, model, "pilot")
        accepted[task["task_id"]] = study.synthetic_fixture(task)
        for week in range(1, weeks + 1):
            task = study.build_task(self.plan, model, "main", week=week, accepted=accepted)
            accepted[task["task_id"]] = study.synthetic_fixture(task)
        if probes:
            task = study.build_task(self.plan, model, "probe", accepted=accepted)
            accepted[task["task_id"]] = study.synthetic_fixture(task)
        return accepted

    def save_analysis_fixtures(self, accepted):
        """Fake receipt hashes isolate scientific analysis from API audit tests."""
        status = {"tasks": {}}
        for ident, payload in accepted.items():
            path = self.run / "accepted" / (ident + ".json")
            study.save_new(path, payload)
            status["tasks"][ident] = {"status": "accepted", "accepted_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        (self.run / "api_status.json").write_text(json.dumps(status))
        return patch("beergame_study.weekly_pressure_api.audit_saved", return_value=accepted)

    def test_plan_is_104_calls_and_eighty_main_identities_per_model(self):
        self.assertEqual(self.plan["expected_requests"], 104)
        self.assertEqual(self.plan["expected_pilot_requests"], 4)
        self.assertEqual(self.plan["expected_main_weekly_requests"], 96)
        self.assertEqual(self.plan["expected_probe_requests"], 4)
        main, pilot = self.plan["chains_by_phase"]["main"], self.plan["chains_by_phase"]["pilot"]
        self.assertEqual(len(main), 20)
        self.assertEqual(len(pilot), 20)
        self.assertEqual(sum(c["condition"] == "strong_pressure" for c in main), 10)
        self.assertEqual(sum(c["condition"] == "no_pressure" for c in main), 10)
        main_ids = {p for c in main for p in c["participant_ids"]}
        pilot_ids = {p for c in pilot for p in c["participant_ids"]}
        self.assertEqual(len(main_ids), 80)
        self.assertEqual(len(pilot_ids), 80)
        self.assertFalse(main_ids & pilot_ids)
        for block in range(10):
            pair = [c for c in main if c["block"] == block]
            self.assertEqual(pair[0]["customer_demand"], pair[1]["customer_demand"])
            self.assertEqual(pair[0]["profile_ids"], pair[1]["profile_ids"])
            self.assertEqual(len(pair[0]["customer_demand"]), 24)
        self.assertEqual(self.plan["output_caps"], {"pilot": 2048, "main": 2048, "probe": 4096})

    def test_week_one_is_free_preview_and_later_weeks_require_valid_predecessors(self):
        task = study.build_task(self.plan, self.model, "main", week=1, accepted={})
        self.assertEqual(len(task["states"]), 20)
        self.assertTrue(all(history == [] for history in task["history"].values()))
        with self.assertRaisesRegex(ValueError, "Missing earlier"):
            study.build_task(self.plan, self.model, "main", week=2, accepted={})
        with self.assertRaisesRegex(ValueError, "Missing earlier"):
            study.build_task(self.plan, self.model, "probe", accepted={})
        bad = study.synthetic_fixture(task)
        bad["orders"][task["chain_ids"][0]]["r"] = True
        with self.assertRaisesRegex(ValueError, "Invalid earlier"):
            study.build_task(self.plan, self.model, "main", week=2, accepted={task["task_id"]: bad})

    def test_future_demand_and_stopping_week_never_enter_current_prompt(self):
        task = study.build_task(self.plan, self.model, "main", week=1)
        future = copy.deepcopy(self.plan)
        for chain in future["chains_by_phase"]["main"]:
            chain["customer_demand"][1:] = [987654] * 23
        rebuilt = study.build_task(future, self.model, "main", week=1)
        self.assertEqual(study.prompt_text(task), study.prompt_text(rebuilt))
        self.assertNotIn("987654", study.prompt_text(rebuilt))
        self.assertNotIn("24 weeks", study.prompt_text(task))
        payload = study.synthetic_fixture(task)
        future2 = copy.deepcopy(self.plan)
        for chain in future2["chains_by_phase"]["main"]:
            chain["customer_demand"][2:] = [987654] * 22
        accepted = {task["task_id"]: payload}
        next_original = study.build_task(self.plan, self.model, "main", week=2, accepted=accepted)
        next_changed = study.build_task(future2, self.model, "main", week=2, accepted=accepted)
        self.assertEqual(study.prompt_text(next_original), study.prompt_text(next_changed))

    def test_history_uses_last_four_realized_demand_order_pairs_only(self):
        accepted = self.full_model(weeks=5, probes=False)
        task = study.build_task(self.plan, self.model, "main", week=6, accepted=accepted)
        rows = study.replay(self.plan, self.model, accepted)
        for cid in task["chain_ids"]:
            expected = [[[r["demand"], r["order"]] for r in rows if r["chain_id"] == cid and r["week"] == w]
                        for w in range(2, 6)]
            self.assertEqual(task["history"][cid], expected)
            self.assertEqual(len(task["history"][cid]), 4)
            self.assertEqual(len(task["states"][cid]), 4)

    def test_hand_calculated_constant_flow_cost_is_576_each_chain(self):
        plan = copy.deepcopy(self.plan)
        for chain in plan["chains_by_phase"]["main"]:
            chain["customer_demand"] = [4] * 24
        accepted = {}
        for week in range(1, 25):
            task = study.build_task(plan, self.model, "main", week=week, accepted=accepted)
            payload = study.synthetic_fixture(task)
            self.assertEqual(study.validate_response(task, payload), [])
            accepted[task["task_id"]] = payload
        rows = study.replay(plan, self.model, accepted)
        self.assertEqual(len(rows), 20 * 24 * 4)
        for chain in plan["chains_by_phase"]["main"]:
            own = [r for r in rows if r["chain_id"] == chain["chain_id"]]
            self.assertEqual(sum(r["cost"] for r in own), 576)
            self.assertTrue(all(r["inventory"] == 12 and r["backlog"] == 0 for r in own))

    def test_orders_update_next_state_and_unreceived_pipeline_not_current_inventory(self):
        task = study.build_task(self.plan, self.model, "main", week=1)
        payload = study.synthetic_fixture(task)
        for cid in task["chain_ids"]:
            payload["orders"][cid] = {role: 100000 for role in study.ROLE_KEYS}
        current = copy.deepcopy(task["states"])
        later = study.build_task(self.plan, self.model, "main", week=2, accepted={task["task_id"]: payload})
        self.assertEqual(task["states"], current)
        for cid in task["chain_ids"]:
            self.assertEqual(later["states"][cid][3]["supply_line"], 100004)
            self.assertEqual(later["states"][cid][3]["inventory"], 0)
            self.assertEqual(later["states"][cid][3]["backlog"], 99984)

    def test_fixed_object_schema_and_local_validator_reject_missing_extra_or_wrong_types(self):
        task = study.build_task(self.plan, self.model, "pilot")
        good = study.synthetic_fixture(task)
        schema = study.response_schema(task)
        self.assertEqual(set(schema["properties"]["orders"]["required"]), set(task["chain_ids"]))
        self.assertEqual(set(schema["$defs"]["choice"]["required"]), set(study.ROLE_KEYS))
        self.assertTrue(all(v == {"$ref": "#/$defs/choice"} for v in schema["properties"]["orders"]["properties"].values()))
        for value in (True, 4.0, "4", None, -1, 100001):
            mutated = copy.deepcopy(good)
            mutated["orders"][task["chain_ids"][0]]["r"] = value
            self.assertTrue(study.validate_response(task, mutated))
        empty = copy.deepcopy(good)
        empty["orders"] = {}
        self.assertTrue(study.validate_response(task, empty))
        missing_role = copy.deepcopy(good)
        del missing_role["orders"][task["chain_ids"][0]]["f"]
        self.assertTrue(study.validate_response(task, missing_role))
        wrong_id = copy.deepcopy(good)
        wrong_id["task_id"] = "different_request"
        self.assertTrue(study.validate_response(task, wrong_id))
        for value in (0, 100000):
            allowed = copy.deepcopy(good)
            for choices in allowed["orders"].values():
                choices.update({role: value for role in study.ROLE_KEYS})
            self.assertEqual(study.validate_response(task, allowed), [])

    def test_probe_request_requires_complete_game_and_all_320_named_choices(self):
        accepted = self.full_model(probes=False)
        task = study.build_task(self.plan, self.model, "probe", accepted=accepted)
        payload = study.synthetic_fixture(task)
        self.assertEqual(sum(len(v) for v in payload["probes"].values()), 320)
        self.assertEqual(study.validate_response(task, payload), [])
        self.assertEqual(task["max_output_tokens"], 4096)
        cid = task["chain_ids"][0]
        del payload["probes"][cid][next(iter(payload["probes"][cid]))]
        self.assertTrue(study.validate_response(task, payload))

    def test_partial_costs_stay_separate_and_complete_h2_does_not_require_h1_probe(self):
        partial = self.full_model(weeks=3, probes=False)
        with self.save_analysis_fixtures(partial):
            result = study.analyze(self.run)
        self.assertEqual(len(result["rounds"]), 20 * 3 * 4)
        self.assertTrue(all(r["total_cost"] is None and r["weeks_observed"] == 3 for r in result["chains"]))
        self.assertTrue(all(r["observed_cost_partial"] >= 0 for r in result["chains"]))
        self.assertTrue(all(r["mean_strong_minus_no"] is None for r in result["hypotheses"]))
        complete = self.full_model(probes=False)
        with self.save_analysis_fixtures(complete):
            result = study.analyze(self.run)
        own = {r["hypothesis"]: r for r in result["hypotheses"] if r["model"] == self.model}
        self.assertEqual(own["H2"]["mean_strong_minus_no"], 0)
        self.assertIsNone(own["H1"]["mean_strong_minus_no"])
        self.assertTrue(all(r["complete"] for r in result["chains"]))

    def test_complete_descriptive_analysis_and_both_directions_are_allowed(self):
        accepted = {}
        expected = dict(zip(study.MODELS, (-1., 1., 0., -2.)))
        for model in study.MODELS:
            own = self.full_model(model)
            task = study.build_task(self.plan, model, "probe", accepted=own)
            payload = own[task["task_id"]]
            for spec in task["chains"]:
                slope = 1. + expected[model] if spec["condition"] == "strong_pressure" else 1.
                payload["probes"][spec["chain_id"]] = {
                    p["probe_id"]: 100 + int(24*slope) if p["supply_line"] == 8 else 100
                    for p in task["probe_states"]}
            self.assertEqual(study.validate_response(task, payload), [])
            accepted.update(own)
        with self.save_analysis_fixtures(accepted):
            result = study.analyze(self.run)
        self.assertEqual(len(result["rounds"]), 7680)
        self.assertEqual(len(result["probes"]), 1280)
        self.assertEqual(len(result["chains"]), 80)
        self.assertEqual(len(result["hypotheses"]), 8)
        self.assertEqual(len(result["task_status"]), 104)
        self.assertEqual(len(result["condition_means"]), 8)
        for row in result["hypotheses"]:
            self.assertEqual(row["paired_blocks"], 10)
            self.assertEqual(row["mean_strong_minus_no"], expected[row["model"]] if row["hypothesis"] == "H1" else 0.)
            self.assertIsNone(row["p_raw"])
            self.assertIsNone(row["paired_bootstrap_95"])
            self.assertFalse(row["inference_available"])
        self.assertTrue(all("bullwhip_factory" in row and "final_supply_line" in row for row in result["chains"]))

    def test_shared_budget_is_portable_cumulative_and_preparation_is_idempotent(self):
        self.assertEqual(self.plan["budget_experiment"], "../12_original")
        self.assertEqual(study.budget_experiment_for(self.run), self.budget.resolve())
        before = (self.run / "plan.json").read_bytes()
        ledger = BudgetLedger(self.budget)
        ledger.reserve("later_call", .02, {"run": "new_weekly"})
        ledger.settle("later_call", .01, "received")
        self.assertEqual(study.prepare(self.experiment, self.budget), self.run)
        self.assertEqual((self.run / "plan.json").read_bytes(), before)
        self.assertAlmostEqual(BudgetLedger(self.budget).spent, .35)
        altered = study.read(self.budget / "data/api_budget.json")
        altered["attempts"]["prior_paid_run"]["charge_usd"] = 0
        (self.budget / "data/api_budget.json").write_text(json.dumps(altered))
        with self.assertRaisesRegex(ValueError, "Earlier shared-budget charge"):
            study.loadplan(self.run)

    def test_no_new_budget_is_created_and_tampered_plan_or_snapshot_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "existing separate"):
            study.prepare(self.experiment, self.root / "not_an_authorized_budget")
        snapshot = self.run / "source_snapshot/game.py"
        original = snapshot.read_bytes()
        snapshot.write_bytes(original + b"\n# changed\n")
        with self.assertRaisesRegex(ValueError, "source snapshot"):
            study.loadplan(self.run)
        snapshot.write_bytes(original)
        plan = study.read(self.run / "plan.json")
        plan["weeks"] = 30
        (self.run / "plan.json").write_text(json.dumps(plan))
        with self.assertRaisesRegex(ValueError, "Frozen weekly plan"):
            study.loadplan(self.run)

    def test_analysis_calls_strict_provider_evidence_audit(self):
        with patch("beergame_study.weekly_pressure_api.audit_saved", side_effect=ValueError("provider evidence changed")) as audit:
            with self.assertRaisesRegex(ValueError, "provider evidence changed"):
                study.analyze(self.run)
        audit.assert_called_once_with(self.run)


if __name__ == "__main__":
    unittest.main()
