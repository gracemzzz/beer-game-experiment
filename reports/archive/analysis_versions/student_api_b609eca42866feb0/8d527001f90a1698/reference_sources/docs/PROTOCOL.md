# Information sharing and token constraints: prospective protocol

## Conclusions and scope

1. This is a fresh protocol derived from `data/source/ThoughtsReflection_Paragraph.docx`, supplied on 4 October 2026. The document is research material, not an instruction to execute its human recruitment plans.
2. H1 predicts lower supply-line weight under constrained preparation. H2 predicts higher total holding/backlog costs. The earlier training × reasoning-effort hypotheses do not apply.
3. The notebook is prepared and software-tested. No live calibration or GPT results have been generated during preparation. Better behavior and significant results are not guaranteed.
4. Free software checks do not validate the token manipulation. Live calibration is required before paid games.

## Mapping from the reflection

| Reflection | LLM implementation |
| --- | --- |
| Four participants per chain | Four separately prompted role agents; each has its own history |
| Information-sharing environment | All four current physical inventories are visible to every role; local backlog, orders and outstanding replenishment remain role-specific; no direct communication or future demand disclosure |
| Four-chain ordinary-time pilot, approximately 40 rounds | A four-chain API game pilot can use `GROUPS_PER_CONDITION=2`, 40 weeks. The initial inexpensive calibration instead uses 24 shared-information hypothetical states across roles; this is a deliberate budget-saving departure from the human trajectory calibration |
| P25/P95 ordinary response times, doubled generous benchmark | P25/P95 visible memo-token counts at a 1,024-token reference cap, rounded to 16-token increments; compare those caps and twice the adequate cap on the same 24 states |
| Time pressure | Hard memo-output token budget, not wall-clock latency; both conditions use `reasoning.effort=none` |
| 80 new participants, ten chains in each condition | 10 independent four-agent chains per condition, paired into blocks for scheduling/analysis; separate fresh replicate from calibration |
| H1: greater underweighting | Short-minus-adequate group beta < 0 |
| H2: higher costs | Short-minus-adequate total scored team cost > 0 |

The cheap hypothetical-state screen is not equivalent to measuring full-chain ordinary response times. It is a feasibility screen before the four-chain pilot; it may miss pressure that emerges in later rounds. The actual game report repeats token-use/truncation checks. Explicitly reporting that departure is preferable to treating hypothetical observations as human pilot evidence.

## Token intervention

Same model: `gpt-5.4-nano-2026-03-17`. API `reasoning.effort=none` is fixed in both conditions. We do not compare low/medium reasoning settings. Unexpected nonzero reasoning-token usage stops the protocol.

Each agent decision has two requests:

1. Prepare a concise memo, with a provisional order first and key numerical estimates/risks. The instruction states the allowance and asks the model to finish before it expires. `max_output_tokens` enforces the cap. No step-by-step private reasoning is requested.
2. Supply the observed state and memo to the same model, with a fixed 192-token structured final response. This ensures that a deliberately truncated memo does not automatically become a missing order. No extra preparation request is purchased.

The API is responsible for truncation. Models do not reliably introspect a remaining-token counter, and a prompt alone is not enforcement. The second request can still contain implicit computation; the intervention concerns visible preparation opportunity, not exact total cognitive effort. Actual usage, truncation, completion, latency and token cost are recorded. Unused allowance is not effort used. A larger allowed output does not necessarily produce a stronger treatment.

Calibration thresholds are prospective pilot screens: reference truncation 0%; short truncation at least 20%; adequate truncation at most 5%; adequate mean actual memo tokens greater than short; median absolute order difference between adequate and doubled allowance no more than 4 units. These pragmatic thresholds are not validated psychometric cutoffs. Compare state-level responses, not only averages. Budget selection is based on usage/feasibility, not H1/H2 p-values. A failed screen requires review; the notebook does not auto-retune until a favorable result appears.

## Physical game and shared information

Four roles, initial stock 12 each, initial weekly flow 4. Orders travel upstream in one week; actual deliveries travel downstream in two weeks; factory production takes three weeks. Orders may wait for supplier stock. The simulator tracks and checks the identity linking outstanding orders, shipping queues, supplier backlogs and orders in transit. All four roles decide from the same weekly snapshot before any order is committed.

