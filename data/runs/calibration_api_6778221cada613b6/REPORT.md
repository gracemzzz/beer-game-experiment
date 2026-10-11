# Token-budget Beer Game — conclusions

1. Real API responses; LLM simulation, not human evidence.
2. Run status: complete. Estimated cost/reservations: $0.0540.
3. Saved successful API stages: 192; other saved attempts: 0.
4. Suggested memo caps: 176 / 240 tokens; doubled benchmark 480.
5. Manipulation screen passed: False. This is a provisional feasibility check, not proof of a human time-pressure equivalent.
6. Do not start a paid main experiment yet. Inspect truncation, actual token use and adequate-versus-benchmark agreement.
Calibration uses 24 independent hypothetical states (all four roles), not complete game chains. P25/P95 refer to memo-token use under the 1024-token reference. These percentiles cannot directly represent human response times.
Short truncation: 12.5% (required at least 20%); adequate truncation: 0.0% (required at most 5%).
Adequate versus doubled allowance: median absolute order difference 2.0 units (screen requires at most 4).

## Calibration summary

```
   screen  mean_tokens  truncated_fraction  mean_order
 adequate     147.7917               0.000      8.3333
benchmark     194.0833               0.000      6.6667
reference     193.2083               0.000      6.2500
    short     140.1250               0.125      5.9167
```

## Calibration state results

