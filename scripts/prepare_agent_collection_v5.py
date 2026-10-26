"""Prepare three isolated assistant cases without calling a provider API."""
from pathlib import Path
import json
import sys
import uuid
import zipfile
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import manual_batch_v5 as batch
from beergame_study import manual_batch_analysis_v5 as analysis


def main():
    exp = ROOT / "experiments/13_weekly_state_api_20261021"
    transport = ROOT / "scripts/run_manual_agent_v5.py"
    base = exp / "data/assistant_v5_20261025"
    models = [("gpt_astra", "gpt-6-astra", "01_GPT_ASTRA.md"),
              ("gpt_sol", "gpt-6.1-sol", "02_GPT_SOL.md"),
              ("gpt_luna", "gpt-6-luna", "03_GPT_LUNA.md")]
    plan = dict(collection_id="assistant_v5_20261025", physics_study_id=batch.study_id(),
        transport_sha256=analysis.sha(transport),
        models=[dict(slot=s, requested_model=m, requested_effort="high", fork_turns="none") for s, m, _ in models],
        batches_per_model_this_wave=1, chains_per_condition=50, conditions=3, weeks=24,
        source_kind="isolated_local_assistant_agents", api_calls=0, charge_to_shared_api_ledger=0,
        statistical_unit="one fresh isolated agent context",
        full_transcript_status="pending capture; local step records alone do not authenticate full context",
        stopping_rule="complete the three prepared batches regardless of signs; preserve all partials; no direction-based reruns")
    analysis.freeze(base / "COLLECTION_PLAN.json", plan)
    analysis.freeze(base / "TRANSPORT.py", transport.read_bytes())
    for slot, model, prompt_name in models:
        folder = base / slot / "run001"
        casefile = folder / "CASE.json"
        if casefile.exists():
            continue
        with zipfile.ZipFile(exp / "prompts/LARGE_SAMPLE_V5/beer_game_tools.zip") as z:
            for name in ("beergame_controller.py", "batch_runner.py"):
                analysis.freeze(folder / "helper" / name, z.read(name))
        case = dict(case_id="AGENTV5_" + slot.upper() + "_R001", model_slot=slot,
            requested_model=model, requested_effort="high", batch_id=uuid.uuid4().hex,
            helper_hashes={p.name: analysis.sha(p) for p in (folder / "helper").iterdir()},
            transport_sha256=analysis.sha(transport), source_kind="local_assistant_agent",
            actual_provider_api_id="not independently authenticated")
        analysis.freeze(casefile, case)
        analysis.freeze(folder / "EXACT_WEBSITE_PROMPT.md", (exp / "prompts/LARGE_SAMPLE_V5" / prompt_name).read_bytes())
        task = f"""You are an isolated decision-making participant in a Beer Game collection. Your configured requested model is {model}, reasoning effort high. Do not spawn agents or make API requests. Work only on your prepared case {case['case_id']}.

Read EXACT_WEBSITE_PROMPT.md in this run folder for the behavioral task and game rules. Follow it exactly, except that the researcher has already installed and initialized the Python helper. Replace its SETUP, run.submit and save commands with the local transport below. This substitution only manages persistence and records your literal choices; it supplies no order policy. Do not read helper/transport source, private state, CASE.json, other repository instructions/data/reports, or other runs. The public displays and the exact decision prompt are your task information. Ignore historical project directions to inspect other files: this is an isolated participant task. Do not change any files except an optional final status note in your own folder.

Your run folder: {folder}
Python executable: {ROOT / '.venv/Scripts/python.exe'}
Local transport: {transport}

FIRST display the current public state with:
& '{ROOT / '.venv/Scripts/python.exe'}' -X utf8 '{transport}' show --run '{folder}'

For EVERY page, choose the literal dictionary yourself AFTER seeing its public display, then invoke exactly one submission in a tool call. Use this PowerShell structure, with your actual JSON replacing the placeholder:
@'
YOUR_LITERAL_JSON_DICTIONARY
'@ | & '{ROOT / '.venv/Scripts/python.exe'}' -X utf8 '{transport}' submit --run '{folder}'

The next display is printed by that call. Use a separate assistant/tool interaction for each page, including every revision page. Supply every requested ID on the current page and no others. You must type literal decisions: no policy code, formula generator, loop producing choices, random-order code or automated submissions. Do not use a script to generate your submitted dictionaries. Do not combine multiple submissions in one tool call. JSON serialization of a literal dictionary is allowed. Set max_output_tokens sufficiently high (at least 8000) to read each full display; if it is truncated, use show to reread before choosing.

Continue through all three conditions and all 224 pages without asking the user for input. The transport checkpoints every page into RESULT.json and keeps the exact supplied JSON and returned public state. Never restart or fabricate a missing page. If the context compacts, preserve your folder and last public step, resume with show, and continue the same case. Briefly report progress to the parent after each completed condition, with no cross-condition statistical analysis.

Return the RESULT.json path when complete and honestly state any deviations (source inspection, programmed choices, skipped displays, interrupted steps). If blocked by tool limits, preserve and report the partial state. A local execution record is not a full assistant transcript: do not call it one or fabricate a reconstructed conversation. Do not calculate hypotheses, comparisons or p-values. Do not select outcomes or manufacture differences. A fixed or zero choice you judge appropriate stays valid.
"""
        analysis.freeze(folder / "AGENT_TASK.md", task.encode("utf-8"))
        result = subprocess.run([str(ROOT / ".venv/Scripts/python.exe"), "-X", "utf8", str(transport), "init", "--run", str(folder)],
                                capture_output=True, text=True, encoding="utf-8", check=True)
        print(json.dumps(dict(case_id=case["case_id"], folder=str(folder), initial_display_bytes=len(result.stdout.encode("utf-8")))))


if __name__ == "__main__":
    main()
