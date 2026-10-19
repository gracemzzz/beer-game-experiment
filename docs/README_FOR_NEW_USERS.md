# Beer Game study: a step-by-step guide for a new user and their agent

Prepared 18 October 2026. Share this file **with the project source code**. The final-results ZIP alone cannot run a new experiment. Do not share API keys, `.env` files or the old `.venv` folder.

## Current research question

The owner now specifies four hypotheses: decision-time effects on underweighting and cost (H1/H2), and causal-education effects under binding time (H3/H4). [Exact hypotheses and required design](HYPOTHESES_H1_H4.md). The existing API/manual recipes below describe the historical protocols: they did not collect education/control lecture groups or validate the manual deadline as binding. A new study for all four hypotheses must add those design elements prospectively; do not treat the old bullwhip outcome as education H3.

## 1. Choose the workflow

| | API workflow | Manual copy/paste workflow |
| --- | --- | --- |
| What the model produces | One role's current-week order per decision call | A whole batch of teams' weekly orders in one reply |
| What is compared | Initial choice versus initial choice plus a revision opportunity | Fictional 10-second versus 180-second student deadlines |
| Who runs the model | Python, using your API key | You, in fresh website chats |
| Main notebook | 04 for GPT; 05 for Claude | 07 |
| Progress | Live calibration, weeks, games and estimated spending | Number of validated replies, out of 20 |

These are **different experiments**. Keep their data and conclusions separate. API tokens measure model generation, not human time. Manual deadline wording does not impose a real time or token limit.

Both use fictional second-year University at Buffalo business students, four written personality profiles, and the same Beer Game accounting. No real student data validate the personas. The predictions are: short deliberation/deadline gives **H1 lower pipeline sensitivity, H2 higher cost, H3 higher bullwhip**. H1 is a separate matched-state question measure, not the original structural beta.

## 2. Set up the project once

**You:** give your agent a separate checkout/copy of the repository. For a new study it needs `src/`, `scripts/`, `tests/`, `notebooks/`, `config/`, `configs/`, `docs/`, `requirements.txt`, `README.md` and `AGENTS.md`. Include `data/` and `reports/` if you also want the old evidence. Keep any existing evidence intact.

**Agent:** read the README, maintenance instructions and the chosen protocol. Work in the new user's checkout. The examples below use Windows PowerShell, from the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name beer-game --display-name "Beer Game"
.\.venv\Scripts\python.exe -m jupyter lab
```

Select the **Beer Game** kernel. Choose the model, sample size, seed, conditions and stopping rule before collecting results. Save these choices. A new study needs its own run identity; opening an old completed run does not create new observations.

## 3. API workflow

### A. Agree on the plan and spending limit

**You:** choose a provider and give an explicit total dollar limit. Supply your key only through the masked prompt or an environment variable. This guide does not authorize a purchase.

**Agent:** use the maintained entry points below. These are the repository's recorded configurations, not a claim about today's best model or current prices:

| Provider | Entry point | Recorded setup | Original sample |
| --- | --- | --- | --- |
| OpenAI | `scripts/run_economy_study.py` | `gpt-6-luna`, Flex, high effort | 1 paired block: descriptive pilot |
| Direct Anthropic | `scripts/run_claude_study.py` | `claude-haiku-5-5`, standard-only, high effort | 8 paired blocks |

Check current provider availability, request compatibility and prices before paying. Changed model/pricing/protocol settings require documented changes and fresh compatible calibration. Preserve the historical source snapshots.

The retained design uses an initial ceiling of **16,384 tokens** and an extra revision ceiling of **8,192**. These are maximum allowances, not guaranteed usage. Effort stays **high** and temperature is **omitted in both conditions**. The common **900-second timeout** handles technical failures; it is not the treatment. A game has four practice weeks, 20 model-decision weeks and 12 automatic scoring weeks.

**Budget detail for the agent:** `shared_budget.py` applies its historical cross-run $2.95 guard specifically to campaign `20261011`. Changing `--campaign` does not create that shared guard for a new campaign. The per-run cap still applies. For a new owner, record a separately authorized campaign and start with **one complete calibration-plus-game invocation** below. Before purchasing additional runs/providers, enforce the owner's cumulative limit, including previous charges and unresolved reservations. Never rename a campaign to evade a spending limit. The original owner's historical approval is not the new owner's approval.

### B. Check the software without paying

For the selected provider, run its offline check. For example:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/run_claude_study.py --mode offline --pairs 1 --replicate colleague-software-check-01
```

