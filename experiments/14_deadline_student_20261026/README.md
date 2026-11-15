# Experiment 14 — student time-pressure framing

**Complete and closed: 10 matched blocks, 30 main chain contexts, 24 weeks. Start with the report or values workbook below.**

| Open | What you will see |
|---|---|
| [REPORT.pdf](reports/REPORT.pdf) · [REPORT.md](reports/REPORT.md) | Conclusions first; independent variables; every measured outcome and diagnostic with values, units and calculations; fully named comparisons |
| [H1–H2 slide table](reports/figures/conclusions/H1_H2_TABLE.png) · [PDF](reports/figures/conclusions/H1_H2_TABLE.pdf) | Four columns: hypothesis, mean difference, 95% CI and adjusted p < 0.01; exact p-values remain in the source tables |
| [ALL_VALUES.xlsx](reports/tables/ALL_VALUES.xlsx) | All current tables in one workbook, including every weekly order, state, probe answer and quiz answer |
| [Recorded variables and sources](reports/tables/RECORDED_VARIABLES_AND_SOURCES.xlsx) | Excel guide to settings, game records, outcomes and technical fields; labels Beer Game, proposal, added measurement, analysis and software origins, with saved condition values |
| [Figures](reports/figures/README.md) | Condition values, pressure comparison, education comparison, sample-prefix effects and p-values; PNG/SVG/PDF with explicit axis definitions |
| [Additional figures: control reading only](reports/figures/control_reading_only/README.md) | Six measured quantities for 120 seconds + control reading and 8 seconds + control reading; one overview plus individual PNG/SVG/PDF plots; existing figures unchanged |
| [CSV files and variable dictionaries](reports/tables/README.md) | Exact numeric values and definitions of all reported measurements and original exported fields |
| [Notebook](notebooks/STUDENT_PRESSURE.ipynb) | Open the saved results, view named-condition tables, refresh the publication and display figures |

## Exactly what A, B and C mean

These are **three conditions in one study** (`student_framing_v3`).

| Condition | Assigned fictional time allowance | Assigned reading |
|---|---:|---|
| A — 120 s + control | 120 seconds per fictional student decision | 170-word control reading |
| B — 8 s + control | 8 seconds per fictional student decision | Same control reading |
| C — 8 s + education | 8 seconds per fictional student decision | 170-word causal supply-chain education |

The two independent variables are the **fictional allowance** and **reading**. Requested model/effort is GPT-6 Astra/xhigh in every condition. Actual model runtime is unrestricted; every decision is submitted once. There is no revision round or enforced model timer.

- **Pressure comparison (H1/H2): 8 s + control minus 120 s + control.** This changes the fictional allowance while holding reading fixed.
- **Education comparison (H3/H4a/H4b): 8 s + education minus 8 s + control.** This changes the reading while holding the 8-second framing fixed.
- Positive difference = the first named condition is higher. Negative = lower. A minus B would reverse B minus A.

| Dependent variable: mean across 10 chains | 120 s + control | 8 s + control | 8 s + education |
|---|---:|---:|---:|
| Pipeline response: order decrease per additional outstanding case | 0.318837 | 0.196007 | 0.270122 |
| Total 24-week holding + backlog cost (game units/chain) | 574.45 | 642.95 | 538.45 |
| Within-role weekly order variance, averaged over roles (cases²) | 12.450091 | 17.829438 | 10.104529 |
| Bullwhip: role order variance / external-demand variance | 1.831036 | 2.601594 | 1.484146 |

The report also shows cost components, all weekly state variables, final inventories/backlogs/outstanding orders, probe and ordering diagnostics, comprehension, recall, timing and completeness. H1/H3 reuse the pipeline-response measure for different comparisons. Pipeline response is a responsiveness proxy; no optimal behavioral beta was estimated.

**Consistent presentation terminology:** H1 is **pipeline underweighting**, measured through the **pipeline-response proxy**: order decrease per additional outstanding case in matched probes. These terms are not synonyms. The H1 difference of −0.1228 describes lower response under time constraint, consistent with greater underweighting; it is not a decrease in an underweighting score, and no optimal-response benchmark was estimated. H2 is **total holding and backlog cost**; “total cost” was shorthand for this same outcome. Both H1/H2 presentation images now state these distinctions, with all numerical results unchanged.

