# Token-budget Beer Game — conclusions

1. SYNTHETIC SOFTWARE CHECK: no GPT evidence or hypothesis inference.
2. Run status: complete. Estimated cost/reservations: $0.0000.
3. Saved successful API stages: 584; other saved attempts: 0.
Startup rule checks: 8/8 first attempts passed; 0 clarification rechecks recorded. API success and correct rule answers are separate checks.
4. Completed groups: 2/2; usable beta: 8/8 roles.
5. H1 tests lower beta under the short allowance; H2 tests higher total scored cost. H2 does not require usable beta. See the separate status for each test.
6. Review token separation, failures, cost and bullwhip plots before increasing sample size. Zero orders and large orders are outcomes, not automatic grounds for discarding a group.
Cost is holding plus backlog, including warmup and the 12 automatic terminal weeks. Automatic decisions never enter beta, token-use or bullwhip estimates. Fulfillment counts late delivery; it is not an on-time service rate. Bullwhip ratios use all game weeks including warmup because retailer demand is constant after the step; a constant denominator is reported as missing. The deterministic demand step limits generalization.
Beta is a structural-model diagnostic, not profit. No artificial upper order cap is fitted. Rank, response strength, variation and positive-order checks flag unreliable fits. A sample of at least eight paired chains is a computational inference floor, not a power calculation. The reflection proposes ten chains per condition; no sample size guarantees significance.

![Order trajectories](order_trajectories.png)
![Bullwhip by role](bullwhip.png)

## Startup rule checks

```
     group_id        role  attempt  passed failed_fields                                                                                               answer
b000_adequate    retailer        1    True            [] {'three_week_backlog_cost': 15, 'order_fills_today': False, 'objective_includes_continuation': True}
b000_adequate  wholesaler        1    True            [] {'three_week_backlog_cost': 15, 'order_fills_today': False, 'objective_includes_continuation': True}
b000_adequate distributor        1    True            [] {'three_week_backlog_cost': 15, 'order_fills_today': False, 'objective_includes_continuation': True}
b000_adequate     factory        1    True            [] {'three_week_backlog_cost': 15, 'order_fills_today': False, 'objective_includes_continuation': True}
   b000_short    retailer        1    True            [] {'three_week_backlog_cost': 15, 'order_fills_today': False, 'objective_includes_continuation': True}
   b000_short  wholesaler        1    True            [] {'three_week_backlog_cost': 15, 'order_fills_today': False, 'objective_includes_continuation': True}
   b000_short distributor        1    True            [] {'three_week_backlog_cost': 15, 'order_fills_today': False, 'objective_includes_continuation': True}
   b000_short     factory        1    True            [] {'three_week_backlog_cost': 15, 'order_fills_today': False, 'objective_includes_continuation': True}
```

## Group outcomes

```
     group_id  block condition  agent_phase_cost  continuation_cost  total_scored_cost  group_beta  usable_role_betas  customer_fulfillment  retailer_backlog_weeks  terminal_inventory  terminal_backlog
b000_adequate      0  adequate            1220.0              336.0             1556.0      0.6509                  4                   1.0                       0                  56                 0
   b000_short      0     short            1220.0              336.0             1556.0      0.6509                  4                   1.0                       0                  56                 0
```

## Token manipulation

```
condition  mean_preparation_tokens  median_preparation_tokens  truncated_fraction  mean_final_tokens  zero_rate  max_order
 adequate                      0.0                        0.0                 0.0                0.0     0.0278         31
    short                      0.0                        0.0                 0.0                0.0     0.0278         31
```

## Hypothesis tests

```
hypothesis           outcome  estimate  complete_pairs      predicted_direction  p_raw                                                                                    status  p_holm
        H1        group_beta       0.0               1 short minus adequate < 0    NaN withheld: offline, fewer than 8 pairs, incomplete sample, replacement, or missing outcome     NaN
        H2 total_scored_cost       0.0               1 short minus adequate > 0    NaN withheld: offline, fewer than 8 pairs, incomplete sample, replacement, or missing outcome     NaN
```

