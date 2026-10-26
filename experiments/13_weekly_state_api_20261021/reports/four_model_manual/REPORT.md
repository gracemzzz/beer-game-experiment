# H1–H4: four-model manual collection

1. Reviewed fresh-chat batches: {'gpt_astra': 0, 'gpt_sol': 0, 'gpt_luna': 0, 'claude_sonnet': 0}. Target: 40 per model; 10 chains per condition per chat.
2. No H1–H4 verification can be claimed from a single batch or an uncollected sample.
3. Observed sweeps use only returned, replayed, transcript-reviewed batches; planning curves use stated hypothetical effects.
4. This simplified design shares all conditions in one context. It tests joint-context AI responses, with possible education carryover; it cannot establish human time-pressure or isolated education effects.

## Where the hypotheses are measured

| Hypothesis | Measurement | Contrast / predicted sign |
|---|---|---|
| H1 | Pipeline-response sensitivity (proxy for outstanding-order use) | B − A < 0 |
| H2 | 24-week holding + backlog cost per chain | B − A > 0 |
| H3 | Pipeline-response sensitivity | C − B > 0 |
| H4a | Mean individual weekly order variance | C − B < 0 |
| H4b | Mean order variance / external demand variance | C − B < 0 |

A = control reading + extra review. B = control + initial committed. C = causal education + initial committed.

[Sample-size planning](SAMPLE_SIZE_PLANNING.png) · [Assumed required samples](required_samples_assuming_effect.csv) · [Extracted results](extracted_results.csv) · [Observed sweep table](observed_sample_size_sweep.csv)

No elapsed human deadline is enforced. Sensitivity is not an identified underweighting coefficient. A model can rationally produce no difference. Within-chat chains, weeks and roles are not independent observations.

Inference is exploratory and conditional on independent fresh chats and symmetric paired differences. Two-sided paired sign flips and Holm correction retain all 20 model/endpoints. Prefixes 1/2/5/10/20/40 are descriptive; no stopping at first significance. A single batch has no inferential p-value or interval. Full-sample inference is planned at 40 chats per model. Pointwise bootstrap intervals are not simultaneous intervals.

Planning assumes normally distributed paired chat differences and d = mean difference / between-chat SD. It uses a paired-t approximation and conservative alpha .05/20; it is not a power guarantee for the sign-flip test. Zero true effect has no sample size that produces reliable support. The old pilot does not estimate the new design's between-chat variance.

Methods: [SciPy noncentral t](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nct.html).

No new model responses have been collected for this version. An observed significance curve will appear after eligible results arrive.
