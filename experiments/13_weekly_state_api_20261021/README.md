# Experiment 13: weekly API Beer Game

**Start here: [RUN_EXPERIMENT.ipynb](notebooks/RUN_EXPERIMENT.ipynb).**

1. **Python runs the game.** Each model receives current states and returns only 80 orders for the current week. Python computes shipments, inventories, backlog and costs. Future demand is hidden.
2. **Same sample:** four models; 80 fictional testers in 20 four-role chains per model; ten chains per pressure condition; 24 weeks.
3. **104 planned calls:** four full-size format pilots, 96 weekly decisions and four probe batches. At most one retry per transient technical error. No response is repeated to obtain a favorable effect.
4. **Same $5 cumulative budget:** includes the $0.3404859 already recorded in experiment 12. Before new collection, about $4.6595141 remains. All new attempts use that existing ledger.
5. **Interpret carefully:** this compares imagined pressure framing, not measured binding time. Batched choices remain dependent. No student-level significance or structural β is claimed.

## Run it

1. Open the new notebook above and **restart its kernel**.
2. Run all cells with `RUN_API=False` to review the plan and budget without paid calls.
3. Change `RUN_API=True`, keep `PHASE="all"`, then run all cells again.
4. Enter both keys into section 3's hidden fields. The notebook runs pilots and games automatically; no calibration-to-game switch is needed.
5. Read section 4 or [reports/REPORT.md](reports/REPORT.md). The report begins with conclusions and links the Excel workbook and all CSV files.

Accepted weeks are saved before the next request. Rerunning reuses verified accepted responses. An invalid response stops that model, preserving its evidence; other models can continue. A budget stop cannot be bypassed by changing the run label. No missing orders are filled in, and partial games are not treated as full 24-week H2 observations.

## Cost planning

The notebook shows conservative reservations for all 104 first attempts, using every output allowance and an input-byte bound. A separate stressed input-size estimate allows unusually large state/history numbers. These are planning bounds under the recorded prices, not predicted invoices. Failed/unknown-charge attempts and retries also consume the same allowance; the runner stops before a request whose reservation would exceed it. [Offline cost-planning receipt](analysis/software_checks/COST_PLANNING_20261021.json).

## What changed after experiment 12

The whole-cohort method produced incorrect inventories or a missing cohort for three models. Those requests did not hit their token limits. The new method removes model-calculated inventory checkpoints entirely. Each reply must contain every chain and role as required JSON keys, preventing an empty list from appearing complete. The technical pilot uses the actual 80-order response size.

OpenAI reasoning is `none`; Claude thinking is disabled with low effort. Both pressure conditions use identical settings. These are latency/cost controls, not the treatment. Output allowances are 2,048 tokens for pilot/weekly decisions and 4,096 for probes. There is no temperature override. The new settings and interaction protocol form a separate study; do not pool its results with experiment 12.

## Where everything lives

| Folder | Contents |
| --- | --- |
| [hypotheses/](hypotheses/) | H1/H2, prospective protocol, settings and stopping rules |
| [notebooks/](notebooks/) | Run and review notebook |
| [prompts/](prompts/) | Exact messages and schemas saved before each request |
| [data/](data/) | Frozen plan/source snapshot, accepted choices, status and receipts |
| [raw/](raw/) | Provider responses, including failures |
| [analysis/](analysis/) | Python states, chain costs, order patterns, probes and hypothesis tables |
| [reports/](reports/) | Conclusions first, full report and prior report versions |

Common code: `src/beergame_study/weekly_pressure*.py`. The notebook builder is `scripts/create_weekly_pressure_notebook.py`. Experiment 12 owns the shared budget ledger; experiment 13 records a relative pointer and preserves prior charges.

## How to read results

- **H1 proxy:** reduction in orders when matched outstanding replenishment increases from 8 to 32, divided by 24. A smaller response under strong pressure follows the predicted direction. It does not identify structural β or an optimal benchmark.
- **H2:** total holding plus backlog cost across four roles and 24 weeks. Larger pressure-condition cost follows H2. Terminal stock, backlog and outstanding orders are reported separately.
- **Bullwhip:** variance of a role's orders divided by variance of customer demand over the same weeks. A ratio above 1 indicates amplification. Zero demand variance is undefined.
- **Zero or constant orders:** reported honestly, never rejected solely for their pattern. An accounting-consistent choice is not proof of realistic student behavior.
- **Null/opposite effects:** valid descriptive outcomes; no prompt tuning or repeated samples until significance.

The batch exposes every included state to a single model. Instructions to keep fictional students separate do not enforce information isolation or independence. Actual state trajectories are maintained by Python, but a valid JSON reply cannot verify the model's internal reasoning or realism.

## Free software verification

From the project root, run `python -m unittest discover -s tests -p 'test_weekly_pressure*.py' -v` in the project's Python environment. These tests use temporary synthetic responses and mocked HTTP; they make no paid calls. They check state propagation, required choices, shared spending, failures, resume, provenance and notebook/report behavior. Synthetic checks are never included in the study's observations. Live provider behavior still needs the notebook's full-size format pilots.

## Documentation

Generation controls were checked on 21 October 2026 in official [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol) and [Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5) documentation. Structured output definitions use the supported internal-reference subsets described by [OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs) and [Anthropic](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

**Prepared and verified, 21 October 2026:** 30 new tests and 60 previous-study regression checks passed. The notebook's five code cells also completed in a real Jupyter kernel in free review mode, without changing the shared ledger. Mocked tests exercised all 104 planned requests and the notebook's hidden-key input path. No new paid requests were made. [Validation receipt](analysis/software_checks/VALIDATION_20261021.json).

The exact current planning totals are **$3.3746** in first-attempt reservations for ordinary synthetic states and **$4.3282** for the conservative input-size scenario. Including prior spending gives **$3.7151** / **$4.6687**. Both use the full output allowances; actual charges may be lower, while retries consume extra allowance. The cap remains $5.
