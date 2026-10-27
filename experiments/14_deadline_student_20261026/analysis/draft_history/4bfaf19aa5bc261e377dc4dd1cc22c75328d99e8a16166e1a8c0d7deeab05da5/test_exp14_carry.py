"""Synthetic carry-forward mechanics; no participant model or API requests."""
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
from beergame_study import exp14_carry as study
from beergame_study.manual_weekly_v3 import _PhysicalGame


def point(seconds):
    return dict(monotonic_ns=round(seconds * 1e9),
                utc=(datetime(2026, 10, 26, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat())


def case(**changes):
    result = dict(schema_version=study.SCHEMA, timeout_policy=study.POLICY,
                  case_id="SYNTHETIC-CARRY", block_id="fixture", arm="A",
                  stage="synthetic_software_test", prompt_version="fixture", seed=12, weeks=4,
                  deadline_seconds=10, probes=[], comprehension=[], source_hashes=study.source_hashes())
    result.update(changes)
    return result


class CarryTests(unittest.TestCase):
    def new(self, **changes):
        return study.CarryCase(case(**changes), clock=point(0))

    def audit(self, game):
        self.assertTrue(study.audit_result(game.export(), game.case)["valid"])

    def test_schema_and_policy_and_source_binding(self):
        for field, value in (("schema_version", "old"), ("timeout_policy", "random"),
                             ("source_hashes", {"controller": "wrong"})):
            with self.assertRaises(ValueError):
                self.new(**{field: value})

    def test_exact_boundary_accepts_zero_and_one_nanosecond_late_is_missing(self):
        timely = self.new(weeks=1)
        display = timely.show(point(0))
        self.assertTrue(timely.submit("[0,1,2,3]", display["decision_id"], received=point(10))["accepted"])
        self.assertEqual(timely.weeks[0]["orders"], [0, 1, 2, 3])
        self.assertTrue(timely.status()["all_actor_responses_complete"])
        self.audit(timely)
        late = self.new(weeks=1)
        display = late.show(point(0))
        receipt = point(10)
        receipt["monotonic_ns"] += 1
        ack = late.submit("[0,1,2,3]", display["decision_id"], received=receipt)
        self.assertFalse(ack["accepted"])
        self.assertTrue(ack["continue_allowed"])
        self.assertEqual(ack["transition_kind"], "game_carry_forward")
        self.assertEqual(late.weeks[0]["orders"], [4, 4, 4, 4])
        self.assertEqual(late.weeks[0]["actor_orders"], [None] * 4)
        self.assertEqual(late.weeks[0]["actor_missing_mask"], [True] * 4)
        self.assertEqual(late.decisions, [])
        self.assertTrue(late.status()["complete"])
        self.assertFalse(late.status()["all_actor_responses_complete"])
        self.assertEqual(late.events[-1]["lateness_seconds"], 1e-9)
        self.assertEqual(late.events[-1]["attempted_choices"], [0, 1, 2, 3])
        self.audit(late)

    def test_previous_applied_zero_packet_repeats_across_chained_timeouts(self):
        game = self.new()
        display = game.show(point(0))
        game.submit("[0,0,0,0]", display["decision_id"], received=point(1))
        prior_id = display["decision_id"]
        for week in range(1, 4):
            display = game.show(point(20 * week))
            ack = game.submit("[999,999,999,999]", display["decision_id"], received=point(20 * week + 11))
            self.assertFalse(ack["accepted"])
            self.assertEqual(game.weeks[-1]["orders"], [0] * 4)
            self.assertEqual(game.applied_actions[-1]["carried_from_decision_id"], prior_id)
            self.assertFalse(game.applied_actions[-1]["initial_orders_used"])
            prior_id = display["decision_id"]
        self.assertEqual(len(game.decisions), 1)
        self.assertEqual(game.export()["missing"]["weeks"], [2, 3, 4])
        self.assertEqual(game.export()["missing"]["physical_weeks"], [])
        self.audit(game)

    def test_status_expiry_advances_one_and_never_opens_next_clock(self):
        game = self.new()
        game.show(point(0))
        ack = game.status(clock=point(10000))
        self.assertTrue(ack["continue_allowed"])
        self.assertEqual(ack["completed_weeks"], 1)
        self.assertIsNone(ack["open_decision_id"])
        self.assertEqual(ack["next_action"], "show")
        self.assertNotIn("roles", ack)
        self.assertEqual(game.game.week, 1)
        self.assertFalse(game.game.awaiting)
        self.assertFalse(game.status(clock=point(20000))["continue_allowed"])
        self.assertEqual(len(game.weeks), 1)
        shown = game.show(point(30000))
        self.assertEqual(shown["week"], 2)
        self.assertEqual(shown["deadline_clock"]["opened_monotonic_ns"], point(30000)["monotonic_ns"])
        self.audit(game)

    def test_show_can_expire_one_and_open_one_without_reset(self):
        game = self.new()
        first = game.show(point(0))
        second = game.show(point(1000))
        self.assertEqual(len(game.weeks), 1)
        self.assertEqual(second["week"], 2)
        self.assertNotEqual(first["decision_id"], second["decision_id"])
        self.assertEqual(second, game.show(point(1009)))
        self.assertEqual(game.game.week, 2)
        self.assertNotIn("seed", second)
        self.audit(game)

    def test_on_time_invalid_and_stale_attempts_leave_original_timer(self):
        game = self.new()
        display = game.show(point(0))
        for raw in ("[1,2,3]", "[true,2,3,4]", "[1,-1,2,3]", "[1.5,2,3,4]", "not JSON",
                    "[NaN,1,2,3]", '{"a":1,"a":2}'):
            ack = game.submit(raw, display["decision_id"], received=point(1))
            self.assertFalse(ack["accepted"])
            self.assertFalse(ack["continue_allowed"])
            self.assertEqual(game.events[-1]["literal_input_text"], raw)
            self.assertTrue(game.events[-1]["payload_status"].startswith("invalid_payload:"))
        self.assertFalse(game.submit("[9,9,9,9]", "unknown-id", received=point(2))["accepted"])
        self.assertEqual(display, game.show(point(9)))
        self.assertEqual(game.weeks, [])
        game.submit("[1,2,3,4]", display["decision_id"], received=point(10))
        self.assertEqual(game.weeks[0]["orders"], [1, 2, 3, 4])
        self.audit(game)

    def test_malformed_late_packet_only_falls_back_because_clock_expired(self):
        game = self.new()
        display = game.show(point(0))
        raw = "{broken transcription\n"
        ack = game.submit(raw, display["decision_id"], received=point(11))
        self.assertEqual(ack["reason"], "deadline_expired")
        self.assertTrue(ack["continue_allowed"])
        self.assertEqual(game.events[-1]["receipt_status"], "late")
        self.assertTrue(game.events[-1]["payload_status"].startswith("invalid_payload:"))
        self.assertEqual(game.events[-1]["literal_input_text"], raw)
        self.assertEqual(len(game.weeks), 1)
        self.assertIsNone(game.pending)
        self.audit(game)

    def test_stale_packet_cannot_leak_into_next_open_decision(self):
        game = self.new()
        first = game.show(point(0))
        game.status(clock=point(11))
        second = game.show(point(20))
        ack = game.submit("[99,98,97,96]", first["decision_id"], received=point(21))
        self.assertFalse(ack["accepted"])
        self.assertFalse(ack["continue_allowed"])
        self.assertEqual(game.events[-1]["elapsed_seconds"], 21)
        self.assertEqual(second, game.show(point(22)))
        self.assertEqual(len(game.weeks), 1)
        game.submit("[0,1,2,3]", second["decision_id"], received=point(23))
        self.assertEqual(game.weeks[-1]["orders"], [0, 1, 2, 3])
        self.audit(game)

    def test_stale_receipt_after_new_deadline_expires_only_new_opportunity(self):
        game = self.new()
        first = game.show(point(0))
        game.submit("[1,2,3,4]", first["decision_id"], received=point(1))
        second = game.show(point(20))
        ack = game.submit("[99,99,99,99]", first["decision_id"], received=point(31))
        self.assertFalse(ack["accepted"])
        self.assertFalse(ack["continue_allowed"])
        self.assertEqual(len(game.weeks), 2)
        self.assertEqual(game.weeks[-1]["decision_id"], second["decision_id"])
        self.assertEqual(game.weeks[-1]["orders"], [1, 2, 3, 4])
        self.assertIsNone(game.pending)
        self.audit(game)

    def test_late_probe_page_remains_all_missing_and_next_page_continues(self):
        game = self.new(weeks=1, probes=[dict(probe_id="p" + str(i)) for i in range(8)],
                        comprehension=[dict(question_id="q", options={"A": "a", "B": "b"})])
        display = game.show(point(0))
        game.submit("[0,0,0,0]", display["decision_id"], received=point(1))
        self.assertTrue(game.status()["game_complete"])
        self.assertFalse(game.status()["complete"])
        display = game.show(point(20))
        raw = json.dumps({p["probe_id"]: 7 for p in display["probes"]})
        ack = game.submit(raw, display["decision_id"], received=point(31))
        self.assertEqual(ack["transition_kind"], "probe_missing")
        self.assertEqual(game.probe_answers, {"p0": None, "p1": None, "p2": None, "p3": None})
        self.assertEqual(len(game.applied_actions), 1)
        self.assertIsNone(game.pending)
        display = game.show(point(40))
        self.assertEqual(display["page_index"], 2)
        game.submit(json.dumps({p["probe_id"]: 0 for p in display["probes"]}),
                    display["decision_id"], received=point(50))
        display = game.show(point(60))
        self.assertEqual(display["phase"], "comprehension")
        self.assertIsNone(display["deadline_clock"]["deadline_monotonic_ns"])
        self.assertFalse(game.submit('{"q":"Z"}', display["decision_id"], received=point(1000))["accepted"])
        self.assertFalse(game.check_expiry(point(100000)))
        self.assertIsNone(game.comprehension_answers)
        self.assertTrue(game.submit('{"q":"B"}', display["decision_id"], received=point(100001))["accepted"])
        result = game.export()
        self.assertTrue(result["protocol_complete"])
        self.assertFalse(result["probes_complete"])
        self.assertFalse(result["all_actor_responses_complete"])
        self.assertEqual(result["processed_probe_pages"], 2)
        self.assertEqual(result["completed_probe_pages"], 1)
        self.assertEqual(result["missing"]["probe_ids"], ["p0", "p1", "p2", "p3"])
        self.assertEqual(result["missing"]["question_ids"], [])
        self.audit(game)

    def test_all_arms_mixed_actions_exact_physics_cost_conservation(self):
        demands = []
        for arm in "ABC":
            game = self.new(arm=arm, weeks=24)
            physical = _PhysicalGame()
            prior = [4] * 4
            for week in range(24):
                display = game.show(point(week * 20))
                self.assertEqual(display["roles"], physical.observe(display["customer_demand"]))
                late = week % 3 == 0
                choices = [0, week, 10, week % 2]
                applied = prior if late else choices
                physical.commit(applied)
                game.submit(json.dumps(choices), display["decision_id"], received=point(week * 20 + (11 if late else 1)))
                self.assertEqual(game.weeks[-1]["orders"], applied)
                self.assertEqual(game.game.outstanding, physical.outstanding)
                self.assertEqual(game.game.delivery, physical.delivery)
                self.assertIsNone(game.pending)
                prior = applied
            result = game.export()
            self.assertEqual(result["full_game_cost"], sum(sum(r["cost"] for r in w["roles"]) for w in result["weeks"]))
            self.assertEqual(result["fallback_weeks"], 8)
            self.assertEqual(result["actor_completed_weeks"], 16)
            self.audit(game)
            demands.append([w["customer_demand"] for w in game.weeks])
        self.assertEqual(demands[0], demands[1])
        self.assertEqual(demands[0], demands[2])

    def test_phase_overrides_unlimited_and_clock_discontinuity(self):
        game = self.new(weeks=1, deadline_seconds=10, phase_deadline_seconds={"game": None, "probes": 3},
                        probes=[dict(probe_id="p" + str(i)) for i in range(4)])
        display = game.show(point(0))
        self.assertIsNone(display["deadline_clock"]["deadline_seconds"])
        game.submit("[0,0,0,0]", display["decision_id"], received=point(1000))
        display = game.show(point(2000))
        self.assertEqual(display["deadline_clock"]["deadline_seconds"], 3)
        self.assertFalse(game.submit("{}", display["decision_id"], received=point(1999))["accepted"])
        self.assertEqual(game.terminal_reason, "clock_discontinuity")
        self.assertEqual(game.probe_answers, {})
        self.audit(game)
        for override in ({"comprehension": 1}, {"game": 0}, {"probes": True}):
            with self.assertRaises(ValueError):
                self.new(phase_deadline_seconds=override)

    def test_replay_rejects_action_missingness_cost_deadline_and_event_tampering(self):
        game = self.new()
        display = game.show(point(0))
        game.submit("[8,7,6,5]", display["decision_id"], received=point(11))
        original = game.export()
        for field, value in (("orders", [8, 7, 6, 5]), ("actor_orders", [4] * 4),
                             ("action_source", "actor"), ("actor_missing_mask", [False] * 4), ("cost", -1)):
            bad = copy.deepcopy(original)
            bad["weeks"][0][field] = value
            with self.assertRaisesRegex(ValueError, "replay differs"):
                study.audit_result(bad, game.case)
        bad = copy.deepcopy(original)
        bad["events"][-1]["literal_input_text"] = "[4,4,4,4]"
        with self.assertRaisesRegex(ValueError, "Event chain differs"):
            study.audit_result(bad, game.case)
        bad = copy.deepcopy(original)
        bad["opportunities"][0]["deadline_clock"]["deadline_monotonic_ns"] += 1
        with self.assertRaisesRegex(ValueError, "replay differs"):
            study.audit_result(bad, game.case)

    def test_cli_failed_attempts_atomic_receipts_no_reinit_and_no_automatic_clock(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            fixture = case(weeks=2, deadline_seconds=None)
            (folder / "CASE.json").write_text(json.dumps(fixture), encoding="utf-8")
            def run(action, *extra, raw=None):
                return subprocess.run([sys.executable, str(ROOT / "scripts/run_exp14_carry.py"), action,
                                       "--run", directory, *extra], input=raw, capture_output=True, text=True)
            self.assertEqual(run("init").returncode, 0)
            self.assertNotEqual(run("init").returncode, 0)
            shown = json.loads(run("show").stdout)
            failed = run("submit", "--decision-id", shown["decision_id"], raw="[oops]")
            self.assertEqual(failed.returncode, 2, failed.stderr)
            self.assertFalse(json.loads(failed.stdout)["continue_allowed"])
            self.assertEqual(shown, json.loads(run("show").stdout))
            self.assertEqual(run("submit", "--decision-id", "stale", raw="[1,2,3,4]").returncode, 2)
            accepted = run("submit", "--decision-id", shown["decision_id"], raw="[0,0,0,0]")
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertIsNone(json.loads(accepted.stdout)["open_decision_id"])
            payload = json.loads((folder / "RESULT.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["events"][2]["literal_input_text"], "[oops]")
            self.assertTrue(study.audit_result(payload, fixture)["valid"])
            event_files = list((folder / "events").glob("*.json"))
            self.assertEqual(len(event_files), len(payload["events"]))
            event_files[0].write_text("tampered", encoding="utf-8")
            self.assertNotEqual(run("status").returncode, 0)

    def test_cli_late_attempt_preserved_and_status_cannot_cascade(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            fixture = case(weeks=2, deadline_seconds=1e-9)
            (folder / "CASE.json").write_text(json.dumps(fixture), encoding="utf-8")
            def run(action, *extra, raw=None):
                return subprocess.run([sys.executable, str(ROOT / "scripts/run_exp14_carry.py"), action,
                                       "--run", directory, *extra], input=raw, capture_output=True, text=True)
            self.assertEqual(run("init").returncode, 0)
            shown = json.loads(run("show").stdout)
            late = run("submit", "--decision-id", shown["decision_id"], raw="[999,999,999,999]")
            self.assertEqual(late.returncode, 0, late.stderr)
            ack = json.loads(late.stdout)
            self.assertTrue(ack["continue_allowed"])
            self.assertEqual(ack["completed_weeks"], 1)
            self.assertIsNone(ack["open_decision_id"])
            self.assertEqual(json.loads(run("status").stdout)["completed_weeks"], 1)
            payload = json.loads((folder / "RESULT.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["events"][-1]["literal_input_text"], "[999,999,999,999]")
            self.assertEqual(payload["events"][-1]["receipt_status"], "late")
            self.assertTrue(study.audit_result(payload, fixture)["valid"])


if __name__ == "__main__":
    unittest.main()
