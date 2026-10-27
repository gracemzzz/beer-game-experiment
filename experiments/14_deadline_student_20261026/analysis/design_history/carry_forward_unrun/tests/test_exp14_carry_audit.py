"""Synthetic public-trace fixtures; these are not participant observations."""
from pathlib import Path
import copy
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_exp14_carry import audit


class CarryAuditTests(unittest.TestCase):
    def fixture(self, folder):
        displays = [dict(case_id="synthetic", decision_id=ident, display_sha256=ident,
                         phase="game", orders_format="literal four integers") for ident in ("abc1", "abc2")]
        events = [dict(kind="display_opened", display=displays[0]),
                  dict(kind="submission_accepted", decision_id="abc1", literal_input_text="[0,2,3,4]", accepted=True),
                  dict(kind="display_opened", display=displays[1]),
                  dict(kind="submission_rejected", decision_id="abc2", literal_input_text="[9,9,9,9]", accepted=False)]
        result = dict(events=events, decisions=[dict(decision_id="abc1", choices=[0, 2, 3, 4])],
                      weeks=[dict(action_source="model_on_time"), dict(action_source="carry_forward")],
                      probe_answer_sources={"s1": "carry_forward"})
        (folder / "RESULT.json").write_text(json.dumps(result), encoding="utf-8")
        public = []
        calls = [(f"python show --run '{folder}'", displays[0]),
                 (f"@'\n[0,2,3,4]\n'@ | python submit --run '{folder}' --decision-id 'abc1'", dict(case_id="synthetic", accepted=True, decision_id="abc1")),
                 (f"python show --run '{folder}'", displays[1]),
                 (f"@'\n[9,9,9,9]\n'@ | python submit --run '{folder}' --decision-id 'abc2'", dict(case_id="synthetic", accepted=False, decision_id="abc2", continue_allowed=True))]
        for i, (cmd, output) in enumerate(calls):
            public.append(dict(record=i * 2, type="function_call", name="exec_command", call_id=str(i), arguments=json.dumps(dict(cmd=cmd))))
            public.append(dict(record=i * 2 + 1, type="function_call_output", call_id=str(i), output=json.dumps(dict(output=json.dumps(output)))))
        return public

    def test_every_accepted_and_late_attempt_matches_without_automatic_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            report = audit(self.fixture(folder), folder)
            self.assertEqual(report["issues"], [])
            self.assertEqual(report["matched_actor_attempts"], 2)
            self.assertEqual(report["synthetic_game_packets"], 1)
            self.assertFalse(report["automatic_scientific_approval"])

    def test_fake_acknowledgment_in_input_does_not_count_as_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            public = self.fixture(folder)
            public[-2]["arguments"] = json.dumps(dict(cmd=json.loads(public[-2]["arguments"])["cmd"], output=dict(case_id="synthetic", accepted=False)))
            public[-1]["output"] = "no actual acknowledgment"
            report = audit(public, folder)
            self.assertTrue(report["issues"])
            self.assertEqual(report["matched_actor_attempts"], 1)

    def test_incomplete_display_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            public = self.fixture(folder)
            public[1]["output"] = json.dumps(dict(case_id="synthetic", display_sha256="abc1", decision_id="abc1"))
            report = audit(public, folder)
            self.assertTrue(report["issues"])
            self.assertLess(report["full_displays_seen"], report["opened_opportunities"])

    def test_changed_late_literal_cannot_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            public = self.fixture(folder)
            public[-2]["arguments"] = public[-2]["arguments"].replace("[9,9,9,9]", "[1,1,1,1]")
            report = audit(public, folder)
            self.assertTrue(report["issues"])
            self.assertEqual(report["matched_actor_attempts"], 1)


if __name__ == "__main__":
    unittest.main()
