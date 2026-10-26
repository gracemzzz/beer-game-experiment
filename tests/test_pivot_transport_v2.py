"""Synthetic mocked transport controls, never model-study observations."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from beergame_study import pivot_transport_v2 as api
from beergame_study import weekly_pivot_v2 as study


class TransportTests(unittest.TestCase):
    def fixture(self, base):
        experiment = Path(base) / "experiments/13_weekly_state_api_20261021"
        budget = experiment.parent / "12_pressure_framing_api_20261020"
        (experiment / "hypotheses").mkdir(parents=True)
        original = Path(__file__).resolve().parents[1] / "experiments/13_weekly_state_api_20261021/hypotheses/PIVOT_V2_20261025.md"
        (experiment / "hypotheses/PIVOT_V2_20261025.md").write_bytes(original.read_bytes())
        (budget / "data").mkdir(parents=True)
        (budget / "data/api_budget.json").write_text(json.dumps(dict(cap_usd=5., attempts={
            "historical": dict(charge_usd=1.179072025, reserve_usd=1.179072025, status="received")
        })), encoding="utf-8")
        return api.prepare(experiment, budget, blocks=40), budget

    def test_high_effort_caps_and_no_temperature(self):
        p = study.make_plan(blocks=1)
        for model in study.DEFAULT_MODELS:
            t = api.preflight_task(p, model)
            payload = api.payload_for(model, t["prompt"], t["schema"])
            self.assertNotIn("temperature", payload)
            if model.startswith("gpt"):
                self.assertEqual(payload["reasoning"]["effort"], "high")
                self.assertEqual(payload["max_output_tokens"], 8192)
            else:
                self.assertEqual(payload["thinking"]["type"], "adaptive")
                self.assertEqual(payload["output_config"]["effort"], "high")

    def test_no_new_ledger_or_unfunded_main(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(api.BudgetStop):
                api.budget_status(Path(temp) / "not-created")
            self.assertFalse((Path(temp) / "not-created").exists())
            run, budget = self.fixture(temp)
            before = (budget / "data/api_budget.json").read_bytes()
            plan = api.planning(run)
            self.assertLess(plan["preflight_reserve_usd"], 1.5)
            self.assertGreater(plan["full_fixed_sample_reservation_bound_usd"], plan["budget"]["remaining_usd"])
            with self.assertRaises(api.BudgetStop):
                api.Runner(run).run_games()
            self.assertEqual(before, (budget / "data/api_budget.json").read_bytes())

    def test_mocked_preflight_resume_and_raw_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            run, budget = self.fixture(temp)
            plan = api.read(run / "plan.json")
            count = []
            def handler(request):
                model = json.loads(request.content)["model"]
                t = api.preflight_task(plan, model)
                literal = {a: dict(schema_version=c["schema_version"], study_id=c["study_id"], task_id=c["task_id"],
                                   orders={cid: [0, 0, 0, 0] for cid in c["chain_ids"]}) for a, c in t["cases"].items()}
                text = json.dumps(literal)
                raw = dict(model=model, usage=dict(input_tokens=100, output_tokens=100))
                if model.startswith("gpt"):
                    raw.update(status="completed", output=[dict(type="message", content=[dict(type="output_text", text=text)])])
                else:
                    raw.update(stop_reason="end_turn", content=[dict(type="text", text=text)])
                count.append(model)
                return httpx.Response(200, json=raw)
            runner = api.Runner(run, {"openai": "synthetic-test-credential", "anthropic": "synthetic-test-credential"},
                                transport=httpx.MockTransport(handler))
            self.assertTrue(all(runner.run_preflight().values()))
            self.assertEqual(len(count), 4)
            before = (budget / "data/api_budget.json").read_bytes()
            self.assertTrue(all(runner.run_preflight().values()))
            self.assertEqual(len(count), 4)
            self.assertEqual(before, (budget / "data/api_budget.json").read_bytes())
            ledger = api.read(budget / "data/api_budget.json")
            self.assertEqual(ledger["attempts"]["historical"]["charge_usd"], 1.179072025)
            # New charges never change the run identity or reopen paid slots.
            self.assertEqual(api.prepare(run.parent.parent, budget, blocks=40), run)
            for path in run.rglob("*"):
                if path.is_file():
                    self.assertNotIn(b"synthetic-test-credential", path.read_bytes())
            accepted = next((run / "attempts").glob("*/accepted.json"))
            accepted.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.run_preflight()

    def test_unknown_charge_remains_reserved_and_no_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            run, budget = self.fixture(temp)
            count = []
            def handler(request):
                count.append(1)
                raise httpx.ReadTimeout("Synthetic timeout")
            runner = api.Runner(run, {"openai": "fake", "anthropic": "fake"}, transport=httpx.MockTransport(handler))
            self.assertFalse(any(runner.run_preflight().values()))
            entries = [v for k, v in api.read(budget / "data/api_budget.json")["attempts"].items() if k != "historical"]
            self.assertEqual(len(entries), 4)
            self.assertTrue(all(v["charge_usd"] == v["reserve_usd"] for v in entries))
            self.assertFalse(any(runner.run_preflight().values()))
            self.assertEqual(len(count), 4)

    def test_usage_counts_reasoning_once_and_rejects_bad_counts(self):
        raw = dict(usage=dict(input_tokens=100, output_tokens=1000, output_tokens_details=dict(reasoning_tokens=900)))
        usage, amount = api.measured_usage("gpt-6-astra", raw)
        self.assertEqual(usage["reasoning_tokens"], 900)
        self.assertAlmostEqual(amount, (100 * 12.5 + 1000 * 50) / 1e6)
        raw["usage"]["output_tokens_details"]["reasoning_tokens"] = 1001
        self.assertEqual(api.measured_usage("gpt-6-astra", raw), (None, None))

    def test_missing_provider_or_changed_ledger_buys_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            run, budget = self.fixture(temp)
            requests = []
            def handler(request):
                requests.append(request)
                return httpx.Response(500)
            runner = api.Runner(run, {"openai": "fake"}, transport=httpx.MockTransport(handler))
            with self.assertRaises(ValueError):
                runner.run_preflight()
            self.assertEqual(requests, [])
            runner.keys["anthropic"] = "fake"
            ledger = api.read(budget / "data/api_budget.json")
            ledger["attempts"]["historical"]["charge_usd"] = 0.
            (budget / "data/api_budget.json").write_text(json.dumps(ledger), encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.run_preflight()
            self.assertEqual(requests, [])

    def test_success_body_without_usage_fails_accounting_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            run, budget = self.fixture(temp)
            def handler(request):
                model = json.loads(request.content)["model"]
                return httpx.Response(200, json=dict(model=model, status="completed", output=[]))
            runner = api.Runner(run, {"openai": "fake", "anthropic": "fake"}, transport=httpx.MockTransport(handler))
            self.assertFalse(any(runner.run_preflight().values()))
            receipts = [api.read(p) for p in (run / "attempts").glob("*/receipt.json")]
            self.assertEqual(len(receipts), 4)
            self.assertTrue(all(not r["accepted"] and r["charge_usd"] == r["reserve_usd"] for r in receipts))
            self.assertTrue(all("usage" in r["error"] for r in receipts))


if __name__ == "__main__":
    unittest.main()
