# Beer Game: current findings and revised-study review

1. **The latest four-model game completed:** 104/104 accepted responses and 7,680 main decisions. It was a pressure-wording feasibility study, not a binding-time experiment.
2. **It does not verify H1–H4.** H1 is a pipeline-response proxy, H2 contrasts are mixed/zero, and education groups for H3/H4 were absent. The new H4 is order variance/bullwhip, not the earlier cost hypothesis.
3. **More independently generated runs can improve precision; more names inside one response cannot establish independent significance.** The new analysis prepares fixed 10/20/40-block sweeps with paired effects, uncertainty and multiplicity correction.
4. **The free revised-prompt check did not establish a reliable treatment effect.** All eight isolated-assistant replies were usable; both reconsideration replies stayed unchanged. The two development-block comparisons were mixed. No prompt was selected because it became significant.
5. **No new paid calls were made during this review.** Shared charges remain $1.179072025; $3.820927975 remains under the SAME cumulative $5 cap. The stronger four-model main study is not funded or collected.
6. **The new manual controller completed a free end-to-end technical check:** two chains, all 24 weeks, 192 weekly orders and 32 probes, with full replay passing. It is a one-arm assistant demonstration, not a hypothesis comparison or provider-verified website sample. [Evidence](SELF_CHECK.md#additional-manual-controller-technical-check).

**Latest user decision: keep the $5 maximum and use website prompts.** The active new workflow is [five simple website steps](WEBSITE_STEPS.md), [exact prompts and helper](../../prompts/WEBSITE_START_HERE.md), and the [manual notebook](../../notebooks/MANUAL_WEBSITE.ipynb). One code-enabled chat handles ten chains; Python maintains state and the model chooses weekly orders. It makes no repository API calls. Three pilot chats must be reviewed before main collection. No website main results have been received for this version. The v2 API cost discussion below is retained to explain why it was not launched.

## Observed results

Frozen run: `weekly_api_c64d75aa3a03356f`; [original publication](../history/b34972b65bf5/REPORT.md); [original extracted tables](../../analysis/weekly_api_c64d75aa3a03356f/b34972b65bf5/).

| Model actually collected | Strong − no pressure: pipeline sensitivity | Strong − no pressure: mean 24-week chain cost | Orders differing between matched arms |
| --- | ---: | ---: | ---: |
| GPT-6 Luna | 0 | 0 | 0/960 |
| GPT-5.6 Luna | −0.008333 | +17.85 | 53/960 |
| GPT-5.6 Sol | 0 | 0 | 0/960 |
| Claude Haiku 5.5 | −0.014583 | −19.40 | 10/960 |

Each model jointly generated 20 chains over 24 weeks: ten chains/condition and four roles/chain. Both pressure conditions had identical generation settings. There was no enforced or measured difference in decision time, token allowance or reasoning resources. OpenAI requested reasoning `none`; Claude thinking was disabled with low effort. These were the saved settings, not high effort. Pilot and probe choices are separate from the 7,680 main decisions.

GPT-5.6 Luna follows both descriptive proxy directions. Claude's cost contrast goes against H2. Exact zero contrasts for the other two models are legitimate completed observations. No model is discarded or rerun because of these signs. Differences in the H1 assay do not identify normative underweighting; general insensitivity and boundary effects remain possible.

The 20 chains share one response per week, including both conditions. The 24 weeks evolve one dependent stream per model. Student/chain/week counts therefore do not provide independent inferential sample sizes. This report adds no p-values or inferential confidence intervals to those data.

## H1–H4 status

| User hypothesis | What is available now | Conclusion |
| --- | --- | --- |
| H1: binding time increases outstanding-order underweighting | Imagined pressure and pipeline sensitivity | Literal hypothesis unverified |
| H2: binding time increases cumulative holding/backlog cost | Complete 24-week costs; mixed/zero framing contrasts | Literal hypothesis unverified |
| H3: causal education reduces underweighting under binding time | No education arm in latest API sample | Untested here |
| H4a/b: causal education reduces order variation/bullwhip under binding time | Order paths exist, but no education/control comparison | Untested here |

Earlier education/deadline studies are separate samples with different protocols. The completed Astra website collection had only two whole-cohort generations per arm and fictional deadlines. It cannot be relabeled as this four-model test, and its historical H4 cost outcome must not replace the new variance/bullwhip H4.

## Figures for the presentation

[Open the figures and short copyable captions](FIGURE_CAPTIONS.md). All four figure sets are supplied in PNG, PDF and SVG, with underlying CSV values and a hash receipt. The original presentation remains unchanged.

- [Ready-to-insert 16:9 results slide, PDF](figures/04_presentation_results_slide.pdf).
- [Four observed models, PNG](figures/01_observed_model_comparison.png).
- [Observed 10 versus 20 total chains, PNG](figures/02_observed_10_vs_20_chains.png): a descriptive prefix comparison only.
- [Prospective 10/20/40 independent-block power, PNG](figures/03_prospective_power_assumptions.png): a separate planning calculation, not new observations.

For illustration, with a true standardized paired effect of 0.5 and a within-model five-endpoint threshold of .01, the planning approximation gives about **10%, 30%, 67% power** at 10, 20 and 40 independent blocks. A larger sample improves sensitivity to a real effect; it cannot create an absent effect. The curves assume normal independent paired contrasts and use a paired-t calculation; the planned robust sign-flip analysis and twenty-endpoint cross-model correction need their own prospective power assessment. These are not guarantees or estimates inferred from the existing coupled chains.

## Revised design prepared

[Protocol](../../hypotheses/PIVOT_V2_20261025.md) · [New notebook](../../notebooks/PIVOT_V2.ipynb) · [Free self-check](SELF_CHECK.md).

The prepared models are **GPT-6 Luna, GPT-6.1 Sol, GPT-6 Astra and Claude Sonnet 5.5**, covering economy, balanced and flagship GPT tiers plus a stronger Claude model. All request high effort, use no temperature override and allow 8,192 total output tokens including hidden reasoning. This allowance protects complete structured decisions; it is not a hurried-condition manipulation. These settings are proposals checked against official documentation, not a claim that account access or task efficacy has been established. [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra), [Sonnet](https://platform.claude.com/docs/en/models/sonnet-5-5/overview).

Three arms receive adequate opportunity/control, restricted opportunity/control, or restricted opportunity/causal education. A gets one additional reconsideration call; B/C commit their first valid response. Python calculates the physical game and requests decisions one week at a time. Each arm/block has a separate request stream. Generated chains batched within a stream are averaged before inference.

**Construct limit:** this is a real restriction on reconsideration opportunities, not calibrated clock time. It can test an AI resource analogue of the hypotheses. A literal binding-deadline claim requires another prospectively calibrated manipulation. A lecture or student persona does not make LLM decisions validated human behavior. Stronger models may already understand the mechanism, leaving little measurable education effect.

With one chain/arm/block, 10/20/40 independent three-arm blocks mean **30/60/120 chains per model**, or **120/240/480 across four models**. The full fixed maximum is chosen before held-out data; prefix plots do not license stopping at the first small p-value. The inference module tests five directional endpoints using paired two-sided tests, Holm correction and block bootstrap estimates, while preserving opposite/null outcomes and missing pairs.

## Cost and the next collection

The existing ledger is [experiment 12's ledger](../../../12_pressure_framing_api_20261020/data/api_budget.json). Experiment 12 used $0.3404859 and experiment 13 used $0.838586125. Every new attempt must use that same ledger and exclusive lock. No cap was increased.

The new notebook computes exact technical-pilot reservations and whole-study scenarios from the frozen payload/rates. A bounded four-call **format pilot** can fit the remaining authorization; its local maximum is $1.50. It jointly includes three cases per model and therefore provides no independent treatment inference. The free self-check has not shown reliable effects, so a format pilot should not be purchased with an expectation of significant H1–H4 results.

An independent 24-week three-arm block needs **100 calls/model**, including A's extra opportunity and probes. Four models with 10/20/40 blocks require **4,000/8,000/16,000 calls**. Under illustrative no-cache, 2,000-input-token assumptions, consuming a 2,048-output allowance costs about **$178.63/$357.27/$714.54**; consuming 8,192 costs about **$611.79/$1,223.57/$2,447.14**. These are cost-at-cap scenarios, not predicted bills; a 2,048 cap has not been validated for high-effort completion. The runner's full input-byte bound is more conservative still. It blocks an unfunded fixed sample before making a main request.

To reduce cost, batch chains within a replication, return only compact orders, and reuse a stable instruction prefix where provider caching applies. Independence is counted at the shared response stream, so batching does not turn one response into many independent replications. The completed sample reported zero cache hits. Caching and provider batch discounts can help but cannot turn the stated stronger four-model independent design into a guaranteed $3.82 study. A policy generated once and replayed many times would be a synthetic policy simulation, a different study from repeated LLM decisions. [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching), [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing).

## Validation and preservation

The read-only audit independently reconciled all 104 original accepted/raw responses, exact frozen payloads, usage-based charges and all **7,680 Python game states** against the saved tables. No original response, publication, game source or ledger was edited.

The original strict `audit_saved()` still rejects the canonical `game.py` hash because current LF/CRLF bytes differ from its frozen snapshot; normalized source is identical. This review does not claim a successful canonical strict audit. Historical byte recovery belongs only in a separate, hash-proven derived copy.

The repository migration verifier also currently fails: 39,550/39,589 mapped files match exactly, none are missing, and all 39 mismatches are hash-proved line-ending differences in retained root/shared files. No unexplained content differences were found and no canonical bytes were repaired. This is a separate check from the older historical baseline. [Recheck receipt](../../analysis/review_20261025/MIGRATION_RECHECK.json).

The bounded historical weekly suite ran **30 tests: 28 passed, one Windows-path assertion failed, one GBK decoding error occurred**. These portability problems were recorded, not patched in frozen files. New v2 tests are separate synthetic software controls; final check details are in [VALIDATION.json](VALIDATION.json). Default notebook execution makes no API calls and verifies that shared spending remains unchanged.

## Reproduce

Open the new notebook and restart its kernel. Keep `RUN_API=False` for free review. The hidden fields and four-slot progress bar appear only if you explicitly turn on the optional technical pilot. Progress includes the current request, elapsed seconds and cumulative shared spending.

From the repository root, offline checks and figure generation are:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_*pivot*v2.py' -v
.venv/Scripts/python.exe scripts/plot_weekly_review_20261025.py
```

For a future validated block-outcome CSV and its corresponding frozen inference plan:

```powershell
.venv/Scripts/python.exe scripts/analyze_pivot_v2.py --plan PLAN.json --input block_outcomes.csv --output NEW_ANALYSIS_FOLDER
```

That analysis checks outcome structure and supplied receipt hashes; it does not itself authenticate API lineage or replay physical states. Use the transport audit and game replay before interpreting exported observations. Development and synthetic controls are excluded from held-out findings.
