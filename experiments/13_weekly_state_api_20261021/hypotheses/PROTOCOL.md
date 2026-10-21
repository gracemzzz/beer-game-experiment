# Experiment 13: weekly batches with Python-maintained states

Prepared prospectively on 21 October 2026 after the owner approved weekly API batches and continuing the **same cumulative $5 allowance**. This is separate from experiment 12; its failures, accepted Sol cohort and all spending remain unchanged.

## Questions and design

**H1:** Within an information-sharing environment, a binding decision-time constraint increases the underweighting of outstanding replenishment orders relative to adequate decision time.

**H2:** Supply chains operating under a binding decision-time constraint incur higher cumulative total inventory-holding and backlog costs than supply chains operating with adequate decision time.

These exact hypotheses motivate an **exploratory pressure-framing simulation**. The prompts describe students experiencing strong pressure or no pressure. They do not enforce actual time, cognitive pressure, or different reasoning resources. Results cannot establish the literal binding-time or human-behavior claims.

- Requested models: GPT-6 Luna, GPT-5.6 Luna, GPT-5.6 Sol and Claude Haiku 5.5, with actual API model IDs recorded.
- **80 main fictional identities and 20 chains per model**, ten chains per condition, four roles per chain. Ten blocks match demand paths and personality-to-role assignments; each condition has distinct identities. Across models there are 320 main fictional role instances.
- **24 main decision weeks**, all chosen by the model. No practice or automatic continuation contributes to primary cost.
- One request per model/week supplies current Python-calculated displays and returns **80 orders**. Python commits those orders and calculates the next week before requesting it. No future demand realization or future-week action is requested or supplied.
- A separate **full-size 20-chain one-week technical pilot per model** checks the same 80-order response structure. Pilot identities and demand seeds are disjoint from the main sample. Its 80 additional technical role instances per model are not included in the 80-person main sample.
- After all 24 weeks for a model, one request collects 16 matched hypothetical state choices per chain (320 probe choices). Exactly **104 planned API response slots**: four pilots, 96 weekly batches, four probe batches.
- Per-model technical gate: a model's own pilot must pass before its main weeks begin. One model's failure does not block the other models; missing models remain visible, and no alternative model is substituted.

## Model settings and output structure

All three OpenAI models use reasoning effort `none`. Claude uses disabled thinking with low output effort. Settings are the same for both classroom situations within each model. Whole-response output caps are **2,048 tokens** for a pilot/weekly order batch and **4,096 tokens** for probes. These are output allowances, not experimental pressure treatments. Provider settings differ and do not support a clean causal comparison of model identity alone.

The response is a fixed object. Every assigned chain ID is a required key. Weekly choices require the four role keys `r`, `w`, `d`, `f`; probes require all 16 neutral probe IDs. Shared nonrecursive `$defs`/`$ref` schemas avoid repeating the same role schema twenty times. Local validation independently rejects missing/extra IDs, Booleans, decimals, strings, nulls, negative choices and values above the 100,000-case technical guard. The guard is not advertised as a preferred maximum. No completion flag can substitute for actual choices.

The model returns decisions only. It does not calculate or report inventory, costs, checkpoints, p-values or summaries. Python calculates those quantities from the accepted literal orders. This removes the demonstrated whole-trajectory bookkeeping failure, but does not establish that each chosen order is optimal or human-like.

## Physical rules and displayed information

Reuse the unchanged four-role BeerGame simulator. Initial inventory is 12 cases per role, backlog zero and 12 outstanding cases per role. The retailer, wholesaler and distributor each have `[4,4]` deliveries due, plus four cases awaiting dispatch. Factory completions are `[4,4,4]`. Initial upstream incoming orders are four. Subsequent customer demand is independent uniform integers from 0 through 8, frozen before collection using seed `2026102107` and separate pilot/main seed ranges.

Each week receives arrivals, processes incoming demand, ships against backlog plus demand, assesses costs, then accepts the new orders. Holding cost is $0.50 per remaining case/week; backlog cost is $1 per unfilled case/week. There is no revenue, production fee, ordering charge, discount or capacity limit. Orders cannot be canceled. New replenishment arrives no sooner than three weeks later and can be delayed by upstream shortage; factory production arrives after three weeks without an extra upstream supplier delay.

