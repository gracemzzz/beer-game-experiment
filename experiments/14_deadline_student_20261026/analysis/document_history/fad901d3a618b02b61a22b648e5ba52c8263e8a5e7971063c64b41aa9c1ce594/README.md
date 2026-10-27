# Experiment 14 — student Beer Game with measured deadlines

**Start here:** [PDF report](reports/REPORT.pdf) · [Report text](reports/REPORT.md) · [Figures](reports/figures/README.md) · [Live notebook](notebooks/EXPERIMENT_14.ipynb)

**Current result:** development finished at **16 isolated cases**. In the twelve feasibility cases, adequate-time A completed **4/4**, restricted-time B **1/4**, and restricted-time plus education C **0/4**. Seven stopped at enforced deadlines. Both tested wordings failed the registered gate; the main study is **0/10 blocks** and no main H1?H4 p-values exist. The report shows these actual results, not fictional main data. A clarification is pending between student time-pressure framing and actual model response deadlines before a revised study is prepared.

1. **One model:** GPT-6 Astra, extra-high (`xhigh`), in fresh local agent contexts. No direct API requests or keys are used. Local agents consume the account's agent allowance; the shared API ledger is unchanged.
2. **Ten independent chains per condition:** four fictional second-year University at Buffalo business students per chain. One fresh context controls one chain. Match the same forty persona descriptions across the three potential-condition sessions; these are 120 role-condition instances, not 120 independent students.
3. **One submission in every condition:** A has a calibrated longer deadline; B has a shorter deadline; C has the same shorter deadline plus causal education. There is no extra revision pass. Late decisions are recorded as missing and stop that case; no default orders are inserted.
4. **Development first, held-out study second:** the two prompt versions and finite latency/feasibility plan are saved before their model runs. Choose on implementation, completion and comprehension, never on p-values. Main collection stays blocked until qualification passes and the protocol is frozen.

## What gets measured?

| Hypothesis | Simple quantity |
|---|---|
| H1 | How much an order falls when more previously ordered beer is already on the way; compare short versus adequate time. |
| H2 | Total holding and backlog cost across four roles and 24 weeks; compare short versus adequate time. |
| H3 | The same response to outstanding orders; compare causal education versus the matched control under the shorter deadline. |
| H4a | How much each role's weekly orders fluctuate after education. |
| H4b | Order variance divided by external customer-demand variance after education: the bullwhip ratio. |

The pipeline measure is a responsiveness proxy, not an independently identified optimal weight. Extra checks cover backlog response, pair/role differences, constant and zero orders, end inventory/backlog, timing, completion, physical conservation and a post-task knowledge/transfer quiz. Both readings contain exactly 170 words. No human student data are available to validate the personas.

## Is the sample 10 or 40?

Per condition: **10 chains × 4 roles × 24 weeks = 960 weekly orders**, plus 320 probe choices and 40 quiz answers. The independent inferential sample is **10 chains**, because each is generated in its own fresh context. Roles, weeks and questions are repeated measurements. Three conditions produce 2,880 weekly orders if every main game completes.

One shared context generating all ten chains would supply only one joint replication per condition. That is why this design separates the chains. Ten independent matched pairs permit an exact two-sided p-value as low as 0.001953; this mathematical resolution does not guarantee power or significance. Main stopping is fixed at ten assigned blocks, with five outcomes and Holm correction. Development data never enter those tests.

## Where are the files?

- `reports/REPORT.pdf` and `reports/REPORT.md`: current findings and status, always here.
- `reports/figures/`: current figures and their index.
- `prompts/`: the exact two student framings, matched readings and frozen assay/quiz fixtures. Each case also saves its exact combined prompt.
- `data/latency/`, `data/feasibility/`, `data/main/`: original case records, literal responses, timing events and public transcripts. `data/protocols/` holds exact source snapshots.
- `analysis/tables/`: extracted results; `analysis/qualification/`: preserved gate decisions.
- `hypotheses/`: protocol, literature, prospective development plan, calibrated deadline records and, only after qualification, the frozen main plan.
- `notebooks/EXPERIMENT_14.ipynb`: read-only progress and report refresh; no `ipywidgets` dependency.

## Run and review

Open the notebook, select `D:/beergame/.venv/Scripts/python.exe`, and run its setup cell. It refreshes every ten seconds. The assistant launches isolated contexts; the notebook does not create fictional independent calls. Refresh saved-data analysis with:

```powershell
.venv/Scripts/python.exe -X utf8 scripts/report_exp14.py
```

The operational sequence is `prepare_exp14.py` → isolated actor → `audit_exp14_agent.py` plus attributed procedure review → `qualify_exp14.py`. The main preparation command refuses to run until `MAIN_PLAN.json` is qualified and frozen. Never reset a prepared case, edit decisions, overwrite a failed run, or change the clock during a case. Never continue a timed-out case by filling its orders.

Validation: **19 tests passed**, all 16 saved cases replayed with matching public-choice/procedure reviews, and the setup/progress cell executed in a real Jupyter kernel without widgets. [Development validation receipt](analysis/DEVELOPMENT_REVIEW.json). `tests/test_exp14_deadline.py` checks timing boundaries, missingness, atomic transport and exact physics replay; `tests/test_exp14_analysis.py` checks quantitative extraction and inferential gates. Earlier experiment sources and data remain separate and unchanged.

## Important interpretation

The enforced clock measures display-to-payload wall time, including tool and service latency. It does not reveal hidden reasoning tokens or establish subjective human time pressure. Temperature and per-call token limits are not exposed by this local launcher. An instruction to act rushed cannot by itself establish a binding constraint. See [the protocol](hypotheses/PROTOCOL.md) and [primary references](hypotheses/REFERENCES.md).
