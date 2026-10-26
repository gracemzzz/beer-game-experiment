# First-context presentation figures

1. **H2 and H4 have the predicted direction in the first Astra and Sol contexts.**
2. **H1 and H3 do not show the predicted pattern. No hypothesis is statistically established.**
3. **Transcript review pending.** Each model has one displayed context, containing 50 dependent chains per condition and 24 weeks. These are provisional descriptive results.

[Open all three slides as PDF](ALL_THREE_SLIDES.pdf). Use the PNGs directly in PowerPoint, or SVGs for scalable graphics.

## Slide 1 — Costs and order fluctuations

[PNG](01_costs_and_fluctuations.png) · [SVG](01_costs_and_fluctuations.svg) · [PDF](01_costs_and_fluctuations.pdf)

**Caption:** In the first completed Astra and Sol contexts, the one-decision control condition had higher costs than the condition with a separate revision. Causal education was associated with lower order variation and bullwhip than the one-decision control. These are observed simulation differences, not significance results.

| Model | H2: cost B vs A | H4a: variance C vs B | H4b: bullwhip C vs B |
|---|---:|---:|---:|
| GPT-6 Astra | +28.7% | -79.1% | -78.9% |
| GPT-6.1 Sol | +7.2% | -40.1% | -40.9% |

## Slide 2 — Outstanding replenishment orders

[PNG](02_outstanding_order_response.png) · [SVG](02_outstanding_order_response.svg) · [PDF](02_outstanding_order_response.pdf)

**Caption:** Restricting revision did not reduce sensitivity to outstanding orders in these first contexts. Education did not increase sensitivity either. Thus the observed H2/H4 directions are not accompanied by the proposed H1/H3 mechanism.

## Slide 3 — Effects versus the number of chains

[PNG](03_effects_vs_chain_count.png) · [SVG](03_effects_vs_chain_count.svg) · [PDF](03_effects_vs_chain_count.pdf)

**Caption:** Effects are recomputed using the first 5 to 50 chains in each context. This shows within-context stability; it does not add independent replications. A valid observed significance-versus-size curve requires more eligible fresh contexts.

## What these figures include

First completed context from each non-excluded model (Astra and Sol); all three conditions are shown. The two completed Luna attempts are excluded because of filtered state displays (run001) and programmatically generated choices (run002), not their effect directions. Claude has no collected local-agent data. Additional contexts are still being collected.

A = control reading + initial decision and separate revision. B = control + one decision. C = causal education + one decision. All conditions share a context, so carryover is possible. All models requested high reasoning effort; client labels are not provider-authenticated model identity. This tests revision opportunities, not a timed human deadline; sensitivity is a proxy, not a calibrated underweighting coefficient.

H2 is mean 24-week holding plus backlog cost per chain. H4a averages weekly order variance over roles and chains; H4b averages role order variance divided by external demand variance. These quantities are not comparisons of model accuracy against human data.

[Plotted values](plotted_condition_values.csv) · [Plotted size prefixes](plotted_chain_prefixes.csv) · [Source evidence](SOURCE_RESULTS.json) · [Hashes and provenance](MANIFEST.json).

This is a frozen first-context slide snapshot. For newer completed runs, see the [live report](../REPORT.md) and [progress notebook](../../../notebooks/AGENT_PROGRESS.ipynb).

Export: `.venv/Scripts/python.exe scripts/export_agent_slides_v5.py`. The script verifies that the 50-chain endpoints equal the condition summaries and refuses to overwrite a snapshot with different evidence. No API calls or new decisions are made.
