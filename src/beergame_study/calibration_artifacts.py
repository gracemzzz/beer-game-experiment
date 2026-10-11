"""Create a reusable calibration checkpoint without any model requests."""
import json
import shutil
from pathlib import Path

import pandas as pd

from .reasoning_protocol import ReasoningConfig, StudyStopped, save
from .student_study import load_calibration


def _copy_identical(source, destination):
    if destination.exists():
        if destination.read_bytes() != source.read_bytes():
            raise StudyStopped('Existing checkpoint differs; no evidence overwritten.')
    else:
        shutil.copy2(source, destination)


def _save_identical(path, value):
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8')) != value:
            raise StudyStopped('Existing checkpoint metadata differs; no evidence overwritten.')
    else:
        save(path, value)


def make_calibration_snapshot(run_directory):
    source = Path(run_directory).resolve()
    manifest = json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    config = ReasoningConfig(**manifest['config'])
    rows = pd.read_csv(source/'calibration.csv')
    pairs = set(zip(rows['item'], rows['cap']))
    expected = {(i, cap) for i in range(24) for cap in (*config.candidate_caps, config.reference_tokens)}
    if len(rows) != len(expected) or pairs != expected or not (source/'calibration_recommendation.json').exists():
        raise StudyStopped('A full matched calibration is required before creating its checkpoint.')
    target = source/'calibration_checkpoint'
    target.mkdir(exist_ok=True)
    for name in ('calibration.csv', 'calibration_recommendation.json', 'calibration_import.json'):
        path = source/name
        if path.exists():
            _copy_identical(path, target/name)
    for folder in ('requests', 'source_implementation'):
        (target/folder).mkdir(exist_ok=True)
        for path in (source/folder).glob('*.json' if folder == 'requests' else '*.py'):
            if folder == 'requests':
                record = json.loads(path.read_text(encoding='utf-8'))
                if record.get('identity', {}).get('stage') != 'calibration':
                    continue
                if record.get('status') == 'pending':
                    raise StudyStopped('Unresolved calibration request cannot enter a completed checkpoint.')
            destination = target/folder/path.name
            _copy_identical(path, destination)
    copied_manifest = dict(manifest, calibration_only=True, execution_scope='calibration_checkpoint',
                           calibration_snapshot_of=str(source),
                           snapshot_interpretation='Byte-identical copies of existing calibration; no new calls, spending, or independent observations.')
    _save_identical(target/'manifest.json', copied_manifest)
    charges = sum(json.loads(p.read_text(encoding='utf-8')).get('charge_usd', 0) for p in (target/'requests').glob('*.json'))
    _save_identical(target/'progress.json', dict(phase='complete', stage='calibration_complete', calibration_only=True,
         mode=config.mode, calibration_completed=len(rows), calibration_expected=len(rows),
         planned_groups=0, groups_complete=0, decisions=0, fallback_decisions=0,
         estimated_charged_or_reserved_usd=charges, budget_usd=config.budget_usd,
         run_directory=str(target), snapshot_of=str(source), additional_spending_usd=0))
    load_calibration(target, config)
    from .student_report import build_report
    build_report(target)
    (target/'CHECKPOINT_NOTE.txt').write_text(
        'Reusable copies of the completed calibration from '+str(source)+'.\n'
        'No API calls were made to create this checkpoint. Do not count copies as additional observations or spending.\n',
        encoding='utf-8')
    return target
