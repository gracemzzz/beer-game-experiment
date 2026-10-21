"""Build a byte-preserving executable handoff without environments or credentials."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-10-20'


def inside(root, relative):
    relative = PurePosixPath(relative)
    if relative.is_absolute() or '..' in relative.parts or '\\' in str(relative):
        raise ValueError('Unsafe transfer member: '+str(relative))
    path = (root/str(relative)).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Transfer member leaves project: '+str(relative))
    return path


def source_files(root):
    root = Path(root)
    selected = set()

    def add(path):
        path = Path(path)
        relative = path.relative_to(root).as_posix()
        if any(part in ('.git', '.venv', '__pycache__', '.ipynb_checkpoints') for part in path.relative_to(root).parts):
            return
        if path.name == '.env' or path.name.startswith('.env.') or path.suffix.lower() == '.pyc':
            return
        checked = inside(root, relative)
        if not checked.is_file():
            raise FileNotFoundError(checked)
        selected.add(relative)

    for name in ('README.md', 'AGENTS.md', 'AGENT_HANDOFF.md', 'requirements.txt', '.gitignore'):
        add(root/name)
    for name in ('src', 'scripts', 'tests', 'notebooks', 'config', 'configs', 'docs'):
        for path in (root/name).rglob('*'):
            if path.is_file():
                add(path)
    baseline_path = root/'reports/software_checks/education_deadline_astra_before_20261020.json'
    baseline = json.loads(baseline_path.read_text(encoding='utf-8'))['files']
    add(baseline_path)
    for relative in baseline:
        add(inside(root, relative))
    pointer_path = root/'reports/LATEST_EDUCATION_DEADLINE_COLLECTION.json'
    pointer = json.loads(pointer_path.read_text(encoding='utf-8'))
    add(pointer_path)
    for relative in (pointer['collection_run'], pointer['report_folder'],
                     'data/submissions/education_deadline_astra_20261020',
                     'reports/archive/education_deadline_reporting_20261020'):
        folder = inside(root, relative)
        for path in folder.rglob('*'):
            if path.is_file():
                add(path)
    for relative in (
        'reports/README.md',
        'reports/LATEST_EDUCATION_DEADLINE_PLAN.json',
        'reports/software_checks/education_deadline_astra_20261020.json',
        'reports/software_checks/education_deadline_before_20261019.json',
        'reports/software_checks/education_deadline_20261019.json',
        'reports/logs/education_deadline_astra_20261020/offline_tests.log',
        'handoff/constraints_analysis_python312.txt',
        'handoff/environment_source_20261020.json',
    ):
        add(root/relative)
    missing_baseline = set(baseline)-selected
    if missing_baseline:
        raise ValueError('Required preservation evidence was excluded: '+str(sorted(missing_baseline)[:5]))
    return sorted(selected)


def build(output, root=ROOT):
    root, output = Path(root).resolve(), Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError('Choose a new bundle filename; existing transfers are preserved: '+str(output))
    names = source_files(root)
    hashes = {}
    sizes = {}
    for name in names:
        data = inside(root, name).read_bytes()
        hashes[name] = hashlib.sha256(data).hexdigest()
        sizes[name] = len(data)
    baseline = json.loads((root/'reports/software_checks/education_deadline_astra_before_20261020.json').read_text(encoding='utf-8'))['files']
    for name, expected in baseline.items():
        if hashes[name] != expected:
            raise ValueError('Earlier evidence changed before transfer: '+name)
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True)
    status = subprocess.run(['git', 'status', '--porcelain'], cwd=root, capture_output=True, text=True)
    manifest = dict(date=DATE, purpose='Executable source and evidence for the completed Astra collection and separate future-study preparation.',
        source_root=str(root), reference_git_commit=commit.stdout.strip() if commit.returncode == 0 else None,
        working_files_are_authoritative=True, working_tree_dirty=bool(status.stdout.strip()) if status.returncode == 0 else None,
        required_python='3.12', exact_source_python='3.12.8',
        collection_id='education_deadline_observed_d30e00f21698e1ce',
        parent_study_id='education_deadline_32c0be7299465c2c',
        earlier_preserved_files=len(baseline), file_count=len(hashes), uncompressed_bytes=sum(sizes.values()),
        byte_preserving=True, exclusions=['.git', '.venv', 'environment secrets', 'caches', 'unrelated historical archive files'],
        original_external_locations_rechecked=False, model_calls=0,
        files_sha256=hashes)
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False)+'\n').encode('utf-8')
    # Each archive member is copied from the bytes verified above; never normalize text.
    with ZipFile(output, 'x', compression=ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for name in names:
            data = inside(root, name).read_bytes()
            if hashlib.sha256(data).hexdigest() != hashes[name]:
                raise ValueError('File changed while building transfer: '+name)
            info = ZipInfo(name, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
        info = ZipInfo('HANDOFF_FILES_SHA256.json', date_time=(2026, 10, 20, 0, 0, 0))
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, manifest_bytes)
    with ZipFile(output) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(names) | {'HANDOFF_FILES_SHA256.json'}:
            raise ValueError('Transfer archive integrity check failed.')
        for name, expected in hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError('Transfer archive differs from verified working file: '+name)
    checksum = hashlib.file_digest(output.open('rb'), 'sha256').hexdigest()
    checksum_path = output.with_suffix(output.suffix+'.sha256')
    with checksum_path.open('x', encoding='ascii', newline='\n') as stream:
        stream.write(checksum+'  '+output.name+'\n')
    manifest_path = output.with_suffix('.files.json')
    with manifest_path.open('xb') as stream:
        stream.write(manifest_bytes)
    return dict(bundle=str(output), sha256=checksum, checksum_file=str(checksum_path),
                manifest_file=str(manifest_path), file_count=len(names),
                bundle_bytes=output.stat().st_size, uncompressed_bytes=sum(sizes.values()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'handoff/Beer_Game_Agent_Handoff_20261020.zip')
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))


if __name__ == '__main__':
    main()
