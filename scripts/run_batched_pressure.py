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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment', type=Path, default=ROOT / 'experiments/12_pressure_framing_api_20261020')
    parser.add_argument('--run', type=Path, help='Review/resume a particular frozen run.')
    parser.add_argument('--api', action='store_true', help='Make paid calls within the authorized shared $5 cap.')
    parser.add_argument('--phase', choices=('pilot', 'main', 'all'), default='all')
    args = parser.parse_args()
    run = args.run or prepare(args.experiment)
    print('Run:', run)
    print(json.dumps(estimate(run), indent=2))
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
            runner = Runner(run, keys, callback=progress)
            asyncio.run(runner.execute(args.phase))
            runner.keys.clear()
    finally:
        keys.clear()
        exported = build_report(run)
        print('Report:', exported['report'])
        print('Workbook:', exported['workbook'])


if __name__ == '__main__':
    main()
