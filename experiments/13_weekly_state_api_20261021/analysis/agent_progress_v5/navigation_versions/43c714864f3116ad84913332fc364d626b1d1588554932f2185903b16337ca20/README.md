# Experiment 13: weekly Beer Game — API and manual website versions

## Current: live agent collection and manual v5

**[LIVE PROGRESS: AGENT_PROGRESS.ipynb](notebooks/AGENT_PROGRESS.ipynb)**

1. Open that notebook and select the project's Python environment (`D:/beergame/.venv/Scripts/python.exe`).
2. Run all cells.
3. Tick **Auto-refresh (10 s)** if shown. If `ipywidgets` is unavailable, the HTML display refreshes automatically; no installation is needed. To refresh immediately, run `monitor["refresh"]()`.

The notebook reads saved checkpoints from `data/assistant_v5_20261025/`. It shows each model's progress, A/B/C weeks, completed chain-games and H1-H4 status. It does not start or resume agents, change decisions, or make API calls. Keep the notebook kernel open for automatic refresh. A model thinking between submissions will not move its bar; check the last saved timestamp. `Pending` means data/review are incomplete, not a failed hypothesis.

Current agent models: requested GPT-6 Astra, GPT-6.1 Sol and GPT-6 Luna, all high effort. Each fresh context completes 50 chains per condition, three conditions and 24 weeks (224 submitted pages). Follow-up turns resume the same context. Counts of chains, roles or weeks do not increase the independent sample size. Each completed run needs physical replay and public-transcript review before inferential use. Claude remains a manual website route.

**Manual route:** [four prompts + ZIP](prompts/LARGE_SAMPLE_V5/README.md), [analysis notebook](notebooks/LARGE_SAMPLE_V5.ipynb), [protocol](hypotheses/MANUAL_BATCH_V5.md), [report / planning figures](reports/large_sample_v5/REPORT.md), [v5 validation](reports/large_sample_v5/VALIDATION.json). Frozen physics study: `manual_batch_v5_614dfdfeb3f15acf`. Website and agent observations are kept separate.

H1/H3 use pipeline-response sensitivity, H2 total cost, and H4a/b order variance and bullwhip. The treatment is one versus two decision opportunities, not a measured clock deadline. All three conditions share one context, so education carryover is possible. Live statistics are exploratory; collection does not stop when a p-value first crosses .05. No student validation or guaranteed significance is claimed.

The read-only monitor is implemented in `src/beergame_study/agent_progress_v5.py`; its builder is `scripts/prepare_agent_progress_v5.py`. Validation is saved in `analysis/agent_progress_v5/VALIDATION.json`; the missing-widget fix has four monitor tests and a successful notebook execution with widgets disabled in `analysis/agent_progress_v5/FALLBACK_VALIDATION.json`. If an existing kernel still has the old code, Restart Kernel and Run All. The prior navigation bytes are preserved alongside it. Frozen v3/v4/v5 protocol files, prompts, raw decisions and publications are unchanged. No direct API requests were added; the same shared ledger remains $1.179072025 of $5.



**H1?H4 versus chain size:** [five-panel presentation plot and exact data](reports/agent_collection_v5/chain_size_stability/README.md). X-axis: first 5/10/20/30/40/50 chains per condition. Y-axis: each hypothesis's condition difference, including both H4 metrics; green shows the predicted direction. Includes all complete non-excluded contexts, with pending reviews labeled provisional. Astra H3 and Luna H2 change sign across sizes; Astra/Sol H2/H4 signs are stable. This is descriptive direction stability, not a significance curve. Run `scripts/plot_agent_chain_size_stability_v5.py` after refreshing the agent report; original plotted values, hashes and earlier renders are preserved.

**Presentation figures:** [three slides and short captions](reports/agent_collection_v5/slides_first_context/README.md), available as PNG, SVG and a combined PDF. Frozen first-context snapshot: observed H2/H4 directions in Astra/Sol; H1/H3 predicted patterns absent; transcript review pending. The 5-to-50-chain curves are descriptive, not an independent sample-size significance curve. Exporter: `scripts/export_agent_slides_v5.py`; every 50-chain endpoint was checked against its condition summary, all figures visually inspected.

