"""Export the completed Claude v4 and GPT v3 prompt catalogs from saved evidence only.

Uses only the standard library; never imports an API client or the study runner.
The default is deliberately pinned to the completed run requested on 17 Oct 2026.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "claude_api_fd5533fef5828d96"
ROLES = ("retailer", "wholesaler", "distributor", "factory")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def raw_hashes(run):
    return {p.relative_to(run).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(run.rglob("*")) if p.is_file()}


def literal(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name
                                               for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f"Missing frozen constant: {name}")


def frozen_function(tree, name, namespace):
    """Load only the specified pure formatter, without executing module imports."""
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<frozen formatter>", "exec"), namespace)
    return namespace[name]


def code(value, language="json"):
    content = json.dumps(value, indent=2, ensure_ascii=False) if not isinstance(value, str) else value
    return f"```{language}\n{content}\n```\n"


def export(run):
    run = run.resolve()
    require(run.parent == (ROOT / "data/runs").resolve(), "Select a run directly under data/runs.")
    report = ROOT / "reports" / run.name
    manifest = read_json(run / "manifest.json")
    prefix = {"student-high-claude-revision-v4": "claude", "student-high-economy-revision-v3": "economy"}.get(manifest["protocol"])
    require(prefix is not None, "Exporter supports the completed Claude v4 and GPT v3 protocols.")
    require(manifest["config"]["mode"] == "api", "Select completed API evidence.")
    require(read_json(run / "progress.json")["stage"] == "complete", "Run must be complete.")
    before = raw_hashes(run)
    provenance = read_json(report / "findings_provenance.json")
    baseline = {name.replace("\\", "/"): value for name, value in provenance["raw_sha256"].items()}
    require(before == baseline, "Raw evidence differs from the completed findings audit.")
    source = run / "source_implementation"
    for name, expected in manifest["source_hashes"].items():
        require(digest((source / name).read_text(encoding="utf-8")) == expected,
                f"Frozen source hash mismatch: {name}")
    protocol_text = (source / f"{prefix}_protocol.py").read_text(encoding="utf-8")
    protocol = ast.parse(protocol_text)
    common, task = literal(protocol, "COMMON"), literal(protocol, "TASK")
    require(common == manifest["common_prompt"], "Common prompt differs from manifest.")
    profiles = manifest["student_profiles"]
    for profile_id, profile in profiles.items():
        require(profile == read_json(source / "profiles" / f"{profile_id}.json"), "Profile snapshot differs.")
    formatter = frozen_function(protocol, "messages", {
        "json": json, "COMMON": common, "TASK": task,
        "PROFILE_IDS": tuple(profiles), "profiles": lambda: profiles})
    wire_formatter = None
    if prefix == "claude":
        transport = ast.parse((source / "claude_transport.py").read_text(encoding="utf-8"))
        wire_formatter = frozen_function(transport, "request_parameters", {"copy": copy})
    study = ast.parse((source / f"{prefix}_study.py").read_text(encoding="utf-8"))
    question_dicts = [n for n in ast.walk(study) if isinstance(n, ast.Dict)
                      and any(isinstance(k, ast.Constant) and k.value == "questions" for k in n.keys)]
    require(len(question_dicts) == 1, "Unexpected rules prompt construction.")
    question_dict = question_dicts[0]
    questions = ast.literal_eval(next(v for k, v in zip(question_dict.keys, question_dict.values)
                                     if isinstance(k, ast.Constant) and k.value == "questions"))
    schema_tree = ast.parse((source / "reasoning_protocol.py").read_text(encoding="utf-8"))
    rules_schema = literal(schema_tree, "RULES_SCHEMA")
    order_schema = literal(schema_tree, "ORDER_SCHEMA")
    require(order_schema == manifest["order_schema"], "Order schema differs from manifest.")
    records = [read_json(p) for p in sorted((run / "requests").glob("*.json"))]
    require(records, "No saved requests.")
    records.sort(key=lambda r: (r["created_utc"], r["request_key"]))
    index = {digest(r["identity"]): r for r in records}
    require(len(index) == len(records), "Unexpected repeated request identities.")
    config = manifest["config"]
    plan = read_json(run / "plan.json")
    bank = {c["case_id"]: c for c in manifest["calibration_bank"]}
    probes = {c["case_id"]: c for c in manifest["probes"]}
    counts = Counter()
    for record in records:
        ident = record["identity"]
        stage, phase = ident["stage"], ident.get("phase")
        require((stage, phase) in {("rules", None), ("calibration", "initial"),
                ("calibration", "revision"), ("probe", "initial"), ("probe", "revision"),
                ("game", "initial"), ("game", "revision")}, "Uncatalogued request type.")
        counts[stage, phase] += 1
        require(record["status"] == "ok" and record["response_status"] == "completed",
                "Unexpected incomplete response.")
        require(not record["synthetic"] and record["returned_model"] == config["model"],
                "Unexpected synthetic response or model.")
        limit = config["revision_tokens"] if phase == "revision" else config["initial_tokens"]
        require(record["limit"] == limit and record["requested_effort"] == config["effort"] == "high",
                "Unexpected generation settings.")
        schema = rules_schema if stage == "rules" else order_schema
        require(record["schema"] == schema, "Unexpected response schema.")
        messages = record["messages"]
        require(len(messages) == 2 and messages[0] == {"role": "system", "content": common}
                and messages[1]["role"] == "user", "Unexpected message structure.")
        payload = json.loads(messages[1]["content"])
        profile = payload["participant_profile"]
        require(profile == profiles[profile["id"]], "Uncatalogued profile.")
        if stage == "rules":
            role = ident["role"]
            assigned = plan["profile_assignments"][ident["block"]][ROLES.index(role)]
            expected = dict(role=role, participant_profile=profiles[assigned], questions=questions)
            require(messages[1]["content"] == json.dumps(expected), "Rules prompt differs from source.")
        else:
            previous = payload.get("submitted_order") if phase == "revision" else None
            state = payload["current_state"] | {"profile_id": profile["id"]}
            history = payload["past_rounds"]
            require(formatter(state, history, previous) == messages, "Order prompt differs from source.")
            if stage == "calibration":
                case = bank[ident["item"]]
                require(formatter(case["state"], case["history"], previous) == messages,
                        "Calibration payload differs from frozen bank.")
            else:
                role = payload["current_state"]["role"]
                assigned = plan["profile_assignments"][ident["block"]][ROLES.index(role)]
                require(profile["id"] == assigned, "Profile differs from frozen block assignment.")
                if stage == "probe":
                    case = probes[ident["item"]]
                    require(formatter(case["state"] | {"profile_id": assigned}, [], previous) == messages,
                            "Probe differs from frozen state.")
                else:
                    require(role == ident["role"] and state["week"] == ident["week"], "Game identity differs.")
                    require(len(history) == state["week"] - 1, "Game history was shortened.")
            if phase == "revision":
                initial_id = ident | {"phase": "initial"}
                if digest(initial_id) not in index:
                    initial_id["condition"] = "shared"
                initial = index[digest(initial_id)]
                require(previous == json.loads(initial["text"])["order"], "Revision choice differs from initial.")
                require(formatter(state, history) == initial["messages"], "Revision has changed state/history.")
        if wire_formatter is not None:
            require(record["api_request"] == wire_formatter(config["model"], messages, limit, schema),
                    "Native request differs from frozen transport.")
        else:
            require(record["reasoning"] == {"effort": "high"} and record["service_tier"] == "flex"
                    and record["returned_service_tier"] == "flex", "Unexpected GPT settings.")

    base = f"../../data/runs/{run.name}"
    provider = "Claude" if prefix == "claude" else "GPT"
    model_label = "Claude Haiku 5.5" if prefix == "claude" else "GPT-6 Luna Flex"
    filename = f"{provider.upper()}_API_PROMPTS.md"
    notebook = "05_claude_deliberation_study.ipynb" if prefix == "claude" else "04_personality_deliberation_study.ipynb"
    rules = next(r for r in records if r["identity"] == {"stage": "rules", "block": 0, "role": "retailer"})
    initial = next(r for r in records if r["identity"] == {
        "stage": "probe", "block": 0, "item": "retailer-low", "condition": "shared", "phase": "initial"})
    revision = index[digest(initial["identity"] | {"condition": "adequate", "phase": "revision"})]

    def saved_message(record):
        return (f"[Saved API message]({base}/requests/{record['request_key']}.json).\n\n"
                + code(json.loads(record["messages"][1]["content"])))

    parts = [f"# {provider} run — exact API prompts\n\n"
             f"**Model:** {model_label} (`{config['model']}`) · **Effort:** high · **Run date:** 11 October 2026.\n\n"
             "Each call combines the **system prompt** below with **one user message**. "
             "The boxes contain saved prompt text; JSON indentation is expanded for readability, with wording and values unchanged. "
             "Sections 3–5 show one actual message for each user-message form. "
             "Profiles, states and histories vary between calls.\n\n"
             "| Experiment section | Prompts used |\n| --- | --- |\n"
             "| Calibration | System + assigned profile + initial decision, then revision |\n"
             "| Rules check before games | System + assigned profile + rules questions |\n"
             "| Matched-state probes and weekly games | System + assigned profile + initial decision; adequate condition also gets revision |\n\n"
             "## 1. Shared system prompt\n\n"
             "Used in every API call. Defines the fictional student, game rules and decision objective.\n\n"
             + code(common, "text") + "\n"
             "## 2. Student personality profiles\n\n"
             "One complete profile is included in each user message as `participant_profile`. "
             "The same assigned profile is used throughout that role's game.\n\n"]
    for profile in profiles.values():
        parts.append(f"### {profile['label']}\n\n" + code(profile) + "\n")
    parts.extend([
        "## 3. Rules-check user message\n\n"
        "Checks understanding before a paired game. Actual example: retailer in the first block.\n\n"
        + saved_message(rules) + "\n",
        "## 4. Initial-decision user message\n\n"
        "Asks for the first order. Used in calibration, matched-state probes and weekly games. "
        "This exact saved example is the first retailer probe, so `past_rounds` is empty. "
        "Weekly-game messages use the same format and include the role's prior rounds.\n\n"
        + saved_message(initial) + "\n",
        "## 5. Revision user message\n\n"
        "Provides one chance to keep or change the initial order. Used in calibration and in the adequate condition "
        "of probes/games. This is the revision of the exact example above; "
        "`submitted_order` and `opportunity` are the added fields.\n\n"
        + saved_message(revision) + "\n",
        "**Token ceilings:** initial/rules 16,384; revision 8,192. High effort is fixed; temperature is omitted. "
        "Order responses must contain an integer `order`; negative orders are rejected.\n\n"
        f"**Run:** `{run.name}`. "
        f"[All saved requests]({base}/requests/) · "
        f"[Prompt definitions]({base}/source_implementation/{prefix}_protocol.py) · "
        f"[Rules and stage usage]({base}/source_implementation/{prefix}_study.py) · "
        f"[Notebook](../../notebooks/{notebook}).\n"
    ])
    document = "".join(parts)
    require(raw_hashes(run) == before, "Raw evidence changed during export.")
    destination = report / filename
    destination.write_text(document, encoding="utf-8", newline="\n")
    return {"report": str(destination), "api_requests_checked": len(records),
            "raw_files_unchanged": len(before), "api_calls_made": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "data/runs" / RUN_ID)
    parser.add_argument("--both", action="store_true", help="Export the completed Claude and GPT runs separately.")
    args = parser.parse_args()
    runs = [ROOT / "data/runs" / name for name in (RUN_ID, "economy_api_a80275c58f2c07e0")] if args.both else [args.run]
    print(json.dumps([export(run) for run in runs], indent=2))

