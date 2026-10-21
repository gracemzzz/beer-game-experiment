# Beer Game agent handoff

Read [AGENTS.md](AGENTS.md), [README.md](README.md) and [the experiment index](experiments/README.md).

The repository was reorganized on 20 October 2026 at the user's request. Each study now owns its hypotheses, prompts, raw data, analysis, reports and notebooks under `experiments/`. Common implementation remains under `src/`, `scripts/` and `tests/`. New work is [experiment 12](experiments/12_pressure_framing_api_20261020/README.md); the eleven historical folders remain distinct.

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

Use a new experiment folder and prospective settings/protocol. Keep actual model names, treatment, sample size, scoring horizon, independent generation unit, stopping rule and hard cumulative API cap explicit. The new experiment requests one cohort response per model; it cannot treat the 80 generated identities as 80 independent model replications. Preserve all unsuccessful attempts and null/opposite effects. Follow its README and notebook rather than launching historical paid entry points, whose spending guard assumes the old directory tree.

Experiment 12 update, 21 October 2026: the user collected four live pilots. GPT-5.6 Luna and Sol passed; GPT-6 Luna failed physical inventory readbacks and Claude Haiku exhausted 8,192 tokens entirely on reasoning. The original run remains frozen at two accepted pilots, no main cohorts, and $0.0716918 estimated charges. Follow [the recovery amendment](experiments/12_pressure_framing_api_20261020/hypotheses/RECOVERY_20261021.md) and the updated notebook for the separate bounded recovery. It reuses successful pilots by hash, schedules two revised pilot generations plus four main generations, and shares the original cumulative $5 ledger. Do not reset original statuses, overwrite failures, or run the original runner to bypass recovery provenance. Terminal keys remain unavailable; new live recovery must be initiated through the notebook's hidden fields.
