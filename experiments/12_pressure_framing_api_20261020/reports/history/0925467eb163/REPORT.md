# Experiment 12: conclusions first

1. **Collection:** 1/4 main responses and 4/4 pilot responses accepted. **Current failure:** gpt-6-luna: inventory calculations disagree with the game engine; gpt-5.6-luna: inventory calculations disagree with the game engine; claude-haiku-5-5: response validation. 0 main calls blocked.
2. **H1/H2 findings:** gpt-5.6-sol H1: +0.0000 (zero); gpt-5.6-sol H2: +0.0000 (zero). Differences are strong pressure minus no pressure; these are descriptive findings.
3. **Interpretation:** This tests imagined pressure framing. It does not establish a binding deadline, original structural β, or effects on real students.
4. **Statistical independence:** All 20 chains and both conditions share one main response per model. No p-values or inferential confidence intervals are reported.
5. **Budget:** $0.3405 charged or conservatively reserved out of the authorized $5 total across this experiment, including pilot and retries.
6. **Claude follow-up:** Three accepted GPT pilots are reused. One revised Claude pilot is scheduled with medium effort and explicit physical bookkeeping; both earlier Claude failures remain preserved.

## Design

Each model represents 80 fictional students in 20 four-role chains: 10 no-pressure and 10 strong-pressure chains. Each chain submits all 24 weeks at once. H2 includes only those 24 weeks; there are no automatic continuation costs. Matched chains share demand paths and profile assignments. Four disjoint two-chain pilot responses are outside the main sample.

Recovery settings: GPT-6 Luna uses medium effort with 16,384 pilot / 32,768 main output tokens and an explicit accounting algorithm. Claude Haiku uses adaptive thinking at medium effort with 32,768 pilot / 65,536 main output tokens and explicit physical queue bookkeeping plus a concise-completion reminder. Both GPT-5.6 models retain low effort and their original settings. Settings are identical across pressure conditions within each model, but differ across models; model comparisons therefore include settings differences. These are completion allowances, not the experimental pressure manipulation. Provider effort labels are not equivalent measurements of computation.

## Findings by model

| model | hypothesis | paired_blocks | mean_strong_minus_no | descriptive_direction |
| --- | --- | --- | --- | --- |
| gpt-6-luna | H1 | 0 | — | unavailable |
| gpt-6-luna | H2 | 0 | — | unavailable |
| gpt-5.6-luna | H1 | 0 | — | unavailable |
| gpt-5.6-luna | H2 | 0 | — | unavailable |
| gpt-5.6-sol | H1 | 10 | 0.0000 | zero |
| gpt-5.6-sol | H2 | 10 | 0.0000 | zero |
| claude-haiku-5-5 | H1 | 0 | — | unavailable |
| claude-haiku-5-5 | H2 | 0 | — | unavailable |

**H1:** mean reduction in order divided by a 24-case increase in outstanding dispatched replenishment, over eight matched probes per chain. A smaller sensitivity under strong pressure is consistent with the predicted proxy direction. This does not identify an optimal benchmark or the original structural coefficient.

**H2:** cumulative chain holding cost ($0.50 per case-week) plus backlog cost ($1 per case-week). A positive strong-minus-no-pressure difference follows the prediction. There is no revenue or factory production fee.

## Completion and technical checks

| model | accepted_pilot_responses | accepted_main_responses | accepted_main | complete |
| --- | --- | --- | --- | --- |
| gpt-6-luna | 1 | 0 | 0 | False |
| gpt-5.6-luna | 1 | 0 | 0 | False |
| gpt-5.6-sol | 1 | 1 | 20 | True |
| claude-haiku-5-5 | 1 | 0 | 0 | False |

Acceptance requires all chain IDs, 24 order rows, probes, factual rules and inventory readbacks at weeks 1, 12 and 24. All four pilot slots must pass before main collection, including the three inherited accepted GPT pilots. This follow-up provides one revised Claude pilot generation. Prior failures are retained. Further semantic retries, replacements, clipping and filled-in orders are not used. At most one retry is allowed for a transient transport/rate/server error, with its cost reserved.

## Preserved pilot diagnosis

- GPT-6 Luna returned complete choices, but its week-12 and week-24 inventory readbacks disagreed with independent game replay. It was not an API connection or balance failure.
- Claude Haiku returned HTTP 200 with `stop_reason=max_tokens`: all 8,192 output tokens were reasoning tokens and there was no answer text. This was truncation, not a refusal.
- Original recorded charge estimate: $0.0716918. All old charges remain in the shared $5 ledger. The first recovery scheduled two pilot calls and four main calls before possible transient retries.
- Software verification cannot guarantee the next model-generated trajectories pass. A new failure remains visible and does not become a fabricated participant.

