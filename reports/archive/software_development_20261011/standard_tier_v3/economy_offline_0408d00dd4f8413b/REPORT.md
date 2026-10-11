# SYNTHETIC SOFTWARE CHECK — no model or human observations

Run `economy_offline_0408d00dd4f8413b`. Protocol `student-high-economy-revision-v3`. Status: **complete**. Reason: Finished requested stage. Conservative API charges/reservations for this run: **$0.000000**.

## What this experiment tests

A hypothetical second-year UB business student makes an initial current-week choice at fixed high effort. The short condition submits that choice. The adequate condition receives one additional high-effort revision opportunity. Initial generation has a 16,384-token ceiling; the extra opportunity has an 8,192-token ceiling. This is an additional-deliberation intervention, not a single-call total-budget intervention or a validated human deadline. Information quantity is held constant; information overload is not separately randomized. Four fictional personality profiles are matched across treatments and rotated across roles in four-pair blocks. Their equal weighting is a design choice, not a measured student population. No human data exist.

Only valid same-week model submissions become orders. An unfinished token-limited revision leaves the initial submission in force. An initial failure or technical error stops the run. Zero and large orders remain outcomes; no interior-order target is imposed.

## Manipulation checks

Held-out and development feasibility screen passed: **False**. Main-game median short/adequate total-token ratio: **None**; required ≤0.75. Main-game separation passed: **False**. These are small-sample computational checks, not population validation. Both phases count toward computation. No games are purchased after a failed live feasibility screen.

| split | n | initial_valid | revision_valid | median_initial_to_total_ratio | passed |
| --- | --- | --- | --- | --- | --- |
| development | 8 | 8 | 8 | — | False |
| holdout | 8 | 8 | 8 | — | False |

## Hypotheses and conclusions

| hypothesis | predicted_short_minus_adequate | pairs | estimate | p_raw | ci_lower | ci_upper | status | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1_sensitivity | <0 | 1 | 0 | — | — | — | descriptive; inference withheld | — |
| H2_cost | >0 | 1 | 0 | — | — | — | descriptive; inference withheld | — |
| H3_bullwhip | >0 | 1 | 0 | — | — | — | descriptive; inference withheld | — |

H3 is the primary bullwhip outcome: mean over roles of sample order variance divided by customer-demand variance during model decision weeks only. H2 is total chain holding/backlog cost including the fixed practice and automatic continuation. H1 is a separate matched-state mechanism assay: negative order change divided by the 24-case pipeline increase, averaged across roles. H1 measures direct supply-line responsiveness; it does not identify the old dynamic beta. The historical beta hypothesis remains separate.

All contrasts are short minus adequate. Independent replication is the paired four-role chain block, not a call or week. Initial draws are shared only within a pair when complete prompts match, a common-random-draw variance-reduction design. Different blocks always buy distinct draws. Paired t tests and 95% intervals require independent blocks and suitable difference distributions. The three tests form one Holm family. Fewer than eight pairs, failed manipulation, incomplete games or synthetic inputs withhold inference. Eight is a reporting floor, not evidence of adequate power. No sample size guarantees significance.

## Chain outcomes

| block | condition | complete | scored_cost | observed_cost | decision_cost | bullwhip | sensitivity | decisions | mean_tokens | median_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | adequate | True | 1085 | 1085 | 493.5 | 0.902555 | 0 | 80 | 0 | 0 |
| 0 | short | True | 1085 | 1085 | 493.5 | 0.902555 | 0 | 80 | 0 | 0 |

## Bullwhip and behavior by role

| block | condition | role | profile_id | bullwhip_customer | bullwhip_local | demand_variance | order_variance | zero_orders | max_order | backlog_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | adequate | distributor | flexible_calm | 0.8998 | 1 | 5.25263 | 4.72632 | 1 | 7 | 0 |
| 0 | adequate | factory | methodical_calm | 0.799098 | 1 | 5.25263 | 4.19737 | 1 | 7 | 0 |
| 0 | adequate | retailer | flexible_concerned | 1 | 1 | 5.25263 | 5.25263 | 1 | 7 | 0 |
| 0 | adequate | wholesaler | methodical_concerned | 0.911323 | 1 | 5.25263 | 4.78684 | 1 | 7 | 0 |
| 0 | short | distributor | flexible_calm | 0.8998 | 1 | 5.25263 | 4.72632 | 1 | 7 | 0 |
| 0 | short | factory | methodical_calm | 0.799098 | 1 | 5.25263 | 4.19737 | 1 | 7 | 0 |
| 0 | short | retailer | flexible_concerned | 1 | 1 | 5.25263 | 5.25263 | 1 | 7 | 0 |
| 0 | short | wholesaler | methodical_concerned | 0.911323 | 1 | 5.25263 | 4.78684 | 1 | 7 | 0 |

Customer demand is prospectively generated as independent uniform integers 0 through 8 after four practice weeks. Participants know the distribution; this reduces a demand-learning confound. Each paired block receives the same exogenous sequence, hidden from participants. This preserves variation in the measurement window. A local ratio with constant local demand remains undefined. Twelve automatic weeks repeat each role's final submitted quantity and the final customer demand; this differs from the historical demand-following tail and is not behavioral data.

## Cost controls and reproducibility

Conservative standard-tier estimate: all uncached input charged at cache-write rate .125 per million; ordinary input rate is .10. Output .50; cached reads .01.

Official API ID gpt-6-luna; no dated snapshot is published. Requested and returned IDs must match; long-term alias drift remains a reproducibility limitation.

