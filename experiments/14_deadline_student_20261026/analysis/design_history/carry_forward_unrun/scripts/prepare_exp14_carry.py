"""Freeze and prepare the separately versioned, user-selected carry-forward study.

This command creates no participant decisions and makes no API calls. It never
reopens an old case. Main preparation requires its own complete qualification.
"""
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
from beergame_study.exp14_carry import SCHEMA, POLICY, PROBE_POLICY, digest, source_hashes

EXP = ROOT / "experiments/14_deadline_student_20261026"
PLAN = EXP / "hypotheses/CARRY_FORWARD_V2_PLAN.json"
MAIN_PLAN = EXP / "hypotheses/CARRY_FORWARD_V2_MAIN_PLAN.json"
PUBLIC_PROBE = ("probe_id", "role", "inventory", "backlog", "outstanding",
                "pipeline_arrivals", "customer_demand", "recent_demand_history", "shared_inventory")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(path, value):
    data = value if isinstance(value, bytes) else (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Preserve existing bytes: " + str(path))
    else:
        path.write_bytes(data)


def materials():
    paths = [EXP / "hypotheses/CARRY_FORWARD_V2.md",
             EXP / "prompts/carry_forward_v2/STUDENT.md", EXP / "prompts/carry_forward_v2/README.md"]
    paths += [EXP / "prompts" / name for name in ("CONTROL.md", "EDUCATION.md", "probes.json", "comprehension.json")]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}


def analysis_sources():
    paths = [ROOT / x for x in ("src/beergame_study/exp14_carry_analysis.py",
             "src/beergame_study/exp14_analysis.py", "src/beergame_study/pivot_inference_v2.py",
             "scripts/report_exp14_carry.py", "scripts/prepare_exp14_carry.py", "scripts/qualify_exp14_carry.py")]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}


def plan(freeze_new=False):
    if PLAN.exists():
        value = json.loads(PLAN.read_text(encoding="utf-8"))
        if value["source_hashes"] != source_hashes() or value["material_hashes"] != materials():
            raise ValueError("Frozen carry mechanics/materials changed; use a new protocol version")
        return value
    if not freeze_new:
        raise ValueError("First validate software and explicitly --freeze-plan before preparation")
    order = list("ABC")
    random.Random("exp14-carry-v2-d001").shuffle(order)
    value = dict(schema_version="exp14-carry-forward-plan-v2", prospective=True,
        created_utc=datetime.now(timezone.utc).isoformat(), controller_schema=SCHEMA, timeout_policy=POLICY,
        probe_timeout_policy=PROBE_POLICY,
        requested_model="gpt-6-astra", requested_effort="xhigh", prompt_version="CF2-V1",
        temperature="not exposed; unchanged", development=dict(block_id="cf2_d001", seed=1420001,
            weeks=24, arms=list("ABC"), launch_order=order, maximum_contexts=3),
        main=dict(block_ids=["c2m%03d" % n for n in range(1, 11)], seed_base=1430000,
            weeks=24, chains_per_arm=10, contexts=30, status="not qualified; do not launch"),
        deadlines=dict(A=dict(game=30.0, probes=30.0), restricted=dict(game=4.0, probes=3.8)),
        deadline_basis="Reuse original V1 latency-only rule; no outcome-based adjustment",
        first_game_fallback=[4, 4, 4, 4], later_game_fallback="Previous APPLIED four-role orders",
        probe_fallback="For each displayed role use its last APPLIED game order. Every applied probe has an answer; missing actor observations stay flagged.",
        near_deadline="Complete valid payload at or before the boundary remains unchanged",
        missingness="Every applied game/probe answer is provided. Synthetic fallback is never relabelled an observed actor choice.",
        actor_coverage_gate=dict(minimum_game_fraction=.75, minimum_probe_fraction=.75, scope="each_development_case"),
        coverage_after_main_assignment="Diagnostic only; do not exclude, replace or drop software actions or low-coverage assigned cases",
        concurrency="At most three development contexts, launched in frozen A/C/B order; wall time includes shared service load",
        endpoints=dict(H1="B-A fixed eight-pair APPLIED-policy pipeline sensitivity; actor-only sensitivity reported separately",
            H2="B-A complete 24-week chain cost under the model-plus-fallback policy",
            H3="C-B fixed eight-pair APPLIED-policy pipeline sensitivity; actor-only sensitivity reported separately",
            H4a="C-B mean role sample variance of APPLIED weekly orders",
            H4b="C-B mean role applied-order variance / external-demand variance"),
        selection="Operational completion, endpoint availability and adherence only; never H signs/p-values",
        main_gate="Full prospective ten-block plan allowed only after this fixed development block passes all behavioral endpoint and procedure checks",
        main_stopping="All ten assigned blocks; no favorable replacement or significance-based extension",
        source_hashes=source_hashes(), material_hashes=materials(), analysis_hashes=analysis_sources(),
        old_cases_untouched=True, api_requests=0,
        shared_api_ledger="experiments/12_pressure_framing_api_20261020/data/api_budget.json")
    freeze(PLAN, value)
    sources = dict(value["material_hashes"], **value["analysis_hashes"])
    sources.update({"src/beergame_study/exp14_carry.py": value["source_hashes"]["controller"],
                    "scripts/run_exp14_carry.py": value["source_hashes"]["transport"],
                    "src/beergame_study/manual_weekly_v3.py": value["source_hashes"]["physics"]})
    snapshot = EXP / "data/carry_forward_v2/protocols" / digest(value)[:20]
    for name, expected in sources.items():
        if sha(ROOT / name) != expected:
            raise ValueError("Source changed during freeze: " + name)
        freeze(snapshot / name, (ROOT / name).read_bytes())
    freeze(snapshot / "PLAN.json", PLAN.read_bytes())
    freeze(snapshot / "SOURCE_HASHES.json", sources)
    return value


