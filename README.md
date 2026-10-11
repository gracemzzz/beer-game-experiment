# Beer Game: token-budget experiment

**Start with [the budget follow-up notebook](notebooks/02_budget_model_comparison.ipynb).** It opens in review-only mode and shows the model comparison, calibration, spending and follow-up games. The [original notebook](notebooks/01_token_budget_beer_game.ipynb) and its completed nano pilot are preserved separately.

1. Notebook 02 uses `RUN_API=False`: running its cells reads saved results and makes no paid calls. Its optional resume action reads completed stages without repurchasing them.
2. The fixed comparison tested nano, mini and Luna with original/clarified physical rules. Luna with clarified rules was selected on feasibility and price, never on H1/H2 significance.
3. The fresh calibration uses 32/240/480 memo tokens. The planned follow-up has two chains per condition, four role agents per chain, and 1,168 game API calls. This is a feasibility pilot, not a powered H1/H2 test.
4. Limits: model screen $0.45, fresh calibration $0.12, games $0.90, and calibration-metadata recheck $0.03. Including the four earlier current-study runs ($0.3720), these ceilings stay below the approximately $3 allowance. This ledger is not an account balance and excludes older archived experiments.

The enforced constraint is the **API output cap on a decision memo**, followed by the same 192-token final-answer allowance. Both conditions within a study use the same selected model with reasoning disabled. It measures constrained visible preparation, not human seconds or all internal computation. The free checks and live calibration evaluate the implementation and manipulation separately. `reports/LATEST_REPORT.txt` points to the current human-readable report and detailed workbook.

## Folders

| Folder | Purpose |
| --- | --- |
| `notebooks/` | User-facing notebook |
| `src/beergame_study/` | Config, physical game, prompts, API handling, runner, estimation and reports |
| `configs/` | Reusable example settings |
| `data/source/` | Unmodified copy of the supplied reflection |
| `data/runs/` | New run manifests, request checkpoints, data, reports and plots |
| `data/development/` | Budgeted model comparison, fresh follow-up calibration/games and repair-check evidence |
| `scripts/` | Reproducible audits, report builders and the isolated budget follow-up implementation |
| `reports/budget_followup_20261005/` | Conclusions-first follow-up Word report, workbook and independent game audit |
| `reports/pilot_02_game_api_8236a9c840b29d36/` | Audited report for the completed original nano pilot |
| `reports/software_checks/` | Executed free notebook checks and validation summary |
| `tests/` | Offline and mocked-API checks; never live calls |
| `docs/` | Protocol, sources and migration notes |
| `archive/pre_token_budget_20261004/` | All earlier notebooks, code, reports, results and backups, preserved together |

Each completed run writes `REPORT.docx`, `REPORT.md`, `DETAILS.xlsx`, raw request JSON and CSVs. Game runs additionally write beta diagnostics, H1/H2 test status, group cost tables, order trajectories and bullwhip plots. Conclusions appear first in reports. New and old protocols are never pooled.

## Setup and testing

Install `requirements.txt` into the Python environment used by Jupyter. Run tests from this directory:

```sh
python -m pip install -r requirements.txt
PYTHONPATH=src python -m unittest discover -s tests -v
```

Notebook 01 retains its original settings for historical reproduction. Notebook 02 defaults to review only. If explicitly resuming an incomplete follow-up, set `RUN_API=True` and use its hidden key prompt. The campaign and stage limits are frozen in saved manifests; the notebook does not silently change a model, increase the sample or raise the spending allowance.

Read [the protocol](docs/PROTOCOL.md) before research use, especially the calibration deviations, finite continuation, failure handling and limitations on inference. Prior report paths have moved; [migration notes](docs/FILE_ORGANIZATION.md) explain where to find them.

Startup quiz fix: the notebook now uses `token-game-pilot-02`. The previous attempt failed before any game orders. All roles now complete named rules questions with at most one recheck before play begins. The passed token calibration is retained with an explicit compatibility audit.
