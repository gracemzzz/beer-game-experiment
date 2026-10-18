"""Import a saved response into an existing manual chat-settings run; no API calls."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from beergame_study.manual_cohort_chat import import_response, next_task, progress
from beergame_study.manual_response_formatting import build_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--response', type=Path, required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--stage', choices=['initial', 'revision'], required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--effort', choices=['pro', 'high'], required=True)
    parser.add_argument('--chat-label', required=True)
    parser.add_argument('--full-prompt-confirmed', action='store_true', required=True)
    args = parser.parse_args()
    import_response(args.run, args.batch, args.stage, args.response.read_text(encoding='utf-8'),
                    model_label=args.model, effort_label=args.effort, session_label=args.chat_label,
                    confirm_full_prompt=args.full_prompt_confirmed)
    report = build_report(args.run)
    print(progress(args.run).to_string(index=False))
    print('Report:', report['report'])
    task = next_task(args.run)
    print('Next prompt:', task['prompt_path'] if task else 'Complete')


if __name__ == '__main__':
    main()
