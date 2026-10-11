# Beer-Game v2 API Diagnostic Report

## 1. Conclusions

1. **API execution passed:** all 64 requests succeeded—16 basic-rules checks and 48 diagnostic orders. No errors or replacement orders were recorded.
2. H1 and H2 remain untested. This was the diagnostic stage, not the four-role beer-game simulation. No β estimates, p-values, or significance claims are justified.
3. **The reasoning setting changed resource use:** high effort used 8.53× as many reasoning tokens on average as low effort in diagnostic decisions. This supports an effort manipulation, not human time pressure.
4. **Orders responded to inventory and outstanding orders:** none of the four condition screens copied demand in every state. However, 31/48 orders (64.6%) were zero, which may still make β hard to identify.
5. No clear training advantage is established. The observed supply-line response was equal across training conditions at high effort and weaker for trained prompts at low effort. These are descriptive comparisons, not β or hypothesis tests.
6. **Next step:** a small full-game measurement pilot. Check β identification before paying for a larger significance-testing run.

## 2. What actually ran

Run: v2_api_7774f231a26789fc; completed 27 September 2026, 16:34 New York time. Model: gpt-5.4-mini-2026-03-17. Runtime: 4 min 7 sec. The settings contained GROUPS_PER_CELL = 4 and WEEKS = 36, but STAGE = "diagnostics" ignores both for execution. There were four prompt/effort conditions, each with four repeated rules checks and 12 independent hypothetical retailer states. There were no 16-group games, no linked supply-chain trajectories, and no 36-week observations in this run.

## 3. Response quality and test design

All 16 rules checks returned the expected answers: net inventory 6, holding cost 4, shipping delay 2 weeks, and production delay 3 weeks. All 48 decisions correctly read back demand, inventory, backlog, and supply line. The rules checks used the same questions and were labeled by role; they did not test separate role-specific skills. Format and state-reading success do not establish optimal ordering or effective training. Each diagnostic state had demand 8 and backlog 0; inventory was 0, 12, or 24, crossed with outstanding orders of 4, 12, 24, or 36. Each state was sampled once per condition, without a game history.

## 4. Main behavioral findings

| Condition | Supply-line change → order change | Inventory change → order change | Zero orders |
| --- | --- | --- | --- |
| Control / low | -5.33 | -6.00 | 5/12 |
| Trained / low | -4.00 | -5.00 | 6/12 |
| Control / high | -6.67 | -8.00 | 10/12 |
| Trained / high | -6.67 | -7.00 | 10/12 |

Supply-line effect: increase outstanding orders from 4 to 36, holding inventory fixed, then average across the three inventory levels. Inventory effect: increase inventory from 0 to 24, holding outstanding orders fixed, then average across four supply-line levels. Negative values mean fewer units ordered. These are finite differences, not β estimates. High effort produced 10/12 zero orders in each training condition (83.3%). A zero order can be a valid decision; it is not a response error.

## 5. Reasoning effort and response time

| Effort | Diagnostic orders | Mean reasoning tokens | Median latency |
| --- | --- | --- | --- |
| low | 24 | 190.7 | 1.61 s |
| high | 24 | 1,625.7 | 5.53 s |

These figures cover the 48 diagnostic orders, excluding rules checks. The same 8,192-token maximum and 180-second infrastructure timeout applied to both conditions. The longest diagnostic response took 23.12 seconds. Effort settings are not exact time or token budgets; they do not recreate a human 60/120-second deadline.

## 6. H1/H2 interpretation and comparison with the original pilot

H1 asks whether training increases fitted supply-line weight β. H2_API asks whether low effort reduces β among trained GPT agents. Neither is tested here because diagnostic finite differences are not fitted β, and 12 states are not 12 independent groups. The original human time-pressure H2 is outside this protocol. The old pilot had 34/64 roles copying demand throughout their games; this diagnostic had 0/4 condition screens copying demand in every state. The different model, prompts, states, and design prevent attributing that difference to a specific change or treating it as a controlled improvement.

## 7. Spending

The 64 successful requests used 36,880 input tokens (0 cached) and 47,067 output tokens, including 44,559 reasoning tokens. Using the rates saved in the run manifest ($0.75 input / $0.075 cached input / $4.50 output per million), the calculated cost is $0.2395, approximately $0.24. Reasoning tokens are already included in output, not charged twice. This matches the local spending record; it is an estimate, not an invoice or remaining account balance. The configured local allowance was $3.00. These short diagnostic prompts do not reliably predict full-game cost as histories grow.

## 8. Recommended next run

Keep the diagnostic records separate. For a full-game measurement pilot, use MODE = "api", STAGE = "game", GROUPS_PER_CELL = 4, and WEEKS = 36. This plans 16 four-role groups, 64 agents, 2,304 orders, and 64 rules checks. Review the budget scenarios before starting. Inspect β identification, demand copying, zero-order frequency, and reasoning usage before scaling. Four groups per cell will not produce p-values under the current v2 rules. The reporting floor is eight complete blocks (eight usable groups per cell), with no excluded planned blocks; it is not a power calculation. Determine a fixed sample size from a stable pilot and a meaningful effect size. Do not alter prompts or add groups merely to reach p < .05.

Full detail: Beer_Game_V2_Diagnostic_Details.xlsx. Original v1 reports are preserved.