**Current agent results:** [report and extracted results](reports/agent_collection_v5/REPORT.md). The fixed first replication stage is 10 attempted fresh contexts per GPT model (500 chains per condition if all finish), recorded in `data/assistant_v5_20261025/REPLICATION_AMENDMENT_01.json`. Failed or excluded attempts remain in the count; they are not replaced according to outcome. The first Luna context is preserved but excluded from inference because 44 public displays were filtered and 43 were followed by submissions without restoring the full display. Luna run002 is also excluded because its public tool calls generated current-page choices with code. Raw results and both exclusions remain preserved. Later runs repeat the original full-display and literal-choice requirements explicitly.

All sections below are earlier workflows and records.


## Start here — manual website route, 25 October 2026

**Pilots now received:** all three GPT-6 Astra / ultra files completed 24 weeks and passed physical replay. [Pilot report](reports/manual_pilot_review_20261025/REPORT.md) · [Plots](reports/manual_pilot_review_20261025/FIGURE_CAPTIONS.md). The model/mode are user-reported and preserved separately from unchanged JSON metadata. All three pipeline sensitivities are 1.0. A's partial execution record supports its recorded decision steps, B lacks a full transcript, and C's provenance reports source exposure. The full-context adherence gate remains incomplete. These development pilots are excluded from the main independent-block analysis; no main sample or significance result is claimed.

The working manual notebook now shows these three received pilots and their plots in a separate review section. Its four default code cells executed successfully with no API calls and an unchanged shared ledger. The previous notebook/builder bytes were preserved with the pilot receipt; the frozen protocol, source, prompts and original JSONs are unchanged. [Notebook validation](reports/manual_pilot_review_20261025/NOTEBOOK_VALIDATION.json).

The user reaffirmed a **$5 maximum** and chose a website alternative to the expensive stronger-model API proposal. The active new route is [MANUAL_WEBSITE.ipynb](notebooks/MANUAL_WEBSITE.ipynb). It makes **no API calls** and needs no keys. [Simple five steps](reports/review_20261025/WEBSITE_STEPS.md) · [Helper and exact copyable prompts](prompts/WEBSITE_START_HERE.md) · [Manual protocol](hypotheses/MANUAL_V3_20261025.md).

Upload the helper in a fresh code-enabled website chat, paste one prompt, and let that chat run ten chains (40 fictional students) through the Python-controlled game. Return the JSON **and full chat/tool transcript**, plus exact website model/mode. Start with PILOT A/B/C; they remain development data. The notebook replays every state and keeps unreviewed transcripts outside the eligible main analysis. No automatic ordering policy, invented missing choices or assumed API backend is accepted.

The prepared main prompts cover fixed 10/20/40 independent matched blocks. Chains within a chat are dependent and averaged first. Three chats make one block; four models at 40 blocks require 480 main chats. The model supplies weekly orders and A's separate reconsideration, while Python handles physics. This is a resource-opportunity analogue, not calibrated human time pressure. Significance and student fidelity are not guaranteed.

The v2 paid proposal below is preserved as an **unfunded development option**. Do not mistake it for the active manual entry point or a newly completed stronger-model study. The original weekly API collection remains closed and unchanged.

## Current status — 25 October 2026

1. **The original weekly run is complete: 104/104 accepted replies.** [Current review and H1–H4 status](reports/review_20261025/REPORT.md). It tests pressure wording, has no education arm and supports descriptive comparisons only.
2. **Use the new [PIVOT_V2.ipynb](notebooks/PIVOT_V2.ipynb) for revised work.** Default review is free. The separate v2 development protocol prepares high-effort GPT-6 Luna, GPT-6.1 Sol, GPT-6 Astra and Claude Sonnet 5.5, three isolated arms, Python-calculated weekly states, and independent-block analysis at fixed 10/20/40 prefixes. The resource intervention is one versus two decision opportunities, not literal human clock time. [Protocol](hypotheses/PIVOT_V2_20261025.md).
3. **Free isolated-assistant checks are complete, with mixed results.** All eight replies passed format checks; neither reconsideration reply changed an order. They are development data, excluded from held-out findings. [Self-check](reports/review_20261025/SELF_CHECK.md).
4. **Cumulative spending is $1.179072025; $3.820927975 remains under the SAME $5 cap.** No new paid requests were made in this review. A four-call technical pilot is optional and bounded at $1.50; the independently replicated stronger-model main study is not funded and is blocked before launch. No result or significance is promised by a pilot.
5. **Presentation files are ready:** [figures and short captions](reports/review_20261025/FIGURE_CAPTIONS.md), including a [16:9 results-slide PDF](reports/review_20261025/figures/04_presentation_results_slide.pdf). Observed chain prefixes and hypothetical power curves are labeled separately.

