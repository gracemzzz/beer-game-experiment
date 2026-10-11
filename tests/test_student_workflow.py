"""Offline integration checks for separate calibration and simulation actions.

These tests exercise saved-run reuse and paid-call boundaries; no credentials or
network access are needed. Report rendering has its own tests and is stubbed here.
"""
import asyncio
import copy
import json
import shutil
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from beergame_study import student_study as workflow
from beergame_study.reasoning_protocol import (
    Gateway, MODEL, ORDER_SCHEMA, PROTOCOL, RULE_ANSWERS, RULES_SCHEMA, ReasoningConfig, StudyStopped, digest,
    make_messages, save,
)


class ForbiddenPaidClient:
    def __init__(self):
        self.calls = []
        self.responses = SimpleNamespace(create=self.create)

    def with_options(self, **kwargs):
        return self

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        raise AssertionError("An invalid calibration or offline workflow attempted a paid call.")


class ValidInjectedClient:
    """API-shaped deterministic responses for checking resume accounting only."""
    def __init__(self):
        self.calls = []
        self.responses = SimpleNamespace(create=self.create)

    def with_options(self, **kwargs):
        return self

    async def create(self, **kwargs):
        self.calls.append(copy.deepcopy(kwargs))
        schema = kwargs["text"]["format"]["schema"]
        if schema == RULES_SCHEMA:
            answer = RULE_ANSWERS
        else:
            state = json.loads(kwargs["input"][1]["content"])["current_state"]
            answer = {"order": state["demand"]}
        return {"model": MODEL, "status": "completed", "incomplete_details": None,
                "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(answer)}]}],
                "usage": {"input_tokens": 100, "input_tokens_details": {"cached_tokens": 20},
                          "output_tokens": 220, "output_tokens_details": {"reasoning_tokens": 200}}}


class StudentWorkflowTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(workflow, "ROOT", self.root)
        self.root_patch.start()
        self.report_patch = patch("beergame_study.student_report.build_report", return_value=None)
        self.report_patch.start()
        self.config = replace(ReasoningConfig(), mode="offline", stage="game", weeks=20,
                              groups_per_condition=1, request_interval_s=0, replicate_id="workflow-calibration")

    def tearDown(self):
        self.report_patch.stop()
        self.root_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def records(directory):
        return [(p, json.loads(p.read_text(encoding="utf-8")))
                for p in (directory/"requests").glob("*.json")]

    async def calibration(self):
        return await workflow.run_campaign(self.config, calibration_only=True)

    async def test_calibration_action_stops_before_onboarding_and_games(self):
        events = []
        client = ForbiddenPaidClient()
        directory = await workflow.run_campaign(self.config, client=client, calibration_only=True,
                                                 on_progress=lambda progress: events.append(copy.deepcopy(progress)))
        progress = json.loads((directory/"progress.json").read_text())
        self.assertEqual((progress["stage"], progress["phase"]), ("calibration_complete", "complete"))
        self.assertEqual(progress["groups_complete"], 0)
        self.assertEqual(progress["planned_groups"], 0)
        self.assertEqual(progress["decisions"], 0)
        self.assertFalse((directory/"rounds.csv").exists())
        self.assertFalse((directory/"continuation.csv").exists())
        self.assertFalse((directory/"rules_checks.json").exists())
        records = self.records(directory)
        self.assertEqual(len(records), 144)
        self.assertEqual({r["identity"]["stage"] for _, r in records}, {"calibration"})
        self.assertTrue(all(r["synthetic"] for _, r in records))
        self.assertEqual(len(pd.read_csv(directory/"calibration.csv")), 144)
        self.assertFalse(json.loads((directory/"calibration_recommendation.json").read_text())["manipulation_screen_passed"])
        self.assertTrue(events)
        self.assertEqual(events[-1]["stage"], "calibration_complete")
        self.assertEqual(client.calls, [])

    async def test_separate_games_reuse_calibration_without_duplicating_its_requests(self):
        parent = await self.calibration()
        original = {p.name: p.read_bytes() for p, _ in self.records(parent)}
        config = replace(self.config, replicate_id="workflow-new-games", groups_per_condition=2,
                         weeks=24, budget_usd=12)
        client = ForbiddenPaidClient()
        events = []
        directory = await workflow.run_campaign(config, client=client, calibration_run=parent,
                                                 on_progress=lambda p: events.append(copy.deepcopy(p)))
        self.assertNotEqual(directory, parent)
        progress = json.loads((directory/"progress.json").read_text())
        self.assertEqual((progress["phase"], progress["stage"]), ("complete", "complete"))
        self.assertEqual(progress["groups_complete"], 4)
        rounds = pd.read_csv(directory/"rounds.csv")
        tail = pd.read_csv(directory/"continuation.csv")
        self.assertEqual(len(rounds), 4*4*24)
        self.assertEqual(len(tail), 4*4*12)
        self.assertFalse(rounds.fallback.any())
        self.assertEqual(set(rounds.condition), {"short", "adequate"})
        child_records = self.records(directory)
        self.assertEqual({r["identity"]["stage"] for _, r in child_records}, {"rules", "decision"})
        self.assertEqual(len(child_records), 4*4*(24-4+1))
        self.assertTrue(all(r["synthetic"] for _, r in child_records))
        self.assertEqual({p.name: p.read_bytes() for p, _ in self.records(parent)}, original)
        self.assertIn("games", {p["stage"] for p in events})
        self.assertEqual(client.calls, [])
        # Resuming the same simulation also preserves the request ledger.
        child_before = {p.name: p.read_bytes() for p, _ in child_records}
        again = await workflow.run_campaign(config, client=client, calibration_run=parent)
        self.assertEqual(again, directory)
        self.assertEqual({p.name: p.read_bytes() for p, _ in self.records(directory)}, child_before)

    async def test_invalid_parent_provenance_stops_before_any_new_request(self):
        original = await self.calibration()
        mutations = {
            "incomplete": lambda m, p: p.update(phase="stopped"),
            "protocol": lambda m, p: m.update(protocol="different-protocol"),
            "model": lambda m, p: m["config"].update(model="different-model"),
            "effort": lambda m, p: m["config"].update(effort="none"),
            "caps": lambda m, p: m["config"].update(candidate_caps=[1024, 2048, 4096, 8192]),
            "timeout": lambda m, p: m["config"].update(timeout_s=1),
            "source": lambda m, p: m["source_hashes"].update({"reasoning_protocol.py": "incorrect-hash"}),
            "missing_sources": lambda m, p: m.update(source_hashes={}),
            "prompt": lambda m, p: m["question_template"][0].update(content="Changed fictional participant prompt"),
            "schema": lambda m, p: m.update(order_schema={"type": "object"}),
        }
        for label, mutation in mutations.items():
            with self.subTest(label=label):
                parent = self.root/label
                shutil.copytree(original, parent)
                manifest = json.loads((parent/"manifest.json").read_text())
                progress = json.loads((parent/"progress.json").read_text())
                mutation(manifest, progress)
                save(parent/"manifest.json", manifest)
                save(parent/"progress.json", progress)
                calls = []
                async def forbidden_request(*args, **kwargs):
                    calls.append((args, kwargs))
                    raise AssertionError("Parent validation must precede requests.")
                client = ForbiddenPaidClient()
                with patch.object(workflow.Gateway, "request", new=forbidden_request):
                    with self.assertRaises(StudyStopped):
                        await workflow.run_campaign(replace(self.config, replicate_id="invalid-"+label),
                                                    client=client, calibration_run=parent)
                self.assertEqual(calls, [])
                self.assertEqual(client.calls, [])

    async def test_raw_parent_request_tampering_stops_before_calls(self):
        parent = await self.calibration()
        path, record = self.records(parent)[0]
        record["messages"][0]["content"] = "Different participant instructions"
        save(path, record)
        client = ForbiddenPaidClient()
        with self.assertRaises(StudyStopped):
            await workflow.run_campaign(replace(self.config, replicate_id="tampered-raw"),
                                        client=client, calibration_run=parent)
        self.assertEqual(client.calls, [])

    async def test_completed_api_campaign_resume_keeps_frozen_sample_after_budget_reduction(self):
        config = replace(self.config, mode="api", replicate_id="resume-frozen-sample", budget_usd=3)
        client = ValidInjectedClient()
        directory = await workflow.run_campaign(config, client=client)
        progress = json.loads((directory/"progress.json").read_text())
        self.assertEqual((progress["phase"], progress["groups_complete"]), ("complete", 2))
        selection_path = directory/"selection.json"
        selection_before = selection_path.read_bytes()
        selection = json.loads(selection_before)
        self.assertEqual(selection["groups_per_condition"], 1)
        self.assertGreater(selection["forecast_cost_per_pair_usd"], 0)
        rounds_before = (directory/"rounds.csv").read_bytes()
        tail_before = (directory/"continuation.csv").read_bytes()
        ledger_before = {p.name: p.read_bytes() for p, _ in self.records(directory)}
        calls_before = len(client.calls)
        self.assertEqual(calls_before, 144+2*4*(20-4+1))
        self.assertTrue(all(call["reasoning"] == {"effort": "high"} for call in client.calls))
        # A newly computed sample would have zero affordable pairs. A completed
        # cached campaign must preserve the prospectively frozen sample instead.
        reduced = replace(config, budget_usd=.001)
        self.assertLess(reduced.budget_usd, progress["estimated_charged_or_reserved_usd"])
        self.assertEqual(config.fingerprint(), reduced.fingerprint())
        again = await workflow.run_campaign(reduced, client=client)
        self.assertEqual(again, directory)
        self.assertEqual(len(client.calls), calls_before)
        self.assertEqual(selection_path.read_bytes(), selection_before)
        self.assertEqual((directory/"rounds.csv").read_bytes(), rounds_before)
        self.assertEqual((directory/"continuation.csv").read_bytes(), tail_before)
        self.assertEqual({p.name: p.read_bytes() for p, _ in self.records(directory)}, ledger_before)
        resumed = json.loads((directory/"progress.json").read_text())
        self.assertEqual((resumed["phase"], resumed["groups_complete"], resumed["planned_groups"]), ("complete", 2, 2))
        self.assertEqual(resumed["cached_requests"], calls_before)

    def test_partial_73_record_import_preserves_exact_cache_and_rejection(self):
        config = replace(self.config, mode="api", replicate_id="historical-partial")
        parent = workflow.prepare(config, output_root=self.root/"old")
        bank = workflow.calibration_cases()
        caps = (*config.candidate_caps, config.reference_tokens)
        requests = [(item, cap) for item in range(len(bank)) for cap in caps][:73]
        for index, (item, cap) in enumerate(requests):
            specification = dict(protocol=PROTOCOL, identity=dict(stage="calibration", item=item, cap=cap),
                                 messages=make_messages(bank[item]["state"], []), limit=cap, schema=ORDER_SCHEMA,
                                 requested_model=config.model, reasoning={"effort": config.effort}, mode=config.mode,
                                 config_fingerprint=config.fingerprint())
            key = digest(specification)
            record = dict(specification, request_key=key, requested_effort=config.effort, timeout_s=config.timeout_s,
                          status="ok", charge_usd=.001, synthetic=False, usage_observed=True,
                          response_status="completed", text='{"order":4}', returned_model=config.model,
                          usage={"input_tokens": 1, "output_tokens": 1, "reasoning_tokens": 1})
            if index == 72:
                record.update(status="api_error", http_status=429, error_category="rate_or_quota", fatal_error=True,
                              charge_usd=0, usage_observed=False, response_status=None, text="", usage=None)
            save(parent/"requests"/(key+".json"), record)
        before = {p.name: p.read_bytes() for p, _ in self.records(parent)}
        child = workflow.prepare(config, output_root=self.root/"new", calibration_parent=parent)
        self.assertEqual({p.name: p.read_bytes() for p, _ in self.records(child)}, before)
        self.assertEqual({p.name: p.read_bytes() for p, _ in self.records(parent)}, before)
        gateway = Gateway(child, config, client=ForbiddenPaidClient())
        self.assertAlmostEqual(gateway.charged, .072)
        imported = json.loads((child/"calibration_import.json").read_text())
        self.assertEqual(len(imported["reused_records"]), 73)
        self.assertTrue(imported["originals_unchanged"])
        # Changing a transport/prompt provenance field must invalidate import,
        # even when the old self-reported config fingerprint remains unchanged.
        first, record = self.records(parent)[0]
        record["reasoning"] = {"effort": "none"}
        save(first, record)
        with self.assertRaises(StudyStopped):
            workflow.prepare(config, output_root=self.root/"bad-import", calibration_parent=parent)


if __name__ == "__main__":
    unittest.main()
