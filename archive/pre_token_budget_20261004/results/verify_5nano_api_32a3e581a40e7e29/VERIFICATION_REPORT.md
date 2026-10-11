# Budget verification — conclusions

1. Real GPT API run.
2. Run stopped before completion: 51 successful responses; 2 saved failed/pending requests.
3. Ordering checks across conditions: 4/4 passed. Recorded estimated charges/reservations: $0.0070; allowance $0.75.
4. H1/H2 are not established by this pilot. One group per condition is for measurement verification only.
- Comprehension check failed ({'group': 'b000_trained_minimal', 'role': 'retailer', 'week': 3, 'kind': 'game'}): observed_supply_line: expected 0, received 4.
- Comprehension check failed ({'group': 'b000_control_minimal', 'role': 'retailer', 'week': 3, 'kind': 'game'}): observed_supply_line: expected 0, received 8.

Do not interpret partial games as H1/H2 evidence. The last successful requests and any failure remain saved. If the local allowance stopped the run, review spending before raising it. If a request failed, keep the record and review the error; do not keep retrying blindly.

Standard scoring: 0.50 per held unit/week + 1.00 per backlogged unit/week; no sales revenue or production fee. Four roles, local information, 12 initial units per role; external demand 4 in weeks 1–4 and 8 afterward. Free choices start in week 1; this is a standard-cost implementation, not a claim to reproduce every classroom instruction. H2_API concerns reasoning effort; it cannot establish human time-pressure effects.

A useful verification result means complete responses, measurable beta, interpretable performance, and affordable token use. It does NOT mean the treatment effect has the predicted sign.
