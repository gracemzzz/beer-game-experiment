"""Temporary synthetic intake controls; no website/API observations are created."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import manual_weekly_v3 as controller
from beergame_study import manual_workflow_v3 as workflow


class ManualWorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.experiment = self.root / "experiments/13_weekly_state_api_20261021"
        protocol = self.experiment / "hypotheses/MANUAL_V3_20261025.md"
        protocol.parent.mkdir(parents=True)
        protocol.write_bytes((ROOT / "experiments/13_weekly_state_api_20261021/hypotheses/MANUAL_V3_20261025.md").read_bytes())
        self.ledger = self.experiment.parent / "12_pressure_framing_api_20261020/data/api_budget.json"
        self.ledger.parent.mkdir(parents=True)
        self.ledger.write_text(json.dumps(dict(cap_usd=5., attempts={"original_paid_campaign":
            dict(charge_usd=1.179072025, reserve_usd=1.179072025, status="received")})), encoding="utf-8")
        self.ledger_before = self.ledger.read_bytes()
        self.no_http = patch("httpx.Client", side_effect=AssertionError("Manual collection cannot make API calls"))
        self.no_http.start()
        self.addCleanup(self.no_http.stop)
        self.no_async_http = patch("httpx.AsyncClient", side_effect=AssertionError("Manual collection cannot make API calls"))
        self.no_async_http.start()
        self.addCleanup(self.no_async_http.stop)
        self.addCleanup(lambda: self.assertEqual(self.ledger.read_bytes(), self.ledger_before))

    def prepare(self, blocks=1):
        self.run = workflow.prepare(self.experiment, blocks=blocks, chains=1)
        self.manifest = workflow.load_manifest(self.run)
        return self.run

    def synthetic_export(self, case_id="MW3_B001_B", weeks=24, probes=True):
        """All-zero software fixture, never a model-generated student trajectory."""
        case = next(c for c in self.manifest["cases"] if c["case_id"] == case_id)
        config = {key: case[key] for key in ("case_id", "arm", "replicate", "chains", "seed")}
        game = controller.WebsiteGame(**config, study_id=self.manifest["study_id"],
            provider="synthetic_software_fixture", model="SYNTHETIC_NOT_A_MODEL_OBSERVATION",
            reasoning_setting="not applicable: software-generated choices")
        for _ in range(weeks):
            game.display()
            choices = {cid: [0, 0, 0, 0] for cid in game.chain_ids}
            game.submit_initial(choices)
            if case["arm"] == "A":
                game.display()
                game.submit_revision(choices)
        if weeks == 24 and probes:
            display = game.display()
            choices = {state["probe_id"]: 0 for state in display["hypothetical_independent_decisions"]}
            game.submit_probe_initial(choices)
            if case["arm"] == "A":
                game.display()
                game.submit_probe_revision(choices)
        source = self.root / (case_id + ".json")
        source.write_text(json.dumps(game.export(require_complete=False), allow_nan=False), encoding="utf-8")
        transcript = self.root / (case_id + "_SYNTHETIC_TRANSCRIPT.txt")
        transcript.write_text("SYNTHETIC SOFTWARE TEST ONLY. No model made these choices. "
            "This temporary text exercises transcript intake, not authenticity or student fidelity.", encoding="utf-8")
        return source, transcript

    def intake(self, source, transcript, *, reviewed=False, **kwargs):
        values = dict(model_slot="gpt_flagship", website_label="Synthetic website label for software test",
                      reasoning_setting="Synthetic selected setting", transcript_reviewed=reviewed,
                      reviewer="Synthetic test reviewer" if reviewed else "",
                      review_note="Explicit temporary review-branch test; not real model evidence" if reviewed else "")
        values.update(kwargs)
        return workflow.intake(self.run, source, transcript, **values)

    def test_default_plan_has_123_prompts_and_exact_controller_source(self):
        self.prepare(blocks=40)
        cases = self.manifest["cases"]
        self.assertEqual(len(cases), 123)
        self.assertEqual(sum(c["collection_kind"] == "development" for c in cases), 3)
        self.assertEqual(sum(c["collection_kind"] == "heldout" for c in cases), 120)
        directory = self.experiment / "prompts" / self.run.name
        for case in cases:
            self.assertEqual((directory / case["prompt_file"]).read_text(encoding="utf-8"), workflow.prompt_for(self.manifest, case))
        self.assertEqual((directory / "beergame_controller.py").read_bytes(), Path(controller.__file__).read_bytes())
        self.assertEqual(self.manifest["api_requests"], 0)
        before = (self.run / "manifest.json").read_bytes()
        self.assertEqual(workflow.prepare(self.experiment, blocks=40, chains=1), self.run)
        self.assertEqual((self.run / "manifest.json").read_bytes(), before)

    def test_tampered_prompt_controller_or_protocol_snapshot_is_rejected(self):
        self.prepare()
        directory = self.experiment / "prompts" / self.run.name
        targets = [directory / self.manifest["cases"][0]["prompt_file"],
                   directory / "beergame_controller.py",
                   self.run / "source_snapshot/MANUAL_V3_20261025.md"]
        for target in targets:
            original = target.read_bytes()
            target.write_bytes(original + b"\nSYNTHETIC TAMPER TEST\n")
            try:
                with self.subTest(target=target.name):
                    with self.assertRaises(ValueError):
                        workflow.load_manifest(self.run)
            finally:
                target.write_bytes(original)

    def test_zero_orders_and_partial_exports_replay_but_need_explicit_transcript_review(self):
        self.prepare()
        source, transcript = self.synthetic_export()
        receipt = self.intake(source, transcript)
        self.assertTrue(receipt["replay_passed"])
        self.assertFalse(receipt["eligible_for_heldout"])
        self.assertEqual(receipt["outcome"]["game_zero_order_fraction"], 1)
        self.assertFalse(receipt["provider_api_identity_verified"])
        _, eligible = workflow.collect(self.run)
        self.assertEqual(eligible, [])
        partial, partial_transcript = self.synthetic_export("MW3_B001_C", weeks=3, probes=False)
        reviewed = self.intake(partial, partial_transcript, reviewed=True)
        self.assertTrue(reviewed["replay_passed"])
        self.assertFalse(reviewed["outcome"]["complete"])
        self.assertEqual(reviewed["outcome"]["weeks"], 3)
        self.assertIsNone(reviewed["outcome"]["chain_total_cost"])
        self.assertIsNone(reviewed["outcome"]["pipeline_sensitivity"])
        output, result, _ = workflow.analyze(self.run)
        self.assertEqual(result["complete_game_cluster_arm_rows"], 0)
        self.assertTrue(all(row["n_pairs"] == 0 for row in result["primary"]))
        self.assertTrue((output / "REPORT.md").is_file())

    def test_missing_empty_or_reused_json_as_transcript_is_rejected(self):
        self.prepare()
        source, transcript = self.synthetic_export()
        empty = self.root / "empty.txt"
        empty.write_bytes(b"")
        for bad in (self.root / "not_found.txt", empty, source):
            with self.subTest(path=bad.name):
                with self.assertRaises(ValueError):
                    self.intake(source, bad, reviewed=True)
        with self.assertRaises(ValueError):
            self.intake(source, transcript, reviewed=True, reviewer="")

    def test_pilot_never_enters_heldout_even_after_review_and_case_hashes_are_bound(self):
        self.prepare()
        source, transcript = self.synthetic_export("MW3_PILOT_A")
        pilot = self.intake(source, transcript, reviewed=True)
        self.assertTrue(pilot["replay_passed"])
        self.assertFalse(pilot["eligible_for_heldout"])
        payload = json.loads(source.read_text(encoding="utf-8"))
        payload["controller_source_sha256"] = "wrong source"
        bad = self.root / "bad_source.json"
        bad.write_text(json.dumps(payload), encoding="utf-8")
        rejected = self.intake(bad, transcript)
        self.assertFalse(rejected["replay_passed"])
        self.assertFalse(rejected["eligible_for_heldout"])
        self.assertEqual(workflow.collect(self.run)[1], [])

    def test_identical_reimport_is_idempotent_and_new_duplicate_never_counts_twice(self):
        self.prepare()
        source, transcript = self.synthetic_export()
        receipt = self.intake(source, transcript, reviewed=True)
        self.assertEqual(self.intake(source, transcript, reviewed=True), receipt)
        self.assertEqual(len(workflow.collect(self.run)[1]), 1)
        alternative = self.root / "another_SYNTHETIC_transcript.txt"
        alternative.write_text("A different synthetic transcript attempt for the same frozen case.", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.intake(source, alternative, reviewed=True)
            workflow.collect(self.run)

    def test_one_response_cannot_be_counted_as_two_different_models(self):
        self.prepare()
        source, transcript = self.synthetic_export()
        self.intake(source, transcript, reviewed=True)
        with self.assertRaises(ValueError):
            self.intake(source, transcript, reviewed=True, model_slot="claude", website_label="Another synthetic model")
            workflow.collect(self.run)

    def test_mixed_website_settings_in_one_model_slot_are_rejected(self):
        self.prepare()
        a, ta = self.synthetic_export("MW3_B001_A")
        b, tb = self.synthetic_export("MW3_B001_B")
        self.intake(a, ta, reviewed=True)
        with self.assertRaises(ValueError):
            self.intake(b, tb, reviewed=True, reasoning_setting="Different synthetic setting")
            workflow.collect(self.run)

    def test_receipt_flag_cannot_promote_unreviewed_or_pilot_evidence(self):
        self.prepare()
        source, transcript = self.synthetic_export()
        receipt = self.intake(source, transcript)
        path = self.run / "intake" / receipt["intake_id"] / "receipt.json"
        forged = json.loads(path.read_text(encoding="utf-8"))
        forged["eligible_for_heldout"] = True
        path.write_text(json.dumps(forged), encoding="utf-8")
        with self.assertRaises(ValueError):
            workflow.collect(self.run)


if __name__ == "__main__":
    unittest.main()
