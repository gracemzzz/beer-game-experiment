# GPT AGENT PILOT: budget verification results

## Conclusions

1. Completed 576 decision records with validated state readbacks; no replacement orders.
2. 0/4 groups have four usable beta estimates; 0/16 roles copied demand every week.
3. H1 tests training; H2_API compares low versus medium reasoning, not 60/120-second human time pressure.
- H1_training_average: withheld: offline, too few blocks, incomplete/excluded data, or replacement selection; no significance conclusion.
- H2_API_low_minus_medium_trained: withheld: offline, too few blocks, incomplete/excluded data, or replacement selection; no significance conclusion.

## Supply-chain performance (all groups)

```
 trained effort  groups  mean_team_cost  median_team_cost  min_team_cost  max_team_cost  mean_backlog_cost  mean_customer_fulfillment
   False    low       1          2184.0            2184.0         2184.0         2184.0              852.0                        1.0
   False medium       1          2920.0            2920.0         2920.0         2920.0              868.0                        1.0
    True    low       1          1984.0            1984.0         1984.0         1984.0              858.0                        1.0
    True medium       1          3142.5            3142.5         3142.5         3142.5             1328.0                        1.0
```
Cost is in game cost units, not API dollars. Team cost sums all four roles. Customer fulfillment is cumulative retailer shipments / cumulative customer demand; it includes late deliveries and is not an on-time service measure. Bullwhip is sample variance of role orders / variance of incoming demand; it is undefined when incoming demand has zero variance. No terminal inventory penalty is added.

## Beta measurement coverage

```
                roles  usable_beta
trained effort                    
False   low         4            2
        medium      4            3
True    low         4            2
        medium      4            1
```
See agent_beta_fits.csv: beta_for_interpretation is blank when beta is unreliable. The raw optimizer beta is retained for audit only. See group_beta.csv for analysis_beta. Missing beta means unidentified, not zero and not a failed hypothesis.

![Supply-chain performance](supply_chain_performance.png)

## Hypothesis results

```
                     hypothesis  estimate  complete_blocks  planned_blocks  p_two_sided  p_holm  ci95_low  ci95_high predicted_direction                                                                                status
            H1_training_average       NaN                0               1          NaN     NaN       NaN        NaN            positive withheld: offline, too few blocks, incomplete/excluded data, or replacement selection
H2_API_low_minus_medium_trained       NaN                0               1          NaN     NaN       NaN        NaN            negative withheld: offline, too few blocks, incomplete/excluded data, or replacement selection
```

CIs are descriptive paired bootstrap 95% intervals, not multiplicity-adjusted. The two planned p-values are Holm-adjusted. No p-values are computed after excluding any planned block; identification failures depend on behavior and can bias selection. Eight blocks is a reporting floor, not a power calculation.

## Reasoning manipulation check

```
        mean_reasoning_tokens  median_reasoning_tokens  median_latency_s
effort                                                                  
low                338.194444                    295.0          2.831526
medium            1573.340278                   1161.5          8.043866
```
Reasoning tokens and latency describe resource use, not human thinking time. Overlapping resource use between the two effort settings weakens the mechanism interpretation.

## Spending and interpretation

Recorded estimated charges/reservations: $0.8737. Not an invoice or account balance.
The original pilot remains separate. This redesigned protocol cannot confirm effects in humans. Do not repeatedly change prompts, exclusions, sample size, or models until p < .05. Use the pilot to fix measurement, then freeze a new protocol and collect independent confirmation data.
