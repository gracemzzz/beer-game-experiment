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

## Order-boundary audit

```
                decisions  zero_rate  cap_hit_rate  max_order
trained effort                                               
False   low           144      0.014           0.0         20
        medium        144      0.021           0.0         23
True    low           144      0.000           0.0         22
        medium        144      0.014           0.0         16
```
The cap prevents million-unit orders mechanically. It does not prove realistic behavior. Beta predictions are capped at the same limit; fewer than 8 strictly interior orders per role makes beta unusable. A cap-hit rate above 20% in any condition is a prespecified pilot warning, not a significance filter. High zero rates remain visible; zero orders never trigger replacement.
5. 16/16 roles and 4/4 groups have usable beta.
6. Zero orders: 1.2%; 0/16 roles copied demand for every week.
7. Offline check only; live model behavior is unverified.

## Supply-chain performance

```
 trained effort  groups  mean_team_cost  median_team_cost  min_team_cost  max_team_cost  mean_backlog_cost  mean_customer_fulfillment
   False    low       1           908.5             908.5          908.5          908.5               11.0                        1.0
   False medium       1           932.0             932.0          932.0          932.0               25.0                        1.0
    True    low       1           895.0             895.0          895.0          895.0                8.0                        1.0
    True medium       1           883.5             883.5          883.5          883.5                9.0                        1.0
```

## Beta and reasons for unusable fits

```
                       agent_id  alpha  beta_for_interpretation  usable fit_flag
   b000_control_low_distributor 0.3826                   0.7897    True       ok
       b000_control_low_factory 0.3795                   0.6588    True       ok
      b000_control_low_retailer 0.4739                   0.5628    True       ok
    b000_control_low_wholesaler 0.3729                   0.7083    True       ok
b000_control_medium_distributor 0.4208                   0.6780    True       ok
    b000_control_medium_factory 0.3603                   0.7192    True       ok
   b000_control_medium_retailer 0.5275                   0.4953    True       ok
 b000_control_medium_wholesaler 0.4282                   0.6589    True       ok
   b000_trained_low_distributor 0.3400                   0.7600    True       ok
       b000_trained_low_factory 0.3382                   0.6795    True       ok
      b000_trained_low_retailer 0.3602                   0.5844    True       ok
    b000_trained_low_wholesaler 0.3608                   0.7838    True       ok
b000_trained_medium_distributor 0.4337                   0.7048    True       ok
    b000_trained_medium_factory 0.3038                   0.6384    True       ok
   b000_trained_medium_retailer 0.2432                   1.1369    True       ok
 b000_trained_medium_wholesaler 0.4614                   0.7830    True       ok
```

Standard scoring: 0.50 per held unit/week + 1.00 per backlogged unit/week; no sales revenue or production fee. Four roles, local information, 12 initial units per role; external demand 4 in weeks 1–4 and 8 afterward. Free choices start in week 1; this is a bounded-order variant with a 40-unit weekly order limit, not an unrestricted standard Beer Game. H2_API concerns reasoning effort; it cannot establish human time-pressure effects.

A useful verification result means complete responses, measurable beta, interpretable performance, and affordable token use. It does NOT mean the treatment effect has the predicted sign.
