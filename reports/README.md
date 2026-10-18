# Beer Game reports

**17 October 2026: manual cohort workflow.** [Notebook 06](../notebooks/06_manual_cohort_simulation.ipynb) accepts copied chat-model output for many fictional students at once. [Protocol and interpretation](../docs/MANUAL_COHORT_PROTOCOL_20261017.md). New prompts, descriptive reports, Excel/CSV tables and PNG/PDF plots use `manual_cohort_<fingerprint>/`; [LATEST_MANUAL_COHORT_REPORT.json](LATEST_MANUAL_COHORT_REPORT.json) identifies the current prepared/imported run. [Software checks](software_checks/manual_cohort_20261017.json) use synthetic data only. No manual model output has been collected as part of implementation. Whole-trajectory revision differs from the API experiment; generated students do not supply independent-human hypothesis tests. API results below remain separate.

Prepared 500-identity run: [prompt index](manual_cohort_47982790c9de87be/PROMPTS.md), [first copy-and-paste prompt](manual_cohort_47982790c9de87be/prompts/b0001_INITIAL.md), [waiting-for-data report](manual_cohort_47982790c9de87be/REPORT.md). The two-pass workflow needs ten responses at the default batch size; none have yet been collected.

The new under-$3 replication is **Claude Haiku 5.5, fixed high effort (v4), direct Anthropic**; see [the prospective amendment](../docs/CLAUDE_PROTOCOL_20261011.md) and [notebook 05](../notebooks/05_claude_deliberation_study.ipynb). Its new-run cap is $2.15 (fresh calibration capped at $0.18), with a $2.95 shared redesign guard counting previous Mini/Luna spending. New reports use `claude_<mode>_<fingerprint>/` and `LATEST_CLAUDE_REPORT.json`. The target is eight paired blocks conditional on calibration and cost eligibility; software checks are not empirical evidence.

The separately completed **GPT-6 Luna Flex v3** study remains in notebook 04; see [its cost amendment](../docs/ECONOMY_PROTOCOL_20261011.md). Its reports use `economy_<mode>_<fingerprint>/` and `LATEST_ECONOMY_REPORT.json`.

The latest paid study is **[Claude, eight paired blocks](claude_api_fd5533fef5828d96/FINDINGS.md)**: all 16 chains finished, 1,280 model orders, zero fallbacks, all 2,060 responses completed and both computation checks passed (506 versus 1,121 median generated tokens). Revised H1 has evidence in the predicted direction (Holm p=0.015987); H2 and primary H3 remain inconclusive (both Holm p=0.327260), with opposite-direction point estimates. The original structural-beta hypothesis remains unresolved. Claude cost **$1.065919405**; total redesign spending including earlier Mini/Luna calls is **$1.8536507275**. Every chain-average customer-referenced bullwhip ratio was below 1, and the automatic continuation reverses the model-week cost contrast. These limitations are explicit in the findings.

| Current Claude file | Contents |
| --- | --- |
| [CLAUDE_API_PROMPTS.md](claude_api_fd5533fef5828d96/CLAUDE_API_PROMPTS.md) | Readable boxes for the system prompt, four profiles, rules questions, initial choice and revision, with short stage explanations; checked against all 2,060 Claude requests |
| [FINDINGS.md](claude_api_fd5533fef5828d96/FINDINGS.md) / [Pilot_Findings.docx](claude_api_fd5533fef5828d96/Pilot_Findings.docx) | Conclusions, uncertainty, order behavior, cost phases, paired-difference plot and notebook instructions |
| [REPORT.md](claude_api_fd5533fef5828d96/REPORT.md) / [Claude_Study_Report.docx](claude_api_fd5533fef5828d96/Claude_Study_Report.docx) | Full hypothesis analysis, calibration, role results, beta diagnostics and provenance |
| [DETAILS.xlsx](claude_api_fd5533fef5828d96/DETAILS.xlsx) | Numerical tables |
| [Paired contrasts PDF](claude_api_fd5533fef5828d96/paired_contrasts.pdf) | Every independent paired difference and eligible marginal intervals |
| [Evidence audit](software_checks/claude_api_fd5533fef5828d96_audit.json) / [independent statistics/export check](software_checks/claude_final_findings_20261011.json) | 2,304 replayed states, 1,408 verified choices, 2,082 unchanged raw files, independently checked tests/intervals/Holm |

The earlier paid pilot is **[economy_api_a80275c58f2c07e0](economy_api_a80275c58f2c07e0/FINDINGS.md)**. Both chains completed, with 160 model orders, zero fallbacks, passed calibration and passed actual-token separation (495 versus 871 median tokens). The Luna run cost an estimated **$0.0679134225**; redesign spending at that time including Mini was **$0.7877313225**. One pair remains descriptive: H2/H3 point in the predicted direction, while revised H1 points in the opposite direction. Both customer-referenced variance ratios are below 1, and most of the cost contrast comes from the artificial continuation. Read the findings before interpreting the tables. Do not pool it with Claude or interpret the unequal samples as a model-by-treatment test.

| Earlier Luna pilot file | Contents |
| --- | --- |
| [GPT_API_PROMPTS.md](economy_api_a80275c58f2c07e0/GPT_API_PROMPTS.md) | Separate GPT prompt file in the same simple format; checked against all 260 GPT requests |
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
