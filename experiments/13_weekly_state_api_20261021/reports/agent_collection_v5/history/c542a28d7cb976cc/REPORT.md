# Agent Beer Game results (v5)

1. **10 complete agent contexts received; 6 have passed the recorded procedure review.** Final round still collecting; stop after three complete non-excluded contexts per GPT model. No additional contexts will start.
2. **H1:** No observed difference in any reviewed context. **H3:** No observed difference in any reviewed context.
3. **H2:** Astra: higher costs; Sol: lower costs; Luna: higher costs.
4. **H4a and H4b:** Education effects vary across models and contexts. Negative values mean lower order variance or bullwhip after education.
5. **Read the effect and p-value together.** The tables show signed means, reviewed context counts, raw two-sided p-values and Holm-adjusted p-values.

## H1-H4 trends

| Hypothesis | Observed trend |
|---|---|
| H1: Constraint increases underweighting | No observed difference in any reviewed context. |
| H2: Constraint increases holding + backlog costs | Astra: higher costs; Sol: lower costs; Luna: higher costs. |
| H3: Education reduces underweighting | No observed difference in any reviewed context. |
| H4a: Education reduces individual order variance | Astra: lower order variance; Sol: higher order variance; Luna: higher order variance. |
| H4b: Education reduces bullwhip ratio | Astra: lower bullwhip; Sol: higher bullwhip; Luna: higher bullwhip. |

## Effect sizes and p-values

| Outcome | Model | Reviewed n | Mean difference | 95% bootstrap interval | Raw p | Holm p (20 tests) | Direction |
|---|---|---:|---:|---|---:|---:|---|
| H1 | GPT-6 Astra | 1 | 0 | — | — (n < 2) | — | No difference |
| H1 | GPT-6.1 Sol | 2 | 0 | [0, 0] | 1 | 1 | No difference |
| H1 | GPT-6 Luna | 3 | 0 | [0, 0] | 1 | 1 | No difference |
| H2 | GPT-6 Astra | 1 | 61.88 | — | — (n < 2) | — | Predicted direction |
| H2 | GPT-6.1 Sol | 2 | -13.82 | [-27.65, 0] | 1 | 1 | Opposite direction |
| H2 | GPT-6 Luna | 3 | 6.433 | [0, 11.85] | 0.5 | 1 | Predicted direction |
| H3 | GPT-6 Astra | 1 | 0 | — | — (n < 2) | — | No difference |
| H3 | GPT-6.1 Sol | 2 | 0 | [0, 0] | 1 | 1 | No difference |
| H3 | GPT-6 Luna | 3 | 0 | [0, 0] | 1 | 1 | No difference |
| H4a | GPT-6 Astra | 1 | -29.14 | — | — (n < 2) | — | Predicted direction |
| H4a | GPT-6.1 Sol | 2 | 11.48 | [-0.2473, 23.22] | 1 | 1 | Opposite direction |
| H4a | GPT-6 Luna | 3 | 1.473 | [0, 4.42] | 1 | 1 | Opposite direction |
| H4b | GPT-6 Astra | 1 | -4.481 | — | — (n < 2) | — | Predicted direction |
| H4b | GPT-6.1 Sol | 2 | 1.774 | [-0.03711, 3.586] | 1 | 1 | Opposite direction |
| H4b | GPT-6 Luna | 3 | 0.2148 | [0, 0.6444] | 1 | 1 | Opposite direction |

Here n is reviewed fresh contexts, not chains. Values are condition differences: H1/H2 = B−A; H3/H4 = C−B. Predicted signs are H1 negative, H2 positive, H3 positive, H4a/b negative. H1/H3 use outstanding-order sensitivity as a proxy for underweighting. A zero contrast means no treatment difference in this measurement.

P-values use the preselected two-sided exact paired sign-flip test. With three independent contexts its smallest possible p-value is 0.25. Bootstrap intervals are pointwise and descriptive in this small pilot. Collection ends at the requested three rounds regardless of the p-values.

Absolute sensitivity helps explain the zero H1/H3 contrasts. The table below averages each arm over reviewed contexts. Identical sensitivity across arms leaves no measured effect for the constraint or education. These probe slopes do not establish normative underweighting or validate student behavior.

| Model | A: control + revision | B: control, one decision | C: education, one decision |
|---|---:|---:|---:|
| GPT-6 Astra | 1 | 1 | 1 |
| GPT-6.1 Sol | 1 | 1 | 1 |
| GPT-6 Luna | 0 | 0 | 0 |

## Collection status

| Model | Complete non-excluded contexts | Reviewed for inference | Complete excluded attempts |
|---|---:|---:|---:|
| GPT-6 Astra | 2/3 | 1 | 0 |
| GPT-6.1 Sol | 3/3 | 2 | 0 |
| GPT-6 Luna | 3/3 | 3 | 2 |

