"""Report scope and provenance checks; no API calls or persistent run writes."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from beergame_study.student_report import build_report


class StudentReportTests(unittest.TestCase):
    @staticmethod
    def save(directory, name, value):
        (directory / name).write_text(json.dumps(value), encoding="utf-8")

    @staticmethod
    def build(directory):
        with patch("beergame_study.student_report._plots", return_value=[]), \
             patch("beergame_study.student_report._workbook"), \
             patch("beergame_study.student_report._docx"):
            build_report(directory)
        return json.loads((directory / "report_summary.json").read_text(encoding="utf-8"))

    def test_completed_calibration_is_not_a_completed_game_study(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.save(directory, "manifest.json", dict(calibration_only=True, execution_scope="calibration",
                      config=dict(mode="api", model="test-model", effort="high", groups_per_condition=3)))
            self.save(directory, "progress.json", dict(phase="complete", stage="calibration_complete", calibration_only=True))
            self.save(directory, "calibration_recommendation.json", dict(manipulation_screen_passed=True,
                      complete_matched_batch=True, screen_rows=[dict(limit=8192, n=24, completion_rate=1)]))
            self.save(directory, "selection.json", dict(short_tokens=8192, adequate_tokens=16384, groups_per_condition=3))
            summary = self.build(directory)
            self.assertEqual(summary["expected_chains"], 0)
            self.assertEqual(summary["completed_chains"], 0)
            self.assertTrue(summary["calibration_completed"])
            self.assertTrue(summary["calibration_passed"])
            self.assertFalse(summary["clean_behavior_study"])
            text = (directory / "REPORT.md").read_text(encoding="utf-8")
            self.assertIn("Calibration-only run completed", text)
            self.assertIn("No games were requested", text)
            self.assertNotIn("All planned games and continuation weeks completed", text)

    def test_reused_api_calibration_keeps_parent_cost_out_of_local_ledger(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.save(directory, "manifest.json", dict(execution_scope="game",
                      config=dict(mode="api", model="test-model", effort="high", groups_per_condition=3)))
            self.save(directory, "progress.json", dict(phase="stopped", stage="onboarding", reason="test stop"))
            self.save(directory, "calibration_recommendation.json", dict(manipulation_screen_passed=True,
                      screen_rows=[dict(limit=8192, n=24, completion_rate=1)]))
            self.save(directory, "selection.json", dict(short_tokens=8192, adequate_tokens=16384, groups_per_condition=1))
            self.save(directory, "calibration_reuse.json", dict(parent="preserved-parent", source_mode="api",
                      requested_model="test-model", effort="high", returned_models=["test-model"],
                      original_calibration_estimated_usd=1.25, local_budget_includes_parent_charges=False,
                      request_files=[dict(path="parent/requests/example.json", sha256="example")]))
            pd.DataFrame([dict(cap=8192, synthetic=False, valid_decision=True, usage_observed=True,
                               output_tokens=5000, reasoning_tokens=4990)]).to_csv(directory / "calibration.csv", index=False)
            summary = self.build(directory)
            self.assertTrue(summary["calibration_reused"])
            self.assertFalse(summary["calibration_synthetic"])
            self.assertEqual(summary["expected_chains"], 2)
            self.assertEqual(summary["saved_requests"], 0)
            self.assertEqual(summary["returned_models"], [])
            self.assertEqual(summary["calibration_returned_models"], ["test-model"])
            self.assertEqual(summary["estimated_charged_or_reserved_usd"], 0)
            self.assertEqual(summary["prior_calibration_estimated_usd"], 1.25)
            self.assertEqual(summary["estimated_total_including_prior_calibration_usd"], 1.25)
            text = (directory / "REPORT.md").read_text(encoding="utf-8")
            self.assertIn("no local API responses yet", text)
            self.assertIn("Parent charges are excluded", text)

    def test_synthetic_reused_calibration_cannot_validate_live_treatment(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.save(directory, "manifest.json", dict(execution_scope="game", config=dict(mode="api")))
            self.save(directory, "progress.json", dict(phase="complete"))
            self.save(directory, "calibration_recommendation.json", dict(manipulation_screen_passed=True))
            self.save(directory, "calibration_reuse.json", dict(parent="synthetic-parent", source_mode="offline"))
            self.save(directory, "selection.json", dict(groups_per_condition=0))
            summary = self.build(directory)
            self.assertTrue(summary["calibration_synthetic"])
            self.assertFalse(summary["calibration_passed"])
            self.assertFalse(summary["clean_behavior_study"])
            self.assertEqual(summary["expected_chains"], 0)

    def test_corrected_calibration_excludes_old_evidence_and_retains_its_charge(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.save(directory, "manifest.json", dict(calibration_state_correction=True,
                      calibration_only=True, config=dict(mode="api", model="test-model", effort="high")))
            self.save(directory, "progress.json", dict(phase="complete", stage="calibration_complete"))
            self.save(directory, "calibration_import.json", dict(correction=dict(
                fields=["received", "shipped"], changed_items=[0, 2, 6, 8, 12, 14, 18, 20],
                excluded_request_files=["old.json"], reused_request_files=["unchanged.json"],
                reason="Post-shipment placeholders corrected.")))
            self.save(directory, "calibration_recommendation.json", dict(manipulation_screen_passed=False,
                      screen_rows=[dict(limit=8192, n=1, completion_rate=1)]))
            request_directory = directory / "requests"
            request_directory.mkdir()
            for name, charge, item in (("old.json", .25, 0), ("unchanged.json", .50, 1),
                                       ("corrected.json", .75, 0)):
                self.save(request_directory, name, dict(identity=dict(stage="calibration", item=item),
                    status="ok", response_status="completed", text='{"order": 8}', returned_model="test-model",
                    usage_observed=True, usage=dict(input_tokens=10, output_tokens=100,
                        output_tokens_details=dict(reasoning_tokens=90)), charge_usd=charge))
            pd.DataFrame([dict(item=0, cap=8192, synthetic=False, valid_decision=True,
                               usage_observed=True, output_tokens=100, reasoning_tokens=90)]).to_csv(
                                   directory / "calibration.csv", index=False)
            summary = self.build(directory)
            self.assertTrue(summary["calibration_state_corrected"])
            self.assertEqual(summary["calibration_import_excluded_files"], 1)
            self.assertEqual(summary["calibration_import_reused_files"], 1)
            self.assertEqual(summary["excluded_measured_calibration_responses"], 1)
            self.assertEqual(summary["excluded_calibration_charge_or_reservation_usd"], .25)
            self.assertEqual(summary["estimated_charged_or_reserved_usd"], 1.5)
            self.assertEqual(summary["calibration_screen_observations"], 1)
            self.assertEqual(summary["saved_requests"], 3)
            index = pd.read_csv(directory / "request_index.csv").set_index("request_file")
            self.assertTrue(index.loc["old.json", "excluded_from_corrected_calibration"])
            self.assertFalse(index.loc["corrected.json", "excluded_from_corrected_calibration"])
            self.assertTrue(index.loc["unchanged.json", "imported_compatible_calibration"])
            text = (directory / "REPORT.md").read_text(encoding="utf-8")
            self.assertIn("corrected before game outcomes", text)
            self.assertIn("not observations in calibration.csv", text)
            self.assertIn("remain included in the local campaign ledger", text)


if __name__ == "__main__":
    unittest.main()
