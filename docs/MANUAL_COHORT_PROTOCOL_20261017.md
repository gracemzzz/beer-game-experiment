# Manual cohort generation — 17 October 2026

Protocol `manual-cohort-trajectories-v1` supports notebook 06. The user requested copy-and-paste prompts that generate weekly Beer Game orders for many fictional students in one response, with local analysis after pasting the output. This protocol makes **no API calls** and does not spend the API campaign allowance.

## What to run

Open [06_manual_cohort_simulation.ipynb](../notebooks/06_manual_cohort_simulation.ipynb). It prepares the plan, displays the next prompt, accepts pasted JSON through a form, shows a progress bar, and exports results. There is also a plain-text-file import option. Install `requirements.txt` in the notebook kernel; `ipywidgets` supplies the paste form and chain selector.

Default: 500 fictional identities, assigned to 125 four-role chains. Each identity appears in an initial and a reconsidered trajectory, giving 1,000 condition-specific role trajectories. These are **500 generated identities, zero observed human students**. Five batches of 100 identities require ten responses: five initial outputs followed by five revisions. There are 24 weeks: four fixed practice weeks, twenty generated decision weeks, and twelve additional automatic scoring weeks.

`BATCH_STUDENTS=500` requests the entire cohort in one response per pass. This means 10,000 weekly integers plus 1,000 matched-state choices per response, before JSON overhead. Chat output limits may truncate it. The default batch size requests 2,000 weekly integers plus 200 probe choices per response. Choose batch size, cohort size, repetitions, horizon and model **before** collecting outputs; changing any creates a new fingerprint. A four-identity formatting check should use a separate plan and remain separate from the main cohort.

## Model and prompts

Suggested starting point: GPT-6 Astra, if available in the user's chat interface. OpenAI describes it as its most capable model, and documents high effort among its settings. This recommendation is about task capability, not validated fidelity to students. Chat access, controls and output limits can differ from the API; an API output specification does not guarantee a chat response length. Record the exact displayed model name and use **high** consistently. If high cannot be selected or verified in the interface, document that before collection rather than claiming it was controlled. [Official model page](https://developers.openai.com/api/docs/models/gpt-6-astra), [model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection), checked 17 October 2026.

Prompts retain the four existing fictional UB sophomore profiles, costs, demand distribution, supply delays and valid zero orders. They contain no predicted H1/H2/H3 direction, target effect size, preferred order, preferred maximum or forced variation. They ask for individual orders, not summary outcomes. Arithmetic/code can be used for bookkeeping, but the prompt asks the model not to substitute one optimized policy for all students.

Each prompt is standalone. Start a fresh chat for each, keep model and effort fixed, disable memory/personalization where available, and do not supply previous findings or desired hypothesis results. This reduces carryover but does not prove independent sampling or student realism. The user records a chat/session label and confirms the complete prompt was submitted. These labels are operator reports, not provider-verified model IDs or timestamps.

## Two passes

1. **Initial:** generate the cohort's complete weekly order trajectories and separate matched-state probe choices.
2. **Revision:** receive the same assignments and demand paths plus the locked initial orders; reconsider the entire trajectories and probes once. The model may retain or change choices and must recompute later physical states after changed orders.

The response is a single JSON object with `schema_version`, `study_id`, `batch_id`, `stage`, `rules`, `chains`, and `complete`. Every chain has its ID, an `orders` array of twenty four-integer rows by default, and a `probes` array of four two-integer rows. Roles always occur in retailer/wholesaler/distributor/factory order. Probe columns correspond to deliveries `[4,4]` and `[16,16]`. No summary costs or statistical claims are accepted as data.

A fictional student's stable identity is the pair `(chain_id, role)`. Its assigned personality is in the frozen plan; repeating that identity in both passes is a matched comparison, not a new student.

The factual rules questions are retained as comprehension checks. They do not reproduce the API calibration's completion/token-headroom tests. Actual hidden reasoning tokens, per-role thought allocation and generation wall time are unobserved. Do not report that token separation passed, and do not equate initial/revision to a verified short/adequate human-time treatment.

## What changes scientifically

| Feature | Earlier API revision study | New manual cohort study |
| --- | --- | --- |
| Decision generation | Separate current-state role calls | Many whole trajectories in one response |
| Revision | Same role, week, state and history | Entire trajectories reconsidered; downstream states change |
| Information | Role-local display and past rounds | Generator sees every supplied path, horizon and assigned role |
| Computation | Recorded provider token counts and fixed ceilings | Shared chat generation; per-student tokens unobserved |
| Dependence | Matched chain blocks were the planned units | Students/chains in the same generation are dependent; session labels do not establish independence |
| H1 probes | Separate low/high matched-state calls | Low/high choices are jointly visible in one output |
| Inference | Eligible prespecified paired tests in completed API studies | Descriptive contrasts and distributions; no student-row p-values or confidence intervals |

