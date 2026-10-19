# Beer Game study

**Open the current report here: [reports/CURRENT_BEER_GAME/REPORT.md](reports/CURRENT_BEER_GAME/REPORT.md).**

| What you need | File |
| --- | --- |
| README | [Current study overview](reports/CURRENT_BEER_GAME/README.md) |
| Report and six plots | [H1-H4 report](reports/CURRENT_BEER_GAME/REPORT.md) |
| Exact prompts | [All 20 prompts](reports/CURRENT_BEER_GAME/EXACT_PROMPTS.md) |
| Extracted results | [Excel](reports/CURRENT_BEER_GAME/results/RESULTS.xlsx), [40,000 orders CSV](reports/CURRENT_BEER_GAME/results/weekly_orders.csv), [column guide](reports/CURRENT_BEER_GAME/results/README.md) |
| Complete download | [Beer_Game_H1_H4.zip](reports/CURRENT_BEER_GAME/Beer_Game_H1_H4.zip) |

## What the data can tell you

The existing collection is complete: 20 replies and 500 fictional identities. For your four hypotheses, H1 has exploratory proxy evidence; H2 costs point opposite the prediction; H3/H4 were not tested because education/control lecture groups are absent. Binding decision time was not verified. **A new experiment is required to test all four as written.** [Hypotheses and proposed design](docs/HYPOTHESES_H1_H4.md).

The framework was supplied after collection. No original decisions, prompts or scoring rules were changed. These are model-generated scenarios, not independent human observations.

## Read or verify

Open [notebook 07](notebooks/07_deadline_cohort_rerun.ipynb), run sections 1-4, then 7-8. It now shows the four-hypothesis assessment and 125 interactive team charts.

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_current_report.py
.\.venv\Scripts\python.exe -X utf8 scripts/audit_deadline_run.py --run data/runs/deadline_cohort_2800524c9b2e0729
.\.venv\Scripts\python.exe -X utf8 scripts/check_deadline_notebook.py --run data/runs/deadline_cohort_2800524c9b2e0729
.\.venv\Scripts\python.exe -X utf8 scripts/check_current_report.py
```

All commands above use saved data only. The publisher verifies an existing package without replacing it; further publication changes must archive the superseded package first. [Guide for another user and their agent](docs/README_FOR_NEW_USERS.md).

## Folder layout

- `reports/CURRENT_BEER_GAME/`: the one current report, plots, prompts and results.
- `reports/archive/`: earlier reports, superseded publications and historical notes; [archive index](reports/archive/README.md).
- `reports/logs/` and `reports/software_checks/`: operational evidence.
- `data/`: preserved raw replies, plans and scientific source snapshots.
- `notebooks/`, `src/`, `scripts/`, `tests/`, `docs/`, `config/`, `configs/`: maintained project files. [Maintenance instructions](AGENTS.md).

**18 October 2026 update:** replaced the three-outcome presentation with your exact H1-H4; marked education effects missing; added an explicit rerun design; consolidated active output into one named folder; archived 16 older study/report folders and the superseded ZIP. Notebook and CLI navigation use the corrected report. Raw evidence and frozen scientific sources are unchanged. [Verification](reports/software_checks/hypothesis_alignment_20261018.json).

**18 October 2026 Git maintenance:** resolved a merge conflict involving a temporary Word lock file by retaining the incoming file; added an ignore rule for newly created Office lock files (`~$*`). Existing tracked lock files remain tracked. The staged notebook metadata change is preserved. Verify with `git diff --cached --check` and `git ls-files -u` (no output means no unresolved conflicts), then finish the pending merge with `git commit --no-edit`. This maintenance does not alter study data, scientific sources or report contents.
