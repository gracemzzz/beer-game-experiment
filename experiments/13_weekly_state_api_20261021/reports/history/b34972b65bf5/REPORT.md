# Experiment 13: conclusions first

1. **Completion:** 4/4 models complete; 96/96 weekly batches, 4/4 pilots and 4/4 probe batches accepted.
2. **H1/H2:** gpt-6-luna H1: +0.0000; gpt-6-luna H2: +0.0000; gpt-5.6-luna H1: -0.0083; gpt-5.6-luna H2: +17.8500; gpt-5.6-sol H1: +0.0000; gpt-5.6-sol H2: +0.0000; claude-haiku-5-5 H1: -0.0146; claude-haiku-5-5 H2: -19.4000. These are descriptive strong-minus-no-pressure differences.
3. **Accounting:** Python calculates all inventory, deliveries, backlog and costs from accepted orders. Missing decisions remain missing.
4. **Meaning:** Imagined pressure framing, not an enforced deadline. H1 is a matched-state sensitivity proxy, not structural β. Batched fictional chains are dependent; no p-values are reported.
5. **Shared budget:** $1.179072 charged/reserved across experiments 12 and 13; $3.820928 remains within the original $5 cap.

## Completion by model

| model | accepted_pilot_responses | accepted_weeks | accepted_probe_responses | complete |
| --- | --- | --- | --- | --- |
| gpt-6-luna | 1 | 24 | 1 | True |
| gpt-5.6-luna | 1 | 24 | 1 | True |
| gpt-5.6-sol | 1 | 24 | 1 | True |
| claude-haiku-5-5 | 1 | 24 | 1 | True |

A complete model has an accepted full-size format pilot, all 24 weekly batches and its probe batch. Pilot choices are excluded from the main outcomes. Partial games are exported for diagnosis but cannot supply 24-week H2 costs.

## Hypotheses

| model | hypothesis | paired_blocks | mean_strong_minus_no | descriptive_direction |
| --- | --- | --- | --- | --- |
| gpt-6-luna | H1 | 10 | 0.0000 | zero |
| gpt-6-luna | H2 | 10 | 0.0000 | zero |
| gpt-5.6-luna | H1 | 10 | -0.0083 | predicted |
| gpt-5.6-luna | H2 | 10 | 17.8500 | predicted |
| gpt-5.6-sol | H1 | 10 | 0.0000 | zero |
| gpt-5.6-sol | H2 | 10 | 0.0000 | zero |
| claude-haiku-5-5 | H1 | 10 | -0.0146 | predicted |
| claude-haiku-5-5 | H2 | 10 | -19.4000 | opposite |

**H1 proxy:** For otherwise matched states, (order with 8 outstanding cases − order with 32 outstanding cases) / 24. Average over roles and backlog states, then compare matched pressure conditions. A negative difference follows the predicted proxy direction. This does not identify an optimal weight or establish literal underweighting.

**H2:** Sum of $0.50 × end-of-week inventory + $1.00 × backlog over four roles and exactly 24 weeks. A positive difference follows the prediction. There is no revenue or production fee. Terminal inventory, backlog and outstanding orders are reported; unplayed future weeks carry no invented costs.

A null or opposite comparison is a valid result. The protocol does not change prompts, sample size, prices or ordering rules to obtain significance.

## Means by condition

| model | condition | chains | weeks_observed | sensitivity | total_cost | observed_cost_partial |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-6-luna | no_pressure | 10 | 24 | 0.6667 | 570.6000 | 570.6000 |
| gpt-6-luna | strong_pressure | 10 | 24 | 0.6667 | 570.6000 | 570.6000 |
| gpt-5.6-luna | no_pressure | 10 | 24 | 0.0000 | 557.1000 | 557.1000 |
| gpt-5.6-luna | strong_pressure | 10 | 24 | -0.0083 | 574.9500 | 574.9500 |
| gpt-5.6-sol | no_pressure | 10 | 24 | 0.5833 | 647.8500 | 647.8500 |
| gpt-5.6-sol | strong_pressure | 10 | 24 | 0.5833 | 647.8500 | 647.8500 |
| claude-haiku-5-5 | no_pressure | 10 | 24 | -0.0375 | 803.5500 | 803.5500 |
| claude-haiku-5-5 | strong_pressure | 10 | 24 | -0.0521 | 784.1500 | 784.1500 |

## Chain performance

