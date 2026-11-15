# Human Beer Game study — start here

**Design draft, 14 November 2026. No human data have been collected.** This is a new study; the completed AI experiments stay separate.

1. **Measure underweighting by comparing two responses:** how much an order falls when available inventory increases, and how much it falls when an equally usable outstanding order increases. Measuring only the second response is insufficient.
2. **Use four human treatment groups:** adequate time/control lecture, pressure/control, adequate time/education, and pressure/education. All share the same operational information. The fourth group is necessary for H6.
3. **Test H5 with an actual change in conditions.** A separate routine-transfer task distinguishes persisting with an old rule from correctly adapting to changed delivery timing.
4. **Determine recruitment from human pilot variability and a meaningful effect size.** The AI significance does not establish human power. Ten chains per group is a possible pilot-scale design, not a demonstrated sufficient sample.

## Read these in order

| File | What it answers |
|---|---|
| [1. Study design](01_STUDY_DESIGN.md) | Who participates, four groups, deadlines, H1–H6, session steps |
| [2. Measurement and mathematical model](02_MEASUREMENT_MODEL.md) | Every outcome, exact equations, estimation, worked examples; **the main document for Inki** |
| [3. Sample size](03_SAMPLE_SIZE.md) | Assumptions, equations, calculated recruitment scenarios, H5 and H6 power |
| [4. Data collection](04_DATA_COLLECTION.md) | Exactly what the platform must save and what one observation means |
| [5. Literature and source mapping](05_LITERATURE.md) | Donohue's equation and the adaptations; original H5/H6 wording |
| [Calculation notebook](notebooks/POWER_AND_MEASURES.ipynb) | Change effect size/ICC/power assumptions; view power-versus-size figures |

The root contains only this guide and the five numbered documents. `analysis/` contains **planning calculations and software examples**, `data/` contains empty CSV templates, `materials/` contains proposed task states, and `notebooks/` contains one notebook. There are no human results or claims of confirmed hypotheses here.

## The central measurement in one example

Suppose four extra cases on hand reduce someone's order by three cases, but four extra cases already ordered reduce it by only one case. Inventory responsiveness is 3/4 = 0.75; pipeline responsiveness is 1/4 = 0.25. The **underweighting gap is 0.75 − 0.25 = 0.50**. The relative pipeline weight is 0.25/0.75 = 1/3, if the inventory response is reliably nonzero. Both quantities and their uncertainty must be reported.

H5 is different: after a delivery becomes too late to meet the task's deadline, reducing its weight can be **correct adaptation**. The old rule, new benchmark and persistence score are defined explicitly in document 2.

## Run the calculations

From `D:\beergame`:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/plan_human_study.py
.venv/Scripts/python.exe -m unittest discover -s tests -p test_human_study_planning.py
```

Or open the notebook and select **Beer Game (.venv)**. It uses NumPy, SciPy, pandas and matplotlib; no API, agent, widget or participant collection is started. Generated tables: [sample sizes](analysis/sample_sizes.csv), [power curves](analysis/power_curves.csv), [worked examples](analysis/measurement_examples.json). Figure: [power versus chains](analysis/POWER_VS_CHAINS.png).

## Before calling this a finalized protocol

The documents distinguish proposed settings from known quantities. The human timing pilot, smallest meaningful effects, lecture scripts, platform implementation, compensation and institutional human-research review still need to be finalized. Freeze those items and the analysis before recruiting the main sample. Software validation establishes arithmetic, not human validity or statistical significance.

For future agents: use [the data specification](04_DATA_COLLECTION.md), retain versioned draft changes, and never import AI responses as human observations. Do not revise hypotheses or stop collection in response to emerging p-values.
