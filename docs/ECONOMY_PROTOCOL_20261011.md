# Under-$3 amendment: GPT-6 Luna, fixed high effort

Declared on 11 October 2026 after the user requested a total redesign cost below $3, before any Luna outcomes. Protocol: `student-high-economy-revision-v3`. Read the earlier [complete v2 design](ANYTIME_PROTOCOL_20261011.md) for the unchanged game, demand, profiles, treatment, measurements and inference assumptions. This is a separate model experiment; Mini evidence is not pooled with it.

The earlier Mini calibration cost $0.7198179. All 16 initial choices completed, but two of eight held-out revisions exhausted their token ceilings, so its completion screen failed. No Mini games were bought. The new model choice responds to the user's price constraint; it was not chosen for a favorable bullwhip result.

## What changes

- Fixed API model ID `gpt-6-luna`, with `reasoning.effort=high` in every phase and condition. Both requested and returned IDs are retained and must match. Official documentation publishes no dated snapshot for this model; later alias drift limits exact long-term reproducibility.
- Explicit `service_tier='flex'`. No automatic switch to standard/premium pricing or another model. Flex can be slower and occasionally unavailable. Temperature and top-p remain omitted. The same 900-second technical timeout applies to both conditions.
- Official Flex prices per million tokens: ordinary input $0.05, cached input $0.005, cache writes $0.0625, output $0.25. The ledger conservatively counts every uncached input token at $0.0625 to cover cache writes. It is an upper estimate, not a provider invoice. [Official model and pricing documentation](https://developers.openai.com/api/docs/models/gpt-6-luna).
- New-run hard cap $2.20. Including the already-spent Mini calibration, this attempt can cost at most $2.9198179. A shared campaign guard also limits all v2/v3 redesign calls together to $2.95 and preserves the original $10 campaign ceiling including the historical $5.19360675.
- A pre-request input-accounting bound of 32,768 tokens (conservatively estimated from serialized UTF-8 bytes plus 2,048 overhead) stops oversized requests before payment. No history is trimmed. The 24-week paired pilot, calibration and probes fit a conservative 300-billable-request cost envelope of $1.630208 when every call reaches its output and input allowance. This calculation assumes documented Flex pricing and excludes taxes and unrelated account activity; the request-level cost guard remains in force.

The first four development cases are a quick check: valid initial submissions, at least three valid revisions, positive reasoning use and median initial/combined generation at most 0.75. Failure stops before further calls. The full calibration has its own **$0.18** guard; a completion or headroom gate that has already become impossible stops immediately. These are validity/usage rules, never order or hypothesis-direction filters. Technical reservations use standard prices to cover unknown outcomes; actual eligible responses use Flex accounting. Recognized capacity rejections can retry at Flex rates only, with no charge for rejected requests. [Flex documentation](https://developers.openai.com/api/docs/guides/flex-processing).

No paid Luna calls occurred during either cost amendment. The earlier standard-tier v3 prototype was tested offline only and is superseded by this prospective Flex configuration. Its raw software evidence remains separate.

## What remains fixed

Four fictional UB student profiles; matched profile-role assignments; separate decentralized role decisions; common question and physical rules; 4 practice plus 20 model weeks; known iid integer demand 0 through 8; 12 automatic scoring weeks; initial ceiling 16,384 and revision ceiling 8,192. No change to valid zero orders, no forced bias, no correction of undesired choices, and no outcome-based sample changes.

Fresh Luna calibration uses the same 8 development and 8 held-out state/history cases. Mini calibration cannot certify another model. Both splits must pass the existing initial-completion, revision-completion, reasoning-use, headroom and actual-generation-separation checks. Failure saves a report and buys no games. Passing calibration then permits the same rules checks, matched supply-line probes and one paired chain pilot.

The primary bullwhip outcome, cost outcome, revised H1 supply-line-sensitivity assay, exploratory original beta and inference eligibility remain as specified in v2. One pair provides descriptive feasibility evidence; it cannot provide a powered hypothesis test or validate actual student behavior. The token treatment measures an extra reconsideration opportunity, not pure information overload or human time.

## Run and audit

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/run_economy_study.py --mode offline --weeks 24 --replicate economy-software-check
.\.venv\Scripts\python.exe -X utf8 scripts/run_economy_study.py --mode api --weeks 24 --pairs 1 --budget 2.20 --replicate economy-pilot-01 --prompt-key-gui
```

Opening notebook 04 makes no paid calls. Its progress watcher uses `reports/ACTIVE_ECONOMY_RUN.json`. Reports go to `reports/economy_<mode>_<fingerprint>/`, with raw evidence and frozen sources under `data/runs/`. Completed compatible Luna calibration and exact request checkpoints can be reused. Changing a campaign ID is not authorization for additional spending.

`scripts/audit_anytime_run.py --run <saved-run>` audits either v2 or v3 without API calls. The v2 scientific files remain byte-identical to their saved run; v3 has its own source snapshots, fingerprint, rates, report pointer and tests.
