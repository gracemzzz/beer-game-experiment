# Measured outcomes: control reading only

**120 seconds + control reading versus 8 seconds + control reading.** These figures add a two-condition view of the closed experiment-14 data. The existing figures remain unchanged.

[Overview PNG](00_ALL_MEASURED_OUTCOMES.png) · [Overview PDF](00_ALL_MEASURED_OUTCOMES.pdf) · [All seven figures in one PDF](ALL_CONTROL_FIGURES.pdf) · [Existing figure set](../README.md)

Each unconnected dot is one chain. Diamonds and printed numbers are means across ten chains per condition. The x-axis gives the fictional time allowance, with the same control reading in both conditions. Each y-axis names its measured quantity and unit. No confidence intervals or new significance tests are plotted.

The six individual figures use a 16:9 slide layout with 22-point axis labels and tick labels. The overview uses 18-point axis labels and 16-point tick labels. Use PDF or SVG for scalable slide graphics; PNG copies are also provided.

These are absolute measured values. Fictional student seconds do not restrict actual model runtime. Only the two control-reading conditions enter these plots; the education condition remains in the original report and figures.

| Measured quantity | 120 seconds + control reading | 8 seconds + control reading | Unit |
|---|---:|---:|---|
| Pipeline response | 0.318837 | 0.196007 | order cases / outstanding case |
| Total holding + backlog cost | 574.45 | 642.95 | game cost units / chain |
| Inventory-holding cost | 562.65 | 622.65 | game cost units / chain |
| Backlog cost | 11.80 | 20.30 | game cost units / chain |
| Weekly order variance | 12.4501 | 17.8294 | cases² |
| Bullwhip ratio | 1.8310 | 2.6016 | dimensionless ratio |

[Exact condition means and SDs](CONDITION_MEANS.csv) · [Every plotted chain value](CHAIN_VALUES.csv) · [Machine-readable axis definitions](FIGURE_DEFINITIONS.json)

## Pipeline response

[PNG](01_PIPELINE_RESPONSE.png) · [PDF](01_PIPELINE_RESPONSE.pdf) · [SVG](01_PIPELINE_RESPONSE.svg)

Within each chain, average the 8 matched probe slopes: (order with low outstanding replenishment − order with high outstanding replenishment) / increase in outstanding cases. Then average 10 chains.

## Total holding + backlog cost

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

Pipeline response is a responsiveness proxy rather than an identified optimal supply-line weight. Total cost equals holding cost plus backlog cost. Order variance and bullwhip here are descriptive comparisons between the control-reading conditions; the original H4 tests compare different conditions and are not redefined.

Rebuild offline from the repository root: `python scripts/export_exp14_control_figures.py`. No model calls. [Preservation and source hashes](MANIFEST.json).
