"""Prepare copy-and-paste cohort prompts, without contacting a model."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study.manual_cohort import CohortConfig, prepare
from beergame_study.manual_cohort_report import build_report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--students',type=int,default=500)
    p.add_argument('--batch-students',type=int,default=100)
    p.add_argument('--weeks',type=int,default=24)
    p.add_argument('--repetitions',type=int,default=1)
    p.add_argument('--seed',type=int,default=20261017)
    p.add_argument('--label',default='cohort-500-first-plan')
    p.add_argument('--model',default='GPT-6 Astra')
    a=p.parse_args()
    run=prepare(CohortConfig(students=a.students,batch_students=a.batch_students,weeks=a.weeks,
                             repetitions=a.repetitions,seed=a.seed,study_label=a.label,model_label=a.model))
    result=build_report(run)
    print('Run:',run)
    print('Prompts:',run.parents[2]/'reports'/run.name/'PROMPTS.md')
    print('Report:',result['report'])
