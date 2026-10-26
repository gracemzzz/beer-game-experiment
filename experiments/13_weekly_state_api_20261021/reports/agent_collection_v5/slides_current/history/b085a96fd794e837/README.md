# Current figures for your slides

1. **Use this current export rather than the frozen first-run slides for the latest evidence.**
2. **H1–H4 are not statistically established.** Full tables, eligible counts and available adjusted p-values are in the [current report](../REPORT.md).
3. **Both review status and individual repeats are visible.** Opposite or zero results are retained.

## Slide 1 — Conclusions for H1, H2, H3, H4a and H4b

[PNG](HYPOTHESIS_CONCLUSIONS.png) · [SVG](HYPOTHESIS_CONCLUSIONS.svg) · [PDF](HYPOTHESIS_CONCLUSIONS.pdf)

**Caption:** H1 and H3 show no measured treatment differences in reviewed contexts. Cost, order-variance and bullwhip effects vary across models and repeated contexts. No hypothesis is statistically established in this three-round AI pilot. Values average reviewed contexts only; review counts remain explicit.

## Slide 2 — Replication stability

[PNG](CURRENT_REPLICATION_RESULTS.png) · [SVG](CURRENT_REPLICATION_RESULTS.svg) · [PDF](CURRENT_REPLICATION_RESULTS.pdf)

**Caption:** Each point is one complete AI context with 50 chains per condition. The H2 and H4 contrasts vary across repeated contexts; the early Sol directions reverse in its second completed run. Open markers have incomplete provenance review, and filled markers passed the recorded procedure review. These are descriptive observations.

## Slide 3 — H1–H4 effects versus chain count

[PNG](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.png) · [SVG](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.svg) · [PDF](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.pdf)

**Caption:** Each curve recomputes a context's H1–H4 contrast using its first 5–50 chains per condition. Green marks the predicted direction. Stability along a curve describes sensitivity to chain count; agreement across separate curves describes repeatability across contexts. Neither substitutes for an independent-context significance test.

[Exact slide data](plotted_replication_values.csv) · [Current report and all extracted results](../REPORT.md) · [Export hashes](MANIFEST.json).

Model labels/settings are client-requested, all high effort. A/B/C share one context; the intervention changes revision opportunities rather than enforcing a clock deadline. No real-student validation is available.

Rebuild: `.venv/Scripts/python.exe scripts/export_agent_current_slide_v5.py` after refreshing the report. Prior exports are preserved in history/.
