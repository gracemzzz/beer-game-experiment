# 1. Study design

**Status: proposed human protocol, not a preregistration or a completed experiment.**

## What is being tested

The core experiment asks whether an actual deadline changes students' use of outstanding replenishment orders and their chain's performance, and whether causal education changes those effects. Four different humans operate each chain. No student plays multiple roles or switches treatment during the main game.

Recruit adult undergraduate business students, recording year of study and previous Beer Game/operations experience. If second-year students are the target population, restrict eligibility prospectively. A convenience sample from one university supports conclusions about that recruited population, not all students or managers.

## Four conditions, randomized by whole chain

| Code | Time indicator P | Education indicator E | Condition |
|---|---:|---:|---|
| A | 0 | 0 | Adequate decision time + control lecture |
| B | 1 | 0 | Binding decision time + control lecture |
| D | 0 | 1 | Adequate decision time + causal education |
| C | 1 | 1 | Binding decision time + causal education |

The letters preserve the AI study's A/B/C meanings; D is the new condition. The mathematical cell order is always **A, B, D, C = 00, 10, 01, 11**.

One randomization block contains four chains, one randomly assigned to each condition. All four use the same hidden customer-demand sequence. Different blocks use independently generated sequences. Match the session and recruitment stratum within blocks where practical. Use a reproducible allocation seed, concealed until assignment. Randomize the four roles within each chain. Keep lectures private and forbid inter-chain discussion during decisions. Do not assign one entire class to each condition, which would confound class with treatment.

With k blocks there are **k chains per condition, 4k chains total and 16k different people**. A chain is the randomization unit; its four participants and forty weeks are dependent measurements. All four conditions must be run in the same prospective experiment for a clean education-by-pressure interaction. Comparing unrelated historical studies does not identify H6.

## Hypotheses and exact tests

The presentation supplies the latest H1–H4. The saved reflection supplies H5/H6; see [source mapping](05_LITERATURE.md). Definitions of G, C, V, BW and R are in [document 2](02_MEASUREMENT_MODEL.md).

| Hypothesis | Plain-language outcome | Prespecified contrast | Predicted sign |
|---|---|---|---|
| H1 | Stock-versus-pipeline response gap G | G(B) − G(A) | Positive |
| H2 | Whole-chain cumulative holding + backlog cost C | C(B) − C(A) | Positive |
| H3 | The same underweighting gap G | G(C) − G(B) | Negative |
| H4a | Average participant weekly order variance V | V(C) − V(B) | Negative |
| H4b | Average order variance / external demand variance BW | BW(C) − BW(B) | Negative |
| H5 | Persistence R with an adopted rule after its consequences change | R(pressure) − R(adequate), in the separate educated cohort | Positive |
| H6a | Education effect on G differs by time condition | [G(C) − G(B)] − [G(D) − G(A)] | Two-sided; no sign specified in source |
| H6b | Education effect on cost differs by time condition | [C(C) − C(B)] − [C(D) − C(A)] | Two-sided; no sign specified in source |

Use eight two-sided tests and Holm adjustment across this family. A directional hypothesis requires the estimated sign as well as statistical evidence. H4a and H4b are related measurements, not independent replications. H6a/H6b are two distinct outcomes; report them separately rather than claiming both from one significant test. Other coefficients, role differences and questionnaires are explanatory diagnostics.

## Core session

1. Consent, pseudonymous participant ID, eligibility and baseline experience. Complete any baseline cognition questionnaire before treatment if retained; do not make it a new exclusion rule after seeing results.
2. Identical rules, a comprehension check and four unscored practice rounds. Correct misunderstandings before randomization; use the same procedure for everyone.
3. Concealed chain allocation. Deliver a standardized 20-minute causal lecture or 20-minute control lecture, using the same format, instructor exposure and engagement questions. Education covers delay, accumulation and propagation, with causal diagrams; control covers business record organization and terminology. Both receive essential game rules. Neither gets a recommended order, inventory target or a worked policy solution. Exact scripts need to be written and frozen before the human pilot.
4. Forty scored Beer Game weeks. Each role receives the same screen layout and operational information, with only the allotted decision time differing. Orders are simultaneous within a week and hidden until all decisions are locked. Python/server code computes inventory, shipments and costs.
5. Thirty-two individually presented randomized stock-allocation decisions, under the assigned time allowance, to estimate the response gap. No correctness feedback or jointly displayed paired answers. This is a separate measurement task after the game, so it cannot train main-game behavior.
6. Post-task pressure ratings, education comprehension and a short written explanation of how orders were chosen. These support interpretation; education-quiz failure is not a post-randomization exclusion criterion. Debrief after all tasks.

**Information sharing is held constant:** own stock, backlog, receipts, incoming demand, outstanding order ledger and history; current stock/backlog and past orders for all four roles; past/current realized retail demand and its known distribution. Show the same cutoff of history to all arms, never future realized demand or other participants' current uncommitted orders. Specify this scope in the platform; it is broader than sharing inventory alone in Croson and Donohue (2006).

Proposed game settings: four roles; 40 scored weeks; integer customer demand Uniform{0,…,8}; starting on-hand stock 12 per role and no backlog; initial orders/shipments 4; information delay one week, shipment transit two weeks, factory production three weeks; holding cost 0.50 and backlog cost 1.00 per unit-week. These are **new design choices**, not a claim to reproduce Donohue's delays. Equations and initial outstanding queues are specified in document 2. Use no low artificial order cap. Any technical integer bound must be fixed, documented and monitored as a censoring boundary.

