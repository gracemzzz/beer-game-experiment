"""Meaningful protocol invariants, with injected responses and no API network."""
import asyncio
import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from beergame_study.reasoning_protocol import (
    COMMON, MODEL, ORDER_SCHEMA, RATES, RULE_ANSWERS, RULES_SCHEMA, Decision,
    Gateway, ReasoningConfig, StudyStopped, decide, make_messages, price,
    rules_messages, rules_result, screen_caps, synthetic_order,
)


def response(order=7, total=220, reasoning=200, status="completed", model=MODEL):
    return {
        "id": "resp_test", "model": model, "status": status,
        "incomplete_details": {"reason": "max_output_tokens"} if status == "incomplete" else None,
        "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps({"order": order})}]}],
        "usage": {"input_tokens": 1000, "input_tokens_details": {"cached_tokens": 400},
                  "output_tokens": total, "output_tokens_details": {"reasoning_tokens": reasoning}},
    }


class FakeClient:
    def __init__(self, raw=None, exception=None, delay=0, outcomes=None):
        self.raw = response() if raw is None else raw
        self.exception = exception
        self.delay = delay
        self.outcomes = list(outcomes) if outcomes is not None else None
        self.calls = []
        self.options = []
        self.responses = SimpleNamespace(create=self.create)

    def with_options(self, **kwargs):
        self.options.append(kwargs)
        return self

    async def create(self, **kwargs):
        self.calls.append(copy.deepcopy(kwargs))
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.outcomes is not None:
            item = self.outcomes.pop(0)
            if isinstance(item, Exception):
                raise item
            return copy.deepcopy(item)
        if self.exception:
            raise self.exception
        return copy.deepcopy(self.raw)


def screen_record(cap, total, *, item=0, valid=True, reasoning=20, synthetic=False):
    return {"limit": cap, "status": "ok", "response_status": "completed" if valid else "incomplete",
            "incomplete_reason": None if valid else "max_output_tokens", "refused": False,
            "text": '{"order":7}', "identity": {"stage": "calibration", "item": item, "cap": cap},
            "synthetic": synthetic, "usage_observed": not synthetic,
            "usage": {"output_tokens": total, "reasoning_tokens": reasoning}}


