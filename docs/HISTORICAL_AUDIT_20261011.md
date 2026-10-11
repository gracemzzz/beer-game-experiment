# Historical Beer Game audit, 11 October 2026

This audit reads and independently replays saved API evidence. It made no new API calls and does not provide results for the new student-persona, high-reasoning protocol. The two completed historical protocols both used `reasoning.effort=none` with a capped visible preparation memo followed by a separate 192-token final-answer call.

## Completion and order behavior

The following counts were derived directly from `rounds.csv`, selecting `phase == "agent"`. Four fixed warmup weeks and twelve automatic continuation weeks are excluded from decision counts and zero rates.

| Historical protocol | Condition | Completed chains | Agent decisions | Zero orders | Zero rate | Smallest order | Largest order | Mean total scored chain cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original nano pilot | Short | 1 | 144 | 81 | 56.25% | 0 | 312 | 28,198 |
| Original nano pilot | Adequate | 1 | 144 | 60 | 41.67% | 0 | 210 | 5,247 |
| Clarified Luna follow-up | Short | 2 | 288 | 0 | 0% | 4 | 12 | 546 |
| Clarified Luna follow-up | Adequate | 2 | 288 | 0 | 0% | 4 | 8 | 156 |

Total scored cost includes all forty game weeks, including fixed warmup, plus twelve automatic continuation weeks. The two short follow-up chain costs are 852 and 240; both adequate chain costs are 156. These are descriptive simulation results. Neither a before/after causal comparison nor a result about University at Buffalo students follows from this table: model, prompt and preparation caps changed together.

Source directories, relative to the project root:

- [Original nano pilot](../data/runs/game_api_8236a9c840b29d36/): returned model `gpt-5.4-nano-2026-03-17`; 96/240 memo-token caps; 2 completed chains, 288 decisions, 584 successful saved requests, no failed requests or replacement groups; saved estimated API charge $0.277483.
- [Clarified Luna follow-up](../data/development/budget_followup_20261005/game_145c7933d7ee/): returned model `gpt-5.6-luna`; 32/240 memo-token caps; 4 completed chains, 576 decisions, 1,168 successful saved requests, no failed requests or replacement groups; saved estimated charge $0.6667273. The historical Luna gateway includes an extra conservative input surcharge in this estimate.

The original pilot's `progress.json` has `decisions: 0`, a stale display field. It is not evidence that the game failed to finish: 288 final responses, their committed orders, and complete game/continuation CSVs independently agree. Its `groups_complete: 2`, `phase: "complete"` and 584 request counter are accurate. The earlier startup-only attempt, `data/runs/game_api_d7df690aed2c8ead`, did stop during rule checks and generated no game choices; it is a different run.

On 11 October 2026 an in-memory replay with the current unchanged physical simulator verified every saved observation field, warmup order, final order and numeric readback for both completed runs:

| Run | Verified decisions | Replayed game states | Replayed continuation states |
| --- | ---: | ---: | ---: |
| Original nano | 288 | 320 | 96 |
| Clarified Luna | 576 | 640 | 192 |

No files in either evidence directory were modified by this audit. Historical [nano audit](../reports/pilot_02_game_api_8236a9c840b29d36/audit.json) and [follow-up audit](../reports/budget_followup_20261005/game_audit.json) provide earlier verification records.

## Evidence about the factory failure

A zero order can be appropriate when stock or outstanding replenishment already covers demand. A more concerning state is `order == 0`, `inventory == 0`, `supply_line == 0`, and `backlog > 0`. The original nano pilot has 13 such decisions: 11 factory decisions and 2 distributor decisions. The clarified follow-up has none.

For example, original short-chain factory week 29 has new demand 312, backlog 276, no inventory, no outstanding production, and order 0. At week 31 the backlog is 588 with another demand of 312; the recorded order is again 0. Its week-31 memo argues that production cannot reduce today's backlog and that ordering zero avoids future holding once demand drops. This is evidence of an economically problematic explanation under the stated future-cost objective. It does not establish the model's private internal reasoning or a single causal explanation for all zero orders.

The original common prompt describes the factory only parenthetically as `factory: produce` and combines its production lag with other roles' upstream ordering and supplier shortages. The follow-up added explicit physical rules:

- New demand and accumulated backlog are different fields; backlog already includes this week's unfilled demand and remains owed in later quiet weeks.
- Factory orders start production directly, without an external supplier or a pre-existing supply line. Production started in week t is received in week t+3.
- Previously placed orders stay outstanding; they are not usable inventory until received.
- A new order changes future costs even though current-week costs and shipments have already occurred.

These clarifications, plus a more capable model chosen in the historical development screen, were associated with the disappearance of the problematic pattern in that small follow-up. The screen itself used deliberately selected failure states, so its results do not demonstrate broad out-of-sample reliability.

Relevant code locations in the legacy implementation:

