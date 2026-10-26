"""Synthetic software checks only; these choices are never study observations."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from beergame_study import manual_batch_v4 as batch
from beergame_study import manual_batch_analysis_v4 as analysis


def synthetic_complete(ident="1" * 32):
    run = batch.Batch("gpt_astra", ident)
    view = run.display()
    while view.get("phase") != "complete":
        decision = view["decision"]
        if decision["phase"].startswith("probe"):
            choices = {p["probe_id"]: 4 for p in decision["hypothetical_independent_decisions"]}
        else:
            choices = {c["chain_id"]: [4, 4, 4, 4] for c in decision["chains"]}
        view = run.submit(choices)
    return run.export()


class BatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = synthetic_complete()

    def test_full_physical_and_trace_replay(self):
        rows = batch.audit(self.payload)
        self.assertEqual(len(self.payload["trace"]), 100)
        self.assertEqual([r["weeks"] for r in rows], [24] * 3)
        self.assertTrue(all(r["probe_complete"] for r in rows))
        self.assertEqual({r["pipeline_sensitivity"] for r in rows}, {0})
        self.assertEqual(len(batch.CONTROL.split()), len(batch.EDUCATION.split()))

    def test_tampering_and_missing_trace_rejected(self):
        for mutate in (lambda p: p["trace"].pop(),
                       lambda p: p["games"]["B"]["final_orders"][0].__setitem__(0, [9, 9, 9, 9]),
                       lambda p: p.__setitem__("complete", False),
                       lambda p: p.__setitem__("source_hashes", {})):
            value = copy.deepcopy(self.payload)
            mutate(value)
            with self.assertRaises((ValueError, IndexError)):
                batch.audit(value)

    def test_partial_preserved_and_not_filled(self):
        run = batch.Batch("gpt_sol", "2" * 32)
        view = run.display()
        run.submit({c["chain_id"]: [0] * 4 for c in view["decision"]["chains"]})
        with self.assertRaises(ValueError):
            run.export()
        rows = batch.audit(run.export(require_complete=False))
        self.assertFalse(any(r["complete"] for r in rows))

    def test_transcript_gate_duplicate_and_raw_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data, transcript = root / "received.json", root / "transcript.txt"
            data.write_text(json.dumps(self.payload))
            original = data.read_bytes()
            transcript.write_text("SYNTHETIC SOFTWARE TEST transcript placeholder; not model evidence")
            kwargs = dict(website_label="synthetic software control", reasoning_setting="not applicable")
            r = analysis.intake(root, data, **kwargs)
            self.assertFalse(r["eligible"])
            self.assertEqual(analysis.collect(root)[1], [])
            kwargs.update(transcript_path=transcript, reviewed=True, fresh_chat_confirmed=True,
                          reviewer="unit test", note="Synthetic test of gate mechanics only")
            r = analysis.intake(root, data, **kwargs)
            self.assertTrue(r["eligible"])
            self.assertEqual(len(analysis.collect(root)[1]), 1)
            self.assertEqual(data.read_bytes(), original)
            analysis.intake(root, data, **dict(kwargs, note="Duplicate receipt test"))
            with self.assertRaises(ValueError):
                analysis.collect(root)

    def test_power_assumptions_not_results(self):
        self.assertAlmostEqual(float(analysis.power(40, 0)), .05 / 20, places=10)
        self.assertGreater(float(analysis.power(100, .5)), float(analysis.power(10, .5)))

    def test_analysis_does_not_inflate_chain_sample_size(self):
        second = synthetic_complete("3" * 32)
        receipts = [dict(model="gpt_astra", batch_id=p["batch_id"], source_sha256=str(i),
                         outcomes=batch.audit(p)) for i, p in enumerate((self.payload, second))]
        with tempfile.TemporaryDirectory() as folder, patch.object(analysis, "verify_manifest"), patch.object(analysis, "collect", return_value=(receipts, receipts)):
            result = analysis.analyze(folder, Path(folder) / "report")
            self.assertEqual(result["eligible_fresh_chat_batches"]["gpt_astra"], 2)
            prefix1 = [r for r in result["observations"] if r["prefix_chats"] == 1]
            self.assertTrue(all(r["p_two_sided"] is None for r in prefix1))
            prefix2 = [r for r in result["observations"] if r["prefix_chats"] == 2]
            self.assertTrue(all(r["n_pairs"] == 2 and r["chains_per_condition"] == 20 for r in prefix2))
            self.assertFalse(result["primary_sample_complete"])
            self.assertTrue((Path(folder) / "report/OBSERVED_H1_H4_SWEEP.png").is_file())


if __name__ == "__main__":
    unittest.main()