Full-trajectory generation necessarily exposes the horizon and demand path to the generator. Asking it not to give that information to its fictional students does not enforce information isolation. Physical replay verifies accounting for the supplied orders; it cannot verify what states the model actually considered. The method therefore cannot preserve every aspect of the earlier experiment and cannot be pooled with v3/v4 evidence.

## H1, H2, H3 and interpretation

- **H1:** initial minus revised pipeline sensitivity is predicted negative. Sensitivity is `(order with 8 dispatched cases − order with 32 dispatched cases) / 24`, averaged over the four roles. The current display is otherwise matched: week 12, local inventory 0, backlog 8, demand 8, receipts/shipments 4, awaiting dispatch 0, no history, and other-role inventories 12.
- **H2:** initial minus revised full chain cost is predicted positive. Costs include practice, decision and twelve automatic scoring weeks. The report separates these phases because automatic continuation can reverse the model-week contrast.
- **H3:** initial minus revised chain-average bullwhip is predicted positive. Compute the sample variance of each role's orders divided by the sample variance of customer demand during the decision weeks, then average all four roles. Also retain local-demand ratios. Zero denominator variance is undefined, never silently changed to zero. A ratio below one is not amplification above customer-demand variability.

The original structural-beta fit remains optional and exploratory, with its existing identification flags. It does not replace the matched-state H1 measure.

Reports label contrasts as predicted direction, opposite direction, no mean difference or undefined. These labels describe a generated dataset. They do not verify/disprove hypotheses about human students or causal effects of time pressure. More rows within one generation do not repair this limitation. Repeated cohort generations may describe reproducibility under a fixed prompting workflow, but require a prospective replication plan; this notebook does not automatically promote them to independent-human inference.

Prior research comparing synthetic respondent data with actual survey data found distorted relationships and potentially different substantive conclusions. That result is a reason to validate against real students before generalizing; it is not evidence that this particular Beer Game simulation must fail. [Bisbee et al., *Political Analysis*, “Synthetic Replacements for Human Survey Data? The Perils of Large Language Models”](https://www.cambridge.org/core/journals/political-analysis/article/synthetic-replacements-for-human-survey-data-the-perils-of-large-language-models/B92267DC26195C7F36E63EA04A47D2FE).

## Import integrity and reporting

The importer accepts JSON only, optionally in one JSON code block. It never evaluates pasted code. It checks IDs, exact fields, all required chains/weeks, integer/nonnegative quantities and factual answers. Duplicate keys, omitted rows, wrong models, nonfinite values and malformed or truncated output are rejected. The simulator's existing 100,000-case technical circuit breaker is a rejection threshold, not a suggested maximum, model instruction or clipping rule.

Raw attempts, metadata, exact prompts and source snapshots stay in `data/runs/manual_cohort_<fingerprint>/`. The first valid submission is locked; later alternatives cannot replace it. Rejected attempts remain visible. A technical retry must use the same frozen prompt, without desired-direction coaching. Repeated attempts are not independent cohort replications. No automatic paid retries occur.

Only batches with both accepted passes enter paired summaries. Partial reports identify missing batches. Reports, prompt boxes, CSV/Excel tables and PNG/PDF plots go to `reports/manual_cohort_<fingerprint>/`. Each analysis input set gets a separate version folder; earlier exports remain intact. `LATEST_MANUAL_COHORT_REPORT.json` is separate from the completed API-report pointers.

Figures include H1/H2/H3 contrasts with batch means, bullwhip by role, phase/cumulative costs, matched-state probe responses, every submitted order trajectory as a heatmap, and an interactive chain selector in the notebook. Spread plots describe generated values; they are not confidence intervals for a student population. Duplicated trajectories and zero-order rates are reported without being altered.

## Reproduce software checks

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -X utf8 scripts/build_manual_cohort_notebook.py
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -p test_manual_cohort.py -v
.\.venv\Scripts\python.exe -X utf8 scripts/check_manual_cohort.py
.\.venv\Scripts\python.exe -X utf8 scripts/prepare_manual_cohort.py
```

The full software check uses explicitly synthetic controls, including a 500-identity replay and plot export. It makes no model calls, proves no persona fidelity and provides no experimental hypothesis result. Notebook controls leave file import off; the paste form saves only after the user presses its button. The run prepared for the user contains no model response until one is actually pasted.
