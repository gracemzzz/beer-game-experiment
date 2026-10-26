"""Synthetic software checks for larger paged batches. Never research data."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from beergame_study import manual_batch_v5 as batch
from beergame_study import manual_batch_analysis_v5 as analysis


def synthetic_complete(ident="1" * 32):
    run = batch.Batch("gpt_astra", ident)
    view = run.display()
    largest_display = 0
    while view.get("phase") != "complete":
        largest_display = max(largest_display, len(json.dumps(view, separators=(",", ":")).encode()))
        d = view["decision"]
        if d["phase"].startswith("probe"):
            choices = {pid: 4 for pid in d["requested_ids"]}
        else:
            choices = {cid: [4, 4, 4, 4] for cid in d["requested_ids"]}
        view = run.submit(choices)
    return run.export(), largest_display


class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload, cls.largest_display = synthetic_complete()

    def test_full_50_chain_replay_and_bounded_pages(self):
        rows = batch.audit(self.payload)
        self.assertEqual(len(self.payload["page_events"]), 224)
        self.assertEqual(len(self.payload["trace"]), 100)
        self.assertEqual([r["chains_in_cluster"] for r in rows], [50] * 3)
        self.assertTrue(all(r["probe_complete"] and r["weeks"] == 24 for r in rows))
        self.assertLess(self.largest_display, 20000)
        self.assertEqual(len(batch.CONTROL.split()), len(batch.EDUCATION.split()))

    def test_partial_page_survives_replay_and_never_advances_week(self):
        run = batch.Batch("gpt_luna", "2" * 32)
        d = run.display()["decision"]
        run.submit({cid: [0] * 4 for cid in d["requested_ids"]})
        partial = run.export(require_complete=False)
        self.assertEqual(partial["page_offset"], 25)
        self.assertEqual(len(partial["pending_page_choices"]), 25)
        rows = batch.audit(partial)
        self.assertTrue(all(r["weeks"] == 0 for r in rows))
        with self.assertRaises(ValueError):
            run.export()

    def test_rejects_missing_other_page_and_boolean_choices(self):
        run = batch.Batch("gpt_sol", "4" * 32)
        d = run.display()["decision"]
        choices = {cid: [4] * 4 for cid in d["requested_ids"]}
        for value in ({}, dict(choices, c050=[4] * 4), dict(choices, **{d["requested_ids"][0]: [True, 4, 4, 4]})):
            with self.assertRaises(ValueError):
                run.submit(value)
        self.assertEqual(run.page_events, [])

    def test_tampering_and_wrong_version_rejected(self):
        for mutate in (lambda p: p["page_events"].pop(),
                       lambda p: p["page_events"][0]["choices"].__setitem__("c001", [9] * 4),
                       lambda p: p.__setitem__("complete", False),
                       lambda p: p.__setitem__("schema_version", "manual-three-condition-batch-v4")):
            value = copy.deepcopy(self.payload)
            mutate(value)
            with self.assertRaises((ValueError, KeyError, IndexError)):
                batch.audit(value)

    def test_chain_extraction_reconciles_to_cluster_outcomes(self):
        rows = batch.audit(self.payload)
        chain_rows = analysis.chain_metrics(self.payload)
        prefixes = analysis.chain_prefix_summary(chain_rows)
        self.assertEqual(len(chain_rows), 150)
        self.assertEqual(len(prefixes), 3 * len(analysis.CHAIN_PREFIXES))
        for row in rows:
            aggregate = prefixes[(prefixes.arm == row["arm"]) & (prefixes.chains_per_condition == 50)].iloc[0]
            for name in ("pipeline_sensitivity", "chain_total_cost", "mean_role_order_variance", "mean_role_bullwhip"):
                self.assertAlmostEqual(aggregate[name], row[name])
        self.assertNotIn("p_two_sided", prefixes.columns)

    def test_intake_review_gate_and_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, transcript = root / "response.json", root / "transcript.txt"
            source.write_text(json.dumps(self.payload))
            transcript.write_text("SYNTHETIC TEST ONLY; no real model transcript")
            kwargs = dict(website_label="synthetic software control", reasoning_setting="not applicable")
            first = analysis.intake(root, source, **kwargs)
            self.assertFalse(first["eligible"])
            self.assertEqual(analysis.collect(root)[1], [])
            kwargs.update(transcript_path=transcript, reviewed=True, fresh_chat_confirmed=True,
                          reviewer="unit test", note="Test gate mechanics, not observations")
            second = analysis.intake(root, source, **kwargs)
            self.assertEqual(first["attempt_order"], second["attempt_order"])
            self.assertEqual(len(analysis.collect(root)[1]), 1)
            analysis.intake(root, source, **dict(kwargs, note="Duplicate review"))
            with self.assertRaises(ValueError):
                analysis.collect(root)

    def test_one_chat_is_not_50_independent_observations(self):
        receipt = dict(model="gpt_astra", batch_id=self.payload["batch_id"], source_sha256="synthetic",
                       attempt_order=1, outcomes=batch.audit(self.payload))
        with tempfile.TemporaryDirectory() as folder, patch.object(analysis, "verify_manifest"), patch.object(analysis, "collect", return_value=([receipt], [receipt])):
            result = analysis.analyze(folder, Path(folder) / "report")
            self.assertEqual(result["eligible_fresh_chat_batches"]["gpt_astra"], 1)
            self.assertTrue(all(r["n_pairs"] == 1 and r["chains_per_condition"] == 50 for r in result["observations"]))
            self.assertTrue(all(r["p_holm_20"] is None and r["ci95_low"] is None for r in result["observations"]))
            self.assertFalse((Path(folder) / "report/OBSERVED_ADJUSTED_P_VALUES.png").exists())

    def test_p_plot_and_prefix_mean_plots_accept_actual_summary_shape(self):
        import pandas as pd
        table = pd.DataFrame([dict(model="gpt_astra", hypothesis=h[0], chains_per_condition=n * 50,
                                   p_holm_20=p) for h in analysis.ENDPOINTS for n, p in ((2, 1), (20, .000001))])
        with tempfile.TemporaryDirectory() as folder:
            analysis.plot_p_values(table, folder)
            prefixes = analysis.chain_prefix_summary(analysis.chain_metrics(self.payload))
            analysis.plot_chain_prefixes(prefixes, folder)
            self.assertTrue((Path(folder) / "OBSERVED_ADJUSTED_P_VALUES.png").is_file())
            self.assertTrue((Path(folder) / "WITHIN_RESPONSE_SIZE_gpt_astra.png").is_file())

    def test_planning_power_is_per_chat_and_report_history_is_preserved(self):
        self.assertAlmostEqual(float(analysis.power(40, 0)), .05 / 20, places=10)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            old = b'Original publication bytes\r\n'
            (path / "REPORT.md").write_bytes(old)
            (path / "RESULTS.json").write_text(json.dumps(dict(evidence_id="old")))
            analysis.preserve_previous_report(path, "new")
            self.assertEqual((path / "history/old/REPORT.md").read_bytes(), old)


if __name__ == "__main__":
    unittest.main()
