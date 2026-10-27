"""Local experiment-14 carry-forward transport. No API calls.

Usage: init/show/status --run PATH; submit --run PATH --decision-id ID < choices.json
CASE.json must fingerprint controller/transport/physics via source_hashes.
Only this transport creates the trusted private pickle. Never import a supplied
pickle. Immutable event JSON records and atomic result/status files accompany it.
The clock opens only at show. Timeout state is persisted on next access, while
every submit checks complete stdin reception against the original deadline.
Handled current timeouts return exit 0 with accepted=false and
continue_allowed=true; stale/invalid unhandled submissions return exit 2.
"""
from pathlib import Path
import argparse
import json
import os
import pickle
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_carry import CarryCase, clock_point, digest, verify_sources


def atomic_bytes(path, data):
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def json_bytes(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def save(folder, state):
    events = folder / "events"
    events.mkdir(exist_ok=True)
    for event in state.events:
        target = events / ("%06d.json" % event["index"])
        data = json_bytes(event)
        if target.exists():
            if target.read_bytes() != data:
                raise ValueError("Immutable event bytes changed")
        else:
            with target.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
    atomic_bytes(folder / "controller_state.pkl", pickle.dumps(state, protocol=pickle.HIGHEST_PROTOCOL))
    atomic_bytes(folder / "RESULT.json", json_bytes(state.export()))
    atomic_bytes(folder / "STATUS.json", json_bytes(state.status()))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("init", "show", "submit", "status"))
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--decision-id")
    args = parser.parse_args(argv)
    if args.action == "submit" and not args.decision_id:
        parser.error("submit requires --decision-id from the current display")
    # Capture the complete payload's arrival before source checks, parsing, or validation.
    raw = sys.stdin.read() if args.action == "submit" else None
    received = clock_point() if args.action == "submit" else None
    folder = args.run.resolve(strict=True)
    lock = folder / ".exp14_carry_transport.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise RuntimeError("Case transport is locked; do not reset a live or interrupted case")
    try:
        os.close(descriptor)
        case = json.loads((folder / "CASE.json").read_text(encoding="utf-8"))
        verify_sources(case)
        state_path = folder / "controller_state.pkl"
        if args.action == "init":
            if state_path.exists() or (folder / "events").exists() or (folder / "RESULT.json").exists():
                raise ValueError("Case already initialized or interrupted; restarting is forbidden")
            state = CarryCase(case)
            result = state.status()
        else:
            with state_path.open("rb") as stream:
                state = pickle.load(stream)
            if not isinstance(state, CarryCase) or state.case_hash != digest(case):
                raise ValueError("CASE or trusted controller state changed")
            event_files = sorted((folder / "events").glob("*.json"))
            if len(event_files) != len(state.events):
                raise ValueError("Interrupted or inconsistent event/state write; scientific review required")
            for path, event in zip(event_files, state.events):
                if path.read_bytes() != json_bytes(event):
                    raise ValueError("Immutable event bytes changed")
            if args.action == "submit":
                result = state.submit(raw, args.decision_id, received=received)
            elif args.action == "show":
                result = state.show()
            else:
                result = state.status(clock=clock_point())
        save(folder, state)
        print(json.dumps(result, separators=(",", ":"), ensure_ascii=False, allow_nan=False), flush=True)
        return (2 if args.action == "submit" and not result["accepted"]
                and not result.get("continue_allowed", False) else 0)
    finally:
        lock.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
