# Project maintenance instructions

The active study is the hypothetical-student, fixed-high, single-call protocol described in README.md. Historical implementations, notebooks, results, and docs/PROTOCOL.md describe different protocols and must remain interpretable.

- Read README.md and the dated research/audit notes before changing the experiment.
- For every change, update README.md with what changed, why, run instructions, checks, and material limitations. Keep a dated change entry so another agent can continue.
- Preserve exact prompt/model/config/source provenance. Scientific changes create a new run fingerprint. Do not overwrite completed raw evidence or combine incompatible protocols.
- Use offline and mocked calls for software tests. Paid experiments need user authorization and an explicit hard dollar cap; the new 11 October 2026 campaign is authorized up to $10.
- Keep secrets in masked interactive prompts or environment variables, never in chat, source, notebook output, logs, reports, or command arguments.
- Keep reasoning effort high and model constant across token conditions. Document any future change as a new protocol.
- Do not force positive/interior orders, introduce a preferred maximum, invent cognitive biases, retune for significance, or label fallback orders as LLM decisions.
- Distinguish model simulations from actual human observations. Weekly calls are not independent students. Synthetic checks do not validate the persona or computational intervention.
- After changes, run appropriate tests and produce reproducible reports, including partial reports if an API run stops.
