# Experiment 14: presentation conclusions

[Slide PNG](CONCLUSIONS_SLIDE.png) · [Vector PDF](CONCLUSIONS_SLIDE.pdf) · [Editable SVG](CONCLUSIONS_SLIDE.svg)

The 16:9 slide summarizes the five existing planned comparisons, using condition means before percentage changes. Titles are 28–34 pt; means are 30 pt; percentage changes are 26 pt; outcome labels are 20 pt. Units and method notes remain explicit.

## Reading the slide

- Left column: 120 seconds + control reading → 8 seconds + the same control reading. H1 measures pipeline response; H2 measures cumulative holding plus backlog cost.
- Right column: 8 seconds + control reading → 8 seconds + causal education. H3 measures pipeline response; H4a measures order variance; H4b measures bullwhip.
- Each arrow lists the first named condition's mean and then the second named condition's mean. Percent change = 100 × (second mean − first mean) / first mean. It is a descriptive ratio of condition means, not the mean of individual percentage changes.
- The shared p-value is the existing exact two-sided paired sign-flip result after Holm adjustment across all five original tests: 0.009765625 each, displayed as 0.0098. There are ten matched differences per test, not forty independent participants.

## Measured quantities

- Pipeline response: for each chain, average eight matched probe slopes, (order at low outstanding replenishment − order at high outstanding replenishment) / increase in outstanding cases; then average ten chains. It measures responsiveness, not an identified optimal behavioral weight.
- Total cost: for each chain, sum 0.5 × remaining inventory + 1 × backlog across four roles and 24 weeks, then average ten chain totals. Units are game cost units per chain.
- Order variance: calculate each role's sample variance of 24 weekly orders (divisor 23), average four roles, then average ten chains. Units are cases squared.
- Bullwhip: divide each role's sample order variance by its own chain's sample final-consumer-demand variance; average four roles, then ten chains. The ratio is unitless.

This is a concise conclusion graphic. Exact mean differences, original paired-bootstrap 95% intervals, raw p-values, adjusted p-values and displayed percentages are retained in [DISPLAYED_VALUES.csv](DISPLAYED_VALUES.csv). Full definitions and inference limits remain in [the current report](../../REPORT.md). [Original detailed conclusions image](../../../analysis/student_framing_v3/publication_review/CONCLUSIONS.png) remains unchanged as a reference. The mean-interval figures are still available in [the control-reading figure set](../control_reading_only/README.md).

The sample consists of LLM responses to fictional time allowances, with unrestricted actual model runtime. The 8/120-second settings were not established by human deadline calibration. The observations do not establish effects on real students or optimal supply-line underweighting. The requested model was GPT-6 Astra with extra-high effort; that label is not provider-authenticated provenance.

Rebuild offline from the repository root with `python scripts/export_exp14_conclusions.py`. No new data collection, model calls or hypothesis tests. The original image, canonical publication and existing control-reading figures are preserved; hashes are recorded in [MANIFEST.json](MANIFEST.json).
