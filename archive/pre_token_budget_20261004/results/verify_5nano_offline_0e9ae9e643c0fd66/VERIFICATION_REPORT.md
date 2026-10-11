# Budget verification — conclusions

1. OFFLINE SOFTWARE CHECK ONLY: not GPT behavior.
2. Run completed: 596 successful responses; 0 saved failed/pending requests.
3. Ordering checks across conditions: 4/4 passed. Recorded estimated charges/reservations: $0.0000; allowance $0.75.
4. H1/H2 are not established by this pilot. One group per condition is for measurement verification only.
5. 16/16 roles and 4/4 groups have usable beta.
6. Zero orders: 1.2%; 0/16 roles copied demand for every week.
7. Offline check only; live model behavior is unverified.

## Supply-chain performance

```
 trained effort  groups  mean_team_cost  median_team_cost  min_team_cost  max_team_cost  mean_backlog_cost  mean_customer_fulfillment
   False   high       1           896.5             896.5          896.5          896.5                6.0                        1.0
   False    low       1           889.0             889.0          889.0          889.0               19.0                        1.0
    True   high       1           923.0             923.0          923.0          923.0               15.0                        1.0
    True    low       1           934.0             934.0          934.0          934.0               10.0                        1.0
```

## Beta and reasons for unusable fits

```
                     agent_id  alpha  beta_for_interpretation  usable fit_flag
b000_control_high_distributor 0.3438                   0.7195    True       ok
    b000_control_high_factory 0.3300                   0.6702    True       ok
   b000_control_high_retailer 0.3665                   0.8004    True       ok
 b000_control_high_wholesaler 0.2877                   0.5008    True       ok
 b000_control_low_distributor 0.3238                   0.6689    True       ok
     b000_control_low_factory 0.3625                   0.7599    True       ok
    b000_control_low_retailer 0.5510                   0.3914    True       ok
  b000_control_low_wholesaler 0.3571                   0.7312    True       ok
b000_trained_high_distributor 0.3470                   0.6251    True       ok
    b000_trained_high_factory 0.3579                   0.7140    True       ok
   b000_trained_high_retailer 0.4255                   0.6756    True       ok
 b000_trained_high_wholesaler 0.3930                   0.6133    True       ok
 b000_trained_low_distributor 0.3365                   0.7111    True       ok
     b000_trained_low_factory 0.3962                   0.7133    True       ok
    b000_trained_low_retailer 0.4436                   0.7173    True       ok
  b000_trained_low_wholesaler 0.3311                   0.5507    True       ok
```

Standard scoring: 0.50 per held unit/week + 1.00 per backlogged unit/week; no sales revenue or production fee. Four roles, local information, 12 initial units per role; external demand 4 in weeks 1–4 and 8 afterward. Free choices start in week 1; this is a standard-cost implementation, not a claim to reproduce every classroom instruction. H2_API concerns reasoning effort; it cannot establish human time-pressure effects.

A useful verification result means complete responses, measurable beta, interpretable performance, and affordable token use. It does NOT mean the treatment effect has the predicted sign.
