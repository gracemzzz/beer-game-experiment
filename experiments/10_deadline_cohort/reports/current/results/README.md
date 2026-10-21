# Results for the H1-H4 assessment

Start with [RESULTS.xlsx](RESULTS.xlsx), or [weekly_orders.csv](weekly_orders.csv) for the 40,000 model orders. The workbook has ten sheets. Its `hypotheses` sheet now contains the four user-specified hypotheses, not the earlier three-outcome labels.

| File/sheet | Meaning |
| --- | --- |
| `hypotheses` | Four exact hypotheses, available proxy means, missing design elements and assessment. H3/H4 estimates are blank because the groups do not exist. |
| `chains`, `roles` | 500 team-condition/round outcomes and 2,000 role trajectories; repeated identities are not additional people. |
| `batches`, `contrasts` | Ten batch comparisons and 250 matched team/round comparisons. |
| `repeat_variation`, `choice_changes` | Same-deadline repeats and order changes. |
| `probes` | 2,000 order pairs underlying the H1 sensitivity proxy. |
| `quality` | Four condition/round summaries. |
| `rounds` | 72,000 Python-replayed states, including practice and automatic continuation. |
| `weekly_orders.csv` | Model weeks 5-24 only; excludes practice and continuation orders. |
| `task_provenance.csv` | Twenty task IDs, reported model/mode and prompt/response hashes. |

`brief` means the fictional 10-second scenario and `ample` the 180-second scenario. `generation` is round 1 or 2. A team has retailer, wholesaler, distributor and factory roles. `fictional_student_id` is an export label formed from team + role, not a real student record.

Sensitivity is `(probe order with 8 dispatched cases - order with 32)/24`. Lower sensitivity is only a proxy consistent with relatively less response to the supply line; it is not an identified structural underweighting coefficient. `cost` includes all scoring phases; `model_cost` and `automatic_cost` distinguish them. Inventory/backlog/shipment states were computed by Python.

`bullwhip` and `bullwhip_difference` are preserved supplementary outcome columns. **They do not measure the new education hypotheses H3 or H4.** Deadline differences are brief minus ample. Repeat differences are round 1 minus round 2. No education/control assignment or verified binding-time variable exists in the source data.

The nine accounting/decision CSVs retain their source values. The hypothesis assessment and workbook were republished for the new framework. [Provenance](provenance.json) records the unchanged raw evidence and the post-collection reporting update.
