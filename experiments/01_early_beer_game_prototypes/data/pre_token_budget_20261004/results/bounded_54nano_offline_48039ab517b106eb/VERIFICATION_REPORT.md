# Budget verification — conclusions

1. OFFLINE SOFTWARE CHECK ONLY: not GPT behavior.
2. Run completed: 596 successful responses; 0 saved failed/pending requests.
3. Ordering checks across conditions: 4/4 passed. Recorded estimated charges/reservations: $0.0000; allowance $0.75.
4. This modified game limits weekly orders to 0–40; H2_API compares low/medium reasoning, not human time pressure. Completion alone does not establish H1/H2.

Retries: 0 failed attempts later recovered; 0 failed/pending attempts remain unresolved. All attempt costs are included.
The protocol permits at most two retries for incorrect observation/rules replies, using the same model and effort. Separately, bounded transport retries handle temporary service errors without changing prompts. No desired order, beta, or hypothesis result is supplied. Results describe agents with this retry policy; retries add resources and may differ by condition.

## First-attempt reliability

```
                first_attempt_requests  first_attempt_valid  first_attempt_valid_rate
trained effort                                                                       
False   low                        149                  149                       1.0
        medium                     149                  149                       1.0
True    low                        149                  149                       1.0
        medium                     149                  149                       1.0
```
These checks measure rules answers and accurate copying of observations. Passing does not prove optimal ordering, understanding of delays, or identifiable beta. Retries can conceal a weak first-attempt rate, so inspect this table before scaling.

## Retry counts by condition

```
                attempts  logical_requests  recovered_failed_attempts  extra_attempts
trained effort                                                                       
False   low          149               149                          0               0
        medium       149               149                          0               0
True    low          149               149                          0               0
        medium       149               149                          0               0
```

Group collection: 4/4 required groups completed; 0 failed groups retained in the audit.
Completed-group performance and beta exclude failed partial games. all_candidate_rows.csv retains committed rounds from all candidates; individual request files retain uncommitted replies. Replacement is based only on exhausted correctness failures, never beta or effect direction. Replacing failures selects for successful responders; confirmatory H1/H2 p-values are withheld if replacement occurred.

## Scored objective: agent phase plus automatic continuation

```
           group_id  trained effort  agent_phase_cost  continuation_cost  scored_total_cost  continuation_weeks  end_inventory  end_backlog  end_supply_line
   b000_control_low    False    low             910.5              919.0             1829.5                  36             51            0               96
b000_control_medium    False medium             896.5              981.5             1878.0                  36             55            0               96
   b000_trained_low     True    low             907.0              831.5             1738.5                  36             45            0               96
b000_trained_medium     True medium             919.0              952.5             1871.5                  36             52            0               96
```
Lower scored_total_cost is better. Automatic continuation is a fixed 36-week evaluation with no API calls; it is not GPT behavior and is excluded from beta, fulfillment and boundary statistics below. Existing performance charts show the agent phase only. This finite continuation is a protocol choice, not an infinite-horizon optimum. Residual inventory, backlog and supply line are reported for review.

## Order-boundary audit

```
                decisions  zero_rate  cap_hit_rate  max_order
trained effort                                               
False   low           144      0.021           0.0         20
        medium        144      0.000           0.0         17
True    low           144      0.007           0.0         18
        medium        144      0.021           0.0         26
```
The cap prevents million-unit orders mechanically. It does not prove realistic behavior. Beta predictions are capped at the same limit; fewer than 8 strictly interior orders per role makes beta unusable. A cap-hit rate above 20% in any condition is a prespecified pilot warning, not a significance filter. High zero rates remain visible; zero orders never trigger replacement.
5. 16/16 roles and 4/4 groups have usable beta.
6. Zero orders: 1.2%; 0/16 roles copied demand for every week.
7. Offline check only; live model behavior is unverified.

## Supply-chain performance

```
 trained effort  groups  mean_team_cost  median_team_cost  min_team_cost  max_team_cost  mean_backlog_cost  mean_customer_fulfillment
   False    low       1           910.5             910.5          910.5          910.5               32.0                        1.0
   False medium       1           896.5             896.5          896.5          896.5                8.0                        1.0
    True    low       1           907.0             907.0          907.0          907.0                3.0                        1.0
    True medium       1           919.0             919.0          919.0          919.0               18.0                        1.0
```

## Beta and reasons for unusable fits

```
                       agent_id  alpha  beta_for_interpretation  usable fit_flag
   b000_control_low_distributor 0.3932                   0.6424    True       ok
       b000_control_low_factory 0.3527                   0.7264    True       ok
      b000_control_low_retailer 0.4032                   0.4758    True       ok
    b000_control_low_wholesaler 0.3663                   0.5493    True       ok
b000_control_medium_distributor 0.4165                   0.7000    True       ok
    b000_control_medium_factory 0.3846                   0.7280    True       ok
   b000_control_medium_retailer 0.2518                   1.1182    True       ok
 b000_control_medium_wholesaler 0.3969                   0.6630    True       ok
   b000_trained_low_distributor 0.4329                   0.7293    True       ok
       b000_trained_low_factory 0.3582                   0.7222    True       ok
      b000_trained_low_retailer 0.3832                   0.6238    True       ok
    b000_trained_low_wholesaler 0.3233                   0.7094    True       ok
b000_trained_medium_distributor 0.5017                   0.6860    True       ok
    b000_trained_medium_factory 0.3671                   0.6925    True       ok
   b000_trained_medium_retailer 0.5146                   0.6667    True       ok
 b000_trained_medium_wholesaler 0.4520                   0.6009    True       ok
```

Standard scoring: 0.50 per held unit/week + 1.00 per backlogged unit/week; no sales revenue or production fee. Four roles, local information, 12 initial units per role; external demand 4 in weeks 1–4 and 8 afterward. Free choices start in week 1; this is a bounded-order variant with a 40-unit weekly order limit, not an unrestricted standard Beer Game. H2_API concerns reasoning effort; it cannot establish human time-pressure effects.

A useful verification result means complete responses, measurable beta, interpretable performance, and affordable token use. It does NOT mean the treatment effect has the predicted sign.
