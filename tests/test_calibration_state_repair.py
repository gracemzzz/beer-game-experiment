"""Restrict calibration-state repair while retaining its full original ledger."""
import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from beergame_study import student_study as workflow
from beergame_study.reasoning_protocol import Gateway, ReasoningConfig, StudyStopped, make_messages, save


class CalibrationStateRepairTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(workflow, "ROOT", self.root)
        self.root_patch.start()
        self.report_patch = patch("beergame_study.student_report.build_report", return_value=None)
        self.report_patch.start()
        self.config = replace(ReasoningConfig(), mode="offline", stage="calibration", weeks=20,
                              groups_per_condition=1, request_interval_s=0, replicate_id="state-repair-fixture")

    def tearDown(self):
        self.report_patch.stop()
        self.root_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def records(directory):
        return [(p, json.loads(p.read_text(encoding="utf-8")))
                for p in (directory/"requests").glob("*.json")]

    @staticmethod
    def legacy_cases():
        cases = copy.deepcopy(workflow.calibration_cases())
        for case in cases:
            case["state"].update(received=0, shipped=0)
        return cases

    async def legacy_fixture(self, cases=None, label="legacy"):
        cases = self.legacy_cases() if cases is None else cases
        # This represents the explicitly supported old observation bank. Its
        # small artificial charges test accounting and are never research data.
        with patch.object(workflow, "calibration_cases", return_value=copy.deepcopy(cases)):
            directory = workflow.prepare(self.config, output_root=self.root/label, calibration_only=True)
        gateway = Gateway(directory, self.config)
        for item, case in enumerate(cases):
            for cap in (*self.config.candidate_caps, self.config.reference_tokens):
                record = await gateway.request(dict(stage="calibration", item=item, cap=cap),
                                               make_messages(case["state"], case["history"]), cap,
                                               synthetic=json.dumps({"order": case["state"]["demand"]}))
                record.update(charge_usd=.001, fixture_accounting_only=True)
                save(directory/"requests"/(record["request_key"]+".json"), record)
        return directory

    def test_bank_observations_obey_post_shipment_conservation(self):
        cases = workflow.calibration_cases()
        self.assertEqual(len(cases), 24)
        corrected = []
        for item, case in enumerate(cases):
            state = case["state"]
            inventory, backlog = state["inventory"], state["backlog"]
            received, shipped, demand = state["received"], state["shipped"], state["demand"]
            self.assertTrue(all(type(x) is int and x >= 0 for x in (inventory, backlog, received, shipped, demand)))
            self.assertFalse(inventory > 0 and backlog > 0)
            self.assertGreaterEqual(shipped+backlog, demand)  # current demand is already processed
            self.assertGreaterEqual(inventory+shipped-received, 0)  # stock before deliveries
            self.assertEqual(state["net_inventory"], inventory-backlog)
            self.assertEqual(state["cost"], .5*inventory+backlog)
            self.assertEqual(state["shared_inventory"][state["role"]], inventory)
            if inventory > 0 and demand > 0:
                self.assertEqual((received, shipped), (demand, demand))
                corrected.append(item)
        self.assertEqual(corrected, [0, 2, 6, 8, 12, 14, 18, 20])

    async def test_explicit_repair_preserves_ledger_and_refreshes_only_48_changed_calls(self):
        parent = await self.legacy_fixture()
        before = {p.name: p.read_bytes() for p, _ in self.records(parent)}
        old_charge = sum(r["charge_usd"] for _, r in self.records(parent))
        self.assertEqual(len(before), 144)
        directory = await workflow.run_campaign(self.config, output_root=self.root/"corrected",
                                                 calibration_parent=parent, calibration_only=True,
                                                 correct_calibration_states=True)
        records = self.records(directory)
        self.assertEqual(len(records), 192)
        self.assertEqual({p.name: p.read_bytes() for p, _ in records if p.name in before}, before)
        self.assertEqual({p.name: p.read_bytes() for p, _ in self.records(parent)}, before)
        new = [(p, r) for p, r in records if p.name not in before]
        self.assertEqual(len(new), 48)
        self.assertEqual({r["identity"]["item"] for _, r in new}, {0, 2, 6, 8, 12, 14, 18, 20})
        progress = json.loads((directory/"progress.json").read_text())
        self.assertEqual((progress["phase"], progress["stage"]), ("complete", "calibration_complete"))
        self.assertEqual((progress["requests_done"], progress["cached_requests"]), (144, 96))
        self.assertAlmostEqual(progress["estimated_charged_or_reserved_usd"], old_charge)
        self.assertAlmostEqual(sum(r["charge_usd"] for _, r in records), old_charge)
        self.assertFalse((directory/"rounds.csv").exists())
        self.assertFalse((directory/"rules_checks.json").exists())
        bank = workflow.calibration_cases()
        current = [r for _, r in records if r["messages"] == make_messages(
            bank[r["identity"]["item"]]["state"], bank[r["identity"]["item"]]["history"])]
        self.assertEqual(len(current), 144)
        self.assertEqual(len(pd.read_csv(directory/"calibration.csv")), 144)
        recommendation = json.loads((directory/"calibration_recommendation.json").read_text())
        self.assertTrue(all(row["n"] == 24 for row in recommendation["screen_rows"]))
        # The completed repaired calibration must remain reusable for games;
        # historical incompatible states stay in its ledger, outside screening.
        selected, _, provenance = workflow.load_calibration(directory, self.config)
        self.assertEqual(len(selected), 144)
        self.assertTrue(all(r in current for r in selected))
        self.assertAlmostEqual(provenance["original_calibration_estimated_usd"], old_charge)

    async def test_old_bank_requires_explicit_repair_before_any_request(self):
        parent = await self.legacy_fixture()
        calls = []
        async def forbidden(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("State-bank validation must precede requests.")
        with patch.object(workflow.Gateway, "request", new=forbidden):
            with self.assertRaises(StudyStopped):
                await workflow.run_campaign(self.config, output_root=self.root/"no-repair",
                                            calibration_parent=parent, calibration_only=True)
        self.assertEqual(calls, [])

    async def test_repair_cannot_change_inventory_or_other_game_fields(self):
        cases = self.legacy_cases()
        state = cases[0]["state"]
        state["inventory"] += 1
        state["net_inventory"] += 1
        state["cost"] += .5
        state["shared_inventory"][state["role"]] += 1
        parent = await self.legacy_fixture(cases=cases, label="bad-legacy")
        before = {p.name: p.read_bytes() for p, _ in self.records(parent)}
        calls = []
        async def forbidden(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("Broader state changes cannot buy new calls under the repair exception.")
        with patch.object(workflow.Gateway, "request", new=forbidden):
            with self.assertRaises(StudyStopped):
                await workflow.run_campaign(self.config, output_root=self.root/"bad-repair",
                                            calibration_parent=parent, calibration_only=True,
                                            correct_calibration_states=True)
        self.assertEqual(calls, [])
        self.assertEqual({p.name: p.read_bytes() for p, _ in self.records(parent)}, before)


if __name__ == "__main__":
    unittest.main()