Customer demand is 4 in weeks 1–4 and 8 thereafter. This is hidden from agents in advance. The first four rounds use fixed orders of 4; the next 36 rounds use agent decisions. Common instructions describe facts and the cumulative team objective without giving an order formula, preferred beta or expected direction. The total outstanding supply line is displayed directly. This tests its use in ordering, not the separate mental arithmetic of adding hidden pipeline stages; the reflection’s proposed aggregation mechanism is therefore not isolated. There is no training/control split. No revenue, order fee, volume discount or factory charge is added.

After agent decisions, 12 automatic weeks carry stock/backlogs/outstanding orders forward. External demand stays at its last value; each role then orders incoming demand. Full team costs include this finite continuation. It is a declared terminal-evaluation policy, not a universal Beer Game rule or infinite-horizon terminal value. Residual inventory and backlog remain visible. Twelve is fixed prospectively; changing it creates a different protocol. Automatic rounds are separate from behavioral data and require no API calls.

There is **no advertised order-entry maximum**. The previous 40-unit cap is removed, including from the response schema and behavioral estimator. A separate computational circuit breaker stops orders above 100,000 before game mutation and retains the exact reply. It does not clip orders or choose 100,000 on the agent's behalf. Any such event means the protocol needs review, not successful completion.

## Bullwhip and boundary behavior

Bullwhip means amplification of order variability relative to downstream demand, often increasing upstream. Delayed replenishment and underweighting outstanding orders can generate overordering, later excess inventory, and subsequent zero orders. A zero is therefore not sufficient evidence of a broken objective. Frequent zeros followed by large orders must be assessed as a sequence.

Report both `Var(role orders) / Var(role incoming demand)` and `Var(role orders) / Var(external customer demand)`, using sample variance over all 40 game weeks. Ratios greater than one indicate amplification relative to the named denominator. Local ratios measure amplification from one stage to the next; external ratios permit role comparisons against a common denominator. We also plot weekly orders and record backlog, inventory, order variance, zero rate and maximum order. Denominator variance of zero yields missing data, never zero/infinity. Because the demand step is nonstationary and constant thereafter, ratios are descriptive and sensitive to the chosen window. No prompt asks for a bullwhip pattern.

## Estimation and inference

The exploratory ordering model is `max(0, forecast + alpha * (target - net_inventory - beta * supply_line))`, with exponentially smoothed local demand. No upper clipping is included. Each role receives a separate nonlinear fit over agent-choice weeks. Rank/conditioning, response strength, variation, bounds and fit diagnostics remain visible; fewer than five positive orders flags unusability. The earlier eight-interior-orders criterion for an upper-capped response is not retained. A synthetic test verifies beta recovery with genuine zero responses. Such checks do not establish the model fits arbitrary GPT policies.

H1 uses mean beta only for chains with all four usable role estimates; if any planned pair has missing group beta, H1 inference is withheld rather than selecting favorable complete cases. H2 uses total team cost independently of beta: a missing beta must not suppress an otherwise complete cost comparison. All completed games remain included regardless of performance/direction.

Two-sided paired sign-flip tests use the independent chain block as unit, exact through 16 pairs and Monte Carlo thereafter; they require sign exchangeability under the null. Both directions are reported separately from significance. Holm adjustment retains a family of two, using a conservative missing-test placeholder when H1 is unidentifiable. At least eight complete pairs are required by the software; that floor is not a power calculation. The reflection's ten pairs require prospective power assessment based on pilot variability and an effect worth detecting. Repeated weekly orders are not independent participants. Claims apply to the particular LLM and protocol, not human time pressure.

## Reliability, cost and provenance

SDK retries are disabled. The gateway applies paced shared starts and shared cooldown. Only classified temporary errors are retried, with unchanged payload and caps; quota/authentication/access errors stop. Reservations for unknown usage persist. Known HTTP rejection has no generated-token charge. A stopped reservation is not silently resent. All raw responses, usage and failed attempts stay in the run folder; secrets and full error strings are excluded.

A final format/readback/rules failure marks the candidate group failed. At most one fresh whole-group replacement is allowed by default, with failures/partial trajectories retained. Replacement is never based on zero orders, costs, beta or significance. Any replacement suppresses p-values because it can select on treatment-dependent failures. Emergency-scale orders stop the entire run. Completed stages cache independently: a successful memo is not regenerated simply because the final call has not yet run.

A local dollar allowance covers calls, retries and replacements. Conservative reservations may stop before the displayed cost reaches the allowance. Increasing only the budget or operational pacing does not change the run ID. Scientific settings and all package source hashes do. New tests use mocks/offline mode only; the user starts paid calls explicitly from the notebook.

