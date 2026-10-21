# Experiment 12: API pressure-framing study

**Question:** Does a model representing students under strong time pressure respond less to outstanding orders and produce higher Beer Game costs?

**Current status:** **Three GPT pilots pass. Claude alone fails inventory arithmetic.** Claude now finishes its JSON normally, using only 3,519 of 32,768 allowed tokens, but its week-12 and week-24 stock figures are incorrect. **No main cohort was collected.** Recorded spending is approximately **$0.0759**. The next fixed stage reuses all three accepted pilots and schedules **one Claude pilot plus four main calls**. [Current diagnosis and Claude follow-up](hypotheses/CLAUDE_FOLLOWUP_20261021.md) · [first recovery history](hypotheses/RECOVERY_20261021.md).

**Plan:** Four requested models; **80 fictional testers / 20 four-person chains per model**; ten chains per condition; **24 model-decision weeks**. **One main API call generates all 20 chains for a model.** Total authorized spending is **$5**, including every original pilot, recovery/follow-up pilot, main call, failure and technical retry.

This is a new prospective study. Imagined pressure does not enforce actual decision time, and fictional students are not human observations. Hypothesis results can be positive, null or opposite. Technical acceptance never depends on the direction of a result.

## Run it

1. Close and reopen [RUN_EXPERIMENT.ipynb](notebooks/RUN_EXPERIMENT.ipynb) to load the updated cells, then **restart its kernel** so it loads the recovery implementation.
2. Run all cells with the default `RUN_API = False` to review the automatically selected Claude follow-up, exact prompts, estimated cost and saved status for free.
3. When ready, change `RUN_API = True`, keep `PHASE = "all"`, and run all cells again.
4. In section 3, enter the OpenAI key and then the Anthropic key in the two hidden input fields. The progress bar shows completed requests and requests left.
5. The API cell now updates [the latest report](reports/REPORT.md) automatically on completion, including a failed result. Section 4 displays it together with detailed CSV tables and an Excel workbook. If the cell raises an exception, run section 4 to inspect saved status.

All four technical pilots must pass before any main call. This follow-up reuses GPT-6 Luna and both GPT-5.6 pilots. Only Claude receives a new pilot, with medium adaptive effort and the explicit neutral state-accounting appendix. Original failures remain invalid and available for diagnosis. The shared budget ledger covers every attempt across this experiment's run folders. Null or opposite results do not trigger additional collection.

The six requests so far recorded **$0.07590755** in estimated charges. The five follow-up first attempts reserve approximately **$0.606**, within the same **$5 hard cap**. Claude's caps stay at 32,768 pilot / 65,536 main tokens; the change targets accounting and reasoning, since its latest failure was not truncation. Other models' main payloads stay unchanged. These changes do not guarantee valid data or favorable hypotheses. [Exact settings and evidence](hypotheses/CLAUDE_FOLLOWUP_20261021.md).

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

**Claude follow-up verification: 60 checks passed**, including eight new follow-up tests. The updated notebook ran in free review mode; a separate mocked API run verified one Claude pilot followed by four main requests and automatic report export. All 45 protected earlier evidence files stayed byte-identical. No live follow-up calls have been made. [Follow-up validation](analysis/software_checks/FOLLOWUP_VALIDATION_20261021.json) · [test log](analysis/software_checks/followup_tests_20261021.log).

**Earlier recovery verification: 52 checks passed**, including 10 dedicated recovery checks. At that stage, all five notebook code cells executed in review mode, two accepted pilots and 19 original evidence files stayed byte-identical, the six first-attempt reservation was approximately **$0.616**, and prior spending was approximately **$0.072**. [Recovery validation](analysis/software_checks/RECOVERY_VALIDATION_20261021.json) · [recovery test log](analysis/software_checks/recovery_tests_20261021.log). These checks preceded the live recovery that subsequently accepted GPT-6 and rejected Claude's inventory arithmetic.

**42 new-study checks passed:** 11 game/protocol checks, 26 API accounting/retry/provenance checks and 5 report/CLI/notebook checks. The notebook's five code cells also ran in a real Jupyter kernel with review mode enabled and no errors. [Validation receipt](analysis/software_checks/VALIDATION.json) · [test log](analysis/software_checks/new_study_tests.log).

Temporary synthetic responses verified all eight original response slots, 8,448 pilot/main role-week rows, budget accounting, resume without repeat calls, and CSV/Excel exports. These are software checks. The subsequent live original pilot produced two accepted and two failed responses; the main H1/H2 comparison remains uncollected. Recovery validation and execution receipts must be read separately from these original setup checks.

20 October 2026: added a separate versioned implementation and prospective protocol. Preparation and offline checks make no API calls. Collection status and actual spending must be taken from saved run records, not inferred from this plan. Historical studies and their evidence remain separate.

21 October 2026: diagnosed the actual pilot failures and prepared a bounded technical recovery. Original successes are reused with lineage; failures and frozen sources are preserved. The same physical model and acceptance checks apply. Results remain exploratory: different provider settings and one jointly generated cohort per model prevent a clean model-only comparison or independent-chain significance claim.