[Recovery amendment](../../../hypotheses/RECOVERY_20261021.md) · [Frozen current inputs and status](../../../data/pressure_api_c04ef16c05dd826c/followup/pressure_followup_aa5649bfb1e797ee)

### Outcome of the first recovery

GPT-6 Luna passed. Claude finished JSON normally using 3,519 of 32,768 output tokens, but four inventory checkpoints were incorrect. This follow-up addresses state bookkeeping rather than increasing the cap again. Three accepted pilots are inherited; only Claude receives another pilot generation. Cumulative recorded spending before this stage was $0.07590755.

[Claude follow-up amendment](../../../hypotheses/CLAUDE_FOLLOWUP_20261021.md)

| task_id | status | reason |
| --- | --- | --- |
| gpt-6-luna_pilot | accepted | — |
| gpt-5.6-luna_pilot | accepted | — |
| gpt-5.6-sol_pilot | accepted | — |
| claude-haiku-5-5_pilot | accepted | — |
| gpt-6-luna_main | invalid | response_validation |
| gpt-5.6-luna_main | invalid | response_validation |
| gpt-5.6-sol_main | accepted | — |
| claude-haiku-5-5_main | invalid | response_validation |

### Current failed checks

**gpt-6-luna (main):** inventory calculations disagree with the game engine.

- main_b07_c0: Physical inventory readback mismatch at week 12.
- main_b07_c0: Physical inventory readback mismatch at week 24.
- main_b05_c1: Physical inventory readback mismatch at week 12.
- main_b05_c1: Physical inventory readback mismatch at week 24.
- main_b03_c1: Physical inventory readback mismatch at week 12.
- main_b03_c1: Physical inventory readback mismatch at week 24.
- main_b02_c0: Physical inventory readback mismatch at week 12.
- main_b02_c0: Physical inventory readback mismatch at week 24.
- main_b09_c1: Physical inventory readback mismatch at week 12.
- main_b09_c1: Physical inventory readback mismatch at week 24.
- main_b01_c0: Physical inventory readback mismatch at week 12.
- main_b01_c0: Physical inventory readback mismatch at week 24.
- main_b07_c1: Physical inventory readback mismatch at week 12.
- main_b07_c1: Physical inventory readback mismatch at week 24.
- main_b00_c0: Physical inventory readback mismatch at week 12.
- main_b00_c0: Physical inventory readback mismatch at week 24.
- main_b01_c1: Physical inventory readback mismatch at week 12.
- main_b01_c1: Physical inventory readback mismatch at week 24.
- main_b04_c1: Physical inventory readback mismatch at week 12.
- main_b04_c1: Physical inventory readback mismatch at week 24.
- main_b08_c0: Physical inventory readback mismatch at week 12.
- main_b08_c0: Physical inventory readback mismatch at week 24.
- main_b02_c1: Physical inventory readback mismatch at week 12.
- main_b02_c1: Physical inventory readback mismatch at week 24.
- main_b08_c1: Physical inventory readback mismatch at week 12.
- main_b08_c1: Physical inventory readback mismatch at week 24.
- main_b00_c1: Physical inventory readback mismatch at week 12.
- main_b00_c1: Physical inventory readback mismatch at week 24.
- main_b06_c0: Physical inventory readback mismatch at week 12.
- main_b06_c0: Physical inventory readback mismatch at week 24.
- main_b05_c0: Physical inventory readback mismatch at week 12.
- main_b05_c0: Physical inventory readback mismatch at week 24.
- main_b09_c0: Physical inventory readback mismatch at week 12.
- main_b09_c0: Physical inventory readback mismatch at week 24.
- main_b03_c0: Physical inventory readback mismatch at week 12.
- main_b03_c0: Physical inventory readback mismatch at week 24.
- main_b06_c1: Physical inventory readback mismatch at week 12.
- main_b06_c1: Physical inventory readback mismatch at week 24.
- main_b04_c0: Physical inventory readback mismatch at week 12.
- main_b04_c0: Physical inventory readback mismatch at week 24.

**gpt-5.6-luna (main):** inventory calculations disagree with the game engine.

