# Experiment 13: conclusions first

1. **Completion:** 0/4 models complete; 0/96 weekly batches, 0/4 pilots and 0/4 probe batches accepted.
2. **H1/H2:** No complete hypothesis comparisons yet. Software checks are not model results.
3. **Accounting:** Python calculates all inventory, deliveries, backlog and costs from accepted orders. Missing decisions remain missing.
4. **Meaning:** Imagined pressure framing, not an enforced deadline. H1 is a matched-state sensitivity proxy, not structural β. Batched fictional chains are dependent; no p-values are reported.
5. **Shared budget:** $0.340486 charged/reserved across experiments 12 and 13; $4.659514 remains within the original $5 cap.

## Completion by model

| model | accepted_pilot_responses | accepted_weeks | accepted_probe_responses | complete |
| --- | --- | --- | --- | --- |
| gpt-6-luna | 0 | 0 | 0 | False |
| gpt-5.6-luna | 0 | 0 | 0 | False |
| gpt-5.6-sol | 0 | 0 | 0 | False |
| claude-haiku-5-5 | 0 | 0 | 0 | False |

A complete model has an accepted full-size format pilot, all 24 weekly batches and its probe batch. Pilot choices are excluded from the main outcomes. Partial games are exported for diagnosis but cannot supply 24-week H2 costs.

## Hypotheses

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

**H1 proxy:** For otherwise matched states, (order with 8 outstanding cases − order with 32 outstanding cases) / 24. Average over roles and backlog states, then compare matched pressure conditions. A negative difference follows the predicted proxy direction. This does not identify an optimal weight or establish literal underweighting.

**H2:** Sum of $0.50 × end-of-week inventory + $1.00 × backlog over four roles and exactly 24 weeks. A positive difference follows the prediction. There is no revenue or production fee. Terminal inventory, backlog and outstanding orders are reported; unplayed future weeks carry no invented costs.

A null or opposite comparison is a valid result. The protocol does not change prompts, sample size, prices or ordering rules to obtain significance.

## Means by condition

| model | condition | chains | weeks_observed | sensitivity | total_cost | observed_cost_partial |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-6-luna | no_pressure | 0 | 0 | — | — | — |
| gpt-6-luna | strong_pressure | 0 | 0 | — | — | — |
| gpt-5.6-luna | no_pressure | 0 | 0 | — | — | — |
| gpt-5.6-luna | strong_pressure | 0 | 0 | — | — | — |
| gpt-5.6-sol | no_pressure | 0 | 0 | — | — | — |
| gpt-5.6-sol | strong_pressure | 0 | 0 | — | — | — |
| claude-haiku-5-5 | no_pressure | 0 | 0 | — | — | — |
| claude-haiku-5-5 | strong_pressure | 0 | 0 | — | — | — |

## Chain performance

| model | block | condition | weeks_observed | complete | holding_cost | backlog_cost | total_cost | observed_cost_partial | sensitivity | zero_orders | max_order | final_inventory | final_backlog | final_supply_line | bullwhip |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

For an incomplete game, only observed partial costs are available. Do not compare them with full 24-week totals. Bullwhip tables use variance of a role’s weekly orders divided by variance of customer demand over the same observed weeks; a ratio above 1 indicates amplification. A zero denominator is undefined, not zero.

## Execution and model provenance

