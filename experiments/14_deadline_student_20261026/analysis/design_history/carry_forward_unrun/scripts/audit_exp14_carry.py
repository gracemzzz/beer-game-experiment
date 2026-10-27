"""Project only public participant messages and verify literal carry-study inputs.

No private reasoning/system/developer trace is exported. Mechanical matching is
separate from the researcher's attributed procedure review.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_agent_public_trace_v5 import project, CMD
from audit_exp14_agent import audit as accepted_audit, objects


def audit(public, folder):
    report = accepted_audit(public, folder)
    result = json.loads((folder / "RESULT.json").read_text(encoding="utf-8"))
    attempts = [e for e in result["events"] if e["kind"] in ("submission_accepted", "submission_rejected")]
    outputs = {e.get("call_id"): e for e in public if e["type"] in ("custom_tool_call_output", "function_call_output")}
    matched = []
    for event in public:
        if event["type"] not in ("custom_tool_call", "function_call"):
            continue
        text = event.get("input", event.get("arguments", ""))
        commands = [json.loads(m.group(1)) for m in CMD.finditer(text)]
        if event.get("name") == "exec_command":
            try:
                commands = [json.loads(text)["cmd"]]
            except (ValueError, KeyError):
                pass
        actual_outputs = objects(outputs.get(event.get("call_id"), {}).get("output"))
        for command in commands:
            if " submit " not in command:
                continue
            ident = re.search(r"--decision-id\s+['\"]?([0-9a-f]+)", command)
            literal = re.search(r"@'\r?\n(.*?)\r?\n'@", command, re.S)
            if not ident or not literal:
                report["issues"].append(dict(record=event["record"], problem="Submission is not the required literal here-string"))
                continue
            candidates = [(i, e) for i, e in enumerate(attempts) if i not in matched
                          and e["decision_id"] == ident.group(1)
                          and e["literal_input_text"].strip() == literal.group(1).strip()]
            if not candidates:
                report["issues"].append(dict(record=event["record"], problem="Literal accepted/rejected attempt absent from controller record"))
                continue
            i, attempt = candidates[0]
            acknowledgments = [x for x in actual_outputs if x.get("accepted") is attempt["accepted"]]
            if not acknowledgments:
                report["issues"].append(dict(record=event["record"], problem="No actual matching admission acknowledgment"))
                continue
            matched.append(i)
    if len(matched) != len(attempts):
        report["issues"].append(dict(problem="Not all actor attempts, including late inputs, match the public transcript"))
    opened = sum(e["kind"] == "display_opened" for e in result["events"])
    if report["full_displays_seen"] != opened:
        report["issues"].append(dict(problem="Not all open opportunities match complete public displays"))
    report.update(total_actor_attempts=len(attempts), matched_actor_attempts=len(matched),
                  opened_opportunities=opened,
                  synthetic_game_packets=sum(w.get("action_source") != "model_on_time" for w in result["weeks"]),
                  synthetic_probe_answers=sum(v != "model_on_time" for v in result.get("probe_answer_sources", {}).values()),
                  scientific_interpretation="Applied policy answers and actual actor observations remain distinct")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    raw = args.session.read_bytes()
    public, settings, excluded = project(raw)
    data = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in public).encode("utf-8")
    report = audit(public, args.run)
    report.update(created_utc=datetime.now(timezone.utc).isoformat(), requested_settings=settings,
        result_sha256=hashlib.sha256((args.run / "RESULT.json").read_bytes()).hexdigest(),
        transcript_sha256=hashlib.sha256(data).hexdigest(), source_session_sha256=hashlib.sha256(raw).hexdigest(),
        excluded_nonpublic_counts=excluded)
    for path, value in ((args.run / "PUBLIC_TRANSCRIPT.jsonl", data),
                        (args.run / "PUBLIC_PROCEDURE_REVIEW.json", (json.dumps(report, indent=2) + "\n").encode("utf-8"))):
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(value)
    print(json.dumps({k: v for k, v in report.items() if k not in ("commands", "matches", "file_reads", "requested_settings")}, indent=2))


if __name__ == "__main__":
    main()
