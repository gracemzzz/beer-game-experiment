> **Subsequent transport update:** the next real run produced 307 valid responses and zero comprehension failures before HTTP 429 errors. Rate-limit recovery and pacing are now implemented; see [RATE_LIMIT_RECOVERY.md](RATE_LIMIT_RECOVERY.md). This supersedes the transport-handling and concurrency entries below.

# Conclusions

1. **There were real model errors and a preventable prompt-layout weakness.** The old payload sorted keys alphabetically, placing the current task before the past history. Two week-3 replies copied earlier supply-line values (4 and 8) when the current supply line was 0. That is consistent with confusion between past and current state; the records do not prove its cause.
2. **The prompt is now clearer, but live reliability is not yet established.** Local tests validate code, formatting, accounting, and failure handling. They cannot demonstrate that GPT follows the revised prompt.
3. **Minimal reasoning is a speed/accuracy tradeoff.** Do not assume retries make it scientifically equivalent to a reliable first response. New reports show first-attempt correctness separately for each condition.
4. **Completed games are not necessarily valid H1/H2 measurements.** Beta may remain unidentified. Rules checks and copied observations do not prove strategic understanding. Replacement selects successful responders; confirmatory p-values remain withheld after replacement.

## Changes made

- Present full local history first and current state last; explicitly identify task.current_state as authoritative. All original historical information remains available.
- Ask for current observations before the chosen order; give each field an exact source description. Zero is explicitly a real value, not missing data. Readback values remain unconstrained integers checked against the simulator; the schema does not force the right answer.
- Match each rules question to its output key. Clarify per-unit versus total holding cost and weekly backlog cost.
- State the same 0–1,000,000 order bounds enforced by the schema. There is no preferred ordering strategy or enforced positive order.
- Apply identical formatting and operational instructions to all conditions. The training lesson remains the only treatment-specific prompt difference.
- Add first_attempt_reliability.csv alongside retry counts and group replacement records.

## Settings reviewed

| Setting | Current choice | Implication |
|---|---|---|
| Model | GPT-5 nano snapshot | Access already worked; cognitive reliability remains a separate question. |
| Effort | minimal versus low | Faster revised H2_API comparison, not human time pressure. |
| Response ceiling | 8,192 tokens for both | Includes reasoning and output; not a target. Hitting it still stops the run. |
| Timeout | 300 seconds for both | Infrastructure limit, not thinking-time manipulation. |
| Concurrency | 8 requests total | Groups and roles may overlap, but a group advances only after four valid orders. |
| Correctness retries | 3 attempts total | Same state/model/effort; every attempt saved and charged. No retry based on order size or desired result. |
| Group replacements | At most 3 per target group | Entire four-role group restarts; partial failures stay audited. No replacement for unusable beta. |
| Spending allowance | $0.75 | Includes failed calls and unknown-usage reservations; can stop before the completion target. |
| Other API failures | Stop and preserve | No blind retries for authentication, quota, refusal or output exhaustion. Transient network recovery is not implemented in this revision. |

## Remaining limits

- Neither reducing reasoning nor rewording a prompt guarantees valid answers, a measurable beta, realistic human behavior, or significant effects.
- Initial inventory and pipeline can rationally lead to zero orders. Zero orders alone are not an error and must not trigger a retry.
- A rules check is a separate call. Its answer is not inserted into the game agent's memory; every game decision receives the rules and its local history again.
- A large number of replacements can exhaust the budget and distort the completed sample. Inspect all attempts rather than just successful games.
- Earlier API trials are preserved. This protocol change creates a new run; do not pool it with previous protocols as one unchanged experiment.

Official reference: [Structured Outputs: handling mistakes](https://developers.openai.com/api/docs/guides/structured-outputs). Correct JSON structure does not guarantee correct values.

## Local validation

16 offline/mocked tests passed, including conflicting old history versus a zero current supply line, negative net inventory, rejection of incorrect readbacks, per-condition prompt isolation, group replacement limits, resume behavior, retry accounting, simulator conservation, and beta recovery. No live API requests were sent during this audit.
