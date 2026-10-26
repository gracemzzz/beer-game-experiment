"""Offline preparation/intake for the manual, Python-guided website workflow.

No API transport, credentials or spending-ledger mutations are used here.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

from . import manual_weekly_v3 as controller
from . import pivot_inference_v2 as inference
from .weekly_pivot_v2 import CONTROL, EDUCATION

SLOTS = ("gpt_flagship", "gpt_balanced", "gpt_economy", "claude")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def freeze(path, value):
    path = Path(path)
    data = value if isinstance(value, bytes) else (
        value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Use a new version; refusing to overwrite evidence: " + path.name)
    else:
        with path.open("xb") as stream:
            stream.write(data)


def prompt_for(manifest, case):
    config = {key: case[key] for key in ("case_id", "arm", "replicate", "chains", "seed")}
    config.update(study_id=manifest["study_id"], provider="website-user-reported", model="UNRECORDED",
                  reasoning_setting="UNRECORDED")
    lecture = EDUCATION if case["arm"] == "C" else CONTROL
    return """Run a Python-guided Beer Game study in this chat using the uploaded beergame_controller.py. You need real Python/code execution. If you cannot use it, say so and stop; do not invent a completed export.

Simulate fictional second-year business students at the University at Buffalo, an American university. Use the controller's ordinary-coursework profiles consistently. These are hypothetical students, not actual respondents or estimates from student data. Their objective is to minimize cumulative team inventory-holding and backlog cost over a continuing game. Make plausible student judgments from the displayed information and classroom reading. Do not aim for a particular experimental outcome or invent differences between people.

Rules: roles are retailer, wholesaler, distributor, factory, in that order. Each order is a nonnegative integer. Holding costs 0.5 per case/week and backlog costs 1 per case/week. Backlog already includes current unfilled demand. Outstanding replenishment means prior orders not received. An order reaches the next upstream role the following week; physical shipments require two weeks. Factory production takes three weeks. Orders cannot be cancelled. Python processes receipts and shipments before asking for orders. Current inventories and the supplied histories are shared. Future demand is unknown to the students.

CLASSROOM READING
""" + lecture + """

EXECUTION
1. Import WebsiteGame from the attached beergame_controller.py without changing the file. Create exactly this session:
```python
import json
from pathlib import Path
from beergame_controller import WebsiteGame
game = WebsiteGame(**""" + repr(config) + """ )
print(json.dumps(game.display(), separators=(',', ':')))
```
If the uploaded file is in a tool-specific folder, import that exact file using importlib.util; do not rewrite it. Do not inspect the controller source, private state, RNG or future demand. Use only public method outputs. Never change this case's identity, seed or controller settings.

2. After EACH returned display, choose each requested student's literal order yourself as the model. For phase 'initial', call game.submit_initial with a literal dictionary containing all requested chain IDs and four orders per chain. Print its result and game.display(). One response covers all requested chains in this chat.

3. If the returned phase is 'revision', use a SEPARATE assistant/tool interaction to reconsider the displayed initial proposals. The physical state is unchanged. You may keep or change any order. Call game.submit_revision with your literal dictionary, then print game.display(). Do not combine an initial proposal and its revision in one Python call. If there is no revision phase, commit the initial result and continue from the next displayed week.

4. Continue from returned displays until the controller switches to hypothetical probes. For 'probe_initial', choose a literal integer for EVERY probe ID and call game.submit_probe_initial. For 'probe_revision', reconsider in a separate assistant/tool interaction and call game.submit_probe_revision. The hypothetical situations are separate choices, not more game weeks.

5. When phase is 'complete', export the UNEDITED controller result to a downloadable JSON file:
```python
result = game.export()
out = Path('""" + case["case_id"] + """.json')
out.write_text(json.dumps(result, separators=(',', ':'), allow_nan=False), encoding='utf-8')
print(out)
```
Return a download link to that JSON and say whether all controller phases finished. Do not substitute a report, summary or plots for the file. If downloadable files are unavailable, paste the complete JSON unchanged. If the session stops early, return game.export(require_complete=False) and label it incomplete; do not fill gaps.

