# API study: imagined pressure in the Beer Game

Prospectively specified 20 October 2026. This is a new study, separate from all completed samples. The owner authorized a **$5 total cap**, including technical pilots, failed requests and transport retries, and **80 fictional testers per model**. No claim is made that fictional students are human observations.

## Questions and interpretation

**H1:** Within an information-sharing environment, a binding decision-time constraint increases the underweighting of outstanding replenishment orders relative to adequate decision time.

**H2:** Supply chains operating under a binding decision-time constraint incur higher cumulative total inventory-holding and backlog costs than supply chains operating with adequate decision time.

This experiment provides exploratory operational comparisons of those questions. Its treatment asks the model to represent students experiencing **strong time pressure** or **no time pressure**. It does not enforce or measure a binding deadline. A result about this framing cannot establish the literal human-time hypotheses. The prompt contains neither hypothesis directions nor desired outcomes.

## Fixed design

- Models requested: `gpt-6-luna`, `gpt-5.6-luna`, `gpt-5.6-sol`, and `claude-haiku-5-5`. Provider access and actual returned model IDs must be recorded; unavailable models are not silently substituted.
- Each model: 80 distinct fictional role identities, 20 chains, ten chains per condition. Across four models there are 320 main-sample role instances and 80 chains. Matched scenarios across models are not additional human participants.
- A chain has retailer, wholesaler, distributor and factory. **One fresh main request returns all 20 chains for a model**, including both classroom situations, with their complete trajectories and state probes. No previous reply is supplied. There are four main API requests total, one per model.
- Ten matched blocks per model. Each block shares a customer-demand path and personality-to-role assignment, but has two distinct chain/identity slots. Condition assignment to those slots is randomized before generation. Chain order inside each cohort is shuffled prospectively. Randomization does not make jointly generated chains independent.
- Exactly **24 model-decision weeks**. No practice weeks and no automatic continuation contribute to primary cost. Initial stock is 12 cases per role, backlog zero, and a steady flow of four cases is already in transit/production.
- Customer demand is a frozen independent uniform-integer path from 0 through 8, created with seed `2026102003` and separate pilot/main seed ranges. Main paths are matched between arms and models.
- API reasoning effort is `low`. The whole-response output cap is **8,192 tokens for each two-chain pilot** and **16,384 tokens for each 20-chain main response**. Both classroom conditions share the same request and settings. Actual temperature and all other generation settings are recorded. The output cap is a serialization allowance, not the experimental treatment.

## Physical rules and information

Reuse the unchanged `BeerGame` implementation. Each week receives deliveries, processes incoming demand and shipments, assesses holding/backlog cost, and then accepts orders. Holding costs $0.50 per case/week and backlog costs $1 per case/week. There is no revenue, manufacturing charge, ordering fee or capacity limit. Orders cannot be canceled. Factory production takes three weeks; upstream order transmission takes one week and a dispatched shipment takes two weeks. Supplier shortages can delay delivery further.

Fictional students can use local state/history and the four current inventories. The generator nevertheless sees all roles, all chains, both classroom situations and future demand because it emits the entire cohort. Instructions cannot enforce information isolation. Shared context permits cross-chain and cross-condition influence. Physical replay verifies accounting; any nonnegative order matrix can generate consistent physical states, so replay alone does not validate the decision process. Three exact inventory readbacks per chain at weeks 1, 12 and 24 provide additional, limited checks of state tracking.

No positive-order floor, preferred maximum, interior-order requirement, induced mistakes or imposed demand-following policy is used. A 100,000-case numerical circuit breaker rejects a payload without clipping; it is not advertised as an action target. Zero, repeated and large admissible orders are retained regardless of direction.

## H1 measurement

Each chain also answers 16 separate, neutrally labeled hypothetical states: four roles × two backlog levels (8 and 24) × two outstanding-pipeline levels (8 and 32). Inventory is zero, current demand 8, received/shipped quantities 4, awaiting dispatch zero, and other-role shared inventories 12. Displayed future arrivals sum to the outstanding pipeline. Factory displays include an additional zero third-week completion. These post-shipment states are physically possible. Probe order is shuffled prospectively and matched between treatments.

