"""Build experiment 13's notebook. No imports or actions here make API calls."""
from pathlib import Path
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / 'experiments/13_weekly_state_api_20261021/notebooks/RUN_EXPERIMENT.ipynb'


def main():
    cells = [
        nb.v4.new_markdown_cell('''# Experiment 13 — weekly Beer Game decisions

**Python calculates the game; models choose orders.** Each model represents 80 fictional students in 20 four-role chains, over 24 weeks. Each week is one API request containing all 80 current decisions. Future demand is hidden.

**Run order:** full-size format pilot → 24 weekly requests → H1 probe request, for each model. This is **104 planned calls across four models**, before bounded technical retries. A failed model stops independently; successful models continue. Earlier experiment 12 results stay separate.

The **same cumulative $5 budget** covers experiments 12 and 13. It is not a fresh $5 allowance. The notebook checks the existing ledger before paid requests. It starts in free review mode.

The conditions describe imagined no pressure / strong pressure. Actual generation settings are equal between conditions. Results are descriptive: this design does not establish binding time pressure, independent student observations, structural β, or statistical significance.

[Guide](../README.md) · [Protocol](../hypotheses/PROTOCOL.md) · [Latest report](../reports/REPORT.md)'''),
        nb.v4.new_markdown_cell('''## 1. Setup

Open this **new experiment 13 notebook**, restart its kernel, then run the cells in order. If dependencies are missing, run `%pip install -r ../../../requirements.txt` in this notebook and restart the kernel. Word/docx is not required for reporting.'''),
        nb.v4.new_code_cell('''from pathlib import Path
import sys, os, json, getpass, html
import pandas as pd
from IPython.display import display, Markdown, HTML

here = Path.cwd().resolve()
candidates = [here, *here.parents, here / "Project/beer_game_experiment", here / "beer_game_experiment"]
ROOT = next((p for p in candidates if (p / "src/beergame_study/weekly_pressure.py").exists()), None)
if ROOT is None:
    raise RuntimeError("Open this notebook inside the Beer Game project.")
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import weekly_pressure as study
from beergame_study.weekly_pressure_api import Runner, estimate
from beergame_study.weekly_pressure_report import build_report

EXPERIMENT = ROOT / "experiments/13_weekly_state_api_20261021"
BUDGET_EXPERIMENT = ROOT / "experiments/12_pressure_framing_api_20261020"
print("New study:", EXPERIMENT)
print("Existing shared budget:", BUDGET_EXPERIMENT / "data/api_budget.json")'''),
        nb.v4.new_markdown_cell('''## 2. Settings and cost check

Keep `RUN_API=False` to inspect everything for free. To collect, change it to `True` and keep `PHASE="all"`; no manual switch from calibration to game is needed. Use `PHASE="pilot"` only if you want to inspect the four format pilots first.

Models: `gpt-6-luna`, `gpt-5.6-luna`, `gpt-5.6-sol`, `claude-haiku-5-5`. OpenAI reasoning is `none`; Claude thinking is disabled, with low effort. These are budget/latency settings, not the pressure treatment. Output allowances are 2,048 tokens per weekly/pilot response and 4,096 per probe response.

The estimate uses synthetic states only for planning, not as experimental observations. Actual states and retries affect cost. The shared hard cap applies before every attempt; it can stop an incomplete study.'''),
        nb.v4.new_code_cell('''RUN_API = False
PHASE = "all"  # "all", "pilot", or "main" (main requires a saved accepted pilot)

run_dir = study.prepare(EXPERIMENT, BUDGET_EXPERIMENT)
plan = study.loadplan(run_dir)
print("Frozen study:", run_dir.name)
costs = pd.DataFrame(estimate(run_dir))
display(costs)
if "first_attempt_reservation_ceiling_usd" in costs:
    print(f"Planning reservations for 104 first attempts: ${costs.first_attempt_reservation_ceiling_usd.sum():.4f}")
if "stressed_input_reservation_usd" in costs:
    print(f"Large-state input sizing scenario: ${costs.stressed_input_reservation_usd.sum():.4f}")
ledger = json.loads((BUDGET_EXPERIMENT / "data/api_budget.json").read_text())
spent = sum(row["charge_usd"] for row in ledger["attempts"].values())
print(f"Already charged/reserved: ${spent:.6f}; remaining: ${ledger['cap_usd'] - spent:.6f}")
print("Main sample: 20 chains × 4 roles × 4 models = 320 fictional role identities.")
print("104 planned requests: 4 full-size format pilots + 96 weekly requests + 4 probe requests.")'''),
        nb.v4.new_markdown_cell('''## 3. API-key input and collection

With `RUN_API=True`, this cell asks for the OpenAI and Anthropic keys in **hidden input fields**. Paste each key into its field and press Enter. Do not put keys in code cells.

Each accepted week is saved before continuing. Rerunning reuses saved accepted responses. Temporary network/rate errors get at most one budgeted retry; invalid choices stop that model and remain saved. There are no invented replacement orders or retries to obtain a desired effect. The progress bar counts accepted, failed, blocked, and remaining requests.'''),
        nb.v4.new_code_cell('''if RUN_API:
    keys = {}
    runner = None
    try:
        keys["openai"] = os.environ.get("OPENAI_API_KEY") or getpass.getpass("OpenAI API key (hidden): ").strip()
        keys["anthropic"] = os.environ.get("ANTHROPIC_API_KEY") or getpass.getpass("Anthropic API key (hidden): ").strip()
        if not all(keys.values()):
            raise ValueError("Both keys are required; no requests sent.")
        progress_display = display(HTML("Checking saved requests…"), display_id=True)
        def show_progress(p):
            text = (f"{p['done']}/{p['total']} resolved · {p['remaining']} left · "
                    f"{p['accepted']} accepted · {p['failed']} failed · {p['skipped']} blocked · "
                    f"${p['charged_or_reserved_usd']:.4f} / $5.00")
            progress_display.update(HTML(f'<progress value="{p["done"]}" max="{p["total"]}" style="width:100%"></progress><p>{html.escape(text)}</p>'))
        runner = Runner(run_dir, keys=keys, callback=show_progress)
        execution = await runner.execute(PHASE)
        print("Saved execution status:", run_dir / "api_status.json")
    finally:
        keys.clear()
        if runner is not None:
            runner.keys.clear()
        del keys
        published = build_report(run_dir)
        print("Report updated:", published["report"])
else:
    print("Review mode: no calls and no key input. Set RUN_API=True in section 2 when ready.")'''),
        nb.v4.new_markdown_cell('''## 4. Results and report

Run this even after an interruption. Conclusions appear first. Missing weeks stay missing; only full 24-week games enter H2. A valid null or opposite result is kept. The workbook and CSV files include every accepted weekly order, Python state, cost, probe choice, hypothesis comparison and recorded API attempt.'''),
        nb.v4.new_code_cell('''published = build_report(run_dir)
summary = published["summary"]
display(pd.DataFrame(summary["model_status"]))
display(pd.DataFrame(summary["hypotheses"]))
report_link = os.path.relpath(published["report"], EXPERIMENT / "notebooks")
workbook_link = os.path.relpath(published["workbook"], EXPERIMENT / "notebooks")
display(Markdown(f"[Full report]({report_link}) · [Excel results]({workbook_link})"))
display(Markdown((EXPERIMENT / "reports/REPORT.md").read_text().replace("](history/", "](../reports/history/")))
print("All raw responses and exact requests are linked from the report.")'''),
        nb.v4.new_markdown_cell('''## 5. See the prompts

This preview shows the first main week before any choices. Later weekly prompts depend on previously accepted orders. Exact sent messages and schemas are saved as each request is prepared. The full demand schedule remains in the local frozen plan and is never included in a weekly prompt.'''),
        nb.v4.new_code_cell('''preview = study.build_task(plan, study.MODELS[0], "main", week=1, accepted={})
print(study.prompt_text(preview))
print("Exact request records:", run_dir)
print("Prompt archive:", EXPERIMENT / "prompts" / run_dir.name)'''),
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
