# Beer Game: completed GPT pilot review

Reviewed 28 September 2026. GPT-agent data, not human participants. Run: bounded_54nano_api_465dbda1ee6129f1

## Conclusions — read first

1. TECHNICALLY SUCCESSFUL: 4 complete groups, 16 agents, 576 game orders; all 596 API replies passed on the first attempt. No API errors, correctness retries, substituted orders or replacement groups.

2. H1/H2 NOT ESTABLISHED: 8/16 roles have usable beta estimates, but 0/4 groups have all four usable. One group per condition is also insufficient for inference. No valid hypothesis estimate, confidence interval or p-value is available.

3. PERFORMANCE REMAINS INEFFICIENT: all customer demand was eventually filled by week 36, but retailer backlog occurred in 12–17 of 36 weeks. Full scored team costs range from 3,644 to 6,888.

4. EXTREME CHOICES REMAIN COMMON: 356/576 orders (61.8%) were zero and 75/576 (13.0%) were at the cap. Zero can be appropriate after a large order; its frequency alone does not prove an error.

5. ESTIMATED API COST: $0.87374 total, below the $1.05 allowance. The resume reused 508 replies and added 88; it did not buy all replies again. These are token-based estimates, not a billing invoice.

6. NEXT STEP: retain this as a completed pilot. Do not scale the current design for H1/H2 yet; the remaining obstacle is measurement, not API reliability.

## 1. What was run and verified

Design: control/trained × low/medium reasoning, one four-role group in each condition. Model: gpt-5.4-nano-2026-03-17. Roles: retailer, wholesaler, distributor, factory. Agents made 36 weekly decisions each. Orders were restricted to 0–40; the restriction is a research design choice, not a standard unrestricted Beer Game rule.

The objective was to minimize team holding costs (0.50/unit/week) plus backlog costs (1.00/unit/week). There was no revenue, profit objective or factory production fee. After agent week 36, 36 automatic continuation weeks carried all state forward. Each role then ordered incoming demand and external demand stayed at its last value. Those 576 automatic role-weeks required no API calls and are excluded from beta and agent behavior statistics.

Independent audit: all 596 parsed answers matched their saved raw API responses; all 576 game orders/readbacks matched the records; replay reproduced every saved physical state and both continuation and score files. Estimated charges reconciled to saved usage. All groups finished without replacement. The initial stop was the local spending guard, not a failed agent. The final resume took 4 min 59 sec; adding the previously observed first-session 26 min 8 sec gives approximately 31 min 6 sec active runtime, excluding the pause.

## 2. Supply-chain performance

| Condition | Agent cost | Continuation cost | Total scored cost | Retailer backlog weeks | Peak retailer backlog |
| --- | --- | --- | --- | --- | --- |
| Control / low | 2184.0 | 1460.0 | 3644.0 | 17 | 24 |
| Control / medium | 2920.0 | 3968.0 | 6888.0 | 12 | 20 |
| Trained / low | 1984.0 | 1736.0 | 3720.0 | 15 | 36 |
| Trained / medium | 3142.5 | 2618.0 | 5760.5 | 14 | 28 |

Costs are game cost units, not API dollars; lower is better. “100% filled” includes late shipments and is not an on-time service rate. End-of-continuation backlog was zero in every group, but 76–220 units of inventory remained; each group also had 96 outstanding units. Continuation scoring exposes later inventory costs but is a finite, policy-dependent evaluation, not an infinite-horizon optimum.

DESCRIPTIVE FINDING: medium effort had higher full scored cost than low effort in both training conditions. Training increased full cost slightly at low effort (3,644 → 3,720; +2.1%) and reduced it at medium effort (6,888 → 5,760.5; −16.4%). These are single-group comparisons, not statistically established effects. Using agent-phase costs alone reverses both training comparisons; the declared full score must therefore remain the performance objective.

A free benchmark in the same simulator, where all roles order their currently received demand, scores 156 in total; always-zero scores 15,968 and always-40 scores 41,788. The GPT groups cost about 23–44 times the simple benchmark. This demonstrates substantial inefficiency on this demand path; the benchmark is not proven optimal or a human comparison, and was not supplied as a recommended agent strategy.

## 3. Ordering behavior

| Condition | Zero orders | Zero % | Orders at 40 | Cap % | Interior orders | Mean order |
| --- | --- | --- | --- | --- | --- | --- |
| Control / low | 94 | 65.3 | 19 | 13.2 | 31 | 8.53 |
| Control / medium | 86 | 59.7 | 21 | 14.6 | 37 | 10.15 |
| Trained / low | 89 | 61.8 | 16 | 11.1 | 39 | 8.56 |
| Trained / medium | 87 | 60.4 | 19 | 13.2 | 38 | 9.15 |

Each condition contains 144 agent orders. Only 145/576 orders (25.2%) were strictly between 0 and 40. The pattern includes large orders followed by zero-order weeks, not simply a refusal to replenish. Example, control/low retailer weeks 7–13: 24, 0, 40, 0, 0, 32, 0. These patterns create delayed inventory swings; they do not prove that every individual zero was irrational.

IMPORTANT: no condition exceeded the prespecified 20% aggregate cap-use warning, but factory cap-use ranged from 16.7% to 30.6%, with three factories above 20%. Group averages conceal role-level problems. Compared descriptively with the older pilot, zeros fell from 91.0% to 61.8%; model, effort, prompts, cap and scoring all changed, so no improvement can be attributed to a single change.

## 4. Beta and H1/H2

Beta is the fitted weight on outstanding supply-line units in an ordering model; it is not profit or overall performance. A value near 1 means approximately full weighting within that model; values above 1 imply stronger weighting. “Usable” only means the planned numerical checks passed. It does not establish a correct behavioral model.