The primary H1 proxy is the average of eight matched sensitivities:

`S = (order at 8 outstanding cases − order at 32 outstanding cases) / 24`.

The contrast is `S_strong − S_no`; the predicted direction is negative. This measures response to pipeline variation. It does not identify the original dynamic structural β, and lower sensitivity can reflect a generally weaker response to state rather than pipeline-specific neglect.

A supplementary backlog sensitivity is the average order increase when backlog rises from 8 to 24, divided by 16. The pipeline/backlog sensitivity ratio is reported only when the absolute backlog response is at least 0.02. It remains a descriptive relative probe weight, not the original structural β, and is not a primary test or a substitute when H1 is unfavorable. The full probe grid remains available.

## H2 measurement

Primary H2 is total chain holding plus backlog cost summed over all four roles and **weeks 1–24 only**. The contrast is `cost_strong − cost_no`; the predicted direction is positive. Holding and backlog components, trajectories, zero-order counts, and final stock/backlog/outstanding commitments are also reported.

No automatic continuation is included. This prevents a mechanical continuation policy from determining the primary contrast, but costs incurred after week 24 are omitted. Final-state liabilities must remain visible. The generator sees the horizon, even though the fictional decision-maker is instructed to use only current/past information.

## Technical pilot, failures and stopping

Before main collection, request exactly one **two-chain pilot cohort per model**, containing one disjoint matched pair: four pilot responses total, separate from the four main responses and from main analysis. Thus the plan has **eight API response slots total**. The pilot uses the same technical gate for both conditions: exact JSON schema/types/IDs/counts; all three common factual rules correct; all 24 complete four-role order rows per chain; all 16 probe choices per chain; and exact post-shipment inventory readbacks at weeks 1, 12 and 24 for every chain.

**All four entire pilot responses must pass before any main request begins.** This common gate prevents proceeding only with models that happened to produce technically acceptable pilots. The gate does not consider cost, sensitivity, effect direction, p-values, zero orders, extreme but admissible orders, or whether the conditions differ. A failed pilot remains failed; a substantive technical fix needs a new frozen protocol/source identity and a separate explicit prospective collection plan. No retry-until-correct, outcome-based model selection, replacement chain, missing-choice imputation or additional sampling is allowed.

Main responses have the same validation. A main cohort is accepted only when all 20 chains pass. Invalid or incomplete outputs remain in raw evidence; valid-looking portions of a failed response are not promoted into an accepted cohort. There is no semantic retry. Transient transport failures may receive only the API runner's prospectively bounded same-request retries, with all attempts and unknown charges reserved against the **same $5 cumulative cap**. Stop at the fixed slots or budget/access limit and report partial completion. Resuming never purchases a completed or terminally rejected slot again.

## Analysis and evidence

Each model has **one jointly generated main response**, containing ten matched pairs of fictional chains. Roles, weeks, probes, chains and both classroom situations inside that response are dependent. The four different models are comparisons of different generators, not interchangeable replications of one model.

Report descriptive mean contrasts, each matched-pair contrast, costs and probe quantities separately by model. Direction labels are “predicted,” “opposite,” or “zero”; they do not mean a hypothesis has been proven or statistically supported. There are **no p-values, inferential confidence intervals, significance statements, independent-chain tests or bootstrap intervals**. An incomplete or rejected cohort has no accepted main comparison. The pilot is not added as a second main replication.

The whole-cohort request is an explicit economy/completion choice. It provides model-generated scenario patterns with a transparent fixed sample. It cannot establish literal binding-time effects, human behavior, or an independently replicated causal effect. A future inferential study would require a separate prospectively specified collection with independent requests/replications and an adequate manipulation of decision resources.

Freeze plan, full prompts, schema, source bytes and IDs before generation. Preserve exact raw provider responses and failures; record actual model IDs, effort, token use, latency, provider status and cumulative dollar accounting. The model returns choices and factual readbacks; Python independently computes all states, costs and analyses. Software fixtures remain explicitly synthetic and outside model evidence.
