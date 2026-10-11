"""Versioned transport for the anytime protocol.

Copied from the audited legacy gateway to preserve old scientific source hashes.
The request protocol and config fingerprint now identify the anytime experiment.
No calls occur on import. Keep safety fixes covered in both gateway test suites.
"""
from __future__ import annotations
import asyncio
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from .reasoning_protocol import ORDER_SCHEMA, StudyStopped, digest, save
from .economy_pricing import RATES, price, MAX_INPUT_ALLOWANCE, CALIBRATION_CAP_USD
from .economy_protocol import EconomyConfig as ReasoningConfig, PROTOCOL

class Gateway:
    """One generated response per identity; bounded retries of rejected rate calls.

    The reservation survives unknown transport outcomes and interrupted calls.
    HTTP rejections refund only when no generation is known to have occurred.
    Error records omit exception text, bodies, and all but numeric rate headers.
    """
    MAX_RATE_RETRIES = 2
    RATE_COOLDOWN_SECONDS = 30.0
    RATE_COOLDOWN_MAX_SECONDS = 60.0
    TEMPORARY_RATE_CODES = frozenset(("rate_limit_exceeded", "rate_limit_error", "slow_down", "resource_unavailable"))
    QUOTA_CODES = frozenset(("insufficient_quota", "quota_exceeded", "billing_hard_limit_reached",
                            "billing_hard_limit_exceeded", "billing_not_active", "usage_limit_reached",
                            "credit_balance_exhausted", "organization_spend_limit_exceeded",
                            "project_spend_limit_exceeded", "organization_usage_limit_exceeded"))
    SAFE_ERROR_CODES = TEMPORARY_RATE_CODES | QUOTA_CODES | frozenset((
        "invalid_api_key", "model_not_found", "invalid_request_error", "permission_denied"))
    SAFE_RATE_HEADERS = frozenset(("retry-after", "x-ratelimit-limit-requests", "x-ratelimit-limit-tokens",
                                   "x-ratelimit-remaining-requests", "x-ratelimit-remaining-tokens"))

    def __init__(self, directory: str | Path, config: ReasoningConfig, client: Any = None, callback: Any = None,
                 *, recheck_rejections: bool = False):
        self.config = config.validate()
        self.directory = Path(directory)
        self.cache = self.directory / "requests"
        self.cache.mkdir(parents=True, exist_ok=True)
        self.client = client
        if client is not None and callable(getattr(client, "with_options", None)):
            self.client = client.with_options(max_retries=0, timeout=config.timeout_s)
        self.callback = callback or (lambda: None)
        saved = [(p, json.loads(p.read_text(encoding="utf-8"))) for p in self.cache.glob("*.json")]
        self.charged = sum(record.get("charge_usd", 0.0) for _, record in saved)
        self.calibration_charged = sum(record.get('charge_usd', 0.0) for _, record in saved if record.get('identity', {}).get('stage') == 'calibration')
        self.recheck_rejections = bool(recheck_rejections)
        self._access_rechecks: dict[str, int] = {}
        self._access_rechecks_consumed: set[str] = set()
        if self.recheck_rejections:
            latest = {}
            for path, record in saved:
                key = record.get("request_key")
                if not isinstance(key, str):
                    continue
                for attempt in range(self.MAX_RATE_RETRIES + 1):
                    if path == self._attempt_path(key, attempt) and (key not in latest or attempt > latest[key][0]):
                        latest[key] = (attempt, record)
            for key, (attempt, record) in latest.items():
                if attempt < self.MAX_RATE_RETRIES and self._known_zero_charge_fatal_429(record):
                    self._access_rechecks[key] = attempt
        self.sem = asyncio.Semaphore(config.concurrency)
        self.lock = asyncio.Lock()
        self._key_locks: dict[str, asyncio.Lock] = {}
        self.next_start = 0.0
        self.cooldown = 0.0
        self.cached = 0
        self.finished = 0
        self.active = 0
        self.fatal: StudyStopped | None = None

    async def _pace(self) -> None:
        while True:
            async with self.lock:
                delay = max(self.next_start, self.cooldown) - time.monotonic()
                if delay <= 0:
                    self.next_start = time.monotonic() + self.config.request_interval_s
                    return
            await asyncio.sleep(min(delay, 1.0))

    def reservation(self, messages: Any, limit: int, schema: Any) -> float:
        # UTF-8 bytes overestimate typical text tokens; overhead covers request
        # wrapping. Cached-input discounts are never assumed in reservations.
        input_allowance = len(json.dumps({"input": messages, "schema": schema}, ensure_ascii=False).encode("utf-8")) + 2048
        if input_allowance > MAX_INPUT_ALLOWANCE:
            raise StudyStopped('Input exceeds the economy protocol accounting bound; no history was silently shortened.')
        # Reserve standard-tier prices even though Flex is required. This covers
        # unknown outcomes or a provider returning an unexpected service tier.
        return 2 * (input_allowance * RATES["input"] + limit * RATES["output"]) / 1e6

    def _attempt_path(self, key: str, attempt: int) -> Path:
        return self.cache / (key + (f"_retry_{attempt}" if attempt else "") + ".json")

    @classmethod
    def _safe_error_metadata(cls, exc: Exception) -> tuple[str | None, dict[str, float]]:
        # The exception's body may contain credentials or account information.
        # Select only exact allowlisted code values; never persist the body.
        body = getattr(exc, "body", None)
        error = body.get("error", body) if isinstance(body, Mapping) else {}
        if not isinstance(error, Mapping):
            error = {}
        raw_codes = (getattr(exc, "code", None), error.get("code"))
        code = next((value for value in raw_codes if isinstance(value, str) and value in cls.SAFE_ERROR_CODES), None)
        if code is None:
            raw_types = (getattr(exc, "type", None), error.get("type"))
            # A quota type always supplies a conservative permanent diagnosis.
            # A generic rate type must not turn an unknown supplied code into
            # a retryable rejection; it is allowed only when code is absent.
            code = next((value for value in raw_types if isinstance(value, str) and value in cls.QUOTA_CODES), None)
            if code is None and not any(value is not None and value != "" for value in raw_codes):
                code = next((value for value in raw_types if isinstance(value, str) and value in cls.SAFE_ERROR_CODES), None)
        raw_headers = getattr(getattr(exc, "response", None), "headers", {}) or {}
        headers = {}
        for name in cls.SAFE_RATE_HEADERS:
            try:
                value = float(raw_headers.get(name))
            except (TypeError, ValueError, AttributeError):
                continue
            if math.isfinite(value) and value >= 0:
                headers[name] = value
        return code, headers

    async def _rate_cooldown(self, record: Mapping[str, Any]) -> None:
        retry_after = (record.get("rate_limit_headers") or {}).get("retry-after", 0.0)
        delay = max(self.RATE_COOLDOWN_SECONDS, min(self.RATE_COOLDOWN_MAX_SECONDS, retry_after))
        async with self.lock:
            self.cooldown = max(self.cooldown, time.monotonic() + delay)

    @staticmethod
    def _historical_ambiguous_rate(record: Mapping[str, Any], attempt: int) -> bool:
        # One diagnostic recheck for old zero-charge 429 records that predate
        # safe error-code recording. New ambiguous errors contain error_code
        # (even when None), so they do not gain this migration exception.
        return (attempt == 0 and record.get("status") == "api_error" and record.get("http_status") == 429
                and record.get("error_category") == "rate_or_quota" and "error_code" not in record
                and record.get("charge_usd") == 0 and not record.get("usage_observed"))

    @staticmethod
    def _known_zero_charge_fatal_429(record: Mapping[str, Any]) -> bool:
        return (record.get("status") == "api_error" and record.get("fatal_error")
                and record.get("http_status") == 429 and record.get("charge_usd") == 0
                and not record.get("usage_observed") and not record.get("usage")
                and record.get("error_category") in ("quota_or_billing", "unknown_rate_or_quota", "rate_or_quota"))

    def _access_recheck_available(self, record: Mapping[str, Any], attempt: int) -> bool:
        key = record.get("request_key")
        return (self._known_zero_charge_fatal_429(record) and self._access_rechecks.get(key) == attempt
                and key not in self._access_rechecks_consumed and attempt < self.MAX_RATE_RETRIES)

    async def request(self, identity: Any, messages: Any, limit: int, schema: Any = ORDER_SCHEMA, synthetic: str | None = None) -> dict[str, Any]:
        for attempt in range(self.MAX_RATE_RETRIES + 1):
            record = await self._request_once(identity, messages, limit, schema, synthetic, attempt)
            temporary = (record.get("status") == "api_error" and record.get("http_status") == 429
                         and record.get("error_code") in self.TEMPORARY_RATE_CODES
                         and record.get("charge_usd") == 0 and not record.get("usage_observed"))
            historical_probe = self._historical_ambiguous_rate(record, attempt)
            cached_after_rejection = (self._known_zero_charge_fatal_429(record) and attempt < self.MAX_RATE_RETRIES
                                      and self._attempt_path(record["request_key"], attempt + 1).exists())
            access_probe = self._access_recheck_available(record, attempt)
            if not (temporary or historical_probe or cached_after_rejection or access_probe):
                return record
            if attempt >= self.MAX_RATE_RETRIES:
                self.fatal = StudyStopped("Temporary API rate limit persisted after two identical rejected-call retries; all attempts are saved.")
                raise self.fatal
            # Completed retry chains resume without a new delay or generation.
            if not self._attempt_path(record["request_key"], attempt + 1).exists():
                if access_probe:
                    self._access_rechecks_consumed.add(record["request_key"])
                await self._rate_cooldown(record)
        raise StudyStopped("Bounded rate-retry chain exhausted.")

    async def _request_once(self, identity: Any, messages: Any, limit: int, schema: Any,
                            synthetic: str | None, transport_attempt: int) -> dict[str, Any]:
        if type(limit) is not int or limit < 16 or limit > self.config.initial_tokens:
            raise ValueError("Request allowance must be an integer within the protocol reference allowance.")
        specification = {"protocol": PROTOCOL, "identity": identity, "messages": messages, "limit": limit,
                         "schema": schema, "requested_model": self.config.model, "reasoning": {"effort": self.config.effort},
                         "mode": self.config.mode, "config_fingerprint": self.config.fingerprint(),
                         "service_tier": "flex"}
        key = digest(specification)
        async with self._key_locks.setdefault(key, asyncio.Lock()):
            path = self._attempt_path(key, transport_attempt)
            if path.exists():
                record = json.loads(path.read_text(encoding="utf-8"))
                if record["status"] == "pending":
                    raise StudyStopped("Saved pending request has unknown usage/outcome; inspect it before resuming. No request was resubmitted.")
                later_cached_attempt = (self._known_zero_charge_fatal_429(record) and transport_attempt < self.MAX_RATE_RETRIES
                                        and self._attempt_path(key, transport_attempt + 1).exists())
                if (record.get("fatal_error") and not self._historical_ambiguous_rate(record, transport_attempt)
                        and not later_cached_attempt and not self._access_recheck_available(record, transport_attempt)):
                    raise StudyStopped("Saved fatal API rejection; inspect configuration. No request was resubmitted.")
                self.cached += 1
                self.finished += 1
                self.callback()
                return record
            if self.fatal:
                raise self.fatal
            record = dict(specification, request_key=key, created_utc=datetime.now(timezone.utc).isoformat(),
                          requested_effort=self.config.effort, max_retries=0, timeout_s=self.config.timeout_s,
                          transport_attempt=transport_attempt, local_rate_retries_max=self.MAX_RATE_RETRIES)
            if self.config.mode == "offline":
                record.update(status="ok", response_status="completed", text=synthetic or "", synthetic=True,
                              returned_model=None, response=None, refused=False, incomplete_reason=None,
                              usage={"input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0,
                                     "reasoning_tokens": 0, "nonreasoning_output_tokens_proxy": 0},
                              usage_observed=False, charge_usd=0.0, elapsed_s=0.0,
                              note="SYNTHETIC software benchmark; no GPT call, hidden reasoning, or human validation.")
                save(path, record)
                self.finished += 1
                self.callback()
                return record
            async with self.sem:
                if self.client is None:
                    raise StudyStopped("An explicit live API client is required in API mode.")
                await self._pace()
                reserve = self.reservation(messages, limit, schema)
                is_calibration = identity.get('stage') == 'calibration'
                async with self.lock:
                    if self.fatal:
                        raise self.fatal
                    if is_calibration and self.calibration_charged + reserve > CALIBRATION_CAP_USD:
                        self.fatal = StudyStopped('Calibration cost guard: at most $0.18 is allocated to the fresh screen. No games purchased.')
                        raise self.fatal
                    if self.charged + reserve > self.config.budget_usd:
                        self.fatal = StudyStopped(f"Local cost guard: ${self.charged:.4f} charged/reserved plus ${reserve:.4f} would exceed budget ${self.config.budget_usd:.4f}.")
                        raise self.fatal
                    self.charged += reserve
                    if is_calibration:
                        self.calibration_charged += reserve
                record.update(status="pending", charge_usd=reserve, reserved_usd=reserve, synthetic=False)
                save(path, record)
                start = time.monotonic()
                self.active += 1
                self.callback()
                try:
                    kwargs = {"model": self.config.model, "input": messages, "reasoning": {"effort": "high"},
                              "max_output_tokens": limit, "store": False, "service_tier": "flex"}
                    if schema is not None:
                        kwargs["text"] = {"format": {"type": "json_schema", "name": "answer", "strict": True, "schema": schema}}
                    response = await self.client.responses.create(**kwargs)
                    raw = response.model_dump(mode="json") if hasattr(response, "model_dump") else dict(response)
                    raw_usage = raw.get("usage")
                    usage = raw_usage if isinstance(raw_usage, dict) else {}
                    output_details = usage.get("output_tokens_details") or {}
                    u = {"input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0),
                         "cached_input_tokens": (usage.get("input_tokens_details") or {}).get("cached_tokens", 0),
                         "reasoning_tokens": output_details.get("reasoning_tokens", 0)}
                    complete_usage = (all(k in usage for k in ("input_tokens", "output_tokens"))
                                      and "reasoning_tokens" in output_details)
                    valid_usage = all(type(v) is int and v >= 0 for v in u.values()) and u["reasoning_tokens"] <= u["output_tokens"] and u["cached_input_tokens"] <= u["input_tokens"]
                    u["nonreasoning_output_tokens_proxy"] = u["output_tokens"] - u["reasoning_tokens"] if valid_usage else None
                    text = "".join(c.get("text", "") for o in raw.get("output", []) if o.get("type") == "message"
                                   for c in o.get("content", []) if c.get("type") == "output_text")
                    refused = any(c.get("type") == "refusal" for o in raw.get("output", []) for c in o.get("content", []))
                    protocol_errors = []
                    if raw.get("model") != self.config.model:
                        protocol_errors.append("returned_model_mismatch")
                    if raw.get('service_tier') != 'flex':
                        protocol_errors.append('unexpected_service_tier')
                    if not complete_usage or not valid_usage:
                        protocol_errors.append("missing_or_invalid_usage")
                    if valid_usage and u["output_tokens"] > limit:
                        protocol_errors.append("output_exceeds_allowance")
                    record.update(status="protocol_error" if protocol_errors else "ok", response_status=raw.get("status"),
                                  returned_model=raw.get("model"), returned_service_tier=raw.get('service_tier'), response=raw, text=text, refused=refused,
                                  incomplete_reason=(raw.get("incomplete_details") or {}).get("reason"), usage=u,
                                  usage_observed=complete_usage and valid_usage, protocol_errors=protocol_errors,
                                  elapsed_s=time.monotonic() - start)
                    if valid_usage and all(k in usage for k in ("input_tokens", "output_tokens")):
                        actual = price(u) * (1 if raw.get('service_tier') == 'flex' else 2)
                        async with self.lock:
                            self.charged += actual - reserve
                            if is_calibration:
                                self.calibration_charged += actual - reserve
                        record["charge_usd"] = actual
                    save(path, record)
                    self.finished += 1
                    return record
                except asyncio.CancelledError:
                    # Persisted pending reservation remains: do not silently resend.
                    raise
                except Exception as exc:
                    http = getattr(exc, "status_code", None)
                    error_code, rate_headers = self._safe_error_metadata(exc)
                    # Record only safe categories, never exception text or bodies.
                    category = ("authentication" if http in (401, 403) else "configuration" if http in (400, 404, 422)
                                else "quota_or_billing" if http == 429 and error_code in self.QUOTA_CODES
                                else "temporary_rate" if http == 429 and error_code in self.TEMPORARY_RATE_CODES
                                else "unknown_rate_or_quota" if http == 429 else "server" if isinstance(http, int) and http >= 500
                                else "timeout" if "Timeout" in type(exc).__name__ else "connection" if "Connection" in type(exc).__name__
                                else "unexpected_api_error")
                    known_rejection = http in (400, 401, 403, 404, 422, 429)
                    if known_rejection:
                        async with self.lock:
                            self.charged -= reserve
                            if is_calibration:
                                self.calibration_charged -= reserve
                        record["charge_usd"] = 0.0
                    fatal = category in ("authentication", "configuration", "quota_or_billing", "unknown_rate_or_quota")
                    record.update(status="api_error", error_category=category, http_status=http if isinstance(http, int) else None,
                                  fatal_error=fatal, usage_observed=False, response_status=None, text="", response=None,
                                  returned_model=None, usage=None, elapsed_s=time.monotonic() - start,
                                  error_code=error_code, rate_limit_headers=rate_headers,
                                  rate_retry_exhausted=category == "temporary_rate" and transport_attempt >= self.MAX_RATE_RETRIES)
                    save(path, record)
                    self.finished += 1
                    if category == "temporary_rate":
                        await self._rate_cooldown(record)
                    if fatal:
                        self.fatal = StudyStopped(f"API rejected the call ({category}, HTTP {http}); safe provenance was saved. This rejection will not be retried.")
                        raise self.fatal from None
                    return record
                finally:
                    self.active -= 1
                    self.callback()
