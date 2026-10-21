# Experiment 12: conclusions first

1. **Collection:** 0/4 main responses and 3/4 pilot responses accepted.
2. **H1/H2 findings:** No main API results have been collected. Software checks do not provide hypothesis evidence.
3. **Interpretation:** This tests imagined pressure framing. It does not establish a binding deadline, original structural β, or effects on real students.
4. **Statistical independence:** All 20 chains and both conditions share one main response per model. No p-values or inferential confidence intervals are reported.
5. **Budget:** $0.0759 charged or conservatively reserved out of the authorized $5 total across this experiment, including pilot and retries.
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
| gpt-5.6-sol | H1 | 0 | — | unavailable |
| gpt-5.6-sol | H2 | 0 | — | unavailable |
| claude-haiku-5-5 | H1 | 0 | — | unavailable |
| claude-haiku-5-5 | H2 | 0 | — | unavailable |

**H1:** mean reduction in order divided by a 24-case increase in outstanding dispatched replenishment, over eight matched probes per chain. A smaller sensitivity under strong pressure is consistent with the predicted proxy direction. This does not identify an optimal benchmark or the original structural coefficient.

**H2:** cumulative chain holding cost ($0.50 per case-week) plus backlog cost ($1 per case-week). A positive strong-minus-no-pressure difference follows the prediction. There is no revenue or factory production fee.

## Completion and technical checks

| model | accepted_pilot_responses | accepted_main_responses | accepted_main | complete |
| --- | --- | --- | --- | --- |
| gpt-6-luna | 1 | 0 | 0 | False |
| gpt-5.6-luna | 1 | 0 | 0 | False |
| gpt-5.6-sol | 1 | 0 | 0 | False |
| claude-haiku-5-5 | 0 | 0 | 0 | False |

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

## Spending and models

First-attempt conservative reservation for the 5 planned calls in this collection stage: **$0.6056**. This assumes every output cap is filled and uses a conservative input byte bound. Actual token usage settles each reservation; an uncertain charge keeps its full reservation. Prices were checked on 20 October 2026. The local ledger is not an account balance.

| model | pilot_calls | main_calls | first_attempt_reservation_ceiling_usd |
| --- | --- | --- | --- |
| gpt-6-luna | 0 | 1 | 0.0208 |
| gpt-5.6-luna | 0 | 1 | 0.0281 |
| gpt-5.6-sol | 0 | 1 | 0.4964 |
| claude-haiku-5-5 | 1 | 1 | 0.0603 |

Returned model IDs: {"gpt-6-luna": "gpt-6-luna", "gpt-5.6-luna": "gpt-5.6-luna", "gpt-5.6-sol": "gpt-5.6-sol"}

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

- [Excel: results and costs](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_followup_aa5649bfb1e797ee/6dfb729f1751/RESULTS.xlsx)
- [All weekly states and orders](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_followup_aa5649bfb1e797ee/6dfb729f1751/rounds.csv)
- [Hypotheses and comparisons](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_followup_aa5649bfb1e797ee/6dfb729f1751/hypotheses.csv)
- [Exact prompts and schemas](../../../prompts/pressure_api_c04ef16c05dd826c)
- [Frozen plan](../../../data/pressure_api_c04ef16c05dd826c/plan.json)
- [Original API records](../../../raw/pressure_api_c04ef16c05dd826c)
- [Protocol](../../../hypotheses/PROTOCOL.md)
