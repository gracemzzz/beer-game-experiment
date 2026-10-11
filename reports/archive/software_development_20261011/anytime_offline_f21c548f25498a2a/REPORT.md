# SYNTHETIC SOFTWARE CHECK — no model or human observations

Run `anytime_offline_f21c548f25498a2a`. Protocol `student-high-anytime-revision-v2`. Status: **stopped**. Reason: Interrupted or software error: AttributeError API charges/reservations for this run: **$0.000000**.

## What this experiment tests

A hypothetical second-year UB business student makes an initial current-week choice at fixed high effort. The short condition submits that choice. The adequate condition receives one additional high-effort revision opportunity. Initial generation has a 16,384-token ceiling; the extra opportunity has an 8,192-token ceiling. This is an additional-deliberation intervention, not a single-call total-budget intervention or a validated human deadline. Information quantity is held constant; information overload is not separately randomized. The central persona is identical across roles and is an assumption. No human data exist.

Only valid same-week model submissions become orders. An unfinished token-limited revision leaves the initial submission in force. An initial failure or technical error stops the run. Zero and large orders remain outcomes; no interior-order target is imposed.

## Manipulation checks

Held-out and development feasibility screen passed: **False**. Main-game median short/adequate total-token ratio: **None**; required ≤0.75. Main-game separation passed: **False**. These are small-sample computational checks, not population validation. Both phases count toward computation. No games are purchased after a failed live feasibility screen.

No observations available.

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

Customer demand is prospectively generated in balanced shuffled blocks of 4, 6, 10 and 12 after four practice weeks. Each paired block receives the same exogenous sequence, hidden from participants. This preserves variation in the measurement window. A local ratio with constant local demand remains undefined. Twelve automatic weeks repeat each role's final submitted quantity and the final customer demand; this differs from the historical demand-following tail and is not behavioral data.

## Cost controls and reproducibility

Identical paired initial prompts share one paid draw; repeated independent replications never share draws. Exact completed request checkpoints are reused on resume. Stable instructions occur first for provider prompt caching; actual cached-input usage is recorded and output/reasoning charges remain payable. Temperature is omitted in all calls. No correctness retry or automatic switch to a more expensive model is used. The $10 campaign includes the previous $5.19360675; new campaign identifiers require new explicit budget authorization.

Saved-evidence audit: **{'passed': True, 'physical_states_replayed': 0, 'request_records': 0, 'selected_orders_verified': 0}**. Exact requests, responses, chosen-source request IDs, code snapshots, demand paths and configuration are retained under the source data directory. Analysis makes no API calls.

## Limitations and next decision

A completed pilot establishes operation and, if the checks pass, a measured extra-computation contrast. It does not establish that an LLM is a real UB student, that information overload was manipulated, or that extra computation must improve decisions. Keep null or opposite-direction outcomes. Determine a meaningful chain-level effect and power before a larger study. Human comparison materials are available in docs/STUDENT_VALIDATION_20261011.md.

## Calibration observations

No observations available.

## Primary API documentation

[Reasoning output limits](https://developers.openai.com/api/docs/guides/reasoning), [model and pricing](https://developers.openai.com/api/docs/models/gpt-5.4-mini), [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).