For GPT, use `run_economy_study.py` instead. Offline choices are synthetic software tests; never include them in the model-results sample. Check the selected provider's tests under `tests/test_claude_study.py` or `tests/test_economy_study.py` before live work.

### C. Run calibration and games together

**Only after the new owner authorizes the provider and cap**, choose **one** command. Replace the example campaign/replicate names with the recorded new-study names. The caps below include that invocation's calibration and games; they are not promises that the requested sample will fit.

```powershell
# Claude example: one complete invocation, maximum run allowance $2.15.
.\.venv\Scripts\python.exe -X utf8 scripts/run_claude_study.py --mode api --weeks 24 --pairs 8 --budget 2.15 --campaign colleague-authorized-01 --replicate colleague-claude-01 --prompt-key-gui

# Alternative GPT example: one paired pilot, maximum run allowance $2.20.
.\.venv\Scripts\python.exe -X utf8 scripts/run_economy_study.py --mode api --weeks 24 --pairs 1 --budget 2.20 --campaign colleague-authorized-01 --replicate colleague-gpt-01 --prompt-key-gui
```

The program starts with calibration: a quick screen and development/held-out cases check valid completion, measured reasoning, token headroom and actual initial-versus-combined generation. The stored calibration allowance is $0.18. Games proceed only if the gates pass and the planned sample's forecast fits the remaining allowance. The request-level spending guard can still stop a run later. A small calibration checks feasibility; it cannot guarantee hypothesis support, statistical power or human realism.

If calibration fails, preserve the partial report and stop that plan. If a separate calibration-only run was intentionally purchased, reuse it with `--calibration-run` and a new game replicate ID; count its cost in the same authorized total. Do not silently buy it again.

### D. Watch progress and finish

The terminal prints calibration progress, game week, completed chains and charged/reserved spending. To watch in Jupyter, open notebook **04** or **05**, leave `RUN_CALIBRATION=False` and `RUN_GAMES=False`, and use the **Watch a run started from PowerShell** section with `WATCH_RUNNING=True`. Watching does not start another paid worker.

When the run completes or stops, note the printed raw-data and report paths. Audit it without model calls:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/audit_anytime_run.py --run data/runs/YOUR_API_RUN
```

Keep the exact request payloads, responses, requested/returned model IDs, usage, costs, selected-order provenance and source snapshots. A missing initial decision or technical error stops the run; only the protocol's token-exhausted revision may retain its valid same-state initial choice. Do not invent replacement orders.

The retained API analysis reports paired-block tests and Holm adjustment only when the full planned sample, its minimum eight-pair reporting threshold and computational checks qualify. One paired pilot is descriptive. Weekly calls and four roles are not independent students; eight pairs are not a guarantee of adequate statistical power.

## 4. Manual copy/paste workflow

### A. Prepare a new collection

**You:** choose the website's displayed model and reasoning mode and use them consistently. The reference collection used user-reported **GPT-6 / Pro**. Website Pro is not assumed to equal API high. No API key is needed; website access/subscription is separate.

**Agent:** open a working copy of notebook **07**, run section 1, then replace section 2's existing-run selection with the following. Choose a new label and seed before collecting. Record the actual displayed model; the helper accepts mode labels `pro` or `high`.

```python
# Section 1 already imports these project helpers.
MODEL_LABEL = "GPT-6"       # Replace if the user selected a different model.
EFFORT_LABEL = "pro"       # Record the actual selected mode.
RUN = prepare(DeadlineConfig(
    students=500, batch_students=100, weeks=24, generations=2,
    seed=2026101901, study_label="colleague-deadline-01",
    model_label=MODEL_LABEL, effort_label=EFFORT_LABEL,
))
MANIFEST = audit(RUN)
PLAN = read(RUN / "plan.json")
RESULT = build_report(RUN)  # Publishes the new prompt index and empty report.
print("New study:", RUN)
```

This creates **five batches × two deadlines × two generations = 20 prompts**. Each reply represents 100 fictional identities in 25 teams, with 2,000 weekly orders. The completed study has 500 unique identities, not 2,000 independent students.

Do not use the old completed study's prompt IDs for your new collection. Do not run `prepare_deadline_rerun.py` expecting a new study: its defaults recreate/open the original plans. Update the working notebook's static introductory links to identify your new run; section 3's progress is authoritative. Keep the same new configuration on later notebook sessions.

### B. Send the prompts

1. Run notebook sections 3–4. Open the next prompt, or the new run's `reports/deadline_cohort_.../PROMPTS.md` index.
2. Copy the **entire box** into a **fresh chat** with the chosen model/mode. Include no previous replies and no desired result.
3. Save the complete JSON response unchanged as a UTF-8 `.txt` file named for its `task_id`.
4. Send the file to your agent, or paste it into notebook section 5 and click **Validate and save**. Section 6 supports file import.
5. Repeat for all 20 planned tasks, including the second generation. Generation 2 is a fresh response to the same scenario, not a request to revise the first answer.

Separate tabs can be used for different prompts without waiting for the agent after every reply. Submit in the listed order, keep settings fixed and record any errors or changed execution arrangements. Follow the website's limits; do not switch models to bypass them. Files may be returned together because their task IDs identify them.

### C. Validate each response

The agent checks the study/task IDs, deadline, rule answers, all 25 teams, the 20-by-4 order arrays, the four-by-two probe arrays and completeness. Original text stays in `data/runs/`; accepted decisions are locked.

The existing formatter permits only documented, unambiguous rule-answer type conversions. Never fill missing orders, change incorrect rule answers, remove zero orders, or regenerate a valid reply merely because its results are unwanted. Preserve rejected attempts and disclose technical retries.

CLI alternative, after the user confirms the full prompt and settings:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/import_deadline_response.py --run data/runs/YOUR_MANUAL_RUN --task b0001_g01_brief --response "C:\path\to\reply.txt" --chat-label colleague-chat-01 --full-prompt-confirmed
```

