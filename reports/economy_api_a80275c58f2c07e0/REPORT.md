# LLM Beer Game: initial choice and additional deliberation

Run `economy_api_a80275c58f2c07e0`. Protocol `student-high-economy-revision-v3`. Status: **complete**. Reason: Finished requested stage. Conservative API charges/reservations for this run: **$0.067913**.

## What this experiment tests

A hypothetical second-year UB business student makes an initial current-week choice at fixed high effort. The short condition submits that choice. The adequate condition receives one additional high-effort revision opportunity. Initial generation has a 16,384-token ceiling; the extra opportunity has an 8,192-token ceiling. This is an additional-deliberation intervention, not a single-call total-budget intervention or a validated human deadline. Information quantity is held constant; information overload is not separately randomized. Four fictional personality profiles are matched across treatments and rotated across roles in four-pair blocks. Their equal weighting is a design choice, not a measured student population. No human data exist.

Only valid same-week model submissions become orders. An unfinished token-limited revision leaves the initial submission in force. An initial failure or technical error stops the run. Zero and large orders remain outcomes; no interior-order target is imposed.

## Small feasibility test and spending limits

The first four development states form a quick computation check across all roles. Failed completion/headroom or computation-separation checks stop before further purchases. The entire fresh calibration has a $0.18 cap. Only passing both full eight-case splits permits games. The live pilot cap is $2.20; with the earlier $0.7198179 Mini calibration this attempt stays below $2.92. Synthetic positive, negative and null controls verify the analysis code, not the model persona.

| cases | median_initial_tokens | median_combined_tokens | initial_to_combined_ratio | passed | synthetic | note |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | 726 | 1633 | 0.444581 | True | False | First four development cases only; not independent validation or a hypothesis test. |

## Manipulation checks

Held-out and development feasibility screen passed: **True**. Main-game median short/adequate total-token ratio: **0.5683122847301951**; required ≤0.75. Main-game separation passed: **True**. These are small-sample computational checks, not population validation. Both phases count toward computation. No games are purchased after a failed live feasibility screen.

| split | n | initial_valid | revision_valid | median_initial_to_total_ratio | passed |
| --- | --- | --- | --- | --- | --- |
| development | 8 | 8 | 8 | 0.446996 | True |
| holdout | 8 | 8 | 8 | 0.514887 | True |

## Hypotheses and conclusions

| hypothesis | predicted_short_minus_adequate | pairs | estimate | p_raw | ci_lower | ci_upper | status | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1_sensitivity | <0 | 1 | 0.104167 | — | — | — | descriptive; inference withheld | — |
| H2_cost | >0 | 1 | 242.5 | — | — | — | descriptive; inference withheld | — |
| H3_bullwhip | >0 | 1 | 0.123497 | — | — | — | descriptive; inference withheld | — |

H3 is the primary bullwhip outcome: mean over roles of sample order variance divided by customer-demand variance during model decision weeks only. H2 is total chain holding/backlog cost including the fixed practice and automatic continuation. H1 is a separate matched-state mechanism assay: negative order change divided by the 24-case pipeline increase, averaged across roles. H1 measures direct supply-line responsiveness; it does not identify the old dynamic beta. The historical beta hypothesis remains separate.

All contrasts are short minus adequate. Independent replication is the paired four-role chain block, not a call or week. Initial draws are shared only within a pair when complete prompts match, a common-random-draw variance-reduction design. Different blocks always buy distinct draws. Paired t tests and 95% intervals require independent blocks and suitable difference distributions. The three tests form one Holm family. Fewer than eight pairs, failed manipulation, incomplete games or synthetic inputs withhold inference. Eight is a reporting floor, not evidence of adequate power. No sample size guarantees significance.

## Chain outcomes

| block | condition | complete | scored_cost | observed_cost | decision_cost | bullwhip | sensitivity | decisions | mean_tokens | median_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | adequate | True | 1091 | 1091 | 441 | 0.757515 | 0.333333 | 80 | 1015.48 | 871 |
| 0 | short | True | 1333.5 | 1333.5 | 458.5 | 0.881012 | 0.4375 | 80 | 596.562 | 495 |

