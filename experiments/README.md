# Experiment index

Each experiment has its own hypotheses, prompts, data, analysis, reports and notebooks. Shared code lives at the repository root.

| Experiment | Model / design |
| --- | --- |
| [Early Beer Game prototypes](01_early_beer_game_prototypes/README.md) | Before 4 October 2026; multiple historical models and protocols |
| [Nano token-budget pilot](02_nano_token_budget/README.md) | GPT-5.4 Nano; API decisions and separate offline checks |
| [Luna model comparison and follow-up](03_luna_model_comparison/README.md) | 5 October; Nano/Mini/Luna screen, then GPT-5.6 Luna games |
| [Mini student-reasoning study](04_mini_student_reasoning/README.md) | 11 October; GPT-5.4 Mini, fixed-high single-call protocol |
| [Mini initial decision and revision](05_mini_deliberation/README.md) | 11 October; GPT-5.4 Mini, deliberation protocol v2 |
| [Luna initial decision and revision](06_luna_deliberation/README.md) | 11 October; GPT-6 Luna Flex, deliberation protocol v3 |
| [Claude initial decision and revision](07_claude_deliberation/README.md) | 11 October; Claude Haiku 5.5, deliberation protocol v4 |
| [Manual cohort initial decision and revision](08_manual_cohort_revision/README.md) | 17–18 October; completed user-reported GPT-6 / Pro collection and separate preparations |
| [Static pressure-prompt development](09_pressure_prompt_development/README.md) | 18 October; bounded isolated-assistant development checks |
| [10-second / 180-second deadline framing](10_deadline_cohort/README.md) | 18 October; completed user-reported GPT-6 / Pro website sample; separate assistant pilot |
| [10-second / 60-second education study](11_education_deadline/README.md) | 19–20 October; prepared GPT-6 / Pro plan, assistant preflight, received GPT-6 Astra / extra high effort collection |
| [Whole-cohort API feasibility collection](12_pressure_framing_api_20261020/README.md) | Four models; 80 fictional testers / 20 chains / 24 decision weeks per model; one joint response per model; 1/4 accepted mains, zero Sol contrasts |

| [Weekly-state API experiment](13_weekly_state_api_20261021/README.md) | Four models; 80 fictional testers/model; Python calculates 24 weeks; 104 planned calls; same cumulative $5 ledger as experiment 12 |

The historical folders preserve distinct protocols and evidence. The new experiment has its own sample and shares experiment 12’s original $5 budget; historical samples are closed.

## Add a future experiment

Create the next numbered folder with a short descriptive name and a `README.md` linking its notebook, protocol and report. Give it its own `hypotheses/`, `prompts/`, `raw/`, `data/`, `analysis/`, `reports/` and `notebooks/` folders. Record model/settings, sample size, manipulation, outcomes, stopping rule and budget before collection. Keep reusable code under the root `src/`, `scripts/` and `tests/` folders. Add one row to this index; preserve previous experiments and unsuccessful attempts.

[Repository guide](../README.md)
