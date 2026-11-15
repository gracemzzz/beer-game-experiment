# H1 and H2 presentation image

[PNG](H1_H2_CONCLUSIONS.png) · [PDF](H1_H2_CONCLUSIONS.pdf) · [SVG](H1_H2_CONCLUSIONS.svg) · [Exact values](H1_H2_CONCLUSIONS_VALUES.csv)

Only the original H1 and H2 results are shown. The requested presentation labels map to the frozen conditions as follows:

| Presentation label | Actual prompt condition |
|---|---|
| No time constraint | 120 fictional seconds + control reading |
| Time constraint | 8 fictional seconds + the same control reading |

“No time constraint” is a presentation shorthand for the adequate-time scenario, not a literal unlimited student allowance. Both conditions had unrestricted actual model runtime. These data are LLM portrayals, not observations of human students.

Condition values are means across ten chains. Every displayed mean difference is **Time constraint minus No time constraint**. Percent change uses the no-time-constraint mean as its denominator. The 95% intervals are the existing paired-block bootstrap intervals for the mean difference; they are not intervals for individual condition means. The tests are the original exact two-sided paired sign-flip tests with ten matched pairs; the Holm adjustment is retained across the original five planned tests even though only H1 and H2 are displayed. No new tests, exclusions or participants were added.

H1 pipeline response is the chain's average of eight matched probe slopes: (order with low outstanding supply − order with high outstanding supply) / increase in outstanding cases. The condition value averages ten chains. It measures responsiveness, not an independently identified optimal supply-line weight.

H2 cost is the sum of 0.5 × remaining inventory + 1 × backlog across four roles and 24 weeks for a chain, then averaged across ten chains. Its unit is game cost units per chain.

The exact source is [HYPOTHESIS_COMPARISONS.csv](../../tables/HYPOTHESIS_COMPARISONS.csv). The original conclusions images, full report and other figures are preserved. Rebuild offline with `python scripts/export_exp14_h1_h2.py` from the repository root; no model calls are made.
