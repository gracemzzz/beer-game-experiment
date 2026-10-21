"""Offline scientific checks for the separate whole-cohort pressure study.

Every accepted fixture is stored in a temporary directory. No test calls an API
or writes synthetic choices into the prepared live experiment.
"""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import batched_pressure as study


class BatchedPressureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.temporary = Path(temporary.name)
        self.experiment = self.temporary / "experiment"
        (self.experiment / "hypotheses").mkdir(parents=True)
        shutil.copyfile(ROOT / "experiments/12_pressure_framing_api_20261020/hypotheses/PROTOCOL.md",
                        self.experiment / "hypotheses/PROTOCOL.md")
        # Mirror current scientific files so tampering tests never touch shared
        # workspace sources, even while another agent is preparing real files.
        self.sources = self.temporary / "sources"
        self.sources.mkdir()
        for name in ("batched_pressure.py", "batched_pressure_api.py", "game.py"):
            shutil.copyfile(ROOT / "src/beergame_study" / name, self.sources / name)
        current_file = patch.object(study, "__file__", str(self.sources / "batched_pressure.py"))
        current_file.start()
        self.addCleanup(current_file.stop)
        self.run = study.prepare(self.experiment)
        self.plan = study.loadplan(self.run)

    def task(self, phase="pilot", model=None):
        model = model or study.MODELS[0]
        return next(t for t in self.plan["tasks"] if t["phase"] == phase and t["model"] == model)

    def refresh_readbacks(self, task, payload):
        """Recompute fixture readbacks after a deliberate order mutation."""
        rows = study.replay(task, payload)
        for chain in payload["chains"]:
            chain["inventory_checkpoints"] = [
                dict(week=week, inventories=[r["inventory"] for r in rows
                                            if r["chain_id"] == chain["chain_id"] and r["week"] == week])
                for week in study.CHECKPOINTS
            ]

    def write_fixture(self, task, payload):
        self.assertEqual(study.validate_response(task, payload), [])
        study.save_new(self.run / task["response_path"], payload)

    def test_hand_calculated_constant_flow_cost_is_576_per_chain(self):
        task = copy.deepcopy(self.task())
        for chain in task["chains"]:
            chain["customer_demand"] = [4] * 24
        payload = study.synthetic_fixture(task)
        self.assertEqual(study.validate_response(task, payload), [])
        rows = study.replay(task, payload)
        self.assertEqual(len(rows), 2 * 24 * 4)
        for chain in task["chains"]:
            own = [r for r in rows if r["chain_id"] == chain["chain_id"]]
            # Every role holds12 cases, so 4roles ×24weeks ×12cases ×$0.50.
            self.assertEqual(sum(r["cost"] for r in own), 576)
            self.assertTrue(all(r["inventory"] == 12 and r["backlog"] == 0 and r["order"] == 4
                                for r in own))
            self.assertEqual({r["week"] for r in own}, set(range(1, 25)))

    def test_fixed_four_plus_four_calls_and_80_distinct_main_identities_per_model(self):
        tasks = self.plan["tasks"]
        self.assertEqual(len(tasks), 8)
        self.assertEqual([t["phase"] for t in tasks], ["pilot"] * 4 + ["main"] * 4)
        self.assertEqual(self.plan["cap_usd"], 5)
        for model in study.MODELS:
            main, pilot = self.task("main", model), self.task("pilot", model)
            self.assertEqual(len(main["chains"]), 20)
            self.assertEqual(len(pilot["chains"]), 2)
            self.assertEqual(main["max_output_tokens"], 16384)
            self.assertEqual(pilot["max_output_tokens"], 8192)
            self.assertEqual(sum(c["condition"] == "strong_pressure" for c in main["chains"]), 10)
            self.assertEqual(sum(c["condition"] == "no_pressure" for c in main["chains"]), 10)
            ids = [identity for chain in main["chains"] for identity in chain["participant_ids"]]
            pilot_ids = [identity for chain in pilot["chains"] for identity in chain["participant_ids"]]
            self.assertEqual(len(set(ids)), 80)
            self.assertFalse(set(ids) & set(pilot_ids))
            for block in range(10):
                pair = [c for c in main["chains"] if c["block"] == block]
                self.assertEqual(len(pair), 2)
                self.assertNotEqual(pair[0]["chain_id"], pair[1]["chain_id"])
                self.assertEqual(pair[0]["customer_demand"], pair[1]["customer_demand"])
                self.assertEqual(len(pair[0]["customer_demand"]), 24)
                self.assertEqual(pair[0]["profiles"], pair[1]["profiles"])
                self.assertEqual(pair[0]["probes"], pair[1]["probes"])

    def test_preparation_is_idempotent_and_new_label_has_fresh_run_and_prompt_ids(self):
        original = (self.run / "plan.json").read_bytes()
        self.assertEqual(study.prepare(self.experiment), self.run)
        self.assertEqual((self.run / "plan.json").read_bytes(), original)
        fresh = study.prepare(self.experiment, label="separate-prospective-sample")
        self.assertNotEqual(fresh, self.run)
        new_plan = study.loadplan(fresh)
        self.assertNotEqual(new_plan["study_id"], self.plan["study_id"])
        self.assertNotEqual(new_plan["tasks"][0]["prompt_path"], self.plan["tasks"][0]["prompt_path"])
        payload = study.synthetic_fixture(self.task())
        self.assertTrue(study.validate_response(new_plan["tasks"][0], payload))
        self.assertEqual((self.run / "plan.json").read_bytes(), original)

    def test_rejects_missing_weeks_duplicate_chains_and_boolean_orders(self):
        task = self.task()
        good = study.synthetic_fixture(task)
        mutations = []
        short = copy.deepcopy(good)
        short["chains"][0]["orders"].pop()
        mutations.append(("missing week", short))
        duplicate = copy.deepcopy(good)
        duplicate["chains"][1]["chain_id"] = duplicate["chains"][0]["chain_id"]
        mutations.append(("duplicate chain", duplicate))
        boolean = copy.deepcopy(good)
        boolean["chains"][0]["orders"][0][0] = True
        mutations.append(("Boolean order", boolean))
        duplicate_probe = copy.deepcopy(good)
        duplicate_probe["chains"][0]["probes"][1]["probe_id"] = duplicate_probe["chains"][0]["probes"][0]["probe_id"]
        mutations.append(("duplicate probe", duplicate_probe))
        for name, payload in mutations:
            with self.subTest(name=name):
                self.assertTrue(study.validate_response(task, payload))
        self.assertEqual(study.validate_response(task, good), [])

    def test_wrong_physical_readback_is_rejected_without_repair(self):
        task = self.task()
        payload = study.synthetic_fixture(task)
        payload["chains"][0]["inventory_checkpoints"][1]["inventories"][2] += 1
        original = copy.deepcopy(payload)
        issues = study.validate_response(task, payload)
        self.assertTrue(any("Physical inventory readback mismatch at week 12" in issue for issue in issues))
        self.assertEqual(payload, original)

    def test_wrong_factual_rules_and_noninteger_probe_fail(self):
        task = self.task()
        payload = study.synthetic_fixture(task)
        payload["rules"]["factory_order_week_7_arrival_week"] = 11
        self.assertTrue(any("Factual rule comprehension" in issue for issue in study.validate_response(task, payload)))
        payload = study.synthetic_fixture(task)
        payload["chains"][0]["probes"][0]["order"] = 4.0
        self.assertTrue(any("probe" in issue for issue in study.validate_response(task, payload)))

    def test_zero_and_technical_ceiling_orders_are_allowed_without_behavior_filter(self):
        task = self.task()
        for value in (0, 100000):
            with self.subTest(value=value):
                payload = study.synthetic_fixture(task)
                for chain in payload["chains"]:
                    chain["orders"] = [[value] * 4 for _ in range(24)]
                    for probe in chain["probes"]:
                        probe["order"] = value
                self.refresh_readbacks(task, payload)
                self.assertEqual(study.validate_response(task, payload), [])
        excessive = study.synthetic_fixture(task)
        excessive["chains"][0]["orders"][0][0] = 100001
        self.assertTrue(any("technical safety ceiling" in issue for issue in study.validate_response(task, excessive)))

    def test_synthetic_positive_negative_and_null_sensitivity_have_no_inference(self):
        # Each model receives an intentionally different *synthetic* condition
        # contrast. Tests demonstrate metrics accept any sign; no sign is a gate.
        treatment_sensitivity = dict(zip(study.MODELS, (0., 2., 1., -1.)))
        expected = dict(zip(study.MODELS, (-1., 1., 0., -2.)))
        for task in self.plan["tasks"]:
            payload = study.synthetic_fixture(task)
            specs = {c["chain_id"]: c for c in task["chains"]}
            for chain in payload["chains"]:
                spec = specs[chain["chain_id"]]
                slope = treatment_sensitivity[task["model"]] if spec["condition"] == "strong_pressure" else 1.
                probe_specs = {p["probe_id"]: p for p in spec["probes"]}
                for choice in chain["probes"]:
                    # All nonnegative; exactly prescribed sensitivity without
                    # affecting the physical game or checkpoints.
                    choice["order"] = 100 + int(24 * slope) if probe_specs[choice["probe_id"]]["supply_line"] == 8 else 100
            self.write_fixture(task, payload)
        result = study.analyze(self.run)
        self.assertEqual(len(result["chains"]), 88)
        self.assertEqual(len(result["rounds"]), 88 * 24 * 4)
        for row in result["hypotheses"]:
            self.assertEqual(row["paired_blocks"], 10)
            self.assertEqual(row["mean_strong_minus_no"], expected[row["model"]] if row["hypothesis"] == "H1" else 0)
            self.assertIsNone(row["p_raw"])
            self.assertIsNone(row["p_holm_8"])
            self.assertIsNone(row["paired_bootstrap_95"])
            self.assertFalse(row["inference_available"])
            self.assertFalse(row["literal_binding_time_test"])

    def test_missing_or_invalid_cohort_has_no_accepted_partial_chains(self):
        task = self.task("main")
        payload = study.synthetic_fixture(task)
        payload["chains"][0]["orders"].pop()
        study.save_new(self.run / task["response_path"], payload)
        result = study.analyze(self.run)
        self.assertEqual(result["chains"], [])
        self.assertEqual(sum(s["status"] == "invalid" for s in result["task_status"]), 1)
        for row in result["hypotheses"]:
            self.assertEqual(row["paired_blocks"], 0)
            self.assertIsNone(row["mean_strong_minus_no"])
            self.assertIsNone(row["p_raw"])

    def test_changed_current_api_or_core_source_is_detected(self):
        for name in ("batched_pressure_api.py", "batched_pressure.py"):
            path = self.sources / name
            original = path.read_bytes()
            with self.subTest(name=name):
                path.write_bytes(original + b"\n# temporary source tampering test\n")
                with self.assertRaisesRegex(ValueError, "Scientific implementation changed"):
                    study.loadplan(self.run)
                path.write_bytes(original)
                self.assertEqual(study.loadplan(self.run)["study_id"], self.plan["study_id"])

    def test_changed_frozen_source_prompt_schema_and_plan_are_detected(self):
        cases = (
            (self.run / "source_snapshot/game.py", b"\n# altered snapshot\n", "Frozen source snapshot changed"),
            (self.experiment / self.task()["prompt_path"], b"\nextra instruction\n", "Frozen prompt changed"),
            (self.run / "plan.json", b" ", None),
        )
        for path, suffix, expected in cases:
            original = path.read_bytes()
            with self.subTest(path=path.name):
                if path.name == "plan.json":
                    changed = json.loads(original)
                    changed["cap_usd"] = 6
                    path.write_text(json.dumps(changed))
                    with self.assertRaisesRegex(ValueError, "Frozen study plan changed"):
                        study.loadplan(self.run)
                else:
                    path.write_bytes(original + suffix)
                    with self.assertRaisesRegex(ValueError, expected):
                        study.loadplan(self.run)
                path.write_bytes(original)
        schema_path = self.experiment / self.task()["schema_path"]
        schema = json.loads(schema_path.read_text())
        schema["additionalProperties"] = True
        schema_path.write_text(json.dumps(schema))
        with self.assertRaisesRegex(ValueError, "Frozen response schema changed"):
            study.loadplan(self.run)


if __name__ == "__main__":
    unittest.main()
