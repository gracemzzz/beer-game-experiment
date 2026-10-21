# Experiment 12: API pressure-framing study

**Question:** Does a model representing students under strong time pressure respond less to outstanding orders and produce higher Beer Game costs?

**Plan:** Four requested models; **80 fictional testers / 20 four-person chains per model**; ten chains per condition; **24 model-decision weeks**. **One main API call generates all 20 chains for a model.** Total authorized spending is **$5**, including four technical pilot calls, four main calls, failures and retries.

This is a new prospective study. Imagined pressure does not enforce actual decision time, and fictional students are not human observations. Hypothesis results can be positive, null or opposite. Technical acceptance never depends on the direction of a result.

## Run it

1. Open [RUN_EXPERIMENT.ipynb](notebooks/RUN_EXPERIMENT.ipynb).
2. Run all cells with the default `RUN_API = False` to review the plan, exact prompts, estimated cost and empty report for free.
3. When ready, change `RUN_API = True`, keep `PHASE = "all"`, and run all cells again.
4. In section 3, enter the OpenAI key and then the Anthropic key in the two hidden input fields. The progress bar shows completed requests and requests left.
5. Section 4 writes [the latest report](reports/REPORT.md), detailed CSV tables and an Excel workbook. If a call stops, run section 4 to inspect its saved status.

All four technical pilots must pass before any main call. A completed response is reused when resuming; invalid responses remain available for diagnosis. The shared budget ledger covers every attempt across this experiment's run folders. Null or opposite results do not trigger additional collection.

The current conservative reservation is approximately **$0.84 for eight first attempts**, or **$1.68 if every request needs its one permitted technical retry**. These are bounds using configured token caps and prices checked on 20 October 2026, not measured spending. The hard campaign cap is **$5**. No live API data were collected during setup; software checks use synthetic fixtures and are not H1/H2 evidence.

## Find everything for this experiment

| Folder | Contents |
| --- | --- |
| `hypotheses/` | Exact H1/H2, protocol, sample size, outcomes and stopping rule |
| `notebooks/` | Review and run notebook |
| `prompts/<run>/` | Exact API prompts and JSON schemas, organized by model and pilot/main phase |
| `data/<run>/` | Frozen plan, source snapshot and accepted JSON choices |
| `raw/` | Original provider requests/responses and failures, as organized by the API runner |
| `analysis/` | Recomputed physical states, chain costs, probe responses and comparisons |
| `reports/` | Human-readable conclusions, chain results and execution/spending status |

Shared implementation lives outside experiments in `src/beergame_study/` and reusable launchers in `scripts/`. Read [the frozen scientific protocol](hypotheses/PROTOCOL.md) before collecting data.

## What the numbers mean

- **H1 proxy:** How much an order falls when otherwise matched outstanding replenishment rises from 8 to 32 cases. A smaller response under pressure follows H1's predicted direction. This is not the original structural β.
- **H2:** Holding plus backlog cost across the four roles and exactly 24 weeks. Higher pressure-condition cost follows H2's predicted direction. No automatic extra weeks are included.
- **Technical pilot:** One separate two-chain response per model verifies JSON, factual rules and three inventory readbacks per chain. These chains are outside the main sample.
- **Sample size:** Ten matched chain pairs are generated together per model. There is only one main response per model; its chains, conditions, weekly choices and roles are not independent statistical participants. Results are descriptive, without p-values or significance claims.

## Validation and collection status

**42 new-study checks passed:** 11 game/protocol checks, 26 API accounting/retry/provenance checks and 5 report/CLI/notebook checks. The notebook's five code cells also ran in a real Jupyter kernel with review mode enabled and no errors. [Validation receipt](analysis/software_checks/VALIDATION.json) · [test log](analysis/software_checks/new_study_tests.log).

Temporary synthetic responses verified all eight response slots, 8,448 pilot/main role-week rows, budget accounting, resume without repeat calls, and CSV/Excel exports. These checks establish software behavior; live model comprehension and H1/H2 trends remain untested until keys are entered and collection runs.

20 October 2026: added a separate versioned implementation and prospective protocol. Preparation and offline checks make no API calls. Collection status and actual spending must be taken from saved run records, not inferred from this plan. Historical studies and their evidence remain separate.
