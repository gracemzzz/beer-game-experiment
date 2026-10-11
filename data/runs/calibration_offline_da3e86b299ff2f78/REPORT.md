# Token-budget Beer Game — conclusions

1. SYNTHETIC SOFTWARE CHECK: no GPT evidence or hypothesis inference.
2. Run status: complete. Estimated cost/reservations: $0.0000.
3. Saved successful API stages: 144; other saved attempts: 0.
4. Suggested memo caps: 96 / 240 tokens; doubled benchmark 480.
5. Manipulation screen passed: False. This is a provisional feasibility check, not proof of a human time-pressure equivalent.
6. Do not start a paid main experiment yet. Inspect truncation, actual token use and adequate-versus-benchmark agreement.
Calibration uses 24 independent hypothetical states (all four roles), not complete game chains. This follow-up uses prospectively fixed caps and retains the earlier completed reference screen. It does not reselect percentiles or change the pass thresholds.
Short truncation: 0.0% (required at least 20%); adequate truncation: 0.0% (required at most 5%).
Adequate versus doubled allowance: median absolute order difference 0.0 units (screen requires at most 4).

## Calibration summary

```
   screen  mean_tokens  truncated_fraction  mean_order
 adequate          0.0                 0.0      9.8333
benchmark          0.0                 0.0      9.8333
    short          0.0                 0.0      9.8333
```

## Calibration state results

```
   screen  item        role  inventory  supply_line  order  plan_tokens  final_tokens  plan_truncated  plan_limit  latency_s
    short     0    retailer          0            0     19            0             0           False          96        0.0
    short     1    retailer          0           12     16            0             0           False          96        0.0
    short     2    retailer          0           36     11            0             0           False          96        0.0
    short     3    retailer         24            0      8            0             0           False          96        0.0
    short     4    retailer         24           12      5            0             0           False          96        0.0
    short     5    retailer         24           36      0            0             0           False          96        0.0
    short     6  wholesaler          0            0     19            0             0           False          96        0.0
    short     7  wholesaler          0           12     16            0             0           False          96        0.0
    short     8  wholesaler          0           36     11            0             0           False          96        0.0
    short     9  wholesaler         24            0      8            0             0           False          96        0.0
    short    10  wholesaler         24           12      5            0             0           False          96        0.0
    short    11  wholesaler         24           36      0            0             0           False          96        0.0
    short    12 distributor          0            0     19            0             0           False          96        0.0
    short    13 distributor          0           12     16            0             0           False          96        0.0
    short    14 distributor          0           36     11            0             0           False          96        0.0
    short    15 distributor         24            0      8            0             0           False          96        0.0
    short    16 distributor         24           12      5            0             0           False          96        0.0
    short    17 distributor         24           36      0            0             0           False          96        0.0
    short    18     factory          0            0     19            0             0           False          96        0.0
    short    19     factory          0           12     16            0             0           False          96        0.0
    short    20     factory          0           36     11            0             0           False          96        0.0
    short    21     factory         24            0      8            0             0           False          96        0.0
    short    22     factory         24           12      5            0             0           False          96        0.0
    short    23     factory         24           36      0            0             0           False          96        0.0
 adequate     0    retailer          0            0     19            0             0           False         240        0.0
 adequate     1    retailer          0           12     16            0             0           False         240        0.0
 adequate     2    retailer          0           36     11            0             0           False         240        0.0
 adequate     3    retailer         24            0      8            0             0           False         240        0.0
 adequate     4    retailer         24           12      5            0             0           False         240        0.0
 adequate     5    retailer         24           36      0            0             0           False         240        0.0
 adequate     6  wholesaler          0            0     19            0             0           False         240        0.0
 adequate     7  wholesaler          0           12     16            0             0           False         240        0.0
 adequate     8  wholesaler          0           36     11            0             0           False         240        0.0
 adequate     9  wholesaler         24            0      8            0             0           False         240        0.0
 adequate    10  wholesaler         24           12      5            0             0           False         240        0.0
 adequate    11  wholesaler         24           36      0            0             0           False         240        0.0
 adequate    12 distributor          0            0     19            0             0           False         240        0.0
 adequate    13 distributor          0           12     16            0             0           False         240        0.0
 adequate    14 distributor          0           36     11            0             0           False         240        0.0
 adequate    15 distributor         24            0      8            0             0           False         240        0.0
 adequate    16 distributor         24           12      5            0             0           False         240        0.0
 adequate    17 distributor         24           36      0            0             0           False         240        0.0
 adequate    18     factory          0            0     19            0             0           False         240        0.0
 adequate    19     factory          0           12     16            0             0           False         240        0.0
 adequate    20     factory          0           36     11            0             0           False         240        0.0
 adequate    21     factory         24            0      8            0             0           False         240        0.0
 adequate    22     factory         24           12      5            0             0           False         240        0.0
 adequate    23     factory         24           36      0            0             0           False         240        0.0
benchmark     0    retailer          0            0     19            0             0           False         480        0.0
benchmark     1    retailer          0           12     16            0             0           False         480        0.0
benchmark     2    retailer          0           36     11            0             0           False         480        0.0
benchmark     3    retailer         24            0      8            0             0           False         480        0.0
benchmark     4    retailer         24           12      5            0             0           False         480        0.0
benchmark     5    retailer         24           36      0            0             0           False         480        0.0
benchmark     6  wholesaler          0            0     19            0             0           False         480        0.0
benchmark     7  wholesaler          0           12     16            0             0           False         480        0.0
benchmark     8  wholesaler          0           36     11            0             0           False         480        0.0
benchmark     9  wholesaler         24            0      8            0             0           False         480        0.0
benchmark    10  wholesaler         24           12      5            0             0           False         480        0.0
benchmark    11  wholesaler         24           36      0            0             0           False         480        0.0
benchmark    12 distributor          0            0     19            0             0           False         480        0.0
benchmark    13 distributor          0           12     16            0             0           False         480        0.0
benchmark    14 distributor          0           36     11            0             0           False         480        0.0
benchmark    15 distributor         24            0      8            0             0           False         480        0.0
benchmark    16 distributor         24           12      5            0             0           False         480        0.0
benchmark    17 distributor         24           36      0            0             0           False         480        0.0
benchmark    18     factory          0            0     19            0             0           False         480        0.0
benchmark    19     factory          0           12     16            0             0           False         480        0.0
benchmark    20     factory          0           36     11            0             0           False         480        0.0
benchmark    21     factory         24            0      8            0             0           False         480        0.0
benchmark    22     factory         24           12      5            0             0           False         480        0.0
benchmark    23     factory         24           36      0            0             0           False         480        0.0
```

## Interpretation limits

This protocol restricts visible preparation tokens plus a common final-response allowance, with reasoning effort none. It does not directly limit hidden cognitive effort, wall-clock time or human thinking time. Prompts cannot reliably count remaining tokens; the API hard cap is the enforced constraint. A truncated memo is accepted as a deadline outcome, then a common 192-token stage solicits the order. The final stage can still involve implicit computation, and unused token allowance is not effort used.
Technical retries retain the same prompt and cap. Failed final responses can replace a whole group only within the configured limit; all failed attempts remain recorded. Replacement selection withholds inferential p-values. No order is clipped or replaced by a fabricated answer. The separate emergency scale check stops the run rather than making a boundary order.

Sources: [provided reflection](../../source/ThoughtsReflection_Paragraph.docx); [MIT Beer Game](https://web.mit.edu/jsterman/www/SDG/beergame.html); [Lee, Padmanabhan & Whang](https://pubsonline.informs.org/doi/10.1287/mnsc.43.4.546); [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-nano).
