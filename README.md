# Beer Game: hypothetical student reasoning-budget study

Start with [notebook 03](notebooks/03_student_reasoning_study.ipynb) or the commands below. The active protocol uses a **hypothetical second-year business student at the University at Buffalo**, the pinned model **gpt-5.4-mini-2026-03-17**, and **reasoning effort high for every call**. The notebook separates calibration from independent games and shows live progress during execution. Historical notebooks 01/02 and their results remain separate.

This study asks whether a constrained computation allowance changes this configured LLM's ordering, costs, and bullwhip amplification. It does not establish effects in real students. API calls and weekly decisions are repeated observations, not independent students. The simulation unit is a four-agent supply-chain game.

The paid pilot is **complete**: two 40-week games, each followed by 12 automatic scoring weeks, with **288 valid model decisions, zero fallbacks and zero zero-orders**. Both diagnostic conditions produced identical orders of 4 or 8 cases and a total scored team cost of **156** each. The corrected calibration's token-manipulation screen **failed**, so this pilot cannot establish a time-pressure, validated token-treatment or human-student effect. Final results, reports and limitations are below. No further paid runs were started.

## Completed pilot results on 11 October 2026

The model and high effort stayed fixed; the predeclared diagnostic allowances were 8,192 and 16,384 generated tokens. One independently initialized chain ran in each condition. Four fixed familiarization weeks preceded 36 model-controlled weeks per game.

| Final measure | 8,192-token diagnostic | 16,384-token diagnostic |
| --- | --- | --- |
| Complete game plus automatic continuation | 40 + 12 weeks | 40 + 12 weeks |
| Valid model decisions | 144 | 144 |
| Missing decisions / fallback orders / zero orders | 0 / 0 / 0 | 0 / 0 / 0 |
| Observed model order quantities | 4 and 8 | 4 and 8 |
| Total scored team cost | 156 | 156 |
| Automatic continuation cost | 0 | 0 |
| Bullwhip ratio versus local demand, every role | 1.000 | 1.000 |
| Usable supply-line coefficient fits | 0 of 4 | 0 of 4 |

Customer-referenced ratios were identical across conditions: retailer **1.000**, wholesaler **1.215278**, distributor **1.416667**, and factory **1.604167**. These ratios reflect delayed responses to a single demand step within a finite measurement window; each role's order variance exactly matched its own incoming-demand variance. They do not demonstrate local behavioral amplification. All eight coefficient fits were unusable because of weak inventory response, boundary estimates or insufficient retailer variation, so no supply-line-neglect claim follows.

Read the final [Markdown report](data/runs/student_api_b609eca42866feb0/REPORT.md), [Word report](data/runs/student_api_b609eca42866feb0/REPORT.docx), [Excel details](data/runs/student_api_b609eca42866feb0/DETAILS.xlsx), and [independent evidence audit](data/runs/student_api_b609eca42866feb0/independent_audit.json). The audit reconstructed all 288 decisions and physical game/tail states without model calls, checked source hashes and saved report tables, and verified unchanged paid checkpoints after recovery.

The final campaign ledger is **$5.19360675** within the authorized $10 maximum: **$2.24484225** for calibration, including **$0.45876525** in excluded old-state charges, plus **$2.94876450** for eight common rules checks and game decisions. Same-campaign imported charges are already included; copying or reusing evidence does not add charges again. There are no pending requests. The two preserved HTTP 429 rejection records have no measured usage and zero charges; all main decisions have measured usage. Completion and identical outcomes describe this configured LLM pilot; one chain per condition, failed manipulation and no real-student validation preclude confirmatory or human-behavior claims.

## Run and review

From PowerShell in `D:\beergame`:

```powershell
python -m venv --system-site-packages .venv
.\.venv\Scripts\python.exe -X utf8 -m pip install -r requirements.txt
$env:PYTHONPATH = 'src'
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 scripts/run_student_reasoning_study.py --mode offline
```

