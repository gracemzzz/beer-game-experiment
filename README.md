# Beer Game experiments

**Start with [the experiment index](experiments/README.md).** Every experiment has its own hypotheses, prompts, data, analysis, reports and notebooks.

| What you want | Open |
| --- | --- |
| New four-model API experiment: 80 fictional testers, 20 chains, 24 decision weeks per model | [Experiment 12](experiments/12_pressure_framing_api_20261020/README.md) |
| Run the new study: four pilot calls + four main calls, shared $5 cap | [Run notebook](experiments/12_pressure_framing_api_20261020/notebooks/RUN_EXPERIMENT.ipynb) |
| Latest completed Astra education/deadline findings | [Experiment 11 report](experiments/11_education_deadline/reports/website_astra_extra_high/REPORT.md) |
| Earlier completed 10s/180s deadline study | [Experiment 10 report](experiments/10_deadline_cohort/reports/current/REPORT.md) |
| All previous studies, their models and results | [Experiment index](experiments/README.md) |
| Verify old results or understand the reorganization | [Maintenance and compatibility guide](maintenance/README.md) |

## Folder structure

```text
experiments/
  01_... through 11_.../     preserved historical studies
  12_pressure_framing_api_20261020/
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
