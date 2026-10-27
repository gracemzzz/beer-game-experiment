"""Prepare isolated fictional-student time-pressure cases, with no model timer."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_framing import SCHEMA, source_hashes, digest

EXP = ROOT / "experiments/14_deadline_student_20261026"
PLAN = EXP / "hypotheses/STUDENT_FRAMING_V3_PLAN.json"
MAIN_PLAN = EXP / "hypotheses/STUDENT_FRAMING_V3_MAIN_PLAN.json"
PUBLIC_PROBE = ("probe_id", "role", "inventory", "backlog", "outstanding", "pipeline_arrivals",
                "customer_demand", "recent_demand_history", "shared_inventory")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(path, data):
    raw = data if isinstance(data, bytes) else (json.dumps(data, indent=2, allow_nan=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError("Preserve existing prepared bytes: " + str(path))
    else:
        path.write_bytes(raw)


def materials():
    paths = [EXP / "hypotheses/STUDENT_FRAMING_V3.md"]
    paths += sorted((EXP / "prompts/student_framing_v3").glob("*.md"))
    paths += [EXP / "prompts" / name for name in ("CONTROL.md", "EDUCATION.md", "probes.json", "comprehension.json")]
    if len(paths) != 9:
        raise ValueError("All nine planned framing protocol/prompt/fixture files must exist")
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}


def analysis_sources():
    files = ("src/beergame_study/exp14_framing_analysis.py", "src/beergame_study/exp14_analysis.py",
             "src/beergame_study/pivot_inference_v2.py", "scripts/report_exp14_framing.py",
             "scripts/prepare_exp14_framing.py", "scripts/qualify_exp14_framing.py")
    return {name: sha(ROOT / name) for name in files}


def plan(freeze_new=False):
    if PLAN.exists():
        value = json.loads(PLAN.read_text(encoding="utf-8"))
        if value["source_hashes"] != source_hashes() or value["material_hashes"] != materials() or value["analysis_hashes"] != analysis_sources():
            raise ValueError("Frozen framing mechanics/materials/analysis changed")
        snapshot = EXP / "data/student_framing_v3/protocols" / digest(value)[:20]
        if not (snapshot / "SOURCE_HASHES.json").exists() or not (snapshot / "PLAN.json").exists():
            raise ValueError("Frozen source snapshot is incomplete")
        if (snapshot / "PLAN.json").read_bytes() != PLAN.read_bytes():
            raise ValueError("Frozen snapshot plan differs")
        recorded = json.loads((snapshot / "SOURCE_HASHES.json").read_text(encoding="utf-8"))
        expected = dict(value["material_hashes"], **value["analysis_hashes"])
        expected.update({"src/beergame_study/exp14_framing.py": value["source_hashes"]["controller"],
                         "scripts/run_exp14_framing.py": value["source_hashes"]["transport"],
                         "src/beergame_study/manual_weekly_v3.py": value["source_hashes"]["physics"],
                         "scripts/audit_exp14_agent.py": sha(ROOT / "scripts/audit_exp14_agent.py"),
                         "scripts/audit_agent_public_trace_v5.py": sha(ROOT / "scripts/audit_agent_public_trace_v5.py")})
        if recorded != expected or any(not (snapshot / name).exists() or sha(snapshot / name) != checksum for name, checksum in expected.items()):
            raise ValueError("Frozen source snapshot is incomplete or changed")
        return value
    if not freeze_new:
        raise ValueError("Validate software, then explicitly --freeze-plan before preparing cases")
    order = list("ABC")
    random.Random("exp14-student-framing-v3-d001").shuffle(order)
    value = dict(schema_version="exp14-student-framing-plan-v3", prospective=True,
        created_utc=datetime.now(timezone.utc).isoformat(), controller_schema=SCHEMA,
        requested_model="gpt-6-astra", requested_effort="xhigh", prompt_version="SF3-V1",
        model_runtime_limit_seconds=None, temperature="not exposed; unchanged", fallback_policy=None,
        fictional_student_seconds=dict(A=120, B=8, C=8),
        treatment="Portray a fictional novice student with adequate/insufficient classroom decision time; no actual model computation restriction",
        development=dict(block_id="sf3_d001", seed=1440001, weeks=24, arms=list("ABC"),
            launch_order=order, maximum_contexts=3),
        main=dict(block_ids=["c3m%03d" % n for n in range(1, 11)], seed_base=1450000,
            weeks=24, chains_per_arm=10, contexts=30, status="not yet qualified"),
        concurrency="At most three fresh contexts; freeze launch order and keep client model/effort unchanged",
        selection="Completion, actual-choice provenance and comprehension only; no H1-H4 signs or p-values",
        gate="All three full24-week games, all32 actual probe choices, complete quiz, clean attributed reviews/replay; C quiz>=75%",
        main_stopping="All ten assigned blocks; no favorable replacement, significant-crossing stop or extension",
        endpoints=dict(H1="B-A equal mean of eight actual pipeline-pair slopes", H2="B-A complete chain cost",
            H3="C-B equal mean of eight actual pipeline-pair slopes", H4a="C-B mean role order variance",
            H4b="C-B mean role order variance divided by external demand variance"),
        inference="Ten independent matched chain contexts, two-sided paired sign-flip and Holm5; not forty independent students",
        source_hashes=source_hashes(), material_hashes=materials(), analysis_hashes=analysis_sources(),
        old_strict_cases_untouched=True, carry_proposal="superseded unrun; not a participant sample", api_requests=0)
    files = dict(value["material_hashes"], **value["analysis_hashes"])
    files.update({"src/beergame_study/exp14_framing.py": value["source_hashes"]["controller"],
                  "scripts/run_exp14_framing.py": value["source_hashes"]["transport"],
                  "src/beergame_study/manual_weekly_v3.py": value["source_hashes"]["physics"],
                  "scripts/audit_exp14_agent.py": sha(ROOT / "scripts/audit_exp14_agent.py"),
                  "scripts/audit_agent_public_trace_v5.py": sha(ROOT / "scripts/audit_agent_public_trace_v5.py")})
    snapshot = EXP / "data/student_framing_v3/protocols" / digest(value)[:20]
    for name, expected in files.items():
        if sha(ROOT / name) != expected:
            raise ValueError("Source changed during freezing: " + name)
        freeze(snapshot / name, (ROOT / name).read_bytes())
    freeze(snapshot / "PLAN.json", value)
    freeze(snapshot / "SOURCE_HASHES.json", files)
    freeze(PLAN, value)
    return value


def prepare(stage, arm, block=None):
    value = plan()
    if arm not in ("A", "B", "C"):
        raise ValueError("Unknown arm")
    if stage == "main":
        if not MAIN_PLAN.exists():
            raise ValueError("Main blocked until development qualification and its own frozen main plan")
        main = json.loads(MAIN_PLAN.read_text(encoding="utf-8"))
        if not main.get("frozen") or not main.get("qualification_passed") or block not in main["block_ids"]:
            raise ValueError("Main block/qualification mismatch")
        for key, current in (("source_hashes", source_hashes()), ("material_hashes", materials()), ("analysis_hashes", analysis_sources())):
            if main.get(key) != current:
                raise ValueError("Frozen main source/material/analysis mismatch: " + key)
        seed = value["main"]["seed_base"] + int(block[3:])
    elif stage == "development":
        if block is not None and block != value["development"]["block_id"]:
            raise ValueError("Only the prospectively registered development block is allowed")
        block, seed = value["development"]["block_id"], value["development"]["seed"]
    else:
        raise ValueError("Unknown stage")
    folder = EXP / "data/student_framing_v3" / stage / (block + "_" + arm.lower())
    if folder.exists():
        raise ValueError("Prepared case exists; never reset or replace it")
    bank = json.loads((EXP / "prompts/probes.json").read_text(encoding="utf-8"))
    quiz = json.loads((EXP / "prompts/comprehension.json").read_text(encoding="utf-8"))
    case = dict(schema_version=SCHEMA, case_id="E14SF3_" + digest([stage, block, arm, seed])[:20],
        block_id=block, arm=arm, stage=stage, prompt_version=value["prompt_version"], seed=seed, weeks=24,
        fictional_student_seconds=value["fictional_student_seconds"][arm], model_runtime_limit_seconds=None,
        deadline_seconds=None, phase_deadline_seconds={"game": None, "probes": None},
        requested_model="gpt-6-astra", requested_effort="xhigh", source_hashes=source_hashes(),
        material_hashes=value["material_hashes"], plan_sha256=sha(PLAN),
        probes=[{key: p[key] for key in PUBLIC_PROBE} for p in bank],
        assay_scoring={p["probe_id"]: {key: p[key] for key in ("pair_id", "assay_dimension")} for p in bank},
        comprehension=[{key: q[key] for key in ("question_id", "question", "choices")} for q in quiz],
        comprehension_scoring={q["question_id"]: {key: q[key] for key in ("correct_answer", "reason")} for q in quiz})
    freeze(folder / "CASE.json", case)
    prompt_dir = EXP / "prompts/student_framing_v3"
    texts = [prompt_dir / "STUDENT.md", prompt_dir / ("ADEQUATE.md" if arm == "A" else "PRESSURE.md"),
             EXP / "prompts" / ("EDUCATION.md" if arm == "C" else "CONTROL.md")]
    exact = "\n\n".join(p.read_text(encoding="utf-8") for p in texts)
    freeze(folder / "EXACT_PROMPT.md", exact.encode("utf-8"))
    python, transport = ROOT / ".venv/Scripts/python.exe", ROOT / "scripts/run_exp14_framing.py"
    task = f"""You are one isolated experimental student-decision participant, not a maintainer. Requested model gpt-6-astra, effort xhigh. Read EXACT_PROMPT.md completely and portray the four supplied student profiles in the fictional classroom situation. No actual model wall-clock limit is imposed. Do not act as an expert optimizing the supply chain in place of those novices.