```
   screen  item        role  inventory  supply_line  order  plan_tokens  final_tokens  plan_truncated  plan_limit  latency_s
reference     0    retailer          0            0     20          217            39           False        1024     6.1064
reference     1    retailer          0           12      4          203            39           False        1024     3.5020
reference     2    retailer          0           36      0          213            39           False        1024     2.4270
reference     3    retailer         24            0      8          186            39           False        1024     3.6489
reference     4    retailer         24           12      6          189            39           False        1024     3.5273
reference     5    retailer         24           36      8          191            39           False        1024     2.1609
reference     6  wholesaler          0            0     16          149            39           False        1024     2.7733
reference     7  wholesaler          0           12     12          217            39           False        1024     2.6719
reference     8  wholesaler          0           36      0          195            39           False        1024     3.6166
reference     9  wholesaler         24            0      8          201            39           False        1024     2.3751
reference    10  wholesaler         24           12      4          141            39           False        1024     2.0135
reference    11  wholesaler         24           36      4          176            39           False        1024     2.5155
reference    12 distributor          0            0     12          197            39           False        1024     2.1294
reference    13 distributor          0           12     16          225            39           False        1024     3.2515
reference    14 distributor          0           36      0          185            39           False        1024     2.0435
reference    15 distributor         24            0      0          179            39           False        1024     2.8316
reference    16 distributor         24           12      8          176            39           False        1024     2.3025
reference    17 distributor         24           36      0          181            39           False        1024     2.2435
reference    18     factory          0            0     16          207            39           False        1024     2.4025
reference    19     factory          0           12      0          257            39           False        1024     8.1857
reference    20     factory          0           36      0          224            39           False        1024     3.3732
reference    21     factory         24            0      0          137            39           False        1024     2.0790
reference    22     factory         24           12      8          215            39           False        1024     2.8037
reference    23     factory         24           36      0          176            39           False        1024     2.0998
    short     0    retailer          0            0      8          111            39           False         176     1.7493
    short     1    retailer          0           12     16          176            39            True         176     2.3370
    short     2    retailer          0           36      0          157            39           False         176     2.1432
    short     3    retailer         24            0      8          129            39           False         176     1.8628
    short     4    retailer         24           12      0          147            39           False         176     2.0383
    short     5    retailer         24           36      0          114            39           False         176     1.6541
    short     6  wholesaler          0            0     16          149            39           False         176     1.8495
    short     7  wholesaler          0           12     10          128            39           False         176     2.0964
    short     8  wholesaler          0           36      0          176            39           False         176     2.3276
    short     9  wholesaler         24            0      4          113            39           False         176     1.7167
    short    10  wholesaler         24           12      6          163            39           False         176     2.0605
    short    11  wholesaler         24           36     10          113            39           False         176     2.0257
    short    12 distributor          0            0     16          131            39           False         176     1.8217
    short    13 distributor          0           12      8          159            39           False         176     2.2999
    short    14 distributor          0           36      0          153            39           False         176     1.8168
    short    15 distributor         24            0      8          176            39            True         176     2.0379
    short    16 distributor         24           12      8          153            39           False         176     2.0569
    short    17 distributor         24           36      0          122            39           False         176     2.3368
    short    18     factory          0            0     16          118            39           False         176     2.2284
    short    19     factory          0           12      0          176            39            True         176     2.2372
    short    20     factory          0           36      0          128            39           False         176     1.7501
    short    21     factory         24            0      8          142            39           False         176     1.8053
    short    22     factory         24           12      0          132            39           False         176     1.7398
    short    23     factory         24           36      0           97            39           False         176     1.7708
 adequate     0    retailer          0            0     16          162            39           False         240     2.1358
 adequate     1    retailer          0           12     12          148            39           False         240     1.8876
 adequate     2    retailer          0           36     20          123            39           False         240     2.2018
 adequate     3    retailer         24            0      6          125            39           False         240     1.9417
 adequate     4    retailer         24           12      6          173            39           False         240     1.9116
 adequate     5    retailer         24           36      0          137            39           False         240     1.8230
 adequate     6  wholesaler          0            0     12          165            39           False         240     1.8376
 adequate     7  wholesaler          0           12     14          173            39           False         240     2.3376
 adequate     8  wholesaler          0           36      0          138            39           False         240     1.9444
 adequate     9  wholesaler         24            0      8          156            39           False         240     2.0911
 adequate    10  wholesaler         24           12      0          120            39           False         240     1.9844
 adequate    11  wholesaler         24           36      0          131            39           False         240     2.5248
 adequate    12 distributor          0            0     16          217            39           False         240     2.3227
 adequate    13 distributor          0           12     20          139            39           False         240     1.9069
 adequate    14 distributor          0           36     24          195            39           False         240     2.3898
 adequate    15 distributor         24            0      8          128            39           False         240     1.8964
 adequate    16 distributor         24           12      8          157            39           False         240     2.0163
 adequate    17 distributor         24           36      0          163            39           False         240     2.0868
 adequate    18     factory          0            0     16          121            39           False         240     1.9078
 adequate    19     factory          0           12      0          165            39           False         240     2.2988
 adequate    20     factory          0           36      0          145            39           False         240     1.9370
 adequate    21     factory         24            0      8          122            39           False         240     1.8504
 adequate    22     factory         24           12      0          133            39           False         240     1.9703
 adequate    23     factory         24           36      6          111            39           False         240     1.7600
benchmark     0    retailer          0            0     12          193            39           False         480     2.5104
benchmark     1    retailer          0           12     20          164            39           False         480     2.5150
benchmark     2    retailer          0           36     20          173            39           False         480     2.2573
benchmark     3    retailer         24            0      4          189            39           False         480     2.5145
benchmark     4    retailer         24           12      0          160            39           False         480     2.4656
benchmark     5    retailer         24           36      2          213            39           False         480     2.3968
benchmark     6  wholesaler          0            0     12          212            39           False         480     2.3905
benchmark     7  wholesaler          0           12      8          234            39           False         480     2.8176
benchmark     8  wholesaler          0           36      0          212            39           False         480     2.4626
benchmark     9  wholesaler         24            0      8          265            39           False         480     2.4969
benchmark    10  wholesaler         24           12      0          194            39           False         480     2.0356
benchmark    11  wholesaler         24           36      4          183            39           False         480     2.1428
benchmark    12 distributor          0            0     16          159            39           False         480     2.3228
benchmark    13 distributor          0           12     14          227            39           False         480     2.5830
benchmark    14 distributor          0           36     14          272            39           False         480     2.5536
benchmark    15 distributor         24            0      6          175            39           False         480     2.3408
benchmark    16 distributor         24           12      0          175            39           False         480     2.8412
benchmark    17 distributor         24           36      0          169            39           False         480     2.4627
benchmark    18     factory          0            0     16          181            39           False         480     2.3592
benchmark    19     factory          0           12      0          189            39           False         480     2.3470
benchmark    20     factory          0           36      0          173            39           False         480     2.2988
benchmark    21     factory         24            0      0          202            39           False         480     2.0984
benchmark    22     factory         24           12      4          161            39           False         480     2.5308
benchmark    23     factory         24           36      0          183            39           False         480     2.5602
```

## Interpretation limits

This protocol restricts visible preparation tokens plus a common final-response allowance, with reasoning effort none. It does not directly limit hidden cognitive effort, wall-clock time or human thinking time. Prompts cannot reliably count remaining tokens; the API hard cap is the enforced constraint. A truncated memo is accepted as a deadline outcome, then a common 192-token stage solicits the order. The final stage can still involve implicit computation, and unused token allowance is not effort used.
Technical retries retain the same prompt and cap. Failed final responses can replace a whole group only within the configured limit; all failed attempts remain recorded. Replacement selection withholds inferential p-values. No order is clipped or replaced by a fabricated answer. The separate emergency scale check stops the run rather than making a boundary order.

Sources: [provided reflection](../../source/ThoughtsReflection_Paragraph.docx); [MIT Beer Game](https://web.mit.edu/jsterman/www/SDG/beergame.html); [Lee, Padmanabhan & Whang](https://pubsonline.informs.org/doi/10.1287/mnsc.43.4.546); [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-nano).
