# Run the full game and view performance / β

1. Open **thoughts_reflection_experiment_v2.ipynb**, beside **beer_game_v2.py**. The selected settings are now API mode, full game, 8 groups per cell, 36 weeks, and a fresh v2-game-01 replicate.
2. The notebook first displays the original completed API game's performance and β results and runs a free estimator self-check.
3. For free verification, change MODE to "offline", restart the kernel, and Run All. This generates synthetic performance, β, and a report; it is not GPT evidence.
4. For real GPT data, MODE = "api" and STAGE = "game". The plan is 32 groups / 128 agents / 4,608 orders plus 128 rules checks. Eight groups per cell is only the current reporting floor, not a power guarantee. All planned blocks must have usable β for the current test.
5. The retained $3 local allowance may stop before completion. Review the printed cost scenarios; the allowance is not an estimate of the total cost or your account balance. Raising only BUDGET_USD resumes successful cached responses. Other changes create a new experiment.
6. Results appear directly in the notebook: condition performance, weekly graphs, role-level β with validity flags, and H1/H2_API status. Missing β remains explicitly unidentified. Game performance is reported for every group regardless of β validity.

## Changes

- Four-role beer-game mechanics retained, with varying demand paths matched across conditions within each block.
- Clear shared rules; similar-length control and supply-line training lessons with worked examples.
- Model: `gpt-5.4-mini-2026-03-17`, held constant across conditions.
- Low/high reasoning effort replaces 60/120-second deadlines. **H2_API concerns reasoning effort; it is not the original human time-pressure hypothesis.**
- Strict structured answers and exact state readbacks; standalone basic-rules checks for each role context.
- Incorrect, refused, or incomplete responses stop the run. No fabricated orders or adaptive retries until an answer is correct.
- Request checkpoints, progress bar, input/output/reasoning tokens, and local estimated spending guard.
- Two group/block-level hypothesis tests with two-sided p-values and Holm correction. P-values withheld for offline runs, fewer than eight complete blocks, or any excluded/incomplete planned block. Eight is a reporting floor, not a sample-size recommendation.
- Conclusions-first Markdown report and detailed CSVs saved in a fresh `results/v2_...` folder.

## Important distinctions

A valid reply means it follows the format and reads the state correctly. It does not mean the order must support H1/H2. An agent can correctly copy demand; β may then be unidentifiable. Diagnostic finite differences are not replacement β estimates. The diagnostic checks are separate calls, not evidence of persistent model learning. Cost/operational results and excluded estimates remain available even if hypothesis testing is withheld.

The revised demand process, instructions, output fields, model, and effort manipulation mean v2 is a new protocol. Do not pool its data with the original run. The original notebook and reports remain unchanged.

## Troubleshooting

- Local spending stop: raise only `BUDGET_USD` and rerun with identical settings. This is not your account balance.
- Actual failed request: preserve the failed pilot. Review its saved status, fix access/token settings if necessary, and use a fresh `REPLICATE_ID`. Successful calls may already have incurred charges.
- HTTP 401: check the API key/project. HTTP 429: check API credits and rate limits. Incomplete output: review the shared output allowance in a new pilot; do not change it mid-experiment.
- Keys are read from the environment or a hidden prompt and are not saved in results.

## Verification

Run `python test_v2.py` in an environment containing the requirements. Tests use synthetic data and a mocked OpenAI HTTP transport; they incur no charges. A fully executed offline notebook is also saved under `reports/software_checks/` after validation. These checks verify software behavior, not real API account access or model behavior.

API capabilities and rates were checked against the [official model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini), [reasoning guide](https://developers.openai.com/api/docs/guides/reasoning), and [structured outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs), 2026-09-27.

## Update: full-game dashboard

The selected notebook settings now run `STAGE = "game"`, `GROUPS_PER_CELL = 8`, `WEEKS = 36`, with a fresh `v2-game-01` replicate. The user's API mode and $3 local allowance are retained. Set MODE to offline for a free run; the API full game may exceed the allowance. Do not repeat the diagnostic stage merely to obtain performance or β—it cannot produce either.

The notebook now opens the original completed API game's performance and β tables without API calls. It checks the estimator using known β values before any new paid requests. A completed full game displays supply-chain metrics, weekly plots, usable β estimates, and hypothesis status directly. Performance includes every group even if β is unidentified. No automatic fallback outcome is substituted for H1/H2.