Run folder: {folder}
Python: {python}
Transport: {transport}

Only read this AGENT_TASK.md and EXACT_PROMPT.md. Never read private CASE/state/source/scoring/protocol/report/other runs. No other agents, API calls, ordering-policy code, random generators, optimizers or precomputed future orders.

For EACH opportunity use a separate tool call with max_output_tokens>=10000:
& '{python}' -X utf8 '{transport}' show --run '{folder}'

Read its COMPLETE public state. Decide your actual four literal answers reflecting the fictional students in that situation. Use a separate interaction to submit your real current JSON and decision_id:
@'
YOUR_LITERAL_JSON
'@ | & '{python}' -X utf8 '{transport}' submit --run '{folder}' --decision-id 'CURRENT_DECISION_ID'

For game, JSON is a list of four nonnegative integer orders in displayed role_order. For probes it maps exactly the four displayed probe_id values to integer orders. For comprehension map all question_id values to letters. You must actually choose every requested order; never leave blanks, ask software to fill values, generate choices with code or copy future decisions. Zero and repeated choices are allowed. There is one accepted submission per opportunity, no second-round thinking/revision pass. The only time difference is the student's fictional classroom time in your prompt, not your own tool/runtime limit.

After accepted:true, call show for the next state. Continue all24weeks, all8 probe pages, then untimed questions until complete. No defaults, random filler, software fallback or late-answer substitution exists. If an input is rejected, a required tool fails or any public state is incomplete, STOP and disclose the technical deviation; never silently repair/restart/replace decisions. Never invent a missing transcript or claim provider-authenticated settings.