| File / location | Finding |
| --- | --- |
| `src/beergame_study/prompts.py:8` and `:14` | Brief factory action description and combined lag description. |
| `scripts/budget_model_screen.py:29` | Explicit factory, demand and backlog clarification. |
| `src/beergame_study/game.py:22` | Existing backlog is added to new demand before automatic shipment. |
| `src/beergame_study/game.py:41` | A factory order is appended to the three-week production queue. |
| `src/beergame_study/prompts.py:33` | Order schema permits nonnegative integers and advertises no maximum. |
| `src/beergame_study/runner.py:42` and `scripts/budget_followup_study.py:51` | Orders above 100,000 trigger a computational stop; they are never clipped. |
| `src/beergame_study/api.py:75` and `scripts/budget_model_screen.py:153` | Legacy calls set reasoning effort to `none`. |
| `src/beergame_study/api.py:93` and `scripts/budget_model_screen.py:174` | Legacy gateways reject nonzero reasoning-token usage. |

The completed pilots did not hit an order maximum. The largest actual order was 312, far below the hidden computational safeguard. A previous archived implementation imposed a 40-case entry cap; that cap is absent from the completed protocols audited here. Retaining an advertised small cap in a new design could create an artificial concentration at its boundary.

## Calibration and inference limits

The [follow-up calibration](../data/development/budget_followup_20261005/calibration_a36a6f19041f/calibration_summary.csv) tested 24 hypothetical states at 32, 240 and 480 memo tokens. Short memos truncated in 17/24 states (70.83%); adequate and benchmark memos had no truncation. Mean actual memo output was 31.375, 95.2083 and 150.8333 tokens, respectively. The median absolute adequate-versus-benchmark order difference was 0. These values supported that particular visible-memo intervention; they are unsuitable as caps for a new high-reasoning, total-output-budget protocol.

The follow-up has only 3 usable role beta estimates out of 16 and no chain with four usable role betas. In adequate chains every agent choice equals current incoming demand. Retailer choices are constant, and inventory-adjustment strength is effectively zero for other roles, leaving supply-line weight beta unidentified. Numerical beta values around 1.504 in unusable fits are not measured evidence of over-weighting. The saved H1 result is therefore missing; H2 has a descriptive short-minus-adequate cost difference of 390 but no p-value because only two paired chains were run.

The historical bullwhip table uses all forty game weeks. Demand is a single step followed by a constant level, so amplification depends on the analysis window and the shifted timing of that step upstream. Adequate follow-up local order-to-demand variance ratios equal 1 for every role, while ratios against external customer demand can exceed 1 because transients occur at different weeks. This should not be interpreted as a demonstrated sustained oscillatory bullwhip response. A future design should report demand variance, analysis window, trajectories and missing ratios explicitly, and preserve these historical results separately.

## Practical corrections for the next protocol

Keep the factory/backlog clarifications and the same question format in every condition. Use the requested hypothetical student persona without asking the model to manufacture bias, noise or oscillation. Do not supply a preferred ordering formula or enforce positive orders just to improve the appearance of results. Record exact prompts, requested and returned models, reasoning effort, total output usage, reasoning-token usage, visible output, completion status and failure reasons.

Calibrate the new caps from the new model and prompt, with reasoning effort fixed. Distinguish a valid zero decision from a missing decision. A token-limited call may run out of its allowance before emitting an order: preserve that outcome rather than converting it to order 0 or purchasing more reasoning within the same condition. Report whole-game completion and missing decisions alongside behavior. If a separate continuation policy is needed to complete a diagnostic trajectory, label its orders and costs as fallback/automatic and exclude them from the model-decision effect estimate.

Use identical generous transport timeouts in both conditions and record latency. A shorter network timeout conflates generation with network and server delay; it is not calibrated human thinking time. Any wall-clock intervention should be a separately calibrated condition, with token caps held fixed.

Repeated calls and weekly observations are not independent human students. The chain is the natural experimental unit because role decisions interact. Persona prompting does not validate actual student behavior; comparisons with real students are needed before claims about that population.

## Portable paths and authentication

Saved campaign manifests and `reports/LATEST_REPORT.txt` contain absolute paths from the original macOS machine. Resolve historical data by its project-relative directory name on Windows; do not silently rewrite immutable manifests or treat those old paths as evidence that data is missing. Legacy campaign/report scripts may require path rebasing before reuse.

The current process had no `OPENAI_API_KEY` or `OPENAI_BASE_URL` environment variable on 11 October 2026. No authentication values are printed or stored in this document. Notebook 01's setup at line 338 and notebook 02's at line 102 obtain a key from `OPENAI_API_KEY` or a hidden `getpass` prompt; the SDK client is then created with automatic SDK retries disabled. Reuse that hidden-input pattern or a configured environment variable. Never place a key in a notebook, committed source, CLI arguments, manifest, report, raw request record or chat message.