| model | block | condition | weeks_observed | complete | holding_cost | backlog_cost | total_cost | observed_cost_partial | sensitivity | zero_orders | max_order | final_inventory | final_backlog | final_supply_line | bullwhip |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-6-luna | 6 | no_pressure | 24 | True | 480.5000 | 2 | 482.5000 | 482.5000 | 0.6667 | 0 | 4 | 37 | 0 | 48 | 0.0000 |
| gpt-6-luna | 0 | strong_pressure | 24 | True | 580.5000 | 0 | 580.5000 | 580.5000 | 0.6667 | 0 | 8 | 45 | 0 | 48 | 0.0220 |
| gpt-6-luna | 1 | no_pressure | 24 | True | 610.0000 | 0 | 610.0000 | 610.0000 | 0.6667 | 0 | 6 | 45 | 0 | 48 | 0.0056 |
| gpt-6-luna | 6 | strong_pressure | 24 | True | 480.5000 | 2 | 482.5000 | 482.5000 | 0.6667 | 0 | 4 | 37 | 0 | 48 | 0.0000 |
| gpt-6-luna | 3 | strong_pressure | 24 | True | 637.0000 | 0 | 637.0000 | 637.0000 | 0.6667 | 0 | 4 | 51 | 0 | 48 | 0.0000 |
| gpt-6-luna | 9 | no_pressure | 24 | True | 485.5000 | 0 | 485.5000 | 485.5000 | 0.6667 | 0 | 7 | 39 | 0 | 48 | 0.0187 |
| gpt-6-luna | 7 | no_pressure | 24 | True | 613.0000 | 0 | 613.0000 | 613.0000 | 0.6667 | 0 | 4 | 47 | 0 | 48 | 0.0000 |
| gpt-6-luna | 4 | strong_pressure | 24 | True | 476.0000 | 10 | 486.0000 | 486.0000 | 0.6667 | 0 | 6 | 38 | 0 | 48 | 0.0087 |
| gpt-6-luna | 3 | no_pressure | 24 | True | 637.0000 | 0 | 637.0000 | 637.0000 | 0.6667 | 0 | 4 | 51 | 0 | 48 | 0.0000 |
| gpt-6-luna | 5 | strong_pressure | 24 | True | 660.0000 | 0 | 660.0000 | 660.0000 | 0.6667 | 0 | 5 | 58 | 0 | 48 | 0.0015 |
| gpt-6-luna | 9 | strong_pressure | 24 | True | 485.5000 | 0 | 485.5000 | 485.5000 | 0.6667 | 0 | 7 | 39 | 0 | 48 | 0.0187 |
| gpt-6-luna | 1 | strong_pressure | 24 | True | 610.0000 | 0 | 610.0000 | 610.0000 | 0.6667 | 0 | 6 | 45 | 0 | 48 | 0.0056 |
| gpt-6-luna | 8 | no_pressure | 24 | True | 450.0000 | 57 | 507.0000 | 507.0000 | 0.6667 | 0 | 6 | 33 | 14 | 48 | 0.0095 |
| gpt-6-luna | 5 | no_pressure | 24 | True | 660.0000 | 0 | 660.0000 | 660.0000 | 0.6667 | 0 | 5 | 58 | 0 | 48 | 0.0015 |
| gpt-6-luna | 8 | strong_pressure | 24 | True | 450.0000 | 57 | 507.0000 | 507.0000 | 0.6667 | 0 | 6 | 33 | 14 | 48 | 0.0095 |
| gpt-6-luna | 2 | no_pressure | 24 | True | 644.5000 | 0 | 644.5000 | 644.5000 | 0.6667 | 0 | 7 | 48 | 0 | 48 | 0.0122 |
| gpt-6-luna | 2 | strong_pressure | 24 | True | 644.5000 | 0 | 644.5000 | 644.5000 | 0.6667 | 0 | 7 | 48 | 0 | 48 | 0.0122 |
| gpt-6-luna | 7 | strong_pressure | 24 | True | 613.0000 | 0 | 613.0000 | 613.0000 | 0.6667 | 0 | 4 | 47 | 0 | 48 | 0.0000 |
| gpt-6-luna | 0 | no_pressure | 24 | True | 580.5000 | 0 | 580.5000 | 580.5000 | 0.6667 | 0 | 8 | 45 | 0 | 48 | 0.0220 |
| gpt-6-luna | 4 | no_pressure | 24 | True | 476.0000 | 10 | 486.0000 | 486.0000 | 0.6667 | 0 | 6 | 38 | 0 | 48 | 0.0087 |
| gpt-5.6-luna | 6 | no_pressure | 24 | True | 471.5000 | 0 | 471.5000 | 471.5000 | 0.0000 | 0 | 8 | 37 | 0 | 48 | 0.0539 |
| gpt-5.6-luna | 0 | strong_pressure | 24 | True | 524.5000 | 248 | 772.5000 | 772.5000 | 0.0000 | 0 | 12 | 41 | 24 | 120 | 0.5526 |
| gpt-5.6-luna | 1 | no_pressure | 24 | True | 602.0000 | 0 | 602.0000 | 602.0000 | 0.0000 | 0 | 8 | 45 | 0 | 48 | 0.0448 |
| gpt-5.6-luna | 6 | strong_pressure | 24 | True | 471.5000 | 0 | 471.5000 | 471.5000 | 0.0000 | 0 | 8 | 37 | 0 | 48 | 0.0539 |
| gpt-5.6-luna | 3 | strong_pressure | 24 | True | 607.0000 | 6 | 613.0000 | 613.0000 | 0.0000 | 0 | 8 | 41 | 2 | 74 | 0.1286 |
| gpt-5.6-luna | 9 | no_pressure | 24 | True | 481.5000 | 0 | 481.5000 | 481.5000 | 0.0000 | 0 | 8 | 39 | 0 | 48 | 0.0401 |
| gpt-5.6-luna | 7 | no_pressure | 24 | True | 605.0000 | 0 | 605.0000 | 605.0000 | 0.0000 | 0 | 8 | 47 | 0 | 48 | 0.0473 |
| gpt-5.6-luna | 4 | strong_pressure | 24 | True | 451.0000 | 14 | 465.0000 | 465.0000 | 0.0000 | 0 | 8 | 30 | 5 | 75 | 0.1744 |
| gpt-5.6-luna | 3 | no_pressure | 24 | True | 611.0000 | 4 | 615.0000 | 615.0000 | 0.0000 | 0 | 8 | 43 | 2 | 72 | 0.1242 |
| gpt-5.6-luna | 5 | strong_pressure | 24 | True | 641.5000 | 3 | 644.5000 | 644.5000 | 0.0000 | 1 | 8 | 49 | 1 | 73 | 0.1962 |
| gpt-5.6-luna | 9 | strong_pressure | 24 | True | 481.5000 | 0 | 481.5000 | 481.5000 | -0.0833 | 0 | 8 | 39 | 0 | 48 | 0.0401 |
| gpt-5.6-luna | 1 | strong_pressure | 24 | True | 602.0000 | 0 | 602.0000 | 602.0000 | 0.0000 | 0 | 8 | 45 | 0 | 48 | 0.0448 |
| gpt-5.6-luna | 8 | no_pressure | 24 | True | 393.0000 | 39 | 432.0000 | 432.0000 | 0.0000 | 0 | 8 | 6 | 11 | 89 | 0.2852 |
| gpt-5.6-luna | 5 | no_pressure | 24 | True | 660.0000 | 0 | 660.0000 | 660.0000 | 0.0000 | 1 | 8 | 58 | 0 | 48 | 0.0503 |
| gpt-5.6-luna | 8 | strong_pressure | 24 | True | 393.0000 | 39 | 432.0000 | 432.0000 | 0.0000 | 0 | 8 | 6 | 11 | 89 | 0.2852 |
| gpt-5.6-luna | 2 | no_pressure | 24 | True | 630.5000 | 32 | 662.5000 | 662.5000 | 0.0000 | 0 | 8 | 40 | 7 | 74 | 0.1248 |
| gpt-5.6-luna | 2 | strong_pressure | 24 | True | 630.5000 | 32 | 662.5000 | 662.5000 | 0.0000 | 0 | 8 | 40 | 7 | 74 | 0.1248 |
| gpt-5.6-luna | 7 | strong_pressure | 24 | True | 605.0000 | 0 | 605.0000 | 605.0000 | 0.0000 | 0 | 8 | 47 | 0 | 48 | 0.0473 |
| gpt-5.6-luna | 0 | no_pressure | 24 | True | 545.5000 | 30 | 575.5000 | 575.5000 | 0.0000 | 0 | 8 | 31 | 4 | 78 | 0.1696 |
| gpt-5.6-luna | 4 | no_pressure | 24 | True | 452.0000 | 14 | 466.0000 | 466.0000 | 0.0000 | 0 | 8 | 28 | 5 | 75 | 0.1615 |
| gpt-5.6-sol | 6 | no_pressure | 24 | True | 476.5000 | 215 | 691.5000 | 691.5000 | 0.5833 | 27 | 28 | 0 | 78 | 179 | 3.9185 |
| gpt-5.6-sol | 0 | strong_pressure | 24 | True | 576.0000 | 272 | 848.0000 | 848.0000 | 0.5833 | 28 | 30 | 149 | 8 | 28 | 5.5986 |
| gpt-5.6-sol | 1 | no_pressure | 24 | True | 467.5000 | 80 | 547.5000 | 547.5000 | 0.5833 | 30 | 16 | 65 | 9 | 17 | 1.3267 |
| gpt-5.6-sol | 6 | strong_pressure | 24 | True | 476.5000 | 215 | 691.5000 | 691.5000 | 0.5833 | 27 | 28 | 0 | 78 | 179 | 3.9185 |
| gpt-5.6-sol | 3 | strong_pressure | 24 | True | 537.0000 | 80 | 617.0000 | 617.0000 | 0.5833 | 30 | 22 | 18 | 37 | 97 | 2.0250 |
| gpt-5.6-sol | 9 | no_pressure | 24 | True | 549.5000 | 116 | 665.5000 | 665.5000 | 0.5833 | 30 | 28 | 11 | 45 | 143 | 3.3752 |
| gpt-5.6-sol | 7 | no_pressure | 24 | True | 476.5000 | 69 | 545.5000 | 545.5000 | 0.5833 | 32 | 10 | 4 | 19 | 65 | 0.9123 |
| gpt-5.6-sol | 4 | strong_pressure | 24 | True | 436.0000 | 138 | 574.0000 | 574.0000 | 0.5833 | 20 | 18 | 8 | 48 | 141 | 2.9968 |
| gpt-5.6-sol | 3 | no_pressure | 24 | True | 537.0000 | 80 | 617.0000 | 617.0000 | 0.5833 | 30 | 22 | 18 | 37 | 97 | 2.0250 |
| gpt-5.6-sol | 5 | strong_pressure | 24 | True | 598.0000 | 22 | 620.0000 | 620.0000 | 0.5833 | 39 | 12 | 32 | 12 | 28 | 0.6294 |
| gpt-5.6-sol | 9 | strong_pressure | 24 | True | 549.5000 | 116 | 665.5000 | 665.5000 | 0.5833 | 30 | 28 | 11 | 45 | 143 | 3.3752 |
| gpt-5.6-sol | 1 | strong_pressure | 24 | True | 467.5000 | 80 | 547.5000 | 547.5000 | 0.5833 | 30 | 16 | 65 | 9 | 17 | 1.3267 |
| gpt-5.6-sol | 8 | no_pressure | 24 | True | 422.5000 | 88 | 510.5000 | 510.5000 | 0.5833 | 12 | 15 | 12 | 33 | 85 | 1.4401 |
| gpt-5.6-sol | 5 | no_pressure | 24 | True | 598.0000 | 22 | 620.0000 | 620.0000 | 0.5833 | 39 | 12 | 32 | 12 | 28 | 0.6294 |
| gpt-5.6-sol | 8 | strong_pressure | 24 | True | 422.5000 | 88 | 510.5000 | 510.5000 | 0.5833 | 12 | 15 | 12 | 33 | 85 | 1.4401 |
| gpt-5.6-sol | 2 | no_pressure | 24 | True | 643.0000 | 216 | 859.0000 | 859.0000 | 0.5833 | 39 | 28 | 132 | 13 | 39 | 4.4195 |
| gpt-5.6-sol | 2 | strong_pressure | 24 | True | 643.0000 | 216 | 859.0000 | 859.0000 | 0.5833 | 39 | 28 | 132 | 13 | 39 | 4.4195 |
| gpt-5.6-sol | 7 | strong_pressure | 24 | True | 476.5000 | 69 | 545.5000 | 545.5000 | 0.5833 | 32 | 10 | 4 | 19 | 65 | 0.9123 |
| gpt-5.6-sol | 0 | no_pressure | 24 | True | 576.0000 | 272 | 848.0000 | 848.0000 | 0.5833 | 28 | 30 | 149 | 8 | 28 | 5.5986 |
| gpt-5.6-sol | 4 | no_pressure | 24 | True | 436.0000 | 138 | 574.0000 | 574.0000 | 0.5833 | 20 | 18 | 8 | 48 | 141 | 2.9968 |
| claude-haiku-5-5 | 6 | no_pressure | 24 | True | 465.5000 | 488 | 953.5000 | 953.5000 | -0.0312 | 0 | 16 | 61 | 39 | 135 | 0.5926 |
| claude-haiku-5-5 | 0 | strong_pressure | 24 | True | 602.5000 | 62 | 664.5000 | 664.5000 | -0.0521 | 0 | 12 | 63 | 0 | 82 | 0.1780 |
| claude-haiku-5-5 | 1 | no_pressure | 24 | True | 602.0000 | 572 | 1,174.0000 | 1,174.0000 | -0.0521 | 0 | 16 | 69 | 40 | 144 | 0.4669 |
| claude-haiku-5-5 | 6 | strong_pressure | 24 | True | 465.5000 | 488 | 953.5000 | 953.5000 | -0.0521 | 0 | 16 | 61 | 39 | 135 | 0.5926 |
| claude-haiku-5-5 | 3 | strong_pressure | 24 | True | 621.0000 | 284 | 905.0000 | 905.0000 | -0.0521 | 0 | 16 | 79 | 24 | 120 | 0.5438 |
| claude-haiku-5-5 | 9 | no_pressure | 24 | True | 499.5000 | 0 | 499.5000 | 499.5000 | -0.0312 | 0 | 12 | 61 | 0 | 78 | 0.1858 |
| claude-haiku-5-5 | 7 | no_pressure | 24 | True | 621.0000 | 684 | 1,305.0000 | 1,305.0000 | -0.0521 | 0 | 16 | 67 | 40 | 152 | 0.6174 |
| claude-haiku-5-5 | 4 | strong_pressure | 24 | True | 485.0000 | 0 | 485.0000 | 485.0000 | -0.0521 | 0 | 12 | 60 | 0 | 78 | 0.2618 |
| claude-haiku-5-5 | 3 | no_pressure | 24 | True | 621.0000 | 284 | 905.0000 | 905.0000 | -0.0312 | 0 | 16 | 79 | 24 | 120 | 0.5438 |
| claude-haiku-5-5 | 5 | strong_pressure | 24 | True | 657.0000 | 0 | 657.0000 | 657.0000 | -0.0521 | 0 | 10 | 69 | 0 | 65 | 0.1354 |
| claude-haiku-5-5 | 9 | strong_pressure | 24 | True | 499.5000 | 0 | 499.5000 | 499.5000 | -0.0521 | 0 | 12 | 61 | 0 | 78 | 0.1858 |
| claude-haiku-5-5 | 1 | strong_pressure | 24 | True | 596.0000 | 400 | 996.0000 | 996.0000 | -0.0521 | 0 | 16 | 73 | 34 | 130 | 0.4706 |
| claude-haiku-5-5 | 8 | no_pressure | 24 | True | 437.5000 | 0 | 437.5000 | 437.5000 | -0.0312 | 0 | 12 | 41 | 0 | 78 | 0.2292 |
| claude-haiku-5-5 | 5 | no_pressure | 24 | True | 657.0000 | 0 | 657.0000 | 657.0000 | -0.0312 | 0 | 10 | 69 | 0 | 65 | 0.1354 |
| claude-haiku-5-5 | 8 | strong_pressure | 24 | True | 437.5000 | 0 | 437.5000 | 437.5000 | -0.0521 | 0 | 12 | 41 | 0 | 78 | 0.2292 |
| claude-haiku-5-5 | 2 | no_pressure | 24 | True | 632.5000 | 384 | 1,016.5000 | 1,016.5000 | -0.0312 | 0 | 16 | 76 | 33 | 129 | 0.4344 |
| claude-haiku-5-5 | 2 | strong_pressure | 24 | True | 632.5000 | 384 | 1,016.5000 | 1,016.5000 | -0.0521 | 0 | 16 | 76 | 33 | 129 | 0.4344 |
| claude-haiku-5-5 | 7 | strong_pressure | 24 | True | 631.0000 | 596 | 1,227.0000 | 1,227.0000 | -0.0521 | 0 | 16 | 71 | 32 | 144 | 0.5916 |
| claude-haiku-5-5 | 0 | no_pressure | 24 | True | 602.5000 | 0 | 602.5000 | 602.5000 | -0.0521 | 1 | 12 | 67 | 0 | 78 | 0.2283 |
| claude-haiku-5-5 | 4 | no_pressure | 24 | True | 485.0000 | 0 | 485.0000 | 485.0000 | -0.0312 | 0 | 12 | 60 | 0 | 78 | 0.2618 |

