# New 10-second / 60-second Beer Game prompts

This is a separate prepared study. The completed report remains in `reports/CURRENT_BEER_GAME/`.

Each prompt covers **all 500 fictional identities in 125 chains**. Three cases cover H1-H4: 60s/control, 10s/control, and 10s/causal education. Two independent generations mean **six fresh chats**, rather than twenty. The same identities are matched across cases; they are not additional people. There are 60,000 submitted weekly orders across six complete replies.

1. Open a fresh chat with the same user-reported **GPT-6 / Pro** selection for each task. Check that the selected chat can produce downloadable files; availability on your exact selection is unverified.
2. Copy the entire task text below. Alternatively, attach its `.txt` file and say: "Read the attached task file as my request and complete that one task. Return the complete downloadable JSON file."
3. Download the complete response JSON. Name it after the task, such as `r01_a60_control.json`. If tools were used, also save the serialization source or transcript. The model should choose the explicit orders; code should track physical state or save them, rather than invent missing decisions using a policy.
4. Repeat with the next task in a fresh chat, without earlier responses. Keep failures and incomplete files too. Do not ask for a better effect or replace an unfavorable result.
5. Return the six files here together, or put them in one folder/ZIP. I can import and report them together; no manual extraction of individual chains is needed. Downloadable delivery avoids copying long answer text, but does not guarantee completion.

| Order | Task | Fictional deadline | Reading | File |
| --- | --- | ---: | --- | --- |
| 1 | `r01_a60_control` | 60 s | control | [Prompt](prompts/r01_a60_control.txt) |
| 2 | `r01_b10_control` | 10 s | control | [Prompt](prompts/r01_b10_control.txt) |
| 3 | `r01_c10_education` | 10 s | causal | [Prompt](prompts/r01_c10_education.txt) |
| 4 | `r02_a60_control` | 60 s | control | [Prompt](prompts/r02_a60_control.txt) |
| 5 | `r02_c10_education` | 10 s | causal | [Prompt](prompts/r02_c10_education.txt) |
| 6 | `r02_b10_control` | 10 s | control | [Prompt](prompts/r02_b10_control.txt) |

Each response contains 10,000 weekly orders and 1,000 probe orders. Full arrays are required. A missing or truncated response remains incomplete. Three prompts suffice for one generation; this frozen plan includes a repeat of each case for six total responses.

**What the preflight can establish:** see [pilot results](pilot/REPORT.md), [full-size capacity check](capacity_check/REPORT.md), and [preflight findings](PREFLIGHT_FINDINGS.md) when those files have been generated. These assistant outputs are separate from your website collection. They cannot certify significance or equivalence to your chat backend.

**Limits that affect interpretation:** deadlines are fictional descriptions, not enforced model computation or verified student time; the causal reading is a short text, not an observed 20-minute lecture. H1/H3 use the existing pipeline-sensitivity proxy, not an identified structural underweighting coefficient. Chains within one generated reply are dependent. Six replies do not support student-level significance tests. Read [the full design](DESIGN.md).

To import all downloaded files at once from `D:\beergame`:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/education_deadline_workflow.py import --responses "D:\path\to\your\responses.zip" --session-label "fresh-GPT6-Pro-chats" --confirm-full-prompt
.\.venv\Scripts\python.exe -X utf8 scripts/education_deadline_workflow.py report --collection website
```

The importer makes no API calls, preserves original bytes, retains rejected attempts and locks accepted files. It accepts a single JSON, a folder of JSON files or a ZIP. Existing study evidence and publication packages are unchanged.
