# Presentation: chain size and context count

Both slides show H1, H2, H3, H4a and H4b with short labels and consistent model colors.

1. **[Chain-count PNG](CHAIN_SIZE.png)** · [SVG](CHAIN_SIZE.svg) · [PDF](CHAIN_SIZE.pdf). The x-axis uses the first 5–50 chains per condition in every reviewed run. Curves average the included contexts equally. Independent context counts stay at Astra2 / Sol2 / Luna3.
2. **[Context-count PNG](CONTEXT_COUNT.png)** · [SVG](CONTEXT_COUNT.svg) · [PDF](CONTEXT_COUNT.pdf). The x-axis adds reviewed fresh contexts chronologically. Curves are cumulative model means. Astra and Sol end at two reviewed contexts; Luna ends at three. No unobserved context is drawn.

H1/H3 use a magnified ×10⁻⁴ scale. Their underlying units are order reduction per additional outstanding case. H2 is 24-week cost per chain; H4a is order variance in cases squared; H4b is the order/customer-demand variance ratio. H1/H2 compare B−A, H3/H4 compare C−B. Group definitions and detailed p-values are in the [report](../REPORT.md).

**Data:** [Chain-prefix means](chain_count_values.csv) and [context-prefix means and p-values](context_count_values.csv). Context p-values are unavailable at n=1 and exploratory at later prefixes. No chain-level p-values are created.

Reviewed runs, in order: Astra run002/run003; Sol run002/run003; Luna run003/run004/run005. Pending and excluded attempts remain in the original report and raw records. Selection follows the existing procedure reviews, not effect direction. The final endpoints and p-values match the published statistics to 1e-12. The collection is closed; these exports make no new model calls.

Rebuild: `.venv/Scripts/python.exe scripts/export_agent_size_slides_v5.py`. Previous exports are preserved in history/. [Source/artifact hashes](MANIFEST.json).
