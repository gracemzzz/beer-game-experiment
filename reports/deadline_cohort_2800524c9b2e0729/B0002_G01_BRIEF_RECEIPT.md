# Batch 2 comparison complete

18 October 2026. **Progress: 4/20 responses.** Task `b0002_g01_brief` supplies all 2,000 weekly orders and 100 probe pairs for batch 2's 10-second scenario. It passed validation unchanged, with no formatting conversion or decision edit. The original attachment is preserved byte-for-byte; SHA-256: `7d0d2595325ad92caece70fc328318775724451364529a4f78c51ccb8a1c844e`.

## Results so far

Two batch pairs now cover 50 matched chains and 200 fictional identities, each appearing in both scenarios. Repeated generations have not yet been collected.

| Outcome | 10-second mean | 180-second mean | Brief minus ample | Descriptive direction |
| --- | ---: | ---: | ---: | --- |
| H1: pipeline sensitivity | 0.520000 | 1.000000 | -0.480000 | Predicted |
| H2: full chain cost | 1,065.500 | 1,131.680 | -66.180 | Opposite |
| H3: bullwhip ratio | 1.178028 | 1.504280 | -0.326253 | Opposite |

Batch 2 alone has H1/H2/H3 differences of **-0.420000, -33.360000 and -0.042097**, respectively. Its 871/2,000 changed orders (43.55%) bring the two-batch total to **1,841/4,000 (46.025%)**. Batch 1's accepted decisions and contrasts remain unchanged.

H1 follows the predicted direction in both observed batches; H2/H3 point in the opposite direction in both. This is a partial descriptive comparison, not confirmation or rejection of human time-pressure hypotheses. The remaining batches and repeat generations will be collected under the unchanged plan, regardless of outcome direction.

For batch 2, the model-week cost difference is +2.94 while automatic continuation contributes -36.30, producing the full-cost difference of -33.36. Across both batches, these differences average +0.06 and -66.24. Practice costs are equal. Thus the lower full cost in the brief scenario comes from the fixed continuation; the model-decision-week mean costs are nearly equal. Continuation orders are scoring-rule actions, not additional model choices.

[Updated report and six figures](analysis/2e16d8a1a279/REPORT.md) · [Excel workbook](analysis/2e16d8a1a279/RESULTS.xlsx) · [Saved checks and provenance](B0002_G01_BRIEF_CHECK.json).

## Checks and settings

Checks passed for all 8,000 saved orders, 400 probe pairs, 14,400 replayed role-states, ten workbook sheets and six PNG/PDF figure pairs. All eight notebook cells passed, including 50 interactive chains. Direct H1/H3 calculations for the new chains, matched contrasts and holding/backlog costs reconcile. All 42 earlier run files and both earlier-study report selections remain unchanged. No scientific code, frozen prompts or collection rules changed, and no API calls occurred.

Settings follow established user-reported **GPT-6 / Pro** instructions; provider snapshot, mode, fresh-chat use and full prompt submission are not independently verified. Fictional deadlines do not impose or measure model thinking time. Generated identities share cohort responses and are not independent human observations; no inferential p-values are reported. The assistant pilot remains separate.

**Next:** send the complete [batch 3, 10-second prompt](prompts/b0003_g01_brief.md) in a **fresh GPT-6 / Pro chat** without earlier replies, then return its full JSON here. Notebook 07 sections 3–4 show 4/20 and the next prompt; section 7 refreshes analysis.