- main_b06_c0: Physical inventory readback mismatch at week 1.
- main_b06_c0: Physical inventory readback mismatch at week 12.
- main_b06_c0: Physical inventory readback mismatch at week 24.
- main_b07_c1: Physical inventory readback mismatch at week 1.
- main_b07_c1: Physical inventory readback mismatch at week 12.
- main_b07_c1: Physical inventory readback mismatch at week 24.
- main_b09_c0: Physical inventory readback mismatch at week 12.
- main_b09_c0: Physical inventory readback mismatch at week 24.
- main_b06_c1: Physical inventory readback mismatch at week 1.
- main_b06_c1: Physical inventory readback mismatch at week 12.
- main_b06_c1: Physical inventory readback mismatch at week 24.
- main_b02_c0: Physical inventory readback mismatch at week 1.
- main_b02_c0: Physical inventory readback mismatch at week 12.
- main_b02_c0: Physical inventory readback mismatch at week 24.
- main_b09_c1: Physical inventory readback mismatch at week 12.
- main_b09_c1: Physical inventory readback mismatch at week 24.
- main_b07_c0: Physical inventory readback mismatch at week 1.
- main_b07_c0: Physical inventory readback mismatch at week 12.
- main_b07_c0: Physical inventory readback mismatch at week 24.
- main_b05_c0: Physical inventory readback mismatch at week 1.
- main_b05_c0: Physical inventory readback mismatch at week 12.
- main_b05_c0: Physical inventory readback mismatch at week 24.
- main_b04_c1: Physical inventory readback mismatch at week 12.
- main_b04_c1: Physical inventory readback mismatch at week 24.
- main_b01_c1: Physical inventory readback mismatch at week 1.
- main_b01_c1: Physical inventory readback mismatch at week 12.
- main_b01_c1: Physical inventory readback mismatch at week 24.
- main_b05_c1: Physical inventory readback mismatch at week 1.
- main_b05_c1: Physical inventory readback mismatch at week 12.
- main_b05_c1: Physical inventory readback mismatch at week 24.
- main_b01_c0: Physical inventory readback mismatch at week 1.
- main_b01_c0: Physical inventory readback mismatch at week 12.
- main_b01_c0: Physical inventory readback mismatch at week 24.
- main_b02_c1: Physical inventory readback mismatch at week 1.
- main_b02_c1: Physical inventory readback mismatch at week 12.
- main_b02_c1: Physical inventory readback mismatch at week 24.
- main_b00_c1: Physical inventory readback mismatch at week 1.
- main_b00_c1: Physical inventory readback mismatch at week 12.
- main_b00_c1: Physical inventory readback mismatch at week 24.
- main_b04_c0: Physical inventory readback mismatch at week 12.
- main_b04_c0: Physical inventory readback mismatch at week 24.
- main_b08_c0: Physical inventory readback mismatch at week 1.
- main_b08_c0: Physical inventory readback mismatch at week 12.
- main_b08_c0: Physical inventory readback mismatch at week 24.
- main_b00_c0: Physical inventory readback mismatch at week 1.
- main_b00_c0: Physical inventory readback mismatch at week 12.
- main_b00_c0: Physical inventory readback mismatch at week 24.
- main_b08_c1: Physical inventory readback mismatch at week 1.
- main_b08_c1: Physical inventory readback mismatch at week 12.
- main_b08_c1: Physical inventory readback mismatch at week 24.
- main_b03_c1: Physical inventory readback mismatch at week 1.
- main_b03_c1: Physical inventory readback mismatch at week 12.
- main_b03_c1: Physical inventory readback mismatch at week 24.
- main_b03_c0: Physical inventory readback mismatch at week 1.
- main_b03_c0: Physical inventory readback mismatch at week 12.
- main_b03_c0: Physical inventory readback mismatch at week 24.

**claude-haiku-5-5 (main):** response validation.

- Wrong chain count, fields or chain ID types.

The current stage retains these failures. Re-running the same collection cell does not buy another generated response for a failed slot. Any further change to settings, pilot attempts or the all-model gate requires a separate recorded amendment; already accepted pilots remain available for reuse.

## All chain results

