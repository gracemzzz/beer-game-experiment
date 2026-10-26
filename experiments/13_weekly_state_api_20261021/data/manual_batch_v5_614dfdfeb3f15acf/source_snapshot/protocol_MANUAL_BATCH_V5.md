# Larger manual collection, v5 — prospective amendment

1. The user requested more chains and statistics plotted against sample size. This new version increases each condition from 10 to **50 chains**, with 24 weeks unchanged. One model response contains 150 chain instances / 600 fictional roles, 14,400 weekly orders and 2,400 final probe choices. Four first responses contain 600 chain instances across the models. This is an increase in planned data, not collected evidence.
2. There are still exactly four reusable prompt files, one per requested model. Each prompt runs all three conditions and returns one JSON. All original v4 files remain unchanged and its sample is separate.
3. Model output is requested in pages of **25 chains (100 weekly choices)** or **100 probe choices**. All pages of an initial opportunity must complete before A begins its separate revision. Physical state advances only after all 50 chains' required choices are committed. A complete batch requires 224 page submissions. Long runs may encounter platform limits; incomplete data are retained and never filled.
4. The fresh chat remains the statistical cluster. More chains within one context do not become independent replications. The enlarged design retains the exploratory interpretation and limitations of the earlier joint-context approach.

## Fixed sample and measurements

Keep the same four requested models, fictional second-year University at Buffalo business-student profiles, matched 127-word readings, physical engine, 24-week scoring, decision opportunities and actual-settings provenance rules as [v4](MANUAL_BATCH_V4.md). The new coordinator uses the unchanged v3 engine. A is control plus separate reconsideration; B is control with initial choices committed; C is causal education with initial choices committed. The condition order is randomized once per fresh chat, recorded, and never selected based on outcomes. All conditions share demand/profile paths within the chat. Separate models do not have matched seeds.

Every page displays the same observable information for its requested chains using compact labeled arrays: role states, shared inventories, profiles and recent histories. Chains are separate supply chains; no other chain's state is needed for an individual order. The public page format, paging and longer context are changes to the model's experience, so v4 and v5 must not be pooled or described as merely adding rows to the same experiment. Probe pages use the same existing randomized state ordering and reveal every requested state before its choices. Page timing is not a calibrated human deadline.

Fixed maximum: **40 attempted fresh chats per model**, unchanged by outcomes. With 50 chains per condition this is 2,000 chains per condition / 6,000 total instances per model, and 24,000 total instances across four fully collected model samples. Failures count toward the attempted sample and remain in the intake log. Use the same prompt for a new chat; do not call another batch inside an existing conversation. No stopping or extension at the first significant result. Incomplete or unreviewed attempts cannot support full-sample confirmation. UUIDs do not prove independent model generations.

The raw measures are unchanged:

| Endpoint | Measure | Contrast, predicted direction |
|---|---|---|
| H1 | Mean matched pipeline sensitivity, (order at pipeline 8 − order at pipeline 32) / 24 | B − A < 0 |
| H2 | Cumulative 24-week holding plus backlog cost per chain | B − A > 0 |
| H3 | Mean matched pipeline sensitivity | C − B > 0 |
| H4a | Mean individual weekly order variance, ddof 1 | C − B < 0 |
| H4b | Mean individual order variance / chain external-demand variance | C − B < 0 |

Hypothesis directions appear in analysis documentation only, never in the decision prompts. Pipeline sensitivity is a proxy for outstanding-order responsiveness, not an identified normative underweighting coefficient. Zero demand variance stays undefined. Costs/variances are reconstructed from actual returned orders and Python states. Constant/zero choices, unchanged revisions and opposite effects stay in the dataset. No desired variability, ordering policy or forced interior orders are introduced.

## Two different size plots

**Within each response:** retain the deterministic first 5, 10, 20, 30, 40 and 50 chain IDs in all three conditions. Plot mean pipeline responsiveness, cost, order variance and bullwhip by condition, separately for each model. If several chats are available, average their prefix summaries equally. These curves are descriptive sensitivity to which chains are included. They have no independent-chain p-values or confidence intervals. They cannot show statistical significance from one response.

**Across fresh responses:** at the fixed first 1, 2, 5, 10, 20 and 40 reviewed complete chats, include all 50 chains per condition and aggregate them before testing. X axes show 50, 100, 250, 500, 1,000 and 2,000 chains per condition, plus a second axis with the actual fresh-chat counts. Plot the paired mean difference, pointwise 95% chat-bootstrap interval and two-sided sign-flip p-value adjusted by Holm across all 20 endpoints (five × four models, retaining missing slots). A single chat has no inferential interval or p-value. H4 requires both components in the predicted direction. Prefixes are descriptive accumulation checks, not repeated confirmatory decisions or a rule to stop collecting. Unknown/failed attempts and available-case selection are disclosed. Full-sample interpretation is exploratory even after all planned observations arrive.

Attempt order is recorded on first intake and preserved separately from filesystem modification dates. Continued or re-reviewed copies keep the same attempt identity and cannot count twice. Partial JSONs are retained. Original JSON, transcript and settings must be reviewed before a batch enters inference. No actual observations are substituted with resampled or programmed choices.

**Planning curves:** preserve the normal paired-chat-difference approximation and d=0/.2/.3/.5/.8 assumptions, two-sided alpha .05/20. Only the secondary conversion from chats to chains changes to 50 chains per condition per chat. A larger within-chat cohort does NOT automatically improve the assumed standardized between-chat effect. No old pilot variance is used to invent a required sample size. These curves show detection probabilities under assumptions, not observed statistics or a guaranteed significance threshold. The calculation uses the [SciPy noncentral t distribution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nct.html).

## Limits, accounting and reproducibility

The intervention is one versus two submission opportunities, not a measured or enforced clock/token budget. All three conditions share a model context; causal education may carry over. No real students validate the personas. These remain exploratory AI responses, not verification of literal human H1–H4. More data cannot correct those construct limitations or guarantee an effect.

No API calls or keys are used. The same cumulative $5 API ledger is unchanged. Website usage limits still apply. Do not silently reduce chain count, program an order policy, regenerate a more favorable result, or claim a partial run completed. If a platform cannot finish, retain the partial output and decide any protocol change before new collection.

New v5 source, prompts, ZIP, manifest, notebook and report are frozen separately. Reports preserve their previous publication bytes before new evidence replaces the current view. Validate full paged replay, partial-page preservation, rejected missing/duplicate/tampered choices, exact per-chain aggregation, no one-chat p-values, and all new notebook cells. Synthetic software checks are explicitly labeled and excluded from research data.
