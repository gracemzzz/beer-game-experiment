# Experiment 14: H1-H4 conclusions

GPT-6 Astra / extra high. Ten matched chain pairs; 40 fictional roles per condition; 24 weeks. Development responses are excluded.

1. H1: Pressure - adequate, pipeline response: mean difference -0.1228; Holm p=0.009766.
2. H2: Pressure - adequate, total holding/backlog cost: mean difference +68.5; Holm p=0.009766.
3. H3: Education - control, pipeline response: mean difference +0.07411; Holm p=0.009766.
4. H4: Education - control: order variance -7.725 (Holm p=0.009766); bullwhip -1.117 (Holm p=0.009766).

| H | Quantity / units | Mean contrast | 95% interval | Raw p | Holm 5 |
|---|---|---:|---|---:|---:|
| H1 | Pipeline response (Order cases / outstanding case) | -0.1228 | -0.1384 to -0.1076 | 0.001953 | 0.009766 |
| H2 | Total cost (Game cost units) | +68.5 | 45.5 to 96.55 | 0.001953 | 0.009766 |
| H3 | Pipeline response (Order cases / outstanding case) | +0.07411 | 0.0516 to 0.09498 | 0.001953 | 0.009766 |
| H4a | Order variance (Cases squared) | -7.725 | -11.72 to -4.333 | 0.001953 | 0.009766 |
| H4b | Bullwhip (Ratio) | -1.117 | -1.666 to -0.6332 | 0.001953 | 0.009766 |

H1/H2 compare pressure with adequate time. H3/H4 compare education with control under pressure. Tests are exact two-sided paired sign flips; Holm adjusts the five endpoints. Intervals are pointwise 95% paired-block bootstrap intervals.

These are AI student-roleplay results, not observations of real students. Actual model runtime was unlimited; every answer came from the model. Pipeline response is a proxy for underweighting. Shared project context and the block6 service interruption are documented in the full report/context note.

[Full report](../REPORT.pdf) | [Figures and plotting data](README.md)
