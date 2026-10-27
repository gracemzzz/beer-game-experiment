# Beer Game agent handoff ? experiment 14

Read [Experiment 14](experiments/14_deadline_student_20261026/README.md) first. User requests H1?H4 using GPT-6 Astra / extra-high local agents, ten four-role chains per condition, clear statistical measurements and easy-to-find outputs. Do not promise significance or tune/replace samples for p-values.

## Current result

All 16 development contexts finished: 4 unlimited latency references, 12 four-week feasibility cases (two wording versions ? two blocks ? A/B/C). Adequate A completed4/4; restricted B1/4; restricted+education C0/4. Seven strict-deadline cases stopped; all accepted prefixes, missing measurements and failures are preserved. Both registered completion gates fail. Main is0/10 blocks; no MAIN_PLAN.json exists. Do not launch main, extend a running deadline, impute orders or infer H1?H4 from development completers.

A/B/C mean adequate time+matched control reading, restricted time+control, restricted time+causal education. Both readings have170 words. Same xhigh setting; launcher exposes no temperature/token cap. Clock measures complete-payload admission after public state display, including service latency. It does not measure hidden reasoning or human pressure. V1 restricted game4.0s/probes3.8s; V2 game5.8s/probes3.8s. Adequate30s in both phases. These were calibrated prospectively from unlimited reference latencies, not outcome effects.

## Pending decision

A text question was sent asking whether the intended next study is student time-pressure **framing** or **actual enforced response deadlines**. Do not assume a reply. A new design needs new prospective version/fingerprint and must preserve the16 strict-deadline development records. Neither framing nor larger N guarantees hypothesis support. Keep valid effects and p-values, including null/opposite findings.

## Files and reproduction

- [Current PDF](experiments/14_deadline_student_20261026/reports/REPORT.pdf), [text](experiments/14_deadline_student_20261026/reports/REPORT.md), [figures](experiments/14_deadline_student_20261026/reports/figures/README.md), [notebook](experiments/14_deadline_student_20261026/notebooks/EXPERIMENT_14.ipynb).
- Frozen game/transport: `src/beergame_study/exp14_deadline.py`, `scripts/run_exp14_agent.py`; do not patch after these cases. Exact material hashes and source snapshots live with exp14.
- Preparation/gates: `scripts/prepare_exp14.py`, `scripts/qualify_exp14.py`. Public projection/audit: `scripts/audit_exp14_agent.py`.
- Report: `src/beergame_study/exp14_analysis.py`, `scripts/report_exp14.py`; tests `tests/test_exp14_deadline.py` and `tests/test_exp14_analysis.py` (19 expected). Use `.venv/Scripts/python.exe` explicitly; another default Python lacks PDF dependencies.
- Report rebuild: `.venv/Scripts/python.exe -X utf8 scripts/report_exp14.py`. Notebook/monitor is read-only, no widgets needed, no agent/API launching.
- Each case saves CASE/EXACT_PROMPT/RESULT/STATUS, immutable timing events, public transcript and attributed adherence review. All16 public traces match literal accepted choices and replay. Reviews are operator-attested, not provider authentication. Never export hidden reasoning/system/developer messages.
- Inference target:10 independent matched chain contrasts, not40 students/960 orders. Per main arm960weeklyorders+320probes+40quizitems. H1/H3 equal-weight mean pipeline-pair slopes; H2 full24wk4role cost; H4a role-mean order variance; H4b role-mean order/demand variance. Holm family5; fixed sample, no significant-crossing stopping.

No direct provider API use in14. Shared API ledger remains experiment12, spending$1.179072025 of$5, SHA256 `81f75f9fb53f87f3ef979b11f086a7ac787c15c2cf6d9b2e8acb69f6a0efa7c3`. Local agents use the account allowance. Experiment13 is closed and unchanged.

Earlier detailed handoff preserved verbatim: [historical handoff](experiments/14_deadline_student_20261026/analysis/navigation_history/f95f0215378e251a754b5932b25c58be109d0e0b31e5d1f979fdb846d2c85e92/AGENT_HANDOFF.md).
