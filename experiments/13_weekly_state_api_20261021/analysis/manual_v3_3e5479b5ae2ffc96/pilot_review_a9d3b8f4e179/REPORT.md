# GPT-6 Astra / ultra: three received manual pilots

1. **All three games completed and passed independent replay:** 24 weeks × 10 chains each, 2,880 weekly orders and 480 final probe choices in total.
2. **Model recorded:** GPT-6 Astra; reasoning setting ultra, as reported by the user. The original JSON metadata remains unchanged. The backend/API model is not independently verified.
3. **H1/H3 show no pipeline-sensitivity difference:** all three values are 1.0. H2/H4 differences follow the predicted descriptive directions, but are not statistically established.
4. **These are development pilots, one matched block—not 30 independent trials.** They stay outside the main 10/20/40-block analysis. No p-values or inferential confidence intervals are computed.
5. **Protocol review remains incomplete:** A has partial execution evidence; B lacks a full transcript; C's provenance file reports controller-source exposure. Preserve all three rather than labeling them clean confirmatory observations.
6. **No new API spending.** The cumulative $5 cap remains unchanged; this review made no API calls.

## Pilot outcomes

A = control reading + extra reconsideration; B = control reading + first decision committed; C = causal education + first decision committed.

| Arm | Mean 24-week chain cost | Mean role order variance | Bullwhip | Pipeline sensitivity | Weekly orders changed on review |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 502.95 | 10.8363 | 1.6726 | 1.0000 | 3/960 |
| B | 545.20 | 13.8129 | 2.1306 | 1.0000 | 0/960 |
| C | 476.45 | 11.4229 | 1.7722 | 1.0000 | 0/960 |

Costs are game-cost units; each value averages ten dependent chains. The 120 role instances are fictional, not sampled students.

| Hypothesis | Pilot contrast | Difference | Descriptive reading |
| --- | --- | ---: | --- |
| H1 proxy | B-A | +0.000000 | zero |
| H2 | B-A | +42.250000 | predicted |
| H3 proxy | C-B | +0.000000 | zero |
| H4a | C-B | -2.389991 | predicted |
| H4b | C-B | -0.358381 | predicted |

H2 is cost; H4a/b are order variance and bullwhip, not education's cost contrast. H4a/b share the order-variance numerator and do not provide independent confirmations. C's reported source exposure confounds interpretation of education effects. A changed only 3/960 weekly orders and 0/160 probes; an extra opportunity existed, but its impact was small in this pilot.

## What the evidence establishes

The exact case IDs, seeds, chain assignments, controller fingerprint, all weekly states, costs, literal initial/final choices, probes and event hashes replay correctly against the frozen manifest. Zero and unchanged orders were retained. Orders ranged 0–23 in A, 0–30 in B and 0–16 in C; the controller completed all games without imposing an order floor.

A's saved request matches the frozen prompt after newline normalization. Its 50 recorded submissions contain literal choices and separate initial/revision interactions. However, its execution record explicitly omits initial setup, surrounding chat and administrative tools. B has an export and probe display only. C has an export, probe display and provenance receipt that reports source inspection before decisions; it says the full transcript was not exported. These records cannot establish complete clean-context adherence.

The user supplied the same three folder paths when asked about transcripts. They were rechecked; no missing transcript was invented or inferred from the JSON. Provider/model labels are user-reported. Controller-call timestamps are not verified thinking time, and one versus two decision opportunities is an AI resource analogue rather than a calibrated human deadline.

## Files and plots

- [Extracted arm outcomes](../../analysis/manual_v3_3e5479b5ae2ffc96/pilot_review_a9d3b8f4e179/pilot_outcomes.csv) and [descriptive H1–H4 contrasts](../../analysis/manual_v3_3e5479b5ae2ffc96/pilot_review_a9d3b8f4e179/descriptive_contrasts.csv).
- [Replay and provenance receipt](../../analysis/manual_v3_3e5479b5ae2ffc96/pilot_review_a9d3b8f4e179/REVIEW.json).
- [Preserved originals and separate model report](../../data/manual_v3_3e5479b5ae2ffc96/pilot_reviews/a9d3b8f4e179).
- [Descriptive figures and captions](FIGURE_CAPTIONS.md). No error bars or p-values are attached to these pilots.

## Next collection

Keep these pilots as development evidence. Before a main launch, complete the transcript/adherence check and resolve the reported C source-exposure issue in a separately recorded technical check. Preserve this attempt. Do not tune prompts for significance or add the pilot to the first ten main blocks. The existing main prompts remain prepared, not collected. Large batches increase fictional headcount; independent fresh three-arm blocks determine inferential sample size.
