# Token-budget Beer Game — conclusions

1. Real API responses; LLM simulation, not human evidence.
2. Run status: complete. Estimated cost/reservations: $0.0381.
3. Saved successful API stages: 144; other saved attempts: 0.
4. Suggested memo caps: 96 / 240 tokens; doubled benchmark 480.
5. Manipulation screen passed: True. This is a provisional feasibility check, not proof of a human time-pressure equivalent.
6. Review the state-level choices; then run one group per condition before scaling.
Calibration uses 24 independent hypothetical states (all four roles), not complete game chains. This follow-up uses prospectively fixed caps and retains the earlier completed reference screen. It does not reselect percentiles or change the pass thresholds.
Short truncation: 91.7% (required at least 20%); adequate truncation: 0.0% (required at most 5%).
Adequate versus doubled allowance: median absolute order difference 4.0 units (screen requires at most 4).

## Calibration summary

```
   screen  mean_tokens  truncated_fraction  mean_order
 adequate     151.1250              0.0000      8.9167
benchmark     192.4167              0.0000      6.2500
    short      95.3750              0.9167      6.3750
```

## Calibration state results

```
   screen  item        role  inventory  supply_line  order  plan_tokens  final_tokens  plan_truncated  plan_limit  latency_s
    short     0    retailer          0            0     12           96            39            True          96     3.8590
    short     1    retailer          0           12     16           96            39            True          96     1.5922
    short     2    retailer          0           36     20           96            39            True          96     1.5777
    short     3    retailer         24            0      6           87            39           False          96     2.2658
    short     4    retailer         24           12      0           96            39            True          96     1.9785
    short     5    retailer         24           36      0           96            39            True          96     1.7142
    short     6  wholesaler          0            0      8           96            39            True          96     1.7817
    short     7  wholesaler          0           12      4           96            39            True          96     2.3106
    short     8  wholesaler          0           36      0           96            39            True          96     2.9019
    short     9  wholesaler         24            0      0           96            39            True          96     1.9379
    short    10  wholesaler         24           12      8           96            39            True          96     1.9633
    short    11  wholesaler         24           36     20           96            39            True          96     1.9774
    short    12 distributor          0            0     16           96            39            True          96     1.6387
    short    13 distributor          0           12      8           96            39            True          96     1.8391
    short    14 distributor          0           36      0           96            39            True          96     2.8792
    short    15 distributor         24            0      5           96            39            True          96     2.1493
    short    16 distributor         24           12      6           96            39            True          96     2.0408
    short    17 distributor         24           36      4           90            39           False          96     1.7038
    short    18     factory          0            0      0           96            39            True          96     1.6886
    short    19     factory          0           12      0           96            39            True          96     2.1619
    short    20     factory          0           36     12           96            39            True          96     1.6033
    short    21     factory         24            0      0           96            39            True          96     1.8439
    short    22     factory         24           12      0           96            39            True          96     1.7094
    short    23     factory         24           36      8           96            39            True          96     2.1386
 adequate     0    retailer          0            0     16          212            39           False         240     2.2472
 adequate     1    retailer          0           12     20          175            39           False         240     1.9702
 adequate     2    retailer          0           36     16          167            39           False         240     2.0990
 adequate     3    retailer         24            0      4          168            39           False         240     2.6172
 adequate     4    retailer         24           12      0          148            39           False         240     2.2089
 adequate     5    retailer         24           36      0          119            39           False         240     1.8912
 adequate     6  wholesaler          0            0     12          133            39           False         240     1.9000
 adequate     7  wholesaler          0           12      0          139            39           False         240     2.3801
 adequate     8  wholesaler          0           36     20          114            39           False         240     2.6063
 adequate     9  wholesaler         24            0      8          139            39           False         240     2.9525
 adequate    10  wholesaler         24           12      8          142            39           False         240     2.2577
 adequate    11  wholesaler         24           36      4          117            39           False         240     1.9582
 adequate    12 distributor          0            0     16          128            39           False         240     1.8920
 adequate    13 distributor          0           12     12          132            39           False         240     2.4405
 adequate    14 distributor          0           36     12          174            39           False         240     2.0852
 adequate    15 distributor         24            0      4          133            39           False         240     1.7950
 adequate    16 distributor         24           12      6          175            39           False         240     2.5352
 adequate    17 distributor         24           36      8          161            39           False         240     2.1809
 adequate    18     factory          0            0     12          174            39           False         240     2.2997
 adequate    19     factory          0           12     20          148            39           False         240     1.8175
 adequate    20     factory          0           36      0          142            39           False         240     2.1070
 adequate    21     factory         24            0      0          147            39           False         240     2.1168
 adequate    22     factory         24           12      8          174            39           False         240     2.3845
 adequate    23     factory         24           36      8          166            39           False         240     2.0594
benchmark     0    retailer          0            0     12          187            39           False         480     2.1318
benchmark     1    retailer          0           12      0          214            39           False         480     2.2648
benchmark     2    retailer          0           36      8          204            39           False         480     2.2342
benchmark     3    retailer         24            0      0          137            39           False         480     2.0286
benchmark     4    retailer         24           12      4          165            39           False         480     1.9839
benchmark     5    retailer         24           36      8          224            39           False         480     2.1986
benchmark     6  wholesaler          0            0     20          207            39           False         480     2.1750
benchmark     7  wholesaler          0           12     20          240            39           False         480     2.5564
benchmark     8  wholesaler          0           36      0          166            39           False         480     2.3130
benchmark     9  wholesaler         24            0      8          182            39           False         480     2.6139
benchmark    10  wholesaler         24           12      0          168            39           False         480     2.0184
benchmark    11  wholesaler         24           36      4          131            39           False         480     4.5942
benchmark    12 distributor          0            0     16          209            39           False         480     1.9520
benchmark    13 distributor          0           12     16          217            39           False         480     2.2570
benchmark    14 distributor          0           36      8          201            39           False         480     2.6248
benchmark    15 distributor         24            0      0          167            39           False         480     2.1214
benchmark    16 distributor         24           12      6          213            39           False         480     3.3876
benchmark    17 distributor         24           36      0          214            39           False         480     2.3143
benchmark    18     factory          0            0      0          206            39           False         480     2.0532
benchmark    19     factory          0           12     12          190            39           False         480     2.0257
benchmark    20     factory          0           36      0          189            39           False         480     2.2128
benchmark    21     factory         24            0      0          186            39           False         480     2.2248
benchmark    22     factory         24           12      0          239            39           False         480     2.2541
benchmark    23     factory         24           36      8          162            39           False         480     2.3777
```

## Interpretation limits

This protocol restricts visible preparation tokens plus a common final-response allowance, with reasoning effort none. It does not directly limit hidden cognitive effort, wall-clock time or human thinking time. Prompts cannot reliably count remaining tokens; the API hard cap is the enforced constraint. A truncated memo is accepted as a deadline outcome, then a common 192-token stage solicits the order. The final stage can still involve implicit computation, and unused token allowance is not effort used.
Technical retries retain the same prompt and cap. Failed final responses can replace a whole group only within the configured limit; all failed attempts remain recorded. Replacement selection withholds inferential p-values. No order is clipped or replaced by a fabricated answer. The separate emergency scale check stops the run rather than making a boundary order.

Sources: [provided reflection](../../source/ThoughtsReflection_Paragraph.docx); [MIT Beer Game](https://web.mit.edu/jsterman/www/SDG/beergame.html); [Lee, Padmanabhan & Whang](https://pubsonline.informs.org/doi/10.1287/mnsc.43.4.546); [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-nano).
