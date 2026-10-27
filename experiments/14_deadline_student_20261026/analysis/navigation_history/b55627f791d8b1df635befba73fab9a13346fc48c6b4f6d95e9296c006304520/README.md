# Beer Game experiments

**Current: [Experiment 14](experiments/14_deadline_student_20261026/README.md) ? GPT-6 Astra, extra-high effort, ten planned four-role chains per condition.**

| Open this | What it contains |
|---|---|
| [Experiment 14 report ? PDF](experiments/14_deadline_student_20261026/reports/REPORT.pdf) | Current results, measurements and limitations |
| [Experiment 14 report ? text](experiments/14_deadline_student_20261026/reports/REPORT.md) | Same findings with links to extracted tables |
| [Experiment 14 figures](experiments/14_deadline_student_20261026/reports/figures/README.md) | Current plots and short explanations |
| [Experiment 14 notebook](experiments/14_deadline_student_20261026/notebooks/EXPERIMENT_14.ipynb) | Read-only progress and offline report refresh |
| [Experiment 14 exact materials](experiments/14_deadline_student_20261026/prompts/README.md) | Student prompts, readings and measurement scenarios |
| [All experiments](experiments/README.md) | Separate guides for experiments 1?14 |
| [Agent handoff](AGENT_HANDOFF.md) | Current state and continuation instructions |

**Development result:** 16 isolated-agent cases finished: four latency references and twelve feasibility cases. All four adequate-time feasibility cases completed; one of eight restricted-time cases completed. Seven stopped at enforced response deadlines. Neither tested wording passed the registered completion gate. Main collection remains **0/10 matched blocks**, with no main H1?H4 p-values. The next design decision is whether to study prompted student time pressure or actual model response deadlines; those are different treatments.

The ten planned main chains each receive their own fresh context per condition. There would be 960 weekly orders per condition, but ten independent matched chain comparisons. Development responses never enter main inference. These are fictional students; no human-student data validate them. No provider API calls were made for experiment 14. The existing cumulative API cap and spending ledger remain unchanged.

Experiment 13 is **closed**. Its [final report](experiments/13_weekly_state_api_20261021/reports/agent_collection_v5/REPORT.md), [PDF](experiments/13_weekly_state_api_20261021/reports/agent_collection_v5/REPORT.pdf), and [slide figures](experiments/13_weekly_state_api_20261021/reports/agent_collection_v5/slides_current/README.md) remain available. Do not mix its samples with experiment 14.

Each experiment owns `hypotheses/`, `prompts/`, `data/`, `analysis/`, `reports/` and `notebooks/`. Shared implementations, commands and checks live in `src/`, `scripts/` and `tests/`. [Maintenance instructions](maintenance/README.md) explain the historical reorganization and replay workflow. Older navigation bytes are preserved under experiment 14's `analysis/navigation_history/`.

Historical integrity limitations remain: the canonical checkout does not match every historical hash. Earlier rechecks found line-ending-only differences; do not claim a clean historical byte baseline or rewrite frozen studies to repair it. See the maintenance guide and experiment 13's saved integrity receipts.