**Fifty chains inside one context are dependent.** Additional fresh contexts provide replication; increasing a within-context prefix does not create independent students.
**This tests decision opportunities in fictional students.** It does not establish binding human clock pressure, normative underweighting, or real student behavior.

## Observed H1-H4 differences

| Requested model | Run | H1: B-A sensitivity | H2: B-A cost | H3: C-B sensitivity | H4a: C-B variance | H4b: C-B bullwhip | Review |
|---|---|---:|---:|---:|---:|---:|---|
| GPT-6 Astra | run001 | 0.1425 | 148.2 | -0.001667 | -23.38 | -3.502 | Pending: incomplete orchestration record |
| GPT-6 Astra | run002 | 0 | 61.88 | 0 | -29.14 | -4.481 | Reviewed |
| GPT-6.1 Sol | run001 | 0 | 36.69 | 0 | -12.33 | -1.993 | Pending: incomplete orchestration record |
| GPT-6.1 Sol | run002 | 0 | -27.65 | 0 | 23.22 | 3.586 | Reviewed |
| GPT-6.1 Sol | run003 | 0 | 0 | 0 | -0.2473 | -0.03711 | Reviewed |
| GPT-6 Luna | run001 | 0 | 8.36 | 0 | 0.0209 | 0.003169 | Excluded: Public state fields omitted before decisions |
| GPT-6 Luna | run002 | 0 | 0 | 0 | 0.07625 | 0.01026 | Excluded: Code generated current-page choices |
| GPT-6 Luna | run003 | 0 | 7.45 | 0 | 0 | 0 | Reviewed |
| GPT-6 Luna | run004 | 0 | 11.85 | 0 | 4.42 | 0.6444 | Reviewed |
| GPT-6 Luna | run005 | 0 | 0 | 0 | 0 | 0 | Reviewed |

Expected directions are H1 negative, H2 positive, H3 positive, and H4a/b negative. A difference in that direction alone is not significance. H1/H3 use pipeline sensitivity as a proxy.

## Open these files

- [Current presentation figures, PDF/SVG exports and short captions](slides_current/README.md).
- [Short extracted hypothesis conclusions](hypothesis_conclusions.csv).
- [Live notebook](../../notebooks/AGENT_PROGRESS.ipynb): run all cells and tick Auto-refresh (10 s).
- [Per-context / condition results](context_arm_results.csv) and [per-chain extracted results](per_chain_results.csv).
- [Current reviewed-context estimates, intervals and adjusted p-values](current_context_inference.csv). Missing p-values mean replication or review is insufficient.
- [Within-context size table](within_context_chain_prefixes.csv): first 5/10/20/30/40/50 chains, descriptive only.
- [Fresh-context size table](observed_context_size_sweep.csv): original attempted prefixes 1/2/5/10 plus observed time-cutoff sizes; eligible counts and missingness remain explicit.
- [H1-H4 versus chain-count plot and data](chain_size_stability/README.md): observed direction stability within contexts.
- [Exact tasks, prompts, decisions and public trace reviews](../../data/assistant_v5_20261025/).

![Observed contrasts](DESCRIPTIVE_H1_H4.png)

## Collection and limits

Requested agent models are GPT-6 Astra, GPT-6.1 Sol and GPT-6 Luna, all high effort. Client model labels/settings are recorded separately from provider authentication. These agent observations are not pooled with manual website or historical API data. Claude is still a manual route.

A has a matched control reading plus a separate revision opportunity; B has the control reading and one committed decision; C has causal education and one decision. All three arms share a context, allowing carryover. Python computes state; the model supplies literal order pages. Full games replay before extraction. A code execution log does not by itself prove prompt adherence.

Procedure review covers visible prompts and tool interactions, complete public state exposure, and actual literal decisions. Encrypted parent-message bodies are covered only where exact operator-saved plaintext receipts exist; these are operator attestations, not decrypted or independently authenticated provider transcripts. Missing receipts remain explicit review gaps. This review does not validate student fidelity or clock pressure. Deviating attempts are preserved and do not disappear from the attempted sample.

When eligible replication exists, the exploratory tests use paired context differences, two-sided sign flips and pointwise bootstrap intervals. The Holm family retains all 20 model-by-endpoint tests, including missing Claude tests. These assumptions do not make model contexts equivalent to real human samples. Repeated live looks are not a stopping rule.

No new direct API calls are made by this monitor, analysis or local transport. The shared API ledger is unchanged; agent-service usage is separate.

Report generated UTC: 2026-10-26T02:43:06.414765+00:00. Evidence ID: `c542a28d7cb976cc`. Earlier current-report bytes are preserved in `history/` before changed evidence is published.
