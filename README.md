# Beer Game experiments

## Current: live agent collection and 50-chain manual batches

**[Open the live progress notebook](experiments/13_weekly_state_api_20261021/notebooks/AGENT_PROGRESS.ipynb). Run all cells; tick Auto-refresh (10 s) if a checkbox appears. Without ipywidgets, HTML auto-refresh starts automatically.** It shows saved pages, completed weeks and H1-H4 status for GPT-6 Astra, GPT-6.1 Sol and GPT-6 Luna. It monitors collection; it does not launch agents or call an API.

For your own website collection: [four prompts + helper](experiments/13_weekly_state_api_20261021/prompts/LARGE_SAMPLE_V5/README.md), [manual analysis notebook](experiments/13_weekly_state_api_20261021/notebooks/LARGE_SAMPLE_V5.ipynb), [manual report / sample-size plan](experiments/13_weekly_state_api_20261021/reports/large_sample_v5/REPORT.md). V5 uses 50 chains per condition, three conditions and 24 weeks per fresh context. Agent and website samples remain separate. One context is one replication; the 50 chains are dependent. Current agent collection is ongoing, not an established significance result.

[Current agent report and extracted results](experiments/13_weekly_state_api_20261021/reports/agent_collection_v5/REPORT.md). The user has replaced the ten-run target with a 90-minute maximum: collection stops at 11:07 p.m. Eastern on 25 October; report deadline 11:27 p.m. Three-round review/plots after three complete non-excluded contexts per model, followed by a final update within that cap. The live notebook shows completion and review status.

**[Current slide figures and short captions](experiments/13_weekly_state_api_20261021/reports/agent_collection_v5/slides_current/README.md)**: repeated-context results and H1-H4 versus chain count. Use these current figures for slides; early first-run figures are a historical snapshot.

The navigation below describes preserved earlier stages.


**Start with [the experiment index](experiments/README.md).** Every experiment has its own hypotheses, prompts, data, analysis, reports and notebooks.

| What you want | Open |
| --- | --- |
| Received GPT-6 Astra / ultra manual pilots: replay, findings and plots | [Pilot report](experiments/13_weekly_state_api_20261021/reports/manual_pilot_review_20261025/REPORT.md) |
| Latest four-model findings, H1–H4 audit and presentation figures | [25 October review](experiments/13_weekly_state_api_20261021/reports/review_20261025/REPORT.md) |
| Active manual website route: upload one helper, paste prompts, return JSON + transcript; no API calls | [Website steps and prompts](experiments/13_weekly_state_api_20261021/reports/review_20261025/WEBSITE_STEPS.md) |
| Import and analyze the new website responses; independent 10/20/40-block sweeps | [Manual notebook](experiments/13_weekly_state_api_20261021/notebooks/MANUAL_WEBSITE.ipynb) |
| Experiment 13 guide, current workflow and preserved earlier stages | [Experiment 13](experiments/13_weekly_state_api_20261021/README.md) |
| Completed 104-response API run, preserved original publication | [Original completed report](experiments/13_weekly_state_api_20261021/reports/history/b34972b65bf5/REPORT.md) |
| Latest completed Astra education/deadline findings | [Experiment 11 report](experiments/11_education_deadline/reports/website_astra_extra_high/REPORT.md) |
| Earlier completed 10s/180s deadline study | [Experiment 10 report](experiments/10_deadline_cohort/reports/current/REPORT.md) |
| All previous studies, their models and results | [Experiment index](experiments/README.md) |
| Verify old results or understand the reorganization | [Maintenance and compatibility guide](maintenance/README.md) |

The completed [experiment 12](experiments/12_pressure_framing_api_20261020/README.md) accepted only Sol’s main response, with zero H1/H2 contrasts. Experiment 13 addresses the other models’ accounting failures by calculating state in Python. Both studies share the original cumulative $5 budget.

