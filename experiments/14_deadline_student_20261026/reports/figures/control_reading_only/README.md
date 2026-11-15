# Measured outcomes: control reading only

**120 seconds + control reading versus 8 seconds + control reading.** These figures add a two-condition view of the closed experiment-14 data. The existing figures remain unchanged.

[Overview PNG](00_ALL_MEASURED_OUTCOMES.png) · [Overview PDF](00_ALL_MEASURED_OUTCOMES.pdf) · [All seven figures in one PDF](ALL_CONTROL_FIGURES.pdf) · [Existing figure set](../README.md)

**Slide overview:** the two large upper panels combine each H1/H2 prediction with its observed result, condition means and **95% confidence bands**. H1 predicts greater pipeline underweighting under time constraint; its measured response proxy falls 38.5%. H2 predicts higher cumulative total holding and backlog cost; observed cost rises 11.9%. Percent change is `(8-second mean / 120-second mean − 1) × 100`; these are descriptive changes in condition means, with the original paired tests shown as **p < 0.01** after Holm correction. The lower four panels are explicitly descriptive, not additional H1/H2 tests. One shared color legend identifies blue = 120 seconds and orange = 8 seconds. Band width shows the condition-mean CI; its center mark and numeric label show the mean. Detailed individual figures retain chain dots and mean ± CI half-width labels; all exact statistics and calculations remain in the CSV files.

**Error-band calculation:** Pointwise 95% Student t interval for a condition mean: mean ± t(0.975, n−1) × SD / sqrt(n). Here n=10 chains per condition, df=9, and the critical t value is 2.262157163. SD is the sample standard deviation across chain scores. These are approximate pointwise mean intervals under independent, approximately normal chain-score assumptions; they are not SD bands, prediction intervals or simultaneous intervals. The dots show the observed spread.

**Terminology:** H1 is pipeline underweighting; the plotted response proxy is labeled on its x-axis. One case/case means one case of order reduction per additional outstanding case. Lower response is consistent with greater underweighting, but no optimal-response benchmark was estimated. The plotted values are response scores, not direct underweighting scores. H2 uses the full name total holding and backlog cost; this is the same quantity previously shortened to total cost. Labels changed; observations, means, intervals and tests did not.

**P-values:** pipeline underweighting's response proxy (H1) and total holding and backlog cost (H2) display the existing exact two-sided paired sign-flip p-values, Holm-adjusted across all five original planned tests: **p=0.009765625** each (raw p=0.001953125). Both compare **8 seconds + control reading minus 120 seconds + control reading**, using ten matched differences. Mean intervals describe each condition separately, while the tests use the pairing; overlapping mean intervals do not imply a nonsignificant paired comparison. The other four panels are descriptive: no primary test was planned for those outcomes with this two-condition comparison. No new hypothesis tests were added.

All figures use a 16:9 layout. The overview prioritizes H1/H2 with 22-point hypothesis headings, 19-point mean labels and 17-point axis labels; the four supplementary panels use 17-point titles and 15-point mean labels. Individual figures use 22-point axis labels and ticks. Use PDF or SVG for scalable slide graphics; PNG copies are also provided.

These are absolute measured values. Fictional student seconds do not restrict actual model runtime. Only the two control-reading conditions enter these plots; the education condition remains in the original report and figures.

| Measured quantity | 120 seconds + control reading: mean ± 95% CI margin | 8 seconds + control reading: mean ± 95% CI margin | Unit |
|---|---:|---:|---|
| Pipeline response | 0.318837 ± 0.023785 | 0.196007 ± 0.018531 | order cases / outstanding case |
| Total holding and backlog cost | 574.45 ± 34.55 | 642.95 ± 49.52 | game cost units / chain |
| Inventory-holding cost | 562.65 ± 32.67 | 622.65 ± 37.97 | game cost units / chain |
| Backlog cost | 11.80 ± 9.31 | 20.30 ± 13.64 | game cost units / chain |
| Weekly order variance | 12.4501 ± 3.5129 | 17.8294 ± 5.2822 | cases² |
| Bullwhip ratio | 1.8310 ± 0.5587 | 2.6016 ± 0.8020 | dimensionless ratio |

[Exact means, SDs and CI limits](CONDITION_MEANS.csv) · [Every plotted chain value](CHAIN_VALUES.csv) · [Saved p-value annotations](TEST_ANNOTATIONS.csv) · [Machine-readable axis definitions](FIGURE_DEFINITIONS.json)

## Pipeline response

[PNG](01_PIPELINE_RESPONSE.png) · [PDF](01_PIPELINE_RESPONSE.pdf) · [SVG](01_PIPELINE_RESPONSE.svg)

Within each chain, average the 8 matched probe slopes: (order with low outstanding replenishment − order with high outstanding replenishment) / increase in outstanding cases. Then average 10 chains.

## Total holding and backlog cost

[PNG](02_TOTAL_COST.png) · [PDF](02_TOTAL_COST.pdf) · [SVG](02_TOTAL_COST.svg)

Sum (0.5 × remaining inventory + 1 × unfilled demand) across all 4 roles and 24 weeks for each chain. Then average 10 chain totals.

## Inventory-holding cost

[PNG](03_HOLDING_COST.png) · [PDF](03_HOLDING_COST.pdf) · [SVG](03_HOLDING_COST.svg)

Sum 0.5 × remaining inventory across all 4 roles and 24 weeks for each chain. Then average 10 chain totals.

## Backlog cost

[PNG](04_BACKLOG_COST.png) · [PDF](04_BACKLOG_COST.pdf) · [SVG](04_BACKLOG_COST.svg)

Sum 1 × unfilled demand across all 4 roles and 24 weeks for each chain. Then average 10 chain totals.

## Weekly order variance

[PNG](05_ORDER_VARIANCE.png) · [PDF](05_ORDER_VARIANCE.pdf) · [SVG](05_ORDER_VARIANCE.svg)

For each role, calculate sample variance of its 24 weekly orders: sum of squared deviations from that role's mean divided by 23. Average the 4 role variances, then average 10 chains.

## Bullwhip ratio

[PNG](06_BULLWHIP.png) · [PDF](06_BULLWHIP.pdf) · [SVG](06_BULLWHIP.svg)

Within each chain, divide each role's 24-week sample order variance by that chain's 24-week sample final-consumer-demand variance. Average its 4 role ratios, then average 10 chains. Do not divide pooled means.

Pipeline response is a responsiveness proxy rather than an identified optimal supply-line weight. Total holding and backlog cost equals the sum of the two separately plotted cost components. Order variance and bullwhip here are descriptive comparisons between the control-reading conditions; the original H4 tests compare different conditions and are not redefined.

Rebuild offline from the repository root: `python scripts/export_exp14_control_figures.py`. No model calls. [Preservation and source hashes](MANIFEST.json).
