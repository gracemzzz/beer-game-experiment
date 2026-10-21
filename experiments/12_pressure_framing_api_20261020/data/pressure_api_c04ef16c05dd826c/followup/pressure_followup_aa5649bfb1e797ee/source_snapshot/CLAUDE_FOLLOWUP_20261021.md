# Claude arithmetic follow-up — 21 October 2026

1. **Three model pilots now pass:** GPT-6 Luna, GPT-5.6 Luna and GPT-5.6 Sol. Their accepted responses will be reused unchanged.
2. **Claude now finishes JSON but fails physical inventory checks.** It used 3,519 of 32,768 output tokens and stopped normally. Increasing the output cap alone would not address the observed error.
3. **No main experiment data exist yet.** All four main cohorts remain blocked by the all-model pilot gate. Pilot contrasts are not H1/H2 evidence.
4. **One further Claude pilot is specified here before collecting it.** It uses medium adaptive effort and an explicit neutral queue-accounting appendix. No order preferences, target effects or corrected answers from the failed attempt are supplied.
5. **The $5 cumulative cap is unchanged.** The six original/recovery requests total $0.07590755 in local charge estimates. Future calls and technical retries use the same ledger.

## Observed failure

The earlier recovery is `pressure_recovery_94cd561f22269535` under the original run `pressure_api_c04ef16c05dd826c`. Its Claude response passed schema and factual questions but failed four inventory readbacks. Both week-one readbacks were correct. Independent event-ledger calculations agree with the Python game engine:

| Condition | Week | Claude's inventory | Replayed inventory |
| --- | ---: | --- | --- |
| Strong pressure | 12 | `[6,9,11,13]` | `[30,14,12,10]` |
| Strong pressure | 24 | `[5,8,10,12]` | `[35,13,10,8]` |
| No pressure | 12 | `[7,8,11,12]` | `[31,12,13,10]` |
| No pressure | 24 | `[4,9,9,11]` | `[37,9,12,8]` |

These recalculations diagnose the failure. They do not replace any submitted values and are not included in the next model prompt. The failed response remains invalid. Its normal `end_turn` termination and 2,261 reasoning tokens distinguish this from the first Claude attempt, which exhausted 8,192 tokens before producing an answer.

## Fixed follow-up collection

The original four-model objective remains the default. This amendment authorizes one bounded generation slot for the remaining Claude technical pilot, followed by the four originally planned main slots if every pilot passes. Re-running this stage reuses the same saved slot identities; it cannot create more generations or select among repeated answers. A failure remains visible. No follow-up calls have been made at preparation.

- Reuse the original GPT-5.6 Luna and Sol pilots and the accepted GPT-6 recovery pilot, with exact response hashes and original model/settings metadata.
- Claude uses `thinking.type=adaptive`, `output_config.effort=medium`, 32,768 pilot output tokens and 65,536 main output tokens. Append the same neutral physical-stock, backlog and delivery-queue bookkeeping used in the successful GPT-6 recovery.
- GPT-6 and both GPT-5.6 main requests retain their prior frozen settings and messages. The two pressure conditions within every model share the same API settings.
- The state-accounting instruction specifies no ordering strategy and discloses no failed trajectory, expected checkpoint values, H1/H2 direction, desired variation or significance requirement.
- The original strict JSON, factual-rule and physical-checkpoint validation applies unchanged. Main replies must contain all 20 chains, four roles and 24 weeks. No generated choices are repaired, clipped or fabricated.
- Each scheduled generation allows at most one identical-payload retry for transient transport/rate/server errors; invalid generated content never triggers an automatic retry. Both attempts count against the shared budget.
- All original plans, source snapshots, prompts, successes, failures, usage records and charge rows remain unchanged. The new stage has its own immutable manifest, request payloads, status and responses.

This is a post-pilot technical amendment, not a prospectively untouched comparison. Model-specific settings and prompt changes limit comparisons of model identity alone. All main outcomes remain descriptive, with no independent-chain p-values or inferential confidence intervals. No binding student time or compute restriction is established by the fictional classroom framing.

## If this also fails

This stage stops at its fixed failed slot. Another automatic generation, a reduced acceptance standard or overwriting a failed checkpoint is not permitted. A further design decision would be needed: report Claude's technical failure while collecting the other models under an explicit gate amendment, or develop a separate experiment where Python supplies each week's state. Neither alternative is silently substituted here.
