# Beer Game study

**Open the current report here: [reports/CURRENT_BEER_GAME/REPORT.md](reports/CURRENT_BEER_GAME/REPORT.md).**

**20 October 2026 supplied collection:** [GPT-6 Astra / extra high effort findings](reports/EDUCATION_DEADLINE_10S_60S/website_astra_extra_high/FINDINGS.md), [full report](reports/EDUCATION_DEADLINE_10S_60S/website_astra_extra_high/REPORT.md), and [Excel results](reports/EDUCATION_DEADLINE_10S_60S/website_astra_extra_high/results/RESULTS.xlsx). All six new response files were accepted unchanged. This separate collection preserves the original prepared plan and earlier completed publication.

**Run on another computer:** [Agent handoff](AGENT_HANDOFF.md) covers verifying this completed collection and preparing a separate new sample. Use the byte-preserving project transfer bundle described there; a reader ZIP or a Git checkout with normalized line endings is insufficient for exact evidence reproduction. The separate portable verifier resolves local copies while preserving recorded original paths.

| What you need | File |
| --- | --- |
| README | [Current study overview](reports/CURRENT_BEER_GAME/README.md) |
| Report and six plots | [H1-H4 report](reports/CURRENT_BEER_GAME/REPORT.md) |
| Exact prompts | [All 20 prompts](reports/CURRENT_BEER_GAME/EXACT_PROMPTS.md) |
| Extracted results | [Excel](reports/CURRENT_BEER_GAME/results/RESULTS.xlsx), [40,000 orders CSV](reports/CURRENT_BEER_GAME/results/weekly_orders.csv), [column guide](reports/CURRENT_BEER_GAME/results/README.md) |
| Complete download | [Beer_Game_H1_H4.zip](reports/CURRENT_BEER_GAME/Beer_Game_H1_H4.zip) |

## What the data can tell you

The existing collection is complete: 20 replies and 500 fictional identities. For your four hypotheses, H1 has exploratory proxy evidence; H2 costs point opposite the prediction; H3/H4 were not tested because education/control lecture groups are absent. Binding decision time was not verified. **A new experiment is required to test all four as written.** [Hypotheses and proposed design](docs/HYPOTHESES_H1_H4.md).

The framework was supplied after collection. No original decisions, prompts or scoring rules were changed. These are model-generated scenarios, not independent human observations.

## Read or verify