| Condition | Role | Usable beta | Interior /36 | R² | Note |
| --- | --- | --- | --- | --- | --- |
| Control / low | distributor | Not usable | 7 | 0.736 | Fewer than 8 interior orders |
| Control / low | factory | Not usable | 2 | 0.72 | Fewer than 8 interior orders |
| Control / low | retailer | 0.565 | 14 | 0.45 | Alpha at boundary; interpret cautiously |
| Control / low | wholesaler | 0.426 | 8 | 0.73 | Passed numerical checks |
| Control / medium | distributor | 1.684 | 8 | 0.659 | Passed numerical checks |
| Control / medium | factory | Not usable | 3 | 0.538 | Fewer than 8 interior orders |
| Control / medium | retailer | 0.287 | 17 | 0.505 | Passed numerical checks |
| Control / medium | wholesaler | 0.861 | 9 | 0.684 | Passed numerical checks |
| Trained / low | distributor | Not usable | 5 | 0.867 | Fewer than 8 interior orders |
| Trained / low | factory | Not usable | 6 | 0.831 | Fewer than 8 interior orders |
| Trained / low | retailer | 0.956 | 17 | 0.248 | Passed numerical checks |
| Trained / low | wholesaler | 1.074 | 11 | 0.518 | Passed numerical checks |
| Trained / medium | distributor | Not usable | 5 | 0.536 | Fewer than 8 interior orders |
| Trained / medium | factory | Not usable | 4 | 0.748 | Fewer than 8 interior orders |
| Trained / medium | retailer | 0.577 | 22 | 0.28 | Passed numerical checks |
| Trained / medium | wholesaler | Not usable | 7 | 0.66 | Fewer than 8 interior orders |

All eight rejected fits had fewer than eight interior orders under the prespecified rule. All four factories failed, three distributors failed, and one wholesaler failed. Do not substitute their fitted numbers for interpretable betas or drop those agents to obtain a favorable result. One otherwise usable retailer fit has alpha at its upper boundary and merits caution.

H1: training’s planned average effect on group beta cannot be evaluated because no complete group beta is eligible. H2_API: the planned low-minus-medium beta contrast among trained groups is likewise unavailable. Blank p-values mean “not validly tested,” not p > 0.05 or evidence of no effect. The 576 repeated orders are not 576 independent participants. H2_API concerns API reasoning effort, not the original human 60/120-second deadline.

## 5. API reliability, reasoning and cost

| effort | requests | estimated_api_usd | input_tokens | output_tokens |
| --- | --- | --- | --- | --- |
| low | 298 | 0.21338 | 578205 | 110191 |
| medium | 298 | 0.66036 | 578341 | 468264 |

| effort | mean_reasoning_tokens | median_response_seconds |
| --- | --- | --- |
| low | 338.194 | 2.832 |
| medium | 1573.34 | 8.044 |

Counts include 4 startup ordering checks, 16 rules checks and 576 game decisions. Output tokens include reasoning tokens; they must not be billed twice. Medium effort used about 4.7 times as many reasoning tokens per game decision as low effort, yet had higher full scored cost in this pilot. More reasoning tokens did not demonstrate better management here.

The resume added approximately $0.1576 to the previously saved $0.7161. At the same observed traffic, 8 groups per cell (128 agents) would cost roughly $6.97, and 16 groups per cell (256 agents) roughly $13.93. These are extrapolations, not guarantees or recommendations; larger samples would not automatically resolve beta identification.

## 6. Recommended next decision
- Keep this run and its protocol unchanged. Do not repeat it because the effect direction is undesirable.
- Before more paid collection, inspect role trajectories and run free synthetic recovery checks for the actual burst-and-zero ordering patterns. Determine whether the chosen capped ordering model can support group beta under realistic behavior.
- If the measurement model or experimental task must change, define and freeze a new protocol before a separate pilot. Do not remove the interior-order criterion retrospectively, force nonzero answers, select favorable agents or seek significance through repeated reruns.
- If supply-chain performance is to become the primary outcome instead of beta, declare that prospectively and plan independent group replication and power. The current four groups provide descriptive evidence only.

## 7. Where to verify every number

The accompanying Beer_Game_Latest_Pilot_Details.xlsx contains all agent rounds, automatic rounds, all fitted parameters including flagged estimates, group eligibility, performance, order boundaries, API request accounting and hypothesis-test status. Earlier human-readable reports are preserved under reports/archive/previous_pilot_before_continuation_review. The source run retains raw responses and its manifest.
- /Users/gracezhang/Desktop/Y3S1/Project/beer_game_experiment/results/bounded_54nano_api_465dbda1ee6129f1/rounds.csv
- /Users/gracezhang/Desktop/Y3S1/Project/beer_game_experiment/results/bounded_54nano_api_465dbda1ee6129f1/automatic_continuation.csv
- /Users/gracezhang/Desktop/Y3S1/Project/beer_game_experiment/results/bounded_54nano_api_465dbda1ee6129f1/scored_team_costs.csv
- /Users/gracezhang/Desktop/Y3S1/Project/beer_game_experiment/results/bounded_54nano_api_465dbda1ee6129f1/agent_beta_fits.csv
- /Users/gracezhang/Desktop/Y3S1/Project/beer_game_experiment/results/bounded_54nano_api_465dbda1ee6129f1/hypothesis_tests.csv
- /Users/gracezhang/Desktop/Y3S1/Project/beer_game_experiment/results/bounded_54nano_api_465dbda1ee6129f1/request_audit.csv
- /Users/gracezhang/Desktop/Y3S1/Project/beer_game_experiment/results/bounded_54nano_api_465dbda1ee6129f1/independent_result_audit.json
