# Batch 3 comparison complete

18 October 2026. **Progress: 6/20 responses.** Task `b0003_g01_ample` supplies all 2,000 weekly orders and 100 probe pairs for batch 3's 180-second scenario. It passed validation unchanged, without formatting conversion or decision edits. The original attachment is preserved byte-for-byte; SHA-256: `a534913e78839259a1e428648deaf551cd4befa03195d3245d1427dd7fe07fc4`.

## Three-batch results

The current matched sample contains 75 chains and 300 fictional identities, each appearing in both deadline scenarios. It has 600 condition-specific role trajectories, not 600 independent students. Repeat generations remain pending.

| Outcome | 10-second mean | 180-second mean | Brief minus ample | Descriptive direction |
| --- | ---: | ---: | ---: | --- |
| H1: pipeline sensitivity | 0.513333 | 0.955556 | -0.442222 | Predicted |
| H2: full chain cost | 1,056.706667 | 1,071.733333 | -15.026667 | Opposite |
| H3: bullwhip ratio | 1.144638 | 1.287239 | -0.142602 | Opposite |

**Batch 3 alone follows all three predicted directions:** H1 difference -0.366667, H2 difference +87.280000, and H3 difference +0.224700. H2/H3 therefore differ in direction from batches 1 and 2, whose accepted results remain unchanged. The three-batch averages still put H2/H3 opposite to their predictions. This variation is retained; no outcome is replaced and the collection plan is unchanged.

Batch 3 changes **877/2,000 paired orders (43.85%)**, bringing the total to **2,718/6,000 (45.3%)**. These are descriptive differences in generated scenarios, not confirmation or rejection of actual human time-pressure hypotheses.

Batch 3's full-cost difference of +87.28 comprises +4.52 during model-decision weeks and +82.76 during automatic continuation. Across all three batches, these components average +1.546667 and -16.573333, yielding the combined -15.026667. Practice costs are equal. Continuation is a fixed scoring rule, not additional model decision evidence.

[Updated report and six figures](analysis/e6653b46e6f6/REPORT.md) · [Excel workbook](analysis/e6653b46e6f6/RESULTS.xlsx) · [Saved checks and provenance](B0003_G01_AMPLE_CHECK.json).

## Checks and settings

Checks passed for all 12,000 saved orders, 600 probe pairs, 21,600 replayed role-states, ten workbook sheets and six PNG/PDF figure pairs. All eight notebook cells passed, including 75 interactive chains. Direct new-chain H1/H3 calculations, matched contrasts and holding/backlog costs reconcile. All 48 earlier raw files, earlier batch contrasts and both earlier-study report selections remain unchanged. No scientific code, frozen prompts or collection rules changed, and no API calls occurred.

Settings follow established user-reported **GPT-6 / Pro** instructions. Provider snapshot, UI mode, fresh-chat use and full prompt submission are not independently verified. Fictional deadlines do not impose or measure model thinking time; generated identities share cohort responses and are not independent human observations. No inferential p-values are reported. The assistant pilot remains separate.

**Next:** send the full [batch 4, 180-second prompt](prompts/b0004_g01_ample.md) in a **fresh GPT-6 / Pro chat**, without earlier replies, then return the complete JSON here. The frozen plan alternates which deadline comes first. Notebook 07 sections 3–4 show 6/20 and the next prompt; section 7 refreshes analysis.
