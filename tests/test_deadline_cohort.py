"""Offline controls for independent deadline conditions and repeated generation accounting."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study.deadline_cohort import (DeadlineConfig,prepare,read,prompt_text,progress,import_response,
    synthetic_response,validate_response,load_accepted,accepted_path,replay,next_task,audit)
from beergame_study.deadline_cohort_report import summarize,build_report


class DeadlineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.cfg=DeadlineConfig(students=4,batch_students=4,synthetic=True,study_label='test')
        self.run=prepare(self.cfg,root=self.root)
        self.tasks=read(self.run/'plan.json')['tasks']

    def tearDown(self):self.tmp.cleanup()

    def payload(self,task):return json.loads(synthetic_response(self.run,task))

    def put(self,task,payload=None):
        text=json.dumps(payload or self.payload(task))
        return import_response(self.run,task,text,model_label='GPT-6',effort_label='pro',session_label='mock',
                               confirm_full_prompt=True,evidence_kind='synthetic_test')

    def test_plan_repeats_reuse_identities_and_all_prompts_exist(self):
        plan=read(self.run/'plan.json')
        self.assertEqual(plan['fictional_identities'],4)
        self.assertEqual(plan['generation_role_trajectories'],16)
        self.assertEqual(len(plan['chains']),1);self.assertEqual(len(plan['tasks']),4)
        for t in self.tasks:
            self.assertTrue((self.run/'prompts'/(t['task_id']+'.txt')).exists())
        self.assertEqual(prepare(self.cfg,root=self.root),self.run)

    def test_conditions_independent_of_prior_acceptance(self):
        task=self.tasks[1]['task_id'];before=prompt_text(self.run,task)
        self.assertNotIn('initial_submission',before)
        self.assertNotIn('RECONSIDERATION PASS',before)
        self.put(task)  # Any scheduled condition can be imported without its counterpart.
        self.assertEqual(prompt_text(self.run,task),before)
        self.assertEqual(next_task(self.run)['task_id'],self.tasks[0]['task_id'])

    def test_reject_wrong_id_deadline_missing_order_float_duplicate(self):
        task=self.tasks[0]['task_id'];base=self.payload(task)
        for mutate in (lambda p:p.update(task_id='wrong'),lambda p:p.update(deadline_seconds=1),
                       lambda p:p['chains'][0]['orders'].pop(),lambda p:p['chains'][0]['orders'][0].__setitem__(0,2.5),
                       lambda p:p['chains'][0]['orders'][0].__setitem__(0,True)):
            p=copy.deepcopy(base);mutate(p)
            with self.assertRaises(ValueError):validate_response(self.run,task,json.dumps(p))
        with self.assertRaises(ValueError):validate_response(self.run,task,json.dumps(base).replace('"complete": true','"complete": true, "complete": true'))

    def test_prospective_type_conversion_preserves_original_and_decisions(self):
        task=self.tasks[0]['task_id'];p=self.payload(task)
        p['rules']={'backlog_includes_current_unfilled_demand':'Yes','factory_order_week_7_arrival_week':'Week 10','three_week_backlog_cost':'$15'}
        e=self.put(task,p)
        self.assertEqual(len(e['formatting_edits']),3)
        self.assertEqual(read(self.run/e['raw_path'])['rules'],p['rules'])
        self.assertEqual(e['payload']['chains'],p['chains']);load_accepted(self.run,task)

    def test_incorrect_rules_not_repaired_and_failure_retained(self):
        task=self.tasks[0]['task_id'];p=self.payload(task);p['rules']['three_week_backlog_cost']='$99'
        with self.assertRaises(ValueError):self.put(task,p)
        self.assertFalse(accepted_path(self.run,task).exists())
        self.assertEqual(len(list((self.run/'attempts').glob('*.txt'))),1)

    def test_immutable_acceptance_and_raw_tamper_detection(self):
        task=self.tasks[0]['task_id'];e=self.put(task)
        with self.assertRaises(ValueError):self.put(task)
        p=self.run/e['raw_path'];p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaises(ValueError):load_accepted(self.run,task)

    def test_source_and_plan_hashes(self):
        audit(self.run)
        plan=read(self.run/'plan.json');plan['fictional_identities']=999
        (self.run/'plan.json').write_text(json.dumps(plan))
        with self.assertRaises(ValueError):audit(self.run)

    def test_settings_and_synthetic_separation(self):
        task=self.tasks[0]['task_id']
        with self.assertRaises(ValueError):import_response(self.run,task,synthetic_response(self.run,task),
            model_label='other',effort_label='pro',session_label='test',confirm_full_prompt=True,evidence_kind='synthetic_test')
        actual=prepare(DeadlineConfig(students=4,batch_students=4),root=self.root)
        with self.assertRaises(ValueError):synthetic_response(actual,task)

    def test_complete_null_controls_and_physical_replay(self):
        for t in self.tasks:self.put(t['task_id'])
        rounds,probes,_=replay(self.run);tables=summarize(rounds,probes)
        self.assertEqual(len(rounds),4*4*36);self.assertEqual(len(probes),16)
        self.assertEqual(len(tables['contrasts']),2);self.assertEqual(len(tables['repeat_variation']),2)
        self.assertTrue((tables['hypotheses'].brief_minus_ample==0).all())
        self.assertTrue((tables['choice_changes'].changed==0).all())
        np.testing.assert_array_equal(rounds.cost,.5*rounds.inventory+rounds.backlog)
        self.assertIsNone(next_task(self.run))

    def test_nonzero_variance_and_probe_controls(self):
        for t in self.tasks:
            p=self.payload(t['task_id'])
            if t['condition']=='brief':
                p['chains'][0]['orders']=[[2*(i%2)]*4 for i in range(20)]
                p['chains'][0]['probes']=[[8,8]]*4
            else:p['chains'][0]['orders']=[[1]*4 for _ in range(20)]
            self.put(t['task_id'],p)
        rounds,probes,_=replay(self.run);tables=summarize(rounds,probes)
        h=tables['hypotheses'].set_index('hypothesis')
        self.assertAlmostEqual(h.loc['H1','brief_minus_ample'],-4/24)
        demand=read(self.run/'plan.json')['chains'][0]['customer_demand'][4:]
        expected=np.var([2*(i%2) for i in range(20)],ddof=1)/np.var(demand,ddof=1)
        self.assertAlmostEqual(h.loc['H3','brief_minus_ample'],expected)
        self.assertTrue(h.p_value.isna().all())
        self.assertEqual(tables['choice_changes'].query("kind=='between_deadlines'").changed.tolist(),[80,80])

    def test_partial_report_and_full_exports_preserve_raw(self):
        result=build_report(self.run);self.assertFalse(result['complete'])
        self.put(self.tasks[0]['task_id']);result=build_report(self.run)
        self.assertTrue(result['tables']['hypotheses'].empty)
        for t in self.tasks[1:]:self.put(t['task_id'])
        hashes={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.run.rglob('*') if p.is_file()}
        result=build_report(self.run)
        self.assertTrue(result['complete']);self.assertEqual(len(result['images']),6)
        self.assertTrue((result['folder']/'RESULTS.xlsx').exists())
        self.assertEqual(hashes,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in self.run.rglob('*') if p.is_file()})
        self.assertFalse((self.root/'reports/LATEST_DEADLINE_COHORT_REPORT.json').exists())


if __name__=='__main__':unittest.main()
