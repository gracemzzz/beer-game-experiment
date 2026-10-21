"""Materialize a disposable old-layout copy for historical, saved-data audits.

The organized repository remains canonical. No scientific module is patched and
no historical manifest/path string is rewritten. Optional line-ending recovery
only changes a COPY when its candidate bytes match a preexisting expected hash.
This command never launches model/API calls or copies keys/environment files.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAP = Path('maintenance/reorganization_20261020/FILE_MAP.json')
BASELINE = 'reports/software_checks/education_deadline_astra_before_20261020.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inside(root, relative):
    value = PurePosixPath(relative)
    if not isinstance(relative, str) or value.is_absolute() or '..' in value.parts or '\\' in relative or ':' in relative:
        raise ValueError('Unsafe relative path: '+repr(relative))
    target = (Path(root) / relative).resolve()
    if not target.is_relative_to(Path(root).resolve()):
        raise ValueError('Path escapes workspace: '+relative)
    return target


def hash_confirmed_recovery(path, expected):
    """Return a derivation record, or None if the exact historical bytes exist."""
    path = Path(path)
    original = path.read_bytes()
    actual = digest(original)
    if actual == expected:
        return None
    lf = original.replace(b'\r\n', b'\n')
    for name, candidate in [('CRLF_to_LF', lf), ('LF_to_CRLF', lf.replace(b'\n', b'\r\n'))]:
        if digest(candidate) == expected:
            path.write_bytes(candidate)
            return dict(transformation=name, copied_sha256=actual, expected_historical_sha256=expected,
                        recovered_sha256=digest(candidate))
    raise ValueError('No hash-confirmed line-ending reconstruction for '+str(path))


def recover_astra(copy_root):
    """Recover only bytes independently fixed by existing historical receipts."""
    copy_root = Path(copy_root)
    recovered = []

    def apply(relative, expected, evidence):
        record = hash_confirmed_recovery(inside(copy_root, relative), expected)
        if record:
            recovered.append(dict(path=relative, expected_hash_source=evidence, **record))

    baseline = json.loads(inside(copy_root, BASELINE).read_text(encoding='utf-8'))['files']
    for relative, expected in baseline.items():
        apply(relative, expected, BASELINE)
    pointer_name = 'reports/LATEST_EDUCATION_DEADLINE_COLLECTION.json'
    pointer = json.loads(inside(copy_root, pointer_name).read_text(encoding='utf-8'))
    collection_rel = pointer['collection_run']
    manifest = json.loads(inside(copy_root, collection_rel+'/manifest.json').read_text(encoding='utf-8'))
    parent_rel = 'data/runs/'+manifest['lineage']['parent_study_id']
    parent_manifest = json.loads(inside(copy_root, parent_rel+'/manifest.json').read_text(encoding='utf-8'))
    source_locations = {
        'protocol.md': 'docs/EDUCATION_DEADLINE_PROTOCOL_20261019.md',
        'lectures/control.txt': 'docs/education_deadline_20261019/control_lecture.txt',
        'lectures/causal.txt': 'docs/education_deadline_20261019/causal_lecture.txt',
    }
    for name, expected in parent_manifest['sources'].items():
        current = source_locations.get(name)
        if current is None:
            current = 'config/student_profiles/'+name.split('/', 1)[1] if name.startswith('profiles/') else 'src/beergame_study/'+name
        apply(current, expected, parent_rel+'/manifest.json:sources/'+name)
    for relative, expected in manifest['lineage']['parent_inputs_sha256'].items():
        apply(parent_rel+'/'+relative, expected, collection_rel+'/manifest.json:lineage')
        apply(collection_rel+'/'+manifest['lineage']['snapshot_relative_path']+'/'+relative,
              expected, collection_rel+'/manifest.json:lineage')
    return recovered


def materialize(root=ROOT, target=None, recover_historical=False):
    root = Path(root).resolve()
    mapping = json.loads((root / MAP).read_text(encoding='utf-8'))
    if target is None:
        target = Path(tempfile.mkdtemp(prefix='beer-game-legacy-'))
    else:
        target = Path(target).resolve()
        if target.exists() and any(target.iterdir()):
            raise ValueError('Legacy copy destination must be new or empty.')
        target.mkdir(parents=True, exist_ok=True)
    if target == root or root.is_relative_to(target):
        raise ValueError('Legacy copy must not contain the canonical project.')
    copied = 0
    for item in mapping['files']:
        source = inside(root, item['new_path'])
        if digest(source.read_bytes()) != item['sha256']:
            raise ValueError('Canonical migration bytes changed: '+item['new_path'])
        destination = inside(target, item['old_path'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if digest(destination.read_bytes()) != item['sha256']:
            raise ValueError('Copy verification failed: '+item['old_path'])
        copied += 1
    derivations = recover_astra(target) if recover_historical else []
    receipt = dict(schema='legacy-workspace-copy-v1', created_utc=datetime.now(timezone.utc).isoformat(),
                   canonical_root=str(root), copy_root=str(target), copied_files=copied,
                   canonical_migration_sha256=digest((root/MAP).read_bytes()),
                   canonical_bytes_changed=False, frozen_scientific_modules_patched=False,
                   stored_provenance_paths_rewritten=False, historical_hash_recovery=recover_historical,
                   recovered_copy_files=len(derivations), derivations=derivations,
                   paid_api_calls=0,
                   usage='Saved-data verification only. This copy retains full old spending history; do not launch historical paid experiments.')
    (target/'LEGACY_WORKSPACE_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    return target, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New or empty directory; defaults to a new temporary folder.')
    parser.add_argument('--recover-historical-bytes', action='store_true', help='In the copy only, recover LF/CRLF candidates that match saved hashes.')
    parser.add_argument('--verify-astra', action='store_true', help='Run the unchanged portable verifier, including physical replay, in this copy.')
    args = parser.parse_args()
    folder, receipt = materialize(target=args.output, recover_historical=args.recover_historical_bytes)
    print(json.dumps({key: value for key, value in receipt.items() if key != 'derivations'}, indent=2), flush=True)
    if args.verify_astra:
        command = [sys.executable, '-X', 'utf8', str(folder/'scripts/verify_beergame_handoff.py'),
                   '--root', str(folder), '--output', str(folder/'LEGACY_ASTRA_VERIFICATION.json')]
        completed = subprocess.run(command, cwd=folder)
        if completed.returncode:
            raise SystemExit(completed.returncode)


if __name__ == '__main__':
    main()