Return RESULT.json path and any observed deviations. Also report fictional_student_seconds from your assigned classroom framing as a short instruction-recall check (not a claim of actual model runtime or human pressure). Do not produce hidden reasoning, comparisons, p-values or outcome analysis.
"""
    freeze(folder / "AGENT_TASK.md", task.encode("utf-8"))
    launch = f"Read and follow only {folder / 'AGENT_TASK.md'} and its EXACT_PROMPT.md. You are an isolated fictional student-decision participant controlling one four-role chain. Simulate your assigned classroom situation; there is no actual model timer. Complete full show/literal submit until complete or a technical failure. No source/private/other-run reads, order-policy code, other agents, APIs or analysis. Return preserved RESULT.json path, deviations and assigned fictional_student_seconds."
    freeze(folder / "LAUNCH_MESSAGE.txt", launch.encode("utf-8"))
    subprocess.run([sys.executable, "-X", "utf8", str(transport), "init", "--run", str(folder)], check=True, capture_output=True)
    return dict(folder=str(folder), launch_message=launch, requested_model="gpt-6-astra", requested_effort="xhigh")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze-plan", action="store_true")
    parser.add_argument("--stage", choices=("development", "main"), default="development")
    parser.add_argument("--arm", choices=("A", "B", "C"))
    parser.add_argument("--block")
    args = parser.parse_args()
    if args.freeze_plan:
        print(json.dumps(plan(freeze_new=True), indent=2))
    elif args.arm:
        print(json.dumps(prepare(args.stage, args.arm, args.block)))
    else:
        parser.error("Choose --freeze-plan or --arm")
