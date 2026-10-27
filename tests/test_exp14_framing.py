"""Synthetic fictional-pressure controls. No participant/API execution."""
import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import exp14_framing as study
from beergame_study.manual_weekly_v3 import _PhysicalGame


def point(seconds):
    return dict(monotonic_ns=round(seconds * 1e9),
                utc=(datetime(2026, 10, 26, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat())


def case(arm="A", **changes):
    result = dict(schema_version=study.SCHEMA, case_id="SYNTHETIC-FRAMING-" + arm,
                  block_id="fixture", arm=arm, stage="synthetic_software_test", prompt_version="fixture",
                  seed=12, weeks=24, fictional_student_seconds=120 if arm == "A" else 8,
                  model_runtime_limit_seconds=None, deadline_seconds=None,
                  probes=[], comprehension=[], source_hashes=study.source_hashes())
    result.update(changes)
    return result


class FramingTests(unittest.TestCase):
    def new(self, **changes):
        return study.FramingCase(case(**changes), clock=point(0))

    def audit(self, game):
        self.assertTrue(study.audit_result(game.export(), game.case)["valid"])

    def test_all_arms_fictional_metadata_unlimited_model_time_100000_seconds(self):
        for arm in "ABC":
            game = self.new(arm=arm, weeks=1)
            shown = game.show(point(0))
            self.assertEqual(shown["fictional_student_seconds"], 120 if arm == "A" else 8)
            self.assertIsNone(shown["model_runtime_limit_seconds"])
            self.assertIsNone(shown["deadline_clock"]["deadline_monotonic_ns"])
            self.assertEqual(shown, game.show(point(99999)))
            ack = game.submit("[0,1,2,3]", shown["decision_id"], received=point(100000))
            self.assertTrue(ack["accepted"])
            self.assertTrue(ack["complete"])
            result = game.export()
            self.assertEqual(result["decisions"][0]["elapsed_seconds"], 100000)
            self.assertEqual(result["weeks"][0]["orders"], [0, 1, 2, 3])
            self.assertIsNone(result["model_runtime_limit_seconds"])
            self.assertIsNone(result["deadline_seconds"])
            self.assertEqual(result["missing"]["weeks"], [])
            self.audit(game)

    def test_no_clock_on_init_no_reset_show_no_future_state_in_ack(self):
        game = self.new()
        self.assertIsNone(game.pending)
        self.assertEqual(game.game.week, 0)
        first = game.show(point(20))
        self.assertEqual(first, game.show(point(1000000)))
        self.assertEqual(game.game.week, 1)
        self.assertNotIn("seed", first)
        self.assertNotIn("future", json.dumps(first))
        ack = game.submit("[0,0,0,0]", first["decision_id"], received=point(2000000))
        self.assertNotIn("roles", ack)
        self.assertIsNone(ack["open_decision_id"])
        self.assertEqual(ack["next_action"], "show")
        self.assertEqual(game.game.week, 1)
        self.audit(game)

    def test_24_weeks_all_arms_literal_actions_exact_physics_cost_conservation(self):
        all_demands = []
        for arm in "ABC":
            game = self.new(arm=arm)
            physical = _PhysicalGame()
            for week in range(24):
                shown = game.show(point(week * 200000))
                self.assertEqual(shown["roles"], physical.observe(shown["customer_demand"]))
                orders = [0, week + 1, 30 - week, week % 2]
                physical.commit(orders)
                ack = game.submit(json.dumps(orders), shown["decision_id"], received=point(week * 200000 + 100000))
                self.assertTrue(ack["accepted"])
                self.assertEqual(game.weeks[-1]["orders"], orders)
                self.assertEqual(game.game.outstanding, physical.outstanding)
                self.assertEqual(game.game.delivery, physical.delivery)
                self.assertIsNone(game.pending)
            result = game.export()
            self.assertTrue(result["complete"])
            self.assertEqual(len(result["decisions"]), 24)
            self.assertEqual(result["full_game_cost"], sum(sum(row["cost"] for row in w["roles"]) for w in result["weeks"]))
            self.audit(game)
            all_demands.append([w["customer_demand"] for w in game.weeks])
        self.assertEqual(all_demands[0], all_demands[1])
        self.assertEqual(all_demands[0], all_demands[2])

    def test_all_32_probes_actual_answers_and_quiz_required(self):
        game = self.new(weeks=1, probes=[dict(probe_id="p" + str(i), role="factory") for i in range(32)],
                        comprehension=[dict(question_id="q", options={"A": "a", "B": "b"})])
        shown = game.show(point(0))
        game.submit("[0,0,0,0]", shown["decision_id"], received=point(100000))
        self.assertFalse(game.status()["complete"])
        self.assertIsNotNone(game.export()["full_game_cost"])
        expected = {}
        for page in range(8):
            shown = game.show(point((page + 1) * 200000))
            self.assertEqual(shown["phase"], "probes")
            self.assertIsNone(shown["deadline_clock"]["deadline_monotonic_ns"])
            choices = {row["probe_id"]: page for row in shown["probes"]}
            expected.update(choices)
            self.assertTrue(game.submit(json.dumps(choices), shown["decision_id"],
                                        received=point((page + 1) * 200000 + 100000))["accepted"])
        self.assertEqual(game.probe_answers, expected)
        self.assertEqual(game.export()["missing"]["probe_ids"], [])
        self.assertFalse(game.status()["complete"])
        shown = game.show(point(2000000))
        self.assertEqual(shown["phase"], "comprehension")
        self.assertTrue(game.submit('{"q":"B"}', shown["decision_id"], received=point(3000000))["accepted"])
        self.assertTrue(game.status()["complete"])
        self.assertEqual(len(game.decisions), 10)
        self.audit(game)

    def test_stale_duplicate_cannot_revise_or_apply_to_next_week(self):
        game = self.new()
        first = game.show(point(0))
        self.assertFalse(game.submit("[9,9,9,9]", "unknown", received=point(1))["accepted"])
        self.assertEqual(first, game.show(point(2)))
        self.assertTrue(game.submit("[0,1,2,3]", first["decision_id"], received=point(3))["accepted"])
        self.assertFalse(game.submit("[9,9,9,9]", first["decision_id"], received=point(4))["accepted"])
        second = game.show(point(5))
        self.assertFalse(game.submit("[9,9,9,9]", first["decision_id"], received=point(100000))["accepted"])
        self.assertEqual(second, game.show(point(100001)))
        self.assertEqual(len(game.weeks), 1)
        self.assertEqual(game.weeks[0]["orders"], [0, 1, 2, 3])
        self.audit(game)

    def test_invalid_attempt_preserved_and_stops_without_repair_or_default(self):
        for raw in ("not JSON", "[true,2,3,4]", "[1,2,3]", "[0,-1,2,3]", "[1.5,2,3,4]", "[NaN,1,2,3]"):
            game = self.new()
            shown = game.show(point(0))
            ack = game.submit(raw, shown["decision_id"], received=point(100000))
            self.assertFalse(ack["accepted"])
            self.assertTrue(ack["stopped"])
            self.assertEqual(ack["terminal_reason"], "invalid_payload")
            self.assertEqual(game.events[-2]["literal_input_text"], raw)
            self.assertEqual(game.decisions, [])
            self.assertEqual(game.weeks, [])
            self.assertIsNone(game.export()["full_game_cost"])
            self.assertFalse(game.submit("[1,2,3,4]", shown["decision_id"], received=point(100001))["accepted"])
            self.audit(game)

    def test_schema_no_physical_deadline_or_wrong_fictional_setting(self):
        for changes in ({"schema_version": "old"}, {"deadline_seconds": 8},
                        {"model_runtime_limit_seconds": 120}, {"fictional_student_seconds": 8},
                        {"phase_deadline_seconds": {"game": 8}}, {"phase_deadline_seconds": []},
                        {"requested_model": "other"}, {"requested_effort": "low"}):
            with self.assertRaises(ValueError):
                self.new(**changes)

    def test_source_and_replay_tampering_rejected(self):
        with self.assertRaisesRegex(ValueError, "source_hashes"):
            self.new(source_hashes={})
        game = self.new(weeks=1)
        shown = game.show(point(0))
        game.submit("[0,0,0,0]", shown["decision_id"], received=point(100000))
        for mutate in (lambda p: p["weeks"][0].update(orders=[4] * 4),
                       lambda p: p.update(fictional_student_seconds=8),
                       lambda p: p.update(model_runtime_limit_seconds=8),
                       lambda p: p["decisions"][0].update(elapsed_seconds=1)):
            bad = copy.deepcopy(game.export())
            mutate(bad)
            with self.assertRaisesRegex(ValueError, "replay differs"):
                study.audit_result(bad, game.case)
        bad = copy.deepcopy(game.export())
        bad["events"][-1]["literal_input_text"] = "[4,4,4,4]"
        with self.assertRaisesRegex(ValueError, "Event chain differs"):
            study.audit_result(bad, game.case)

    def test_cli_atomic_receipts_source_binding_and_no_reset(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            fixture = case(arm="C", weeks=1)
            (folder / "CASE.json").write_text(json.dumps(fixture), encoding="utf-8")
            def run(action, *extra, raw=None):
                return subprocess.run([sys.executable, str(ROOT / "scripts/run_exp14_framing.py"), action,
                                       "--run", directory, *extra], input=raw, capture_output=True, text=True)
            self.assertEqual(run("init").returncode, 0)
            self.assertNotEqual(run("init").returncode, 0)
            shown = json.loads(run("show").stdout)
            self.assertEqual(shown, json.loads(run("show").stdout))
            self.assertEqual(shown["fictional_student_seconds"], 8)
            self.assertIsNone(shown["model_runtime_limit_seconds"])
            self.assertEqual(run("submit", "--decision-id", "stale", raw="[1,2,3,4]").returncode, 2)
            result = run("submit", "--decision-id", shown["decision_id"], raw="[0,0,0,0]")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["complete"])
            payload = json.loads((folder / "RESULT.json").read_text(encoding="utf-8"))
            self.assertTrue(study.audit_result(payload, fixture)["valid"])
            self.assertEqual(len(list((folder / "events").glob("*.json"))), len(payload["events"]))
            fixture["fictional_student_seconds"] = 120
            (folder / "CASE.json").write_text(json.dumps(fixture), encoding="utf-8")
            self.assertNotEqual(run("status").returncode, 0)


if __name__ == "__main__":
    unittest.main()
