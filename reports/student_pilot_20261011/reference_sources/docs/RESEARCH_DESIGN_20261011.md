# Research design recommendations: student persona and token pressure

Reviewed 11 October 2026. This document records methodological recommendations and source checks for the new protocol. It does not change historical results or certify the new calibration. The new run's saved configuration, calibration outputs and report are authoritative for what was actually implemented and executed.

## Implemented feasibility protocol

The implemented screen uses 24 fixed hypothetical states at 512, 1,024, 2,048, 4,096, 8,192 and a 16,384-token reference, all with fixed high effort and the pinned GPT-5.4 Mini snapshot. The model is not told its cap. The exact repeated question is: "How many cases do you order this week? Return the integer in the order field." One strict structured call returns the order; there is no second reasoning opportunity.

Cap selection requires a complete matched bank, at least 95% observed valid decisions at both selected caps, recorded positive reasoning usage for valid calibration answers, at least 25% separation in median actual total generated tokens, and a reference without frequent near-cap responses. Usage comparisons include incomplete calls. These small-sample engineering screens are not established psychometric thresholds or guarantees for long histories. No order, game cost or bullwhip result determines caps.

If the screen fails, the prospective diagnostic pair is 8,192/16,384, fixed before game outcomes. It prioritizes observing complete decisions after smaller caps showed frequent truncation; it is not a certified computational treatment. The original exploratory 2,048/8,192 diagnostic proposal was superseded before any live game decisions. Rule comprehension is checked identically at 8,192 tokens before gameplay; the technical timeout is 180 seconds throughout. Independent pairs are planned from calibration token costs and the remaining campaign allowance before outcomes, with a 15% cost margin. A cost forecast cannot guarantee completion.

The first live calibration attempt stopped after 72 measured responses and an unclassified HTTP 429, with estimated spending of $0.920223. The preserved follow-up recheck also stopped without new measured generation. Credit-restoration recovery and the declared receipt/shipment correction subsequently completed the current 144-observation calibration. Historical failed attempts and excluded old-state charges remain preserved; they are not additional current-bank observations.

## Completed empirical calibration: 11 October 2026

The corrected bank contains 24 matched hypothetical states at each allowance, all using `gpt-5.4-mini-2026-03-17` with fixed `high` effort. The recorded results are:

| Generated-token allowance | Valid complete structured orders | Observed completion | Median actual total generation |
| --- | --- | --- | --- |
| 512 | 0/24 | 0% | 512 tokens |
| 1,024 | 2/24 | 8.3% | 1,024 tokens |
| 2,048 | 5/24 | 20.8% | 2,048 tokens |
| 4,096 | 11/24 | 45.8% | 4,096 tokens |
| 8,192 | 23/24 | 95.8% | 5,057 tokens |
| 16,384 reference | 24/24 | 100% | 4,413 tokens |

The medians use all measured calls at each cap, including incomplete generation. The complete matched-bank and reference checks passed, but the **token-manipulation screen failed**: no candidate pair satisfied the prespecified completion-and-usage criteria. Only the 8,192-token candidate met the observed 95% completion threshold. Its actual median generation also exceeded the 16,384-token reference median, rather than showing a 25% reduction. These observations do not demonstrate a computational contrast between the diagnostic allowances. They do show that the smallest tested caps frequently prevent a structured decision. The 24-state completion rates cannot establish reliability over a whole game or long histories.

The completed calibration ledger is **$2.24484225**, including the preserved **$0.45876525** charged for 38 excluded old-state records and retained historical attempts. The checkpoint duplicates completed evidence without any new API calls, costs or independent observations. See the [completed calibration report](../data/runs/student_api_b609eca42866feb0/calibration_checkpoint/REPORT.md), [exact screen results](../data/runs/student_api_b609eca42866feb0/calibration_checkpoint/calibration_recommendation.json), and [state-level observations](../data/runs/student_api_b609eca42866feb0/calibration_checkpoint/calibration.csv). Exact prompts, returned model, effort and usage are preserved in that checkpoint's request JSON files; [the calibration pointer](../reports/LATEST_CALIBRATION.json) identifies its directory.

## Completed diagnostic pilot: 11 October 2026