### New notebook, step by step

1. Open `notebooks/PIVOT_V2.ipynb`, **restart its kernel**, and run all cells with `RUN_API=False`.
2. Review the old results, free self-check, revised design and cost table. No keys are requested and the shared ledger stays unchanged.
3. Only if you want the optional **format-only** pilot, set `RUN_API=True`, run all cells, enter both keys in the hidden fields, and click **Run four format checks**. The notebook shows progress, current-request elapsed time and cumulative spending. A response contains all three technical cases, so this pilot cannot support independent treatment inference.
4. Exact requests, literal replies and receipts are stored in the new fingerprinted `data/pivot_v2_.../attempts/` directory. Rerunning resumes that same run without repurchasing accepted or failed slots. Never extract credentials from another notebook.
5. Do not launch the main sample without a funded fixed maximum and a final frozen protocol. More chains inside one batch do not increase independent N; null/opposite results and failures stay in the evidence.

### V2 implementation and analysis

New source is separate: `src/beergame_study/weekly_pivot_v2.py`, `pivot_transport_v2.py` and `pivot_inference_v2.py`. The old `weekly_pressure*.py` implementation, protocols, original publications, raw responses and ledger entries are preserved. H4 now measures order variance and bullwhip, not the older cost endpoint. The block-analysis module is conditional on validated raw lineage and independent streams; it does not authenticate APIs by itself.

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*pivot*v2.py' -v
.venv/Scripts/python.exe scripts/plot_weekly_review_20261025.py
.venv/Scripts/python.exe scripts/analyze_pivot_v2.py --plan PLAN.json --input block_outcomes.csv --output NEW_ANALYSIS_FOLDER
```

Use one aggregate row per model/block/arm. `PLAN.json` records the fixed ordered block IDs, arms, outcome family and prefixes. Synthetic controls and prompt-development answers are never pooled with held-out data. See [validation](reports/review_20261025/VALIDATION.json) for checks and the two documented historical Windows portability failures. Canonical `game.py` still differs in line-ending bytes from its old frozen hash; independent numerical replay succeeded, but a strict canonical byte audit is not claimed.

## Original weekly-run instructions and preparation record — 21 October 2026

The rest of this page preserves the original preparation description. Its pre-collection balances and “no new calls” statements are historical; use the current status above for today's balance and collection status. The old notebook resumes the closed sample; it is not the entry point for the v2 proposal.

**Start here: [RUN_EXPERIMENT.ipynb](notebooks/RUN_EXPERIMENT.ipynb).**

1. **Python runs the game.** Each model receives current states and returns only 80 orders for the current week. Python computes shipments, inventories, backlog and costs. Future demand is hidden.
2. **Same sample:** four models; 80 fictional testers in 20 four-role chains per model; ten chains per pressure condition; 24 weeks.
3. **104 planned calls:** four full-size format pilots, 96 weekly decisions and four probe batches. At most one retry per transient technical error. No response is repeated to obtain a favorable effect.
4. **Same $5 cumulative budget:** includes the $0.3404859 already recorded in experiment 12. Before new collection, about $4.6595141 remains. All new attempts use that existing ledger.
5. **Interpret carefully:** this compares imagined pressure framing, not measured binding time. Batched choices remain dependent. No student-level significance or structural β is claimed.

## Run it

1. Open the new notebook above and **restart its kernel**.
2. Run all cells with `RUN_API=False` to review the plan and budget without paid calls.
3. Change `RUN_API=True`, keep `PHASE="all"`, then run all cells again.
4. Enter both keys into section 3's hidden fields. The notebook runs pilots and games automatically; no calibration-to-game switch is needed.
5. Read section 4 or [reports/REPORT.md](reports/REPORT.md). The report begins with conclusions and links the Excel workbook and all CSV files.

Accepted weeks are saved before the next request. Rerunning reuses verified accepted responses. An invalid response stops that model, preserving its evidence; other models can continue. A budget stop cannot be bypassed by changing the run label. No missing orders are filled in, and partial games are not treated as full 24-week H2 observations.

## Cost planning

The notebook shows conservative reservations for all 104 first attempts, using every output allowance and an input-byte bound. A separate stressed input-size estimate allows unusually large state/history numbers. These are planning bounds under the recorded prices, not predicted invoices. Failed/unknown-charge attempts and retries also consume the same allowance; the runner stops before a request whose reservation would exceed it. [Offline cost-planning receipt](analysis/software_checks/COST_PLANNING_20261021.json).

## What changed after experiment 12

The whole-cohort method produced incorrect inventories or a missing cohort for three models. Those requests did not hit their token limits. The new method removes model-calculated inventory checkpoints entirely. Each reply must contain every chain and role as required JSON keys, preventing an empty list from appearing complete. The technical pilot uses the actual 80-order response size.

OpenAI reasoning is `none`; Claude thinking is disabled with low effort. Both pressure conditions use identical settings. These are latency/cost controls, not the treatment. Output allowances are 2,048 tokens for pilot/weekly decisions and 4,096 for probes. There is no temperature override. The new settings and interaction protocol form a separate study; do not pool its results with experiment 12.

## Where everything lives

| Folder | Contents |
| --- | --- |
| [hypotheses/](hypotheses/) | H1/H2, prospective protocol, settings and stopping rules |
| [notebooks/](notebooks/) | Run and review notebook |
| [prompts/](prompts/) | Exact messages and schemas saved before each request |
| [data/](data/) | Frozen plan/source snapshot, accepted choices, status and receipts |
| [raw/](raw/) | Provider responses, including failures |
| [analysis/](analysis/) | Python states, chain costs, order patterns, probes and hypothesis tables |
| [reports/](reports/) | Conclusions first, full report and prior report versions |

Common code: `src/beergame_study/weekly_pressure*.py`. The notebook builder is `scripts/create_weekly_pressure_notebook.py`. Experiment 12 owns the shared budget ledger; experiment 13 records a relative pointer and preserves prior charges.

## How to read results

- **H1 proxy:** reduction in orders when matched outstanding replenishment increases from 8 to 32, divided by 24. A smaller response under strong pressure follows the predicted direction. It does not identify structural β or an optimal benchmark.
- **H2:** total holding plus backlog cost across four roles and 24 weeks. Larger pressure-condition cost follows H2. Terminal stock, backlog and outstanding orders are reported separately.
- **Bullwhip:** variance of a role's orders divided by variance of customer demand over the same weeks. A ratio above 1 indicates amplification. Zero demand variance is undefined.
- **Zero or constant orders:** reported honestly, never rejected solely for their pattern. An accounting-consistent choice is not proof of realistic student behavior.
- **Null/opposite effects:** valid descriptive outcomes; no prompt tuning or repeated samples until significance.

The batch exposes every included state to a single model. Instructions to keep fictional students separate do not enforce information isolation or independence. Actual state trajectories are maintained by Python, but a valid JSON reply cannot verify the model's internal reasoning or realism.

## Free software verification

From the project root, run `python -m unittest discover -s tests -p 'test_weekly_pressure*.py' -v` in the project's Python environment. These tests use temporary synthetic responses and mocked HTTP; they make no paid calls. They check state propagation, required choices, shared spending, failures, resume, provenance and notebook/report behavior. Synthetic checks are never included in the study's observations. Live provider behavior still needs the notebook's full-size format pilots.

## Documentation

Generation controls were checked on 21 October 2026 in official [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol) and [Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5) documentation. Structured output definitions use the supported internal-reference subsets described by [OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs) and [Anthropic](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

**Prepared and verified, 21 October 2026:** 30 new tests and 60 previous-study regression checks passed. The notebook's five code cells also completed in a real Jupyter kernel in free review mode, without changing the shared ledger. Mocked tests exercised all 104 planned requests and the notebook's hidden-key input path. No new paid requests were made. [Validation receipt](analysis/software_checks/VALIDATION_20261021.json).

The exact current planning totals are **$3.3746** in first-attempt reservations for ordinary synthetic states and **$4.3282** for the conservative input-size scenario. Including prior spending gives **$3.7151** / **$4.6687**. Both use the full output allowances; actual charges may be lower, while retries consume extra allowance. The cap remains $5.

## Manual pilot MW3_PILOT_A - 25 October 2026

The in-chat pilot completed 24 weeks for ten chains (40 fictional profiles) and all 160 hypothetical probes, with initial and revised choices submitted in separate tool interactions. The unedited [MW3_PILOT_A JSON export](data/manual_v3_3e5479b5ae2ffc96/chat_runs/MW3_PILOT_A_20261025/MW3_PILOT_A.json) is pilot/development data, excluded from held-out main findings. Model: `UNRECORDED`; reasoning setting: `UNRECORDED`, as requested. No API requests were made, and the controller source was not opened or changed.

The compact JSON export is 28,581 bytes; its readback was verified equal to the public `game.export()` result. Per-step public outputs and a supplemental execution log accompany the file. They do not constitute the full chat/tool transcript, which remains required for provenance and review before any eligible analysis. For another authorized manual run, use the active manual notebook and prepared prompts above, retain a separate output folder, and return the JSON together with the full transcript and recorded model/mode.


### 2026-10-25 ? local chat run location

Local Python-guided chat case `MW3_PILOT_B` (arm B, replicate 1001, seed 20261025) imported the unchanged `manual_v3_3e5479b5ae2ffc96` controller by its exact path, `D:\beergame\experiments\13_weekly_state_api_20261021\prompts\manual_v3_3e5479b5ae2ffc96\beergame_controller.py`. It completed 10 chains / 40 fictional students, 24 game weeks and 160 hypothetical choices; the controller requested no revision phase. No API calls were made; requested model/reasoning metadata remains `UNRECORDED`.

The unedited export is [MW3_PILOT_B.json](data/manual_v3_chat_MW3_PILOT_B_20261025/MW3_PILOT_B.json); the public long probe display is saved alongside as [probe_initial_display.json](data/manual_v3_chat_MW3_PILOT_B_20261025/probe_initial_display.json). JSON round-trip equality passed. Reproduce only in a new authorized session with the exact pasted case settings and separate literal model choices after public displays, not automatic order code.

Responses are fictional and dependent. The JSON is an arithmetic record; the current chat/tool transcript is still needed for provenance and researcher acceptance. This note records the run location, not scientific acceptance or a treatment comparison.

## Manual chat development export - 25 October 2026

The [MW3_PILOT_C export](data/manual_chat_20261025_MW3_PILOT_C_source_exposure/MW3_PILOT_C.json) is complete for 10 four-role chains over 24 weeks, with 160 probe decisions. [Provenance and checks](data/manual_chat_20261025_MW3_PILOT_C_source_exposure/PROVENANCE.json) record the unmodified export's SHA-256, 25 events, and a matching supplied-controller hash. The live session also confirmed exact saved-byte equality with its `game.export()` serialization. These are bookkeeping checks; no independent numerical replay or transcript/model authentication was performed. Model and reasoning setting remain `UNRECORDED`.

The assistant displayed controller source before noticing the prohibition, disclosed the deviation, and continued. This session requires researcher review and must not be treated as a source-blind run. The authentic chat/tool history remains in the current conversation; no separate transcript file has been exported. A [public probe display](data/manual_chat_20261025_MW3_PILOT_C_source_exposure/probe_display.json) was retained because terminal output was cut off; all 160 rows were then read with PowerShell `Format-Table` before submitting a literal decision dictionary. Delegated support was limited to artifact/provenance housekeeping, with no ordering assistance.

Run instructions remain in the [prepared manual helper and prompts](prompts/WEBSITE_START_HERE.md) and [manual notebook](notebooks/MANUAL_WEBSITE.ipynb); this record documents the completed chat and does not request a new collection.
