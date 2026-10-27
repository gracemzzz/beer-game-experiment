# Experiment 14: externally timed fictional-student Beer Game

1. This is a new, prospective development protocol for one requested model, `gpt-6-astra`, with requested reasoning effort `xhigh`. It contains no collected participants or model decisions. Experiment 13 and all earlier samples remain closed and separate.
2. The planned main sample is ten matched independent blocks, with one four-role chain in each of three fresh condition contexts. A, B and C use the same forty matched persona IDs and profiles across potential-condition sessions: **30 contexts, 30 chain-games, 120 role-condition instances, 2,880 final weekly orders** over 24 weeks. There are ten paired context contrasts per endpoint, not forty independent students.
3. Main collection cannot begin until latency calibration, complete-display checks, comprehension/feasibility checks, deadline enforcement and source/prompt freezing pass. Deadline values are deliberately unset in this document. Development samples never enter the held-out main sample.
4. Null, zero, opposite and failed results are retained. Prompt optimization until significance, outcome-dependent stopping, favorable replacements and fabricated missing choices are prohibited. These materials do not establish behavior of actual University at Buffalo students.

## Conditions and unit of inference

| Arm | Reading | Deadline | Submission opportunities |
|---|---|---|---|
| A | CONTROL.md | Calibrated adequate window | One per game week or probe page |
| B | CONTROL.md | Calibrated restricted window | One per game week or probe page |
| C | EDUCATION.md | The same restricted window as B | One per game week or probe page |

Match external-demand paths and persona-to-role assignments within each block. Start a fresh context for every block/arm; never reveal another arm's decisions or reading. Randomize treatment assignment to launch slots and arm execution order within blocks before collection. Four roles within a context interact and are dependent. Different persona IDs, repeated weeks and hypothetical questions do not create extra independent replications. One model choosing all roles can coordinate them despite the local-information instruction; it is not a group of autonomous human students.

The same requested model and effort apply to every arm and development candidate. Record requested and actually reported identifiers/settings separately. Launcher temperature is unavailable and must be reported as unavailable, not assumed to be zero or another value. An external wall-time deadline does not verify hidden reasoning-token allocation, subjective pressure or cognitive processing time.

## Timing calibration and feasibility gate

Use disjoint development blocks/seeds. Register the finite development attempt list, calibration sample size, candidate deadline-selection rule and technical acceptance thresholds before launching those attempts. Estimate latency from public-display release to receipt of a complete valid submission; preserve monotonic timestamps, wall-clock timestamps, transport intervals, deadline setting and late/invalid events. Select deadline values using latency and task-completion feasibility only, without inspecting hypothesis contrasts or p-values.

Use at most the two supplied wording versions. They differ only in classroom-role framing; information, lectures, physical rules, output constraints and outcome definitions are identical. Selection may consider full-display exposure, literal-choice compliance, completion and post-task knowledge/transfer scores. Do not pick a version because its orders produce the desired direction. If neither passes, retain a failed development status; do not silently add wording versions or start the main sample.

Freeze the selected wording, both readings, assay, calibration rule/results, numeric deadlines, model settings, blocks, seeds, randomization, deadline enforcement and analysis/source fingerprint before main collection. Main collection has a fixed maximum of ten blocks (30 contexts); it is not extended or restarted to obtain significance. Feasibility does not guarantee power.

The controller opens and closes an external submission gate. All arms allow one submission, with no reconsideration pass. A late or invalid submission is preserved and cannot advance the game. No default or repaired order is inserted. Record completion and missingness by arm; failures caused by treatment are outcomes, not administrative cases to replace. Any permitted transport handling must be prospectively specified and must never grant another semantic decision or extend a deadline.

## State and measurement

Use Python for physical accounting only. Initial conditions and physical transitions must be separately frozen with the implementation and replay-checked. The actor receives the current state, allowed history and shared inventories, never future realized demand or private analysis. Score 24 weeks; describe the task as continuing rather than revealing a known terminal optimization target.

Holding cost is 0.5 per remaining case per week; backlog cost is 1 per unfilled case per week. Report their separate components, total chain cost and final inventory/backlog/outstanding commitments. Consequences after week 24 are unmeasured. The external-demand denominator is the final-consumer demand path of that chain, not the endogenous order stream received by an upstream role.

