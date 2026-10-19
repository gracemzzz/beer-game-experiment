# Batch 4 comparison complete

18 October 2026. **Progress: 8/20 responses.** All 2,000 weekly orders and 100 probe pairs for `b0004_g01_brief` passed unchanged. The original attachment is preserved byte-for-byte, with no formatting conversion or decision edit.

## Results across four batches

We now have 100 matched teams containing 400 fictional identities, each appearing in both scenarios. Repeat generations have not yet been collected.

| Outcome | 10-second mean | 180-second mean | Brief minus ample | Direction |
| --- | ---: | ---: | ---: | --- |
| H1: pipeline sensitivity | 0.521667 | 0.883333 | -0.361667 | Predicted |
| H2: full team cost | 1,043.145 | 1,059.820 | -16.675 | Opposite |
| H3: bullwhip ratio | 1.148532 | 1.207696 | -0.059164 | Opposite |

**Batch 4 alone:** H1 difference -0.120000, H2 difference -21.620000 and H3 difference +0.191148. H1/H3 follow their predictions in this batch; H2 points the other way. Earlier batches' accepted decisions and comparisons are unchanged.

Batch 4 changes **906/2,000 paired orders (45.3%)**. Across all four batches, **3,624/8,000 orders changed (45.3%)**. These remain partial descriptive results; changing orders alone does not establish a deadline effect. The remaining collection plan is unchanged.

Batch 4's full-cost difference combines +5.70 during model-decision weeks and -27.32 during automatic continuation. Across four batches, these components average +2.585 and -19.260. Practice costs are equal. The continuation is calculated by Python, not additional model decisions.

[Simple study explanation](STUDY_EXPLAINED.md) · [Updated results and plots](analysis/d7b627a5ca8a/REPORT.md) · [Excel workbook](analysis/d7b627a5ca8a/RESULTS.xlsx) · [Checks and original-file hash](B0004_G01_BRIEF_CHECK.json).

## Checks

All 16,000 saved orders, 800 probe pairs, 28,800 replayed states, ten workbook sheets and six figure pairs passed checks. All eight notebook cells passed, with 100 interactive team charts. New-chain H1/H3 values and matched contrasts reconcile; all 54 earlier raw files and both earlier-study report selections remain unchanged. No scientific code, prompts or collection rules changed, and no API calls occurred.

Settings continue under user-reported **GPT-6 / Pro**, without independent verification of the provider, mode or chat submission. Fictional deadlines do not measure model thinking time, and generated students are not independent human participants. No inferential p-values are reported; the assistant pilot remains separate.

**Next:** send the entire [batch 5, 10-second prompt](prompts/b0005_g01_brief.md) in a **fresh GPT-6 / Pro chat**, without previous replies, then return its complete JSON here. Notebook 07 sections 3–4 show 8/20 and the next prompt; section 7 refreshes analysis.
