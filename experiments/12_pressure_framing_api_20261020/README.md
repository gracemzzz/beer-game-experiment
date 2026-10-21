# Experiment 12: API pressure-framing study

**Question:** Does a model representing students under strong time pressure respond less to outstanding orders and produce higher Beer Game costs?

**Current status:** The first pilot stopped: GPT-5.6 Luna and Sol passed; GPT-6 Luna returned wrong inventory checkpoints; Claude reached its output cap before returning JSON. **No main cohort was collected.** Recorded spending is approximately **$0.0717**. A bounded recovery is prepared; its live success is not yet verified. Read [the diagnosis and recovery plan](hypotheses/RECOVERY_20261021.md).

**Plan:** Four requested models; **80 fictional testers / 20 four-person chains per model**; ten chains per condition; **24 model-decision weeks**. **One main API call generates all 20 chains for a model.** Total authorized spending is **$5**, including the original pilots, two additional recovery pilots, four main calls, failures and technical retries.

This is a new prospective study. Imagined pressure does not enforce actual decision time, and fictional students are not human observations. Hypothesis results can be positive, null or opposite. Technical acceptance never depends on the direction of a result.

## Run it

1. Close and reopen [RUN_EXPERIMENT.ipynb](notebooks/RUN_EXPERIMENT.ipynb) to load the updated cells, then **restart its kernel** so it loads the recovery implementation.
2. Run all cells with the default `RUN_API = False` to review the recovery plan, exact prompts, estimated remaining cost and saved status for free.
3. When ready, change `RUN_API = True`, keep `PHASE = "all"`, and run all cells again.
4. In section 3, enter the OpenAI key and then the Anthropic key in the two hidden input fields. The progress bar shows completed requests and requests left.
5. Section 4 writes [the latest report](reports/REPORT.md), detailed CSV tables and an Excel workbook. If a call stops, run section 4 to inspect its saved status.

All four technical pilots must pass before any main call. The recovery reuses the two accepted GPT-5.6 pilots and schedules one new pilot each for GPT-6 Luna and Claude. Original failures remain invalid and available for diagnosis. The shared budget ledger covers every attempt across this experiment's run folders. Null or opposite results do not trigger additional collection.

The original four pilot requests recorded **$0.0716918** in estimated charges. Recovery and main requests share the original **$5 hard cap**; the notebook displays their updated conservative reservation before execution. GPT-6 uses medium effort and larger output caps with explicit physical bookkeeping. Claude retains low adaptive thinking with more output room for JSON. GPT-5.6 settings stay unchanged. These changes may improve completion; they do not guarantee valid data or favorable hypotheses. [Exact settings and original evidence](hypotheses/RECOVERY_20261021.md).

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

Shared implementation lives outside experiments in `src/beergame_study/` and reusable launchers in `scripts/`. Read [the original frozen scientific protocol](hypotheses/PROTOCOL.md) together with [the prospective technical recovery amendment](hypotheses/RECOVERY_20261021.md) before continuing. The amendment uses a separate namespace and preserves original evidence and source snapshots.

## What the numbers mean

- **H1 proxy:** How much an order falls when otherwise matched outstanding replenishment rises from 8 to 32 cases. A smaller response under pressure follows H1's predicted direction. This is not the original structural β.
- **H2:** Holding plus backlog cost across the four roles and exactly 24 weeks. Higher pressure-condition cost follows H2's predicted direction. No automatic extra weeks are included.
- **Technical pilot:** One separate two-chain response per model verifies JSON, factual rules and three inventory readbacks per chain. These chains are outside the main sample.
- **Sample size:** Ten matched chain pairs are generated together per model. There is only one main response per model; its chains, conditions, weekly choices and roles are not independent statistical participants. Results are descriptive, without p-values or significance claims.

## Validation and collection status

**Recovery verification: 52 checks passed**, including 10 dedicated recovery checks. All five updated notebook code cells executed in review mode with no API calls. The two accepted pilots and all 19 original evidence files stayed byte-identical. The recovery's six first attempts reserve approximately **$0.616**; prior spending remains approximately **$0.072**. [Recovery validation](analysis/software_checks/RECOVERY_VALIDATION_20261021.json) · [recovery test log](analysis/software_checks/recovery_tests_20261021.log). New live recovery responses have not yet been collected.

**42 new-study checks passed:** 11 game/protocol checks, 26 API accounting/retry/provenance checks and 5 report/CLI/notebook checks. The notebook's five code cells also ran in a real Jupyter kernel with review mode enabled and no errors. [Validation receipt](analysis/software_checks/VALIDATION.json) · [test log](analysis/software_checks/new_study_tests.log).

Temporary synthetic responses verified all eight original response slots, 8,448 pilot/main role-week rows, budget accounting, resume without repeat calls, and CSV/Excel exports. These are software checks. The subsequent live original pilot produced two accepted and two failed responses; the main H1/H2 comparison remains uncollected. Recovery validation and execution receipts must be read separately from these original setup checks.

20 October 2026: added a separate versioned implementation and prospective protocol. Preparation and offline checks make no API calls. Collection status and actual spending must be taken from saved run records, not inferred from this plan. Historical studies and their evidence remain separate.

21 October 2026: diagnosed the actual pilot failures and prepared a bounded technical recovery. Original successes are reused with lineage; failures and frozen sources are preserved. The same physical model and acceptance checks apply. Results remain exploratory: different provider settings and one jointly generated cohort per model prevent a clean model-only comparison or independent-chain significance claim.