**25 October status:** experiment 13's original run is complete at 104/104 responses. Combined spending is $1.179072025, leaving $3.820927975. It was a descriptive pressure-framing study without education arms or binding time. The separately versioned v2 proposal adds causal education, actual restricted reconsideration opportunities, fixed high effort and independent-block analysis; it is a development resource analogue, not verified human deadline evidence. Its free isolated-assistant check had mixed effects. New paid collection is stopped; the larger stronger-model main sample does not fit the existing cap. Historical samples and publications remain unchanged.

**User's latest choice:** keep the $5 maximum and use manual website prompts. The new Python-guided manual workflow handles ten chains per chat and makes zero repository API calls. Use the active website links above; three pilot chats check feasibility before main collection. Do not treat chat headcounts as independent samples or driver JSON as proof of model decision provenance without reviewing the tool transcript.

## Folder structure

```text
experiments/
  01_... through 12_.../     preserved previous studies
  13_weekly_state_api_20261021/
    hypotheses/             hypotheses, protocol and configuration
    prompts/                exact messages and schemas
    data/                   original responses, settings and receipts
    analysis/               computed tables and checks
    reports/                conclusions, figures and findings
    notebooks/              notebook to run or review this experiment
src/                        common game and scientific implementations
scripts/                    common run, analysis and maintenance commands
tests/                      software checks
maintenance/                migration map, older navigation and shared inputs
```

Historical run bundles retain their internal prompt/source snapshots so their provenance remains interpretable. Each experiment's section guides point directly to those files. Original published reports and notebooks keep their exact bytes; the new `review_saved_results.ipynb` in each historical experiment reads the organized paths safely.

## Saved-data verification

```bash
python3 scripts/reorganize_experiments.py --verify
python3 scripts/legacy_workspace.py --recover-historical-bytes --verify-astra
```

The first command checks all 39,589 original tracked files against the bytes present before reorganization. The second makes a temporary old-layout copy and runs the unchanged historical verifier. It makes no API calls. Do not run the original paid entry points directly from the organized root: their historical spending guards expect the old data tree. Use the separate new experiment for new work.

**20 October 2026 reorganization:** moved 39,470 tracked files into 11 experiment folders, preserved three original navigation files, and retained 116 shared/root files. All 701,413,272 preexisting tracked bytes were verified unchanged. The [complete move map](maintenance/reorganization_20261020/FILE_MAP.json) resolves every old path. Seven ignored cache files were separately quarantined.

The checkout already had an older integrity problem: 14,435 of 15,013 historical baseline files had LF instead of the CRLF expected by saved hashes. All these differences were proved to be line-ending-only before migration. Canonical files keep their existing bytes. The compatibility helper can recover a temporary copy only when its candidate bytes match the original saved hash; every derivation is recorded. [Original checks](maintenance/reorganization_20261020/beer_handoff_byte_scan_20261020.json).

**Checks completed:** six organization tests, fourteen historical portability tests, all eleven review notebooks, and the complete 108,000-state Astra replay passed. Five older publication-generation tests need a newer pandas version than the installed Anaconda environment; existing publication bytes were verified. [Validation receipt](maintenance/reorganization_20261020/VALIDATION_STATUS.json). New `.gitattributes` disables automatic line-ending conversion on future Git checkouts.

The model-generated identities are fictional and may be dependent within one response. Fictional deadline prompts do not establish measured or enforced human time pressure. Read each experiment's protocol and limitations before interpreting its results.

**25 October preservation recheck:** the canonical migration verifier currently fails for 39 retained root/shared files. Of 39,589 mapped files, 39,550 match exactly, none are missing, and all 39 differences were hash-proved to be line-ending-only; no unexplained content difference was found. Canonical files were not repaired. This is separate from the older 14,435-file historical issue. [Current receipt](experiments/13_weekly_state_api_20261021/analysis/review_20261025/MIGRATION_RECHECK.json).