class ReasoningProtocolTests(unittest.TestCase):
    @staticmethod
    def rate_error(code="rate_limit_exceeded", headers=None):
        class RateError(Exception):
            status_code = 429
        error = RateError("sensitive API key must never be stored")
        error.body = {"error": {"code": code, "type": "must not copy", "message": "sensitive account data"},
                      "api_key": "sensitive secret"}
        error.response = SimpleNamespace(headers=headers or {})
        return error

    @staticmethod
    def fast_gateway(directory, client, *, recheck_rejections=False):
        g = Gateway(directory, replace(ReasoningConfig(mode="api"), request_interval_s=0), client=client,
                    recheck_rejections=recheck_rejections)
        g.RATE_COOLDOWN_SECONDS = 0
        g.RATE_COOLDOWN_MAX_SECONDS = 0
        return g

    def test_fixed_config_hashes_separate_science_from_operational_budget(self):
        c = ReasoningConfig().validate()
        self.assertEqual(c.effort, "high")
        self.assertEqual(c.fingerprint(), replace(c, budget_usd=12, concurrency=2, request_interval_s=0).fingerprint())
        self.assertNotEqual(c.fingerprint(), replace(c, short_tokens=1024).fingerprint())
        self.assertNotEqual(c.fingerprint(), replace(c, timeout_s=200).fingerprint())
        for altered in (replace(c, effort="none"), replace(c, model="gpt-5.4-nano-2026-03-17"),
                        replace(c, candidate_caps=(1024, 512)), replace(c, budget_usd=float("inf"))):
            with self.assertRaises(ValueError):
                altered.validate()

    def test_same_question_factual_rules_and_no_suggested_maximum(self):
        state = {"week": 7, "role": "factory", "demand": 8, "inventory": 0, "backlog": 8, "supply_line": 12}
        first = make_messages(state, [])
        second = make_messages(state, [])
        self.assertEqual(first, second)
        self.assertIn("hypothetical second-year", COMMON)
        self.assertIn("University at Buffalo", COMMON)
        self.assertIn("already includes", COMMON)
        self.assertIn("week t+3, not week t+2", COMMON)
        self.assertNotIn("maximum", ORDER_SCHEMA["properties"]["order"])
        self.assertNotIn("100000", json.dumps(first))
        self.assertNotIn("2048", json.dumps(first))
        self.assertNotIn("8192", json.dumps(first))
        self.assertEqual(json.loads(first[1]["content"])["current_state"], state)
        check = {"status": "ok", "response_status": "completed", "text": json.dumps(RULE_ANSWERS)}
        self.assertTrue(rules_result(check)["passed"])
        incorrect = copy.deepcopy(RULE_ANSWERS)
        incorrect["factory_order_week_7_arrival_week"] = 9
        self.assertFalse(rules_result(dict(check, text=json.dumps(incorrect)))["passed"])
        self.assertIn("week 7", rules_messages("factory")[1]["content"])

    def test_orders_preserve_zero_and_fallback_last_valid_without_clipping(self):
        normal = {"status": "ok", "response_status": "completed", "refused": False, "text": '{"order":0}'}
        result = decide(normal, last_valid_order=9)
        self.assertEqual(result.order, 0)
        self.assertTrue(result.valid)
        self.assertFalse(result.fallback)
        for value in ('{"order":true}', '{"order":-1}', '{"order":3.5}', '{"order":100001}',
                      '{"order":5,"extra":1}', 'bad JSON'):
            result = decide(dict(normal, text=value), last_valid_order=9)
            self.assertEqual(result.order, 9)
            self.assertTrue(result.fallback)
            self.assertFalse(result.valid)
            self.assertFalse(result.confirmatory_eligible)
        truncated = decide(dict(normal, response_status="incomplete", incomplete_reason="max_output_tokens"), last_valid_order=0)
        self.assertEqual((truncated.order, truncated.reason), (0, "truncated"))
        self.assertTrue(decide(dict(normal, refused=True)).fallback)
        self.assertFalse(decide(dict(normal, synthetic=True)).confirmatory_eligible)

    def test_price_counts_total_output_once_and_cached_discount(self):
        usage = {"input_tokens": 1000, "cached_input_tokens": 400, "output_tokens": 220, "reasoning_tokens": 200}
        expected = (600 * .75 + 400 * .075 + 220 * 4.5) / 1e6
        self.assertAlmostEqual(price(usage), expected)
        with self.assertRaises(ValueError):
            price(dict(usage, cached_input_tokens=1001))

    def test_offline_benchmark_provenance_and_no_live_client(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                client = FakeClient()
                gateway = Gateway(tmp, replace(ReasoningConfig(), request_interval_s=0), client=client)
                messages = make_messages({"demand": 8}, [])
                record = await gateway.request({"round": 1}, messages, 2048, synthetic='{"order":8}')
                self.assertEqual(client.calls, [])
                self.assertTrue(record["synthetic"])
                self.assertFalse(record["usage_observed"])
                self.assertEqual(record["messages"], messages)
                self.assertEqual(record["schema"], ORDER_SCHEMA)
                self.assertEqual(record["requested_model"], MODEL)
                self.assertEqual(record["requested_effort"], "high")
                self.assertEqual(record["usage"]["output_tokens"], 0)
                self.assertFalse(decide(record).confirmatory_eligible)
                self.assertEqual(synthetic_order({"demand": 8}), 8)
                self.assertFalse(screen_caps([record])["manipulation_screen_passed"])
        asyncio.run(check())

    def test_single_call_high_effort_complete_usage_raw_response_and_cache(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                client = FakeClient()
                config = replace(ReasoningConfig(mode="api"), request_interval_s=0)
                gateway = Gateway(tmp, config, client=client)
                messages = make_messages({"demand": 8}, [])
                records = await asyncio.gather(*[gateway.request({"round": 1}, messages, 512) for _ in range(3)])
                self.assertEqual(len(client.calls), 1)
                self.assertEqual(client.options, [{"max_retries": 0, "timeout": config.timeout_s}])
                request = client.calls[0]
                self.assertEqual(request["reasoning"], {"effort": "high"})
                self.assertEqual(request["max_output_tokens"], 512)
                self.assertEqual(request["text"]["format"]["schema"], ORDER_SCHEMA)
                record = records[0]
                self.assertEqual(record["response"], response())
                self.assertEqual(record["returned_model"], MODEL)
                self.assertEqual(record["usage"]["nonreasoning_output_tokens_proxy"], 20)
                self.assertGreaterEqual(record["elapsed_s"], 0)
                self.assertAlmostEqual(gateway.charged, price(record["usage"]))
                resumed = Gateway(tmp, replace(config, budget_usd=12), client=client)
                cached = await resumed.request({"round": 1}, messages, 512)
                self.assertEqual(cached, record)
                self.assertEqual(len(client.calls), 1)
                self.assertEqual(len(list((Path(tmp) / "requests").glob("*.json"))), 1)
        asyncio.run(check())

    def test_truncation_refusal_malformed_never_resubmitted(self):
        async def check():
            cases = [response(status="incomplete")]
            malformed = response()
            malformed["output"][0]["content"][0]["text"] = "malformed"
            cases.append(malformed)
            refused = response()
            refused["output"][0]["content"] = [{"type": "refusal", "refusal": "Cannot answer"}]
            cases.append(refused)
            for raw in cases:
                with tempfile.TemporaryDirectory() as tmp:
                    client = FakeClient(raw)
                    g = Gateway(tmp, replace(ReasoningConfig(mode="api"), request_interval_s=0), client=client)
                    a = await g.request("one", make_messages({"demand": 8}, []), 512)
                    b = await g.request("one", make_messages({"demand": 8}, []), 512)
                    self.assertTrue(decide(a, last_valid_order=6).fallback)
                    self.assertEqual(decide(a, last_valid_order=6).order, 6)
                    self.assertEqual(a, b)
                    self.assertEqual(len(client.calls), 1)
        asyncio.run(check())

    def test_concurrent_reservations_cannot_exceed_budget(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                messages = make_messages({"demand": 8}, [])
                config = replace(ReasoningConfig(mode="api"), request_interval_s=0)
                probe = Gateway(tmp, config, client=FakeClient())
                reservation = probe.reservation(messages, 512, ORDER_SCHEMA)
                client = FakeClient(delay=.03)
                gateway = Gateway(tmp, replace(config, budget_usd=reservation * 1.5), client=client)
                results = await asyncio.gather(gateway.request("a", messages, 512), gateway.request("b", messages, 512), return_exceptions=True)
                self.assertEqual(len(client.calls), 1)
                self.assertEqual(sum(isinstance(x, StudyStopped) for x in results), 1)
                self.assertLessEqual(gateway.charged, gateway.config.budget_usd)
        asyncio.run(check())

    def test_unknown_transport_reserves_cost_safe_error_and_no_retry(self):
        class ConnectionFailure(Exception):
            pass
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                client = FakeClient(exception=ConnectionFailure("secret should never be logged"))
                gateway = Gateway(tmp, replace(ReasoningConfig(mode="api"), request_interval_s=0), client=client)
                messages = make_messages({"demand": 8}, [])
                record = await gateway.request("a", messages, 512)
                cached = await gateway.request("a", messages, 512)
                self.assertEqual(record, cached)
                self.assertEqual(len(client.calls), 1)
                self.assertEqual(record["error_category"], "connection")
                self.assertEqual(gateway.charged, record["reserved_usd"])
                self.assertEqual(record["charge_usd"], record["reserved_usd"])
                self.assertNotIn("secret", json.dumps(record))
                self.assertTrue(decide(record).fallback)
        asyncio.run(check())

    def test_known_api_rejection_refunds_and_stops_without_logging_body(self):
        class AuthError(Exception):
            status_code = 401
            body = {"secret": "must not save"}
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                client = FakeClient(exception=AuthError("sensitive"))
                gateway = Gateway(tmp, replace(ReasoningConfig(mode="api"), request_interval_s=0), client=client)
                with self.assertRaises(StudyStopped):
                    await gateway.request("a", make_messages({"demand": 8}, []), 512)
                self.assertEqual(gateway.charged, 0)
                saved = json.loads(next((Path(tmp)/"requests").glob("*.json")).read_text())
                self.assertEqual(saved["error_category"], "authentication")
                self.assertNotIn("sensitive", json.dumps(saved))
                self.assertNotIn("secret", json.dumps(saved))
                with self.assertRaises(StudyStopped):
                    await gateway.request("a", make_messages({"demand": 8}, []), 512)
                self.assertEqual(len(client.calls), 1)
        asyncio.run(check())

    def test_temporary_rate_rejection_retries_identical_payload_and_preserves_both_records(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                error = self.rate_error(headers={"retry-after": "0", "x-ratelimit-remaining-tokens": "25",
                                                 "authorization": "sensitive secret", "x-request-id": "private"})
                client = FakeClient(outcomes=[error, response()])
                gateway = self.fast_gateway(tmp, client)
                messages = make_messages({"demand": 8}, [])
                record = await gateway.request("a", messages, 512)
                self.assertTrue(decide(record).valid)
                self.assertEqual(record["transport_attempt"], 1)
                self.assertEqual(client.calls[0], client.calls[1])
                self.assertEqual(client.calls[1]["reasoning"], {"effort": "high"})
                self.assertEqual(client.calls[1]["max_output_tokens"], 512)
                saved = sorted((Path(tmp)/"requests").glob("*.json"))
                self.assertEqual(len(saved), 2)
                failed = [json.loads(p.read_text()) for p in saved if "_retry_" not in p.stem][0]
                self.assertEqual(failed["error_category"], "temporary_rate")
                self.assertEqual(failed["error_code"], "rate_limit_exceeded")
                self.assertEqual(failed["charge_usd"], 0)
                self.assertEqual(failed["rate_limit_headers"], {"retry-after": 0, "x-ratelimit-remaining-tokens": 25})
                self.assertNotIn("sensitive", json.dumps(failed))
                self.assertNotIn("authorization", json.dumps(failed))
                self.assertAlmostEqual(gateway.charged, price(record["usage"]))
                before = [p.read_bytes() for p in saved]
                self.assertEqual(await gateway.request("a", messages, 512), record)
                resumed = self.fast_gateway(tmp, client)
                self.assertEqual(await resumed.request("a", messages, 512), record)
                self.assertEqual(len(client.calls), 2)
                self.assertEqual([p.read_bytes() for p in saved], before)
                self.assertAlmostEqual(resumed.charged, price(record["usage"]))
        asyncio.run(check())

    def test_permanent_quota_and_new_ambiguous_429_never_retry(self):
        async def check():
            for code in ("insufficient_quota", "billing_hard_limit_reached", "unrecognized secret code"):
                with tempfile.TemporaryDirectory() as tmp:
                    client = FakeClient(outcomes=[self.rate_error(code), response()])
                    gateway = self.fast_gateway(tmp, client)
                    messages = make_messages({"demand": 8}, [])
                    with self.assertRaises(StudyStopped):
                        await gateway.request("a", messages, 512)
                    self.assertEqual(len(client.calls), 1)
                    self.assertEqual(gateway.charged, 0)
                    saved = json.loads(next((Path(tmp)/"requests").glob("*.json")).read_text())
                    self.assertTrue(saved["fatal_error"])
                    self.assertNotIn("sensitive", json.dumps(saved))
                    self.assertNotIn("secret code", json.dumps(saved))
                    resumed = self.fast_gateway(tmp, client)
                    with self.assertRaises(StudyStopped):
                        await resumed.request("a", messages, 512)
                    self.assertEqual(len(client.calls), 1)
        asyncio.run(check())

    def test_documented_credit_spend_usage_rejections_stop_and_slow_down_retries(self):
        async def check():
            for code in ("credit_balance_exhausted", "organization_spend_limit_exceeded",
                         "project_spend_limit_exceeded", "organization_usage_limit_exceeded", "slow_down"):
                with self.subTest(code=code), tempfile.TemporaryDirectory() as tmp:
                    error = self.rate_error(code)
                    error.body["error"]["type"] = "rate_limit_error"
                    client = FakeClient(outcomes=[error, response()])
                    gateway = self.fast_gateway(tmp, client)
                    messages = make_messages({"demand": 8}, [])
                    if code == "slow_down":
                        record = await gateway.request("a", messages, 512)
                        self.assertTrue(decide(record).valid)
                        self.assertEqual(len(client.calls), 2)
                    else:
                        with self.assertRaises(StudyStopped):
                            await gateway.request("a", messages, 512)
                        self.assertEqual(len(client.calls), 1)
                        self.assertEqual(gateway.charged, 0)
                    rejected = json.loads(next(p for p in (Path(tmp)/"requests").glob("*.json")
                                               if "_retry_" not in p.stem).read_text())
                    self.assertEqual(rejected["error_code"], code)
                    self.assertEqual(rejected["error_category"], "temporary_rate" if code == "slow_down" else "quota_or_billing")
                    self.assertNotIn("sensitive", json.dumps(rejected))
        asyncio.run(check())

    def test_safe_type_fallback_never_retries_unknown_code_with_generic_rate_type(self):
        cases = [("unknown private code", "insufficient_quota", "insufficient_quota", False),
                 ("unknown private code", "rate_limit_error", None, False),
                 (None, "rate_limit_error", "rate_limit_error", True),
                 (None, "insufficient_quota", "insufficient_quota", False),
                 ("rate_limit_exceeded", "insufficient_quota", "rate_limit_exceeded", True)]
        async def check():
            for supplied, error_type, expected, retry in cases:
                with self.subTest(code=supplied, type=error_type), tempfile.TemporaryDirectory() as tmp:
                    error = self.rate_error(supplied)
                    error.body["error"]["type"] = error_type
                    client = FakeClient(outcomes=[error, response()])
                    gateway = self.fast_gateway(tmp, client)
                    messages = make_messages({"demand": 8}, [])
                    if retry:
                        self.assertTrue(decide(await gateway.request("a", messages, 512)).valid)
                    else:
                        with self.assertRaises(StudyStopped):
                            await gateway.request("a", messages, 512)
                    self.assertEqual(len(client.calls), 2 if retry else 1)
                    rejected = json.loads(next(p for p in (Path(tmp)/"requests").glob("*.json")
                                               if "_retry_" not in p.stem).read_text())
                    self.assertEqual(rejected["error_code"], expected)
                    self.assertNotIn("unknown private code", json.dumps(rejected))
                    self.assertNotIn("sensitive", json.dumps(rejected))
                    if expected == "insufficient_quota":
                        self.assertEqual(rejected["error_category"], "quota_or_billing")
                    elif expected is None:
                        self.assertEqual(rejected["error_category"], "unknown_rate_or_quota")
        asyncio.run(check())

    def test_explicit_access_recheck_probes_saved_quota_once_and_preserves_history(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                messages = make_messages({"demand": 8}, [])
                initial = self.fast_gateway(tmp, FakeClient(outcomes=[self.rate_error("insufficient_quota")]))
                with self.assertRaises(StudyStopped):
                    await initial.request("a", messages, 512)
                base = next((Path(tmp)/"requests").glob("*.json"))
                before = base.read_bytes()
                blocked_client = FakeClient(outcomes=[response()])
                with self.assertRaises(StudyStopped):
                    await self.fast_gateway(tmp, blocked_client).request("a", messages, 512)
                self.assertEqual(blocked_client.calls, [])
                client = FakeClient(outcomes=[response()])
                gateway = self.fast_gateway(tmp, client, recheck_rejections=True)
                record = await gateway.request("a", messages, 512)
                self.assertTrue(decide(record).valid)
                self.assertEqual(record["transport_attempt"], 1)
                self.assertEqual(base.read_bytes(), before)
                self.assertEqual(len(client.calls), 1)
                self.assertEqual(await gateway.request("a", messages, 512), record)
                # Recovery is durable: later ordinary resumes need no new flag.
                self.assertEqual(await self.fast_gateway(tmp, client).request("a", messages, 512), record)
                self.assertEqual(len(client.calls), 1)
                self.assertAlmostEqual(gateway.charged, price(record["usage"]))
        asyncio.run(check())

    def test_access_recheck_new_quota_rejection_stops_without_another_fresh_probe(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                messages = make_messages({"demand": 8}, [])
                initial = self.fast_gateway(tmp, FakeClient(outcomes=[self.rate_error("insufficient_quota")]))
                with self.assertRaises(StudyStopped):
                    await initial.request("a", messages, 512)
                base = next((Path(tmp)/"requests").glob("*.json"))
                before = base.read_bytes()
                client = FakeClient(outcomes=[self.rate_error("credit_balance_exhausted"), response()])
                gateway = self.fast_gateway(tmp, client, recheck_rejections=True)
                with self.assertRaises(StudyStopped):
                    await gateway.request("a", messages, 512)
                self.assertEqual(len(client.calls), 1)
                self.assertEqual(len(list(base.parent.glob("*.json"))), 2)
                self.assertEqual(base.read_bytes(), before)
                with self.assertRaises(StudyStopped):
                    await gateway.request("a", messages, 512)
                with self.assertRaises(StudyStopped):
                    await self.fast_gateway(tmp, client).request("a", messages, 512)
                self.assertEqual(len(client.calls), 1)
                self.assertEqual(gateway.charged, 0)
        asyncio.run(check())

    def test_access_recheck_old_base_and_fatal_retry_one_uses_only_retry_two(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                messages = make_messages({"demand": 8}, [])
                initial = self.fast_gateway(tmp, FakeClient(outcomes=[self.rate_error("insufficient_quota")]))
                with self.assertRaises(StudyStopped):
                    await initial.request("a", messages, 512)
                base = next((Path(tmp)/"requests").glob("*.json"))
                historical = json.loads(base.read_text())
                historical["error_category"] = "rate_or_quota"
                for name in ("error_code", "rate_limit_headers", "rate_retry_exhausted", "transport_attempt"):
                    historical.pop(name, None)
                base.write_text(json.dumps(historical), encoding="utf-8")
                rejected = dict(historical, error_category="unknown_rate_or_quota", error_code=None,
                                rate_limit_headers={}, transport_attempt=1)
                retry_one = base.with_name(base.stem+"_retry_1.json")
                retry_one.write_text(json.dumps(rejected), encoding="utf-8")
                before = {p.name: p.read_bytes() for p in base.parent.glob("*.json")}
                blocked_client = FakeClient(outcomes=[response()])
                with self.assertRaises(StudyStopped):
                    await self.fast_gateway(tmp, blocked_client).request("a", messages, 512)
                self.assertEqual(blocked_client.calls, [])
                client = FakeClient(outcomes=[response()])
                gateway = self.fast_gateway(tmp, client, recheck_rejections=True)
                record = await gateway.request("a", messages, 512)
                self.assertTrue(decide(record).valid)
                self.assertEqual(record["transport_attempt"], 2)
                self.assertEqual(len(client.calls), 1)
                self.assertEqual({p.name: p.read_bytes() for p in base.parent.glob("*.json") if p.name in before}, before)
                self.assertTrue(base.with_name(base.stem+"_retry_2.json").exists())
                self.assertEqual(await self.fast_gateway(tmp, client).request("a", messages, 512), record)
                self.assertEqual(len(client.calls), 1)
        asyncio.run(check())

    def test_access_recheck_excludes_authentication_pending_and_unknown_transport(self):
        async def check():
            for kind in ("authentication", "transport", "pending"):
                with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                    messages = make_messages({"demand": 8}, [])
                    if kind == "authentication":
                        error = self.rate_error("invalid_api_key")
                        error.status_code = 401
                    else:
                        class ConnectionFailure(Exception):
                            pass
                        error = ConnectionFailure("sensitive")
                    initial = self.fast_gateway(tmp, FakeClient(exception=error))
                    if kind == "authentication":
                        with self.assertRaises(StudyStopped):
                            await initial.request("a", messages, 512)
                    else:
                        await initial.request("a", messages, 512)
                    if kind == "pending":
                        path = next((Path(tmp)/"requests").glob("*.json"))
                        record = json.loads(path.read_text())
                        record["status"] = "pending"
                        path.write_text(json.dumps(record), encoding="utf-8")
                    client = FakeClient(outcomes=[response()])
                    gateway = self.fast_gateway(tmp, client, recheck_rejections=True)
                    if kind in ("authentication", "pending"):
                        with self.assertRaises(StudyStopped):
                            await gateway.request("a", messages, 512)
                    else:
                        self.assertTrue(decide(await gateway.request("a", messages, 512)).fallback)
                    self.assertEqual(client.calls, [])
        asyncio.run(check())

    def test_historical_ambiguous_rejection_gets_one_probe_without_rewriting_history(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                messages = make_messages({"demand": 8}, [])
                client = FakeClient(outcomes=[self.rate_error("insufficient_quota")])
                gateway = self.fast_gateway(tmp, client)
                # Generate the precise compatible old key, then replace this
                # rejected record with the historical safe metadata shape.
                with self.assertRaises(StudyStopped):
                    await gateway.request("a", messages, 512)
                path = next((Path(tmp)/"requests").glob("*.json"))
                old = json.loads(path.read_text())
                old["error_category"] = "rate_or_quota"
                for key in ("error_code", "rate_limit_headers", "rate_retry_exhausted", "transport_attempt", "local_rate_retries_max"):
                    old.pop(key, None)
                path.write_text(json.dumps(old), encoding="utf-8")
                before = path.read_bytes()
                probe_client = FakeClient(outcomes=[response()])
                resumed = self.fast_gateway(tmp, probe_client)
                result = await resumed.request("a", messages, 512)
                self.assertTrue(decide(result).valid)
                self.assertEqual(len(probe_client.calls), 1)
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(result["request_key"], old["request_key"])
                self.assertEqual(result["config_fingerprint"], old["config_fingerprint"])
                self.assertEqual(result["transport_attempt"], 1)
                self.assertEqual(len(list(path.parent.glob("*.json"))), 2)
                self.assertEqual(await resumed.request("a", messages, 512), result)
                self.assertEqual(len(probe_client.calls), 1)
        asyncio.run(check())

    def test_temporary_rate_retries_are_bounded_and_final_failure_is_cached(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                client = FakeClient(outcomes=[self.rate_error() for _ in range(3)])
                gateway = self.fast_gateway(tmp, client)
                messages = make_messages({"demand": 8}, [])
                with self.assertRaises(StudyStopped):
                    await gateway.request("a", messages, 512)
                self.assertEqual(len(client.calls), 3)
                self.assertEqual(gateway.charged, 0)
                saved = list((Path(tmp)/"requests").glob("*.json"))
                self.assertEqual(len(saved), 3)
                last = json.loads(next(p for p in saved if p.stem.endswith("_retry_2")).read_text())
                self.assertTrue(last["rate_retry_exhausted"])
                resumed = self.fast_gateway(tmp, client)
                with self.assertRaises(StudyStopped):
                    await resumed.request("a", messages, 512)
                self.assertEqual(len(client.calls), 3)
        asyncio.run(check())

    def test_shared_rate_cooldown_bounds_retry_after_and_does_not_change_fingerprint(self):
        async def check():
            import time
            with tempfile.TemporaryDirectory() as tmp:
                gateway = Gateway(tmp, ReasoningConfig())
                before = gateway.config.fingerprint()
                start = time.monotonic()
                await gateway._rate_cooldown({"rate_limit_headers": {"retry-after": 600}})
                self.assertGreaterEqual(gateway.cooldown-start, 60)
                self.assertLess(gateway.cooldown-start, 61)
                gateway.MAX_RATE_RETRIES = 1
                gateway.RATE_COOLDOWN_SECONDS = 1
                self.assertEqual(gateway.config.fingerprint(), before)
                self.assertEqual(gateway.config.fingerprint(), replace(gateway.config, request_interval_s=2).fingerprint())
        asyncio.run(check())

    def test_interrupted_pending_request_is_not_resubmitted(self):
        async def check():
            with tempfile.TemporaryDirectory() as tmp:
                client = FakeClient(delay=.05)
                config = replace(ReasoningConfig(mode="api"), request_interval_s=0)
                gateway = Gateway(tmp, config, client=client)
                messages = make_messages({"demand": 8}, [])
                task = asyncio.create_task(gateway.request("a", messages, 512))
                await asyncio.sleep(.01)
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task
                resumed = Gateway(tmp, config, client=client)
                with self.assertRaises(StudyStopped):
                    await resumed.request("a", messages, 512)
                self.assertEqual(len(client.calls), 1)
                self.assertGreater(resumed.charged, 0)
        asyncio.run(check())

    def test_model_mismatch_missing_usage_and_token_overrun_fail_protocol(self):
        async def check():
            variants = [response(model="different-model"), response(total=513)]
            missing = response()
            missing["usage"]["output_tokens_details"] = {}
            variants.append(missing)
            for raw in variants:
                with tempfile.TemporaryDirectory() as tmp:
                    g = Gateway(tmp, replace(ReasoningConfig(mode="api"), request_interval_s=0), client=FakeClient(raw))
                    record = await g.request("a", make_messages({"demand": 8}, []), 512)
                    self.assertEqual(record["status"], "protocol_error")
                    self.assertEqual(record["response"], raw)
                    self.assertTrue(decide(record).fallback)
        asyncio.run(check())

    def test_feasibility_screen_uses_completion_reasoning_and_usage_not_orders(self):
        records = []
        for cap, total in [(512, 450), (1024, 850), (2048, 1700), (16384, 3000)]:
            records.extend(screen_record(cap, total, item=i) for i in range(24))
        result = screen_caps(records, candidate_caps=(512, 1024, 2048))
        self.assertTrue(result["reference_screen_passed"])
        self.assertTrue(result["manipulation_screen_passed"])
        self.assertEqual((result["short_tokens"], result["adequate_tokens"]), (512, 1024))
        altered = copy.deepcopy(records)
        for item in altered:
            item["text"] = '{"order":0}'  # boundary choices do not select caps
        self.assertEqual(result, screen_caps(altered, candidate_caps=(512, 1024, 2048)))
        for item in altered[:2]:
            item["response_status"] = "incomplete"  # 22/24, below 95%
            item["incomplete_reason"] = "max_output_tokens"
        result = screen_caps(altered, candidate_caps=(512, 1024, 2048))
        self.assertFalse(result["screen_rows"][0]["viable"])
        self.assertEqual((result["short_tokens"], result["adequate_tokens"]), (1024, 2048))

    def test_screen_rejects_synthetic_zero_reasoning_no_separation_censored_reference(self):
        good = [screen_record(cap, total, item=i) for cap, total in [(512, 400), (1024, 800), (16384, 1500)] for i in range(24)]
        self.assertTrue(screen_caps(good, candidate_caps=(512, 1024))["manipulation_screen_passed"])
        for change in ("synthetic", "no_reasoning", "no_separation", "censored_reference"):
            records = copy.deepcopy(good)
            for item in records:
                if change == "synthetic":
                    item["synthetic"] = True
                elif change == "no_reasoning":
                    item["usage"]["reasoning_tokens"] = 0
                elif change == "no_separation":
                    item["usage"]["output_tokens"] = 400
                elif item["limit"] == 16384:
                    item["usage"]["output_tokens"] = 16000
            self.assertFalse(screen_caps(records, candidate_caps=(512, 1024))["manipulation_screen_passed"], change)
        self.assertFalse(screen_caps([])["manipulation_screen_passed"])

    def test_screen_requires_complete_unique_matched_batches_and_counts_truncated_usage(self):
        good = [screen_record(cap, total, item=i) for cap, total in [(512, 400), (1024, 800), (16384, 1500)] for i in range(24)]
        self.assertTrue(screen_caps(good, candidate_caps=(512, 1024))["complete_matched_batch"])
        missing = good[:-1]
        self.assertFalse(screen_caps(missing, candidate_caps=(512, 1024))["manipulation_screen_passed"])
        duplicated = copy.deepcopy(good)
        duplicated[0]["identity"]["item"] = 1
        self.assertFalse(screen_caps(duplicated, candidate_caps=(512, 1024))["complete_matched_batch"])
        mismatched = copy.deepcopy(good)
        mismatched[0]["identity"]["item"] = 24
        self.assertFalse(screen_caps(mismatched, candidate_caps=(512, 1024))["complete_matched_batch"])
        # One failed answer out of 24 can pass a 95% feasibility threshold, but
        # its consumed allowance remains in the usage distribution.
        truncated = copy.deepcopy(good)
        truncated[0].update(response_status="incomplete", incomplete_reason="max_output_tokens")
        truncated[0]["usage"]["output_tokens"] = 512
        result = screen_caps(truncated, candidate_caps=(512, 1024))
        row = result["screen_rows"][0]
        self.assertTrue(row["viable"])
        self.assertEqual(row["completion_denominator"], 24)
        self.assertEqual(row["completed_valid_n"], 23)
        self.assertEqual(row["measured_usage_n"], 24)
        self.assertAlmostEqual(row["near_cap_fraction"], 1/24)


if __name__ == "__main__":
    unittest.main()
