# Beer Game deadline study — final package

**Completed 18 October 2026.** 20 responses, 500 fictional identities, 40,000 submitted weekly orders. Recorded model/mode: user-reported GPT-6 / Pro.

| What you need | Open this |
| --- | --- |
| Report and all six plots | [REPORT.md](REPORT.md) |
| Every exact prompt, one box per task | [EXACT_PROMPTS.md](EXACT_PROMPTS.md) |
| Extracted results and column meanings | [results/README.md](results/README.md) |
| Excel results | [RESULTS.xlsx](results/RESULTS.xlsx) |
| Only the model's weekly orders | [weekly_orders.csv](results/weekly_orders.csv) |

**Main finding:** H1 points in its predicted direction in both rounds. H2 points the other way. H3 changes direction between rounds and is opposite overall. Same-deadline repeats vary substantially. These are descriptive model-generated scenarios; fictional deadlines are not enforced thinking time and the personas were not validated against real students.

The report displays all six plots. Their PNG and PDF files are in `plots/`. Exact prompts include all profiles, demand paths and the output format. Results retain all valid decisions, including zero orders.

The package can be read without Python or an API key. Extract the entire ZIP together so report images and links work. In the original repository, `notebooks/07_deadline_cohort_rerun.ipynb` provides 125 interactive team charts: run sections 1–4, then 7–8.

Source run: `deadline_cohort_2800524c9b2e0729`; analysis: `daa53a7e838a`. Original JSON replies and scientific source snapshots remain under `data/runs/` in the repository. [Provenance and file hashes](results/provenance.json) identify the package's sources. No new responses, analysis rules or API calls were added by packaging.