Forty weeks improves decision-rule estimation compared with the AI run's 24 weeks; it does not create forty independent participants. Include every scored week in cost/variance. Do not search for a favorable burn-in window. Explain the fixed ending and possible end effects; report first/last-block patterns as diagnostics, without substituting endpoints.

## Calibrate real human time pressure

Start with the proposed **16-person/four-chain pilot**, kept out of main analyses. It estimates usability and response-time distributions, not a precise human treatment effect or ICC. Record time from fully rendered state to final committed entry, and separately record client/server/network delays.

After ordinary untimed decisions, compare candidate deadlines near the human response-time 25th and 95th percentiles and twice the latter. Counterbalance task order and use new states. Choose fixed arm-level limits, not personalized outcome-dependent deadlines. Examine roles, early/late play, positive inventory and backlog separately. Suggested **design criteria**, to be frozen before the pilot: pressure produces clearly higher rushed ratings and compressed response times while at least 90% of choices remain explicit valid entries; adequate time permits at least 95% timely completion and shows little further response-time/quality benefit versus doubled time. These thresholds are engineering criteria, not published constants. If they conflict, change and repilot the task under a documented design revision; do not select time limits using H1–H6 significance.

AI scenario values of 8 and 120 seconds are **not validated human deadlines**. No numeric human deadline is frozen here. If estimating variance/ICC is too uncertain with 16 people, add a separately planned estimation pilot before main recruitment. No repeated significance testing is needed to calibrate usability.

Keep the interval between weekly state releases the same across arms, using the adequate-arm allowance plus a fixed transition interval. After an early lock, hide the current state and do not reveal the next state. This avoids confounding a short decision window with a faster release of supply-chain feedback. Participants may still think about past events; the treatment restricts time to act on the new state, not all mental activity. Pilot the full session duration: lectures, practice, 40 game intervals, 32 measurement intervals and questionnaires must fit the advertised session.

For continuity during a missed game deadline, a proposed interface can execute a **standing order explicitly chosen by that human before the game**. Save it as `human_standing`, never as a fresh timed decision. Keep its realized costs in intention-to-treat chain outcomes; omit it from regressions of fresh decisions and report the missingness/selection limitation. The static measurement task has no standing order: an unanswered item stays missing. This rule needs pilot review and must be identical across arms; do not silently implement it in the old AI study.

## H5: a separate routine-transfer experiment

H5 requires an adopted rule, a change that makes it less appropriate, and observations after that change. Merely comparing pipeline weights after a lecture does not test persistence.

Use **new participants**, all receiving the same causal education, in an individual stock-allocation task. This avoids teaching a rule to the main sample before H1–H4, and avoids selecting people based on responses already affected by the pressure treatment.

1. Under common adequate time, complete 32 acquisition trials with feedback. All previously ordered stock arrives before one final demand/scoring point. The old cost-minimizing rule is to cover demand after subtracting on-hand and both pipeline quantities.
2. A prospectively defined adoption check uses the final eight acquisition trials: at least six orders within one unit of the old benchmark. The pilot must assess whether this reliably indicates rule acquisition. Record all non-adopters, but do **not randomize them** into the confirmatory H5 sample. This restricts the target to educated participants who acquired this routine; it is not an inference about all students.
3. Randomize eligible participants to binding or adequate time, stratified by acquisition score. This assignment occurs **after** the adoption check.
4. Explain that one marked shipment now arrives **after** the task's last demand/scoring point. Keep demand, prices and all other rules unchanged. Check understanding with unlimited time before transfer decisions; record retraining attempts without dropping randomized participants.
5. Give 16 transfer trials without correctness feedback. The first eight are primary persistence measurements; the next eight show adaptation over repeated exposure. Both time arms see the same balanced scenarios in randomized order.

This is an explicit, narrow operationalization of H5 in a supply-chain decision task. It is not a changed-regime four-person Beer Game. If H5 must instead refer to persistence inside the full chain, a separate dynamic regime-change protocol is needed; a lead-time change alone does not imply that total outstanding-stock weight should decline.

## Analysis and stopping

For the core study compute one chain summary per outcome, then one contrast per complete randomization block. Report mean contrasts, 95% confidence intervals, unadjusted and Holm-adjusted p-values. The primary working analysis is a one-sample t-test on independent block contrasts; show randomization-based/sensitivity analyses if distributions are strongly skewed. For H5 use a two-sample comparison of each person's first-eight-trial mean persistence. Never count trials as independent participants.

The supplied power calculations correspond to these contrasts under stated normal/variance assumptions. Skewed chain costs, heterogeneous slopes and missingness require pilot-based simulation before freezing recruitment. Select sample size once from meaningful effects and pilot uncertainty; stop at the registered allocation target, not at p < .05. Preserve all randomized participants and incomplete chains in the flow report. Specify an intention-to-treat missing-data analysis before collection; complete-case analysis alone is insufficient if pressure changes completion.

Set compensation, platform details, final lecture content and institutional human-research approval before recruitment. This folder is the quantitative design package, not authorization to run the study.