| task_id | model | phase | week | status | reason |
| --- | --- | --- | --- | --- | --- |
| gpt-6-luna_pilot | gpt-6-luna | pilot | — | missing | — |
| gpt-6-luna_w01 | gpt-6-luna | main | 1 | missing | — |
| gpt-6-luna_w02 | gpt-6-luna | main | 2 | missing | — |
| gpt-6-luna_w03 | gpt-6-luna | main | 3 | missing | — |
| gpt-6-luna_w04 | gpt-6-luna | main | 4 | missing | — |
| gpt-6-luna_w05 | gpt-6-luna | main | 5 | missing | — |
| gpt-6-luna_w06 | gpt-6-luna | main | 6 | missing | — |
| gpt-6-luna_w07 | gpt-6-luna | main | 7 | missing | — |
| gpt-6-luna_w08 | gpt-6-luna | main | 8 | missing | — |
| gpt-6-luna_w09 | gpt-6-luna | main | 9 | missing | — |
| gpt-6-luna_w10 | gpt-6-luna | main | 10 | missing | — |
| gpt-6-luna_w11 | gpt-6-luna | main | 11 | missing | — |
| gpt-6-luna_w12 | gpt-6-luna | main | 12 | missing | — |
| gpt-6-luna_w13 | gpt-6-luna | main | 13 | missing | — |
| gpt-6-luna_w14 | gpt-6-luna | main | 14 | missing | — |
| gpt-6-luna_w15 | gpt-6-luna | main | 15 | missing | — |
| gpt-6-luna_w16 | gpt-6-luna | main | 16 | missing | — |
| gpt-6-luna_w17 | gpt-6-luna | main | 17 | missing | — |
| gpt-6-luna_w18 | gpt-6-luna | main | 18 | missing | — |
| gpt-6-luna_w19 | gpt-6-luna | main | 19 | missing | — |
| gpt-6-luna_w20 | gpt-6-luna | main | 20 | missing | — |
| gpt-6-luna_w21 | gpt-6-luna | main | 21 | missing | — |
| gpt-6-luna_w22 | gpt-6-luna | main | 22 | missing | — |
| gpt-6-luna_w23 | gpt-6-luna | main | 23 | missing | — |
| gpt-6-luna_w24 | gpt-6-luna | main | 24 | missing | — |
| gpt-6-luna_probe | gpt-6-luna | probe | — | missing | — |
| gpt-5.6-luna_pilot | gpt-5.6-luna | pilot | — | missing | — |
| gpt-5.6-luna_w01 | gpt-5.6-luna | main | 1 | missing | — |
| gpt-5.6-luna_w02 | gpt-5.6-luna | main | 2 | missing | — |
| gpt-5.6-luna_w03 | gpt-5.6-luna | main | 3 | missing | — |
| gpt-5.6-luna_w04 | gpt-5.6-luna | main | 4 | missing | — |
| gpt-5.6-luna_w05 | gpt-5.6-luna | main | 5 | missing | — |
| gpt-5.6-luna_w06 | gpt-5.6-luna | main | 6 | missing | — |
| gpt-5.6-luna_w07 | gpt-5.6-luna | main | 7 | missing | — |
| gpt-5.6-luna_w08 | gpt-5.6-luna | main | 8 | missing | — |
| gpt-5.6-luna_w09 | gpt-5.6-luna | main | 9 | missing | — |
| gpt-5.6-luna_w10 | gpt-5.6-luna | main | 10 | missing | — |
| gpt-5.6-luna_w11 | gpt-5.6-luna | main | 11 | missing | — |
| gpt-5.6-luna_w12 | gpt-5.6-luna | main | 12 | missing | — |
| gpt-5.6-luna_w13 | gpt-5.6-luna | main | 13 | missing | — |
| gpt-5.6-luna_w14 | gpt-5.6-luna | main | 14 | missing | — |
| gpt-5.6-luna_w15 | gpt-5.6-luna | main | 15 | missing | — |
| gpt-5.6-luna_w16 | gpt-5.6-luna | main | 16 | missing | — |
| gpt-5.6-luna_w17 | gpt-5.6-luna | main | 17 | missing | — |
| gpt-5.6-luna_w18 | gpt-5.6-luna | main | 18 | missing | — |
| gpt-5.6-luna_w19 | gpt-5.6-luna | main | 19 | missing | — |
| gpt-5.6-luna_w20 | gpt-5.6-luna | main | 20 | missing | — |
| gpt-5.6-luna_w21 | gpt-5.6-luna | main | 21 | missing | — |
| gpt-5.6-luna_w22 | gpt-5.6-luna | main | 22 | missing | — |
| gpt-5.6-luna_w23 | gpt-5.6-luna | main | 23 | missing | — |
| gpt-5.6-luna_w24 | gpt-5.6-luna | main | 24 | missing | — |
| gpt-5.6-luna_probe | gpt-5.6-luna | probe | — | missing | — |
| gpt-5.6-sol_pilot | gpt-5.6-sol | pilot | — | missing | — |
| gpt-5.6-sol_w01 | gpt-5.6-sol | main | 1 | missing | — |
| gpt-5.6-sol_w02 | gpt-5.6-sol | main | 2 | missing | — |
| gpt-5.6-sol_w03 | gpt-5.6-sol | main | 3 | missing | — |
| gpt-5.6-sol_w04 | gpt-5.6-sol | main | 4 | missing | — |
| gpt-5.6-sol_w05 | gpt-5.6-sol | main | 5 | missing | — |
| gpt-5.6-sol_w06 | gpt-5.6-sol | main | 6 | missing | — |
| gpt-5.6-sol_w07 | gpt-5.6-sol | main | 7 | missing | — |
| gpt-5.6-sol_w08 | gpt-5.6-sol | main | 8 | missing | — |
| gpt-5.6-sol_w09 | gpt-5.6-sol | main | 9 | missing | — |
| gpt-5.6-sol_w10 | gpt-5.6-sol | main | 10 | missing | — |
| gpt-5.6-sol_w11 | gpt-5.6-sol | main | 11 | missing | — |
| gpt-5.6-sol_w12 | gpt-5.6-sol | main | 12 | missing | — |
| gpt-5.6-sol_w13 | gpt-5.6-sol | main | 13 | missing | — |
| gpt-5.6-sol_w14 | gpt-5.6-sol | main | 14 | missing | — |
| gpt-5.6-sol_w15 | gpt-5.6-sol | main | 15 | missing | — |
| gpt-5.6-sol_w16 | gpt-5.6-sol | main | 16 | missing | — |
| gpt-5.6-sol_w17 | gpt-5.6-sol | main | 17 | missing | — |
| gpt-5.6-sol_w18 | gpt-5.6-sol | main | 18 | missing | — |
| gpt-5.6-sol_w19 | gpt-5.6-sol | main | 19 | missing | — |
| gpt-5.6-sol_w20 | gpt-5.6-sol | main | 20 | missing | — |
| gpt-5.6-sol_w21 | gpt-5.6-sol | main | 21 | missing | — |
| gpt-5.6-sol_w22 | gpt-5.6-sol | main | 22 | missing | — |
| gpt-5.6-sol_w23 | gpt-5.6-sol | main | 23 | missing | — |
| gpt-5.6-sol_w24 | gpt-5.6-sol | main | 24 | missing | — |
| gpt-5.6-sol_probe | gpt-5.6-sol | probe | — | missing | — |
| claude-haiku-5-5_pilot | claude-haiku-5-5 | pilot | — | missing | — |
| claude-haiku-5-5_w01 | claude-haiku-5-5 | main | 1 | missing | — |
| claude-haiku-5-5_w02 | claude-haiku-5-5 | main | 2 | missing | — |
| claude-haiku-5-5_w03 | claude-haiku-5-5 | main | 3 | missing | — |
| claude-haiku-5-5_w04 | claude-haiku-5-5 | main | 4 | missing | — |
| claude-haiku-5-5_w05 | claude-haiku-5-5 | main | 5 | missing | — |
| claude-haiku-5-5_w06 | claude-haiku-5-5 | main | 6 | missing | — |
| claude-haiku-5-5_w07 | claude-haiku-5-5 | main | 7 | missing | — |
| claude-haiku-5-5_w08 | claude-haiku-5-5 | main | 8 | missing | — |
| claude-haiku-5-5_w09 | claude-haiku-5-5 | main | 9 | missing | — |
| claude-haiku-5-5_w10 | claude-haiku-5-5 | main | 10 | missing | — |
| claude-haiku-5-5_w11 | claude-haiku-5-5 | main | 11 | missing | — |
| claude-haiku-5-5_w12 | claude-haiku-5-5 | main | 12 | missing | — |
| claude-haiku-5-5_w13 | claude-haiku-5-5 | main | 13 | missing | — |
| claude-haiku-5-5_w14 | claude-haiku-5-5 | main | 14 | missing | — |
| claude-haiku-5-5_w15 | claude-haiku-5-5 | main | 15 | missing | — |
| claude-haiku-5-5_w16 | claude-haiku-5-5 | main | 16 | missing | — |
| claude-haiku-5-5_w17 | claude-haiku-5-5 | main | 17 | missing | — |
| claude-haiku-5-5_w18 | claude-haiku-5-5 | main | 18 | missing | — |
| claude-haiku-5-5_w19 | claude-haiku-5-5 | main | 19 | missing | — |
| claude-haiku-5-5_w20 | claude-haiku-5-5 | main | 20 | missing | — |
| claude-haiku-5-5_w21 | claude-haiku-5-5 | main | 21 | missing | — |
| claude-haiku-5-5_w22 | claude-haiku-5-5 | main | 22 | missing | — |
| claude-haiku-5-5_w23 | claude-haiku-5-5 | main | 23 | missing | — |
| claude-haiku-5-5_w24 | claude-haiku-5-5 | main | 24 | missing | — |
| claude-haiku-5-5_probe | claude-haiku-5-5 | probe | — | missing | — |