def prepare(stage, arm, block=None):
    if stage not in ("development", "main") or arm not in ("A", "B", "C"):
        raise ValueError("Unknown stage or arm")
    value = plan()
    if stage == "main":
        if not MAIN_PLAN.exists():
            raise ValueError("Main blocked until development qualification and a separate frozen main plan")
        main = json.loads(MAIN_PLAN.read_text(encoding="utf-8"))
        if not main.get("frozen") or not main.get("qualification_passed"):
            raise ValueError("Unqualified main plan")
        for key, actual in (("source_hashes", source_hashes()), ("material_hashes", materials()), ("analysis_hashes", analysis_sources())):
            if main.get(key) != actual:
                raise ValueError("Frozen main sources/materials/analysis changed: " + key)
        if block not in main["block_ids"]:
            raise ValueError("Main block was not prospectively assigned")
        seed = value["main"]["seed_base"] + int(block[3:])
    else:
        if block is not None and block != value["development"]["block_id"]:
            raise ValueError("Only the single prospective development block is authorized")
        block = value["development"]["block_id"]
        seed = value["development"]["seed"]
    folder = EXP / "data/carry_forward_v2" / stage / (block + "_" + arm.lower())
    if folder.exists():
        raise ValueError("Prepared case exists; never reset, replace or resume an old protocol as this version")
    probes = json.loads((EXP / "prompts/probes.json").read_text(encoding="utf-8"))
    questions = json.loads((EXP / "prompts/comprehension.json").read_text(encoding="utf-8"))
    case = dict(schema_version=SCHEMA, timeout_policy=POLICY, probe_timeout_policy=PROBE_POLICY,
        case_id="E14CF2_" + digest([stage, block, arm, seed])[:20],
        block_id=block, arm=arm, stage=stage, prompt_version=value["prompt_version"],
        seed=seed, weeks=24, deadline_seconds=None,
        phase_deadline_seconds=value["deadlines"]["A" if arm == "A" else "restricted"],
        requested_model="gpt-6-astra", requested_effort="xhigh", source_hashes=source_hashes(),
        material_hashes=value["material_hashes"], plan_sha256=sha(PLAN),
        probes=[{key: p[key] for key in PUBLIC_PROBE} for p in probes],
        assay_scoring={p["probe_id"]: {key: p[key] for key in ("pair_id", "assay_dimension")} for p in probes},
        comprehension=[{key: q[key] for key in ("question_id", "question", "choices")} for q in questions],
        comprehension_scoring={q["question_id"]: {key: q[key] for key in ("correct_answer", "reason")} for q in questions})
    freeze(folder / "CASE.json", case)
    reading = "EDUCATION.md" if arm == "C" else "CONTROL.md"
    exact = (EXP / "prompts/carry_forward_v2/STUDENT.md").read_text(encoding="utf-8")
    exact += "\n\n" + (EXP / "prompts" / reading).read_text(encoding="utf-8")
    freeze(folder / "EXACT_PROMPT.md", exact.encode("utf-8"))
    python, transport = ROOT / ".venv/Scripts/python.exe", ROOT / "scripts/run_exp14_carry.py"
    task = f"""You are one isolated experimental decision-maker, not a project maintainer. Requested model: gpt-6-astra; effort:xhigh. Read EXACT_PROMPT.md completely. This context controls one four-role chain of fictional students. Do not read CASE/private state/source/scoring/protocol/report/other runs. No other agents, API calls, order-policy code, optimizers, random generators, filtering, or future-decision loops.

Run folder: {folder}
Python: {python}
Transport: {transport}

For each opportunity, use a separate tool call with max_output_tokens >=10000:
& '{python}' -X utf8 '{transport}' show --run '{folder}'

Read the COMPLETE returned public display and its actual immutable decision_id/deadline. Choose the literal values yourself only after this current display. Submit your actual literal JSON and current ID using a separate interaction:
@'
YOUR_LITERAL_JSON
'@ | & '{python}' -X utf8 '{transport}' submit --run '{folder}' --decision-id 'CURRENT_DECISION_ID'

Game input is a JSON list of four nonnegative integer orders in role order. Probe input maps exactly the four displayed probe_id values to literal integer orders. Comprehension maps all displayed question_id values to letters. Never generate these values with code or precompute future orders. Zero/repeated/constant choices are allowed. There is one actor submission per opportunity and no revision pass. Do not narrate while a timed opportunity is open.

After accepted:true, call show again. After accepted:false with continue_allowed:true and transition_kind game_carry_forward or probe_carry_forward, the old opportunity is finished: call show for the next one. NEVER retry the old ID or edit the fallback. Carry-forward applies the previous APPLIED four-role game orders, firstweek [4,4,4,4]; it is a software action. An expired probe page receives each displayed role's last APPLIED game order as a labelled software answer. The current actor choice remains unobserved; never claim you supplied it in time. Repeated show never resets a clock. An explicit show may process a just-expired old opportunity and return the next full current display.

If rejected with continue_allowed:false, a tool fails, or any public display is incomplete, STOP and report the failure without repair/retry/restart. Otherwise continue all24 gameweeks, all8 probe pages (including fallback pages), and the untimed questions until the controller says complete. Every resolved game/probe opportunity has an applied answer, while some actor responses can remain unobserved; report that distinction honestly. Preserve all raw and applied records. Return RESULT.json path and deviations only, with no invented transcript, analysis, p-values or hidden reasoning.
"""
    freeze(folder / "AGENT_TASK.md", task.encode("utf-8"))
    launch = f"Read and follow only {folder / 'AGENT_TASK.md'} and its EXACT_PROMPT.md. You are an isolated fictional student-decision participant in one four-role chain. Follow full show/literal submit until complete or noncontinuable error. Continue after explicit carry-forward/probe-missing acknowledgments; never repair a missed choice. No private/source/other-run reads, decision code, agents, APIs or analysis. Return preserved RESULT.json path and deviations."
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
