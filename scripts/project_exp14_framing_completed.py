"""Save public-only traces for finished framing cases; never approve adherence.

Session discovery reads filenames and public session headers only. Projection
uses the existing whitelist; hidden reasoning/instructions are never exported.
"""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys
from audit_agent_public_trace_v5 import project

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/14_deadline_student_20261026"


def main():
    sessions = Path.home() / ".codex/sessions"
    found = subprocess.run(["rg", "-l", "--fixed-strings", "exp14_sf3_", str(sessions)],
                           capture_output=True, text=True, encoding="utf-8")
    if found.returncode not in (0, 1):
        raise RuntimeError(found.stderr)
    indexed = {}
    for filename in found.stdout.splitlines():
        path = Path(filename)
        try:
            with path.open(encoding="utf-8") as stream:
                header = json.loads(stream.readline())
            source = header.get("payload", {}).get("source", {})
            agent = source.get("subagent", {}).get("thread_spawn", {}).get("agent_path") if isinstance(source, dict) else None
            if agent and "/exp14_sf3_" in agent:
                if agent in indexed:
                    raise ValueError("Multiple session files for one actor; review before projection: " + agent)
                indexed[agent] = path
        except (OSError, json.JSONDecodeError):
            continue
    projected, existing = [], 0
    for stage in ("development", "main"):
        for result_path in sorted((EXP / "data/student_framing_v3" / stage).glob("*/RESULT.json")):
            result = json.loads(result_path.read_text(encoding="utf-8"))
            if not result.get("complete") and not result.get("stopped"):
                continue
            folder = result_path.parent
            if (folder / "PUBLIC_PROCEDURE_REVIEW.json").exists():
                saved = json.loads((folder / "PUBLIC_PROCEDURE_REVIEW.json").read_text(encoding="utf-8"))
                if saved["result_sha256"] != sha256(result_path.read_bytes()).hexdigest():
                    raise ValueError("Result changed after immutable projection: " + str(folder))
                existing += 1
                continue
            receipts = [json.loads(line) for line in (folder / "ORCHESTRATOR_MESSAGES.jsonl").read_text(encoding="utf-8").splitlines()]
            agent = receipts[0]["agent"]
            if agent not in indexed:
                raise ValueError("No exact session header for launched actor: " + agent)
            public, _, _ = project(indexed[agent].read_bytes())
            messages = [e for e in public if e.get("type") == "public_message" and e.get("role") == "assistant"]
            final = messages[-1] if messages else {}
            # Some local session formats omit the channel even on the final
            # message. Require its protocol-mandated result path and recall.
            if not (final.get("channel") in (None, "final") and "RESULT.json" in final.get("text", "")
                    and "fictional_student_seconds" in final.get("text", "")):
                # RESULT may finish just before the participant's final record.
                # Wait for that final public message before freezing its trace.
                continue
            output = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/audit_exp14_agent.py"),
                       "--session", str(indexed[agent]), "--run", str(folder)],
                       capture_output=True, text=True, encoding="utf-8")
            if output.returncode:
                raise RuntimeError(output.stderr)
            audit = json.loads((folder / "PUBLIC_PROCEDURE_REVIEW.json").read_text(encoding="utf-8"))
            projected.append(dict(run=folder.name, accepted=audit["accepted_decisions"],
                matched=audit["matched_public_literal_decisions"], full_displays=audit["full_displays_seen"],
                issues=audit["issues"], unrecognized_calls=audit["unrecognized_calls"]))
    index_path = EXP / "analysis/student_framing_v3/SESSION_INDEX.json"
    data = (json.dumps([dict(agent=agent, session_path=str(path)) for agent, path in sorted(indexed.items())], indent=2) + "\n").encode("utf-8")
    if index_path.exists() and index_path.read_bytes() != data:
        raw = index_path.read_bytes()
        old = index_path.parent / "session_index_history" / (sha256(raw).hexdigest() + ".json")
        old.parent.mkdir(parents=True, exist_ok=True)
        if not old.exists():
            old.write_bytes(raw)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_bytes(data)
    print(json.dumps(dict(projected=projected, previously_projected=existing,
                         automatic_scientific_approval=False), indent=2))


if __name__ == "__main__":
    main()