## Bullwhip and behavior by role

| block | condition | role | profile_id | bullwhip_customer | bullwhip_local | demand_variance | order_variance | zero_orders | max_order | backlog_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | adequate | distributor | flexible_calm | 0.729459 | 1.21333 | 5.25263 | 3.83158 | 7 | 4 | 0 |
| 0 | adequate | factory | methodical_calm | 0.769539 | 1.05495 | 5.25263 | 4.04211 | 8 | 4 | 0 |
| 0 | adequate | retailer | flexible_concerned | 0.92986 | 0.92986 | 5.25263 | 4.88421 | 4 | 8 | 3 |
| 0 | adequate | wholesaler | methodical_concerned | 0.601202 | 0.824176 | 5.25263 | 3.15789 | 5 | 4 | 0 |
| 0 | short | distributor | flexible_calm | 0.839178 | 0.849822 | 5.25263 | 4.40789 | 9 | 5 | 1 |
| 0 | short | factory | methodical_calm | 0.793587 | 1 | 5.25263 | 4.16842 | 11 | 4 | 0 |
| 0 | short | retailer | flexible_concerned | 0.911824 | 0.911824 | 5.25263 | 4.78947 | 4 | 7 | 6 |
| 0 | short | wholesaler | methodical_concerned | 0.979459 | 1.24443 | 5.25263 | 5.14474 | 7 | 7 | 4 |

Customer demand is prospectively generated as independent uniform integers 0 through 8 after four practice weeks. Participants know the distribution; this reduces a demand-learning confound. Each paired block receives the same exogenous sequence, hidden from participants. This preserves variation in the measurement window. A local ratio with constant local demand remains undefined. Twelve automatic weeks repeat each role's final submitted quantity and the final customer demand; this differs from the historical demand-following tail and is not behavioral data.

## Cost controls and reproducibility

Conservative Flex estimate: all uncached input charged at cache-write rate .0625 per million; ordinary input rate is .05. Output .25; cached reads .005. Unknown or non-Flex outcomes reserve/charge standard rates; no automatic standard fallback.

Official API ID gpt-6-luna; no dated snapshot is published. Requested and returned IDs must match; long-term alias drift remains a reproducibility limitation.

This v3 run fixes GPT-6 Luna and high effort across conditions. The model change was chosen for price before v3 outcomes; Mini calibration and game evidence are not pooled with it.

Identical paired initial prompts share one paid draw; repeated independent replications never share draws. Exact completed request checkpoints are reused on resume. Stable instructions occur first for provider prompt caching; actual cached-input usage is recorded and output/reasoning charges remain payable. Temperature is omitted in all calls. No correctness retry or automatic switch to a more expensive model is used. The $10 campaign includes the previous $5.19360675, and all v2/v3 redesign work together is capped at $2.95; new campaign identifiers require new explicit budget authorization.

Saved-evidence audit: **{'passed': True, 'physical_states_replayed': 288, 'request_records': 260, 'selected_orders_verified': 176}**. Exact requests, responses, chosen-source request IDs, code snapshots, demand paths and configuration are retained under the source data directory. Analysis makes no API calls.

## Limitations and next decision

A completed pilot establishes operation and, if the checks pass, a measured extra-computation contrast. It does not establish that an LLM is a real UB student, that information overload was manipulated, or that extra computation must improve decisions. Keep null or opposite-direction outcomes. Determine a meaningful chain-level effect and power before a larger study. Human comparison materials are available in docs/STUDENT_VALIDATION_20261011.md.

## Calibration observations

