# Budget verification — conclusions

1. OFFLINE SOFTWARE CHECK ONLY: not GPT behavior.
2. Run completed: 594 successful responses; 0 saved failed/pending requests.
3. Low/high access checks: 2/2 passed. Recorded estimated charges/reservations: $0.0000; allowance $0.75.
4. H1/H2 are not established by this pilot. One group per condition is for measurement verification only.
5. 16/16 roles and 4/4 groups have usable beta.
6. Zero orders: 0.7%; 0/16 roles copied demand for every week.
7. Offline check only; live model behavior is unverified.

## Supply-chain performance

```
 trained effort  groups  mean_team_cost  median_team_cost  min_team_cost  max_team_cost  mean_backlog_cost  mean_customer_fulfillment
   False   high       1           913.0             913.0          913.0          913.0               29.0                        1.0
   False    low       1           908.0             908.0          908.0          908.0                4.0                        1.0
    True   high       1           873.5             873.5          873.5          873.5                8.0                        1.0
    True    low       1           892.0             892.0          892.0          892.0               20.0                        1.0
```

## Beta and reasons for unusable fits

```
                     agent_id  alpha  beta_for_interpretation  usable fit_flag
b000_control_high_distributor 0.3703                   0.7072    True       ok
    b000_control_high_factory 0.3311                   0.6083    True       ok
   b000_control_high_retailer 0.4839                   0.8035    True       ok
 b000_control_high_wholesaler 0.3619                   0.4689    True       ok
 b000_control_low_distributor 0.3666                   0.8273    True       ok
     b000_control_low_factory 0.3576                   0.6979    True       ok
    b000_control_low_retailer 0.2959                   0.7591    True       ok
  b000_control_low_wholesaler 0.3857                   0.5674    True       ok
b000_trained_high_distributor 0.3394                   0.6076    True       ok
    b000_trained_high_factory 0.3179                   0.5807    True       ok
   b000_trained_high_retailer 0.4607                   0.5756    True       ok
 b000_trained_high_wholesaler 0.2870                   0.9231    True       ok
 b000_trained_low_distributor 0.4406                   0.7243    True       ok
     b000_trained_low_factory 0.3858                   0.7569    True       ok
    b000_trained_low_retailer 0.2843                   0.8190    True       ok
  b000_trained_low_wholesaler 0.4292                   0.6633    True       ok
```

Standard scoring: 0.50 per held unit/week + 1.00 per backlogged unit/week; no sales revenue or production fee. Four roles, local information, 12 initial units per role; external demand 4 in weeks 1–4 and 8 afterward. Free choices start in week 1; this is a standard-cost implementation, not a claim to reproduce every classroom instruction. H2_API concerns reasoning effort; it cannot establish human time-pressure effects.

A useful verification result means complete responses, measurable beta, interpretable performance, and affordable token use. It does NOT mean the treatment effect has the predicted sign.
