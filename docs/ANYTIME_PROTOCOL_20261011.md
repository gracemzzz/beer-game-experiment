# Revised experiment: student personalities and additional deliberation

Design date: 11 October 2026. This is a new protocol, `student-high-anytime-revision-v2`, following the user's request to repair the experiment. The original single-call pilot remains preserved and cannot be pooled with this study. See the [literature review](../reports/revised_design_20261011/REPORT.md).

## Participants and assignment

Four separate files in `config/student_profiles/` specify fictional second-year UB business students. They cross methodical versus flexible working style with emotionally steady versus uncertainty-sensitive framing. They share introductory business knowledge and no Beer Game experience. The descriptions contain no target orders, supply-line weights, risk coefficients, instructions to make mistakes, or desired hypothesis outcome. These are deliberately chosen experimental profiles, not estimated personality scores or a measured UB population mixture.

Each chain contains all four profiles. Within every independent pair, both token conditions use the same profile in the same role. Over a quartet of pairs, a randomized Latin-square rotation gives each profile each role once. A one-pair pilot contains all profiles but cannot estimate personality effects separately from role. Role/persona breakdowns are descriptive until a separately planned adequately replicated interaction analysis. No model-generated personality questionnaire or self-description counts as human validation.

## Treatment

The model is pinned to `gpt-5.4-mini-2026-03-17`, with `reasoning.effort=high` on every call. Temperature and top-p are omitted identically in every condition; no sampling parameter is tuned to produce variance. The common transport timeout is 180 seconds, not a cognitive deadline.

Every decision begins with one structured, current-state initial submission, capped at 16,384 generated tokens. Short ends there. Adequate receives one further high-effort call, capped at 8,192, seeing the same information and its submitted choice. It can keep or revise the choice. Thus maximum per-decision generation is 16,384 versus 24,576, and actual use across both phases is the manipulation measure. This is **access to extra deliberation**, not a pure single-call cap, a validated human-seconds conversion, or a separately randomized information-load treatment. A new call also refreshes context and can affect framing; those features are part of this operationalization.

Only valid model submissions for the CURRENT state are scored. A token-exhausted revision leaves that initial submission in force under the participant instructions. That differs from mechanically copying last week's order. An absent initial choice, refusal, malformed answer, model mismatch, or transport error stops the experiment with a partial report. No correctness retry, clipping, positive-order requirement, or significance-driven parameter adjustment is allowed.

## State and dynamics

The physical simulator is unchanged: four serial roles, initial stock 12, initial flow 4, one-week order transmission plus two-week physical shipping, and three-week factory production. Backlogs persist. Inventory information is shared; other positions' orders/backlogs stay hidden. Own outstanding inventory is displayed as separate deliveries due and quantities awaiting dispatch, without a supplied aggregate. These components are derived from physical queues, not invented summaries.

After four fixed practice weeks, customer demand is drawn independently from the discrete uniform distribution on integers 0–8. All positions are told the distribution; only the retailer observes the current external demand directly. Paths are drawn and saved before model outcomes and matched within each pair. No rejection sampling selects attractive paths. The default horizon is 32 total decision-period weeks; a prespecified budget pilot can use 24, and a larger study can use 40 or more. Never shorten a game after seeing its orders. Primary bullwhip is measured only over model-controlled weeks, excluding practice and automatic scoring.

Twelve automatic scoring weeks follow: customer demand stays at its final value and each position repeats its own final submitted quantity. This removes the old demand-following strategy example. It remains an artificial terminal policy that can influence decisions and is disclosed identically to all participants. It differs from the historical scoring rule. The cost report includes all periods and also separates decision-period cost.

These are adaptations, not a literal replication of Croson–Donohue or Sterman: physical lags, training, horizons, fictional profiles, LLM incentives, and terminal scoring differ. Real participants can receive monetary incentives; telling an LLM about game costs does not reproduce human utility.

## Calibration, outcomes, and inference

Calibration has eight development and eight held-out, physically replayed states covering early/middle/late histories and all profiles. One initial and one revision are purchased per state. Caps are fixed in advance, not searched using orders or outcomes. Both splits require all initial choices valid, at least 7/8 valid revisions, recorded positive reasoning in both phases, median initial/total generated tokens at most 0.75, and all initial responses below 90% of the generous initial ceiling. This small feasibility screen is not a whole-game reliability guarantee. A failed live screen stops before any games; there is no automatic diagnostic-game override. Compatible saved calibration is reusable without new purchases.

- **H3, primary:** short produces a higher chain-average order/customer-demand variance ratio over model decision weeks. Local demand ratios and trajectories are also reported. A zero denominator remains missing.
- **H2:** short produces greater full scored chain holding/backlog cost. Its calculation does not depend on beta identification.
- **H1 sensitivity, mechanism assay:** short exhibits lower negative order response per additional pipeline case. Each block has matched one-shot scenarios differing by 24 pipeline cases, holding the other displayed quantities constant, for each role/profile. This is direct response sensitivity, **not the original dynamic beta coefficient**. Probe calls do not enter game history.

The original nonlinear beta fit remains an explicitly exploratory table with all original identification diagnostics. Never report a numerical but unidentified beta as a finding.

Inference uses independent paired chain blocks. Paired t tests and 95% intervals assume independent, suitably distributed differences; Holm adjustment covers the fixed family of three. Inference is withheld below eight complete pairs or when calibration/main-game computation separation fails. Eight is a software reporting floor, not a power calculation. `planned_pairs()` supplies a prospective noncentral-t calculation given a scientifically justified standardized paired effect; illustrative effects do not establish a sample-size recommendation. Future personality interactions require their own prospective plan and multiplicity handling.

## Cost and reproducibility

Identical full initial prompts within one block/week/role share one model draw across conditions (common random draws). If state, personality, or any history differs, separate initial calls are used. Independent blocks always receive new draws. This can save one of three calls per paired decision compared with separately purchasing both initial choices; it is not a promise of savings relative to the old invalid protocol.

Completed exact requests are checkpointed. There is no model call for reports, plots, deterministic policies, or software tests. Stable prompt prefixes permit automatic provider input caching; actual cached tokens are recorded. Reasoning/output costs still dominate many calls. The original $10 campaign includes $5.19360675 already spent and all subsequent v2 requests. Reservations count uncertain transport outcomes, and a campaign lock prevents simultaneous live workers. No paid run begins on opening the notebook.

All human-readable outputs go under `reports/<run_id>/`; raw records, exact messages/replies/model/effort/usage, source snapshots, profile snapshots and paths remain in `data/runs/<run_id>/`. Scientific changes create a new fingerprint. Historical results remain separate.
