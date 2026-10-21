"""Bounded file-save retries for Windows readers; no model-request retries.

Installation changes in-memory function references only. Scientific source files,
model settings, cached requests, and their fingerprints stay unchanged.
"""
from __future__ import annotations

import functools
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


BACKOFF_SECONDS = (0.02, 0.05, 0.10, 0.20, 0.40, 0.80)


def _retry_settings() -> dict[str, Any]:
    return {
        "exception_retried": "PermissionError",
        "backoff_seconds": list(BACKOFF_SECONDS),
        "maximum_file_save_attempts": len(BACKOFF_SECONDS) + 1,
        "maximum_backoff_seconds": sum(BACKOFF_SECONDS),
        "patched_references": ["beergame_study.reasoning_protocol.save", "beergame_study.student_study.save"],
        "api_requests_retried": False,
        "scientific_settings_changed": False,
    }


def install_windows_file_retry() -> dict[str, Any]:
    """Install one shared wrapper; repeated installations never nest retries."""
    from . import reasoning_protocol, student_study

    original = reasoning_protocol.save
    if getattr(original, "_operational_save_retry", False) is True:
        student_study.save = original
        return _retry_settings()

    @functools.wraps(original)
    def retry_save(path: str | Path, value: Any) -> None:
        for attempt in range(len(BACKOFF_SECONDS) + 1):
            try:
                return original(path, value)
            except PermissionError:
                if attempt >= len(BACKOFF_SECONDS):
                    raise
                time.sleep(BACKOFF_SECONDS[attempt])

    retry_save._operational_save_retry = True
    retry_save._operational_save_retry_original = original
    reasoning_protocol.save = retry_save
    student_study.save = retry_save
    return _retry_settings()


def record_operational_io(directory: str | Path, settings: Mapping[str, Any] | None = None) -> Path:
    """Append separate implementation/config provenance for this invocation.

    Caller settings describe the actual resume's operating configuration. They
    never override fixed retry behavior. Supply configuration values, not keys or
    credentials. Earlier invocation records and cached responses are untouched.
    """
    from . import reasoning_protocol

    source = Path(__file__).read_bytes()
    module_hash = hashlib.sha256(source).hexdigest()
    archive = Path(directory) / "operational_io"
    archive.mkdir(parents=True, exist_ok=True)
    implementation = archive / ("implementation_" + module_hash + ".py")
    if implementation.exists():
        if implementation.read_bytes() != source:
            raise RuntimeError("Operational implementation archive differs; no evidence overwritten.")
    else:
        implementation.write_bytes(source)
    created = datetime.now(timezone.utc)
    record = {
        "created_utc": created.isoformat(),
        "implementation_sha256": module_hash,
        "hash_definition": "SHA-256 of source bytes",
        "implementation_copy": implementation.name,
        "retry_behavior": _retry_settings(),
        "run_settings": json.loads(json.dumps(dict(settings or {}), allow_nan=False)),
        "installed": getattr(reasoning_protocol.save, "_operational_save_retry", False) is True,
        "note": "Operational file-I/O retry only. No API retries, new observations, or changes to scientific source/settings.",
    }
    name = created.strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex + ".json"
    target = archive / name
    reasoning_protocol.save(target, record)
    return target
