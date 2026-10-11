# Beer Game reports

The active under-$3 version is **GPT-6 Luna Flex, fixed high effort (v3)**; see [the cost amendment](../docs/ECONOMY_PROTOCOL_20261011.md). Its new run cap is $2.20 (fresh calibration capped at $0.18), with a shared cap on redesign spending. New reports use `economy_<mode>_<fingerprint>/` and `LATEST_ECONOMY_REPORT.json`.

The latest paid pilot is **[economy_api_a80275c58f2c07e0](economy_api_a80275c58f2c07e0/FINDINGS.md)**. Both chains completed, with 160 model orders, zero fallbacks, passed calibration and passed actual-token separation (495 versus 871 median tokens). The Luna run cost an estimated **$0.0679134225**; redesign spending including Mini is **$0.7877313225**. One pair remains descriptive: H2/H3 point in the predicted direction, while revised H1 points in the opposite direction. Both customer-referenced variance ratios are below 1, and most of the cost contrast comes from the artificial continuation. Read the findings before interpreting the tables.

| Current pilot file | Contents |
| --- | --- |
| [FINDINGS.md](economy_api_a80275c58f2c07e0/FINDINGS.md) / [Pilot_Findings.docx](economy_api_a80275c58f2c07e0/Pilot_Findings.docx) | Readable results, interpretation, cost breakdown, order plot, notebook run instructions |
| [REPORT.md](economy_api_a80275c58f2c07e0/REPORT.md) / [Economy_Study_Report.docx](economy_api_a80275c58f2c07e0/Economy_Study_Report.docx) | Full hypotheses, calibration, role results, profiles, beta diagnostics and provenance |
| [DETAILS.xlsx](economy_api_a80275c58f2c07e0/DETAILS.xlsx) | Full numerical tables |
| [Evidence audit](software_checks/economy_api_a80275c58f2c07e0_audit.json) | 288 replayed states, 176 verified selections, 260 completed requests, 281 unchanged raw files |

The earlier **[Mini calibration](anytime_api_206b831bd7eab63e/REPORT.md)** remains separate: two held-out revisions truncated, so no Mini games started. Its cost was $0.7198179; [Word report](anytime_api_206b831bd7eab63e/Anytime_Study_Report.docx), [workbook](anytime_api_206b831bd7eab63e/DETAILS.xlsx), and [audit](software_checks/anytime_api_206b831bd7eab63e_audit.json) are preserved. Different model protocols are not pooled.

The revised design and literature review are in **[revised_design_20261011](revised_design_20261011/REPORT.md)**. New v2 run reports use `anytime_<mode>_<fingerprint>/`, linked by `LATEST_ANYTIME_REPORT.json`.

The completed historical single-call API pilot remains in **[student_pilot_20261011](student_pilot_20261011/)**. Synthetic reports are software checks, not API evidence.

| File | Contents |
| --- | --- |
| [Student_Pilot_Report.docx](student_pilot_20261011/Student_Pilot_Report.docx) | Full readable report: findings, H1/H2 analysis, calibration, coefficient diagnostics, costs and bullwhip |
| [REPORT.md](student_pilot_20261011/REPORT.md) | The same report in Markdown |
| [DETAILS.xlsx](student_pilot_20261011/DETAILS.xlsx) | Analysis tables and evidence hashes |
| [hypotheses.csv](student_pilot_20261011/hypotheses.csv) | H1/H2 estimates, eligibility and conclusions |
| [analysis_manifest.json](student_pilot_20261011/analysis_manifest.json) | Source run, analysis fingerprint, inputs and provenance |

The completed pilot used one chain pair. H1 is unidentifiable; H2's observed cost difference is zero. Failed calibration and insufficient replication withhold inferential conclusions. The full report explains these limits.

## Earlier reports

| Study | Word report | Workbook |
| --- | --- | --- |
| 5 October nano pilot | [Pilot_Report.docx](archive/20261005/pilot_02_game_api_8236a9c840b29d36/Pilot_Report.docx) | [DETAILS.xlsx](archive/20261005/pilot_02_game_api_8236a9c840b29d36/DETAILS.xlsx) |
| 5 October Luna follow-up | [Budget_Followup_Report.docx](archive/20261005/budget_followup_20261005/Budget_Followup_Report.docx) | [DETAILS.xlsx](archive/20261005/budget_followup_20261005/DETAILS.xlsx) |

Earlier full-hypothesis report versions are in [archive/analysis_versions](archive/analysis_versions/). These are historical versions, not additional experiments. Their contents were preserved; the [organization record](archive/organization_20261011.json) records original paths and file hashes.

## Supporting files

- [135-test Flex software check](software_checks/economy_flex_full_tests_20261011.log), [eight-cell notebook execution](software_checks/notebook04_economy_flex_20261011.json), [updated notebook documentation check](software_checks/notebook04_documentation_20261011.json), and [findings export checks](software_checks/economy_findings_20261011.json).
- [software_checks](software_checks/): offline tests, notebook checks and evidence audits.
- [logs/student_pilot_20261011](logs/student_pilot_20261011/): completed campaign logs and historical PID records.
- [LATEST_REPORT.txt](LATEST_REPORT.txt): current report-file paths.
- [LATEST_STUDENT_HYPOTHESIS_REPORT.json](LATEST_STUDENT_HYPOTHESIS_REPORT.json): current report folder and source data folder.
- `ACTIVE_STUDENT_RUN.json` and `LATEST_CALIBRATION.json`: progress and reusable-calibration pointers used by the notebook.

Generate reports from the project root with:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_student_hypothesis_report.py --run data/runs/student_api_b609eca42866feb0
```

The exporter writes to `reports/` and uses saved evidence without API calls. Original raw evidence remains in `data/`.

## Revised design and software evidence, 11 October 2026

- [Design review (Word)](revised_design_20261011/Design_Review.docx) and [literature/design review](revised_design_20261011/REPORT.md).
- [Full 110-test log](software_checks/anytime_full_tests_20261011.log), [eight-cell notebook audit](software_checks/notebook04_20261011.json), and [historical source-preservation audit](software_checks/redesign_provenance_20261011.json).
- Revised live process logs: `logs/personality_pilot_20261011/`. The key is requested only through a masked dialog; it is never written to logs.
- Two superseded development-only reports were archived under `archive/software_development_20261011/`; raw software evidence remains under `data/runs/`.
