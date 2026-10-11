# File organization and preserved history

All 26 pre-existing root entries were moved, not deleted, into `archive/pre_token_budget_20261004/`. This includes the 207 MB results directory, reports, source code, all old notebooks, tests, requirements and backups. The previous files retain their names and relative arrangement. `archive/migration_20261004.json` records every top-level move and file hashes.

Examples:

- Old `START_HERE_bounded_rerun.ipynb` → `archive/pre_token_budget_20261004/START_HERE_bounded_rerun.ipynb`
- Old `results/bounded_54nano_api_465dbda1ee6129f1/` → `archive/pre_token_budget_20261004/results/bounded_54nano_api_465dbda1ee6129f1/`
- Previous latest report → `archive/pre_token_budget_20261004/reports/Beer_Game_Latest_Pilot_Review.docx`

Absolute links in historical reports/conversations still point to the former location; use this mapping. Those reports were not rewritten to imply they belong to the new study. To inspect an archived notebook, open it from its archived directory. Do not rerun it as the new protocol.

The supplied Desktop reflection is unchanged. A source copy is under `data/source/`. Original token-study runs are under `data/runs/`. The 5 October budget follow-up is isolated under `data/development/`, including model screening, fresh calibration/games and a calibration-metadata recheck. New notebooks are under `notebooks/`; the original implementation remains under `src/beergame_study/`, while isolated follow-up runners and reproducible analysis scripts are under `scripts/`.

Open `notebooks/03_student_reasoning_study.ipynb` for the active student study. Its paid-run switches default to false. Human-readable reports live under `reports/`; raw experiment evidence lives under `data/`. The frozen experiment also retains its original generated run snapshots for provenance.

As of 11 October 2026:

- `reports/student_pilot_20261011/`: current Word report, Markdown report, `DETAILS.xlsx`, analysis tables, figures and source/provenance snapshots.
- `reports/README.md`: report index, with current and historical links.
- `reports/archive/20261005/`: original nano pilot and Luna follow-up report folders, preserved without content changes.
- `reports/archive/analysis_versions/`: superseded full-hypothesis analysis versions, including the two versions originally misplaced in `data/`.
- `reports/logs/student_pilot_20261011/`: historical background-process logs and PID records. New launches use timestamped log folders.
- `reports/software_checks/`: validation logs and audit records.
- `reports/LATEST_REPORT.txt`: paths to the current Word, Markdown and Excel files. `LATEST_STUDENT_HYPOTHESIS_REPORT.json` separately identifies the source run and published report folder.

`reports/archive/organization_20261011.json` records the 77 byte-identical moved files. Active notebook, report-builder and documentation links were updated; immutable historical artifacts can still mention their original paths. Root contains the entry README and requirements.
