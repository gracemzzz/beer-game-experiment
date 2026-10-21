# Collected responses: GPT-6 Astra / extra high effort

**Received 20 October 2026: 6/6 complete responses accepted without conversion.** Each contains 125 chains / 500 fictional identities. Together they contain **60,000 submitted weekly orders**, **3,000 matched-state probe pairs**, and **108,000 physically replayed role-week states**. The same identities repeat across cases and generations; this is not a sample of 3,000 independent people.

The reported settings are **GPT-6 Astra / extra high effort**. The original statement was: "I'm using gpt 6-astra extra high effort". Actual provider identity, interface, compute, full-prompt use, fresh-chat isolation and generation code were not independently verified. The frozen parent plan specified GPT-6 / Pro, so the actual reported settings are recorded through a new collection fingerprint and exact parent-prompt lineage. This amendment is recorded after collection. No response IDs or original bytes were changed, and these observations are not pooled with the earlier assistant pilot. [Settings amendment](SETTINGS_AMENDMENT.md).

## Observed case means

A = 60 seconds / control. B = 10 seconds / identical control. C = 10 seconds / causal reading. Both time values describe the fictional students, not enforced model computation. The matched readings contain 254 words each, rather than a delivered 20-minute lecture.

| arm | sensitivity | total_cost | cost_model | cost_automatic |
| --- | --- | --- | --- | --- |
| a60_control | 0.625000 | 1075.136000 | 460.688000 | 518.448000 |
| b10_control | 0.666667 | 1124.986000 | 469.466000 | 559.520000 |
| c10_education | 0.500000 | 1051.420000 | 448.676000 | 506.744000 |

## H1-H4 descriptive contrasts

H1 is B-A sensitivity (predicted negative); H2 is B-A total cost (predicted positive). H3 is C-B sensitivity (predicted positive); H4 is C-B total cost (predicted negative). Sensitivity is the existing matched-state pipeline-responsiveness proxy, not an identified structural underweighting coefficient. Full cost includes four practice, twenty model and twelve automatic continuation weeks. Model-only costs are separately reported.

| hypothesis | mean_difference | direction |
| --- | --- | --- |
| H1 | 0.041667 | opposite direction |
| H2 | 49.850000 | predicted direction |
| H3 | -0.166667 | opposite direction |
| H4 | -73.566000 | predicted direction |

These directions describe this fixed set of generated outputs. They do not establish statistically significant treatment effects or confirm the literal human-time hypotheses. There are two response-level generations per case; jointly generated chain rows do not provide independent student replications. The [full report](REPORT.md) shows each repetition, same-case variation, changed orders and the cost-phase contrasts. The saved ABC/ACB task order provides partial order balance; actual execution order and concurrency were not verified.

No new model calls, paid API runs, prompt changes, favorable-effect filters or additional sampling were used for this analysis. All six source files, including compact response5.json, passed the same exact schema and replay checks. No serialization or generation source was supplied, so JSON validity cannot establish that choices were generated without a scripted policy.

[Excel results](results/RESULTS.xlsx) · [Only submitted weekly orders](results/weekly_orders.csv) · [All exact prompts](EXACT_PROMPTS.md) · [Original responses](original_responses/FILE_MAP.json).
