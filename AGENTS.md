# Project maintenance instructions

The active implementation is the under-$3, four-personality, fixed-high GPT-6 Luna Flex initial-choice-plus-revision protocol v3 in docs/ECONOMY_PROTOCOL_20261011.md and notebook 04. Preserve v2 Mini scientific files and evidence separately. The earlier single-call student protocol, notebooks, results, and docs/PROTOCOL.md are historical and must remain interpretable. The new design tests extra deliberation; it does not claim a pure single-call cap or validated human time pressure.

- Read README.md and the dated research/audit notes before changing the experiment.
- For every change, update README.md with what changed, why, run instructions, checks, and material limitations. Keep a dated change entry so another agent can continue.
- Publish human-readable reports under `reports/`, following its README and existing named-folder layout. Keep raw evidence under `data/`. Update latest-report pointers and notebook links; archive superseded reports under `reports/archive/` and operational logs under `reports/logs/`.
- Preserve exact prompt/model/config/source provenance. Scientific changes create a new run fingerprint. Do not overwrite completed raw evidence or combine incompatible protocols.
- Use offline and mocked calls for software tests. Paid experiments need user authorization and an explicit hard dollar cap; the new 11 October 2026 campaign is authorized up to $10.
- The later user instruction tightens the redesign allowance to less than $3: count the $0.7198179 Mini calibration already spent, cap the current Luna Flex run at $2.20 and its fresh calibration at $0.18, and enforce a $2.95 shared v2/v3 guard. The historical $5.19360675 remains included in the original $10 campaign. Do not reset campaign IDs to obtain more spending authority.
- Keep secrets in masked interactive prompts or environment variables, never in chat, source, notebook output, logs, reports, or command arguments.
- Keep reasoning effort high and model constant across token conditions. Document any future change as a new protocol.
- Do not force positive/interior orders, introduce a preferred maximum, invent cognitive biases, retune for significance, or label fallback orders as LLM decisions.
- Distinguish model simulations from actual human observations. Weekly calls are not independent students. Synthetic checks do not validate the persona or computational intervention.
- After changes, run appropriate tests and produce reproducible reports, including partial reports if an API run stops.
