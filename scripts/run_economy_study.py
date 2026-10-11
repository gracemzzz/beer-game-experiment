"""Run the revised Beer Game. The default is offline and costs nothing."""
import argparse
import asyncio
import getpass
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study.economy_protocol import EconomyConfig
from beergame_study.shared_budget import run_economy_study as run_study
from beergame_study.operational_io import install_windows_file_retry


def masked_key(budget):
    import tkinter as tk
    from tkinter import simpledialog
    window = tk.Tk()
    window.withdraw()
    window.attributes('-topmost', True)
    try:
        return simpledialog.askstring('Revised Beer Game — secure API key',
            f'Fixed-high GPT-6 Luna Flex; additional run cap ${budget:.2f}.\n'
            'All redesign calls combined stay below $2.95; original campaign cap $10.\n'
            'Paste your key here (masked, memory only). Cancel makes no calls.', show='*', parent=window)
    finally:
        window.destroy()


async def main(args):
    config = EconomyConfig(mode=args.mode, weeks=args.weeks, groups_per_condition=args.pairs,
                           budget_usd=args.budget, replicate_id=args.replicate, campaign_id=args.campaign,
                           concurrency=args.concurrency, request_interval_s=args.interval)
    config.validate()
    install_windows_file_retry()
    client = None
    if config.mode == 'api':
        key = os.environ.get('OPENAI_API_KEY')
        if not key:
            key = masked_key(config.budget_usd) if args.prompt_key_gui else getpass.getpass('OpenAI key (hidden): ')
        if not key or not key.strip():
            print('Canceled; no API requests made.', flush=True)
            return 2
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=key.strip(), max_retries=0, timeout=config.timeout_s)
        key = None
    def progress(p):
        stamp = (p['stage'], p['phase'], p['current_week'], p['calibration_completed'], p['groups_complete'])
        if stamp != getattr(progress, 'stamp', None):
            progress.stamp = stamp
            print(f"{p['stage']} | {p['phase']} | calibration {p['calibration_completed']}/16 | "
                  f"week {p['current_week']} | chains {p['groups_complete']}/{p['planned_groups']} | "
                  f"run ${p['estimated_charged_or_reserved_usd']:.3f}/${p['budget_usd']:.2f} | "
                  f"{p.get('reason', '')}", flush=True)
    try:
        directory = await run_study(config, client, calibration_only=args.calibration_only, on_progress=progress,
                                    calibration_run=args.calibration_run)
        print('Raw evidence:', directory, flush=True)
        print('Report:', ROOT/'reports'/directory.name/'REPORT.md', flush=True)
        return 0
    finally:
        if client:
            await client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['offline', 'api'], default='offline')
    parser.add_argument('--weeks', type=int, default=24)
    parser.add_argument('--pairs', type=int, default=1)
    parser.add_argument('--budget', type=float, default=2.20)
    parser.add_argument('--campaign', default='20261011', help='Changing this requires a separately authorized campaign cap.')
    parser.add_argument('--replicate', default='economy-pilot-01')
    parser.add_argument('--concurrency', type=int, default=4)
    parser.add_argument('--interval', type=float, default=1.0)
    parser.add_argument('--calibration-only', action='store_true')
    parser.add_argument('--calibration-run', type=Path)
    parser.add_argument('--prompt-key-gui', action='store_true')
    raise SystemExit(asyncio.run(main(parser.parse_args())))
