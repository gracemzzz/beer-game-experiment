# File organization and preserved history

All 26 pre-existing root entries were moved, not deleted, into `archive/pre_token_budget_20261004/`. This includes the 207 MB results directory, reports, source code, all old notebooks, tests, requirements and backups. The previous files retain their names and relative arrangement. `archive/migration_20261004.json` records every top-level move and file hashes.

Examples:

- Old `START_HERE_bounded_rerun.ipynb` → `archive/pre_token_budget_20261004/START_HERE_bounded_rerun.ipynb`
- Old `results/bounded_54nano_api_465dbda1ee6129f1/` → `archive/pre_token_budget_20261004/results/bounded_54nano_api_465dbda1ee6129f1/`
- Previous latest report → `archive/pre_token_budget_20261004/reports/Beer_Game_Latest_Pilot_Review.docx`

Absolute links in historical reports/conversations still point to the former location; use this mapping. Those reports were not rewritten to imply they belong to the new study. To inspect an archived notebook, open it from its archived directory. Do not rerun it as the new protocol.

The supplied Desktop reflection is unchanged. A source copy is under `data/source/`. Original token-study runs are under `data/runs/`. The 5 October budget follow-up is isolated under `data/development/`, including model screening, fresh calibration/games and a calibration-metadata recheck. New notebooks are under `notebooks/`; the original implementation remains under `src/beergame_study/`, while isolated follow-up runners and reproducible analysis scripts are under `scripts/`.

Open `notebooks/02_budget_model_comparison.ipynb` for the latest follow-up. Its default is review only. Human-readable reports live under `reports/`, with `reports/LATEST_REPORT.txt` pointing to the latest Word report and workbook. The previous audited nano report remains in `reports/pilot_02_game_api_8236a9c840b29d36/`. Root contains the entry README and requirements, not successive numbered code copies.