Open [notebook 07](notebooks/07_deadline_cohort_rerun.ipynb), run sections 1-4, then 7-8. It now shows the four-hypothesis assessment and 125 interactive team charts.

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/build_current_report.py
.\.venv\Scripts\python.exe -X utf8 scripts/audit_deadline_run.py --run data/runs/deadline_cohort_2800524c9b2e0729
.\.venv\Scripts\python.exe -X utf8 scripts/check_deadline_notebook.py --run data/runs/deadline_cohort_2800524c9b2e0729
.\.venv\Scripts\python.exe -X utf8 scripts/check_current_report.py
```

All commands above use saved data only. The publisher verifies an existing package without replacing it; further publication changes must archive the superseded package first. [Guide for another user and their agent](docs/README_FOR_NEW_USERS.md).

## New 10-second / 60-second prompt study

[Original six-prompt package](reports/EDUCATION_DEADLINE_10S_60S/START_HERE.md). Each task covers all 500 fictional identities in 125 chains. Three cases (60s/control, 10s/control, 10s/causal reading), each repeated once, address the H1-H4 simulation contrasts with six replies. [Preflight findings](reports/EDUCATION_DEADLINE_10S_60S/PREFLIGHT_FINDINGS.md) keep the isolated assistant checks separate. The [received Astra collection](reports/EDUCATION_DEADLINE_10S_60S/website_astra_extra_high/README.md) is complete at 6/6; the original GPT-6 / Pro prepared plan remains unchanged. [Protocol](docs/EDUCATION_DEADLINE_PROTOCOL_20261019.md).

Prepare/verify the frozen prompts with `.\.venv\Scripts\python.exe -X utf8 scripts/education_deadline_workflow.py prepare`. The start guide gives one-command folder/ZIP import and reporting. Tests: `.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -p "test_education_deadline*.py" -v`. These commands make no API calls. Deadline wording does not enforce 10/60-second computation; pipeline sensitivity is a proxy; jointly generated rows cannot supply independent student-level significance. The existing current report remains the completed earlier study.

**19 October 2026 update:** read and preserved the supplied reflection; added matched 254-word causal/control readings, a separate three-case full-cohort design, immutable imports, and batch file collection. The fixed small pilot finished 6/6 first-attempt responses; the one planned 500-identity capacity response passed. H3 reverses across repeats and H4's mean cost contrast opposes prediction; these checks do not establish significance. The separate website plan remains at 0/6. All 31 offline tests passed, 21,456 role-week states were independently recomputed, and 13,144 earlier files were unchanged. No prompts were retuned, no extra trials or paid API calls were added, and earlier scientific sources, decisions and publications remain preserved. Reproduce verification with `.\.venv\Scripts\python.exe -X utf8 scripts/check_education_deadline.py`; regenerate the saved preflight publication with `scripts/finalize_education_preflight.py`.

**20 October 2026 update:** received `response1.json` through `response6.json` and the user's statement "I'm using gpt 6-astra extra high effort". All six passed exact schema/replay without conversion. The frozen parent plan expected GPT-6 / Pro, so a separately fingerprinted collection, `education_deadline_observed_d30e00f21698e1ce`, preserves the original response IDs and links each file to its parent prompt. Literal reported effort is not mapped to Pro, high, or an API setting; provider/interface, full prompts, fresh chats and generation source remain unverified. [Dated settings amendment](docs/EDUCATION_DEADLINE_SETTINGS_20261020.md). Reproduce the saved-data report with `.\.venv\Scripts\python.exe -X utf8 scripts/report_education_deadline_collection.py` and audit with `.\.venv\Scripts\python.exe -X utf8 scripts/check_education_deadline_collection.py`. These commands make no model/API calls. The original six source files, frozen scientific code, parent plan and previous publications remain preserved; no further response is needed for this fixed sample.

Verification passed **41 offline tests**, an independent recomputation of all **108,000 states**, exact checks of **60,000 orders / 3,000 probe pairs / 1,000 contrasts**, and preservation of **15,013 earlier files**. [Audit receipt](reports/software_checks/education_deadline_astra_20261020.json). Mean contrasts H1/H2/H3/H4 are +0.041667, +49.850000, -0.166667 and -73.566000: H2/H4 cost means follow predictions, H1/H3 proxy means oppose them. These are descriptive results. The [previous operational report implementation](reports/archive/education_deadline_reporting_20261020/README.md) is archived with its exact saved publication hash; the old packages remain unchanged.

**20 October 2026 cross-computer handoff:** added `AGENT_HANDOFF.md`, analysis dependency constraints, a byte-preserving transfer builder and an operational portable verifier because the original strict audit requires historical Windows paths and Git can normalize frozen LF/CRLF bytes. Build the transfer with `.\.venv\Scripts\python.exe -X utf8 scripts/build_beergame_handoff.py`; verify an extracted copy with `scripts/verify_beergame_handoff.py --root .`. Tests: `python -m unittest discover -s tests -p "test_handoff_portability.py" -v`. The guide covers existing-result verification and a separate prospective sample; literal extra-high preparation requires a versioned fork before collection. This handoff starts no experiment or paid run and changes no frozen scientific source, manifest, response or publication.

## Folder layout

- `reports/CURRENT_BEER_GAME/`: the one current report, plots, prompts and results.
- `reports/archive/`: earlier reports, superseded publications and historical notes; [archive index](reports/archive/README.md).
- `reports/logs/` and `reports/software_checks/`: operational evidence.
- `data/`: preserved raw replies, plans and scientific source snapshots.
- `notebooks/`, `src/`, `scripts/`, `tests/`, `docs/`, `config/`, `configs/`: maintained project files. [Maintenance instructions](AGENTS.md).

**18 October 2026 update:** replaced the three-outcome presentation with your exact H1-H4; marked education effects missing; added an explicit rerun design; consolidated active output into one named folder; archived 16 older study/report folders and the superseded ZIP. Notebook and CLI navigation use the corrected report. Raw evidence and frozen scientific sources are unchanged. [Verification](reports/software_checks/hypothesis_alignment_20261018.json).

**18 October 2026 Git maintenance:** resolved a merge conflict involving a temporary Word lock file by retaining the incoming file; added an ignore rule for newly created Office lock files (`~$*`). Existing tracked lock files remain tracked. The staged notebook metadata change is preserved. Verify with `git diff --cached --check` and `git ls-files -u` (no output means no unresolved conflicts), then finish the pending merge with `git commit --no-edit`. This maintenance does not alter study data, scientific sources or report contents.
