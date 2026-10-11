"""Run the revised study explicitly; secrets never enter files or command arguments."""
import argparse
import asyncio
import getpass
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))

from beergame_study.reasoning_protocol import ReasoningConfig, StudyStopped
from beergame_study.student_study import run_campaign
from beergame_study.operational_io import install_windows_file_retry, record_operational_io


def key_dialog(budget=10.):
    import tkinter as tk
    from tkinter import simpledialog
    window = tk.Tk()
    window.withdraw()
    window.attributes('-topmost', True)
    try:
        return simpledialog.askstring(
            'Beer Game: secure API key entry',
            'Paste your OpenAI API key below (masked).\n'
            'It stays in memory and is not saved.\n'
            f'This run uses GPT-5.4 Mini, fixed high effort, and a ${budget:.2f} hard limit.\n'
            'Cancel makes no API calls.', show='*', parent=window)
    finally:
        window.destroy()


async def main(args):
    config = ReasoningConfig(mode=args.mode, stage='game', budget_usd=args.budget,
                             groups_per_condition=args.groups, replicate_id=args.replicate,
                             request_interval_s=args.interval, concurrency=args.concurrency,
                             weeks=args.weeks)
    config.validate()
    install_windows_file_retry()
    client = None
    if args.mode == 'api':
        key = os.environ.get('OPENAI_API_KEY')
        if not key and args.prompt_key_gui:
            key = key_dialog(config.budget_usd)
        elif not key and args.prompt_key:
            key = getpass.getpass('OpenAI API key (hidden; never saved): ')
        if not key or not key.strip():
            print('No API key supplied. No paid requests made.', flush=True)
            return 2
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=key.strip(), max_retries=0, timeout=config.timeout_s)
        key = None
    try:
        def show_progress(progress):
            if not getattr(show_progress, 'io_recorded', False):
                record_operational_io(progress['run_directory'], {
                    'concurrency': config.concurrency,
                    'request_interval_s': config.request_interval_s,
                    'entrypoint': 'scripts/run_student_reasoning_study.py',
                })
                show_progress.io_recorded = True
            status = (progress['stage'], progress.get('current_week'), progress.get('calibration_completed'), progress.get('phase'))
            if status != getattr(show_progress, 'last', None):
                show_progress.last = status
                print(f"{progress['stage']}: {progress['completed_steps']}/{progress['planned_requests']} steps; "
                      f"week {progress.get('current_week', 0)}; "
                      f"${progress['estimated_charged_or_reserved_usd']:.3f}/${progress['budget_usd']:.2f}; "
                      f"{progress['run_directory']}", flush=True)
        directory = await run_campaign(config, client, calibration_parent=args.resume_calibration,
                                       calibration_only=args.calibration_only,
                                       calibration_run=args.calibration_run, on_progress=show_progress,
                                       recheck_rejections=args.recheck_after_access_change,
                                       correct_calibration_states=args.correct_calibration_states)
        print('Completed:', directory, flush=True)
        print('Report:', directory/'REPORT.md', flush=True)
        return 0
    except StudyStopped as exc:
        print('Stopped:', str(exc), flush=True)
        print('Saved partial report is linked by reports/LATEST_REPORT.txt.', flush=True)
        return 1
    finally:
        if client:
            await client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('offline', 'api'), default='offline')
    parser.add_argument('--budget', type=float, default=10.)
    parser.add_argument('--groups', type=int, default=3, help='Independent chains per condition; default 3.')
    parser.add_argument('--replicate', default='student-high-pilot-01')
    parser.add_argument('--interval', type=float, default=2.)
    parser.add_argument('--concurrency', type=int, default=2)
    parser.add_argument('--weeks', type=int, default=40,
                        help='Decision-period length including four familiarization weeks; minimum 20. Choose before game outcomes.')
    parser.add_argument('--resume-calibration', type=Path,
                        help='Reuse exactly compatible completed calibration request checkpoints; preserve the original run.')
    parser.add_argument('--calibration-only', action='store_true', help='Run calibration without purchasing games.')
    parser.add_argument('--calibration-run', type=Path, help='Use a completed compatible calibration for independent new games.')
    parser.add_argument('--recheck-after-access-change', action='store_true',
                        help='One fresh recheck of a saved zero-charge 429 after credits/limits were explicitly fixed; preserves rejected attempts.')
    parser.add_argument('--correct-calibration-states', action='store_true',
                        help='Import historical calibration charges; replace only the eight receipt/shipment placeholder states, reusing all unchanged prompts.')
    key_options = parser.add_mutually_exclusive_group()
    key_options.add_argument('--prompt-key', action='store_true')
    key_options.add_argument('--prompt-key-gui', action='store_true')
    raise SystemExit(asyncio.run(main(parser.parse_args())))
