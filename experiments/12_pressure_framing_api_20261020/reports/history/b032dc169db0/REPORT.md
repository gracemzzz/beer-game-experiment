# Experiment 12: conclusions first

1. **Collection:** 0/4 main responses and 2/4 pilot responses accepted.
2. **H1/H2 findings:** No main API results have been collected. Software checks do not provide hypothesis evidence.
3. **Interpretation:** This tests imagined pressure framing. It does not establish a binding deadline, original structural β, or effects on real students.
4. **Statistical independence:** All 20 chains and both conditions share one main response per model. No p-values or inferential confidence intervals are reported.
5. **Budget:** $0.0717 charged or conservatively reserved out of the authorized $5 total across this experiment, including pilot and retries.

## Design

Each model represents 80 fictional students in 20 four-role chains: 10 no-pressure and 10 strong-pressure chains. Each chain submits all 24 weeks at once. H2 includes only those 24 weeks; there are no automatic continuation costs. Matched chains share demand paths and profile assignments. Four disjoint two-chain pilot responses are outside the main sample.

All models use low effort; the same settings apply to both conditions. The pilot cap is 8,192 output tokens and the main cap is 16,384, including hidden reasoning. These are completion allowances, not the experimental pressure manipulation. Provider effort labels are not equivalent measurements of computation.

## Findings by model

| model | hypothesis | paired_blocks | mean_strong_minus_no | descriptive_direction |
| --- | --- | --- | --- | --- |
| gpt-6-luna | H1 | 0 | — | unavailable |
| gpt-6-luna | H2 | 0 | — | unavailable |
| gpt-5.6-luna | H1 | 0 | — | unavailable |
| gpt-5.6-luna | H2 | 0 | — | unavailable |
| gpt-5.6-sol | H1 | 0 | — | unavailable |
| gpt-5.6-sol | H2 | 0 | — | unavailable |
| claude-haiku-5-5 | H1 | 0 | — | unavailable |
| claude-haiku-5-5 | H2 | 0 | — | unavailable |

**H1:** mean reduction in order divided by a 24-case increase in outstanding dispatched replenishment, over eight matched probes per chain. A smaller sensitivity under strong pressure is consistent with the predicted proxy direction. This does not identify an optimal benchmark or the original structural coefficient.

**H2:** cumulative chain holding cost ($0.50 per case-week) plus backlog cost ($1 per case-week). A positive strong-minus-no-pressure difference follows the prediction. There is no revenue or factory production fee.

## Completion and technical checks

| model | accepted_pilot_responses | accepted_main_responses | accepted_main | complete |
| --- | --- | --- | --- | --- |
| gpt-6-luna | 0 | 0 | 0 | False |
| gpt-5.6-luna | 1 | 0 | 0 | False |
| gpt-5.6-sol | 1 | 0 | 0 | False |
| claude-haiku-5-5 | 0 | 0 | 0 | False |

Acceptance requires all chain IDs, 24 order rows, probes, factual rules and inventory readbacks at weeks 1, 12 and 24. The four pilots must all pass before any main call. An incorrect or incomplete response is retained; no semantic retries, replacement cohorts, clipping or filled-in orders are used. At most one retry is allowed for a transient transport/rate/server error, with its cost reserved.

| task_id | status | reason |
| --- | --- | --- |
| gpt-6-luna_pilot | invalid | response_validation |
| gpt-5.6-luna_pilot | accepted | — |
| gpt-5.6-sol_pilot | accepted | — |
| claude-haiku-5-5_pilot | invalid | incomplete_or_refused |
| gpt-6-luna_main | pilot_blocked | — |
| gpt-5.6-luna_main | pilot_blocked | — |
| gpt-5.6-sol_main | pilot_blocked | — |
| claude-haiku-5-5_main | pilot_blocked | — |

## Spending and models

First-attempt conservative reservation for the 8 planned calls in this collection stage: **$0.8359**. This assumes every output cap is filled and uses a conservative input byte bound. Actual token usage settles each reservation; an uncertain charge keeps its full reservation. Prices were checked on 20 October 2026. The local ledger is not an account balance.

| model | pilot_calls | main_calls | first_attempt_reservation_ceiling_usd |
| --- | --- | --- | --- |
| gpt-6-luna | 1 | 1 | 0.0188 |
| gpt-5.6-luna | 1 | 1 | 0.0425 |
| gpt-5.6-sol | 1 | 1 | 0.7519 |
| claude-haiku-5-5 | 1 | 1 | 0.0227 |

Returned model IDs: {"gpt-5.6-luna": "gpt-5.6-luna", "gpt-6-luna": "gpt-6-luna", "gpt-5.6-sol": "gpt-5.6-sol"}

## Limits

- Pressure is imagined framing; no binding deadline or token contrast is enforced.
- All four roles and future demand are jointly visible to the trajectory generator.
- Pipeline sensitivity and relative probe weight are proxies, not original structural beta.
- All twenty chains and both conditions share one generation per model; no independent-chain p-values or confidence intervals; human observations=0.
- Seeing both classroom situations in one response permits cross-condition contamination and comparisons by the generator.
- Checkpoint agreement supports three inventory calculations, not every internal decision or state.
- The 24-week primary cost omits liabilities after the horizon; terminal state is reported separately.

A directionally null result is a zero or small descriptive contrast in this generated sample; it does not prove no effect. More generated identities within one reply cannot supply independent replication. Testing literal H1/H2 requires a separate enforced-time/computation design and independent collection.

## Files

- [Excel: results and costs](../../../analysis/pressure_api_c04ef16c05dd826c/b032dc169db0/RESULTS.xlsx)
- [All weekly states and orders](../../../analysis/pressure_api_c04ef16c05dd826c/b032dc169db0/rounds.csv)
- [Hypotheses and comparisons](../../../analysis/pressure_api_c04ef16c05dd826c/b032dc169db0/hypotheses.csv)
- [Exact prompts and schemas](../../../prompts/pressure_api_c04ef16c05dd826c)
- [Frozen plan](../../../data/pressure_api_c04ef16c05dd826c/plan.json)
- [Original API records](../../../raw/pressure_api_c04ef16c05dd826c)
- [Protocol](../../../hypotheses/PROTOCOL.md)
