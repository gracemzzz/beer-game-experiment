"""One-time, byte-preserving migration of the tracked 20 October legacy tree.

New/untracked work is never selected. Frozen evidence and scientific source are
not rewritten. The complete mapping also drives the read-only legacy workspace.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = Path('maintenance/reorganization_20261020')
EXPERIMENTS = {
    'early': ('01_early_beer_game_prototypes', 'Early Beer Game prototypes', 'Before 4 October 2026; multiple historical models and protocols'),
    'nano': ('02_nano_token_budget', 'Nano token-budget pilot', 'GPT-5.4 Nano; API decisions and separate offline checks'),
    'budget': ('03_luna_model_comparison', 'Luna model comparison and follow-up', '5 October; Nano/Mini/Luna screen, then GPT-5.6 Luna games'),
    'student': ('04_mini_student_reasoning', 'Mini student-reasoning study', '11 October; GPT-5.4 Mini, fixed-high single-call protocol'),
    'anytime': ('05_mini_deliberation', 'Mini initial decision and revision', '11 October; GPT-5.4 Mini, deliberation protocol v2'),
    'economy': ('06_luna_deliberation', 'Luna initial decision and revision', '11 October; GPT-6 Luna Flex, deliberation protocol v3'),
    'claude': ('07_claude_deliberation', 'Claude initial decision and revision', '11 October; Claude Haiku 5.5, deliberation protocol v4'),
    'manual': ('08_manual_cohort_revision', 'Manual cohort initial decision and revision', '17–18 October; completed user-reported GPT-6 / Pro collection and separate preparations'),
    'pressure': ('09_pressure_prompt_development', 'Static pressure-prompt development', '18 October; bounded isolated-assistant development checks'),
    'deadline': ('10_deadline_cohort', '10-second / 180-second deadline framing', '18 October; completed user-reported GPT-6 / Pro website sample; separate assistant pilot'),
    'education': ('11_education_deadline', '10-second / 60-second education study', '19–20 October; prepared GPT-6 / Pro plan, assistant preflight, received GPT-6 Astra / extra high effort collection'),
}
NOTEBOOKS = {'01': 'nano', '02': 'budget', '03': 'student', '04': 'economy',
             '05': 'claude', '06': 'manual', '07': 'deadline'}
DOCS = {
    'PROTOCOL.md': 'nano', 'ANYTIME_PROTOCOL_20261011.md': 'anytime',
    'CLAUDE_PROTOCOL_20261011.md': 'claude', 'ECONOMY_PROTOCOL_20261011.md': 'economy',
    'DEADLINE_COHORT_PROTOCOL_20261018.md': 'deadline', 'HYPOTHESES_H1_H4.md': 'deadline',
    'EDUCATION_DEADLINE_PROTOCOL_20261019.md': 'education',
    'EDUCATION_DEADLINE_SETTINGS_20261020.md': 'education', 'education_deadline_20261019': 'education',
    'MANUAL_COHORT_PROTOCOL_20261017.md': 'manual', 'MANUAL_CHAT_SETTINGS_20261018.md': 'manual',
    'MANUAL_FORMATTING_NOTE_20261018.md': 'manual',
    'RESEARCH_DESIGN_20261011.md': 'student', 'STUDENT_VALIDATION_20261011.md': 'student',
    'HYPOTHESIS_ANALYSIS_20261011.md': 'student', 'HISTORICAL_AUDIT_20261011.md': 'student',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def family(name):
    name = name.lower()
    for prefix, key in [('education_', 'education'), ('deadline_', 'deadline'),
                        ('manual_', 'manual'), ('pressure_', 'pressure'),
                        ('claude_', 'claude'), ('economy_', 'economy'),
                        ('anytime_', 'anytime'), ('student_', 'student'),
                        ('personality_', 'anytime'), ('budget_', 'budget'),
                        ('model_screen_', 'budget'), ('calibration_metadata_', 'budget'),
                        ('calibration', 'nano'), ('game_', 'nano'), ('onboarding_', 'nano'),
                        ('hypothesis_alignment', 'deadline'), ('notebook03_', 'student'),
                        ('notebook04_', 'economy'), ('notebook05_', 'claude')]:
        if name.startswith(prefix):
            return key
    return None


def experiment_path(key, section, remainder):
    return Path('experiments') / EXPERIMENTS[key][0] / section / remainder


def destination(relative):
    """Return a single canonical destination for every preexisting tracked file."""
    p = Path(relative)
    parts = p.parts
    top = parts[0]
    if top in {'src', 'scripts', 'tests'} or len(parts) == 1 and top not in {'README.md', 'AGENTS.md', 'AGENT_HANDOFF.md'}:
        return p
    if len(parts) == 1:
        return RECEIPTS / 'original_navigation' / p
    if top == 'data':
        kind, name = parts[1], parts[2] if len(parts) > 2 else ''
        key = family(name)
        if kind in {'collections', 'submissions'}:
            key = 'education'
        if kind == 'source' and name == 'reflection_20261019':
            key = 'education'
        if key:
            return experiment_path(key, 'data', Path(*parts[1:]))
        return Path('maintenance/shared_inputs') / p
    if top == 'notebooks':
        key = NOTEBOOKS.get(parts[1][:2])
        if key:
            return experiment_path(key, 'notebooks', Path(*parts[1:]))
        return Path('maintenance/historical_notebooks') / Path(*parts[1:])
    if top == 'docs':
        if parts[1] in DOCS:
            section = 'prompts' if parts[1] == 'education_deadline_20261019' else 'hypotheses'
            return experiment_path(DOCS[parts[1]], section, Path(*parts[1:]))
        return Path('maintenance/guides') / Path(*parts[1:])
    if top == 'config':
        return Path('maintenance/shared_inputs') / p
    if top == 'configs':
        return experiment_path('nano', 'hypotheses', p)
    if top == 'handoff':
        return Path('maintenance/handoff_20261020') / Path(*parts[1:])
    if top == 'archive':
        name = parts[1]
        if name in {'pre_token_budget_20261004', 'migration_20261004.json'}:
            return experiment_path('early', 'data', Path(*parts[1:]))
        key = 'budget' if name.startswith('budget_') else 'nano' if name.startswith(('before_onboarding', 'calibration_')) else None
        if key:
            return experiment_path(key, 'analysis', Path('source_history', *parts[1:]))
        return Path('maintenance/frozen_source_history') / Path(*parts[1:])
    if top == 'reports':
        name = parts[1]
        if name == 'CURRENT_BEER_GAME':
            return experiment_path('deadline', 'reports', Path('current', *parts[2:]))
        if name == 'EDUCATION_DEADLINE_10S_60S':
            return experiment_path('education', 'reports', Path(*parts[2:]))
        if name in {'software_checks', 'logs'}:
            key = family(parts[2]) if len(parts) > 2 else None
            if key:
                return experiment_path(key, 'analysis', Path(*parts[1:]))
            return Path('maintenance/validation_history') / Path(*parts[1:])
        if name.startswith('LATEST') or name == 'README.md':
            return Path('maintenance/historical_navigation/reports') / Path(*parts[1:])
        if name == 'archive':
            kind = parts[2] if len(parts) > 2 else ''
            child = parts[3] if len(parts) > 3 else ''
            if kind in {'studies', 'analysis_versions', 'prompt_catalogs_20261017', '20261005'}:
                key = family(child)
                if child.startswith('pilot_02_game_'):
                    key = 'nano'
                if key:
                    section = 'analysis' if kind == 'analysis_versions' else 'prompts' if kind == 'prompt_catalogs_20261017' else 'reports'
                    return experiment_path(key, section, Path('archive', kind, *parts[3:]))
            if kind == 'hypothesis_alignment_20261018':
                return experiment_path('deadline', 'reports', Path('archive', *parts[2:]))
            if kind == 'education_deadline_reporting_20261020':
                return experiment_path('education', 'analysis', Path('reporting_history', *parts[2:]))
            return Path('maintenance/report_history') / Path(*parts[2:])
        key = family(name)
        if key:
            return experiment_path(key, 'reports', Path(*parts[1:]))
        return Path('maintenance/report_history') / Path(*parts[1:])
    return Path('maintenance/legacy_misc') / p


def migrate(root=ROOT):
    root = Path(root).resolve()
    folder = root / RECEIPTS
    manifest_path = folder / 'FILE_MAP.json'
    if manifest_path.exists():
        raise RuntimeError('Migration already has a saved inventory. Verify it; do not run it again.')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    tracked = [name for name in tracked if name]
    if any(name.startswith(('experiments/', 'maintenance/')) for name in tracked):
        raise RuntimeError('This one-time migration expects the original tracked layout.')
    entries = []
    for name in tracked:
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError('Expected a regular tracked file: '+name)
        target = destination(name).as_posix()
        entries.append(dict(old_path=name, new_path=target, sha256=sha(path), bytes=path.stat().st_size,
                            action='keep' if target == name else 'copy_navigation' if name in {'README.md', 'AGENTS.md', 'AGENT_HANDOFF.md'} else 'move'))
    targets = [entry['new_path'] for entry in entries]
    if len(set(targets)) != len(targets):
        raise RuntimeError('Destination collision in proposed migration.')
    for entry in entries:
        if entry['action'] != 'keep' and (root / entry['new_path']).exists():
            raise RuntimeError('Destination already exists: '+entry['new_path'])
    folder.mkdir(parents=True, exist_ok=True)
    manifest = dict(schema='experiment-layout-migration-v1', created_utc=datetime.now(timezone.utc).isoformat(),
                    source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip(),
                    selection='All and only preexisting git-tracked regular files; newly created/untracked work excluded.',
                    canonical_bytes='Exact bytes present before migration, including preexisting LF normalization.',
                    file_count=len(entries), files=entries)
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    for entry in entries:
        if entry['action'] == 'keep':
            continue
        source, target = root / entry['old_path'], root / entry['new_path']
        target.parent.mkdir(parents=True, exist_ok=True)
        if entry['action'] == 'copy_navigation':
            shutil.copy2(source, target)
        else:
            shutil.move(str(source), str(target))
    # Remove only empty directories; untracked work and caches are never removed.
    for top in ('data', 'reports', 'docs', 'config', 'configs', 'notebooks', 'archive', 'handoff'):
        old = root / top
        if old.exists():
            for directory in sorted((p for p in old.rglob('*') if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
                try:
                    directory.rmdir()
                except OSError:
                    pass
            try:
                old.rmdir()
            except OSError:
                pass
    result = verify(root)
    (folder / 'MIGRATION_CHECK.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def verify(root=ROOT):
    root = Path(root).resolve()
    manifest = json.loads((root / RECEIPTS / 'FILE_MAP.json').read_text(encoding='utf-8'))
    failures = []
    for entry in manifest['files']:
        target = root / entry['new_path']
        if not target.is_file() or sha(target) != entry['sha256']:
            failures.append(entry['new_path'])
    if failures:
        raise AssertionError('Missing or changed migration files: '+repr(failures[:20]))
    return dict(status='passed', checked_utc=datetime.now(timezone.utc).isoformat(),
                tracked_files_verified=len(manifest['files']),
                actions=dict(Counter(entry['action'] for entry in manifest['files'])),
                bytes_verified=sum(entry['bytes'] for entry in manifest['files']),
                original_current_checkout_bytes_unchanged=True,
                historical_crlf_integrity_is_separate=True, model_api_calls=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.apply == args.verify:
        parser.error('Choose --apply once, or --verify.')
    print(json.dumps(migrate() if args.apply else verify(), indent=2))


if __name__ == '__main__':
    main()
