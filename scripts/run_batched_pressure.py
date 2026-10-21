"""Prepare/review experiment 12, or explicitly run its budgeted API collection."""
from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study.batched_pressure import prepare
from beergame_study.batched_pressure_api import Runner, estimate
from beergame_study.batched_pressure_report import build_report
from beergame_study import batched_pressure_recovery as recovery_study
from beergame_study import batched_pressure_followup as followup_study


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, default=ROOT / 'experiments/12_pressure_framing_api_20261020')
    parser.add_argument('--run', type=Path, help='Review/resume a particular frozen run.')
    parser.add_argument('--recovery', type=Path, help='Review/resume a prepared recovery; preserves the original pilot records.')
    parser.add_argument('--followup', type=Path, help='Review/resume the bounded Claude arithmetic follow-up.')
    parser.add_argument('--api', action='store_true', help='Make paid calls within the authorized shared $5 cap.')
    parser.add_argument('--phase', choices=('pilot', 'main', 'all'), default='all')
    args = parser.parse_args()
    stage = args.followup or args.recovery
    run = stage.resolve().parent.parent if stage else args.run or prepare(args.experiment)
    print('Run:', run)
    print(json.dumps(followup_study.estimate(args.followup) if args.followup else recovery_study.estimate(args.recovery) if args.recovery else estimate(run), indent=2))
    keys = {}
    try:
        if args.api:
            for provider, name in [('openai', 'OPENAI_API_KEY'), ('anthropic', 'ANTHROPIC_API_KEY')]:
                keys[provider] = os.environ.get(name, '')
                if not keys[provider]:
                    if not sys.stdin.isatty():
                        raise RuntimeError('Use the notebook hidden fields or set both API-key environment variables.')
                    keys[provider] = getpass.getpass(provider.title() + ' API key (hidden): ').strip()
            def progress(p):
                print(f"{p['done']}/{p['total']} finished; {p['remaining']} left; "
                      f"{p['accepted']} accepted; {p['failed']} failed; {p['skipped']} blocked; "
                      f"${p['charged_or_reserved_usd']:.4f}/$5", flush=True)
            runner_type = followup_study.Runner if args.followup else recovery_study.Runner if args.recovery else Runner
            runner = runner_type(stage or run, keys, callback=progress)
            asyncio.run(runner.execute(args.phase))
            runner.keys.clear()
    finally:
        keys.clear()
        exported = build_report(run, recovery=args.recovery, followup=args.followup)
        print('Report:', exported['report'])
        print('Workbook:', exported['workbook'])


if __name__ == '__main__':
    main()
