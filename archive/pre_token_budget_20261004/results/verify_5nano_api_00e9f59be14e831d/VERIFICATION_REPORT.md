# Budget verification — conclusions

1. Real GPT API run.
2. Run stopped before completion: 307 successful responses; 5 saved failed/pending requests.
3. Ordering checks across conditions: 4/4 passed. Recorded estimated charges/reservations: $0.0601; allowance $0.75.
4. H1/H2 are not established by this pilot. One group per condition is for measurement verification only.

Retries: 0 failed attempts later recovered; 5 failed/pending attempts remain unresolved. All attempt costs are included.
The protocol permits at most two retries for incorrect observation/rules replies, using the same model and effort. No desired order, beta, or hypothesis result is supplied. Results describe agents with this retry policy; retries add resources and may differ by condition.

## First-attempt reliability

```
                 first_attempt_requests  first_attempt_valid  first_attempt_valid_rate
trained effort                                                                        
False   low                          53                   52                     0.981
        minimal                     109                  109                     1.000
True    low                          45                   41                     0.911
        minimal                     105                  105                     1.000
```
These checks measure rules answers and accurate copying of observations. Passing does not prove optimal ordering, understanding of delays, or identifiable beta. Retries can conceal a weak first-attempt rate, so inspect this table before scaling.

## Retry counts by condition

```
                 attempts  logical_requests  recovered_failed_attempts  extra_attempts
trained effort                                                                        
False   low            53                53                          0               0
        minimal       109               109                          0               0
True    low            45                45                          0               0
        minimal       105               105                          0               0
```

Group collection: 0/4 required groups completed; 0 failed groups retained in the audit.
Completed-group performance and beta exclude failed partial games. all_candidate_rows.csv retains committed rounds from all candidates; individual request files retain uncommitted replies. Replacement is based only on exhausted correctness failures, never beta or effect direction. Replacing failures selects for successful responders; confirmatory H1/H2 p-values are withheld if replacement occurred.

Do not interpret partial games as H1/H2 evidence. The last successful requests and any failure remain saved. If the local allowance stopped the run, review spending before raising it. If a request failed, keep the record and review the error; do not keep retrying blindly.

Standard scoring: 0.50 per held unit/week + 1.00 per backlogged unit/week; no sales revenue or production fee. Four roles, local information, 12 initial units per role; external demand 4 in weeks 1–4 and 8 afterward. Free choices start in week 1; this is a standard-cost implementation, not a claim to reproduce every classroom instruction. H2_API concerns reasoning effort; it cannot establish human time-pressure effects.

A useful verification result means complete responses, measurable beta, interpretable performance, and affordable token use. It does NOT mean the treatment effect has the predicted sign.
