# Experiment 14: fictional student time-pressure framing, version 3

1. The user clarified that the intended treatment is a student's fictional classroom time pressure, with **no actual model response deadline**. This new protocol supersedes the unrun carry-forward proposal before its freeze or participant collection. Preserve that proposal, its draft history and software checks as unused development; preserve all 16 original strict-deadline cases and publications unchanged. Neither supplies observations for this study.
2. Request `gpt-6-astra`, effort `xhigh`, in fresh isolated local contexts. All conditions have the same unrestricted actual response opportunity and require literal model answers. There is no timeout, software fallback, answer imputation, random-response generator or resampling.
3. Develop once in one matched A/B/C block, then permit the separately frozen ten-block main study only if the completion, comprehension and provenance gate passes. Selection, stopping and reporting never depend on hypothesis signs or p-values.

## Conditions and meaning of the treatment

| Arm | Fictional allowance for each student's decision | Assigned reading | Actual model response limit |
|---|---:|---|---|
| A | 120 seconds | Unchanged CONTROL, 170 words | None |
| B | 8 seconds | Unchanged CONTROL, 170 words | None |
| C | 8 seconds | Unchanged EDUCATION, 170 words | None |

The assigned allowance applies to the fictional student's decisions in gameplay and the hypothetical assay. Readings and the post-task quiz are untimed. Use a common [student prompt](../prompts/student_framing_v3/STUDENT.md) and matched allowance texts [ADEQUATE](../prompts/student_framing_v3/ADEQUATE.md) / [PRESSURE](../prompts/student_framing_v3/PRESSURE.md), whose only textual difference is 120 versus 8. Append only the assigned unchanged reading. The common instruction asks the model to portray an ordinary novice's decisions in that fictional situation rather than solve the task as an expert. It does not direct neglect of a state variable, greater noise, panic, a particular ordering rule or a desired hypothesis direction. The ordinary second-year University at Buffalo profiles remain stable and fictional.

Both numbers describe a human classroom scenario, not an enforced clock on the model. The actual model, requested effort, information displays, submission opportunities and tool access are identical across arms. The controller must expose no active response deadline and must never close an opportunity because time elapsed. Service or tool failure remains a technical failure, not a treatment timeout. Record elapsed wall time only as an operational diagnostic; do not interpret it as human time pressure or hidden reasoning time. Temperature and reasoning-token allocation are not exposed and must not be invented.

This design estimates how the model's portrayal changes with fictional time framing and education. It cannot establish effects on real students, subjective pressure, binding model computation or human cognition. The one-context/four-role arrangement can coordinate choices despite the local-information instruction; it does not create four autonomous respondents.

## Cases, exposure and fixed stopping

Use one fresh isolated context for one four-role chain, matching demand path and persona-to-role assignments within each A/B/C block. Never expose another arm's decisions, reading or private analysis. Score 24 game weeks, then 32 fixed hypothetical scenarios in eight pages of four, then the original four untimed comprehension items. A participant supplies 96 game orders, 32 probe choices and four quiz answers. A complete main arm has ten independent contexts, 960 game orders, 320 probe choices and 40 quiz answers. The main independent sample is **ten matched block contrasts**, not forty students, 960 independent weeks/orders or repeated probe questions.

The single development block is `sf3_d001`, seed **1440001**, with prospective launch order **B, C, A**, generated using `random.Random('exp14-student-framing-v3-d001')` to shuffle A/B/C. Verify its seed is disjoint from prior development and all main seeds. The held-out main blocks are **c3m001 through c3m010**, with seeds **1450001 through 1450010**, respectively. Freeze these cases and the within-block randomized main launch orders before their collection. The ten assigned main blocks are a fixed maximum; no replacement, extra block or restart is allowed because of failure, low quiz scores, null results or an unfavorable effect. Development never enters main inference.

Before development, freeze the new controller, transport, preparation, extraction and gate code; this protocol; all four new prompt-folder files; the unchanged reading/probe/quiz fixture bytes; numeric fictional allowances; settings, seed allocation and launch order; and exact source/material fingerprints. Each case saves its exact combined participant prompt and requested/reported model and effort labels. A separate main plan may be frozen only after the development gate passes. No direct provider API requests or keys belong to this work; the shared API ledger and cumulative cap remain unchanged. Local contexts use the account's agent allowance.

## Decision and measurement contract

The physical accounting, initial conditions, inventory/backlog costs, delivery delays and public information remain unchanged. Python advances states and costs only. The actor reads each complete current display, chooses the literal orders itself and submits once. A game packet contains exactly four nonnegative integer orders in role order; a probe packet contains one such order for each of the four displayed IDs. There is no revision pass, policy/optimizer code, future-order loop or precomputation. Zero, repeated, constant, identical and extreme admissible choices remain valid. Never force positivity, a preferred maximum, variability or diversity.

Every presented game/probe item requires an actual submitted choice. The fictional 8-second allowance cannot justify a blank answer, fabricated expiry or default. An opportunity remains open until its actual submission or a recorded technical/procedure failure. Invalid/stale submissions, incomplete displays or unavailable tools require stopping and reporting the failure; never repair choices, silently resample, create synthetic answers or alter the recorded prefix. Ordinary execution delays do not stop a case or change its scientific condition.

