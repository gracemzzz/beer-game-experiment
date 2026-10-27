"""Deadline/admission and physics tests. Every fixture choice is SYNTHETIC."""
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
from beergame_study import exp14_deadline as study
from beergame_study.manual_weekly_v3 import _PhysicalGame


def point(seconds):
    return dict(monotonic_ns=round(seconds * 1e9),
                utc=(datetime(2026, 10, 26, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat())


def case(arm="A", **changes):
    result = dict(case_id="SYNTHETIC-" + arm, block_id="fixture-block", arm=arm,
                  stage="synthetic_software_test", prompt_version="fixture", seed=12, weeks=4,
                  deadline_seconds=10, probes=[], comprehension=[], source_hashes=study.source_hashes())
    result.update(changes)
    return result


class DeadlineTests(unittest.TestCase):
    def new(self, **kwargs):
        return study.DeadlineCase(case(**kwargs), clock=point(0))

    def test_init_no_clock_and_repeated_show_no_reset_or_future_demand(self):
        game = self.new()
        self.assertIsNone(game.pending)
        self.assertEqual(game.game.week, 0)
        first = game.show(point(20))
        self.assertEqual(first, game.show(point(25)))
        self.assertEqual(first["deadline_clock"]["deadline_monotonic_ns"], point(30)["monotonic_ns"])
        self.assertEqual(game.game.week, 1)
        self.assertNotIn("seed", first)
        self.assertNotIn("future", json.dumps(first))

    def test_boundary_is_inclusive_and_one_nanosecond_late_stops(self):
        timely = self.new()
        shown = timely.show(point(0))
        ack = timely.submit("[0,1,2,3]", shown["decision_id"], received=point(10))
        self.assertTrue(ack["accepted"])
        late = self.new()
        shown = late.show(point(0))
        reception = point(10)
        reception["monotonic_ns"] += 1
        ack = late.submit("[0,1,2,3]", shown["decision_id"], received=reception)
        self.assertFalse(ack["accepted"])
        self.assertEqual(late.terminal_reason, "deadline_expired")
        self.assertEqual(late.weeks, [])
        self.assertTrue(late.game.awaiting)
        self.assertEqual(late.game.incoming, [4, 4, 4])
        self.assertIsNone(late.export()["full_game_cost"])
        self.assertEqual(late.export()["missing"]["weeks"], [1, 2, 3, 4])
        self.assertEqual(late.events[-1]["literal_input_text"], "[0,1,2,3]")
        self.assertTrue(study.audit_result(late.export(), late.case)["valid"])

    def test_stale_duplicate_and_invalid_attempt_never_reset_clock(self):
        game = self.new()
        shown = game.show(point(0))
        for raw in ("[1,2,3]", "[true,1,2,3]", "[1,-1,2,3]", "[1.5,1,2,3]"):
            self.assertFalse(game.submit(raw, shown["decision_id"], received=point(1))["accepted"])
        self.assertEqual(game.show(point(2)), shown)
        self.assertFalse(game.submit("[1,2,3,4]", "stale", received=point(2))["accepted"])
        self.assertTrue(game.submit("[1,2,3,4]", shown["decision_id"], received=point(3))["accepted"])
        self.assertFalse(game.submit("[1,2,3,4]", shown["decision_id"], received=point(4))["accepted"])
        next_display = game.show(point(5))
        self.assertNotEqual(next_display["decision_id"], shown["decision_id"])
        self.assertFalse(game.submit("[1,2,3,4]", shown["decision_id"], received=point(6))["accepted"])
        self.assertTrue(study.audit_result(game.export(), game.case)["valid"])

    def test_all_arms_single_submission_paired_demand_conservation_cost(self):
        demands = []
        for arm in "ABC":
            game = self.new(arm=arm)
            physical = _PhysicalGame()
            for week in range(4):
                display = game.show(point(week * 20))
                self.assertEqual(display["roles"], physical.observe(display["customer_demand"]))
                choices = [0, week + 1, 20 - week, 3]
                physical.commit(choices)
                ack = game.submit(json.dumps(choices), display["decision_id"], received=point(week * 20 + 1))
                self.assertTrue(ack["accepted"])
                self.assertEqual(game.game.outstanding, physical.outstanding)
                self.assertEqual(game.game.delivery, physical.delivery)
                self.assertNotEqual(ack["phase"], "revision")
                self.assertNotIn("roles", ack)
            payload = game.export()
            self.assertTrue(payload["complete"])
            self.assertEqual(len(payload["decisions"]), 4)
            self.assertEqual(payload["full_game_cost"], sum(sum(row["cost"] for row in w["roles"]) for w in payload["weeks"]))
            self.assertTrue(study.audit_result(payload, game.case)["valid"])
            demands.append([w["customer_demand"] for w in game.weeks])
        self.assertEqual(demands[0], demands[1])
        self.assertEqual(demands[0], demands[2])

    def test_probe_pages_then_untimed_comprehension_and_exact_ids(self):
        probes = [dict(id="p" + str(i), inventory=i) for i in range(8)]
        questions = [dict(question_id="q1", text="Synthetic question", choices={"A": "a", "B": "b"})]
        game = self.new(weeks=1, probes=probes, comprehension=questions)
        display = game.show(point(0))
        game.submit("[0,0,0,0]", display["decision_id"], received=point(1))
        self.assertEqual(game.phase(), "probes")
        for page in range(2):
            display = game.show(point(20 + page * 20))
            self.assertEqual(len(display["probes"]), 4)
            self.assertEqual(display["deadline_clock"]["deadline_seconds"], 10)
            self.assertFalse(game.submit("{}", display["decision_id"], received=point(21 + page * 20))["accepted"])
            choices = {p["probe_id"]: 0 for p in display["probes"]}
            game.submit(json.dumps(choices), display["decision_id"], received=point(22 + page * 20))
        display = game.show(point(60))
        self.assertEqual(display["phase"], "comprehension")
        self.assertIsNone(display["deadline_clock"]["deadline_seconds"])
        self.assertTrue(game.submit('{"q1":"A"}', display["decision_id"], received=point(10000))["accepted"])
        self.assertTrue(game.export()["complete"])
        self.assertTrue(study.audit_result(game.export(), game.case)["valid"])

    def test_timeout_persists_on_access_and_missing_probes_questions(self):
        game = self.new(probes=[dict(probe_id="p" + str(i)) for i in range(4)],
                        comprehension=[dict(question_id="q", options={"A": "a"})])
        shown = game.show(point(0))
        game.check_expiry(point(11))
        self.assertEqual(game.show(point(12))["phase"], "stopped")
        game.submit("[9,9,9,9]", shown["decision_id"], received=point(13))
        self.assertEqual(game.export()["missing"]["probe_ids"], ["p0", "p1", "p2", "p3"])
        self.assertEqual(game.export()["missing"]["question_ids"], ["q"])
        self.assertTrue(study.audit_result(game.export(), game.case)["valid"])

    def test_timeout_keeps_only_completed_prefix_without_imputation(self):
        game = self.new()
        shown = game.show(point(0))
        game.submit("[0,2,3,4]", shown["decision_id"], received=point(1))
        shown = game.show(point(20))
        game.submit("[99,99,99,99]", shown["decision_id"], received=point(31))
        payload = game.export()
        self.assertEqual(payload["completed_weeks"], 1)
        self.assertEqual(payload["missing"]["weeks"], [2, 3, 4])
        self.assertEqual([w["orders"] for w in payload["weeks"]], [[0, 2, 3, 4]])
        self.assertEqual(len(payload["decisions"]), 1)
        self.assertEqual(payload["completed_prefix_cost"], payload["weeks"][0]["cost"])
        self.assertIsNone(payload["full_game_cost"])
        self.assertEqual(game.game.week, 2)
        self.assertTrue(game.game.awaiting)
        self.assertTrue(study.audit_result(payload, game.case)["valid"])

    def test_latency_only_and_clock_reversal(self):
        game = self.new(deadline_seconds=None)
        shown = game.show(point(0))
        self.assertTrue(game.submit("[0,0,0,0]", shown["decision_id"], received=point(10000))["accepted"])
        shown = game.show(point(10001))
        self.assertFalse(game.submit("[0,0,0,0]", shown["decision_id"], received=point(2))["accepted"])
        self.assertEqual(game.terminal_reason, "clock_discontinuity")

    def test_phase_deadline_overrides_and_bad_override_rejected(self):
        game = self.new(weeks=1, phase_deadline_seconds={"game": None, "probes": 3},
                        probes=[dict(probe_id="p" + str(i)) for i in range(4)])
        shown = game.show(point(0))
        self.assertIsNone(shown["deadline_clock"]["deadline_seconds"])
        self.assertTrue(game.submit("[0,0,0,0]", shown["decision_id"], received=point(100))["accepted"])
        shown = game.show(point(200))
        self.assertEqual(shown["deadline_clock"]["deadline_seconds"], 3)
        self.assertEqual(shown["deadline_clock"]["deadline_monotonic_ns"], point(203)["monotonic_ns"])
        self.assertEqual(game.export()["phase_deadline_seconds"], {"game": None, "probes": 3})
        for overrides in ({"comprehension": 3}, {"game": -1}, {"probes": True}):
            with self.assertRaises(ValueError):
                self.new(phase_deadline_seconds=overrides)

    def test_source_and_result_tampering_rejected(self):
        bad = case()
        bad["source_hashes"]["physics"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source_hashes"):
            study.DeadlineCase(bad)
        game = self.new()
        shown = game.show(point(0))
        game.submit("[0,0,0,0]", shown["decision_id"], received=point(1))
        bad = copy.deepcopy(game.export())
        bad["weeks"][0]["orders"][0] = 10
        with self.assertRaisesRegex(ValueError, "replay differs"):
            study.audit_result(bad, game.case)

    def test_cli_round_trip_no_reinit_and_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "CASE.json").write_text(json.dumps(case(weeks=1, deadline_seconds=None)), encoding="utf-8")
            def run(action, *extra, raw=None):
                return subprocess.run([sys.executable, str(ROOT / "scripts/run_exp14_agent.py"), action,
                                       "--run", directory, *extra], input=raw, capture_output=True, text=True)
            initial = run("init")
            self.assertEqual(initial.returncode, 0, initial.stderr)
            self.assertIsNone(json.loads(initial.stdout)["open_decision_id"])
            self.assertNotEqual(run("init").returncode, 0)
            shown = json.loads(run("show").stdout)
            self.assertEqual(shown, json.loads(run("show").stdout))
            result = run("submit", "--decision-id", shown["decision_id"], raw="[0,0,0,0]")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["complete"])
            payload = json.loads((folder / "RESULT.json").read_text(encoding="utf-8"))
            self.assertTrue(study.audit_result(payload, case(weeks=1, deadline_seconds=None))["valid"])
            self.assertEqual(len(list((folder / "events").glob("*.json"))), len(payload["events"]))


if __name__ == "__main__":
    unittest.main()
