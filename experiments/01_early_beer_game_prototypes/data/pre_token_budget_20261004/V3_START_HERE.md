# Profit-based full game (v3)

Open `thoughts_reflection_experiment_v3.ipynb`, beside `beer_game_v3.py`.

1. The selected settings are API mode, full game, 8 groups per cell, 36 weeks, replicate `v3-profit-01`: 32 groups, 128 agents, 4,608 ordering decisions plus 128 rules checks.
2. To test free, set MODE to offline and Run All. For GPT use API mode and enter the key in the hidden popup. No real API run has been made to validate this revision.
3. The retained $3 local spending allowance can stop before completion. Review the displayed cost scenarios first. Increase only BUDGET_USD to resume cached successes after a spending stop.
4. Read the displayed profit/cost and service tables, weekly plots, zero-order rates, usable beta estimates, and hypothesis-test status. All outcomes are also saved as CSVs with a conclusions-first report in a new `results/v3_...` folder.

## Economics

- Team revenue: 10 per unit actually delivered to an external customer by the retailer. No revenue for just placing orders or moving units internally.
- Factory cost: 2 per newly ordered production unit, charged once when committed.
- Holding cost: 0.25 per unit per week at each role (formerly 0.5).
- Backlog penalty: 2 per unit per week at each role (formerly 1).
- Initial inventory: 4 at each role (formerly 12). Initial pipeline and order flow: 4/week.
- Customer demand: 8/week initially; later variable around 8, 12, or 16, with the same seeded path across conditions within each block.
- Profit = sales revenue − factory commitments − holding cost − backlog penalties. Orders cannot be canceled. Backlogs carry forward; delivery later earns revenue then. Initial endowments are sunk; terminal unsold inventory and pipeline receive no salvage credit.

These are illustrative simulation economics, not calibrated market or student estimates. They change the original cost-only experiment. Do not pool this data with v1/v2. Training and low/high reasoning conditions share the same economics. H2_API remains a reasoning-effort hypothesis, not a human deadline test.

## Verification and limits

The notebook checks profit accounting and compares zero-order, replenishment, and excessive-order policies offline. Replenishment beats both extremes on the fixed sanity-check path but is not an optimized policy and can still lose money. Zero orders are legal and may be correct when stock or pipeline is high. No rule forces positive orders or a preferred beta. New GPT behavior has not yet been observed.

The optional diagnostic screen now covers 24 states per condition, including shortages and surplus (96 decisions + 16 checks). It is not the selected stage; it does not replace full games.

Run `python test_v3.py` for offline and mocked-API checks. P-values still require usable beta in every planned block and at least 8 complete blocks; eight is a reporting floor, not a power justification. Increased ordering does not guarantee identification or significant H1/H2 results.
