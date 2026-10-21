# Maintenance and historical compatibility

The human entry point is [the experiment index](../experiments/README.md). This folder contains shared source documents/profiles, old navigation, and evidence needed to reproduce historical audits.

| Item | Location |
| --- | --- |
| Every original path, new path and pre-migration hash | [FILE_MAP.json](reorganization_20261020/FILE_MAP.json) |
| Migration verification | [MIGRATION_CHECK.json](reorganization_20261020/MIGRATION_CHECK.json) |
| Original README, instructions and cross-computer handoff | [original_navigation/](reorganization_20261020/original_navigation/) |
| Preexisting LF/CRLF audit | [byte scan](reorganization_20261020/beer_handoff_byte_scan_20261020.json) |
| Independent 108,000-state replay before migration | [numerical replay](reorganization_20261020/beer_handoff_numeric_replay_20261020.json) |
| Shared profiles, source reflection and literature | [shared_inputs/](shared_inputs/) |
| Completed organization, notebook and compatibility checks | [validation status](reorganization_20261020/VALIDATION_STATUS.json) |
| Full verified derived-copy receipt | [Astra verification](reorganization_20261020/LEGACY_ASTRA_VERIFICATION.json) |
| Historical environment and constraints | [handoff_20261020/](handoff_20261020/) |

## Verify canonical files

From the repository root:

```bash
python3 scripts/reorganize_experiments.py --verify
```

This checks all 39,589 original tracked files using the complete move map. Its baseline is the current checkout before reorganization. Root navigation originals are preserved separately, so the new guides can be edited without changing historical evidence. New files are not added retroactively to the old evidence baseline.

## Recreate old paths for saved-data checks

```bash
python3 scripts/legacy_workspace.py --recover-historical-bytes --verify-astra
```

The command prints a new temporary folder. It copies all old tracked paths and their exact bytes before attempting any recovery. It never creates symlinks, patches scientific functions, changes manifest strings, copies secrets, or calls a model. The original verifier runs in a fresh subprocess with its own unchanged code and full recorded spending history.

`LEGACY_WORKSPACE_RECEIPT.json` records the mapping and every recovered copy file. `LEGACY_ASTRA_VERIFICATION.json` records the independent audit if it succeeds. A recovery is allowed only when conversion between LF and CRLF reproduces the exact SHA-256 already recorded in historical evidence. Canonical files are never converted.

To make only a copy of current bytes, omit both flags. To choose the location, add `--output /path/to/new-empty-folder`. The copy uses approximately 0.7 GB. Dependencies must already be installed; use the historical constraints where exact environment reproduction matters.

For the original software checks, change into the printed temporary folder and run:

```bash
python3 -m unittest discover -s tests -p 'test_education_deadline*.py' -v
TMPDIR=/private/tmp python3 -m unittest discover -s tests -p 'test_handoff_portability.py' -v
```

The copied original paid notebooks/runners are historical records. Do not use them to start paid collection from the reorganized root: their cumulative guard scans the old `data/runs` path. New collection belongs in the new experiment and its separately authorized budget. Do not reset campaign IDs or infer spending permission from old caps.

## Publication and path limits

The original publication packages, source fingerprints, prompt IDs, receipts and submitted orders retain their bytes. Relative links inside intact packages remain usable. Historical links outside their package may refer to old paths or the original Windows machine; use the experiment guides, move map or compatibility copy. The original strict Windows checker is still original-machine-specific; the portable verifier explicitly records that those external locations were not rechecked.

The repository had 14,435 historical line-ending mismatches before migration. This is recorded rather than hidden by changing baselines. A successful hash-confirmed reconstruction checks a derived copy; it does not claim that the organized canonical files were delivered by the missing byte-preserving ZIP.

Verification completed: six new organization tests, fourteen historical portability tests and all eleven review notebooks passed. The original portable verifier independently checked 108,000 states and the full 15,013-file baseline in the hash-recovered copy. The Anaconda Python environment runs the saved-data audit; its older pandas causes five historical publication-generation tests to error on `lineterminator`. These frozen tests/source were not changed, and saved publications were not regenerated. Use the recorded modern analysis constraints to reproduce the publication-generation suite. On macOS, a resolved `TMPDIR` such as `/private/tmp` avoids old fixture path-alias differences.

New `.gitattributes` keeps exact line endings on future Git checkouts. It does not silently repair already-normalized historical files.
