# Extracted results

Start with **[RESULTS.xlsx](RESULTS.xlsx)** for the ten original analysis sheets, or **[weekly_orders.csv](weekly_orders.csv)** for just the 40,000 model-submitted decisions. CSVs open in Excel, Python or R. CSV copies of the original tables and the workbook are byte-identical to the completed analysis.

| File / Excel sheet | Rows | Meaning |
| --- | ---: | --- |
| `weekly_orders.csv` (CSV only) | 40,000 | One submitted order per task, team, role and week; excludes practice/continuation |
| `hypotheses` | 3 | Overall H1/H2/H3 means and brief-minus-ample differences |
| `batches` | 10 | One paired comparison per batch and round |
| `chains` | 500 | Team outcomes for each condition and round |
| `roles` | 2,000 | Role outcomes for each condition and round |
| `contrasts` | 250 | Matched team/round differences between deadlines |
| `repeat_variation` | 250 | Round 1 minus round 2 under the same deadline |
| `choice_changes` | 20 | Counts and magnitudes of changed orders |
| `quality` | 4 | Order counts, zeros, largest orders and distinct paths |
| `probes` | 2,000 | Matched-state order pairs used for H1 |
| `rounds` | 72,000 | Python-replayed states for model, practice and automatic weeks |
| `task_provenance.csv` (CSV only) | 20 | Task, reported settings, source paths and prompt/response hashes |

## Main columns

- `task_id`: identifies one complete model reply. `b0001_g02_ample` means batch 1, second generation, 180-second scenario.
- `condition`: `brief` = 10 seconds; `ample` = 180 seconds. `generation` means repeated round 1 or 2.
- `chain_id`: one four-role team. `role`: retailer, wholesaler, distributor or factory. `profile_id`: assigned fictional personality.
- `fictional_student_id`: an export label formed from team + role; it identifies the same fictional identity across deadlines and rounds, not a real person.
- `week`: submitted choices cover weeks 5–24. `order`: the model's integer order. `customer_demand`: the supplied customer-demand path, not a generated student response.
- `phase` in `rounds`: `practice` = weeks 1–4; `model` = weeks 5–24; `automatic` = weeks 25–36. Only `model` orders were generated. Inventory, backlog, shipments and cost were calculated by Python.
- `sensitivity`: H1 = (probe order with 8 dispatched cases minus order with 32) / 24. `bullwhip`: H3 = sample variance of orders / sample variance of customer demand.
- `cost`: H2 full scored team/role cost. `model_cost` and `automatic_cost` separate the two main scoring phases; `practice_cost` is also included in the total.
- Deadline contrasts are **brief minus ample**. Same-deadline repeat contrasts are **round 1 minus round 2**. Do not mix them.

Blank p-value/interval cells mean inference was deliberately withheld, not zero. Repeated trajectories and rows within a generated batch are not independent human observations. Raw accepted JSONs remain in the repository; `task_provenance.csv` points to their preserved original text. [File hashes and provenance](provenance.json).
