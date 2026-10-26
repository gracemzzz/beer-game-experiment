"""Build the new v2 review/technical-pilot notebook; never purchase requests."""
from pathlib import Path
import textwrap
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "experiments/13_weekly_state_api_20261021/notebooks/PIVOT_V2.ipynb"


def code(s):
    return nbf.v4.new_code_cell(textwrap.dedent(s).strip())


def main():
    cells = [nbf.v4.new_markdown_cell("""# Beer Game: revised design and sample-size sweep

**Start in free review mode.** This notebook shows the completed study, revised prompts, independent-block design and spending plan. It can run a **four-call technical pilot**, not a significant hypothesis study. No new paid calls run by opening this notebook or using its default settings.

The completed sample tests pressure wording only. The new three-arm design restricts **reconsideration opportunities** (one response versus two), uses high effort throughout, and includes causal education. This is an AI resource analogue, not calibrated human decision-time pressure. Development self-checks are excluded from held-out results.

1. Run all cells unchanged to review.
2. Read the displayed budget, report and free self-check before spending.
3. For the optional technical pilot, set `RUN_API=True`, run all cells, enter the two keys in the hidden fields and click **Run four format checks**. Maximum new pilot spending is $1.50 and the SAME cumulative $5 guard applies. The exact bound is displayed first. Pilot responses are not independent treatment observations.
4. The progress bar and current-request timer stay here. Original prompts, responses and usage receipts are saved automatically. Rerunning resumes verified slots without rebilling.
5. Full games are blocked when the whole fixed sample lacks funding. Do not increase the old ledger cap, lower output allowances until JSON fails, or treat extra batched chains as independent replications.
"""), code('''
        from pathlib import Path
        import sys, json
        ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src/beergame_study").is_dir())
        if str(ROOT / "src") not in sys.path:
            sys.path.insert(0, str(ROOT / "src"))
        from beergame_study import pivot_transport_v2 as api
        from IPython.display import display, Markdown, Image
        import pandas as pd

        RUN_API = False
        BLOCKS = 40  # prospective independent blocks/model; prefixes 10/20/40
        CHAINS_PER_CLUSTER = 1  # more batched chains do not increase independent N
        EXPERIMENT = ROOT / "experiments/13_weekly_state_api_20261021"
        BUDGET_ROOT = ROOT / "experiments/12_pressure_framing_api_20261020"
        ledger_before_review = api.sha(BUDGET_ROOT / "data/api_budget.json")
        RUN = api.prepare(EXPERIMENT, BUDGET_ROOT, blocks=BLOCKS, chains_per_cluster=CHAINS_PER_CLUSTER)
        PLAN = api.read(RUN / "plan.json")
        COST = api.planning(RUN)
        print("Prepared development run:", RUN.name)
        print("Independent blocks/model:", BLOCKS, "| Arms: 3 | Weeks: 24")
        print("Expected main+probe calls:", PLAN["expected_requests"])
        display(pd.DataFrame([COST["budget"]]))
        display(pd.DataFrame(COST["preflight"]))
        print(f"All four pilot reservations: ${COST['preflight_reserve_usd']:.4f}; local cap $1.50.")
        print(f"Full-sample conservative bound: ${COST['full_fixed_sample_reservation_bound_usd']:.2f}.")
        print("Full study funded by remaining authorization:", COST["main_authorized_with_current_budget"])
        display(pd.DataFrame(COST["scenarios"]))
        assert api.sha(BUDGET_ROOT / "data/api_budget.json") == ledger_before_review
    '''), nbf.v4.new_markdown_cell("""## Review the actual results first

The figures below use the closed weekly-state run. The 10-versus-20-chain plot is **descriptive** because those chains were jointly generated. The separate 10/20/40-independent-block power plot uses hypothetical effect sizes, not invented observations. See `reports/review_20261025/REPORT.md` for the audit and interpretation.
"""), code('''
        REPORTS = EXPERIMENT / "reports/review_20261025"
        for name in ("01_observed_model_comparison", "02_observed_10_vs_20_chains", "03_prospective_power_assumptions"):
            display(Image(filename=str(REPORTS / "figures" / (name + ".png")), width=1000))
        selfcheck = REPORTS / "SELF_CHECK.md"
        if selfcheck.exists():
            display(Markdown(selfcheck.read_text(encoding="utf-8")))
        print("Read report:", REPORTS / "REPORT.md")
        print("Exact new protocol:", EXPERIMENT / "hypotheses/PIVOT_V2_20261025.md")
    '''), nbf.v4.new_markdown_cell("""## Hidden keys and visible progress (optional technical pilot)

This pilot only checks that the four proposed models can return the required decisions with high effort. It does **not** show that H1–H4 hold or that larger samples will become significant. Keep `RUN_API=False` to spend nothing. Keys remain in memory and are cleared from the fields when the job starts. No automatic retries or semantic repairs.
"""), code('''
        if not RUN_API:
            print("FREE REVIEW: no keys requested, no API calls made.")
        else:
            import ipywidgets as widgets
            import threading, time, html
            openai_key = widgets.Password(description="OpenAI key:", layout=widgets.Layout(width="600px"))
            anthropic_key = widgets.Password(description="Anthropic key:", layout=widgets.Layout(width="600px"))
            launch = widgets.Button(description="Run four format checks", button_style="warning", layout=widgets.Layout(width="260px"))
            progress = widgets.IntProgress(value=0, max=4, description="Completed:")
            status = widgets.HTML(value="Ready. Enter both keys, then click the button.")
            output = widgets.Output()
            display(widgets.VBox([openai_key, anthropic_key, launch, progress, status, output]))

            def start(_):
                if not openai_key.value or not anthropic_key.value:
                    status.value = "Both hidden fields are required. Do not paste keys in chat."
                    return
                credentials = {"openai": openai_key.value, "anthropic": anthropic_key.value}
                openai_key.value = anthropic_key.value = ""
                launch.disabled = True
                current = {"text": "Starting", "time": time.monotonic(), "done": False}
                def callback(event):
                    current["text"] = event["task_id"] + " | " + event["status"] + " | cumulative $" + f"{event['spent_usd']:.4f}"
                    current["time"] = time.monotonic()
                    if event["status"] in ("accepted", "failed"):
                        progress.value += 1
                def work():
                    try:
                        result = api.Runner(RUN, credentials, callback=callback).run_preflight()
                        with output:
                            display(pd.DataFrame([dict(model=m, format_passed=ok) for m, ok in result.items()]))
                            print("Pilot finished. This is a format check, not hypothesis verification.")
                            print("Receipts:", RUN / "attempts")
                        current["text"] = "Finished; see pilot table and receipts."
                    except Exception as exc:
                        current["text"] = api._clean(type(exc).__name__ + ": " + str(exc), credentials)
                    finally:
                        credentials.clear()
                        current["done"] = True
                        launch.disabled = False
                def heartbeat():
                    while not current["done"]:
                        status.value = html.escape(current["text"]) + " | current request " + str(int(time.monotonic() - current["time"])) + "s"
                        time.sleep(1)
                    status.value = html.escape(current["text"])
                threading.Thread(target=work, daemon=True).start()
                threading.Thread(target=heartbeat, daemon=True).start()
            launch.on_click(start)
    '''), nbf.v4.new_markdown_cell("""## Where to find prompts and results

- New exact technical prompts: the `prompt.txt` files inside this run's `attempts/` folder, frozen before sending.
- Literal responses and requested/reported models: `response.json` and `receipt.json` beside each prompt.
- Completed old study: `reports/history/b34972b65bf5/REPORT.md`; never pooled with v2.
- Free assistant self-check: `data/pivot_v2_assistant_development_20261025/`, summarized separately in `reports/review_20261025/SELF_CHECK.md`.
- Independent-block analysis: `scripts/analyze_pivot_v2.py`. Input is a validated 24-week block/arm outcome CSV plus a frozen inference plan. No missing observations are fabricated. New H4 uses order variance and bullwhip, not the older cost endpoint.

The prospective v2 main sample is **not collected**. A stronger model, extra chains or a different lecture may still yield a null or opposite result. The original H1–H4 remain unverified by these feasibility checks.
"""), code('''
        if not RUN_API:
            assert api.sha(BUDGET_ROOT / "data/api_budget.json") == ledger_before_review
            print("Review completed: shared ledger unchanged.")
    ''')]
    nb = nbf.v4.new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"}})
    DEST.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, DEST)
    print(DEST)


if __name__ == "__main__":
    main()
