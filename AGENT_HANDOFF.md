# Beer Game agent handoff

Read [AGENTS.md](AGENTS.md), [README.md](README.md) and [the experiment index](experiments/README.md).

The repository was reorganized on 20 October 2026 at the user's request. Each study now owns its hypotheses, prompts, raw data, analysis, reports and notebooks under `experiments/`. Common implementation remains under `src/`, `scripts/` and `tests/`. Current work is [experiment 13](experiments/13_weekly_state_api_20261021/README.md); all twelve preceding experiment folders remain distinct.

The original cross-computer handoff is preserved exactly at [maintenance/reorganization_20261020/original_navigation/AGENT_HANDOFF.md](maintenance/reorganization_20261020/original_navigation/AGENT_HANDOFF.md). Its old paths are historical; resolve them using [FILE_MAP.json](maintenance/reorganization_20261020/FILE_MAP.json). The prior transfer ZIP is not present in this checkout. Do not imply that a Git clone preserved historical CRLF bytes.

## Review the latest completed collection

Open [the Astra report](experiments/11_education_deadline/reports/website_astra_extra_high/REPORT.md) or [its experiment guide](experiments/11_education_deadline/README.md). Six supplied replies are accepted; the prepared parent remains unchanged at 0/6. Actual displayed settings were user-reported GPT-6 Astra / extra high effort, not independently provider-verified. These are 500 fictional identities, 60,000 weekly orders and 3,000 probe pairs; the independent replay checks 108,000 states. Do not add responses to this closed sample.

## Verify after relocation

```bash
python3 scripts/reorganize_experiments.py --verify
python3 scripts/legacy_workspace.py --recover-historical-bytes --verify-astra
```

The first command verifies every original tracked file at its new location. The second creates an isolated old-layout copy, records any hash-confirmed line-ending reconstruction, and runs the original portable verifier with full replay. It does not patch scientific functions, change frozen source logic, reopen historical external Windows paths, or make paid calls. The temporary copy can also run the original offline tests.

Before this reorganization, 14,435 of 15,013 baseline files already differed only in LF/CRLF. Canonical files retain the current pre-migration bytes. Exact historical byte recovery is a separate, explicitly recorded operation in the copy. See [maintenance/README.md](maintenance/README.md) and the preserved pre-migration checks.

Use the analysis constraints and recorded source environment under [maintenance/handoff_20261020/](maintenance/handoff_20261020/) if recreating the old environment. The original source environment was Python 3.12.8; rendering image/PDF packages on another platform can change bytes, so verify saved packages rather than overwrite them.

## New experiments

Use a new experiment folder and prospective settings/protocol. Keep actual model names, treatment, sample size, scoring horizon, independent generation unit, stopping rule and hard cumulative API cap explicit. The user approved weekly batches with Python-maintained state on 21 October 2026, replacing the earlier one-cohort-response requirement. The 80 generated identities still are not independent model replications. Preserve all unsuccessful attempts and null/opposite effects. Follow its README and notebook rather than launching historical paid entry points, whose spending guard assumes the old directory tree.

Experiment 12 update, 21 October 2026: the user collected four live pilots. GPT-5.6 Luna and Sol passed; GPT-6 Luna failed physical inventory readbacks and Claude Haiku exhausted 8,192 tokens entirely on reasoning. The original run remains frozen at two accepted pilots, no main cohorts, and $0.0716918 estimated charges. Follow [the recovery amendment](experiments/12_pressure_framing_api_20261020/hypotheses/RECOVERY_20261021.md) and the updated notebook for the separate bounded recovery. It reuses successful pilots by hash, schedules two revised pilot generations plus four main generations, and shares the original cumulative $5 ledger. Do not reset original statuses, overwrite failures, or run the original runner to bypass recovery provenance. Terminal keys remain unavailable; new live recovery must be initiated through the notebook's hidden fields.

Latest experiment 12 update: the first recovery completed with GPT-6 accepted and Claude invalid on physical inventory arithmetic. Claude finished normally at 3,519 output tokens, so this is not another output-cap failure. There are now three accepted GPT pilots, no main cohorts, and $0.07590755 cumulative estimated charges. The separate [Claude follow-up](experiments/12_pressure_framing_api_20261020/hypotheses/CLAUDE_FOLLOWUP_20261021.md) preserves the original four-model objective: three inherited pilots, one fixed revised Claude pilot, then four main calls only if all pilots pass. Use the latest notebook, which detects the stage and updates reports automatically; do not rerun frozen earlier runners to change their saved statuses. New live follow-up results remain uncollected until the user supplies keys in the notebook.

## Current handoff — weekly redesign approved 21 October 2026

Experiment 12's final follow-up completed: all four small pilots passed, but GPT-6 Luna had 40/60 incorrect inventory checkpoint vectors, GPT-5.6 Luna had 56/60 incorrect vectors, and Claude returned an empty chain list. None hit its output cap. GPT-5.6 Sol passed: all 1,920 orders were 4; H1 pipeline sensitivity 0.833333 and mean chain cost 551.60 in both conditions, with all ten pairs tied. Preserve all responses and previous publications. No failed result is promoted or repaired. The [report](experiments/12_pressure_framing_api_20261020/reports/REPORT.md) and [guide](experiments/12_pressure_framing_api_20261020/README.md) supersede earlier pending-stage descriptions above.

The user expressly approved **experiment 13: 24 weekly batches per model, Python-calculated states, same cumulative $5**. Four full-size 80-order pilots + 96 main weekly batches + four 320-choice H1 probe batches = 104 planned requests before technical retries. Each passing model proceeds independently. The same four requested models remain; OpenAI reasoning none and Claude disabled thinking/low effort are documented settings, identical across conditions. Weekly/pilot allowance 2,048, probe 4,096. Prompted pressure remains imagined, not binding; no independent-chain p-values or structural beta claims. Future demand remains local.

Use [the new notebook](experiments/13_weekly_state_api_20261021/notebooks/RUN_EXPERIMENT.ipynb). Free review is default; user sets RUN_API=True and enters both provider keys in hidden fields. No API keys are available in the terminal. Do not extract keys from a running notebook. **Experiment 12's existing data/api_budget.json and runner lock cover both studies.** Prior charge total is $0.3404859; about $4.6595141 remains before weekly collection. Do not reset the ledger or run the old runner to evade failed slots. Prospective source fingerprints and exact dynamically generated request payloads preserve scientific provenance.

Experiment 13 preparation verified: frozen run `weekly_api_c64d75aa3a03356f`; 30 new tests + 60 previous-study regression checks passed, including all 104 mocked requests and resume without rebilling. The five notebook code cells ran in a real Jupyter kernel in review mode with unchanged ledger. Eight pilot/first-week request messages are frozen without paid submission. No new live API calls were made. See [validation](experiments/13_weekly_state_api_20261021/analysis/software_checks/VALIDATION_20261021.json) and [cost planning](experiments/13_weekly_state_api_20261021/analysis/software_checks/COST_PLANNING_20261021.json). Ordinary synthetic first-attempt reservations total $3.3746; conservative input-size reservations $4.3282, or $4.6687 including prior charges. Extra retries can still exhaust the cap.
