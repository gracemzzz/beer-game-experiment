"""Offline controls for manual imports, replay and honest cohort summaries."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from beergame_study.manual_cohort import (CohortConfig,prepare,read,progress,next_task,import_response,
    validate_response,synthetic_response,replay,audit,accepted_path,prompt_text)
from beergame_study.manual_cohort_report import summarize,ratio,build_report


class ManualCohortTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.config=CohortConfig(students=8,batch_students=4,synthetic=True,study_label='software-test')
        self.run=prepare(self.config,root=self.root)

    def tearDown(self):
        self.temp.cleanup()

    def payload(self,stage='initial',batch='b0001'):
        return json.loads(synthetic_response(self.run,batch,stage))

    def put(self,payload):
        return import_response(self.run,payload['batch_id'],payload['stage'],json.dumps(payload),
            model_label=self.config.model_label,effort_label='high',session_label='test-session',
            evidence_kind='synthetic_test',confirm_full_prompt=True)

    def paired(self,initial=None,revision=None):
        self.put(initial or self.payload())
        self.put(self.payload(batch='b0002'))
        self.put(revision or self.payload('revision'))

    def test_plan_counts_and_frozen_model(self):
        p=read(self.run/'plan.json')
        self.assertEqual(p['fictional_identities'],8)
        self.assertEqual(p['condition_trajectories'],16)
        self.assertEqual(p['expected_responses'],4)
        self.assertEqual(prepare(self.config,root=self.root),self.run)
        self.assertNotEqual(prepare(CohortConfig(students=8,batch_students=8,synthetic=True),root=self.root),self.run)

    def test_config_requires_complete_chains(self):
        for kwargs in ({'students':501},{'batch_students':99},{'weeks':4},{'effort_label':'low'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):CohortConfig(**kwargs).validate()

    def test_no_model_fixture_in_actual_study(self):
        real=prepare(CohortConfig(students=4,batch_students=4),root=self.root)
        with self.assertRaises(ValueError):synthetic_response(real,'b0001','initial')

    def test_fenced_json_and_integer_checks(self):
        p=self.payload();text='```json\n'+json.dumps(p)+'\n```'
        self.assertEqual(validate_response(self.run,'b0001','initial',text),p)
        for invalid in (-1,3.5,True,None,100001):
            q=copy.deepcopy(p);q['chains'][0]['orders'][0][0]=invalid
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                validate_response(self.run,'b0001','initial',json.dumps(q))

    def test_truncation_extra_text_and_duplicate_keys(self):
        text=json.dumps(self.payload())
        for broken in (text[:-1],'Here it is: '+text,text.replace('"complete": true','"complete": true, "complete": true')):
            with self.assertRaises(ValueError):validate_response(self.run,'b0001','initial',broken)

    def test_missing_week_wrong_id_and_extra_metrics(self):
        p=self.payload()
        for mutate in (lambda x:x['chains'][0]['orders'].pop(),
                       lambda x:x['chains'][0].update(chain_id='missing'),
                       lambda x:x.update(cost=42),lambda x:x['chains'].append(x['chains'][0])):
            q=copy.deepcopy(p);mutate(q)
            with self.assertRaises(ValueError):validate_response(self.run,'b0001','initial',json.dumps(q))

    def test_rules_failure_raw_attempt_preserved(self):
        p=self.payload();p['rules']['three_week_backlog_cost']=5
        with self.assertRaises(ValueError):self.put(p)
        self.assertEqual(len(list((self.run/'attempts').glob('*.txt'))),1)
        self.assertFalse(accepted_path(self.run,'b0001','initial').exists())

    def test_no_replacement_of_valid_output(self):
        self.put(self.payload())
        with self.assertRaises(ValueError):self.put(self.payload())
        self.assertEqual(len(list((self.run/'attempts').glob('*.txt'))),1)

    def test_model_and_confirmation_required(self):
        p=self.payload()
        args=dict(model_label='different',effort_label='high',session_label='test',evidence_kind='synthetic_test',confirm_full_prompt=True)
        with self.assertRaises(ValueError):import_response(self.run,'b0001','initial',json.dumps(p),**args)
        args['model_label']=self.config.model_label;args['confirm_full_prompt']=False
        with self.assertRaises(ValueError):import_response(self.run,'b0001','initial',json.dumps(p),**args)

    def test_revision_requires_initial(self):
        with self.assertRaises(ValueError):self.put(self.payload('revision'))
        with self.assertRaises(FileNotFoundError):prompt_text(self.run,'b0001','revision')

    def test_next_task_initial_batches_first(self):
        self.assertEqual(next_task(self.run)['stage'],'initial')
        self.put(self.payload())
        self.assertEqual(next_task(self.run)['batch_id'],'b0002')
        with self.assertRaises(ValueError):self.put(self.payload('revision'))
        self.put(self.payload(batch='b0002'))
        self.assertEqual(next_task(self.run)['stage'],'revision')

    def test_zero_orders_are_valid_and_h3_matches_known_sequence(self):
        initial,revision=self.payload(),self.payload('revision')
        initial['chains'][0]['orders']=[[2*(i%2)]*4 for i in range(20)]
        revision['chains'][0]['orders']=[[1]*4 for _ in range(20)]
        self.paired(initial,revision)
        rows,probes,_=replay(self.run)
        h=summarize(rows,probes)['hypotheses'].set_index('hypothesis')
        demands=read(self.run/'plan.json')['chains'][0]['customer_demand'][4:]
        expected=np.var([2*(i%2) for i in range(20)],ddof=1)/np.var(demands,ddof=1)
        self.assertAlmostEqual(h.loc['H3','initial_minus_revision'],expected)
        self.assertEqual(h.loc['H3','direction'],'predicted direction')

    def test_tampered_plan_and_raw_are_detected(self):
        self.put(self.payload())
        raw=next((self.run/'attempts').glob('*.txt'));raw.write_text('{}',encoding='utf-8')
        with self.assertRaises(ValueError):replay(self.run,paired_only=False)
        path=self.run/'plan.json';p=read(path);p['chains'][0]['customer_demand'][5]+=1
        path.write_text(json.dumps(p),encoding='utf-8')
        with self.assertRaises(ValueError):audit(self.run)

    def test_only_complete_pairs_enter_comparison(self):
        self.put(self.payload())
        self.assertTrue(replay(self.run)[0].empty)
        self.assertFalse(replay(self.run,paired_only=False)[0].empty)

    def test_equal_conditions_give_null_and_no_p_values(self):
        self.paired()
        rows,probes,_=replay(self.run)
        t=summarize(rows,probes)
        self.assertTrue((t['hypotheses'].initial_minus_revision==0).all())
        self.assertTrue(t['hypotheses'].p_value.isna().all())
        self.assertEqual(len(rows),2*4*36)
        self.assertEqual(len(rows[rows.phase=='model']),2*4*20)

    def test_h1_positive_and_opposite_controls(self):
        self.paired()
        rows,probes,_=replay(self.run)
        for initial_sensitivity,direction in [(0,'predicted direction'),(2,'opposite direction')]:
            p=probes.copy();p.loc[p.condition=='initial','sensitivity']=initial_sensitivity
            h=summarize(rows,p)['hypotheses'].set_index('hypothesis')
            self.assertEqual(h.loc['H1','direction'],direction)

    def test_known_variance_formula_and_undefined_reference(self):
        self.assertEqual(ratio([0,2,0,2],[0,1,0,1]),4)
        self.assertTrue(np.isnan(ratio([0,2,0,2],[4,4,4,4])))

    def test_physical_cost_and_terminal_orders(self):
        self.paired()
        rows,_,_=replay(self.run)
        self.assertTrue(np.allclose(rows.cost,.5*rows.inventory+rows.backlog))
        for _,g in rows.groupby(['chain_id','condition','role']):
            last=g[g.phase=='model'].sort_values('week').iloc[-1]
            self.assertTrue((g.loc[g.phase=='automatic','order']==last.order).all())
            self.assertTrue((g.loc[g.phase=='automatic','customer_demand']==last.customer_demand).all())

    def test_report_waiting_and_partial_are_labeled(self):
        empty=build_report(self.run)
        self.assertIn('awaiting pasted responses',empty['report'].read_text())
        self.assertFalse(empty['images'])

if __name__=='__main__':unittest.main()
