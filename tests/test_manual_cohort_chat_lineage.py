"""Offline controls for carrying the unchanged first response into UI settings v2."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from beergame_study import manual_cohort as old
from beergame_study import manual_cohort_chat as new


class ChatLineageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.parent = old.prepare(old.CohortConfig(students=8, batch_students=4, synthetic=True), root=self.root)
        self.raw = old.synthetic_response(self.parent, 'b0001', 'initial')
        self.path = self.parent / 'inbox/first.txt'
        self.path.write_text(self.raw, encoding='utf-8')
        self.hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.parent.rglob('*') if p.is_file()}
        self.config = new.CohortConfig(students=8, batch_students=4, synthetic=True,
                                      lineage=new.lineage_for(self.parent, self.path))
        self.run = new.prepare(self.config, root=self.root)

    def tearDown(self):
        self.temp.cleanup()

    def put(self, raw, batch='b0001', stage='initial', effort='pro'):
        return new.import_response(self.run, batch, stage, raw, model_label='GPT-6',
            effort_label=effort, session_label='software-only', evidence_kind='synthetic_test', confirm_full_prompt=True)

    def test_original_payload_and_prompt_preserved_new_fingerprint(self):
        entry = self.put(self.raw)
        self.assertNotEqual(self.run.name, self.parent.name)
        self.assertEqual(entry['payload'], json.loads(self.raw))
        self.assertEqual((self.run/entry['raw_path']).read_bytes(), self.path.read_bytes())
        self.assertEqual(new.prompt_text(self.run, 'b0001', 'initial'), old.prompt_text(self.parent, 'b0001', 'initial'))
        self.assertEqual(new.next_task(self.run)['batch_id'], 'b0002')
        self.assertIn(self.run.name, new.next_task(self.run)['prompt'])
        self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p,h in self.hashes.items()))
        self.assertFalse(old.progress(self.parent).initial.any())

    def test_no_relabeled_or_replacement_first_response(self):
        obj = json.loads(self.raw)
        obj['study_id'] = self.run.name
        with self.assertRaises(ValueError):
            self.put(json.dumps(obj))
        with self.assertRaises(ValueError):
            self.put(self.raw, effort='high')
        self.assertFalse(new.progress(self.run).initial.any())

    def test_tampered_lineage_rejected(self):
        (self.run/'lineage/b0001_initial_prompt.txt').write_text('changed', encoding='utf-8')
        with self.assertRaises(ValueError):
            new.audit(self.run)

    def test_complete_pair_and_replay_with_original_first_id(self):
        self.put(self.raw)
        with self.assertRaises(ValueError):
            self.put(new.synthetic_response(self.run,'b0001','revision'), stage='revision')
        self.put(new.synthetic_response(self.run,'b0002','initial'), batch='b0002')
        self.put(new.synthetic_response(self.run,'b0001','revision'), stage='revision')
        rows, probes, imports = new.replay(self.run)
        self.assertEqual(len(rows), 2*4*36)
        self.assertEqual(len(probes), 8)
        self.assertEqual(imports[0]['model_display_label'], 'GPT-6')
        self.assertEqual(imports[0]['effort_display_label'], 'pro')
        self.assertEqual(imports[0]['carried_from']['parent_study_id'], self.parent.name)


if __name__ == '__main__':
    unittest.main()
