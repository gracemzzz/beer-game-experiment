"""Create the API-free manual website notebook, with frozen prompt navigation."""
from pathlib import Path
import textwrap
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "experiments/13_weekly_state_api_20261021/notebooks/MANUAL_WEBSITE.ipynb"


def code(source):
    return nbf.v4.new_code_cell(textwrap.dedent(source).strip())


def main():
    cells = [nbf.v4.new_markdown_cell("""# Beer Game — manual website workflow

**No API calls, no API keys.** Keep the cumulative API cap at $5. The website model uses its own Python/code-execution tool to run ten chains (40 fictional students) per chat. You copy one prompt; the model processes the weeks and returns a JSON file.

1. Run this notebook unchanged to get the helper and prompt links.
2. In a **fresh website chat with Python/code execution**, upload `beergame_controller.py`, then paste the entire PILOT A prompt. Repeat PILOT B and C in two other fresh chats, using the same model and reasoning mode.
3. Let each chat finish and download its JSON. Also save the **full chat/tool transcript**; this is needed to verify that the model chose decisions after each state, rather than writing an automatic ordering algorithm.
4. Send those files here with the exact displayed model/mode, or use the import cell below. We review these three pilots before starting main collection. Pilot signs do not determine acceptance.
5. After pilot review, use the prepared numbered main prompts in fresh chats. There are fixed 10/20/40 independent-block analysis prefixes; do not stop at the first small p-value.

Each matched block has three chats. Ten chains within a chat are dependent. Arm A gets an extra model reconsideration pass; B/C commit their first choices, with C receiving causal education. This tests an AI review-opportunity analogue, not a calibrated human deadline. Large simulated headcounts do not guarantee significance or student realism.
"""), code('''
        from pathlib import Path
        import sys, json
        ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src/beergame_study").is_dir())
        if str(ROOT / "src") not in sys.path:
            sys.path.insert(0, str(ROOT / "src"))
        from beergame_study import manual_workflow_v3 as manual
        from IPython.display import display, Markdown
        import pandas as pd
        EXPERIMENT = ROOT / "experiments/13_weekly_state_api_20261021"
        LEDGER = ROOT / "experiments/12_pressure_framing_api_20261020/data/api_budget.json"
        ledger_before = manual.sha(LEDGER)
        RUN = manual.prepare(EXPERIMENT, blocks=40, chains=10)
        MANIFEST = manual.load_manifest(RUN)
        PROMPTS = EXPERIMENT / "prompts" / RUN.name
        print("Study:", RUN.name)
        print("API requests from this notebook: 0")
        print("API spending unchanged:", sum(a['charge_usd'] for a in manual.read(LEDGER)['attempts'].values()))
        def link(label, path):
            return f"[{label}]({path.as_posix()})"
        display(Markdown("\\n\\n".join([
            link("1. Helper to upload", PROMPTS / "beergame_controller.py"),
            link("2. PILOT A prompt", PROMPTS / "00_PILOT_A.md"),
            link("3. PILOT B prompt", PROMPTS / "00_PILOT_B.md"),
            link("4. PILOT C prompt", PROMPTS / "00_PILOT_C.md"),
            link("All main prompts, organized into waves of ten", PROMPTS / "README.md"),
        ])))
        print("Store returned files here if convenient:", RUN / "inbox")
    '''), nbf.v4.new_markdown_cell("""## Import a returned JSON and transcript

The import saves original bytes and replays the physical game. `TRANSCRIPT_REVIEWED=False` keeps a submission outside the eligible hypothesis analysis. Set it true only after checking the full tool history for literal model choices after each returned state, separate A initial/review interactions, no programmed decision policy, and adherence to the assigned model/case. Record the reviewer and evidence. A replay pass alone does not establish that provenance.

Keep the model slot and exact website label/reasoning mode consistent across its three arms. Slots are grouping labels, not verified API IDs. The default first slot is `gpt_flagship`; later replications use `gpt_balanced`, `gpt_economy`, `claude` if available. Never infer a website model's backend or silently switch models.
"""), code('''
        IMPORT_NOW = False
        JSON_PATH = r""  # downloaded controller export
        TRANSCRIPT_PATH = r""  # saved full chat/tool transcript, text/HTML/PDF/export
        MODEL_SLOT = "gpt_flagship"
        WEBSITE_MODEL_LABEL = ""  # exact displayed website and model name
        REASONING_SETTING = ""  # exact selected setting; use 'not exposed' if truly unavailable
        TRANSCRIPT_REVIEWED = False
        REVIEWER = ""
        REVIEW_NOTE = ""
        if IMPORT_NOW:
            receipt = manual.intake(RUN, JSON_PATH, TRANSCRIPT_PATH,
                model_slot=MODEL_SLOT, website_label=WEBSITE_MODEL_LABEL,
                reasoning_setting=REASONING_SETTING, transcript_reviewed=TRANSCRIPT_REVIEWED,
                reviewer=REVIEWER, review_note=REVIEW_NOTE)
            display(pd.DataFrame([{k:v for k,v in receipt.items() if k != 'outcome'}]))
        else:
            print("No files imported. Fill paths/settings and set IMPORT_NOW=True when ready.")
    '''), nbf.v4.new_markdown_cell("""## Progress and hypothesis analysis

The table counts independently started chat/block arms, not students. Only main cases with validated replay and explicit transcript review enter the eligible outcome table. Partial games and missing probes remain visible and cannot become complete observations. Until the fixed maximum is collected, results are provisional.

Effects, matched-block intervals, two-sided tests and five/twenty-endpoint corrections are saved separately. The fixed 10/20/40 prefixes show how estimates change with independent replications; they are not a stopping rule. No fabricated rows or synthetic trajectories enter the study.
"""), code('''
        ANALYSIS, RESULT, RECEIPTS = manual.analyze(RUN)
        summary = []
        for slot in MANIFEST['model_slots']:
            own = [r for r in RECEIPTS if r['model_slot'] == slot]
            main = [r for r in own if r['collection_kind'] == 'heldout']
            summary.append(dict(model_slot=slot, pilot_files=sum(r['collection_kind']=='development' for r in own),
                main_files=len(main), replay_passed=sum(r['replay_passed'] for r in main),
                reviewed_eligible=sum(r['eligible_for_heldout'] for r in main),
                complete_games=sum(r['outcome'] is not None and r['outcome']['complete'] for r in main),
                planned_main_chats=MANIFEST['blocks']*3))
        display(pd.DataFrame(summary))
        print('Completed eligible 24-week games:', RESULT['complete_game_cluster_arm_rows'])
        print('Independent blocks planned/model:', MANIFEST['blocks'])
        if RESULT['complete_game_cluster_arm_rows'] == 0:
            print('No eligible completed main games yet. No observed-effect plots or conclusions generated.')
        else:
            display(pd.DataFrame(RESULT['primary'])[['model','hypothesis','n_pairs','mean_difference','p_holm_within_model_5','p_holm_across_models_20','direction']])
        display(Markdown(link('Analysis report', ANALYSIS / 'REPORT.md')))
        print('Extracted tables:', ANALYSIS)
        assert manual.sha(LEDGER) == ledger_before, 'This API-free workflow must not change the shared ledger.'
    ''')]
    notebook = nbf.v4.new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"}})
    DEST.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, DEST)
    print(DEST)


if __name__ == "__main__":
    main()