The offline campaign runs the simulator and reports with a simple synthetic demand-following benchmark. It makes no model calls and cannot validate the persona or token treatment. Its report says **SYNTHETIC**. To use the notebook, launch Jupyter from the project environment and select its Python kernel:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m ipykernel install --prefix .venv --name beergame-venv --display-name "Beer Game (.venv)"
.\.venv\Scripts\python.exe -X utf8 -m jupyterlab notebooks/03_student_reasoning_study.ipynb
```

Select **Beer Game (.venv)**. Run setup first. Leave `RUN_CALIBRATION=False` and `RUN_GAMES=False` to review without calls. Set `WATCH_PROGRESS=True` to inspect the latest background run or its completed status. For a future independent game run, use the reusable `CALIBRATION_DIR`, leave `RUN_CALIBRATION=False`, set `RUN_GAMES=True` and `WATCH_PROGRESS=False`, and choose a **new `REPLICATE_ID`**. The default is one chain per condition. This reuses paid calibration without new calibration calls; future game decisions require a separately budgeted API run and masked key entry. Keep the replicate ID unchanged only to resume that same saved game. `MODE='offline'` is a free synthetic check; `MODE='api'` requires a completed real calibration.

After updating the entrypoint or filesystem helper, restart the notebook kernel and rerun setup before continuing. Setup installs the bounded Windows file-save retry. A kernel that imported the earlier modules does not automatically receive this integration. Watching a background run does not resume it; continue the same saved campaign with the matching CLI command in the operational recovery notes below.

The optional calibration cell runs the fixed state bank alone; the separate game cell consumes that saved calibration directory. The HTML bar shows completed steps, API attempts/cache reads, calibration completion, game week, completed chains, fallbacks, and estimated charges/reservations. The same evidence is saved in `progress.json` and linked by `reports/ACTIVE_STUDENT_RUN.json`. A completed request count includes token-incomplete and failed responses; it is not a count of valid decisions.

The calibration bar advances after a batch is saved. The game bar advances after every role's decision for a week finishes and that week is committed. Request counters can change while the week bar stays in place; high-effort generation can keep a week in progress for a while.

Validation on 11 October 2026: **72 offline/mocked tests passed across the 66-test baseline and six focused filesystem tests**. The baseline completed in **65.503 seconds**, covering complete-game conservation, calibration-only execution, saved calibration validation/reuse, cached resume, spending guards, flagged missed decisions, and bounded temporary-rate retries; the [saved test log](reports/software_checks/student_tests_20261011_final.log) records it. The [latest clean filesystem rerun](reports/software_checks/operational_io_20261011.log) took **0.222 seconds**, including a real Windows reader-handle lock that raises errors 5/32. Four additional [preflight checks](reports/software_checks/operational_io_root_preflight.json) passed for transient permissions, persistent permissions, other exceptions and byte-identical saves, with no model calls. The [notebook verification](reports/software_checks/notebook03_saved_calibration_20261011.json) passed six safe code cells, including real saved-calibration loading and progress/helper integration, without API calls. Notebook review and independent offline games executed successfully. Use `-X utf8` on Windows because historical source readers otherwise inherit a GBK encoding. The full free campaign completed six 40-week games and 864 synthetic decisions, with 12 scored continuation weeks per game.

To run real models, use a masked local prompt:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/run_student_reasoning_study.py --mode api --prompt-key-gui
```

Use `--prompt-key` for a hidden terminal prompt instead, or supply `OPENAI_API_KEY` securely through your environment. Never paste a key into chat, save it in a notebook, or pass it as a command argument. The prompt keeps the key in process memory. No calls occur on import or on opening a notebook.

