# Claude replication amendment, 11 October 2026

Declared before any Claude responses. The user authorized trying a Claude model and choosing the replication count while retaining a $3 cutoff. Conservatively, the cutoff includes the $0.7877313225 already spent on Mini/Luna redesign calls. The historical $5.19360675 pilot stays separately included in the original $10 campaign.

Protocol `student-high-claude-revision-v4` uses the direct Anthropic API and model `claude-haiku-5-5`, `thinking={"type":"adaptive","display":"omitted"}`, and `output_config.effort="high"` in every call. No temperature, top-p or top-k is sent. The same 900-second technical timeout applies to both conditions. This is a new model experiment; GPT calibration and game observations are not pooled into it.

Anthropic lists Haiku 5.5 at $0.10 input / $0.50 output per million tokens below 100,000 input tokens, with high effort available. Sonnet 5.5 costs $2 / $10 per million, leaving much less replication within this budget. Haiku is selected for feasible replication, not for an expected hypothesis direction. Its dateless model ID is a pinned release under Anthropic's versioning; serving infrastructure can still change.

Sources checked 11 October 2026: [Haiku model](https://platform.claude.com/docs/en/models/haiku-5-5/overview), [prices](https://platform.claude.com/docs/en/about-claude/pricing), [effort](https://platform.claude.com/docs/en/build-with-claude/effort), [thinking](https://platform.claude.com/docs/en/build-with-claude/thinking), [model versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions), [Messages API](https://platform.claude.com/docs/en/api/messages/create), [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs). Installed SDK: anthropic 1.13.0.

## Unchanged experimental design

Read [the full revision design](ANYTIME_PROTOCOL_20261011.md) and [literature review](../reports/revised_design_20261011/REPORT.md). The common prompt, four fictional profiles, role rotation, simulator, demand distribution, scenario bank, matched probes, question and hypothesis definitions are unchanged. Each game has four practice weeks, 20 model weeks and 12 automatic scoring weeks. Future demand draws and the last decision week remain hidden. Short submits its initial choice (16,384-token ceiling); adequate receives one additional high-effort revision (8,192-token ceiling). Both phases count toward computation.

No forced positive/interior orders, preferred maximum, bias direction, order correction or significance-based retuning. Failed initial choices or technical errors stop; only a token-exhausted revision retains its valid same-state initial submission. Exact matching initial prompts share one draw within a paired week/role, never across blocks. The one-pair GPT pilot remains separate descriptive evidence.

The primary H3 predicts higher chain-average customer-referenced order variance under short deliberation. H2 predicts higher total simulated cost, including the disclosed automatic continuation; its phase breakdown must be shown. Revised H1 predicts lower matched-state pipeline sensitivity; original structural beta remains an exploratory usability check. Information load is not independently manipulated, extra revision also changes reconsideration opportunity, and no student observations validate these fictional profiles.

## Calibration, sample and inference

The four-case quick check precedes the full eight-development/eight-held-out calibration. The same completion, positive measured reasoning, headroom and median initial/combined generation ratio at most 0.75 gates apply. Claude's official `output_tokens_details.thinking_tokens` reports retokenized reasoning; `output_tokens` is the inclusive billed total. Both raw and normalized usage are preserved. Missing reasoning measurement fails validation; it is not inferred from a visible thinking summary. Token counts are not an equal-computation scale across providers.

The prospective target is **eight paired blocks (16 chains)**. This gives balanced profile-role coverage twice and reaches the existing inference reporting floor. It is a budget-constrained exploratory replication, not a justified adequate-power or guaranteed-significance claim. The sample, all demand paths and assignments are frozen before game outcomes. If calibration fails or the complete requested sample's forecast exceeds the remaining run budget, no games are purchased. A subsequent smaller design can only be chosen before its own outcomes and with a separate fingerprint; no outcome-based extension is allowed.

The existing paired t tests, 95% intervals and fixed three-test Holm adjustment apply only if the full requested sample completes and computational checks pass. Inspect block differences and distribution assumptions. Weekly calls and roles are not independent students. Do not pool Claude and GPT draws as repetitions of one model, or infer a model-by-treatment interaction from one GPT pair versus multiple Claude pairs.

## Spending and provider adaptation

New-run hard cap **$2.15** and calibration cap **$0.18**. All v2/v3/v4 redesigned runs together are capped at **$2.95**, below the user's $3 cutoff. This new run plus existing redesign spending is bounded at $2.9377313225. The original $10 campaign guard and shared exclusive campaign lock remain. Unknown outcomes retain their reservation; completed requests are never repurchased. Recognized ungenerated rate rejections can retry twice; no model or premium-tier fallback occurs. No secrets are saved in arguments, files, reports or logs.

Requests explicitly use `service_tier="standard_only"` and `inference_geo="global"`. The common system prefix has a five-minute cache marker. Anthropic ordinary inputs, cache reads and cache writes are disjoint usage categories; normalization sums them for total input and prices each category separately. Rates per million: ordinary .10, five-minute write .125, one-hour write .20, cached read .01, output .50. Reservations assume no cache hits and cover one-hour writes. Serialized input size plus overhead must fit the 32,768-token accounting bound. A worst-case full eight-pair token envelope exceeds the budget, so the per-request guard may still stop a run if usage grows beyond the calibration forecast. A stop creates a partial report, not fabricated completion.

The model-visible common prompt is unchanged. Anthropic receives it in its native `system` field and receives JSON schema in `output_config.format`. Numeric `minimum` is removed from the provider grammar because that constraint is unsupported; the unchanged prompt and local validator still require a nonnegative integer. Original schema, exact provider payload, response, selected request ID, configuration and source snapshots are retained. This translation is a documented provider difference.

## Run and monitor

Use [notebook 05](../notebooks/05_claude_deliberation_study.ipynb), all run flags off by default. `WATCH_RUNNING=True` watches `reports/ACTIVE_CLAUDE_RUN.json` without API calls; notebook-started games display progress automatically. Enter `ANTHROPIC_API_KEY` through the masked prompt or environment only. The user confirmed direct Anthropic access before any Claude purchase.

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/run_claude_study.py --mode offline --pairs 1 --replicate claude-software-check
.\.venv\Scripts\python.exe -X utf8 scripts/run_claude_study.py --mode api --weeks 24 --pairs 8 --budget 2.15 --replicate claude-replication-01 --prompt-key-gui
```

Reports use `reports/claude_<mode>_<fingerprint>/`; raw evidence uses `data/runs/`. `LATEST_CLAUDE_REPORT.json` identifies the latest Claude report; a synthetic report does not replace the latest paid-report text pointer. Historical GPT scientific files and raw evidence are preserved.

The Luna CLI and notebook 04 now call an operational wrapper in `shared_budget.py`, so they also count Claude charges under the same lock. The original Luna scientific files and calibration hashes are unchanged. New Luna API runs record the wrapper's source and spending policy separately; completed runs return untouched. Calling archived library entry points directly bypasses this newer cross-provider wrapper; use the maintained CLI/notebooks for paid work.
