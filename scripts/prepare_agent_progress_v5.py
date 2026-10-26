"""Prepare the read-only live notebook and preserve replaced navigation bytes."""
from pathlib import Path
from hashlib import sha256
import json
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/13_weekly_state_api_20261021'


def main():
    notebook = nbf.v4.new_notebook()
    notebook.metadata.kernelspec = dict(display_name='Python 3', language='python', name='python3')
    notebook.cells = [
        nbf.v4.new_markdown_cell('''# Live Beer Game progress

**Run all cells, then tick `Auto-refresh (10 s)`.** Keep this notebook and its kernel open.
You can also click **Refresh now** at any time. Untick auto-refresh to pause the display.

This notebook watches the agents already running in Codex. It **does not start or resume agents**, make API calls, or spend the repository API budget. The display updates after saved decision pages, not continuously while a model is thinking. If collection pauses, the last saved time stays unchanged.

The bars show decision pages. The table shows completed weeks for A, B and C, followed by H1-H4 results when available. **Pending is not a failed hypothesis.** Each complete run contains 50 chains per condition, but is only one fresh model context for statistics.
'''),
        nbf.v4.new_code_cell('''from pathlib import Path
import sys

ROOT = next((p for p in (Path.cwd(), *Path.cwd().parents)
             if (p / "src/beergame_study/agent_progress_v5.py").is_file()), None)
if ROOT is None:
    raise RuntimeError("Open this notebook inside the D:/beergame repository.")
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
from beergame_study.agent_progress_v5 import notebook_monitor
if "monitor" in globals():
    monitor["close"]()
monitor = notebook_monitor(ROOT)
'''),
        nbf.v4.new_markdown_cell('''## What is being compared?

- **A:** matched control lecture, initial decision and separate revision opportunity.
- **B:** matched control lecture, one committed decision.
- **C:** causal education, one committed decision.

**H1:** B-A pipeline sensitivity. **H2:** B-A cost. **H3:** C-B pipeline sensitivity.
**H4a:** C-B order variance. **H4b:** C-B bullwhip ratio.

These are AI decision-opportunity experiments, not measured human clock deadlines. The same context sees all three conditions, so education carryover is possible. Complete games are replayed before displaying outcomes; inference also requires a transcript review. Repeated continuations of one agent are not additional independent runs. Live statistics are exploratory; collection does not stop at the first small p-value.

Use [the experiment guide](../README.md) for the current prompts and preserved earlier studies. Raw checkpoints are in `../data/assistant_v5_20261025/`. The separate [manual website notebook](LARGE_SAMPLE_V5.ipynb) handles responses you collect yourself.
''')]
    target = EXP / 'notebooks/AGENT_PROGRESS.ipynb'
    if target.exists():
        raise ValueError('Notebook exists; do not replace a user-edited notebook.')
    nbf.write(notebook, target)

    backup = EXP / 'analysis/agent_progress_v5/navigation_before'
    backup.mkdir(parents=True, exist_ok=True)
    files = ['README.md', 'experiments/README.md',
             'experiments/13_weekly_state_api_20261021/README.md', 'AGENT_HANDOFF.md']
    receipt = []
    for relative in files:
        path = ROOT / relative
        if not path.exists():
            continue
        raw = path.read_bytes()
        saved = backup / relative.replace('/', '__')
        if saved.exists() and saved.read_bytes() != raw:
            raise ValueError('Navigation backup differs: ' + relative)
        saved.write_bytes(raw)
        receipt.append(dict(path=relative, sha256=sha256(raw).hexdigest(), saved=str(saved.relative_to(ROOT))))
    (backup / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')

    paths = dict(root=ROOT / 'README.md', index=ROOT / 'experiments/README.md', exp=EXP / 'README.md')
    for kind, path in paths.items():
        text = path.read_text(encoding='utf-8')
        if kind == 'root':
            start = text.index('## Latest:')
            marker = 'The navigation below describes preserved earlier stages.'
            end = text.index(marker) + len(marker)
            current = '''## Current: live agent collection and 50-chain manual batches

**[Open the live progress notebook](experiments/13_weekly_state_api_20261021/notebooks/AGENT_PROGRESS.ipynb). Run all cells, then tick Auto-refresh (10 s).** It shows saved pages, completed weeks and H1-H4 status for GPT-6 Astra, GPT-6.1 Sol and GPT-6 Luna. It monitors collection; it does not launch agents or call an API.

For your own website collection: [four prompts + helper](experiments/13_weekly_state_api_20261021/prompts/LARGE_SAMPLE_V5/README.md), [manual analysis notebook](experiments/13_weekly_state_api_20261021/notebooks/LARGE_SAMPLE_V5.ipynb), [manual report / sample-size plan](experiments/13_weekly_state_api_20261021/reports/large_sample_v5/REPORT.md). V5 uses 50 chains per condition, three conditions and 24 weeks per fresh context. Agent and website samples remain separate. One context is one replication; the 50 chains are dependent. Current agent collection is ongoing, not an established significance result.

The navigation below describes preserved earlier stages.'''
        elif kind == 'index':
            start = text.index('**Current four-prompt workflow:**')
            end = text.index('\n\n', start)
            current = '''**Current v5 workflow:** [live agent progress notebook](13_weekly_state_api_20261021/notebooks/AGENT_PROGRESS.ipynb), [four manual website prompts](13_weekly_state_api_20261021/prompts/LARGE_SAMPLE_V5/README.md), and [manual analysis notebook](13_weekly_state_api_20261021/notebooks/LARGE_SAMPLE_V5.ipynb). Fifty chains per condition, three conditions, 24 weeks per fresh context. The live monitor reads the ongoing local-agent collection; website responses remain separate. Earlier workflows below are preserved records.'''
        else:
            start = text.index('## Current:')
            marker = 'All sections below are earlier workflows and records.'
            end = text.index(marker) + len(marker)
            current = '''## Current: live agent collection and manual v5

**[LIVE PROGRESS: AGENT_PROGRESS.ipynb](notebooks/AGENT_PROGRESS.ipynb)**

1. Open that notebook and select the project's Python environment (`D:/beergame/.venv/Scripts/python.exe`).
2. Run all cells.
3. Tick **Auto-refresh (10 s)**, or click **Refresh now**.

The notebook reads saved checkpoints from `data/assistant_v5_20261025/`. It shows each model's progress, A/B/C weeks, completed chain-games and H1-H4 status. It does not start or resume agents, change decisions, or make API calls. Keep the notebook kernel open for automatic refresh. A model thinking between submissions will not move its bar; check the last saved timestamp. `Pending` means data/review are incomplete, not a failed hypothesis.

Current agent models: requested GPT-6 Astra, GPT-6.1 Sol and GPT-6 Luna, all high effort. Each fresh context completes 50 chains per condition, three conditions and 24 weeks (224 submitted pages). Follow-up turns resume the same context. Counts of chains, roles or weeks do not increase the independent sample size. Each completed run needs physical replay and public-transcript review before inferential use. Claude remains a manual website route.

**Manual route:** [four prompts + ZIP](prompts/LARGE_SAMPLE_V5/README.md), [analysis notebook](notebooks/LARGE_SAMPLE_V5.ipynb), [protocol](hypotheses/MANUAL_BATCH_V5.md), [report / planning figures](reports/large_sample_v5/REPORT.md), [v5 validation](reports/large_sample_v5/VALIDATION.json). Frozen physics study: `manual_batch_v5_614dfdfeb3f15acf`. Website and agent observations are kept separate.

H1/H3 use pipeline-response sensitivity, H2 total cost, and H4a/b order variance and bullwhip. The treatment is one versus two decision opportunities, not a measured clock deadline. All three conditions share one context, so education carryover is possible. Live statistics are exploratory; collection does not stop when a p-value first crosses .05. No student validation or guaranteed significance is claimed.

The read-only monitor is implemented in `src/beergame_study/agent_progress_v5.py`; its builder is `scripts/prepare_agent_progress_v5.py`. Validation is saved in `analysis/agent_progress_v5/VALIDATION.json`. The prior navigation bytes are preserved alongside it. Frozen v3/v4/v5 protocol files, prompts, raw decisions and publications are unchanged. No direct API requests were added; the same shared ledger remains $1.179072025 of $5.

All sections below are earlier workflows and records.'''
        path.write_text(text[:start] + current + text[end:], encoding='utf-8', newline='')
    print(target)


if __name__ == '__main__':
    main()
