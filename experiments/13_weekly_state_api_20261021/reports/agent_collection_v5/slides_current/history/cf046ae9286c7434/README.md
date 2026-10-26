# Current figures for your slides

1. **Use this current export rather than the frozen first-run slides for the latest evidence.**
2. **Show the observed effect with its p-value.** Full tables, raw p-values and Holm-adjusted p-values are in the [current report](../REPORT.md).
3. **Both review status and individual repeats are visible.** Opposite or zero results are retained.

## Slide 1 — Conclusions for H1, H2, H3, H4a and H4b

[PNG](HYPOTHESIS_CONCLUSIONS.png) · [SVG](HYPOTHESIS_CONCLUSIONS.svg) · [PDF](HYPOTHESIS_CONCLUSIONS.pdf)

**Caption:** H1/H3 measure response to outstanding orders, H2 measures total cost, and H4 measures order variance and bullwhip. The table reports signed mean differences, raw two-sided p-values and Holm-adjusted p-values. Values average reviewed contexts only; review counts remain explicit.

## Slide 2 — Replication stability

[PNG](CURRENT_REPLICATION_RESULTS.png) · [SVG](CURRENT_REPLICATION_RESULTS.svg) · [PDF](CURRENT_REPLICATION_RESULTS.pdf)

**Caption:** Each point is one complete AI context with 50 chains per condition. The H2 and H4 contrasts vary across repeated contexts; the early Sol directions reverse in its second completed run. Open markers have incomplete provenance review, and filled markers passed the recorded procedure review. These are descriptive observations.

## Slide 3 — H1–H4 effects versus chain count

[PNG](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.png) · [SVG](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.svg) · [PDF](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.pdf)

**Caption:** Each curve recomputes a context's H1–H4 contrast using its first 5–50 chains per condition. Green marks the predicted direction. Stability along a curve describes sensitivity to chain count; agreement across separate curves describes repeatability across contexts. Neither substitutes for an independent-context significance test.

## What the quantities mean

- **H1/H3 pipeline sensitivity:** how much the order falls for each extra case already on the way. Zero means no reaction; one means one fewer case ordered per additional outstanding case.
- **H2 cost:** 24-week holding plus backlog costs, summed across all four roles and averaged per chain.
- **H4a order variance:** how much weekly orders fluctuate; averaged over roles and chains, in cases squared.
- **H4b bullwhip:** order variance divided by external customer-demand variance; a ratio of two means twice the demand variance.
- **Comparisons:** H1/H2 = B−A; H3/H4 = C−B. Predicted signs: H1 negative, H2 positive, H3 positive, H4 negative.

[Exact slide data](plotted_replication_values.csv) · [Current report and all extracted results](../REPORT.md) · [Export hashes](MANIFEST.json).

Model labels/settings are client-requested, all high effort. A/B/C share one context; the intervention changes revision opportunities rather than enforcing a clock deadline. No real-student validation is available.

Rebuild: `.venv/Scripts/python.exe scripts/export_agent_current_slide_v5.py` after refreshing the report. Prior exports are preserved in history/.
