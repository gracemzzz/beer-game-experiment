# All values and variable definitions

[Open the workbook](ALL_VALUES.xlsx) for all current tables in one file. [Full report](../REPORT.md).

A = 120 s + control reading; B = 8 s + control reading; C = 8 s + causal education. These are three conditions in one study.

[Measurement dictionary](VARIABLE_DICTIONARY.csv) · [Every original export field explained](SOURCE_FIELD_DICTIONARY.csv)

| File | Rows | What it contains |
|---|---|---|
| [CONDITION_OUTCOMES.csv](CONDITION_OUTCOMES.csv) | 12 | Actual means, SDs and ranges for the four primary measured quantities in all three conditions. |
| [ALL_MEASURED_VALUES.csv](ALL_MEASURED_VALUES.csv) | 81 | All reported measurements: definition, calculation, aggregation, value, SD, range and count for each condition. |
| [HYPOTHESIS_COMPARISONS.csv](HYPOTHESIS_COMPARISONS.csv) | 5 | Full named comparisons, both condition means, signed differences, intervals and p-values. |
| [SAMPLE_SIZE_VALUES.csv](SAMPLE_SIZE_VALUES.csv) | 50 | All exact values behind both sample-prefix figures; n means matched blocks. |
| [CHAIN_VALUES.csv](CHAIN_VALUES.csv) | 30 | All 30 main contexts and their saved metrics/statuses. |
| [WEEKLY_ROLE_VALUES.csv](WEEKLY_ROLE_VALUES.csv) | 2880 | All 2,880 role-week observations, including actual orders, inventory, backlog, receipts, shipments, outstanding orders and costs. |
| [ROLE_VALUES.csv](ROLE_VALUES.csv) | 120 | All 120 role outcomes, final states and ordering diagnostics. |
| [PROBE_ANSWERS.csv](PROBE_ANSWERS.csv) | 960 | All 960 actual scenario answers with complete displayed state variables. |
| [PROBE_PAIRS.csv](PROBE_PAIRS.csv) | 480 | All 480 matched probe pairs, exact low/high quantities, orders and slopes (240 pipeline and 240 backlog pairs). |
| [QUIZ_ANSWERS.csv](QUIZ_ANSWERS.csv) | 120 | All 120 actual quiz answers, question text, alternatives, frozen correct answer and score. |
| [RESPONSE_TIMES.csv](RESPONSE_TIMES.csv) | 990 | All 990 accepted packet latencies: 720 game, 240 probe and 30 quiz packets; not thinking time. |
| [TIME_ALLOWANCE_RECALL.csv](TIME_ALLOWANCE_RECALL.csv) | 30 | Assigned seconds and literal public recall disclosures; missing remains missing. |

The frozen technical analysis and development records remain at [analysis/student_framing_v3](../../analysis/student_framing_v3/). Only the 30 main contexts enter current condition summaries and tests.
