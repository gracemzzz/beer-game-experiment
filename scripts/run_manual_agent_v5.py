"""Local transport for one model-chosen page at a time; never chooses an order.

Trusted state pickles are created ONLY by this script in prepared run folders.
Intake of user model results remains JSON-only in the separate analysis module.
"""
from pathlib import Path
import argparse
import hashlib
import json
import pickle
import sys
from datetime import datetime, timezone


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("init", "show", "submit", "status"))
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    folder = args.run.resolve()
    case = json.loads((folder / "CASE.json").read_text(encoding="utf-8"))
    for name, expected in case["helper_hashes"].items():
        if sha(folder / "helper" / name) != expected:
            raise ValueError("Prepared helper bytes changed")
    if sha(Path(__file__)) != case["transport_sha256"]:
        raise ValueError("Prepared local transport changed")
    sys.path.insert(0, str(folder / "helper"))
    from batch_runner import Batch
    state_path = folder / "controller_state.pkl"
    if args.action == "init":
        if state_path.exists():
            raise ValueError("Run already initialized; use show or status")
        run = Batch(case["model_slot"], case["batch_id"])
        before = None
        after = run.display()
        raw_choices = None
        choices = None
    else:
        with state_path.open("rb") as stream:
            run = pickle.load(stream)
        if args.action == "status":
            print(json.dumps(dict(batch_id=run.batch_id, condition=run.active_arm(),
                completed_pages=len(run.page_events), complete=run.active_arm() is None)))
            return
        before = run.display()
        if args.action == "show":
            print(json.dumps(before, separators=(",", ":"), allow_nan=False))
            return
        raw_choices = sys.stdin.read()
        choices = json.loads(raw_choices)
        after = run.submit(choices)
    index = len(run.page_events)
    receipt = dict(index=index, action=args.action, utc=datetime.now(timezone.utc).isoformat(),
                   literal_input_text=raw_choices, choices=choices, display_before=before,
                   display_after=after, requested_model=case["requested_model"],
                   requested_effort=case["requested_effort"], source="local execution record; not full assistant transcript")
    steps = folder / "steps"
    steps.mkdir(exist_ok=True)
    target = steps / f"{index:04d}.json"
    with target.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, separators=(",", ":"), allow_nan=False)
    temporary = folder / "controller_state.next"
    temporary.write_bytes(pickle.dumps(run))
    temporary.replace(state_path)
    result = run.export(require_complete=False)
    (folder / "RESULT.json").write_text(json.dumps(result, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    (folder / "STATUS.json").write_text(json.dumps(dict(case_id=case["case_id"],
        requested_model=case["requested_model"], requested_effort=case["requested_effort"],
        completed_pages=index, planned_pages=224, complete=result["complete"],
        completed_weeks={a: g["completed_weeks"] for a, g in result["games"].items()},
        next_condition=run.active_arm(), updated_utc=receipt["utc"]), indent=2), encoding="utf-8")
    print(json.dumps(after, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
