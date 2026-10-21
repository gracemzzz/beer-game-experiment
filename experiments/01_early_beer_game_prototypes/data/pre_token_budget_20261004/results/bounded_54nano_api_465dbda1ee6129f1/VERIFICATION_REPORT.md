# Budget verification — conclusions

1. Real GPT API run.
2. Run completed: 596 successful responses; 0 saved failed/pending requests.
3. Ordering checks across conditions: 4/4 passed. Recorded estimated charges/reservations: $0.8737; allowance $1.05.
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
   b000_control_low    False    low            2184.0             1460.0             3644.0                  36             76            0               96
b000_control_medium    False medium            2920.0             3968.0             6888.0                  36            220            0               96
   b000_trained_low     True    low            1984.0             1736.0             3720.0                  36             98            0               96
b000_trained_medium     True medium            3142.5             2618.0             5760.5                  36            142            0               96
```
Lower scored_total_cost is better. Automatic continuation is a fixed 36-week evaluation with no API calls; it is not GPT behavior and is excluded from beta, fulfillment and boundary statistics below. Existing performance charts show the agent phase only. This finite continuation is a protocol choice, not an infinite-horizon optimum. Residual inventory, backlog and supply line are reported for review.

## Order-boundary audit

```
                decisions  zero_rate  cap_hit_rate  max_order
trained effort                                               
False   low           144      0.653         0.132         40
        medium        144      0.597         0.146         40
True    low           144      0.618         0.111         40
        medium        144      0.604         0.132         40
```
The cap prevents million-unit orders mechanically. It does not prove realistic behavior. Beta predictions are capped at the same limit; fewer than 8 strictly interior orders per role makes beta unusable. A cap-hit rate above 20% in any condition is a prespecified pilot warning, not a significance filter. High zero rates remain visible; zero orders never trigger replacement.
5. 8/16 roles and 0/4 groups have usable beta.
6. Zero orders: 61.8%; 0/16 roles copied demand for every week.
7. Do not scale automatically: inspect beta identification and effort separation.

## Supply-chain performance

```
 trained effort  groups  mean_team_cost  median_team_cost  min_team_cost  max_team_cost  mean_backlog_cost  mean_customer_fulfillment
   False    low       1          2184.0            2184.0         2184.0         2184.0              852.0                        1.0
   False medium       1          2920.0            2920.0         2920.0         2920.0              868.0                        1.0
    True    low       1          1984.0            1984.0         1984.0         1984.0              858.0                        1.0
    True medium       1          3142.5            3142.5         3142.5         3142.5             1328.0                        1.0
```

## Beta and reasons for unusable fits

```
                       agent_id  alpha  beta_for_interpretation  usable                                   fit_flag
   b000_control_low_distributor 0.7769                      NaN   False                    too_few_interior_orders
       b000_control_low_factory 0.3593                      NaN   False                    too_few_interior_orders
      b000_control_low_retailer 1.0000                   0.5647    True                         parameter_boundary
    b000_control_low_wholesaler 0.1785                   0.4261    True                                         ok
b000_control_medium_distributor 0.1003                   1.6842    True                                         ok
    b000_control_medium_factory 0.3898                      NaN   False                    too_few_interior_orders
   b000_control_medium_retailer 0.8806                   0.2872    True                                         ok
 b000_control_medium_wholesaler 0.1662                   0.8606    True                                         ok
   b000_trained_low_distributor 0.2376                      NaN   False                    too_few_interior_orders
       b000_trained_low_factory 0.8939                      NaN   False                    too_few_interior_orders
      b000_trained_low_retailer 0.4199                   0.9558    True                                         ok
    b000_trained_low_wholesaler 0.5915                   1.0737    True                                         ok
b000_trained_medium_distributor 0.0987                      NaN   False                    too_few_interior_orders
    b000_trained_medium_factory 0.0680                      NaN   False                    too_few_interior_orders
   b000_trained_medium_retailer 0.6297                   0.5766    True                                         ok
 b000_trained_medium_wholesaler 1.0000                      NaN   False parameter_boundary;too_few_interior_orders
```

## Effort check

```
        mean_reasoning_tokens  median_latency_s
effort                                         
low                   338.194             2.832
medium               1573.340             8.044
```
Per-decision reasoning and latency include failed attempts plus the accepted attempt. Higher average reasoning-token use is a descriptive manipulation check, not a significance test or human thinking-time measure.

## Cost scenarios based on measured traffic

```
                  model  groups_per_cell  agents  estimated_usd
gpt-5.4-nano-2026-03-17                1      16          0.874
gpt-5.4-nano-2026-03-17                8     128          6.967
gpt-5.4-nano-2026-03-17               16     256         13.930
```
Projections use this run’s measured tokens; larger samples and longer histories may cost differently. No automatic larger run occurs.

Standard scoring: 0.50 per held unit/week + 1.00 per backlogged unit/week; no sales revenue or production fee. Four roles, local information, 12 initial units per role; external demand 4 in weeks 1–4 and 8 afterward. Free choices start in week 1; this is a bounded-order variant with a 40-unit weekly order limit, not an unrestricted standard Beer Game. H2_API concerns reasoning effort; it cannot establish human time-pressure effects.

A useful verification result means complete responses, measurable beta, interpretable performance, and affordable token use. It does NOT mean the treatment effect has the predicted sign.
