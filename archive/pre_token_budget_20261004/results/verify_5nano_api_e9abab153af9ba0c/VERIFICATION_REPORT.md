# Budget verification — conclusions

1. Real GPT API run.
2. Run completed: 596 successful responses; 5 saved failed/pending requests.
3. Ordering checks across conditions: 4/4 passed. Recorded estimated charges/reservations: $0.1331; allowance $0.75.
4. H1/H2 are not established by this pilot. One group per condition is for measurement verification only.

Retries: 5 failed attempts later recovered; 0 failed/pending attempts remain unresolved. All attempt costs are included.
The protocol permits at most two retries for incorrect observation/rules replies, using the same model and effort. Separately, bounded transport retries handle temporary service errors without changing prompts. No desired order, beta, or hypothesis result is supplied. Results describe agents with this retry policy; retries add resources and may differ by condition.

## First-attempt reliability

```
                 first_attempt_requests  first_attempt_valid  first_attempt_valid_rate
trained effort                                                                        
False   low                         149                  148                     0.993
        minimal                     149                  149                     1.000
True    low                         149                  145                     0.973
        minimal                     149                  149                     1.000
```
These checks measure rules answers and accurate copying of observations. Passing does not prove optimal ordering, understanding of delays, or identifiable beta. Retries can conceal a weak first-attempt rate, so inspect this table before scaling.

## Retry counts by condition

```
                 attempts  logical_requests  recovered_failed_attempts  extra_attempts
trained effort                                                                        
False   low           150               149                          1               1
        minimal       149               149                          0               0
True    low           153               149                          4               4
        minimal       149               149                          0               0
```

Group collection: 4/4 required groups completed; 0 failed groups retained in the audit.
Completed-group performance and beta exclude failed partial games. all_candidate_rows.csv retains committed rounds from all candidates; individual request files retain uncommitted replies. Replacement is based only on exhausted correctness failures, never beta or effect direction. Replacing failures selects for successful responders; confirmatory H1/H2 p-values are withheld if replacement occurred.
5. 4/16 roles and 0/4 groups have usable beta.
6. Zero orders: 91.0%; 0/16 roles copied demand for every week.
7. Do not scale automatically: inspect beta identification and effort separation.

## Supply-chain performance

```
 trained  effort  groups  mean_team_cost  median_team_cost  min_team_cost  max_team_cost  mean_backlog_cost  mean_customer_fulfillment
   False     low       1      17203896.0        17203896.0     17203896.0     17203896.0         16703112.0                      0.309
   False minimal       1       6504992.0         6504992.0      6504992.0      6504992.0             6908.0                      0.088
    True     low       1         42010.0           42010.0        42010.0        42010.0            37928.0                      1.000
    True minimal       1      22003988.0        22003988.0     22003988.0     22003988.0         22003126.0                      0.162
```

## Beta and reasons for unusable fits

```
                        agent_id  alpha  beta_for_interpretation  usable                                                                                      fit_flag
    b000_control_low_distributor 0.5686                      NaN   False                                                      parameter_boundary;upper_parameter_limit
        b000_control_low_factory 1.0000                   0.5000    True                                                                                            ok
       b000_control_low_retailer 1.0000                      NaN   False                                                      parameter_boundary;upper_parameter_limit
     b000_control_low_wholesaler 1.0000                      NaN   False                                             parameter_boundary;upper_parameter_limit;poor_fit
b000_control_minimal_distributor 1.0000                      NaN   False                         weak_identification;parameter_boundary;upper_parameter_limit;poor_fit
    b000_control_minimal_factory 1.0000                      NaN   False                                             parameter_boundary;upper_parameter_limit;poor_fit
   b000_control_minimal_retailer    NaN                      NaN   False                                                                        insufficient_variation
 b000_control_minimal_wholesaler    NaN                      NaN   False                                                                        insufficient_variation
    b000_trained_low_distributor 0.3723                      NaN   False                                                      parameter_boundary;upper_parameter_limit
        b000_trained_low_factory 1.0000                   0.4168    True                                                                            parameter_boundary
       b000_trained_low_retailer 1.0000                   0.0000    True                                                                            parameter_boundary
     b000_trained_low_wholesaler 0.8187                   0.2887    True                                                                            parameter_boundary
b000_trained_minimal_distributor    NaN                      NaN   False                                                                        insufficient_variation
    b000_trained_minimal_factory    NaN                      NaN   False                                                                        insufficient_variation
   b000_trained_minimal_retailer 1.0000                      NaN   False                                             parameter_boundary;upper_parameter_limit;poor_fit
 b000_trained_minimal_wholesaler 0.0000                      NaN   False weak_inventory_response;weak_identification;parameter_boundary;upper_parameter_limit;poor_fit
```

## Effort check

```
         mean_reasoning_tokens  median_latency_s
effort                                          
low                    602.222             4.900
minimal                  0.000             0.916
```
Per-decision reasoning and latency include failed attempts plus the accepted attempt. Higher average reasoning-token use is a descriptive manipulation check, not a significance test or human thinking-time measure.

## Cost scenarios based on measured traffic

```
                model  groups_per_cell  agents  estimated_usd
gpt-5-nano-2025-08-07                1      16          0.115
gpt-5-nano-2025-08-07                8     128          0.915
gpt-5-nano-2025-08-07               16     256          1.829
         gpt-5.4-nano                1      16          0.384
         gpt-5.4-nano                8     128          3.062
         gpt-5.4-nano               16     256          6.123
```
GPT-5.4 nano may use different token counts and exhibit different behavior. Only a separate small run can measure its actual cost and beta identification. No automatic upgrade occurs.

Standard scoring: 0.50 per held unit/week + 1.00 per backlogged unit/week; no sales revenue or production fee. Four roles, local information, 12 initial units per role; external demand 4 in weeks 1–4 and 8 afterward. Free choices start in week 1; this is a standard-cost implementation, not a claim to reproduce every classroom instruction. H2_API concerns reasoning effort; it cannot establish human time-pressure effects.

A useful verification result means complete responses, measurable beta, interpretable performance, and affordable token use. It does NOT mean the treatment effect has the predicted sign.
