# Claude Haiku 5.5: findings and next run

Run claude_api_fd5533fef5828d96; status complete. Completed chains: 16; Model-controlled orders: 1280. Calibration passed: True; game computation separation passed: True. Four fictional UB sophomore profiles were used, with the same Claude Haiku 5.5 model and high effort in both conditions.

## What happened to the hypotheses

Game costs in the outcome tables are simulated holding/backlog costs, separate from API spending.

| Outcome | Short | Adequate | Short - adequate | Observed direction |
| --- | --- | --- | --- | --- |
| Pipeline sensitivity (revised H1) | 0.397135 | 0.5 | -0.102865 | Predicted direction |
| Full scored cost (H2) | 864.062 | 941.312 | -77.25 | Opposite direction |
| Bullwhip (primary H3) | 0.361597 | 0.435084 | -0.0734873 | Opposite direction |

Pipeline sensitivity (revised H1): Evidence in the predicted direction within this configured model experiment (Holm-adjusted p=0.01599).

Full scored cost (H2): Inconclusive at the prespecified familywise 0.05 level (Holm-adjusted p=0.3273). This does not establish that the conditions are equivalent.

Bullwhip (primary H3): Inconclusive at the prespecified familywise 0.05 level (Holm-adjusted p=0.3273). This does not establish that the conditions are equivalent.

Every chain-average customer-referenced variance ratio is below 1 in this run. A higher ratio between conditions is a relative difference in order variability; it does not demonstrate chain-average amplification above customer-demand variance. Individual local-demand ratios are reported separately in roles.csv.

| Hypothesis | Pairs | Difference | 95% lower | 95% upper | Holm p |
| --- | --- | --- | --- | --- | --- |
| H1 | 8 | -0.102865 | -0.163991 | -0.0417383 | 0.0159872 |
| H2 | 8 | -77.25 | -216.743 | 62.2428 | 0.32726 |
| H3 | 8 | -0.0734873 | -0.185155 | 0.0381804 | 0.32726 |

Intervals are marginal 95% paired t intervals; p-values are adjusted over the three planned hypotheses using Holm. A small p-value tests a zero mean difference; support for a directional hypothesis also requires the predicted sign. A nonsignificant result does not establish equivalence. Eight pairs is an exploratory floor, not an adequate-power guarantee.

Weekly calls and the four roles are not independent students. The independent unit is a matched block of two chains. The full report retains all eligibility checks and any available confidence intervals and adjusted p-values.

Bullwhip is the mean of the four role order-variance/customer-demand-variance ratios over the 20 model weeks. Cost includes practice, model weeks and the 12-week automatic continuation. The revised H1 uses separate matched states with a 24-case pipeline difference; it does not identify the original dynamic beta.

![All independent paired outcome differences](paired_contrasts.png)

## Completion, orders and actual computation

| Condition | Orders | Zero orders | Order range | Distinct quantities |
| --- | --- | --- | --- | --- |
| adequate | 640 | 67 | 0 to 12 | 11 |
| short | 640 | 54 | 0 to 10 | 10 |

| Condition | Median total tokens | Changed by revision | Zero despite empty stock/pipeline and backlog |
| --- | --- | --- | --- |
| adequate | 1121 | 224 | 0 |
| short | 506 | 0 | 0 |

Median short/adequate generated-token ratio: 0.4513826940231936; the prespecified maximum was 0.75. Both initial and revision tokens count. Initial ceiling: 16,384; additional revision ceiling: 8,192. These are ceilings, not observed usage. Temperature is omitted identically; the common 900-second timeout is technical infrastructure.

Order zero remains a valid model choice. No preferred maximum, positive floor or artificial variation is imposed. Fallback orders recorded: 0. A completed game checks operation; it does not validate the profiles against actual students.

| condition | phase | cost |
| --- | --- | --- |
| adequate | automatic | 3273.5 |
| adequate | model | 3489 |
| adequate | practice | 768 |
| short | automatic | 2559 |
| short | model | 3585.5 |
| short | practice | 768 |

Across recorded chains, the short-minus-adequate cost difference is 96.5 during model weeks and -714.5 during automatic continuation (-618 over all scored weeks).

Per paired block, the corresponding mean differences are 12.0625 during model weeks and -89.3125 during automatic continuation, with -77.25 total. This uses the same averaging unit as H2.

The automatic continuation repeats the last order and is not LLM behavior. Compare its cost with the model-week cost before attributing the full-cost contrast to decisions throughout the game.

Original structural beta: 52/64 role fits pass the existing usability checks; 7 chains have four usable role fits, yielding 1 complete paired blocks. An unusable coefficient is not evidence about supply-line neglect. The revised H1 probe result does not validate the original coefficient. The complete diagnostics remain in beta_fits.csv and the full report.

## What was spent

| Stage | Estimated USD |
| --- | --- |
| game | 0.997264 |
| probe | 0.0455875 |
| rules | 0.00641452 |
| calibration | 0.0166529 |

This Claude Haiku 5.5 run: $1.06591941. Prior campaign spending: $5.98133807; combined campaign ledger: $7.04725748. These are conservative usage-based estimates including cache-write rates, not an invoice. They exclude taxes and unrelated account activity. The earlier $0.7198179 Mini calibration remains a separate failed-model screen.

Total charged/reserved for the under-$3 redesign, including previous Mini/Luna calls: $1.85365073. The separate historical single-call pilot cost $5.19360675 before the redesign allowance; it remains in the original campaign ledger above.

Hard guards: $2.15 for this run, $0.18 for its fresh calibration, $2.95 for all redesign runs together, and $10 for the original campaign including the earlier $5.19360675 pilot. Completed evidence and report generation are free to reuse; no new calls are made by this summary.

## Run it yourself in Jupyter

Open notebooks/05_claude_deliberation_study.ipynb in the Beer Game (.venv) kernel. All paid flags default off. WATCH_RUNNING=True displays the background progress bar without buying calls. The Review results cell reads saved evidence without a key.

For a new prospective run, set MODE='api', RUN_CALIBRATION=False, RUN_GAMES=True, choose PAIRS and WEEKS before running, and give REPLICATE_ID a new value. Set CALIBRATION_RUN=ROOT/'data/runs/claude_api_fd5533fef5828d96' to reuse this passed calibration if sources are unchanged. Enter the key only in the masked notebook prompt. Keep CAMPAIGN_ID unchanged; all prior spending still counts.

Use a pair count divisible by four to balance profile-role assignments. The notebook power calculation requires a scientifically meaningful effect-size assumption; eight pairs is only the inference reporting floor. New replicate IDs create new API draws but the default seed repeats the same indexed demand paths. Do not pool incompatible horizons, models or protocols or count repeated demand paths as new demand scenarios.

## What this pilot can establish

Passing completion and computation checks establishes a usable experiment on configured LLM participants. Extra revision combines additional computation with reconsideration; it does not isolate information overload, a pure single-call token cap, or human time pressure. No student data exist, and persona fidelity remains unvalidated. Replication may produce a positive, null, opposite or inconclusive result. Preserve every result and do not retune for the desired direction.

Full analysis: REPORT.md / Claude_Study_Report.docx. Numerical tables: DETAILS.xlsx. Raw requests, exact prompts, usage and source snapshots: the source run under data/runs/. Design and primary literature: reports/revised_design_20261011/REPORT.md.

![Order trajectories by role](orders.png)