The paid pilot completed at **06:58:46 UTC**, with one independently initialized chain per condition, **40 game weeks plus 12 automatic scoring weeks** per chain, and predeclared 8,192/16,384 caps. The [pre-outcome plan](../data/runs/student_api_b609eca42866feb0/selection.json) fixed this pair before outcomes using a $7.65708435 forecast under the remaining original $10 allowance. All [eight factual onboarding checks](../data/runs/student_api_b609eca42866feb0/rules_checks.json) passed. The prospective 20-week option was unused. A week-12 Windows filesystem stop and subsequent operational restart preserved prompts, model, effort, caps and all five scientific source hashes; concurrency/pacing changed commonly from 2 / 2 seconds to 8 / 1 second. [Operational recovery notes](../README.md#windows-filesystem-recovery-on-11-october-2026) preserve this history. No further paid runs were started.

Both chains completed **144 valid model decisions**, with **zero missing decisions, fallbacks or zero orders**. Matched orders were identical between conditions and took values 4 or 8. Each team's total scored cost was **156**, including zero cost in the automatic continuation. The local-demand variance ratio was **1.000 at every role**. Customer-referenced ratios were **1.000 / 1.215278 / 1.416667 / 1.604167** for retailer / wholesaler / distributor / factory. The latter ratios reflect a delayed single step over a finite observation window: local orders exactly matched incoming demand, so they do not establish local behavioral amplification. None of the **eight supply-line coefficient fits** was usable because of weak inventory response, boundary estimates or insufficient retailer variation.

The main-game actual-generation medians were **1,982 tokens** at the 8,192 cap and **1,922** at the 16,384 cap; neither allowance often bound. Alongside the failed calibration screen, this does not establish a clean computational contrast. Identical outcomes in one chain per condition do not demonstrate equivalence or absence of a human time-pressure effect. The configured model completed the game without the previously observed zero/extreme-order problem; these trajectories alone do not validate the student persona or its realism.

The final same-campaign ledger is **$5.19360675**: calibration **$2.24484225**, including **$0.45876525** for preserved excluded old-state responses, and common rules checks plus game decisions **$2.94876450**. Imported same-campaign charges are already included and must not be counted twice. The two preserved zero-charge HTTP 429 rejection records lack measured usage; no request remains pending and all main decisions have usage. The [independent audit](../data/runs/student_api_b609eca42866feb0/independent_audit.json) reconstructed all 288 model decisions and physical game/tail states without new API calls, reproduced calibration, and verified unchanged pre-resume evidence and report tables. Read the final [Markdown report](../reports/student_pilot_20261011/REPORT.md), [Word report](../reports/student_pilot_20261011/Student_Pilot_Report.docx), and [Excel details](../reports/student_pilot_20261011/DETAILS.xlsx).

These are descriptive engineering results. The failed manipulation, one chain per condition, unusable coefficient estimates and absence of real-student responses prevent confirmatory token-treatment, human time-pressure or actual-UB-student conclusions. The 288 repeated decisions are not 288 participants. Software verification comprises **72 offline/mocked tests** across the 66-test baseline and six focused filesystem tests, plus six safe notebook cells; it establishes operation rather than human validity. Future independent games can reuse the immutable calibration checkpoint without repurchasing calibration, with a new prospective replicate identity and budget.

## What the experiment can establish

The immediate estimand is the effect of a computational allowance on the decisions of a particular GPT model under a fixed hypothetical student persona in this Beer Game. Tokens are an operational proxy for limited computation; there is no validated conversion from tokens to human seconds. Calling the result an effect on actual University at Buffalo students requires human comparison data.

When all conditions receive the same observation, reducing tokens manipulates processing opportunity. It does not independently manipulate the quantity of information. A separate overload claim needs a prospective information-load manipulation, such as a 2-by-2 design crossing a compact versus expanded display with short versus adequate token allowance. Define added information, relevance and history availability before that study; simply making prompts longer changes several things at once.

The independent simulation replicate is the separately initialized four-role chain. Weekly calls within a role are repeated decisions; the four roles interact. One thousand calls are not one thousand students. Independent API draws can characterize variation of this configured model, but they do not create independently sampled human identities or remove a common training/model bias. Inference should use chain-level units and preserve any planned pairing/blocking.

## Persona and repeated question

The following persona illustrates the intended framing. It is a recommendation, not the exact active prompt; the run manifest and per-call `messages` are the canonical executed text. The implemented persona is repeated consistently in onboarding and every decision phase:

> You are a hypothetical second-year business student at the University at Buffalo, an American university, taking part in a classroom Beer Game. Make the inventory decisions you would personally submit as this student, using the game rules, your displayed information and your own previous experience in this game.

Introductory business knowledge and no prior Beer Game experience can be added as explicit design assumptions if that matches the intended human sample. A university label alone does not establish experience, numerical ability, income, nationality, gender, risk preferences or personality. Do not invent those attributes and then describe the resulting outputs as representative of UB students.

Keep the rules, objective, field names, field order, output schema and question wording fixed across conditions. Only the enforced generation cap varies by condition; the model is not told its allowance. Dynamic role, week, state and permitted history necessarily change. The exact implemented repeated question is: "How many cases do you order this week? Return the integer in the order field." The strict schema requests only the order, without a state readback or explanation. Do not prescribe an order heuristic, target order distribution or inventory-policy coefficients in the persona.

Save the exact rendered prompt for every call, requested model, returned model, model snapshot when available, reasoning effort, schemas, cap, full visible response, response status, usage, latency and retry/failure metadata. Preserve calibration separately from main games. A scientifically material prompt or parameter change starts a new protocol/run identity.

Demographic prompting is a testable intervention, not evidence of population fidelity. Bisbee and colleagues found that persona-conditioned ChatGPT survey means could resemble human means while variability, regression relationships and sensitivity to wording/model updates differed. That evidence concerns public-opinion surveys, so extending it to Beer Game decisions is a methodological caution, not an established Beer Game finding. [Bisbee et al., Political Analysis (2024)](https://doi.org/10.1017/pan.2024.5).

A newer benchmark also evaluates synthetic data using distributions and associations, finding limited population realism under sparse conditioning. Larger/newer capacity did not reliably resolve the problem. This supports validating behavior, rather than assuming model upgrades make a student persona more realistic. [Xie et al., PNAS (2026)](https://doi.org/10.1073/pnas.2538145123).

Before claims about actual students, collect a small, clearly labeled external validation sample using the same state display, costs, rules and repeated question. At minimum compare decisions on prespecified held-out states; full-chain human trajectories provide stronger validation of dynamic behavior. Compare order distributions, zero frequency, responsiveness to backlog and outstanding orders, costs and variability, not just matching average orders. A small convenience sample is a feasibility comparison and cannot establish broad representativeness. Reserve held-out human observations for validation after any prompt tuning.

## The user's Davis/18-bias passage

The passage is verifiable. Davis's chapter is *Biases in Individual Decision-Making*, first published 19 October 2018, and concerns individual decision biases relevant to operations. [Davis, The Handbook of Behavioral Operations](https://doi.org/10.1002/9781119138341.ch5).

The GPT passage comes from *A Manager and an AI Walk into a Bar: Does ChatGPT Make Biased Decisions Like We Do?* The researchers test 18 biases with adapted experimental vignettes and operational variants, using GPT-3.5 and GPT-4. They report both similarities and divergences from prototypical human responses; the study is not a validation of a UB student persona or a multiround Beer Game. Its useful design lesson is to use controlled task instructions and measure biases rather than instruct the model to display them. [INFORMS article, DOI 10.1287/msom.2023.0279](https://doi.org/10.1287/msom.2023.0279).

Do not insert the 18-bias list, the expected bullwhip direction, or "underweight the supply line" into decision prompts. Such instructions would partly manufacture the behavior being studied. A Beer Game also does not identify all 18 biases. Treat supply-line use and order amplification as focused outcomes, with any broader bias battery separately designed and analyzed.

## Fixed reasoning effort and model selection

Use `reasoning.effort="high"` consistently for every scientific condition. This is a design choice that satisfies the request for active reasoning while keeping the effort knob fixed; it does not equate the model's cognition to that of a sophomore. Higher effort affects compute and cost. `xhigh` should be used only if a prespecified feasibility comparison shows a practical benefit that justifies it. Available effort values and defaults depend on the model. [Official OpenAI reasoning documentation](https://developers.openai.com/api/docs/guides/reasoning).

A reasonable budget-conscious candidate is `gpt-5.4-mini-2026-03-17`, which supports high effort and structured outputs and has an available fixed snapshot. The recommendation is a candidate for this task, not a claim that it is the newest or most human model. Compare it with a stronger accessible model only on prespecified rule comprehension, valid response rate and external behavioral fidelity. Keep each selected model constant within the treatment comparison, and analyze model replications separately. [Official GPT-5.4 mini model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini).

Improving model strength may reduce accidental rule mistakes while also reducing some human-like mistakes. Neither more variable nor more cost-efficient outcomes establish human realism. Model selection must not optimize a favorable bullwhip effect, a particular beta or statistical significance.

## Token thresholds require a fresh calibration

With active reasoning, `max_output_tokens` limits hidden reasoning, visible output and formatting tokens together. A capped reasoning call can run out before producing any visible decision. Thus the old 32/240-token memo caps and 192-token answer allowance cannot be transferred to high-effort calls without fresh evidence. Record `usage.output_tokens_details.reasoning_tokens`; output tokens minus reasoning tokens is non-reasoning output, not necessarily the number of visible text tokens. [Official OpenAI token-counting documentation](https://developers.openai.com/api/docs/guides/token-counting).

Use a two-step prospective procedure:

1. Measure ordinary high-effort responses on a prespecified bank of states covering all roles, equilibrium, shortage, excess inventory, nonzero backlog and large outstanding replenishment. Use a generous reference cap and retain incomplete responses. Include held-out states not used for setting the caps. Small pilot state counts give unstable percentile estimates, so report the calibration sample size and uncertainty.
2. Set candidate short and adequate caps using baseline output usage percentiles, then test them against a doubled adequate/reference allowance on held-out states. Practical prospective screens can require at least 95% valid complete decisions under the adequate cap, materially smaller actual reasoning/output usage under short, and adequate-versus-doubled order differences within a stated tolerance. Report state-level failures and changes, not just mean usage. These are pragmatic feasibility thresholds, not psychometric standards.

If an implementation needs numbers to start its feasibility screen, 4,096 generated tokens with an 8,192-token comparison is a possible initial probe for a compact decision; it is not a validated threshold. If the reference itself frequently truncates, expand the reference once under a declared rule and recalibrate. Do not assume 4,096 is adequate, and do not automatically retune on final costs or bullwhip results. Fix and version the approved treatment caps before independent games.

There is a tradeoff between a strong cap and having a final action. A single capped structured decision most directly constrains total generation for that decision, but missed answers become an outcome. Increasing the cap or purchasing new reasoning until every pressured call succeeds removes the intervention. A separate equal answer phase permits games to continue, but that phase can perform additional computation. If it receives the full state under high effort, describe the treatment as **constrained preparation followed by a common decision phase**, and report total tokens across both phases. It is not a pure total-computation limit.

Any fallback for a missed decision must be deterministic, prespecified, logged and clearly separated from model-generated orders. For example, holding the previous order is an operational continuation rule, not the student's decision. Preserve the missed-decision count and provide sensitivity analyses; a trajectory with fallback interventions must not be presented as a fully observed LLM behavioral game. Select caps for acceptable completion before main games, not for producing a desired response pattern.

## Time limits

For the first study, use token allowance as the experimental treatment and a common generous technical timeout in every condition. Measure wall-clock latency, but do not label client request duration as thinking time: it includes network delay, queueing and service behavior. A timeout is an operational error unless a separate deadline experiment has been preregistered.

If time is later a scientific treatment, calibrate deadlines using uncensored latency distributions of the same model, effort, observation size, service tier and concurrency; use randomized/interleaved conditions and record technical failures separately. Prespecify deadline handling. Do not combine a tight deadline and a tight token cap in the first comparison, because two simultaneous interventions prevent isolating a token effect. Human and model deadlines need separate calibration; there is no defensible fixed seconds-per-token mapping.

## Zero orders, extreme orders and interpretable games

A zero can be sensible after earlier overordering; a large order can be a genuine response to backlog. The physical Beer Game is designed to expose feedback and delivery-delay mistakes, and human work links order amplification to underweighting outstanding replenishment. Clipping to a desired range, disallowing zero, filtering extreme chains or replacing an unpopular answer would alter the outcome. [Sterman, Management Science (1989)](https://doi.org/10.1287/mnsc.35.3.321); [Croson and Donohue, Management Science (2006)](https://doi.org/10.1287/mnsc.1050.0436).

Correct accidental misunderstanding with common factual onboarding: observations occur after receipts/shipments, current backlog already includes unmet current demand, outstanding orders remain live, zero incoming demand does not cancel backlog, and factory production can begin without existing replenishment. Display those physical facts consistently. Check rules before assigning the treatment, without teaching an ordering formula. Preserve any failures.

The historical clarified Luna follow-up in `data/development/budget_followup_20261005/game_145c7933d7ee/REPORT.md` already completed four of four chains with no zero decisions and maximum orders of 8 (adequate) and 12 (short). This evidence is from the old reasoning-none protocol and must not be pooled with the new persona/high-effort study. It shows that extreme orders are not inevitable. Only 3 of 16 role beta fits were usable, illustrating a different limitation: a nearly demand-matching policy can finish successfully yet fail to identify a supply-line coefficient.

Keep total scored cost and clearly defined bullwhip ratios as outcomes even when beta is unidentifiable. For a deterministic demand step, order-variance ratios depend strongly on the evaluation window; report it and missing zero-variance denominators. A more varied demand schedule may improve identification, but it is a new prospective design and must be matched in human validation. No choice of model, prompt or cap guarantees measurable bullwhip, identifiable beta or a significant effect.