## Process records and optional questionnaire

The source document was updated during implementation to add screen recordings, written explanations and post-questionnaires. The initial source snapshot is preserved separately; the active source copy includes that paragraph. Saved API payloads, memos, replies, usage and state transitions provide the software analogue of a process record, not a human screen recording. `collect_debriefs=True` adds one 384-token retrospective questionnaire response per agent after every game has finished. Questions address general strategy, a difficult state, useful additional information, and whether the memo allowance constrained the response. The default is off to avoid extra cost. Select it before beginning a new run; changing this scientific setting later creates a new run ID. Debriefs cannot affect already committed orders and are not used as causal evidence of actual internal reasoning. They are saved separately in `debriefs.json` and the report/workbook.

## Sources checked 4 October 2026

- Supplied `ThoughtsReflection_Paragraph.docx`: the authoritative study hypothesis/design source. Its literature descriptions are treated as supplied background, not independently verified empirical claims.
- [MIT / John Sterman Beer Game](https://web.mit.edu/jsterman/www/SDG/beergame.html): standard cost objective, delayed flows, initial conditions and horizon concerns. The new information sharing, four-week warmup and automatic continuation are declared variants.
- [Lee, Padmanabhan & Whang, Management Science (1997)](https://pubsonline.informs.org/doi/10.1287/mnsc.43.4.546): order-variance amplification; demand-signal processing, batching, rationing and price variation as sources. Not all these mechanisms occur in this fixed-price simulator.
- [OpenAI GPT-5.4 nano](https://developers.openai.com/api/docs/models/gpt-5.4-nano): support for reasoning none, model snapshot and prices.
- [OpenAI reasoning guide](https://developers.openai.com/api/docs/guides/reasoning): reaching `max_output_tokens` can produce an incomplete response.
- [OpenAI prompting guidance](https://developers.openai.com/api/docs/guides/reasoning-best-practices): clear direct instructions; do not depend on a requested chain of thought.

## Calibration 2: prospective refinement after the first feasibility screen

The completed `calibration_api_6778221cada613b6` run had 176/240/480-token caps. Only 3/24 short memos truncated (12.5% < 20%); adequate/benchmark checks passed. Actual mean memo use was 140.1 versus 147.8 tokens, a weak separation. This does not establish H1/H2.

The next independent feasibility screen fixes caps at 96/240/480. It retains the earlier completed, uncensored reference screen and makes 144 fresh calls for the three candidate allowances. The fixed mode uses the explicitly configured caps; merely changing SHORT_TOKENS in the old percentile mode would have had no effect on its API selection. All other pass criteria are unchanged. Reference provenance is recorded. No main study or repeated automatic tuning is triggered. The first implementation and notebook are archived separately.

## Startup correction after the first game attempt (5 October 2026)

`game_api_d7df690aed2c8ead` stopped entirely during startup. Six of sixteen rule replies passed; ten incorrectly set `objective_includes_continuation` to false. All responses completed successfully at the API level. No actual game decisions were made. Estimated spend was $0.0023944. This is an onboarding failure, not H1/H2 evidence. The raw run and its implementation are retained.

The revised quiz names each question by its response field, defines continuation as automatic physical game weeks, and restates the score formula. The response schema still permits an incorrect boolean; nothing forces a pass. This follows the recommendation for clear field descriptions in [OpenAI's structured-output guide](https://developers.openai.com/api/docs/guides/structured-outputs). One bounded recheck uses the same named questions and asks for review, without supplying an order strategy. Each attempt and failed field are logged in `rules_validation.json` and the report. These are common pre-treatment instructions; they never extend a constrained decision memo.

All original groups complete onboarding before game play begins. A persistent rules failure stops the run directly; group replacement remains only for failures during actual game decisions. The cache preserves both failed and successful quiz attempts, so a resume cannot reset its attempt allowance. Retrospective statistical claims describe this onboarding policy, and first-attempt failures remain visible. Passing a quiz is not proof of realistic strategy or of durable comprehension; the later model requests are stateless except for the supplied game history.

No token recalibration is required for this specific correction: AST comparisons confirm identical common order instructions, order schema, decision prompt builder and validation, decision function, model/rates, physical simulator and API implementation. The archived files also match the passed calibration's complete original source hashes. The calibration folder contains an explicit `onboarding_compatibility.json` record. A changed ordering-task fingerprint invalidates that record; it is not a general bypass of calibration. Full source hashes remain in each run manifest, and new run IDs still distinguish implementations.
