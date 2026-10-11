# LLM Beer Game: initial choice and additional deliberation

Run `anytime_api_206b831bd7eab63e`. Protocol `student-high-anytime-revision-v2`. Status: **stopped**. Reason: Feasibility screen failed. No games purchased; no automatic diagnostic override. API charges/reservations for this run: **$0.719818**.

## What this experiment tests

A hypothetical second-year UB business student makes an initial current-week choice at fixed high effort. The short condition submits that choice. The adequate condition receives one additional high-effort revision opportunity. Initial generation has a 16,384-token ceiling; the extra opportunity has an 8,192-token ceiling. This is an additional-deliberation intervention, not a single-call total-budget intervention or a validated human deadline. Information quantity is held constant; information overload is not separately randomized. Four fictional personality profiles are matched across treatments and rotated across roles in four-pair blocks. Their equal weighting is a design choice, not a measured student population. No human data exist.

Only valid same-week model submissions become orders. An unfinished token-limited revision leaves the initial submission in force. An initial failure or technical error stops the run. Zero and large orders remain outcomes; no interior-order target is imposed.

## Manipulation checks

Held-out and development feasibility screen passed: **False**. Main-game median short/adequate total-token ratio: **None**; required ≤0.75. Main-game separation passed: **False**. These are small-sample computational checks, not population validation. Both phases count toward computation. No games are purchased after a failed live feasibility screen.

| split | n | initial_valid | revision_valid | median_initial_to_total_ratio | passed |
| --- | --- | --- | --- | --- | --- |
| development | 8 | 8 | 8 | 0.55569 | True |
| holdout | 8 | 8 | 6 | 0.451188 | False |

## Hypotheses and conclusions

| hypothesis | predicted_short_minus_adequate | pairs | estimate | p_raw | ci_lower | ci_upper | status | p_holm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1_sensitivity | <0 | 0 | — | — | — | — | descriptive; inference withheld | — |
| H2_cost | >0 | 0 | — | — | — | — | descriptive; inference withheld | — |
| H3_bullwhip | >0 | 0 | — | — | — | — | descriptive; inference withheld | — |

H3 is the primary bullwhip outcome: mean over roles of sample order variance divided by customer-demand variance during model decision weeks only. H2 is total chain holding/backlog cost including the fixed practice and automatic continuation. H1 is a separate matched-state mechanism assay: negative order change divided by the 24-case pipeline increase, averaged across roles. H1 measures direct supply-line responsiveness; it does not identify the old dynamic beta. The historical beta hypothesis remains separate.

All contrasts are short minus adequate. Independent replication is the paired four-role chain block, not a call or week. Initial draws are shared only within a pair when complete prompts match, a common-random-draw variance-reduction design. Different blocks always buy distinct draws. Paired t tests and 95% intervals require independent blocks and suitable difference distributions. The three tests form one Holm family. Fewer than eight pairs, failed manipulation, incomplete games or synthetic inputs withhold inference. Eight is a reporting floor, not evidence of adequate power. No sample size guarantees significance.

## Chain outcomes

No observations available.

## Bullwhip and behavior by role

No observations available.

Customer demand is prospectively generated as independent uniform integers 0 through 8 after four practice weeks. Participants know the distribution; this reduces a demand-learning confound. Each paired block receives the same exogenous sequence, hidden from participants. This preserves variation in the measurement window. A local ratio with constant local demand remains undefined. Twelve automatic weeks repeat each role's final submitted quantity and the final customer demand; this differs from the historical demand-following tail and is not behavioral data.

## Cost controls and reproducibility

Identical paired initial prompts share one paid draw; repeated independent replications never share draws. Exact completed request checkpoints are reused on resume. Stable instructions occur first for provider prompt caching; actual cached-input usage is recorded and output/reasoning charges remain payable. Temperature is omitted in all calls. No correctness retry or automatic switch to a more expensive model is used. The $10 campaign includes the previous $5.19360675; new campaign identifiers require new explicit budget authorization.

Saved-evidence audit: **{'passed': True, 'physical_states_replayed': 0, 'request_records': 32, 'selected_orders_verified': 0}**. Exact requests, responses, chosen-source request IDs, code snapshots, demand paths and configuration are retained under the source data directory. Analysis makes no API calls.

## Limitations and next decision

