"""Cross-provider spending policy; preserves the completed GPT scientific sources."""
from dataclasses import replace
import json
from pathlib import Path
import shutil

from .reasoning_protocol import StudyStopped, digest, save

LEGACY_SPEND = 5.19360675
REDESIGN_CAP = 2.95
PROTOCOLS = ('student-high-anytime-revision-v2', 'student-high-economy-revision-v3',
             'student-high-claude-revision-v4')


def campaign_allowance(config, directory, root):
    if config.mode != 'api' or config.campaign_id != '20261011':
        return config, 0.0
    other = LEGACY_SPEND
    for manifest_path in (Path(root) / 'data/runs').glob('*_api_*/manifest.json'):
        if manifest_path.parent.resolve() == Path(directory).resolve():
            continue
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('protocol') in PROTOCOLS and manifest['config']['campaign_id'] == config.campaign_id:
            other += sum(json.loads(p.read_text(encoding='utf-8')).get('charge_usd', 0)
                         for p in (manifest_path.parent / 'requests').glob('*.json'))
    cap = min(config.budget_usd, 10.0 - other, REDESIGN_CAP - (other - LEGACY_SPEND))
    if cap <= 0:
        raise StudyStopped('The shared cross-provider campaign/redesign allowance is exhausted.')
    return replace(config, budget_usd=cap), other


async def run_economy_study(config, client=None, *, root=None, calibration_only=False,
                            on_progress=None, calibration_run=None):
    """Use the frozen Luna experiment with a current, cross-provider budget check.

    The shared campaign lock is held before reading other-provider charges. This
    wrapper changes spending accounting only, and records its own provenance for
    new API runs. Completed raw runs return untouched. Offline work delegates to
    the original runner. No monkey patching of its scientific modules is used.
    """
    from . import economy_study as study
    root = Path(root or study.ROOT)
    if config.mode != 'api':
        return await study.run_study(config, client, root=root, calibration_only=calibration_only,
                                     on_progress=on_progress, calibration_run=calibration_run)
    directory = study.prepare(config, root, calibration_only, calibration_run)
    progress_path = directory / 'progress.json'
    if progress_path.exists():
        saved = json.loads(progress_path.read_text(encoding='utf-8'))
        if saved.get('phase') == 'complete':
            if saved.get('stage') == 'calibration_complete' and not calibration_only:
                raise StudyStopped('Completed calibration is immutable. Start games with a new replicate ID and calibration_run pointing to this run.')
            return directory
    lock_path = root / 'data/campaigns' / (digest(config.campaign_id)[:16] + '.lock')
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock = lock_path.open('x', encoding='utf-8')
    except FileExistsError:
        raise StudyStopped('A live campaign lock exists. Do not start concurrent paid workers.') from None
    try:
        lock.write(str(directory)); lock.flush()
        effective, prior = campaign_allowance(config, directory, root)
        policy = directory / 'operational_budget_policy.json'
        if not policy.exists():
            source = Path(__file__)
            snapshot = directory / 'source_implementation/shared_budget.py'
            shutil.copy2(source, snapshot)
            save(policy, dict(policy='cross-provider-v1', source_sha256=digest(source.read_text(encoding='utf-8')),
                              protocols=list(PROTOCOLS), redesign_cap=REDESIGN_CAP,
                              change='Operational spending accounting only; scientific configuration unchanged.'))
        return await study._run(effective, client, directory, root, prior, calibration_only,
                                on_progress, calibration_run)
    finally:
        lock.close()
        lock_path.unlink(missing_ok=True)