Each role's current display includes inventory, backlog, outstanding orders, incoming demand, received quantity and shipped quantity. The supplied history contains only the last four completed weeks of incoming demand and that role's submitted orders. The four current inventories in a chain provide information sharing. The model sees the batch's other private role fields and other chains; instructions ask it to respect each student's local information but cannot enforce actual isolation. Joint generation also couples chains and conditions. No independent-agent, independent-chain or human sampling claim is made.

The researcher fixes the scoring horizon at 24 weeks, but the API prompt supplies only the current week and does **not reveal the eventual stopping week** to the fictional students. Their stated objective is cumulative team cost over the continuing game. This avoids supplying advance terminal-week information; it does not remove the analysis limitation that consequences after the chosen 24-week scoring window are unmeasured.

Zero, repeated, constant, large admissible and identical choices across conditions are all permitted. No desired strategy, inventory target, pipeline-neglect bias, bullwhip pattern, positive-order floor, artificial diversity or favorable hypothesis direction is supplied.

## Outcomes

**H1 proxy:** Each role answers the same separate displays at backlog 8/24 and outstanding pipeline 8/32. Inventory is zero, incoming demand 8, received/shipped 4, awaiting dispatch 0, and other-role inventories 12. Future arrivals sum to the stated pipeline. Neutral probe IDs and order are frozen. Average `(order with pipeline 8 − order with pipeline 32)/24` across eight role/backlog comparisons per chain. Contrast strong minus no pressure; the hypothesized direction is negative. Lower sensitivity is not an identified structural β and can reflect generally weak responsiveness rather than pipeline-specific neglect.

Supplementary backlog response and the pipeline/backlog response ratio may be shown, with the ratio withheld when the absolute backlog response is below 0.02. These are descriptive measures and do not replace an unfavorable primary result.

**H2:** Cumulative holding plus backlog cost over four roles and exactly 24 main weeks. Contrast strong minus no pressure; the hypothesized direction is positive. A model must complete all 24 weekly batches before H2 becomes a primary comparison. Partial observed costs remain separately labeled and are never compared as full-horizon outcomes. H2 can be reported if all 24 weeks complete even when its subsequent H1 probe response fails.

Report individual chains, condition means, paired contrasts, holding/backlog components, zero-order counts, order range and final stock/backlog/outstanding commitments. A supplementary bullwhip ratio is each role's sample order variance divided by external customer-demand variance, averaged across roles; zero-variance denominators remain missing. No subsequent automatic costs are added, so terminal commitments are shown separately.

## Acceptance, fixed stopping and shared spending

The technical pilot gate checks complete literal choices and the fixed schema, not the direction of H1/H2, order variance, zero choices, a preferred strategy or statistical significance. It establishes formatting feasibility at full batch size, not validated human behavior. Every weekly request is rebuilt from accepted previous orders and the unchanged physical simulator. A missing or rejected week stops that model; no later state is fabricated. Probe requests require all 24 accepted main weeks.

Keep every exact request, raw provider response, failure, usage record and model identifier. Invalid generated content receives no semantic retry, replacement chain or repaired order. Only the transport layer's prospectively bounded same-payload technical retries are allowed. All costs and unknown-charge reservations count against the **existing experiment-12 $5 ledger**. The portable relative reference to that folder is frozen in the plan, together with hashes of all earlier ledger entries. New runs must not reset or erase earlier charges. Stop at the fixed response slots or remaining budget/access limit, and report partial status.

Earlier files and completed samples remain immutable. The new plan, source snapshots, schema version and dynamic request evidence identify this separate design. Actual prompts contain current data only. Failed responses are not promoted to accepted records by calculating replacement numbers in Python; Python only evolves state after valid model-supplied choices.

## Interpretation

All results are **descriptive**: direction may be predicted, opposite or zero. No p-values, inferential confidence intervals, independent-chain significance or proof/nullification claims are made. Shared batches, imagined pressure, different provider settings and fictional identities limit generalization. Fixing state accounting makes the experiment executable and auditable; it does not guarantee heterogeneous orders, a treatment effect or support for H1/H2.
