# GPT AGENT PILOT: v2 results

## Conclusions

1. Completed 48 decision records with validated state readbacks; no replacement orders.
2. 0/4 condition screens copied demand in every diagnostic state.
3. H1 and H2 have not been tested. Review inventory/supply-line sensitivity before running the game.
4. Diagnostic states are separate hypothetical retailer decisions; they are not four-role game trajectories.

## Diagnostic results

```
 trained effort  mean_order_change_supply_line_4_to_36  mean_order_change_inventory_0_to_24  copies_demand_all_states  zero_orders  median_reasoning_tokens                                                                            note
   False   high                              -6.666667                                 -8.0                     False           10                   1137.0 Descriptive retailer sensitivity screen; not a beta estimate or hypothesis test
   False    low                              -5.333333                                 -6.0                     False            5                     98.0 Descriptive retailer sensitivity screen; not a beta estimate or hypothesis test
    True   high                              -6.666667                                 -7.0                     False           10                   1079.5 Descriptive retailer sensitivity screen; not a beta estimate or hypothesis test
    True    low                              -4.000000                                 -5.0                     False            6                    220.5 Descriptive retailer sensitivity screen; not a beta estimate or hypothesis test
```

## Reasoning manipulation check

```
        mean_reasoning_tokens  median_reasoning_tokens  median_latency_s
effort                                                                  
high              1625.666667                   1121.5          5.530433
low                190.666667                    160.0          1.608079
```
Reasoning tokens and latency describe resource use, not human thinking time. Overlapping low/high resource use weakens the mechanism interpretation.

## Spending and interpretation

Recorded estimated charges/reservations: $0.2395. Not an invoice or account balance.
The original pilot remains separate. This redesigned protocol cannot confirm effects in humans. Do not repeatedly change prompts, exclusions, sample size, or models until p < .05. Use the pilot to fix measurement, then freeze a new protocol and collect independent confirmation data.
