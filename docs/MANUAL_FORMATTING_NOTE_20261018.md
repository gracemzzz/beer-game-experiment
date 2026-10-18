# Batch 4 JSON formatting record — 18 October 2026

Run `manual_cohort_975b76e63e5b4882`, initial batch `b0004`, arrived with three factual answers encoded as quoted text: `"Yes"`, `"10"`, and `"15"`. Their meanings match the required answers, but the frozen importer requires Boolean/numeric types and rejected this original text.

The original attachment and rejected raw attempt are retained unchanged. A separately recorded derivative replaces **only those three value tokens in the rules object** with `true`, `10`, and `15`. Every other character, including all weekly orders and probe arrays, is unchanged. The frozen importer accepted that derivative. No second model generation, strategy correction, order substitution, or additional deliberation occurred.

This is a format-only exception documented **after the response was received**, not a prospectively specified parsing policy. The same run is retained because no prompt, model selection, decision quantity, game rule, hypothesis or analysis formula changed. The accepted file is a derived representation; it must never be described as the byte-identical original reply. The original remains available alongside the exact transformation.

## Evidence

- [Receipt](../reports/manual_cohort_975b76e63e5b4882/BATCH_04_RECEIPT.md) and [checks](../reports/manual_cohort_975b76e63e5b4882/BATCH_04_CHECK.json).
- Raw source: `attempts/b0004_initial_001.txt`; accepted derivative: `attempts/b0004_initial_002.txt` within the run.
- `normalization/b0004_initial.json` records both SHA-256 hashes, all three edits, and a saved implementation hash. `normalization/implementation_20261018.py` preserves the helper source.
- `submission_context/b0004_initial.json` records attachment origin and the inherited user-reported GPT-6 / Pro settings. The attachment does not independently verify those settings.

The helper `normalize_rule_types` in `src/beergame_study/manual_response_formatting.py` never looks up correct answers. It converts only unambiguous Boolean words or unsigned digit strings in the designated rule fields. Incorrect answers remain incorrect and still fail the frozen validator. Ambiguous text, duplicate keys and non-rule values are not repaired. No orders or probes are converted.

The helper's report wrapper validates the original/derived hashes, reproduces the transformation and verifies the accepted derivative before appending a visible disclosure. Notebook 06 and the maintained manual-import CLI now use this wrapper. For later reports call `beergame_study.manual_response_formatting.build_report`; calling the frozen report builder directly omits the disclosure. The wrapper leaves all numerical analysis unchanged. Future normalization needs its own explicit record; the ordinary paste importer remains strict.

## Checks and continuation

All five focused offline formatting tests passed, including exact token-only changes, retaining incorrect answers, rejecting ambiguous text, and preserving orders/probes. Batch 4 passed the frozen checks after conversion and replayed 3,600 role-states; all 38 earlier run files remained unchanged. No API calls were made. Run the controls with:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -p test_manual_response_formatting.py -v
```

Collection progress is 4/10 accepted responses, 400 fictional identities and 8,000 initial weekly orders. [Batch 5 initial](../reports/manual_cohort_975b76e63e5b4882/prompts/b0005_INITIAL.md) is next, in a fresh GPT-6 / Pro chat. No revision or paired hypothesis comparison exists yet.

## Batch 5 extension, 18 October 2026

Batch 5 arrived with `"Yes"`, `"Week 10"`, and `"$15"` in the same three fields. Its original reply is preserved as `attempts/b0005_initial_001.txt`; the accepted derivative is `attempts/b0005_initial_002.txt`. Only those value tokens became `true`, `10`, and `15`. All other text, orders and probes are unchanged; no model retry occurred. See the [receipt](../reports/manual_cohort_975b76e63e5b4882/BATCH_05_RECEIPT.md) and [checks](../reports/manual_cohort_975b76e63e5b4882/BATCH_05_CHECK.json).

Formatting helper v2 permits an explicit `Week ` or `week ` prefix only in the arrival-week field, and a `$` prefix only in the backlog-cost field, followed by unsigned digits. It still never consults correct answers. Wrong values remain wrong; mixed/ambiguous text and units in the wrong field are rejected. This narrow extension was documented after receipt, not prospectively. `normalization/b0005_initial.json` records the exact edits and both hashes; `implementation_v2_20261018.py` retains its source separately from the original v1 helper. The report wrapper reproduces both transformations and discloses both derivatives. Frozen scientific sources remain unchanged.

All eight focused formatting tests passed, including the original five controls and three additional unit-label controls. The five initial batches now cover 500 fictional identities and 10,000 weekly orders; local replay covers 18,000 role-states. All five revision prompts were checked against their locked initial decisions. Current progress is **5/10 responses**. [Batch 1 revision](../reports/manual_cohort_975b76e63e5b4882/prompts/b0001_REVISION.md) is next, in a fresh GPT-6 / Pro chat; the prompt already contains the original decisions. No paired comparison exists until a revision arrives.

## First revision, 18 October 2026

Batch 1 revision used the same three strings as batch 5. The existing v2 helper converted only `"Yes"`, `"Week 10"`, and `"$15"` in the rule fields. No helper or scientific source change was needed. The original and derivative are `attempts/b0001_revision_001.txt` and `attempts/b0001_revision_002.txt`; `normalization/b0001_revision.json` records both hashes, edits and the existing v2 implementation hash. All other characters, orders and probes are unchanged. This is one returned model response, not two generations.

The accepted revision retains every initial weekly order and probe choice. The report records that zero change without altering data or requesting a different result. Progress is 6/10, with one paired batch and four revisions missing. [Receipt and checks](../reports/manual_cohort_975b76e63e5b4882/BATCH_01_REVISION_RECEIPT.md). Later reports must retain all three formatting disclosures.

## Second revision, 18 October 2026

Batch 2 revision also used `"Yes"`, `"Week 10"`, and `"$15"`. The unchanged v2 formatter converted only these three rule-answer tokens. Original and derivative files are `attempts/b0002_revision_001.txt` and `attempts/b0002_revision_002.txt`; `normalization/b0002_revision.json` records hashes, edits and the existing helper source hash. All other characters, orders and probes are unchanged, and no model retry occurred. [Receipt and checks](../reports/manual_cohort_975b76e63e5b4882/BATCH_02_REVISION_RECEIPT.md).

This revision matches all its initial orders and probe choices. Progress is 7/10, with two paired batches and three revisions missing. Later reports must retain all four formatting disclosures. No prompts or acceptance rules were adjusted in response to the observed zero changes.