After gameplay, present 32 fixed hypothetical scenarios in eight pages of four. Each page has the arm's deadline and one submission. The bank contains eight pipeline pairs and eight backlog pairs, balanced over the four roles. Neutral IDs and fixed mixed order conceal pair identity. Private pair labels and dimensions must be removed before display. Pipeline pairs vary outstanding quantity with an unchanged timing profile; backlog pairs hold outstanding quantity and timing fixed. Inventory and backlog never coexist positively; the three future-arrival amounts are nonnegative integers summing to outstanding quantity. These are accounting-consistent hypothetical states, not claimed replay states from a complete supplier network.

The hypothetical arrival schedule is known for the assay. This differs from uncertain supplier fulfillment during gameplay and limits ecological generalization. All zero and extreme admissible responses remain in the record. No scenario has a required order or normative answer.

| Endpoint | Definition and units | Contrast and predicted sign |
|---|---|---|
| H1 proxy | Mean of eight pair slopes `(q_lowP - q_highP)/(P_high - P_low)`; cases ordered per additional outstanding case | B minus A, negative |
| H2 | Sum of holding and backlog costs across four roles and 24 weeks; game cost units per chain | B minus A, positive |
| H3 proxy | The same pipeline-response slope | C minus B, positive |
| H4a | Sample weekly order variance for each role (denominator 23), then arithmetic mean over four roles; cases squared | C minus B, negative |
| H4b | Each role's sample order variance divided by that chain's sample external-demand variance, then arithmetic mean over roles; dimensionless | C minus B, negative |

For each arm/block, aggregate the eight pipeline-pair slopes with equal pair weight. Do not infer a normative weight of one: the assay measures responsiveness, and the literal underweighting interpretation remains unverified. Report the eight backlog-response slopes `(q_highB - q_lowB)/(B_high - B_low)` separately as a general-responsiveness comparison/negative-control diagnostic, not as an assumption that education cannot affect backlog response.

Report pair-level slopes, role-level summaries, zero-choice fractions, all observed order ranges/extremes, and timing-profile variation. Supplementary pair-fixed-effect regressions use the manipulated quantity and pair intercepts; retain residuals and pairwise slopes to show heterogeneous responses. Two levels within each pair cannot identify curvature; differences across regimes are descriptive evidence of nonuniform responsiveness, not a formal nonlinear dose-response test. Do not select the regression specification after viewing effects.

H4a and H4b share order variance and are not independent replications. A zero demand-variance denominator is undefined. An incomplete 24-week trajectory has no complete-horizon H2/H4 estimate; retain partial costs and completion status separately. A missing member of a probe pair prevents that pair's slope; a missing required pair makes the predeclared aggregate endpoint unavailable rather than silently changing weights. Probe eligibility and completion must be reported separately from game completion.

## Comprehension and transfer

Present the four fixed questions only after all behavioral decisions, without time pressure and without answer feedback before completion. Display only question ID, question text and choices. Correct answers and reasons are private scoring metadata. Report total and per-item scores; do not exclude a main case for failing comprehension or failing to show the desired treatment response. Their scores are manipulation checks, not evidence of real student learning or causal mediation.

## Inference, provenance and preservation

Use matched block contrasts and report each block before aggregate estimates. With randomized assignment, use the corresponding paired randomization distribution; otherwise state the independent symmetric/exchangeable paired-null assumption of a sign-flip test. Use two-sided tests and Holm adjustment across the five endpoints for this single model. Interpret a significant opposite effect as opposite evidence. Report pointwise uncertainty with its small-sample limitation. With ten nonzero independent pairs the smallest possible two-sided sign-flip p-value is 2/1024; this does not promise detection.

Complete-case contrasts condition on successful completion. When deadlines change completion, those contrasts can be selected and do not automatically identify an effect in all assigned contexts. Report failure rates and the missing-endpoint pattern alongside effects; do not present a complete-case contrast as an unrestricted causal estimate.

Retain the fixed ten-block attempt order, all raw displays/responses, timestamps, requested/reported settings, deadline violations, tool transcripts, hashes, replay receipts and inclusion/missingness reasons. Review procedure independently of treatment-effect direction. No student-level p-values, repeated-week pseudo-replication, favorable subgroup selection or significance-driven sample-size sweeps are permitted.

The fixtures contain researcher-authored hypothetical states and scoring keys, not synthetic participant decisions. Software-only validation must be labeled synthetic. This preparation makes no model calls, paid API calls or ledger changes. Any later paid work remains subject to the existing shared cumulative cap and cannot reset its ledger. Preserve earlier protocols and publications byte-for-byte.

Research basis and limits: [REFERENCES.md](REFERENCES.md). Display/privacy contract: [prompts/README.md](../prompts/README.md).