For a calibration-only run, then independent games using its saved results:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/run_student_reasoning_study.py --mode api --prompt-key-gui --calibration-only
$calibrationRun = 'D:\beergame\data\runs\student_api_REPLACE_WITH_SAVED_RUN_ID'
.\.venv\Scripts\python.exe -X utf8 scripts/run_student_reasoning_study.py --mode api --prompt-key-gui --calibration-run $calibrationRun --groups 3 --budget 10
```

Replace the example path with the completed calibration directory printed by the first command. `--calibration-run` starts a separate game run using validated saved calibration without repurchasing it; its local dollar cap excludes earlier calibration charges, which are reported separately. Use a new `--replicate` value for independent additional games. If continuing under a single total campaign allowance, set the game budget to the allowance remaining after calibration. This assistant's combined live campaign includes the earlier $0.920223 in the same authorized $10 ledger. The saved cap selection and cost forecast determine how many pairs can be attempted before any game outcomes exist; the plan remains frozen on resume.

To continue a compatible stopped calibration under the same allowance:

```powershell
$stoppedCalibration = 'D:\beergame\data\runs\student_api_5d4543fe7af6f92f'
.\.venv\Scripts\python.exe -X utf8 scripts/run_student_reasoning_study.py --mode api --prompt-key-gui --calibration-only --resume-calibration $stoppedCalibration --budget 10
```

`--resume-calibration` imports compatible raw checkpoints into a new versioned run and preserves the original directory. Exact rendered prompts, model, effort, schemas, states and caps must match. Previously measured calls are not purchased again, and imported charges remain in the ledger. Unknown pending requests are retained for inspection rather than automatically resent. Use the completed resumed directory with `--calibration-run` for games.

SDK retries remain disabled. The study gateway permits at most **two identical retries** only after a clearly classified temporary HTTP 429 rejection, with a shared 30–60 second cooldown. Quota/billing errors and ambiguous 429 errors stop. Truncation, incorrect rules answers, malformed decisions and undesirable orders do not receive correctness retries or enlarged allowances. Every transport attempt remains in the request ledger.

The safe classifier recognizes the currently documented `slow_down`, `credit_balance_exhausted`, organization/project spend-limit, and organization usage-limit codes. An unknown code remains a stop even when accompanied by a generic rate-limit type. A saved fatal rejection is retained and will stop a normal cached resume; restore account access before an explicitly reviewed recovery attempt. For the older zero-charge HTTP 429 that predates safe code recording, one diagnostic recheck is permitted and saved separately. See [official OpenAI error documentation](https://developers.openai.com/api/docs/guides/error-codes).

`scripts/start_student_study.ps1` opens the masked dialog in a background Python process and writes safe progress/output to `reports/student_live_*.log`. Canceling the dialog makes no calls. Actual progress is recorded in the live run's `progress.json`; reports are generated on completion or a controlled stop.

If Windows blocks `.ps1` execution, use the Python CLI command above; it does not require a PowerShell execution-policy change.

The user authorized a **$10 maximum for the new campaign on 11 October 2026**. The requested maximum is three independent chains per condition, 40 game weeks (four familiarization and 36 model-controlled), plus 12 automatic scored weeks. Calibration has 24 fixed hypothetical states and six allowances: 144 scientific requests. Before onboarding or games, the runner selects up to the requested three chain pairs using calibration token costs, a 15% forecast margin, and common onboarding reservations. It records this plan before observing game outcomes. A smaller planned sample reflects the cost forecast, not a favorable or unfavorable result.

At three pairs, there are 24 factual checks and 864 game decisions, for 1,032 scientific requests including calibration; transport retries can add saved attempts. If the remaining allowance cannot cover one forecast full pair, games stop before purchasing a partial pair. Forecasts do not guarantee final cost, and the spending guard still applies to every call. This is a feasibility pilot; three pairs are not a powered sample-size guarantee. Reservations may stop the campaign below $10. The ledger is not an account balance and excludes older unrelated spending.

The CLI accepts `--weeks`, defaulting to **40** and requiring at least **20** game weeks. This length includes the four familiarization weeks; the twelve automatic scoring weeks follow separately. Choose and record the horizon before game outcomes. If the completed calibration's cost forecast cannot fund one 40-week pair within the original $10 campaign allowance, a **new 20-week feasibility pilot may be planned prospectively** using the remaining allowance. That decision has not been made here. Changing the horizon requires a new run and replicate identity; it must not shorten a game after observing its decisions or costs.

Each run saves `manifest.json`, `progress.json`, exact per-call request/response JSON, `calibration.csv`, the cap recommendation, `selection.json`, `rules_checks.json`, `rounds.csv`, and `continuation.csv`. Reports include Markdown, Word, an Excel workbook, and plots when dependencies are installed. [reports/LATEST_REPORT.txt](reports/LATEST_REPORT.txt) points to the latest report using paths on this machine. Run directories distinguish synthetic and real API evidence. Rerunning the same configuration and unchanged code reads checkpoints without repurchasing completed requests; unknown pending calls require inspection.

## What changed on 11 October 2026

- Every decision uses the same student persona, question format, costs, factual rules, state fields, and compact order schema. The prompt never asks for a bias, a preferred order range, or a bullwhip effect.
- One request produces each order. `max_output_tokens` now limits **all generated tokens**, including hidden reasoning, rather than just a visible preparation memo followed by another reasoning opportunity.
- Fixed high effort replaces disabled reasoning in the new protocol. Requested and returned model IDs, effort, prompt, schema, actual usage, response status, latency, and spending are recorded. Non-reasoning tokens include formatting and are not a precise visible-token count.
- A prospective screen tests 512, 1,024, 2,048, 4,096, and 8,192 tokens against a 16,384-token reference. Caps are chosen by observed answer completion and usage separation, never costs, orders, beta, or significance. No threshold is certified until real calibration is observed. The small state bank has empty histories and approximates game decisions.
- If the manipulation screen fails after the fixed calibration is completed, an explicitly labeled engineering diagnostic uses the **largest candidate allowance and the reference allowance: 8,192/16,384 tokens by default**. This supersedes the earlier proposed 2,048/8,192 diagnostic pair. Its games do not establish a validated token-treatment effect. The rule is fixed before game outcomes; caps are not repeatedly tuned for a desired result.
- A common 180-second technical timeout applies in both conditions. Latency is recorded; it is not a treatment or a conversion to human thinking seconds. Token limits do not separately vary information quantity.
- Factory production and persistent backlog rules are explicit. Zero remains valid and there is no advertised maximum order. Missed/truncated answers receive a prespecified **repeat-the-last-valid-order** continuation, initially 4. Such orders are flagged as mechanical fallbacks and never presented as model decisions. Affected games cannot support clean behavioral inference. An emergency-scale submission stops without clipping.

The [historical audit](docs/HISTORICAL_AUDIT_20261011.md) verifies that the earlier clarified follow-up completed four games with no zero decisions and maxima of 12/8. Earlier nano games had many zeros and extremes, but also completed; a stale progress counter misreported decisions. Completion does not guarantee an identifiable supply-line coefficient. Read [research design notes](docs/RESEARCH_DESIGN_20261011.md) for primary sources, the Davis/18-bias reference, student validation, and inference limits.

### Operational follow-up on 11 October 2026

The first live attempt, preserved at `data/runs/student_api_5d4543fe7af6f92f`, stopped during calibration after an HTTP 429 rejection: 73 saved attempts, 72 with measured token usage, and estimated charges/reservations of **$0.920223**. It made no game decisions and established no validated treatment thresholds. Its [partial report](data/runs/student_api_5d4543fe7af6f92f/REPORT.md) remains evidence of that attempt; a later resumed report must be assessed separately.

The follow-up adds bounded retries for classified temporary rate rejection, calibration-only execution, importing stopped compatible calibration, independent games from saved calibration, cost-based planning of chain pairs, the updated diagnostic caps, and notebook progress. These changes preserve paid evidence and the original campaign allowance. A software check or a partial calibration is not a successful live manipulation check.

The preserved resume at `data/runs/student_api_4f22122e5e340a9f` read all original checkpoints and saved one further rejected request. It stopped with 74 local request records, 72 measured model responses, unchanged estimated spending of $0.920223, and no game decisions. Its [Markdown report](data/runs/student_api_4f22122e5e340a9f/REPORT.md), Word report and Excel details remain evidence of that stopped attempt. Subsequent credit-restoration and state-correction work is recorded below. The notebook validates a saved calibration before asking for a key, and only automatically selects a calibration matching its mode.

## Files and responsibilities

| Path | Purpose |
| --- | --- |
| `src/beergame_study/reasoning_protocol.py` | New persona, config, fixed-high gateway, provenance, fallback, cap selection |
| `src/beergame_study/student_study.py` | Calibration, onboarding, games, and checkpoints |
| `src/beergame_study/student_report.py` | Reports, metrics, beta diagnostics, and plots |
| `src/beergame_study/calibration_artifacts.py` | `make_calibration_snapshot`: validate and copy a completed calibration into a reusable checkpoint without model calls |
| `src/beergame_study/operational_io.py` | Bounded retry for transient Windows file-save permission errors; save operational helper provenance and actual concurrency/interval separately |
| `scripts/run_student_reasoning_study.py` | Explicit offline/API, calibration-only, calibration import/game entrypoint, and secure key prompts |
| `scripts/annotate_student_report.py` | Add operational recovery/accounting context to derived reports and correct the same-campaign imported-charge flag without changing outcomes |
| `notebooks/03_student_reasoning_study.ipynb` | Review/setup, live progress, optional standalone calibration, and separate independent games |
| `src/beergame_study/game.py` | Existing physical simulator, reused without changing rules |
| `tests/` | Offline and mocked-API verification; no paid tests |
| `docs/PROTOCOL.md` | Historical memo-budget protocol |
| `data/runs/`, `data/development/`, `reports/`, `archive/` | Evidence and historical artifacts; preserve them |

## Requirements for future changes

For every later change, update this README with behavior, run instructions, validation, and limitations. Add a dated change entry; keep historical descriptions intact. Record scientific changes in the manifest and source fingerprint so changed prompts/models/efforts/caps/fallbacks/simulators start a new run. Document failed attempts and incomplete runs. Never pool reasoning-none memo runs with the high-effort protocol, count calls as human participants, suppress zero/extreme orders, or select caps using hypothesis results.

Compare a small real-student sample on the same instructions and prespecified states before claiming student fidelity. Use independent full-game chains and a prospective power assessment before confirmatory inference. No setting guarantees a meaningful difference or significant result.


### Credit-restoration recovery on 11 October 2026

The user reported adding sufficient API credit. The recovery option `--recheck-after-access-change` permits one fresh request after a saved zero-charge HTTP 429 only when account access has explicitly changed. It preserves the rejected attempts, uses the same prompt/model/effort/cap, and stops on a fresh quota rejection. It does not resend pending or unknown-usage calls. Use it with `--resume-calibration` for the stopped run; ordinary runs leave it disabled. In notebook 03, set `RESUME_CALIBRATION` and `RECHECK_AFTER_ACCESS_CHANGE=True` after fixing account access. The notebook retains that run's original scientific configuration while resuming.

### Calibration-state correction on 11 October 2026

An independent audit found eight hypothetical calibration states with positive demand and remaining inventory but zero receipts and shipments. These placeholders were inconsistent with the post-shipment observation rules. Before any games, the live process was stopped at an inactive checkpoint with no pending calls; 124 records and $1.53672975 were preserved. The corrected states use `received=shipped=demand` for these eight cases. The 38 old-state records costing $0.45876525 remain in the ledger and archive but are excluded from cap screening. The 84 unchanged measured jobs are reusable; 12 unchanged jobs were still missing, and 48 corrected-state jobs required new calls. This correction can bring total calibration spending above the earlier $1.80–$2 estimate. All spending remains inside the original $10 campaign cap.

`--correct-calibration-states` with `--resume-calibration` authorizes only this declared receipt/shipment repair. The import preserves old record bytes and costs, validates exact original prompts and keys, and reuses only unchanged rendered prompts. Completed corrected calibration can be reused for new games; the loader recognizes explicitly excluded old records and screens only the 144 current-bank observations. Four focused repair tests passed, including rejection of any broader state change before calls. Reports show the correction and retained excluded costs. Notebook recovery uses `CORRECT_CALIBRATION_STATES=True`; ordinary runs leave it disabled. The progress bar displays calibration out of 144 separately from the overall campaign plan.

During recovery, an interim snapshot of `data/runs/student_api_b609eca42866feb0` showed 112 of 144 calibration steps, approximately $2.02 charged or reserved, and zero game decisions. Completed calibration results supersede that interim status and are recorded below. Read the run's current `progress.json` or the notebook watcher for game progress.

### Completed calibration and diagnostic planning on 11 October 2026

The corrected calibration completed all **144 matched state/cap observations**, using the pinned GPT-5.4 Mini snapshot and fixed high effort. Its observed structured-order completion and actual generation were:

| Generated-token allowance | Valid complete orders | Completion rate | Median actual generated tokens |
| --- | --- | --- | --- |
| 512 | 0/24 | 0% | 512 |
| 1,024 | 2/24 | 8.3% | 1,024 |
| 2,048 | 5/24 | 20.8% | 2,048 |
| 4,096 | 11/24 | 45.8% | 4,096 |
| 8,192 | 23/24 | 95.8% | 5,057 |
| 16,384 reference | 24/24 | 100% | 4,413 |

Actual-token medians include the measured incomplete responses. The small caps frequently exhausted generation before a valid order. The prespecified combined completion-and-usage screen found no eligible treatment pair. The observed median at 8,192 was higher than at 16,384, so that comparison did not provide the required 25% reduction in actual generation. Higher allowance alone does not demonstrate more thinking. These 24 states per cap are an observed feasibility screen, not a guarantee for complete games.

The completed calibration ledger is **$2.24484225**, including **$0.45876525** from excluded old-state responses and retained historical attempts. Those responses remain preserved and charged but are excluded from the 144-observation screen. The [calibration report](data/runs/student_api_b609eca42866feb0/calibration_checkpoint/REPORT.md), [screen evidence](data/runs/student_api_b609eca42866feb0/calibration_checkpoint/calibration_recommendation.json), and [state-level observations](data/runs/student_api_b609eca42866feb0/calibration_checkpoint/calibration.csv) provide the results. [reports/LATEST_CALIBRATION.json](reports/LATEST_CALIBRATION.json) points to this reusable checkpoint. Creating it added no calls, costs or observations.

Before game outcomes, the [saved plan](data/runs/student_api_b609eca42866feb0/selection.json) selected **one 40-week chain per condition** at the predeclared diagnostic allowances of 8,192 and 16,384. The forecast cost per pair was **$7.65708435**, fitting the allowance remaining within the original $10 campaign ledger. All [eight common rules checks](data/runs/student_api_b609eca42866feb0/rules_checks.json) passed. The paid pilot stopped during games after a filesystem error, resumed after the separate operational fix and then completed both full games and scoring continuations. The 20-week option remained unused. Final outcomes are recorded at the top of this README; they cannot establish a validated token-treatment, human thinking-time or actual-student effect.

### Reusable calibration checkpoint on 11 October 2026

`make_calibration_snapshot(run_directory)` in [calibration_artifacts.py](src/beergame_study/calibration_artifacts.py) creates `calibration_checkpoint/` inside a run only after all expected state/cap pairs and their saved evidence match a completed calibration. It copies the existing calibration CSV, recommendation, raw request bytes, import provenance and saved implementation; a separate checkpoint manifest and progress record identify the source run. Existing differing evidence is never overwritten. Creating this artifact makes **no API calls** and adds **no spending or independent observations**.

The checkpoint is a reusable calibration artifact separate from the paid game pilot. Use its directory as `CALIBRATION_DIR` in notebook 03 or with `--calibration-run`. Copied requests are the original observations, not another sample; do not add their costs again when combining campaign spending. Preserved records from the old inconsistent states remain archived and charged but excluded from the current-bank screen. A completed calibration can still fail the manipulation screen: making a checkpoint does not certify caps or turn diagnostic games into a validated treatment comparison.

This artifact helper is outside the five frozen scientific sources: `reasoning_protocol.py`, `student_study.py`, `student_report.py`, `game.py`, and `estimation.py`. Packaging reusable evidence does not change their prompts, model, game rules or cap-selection policy. Record helper changes here while preserving the source run and its provenance.

### CLI horizon and key-dialog update on 11 October 2026

The entrypoint now exposes `--weeks` and shows the actual configured `--budget` in its masked key dialog. Configuration is validated before requesting a key. CLI help was checked, and an API-mode request with `--weeks 19` was rejected before key entry or model calls. The five scientific source files remain frozen. This entrypoint change does not select a shorter pilot or establish live calibration or game results.

### Interim report clarification on 11 October 2026

An interim game report and its Word copy were generated while the paid pilot was running. At that week-10 snapshot, 48 valid model decisions were committed and no fallback orders were committed. A temporary note explained that saved decision requests without a valid completed answer could include calls still processing; pending or unmeasured requests are not observed failed model answers. The controlled stop subsequently regenerated the [game report](data/runs/student_api_b609eca42866feb0/REPORT.md), superseding that snapshot and its temporary note. Read individual raw request statuses for their outcomes. The clarification changed only derived report text; raw evidence, progress and the five frozen scientific sources remained unchanged.

The latest [notebook readiness verification](reports/software_checks/notebook03_saved_calibration_20261011.json) passed six safe code cells, loaded the real 144-observation calibration checkpoint, and checked the live progress display. Its rerun after the filesystem integration verified the idempotent helper installation and the callback's actual-config recording. It constructed no API client, made no new campaign calls or file saves, created no operational records, and added no spending. The saved notebook bytes and controls were preserved. This verifies notebook operation, not a successful manipulation or completed game result.

### Windows filesystem recovery on 11 October 2026

The diagnostic campaign stopped at **06:41 UTC**, through committed game week **12**, after `PermissionError` / Windows error 5 while atomically replacing a progress pointer. Windows can reject a replacement while a reader holds the file. That checkpoint had **64 valid committed decisions**, **zero fallback orders**, **zero pending requests**, and **$3.14142525** in estimated charges/reservations; neither game had completed then. The [week-12 audit](data/runs/student_api_b609eca42866feb0/independent_audit_stop_week12.json) preserves that stopped state. Current progress and final reports now show completion.

The separate [operational_io.py](src/beergame_study/operational_io.py) helper retries filesystem `PermissionError` during JSON saves, including atomic replacement, for at most **seven save attempts** and a bounded **1.57-second** total retry delay. Persistent permission errors and other errors still propagate. These are retries of saving files, not model requests. The CLI and notebook setup install the helper and record its saved source copy, hash and actual concurrency/request interval in the run's `operational_io/` directory, separately from scientific provenance. The five scientific sources remain unchanged, so the completed calibration remains compatible.

Resume the same campaign after secure key re-entry with its unchanged scientific configuration:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/run_student_reasoning_study.py --mode api --prompt-key-gui --budget 10 --groups 3 --weeks 40 --replicate student-high-pilot-01 --concurrency 8 --interval 1
```