Describe gameplay as continuing, without revealing a known optimization endpoint. Holding cost is 0.5 per remaining case per week; backlog cost is 1 per unfilled case per week. Report separate cost components and final inventory, backlog and commitments. Effects beyond week 24 remain unmeasured.

Use the unchanged scenario bank, fixed mixed order and display allowlists from the [original prompt contract](../prompts/README.md). Private pair labels, dimensions, quiz answers and reasons are never displayed. Pipeline pairs vary outstanding quantity while retaining relative arrival timing; backlog pairs retain outstanding quantity and timing. The hypothetical arrival schedule is known, unlike uncertain supplier fulfillment in gameplay, limiting generalization. No probe has a normative or required order.

| Primary endpoint | Fixed calculation | Matched contrast; original prediction |
|---|---|---|
| H1 proxy | Equal-weight mean of all eight pipeline-pair slopes, `(q_lowP - q_highP) / (P_high - P_low)` | B minus A; negative |
| H2 | Sum of holding and backlog costs across four roles and all 24 weeks | B minus A; positive |
| H3 proxy | The same eight-pair pipeline-response mean | C minus B; positive |
| H4a | Sample variance of 24 actual weekly orders for each role, denominator 23, then arithmetic mean across four roles | C minus B; negative |
| H4b | Each role's sample order variance divided by its chain's sample external final-consumer-demand variance, then arithmetic mean across roles | C minus B; negative |

All five endpoints derive from actual model decisions under fictional framing, not software fallback. H1/H3 measure a responsiveness proxy, not an independently identified optimal weight or verified normative underweighting. H4a/H4b share order variance and are not independent replications. A zero demand-variance denominator is undefined. Do not substitute upstream incoming orders for final-consumer demand in the denominator.

Report each block, role/pair summaries, zero fractions, ranges/extremes and the eight backlog-response slopes `(q_highB - q_lowB) / (B_high - B_low)`. Backlog responsiveness is a comparison diagnostic, not an assumption that education cannot affect it. Do not choose new subgroups, nonlinear specifications or weights after viewing outcomes. A missing required probe member caused by a genuine technical failure leaves that pair and the fixed eight-pair aggregate unavailable; an incomplete game has no full-horizon H2/H4 estimate. Preserve incomplete records and failure reasons rather than manufacture responses or silently change denominators.

## Comprehension, recall and main-readiness gate

Administer the unchanged four-question quiz only after all behavioral choices, untimed and without answer feedback or correct-answer coaching. After the quiz is submitted and the controller confirms completion, request the actor's final disclosure field `fictional_student_seconds`: the stated number of seconds per fictional student's game/scenario decision. Collect this outside the four-item quiz as an instruction-recall diagnostic, scored against the frozen arm assignment. It does not enter an endpoint or the main-readiness gate. A correct recall confirms recall of the instruction, not subjective human pressure; absent/incorrect recall is reported without imputing an answer or replacing a case.

The **one-block development gate** requires each of the three planned cases to complete all 24 game weeks with 96 actual submitted orders, all 32 probes with actual submitted answers, and all four quiz items. Require clean full-display/literal-choice review, requested/reported-setting records, no unresolved source/procedure/provenance failure, and exact replay of accepted orders and physical states. C must answer at least **3/4 quiz items correctly (75%)**, retaining the original education-comprehension requirement. No order value, hypothesis slope, cost, variance, sign or p-value determines qualification. Synthetic software tests never count as participant cases.

If any requirement fails, preserve all three planned attempts and keep main blocked; no automatic additional pilot, prompt variant or threshold relaxation follows. Passing one development block establishes only that these operational requirements were met once, not statistical power, human validity, stable future completion or a guaranteed effect. After a passing gate and separate main freeze, collect all ten assigned main blocks. Main quiz scores and recall are diagnostics only: retain low-scoring cases and never exclude or replace them.

## Inference and preservation

Use ten matched independent block contrasts with two-sided tests and Holm correction over the original five primary endpoints. Use the randomization distribution actually supported by the assignment; where that is unavailable, state the independent symmetric/exchangeable paired-null assumption of sign-flip inference. Report estimates, uncertainty, all block values, failures and null/opposite effects. Ten nonzero independent pairs allow a minimum two-sided sign-flip p-value of 2/1024; this is resolution, not promised power. Do not treat roles/weeks as independent samples or continue until significance. No p-value-driven prompt selection or secondary endpoint substitution is allowed.

If a main technical failure makes a planned primary endpoint unavailable, report it honestly, retain the assigned block and fixed five-endpoint family, and distinguish any descriptive observed contrasts from an all-assigned causal estimate. Do not call a selected complete-case result a complete ten-block study.

Preserve immutable decision IDs, full public displays and hashes, exact literal submissions, admission records, timestamps, requested/reported settings, actual choices, public tool transcripts, attributed procedure reviews, replay receipts and source/material fingerprints. Local execution receipts are not provider authentication or hidden reasoning traces. Preserve old studies, unused proposals and publications byte-for-byte. Keep this version's data separate, and update the experiment README as the entry point to its reports, figures, tables and notebook. Reports must label the treatment **fictional student time-pressure framing**, with no claim of an actual model response restriction.