| case_id | split | history_length | initial_valid | revision_valid | initial_output_tokens | initial_reasoning_tokens | revision_output_tokens | revision_reasoning_tokens | initial_charge_usd | revision_charge_usd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| development-0-retailer | development | 4 | True | True | 510 | 496 | 496 | 482 | 0.00019625 | 0.000194187 |
| development-0-wholesaler | development | 9 | True | True | 942 | 928 | 1347 | 1333 | 0.00032775 | 0.000430437 |
| development-0-distributor | development | 18 | True | True | 339 | 325 | 907 | 893 | 0.000217437 | 0.000360875 |
| development-0-factory | development | 27 | True | True | 1378 | 1364 | 642 | 628 | 0.000516562 | 0.000334 |
| development-1-retailer | development | 7 | True | True | 661 | 647 | 380 | 366 | 0.00024775 | 0.000178938 |
| development-1-wholesaler | development | 14 | True | True | 161 | 147 | 234 | 220 | 0.000155625 | 0.000175313 |
| development-1-distributor | development | 23 | True | True | 405 | 391 | 433 | 419 | 0.000256812 | 0.00026525 |
| development-1-factory | development | 30 | True | True | 151 | 137 | 315 | 301 | 0.000223187 | 0.000265625 |
| holdout-0-retailer | holdout | 4 | True | True | 897 | 883 | 619 | 605 | 0.000229923 | 0.000224938 |
| holdout-0-wholesaler | holdout | 9 | True | True | 871 | 857 | 367 | 353 | 0.00031 | 0.000185438 |
| holdout-0-distributor | holdout | 18 | True | True | 547 | 533 | 1044 | 1030 | 0.000269437 | 0.000395125 |
| holdout-0-factory | holdout | 27 | True | True | 1434 | 1420 | 1108 | 1094 | 0.000530563 | 0.0004505 |
| holdout-1-retailer | holdout | 7 | True | True | 110 | 96 | 477 | 463 | 0.00011 | 0.000203187 |
| holdout-1-wholesaler | holdout | 14 | True | True | 1452 | 1438 | 1048 | 1034 | 0.000478375 | 0.000378813 |
| holdout-1-distributor | holdout | 23 | True | True | 114 | 100 | 143 | 129 | 0.000184063 | 0.00019275 |
| holdout-1-factory | holdout | 30 | True | True | 187 | 173 | 165 | 151 | 0.000232187 | 0.000228125 |

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
| 0 | adequate | distributor | 0.533368 | 0.128264 | 1.32007 | 14.1101 | 0.95025 | 0.75193 | 8.33695 | True | ok | 20 | — | 0 |
| 0 | adequate | factory | 1 | 0.108374 | 0.318182 | 11.6364 | 0.823306 | 0.823481 | 10.4758 | True | ok | 20 | — | 0 |
| 0 | adequate | retailer | 1.25964e-16 | 0.49977 | 0.667311 | 8.63237 | 0.793868 | 0.864175 | 9.59157 | True | ok | 20 | — | 0 |
| 0 | adequate | wholesaler | 0.438749 | 0.122163 | 1.08947 | 13.5152 | 0.674695 | 0.848262 | 10.472 | True | ok | 20 | — | 0 |
| 0 | short | distributor | 0.590355 | 0.0459862 | 2 | 8.03823 | 1.11041 | 0.705552 | 8.86604 | False | parameter_boundary;upper_parameter_limit | 20 | — | 0 |
| 0 | short | factory | 1 | 0.335821 | 6.17201e-23 | 9.24444 | 0.651061 | 0.892959 | 4.47359 | True | parameter_boundary | 20 | — | 0 |
| 0 | short | retailer | 2.6326e-24 | 0.526299 | 0.88699 | 8.77775 | 0.83578 | 0.846477 | 8.83064 | True | ok | 20 | — | 0 |
| 0 | short | wholesaler | 0.725523 | 0.0743463 | 0.361973 | 0.0388129 | 1.17085 | 0.719509 | 9.41582 | True | ok | 20 | — | 0 |

The original dynamic beta fit is retained with its original identification checks. Unusable numerical values do not measure supply-line neglect. The H1_sensitivity assay above is a revised operationalization of the mechanism, not a relabeling of these coefficients.

## Primary API documentation

[Reasoning output limits](https://developers.openai.com/api/docs/guides/reasoning), [model and pricing](https://developers.openai.com/api/docs/models/gpt-6-luna), [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).