| model | block | condition | holding_cost | backlog_cost | total_cost | sensitivity | zero_orders | max_order | final_backlog | final_supply_line |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.6-sol | 9 | strong_pressure | 483.5000 | 1 | 484.5000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 4 | strong_pressure | 550.5000 | 4 | 554.5000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 7 | strong_pressure | 580.0000 | 0 | 580.0000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 6 | strong_pressure | 598.0000 | 0 | 598.0000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 2 | strong_pressure | 449.0000 | 95 | 544.0000 | 0.8333 | 0 | 4 | 6 | 48 |
| gpt-5.6-sol | 4 | no_pressure | 550.5000 | 4 | 554.5000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 1 | strong_pressure | 473.5000 | 14 | 487.5000 | 0.8333 | 0 | 4 | 6 | 48 |
| gpt-5.6-sol | 6 | no_pressure | 598.0000 | 0 | 598.0000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 5 | strong_pressure | 592.5000 | 0 | 592.5000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 3 | strong_pressure | 673.5000 | 0 | 673.5000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 5 | no_pressure | 592.5000 | 0 | 592.5000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 3 | no_pressure | 673.5000 | 0 | 673.5000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 7 | no_pressure | 580.0000 | 0 | 580.0000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 9 | no_pressure | 483.5000 | 1 | 484.5000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 2 | no_pressure | 449.0000 | 95 | 544.0000 | 0.8333 | 0 | 4 | 6 | 48 |
| gpt-5.6-sol | 1 | no_pressure | 473.5000 | 14 | 487.5000 | 0.8333 | 0 | 4 | 6 | 48 |
| gpt-5.6-sol | 8 | no_pressure | 491.0000 | 6 | 497.0000 | 0.8333 | 0 | 4 | 0 | 48 |
| gpt-5.6-sol | 0 | strong_pressure | 458.5000 | 46 | 504.5000 | 0.8333 | 0 | 4 | 12 | 48 |
| gpt-5.6-sol | 0 | no_pressure | 458.5000 | 46 | 504.5000 | 0.8333 | 0 | 4 | 12 | 48 |
| gpt-5.6-sol | 8 | strong_pressure | 491.0000 | 6 | 497.0000 | 0.8333 | 0 | 4 | 0 | 48 |

## Spending and models

First-attempt conservative reservation for the 5 planned calls in this collection stage: **$0.6056**. This assumes every output cap is filled and uses a conservative input byte bound. Actual token usage settles each reservation; an uncertain charge keeps its full reservation. Prices were checked on 20 October 2026. The local ledger is not an account balance.

| model | pilot_calls | main_calls | first_attempt_reservation_ceiling_usd |
| --- | --- | --- | --- |
| gpt-6-luna | 0 | 1 | 0.0208 |
| gpt-5.6-luna | 0 | 1 | 0.0281 |
| gpt-5.6-sol | 0 | 1 | 0.4964 |
| claude-haiku-5-5 | 1 | 1 | 0.0603 |

Returned model IDs: {"gpt-5.6-luna": "gpt-5.6-luna", "gpt-6-luna": "gpt-6-luna", "gpt-5.6-sol": "gpt-5.6-sol", "claude-haiku-5-5": "claude-haiku-5-5"}

## Limits

- Pressure is imagined framing; no binding deadline or token contrast is enforced.
- All four roles and future demand are jointly visible to the trajectory generator.
- Pipeline sensitivity and relative probe weight are proxies, not original structural beta.
- All twenty chains and both conditions share one generation per model; no independent-chain p-values or confidence intervals; human observations=0.
- Seeing both classroom situations in one response permits cross-condition contamination and comparisons by the generator.
- Checkpoint agreement supports three inventory calculations, not every internal decision or state.
- The 24-week primary cost omits liabilities after the horizon; terminal state is reported separately.
- This prospective technical amendment follows an invalid Claude inventory readback; the earlier output cap failure and both raw attempts remain preserved.
- Three successful pilots are reused by exact reference and hash, with their original settings and provenance.
- Claude keeps adaptive thinking and 32,768/65,536 output caps, adds neutral physical bookkeeping, and changes effort from low to medium for both classroom conditions.
- GPT-6 and both GPT-5.6 main payloads are unchanged from the first recovery plan.
- Exactly one further Claude pilot generation and four still-unstarted main generations are scheduled; no semantic retries, replacements or outcome-direction gate.
- All four strict pilot validations remain required before main collection.
- Original logical task/chain IDs remain unchanged; the separate follow-up ID and frozen payloads identify this amendment.
- All previous spending, uncertain charges and any technical retries remain inside the same experiment-wide $5 ledger.
- The fixed request transport is inherited unchanged from recovery v1; no module globals are monkeypatched.
- Provider-specific settings limit causal model comparisons. Imagined pressure and jointly generated chains still do not establish human-time or independent-participant effects.

A directionally null result is a zero or small descriptive contrast in this generated sample; it does not prove no effect. More generated identities within one reply cannot supply independent replication. Testing literal H1/H2 requires a separate enforced-time/computation design and independent collection.

## Files

- [Excel: results and costs](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_followup_aa5649bfb1e797ee/0925467eb163/RESULTS.xlsx)
- [All weekly states and orders](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_followup_aa5649bfb1e797ee/0925467eb163/rounds.csv)
- [Hypotheses and comparisons](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_followup_aa5649bfb1e797ee/0925467eb163/hypotheses.csv)
- [Exact prompts and schemas](../../../prompts/pressure_api_c04ef16c05dd826c)
- [Frozen plan](../../../data/pressure_api_c04ef16c05dd826c/plan.json)
- [Original API records](../../../raw/pressure_api_c04ef16c05dd826c)
- [Protocol](../../../hypotheses/PROTOCOL.md)
