# Manual chat settings amendment — 18 October 2026

The user returned the first 100-identity batch and reported the website model label **GPT-6** and selected mode **Pro**. They explicitly clarified that Pro was the selected model/reasoning mode, not merely the subscription name. The prepared v1 plan instead recorded GPT-6 Astra / high. These labels cannot be treated as equivalent or silently substituted.

Protocol `manual-cohort-chat-settings-v2` records **GPT-6 / pro** literally and keeps that selection fixed for all subsequent batches and both passes. The underlying provider model snapshot, API effort, hidden reasoning tokens and generation duration remain unknown. No claim that Pro equals API high is made. The user-facing JSON schema stays `manual-cohort-trajectories-v1` because the response fields and array meanings are unchanged.

## Preserve the received response

This amendment was made **after receiving and inspecting the first initial response**, and before receiving other batches or any revision. It is not a prospective registration for that first response. The change addresses the reported interface settings; it does not alter student profiles, demand paths, cohort size, outcome measures, or choose responses based on hypothesis results.

A separate run fingerprint includes the new settings, versioned scientific sources, and SHA-256 lineage for the original prompt, response, manifest and plan. Only the exact already-received `b0001` initial response may retain the original study ID. Its text and quantities are preserved, and its acceptance record identifies the parent. Future prompts and responses use the new study ID. The original v1 plan and scientific implementation remain usable and unchanged. The response is one observation carried between records, not two model generations.

The first response arrived following the instruction to copy the complete prompt and return the complete JSON. This is user-provided provenance, not an independently observed chat transcript or verified API request. Original model/mode wording and the follow-up clarification are saved with the received submission.

## Continue collection

1. Use the new run's next prompt, beginning with `b0002_INITIAL.md` after the carried response is accepted.
2. Start a fresh chat with **GPT-6 / Pro** each time. Copy the full prompt box, then return the complete JSON here or paste it into notebook 06.
3. Collect all five initial responses before any revision. Keep the first accepted response for each slot; no outcome-based replacements.
4. Notebook 06 opens the latest manual run, selects its matching importer/report implementation, and displays accepted-response progress. Its new-plan controls still allow the original v1 workflow explicitly.

The existing game rules and [descriptive analysis limitations](MANUAL_COHORT_PROTOCOL_20261017.md) still apply. Identical probe choices are retained. No hypothesis comparison is available until both passes exist; no student-row p-values, validated student realism or verified token/time manipulation are claimed. No API calls or charges are made by importing or analyzing these responses.

## Maintenance and checks

The v2 implementation is a versioned fork in `manual_cohort_chat.py` and `manual_cohort_chat_report.py`; editing the frozen v1 modules would invalidate its prepared run. The strict importer continues to enforce settings, dimensions, factual rules, immutable acceptance and initial-before-revision ordering. Lineage checks prohibit modifying the first response or changing its study ID. Every source change requires a new fingerprint.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -p 'test_manual_cohort*.py' -v
.\.venv\Scripts\python.exe -X utf8 scripts/build_manual_cohort_notebook.py
```

All 42 original, chat-settings and lineage tests passed on 18 October 2026. They use offline synthetic controls and validate software only. Raw evidence belongs in `data/`; receipts, partial reports and later plots belong in `reports/`.

The [notebook checkpoint audit](../reports/software_checks/manual_chat_20261018.json) also passed: eight actual-run cells, eight isolated synthetic cells, both paste callbacks and six synthetic plot pairs, with API clients blocked and the real accepted response unchanged. Its dated reproduction script is `scripts/check_manual_chat_notebook.py`; the expected collection state is the first-response checkpoint, before batch 2 arrives.
