"""Monitor safety checks: pending is not zero and unreviewed data cannot infer."""
from pathlib import Path
import json
import tempfile
import unittest
import asyncio
import sys
from unittest.mock import patch

from beergame_study import agent_progress_v5 as progress


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.collection = self.root / progress.COLLECTION
        self.folder = self.collection / 'gpt_astra/run001'
        self.folder.mkdir(parents=True)
        (self.collection / 'COLLECTION_PLAN.json').write_text(json.dumps({'models': [{'slot': 'gpt_astra'}]}))
        (self.folder / 'CASE.json').write_text(json.dumps({'requested_model': 'test model', 'requested_effort': 'high'}))

    def status(self, complete=False):
        (self.folder / 'STATUS.json').write_text(json.dumps(dict(complete=complete, completed_pages=224 if complete else 17,
            planned_pages=224, completed_weeks={'A':24 if complete else 4,'B':24 if complete else 0,'C':24 if complete else 0})))

    def test_partial_does_not_need_result_and_has_no_inference(self):
        self.status()
        s = progress.snapshot(self.root)
        self.assertEqual(s['runs'][0]['completed_pages'],17)
        self.assertEqual(len(s['estimates']),5)
        for row in s['estimates']:
            self.assertIsNone(row['mean_difference'])
            self.assertIsNone(row['p_holm_20'])
        self.assertIn('17/224',progress.html(s))

    def test_one_unreviewed_complete_context_is_descriptive_only(self):
        self.status(True)
        (self.folder / 'RESULT.json').write_text('{}')
        rows = [dict(arm=a, pipeline_sensitivity=i, chain_total_cost=100+i,
                     mean_role_order_variance=3+i, mean_role_bullwhip=2+i) for i,a in enumerate('ABC')]
        with patch.object(progress,'audited_result',return_value=rows):
            s = progress.snapshot(self.root)
        for row in s['estimates']:
            self.assertEqual(row['mean_difference'],1)
            self.assertIsNone(row['p_holm_20'])
            self.assertIsNone(row['ci95_low'])
            self.assertEqual(row['reviewed_contexts'],0)

    def test_transient_checkpoint_write_is_visible_not_a_zero(self):
        (self.folder / 'STATUS.json').write_text('{')
        s = progress.snapshot(self.root)
        self.assertIn('JSONDecodeError',s['runs'][0]['error'])
        self.assertIsNone(s['estimates'][0]['mean_difference'])

    def test_user_time_cap_replaces_ten_run_target_in_monitor(self):
        self.status()
        (self.collection/'REPLICATION_AMENDMENT_01.json').write_text(json.dumps({'target_attempted_contexts_per_model':10}))
        (self.collection/'TIMEBOX_AMENDMENT_02.json').write_text(json.dumps({
            'collection_cutoff_local':'2026-10-25 23:07:34 EDT',
            'delivery_deadline_local':'2026-10-25 23:27:34 EDT'}))
        s=progress.snapshot(self.root)
        self.assertIsNone(s['target_contexts_per_model'])
        rendered=progress.html(s)
        self.assertIn('User-set 90-minute maximum',rendered)
        self.assertIn('23:27:34 EDT',rendered)
        self.assertNotIn('Fixed collection stage: 10',rendered)

    def test_missing_widgets_uses_cancellable_html_auto_refresh(self):
        self.status()
        async def run():
            with patch.dict(sys.modules, {'ipywidgets': None}), patch('IPython.display.display') as display:
                monitor=progress.notebook_monitor(self.root)
                self.assertEqual(monitor['mode'],'plain_html')
                self.assertTrue(monitor['auto'])
                self.assertIn('17/224',display.return_value.update.call_args.args[0].data)
                monitor['close']()
                await asyncio.sleep(0)
                self.assertTrue(monitor['state']['closed'])
        asyncio.run(run())


if __name__ == '__main__':
    unittest.main()
