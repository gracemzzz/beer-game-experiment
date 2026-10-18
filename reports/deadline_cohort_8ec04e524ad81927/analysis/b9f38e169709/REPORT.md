# Deadline-framed Beer Game study

Status: **complete**; 4/4 responses accepted.

**16 fictional identities**, 4 chains, 2 repeated generations per deadline. Repeats reuse the same identities, profiles and demand paths. Model label: **current-assistant-inherited / inherited**; collection: isolated_assistant. Backend equivalence to other studies is unverified.

The manipulation is a fictional 10-second versus 180-second student deadline. No actual per-decision model token budget, runtime or experienced pressure is measured. Conditions are generated independently without earlier answers. Whole trajectories still expose the generator to future demand and all roles; decentralized information use is not verified. No human observations, independent-student tests or inferential p-values are reported.

## H1 / H2 / H3

| hypothesis | metric | brief | ample | brief_minus_ample | defined_chain_generation_pairs | direction |
| --- | --- | --- | --- | --- | --- | --- |
| H1 | sensitivity | 0.666667 | 0.916667 | -0.25 | 8 | predicted direction |
| H2 | cost | 1123.06 | 1043.12 | 79.9375 | 8 | predicted direction |
| H3 | bullwhip | 1.07326 | 0.876485 | 0.196776 | 8 | predicted direction |

H1 = (probe order with 8 dispatched cases minus order with 32) / 24, averaged across roles. It is not the original structural beta. H2 = full chain cost, including four practice and twelve automatic continuation weeks. H3 = mean of four role order/customer-demand sample-variance ratios during model weeks. Zero demand variance makes the ratio undefined. Contrasts use only matched chain/generation pairs; a predicted direction describes these outputs and does not confirm a human-time hypothesis.

## How many orders changed?

| kind | batch_id | generation | condition | choices | changed | changed_fraction | mean_absolute_change |
| --- | --- | --- | --- | --- | --- | --- | --- |
| between_deadlines | b0001 | 1 | brief minus ample | 320 | 166 | 0.51875 | 0.8 |
| between_deadlines | b0001 | 2 | brief minus ample | 320 | 147 | 0.459375 | 0.59375 |
| repeat_same_deadline | b0001 | 1-2 | ample | 320 | 163 | 0.509375 | 0.709375 |
| repeat_same_deadline | b0001 | 1-2 | brief | 320 | 137 | 0.428125 | 0.578125 |

Within-condition repeat changes are shown alongside deadline changes. Different orders alone do not prove a pressure mechanism. Repeat generations and rows within a response are dependent generated data, not new students.

## Data quality

| condition | generation | orders | zeros | zero_fraction | largest_order | distinct_role_paths | role_paths |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ample | 1 | 320 | 30 | 0.09375 | 9 | 16 | 16 |
| ample | 2 | 320 | 46 | 0.14375 | 14 | 16 | 16 |
| brief | 1 | 320 | 40 | 0.125 | 17 | 16 | 16 |
| brief | 2 | 320 | 35 | 0.109375 | 13 | 16 | 16 |

No missing decisions are filled in, no order is clipped and no valid zero is removed. Automatic continuation holds each role at its own final submitted order and demand at its final value; these are scoring-rule actions, not new model decisions.

## Provenance and completion

| task_id | batch_id | generation | condition | students | accepted |
| --- | --- | --- | --- | --- | --- |
| b0001_g01_brief | b0001 | 1 | brief | 16 | True |
| b0001_g01_ample | b0001 | 1 | ample | 16 | True |
| b0001_g02_ample | b0001 | 2 | ample | 16 | True |
| b0001_g02_brief | b0001 | 2 | brief | 16 | True |

Exact prompts, raw responses, settings, plan and source snapshots are preserved in the run. Mechanical conversion of unambiguous rule-answer JSON types is allowed prospectively, with original and derived text retained. No incorrect answer or order is corrected.


![hypothesis levels](hypothesis_levels.png)

![effect and repeat variation](effect_and_repeat_variation.png)

![bullwhip by role](bullwhip_by_role.png)

![cost phases](cost_phases.png)

![all orders](all_orders.png)

![example chain](example_chain.png)

[Excel tables and replayed data](RESULTS.xlsx). All six figures are available as PNG/PDF.

[Protocol and limitations](../../../../docs/DEADLINE_COHORT_PROTOCOL_20261018.md). The previous initial/revision study is preserved separately. No response replacement or sample extension based on outcomes is permitted.