IMPORTANT METHOD RULES
- Python is only the mechanical controller. Do not implement an ordering policy, optimizer, random-order generator or decision loop in Python. Do not precompute future weekly orders or simulate extra students using a program. All submitted orders must be literal choices you make AFTER each tool-returned state.
- Do not batch multiple game weeks into one code call. After submission, receive the printed next state before choosing again. In an A revision phase, receive its new display before the next model decision.
- Preserve zeros, constant choices and decisions you decide to keep. No minimum order, preferred maximum, desired oscillation, required treatment difference or significance target is specified.
- Do not inspect other chats or compare treatment results. Do not fabricate model identity; leave UNRECORDED metadata as supplied. The researcher will separately record the actual website model and reasoning setting.
- Keep the complete chat/tool history available for export. The JSON proves arithmetic consistency only; the researcher needs the transcript to verify that choices came from separate model decisions rather than an automatic policy.
"""


def prepare(experiment, *, blocks=40, chains=10):
    experiment = Path(experiment).resolve()
    if type(blocks) is not int or blocks < 1 or type(chains) is not int or chains < 1:
        raise ValueError("Use positive integer blocks/chains")
    protocol = experiment / "hypotheses/MANUAL_V3_20261025.md"
    sources = {n: Path(__file__).with_name(n) for n in
               ("manual_weekly_v3.py", "manual_workflow_v3.py", "manual_plots_v3.py", "pivot_inference_v2.py", "weekly_pivot_v2.py")}
    identity = dict(protocol=controller.PROTOCOL, schema_version=controller.SCHEMA, seed=20261025,
        blocks=blocks, chains_per_chat=chains, model_slots=list(SLOTS), primary_model_slot="gpt_flagship",
        sweep_sizes=[10, 20, 40], source_hashes={n: sha(p) for n, p in sources.items()},
        protocol_sha256=sha(protocol), controller_source_sha256=controller.source_sha256(),
        inference_unit="independently started matched three-arm block, chains within chat averaged",
        intervention="one versus two separate model decision opportunities; not literal binding clock time",
        requires_transcript_review=True, api_requests=0)
    study_id = "manual_v3_" + controller.digest(identity)[:16]
    run = experiment / "data" / study_id
    prompts = experiment / "prompts" / study_id
    cases = []
    for arm in ("A", "B", "C"):
        cases.append(dict(case_id="MW3_PILOT_" + arm, arm=arm, replicate=1001, chains=chains,
                          seed=identity["seed"], collection_kind="development", prompt_file="00_PILOT_" + arm + ".md"))
    for replicate in range(1, blocks + 1):
        for arm in ("A", "B", "C"):
            ordinal = (replicate - 1) * 3 + ("ABC".index(arm) + 1)
            cases.append(dict(case_id=f"MW3_B{replicate:03d}_{arm}", arm=arm, replicate=replicate, chains=chains,
                              seed=identity["seed"], collection_kind="heldout", prompt_file=f"{ordinal:03d}_B{replicate:03d}_{arm}.md"))
    manifest = dict(identity, study_id=study_id, cases=cases)
    freeze(run / "manifest.json", manifest)
    freeze(run / "manifest.sha256", controller.digest(manifest) + "\n")
    for name, path in sources.items():
        freeze(run / "source_snapshot" / name, path.read_bytes())
    freeze(run / "source_snapshot/MANUAL_V3_20261025.md", protocol.read_bytes())
    controller.write_standalone(prompts / "beergame_controller.py")
    for case in cases:
        freeze(prompts / case["prompt_file"], prompt_for(manifest, case))
    index = ["# Website prompts — start with the three pilots", "",
        "No API calls or keys. Each fresh code-enabled chat runs ten chains (40 fictional students) week by week.", "",
        "1. Upload [beergame_controller.py](beergame_controller.py) in a fresh chat with Python/code execution.",
        "2. Copy the entire assigned Markdown prompt into that chat. Let the model use its Python tool until it returns the JSON file.",
        "3. Download the JSON and save/export the full chat/tool transcript. Return both plus the exact website model and selected reasoning mode.",
        "4. Start with PILOT A, B and C. These are development checks, not part of the main sample.",
        "5. Main prompts are already frozen below, but do not start them until pilot adherence/replay is reviewed. Use a fresh chat per file; keep the same model/mode across each three-arm block.", "",
        "A uses an extra reconsideration pass; B/C commit their initial answers. This is a review-opportunity analogue, not a binding human deadline. A mathematically correct JSON alone is not proof of repeated model decisions.", "",
        "## First three prompts", ""]
    for c in cases[:3]:
        index.append(f"- [{c['case_id']}]({c['prompt_file']})")
    main = cases[3:]
    for start in range(0, len(main), 10):
        index.extend(["", f"## Main wave {start // 10 + 1}: ten tabs", ""])
        for c in main[start:start + 10]:
            index.append(f"- [{c['case_id']}]({c['prompt_file']})")
    index.extend(["", "Ten/20/40 independent blocks mean 30/60/120 chats per model. Fictional students in a shared chat are dependent. Fixed prefixes are not a rule for stopping at significance.", ""])
    freeze(prompts / "README.md", "\n".join(index))
    (run / "inbox").mkdir(exist_ok=True)
    return run


def load_manifest(run):
    run = Path(run)
    m = read(run / "manifest.json")
    if controller.digest(m) != (run / "manifest.sha256").read_text(encoding="utf-8").strip():
        raise ValueError("Prepared manual manifest changed")
    for name, expected in m["source_hashes"].items():
        if sha(run / "source_snapshot" / name) != expected or sha(Path(__file__).with_name(name)) != expected:
            raise ValueError("Source changed; preserve the old version and prepare a new fingerprint: " + name)
    protocol = run.parent.parent / "hypotheses/MANUAL_V3_20261025.md"
    if sha(protocol) != m["protocol_sha256"] or sha(run / "source_snapshot/MANUAL_V3_20261025.md") != m["protocol_sha256"]:
        raise ValueError("Manual protocol changed")
    prompts = run.parent.parent / "prompts" / run.name
    if sha(prompts / "beergame_controller.py") != m["controller_source_sha256"]:
        raise ValueError("The uploadable controller changed")
    for case in m["cases"]:
        if (prompts / case["prompt_file"]).read_text(encoding="utf-8") != prompt_for(m, case):
            raise ValueError("A prepared manual prompt changed: " + case["case_id"])
    return m


def intake(run, json_path, transcript_path, *, model_slot, website_label, reasoning_setting,
           transcript_reviewed=False, reviewer="", review_note=""):
    run = Path(run)
    m = load_manifest(run)
    if model_slot not in m["model_slots"] or not website_label.strip() or not reasoning_setting.strip():
        raise ValueError("Record a planned slot and exact user-reported website model/reasoning labels")
    if type(transcript_reviewed) is not bool:
        raise ValueError("Transcript review must be explicit Boolean")
    if transcript_reviewed and (not reviewer.strip() or not review_note.strip()):
        raise ValueError("Record who reviewed the transcript and its adherence evidence")
    source, transcript = Path(json_path), Path(transcript_path)
    if not source.is_file() or not transcript.is_file() or not transcript.stat().st_size:
        raise ValueError("Both a JSON file and a nonempty full chat/tool transcript are required")
    if transcript.resolve() == source.resolve() or transcript.read_bytes() == source.read_bytes():
        raise ValueError("The JSON export cannot also serve as the tool transcript")
    source_hash, transcript_hash = sha(source), sha(transcript)
    identity = controller.digest([source_hash, transcript_hash, model_slot, website_label, reasoning_setting,
                                  transcript_reviewed, reviewer, review_note])[:20]
    folder = run / "intake" / identity
    freeze(folder / "original.json", source.read_bytes())
    freeze(folder / "transcript.bin", transcript.read_bytes())
    outcome, error, case = None, None, None
    try:
        payload = read(source)
        case = next((c for c in m["cases"] if c["case_id"] == payload.get("case_id")), None)
        if case is None:
            raise ValueError("Case is not in the frozen manifest")
        expected = {key: case[key] for key in ("case_id", "arm", "replicate", "chains", "seed")}
        expected["study_id"] = m["study_id"]
        outcome = controller.audit_export(payload, expected_case=expected, expected_source_sha256=m["controller_source_sha256"])
        outcome["reported_export_model"] = outcome["model"]
        outcome["model"] = model_slot
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        error = type(exc).__name__ + ": " + str(exc)
    receipt = dict(intake_id=identity, json_sha256=source_hash, transcript_sha256=transcript_hash,
        transcript_original_name=transcript.name, case_id=case["case_id"] if case else None,
        model_slot=model_slot, user_reported_website_label=website_label,
        user_reported_reasoning_setting=reasoning_setting, provider_api_identity_verified=False,
        transcript_reviewed=transcript_reviewed, reviewer=reviewer, review_note=review_note,
        collection_kind=case["collection_kind"] if case else "unrecognized", replay_passed=error is None,
        eligible_for_heldout=error is None and transcript_reviewed and case["collection_kind"] == "heldout",
        error=error, outcome=outcome)
    freeze(folder / "receipt.json", receipt)
    freeze(folder / "receipt.sha256", sha(folder / "receipt.json") + "\n")
    return receipt


def collect(run):
    run = Path(run)
    m = load_manifest(run)
    receipts, eligible, seen, settings, source_slots = [], [], set(), {}, {}
    for path in sorted((run / "intake").glob("*/receipt.json")):
        receipt = read(path)
        if sha(path) != (path.parent / "receipt.sha256").read_text(encoding="utf-8").strip():
            raise ValueError("Saved intake receipt changed")
        if sha(path.parent / "original.json") != receipt["json_sha256"] or sha(path.parent / "transcript.bin") != receipt["transcript_sha256"]:
            raise ValueError("Intake originals changed")
        # Re-run physical replay; a saved flag alone is not validation.
        if receipt["replay_passed"]:
            payload = read(path.parent / "original.json")
            case = next(c for c in m["cases"] if c["case_id"] == payload["case_id"])
            expected = {key: case[key] for key in ("case_id", "arm", "replicate", "chains", "seed")}
            expected["study_id"] = m["study_id"]
            outcome = controller.audit_export(payload, expected_case=expected, expected_source_sha256=m["controller_source_sha256"])
            recorded = dict(outcome, reported_export_model=outcome["model"], model=receipt["model_slot"])
            if recorded != receipt["outcome"]:
                raise ValueError("Saved extracted outcomes changed")
            if receipt["collection_kind"] != case["collection_kind"] or receipt["case_id"] != case["case_id"]:
                raise ValueError("Saved case/stage differs from frozen manifest")
            old_slot = source_slots.get(receipt["json_sha256"])
            if old_slot is not None and old_slot != receipt["model_slot"]:
                raise ValueError("The same original export cannot count as observations from different model slots")
            source_slots[receipt["json_sha256"]] = receipt["model_slot"]
        expected_eligible = (receipt["replay_passed"] and receipt["transcript_reviewed"] and
                             receipt["collection_kind"] == "heldout")
        if receipt["eligible_for_heldout"] != expected_eligible:
            raise ValueError("Held-out eligibility differs from replay, review and frozen stage")
        receipts.append(receipt)
        if not receipt["eligible_for_heldout"]:
            continue
        if not receipt["transcript_reviewed"] or not receipt["reviewer"].strip() or not receipt["review_note"].strip() or receipt["collection_kind"] != "heldout":
            raise ValueError("Held-out eligibility has no explicit transcript review")
        reported = (receipt["user_reported_website_label"], receipt["user_reported_reasoning_setting"])
        slot = receipt["model_slot"]
        if slot in settings and settings[slot] != reported:
            raise ValueError("Website model or reasoning setting changed within the same model slot")
        settings[slot] = reported
        key = (receipt["model_slot"], receipt["case_id"])
        if key in seen:
            raise ValueError("Duplicate eligible case: preserve submissions and resolve explicitly; never count twice")
        seen.add(key)
        eligible.append(receipt["outcome"])
    return receipts, eligible


def analyze(run):
    run = Path(run)
    m = load_manifest(run)
    receipts, rows = collect(run)
    plan = dict(schema_version=inference.PLAN_SCHEMA, models=m["model_slots"],
        block_ids=[f"b{i:04d}" for i in range(1, m["blocks"] + 1)], weeks=24, sweep_sizes=[10, 20, 40],
        source_kind="model_observations", collection_kind="heldout", provenance_verified=False,
        independent_blocks_confirmed=False,
        interpretation="User-reported website models; replay and human transcript review; resource-opportunity analogue")
    result = inference.analyze(plan, rows)
    signature = controller.digest([receipts, result])[:12]
    output = run.parent.parent / "analysis" / run.name / signature
    freeze(output / "inference_plan.json", plan)
    freeze(output / "ANALYSIS.json", result)
    freeze(output / "REPORT.md", inference.report_markdown(result))
    freeze(output / "intake_status.json", receipts)
    for name, values in (("block_outcomes", rows), ("hypotheses", result["primary"]), ("sample_size_sweeps", result["sweeps"])):
        if not values:
            freeze(output / (name + ".csv"), "")
            continue
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=list(values[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows({k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()} for row in values)
        freeze(output / (name + ".csv"), stream.getvalue())
    from .manual_plots_v3 import plot_analysis
    plot_analysis(result, output)
    return output, result, receipts