For an incomplete game, only observed partial costs are available. Do not compare them with full 24-week totals. Bullwhip tables use variance of a role’s weekly orders divided by variance of customer demand over the same observed weeks; a ratio above 1 indicates amplification. A zero denominator is undefined, not zero.

## Execution and model provenance

| task_id | model | phase | week | status | reason |
| --- | --- | --- | --- | --- | --- |
| gpt-6-luna_pilot | gpt-6-luna | pilot | — | accepted | — |
| gpt-6-luna_w01 | gpt-6-luna | main | 1 | accepted | — |
| gpt-6-luna_w02 | gpt-6-luna | main | 2 | accepted | — |
| gpt-6-luna_w03 | gpt-6-luna | main | 3 | accepted | — |
| gpt-6-luna_w04 | gpt-6-luna | main | 4 | accepted | — |
| gpt-6-luna_w05 | gpt-6-luna | main | 5 | accepted | — |
| gpt-6-luna_w06 | gpt-6-luna | main | 6 | accepted | — |
| gpt-6-luna_w07 | gpt-6-luna | main | 7 | accepted | — |
| gpt-6-luna_w08 | gpt-6-luna | main | 8 | accepted | — |
| gpt-6-luna_w09 | gpt-6-luna | main | 9 | accepted | — |
| gpt-6-luna_w10 | gpt-6-luna | main | 10 | accepted | — |
| gpt-6-luna_w11 | gpt-6-luna | main | 11 | accepted | — |
| gpt-6-luna_w12 | gpt-6-luna | main | 12 | accepted | — |
| gpt-6-luna_w13 | gpt-6-luna | main | 13 | accepted | — |
| gpt-6-luna_w14 | gpt-6-luna | main | 14 | accepted | — |
| gpt-6-luna_w15 | gpt-6-luna | main | 15 | accepted | — |
| gpt-6-luna_w16 | gpt-6-luna | main | 16 | accepted | — |
| gpt-6-luna_w17 | gpt-6-luna | main | 17 | accepted | — |
| gpt-6-luna_w18 | gpt-6-luna | main | 18 | accepted | — |
| gpt-6-luna_w19 | gpt-6-luna | main | 19 | accepted | — |
| gpt-6-luna_w20 | gpt-6-luna | main | 20 | accepted | — |
| gpt-6-luna_w21 | gpt-6-luna | main | 21 | accepted | — |
| gpt-6-luna_w22 | gpt-6-luna | main | 22 | accepted | — |
| gpt-6-luna_w23 | gpt-6-luna | main | 23 | accepted | — |
| gpt-6-luna_w24 | gpt-6-luna | main | 24 | accepted | — |
| gpt-6-luna_probe | gpt-6-luna | probe | — | accepted | — |
| gpt-5.6-luna_pilot | gpt-5.6-luna | pilot | — | accepted | — |
| gpt-5.6-luna_w01 | gpt-5.6-luna | main | 1 | accepted | — |
| gpt-5.6-luna_w02 | gpt-5.6-luna | main | 2 | accepted | — |
| gpt-5.6-luna_w03 | gpt-5.6-luna | main | 3 | accepted | — |
| gpt-5.6-luna_w04 | gpt-5.6-luna | main | 4 | accepted | — |
| gpt-5.6-luna_w05 | gpt-5.6-luna | main | 5 | accepted | — |
| gpt-5.6-luna_w06 | gpt-5.6-luna | main | 6 | accepted | — |
| gpt-5.6-luna_w07 | gpt-5.6-luna | main | 7 | accepted | — |
| gpt-5.6-luna_w08 | gpt-5.6-luna | main | 8 | accepted | — |
| gpt-5.6-luna_w09 | gpt-5.6-luna | main | 9 | accepted | — |
| gpt-5.6-luna_w10 | gpt-5.6-luna | main | 10 | accepted | — |
| gpt-5.6-luna_w11 | gpt-5.6-luna | main | 11 | accepted | — |
| gpt-5.6-luna_w12 | gpt-5.6-luna | main | 12 | accepted | — |
| gpt-5.6-luna_w13 | gpt-5.6-luna | main | 13 | accepted | — |
| gpt-5.6-luna_w14 | gpt-5.6-luna | main | 14 | accepted | — |
| gpt-5.6-luna_w15 | gpt-5.6-luna | main | 15 | accepted | — |
| gpt-5.6-luna_w16 | gpt-5.6-luna | main | 16 | accepted | — |
| gpt-5.6-luna_w17 | gpt-5.6-luna | main | 17 | accepted | — |
| gpt-5.6-luna_w18 | gpt-5.6-luna | main | 18 | accepted | — |
| gpt-5.6-luna_w19 | gpt-5.6-luna | main | 19 | accepted | — |
| gpt-5.6-luna_w20 | gpt-5.6-luna | main | 20 | accepted | — |
| gpt-5.6-luna_w21 | gpt-5.6-luna | main | 21 | accepted | — |
| gpt-5.6-luna_w22 | gpt-5.6-luna | main | 22 | accepted | — |
| gpt-5.6-luna_w23 | gpt-5.6-luna | main | 23 | accepted | — |
| gpt-5.6-luna_w24 | gpt-5.6-luna | main | 24 | accepted | — |
| gpt-5.6-luna_probe | gpt-5.6-luna | probe | — | accepted | — |
| gpt-5.6-sol_pilot | gpt-5.6-sol | pilot | — | accepted | — |
| gpt-5.6-sol_w01 | gpt-5.6-sol | main | 1 | accepted | — |
| gpt-5.6-sol_w02 | gpt-5.6-sol | main | 2 | accepted | — |
| gpt-5.6-sol_w03 | gpt-5.6-sol | main | 3 | accepted | — |
| gpt-5.6-sol_w04 | gpt-5.6-sol | main | 4 | accepted | — |
| gpt-5.6-sol_w05 | gpt-5.6-sol | main | 5 | accepted | — |
| gpt-5.6-sol_w06 | gpt-5.6-sol | main | 6 | accepted | — |
| gpt-5.6-sol_w07 | gpt-5.6-sol | main | 7 | accepted | — |
| gpt-5.6-sol_w08 | gpt-5.6-sol | main | 8 | accepted | — |
| gpt-5.6-sol_w09 | gpt-5.6-sol | main | 9 | accepted | — |
| gpt-5.6-sol_w10 | gpt-5.6-sol | main | 10 | accepted | — |
| gpt-5.6-sol_w11 | gpt-5.6-sol | main | 11 | accepted | — |
| gpt-5.6-sol_w12 | gpt-5.6-sol | main | 12 | accepted | — |
| gpt-5.6-sol_w13 | gpt-5.6-sol | main | 13 | accepted | — |
| gpt-5.6-sol_w14 | gpt-5.6-sol | main | 14 | accepted | — |
| gpt-5.6-sol_w15 | gpt-5.6-sol | main | 15 | accepted | — |
| gpt-5.6-sol_w16 | gpt-5.6-sol | main | 16 | accepted | — |
| gpt-5.6-sol_w17 | gpt-5.6-sol | main | 17 | accepted | — |
| gpt-5.6-sol_w18 | gpt-5.6-sol | main | 18 | accepted | — |
| gpt-5.6-sol_w19 | gpt-5.6-sol | main | 19 | accepted | — |
| gpt-5.6-sol_w20 | gpt-5.6-sol | main | 20 | accepted | — |
| gpt-5.6-sol_w21 | gpt-5.6-sol | main | 21 | accepted | — |
| gpt-5.6-sol_w22 | gpt-5.6-sol | main | 22 | accepted | — |
| gpt-5.6-sol_w23 | gpt-5.6-sol | main | 23 | accepted | — |
| gpt-5.6-sol_w24 | gpt-5.6-sol | main | 24 | accepted | — |
| gpt-5.6-sol_probe | gpt-5.6-sol | probe | — | accepted | — |
| claude-haiku-5-5_pilot | claude-haiku-5-5 | pilot | — | accepted | — |
| claude-haiku-5-5_w01 | claude-haiku-5-5 | main | 1 | accepted | — |
| claude-haiku-5-5_w02 | claude-haiku-5-5 | main | 2 | accepted | — |
| claude-haiku-5-5_w03 | claude-haiku-5-5 | main | 3 | accepted | — |
| claude-haiku-5-5_w04 | claude-haiku-5-5 | main | 4 | accepted | — |
| claude-haiku-5-5_w05 | claude-haiku-5-5 | main | 5 | accepted | — |
| claude-haiku-5-5_w06 | claude-haiku-5-5 | main | 6 | accepted | — |
| claude-haiku-5-5_w07 | claude-haiku-5-5 | main | 7 | accepted | — |
| claude-haiku-5-5_w08 | claude-haiku-5-5 | main | 8 | accepted | — |
| claude-haiku-5-5_w09 | claude-haiku-5-5 | main | 9 | accepted | — |
| claude-haiku-5-5_w10 | claude-haiku-5-5 | main | 10 | accepted | — |
| claude-haiku-5-5_w11 | claude-haiku-5-5 | main | 11 | accepted | — |
| claude-haiku-5-5_w12 | claude-haiku-5-5 | main | 12 | accepted | — |
| claude-haiku-5-5_w13 | claude-haiku-5-5 | main | 13 | accepted | — |
| claude-haiku-5-5_w14 | claude-haiku-5-5 | main | 14 | accepted | — |
| claude-haiku-5-5_w15 | claude-haiku-5-5 | main | 15 | accepted | — |
| claude-haiku-5-5_w16 | claude-haiku-5-5 | main | 16 | accepted | — |
| claude-haiku-5-5_w17 | claude-haiku-5-5 | main | 17 | accepted | — |
| claude-haiku-5-5_w18 | claude-haiku-5-5 | main | 18 | accepted | — |
| claude-haiku-5-5_w19 | claude-haiku-5-5 | main | 19 | accepted | — |
| claude-haiku-5-5_w20 | claude-haiku-5-5 | main | 20 | accepted | — |
| claude-haiku-5-5_w21 | claude-haiku-5-5 | main | 21 | accepted | — |
| claude-haiku-5-5_w22 | claude-haiku-5-5 | main | 22 | accepted | — |
| claude-haiku-5-5_w23 | claude-haiku-5-5 | main | 23 | accepted | — |
| claude-haiku-5-5_w24 | claude-haiku-5-5 | main | 24 | accepted | — |
| claude-haiku-5-5_probe | claude-haiku-5-5 | probe | — | accepted | — |

