# Conclusions

1. The API connected and returned structured responses. This was a correctness failure, not a key or billing problem.
2. Two control/minimal rules checks (distributor and factory) returned holding_cost = 0.5; the expected total was 8 × 0.5 = 4. All three other fields in each answer were correct.
3. 12 responses were recorded: 4 ordering preflights and 8 rules checks. Ten passed and two failed. No game orders were collected. H1/H2 and beta cannot be evaluated.
4. Estimated API cost: $0.0012524 (about 0.125 cents). Elapsed time: 8.60 seconds. This does not forecast full-game speed or cost.
5. The error is consistent with confusing the per-unit rate with the total charge. It does not establish why the model made that error or whether minimal effort alone caused it.
6. Next protocol explicitly names the field total_holding_cost and asks for the total across all units. Both experimental conditions receive the same clarification. No correct answer is injected and no validation is removed. All rules checks must pass before games start.
7. Earlier request records remain unchanged. The revised prompt requires a separate run; no automatic paid retry was made.
