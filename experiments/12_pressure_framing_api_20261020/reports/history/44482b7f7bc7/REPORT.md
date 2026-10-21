# Experiment 12: conclusions first

1. **Collection:** 0/4 main responses and 2/4 pilot responses accepted.
2. **H1/H2 findings:** No main API results have been collected. Software checks do not provide hypothesis evidence.
3. **Interpretation:** This tests imagined pressure framing. It does not establish a binding deadline, original structural β, or effects on real students.
4. **Statistical independence:** All 20 chains and both conditions share one main response per model. No p-values or inferential confidence intervals are reported.
5. **Budget:** $0.0717 charged or conservatively reserved out of the authorized $5 total across this experiment, including pilot and retries.
6. **Recovery:** Two previously accepted GPT-5.6 pilots are reused. The original GPT-6 inventory failure and Claude token-limit failure remain preserved; recovery changes are recorded separately.

## Design

Each model represents 80 fictional students in 20 four-role chains: 10 no-pressure and 10 strong-pressure chains. Each chain submits all 24 weeks at once. H2 includes only those 24 weeks; there are no automatic continuation costs. Matched chains share demand paths and profile assignments. Four disjoint two-chain pilot responses are outside the main sample.

Recovery settings: GPT-6 Luna uses medium effort with 16,384 pilot / 32,768 main output tokens and an explicit accounting algorithm. Claude Haiku keeps adaptive thinking at low effort with 32,768 pilot / 65,536 main output tokens and a concise-completion reminder. Both GPT-5.6 models retain low effort and their original settings. Settings are identical across pressure conditions within each model, but differ across models; model comparisons therefore include settings differences. These are completion allowances, not the experimental pressure manipulation. Provider effort labels are not equivalent measurements of computation.

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
| gpt-6-luna | 0 | 0 | 0 | False |
| gpt-5.6-luna | 1 | 0 | 0 | False |
| gpt-5.6-sol | 1 | 0 | 0 | False |
| claude-haiku-5-5 | 0 | 0 | 0 | False |

Acceptance requires all chain IDs, 24 order rows, probes, factual rules and inventory readbacks at weeks 1, 12 and 24. All four pilot slots must pass before main collection, including the two inherited accepted pilots. The user-authorized recovery provides one revised generation for each of the two failed pilots. Original failures are retained. Further semantic retries, replacements, clipping and filled-in orders are not used. At most one retry is allowed for a transient transport/rate/server error, with its cost reserved.

## Preserved pilot diagnosis

- GPT-6 Luna returned complete choices, but its week-12 and week-24 inventory readbacks disagreed with independent game replay. It was not an API connection or balance failure.
- Claude Haiku returned HTTP 200 with `stop_reason=max_tokens`: all 8,192 output tokens were reasoning tokens and there was no answer text. This was truncation, not a refusal.
- Original recorded charge estimate: $0.0716918. All old charges remain in the shared $5 ledger. The recovery has two pilot calls and four main calls before possible transient retries.
- Software verification cannot guarantee the next model-generated trajectories pass. A new failure remains visible and does not become a fabricated participant.

[Recovery amendment](../../../hypotheses/RECOVERY_20261021.md) · [Frozen recovery inputs and status](../../../data/pressure_api_c04ef16c05dd826c/recovery/pressure_recovery_94cd561f22269535)

## Spending and models

First-attempt conservative reservation for the 6 planned calls in this collection stage: **$0.6157**. This assumes every output cap is filled and uses a conservative input byte bound. Actual token usage settles each reservation; an uncertain charge keeps its full reservation. Prices were checked on 20 October 2026. The local ledger is not an account balance.

| model | pilot_calls | main_calls | first_attempt_reservation_ceiling_usd |
| --- | --- | --- | --- |
| gpt-6-luna | 1 | 1 | 0.0315 |
| gpt-5.6-luna | 0 | 1 | 0.0281 |
| gpt-5.6-sol | 0 | 1 | 0.4964 |
| claude-haiku-5-5 | 1 | 1 | 0.0597 |

Returned model IDs: {"gpt-5.6-luna": "gpt-5.6-luna", "gpt-5.6-sol": "gpt-5.6-sol"}

## Limits

- Pressure is imagined framing; no binding deadline or token contrast is enforced.
- All four roles and future demand are jointly visible to the trajectory generator.
- Pipeline sensitivity and relative probe weight are proxies, not original structural beta.
- All twenty chains and both conditions share one generation per model; no independent-chain p-values or confidence intervals; human observations=0.
- Seeing both classroom situations in one response permits cross-condition contamination and comparisons by the generator.
- Checkpoint agreement supports three inventory calculations, not every internal decision or state.
- The 24-week primary cost omits liabilities after the horizon; terminal state is reported separately.
- User requested a bounded technical fix after the first pilots; this is a post-pilot amendment.
- Original task, chain and response IDs remain literal parent IDs; this amendment ID identifies changed prompts/settings separately.
- Two successful original pilots are inherited by exact hash, not regenerated.
- No original failure is deleted, repaired, relabelled accepted, or substituted with fabricated orders.
- Only two failed pilot generations are reattempted once; no semantic retry loop or outcome-based replacement.
- All four strict pilot checks must pass before any of the four main generations.
- GPT-6 Luna receives neutral physical bookkeeping and medium effort; Claude keeps adaptive low effort with a larger completion allowance.
- Provider-specific recovery settings limit model-only causal comparisons; both pressure conditions within each model use the same revised request.
- Original failures and recovery costs remain inside the same cumulative $5 ledger.

A directionally null result is a zero or small descriptive contrast in this generated sample; it does not prove no effect. More generated identities within one reply cannot supply independent replication. Testing literal H1/H2 requires a separate enforced-time/computation design and independent collection.

## Files

- [Excel: results and costs](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_recovery_94cd561f22269535/44482b7f7bc7/RESULTS.xlsx)
- [All weekly states and orders](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_recovery_94cd561f22269535/44482b7f7bc7/rounds.csv)
- [Hypotheses and comparisons](../../../analysis/pressure_api_c04ef16c05dd826c__pressure_recovery_94cd561f22269535/44482b7f7bc7/hypotheses.csv)
- [Exact prompts and schemas](../../../prompts/pressure_api_c04ef16c05dd826c)
- [Frozen plan](../../../data/pressure_api_c04ef16c05dd826c/plan.json)
- [Original API records](../../../raw/pressure_api_c04ef16c05dd826c)
- [Protocol](../../../hypotheses/PROTOCOL.md)
