"""Temporary, synthetic HTTP checks for the final bounded Claude follow-up.

Construct the actual failure sequence: original GPT-6 arithmetic failure plus
Claude truncation; first recovery GPT-6 pass plus Claude arithmetic failure.
No real provider calls, credentials, or live-study writes occur in these tests.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import batched_pressure as study
from beergame_study import batched_pressure_api as api
from beergame_study import batched_pressure_recovery as recovery
from beergame_study import batched_pressure_followup as followup

KEYS = {"openai": "fake-openai-followup", "anthropic": "fake-anthropic-followup"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def request_task_id(body):
    output = body.get("text", {}).get("format") or body["output_config"]["format"]
    return output["schema"]["properties"]["task_id"]["enum"][0]


def provider_response(body, payload, truncated=False):
    model = body["model"]
    usage = dict(input_tokens=500, output_tokens=1200)
    if api.RATES[model]["provider"] == "openai":
        return dict(model=model, status="completed", usage=usage,
                    output=[dict(type="message", content=[dict(type="output_text", text=json.dumps(payload))])])
    if truncated:
        return dict(model=model, stop_reason="max_tokens",
                    usage=dict(input_tokens=500, output_tokens=8192,
                               output_tokens_details=dict(reasoning_tokens=8192)),
                    content=[dict(type="thinking", thinking="Explicitly synthetic incomplete fixture.")])
    return dict(model=model, stop_reason="end_turn", usage=usage,
                content=[dict(type="text", text=json.dumps(payload))])


class FollowupTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.experiment = Path(temporary.name).resolve()
        for name in ("PROTOCOL.md", "RECOVERY_20261021.md", "CLAUDE_FOLLOWUP_20261021.md"):
            destination = self.experiment / "hypotheses" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / "experiments/12_pressure_framing_api_20261020/hypotheses" / name).read_bytes())
        self.parent = study.prepare(self.experiment)
        self.plan = study.loadplan(self.parent)
        self.tasks = {task["task_id"]: task for task in self.plan["tasks"]}
        self.prior_calls = []
        self.calls = []
        self.sent = []

        def original_handler(request):
            body = json.loads(request.content)
            task = self.tasks[request_task_id(body)]
            self.prior_calls.append(("original", task["task_id"]))
            payload = study.synthetic_fixture(task)
            if task["model"] == "gpt-6-luna":
                for chain in payload["chains"]:
                    for checkpoint in chain["inventory_checkpoints"][1:]:
                        checkpoint["inventories"][0] += 1
            return httpx.Response(200, json=provider_response(body, payload,
                                  truncated=task["model"] == "claude-haiku-5-5"))

        await api.Runner(self.parent, keys=KEYS, retry_delay=0,
                         transport=httpx.MockTransport(original_handler)).execute("all")
        self.previous = recovery.prepare(self.parent)

        def recovery_handler(request):
            body = json.loads(request.content)
            task = self.tasks[request_task_id(body)]
            self.prior_calls.append(("recovery", task["task_id"]))
            payload = study.synthetic_fixture(task)
            if task["model"] == "claude-haiku-5-5":
                for chain in payload["chains"]:
                    for checkpoint in chain["inventory_checkpoints"][1:]:
                        checkpoint["inventories"][0] += 1
            return httpx.Response(200, json=provider_response(body, payload))

        result = await recovery.Runner(self.previous, keys=KEYS, retry_delay=0,
                     transport=httpx.MockTransport(recovery_handler)).execute("all")
        self.assertEqual((result["accepted"], result["failed"]), (3, 1))
        self.prior_files = {path: sha(path) for directory in (self.parent, self.experiment / "raw")
                            for path in directory.rglob("*") if path.is_file()}
        self.prior_spend = api.BudgetLedger(self.experiment).spent
        self.successor = followup.prepare(self.previous)

    def valid_handler(self, request):
        body = json.loads(request.content)
        task_id = request_task_id(body)
        self.calls.append(task_id)
        self.sent.append(body)
        return httpx.Response(200, json=provider_response(body, study.synthetic_fixture(self.tasks[task_id])))

    def runner(self, handler=None, keys=None):
        return followup.Runner(self.successor, keys=KEYS if keys is None else keys,
                               retry_delay=0, transport=httpx.MockTransport(handler or self.valid_handler))

    def assert_prior_files_unchanged(self):
        self.assertTrue(all(path.exists() and sha(path) == before for path, before in self.prior_files.items()))

    async def test_one_claude_pilot_then_four_main_calls_resume_without_rebilling(self):
        progress = await self.runner().execute("all")
        self.assertEqual(len(self.prior_calls), 6)
        self.assertEqual(self.calls[0], "claude-haiku-5-5_pilot")
        self.assertEqual(len(self.calls), 5)
        self.assertEqual(set(self.calls[1:]), {model + "_main" for model in study.MODELS})
        self.assertEqual((progress["accepted"], progress["failed"], progress["remaining"]), (8, 0, 0))
        self.assertEqual(progress["inherited"], 3)
        ledger = api.BudgetLedger(self.experiment)
        self.assertEqual(len(ledger.data["attempts"]), 11)
        self.assertGreater(ledger.spent, self.prior_spend)
        original_ledger = (self.experiment / "data/api_budget.json").read_bytes()
        self.assertEqual(followup.prepare(self.previous), self.successor)
        await self.runner().execute("all")
        self.assertEqual(len(self.calls), 5)
        self.assertEqual((self.experiment / "data/api_budget.json").read_bytes(), original_ledger)
        self.assertEqual(len(list((self.parent / "accepted").glob("*.json"))), 2)
        self.assertEqual(len(list((self.previous / "accepted").glob("*.json"))), 1)
        self.assert_prior_files_unchanged()

    async def test_frozen_ids_settings_and_only_five_new_payloads(self):
        manifest = followup.load(self.successor)
        self.assertEqual(len(manifest["new_task_ids"]), 5)
        self.assertEqual(len(manifest["inherited_pilots"]), 3)
        expected = {"claude-haiku-5-5_pilot"} | {model + "_main" for model in study.MODELS}
        self.assertEqual(set(manifest["new_task_ids"]), expected)
        self.assertEqual(followup.parent_run(self.successor), self.parent)
        for task_id in expected:
            task = self.tasks[task_id]
            payload = study.read(self.successor / "payloads" / (task_id + ".json"))
            self.assertEqual(request_task_id(payload), task_id)
            if task["model"] == "claude-haiku-5-5":
                self.assertEqual(payload["thinking"], {"type": "adaptive"})
                self.assertEqual(payload["output_config"]["effort"], "medium")
                self.assertEqual(payload["max_tokens"], 32768 if task["phase"] == "pilot" else 65536)
                text = payload["messages"][0]["content"]
                self.assertIn(recovery.STATE_TRACKING_APPENDIX, text)
                self.assertIn(recovery.CLAUDE_COMPLETION_APPENDIX, text)
                # No failed-order/checkpoint answers are fed back as corrections.
                self.assertNotIn("[30,14,12,10]", text)
                self.assertNotIn("[35,13,10,8]", text)
            else:
                self.assertEqual(payload, recovery.amended_payload(task))
        estimate = followup.estimate(self.successor)
        self.assertEqual(sum(row["pilot_calls"] for row in estimate), 1)
        self.assertEqual(sum(row["main_calls"] for row in estimate), 4)
        self.assert_prior_files_unchanged()

    async def test_claude_semantic_failure_stops_after_one_call_and_is_not_regenerated(self):
        def invalid_handler(request):
            body = json.loads(request.content)
            task_id = request_task_id(body)
            self.calls.append(task_id)
            payload = study.synthetic_fixture(self.tasks[task_id])
            payload["chains"][0]["inventory_checkpoints"][1]["inventories"][0] += 1
            return httpx.Response(200, json=provider_response(body, payload))
        result = await self.runner(invalid_handler).execute("all")
        self.assertEqual(self.calls, ["claude-haiku-5-5_pilot"])
        self.assertEqual((result["accepted"], result["failed"], result["skipped"]), (3, 1, 4))
        self.assertFalse((self.successor / "accepted/claude-haiku-5-5_pilot.json").exists())
        before = (self.experiment / "data/api_budget.json").read_bytes()
        self.assertEqual(followup.prepare(self.previous), self.successor)
        await self.runner(invalid_handler).execute("all")
        self.assertEqual(self.calls, ["claude-haiku-5-5_pilot"])
        self.assertEqual((self.experiment / "data/api_budget.json").read_bytes(), before)
        self.assert_prior_files_unchanged()

    async def test_prior_charges_and_unknown_reservations_share_the_five_dollar_cap(self):
        ledger = api.BudgetLedger(self.experiment)
        self.assertAlmostEqual(ledger.spent, self.prior_spend)
        ledger.reserve("synthetic_remaining_allowance_reservation", 5. - ledger.spent,
                       {"run": "temporary_software_check"})
        result = await self.runner().execute("all")
        self.assertEqual(self.calls, [])
        self.assertAlmostEqual(result["charged_or_reserved_usd"], 5.)
        self.assertEqual(result["accepted"], 3)
        self.assert_prior_files_unchanged()

    async def test_technical_retry_repeats_same_payload_and_reserves_unknown_charge(self):
        received = []
        def flaky_handler(request):
            body = json.loads(request.content)
            self.calls.append(request_task_id(body))
            received.append(body)
            if len(received) == 1:
                raise httpx.ReadTimeout("Synthetic transport interruption", request=request)
            return httpx.Response(200, json=provider_response(body,
                                  study.synthetic_fixture(self.tasks[request_task_id(body)])))
        result = await self.runner(flaky_handler).execute("pilot")
        self.assertEqual(self.calls, ["claude-haiku-5-5_pilot"] * 2)
        self.assertEqual(received[0], received[1])
        self.assertEqual(result["accepted"], 4)
        unknown = [row for row in api.BudgetLedger(self.experiment).data["attempts"].values()
                   if row["status"] == "unknown_charge"]
        self.assertEqual(len(unknown), 1)
        self.assertEqual(unknown[0]["charge_usd"], unknown[0]["reserve_usd"])
        self.assert_prior_files_unchanged()

    async def test_tampered_payload_snapshot_or_inherited_evidence_blocks_before_http(self):
        paths = [self.successor / "payloads/claude-haiku-5-5_pilot.json",
                 self.successor / "source_snapshot/batched_pressure_followup.py",
                 self.previous / "accepted/gpt-6-luna_pilot.json"]
        for path in paths:
            before = path.read_bytes()
            with self.subTest(path=path.name):
                if path.parent.name == "payloads":
                    changed = json.loads(before)
                    changed["max_tokens"] = 1024
                    path.write_text(json.dumps(changed))
                else:
                    path.write_bytes(before + b"\n ")
                with self.assertRaises(ValueError):
                    self.runner()
                self.assertEqual(self.calls, [])
                path.write_bytes(before)
        self.assertEqual(followup.prepare(self.previous), self.successor)
        self.assert_prior_files_unchanged()

    async def test_analysis_keeps_eight_descriptive_rows_and_no_false_hypothesis_proof(self):
        before = followup.analyze(self.successor)
        self.assertEqual(sum(row["accepted_pilot_responses"] for row in before["model_status"]), 3)
        self.assertEqual(len(before["hypotheses"]), 8)
        self.assertTrue(all(row["mean_strong_minus_no"] is None for row in before["hypotheses"]))
        await self.runner().execute("all")
        result = followup.analyze(self.successor)
        self.assertEqual(len(result["hypotheses"]), 8)
        self.assertEqual(len(result["rounds"]), 8448)
        self.assertEqual(len([row for row in result["rounds"] if row["phase"] == "main"]), 7680)
        self.assertEqual(len(result["chains"]), 88)
        self.assertEqual(len(result["recovery_metadata"]["inherited_pilots"]), 3)
        for row in result["hypotheses"]:
            self.assertEqual(row["paired_blocks"], 10)
            self.assertEqual(row["mean_strong_minus_no"], 0)
            self.assertIsNone(row["p_raw"])
            self.assertIsNone(row["p_holm_8"])
            self.assertIsNone(row["paired_bootstrap_95"])
            self.assertFalse(row["inference_available"])
            self.assertFalse(row["literal_binding_time_test"])
        original = study.analyze(self.parent)
        previous = recovery.analyze(self.previous)
        self.assertEqual(sum(row["accepted_main_responses"] for row in original["model_status"]), 0)
        self.assertEqual(sum(row["accepted_main_responses"] for row in previous["model_status"]), 0)
        self.assert_prior_files_unchanged()

    async def test_missing_key_does_not_purchase_or_mark_a_new_pilot_accepted(self):
        before = (self.experiment / "data/api_budget.json").read_bytes()
        result = await self.runner(keys={}).execute("all")
        self.assertEqual(self.calls, [])
        self.assertEqual(result["accepted"], 3)
        self.assertEqual((self.experiment / "data/api_budget.json").read_bytes(), before)
        self.assertFalse((self.successor / "accepted/claude-haiku-5-5_pilot.json").exists())
        self.assert_prior_files_unchanged()


if __name__ == "__main__":
    unittest.main()
