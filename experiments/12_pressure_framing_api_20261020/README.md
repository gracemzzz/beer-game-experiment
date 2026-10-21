# Experiment 12: whole-cohort API feasibility results

1. **Finished: four pilots passed; only one of four main responses passed.** GPT-6 Luna and GPT-5.6 Luna failed inventory arithmetic. Claude returned an empty chain list. GPT-5.6 Sol passed.
2. **Accepted Sol result: no pressure effect.** H1 pipeline sensitivity was 0.833333 in both conditions. Mean chain cost was 551.60 in both conditions. All 1,920 weekly orders were exactly 4; all ten paired contrasts were zero.
3. **This does not disprove human H1/H2.** These were jointly generated fictional chains under imagined pressure, with no enforced deadline or independent participant inference.
4. **Cumulative recorded charge: $0.3404859**, including all eleven requests across the original pilots, recovery and follow-up. The remaining allowance is shared with experiment 13; it is not a new budget.
5. **Next collection is [experiment 13](../13_weekly_state_api_20261021/README.md).** The user approved 24 weekly batches per model with Python-calculated states. Do not repeat the completed whole-cohort generation to seek a different result.

[Full current report](reports/REPORT.md) · [Accepted Sol numerical audit](analysis/completed_followup_20261021/accepted_sol_analysis.json) · [New weekly notebook](../13_weekly_state_api_20261021/notebooks/RUN_EXPERIMENT.ipynb)

## Why the method changed

| Model | Main response | Decision |
| --- | --- | --- |
| GPT-6 Luna | All 1,920 orders zero; 40 of 60 inventory checkpoint vectors wrong | Invalid accounting; excluded |
| GPT-5.6 Luna | All 1,920 orders four; 56 of 60 inventory checkpoint vectors wrong | Invalid accounting; excluded |
| GPT-5.6 Sol | All 1,920 orders four; all 60 checkpoint vectors correct | Accepted; H1/H2 differences zero |
| Claude Haiku 5.5 | Empty chain list despite `complete: true` | Missing cohort; excluded |

All four main requests finished normally below their token allowances. Increasing those allowances would not address these failures. Passing a two-chain pilot did not demonstrate reliable twenty-chain generation. Constant or zero orders are allowed; the failed responses were excluded for incorrect physical accounting or missing data, not an undesired pattern.

## Preserved design and evidence

The original design generated each model's 20 chains (80 fictional roles, ten chains per condition, 24 weeks) in one main response. Four separate two-chain pilots were excluded from main analysis. H1 was a matched-state sensitivity proxy, not structural β. H2 included exactly 24 weeks of holding and backlog costs. No revenue or factory production fee applied.

| Item | Location |
| --- | --- |
| Original protocol | [hypotheses/PROTOCOL.md](hypotheses/PROTOCOL.md) |
| First recovery | [RECOVERY_20261021.md](hypotheses/RECOVERY_20261021.md) |
| Completed Claude follow-up | [CLAUDE_FOLLOWUP_20261021.md](hypotheses/CLAUDE_FOLLOWUP_20261021.md) |
| Exact prompts | `prompts/pressure_api_c04ef16c05dd826c/` and the frozen follow-up request files |
| Original, recovery and follow-up records | [data/pressure_api_c04ef16c05dd826c/](data/pressure_api_c04ef16c05dd826c/) |
| Shared cumulative ledger | [data/api_budget.json](data/api_budget.json) |
| Executed notebook | [notebooks/RUN_EXPERIMENT.ipynb](notebooks/RUN_EXPERIMENT.ipynb) |
| Current report and prior publication versions | [reports/](reports/) |
| Earlier software checks | [analysis/software_checks/](analysis/software_checks/) |

The executed notebook is preserved. Use the new experiment 13 notebook for collection. Reports distinguish model data from software tests. Earlier validation receipts describe the implementation at those dates; subsequent live failures are retained here.
