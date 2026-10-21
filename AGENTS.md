# Project maintenance instructions

## Current organization — 20 October 2026

The user explicitly requested experiment-owned folders, superseding the historical root-level data/reports/notebooks arrangement. Read [README.md](README.md), [experiments/README.md](experiments/README.md), and [maintenance/README.md](maintenance/README.md).

- Each experiment owns `hypotheses/`, `prompts/`, `data/`, `analysis/`, `reports/`, and `notebooks/`. Shared source, scripts and tests remain outside under `src/`, `scripts/` and `tests/`.
- New work belongs in `experiments/12_pressure_framing_api_20261020/` and its separately versioned implementation. Do not mix it with closed historical collections.
- The new experiment uses 80 fictional testers in 20 four-role chains, 24 model-decision weeks, and one joint cohort response per model. Treat generated identities as dependent; the sample does not establish independent student-level significance.
- Preserve every historical file's exact current bytes. The move map and hashes are `maintenance/reorganization_20261020/FILE_MAP.json`. A scientific change needs a new protocol/fingerprint; do not edit frozen source, prompts, manifests, responses or original publications to fit new results.
- Old reports and notebooks may contain original paths. Use the new experiment guides for navigation and `scripts/legacy_workspace.py` for saved-data replay in a disposable old-layout copy. Do not monkeypatch frozen code or rewrite recorded Windows source paths.
- Historical paid entry points depend on the original `data/runs` location for cumulative spending. They must not be used directly from this reorganized root. A new API study needs explicit cumulative accounting and a hard total cap including pilots and failed requests. Never rename campaigns to bypass prior spending.
- The user authorized new API testing, but model/settings availability and a new hard cap must be recorded in the new study before calls. Historical handoff caps are not fresh spending authority.
- Credentials remain in environment variables or hidden prompts, never files, notebook outputs, command arguments, logs or reports.
- Do not force interior/positive orders, supply a preferred maximum, encode the desired hypothesis direction, tune for significance, or fabricate missing decisions. Preserve null/opposite outcomes and failed attempts. Software controls must be labeled synthetic.
- Preserve actual provider/model labels and requested/reported settings separately. Prompted pressure is a fictional framing treatment unless computation or time is actually restricted and measured.
- Update the experiment's own README with changes, run instructions, validation and limitations. New reports put short numbered conclusions first. Run checks proportionate to changes.

The original complete instruction history is preserved in [original_navigation/AGENTS.md](maintenance/reorganization_20261020/original_navigation/AGENTS.md). Its frozen-study preservation requirements remain relevant; its old folder paths are resolved through the move map.

## Existing integrity issue

Before reorganization, 14,435 of the saved 15,013-file baseline had LF bytes where its hashes expected CRLF; 578 already matched. All mismatches were line-ending-only. Do not claim the canonical checkout matches the historical byte baseline. The compatibility helper recovers historical bytes only in a temporary copy and only when an existing expected hash proves the conversion. Keep its derivation receipt separate from migration verification.

The latest received Astra study is complete at 6/6. Its unchanged prepared GPT-6 / Pro parent remains 0/6 for provenance; it is not an outstanding request. No extra responses belong in that closed sample. See experiment 11 for reports and intake records.
