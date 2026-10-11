> **CURRENT RERUN:** open [START_HERE_bounded_rerun.ipynb](START_HERE_bounded_rerun.ipynb), using [bounded_experiment.py](bounded_experiment.py). This fresh GPT-5.4 nano low/medium protocol limits weekly orders to 0–40 and fits beta with the same cap. Read [BOUNDED_RERUN_PROTOCOL.md](BOUNDED_RERUN_PROTOCOL.md). Default: four full groups / 16 agents / 36 agent weeks / $0.75 allowance. Scoring now adds 36 automatic continuation weeks with no API calls; see `scored_team_costs.csv` for the full objective. Automatic rounds never enter beta estimation. Earlier notebooks and results below are historical protocols.

> **Rate-limit recovery prepared:** reopen the current notebook with its unchanged replicate ID. It reuses 307 valid responses from the stopped run, uses four paced workers, and waits/retries temporary rate limits. See [RATE_LIMIT_RECOVERY.md](RATE_LIMIT_RECOVERY.md). The $0.75 allowance includes prior estimated charges and reservations.

> **Prompt audit:** current-state observations now follow the full local history, response fields copy observations before choosing an order, and rules questions map directly to their fields. See [PROMPT_AND_STABILITY_AUDIT.md](PROMPT_AND_STABILITY_AUDIT.md). New reports show first-attempt reliability; live improvement is not yet measured.

> **Group replacement:** after exhausting correctness retries, the current notebook saves the failed four-role group and starts a fresh group in the same condition. Target: `groups_per_cell` completed groups in each of four conditions. At most 3 replacements per target group, with all spending inside the $0.75 guard. Failed candidates remain audited; replacements are never based on beta or significance. Replacements trigger withholding of confirmatory p-values.

> **Retry update:** current notebook allows two logged retries after an incorrect observation/rules reply (three attempts total), within the same $0.75 allowance. All attempts are preserved and included in resource reporting; unresolved failures still stop. Reload the notebook from disk to use the new protocol.

> **Current speed settings:** the verification notebook now compares **minimal versus low reasoning** on GPT-5 nano, with 8 concurrent requests and a shared 8,192-token ceiling. This replaces low/high as a new protocol; old results remain separate. Lower effort should reduce token use and latency, but savings are not yet measured. The $0.75 guard remains. Reopen the notebook from disk and restart before running. H2_API is the revised effort comparison, not human time pressure.

> **Current next step — $0.75 verification:** Open [START_HERE_verify_budget.ipynb](START_HERE_verify_budget.ipynb), beside [budget_verification.py](budget_verification.py). It tests GPT-5 nano in four full standard-cost Beer Games, reports beta/performance/cost, and never automatically upgrades models. Use this for the next test; v3 is a separate nonstandard profit variant.

> **Profit-based v3:** Use [thoughts_reflection_experiment_v3.ipynb](thoughts_reflection_experiment_v3.ipynb), beside [beer_game_v3.py](beer_game_v3.py). See [V3_START_HERE.md](V3_START_HERE.md). This is the latest full-game version; prior protocols are retained.

> **Redesigned v2:** Start with [V2_START_HERE.md](V2_START_HERE.md) and [thoughts_reflection_experiment_v2.ipynb](thoughts_reflection_experiment_v2.ipynb). The original experiment below is retained for reproducibility. V2 tests training × reasoning effort, with diagnostics and corrected group-level inference.

# Thoughts reflection experiment

Open `thoughts_reflection_experiment.ipynb`. It implements the training × 60/120-second design from `../Thoughts reflection.docx` using four GPT roles per supply-chain group. The notebook includes the assumptions, prompts, simulator, API runner, β estimation, H1/H2 contrasts, diagnostics, and plots.

## Setup

