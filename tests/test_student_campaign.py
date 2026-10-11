"""End-to-end scientific provenance and physical invariants; never paid calls."""
import asyncio
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from beergame_study import student_study
from beergame_study.game import ROLES
from beergame_study.reasoning_protocol import COMMON, MODEL, TASK, Gateway, ReasoningConfig, save


class ForbiddenClient:
    """Fail immediately if an offline campaign attempts API generation."""

    def __init__(self):
        self.calls = []
        self.responses = self

    def with_options(self, **options):
        return self

    async def create(self, **request):
        self.calls.append(request)
        raise AssertionError("An offline campaign must never call an API.")


class StudentCampaignTests(unittest.TestCase):
    def assert_physical_trajectory(self, rounds, tail):
        trajectory = pd.concat([rounds, tail], ignore_index=True)
        for (_, _), data in trajectory.groupby(["group_id", "role"]):
            data = data.sort_values("week")
            self.assertEqual(data.week.tolist(), list(range(1, 33)))
            prior_inventory, prior_backlog, prior_supply, prior_order = 12, 0, 12, 0
            for row in data.itertuples(index=False):
                self.assertEqual(row.inventory, prior_inventory + row.received - row.shipped)
                self.assertEqual(row.backlog, prior_backlog + row.demand - row.shipped)
                self.assertEqual(row.supply_line, prior_supply + prior_order - row.received)
                self.assertAlmostEqual(row.cost, 0.5 * row.inventory + row.backlog)
                self.assertGreaterEqual(row.inventory, 0)
                self.assertGreaterEqual(row.backlog, 0)
                self.assertGreaterEqual(row.supply_line, 0)
                prior_inventory, prior_backlog = row.inventory, row.backlog
                prior_supply, prior_order = row.supply_line, row.order

    def test_offline_complete_game_provenance_reports_and_cached_resume(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                client = ForbiddenClient()
                config = replace(ReasoningConfig(), weeks=20, groups_per_condition=1,
                                 request_interval_s=0)
                with patch.object(student_study, "ROOT", root):
                    directory = await student_study.run_campaign(config, client=client,
                                                                output_root=root / "runs")
                    rounds = pd.read_csv(directory / "rounds.csv")
                    tail = pd.read_csv(directory / "continuation.csv")
                    self.assertEqual(len(rounds), 2 * 4 * 20)
                    self.assertEqual(len(tail), 2 * 4 * 12)
                    self.assertEqual(set(rounds.condition), {"short", "adequate"})
                    self.assertEqual(set(rounds.role), set(ROLES))
                    self.assertEqual((rounds.phase == "agent").sum(), 2 * 4 * 16)
                    self.assertEqual(rounds.fallback.sum(), 0)
                    self.assertEqual(rounds.order.tolist(), rounds.demand.tolist())
                    self.assert_physical_trajectory(rounds, tail)
                    recommendation = json.loads((directory / "calibration_recommendation.json").read_text())
                    self.assertFalse(recommendation["manipulation_screen_passed"])
                    selection = json.loads((directory / "selection.json").read_text())
                    self.assertFalse(selection["calibration_passed"])
                    progress = json.loads((directory / "progress.json").read_text())
                    self.assertEqual(progress["phase"], "complete")
                    self.assertEqual(progress["groups_complete"], 2)
                    self.assertEqual(progress["fallback_decisions"], 0)
                    report = (directory / "REPORT.md").read_text(encoding="utf-8")
                    self.assertIn("SYNTHETIC", report)
                    for name in ("REPORT.docx", "DETAILS.xlsx"):
                        self.assertTrue((directory / name).is_file(), name)
                    self.assertTrue((root / "reports" / "LATEST_REPORT.txt").is_file())
                    requests = {p.name: p.read_bytes() for p in (directory / "requests").glob("*.json")}
                    expected = 24 * (len(config.candidate_caps) + 1) + 8 + 128
                    self.assertEqual(len(requests), expected)
                    decision_records = []
                    for raw in requests.values():
                        record = json.loads(raw)
                        self.assertTrue(record["synthetic"])
                        self.assertFalse(record["usage_observed"])
                        self.assertEqual(record["requested_model"], MODEL)
                        self.assertEqual(record["requested_effort"], "high")
                        self.assertEqual(record["reasoning"], {"effort": "high"})
                        self.assertEqual(record["messages"][0]["content"], COMMON)
                        if record["identity"]["stage"] == "decision":
                            decision_records.append(record)
                            prompt = json.loads(record["messages"][1]["content"])
                            self.assertEqual(prompt["task"], TASK)
                            state = prompt["current_state"]
                            self.assertEqual(state["week"], record["identity"]["week"])
                            self.assertEqual(state["role"], record["identity"]["role"])
                            self.assertEqual(len(prompt["past_rounds"]), state["week"] - 1)
                    self.assertEqual(len(decision_records), 128)
                    resumed = await student_study.run_campaign(replace(config, budget_usd=12),
                                                              client=client, output_root=root / "runs")
                    self.assertEqual(directory, resumed)
                    self.assertEqual(requests, {p.name: p.read_bytes() for p in (directory / "requests").glob("*.json")})
                    self.assertEqual(client.calls, [])
        asyncio.run(check())

    def test_missed_decision_carries_last_valid_order_and_preserves_full_game(self):
        original_request = Gateway.request
        injected = []

        async def interrupted_request(gateway, identity, messages, limit, *args, **kwargs):
            record = await original_request(gateway, identity, messages, limit, *args, **kwargs)
            if (identity.get("stage") == "decision" and identity.get("group") == "b000_short"
                    and identity.get("role") == "retailer" and identity.get("week") == 8):
                # Preserve a usable-looking partial answer to prove incomplete
                # responses cannot silently become a chosen behavioral order.
                record = dict(record, response_status="incomplete", incomplete_reason="max_output_tokens",
                              text='{"order":31337}')
                save(gateway.cache / (record["request_key"] + ".json"), record)
                injected.append(record["request_key"])
            return record

        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                config = replace(ReasoningConfig(), weeks=20, groups_per_condition=1,
                                 candidate_caps=(512, 1024), request_interval_s=0)
                with patch.object(student_study, "ROOT", root), patch.object(Gateway, "request", interrupted_request):
                    directory = await student_study.run_campaign(config, output_root=root / "runs")
                rounds = pd.read_csv(directory / "rounds.csv")
                tail = pd.read_csv(directory / "continuation.csv")
                short_retailer = rounds[(rounds.group_id == "b000_short") & (rounds.role == "retailer")]
                prior = short_retailer[short_retailer.week == 7].iloc[0]
                missed = short_retailer[short_retailer.week == 8].iloc[0]
                self.assertEqual(len(injected), 1)
                self.assertEqual(rounds.fallback.sum(), 1)
                self.assertEqual(missed.order, prior.order)
                self.assertNotEqual(missed.order, 31337)
                self.assertFalse(missed.valid_decision)
                self.assertEqual(missed.failure_reason, "truncated")
                self.assertEqual(len(rounds), 160)
                self.assertEqual(len(tail), 96)
                self.assert_physical_trajectory(rounds, tail)
                progress = json.loads((directory / "progress.json").read_text())
                self.assertEqual(progress["phase"], "complete")
                self.assertEqual(progress["groups_complete"], 2)
                self.assertEqual(progress["fallback_decisions"], 1)
                # The next prompt makes the executed continuation observable,
                # rather than representing the failed partial reply as an order.
                records = [json.loads(p.read_text(encoding="utf-8")) for p in (directory / "requests").glob("*.json")]
                following = next(r for r in records if r["identity"].get("stage") == "decision"
                                 and r["identity"].get("group") == "b000_short"
                                 and r["identity"].get("role") == "retailer"
                                 and r["identity"].get("week") == 9)
                history = json.loads(following["messages"][1]["content"])["past_rounds"]
                self.assertTrue(history[-1]["fallback"])
                self.assertEqual(history[-1]["order"], missed.order)
                report = (directory / "REPORT.md").read_text(encoding="utf-8")
                self.assertIn("fallback", report.lower())
                self.assertIn("SYNTHETIC", report)
                self.assertEqual(len(records), 24 * 3 + 8 + 128)
        asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