A completed pilot establishes operation and, if the checks pass, a measured extra-computation contrast. It does not establish that an LLM is a real UB student, that information overload was manipulated, or that extra computation must improve decisions. Keep null or opposite-direction outcomes. Determine a meaningful chain-level effect and power before a larger study. Human comparison materials are available in docs/STUDENT_VALIDATION_20261011.md.

## Calibration observations

| case_id | split | history_length | initial_valid | revision_valid | initial_output_tokens | initial_reasoning_tokens | revision_output_tokens | revision_reasoning_tokens | initial_charge_usd | revision_charge_usd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| development-0-retailer | development | 4 | True | True | 9603 | 9589 | 5226 | 5212 | 0.0440385 | 0.0243592 |
| development-0-wholesaler | development | 9 | True | True | 3291 | 3277 | 6016 | 6002 | 0.0159165 | 0.0273322 |
| development-0-distributor | development | 18 | True | True | 4706 | 4692 | 3607 | 3593 | 0.0227693 | 0.0166314 |
| development-0-factory | development | 27 | True | True | 10879 | 10865 | 6615 | 6601 | 0.0510203 | 0.0302943 |
| development-1-retailer | development | 7 | True | True | 3768 | 3754 | 2239 | 2225 | 0.017946 | 0.0110828 |
| development-1-wholesaler | development | 14 | True | True | 4131 | 4117 | 788 | 774 | 0.019974 | 0.00408375 |
| development-1-distributor | development | 23 | True | True | 4605 | 4591 | 2803 | 2789 | 0.0225893 | 0.0129423 |
| development-1-factory | development | 30 | True | True | 3914 | 3900 | 1117 | 1103 | 0.0198383 | 0.0053682 |
| holdout-0-retailer | holdout | 4 | True | True | 3592 | 3578 | 2739 | 2725 | 0.016989 | 0.0131678 |
| holdout-0-wholesaler | holdout | 9 | True | True | 12289 | 12275 | 6228 | 6214 | 0.0564075 | 0.0282862 |
| holdout-0-distributor | holdout | 18 | True | True | 7164 | 7150 | 4114 | 4100 | 0.0338302 | 0.0189129 |
| holdout-0-factory | holdout | 27 | True | False | 7068 | 7054 | 8192 | 8192 | 0.0338707 | 0.0373908 |
| holdout-1-retailer | holdout | 7 | True | True | 2486 | 2472 | 1810 | 1796 | 0.012177 | 0.00915225 |
| holdout-1-wholesaler | holdout | 14 | True | False | 5411 | 5397 | 8192 | 8192 | 0.025734 | 0.0374017 |
| holdout-1-distributor | holdout | 23 | True | True | 775 | 761 | 7901 | 7887 | 0.00535425 | 0.0358833 |
| holdout-1-factory | holdout | 30 | True | True | 523 | 509 | 923 | 909 | 0.00457875 | 0.0044952 |

## Student profiles

| id | label | status | background | description |
| --- | --- | --- | --- | --- |
| methodical_calm | Methodical, emotionally steady | Fictional experimental profile; not measured from UB students | Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training. | In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision. |
| methodical_concerned | Methodical, uncertainty-sensitive | Fictional experimental profile; not measured from UB students | Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training. | In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision. |
| flexible_calm | Flexible, emotionally steady | Fictional experimental profile; not measured from UB students | Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training. | In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision. |
| flexible_concerned | Flexible, uncertainty-sensitive | Fictional experimental profile; not measured from UB students | Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training. | In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision. |

Profiles cross an organized/methodical versus flexible/informal tendency with emotionally steady versus uncertainty-sensitive framing. These are explicit fictional personality prompts, not psychometric scores or instructions to exhibit a bias. See reports/revised_design_20261011/REPORT.md for the primary literature and the limits of this adaptation.

## Original structural beta: exploratory identification check

No observations available.

The original dynamic beta fit is retained with its original identification checks. Unusable numerical values do not measure supply-line neglect. The H1_sensitivity assay above is a revised operationalization of the mechanism, not a relabeling of these coefficients.

## Primary API documentation

[Reasoning output limits](https://developers.openai.com/api/docs/guides/reasoning), [model and pricing](https://developers.openai.com/api/docs/models/gpt-5.4-mini), [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).
