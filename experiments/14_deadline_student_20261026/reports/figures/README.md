# Experiment 14: current figures

All figures use the completed student_framing_v3 main sample. **120 s and 8 s describe fictional students; actual model runtime was unrestricted.**

[Full report](../REPORT.md) · [Report PDF](../REPORT.pdf) · [All figures in one PDF](ALL_FIGURES.pdf) · [Tables and exact values](../tables/README.md)

## Measured outcome values by condition

[PNG](01_CONDITION_VALUES.png) · [SVG](01_CONDITION_VALUES.svg) · [PDF](01_CONDITION_VALUES.pdf) · [Exact numbers](../tables/CONDITION_OUTCOMES.csv)

X: assigned fictional allowance and reading. Y: named outcome with units. Ten small dots per condition are chain values; diamonds and labels are arithmetic condition means. The plot shows levels, not treatment differences.

**Calculation:** Four unique dependent variables support five planned tests; pipeline response is used in both H1 and H3.

## Effect of the fictional time allowance

[PNG](02_PRESSURE_COMPARISON.png) · [SVG](02_PRESSURE_COMPARISON.svg) · [PDF](02_PRESSURE_COMPARISON.pdf) · [Exact numbers](../tables/HYPOTHESIS_COMPARISONS.csv)

X: ten matched blocks and the overall mean. Y: difference in the named dependent variable, in its stated units. The first named condition minus the second is used in every panel. The zero line means equal outcomes; bars are pointwise 95% paired-block bootstrap intervals.

**Calculation:** 8 s + control reading minus 120 s + control reading. H1: For each of 8 matched scenario pairs: (order at low outstanding quantity − order at high outstanding quantity) / (high − low outstanding quantity). Average the 8 slopes equally. H2: Sum (0.5 × end-of-week inventory + 1 × end-of-week backlog) across 4 roles and 24 weeks.

## Effect of causal education under the 8-second framing

[PNG](03_EDUCATION_COMPARISON.png) · [SVG](03_EDUCATION_COMPARISON.svg) · [PDF](03_EDUCATION_COMPARISON.pdf) · [Exact numbers](../tables/HYPOTHESIS_COMPARISONS.csv)

X: ten matched blocks and the overall mean. Y: difference in the named dependent variable, in its stated units. The first named condition minus the second is used in every panel. The zero line means equal outcomes; bars are pointwise 95% paired-block bootstrap intervals.

**Calculation:** 8 s + causal education minus 8 s + control reading. H3: For each of 8 matched scenario pairs: (order at low outstanding quantity − order at high outstanding quantity) / (high − low outstanding quantity). Average the 8 slopes equally. H4a: For each role, sum the squared deviations of its 24 orders from its own mean, divide by 23, then average the 4 role variances. H4b: Within each chain, divide each role's 24-week sample order variance by the 24-week sample variance of final-consumer demand; average the 4 ratios. Then average chains. Do not divide pooled condition means.

## Observed differences by fixed block count

[PNG](04_SAMPLE_SIZE_EFFECTS.png) · [SVG](04_SAMPLE_SIZE_EFFECTS.svg) · [PDF](04_SAMPLE_SIZE_EFFECTS.pdf) · [Exact numbers](../tables/SAMPLE_SIZE_VALUES.csv)

X: n matched blocks, equivalent to n chains in each of the three conditions and 3n separate contexts in total. Y: arithmetic mean of the first n paired differences, with outcome units. Every panel names the subtraction. N=10 is the primary sample.

**Calculation:** For each endpoint and n, mean_difference(n) = sum of block differences 1 through n / n. Individual chain metrics follow the same fixed formulas as the main results.

## Adjusted p-values by fixed block count

[PNG](05_SAMPLE_SIZE_PVALUES.png) · [SVG](05_SAMPLE_SIZE_PVALUES.svg) · [PDF](05_SAMPLE_SIZE_PVALUES.pdf) · [Exact numbers](../tables/SAMPLE_SIZE_VALUES.csv)

X: n matched blocks (= n chains per condition; 3n contexts total). Y: Holm-adjusted two-sided p-value on a log scale. One line represents all five coincident endpoint curves. The dashed line is 0.05, not a target used to select the sample.

**Calculation:** Exact paired sign-flip p-values for the first n block differences, adjusted together across the five preplanned endpoints. n=1 has no test; n=10 is primary.