The requested maximum of three pairs remains the original configuration; the frozen saved plan still selects **one pair**. This operational resume uses concurrency **8** and a **1-second** request interval, replacing the previous **2 / 2 seconds**. It retains the exact prompts, pinned model, high effort, selected caps, 40-week horizon, replicate identity and original $10 ledger. Replaying completed paid checkpoints adds no calls or charges; only missing future decisions require new model requests. For notebook use, restart its kernel and rerun setup to install the filesystem retry; a new independent-game identity would start another run rather than resume this campaign. Notebook setup and execution callbacks now install the helper and record operational provenance; review controls remain `WATCH_PROGRESS=True`, `RUN_CALIBRATION=False`, and `RUN_GAMES=False`.

The masked-key resume process, PID **8068**, launched at **06:49 UTC**. It initially awaited key entry and made no new purchases during that wait. Saved progress at **06:49:35 UTC** then confirmed execution: running through game week **14**, **80 valid committed decisions**, zero fallback orders, and **$3.67660965** in estimated charges/reservations. That record showed **218 cached requests**, confirming reuse of paid checkpoints. This was a dated operational observation, superseded by the final completion below.

### Final completion on 11 October 2026

Saved progress confirmed completion at **06:58:46 UTC**, with **2/2 games**, **288 valid model decisions**, **zero fallbacks**, zero pending requests and a **$5.19360675** campaign ledger. Both 40-week games and their 12-week automatic scoring continuations passed the independent reconstruction audit. All five scientific source hashes matched; pre-resume paid records remained unchanged. Reports were regenerated from completed evidence, and the separate operational recovery note records the state repair, file-save retry and common scheduling change. No additional paid runs were started. Reuse the immutable calibration checkpoint for any prospectively configured future game run; a failed manipulation screen remains failed after game completion.

### Derived report annotation on 11 October 2026

[annotate_student_report.py](scripts/annotate_student_report.py) adds the prepared operational recovery note to Markdown and Word reports and an `Operational_context` sheet to Excel. It also corrects `local_budget_includes_parent_charges` to reflect same-campaign imported charges already included in the local ledger. The generator's original summary is preserved as `report_summary_generated.json`; [report_annotation.json](data/runs/student_api_b609eca42866feb0/report_annotation.json) records the annotation script hash, zero API calls and unchanged numerical outcomes. Scientific sources, raw requests and progress remain unchanged.

After regenerating all derived reports with `build_report`, rerun the annotation because generation can replace its note and accounting flag:

```powershell
$completedRun = 'D:\beergame\data\runs\student_api_b609eca42866feb0'
.\.venv\Scripts\python.exe -X utf8 scripts/annotate_student_report.py $completedRun --note reports/software_checks/student_operational_recovery_note.txt
```

Repeated annotation is idempotent: it does not duplicate the note or context sheet. It changes report context and accounting metadata, preserving result tables and the underlying evidence.
