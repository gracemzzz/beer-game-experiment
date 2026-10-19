"""Import one exact saved reply and regenerate the independent-deadline report."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study.deadline_cohort import read,import_response,next_task,progress
from beergame_study.hypothesis_alignment import build_report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--task',required=True)
    parser.add_argument('--response',type=Path,required=True);parser.add_argument('--chat-label',required=True)
    parser.add_argument('--full-prompt-confirmed',action='store_true',required=True)
    args=parser.parse_args();cfg=read(args.run/'manifest.json')['config']
    import_response(args.run,args.task,args.response.read_bytes().decode('utf-8'),model_label=cfg['model_label'],
        effort_label=cfg['effort_label'],session_label=args.chat_label,confirm_full_prompt=args.full_prompt_confirmed)
    result=build_report(args.run)
    print(progress(args.run).to_string(index=False));print('Report:',result['report'])
    task=next_task(args.run);print('Next:',task['prompt_path'] if task else 'Complete')

if __name__=='__main__':main()
