# Experiment 14: carry-forward timeout policy, version 2

1. The user selected repeat-the-previous-order continuation after a true game timeout. This is a new prospective scientific version. The original 16 strict-deadline development cases, their prompts, source snapshots, failures and publications remain unchanged and outside this sample.
2. The bounded next step is **one matched development block: three fresh contexts, A/B/C, 24 weeks each**, followed by the unchanged eight probe pages and four untimed comprehension items. No provider API calls are authorized or required. There is no main launch until the endpoint and provenance gate below passes and a separate main plan is frozen.
3. Timely valid model orders remain unchanged. A timed-out game packet receives a labelled synthetic action; a timed-out probe page receives missing values, never synthetic answers. Thus game continuation can recover full-horizon policy outcomes without recovering every hypothesis measurement.

## Design and fixed materials

Use requested model `gpt-6-astra`, effort `xhigh`, with one four-role chain per fresh isolated local context. A uses the unchanged 170-word CONTROL reading with adequate deadlines; B uses CONTROL with restricted deadlines; C uses the unchanged 170-word EDUCATION reading with the same restricted deadlines. All arms use [the new common participant prompt](../prompts/carry_forward_v2/STUDENT.md), preserving the original V1 classroom framing and objectives while publishing the timeout consequences. Neither reading, the 32-scenario probe bank, the four-question quiz, nor the physical game rules changes.

| Phase | A | B | C |
|---|---:|---:|---:|
| Each game week | 30.0 seconds | 4.0 seconds | 4.0 seconds |
| Each four-scenario probe page | 30.0 seconds | 3.8 seconds | 3.8 seconds |
| Post-task comprehension | Untimed | Untimed | Untimed |

These are the already recorded V1 numerical limits, fixed before this new development block; they are not recalibrated from its outcomes. Complete payload receipt at or before the deadline is admissible. Time strictly beyond the deadline is late. The clock includes display, tool, service, transport and scheduling time; it does not expose hidden reasoning time or establish subjective student pressure. Requested and reported model/effort identifiers must be recorded separately. Temperature and reasoning-token limits remain unavailable.

Before the first new display, freeze the new controller, transport, preparation, extraction and gate implementations, this protocol, exact prompt bytes, unchanged readings/fixtures, and their hashes. The single development block is `cf2_d001`, stage `development`, with common demand/persona seed **1420001** and launch order **A, C, B**, generated prospectively by `random.Random('exp14-carry-v2-d001').shuffle(list('ABC'))`. Store its cases under `data/carry_forward_v2/development/cf2_d001_{a,b,c}`. Verify that its seed is disjoint from all earlier development and planned main seeds. Match demand and persona-to-role assignments across its three arms. Freeze these values in the development manifest before preparing any case; never select a seed or order from resulting costs, orders or hypothesis contrasts. Retain exact combined prompts and isolated-context launch records. Do not expose the seed, other arms, private pair labels, scoring keys or future realized demand to the actor.

The held-out target remains ten matched blocks, ten fresh chains per arm and 24 scored weeks. Roles and weeks are repeated measurements, not independent students: the planned independent sample is ten block contrasts, not forty roles or 960 weekly orders per arm. A single context controlling four fictional students can coordinate their behavior; this is not evidence from actual University at Buffalo students. Local agents use the account allowance; no provider keys, direct provider requests or shared API-ledger changes belong to this work.

## Timeout and packet contract

Each game week requests one atomic packet of four literal nonnegative integer orders, in the displayed role order. Valid zero, repeated, identical and extreme admissible orders are retained. There is one opportunity, no revisions, no generated policy/optimizer and no precomputed future-week orders. Each choice follows its current complete public display.

If no complete valid game packet is admitted by the deadline, expire that opportunity. Record all four current model decisions as missing. For each role, apply its own **previous applied order**, including an earlier carry-forward action; use **4** when no earlier applied order exists in week 1. The same deterministic rule applies to A, B and C. Record the applied source as `carry_forward`, explicitly synthetic. A valid packet received on time uses its exact orders with source `model_on_time`; proximity to the deadline never triggers changes or noise. No random fallback is used.

The receipt deadline closes the opportunity even if expiry is persisted only on the next controller access. Any late literal payload is retained as rejected evidence and cannot replace the applied action. A partial packet cannot supply some roles while the others fall back. Subsequent public history describes the actual applied orders. After a timeout acknowledgment, the actor reads the next public display and chooses for that newly displayed state. It cannot reuse a rejected late answer as an answer to a different state or backfill an expired week.

For a timed-out probe page, record its four answers as missing and advance to the next page. Do not repeat earlier probe answers, use game orders, infer answers from the reading, or ask for a late replacement. The fixed scenario order, eight pages and pair identities remain unchanged. After the eight pages, administer the original untimed comprehension questions without answer feedback or coaching.

Invalid on-time payloads, stale/duplicate decision IDs, incomplete displays, unavailable required tools, clock discontinuities or other procedure errors require the actor to stop and report a procedure failure. A rejected on-time submission does not itself reset the clock, advance the state, trigger fallback or permit a repair/retry; the transport may retain its open opportunity in the saved record. Only true expiry triggers the timeout policy, and a later expiry cannot erase or reclassify an earlier procedure failure. A normal acknowledgment of carry-forward or probe missingness is a continuation event, not a terminal procedure error. Preserve every attempted case and accepted prefix, including a failed preparation or launch. Never replace a failure with a favorable case or silently add another development block.

## Endpoints and interpretation

The original five endpoint definitions and matched contrasts are retained, with an explicit change to the interpretation of game outcomes:

| Endpoint | Fixed calculation | Interpretation under this policy |
|---|---|---|
| H1 | Equal-weight mean of all eight fixed pipeline-pair slopes, `(q_lowP - q_highP) / (P_high - P_low)`; B minus A | Actual timely probe responses only. Any missing required pair makes the aggregate unavailable. |
| H2 | Total holding plus backlog cost across four roles and all 24 weeks; B minus A | Outcome of **the model plus the fallback policy**. Requires a complete applied trajectory. |
| H3 | The same eight-pair pipeline-response mean; C minus B | Actual timely probe responses only, with the same complete-pair requirement. |
| H4a | Sample variance of 24 applied weekly orders for each role, denominator 23, then mean across four roles; C minus B | Fluctuation of **the model plus the fallback policy**, including every synthetic action. |
| H4b | Each role's applied-order variance divided by the chain's sample external final-customer-demand variance, then mean across roles; C minus B | Bullwhip of **the model plus the fallback policy**. Zero demand variance remains undefined. |

Repeat-last actions can mechanically reduce order variance. They also change later states and costs. Consequently H2/H4 cannot be attributed solely to student or LLM ordering behavior, even if the rule is common across arms. The estimand includes treatment-dependent frequency of software intervention. There is no claim that this rule emulates rushed human students. Future effects after week 24 remain unmeasured.

Report actual on-time model orders separately: counts, fraction, zero fraction, range, role/week coverage and observed choices, together with timeout rates and synthetic-action shares by role and arm. A descriptive variance among observed on-time orders, if shown, must be labelled as a selected incomplete subset with its count and covered weeks. It is not a complete-horizon actor-only variance, an H4 replacement or an estimate of unobserved choices. Do not drop synthetic weeks and present the remainder as a full behavioral trajectory. Do not replay earlier choices under a different policy as validated counterfactual model decisions, because the later displayed states would change.

Preserve the original pair-level and backlog-response diagnostics. A missing member leaves its pair slope unavailable. Report observed pair slopes descriptively, but do not skip missing pairs, change aggregate weights, redefine H1/H3, or fill their responses to obtain an endpoint or significance. Game completion, full probe completion, required pipeline-pair completion and comprehension completion are separate fields. A completed game alone does not pass the all-endpoint gate.

## Bounded development and main gate

Run exactly the three planned full-length development contexts after software checks and the prospective freeze. Audit literal-choice provenance, full public displays, deadline admission, atomic packets, correct previous-applied fallback, probe missingness and exact physical replay. Record requested/reported settings and transcript attribution. Record all deviations, incomplete endpoints and failure reasons. Report development results descriptively; do not compute or select by main H1-H4 p-values.

The new all-endpoint operational gate requires all three planned cases to finish 24 applied game weeks, all eight probe pages with actual valid on-time answers, and all four untimed quiz items; no unresolved source, timing, display, provenance or replay failures; and at least 3/4 correct C quiz answers, preserving the original 75% education-comprehension requirement. Game carry-forward is allowed by this gate if correctly recorded. Probe page progression with missing answers does not satisfy probe completion. Quiz scores do not exclude any future main case. Software tests using artificial actors or clocks are labelled synthetic and never counted as participant observations.

Passing this one-block check would show that the revised mechanism and fixed measurements worked in that bounded block; it would not establish the main completion rate, statistical power, human validity or a desired effect. H2/H4 may be complete while H1/H3 remain missing. If that happens, retain and report the mixed status and keep the all-H1-H4 main study blocked. No automatic extra pilots, deadline extensions or modified probe pages are authorized by a failed gate. A scientific change requires another prospective version.

Only after an affirmative documented gate and a separate frozen main plan may main preparation become eligible. That plan must preserve ten matched blocks, separate held-out seeds, one context per arm/block, fixed 24-week scoring, the same endpoint definitions, all assigned failures and fixed stopping. Freeze sources, materials, seed allocation and randomized launch order. Do not create a main qualification record merely because games can now continue.

If main collection becomes eligible, use matched block contrasts and two-sided paired randomization inference where the assignment supports it; otherwise state the independent symmetric/exchangeable paired-null assumption for sign flips. Use the original Holm family of five endpoints, retain null and opposite effects and report uncertainty. No roles/weeks-as-independent tests or significance-based extension are permitted. Any missing planned primary endpoint must retain its missing status; it cannot silently shrink the multiplicity family or become a complete-case primary claim. With incomplete assigned blocks, report the endpoint/missingness pattern and distinguish any descriptive observed contrast from an all-assigned causal estimate.

## Evidence to retain

For every opportunity retain its immutable decision ID, complete public display/hash, phase/week/page, opening and receipt clocks, deadline, exact literal response including rejected late submissions, admission/rejection reason, actual model choices or missingness, applied game action, per-role source and initialization reference. Keep actual and applied orders distinguishable. Retain chained events, exact source/material fingerprints, result/replay receipts and public tool transcripts with an attributed procedure review. A controller receipt or operator review is local execution evidence, not provider authentication or a hidden reasoning trace.

Preserve all prior publications and source snapshots; store this version's development records separately. Update the experiment's current README/report navigation to explain both the original failed strict-deadline development and this new policy's results. The experiment README remains the entry point for reports, figures, tables and the notebook.

## Possible later probe-completion revisions; none selected here

- A separately calibrated longer probe deadline could improve observed completion, while changing the restriction imposed during measurement.
- A common untimed post-game assay could assess responsiveness following the timed game/reading, while removing the current immediate probe-deadline contrast.
- One scenario per page or a shorter validated public display could reduce packet demands, while changing presentation and opportunity structure.

Each option requires new fixed materials, an explicit estimand, a finite prospective feasibility plan and a new fingerprint before use. None licenses fabricated answers, selective pair retention or a significance-driven choice. The current development block keeps the original probe bank, four-scenario pages and fixed numerical limits.