All five planned contrasts have the predicted direction and Holm-adjusted p=0.009766 in this sample. These are model portrayals, not validated human-student outcomes. The statistical unit is 10 matched block differences; four roles and 24 weeks are repeated observations. Development (one three-context block) stays separate.

## One current location

```text
14_deadline_student_20261026/
  reports/
    REPORT.md                 current full report
    REPORT.pdf                same content as the Markdown report
    figures/                  current labeled plots, captions, PDF/SVG/PNG
    tables/                   all measured values, dictionaries and workbook
    PUBLICATION.json          publication checks and hashes
  data/student_framing_v3/     preserved raw contexts and closed-collection receipt
  analysis/student_framing_v3/ preserved original numerical analysis and verification
  hypotheses/                 frozen protocols and plans
  prompts/                    frozen exact instructions and readings
  notebooks/                  saved-result notebook
  archive/                    old publications and presentation versions
```

[Exact prompts](prompts/student_framing_v3/README.md) · [Frozen protocol](hypotheses/STUDENT_FRAMING_V3.md) · [Original statistical verification](analysis/student_framing_v3/FINAL_VERIFICATION.json) · [Archive index](archive/README.md).

The earlier strict-deadline pilot report has moved into the archive. It is not another current report or part of these data. The unrun carry-forward draft remains under `analysis/design_history/`.

## Rebuild offline

Rebuild the variable inventory with `python scripts/export_exp14_variable_inventory.py` (requires `openpyxl`). It checks all 243 copied condition-summary values and preserves the existing report and input tables. The workbook distinguishes the H1 response proxy from underweighting and fictional time allowances from observed packet latency.

For the enlarged original two-row table, run `python scripts/export_exp14_h1_h2_table.py`. PNG, PDF and SVG are saved as `reports/figures/conclusions/H1_H2_TABLE.*`.

For the H1/H2-only presentation image, run `python scripts/export_exp14_h1_h2.py`. The presentation labels map “No time constraint” to the 120-second fictional scenario and “Time constraint” to the 8-second fictional scenario; both retain unrestricted actual model runtime. The slide footnote states this mapping. Original hypothesis tests and the five-test Holm adjustment are preserved.

From the repository root, using a Python environment with `requirements.txt` installed:

```bash
python scripts/report_exp14_framing.py
```

This single command publishes the report, all five figures and every table. `scripts/export_exp14_framing_slides.py` uses the same publisher, so it cannot create a second competing report folder. The historical `scripts/report_exp14.py` points to its archive when the current collection is closed.

All original analysis values and raw files are preserved; the current publisher checks hashes and replays the saved games. It makes no model calls. [Publication and preservation checks](reports/PUBLICATION.json).

The additional two-condition figures are generated separately with `python scripts/export_exp14_control_figures.py`. This reads the saved values and verifies that the existing publication remains unchanged. [Open their combined PDF](reports/figures/control_reading_only/ALL_CONTROL_FIGURES.pdf).

The overview and individual H1/H2 panels use the same terminology as the conclusions images: **Pipeline underweighting**, explicitly identified as measured through a response proxy, and **Total holding and backlog cost** in full. Lower response is consistent with greater underweighting. Numeric values, confidence bands and tests are unchanged. Prior plot versions are archived automatically when rebuilding.

The table and overview use the user's exact headings: **H1: Tight deadlines increase pipeline underweighting** and **H2: Tight deadlines increase total holding and backlog costs.** Wording is shared in `scripts/exp14_slide_labels.py`. Both images omit explanatory footer sentences. The table names the subtraction in its column header; the overview combines the hypotheses, observed response decrease (38.5%), cost increase (11.9%), means and 95% CI bands. Four descriptive panels appear below. H1/H2 retain **Holm p < 0.01**. Exact values, calculations and limitations remain in the companion README and CSV files; numerical results and individual plots are unchanged.
