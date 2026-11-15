# Slides: current experiment 14

[One-page conclusions PDF](CONCLUSIONS.pdf) ([text](CONCLUSIONS.md)) | [H1-H4](H1_H4.png) ([PDF](H1_H4.pdf), [SVG](H1_H4.svg)) | [Chain size](CHAIN_SIZE.png) ([PDF](CHAIN_SIZE.pdf), [SVG](CHAIN_SIZE.svg)) | [Both slides in PDF](SLIDE_FIGURES.pdf)

One Astra/xhigh model, ten matched chain pairs. Positive numbers mean the first named condition is higher. These are fictional student-pressure responses, with unlimited actual model time and no software answers.

| Hypothesis | Quantity | Mean contrast | Raw p | Holm 5 |
|---|---|---:|---:|---:|
| H1 B-A | Pipeline response | -0.1228 | 0.001953 | 0.009766 |
| H2 B-A | Total cost | 68.5 | 0.001953 | 0.009766 |
| H3 C-B | Pipeline response | 0.07411 | 0.001953 | 0.009766 |
| H4a C-B | Order variance | -7.725 | 0.001953 | 0.009766 |
| H4b C-B | Bullwhip | -1.117 | 0.001953 | 0.009766 |

All ten paired differences have the predicted sign for every endpoint. Thus the exact two-sided raw p is 2/1024 for each test; identical p-values and lower-panel curves are expected, while the effect magnitudes differ.

**H1-H4 slide:** dots show the ten paired differences; the diamond is their mean and the bar is a pointwise 95% interval. H1/H3 measure response to outstanding orders, H2 measures total holding/backlog cost, and H4a/b measure order variance and bullwhip.

**Chain-size slide:** the top row shows cumulative mean contrasts and the bottom row Holm-adjusted p-values across the same five outcomes at each fixed prefix of 1 through 10 pairs. Raw and adjusted values are in [the exact plotting data](CHAIN_SIZE.csv); n=1 p is unavailable. The final adjusted values exactly match the main results. N=10 is primary. These completed-sample sensitivity views do not predict a significance threshold or justify selecting a favorable sample size.

The pipeline quantity is a responsiveness proxy. No human students were observed; shared project context was visible to the agents. See [full report](../REPORT.pdf) and [context limitations](../CONTEXT.md).
