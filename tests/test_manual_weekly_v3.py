"""Offline controller/replay tests. All orders in these fixtures are synthetic."""
import copy
import importlib.util
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.game import BeerGame
from beergame_study import manual_weekly_v3 as study


class ManualWeeklyControllerTests(unittest.TestCase):
    def game(self, arm="B", chains=2):
        return study.WebsiteGame("fixture-" + arm, arm, 1, chains,
                                 provider="fixture", model="synthetic", reasoning_setting="not applicable")

    def choices(self, game, value=4):
        return {cid: [value] * 4 for cid in game.chain_ids}

    def finish(self, arm="B", chains=2, probes=True):
        game = self.game(arm, chains)
        for week in range(24):
            game.display()
            game.submit_initial(self.choices(game, value=week % 9))
            if arm == "A":
                game.display()
                game.submit_revision(self.choices(game, value=(week + 1) % 9))
        if probes:
            display = game.display()
            orders = {state["probe_id"]: state["backlog"] + 8 - state["supply_line"]
                      for state in display["hypothetical_independent_decisions"]}
            game.submit_probe_initial(orders)
            if arm == "A":
                game.display()
                game.submit_probe_revision(orders)
        return game

    def test_physical_derivation_matches_original_over_random_orders(self):
        original, derived = BeerGame(), study._PhysicalGame()
        rng = random.Random(17)
        for week in range(100):
            demand = rng.randrange(20)
            self.assertEqual(original.observe(demand), derived.observe(demand))
            choices = [rng.choice([0, 0, 1, 4, 20, 100000]) for role in range(4)]
            original.commit(choices)
            derived.commit(choices)
            for field in ("inventory", "backlog", "outstanding", "incoming"):
                self.assertEqual(getattr(original, field).tolist(), getattr(derived, field))
            self.assertEqual(original.delivery, derived.delivery)

    def test_display_repeats_without_advancing_or_leaking_future_demand(self):
        game = self.game()
        first = game.display()
        second = game.display()
        self.assertEqual(first, second)
        self.assertEqual(game.games["c001"].week, 1)
        self.assertNotIn("seed", first)
        self.assertNotIn("future", json.dumps(first))
        self.assertNotIn("customer_demand_path", json.dumps(first))
        self.assertNotIn("100000", json.dumps(first))
        self.assertEqual(game.realized_demand, [])
        game.submit_initial(self.choices(game))
        next_display = game.display()
        self.assertEqual(next_display["week"], 2)
        self.assertEqual(len(next_display["chains"][0]["history"]), 1)

    def test_revision_holds_state_and_requires_its_own_display(self):
        game = self.game("A")
        with self.assertRaisesRegex(ValueError, "display"):
            game.submit_initial(self.choices(game))
        initial = game.display()
        game.submit_initial(self.choices(game, value=99))
        self.assertEqual(game.week, 1)
        self.assertFalse(game.final_orders)
        with self.assertRaisesRegex(ValueError, "display"):
            game.submit_revision(self.choices(game, value=0))
        revision = game.display()
        self.assertEqual(initial["chains"], revision["chains"])
        self.assertEqual(revision["initial_proposals"], self.choices(game, value=99))
        game.submit_revision(self.choices(game, value=0))
        self.assertEqual(game.week, 2)
        self.assertEqual(game.final_orders, [[[0] * 4, [0] * 4]])
        self.assertEqual(game.initial_orders, [[[99] * 4, [99] * 4]])

    def test_no_missing_fill_and_no_revision_for_restricted_arms(self):
        game = self.game("C")
        game.display()
        with self.assertRaisesRegex(ValueError, "every requested ID"):
            game.submit_initial({"c001": [0] * 4})
        self.assertFalse(game.events)
        for value in (False, -1, 2.5, 100001):
            choices = self.choices(game)
            choices["c001"][0] = value
            with self.assertRaises(ValueError):
                game.submit_initial(choices)
        game.submit_initial(self.choices(game, value=0))
        self.assertEqual(game.final_orders[0], [[0] * 4, [0] * 4])
        with self.assertRaises(ValueError):
            game.submit_revision(self.choices(game))

    def test_complete_export_replays_all_arms_and_probes(self):
        for arm in ("A", "B", "C"):
            game = self.finish(arm)
            payload = game.export()
            row = study.audit_export(payload, expected_case={"case_id": game.case_id, "arm": arm, "chains": 2})
            self.assertTrue(payload["complete"])
            self.assertTrue(row["complete"])
            self.assertTrue(row["probe_complete"])
            self.assertEqual(row["pipeline_sensitivity"], 1)
            self.assertEqual(row["backlog_sensitivity"], 1)
            self.assertEqual(row["weeks"], 24)
            self.assertEqual(row["chains_in_cluster"], 2)
            self.assertEqual(row["cluster_total_cost"], 2 * row["chain_total_cost"])
            self.assertIsNotNone(row["mean_role_order_variance"])
            self.assertFalse(row["trace_authenticated"])
            self.assertEqual(len(payload["events"]), 50 if arm == "A" else 25)

    def test_tampering_with_choices_physics_source_or_case_is_rejected(self):
        payload = self.finish().export()
        changed = copy.deepcopy(payload)
        changed["final_orders"][0][0][0] += 1
        with self.assertRaisesRegex(ValueError, "cannot revise"):
            study.audit_export(changed)
        changed = copy.deepcopy(payload)
        changed["realized_customer_demand"][0][0] += 1
        with self.assertRaisesRegex(ValueError, "Replay differs"):
            study.audit_export(changed)
        changed = copy.deepcopy(payload)
        changed["controller_source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source hash"):
            study.audit_export(changed)
        with self.assertRaisesRegex(ValueError, "case identity"):
            study.audit_export(payload, expected_case={"arm": "A"})
        changed = copy.deepcopy(payload)
        changed["events"][0]["choices_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "event replay"):
            study.audit_export(changed)

    def test_partial_collection_is_preserved_without_invented_outcomes(self):
        game = self.game()
        game.display()
        game.submit_initial(self.choices(game))
        with self.assertRaisesRegex(ValueError, "incomplete"):
            game.export()
        row = study.audit_export(game.export(require_complete=False))
        self.assertFalse(row["complete"])
        self.assertEqual(row["weeks"], 1)
        self.assertIsNone(row["chain_total_cost"])
        complete_game = self.finish(probes=False)
        row = study.audit_export(complete_game.export(require_complete=False))
        self.assertTrue(row["complete"])
        self.assertFalse(row["probe_complete"])
        self.assertIsNotNone(row["chain_total_cost"])
        self.assertIsNotNone(row["mean_role_bullwhip"])
        pending = self.game("A")
        pending.display()
        pending.submit_initial(self.choices(pending, value=99))
        row = study.audit_export(pending.export(require_complete=False))
        self.assertEqual(row["weeks"], 0)
        self.assertFalse(row["complete"])

    def test_arms_have_matched_exogenous_demand_and_profiles(self):
        cases = [self.finish(arm, probes=False) for arm in ("A", "B", "C")]
        for case in cases[1:]:
            self.assertEqual(cases[0].realized_demand, case.realized_demand)
            self.assertEqual(cases[0].profile_ids, case.profile_ids)

    def test_exported_helper_is_standalone_and_exact_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "beergame_controller.py"
            receipt = study.write_standalone(target)
            self.assertEqual(receipt, study.source_sha256())
            self.assertEqual(target.read_bytes(), Path(study.__file__).read_bytes())
            spec = importlib.util.spec_from_file_location("uploaded_controller", target)
            uploaded = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(uploaded)
            game = uploaded.WebsiteGame("uploaded", "B", 1)
            self.assertEqual(len(game.display()["chains"]), 10)
            target.write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Refusing"):
                study.write_standalone(target)


if __name__ == "__main__":
    unittest.main()