Use the task ID actually inside the corresponding prompt/response. Never claim independent provider/settings verification merely because the user reported a label.

### D. Analyze and report

Run notebook section **7** for tables and six plots, and section **8** for interactive team charts. The progress bar counts accepted replies; it cannot monitor generation on the website. Verify the new run:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/audit_deadline_run.py --run data/runs/YOUR_MANUAL_RUN
.\.venv\Scripts\python.exe -X utf8 scripts/check_deadline_notebook.py --run data/runs/YOUR_MANUAL_RUN
```

Python reconstructs inventory, backlog, shipments and cost. Compare matched deadline scenarios and show same-deadline repeat variation. Keep practice, model decisions and automatic continuation distinguishable. This workflow reports descriptive results, without treating generated identities as independent humans or calculating student-level p-values.

## 5. What your agent should deliver

Use one clearly named `reports/YOUR_STUDY/final/` folder:

```text
README.md            Short overview and run instructions
REPORT.md            H1/H2/H3 results, repeat checks, limits and embedded plots
EXACT_PROMPTS.md      Complete prompts in separate boxes; explain where each is used
plots/               PNG and PDF figures
results/             Excel, CSVs, column guide and provenance
```

Also provide a ZIP. Preserve raw evidence separately under `data/runs/`. For manual data, export a model-only weekly-order CSV; do not label practice/automatic actions as model choices. For API data, retain every actual system/user/provider request, including revisions and calibration, with the request-to-decision mapping.

Use [our current package](../reports/CURRENT_BEER_GAME/README.md) as a layout example. Its publisher is intentionally pinned to our completed run and post-collection H1-H4 assessment; the new user's agent must prepare a corresponding publisher for their own run. Do not overwrite our final package or run the historical completion checker with an unrelated snapshot.

## 6. Copy this instruction to your agent

> Read this guide and the project maintenance instructions. Set up my separate checkout and prepare a new Beer Game study using the workflow I choose. Preserve existing evidence. For API work, confirm my provider and total budget, verify model/pricing compatibility and enforce cumulative spending before purchases; accept keys only through a masked prompt or environment. For manual work, freeze a new plan and give me the exact prompts, then validate and retain every reply. Keep the model/settings fixed, do not force a hypothesis result, and distinguish generated students from real people. Give me a README, report with plots, exact prompts, extracted results and a ZIP. Use offline checks for software verification and update documentation for every change.

## Protocol references

[GPT API protocol](ECONOMY_PROTOCOL_20261011.md) · [Claude API protocol](CLAUDE_PROTOCOL_20261011.md) · [Shared API design](ANYTIME_PROTOCOL_20261011.md) · [Manual deadline protocol](DEADLINE_COHORT_PROTOCOL_20261018.md) · [Personality files](../config/student_profiles) · [Repository README](../README.md).
