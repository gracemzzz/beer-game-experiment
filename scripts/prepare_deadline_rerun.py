"""Prepare separate assistant-pilot and 500-identity website plans, without model calls."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study.deadline_cohort import DeadlineConfig,prepare,next_task
from beergame_study.deadline_cohort_report import build_report

def main():
    pilot=prepare(DeadlineConfig(students=16,batch_students=16,seed=2026101801,
        study_label='deadline-assistant-fullgame-pilot-01',model_label='current-assistant-inherited',
        effort_label='inherited',collection='isolated_assistant'))
    website=prepare(DeadlineConfig())
    for label,run in [('assistant pilot',pilot),('website collection',website)]:
        result=build_report(run)
        print(label,run)
        print('Report:',result['report'])
        task=next_task(run);print('Next:',task['prompt_path'] if task else 'complete')

if __name__=='__main__':main()
