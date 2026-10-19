# Beer Game study

The current deadline-framing study is **complete: 20/20 responses, 500 fictional identities and 40,000 submitted weekly orders**. No more prompts or API calls are needed.

## Current experiment: start here

| What you need | File |
| --- | --- |
| Quick README | [Final-package README](reports/deadline_cohort_2800524c9b2e0729/final/README.md) |
| Report and all six plots | [Final report](reports/deadline_cohort_2800524c9b2e0729/final/REPORT.md) |
| All 20 exact prompts | [Exact prompts](reports/deadline_cohort_2800524c9b2e0729/final/EXACT_PROMPTS.md) |
| Extracted results | [Excel](reports/deadline_cohort_2800524c9b2e0729/final/results/RESULTS.xlsx), [weekly-order CSV](reports/deadline_cohort_2800524c9b2e0729/final/results/weekly_orders.csv), [field guide](reports/deadline_cohort_2800524c9b2e0729/final/results/README.md) |
| Everything in one file | [Download ZIP](reports/deadline_cohort_2800524c9b2e0729/Beer_Game_Deadline_20261018.zip) |

The package is under `reports/deadline_cohort_2800524c9b2e0729/final/`. Plots are in its `plots/` folder as PNG/PDF; tables are in `results/`.

**Main finding:** H1 follows its predicted direction in both rounds; H2 points the other way; H3 changes direction between rounds and is opposite overall. These are descriptive model-generated scenarios under user-reported GPT-6 / Pro. Fictional deadlines do not impose actual model thinking time, and the personas were not validated against real students.

## Open or reproduce

Open [notebook 07](notebooks/07_deadline_cohort_rerun.ipynb) in Jupyter with this project's `.venv`. Run sections 1-4, then 7-8 for all plots and 125 interactive team charts. Sections 5-6 were for collection and are no longer needed. [Dependencies](requirements.txt).

From the project root, these commands use only saved data:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/export_deadline_deliverables.py --run data/runs/deadline_cohort_2800524c9b2e0729 --analysis daa53a7e838a
.\.venv\Scripts\python.exe -X utf8 scripts/audit_deadline_run.py --run data/runs/deadline_cohort_2800524c9b2e0729
.\.venv\Scripts\python.exe -X utf8 scripts/check_deadline_completion.py --run data/runs/deadline_cohort_2800524c9b2e0729 --before reports/software_checks/deadline_generation2_before_20261018.json
.\.venv\Scripts\python.exe -X utf8 scripts/check_deadline_notebook.py --run data/runs/deadline_cohort_2800524c9b2e0729
```

The exporter reproduces the same package/ZIP from unchanged source exports and refuses differing overwrites. Rebuilding a canonical workbook/PDF can change its file bytes; if a new publication copy is needed afterward, add `--label final_v2`. Canonical report regeneration leaves `final/` untouched; it may reset the run's small `REPORT.md` landing page, whose package/guide links should then be restored. Any future scientific change needs a new run fingerprint.

## Repository map

| Folder | Purpose |
| --- | --- |
| `reports/` | Current package, earlier studies, checks and logs; [report index](reports/README.md) |
| `data/` | Preserved raw responses, plans, prompts and scientific source snapshots |
| `notebooks/` | Current notebook 07 and separately usable earlier workflows |
| `src/`, `scripts/`, `tests/` | Simulation, import/export tools and software checks |
| `docs/`, `config/`, `configs/` | Protocols, research notes and experiment settings |
| `archive/` | Earlier source versions |

Maintenance rules are in [AGENTS.md](AGENTS.md). Earlier experiments and source evidence remain in their existing locations so notebooks, audits and historical links continue to work.

## Change record

**18 October 2026 - final package and navigation cleanup.** Added the four requested deliverables and a portable ZIP. Shortened this README and the report index; their complete earlier texts are [archived](reports/archive/repository_cleanup_20261018/README.md). Added a reproducible offline exporter. Checked 20 prompt hashes, all 40,000 extracted orders against original replies, six unchanged figure pairs, ten workbook sheets, package links, ZIP contents and preservation of prior evidence. No scientific outcomes, prompts, accepted responses or spending changed. See [package checks](reports/software_checks/deadline_cohort_2800524c9b2e0729_package.json) and [cleanup checks](reports/software_checks/deadline_repository_cleanup_20261018.json).