This v3 run fixes GPT-6 Luna and high effort across conditions. The model change was chosen for price before v3 outcomes; Mini calibration and game evidence are not pooled with it.

Identical paired initial prompts share one paid draw; repeated independent replications never share draws. Exact completed request checkpoints are reused on resume. Stable instructions occur first for provider prompt caching; actual cached-input usage is recorded and output/reasoning charges remain payable. Temperature is omitted in all calls. No correctness retry or automatic switch to a more expensive model is used. The $10 campaign includes the previous $5.19360675, and all v2/v3 redesign work together is capped at $4.80; new campaign identifiers require new explicit budget authorization.

Saved-evidence audit: **{'passed': True, 'physical_states_replayed': 288, 'request_records': 212, 'selected_orders_verified': 176}**. Exact requests, responses, chosen-source request IDs, code snapshots, demand paths and configuration are retained under the source data directory. Analysis makes no API calls.

## Limitations and next decision

A completed pilot establishes operation and, if the checks pass, a measured extra-computation contrast. It does not establish that an LLM is a real UB student, that information overload was manipulated, or that extra computation must improve decisions. Keep null or opposite-direction outcomes. Determine a meaningful chain-level effect and power before a larger study. Human comparison materials are available in docs/STUDENT_VALIDATION_20261011.md.

## Calibration observations

| case_id | split | history_length | initial_valid | revision_valid | initial_output_tokens | initial_reasoning_tokens | revision_output_tokens | revision_reasoning_tokens | initial_charge_usd | revision_charge_usd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| development-0-retailer | development | 4 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| development-0-wholesaler | development | 9 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| development-0-distributor | development | 18 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| development-0-factory | development | 27 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| development-1-retailer | development | 7 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| development-1-wholesaler | development | 14 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| development-1-distributor | development | 23 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| development-1-factory | development | 30 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| holdout-0-retailer | holdout | 4 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| holdout-0-wholesaler | holdout | 9 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| holdout-0-distributor | holdout | 18 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| holdout-0-factory | holdout | 27 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| holdout-1-retailer | holdout | 7 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| holdout-1-wholesaler | holdout | 14 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| holdout-1-distributor | holdout | 23 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |
| holdout-1-factory | holdout | 30 | True | True | 0 | 0 | 0 | 0 | 0 | 0 |

## Student profiles

| id | label | status | background | description |
| --- | --- | --- | --- | --- |
| methodical_calm | Methodical, emotionally steady | Fictional experimental profile; not measured from UB students | Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training. | In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision. |
| methodical_concerned | Methodical, uncertainty-sensitive | Fictional experimental profile; not measured from UB students | Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training. | In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision. |
| flexible_calm | Flexible, emotionally steady | Fictional experimental profile; not measured from UB students | Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training. | In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision. |
| flexible_concerned | Flexible, uncertainty-sensitive | Fictional experimental profile; not measured from UB students | Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training. | In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision. |

Profiles cross an organized/methodical versus flexible/informal tendency with emotionally steady versus uncertainty-sensitive framing. These are explicit fictional personality prompts, not psychometric scores or instructions to exhibit a bias. See reports/revised_design_20261011/REPORT.md for the primary literature and the limits of this adaptation.

## Original structural beta: exploratory identification check

| block | condition | role | theta | alpha | beta | target | rmse | r2 | jac_condition | usable | fit_flag | n | order_limit | cap_hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | adequate | distributor | 0.999996 | 4.41502e-06 | 1.53728 | 24.3456 | 5.75615e-06 | 1 | 8.76564 | False | weak_inventory_response;parameter_boundary | 20 | — | 0 |
| 0 | adequate | factory | 0.999997 | 2.6467e-06 | 1.60901 | 24.7435 | 3.33199e-06 | 1 | 8.72024 | False | weak_inventory_response;parameter_boundary | 20 | — | 0 |
| 0 | adequate | retailer | 0.999997 | 2.90464e-06 | 1.48198 | 23.8061 | 4.4368e-06 | 1 | 7.55978 | False | weak_inventory_response;parameter_boundary | 20 | — | 0 |
| 0 | adequate | wholesaler | 0.999994 | 5.94154e-06 | 1.54651 | 24.2497 | 9.29097e-06 | 1 | 8.56157 | False | weak_inventory_response;parameter_boundary | 20 | — | 0 |
| 0 | short | distributor | 0.999996 | 4.41502e-06 | 1.53728 | 24.3456 | 5.75615e-06 | 1 | 8.76564 | False | weak_inventory_response;parameter_boundary | 20 | — | 0 |
| 0 | short | factory | 0.999997 | 2.6467e-06 | 1.60901 | 24.7435 | 3.33199e-06 | 1 | 8.72024 | False | weak_inventory_response;parameter_boundary | 20 | — | 0 |
| 0 | short | retailer | 0.999997 | 2.90464e-06 | 1.48198 | 23.8061 | 4.4368e-06 | 1 | 7.55978 | False | weak_inventory_response;parameter_boundary | 20 | — | 0 |
| 0 | short | wholesaler | 0.999994 | 5.94154e-06 | 1.54651 | 24.2497 | 9.29097e-06 | 1 | 8.56157 | False | weak_inventory_response;parameter_boundary | 20 | — | 0 |

The original dynamic beta fit is retained with its original identification checks. Unusable numerical values do not measure supply-line neglect. The H1_sensitivity assay above is a revised operationalization of the mechanism, not a relabeling of these coefficients.

## Primary API documentation

[Reasoning output limits](https://developers.openai.com/api/docs/guides/reasoning), [model and pricing](https://developers.openai.com/api/docs/models/gpt-6-luna), [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).
