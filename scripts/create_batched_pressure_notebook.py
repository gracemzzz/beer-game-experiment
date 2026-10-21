"""Build the user-facing notebook for experiment 12; never calls a model."""
from pathlib import Path
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / 'experiments/12_pressure_framing_api_20261020/notebooks/RUN_EXPERIMENT.ipynb'


def main():
    cells = [
        nb.v4.new_markdown_cell('''# Experiment 12 — four-model Beer Game study

**80 fictional testers / 20 chains per model, 24 decision weeks.**
Models: GPT-6 Luna, GPT-5.6 Luna, GPT-5.6 Sol and Claude Haiku 5.5.

**One main API call per model produces all 20 chains.** Each model first gets one small two-chain pilot. All four pilots must pass before the four main calls start. Total: **8 planned calls**, plus at most one retry per transient technical failure, within the **shared $5 cap**.

**Recovery update:** If the saved run has the two failed GPT-6/Claude pilots, this notebook reuses the two accepted GPT-5.6 pilots and prepares **2 revised pilot calls + 4 main calls**. All original responses and charges remain preserved. Close and reopen this notebook to load the updated cells, then restart the kernel before running it.

This compares **imagined no pressure versus strong pressure**. Both conditions use the same actual API settings. The model generates both conditions together, so results describe a scenario contrast; they do not establish binding time, independent students or statistical significance.

Run cells from top to bottom. Review is free by default. To collect data, change `RUN_API` below to `True`; the next section asks for your two API keys in hidden fields. Never paste keys into a code cell or chat.

[Experiment guide](../README.md) · [Hypotheses and protocol](../hypotheses/PROTOCOL.md) · [Latest report](../reports/REPORT.md)'''),
        nb.v4.new_markdown_cell('''## 1. Setup

Use the Python environment containing the project requirements. If imports fail, install them with `%pip install -r ../../../requirements.txt`, then restart the kernel and run again.'''),
        nb.v4.new_code_cell('''from pathlib import Path
import sys, os, json, getpass
import pandas as pd
from IPython.display import display, Markdown, HTML

here = Path.cwd().resolve()
candidates = [here, *here.parents, here / "Project" / "beer_game_experiment", here / "beer_game_experiment"]
ROOT = next((p for p in candidates if (p / "src/beergame_study/batched_pressure.py").exists()), None)
if ROOT is None:
    raise RuntimeError("Open this notebook from the Beer Game project folder.")
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import batched_pressure as study
from beergame_study.batched_pressure_api import Runner, estimate
from beergame_study.batched_pressure_report import build_report
from beergame_study import batched_pressure_recovery as recovery

EXPERIMENT = ROOT / "experiments/12_pressure_framing_api_20261020"
print("Experiment folder:", EXPERIMENT)'''),
        nb.v4.new_markdown_cell('''## 2. Prepare and check the plan

`RUN_API = False` reads/prepares files without paid calls. Change it to `True` when ready.

`PHASE = "all"` finishes the pilots, checks their format/rules/physical state, and then runs the four main requests only if every pilot passes. Use `"pilot"` to stop after the pilot. The recovery automatically reuses the two accepted pilots and makes one revised attempt for each of the two failed pilots. Completed requests are reused on resume. The $5 cap includes every run and retry in this experiment folder.'''),
        nb.v4.new_code_cell('''RUN_API = False
PHASE = "all"  # "all", "pilot", or "main"

run_dir = study.prepare(EXPERIMENT, cap_usd=5.0)
plan = study.loadplan(run_dir)
old_status_path = run_dir / "api_status.json"
old_tasks = json.loads(old_status_path.read_text()).get("tasks", {}) if old_status_path.exists() else {}
failed_pilots = {name for name, row in old_tasks.items() if name.endswith("_pilot") and row.get("status") == "invalid"}
recovery_dir = recovery.prepare(run_dir) if failed_pilots == {"gpt-6-luna_pilot", "claude-haiku-5-5_pilot"} else None
print("Frozen study:", plan["study_id"])
print("Recovery: reuse 2 accepted pilots; 2 revised pilot calls + 4 main calls" if recovery_dir else "Planned: 4 pilot responses + 4 main responses")
if recovery_dir:
    print("Recovery records:", recovery_dir)
    print("Original failures remain saved. GPT-6: medium reasoning; Claude: larger output allowance.")
print("Main: 80 testers × 4 models = 320 fictional role identities; 7,680 weekly orders")
costs = pd.DataFrame(recovery.estimate(recovery_dir) if recovery_dir else estimate(run_dir))
display(costs)
print("Conservative first-attempt reservation total: $" + f"{costs.first_attempt_reservation_ceiling_usd.sum():.4f}")
print("Hard total cap, including retries: $5.00")'''),
        nb.v4.new_markdown_cell('''## 3. API keys and collection

**This is the API-key input cell.** With `RUN_API=True`, it requests the OpenAI key, then the Anthropic key. Paste each into its hidden input field and press Enter.

The progress bar counts accepted slots (including reused pilots), failures, blocked requests and requests left. A failed technical pilot blocks all main calls; its original response remains available for diagnosis. Null or opposite hypothesis results are accepted normally. Both providers' keys are needed to complete the four-model pilot.

For this recovery, GPT-6 uses medium effort and a precise accounting appendix; Claude keeps low effort with more room for reasoning plus JSON. The two GPT-5.6 models retain their original settings. The notebook does not silently repeat a newly invalid response.'''),
        nb.v4.new_code_cell('''if RUN_API:
    keys = {}
    runner = None
    try:
        keys["openai"] = os.environ.get("OPENAI_API_KEY") or getpass.getpass("OpenAI API key (hidden): ").strip()
        keys["anthropic"] = os.environ.get("ANTHROPIC_API_KEY") or getpass.getpass("Anthropic API key (hidden): ").strip()
        if not all(keys.values()):
            raise ValueError("Both keys are required; no requests have been sent.")
        progress_display = display(HTML("Starting saved-progress check…"), display_id=True)
        def show_progress(p):
            text = (f"{p['done']}/{p['total']} finished · {p['remaining']} left · "
                    f"{p['accepted']} accepted · {p['failed']} failed · {p['skipped']} blocked · "
                    f"${p['charged_or_reserved_usd']:.4f} / $5.00")
            progress_display.update(HTML(f'<progress value="{p["done"]}" max="{p["total"]}" style="width:100%"></progress><p>{text}</p>'))
        runner_type = recovery.Runner if recovery_dir else Runner
        runner = runner_type(recovery_dir or run_dir, keys=keys, callback=show_progress)
        execution = await runner.execute(PHASE)
        print("Collection records:", recovery_dir or (EXPERIMENT / "raw" / run_dir.name))
    finally:
        keys.clear()
        if runner is not None:
            runner.keys.clear()
        del keys
else:
    print("Review mode: no API requests and no key input. Change RUN_API to True in section 2 to collect data.")'''),
        nb.v4.new_markdown_cell('''## 4. Findings and detailed results

Run this section even if collection stopped. Missing results remain missing. H1 is a pipeline-sensitivity proxy; H2 is the cost calculated by Python from the submitted orders. Negative H1 and positive H2 differences follow the predicted directions. The report never labels a trend as proof or reports independent-student p-values.'''),
        nb.v4.new_code_cell('''published = build_report(run_dir, recovery=recovery_dir)
summary = published["summary"]
display(pd.DataFrame(summary["model_status"]))
display(pd.DataFrame(summary["hypotheses"])[["model", "hypothesis", "paired_blocks", "mean_strong_minus_no", "descriptive_direction"]])
print("Full report:", published["report"])
print("Excel results:", published["workbook"])
report_href = os.path.relpath(published["report"], EXPERIMENT / "notebooks")
workbook_href = os.path.relpath(published["workbook"], EXPERIMENT / "notebooks")
display(Markdown(f"[Open full report]({report_href}) · [Download Excel results]({workbook_href})"))
print("Conservative charges/reservations: $" + f"{published['charged_or_reserved_usd']:.4f}")
landing = (EXPERIMENT / "reports/REPORT.md").read_text(encoding="utf-8")
display(Markdown(landing.replace("](history/", "](../reports/history/")))'''),
        nb.v4.new_markdown_cell('''## 5. Inspect the exact prompts

Each file below contains the original API prompt and a separate JSON schema. All 20 main chains are in the single main prompt for that model. If recovery is active, its separate frozen request files include the revised prompts and settings; the original prompts stay unchanged. All stages share the same cumulative $5 cap.'''),
        nb.v4.new_code_cell('''display(pd.DataFrame([
    {"model": t["model"], "phase": t["phase"], "chains": len(t["chains"]),
     "prompt": str(EXPERIMENT / t["prompt_path"]), "schema": str(EXPERIMENT / t["schema_path"])}
    for t in plan["tasks"]
]))
if recovery_dir:
    print("Exact revised request payloads and amendment manifest:", recovery_dir)'''),
    ]
    book = nb.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'},
    })
    nb.validate(book)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    nb.write(book, DESTINATION)
    print(DESTINATION)


if __name__ == '__main__':
    main()