Requested model IDs are fixed in the plan. Provider-returned IDs and token usage are retained in the request records. OpenAI uses reasoning effort none; Claude uses disabled thinking and low effort. Weekly/pilot output allowances are 2,048 tokens; probe allowance is 4,096. Both conditions use the same generation settings. No temperature override is sent. These settings affect the simulation and limit comparison with previous higher-effort collections.

Only a transient transport, rate-limit or server failure can receive one further budgeted attempt. Invalid choices, refusals and incomplete outputs remain failures. A failed model blocks its remaining dependent tasks; other models can continue. Reopening the notebook reuses verified accepted responses. Unknown charges retain their reservation. Local accounting is a conservative estimate, not a provider invoice or account balance.

## Design and limits

Per model: 20 four-role chains, 10 matched pairs, 24 weeks. Python reveals current state and a short past history, then commits all submitted orders simultaneously. It does not reveal future demand to the model. The researcher scores 24 weeks, but the eventual stopping week is deliberately not revealed in the API prompts. All chain choices in a week are generated jointly; the model can see the whole batch. Prompted identity separation is not technical information isolation. No individual-agent or human replication is claimed.

- Pressure is fictional framing; actual time or reasoning resources do not differ by condition.
- All current roles/chains appear in a shared batch, so private information isolation and chain independence are not enforced.
- H1 is a matched-state sensitivity proxy, not the original structural beta or a human cognitive measurement.
- Only full 24-week chains contribute primary H2; partial accrued costs are separately labeled.
- Final commitments after week24 are displayed but subsequent costs are outside the primary horizon.
- Human observations=0. No p-values, independent-chain confidence intervals or hypothesis-proof claims.

## Files

- [Excel workbook](../../../analysis/weekly_api_c64d75aa3a03356f/d22d60e266a2/RESULTS.xlsx)
- [Weekly states and orders](../../../analysis/weekly_api_c64d75aa3a03356f/d22d60e266a2/rounds.csv)
- [Chain performance](../../../analysis/weekly_api_c64d75aa3a03356f/d22d60e266a2/chains.csv)
- [Probe choices](../../../analysis/weekly_api_c64d75aa3a03356f/d22d60e266a2/probes.csv)
- [Matched comparisons](../../../analysis/weekly_api_c64d75aa3a03356f/d22d60e266a2/contrasts.csv)
- [Frozen plan and execution evidence](../../../data/weekly_api_c64d75aa3a03356f)
- [Exact prompt archive](../../../prompts/weekly_api_c64d75aa3a03356f)
- [Raw API records](../../../raw/weekly_api_c64d75aa3a03356f)
- [Original shared budget ledger](../../../../12_pressure_framing_api_20261020/data/api_budget.json)
- [Prospective protocol](../../../hypotheses/PROTOCOL.md)

API settings checked 21 October 2026: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), [Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5).
