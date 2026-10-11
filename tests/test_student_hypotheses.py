"""Offline checks for chain-level hypotheses and read-only saved-run analysis."""
import asyncio
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from beergame_study import student_study
from beergame_study.reasoning_protocol import ReasoningConfig, ORDER_SCHEMA, PROTOCOL, digest, make_messages, price
from beergame_study.student_hypotheses import (AnalysisError, analyze_run, hypothesis_table,
                                             inference_results, paired_contrasts, signflip, SHARED_CHECKS,
                                             _records, _reconcile_response, _token_use)


def all_gates():
    return {name: True for name, _ in SHARED_CHECKS}


def group_fixture(n=8, beta_usable=True):
    rows = []
    for block in range(n):
        for condition in ("short", "adequate"):
            rows.append(dict(group_id=f"b{block:03d}_{condition}", block=block, condition=condition,
                             usable_role_betas=4 if beta_usable else 0,
                             group_beta=.2 if condition == "short" else .8,
                             total_scored_cost=101. if condition == "short" else 100.))
    return pd.DataFrame(rows)


@contextmanager
def changed(path, contents):
    original = path.read_bytes() if path.exists() else None
    path.write_bytes(contents)
    try:
        yield
    finally:
        if original is None:
            path.unlink()
        else:
            path.write_bytes(original)


class HypothesisInferenceTests(unittest.TestCase):
    def test_exact_signflip_known_extreme_and_zero_samples(self):
        self.assertEqual(signflip(np.ones(8)), 2/256)
        self.assertEqual(signflip(np.zeros(8)), 1)
        self.assertEqual(signflip([1, 1]), .5)
        for invalid in ([], [1, np.nan], [[1, 2]]):
            with self.assertRaises(ValueError):
                signflip(invalid)

    def test_h2_can_test_without_any_usable_beta_and_retains_holm_family(self):
        hypotheses = hypothesis_table(group_fixture(beta_usable=False), 8, all_gates()).set_index("hypothesis")
        self.assertFalse(hypotheses.loc["H1", "eligible"])
        self.assertTrue(np.isnan(hypotheses.loc["H1", "estimate"]))
        self.assertTrue(np.isnan(hypotheses.loc["H1", "p_raw"]))
        self.assertTrue(np.isnan(hypotheses.loc["H1", "p_holm"]))
        self.assertTrue(hypotheses.loc["H2", "eligible"])
        self.assertEqual(hypotheses.loc["H2", "estimate"], 1)
        self.assertEqual(hypotheses.loc["H2", "p_raw"], 2/256)
        self.assertEqual(hypotheses.loc["H2", "p_holm"], 4/256)
        self.assertTrue(hypotheses.loc["H2", "hypothesis_supported_holm_05"])

    def test_one_missing_planned_cost_is_not_a_complete_case_test(self):
        groups = group_fixture()
        groups.loc[(groups.block == 7) & (groups.condition == "adequate"), "total_scored_cost"] = np.nan
        results = inference_results(groups, 8, all_gates())
        h = results["hypotheses"].set_index("hypothesis")
        self.assertTrue(h.loc["H1", "eligible"])
        self.assertEqual(h.loc["H2", "complete_pairs"], 7)
        self.assertFalse(h.loc["H2", "eligible"])
        self.assertTrue(np.isnan(h.loc["H2", "estimate"]))
        self.assertTrue(np.isnan(h.loc["H2", "p_raw"]))
        self.assertEqual(len(results["block_contrasts"]), 16)

    def test_missing_chain_stays_in_preplanned_contrast_table(self):
        groups = group_fixture(2).iloc[:-1]
        contrasts = paired_contrasts(groups, 2)
        missing = contrasts[(contrasts.hypothesis == "H2") & (contrasts.block == 1)].iloc[0]
        self.assertFalse(missing.usable_pair)
        self.assertIn("missing adequate chain", missing.pair_reason)
        self.assertTrue(np.isnan(missing.contrast))

    def test_single_zero_contrast_emits_no_p_or_degenerate_ci(self):
        groups = group_fixture(1, beta_usable=False)
        groups["total_scored_cost"] = 156.
        h = hypothesis_table(groups, 1, all_gates()).set_index("hypothesis")
        self.assertEqual(h.loc["H2", "estimate"], 0)
        self.assertEqual(h.loc["H2", "observed_direction"], "zero")
        self.assertTrue(h.loc["H2", ["p_raw", "p_holm", "ci_lower", "ci_upper"]].isna().all())
        self.assertIn("Not tested", h.loc["H2", "conclusion"])
        self.assertFalse(h.loc["H2", "hypothesis_supported_holm_05"])

    def test_shared_failed_gates_withhold_both_hypotheses(self):
        for failed in ("api_observations", "calibration_passed", "complete_planned_sample",
                       "no_replacements", "no_fallbacks_or_missing", "model_effort_caps_consistent"):
            with self.subTest(failed=failed):
                gates = all_gates() | {failed: False}
                results = inference_results(group_fixture(), 8, gates)
                self.assertFalse(results["hypotheses"].eligible.any())
                self.assertTrue(results["hypotheses"].p_raw.isna().all())
                self.assertEqual(len(results["inference_checks"].query("check == @failed and passed == False")), 2)

    def test_opposite_sign_significance_does_not_support_directional_hypothesis(self):
        groups = group_fixture()
        groups.loc[groups.condition == "short", "total_scored_cost"] = 99.
        h = hypothesis_table(groups, 8, all_gates()).set_index("hypothesis")
        self.assertTrue(h.loc["H2", "reject_equal_effect_null_holm_05"])
        self.assertFalse(h.loc["H2", "hypothesis_supported_holm_05"])
        self.assertIn("opposite direction", h.loc["H2", "conclusion"])

    def test_duplicate_block_condition_is_not_an_independent_pair(self):
        groups = group_fixture()
        with self.assertRaisesRegex(ValueError, "More than one chain"):
            paired_contrasts(pd.concat([groups, groups.iloc[:1]]), 8)


class SavedRunAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.config = ReasoningConfig(mode="offline", stage="game", weeks=20,
                                    groups_per_condition=1, replicate_id="hypothesis-free-check")
        with patch.object(student_study, "ROOT", cls.root), \
                patch("beergame_study.student_report.build_report"), \
                patch("openai.AsyncOpenAI", side_effect=AssertionError("No API client allowed")):
            cls.directory = asyncio.run(student_study.run_campaign(cls.config))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_synthetic_run_reconstructs_costs_without_calls_or_writes(self):
        before = {str(p.relative_to(self.directory)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.directory.rglob("*") if p.is_file()}
        with patch("openai.AsyncOpenAI", side_effect=AssertionError("API client forbidden")) as api, \
                patch.object(student_study, "run_campaign", side_effect=AssertionError("Campaign forbidden")) as campaign:
            result = analyze_run(self.directory)
        api.assert_not_called()
        campaign.assert_not_called()
        after = {str(p.relative_to(self.directory)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.directory.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(result["summary"]["planned_pairs"], 1)
        self.assertTrue(result["summary"]["completed_planned_sample"])
        self.assertEqual(result["summary"]["observed_valid_decisions"], 128)
        self.assertFalse(result["summary"]["gates"]["api_observations"])
        self.assertFalse(result["hypotheses"].eligible.any())
        self.assertTrue(result["token_use"].median_output_tokens.isna().all())
        self.assertEqual(result["summary"]["additional_spending_usd"], 0)
        json.dumps(result["summary"], allow_nan=False)

    def test_config_change_invalidates_saved_request_fingerprint(self):
        path = self.directory/"manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["config"]["groups_per_condition"] = 3
        # Request fingerprints depend on the scientific max; a dishonest manifest
        # change must fail instead of being mistaken for three completed pairs.
        with changed(path, json.dumps(manifest).encode("utf-8")):
            with self.assertRaisesRegex(AnalysisError, "Request provenance"):
                analyze_run(self.directory)

    def test_committed_usage_must_agree_with_exact_saved_request(self):
        path = self.directory/"rounds.csv"
        frame = pd.read_csv(path)
        frame.loc[frame.phase == "agent", "output_tokens"] += 1
        with changed(path, frame.to_csv(index=False).encode("utf-8")):
            with self.assertRaisesRegex(AnalysisError, "usage/latency differs"):
                analyze_run(self.directory)

    def test_cost_field_corruption_is_rejected_by_physical_reconstruction(self):
        path = self.directory/"rounds.csv"
        frame = pd.read_csv(path)
        frame.loc[0, "cost"] += 1
        with changed(path, frame.to_csv(index=False).encode("utf-8")):
            with self.assertRaisesRegex(AnalysisError, "Physical state/cost reconstruction"):
                analyze_run(self.directory)

    def test_saved_derived_cost_cannot_override_reconstructed_scored_cost(self):
        result = analyze_run(self.directory)
        frame = result["groups"].copy()
        frame.loc[0, "total_scored_cost"] += 1
        with changed(self.directory/"group_outcomes.csv", frame.to_csv(index=False).encode("utf-8")):
            with self.assertRaisesRegex(AnalysisError, "total_scored_cost differs"):
                analyze_run(self.directory)

    def test_changed_prompt_invalidates_exact_request_provenance(self):
        path = next(p for p in (self.directory/"requests").glob("*.json")
                    if json.loads(p.read_text(encoding="utf-8"))["identity"]["stage"] == "decision")
        record = json.loads(path.read_text(encoding="utf-8"))
        record["messages"][0]["content"] += " Invent a preferred maximum."
        with changed(path, json.dumps(record).encode("utf-8")):
            with self.assertRaisesRegex(AnalysisError, "Request provenance"):
                analyze_run(self.directory)

    def test_incomplete_scoring_tail_withholds_full_scored_cost(self):
        path = self.directory/"continuation.csv"
        frame = pd.read_csv(path)
        frame = frame[~((frame.group_id == "b000_short") & (frame.week == 32))]
        with changed(path, frame.to_csv(index=False).encode("utf-8")):
            result = analyze_run(self.directory)
        h = result["hypotheses"].set_index("hypothesis")
        self.assertFalse(result["summary"]["completed_planned_sample"])
        self.assertEqual(h.loc["H2", "complete_pairs"], 0)
        self.assertTrue(np.isnan(h.loc["H2", "estimate"]))
        self.assertTrue(np.isnan(h.loc["H2", "p_raw"]))

    def test_external_calibration_reuse_is_hash_checked(self):
        config = ReasoningConfig(mode="offline", stage="game", weeks=20,
                                 groups_per_condition=1, replicate_id="hypothesis-external-cal-check")
        with patch.object(student_study, "ROOT", self.root), \
                patch("beergame_study.student_report.build_report"), \
                patch("openai.AsyncOpenAI", side_effect=AssertionError("API client forbidden")):
            directory = asyncio.run(student_study.run_campaign(config, calibration_run=self.directory))
        result = analyze_run(directory)
        self.assertEqual(result["summary"]["calibration_source"], str(self.directory.resolve()))
        self.assertGreater(len(result["provenance"]["external_calibration_input_sha256"]), 144)
        self.assertEqual(result["summary"]["planned_pairs"], 1)
        path = directory/"calibration_reuse.json"
        reuse = json.loads(path.read_text(encoding="utf-8"))
        reuse["parent_manifest_sha256"] = "tampered parent"
        with changed(path, json.dumps(reuse).encode("utf-8")):
            with self.assertRaisesRegex(AnalysisError, "saved reuse provenance"):
                analyze_run(directory)


def api_record(week=5, output=20):
    """Complete fake SDK response fixture; no client or generation is called."""
    config = ReasoningConfig(mode="api", stage="game")
    specification = dict(protocol=PROTOCOL,
                         identity=dict(stage="decision", group="b000_short", role="factory", week=week),
                         messages=make_messages({}, []), limit=8192, schema=ORDER_SCHEMA,
                         requested_model=config.model, reasoning={"effort": "high"}, mode="api",
                         config_fingerprint=config.fingerprint())
    usage = dict(input_tokens=100, output_tokens=output, cached_input_tokens=10,
                 reasoning_tokens=output-14, nonreasoning_output_tokens_proxy=14)
    raw = dict(model=config.model, status="completed", reasoning={"effort": "high"}, max_output_tokens=8192,
               text={"format": {"type": "json_schema", "strict": True, "schema_": ORDER_SCHEMA}},
               output=[{"type": "message", "content": [{"type": "output_text", "text": '{"order":4}'}]}],
               usage=dict(input_tokens=100, output_tokens=output, input_tokens_details={"cached_tokens": 10},
                          output_tokens_details={"reasoning_tokens": output-14}))
    record = dict(specification, request_key=digest(specification), requested_effort="high", timeout_s=config.timeout_s,
                  status="ok", response_status="completed", returned_model=config.model, text='{"order":4}',
                  refused=False, incomplete_reason=None, response=raw, usage=usage, usage_observed=True,
                  synthetic=False, charge_usd=price(usage), protocol_errors=[])
    return record, config


class RawResponseProvenanceTests(unittest.TestCase):
    def test_raw_sdk_schema_alias_and_usage_are_accepted_without_calls(self):
        record, config = api_record()
        _reconcile_response(record, config)
        self.assertAlmostEqual(record["charge_usd"], .00015825)

    def test_raw_model_text_status_usage_schema_effort_limit_or_price_corruption_is_rejected(self):
        mutations = {
            "model": lambda r: r["response"].update(model="another-model"),
            "text": lambda r: r["response"]["output"][0]["content"][0].update(text='{"order":9}'),
            "status": lambda r: r["response"].update(status="incomplete"),
            "usage": lambda r: r["response"]["usage"].update(output_tokens=8193),
            "schema": lambda r: r["response"]["text"]["format"].update(schema_={}),
            "effort": lambda r: r["response"]["reasoning"].update(effort="low"),
            "limit": lambda r: r["response"].update(max_output_tokens=1024),
            "charge": lambda r: r.update(charge_usd=1),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                record, config = api_record()
                mutate(record)
                with self.assertRaises(AnalysisError):
                    _reconcile_response(record, config)

    def test_duplicate_generated_retry_is_rejected(self):
        record, config = api_record()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory/"requests").mkdir()
            key = record["request_key"]
            for suffix in ("", "_retry_1"):
                (directory/"requests"/(key+suffix+".json")).write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaisesRegex(AnalysisError, "repeated generated"):
                _records(directory, config)

    def test_zero_charge_retry_and_uncommitted_attempts_are_not_extra_decisions(self):
        record, config = api_record()
        rejected = record | dict(status="api_error", response_status=None, returned_model=None, response=None,
                                 usage=None, usage_observed=False, charge_usd=0, text="",
                                 http_status=429, error_category="temporary_rate")
        extra, _ = api_record(week=6, output=4096)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            cache = directory/"requests"
            cache.mkdir()
            for name, value in ((record["request_key"]+".json", rejected),
                                (record["request_key"]+"_retry_1.json", record),
                                (extra["request_key"]+".json", extra)):
                (cache/name).write_text(json.dumps(value), encoding="utf-8")
            records, latest = _records(directory, config)
            groups = pd.DataFrame([dict(group_id="b000_short", condition="short")])
            rounds = pd.DataFrame([dict(group_id="b000_short", role="factory", week=5, phase="agent")])
            tokens = _token_use(records, groups, {"short_tokens": 8192, "adequate_tokens": 16384}, rounds, latest).set_index("condition")
            self.assertEqual(tokens.loc["short", "decision_calls"], 1)
            self.assertEqual(tokens.loc["short", "saved_transport_attempts"], 3)
            self.assertEqual(tokens.loc["short", "uncommitted_saved_attempts"], 1)
            self.assertEqual(tokens.loc["short", "median_output_tokens"], 20)
            self.assertEqual(tokens.loc["short", "valid_model_decision_calls"], 1)


if __name__ == "__main__":
    unittest.main()
