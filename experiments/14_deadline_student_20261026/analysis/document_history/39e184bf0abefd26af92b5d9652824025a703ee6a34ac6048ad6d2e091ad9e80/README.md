# Experiment 14: simulated student time pressure

**Current study:** GPT-6 Astra / extra-high (`xhigh`) portrays fictional second-year University at Buffalo business students. The agent supplies every order. **There is no actual model timer, rejection for slow responses, random filler or software fallback.**

| Open | Contents |
|---|---|
| [PDF report](reports/student_framing_v3/REPORT.pdf) | Current results and simple H1-H4 explanations |
| [Text report](reports/student_framing_v3/REPORT.md) | Findings with extracted-data links |
| [Figures](reports/student_framing_v3/figures/README.md) | Current plots and captions |
| [Progress notebook](notebooks/STUDENT_PRESSURE.ipynb) | Saved progress, 10-second refresh, no widgets |
| [Exact prompts](prompts/student_framing_v3/README.md) | Common student prompt, timing framings and readings |
| [Protocol](hypotheses/STUDENT_FRAMING_V3.md) | Sampling, quantities, gates and limitations |

## Three conditions

| Arm | Fictional student's time per decision | Reading |
|---|---|---|
| A | 120 seconds, adequate time | Matched control |
| B | 8 seconds, insufficient time | Matched control |
| C | 8 seconds, insufficient time | Causal supply-chain education |

The model's actual effort and available runtime are the same in every arm. There is one submitted decision, with no second thinking/revision round. The prompts ask it to portray ordinary novices rather than replace them with an expert optimizer. The time allowance is a fictional student circumstance; this tests model responses to that framing, not a measured reduction in model thinking or validated human behavior.

## Measurements and sample size

| Hypothesis | What is measured |
|---|---|
| H1 | Response to outstanding replenishment: mean order decrease per extra case already on the way; B-A |
| H2 | Total four-role inventory-holding and backlog costs over 24 weeks; B-A |
| H3 | The same replenishment-response measure; C-B |
| H4a | Mean role-level weekly order variance; C-B |
| H4b | Order variance divided by external customer-demand variance; C-B |

The pipeline response is a proxy, not an identified optimal weighting coefficient. All choices come from the model. Per condition, ten chains x four roles x 24 weeks gives 960 weekly orders, plus 320 probe answers. **The inferential sample is ten matched chain comparisons**, not 40 independent students. Each chain/arm has its own fresh context. Fixed main target: 30 contexts; no significance-based stopping or favorable replacement. Two-sided paired tests and Holm correction cover the five endpoints. More observations do not guarantee significance.

**Validation:** 24 software/analysis/preparation tests passed. The progress setup ran in a real .venv Jupyter kernel without widgets. Three development contexts are currently running; the monitor reads their live saved status.

First run one separate A/B/C development block with 24 weeks, 32 probes and 4 quiz items per case. Gate on completion, actual-choice provenance and comprehension, never H1-H4 signs or p-values. Only after the gate and main freeze may the ten held-out blocks launch. Development never enters main tests.

## Run and files

Open the progress notebook, select `D:/beergame/.venv/Scripts/python.exe`, and run its setup cell. It only monitors saved records; the assistant launches isolated contexts. Refresh the report offline:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/report_exp14_framing.py
```

- `data/student_framing_v3/development/` and `main/`: exact prompts, cases, literal model choices, states, transcripts and reviews.
- `analysis/student_framing_v3/tables/`: extracted numeric results.
- `reports/student_framing_v3/`: the current PDF/text report and figures.
- `hypotheses/STUDENT_FRAMING_V3_PLAN.json`: prospective frozen plan; the separate main plan exists only after qualification.

## Preserved earlier work

The earlier strict-clock development remains unchanged at16cases; its [report](reports/REPORT.pdf) describes the failed real-time mechanism. It is not the current student-framing sample. The carry-forward proposal was superseded before any participant run or plan freeze; it is an [archived unused design draft](analysis/design_history/carry_forward_unrun/README.md). The user clarified that time pressure must be a student circumstance in the prompt. No earlier sample is pooled with the new one.

No direct provider API calls or keys are used. Local agents consume the account allowance; the shared API budget remains unchanged. Model/persona observations are not independent real University at Buffalo students.
