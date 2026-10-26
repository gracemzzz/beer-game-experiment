"""Build four reusable prompts and a shared upload package. No API access."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study import manual_batch_v4 as batch
from beergame_study import manual_batch_analysis_v4 as analysis

EXP = ROOT / "experiments/13_weekly_state_api_20261021"
PROMPTS = EXP / "prompts/FOUR_MODEL_MANUAL"
MODELS = (("gpt_astra", "GPT-6 Astra", "01_GPT_ASTRA.md"),
          ("gpt_sol", "GPT-6.1 Sol", "02_GPT_SOL.md"),
          ("gpt_luna", "GPT-6 Luna", "03_GPT_LUNA.md"),
          ("claude_sonnet", "Claude Sonnet 5.5", "04_CLAUDE_SONNET.md"))


def prompt(slot, model, zip_hash):
    return f'''Run the attached Beer Game task using real Python/code execution. Requested model slot: {model}. The researcher selects the actual model; do not claim that this prompt changes your model. If Python is unavailable, report that and stop. Make no API requests, delegate no decisions, and use no other model. Run this batch to completion without asking the user for weekly inputs.

You simulate hypothetical second-year business students at the University at Buffalo, an American university. They are fictional participants, not actual students. Keep their supplied ordinary-coursework profiles consistent. Make plausible student decisions based on the current displayed information and that group's classroom reading. Their aim is to minimize cumulative team inventory-holding and backlog costs in a continuing game. Do not invent differences between students or groups to satisfy an experiment.

There are three groups, each containing 10 four-role chains. The helper selects their sequence. Complete all three groups in this chat. Each group has 24 decision weeks followed by separate hypothetical order decisions. The groups share this chat's context; do not claim they are independent experiments.

Rules: roles are retailer, wholesaler, distributor, factory. Each order is a nonnegative integer. Holding costs 0.5 per case/week; backlog costs 1 per case/week. Backlog already includes current unfilled demand. Outstanding replenishment is previously ordered goods not yet received. Upstream order information takes one week; shipments take two weeks; factory production takes three weeks. Orders cannot be cancelled. Python handles receipts and shipments before decisions. All displayed inventories are shared. Future demand is unknown. Treat the game as continuing beyond the scored horizon; do not liquidate stock just because the export ends.

SETUP — run this once in Python. Change only the ZIP path to its actual uploaded location. Do not display helper source, inspect private state/RNG, read other project files, or change the helper. Reading the named ZIP entries as bytes to install them is allowed; printing or examining their source is not.
```python
from pathlib import Path
import hashlib, json, sys, tempfile, zipfile
uploaded_zip = Path('beer_game_tools.zip')
assert hashlib.sha256(uploaded_zip.read_bytes()).hexdigest() == '{zip_hash}'
work = Path(tempfile.mkdtemp(prefix='beer_game_'))
with zipfile.ZipFile(uploaded_zip) as z:
    for name in ('beergame_controller.py', 'batch_runner.py'):
        (work / name).write_bytes(z.read(name))
sys.path.insert(0, str(work))
from batch_runner import Batch
run = Batch(model_slot='{slot}')
print(json.dumps(run.display(), separators=(',', ':')))
run.save(work)
```

AFTER EVERY DISPLAY
- Read the current group's classroom reading and the returned `decision`. Its state columns are named in the display. Every row corresponds to one fictional role.
- For `initial` or `revision`, choose 40 literal integer orders: a dictionary mapping every chain ID to [retailer, wholesaler, distributor, factory]. For `probe_initial` or `probe_revision`, choose one literal integer for every displayed probe ID. Probes are separate hypothetical decisions, not additional game weeks.
- Call `run.submit(YOUR_LITERAL_DICTIONARY)` and print its returned display. Then call `run.save(work)` to checkpoint. Replace the placeholder with actual literal choices; do not run a placeholder. Each next decision must follow a newly returned tool display.
- A `revision` / `probe_revision` phase requires a SEPARATE assistant/tool interaction after seeing initial proposals. You may keep or change any order. Other phases commit initial choices. Do not combine initial and revision submissions in one tool call.
- Continue until the returned top-level phase is `complete`. The next group starts automatically. Do not stop after the first group or after the game weeks before completing probes. Show only brief progress updates (group and week), without analyzing comparisons.

DECISIONS MUST COME FROM YOU
Python is for physical accounting, storage and formatting only. Do not write a policy, optimizer, random-order generator, decision loop, or formula that supplies orders. Do not precompute future choices, copy an earlier group's decisions, or run multiple submissions in one tool call. Choose the literal orders after each current display. Preserve any zeros, constants or unchanged revisions you choose. No desired treatment difference, minimum order, preferred maximum, statistical target or required oscillation is specified. Do not calculate p-values, compare groups, or search for a desired result during collection. Do not provide hidden reasoning traces; the visible choices and tool calls are the required record.

RETURN ONE FILE
```python
assert run.export()['complete'] is True
result_path = run.save(work)
print(result_path)
```
Provide a downloadable link to that exact JSON. It contains all three groups, weekly orders, probes and controller records. Do not replace it with a summary or edited table. Keep the authentic full chat/tool transcript available for researcher export; never invent a transcript or substitute a reconstruction. Leave actual model/reasoning metadata UNRECORDED; the researcher will report the selected UI labels separately.

If interrupted by usage, context or tool limits, return the latest saved partial JSON, identify the last group/week, and say incomplete. Do not fabricate remaining choices or restart silently. If downloadable files cannot be returned, paste the exact complete/partial `run.export(require_complete=False)` JSON. A continuation of this same run remains one batch.
'''


def main():
    PROMPTS.mkdir(parents=True, exist_ok=True)
    archive = PROMPTS / "beer_game_tools.zip"
    from io import BytesIO
    blob = BytesIO()
    files = {"beergame_controller.py": ROOT / "src/beergame_study/manual_weekly_v3.py",
             "batch_runner.py": ROOT / "src/beergame_study/manual_batch_v4.py"}
    with zipfile.ZipFile(blob, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, source in files.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, source.read_bytes())
    analysis.freeze(archive, blob.getvalue())
    zip_hash = analysis.sha(archive)
    for slot, model, filename in MODELS:
        analysis.freeze(PROMPTS / filename, prompt(slot, model, zip_hash).encode())
    run = EXP / "data" / batch.study_id()
    (run / "inbox").mkdir(parents=True, exist_ok=True)
    sources = dict(files)
    sources.update(analysis=ROOT / "src/beergame_study/manual_batch_analysis_v4.py",
                   inference=ROOT / "src/beergame_study/pivot_inference_v2.py",
                   protocol=EXP / "hypotheses/MANUAL_BATCH_V4.md", builder=Path(__file__))
    manifest = dict(study_id=batch.study_id(), source_hashes={k: analysis.sha(v) for k, v in sources.items()},
        prompts={name: analysis.sha(PROMPTS / name) for _, _, name in MODELS}, zip_sha256=zip_hash,
        requested_models={slot: model for slot, model, _ in MODELS}, independent_unit="fresh chat",
        chains_per_arm=10, arms=3, weeks=24, planned_attempts_per_model=40,
        sweep_prefixes=list(analysis.PREFIXES), source_kind="uncollected_model_observations",
        context="three conditions share one chat; education carryover possible", api_calls=0)
    analysis.freeze(run / "manifest.json", manifest)
    for key, path in sources.items():
        analysis.freeze(run / "source_snapshot" / (key + "_" + path.name), path.read_bytes())
    guide = '''# Start here — four prompts, four models

1. Open **four fresh code-enabled chats**, selecting the four models below. For OpenAI use Work/Codex if needed; Sol/Luna are not currently ordinary Chat models. Use high reasoning where offered and keep each model's setting fixed. Use Claude thinking/high where offered. Do not use Ultra/delegation for this protocol. If a named model is unavailable, tell the researcher the available names before substituting.
2. Attach the SAME [beer_game_tools.zip](beer_game_tools.zip) in each chat. Open the matching prompt below, **copy its entire text**, and paste it. The model runs all three conditions automatically. No weekly input or API key is needed.
3. Download the returned JSON from each chat. **Upload the four JSON files back into this Codex conversation**, with the exact displayed model/mode and the saved full chat/tool transcripts. Preserve partial/failed files too. Do not send only screenshots or summaries.

| Selected model | Copy this prompt |
|---|---|
| GPT-6 Astra | [01_GPT_ASTRA.md](01_GPT_ASTRA.md) |
| GPT-6.1 Sol | [02_GPT_SOL.md](02_GPT_SOL.md) |
| GPT-6 Luna | [03_GPT_LUNA.md](03_GPT_LUNA.md) |
| Claude Sonnet 5.5 | [04_CLAUDE_SONNET.md](04_CLAUDE_SONNET.md) |

**You have exactly four prompt files.** To collect more observations, reuse the SAME model's prompt plus ZIP in a NEW chat. No prompt editing or manual numbering is needed. Start with one response per model. The fixed collection target is 40 attempted chats per model; failures count and remain recorded. Do not stop or change prompts based on a p-value. Website usage limits may require a continuation in the same chat; it is still one run. No new repository API charges occur.

Each response contains 10 chains × three conditions × 24 weeks: **30 chain instances / 120 fictional student roles**, 2,880 weekly orders and 480 final probe decisions. A JSON is the saved decision record, not a result generated by an ordering algorithm. Python only advances the game; the model supplies each week's choices.

A = control reading with an extra review; B = control with first choice committed; C = causal education with first choice committed. All receive shared inventory information. The extra-review rule is an AI opportunity constraint, not an enforced human deadline. Keeping all conditions in one chat makes collection easier but permits education carryover. These are exploratory AI comparisons, not validated student findings.

One response per model is **one generation cluster**, so it cannot establish statistical significance. Ten chains in that response are dependent. Repeated fresh chats let analysis plot evidence at 10/20/50/100/200/400 chains per condition, corresponding to 1/2/5/10/20/40 chats. The planning plot shows assumed detection probabilities, not a guaranteed chain count or a prediction fitted to the old null H1/H3 pilot.

- [Notebook: import, progress and H1–H4 analysis](../../notebooks/FOUR_MODEL_MANUAL.ipynb)
- [Current report and sample-size planning figure](../../reports/four_model_manual/REPORT.md)
- [Exact scientific protocol and limitations](../../hypotheses/MANUAL_BATCH_V4.md)
- [Previous A/B/C pilot results](../../reports/manual_pilot_review_20261025/REPORT.md)

Model/interface references: [OpenAI](https://learn.chatgpt.com/docs/models), [Claude](https://platform.claude.com/docs/en/models/sonnet-5-5/overview). Selectability depends on the account; a prompt cannot change the underlying model. No actual new model results have been collected by preparing these files.
'''
    analysis.freeze(PROMPTS / "README.md", guide.encode())
    notebook = nbf.v4.new_notebook(cells=[
        nbf.v4.new_markdown_cell("# Four-model manual Beer Game\n\n[Three simple steps and four prompts](../prompts/FOUR_MODEL_MANUAL/README.md). No API calls. Import the exact returned JSON and authentic transcript; set review flags only after checking adherence. The new joint-context sample is separate from all previous pilots."),
        nbf.v4.new_code_cell('''from pathlib import Path
import sys, json
import pandas as pd
from IPython.display import display, Markdown, Image
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'src/beergame_study').is_dir())
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study import manual_batch_v4 as batch
from beergame_study import manual_batch_analysis_v4 as analysis
EXP = ROOT / 'experiments/13_weekly_state_api_20261021'
RUN = EXP / 'data' / batch.study_id()
REPORT = EXP / 'reports/four_model_manual'
LEDGER = ROOT / 'experiments/12_pressure_framing_api_20261020/data/api_budget.json'
ledger_before = analysis.sha(LEDGER)
print('Study:', batch.study_id())
print('Returned files can be placed in:', RUN / 'inbox')'''),
        nbf.v4.new_markdown_cell("## Import returned files\n\nLeave this list empty to review existing data. Add one dictionary per response. The JSON and transcript are preserved exactly. Unreviewed/partial files stay in the intake log and cannot enter inference. `website_label` and `reasoning_setting` are your actual selections, not the requested prompt labels."),
        nbf.v4.new_code_cell('''IMPORTS = []
# Example (replace paths and actual UI labels):
# IMPORTS = [dict(json_path=r'D:\\downloaded.json', transcript_path=r'D:\\full_transcript.txt',
#    website_label='ACTUAL MODEL LABEL', reasoning_setting='ACTUAL MODE',
#    reviewed=False, fresh_chat_confirmed=False, reviewer='', note='')]
from tqdm.auto import tqdm
for item in tqdm(IMPORTS, desc='Validate and preserve returned batches'):
    receipt = analysis.intake(RUN, **item)
    print(receipt.get('model'), receipt.get('batch_id'), 'eligible:', receipt['eligible'], 'error:', receipt['error'])'''),
        nbf.v4.new_code_cell('''result = analysis.analyze(RUN, REPORT)
display(pd.DataFrame([dict(model=k, reviewed_batches=v, planned_attempts=40,
                           chains_per_condition=10*v, total_chain_instances=30*v)
                      for k, v in result['eligible_fresh_chat_batches'].items()]))
if result['observations']:
    display(pd.DataFrame(result['observations']))
    display(Image(filename=str(REPORT / 'OBSERVED_H1_H4_SWEEP.png')))
else:
    print('No reviewed new observations yet. H1-H4 remain unestablished.')
display(Image(filename=str(REPORT / 'SAMPLE_SIZE_PLANNING.png')))
display(Markdown((REPORT / 'REPORT.md').read_text(encoding='utf-8')))
assert analysis.sha(LEDGER) == ledger_before
print('API ledger unchanged. Planning curves are assumptions, not observed findings.')''')],
        metadata=dict(kernelspec=dict(display_name="Python 3", language="python", name="python3")))
    target = EXP / "notebooks/FOUR_MODEL_MANUAL.ipynb"
    if not target.exists():
        nbf.write(notebook, target)
    analysis.analyze(run, EXP / "reports/four_model_manual")
    print(json.dumps(dict(study_id=batch.study_id(), prompt_directory=str(PROMPTS), notebook=str(target)), indent=2))


if __name__ == "__main__":
    main()
