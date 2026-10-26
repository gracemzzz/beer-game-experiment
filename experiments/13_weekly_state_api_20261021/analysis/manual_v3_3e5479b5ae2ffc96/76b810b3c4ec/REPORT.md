# Paired Beer Game block analysis

1. Conditional model-simulation analysis; human observations: 0.
2. CSV records supplied: 0/480; missing CSV rows: 480. Completed 24-week games: 0/480; unobserved games (zero weeks): 0; partial games: 0. Planned placeholder rows are not collected model responses.
3. Provenance: not_verified; this analysis does not authenticate raw API lineage.
4. Inference uses matched independent blocks; chains, roles, and weeks inside a batch do not increase the inferential sample size.

| Model | Test | Matched blocks | Contrast mean | 95% interval | Two-sided p | Holm 5 | Holm 20 | Direction |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| gpt_flagship | H1 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_flagship | H2 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_flagship | H3 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_flagship | H4a | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_flagship | H4b | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_balanced | H1 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_balanced | H2 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_balanced | H3 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_balanced | H4a | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_balanced | H4b | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_economy | H1 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_economy | H2 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_economy | H3 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_economy | H4a | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| gpt_economy | H4b | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| claude | H1 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| claude | H2 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| claude | H3 | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| claude | H4a | 0 | missing | missing to missing | missing | missing | missing | unavailable |
| claude | H4b | 0 | missing | missing to missing | missing | missing | missing | unavailable |

Missing decisions and endpoints remain missing. Each test's matched-block count reflects only its eligible paired outcomes.

Opposite significant effects are not support for a directional hypothesis. Confidence intervals are unadjusted; significance uses Holm-adjusted two-sided p-values.

Fixed 10/20/40 prefixes; only the full prospective sample is primary. Do not select a preferred significant prefix.

- Independent generation blocks, not generated chains, roles, or weeks, are the inferential units.
- Each arm must have a separately generated response stream; separate identity labels inside a shared response do not establish independent blocks or arms.
- The sign-flip test assumes exchangeability under the paired null (or symmetric independent paired differences); the CSV cannot verify this design assumption.
- Pipeline sensitivity is an assay proxy, not an identified normative underweighting coefficient.
- Computational opportunity or prompted pressure is an analogue, not measured binding human decision time.
- The input contains caller-aggregated outcomes. This module does not replay game states or independently authenticate API response lineage.
- Sample-size sweeps are fixed descriptive sensitivity analyses, not additional opportunities to stop when significance appears.
- Available-case comparisons from an incomplete planned sample are provisional; treatment-related failures can bias complete-case contrasts.
