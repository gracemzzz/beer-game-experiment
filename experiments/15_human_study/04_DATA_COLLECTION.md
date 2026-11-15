# 4. What to collect and how to calculate it

**This is a platform specification. The human game interface and final missing-data analysis have not yet been implemented.** The supplied CSVs are empty templates, not participant records.

## One row means one real observation

| File / unit | Minimum fields | Why it is needed |
|---|---|---|
| [participants.csv](data/participants.csv): one person | participant_id, block_id, chain_id, role, pressure, education, assignment_time, study_version, eligibility/experience, completion | Randomization, clustering, sample flow; keep identifying/consent records elsewhere |
| [game_decisions.csv](data/game_decisions.csv): one role-week | IDs, week, pre-stock/backlog, receipts, new demand, shipments, end-stock/backlog, outstanding before/after order, fresh choice, implemented order, source, clock events | Replay physical balances, cost and dynamic coefficients without reconstructing ambiguous timing |
| [stock_task.csv](data/stock_task.csv): one measurement decision | IDs, frame/state/order of presentation, I, P, D, literal order, source, timer events, missing reason | Estimate both stock coefficients and G from independent cue variation |
| [h5_task.csv](data/h5_task.csv): one routine task decision | person, acquisition/transfer, block/trial index, I, PE, PL, D, arrival regime, literal choice, adoption eligibility, randomized time, timer events | Verify rule acquisition, identify changed benchmark, compute R and late-pipeline slope |
| [questionnaires.csv](data/questionnaires.csv): one item response | person, task/time, item_id, response, version | Pressure manipulation, comprehension and experience, without changing primary outcomes |

Store exact rendered screens, scenario/lecture versions, allocation seeds, demand sequences, purchase-order and shipment events in append-only study logs. Keep the raw logs immutable after collection; derive tables into `analysis/`. No names or student numbers belong in analysis exports.

Coding: `pressure` and `education` are 0/1; `role` is 1–4 in retailer-to-factory order; weeks are 1–40 excluding practice. Quantities are nonnegative integer cases; costs are experimental currency, not participant compensation. `first_entry_seconds` and `commit_seconds` are durations since render completion. `order_source` is `fresh_human`, `human_standing` or `missing`; never encode an absent order as 0. Blank numeric fields remain missing. The dedicated `cohort` distinguishes timing/variance pilot, main game and H5. Save new demand separately from outstanding customer backlog, and save own outstanding replenishments separately from either.

## Required clock events

Save state render complete, first valid input, each changed input, explicit submission, local deadline, server receipt and lock time. Use a monotonic client clock for response duration and UTC timestamps for audit. A late network packet is not necessarily late thinking: distinguish local action from server transport. Save both and specify which governs acceptance before the pilot.

RT = committed-choice time − fully-rendered-state time. Also retain time to first entry. A self-report or the elapsed length of the whole session is not a decision-time measure. Do not infer reading time from network latency.

Report on-time valid-choice proportion, unused time, pressure rating and technical failures by arm and role. Record human-selected standing orders separately. A deadline miss is neither a zero order nor a valid probe answer. Technical pauses must follow one prospectively specified rule across groups.

## Stock measurement task

[stock_task_states.csv](materials/stock_task_states.csv) contains all 32 states and analyst-only benchmark orders. It does not contain responses. The participant must not see `benchmark_order`. Shuffle the four factorial cells across the eight frames, with a saved participant-specific seed. IDs and quantities must survive the shuffle unchanged. Show one state at a time, with no paired comparison display or correctness feedback. Keep display complexity identical across arms.

Suggested common wording: “You have the stock shown below. Previously ordered stock and anything you order now will arrive before the one customer demand shown. There is no earlier demand. At the final scoring point, each extra unit costs 0.50 and each unfilled unit costs 1.00. Choose your new order.” Do not tell participants the benchmark equation or desired coefficient. This instrument isolates cue integration; it is not a second full Beer Game.

The reference `estimate_stock_weights` function requires all 32 cells, verifies IDs/values, retains zero orders, and returns κI, κP, G, the descriptive ratio and covariance. It is not a complete human inferential pipeline. Before main collection, add the prespecified missingness and block-level inferential analysis; do not run it only on favorable participants.

## H5 task

[h5_task_states.csv](materials/h5_task_states.csv) contains 32 acquisition and 16 transfer states. Within each eight-state block, randomize presentation order and save the seed. This guarantees a balanced final-eight acquisition check and a balanced first-eight transfer endpoint. Hide all benchmark and `primary_transfer` columns from participants.

During acquisition, explain that both shipments arrive before the one final demand/scoring point and give identical outcome feedback. During transfer, visibly mark one shipment as arriving afterward; retain this marker on every screen. Do not change the demand distribution, cost coefficients, labels or display layout at the same time. All participants receive the new rule, while only response time is randomized.

Save pre-randomization eligibility, score, randomization timestamp and all non-adopter records. A record containing an assignment before the adoption check violates this proposed design. Save each benchmark with the analyst's copy of the state so the persistence calculation is auditable, but never send it to the participant interface.

## Analysis recipe

1. Validate the human roster and allocation; distinguish pilot, main game and H5 cohorts. No ID may occur as both an AI and human observation.
2. Replay each role-week using model equations (1)–(3). Check q source, inventory/backlog conservation, outstanding-order reconciliation, arrival dates and shared demand. Retain failures for investigation instead of silently fixing raw logs.
3. Calculate each complete person's diagnostic slopes and G using (9)–(14). Save all four response cells per frame. Record missing/invalid counts and weak ratio identification.
4. Calculate forty-week chain C, V and BW using (15)–(17). Save component costs and all four role variances. Do not substitute a different window or denominator after seeing results.
5. Compute one H1–H4/H6 contrast per complete block, its standard error and interval using (22)–(25). Apply the prespecified missing-data procedure to randomized incomplete cases and show its sensitivity beside complete-block estimates.
6. In the separate H5 sample, check acquisition before allocation; calculate each eligible randomized person's first-eight-trial mean R. Compare groups, retaining opposite and out-of-range responses. Report secondary late-shipment coefficients and later adaptation.
7. Publish the eight planned raw p-values and Holm-adjusted p-values together, including null/opposite results. If an endpoint is not estimable, show why; do not fabricate a p-value or use another measure as a silent replacement.

## Planned figures

| Figure | What it should show |
|---|---|
| Four-group response estimates | κI and κP with intervals, plus G and the normalized weight when identified |
| H1–H6 summary | Raw-unit contrasts and intervals, with raw/Holm p-values; H5 on its own cohort scale |
| Chain performance | Each chain's C, V and BW, with all four arm means and intervals |
| H5 transfer | Persistence across the two eight-trial blocks, and observed versus correct late-pipeline weights |
| Sample-size precision | Prospective power before collection; final descriptive fixed-prefix estimates afterward, clearly labeled and not used for stopping |

## Handoff and validation

Shared calculator: `scripts/plan_human_study.py`. Numerical checks: `tests/test_human_study_planning.py`. Notebook: `notebooks/POWER_AND_MEASURES.ipynb`. The notebook runs offline and exposes the planning assumptions.

Tests check identification of equal/ignored/partially adjusted cues, missing/duplicate refusal, denominator weakness, stock/backlog conservation, within-role variance, undefined bullwhip denominators, the H5 changing benchmark and t-power sample boundaries. These are software tests, not validation against human responses.

Preserve the closed experiments 1–14. This new study's design choices, templates and calculated scenarios may be revised prospectively, with dates and rationale. Freeze exact materials, timings, analysis, enrollment target and exclusions before main collection; then changes require a recorded amendment.
