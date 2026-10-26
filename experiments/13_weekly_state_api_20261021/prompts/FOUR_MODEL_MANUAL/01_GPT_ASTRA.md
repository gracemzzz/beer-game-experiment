Run the attached Beer Game task using real Python/code execution. Requested model slot: GPT-6 Astra. The researcher selects the actual model; do not claim that this prompt changes your model. If Python is unavailable, report that and stop. Make no API requests, delegate no decisions, and use no other model. Run this batch to completion without asking the user for weekly inputs.

You simulate hypothetical second-year business students at the University at Buffalo, an American university. They are fictional participants, not actual students. Keep their supplied ordinary-coursework profiles consistent. Make plausible student decisions based on the current displayed information and that group's classroom reading. Their aim is to minimize cumulative team inventory-holding and backlog costs in a continuing game. Do not invent differences between students or groups to satisfy an experiment.

There are three groups, each containing 10 four-role chains. The helper selects their sequence. Complete all three groups in this chat. Each group has 24 decision weeks followed by separate hypothetical order decisions. The groups share this chat's context; do not claim they are independent experiments.

Rules: roles are retailer, wholesaler, distributor, factory. Each order is a nonnegative integer. Holding costs 0.5 per case/week; backlog costs 1 per case/week. Backlog already includes current unfilled demand. Outstanding replenishment is previously ordered goods not yet received. Upstream order information takes one week; shipments take two weeks; factory production takes three weeks. Orders cannot be cancelled. Python handles receipts and shipments before decisions. All displayed inventories are shared. Future demand is unknown. Treat the game as continuing beyond the scored horizon; do not liquidate stock just because the export ends.

SETUP — run this once in Python. Change only the ZIP path to its actual uploaded location. Do not display helper source, inspect private state/RNG, read other project files, or change the helper. Reading the named ZIP entries as bytes to install them is allowed; printing or examining their source is not.
```python
from pathlib import Path
import hashlib, json, sys, tempfile, zipfile
uploaded_zip = Path('beer_game_tools.zip')
assert hashlib.sha256(uploaded_zip.read_bytes()).hexdigest() == '9fd85234152f9f018158a2400dbc3d198693429d530bacaa5057d20c46964b25'
work = Path(tempfile.mkdtemp(prefix='beer_game_'))
with zipfile.ZipFile(uploaded_zip) as z:
    for name in ('beergame_controller.py', 'batch_runner.py'):
        (work / name).write_bytes(z.read(name))
sys.path.insert(0, str(work))
from batch_runner import Batch
run = Batch(model_slot='gpt_astra')
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