From this directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab thoughts_reflection_experiment.ipynb
```

Use the Python kernel from this environment. The notebook includes an installation cell for an existing notebook environment.

## Run

1. Leave `MODE = "offline"` and run all cells for a free synthetic demonstration.
2. To collect GPT decisions, set `MODE = "api"`, select a model accessible to your API account, save the notebook, and restart/run all cells. The notebook reads `OPENAI_API_KEY` or prompts for it with hidden input. Do not put the key in notebook source.
3. Default pilot: 1 group per cell × 4 cells × 4 roles × 24 weeks = **384 API requests**. This is a functionality pilot; one group per cell cannot support inference.
4. Full reflection layout: `GROUPS_PER_CELL = 15`, giving 240 GPT agents. With `WEEKS = 36`, this is **8,640 requests**, with API charges. It is not a power calculation or a human experiment.
5. Change `REPLICATE_ID` to collect a fresh run. Keep it unchanged to resume cached responses. Save code edits before running; saved code and settings determine the result directory.

Outputs are under `results/`. Included executed outputs are **synthetic**, not GPT findings. Failures are preserved, and affected groups are excluded from primary comparisons. Check fit quality, group exclusions, actual latencies, and fallback rates before reading the hypothesis contrasts.

The 60/120-second manipulation combines deadline wording with an enforced request deadline. API latency is not human thinking time; GPT results cannot establish the reflection's claims about students.

## Validation

```sh
python test_notebook.py
```

These checks use synthetic decisions and an HTTP mock of the OpenAI SDK. They cover inventory conservation, delivery delays, known-β recovery (including β=0), group-level contrast signs, treatment isolation, parsed responses, refusals, timeouts, and resumable runs. No live API call is needed.

API implementation references: [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) and [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini). Beer-game mechanics and estimator references are linked in the notebook.

## API credit error fixed (protocol 1.1)

The attempted API run returned the specific code `credit_balance_exhausted`: the API organization has no prepaid credits remaining. This was confirmed by a single diagnostic request using the existing notebook client; the key was not displayed or saved.

1. Open https://platform.openai.com/settings/organization/billing/overview for the organization owning the API key and select **Add to credit balance**.
2. After the balance updates, close and reopen the updated notebook, then run all cells and enter the key in the hidden prompt. If the editor asks about the external file change, load the version from disk.
3. The notebook now makes one small access check first, then prints progress every week. API errors stop the run and show the specific action; they do not silently become experimental orders.

Your settings remain API mode, 4 groups per condition, and 36 weeks. The new replicate is `api-pilot-02`; the failed run is preserved separately. The access check is an extra small paid request when it succeeds.

## Live progress bar

The run cell shows a native Jupyter progress bar without extra widget dependencies. It updates after each role finishes and shows processed/remaining decisions, successful GPT responses, fallback/error counts, reused cached records, current group/week, elapsed time, and an approximate ETA. Failed API access shows **Stopped** with zero experiment decisions completed. The separate access-check request is excluded from the 2,304-decision total for your 4-group/36-week settings. ETA is omitted on resumed runs because cached decisions are not representative of API speed. The same counts are saved to `progress.json`.

Close and reopen the notebook to load this update, then run all cells. If a simulation is already running, allow it to finish or stop it before reloading; editing the file does not update an already-running cell.

## Resume the interrupted API run

The notebook is configured with `RESUME_RUN_DIR = "api_023f89662165ca64"`. Keep 4 groups/cell, 36 weeks, the same model, and `REPLICATE_ID = "api-pilot-02"`. Reopen the saved notebook and run all cells. It reuses the 1,442 successful responses already saved and collects the remaining 862 decisions. Changing any experimental setting is rejected during explicit resume. Set `RESUME_RUN_DIR = None` only to start a separate experiment.

Connection failures receive up to three attempts inside one 60/120-second decision window, including backoff; SDK retries remain disabled. Saved connection errors are archived in `connection_errors/` before retrying. A retry after restarting gets a new window and is marked `recovered_after_restart`; that entire group remains in descriptive outputs but is excluded from primary hypothesis contrasts. The original failed attempts and resume/code-version events are retained. Billing and authentication errors are not automatically retried. Successful cached responses are never requested again, although a failed transport request may already have reached the server and incurred usage.
