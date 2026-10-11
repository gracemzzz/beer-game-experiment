# Continuation-scoring update (protocol 2)

1. Final agent orders now have consequences in the scored objective: 36 automatic weeks follow the agent phase, with no reset and no API calls. The score is agent-phase cost plus continuation cost.
2. During continuation, customer demand stays at its last observed value; every role automatically orders its incoming demand, bounded at 40. This rule is fixed for all conditions and disclosed to agents, not recommended for their own decisions. No new GPT decisions are generated.
3. This finite continuation is a researcher-selected modification, not standard Beer Game rules or a validated infinite-horizon terminal value. Residual inventory, backlog and outstanding units are reported. Different continuation policies can change incentives; freeze this protocol before collection.
4. Common instructions clarify that current cost is already incurred, orders affect future costs, and no revenue or order-placement reward exists. Three new rules questions verify recurring backlog costs, timing and continuation scoring. They do not test a preferred strategy. Training/control lessons remain distinct and unchanged.
5. Automatic rounds go only to `automatic_continuation.csv`; full scored costs go to `scored_team_costs.csv`. Beta, agent-phase performance, fulfillment and boundary rates use only agent decisions. The notebook report explicitly distinguishes both phases.
6. A new protocol/cache identity prevents reuse of earlier replies. Old results remain unchanged. The default is still one group per condition, 16 agents, 36 agent weeks and a $0.75 local allowance. No additional planned API requests are introduced; slightly longer prompts can change actual cost.
7. Run the notebook's free measurement and economic checks before the paid cell. Neither these changes nor a passed rules check guarantees realistic GPT strategies, identified beta or significant H1/H2.

Prompt wording follows the clear, direct instructions guidance in [OpenAI Docs](https://developers.openai.com/api/docs/guides/reasoning-best-practices).

**Validation of this update:** all 23 offline/mocked tests passed, including separate final-order sensitivity for each role, exact replay, score reconciliation, and exclusion of automatic rounds from agent data. The entire notebook ran in offline mode with zero cell errors; saved at `reports/software_checks/continuation_rerun_offline_executed.ipynb`. No live API requests were made.

The previous bounded-order design notes follow; the continuation changes above supersede their original scoring description.

---

# Fresh rerun: conclusions and changes

1. **The million-unit outcome is prevented mechanically.** New weekly orders must be integers from 0 to 40 in the response schema, application validation and simulator. An invalid order cannot mutate game state. GPT orders are never clipped to fit.
2. **The earlier design contributed to the risk.** It explicitly presented 1,000,000 as an allowed order. Ten generated orders matched that boundary. This suggests possible anchoring but does not prove why the model chose it. Copying observations correctly was not enough evidence of sensible management.
3. **The next run uses GPT-5.4 nano, low versus medium effort.** This is a new prospective protocol, not a continuation of the old minimal/low GPT-5 nano sample. Improved strategy remains unverified until the user runs it.
4. **This is a modified, bounded-order Beer Game.** Forty is a researcher-selected limit: ten times initial customer demand and five times later customer demand. It is not claimed to be a universal Beer Game rule or a validated human maximum. The same limit applies to all roles and conditions; future demand is not revealed to agents.
5. **Ready to rerun the four complete games; not yet declared ready for a powered H1/H2 study.** Defaults: one group per cell, four roles per group, 36 weeks, $0.75 local allowance. Completion within that allowance is not guaranteed. No live requests were made during preparation.

## How to run

Open `START_HERE_bounded_rerun.ipynb`, beside `bounded_experiment.py`. Restart the kernel, run all cells, and enter the key in the hidden prompt. The free estimator checks run first. The final cell creates the report even if the run stops. Keep the prepared settings; this fresh run must not reuse old-model game decisions.

## Instructions and decisions

- The common instructions explicitly state cumulative holding/backlog costs and that minimizing orders is not the objective. Backlog persists; excess inventory costs money. The maximum is a limit, not a target.
- Zero remains legal and is not automatically an error. No positive-order minimum, target ordering formula, preferred beta or preferred treatment-effect sign is supplied.
- Current observations remain last in the input; readbacks precede the chosen order. Historical records remain available. Rules checks and exact readback validation remain active.
- Training and control lessons remain unchanged. Both conditions receive the same revised economic instructions and order limit. The shared framing can influence both conditions, so old and new results must not be pooled.
- Holding cost stays 0.50 and backlog cost 1.00 per unit per week. No factory fee, sales revenue or profit objective is introduced. Initial stock, flow, demand path and shipping/production delays remain as before.

## Measurement and audit

The estimator predicts `min(40, max(0, forecast + alpha * (target - net_inventory - beta * supply_line)))` for the new trajectories. It does not fit the old unbounded equation to capped choices. Fewer than eight strictly interior orders makes a role's beta unusable. Other identification checks remain active. Known-beta recovery under the upper cap is included in the free self-check.

The report retains zero-order rates, cap-hit rates, performance, first-attempt reliability, all failures, retries and group replacements. A condition with more than 20% cap hits triggers a pilot warning about a potentially binding limit. That threshold is a disclosed design choice, not a validated universal cutoff or a rule for selecting statistically favorable data. Completed groups are not discarded for poor performance, unusable beta or an undesired hypothesis result.

H1 concerns training. H2_API now contrasts low/medium API reasoning, not the reflection's human 60/120-second deadlines. The order limit can alter the treatment effect and reduce identification; neither this cap nor a different model guarantees significant results.

## Operational settings

Four workers, new request starts at least three seconds apart, shared cooldown and bounded transport retries remain. All retries and replacement groups count against the same $0.75 local allowance. Correctness failures get at most three attempts; then an entire group may be replaced, at most three replacements per target. Replacement selection still prevents confirmatory p-values. The allowance is an estimate/reservation guard, not an account billing setting.

At 596 initial requests and three-second pacing, request starts alone span about 30 minutes before additional latency/cooldowns. Cached requests on a later resume do not incur that delay. The pricing table is updated to GPT-5.4 nano: $0.20 input, $0.02 cached input, $1.25 output per million tokens. Low/medium token use is not yet measured; the earlier model's cost is not a reliable prediction.

## Validation

20 offline/mocked tests passed: response limits, rejection before state mutation, simulator conservation, capped beta recovery, zero/boundary identification, pricing, retries, quota versus rate limits, group replacement limits, caching and resume, and prompt history/readback integrity. The complete notebook is also executed in offline mode; its saved output is a synthetic software check, not GPT evidence.

Official model and pricing reference: https://developers.openai.com/api/docs/models/gpt-5.4-nano
