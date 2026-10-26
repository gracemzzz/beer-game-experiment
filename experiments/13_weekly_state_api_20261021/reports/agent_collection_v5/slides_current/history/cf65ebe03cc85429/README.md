# Current figures for your slides

1. **Use this current export rather than the frozen first-run slides for the latest evidence.**
2. **Show the observed effect with its p-value.** Full tables, raw p-values and Holm-adjusted p-values are in the [current report](../REPORT.md).
3. **Both review status and individual repeats are visible.** Opposite or zero results are retained.

## Slide 1 — Conclusions for H1, H2, H3, H4a and H4b

[PNG](HYPOTHESIS_CONCLUSIONS.png) · [SVG](HYPOTHESIS_CONCLUSIONS.svg) · [PDF](HYPOTHESIS_CONCLUSIONS.pdf)

**Caption:** H1/H3 measure response to outstanding orders, H2 measures total cost, and H4 measures order variance and bullwhip. The table reports signed mean differences, raw two-sided p-values and Holm-adjusted p-values. Values average reviewed contexts only; review counts remain explicit.

## Slide 2 — Model comparison, same reviewed sample as the statistics

[PNG](MODEL_COMPARISON_REVIEWED.png) · [SVG](MODEL_COMPARISON_REVIEWED.svg) · [PDF](MODEL_COMPARISON_REVIEWED.pdf)

**Caption:** All five outcomes are shown in one clean slide: H1, H2, H3, H4a and H4b. Dots show model means; labels show mean differences and raw p-values. H1/H3 axes use ×10⁻⁴. Reviewed contexts: Astra2, Sol2, Luna3.

## Slide 3 — H1–H4 effects versus chain count

[PNG](../chain_size_stability/H1_H4_CHAIN_SIZE_REVIEWED.png) · [SVG](../chain_size_stability/H1_H4_CHAIN_SIZE_REVIEWED.svg) · [PDF](../chain_size_stability/H1_H4_CHAIN_SIZE_REVIEWED.pdf)

**Caption:** Bold curves show equal-context model means, recalculated using the first 5–50 chains per condition in each reviewed run. Faint curves show the individual reviewed runs. Independent sample counts stay at 2/2/3; the 50-chain endpoints match the statistics table. H1/H3 axes magnify very small differences.

## Supplementary: all recorded non-excluded contexts

[All-recorded run chart](CURRENT_REPLICATION_RESULTS.png) and [all-recorded chain-prefix curves](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.png) retain the earlier views, including pending-review runs. They use a broader descriptive sample than the primary statistics.

## What the quantities mean

- **H1/H3 pipeline sensitivity:** how much the order falls for each extra case already on the way. Zero means no reaction; one means one fewer case ordered per additional outstanding case.
- **H2 cost:** 24-week holding plus backlog costs, summed across all four roles and averaged per chain.
- **H4a order variance:** how much weekly orders fluctuate; averaged over roles and chains, in cases squared.
- **H4b bullwhip:** order variance divided by external customer-demand variance; a ratio of two means twice the demand variance.
- **Comparisons:** H1/H2 = B−A; H3/H4 = C−B. Predicted signs: H1 negative, H2 positive, H3 positive, H4 negative.

[Exact slide data](plotted_replication_values.csv) · [Current report and all extracted results](../REPORT.md) · [Export hashes](MANIFEST.json).

Model labels/settings are client-requested, all high effort. A/B/C share one context; the intervention changes revision opportunities rather than enforcing a clock deadline. No real-student validation is available.

Rebuild: `.venv/Scripts/python.exe scripts/export_agent_current_slide_v5.py` after refreshing the report. Prior exports are preserved in history/.
