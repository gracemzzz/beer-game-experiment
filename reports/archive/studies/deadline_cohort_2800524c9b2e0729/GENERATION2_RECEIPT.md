# Final ten responses accepted

18 October 2026. **20/20 complete.** All ten planned generation-2 replies passed on their first import, unchanged. They add 20,000 weekly orders and 1,000 probe pairs. No decisions or rule answers were edited, and no API calls were made.

[Read the short final findings](FINDINGS.md) or [open the full report and plots](analysis/daa53a7e838a/REPORT.md). [Detailed checks and attachment hashes](GENERATION2_CHECK.json).

## Original responses

Each link opens the exact received text. SHA-256 values, attachment paths and settings are retained in the check file.

| Task | Raw response | Orders | Probe pairs | Status |
| --- | --- | ---: | ---: | --- |
| `b0001_g02_ample` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0001_g02_ample_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0001_g02_brief` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0001_g02_brief_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0002_g02_brief` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0002_g02_brief_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0002_g02_ample` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0002_g02_ample_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0003_g02_ample` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0003_g02_ample_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0003_g02_brief` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0003_g02_brief_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0004_g02_brief` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0004_g02_brief_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0004_g02_ample` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0004_g02_ample_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0005_g02_ample` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0005_g02_ample_001.txt) | 2,000 | 100 | Accepted unchanged |
| `b0005_g02_brief` | [Original text](../../data/runs/deadline_cohort_2800524c9b2e0729/attempts/b0005_g02_brief_001.txt) | 2,000 | 100 | Accepted unchanged |

## Checks and provenance

The completed study contains 500 fictional identities, 125 teams, 2,000 role trajectories, 40,000 model-submitted orders and 2,000 probe pairs. Replay produces 72,000 role-week states, including practice and automatic continuation. The 250 matched team/generation pairs are not 250 independent human teams.

Direct checks passed for H1/H3, the holding/backlog cost identity, every deadline and repeat order comparison, all 250 repeat-metric rows, ten workbook sheets and six PNG/PDF figure pairs. All eight notebook cells passed with API constructors blocked; 125 team charts are available. The main outcome and repeat-variation plots were visually inspected. The 63 files present before this import, every first-generation comparison and both earlier-study report selections remain unchanged. The completed raw run has 93 files.

The ten replies were submitted together after the user requested a multi-tab workflow. Actual execution order, concurrency, fresh-chat use and complete prompt submission were not independently observed. Model/mode labels follow the established user-reported GPT-6 / Pro selection, not provider-verified snapshots. Scientific prompts, profiles, rules, scoring and the sample plan are unchanged. No new human data or measured token/time intervention was introduced.

All planned slots are now filled. No further sampling or outcome-based replacement is part of this completed collection. Earlier partial reports and the separate assistant pilot remain preserved.

## Reproduce

From the project folder, using its Python environment:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/audit_deadline_run.py --run data/runs/deadline_cohort_2800524c9b2e0729
.\.venv\Scripts\python.exe -X utf8 scripts/check_deadline_notebook.py --run data/runs/deadline_cohort_2800524c9b2e0729
.\.venv\Scripts\python.exe -X utf8 scripts/check_deadline_completion.py --run data/runs/deadline_cohort_2800524c9b2e0729 --before reports/software_checks/deadline_generation2_before_20261018.json
```

The new completion checker verifies repeat comparisons and preservation; it does not change the scientific analysis. Its generation labels are read as text so that `1`, `2` and `1-2` compare correctly against earlier exports. Notebook 07 and its builder now link to the completed findings; their analysis code is unchanged.