Requested model IDs are fixed in the plan. Provider-returned IDs and token usage are retained in the request records. OpenAI uses reasoning effort none; Claude uses disabled thinking and low effort. Weekly/pilot output allowances are 2,048 tokens; probe allowance is 4,096. Both conditions use the same generation settings. No temperature override is sent. These settings affect the simulation and limit comparison with previous higher-effort collections.

Only a transient transport, rate-limit or server failure can receive one further budgeted attempt. Invalid choices, refusals and incomplete outputs remain failures. A failed model blocks its remaining dependent tasks; other models can continue. Reopening the notebook reuses verified accepted responses. Unknown charges retain their reservation. Local accounting is a conservative estimate, not a provider invoice or account balance.

## Design and limits

Per model: 20 four-role chains, 10 matched pairs, 24 weeks. Python reveals current state and a short past history, then commits all submitted orders simultaneously. It does not reveal future demand to the model. The researcher scores 24 weeks, but the eventual stopping week is deliberately not revealed in the API prompts. All chain choices in a week are generated jointly; the model can see the whole batch. Prompted identity separation is not technical information isolation. No individual-agent or human replication is claimed.

- Pressure is fictional framing; actual time or reasoning resources do not differ by condition.
- All current roles/chains appear in a shared batch, so private information isolation and chain independence are not enforced.
- H1 is a matched-state sensitivity proxy, not the original structural beta or a human cognitive measurement.
- Only full 24-week chains contribute primary H2; partial accrued costs are separately labeled.
- Final commitments after week24 are displayed but subsequent costs are outside the primary horizon.
- Human observations=0. No p-values, independent-chain confidence intervals or hypothesis-proof claims.

## Files

- [Excel workbook](../../../analysis/weekly_api_c64d75aa3a03356f/b34972b65bf5/RESULTS.xlsx)
- [Weekly states and orders](../../../analysis/weekly_api_c64d75aa3a03356f/b34972b65bf5/rounds.csv)
- [Chain performance](../../../analysis/weekly_api_c64d75aa3a03356f/b34972b65bf5/chains.csv)
- [Probe choices](../../../analysis/weekly_api_c64d75aa3a03356f/b34972b65bf5/probes.csv)
- [Matched comparisons](../../../analysis/weekly_api_c64d75aa3a03356f/b34972b65bf5/contrasts.csv)
- [Frozen plan and execution evidence](../../../data/weekly_api_c64d75aa3a03356f)
- [Exact prompt archive](../../../prompts/weekly_api_c64d75aa3a03356f)
- [Raw API records](../../../raw/weekly_api_c64d75aa3a03356f)
- [Original shared budget ledger](../../../../12_pressure_framing_api_20261020/data/api_budget.json)
- [Prospective protocol](../../../hypotheses/PROTOCOL.md)

API settings checked 21 October 2026: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), [Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5).
