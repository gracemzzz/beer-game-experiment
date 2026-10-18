"""Full 500-identity synthetic accounting/export check; never model evidence."""
from pathlib import Path
import json
import sys
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study.deadline_cohort import DeadlineConfig,prepare,read,synthetic_response,import_response
from beergame_study.deadline_cohort_report import build_report

ROOT=Path(__file__).resolve().parents[1]

def main():
    parent=ROOT/'data/software_checks';parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='deadline-scale-',dir=parent) as temporary:
        root=Path(temporary).resolve()
        assert root.is_relative_to(parent.resolve())  # Cleanup stays within the explicit test directory.
        with patch('openai.OpenAI',side_effect=AssertionError('API forbidden')),patch('anthropic.Anthropic',side_effect=AssertionError('API forbidden')):
            run=prepare(DeadlineConfig(synthetic=True,study_label='full-scale-software-control'),root=root)
            plan=read(run/'plan.json')
            for task in plan['tasks']:
                import_response(run,task['task_id'],synthetic_response(run,task['task_id']),model_label='GPT-6',effort_label='pro',
                    session_label='synthetic-control',confirm_full_prompt=True,evidence_kind='synthetic_test')
            result=build_report(run)
            assert result['complete'] and plan['expected_responses']==20 and plan['fictional_identities']==500
            assert len(result['rounds'])==72000 and int((result['rounds'].phase=='model').sum())==40000
            assert len(result['probes'])==2000 and len(result['tables']['contrasts'])==250
            assert len(result['tables']['repeat_variation'])==250
            assert (result['tables']['hypotheses'].brief_minus_ample==0).all()
            assert (result['tables']['choice_changes'].changed==0).all()
            assert len(result['images'])==6 and (result['folder']/'RESULTS.xlsx').exists()
            assert not (root/'reports/LATEST_DEADLINE_COHORT_REPORT.json').exists()
            record=dict(status='passed',synthetic_only=True,api_calls=0,fictional_identities=500,expected_responses=20,
                submitted_orders=40000,replayed_states=72000,probe_pairs=2000,matched_chain_generation_pairs=250,
                repeat_condition_chain_pairs=250,figures=6,workbook=True,temporary_control_removed=True)
    path=ROOT/'reports/software_checks/deadline_scale_20261018.json'
    path.write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record,indent=2))

if __name__=='__main__':main()