## Role performance and bullwhip

```
     group_id        role condition  holding_cost  backlog_cost  bullwhip_vs_local  bullwhip_vs_customer  order_variance  mean_order  zero_rate  max_order  backlog_weeks  max_backlog  terminal_backlog
b000_adequate distributor  adequate         256.0          95.0             2.4505               14.7530         21.7891      8.9167     0.0000         23              6           22                 0
b000_adequate     factory  adequate         286.0          84.0             2.0792               31.3611         46.3179      9.2222     0.1111         31              5           31                 0
b000_adequate    retailer  adequate         234.0           0.0             1.9080                1.9080          2.8179      8.3889     0.0000         12              0            0                 0
b000_adequate  wholesaler  adequate         223.0          42.0             2.6361                5.7253          8.4558      8.6389     0.0000         17              8            8                 0
   b000_short distributor     short         256.0          95.0             2.4505               14.7530         21.7891      8.9167     0.0000         23              6           22                 0
   b000_short     factory     short         286.0          84.0             2.0792               31.3611         46.3179      9.2222     0.1111         31              5           31                 0
   b000_short    retailer     short         234.0           0.0             1.9080                1.9080          2.8179      8.3889     0.0000         12              0            0                 0
   b000_short  wholesaler     short         223.0          42.0             2.6361                5.7253          8.4558      8.6389     0.0000         17              8            8                 0
```

## Beta diagnostics

```
     group_id        role condition  block  positive_orders  theta  alpha   beta  target   rmse     r2  jac_condition  usable fit_flag  n order_limit  cap_hit_rate
b000_adequate distributor  adequate      0               36    1.0 0.3459 0.6620 24.5036 0.1889 0.9983         4.3806    True       ok 36        None           0.0
b000_adequate     factory  adequate      0               32    1.0 0.3387 0.6411 24.5202 0.2974 0.9981         5.2894    True       ok 36        None           0.0
b000_adequate    retailer  adequate      0               36    1.0 0.3385 0.6912 24.9892 0.1976 0.9653        12.3089    True       ok 36        None           0.0
b000_adequate  wholesaler  adequate      0               36    1.0 0.3476 0.6095 22.8634 0.2230 0.9929         5.3218    True       ok 36        None           0.0
   b000_short distributor     short      0               36    1.0 0.3459 0.6620 24.5036 0.1889 0.9983         4.3806    True       ok 36        None           0.0
   b000_short     factory     short      0               32    1.0 0.3387 0.6411 24.5202 0.2974 0.9981         5.2894    True       ok 36        None           0.0
   b000_short    retailer     short      0               36    1.0 0.3385 0.6912 24.9892 0.1976 0.9653        12.3089    True       ok 36        None           0.0
   b000_short  wholesaler     short      0               36    1.0 0.3476 0.6095 22.8634 0.2230 0.9929         5.3218    True       ok 36        None           0.0
```

## Interpretation limits

This protocol restricts visible preparation tokens plus a common final-response allowance, with reasoning effort none. It does not directly limit hidden cognitive effort, wall-clock time or human thinking time. Prompts cannot reliably count remaining tokens; the API hard cap is the enforced constraint. A truncated memo is accepted as a deadline outcome, then a common 192-token stage solicits the order. The final stage can still involve implicit computation, and unused token allowance is not effort used.
Technical retries retain the same prompt and cap. Failed final responses can replace a whole group only within the configured limit; all failed attempts remain recorded. Replacement selection withholds inferential p-values. No order is clipped or replaced by a fabricated answer. The separate emergency scale check stops the run rather than making a boundary order.

Sources: [provided reflection](../../source/ThoughtsReflection_Paragraph.docx); [MIT Beer Game](https://web.mit.edu/jsterman/www/SDG/beergame.html); [Lee, Padmanabhan & Whang](https://pubsonline.informs.org/doi/10.1287/mnsc.43.4.546); [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-nano).
