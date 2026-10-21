"""Offline integrity and navigation checks for the experiment folder migration."""
from pathlib import Path
import hashlib
import json
import re
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import legacy_workspace as legacy
import reorganize_experiments as migration


class LayoutTests(unittest.TestCase):
    def test_complete_original_inventory_preserved(self):
        result=migration.verify(ROOT)
        self.assertEqual(result['tracked_files_verified'],39589)
        self.assertTrue(result['original_current_checkout_bytes_unchanged'])

    def test_all_historical_experiments_have_expected_sections(self):
        for identifier,title,description in migration.EXPERIMENTS.values():
            base=ROOT/'experiments'/identifier
            metadata=json.loads((base/'EXPERIMENT.json').read_text())
            self.assertTrue((base/metadata['primary_report']).is_file())
            for section in ['hypotheses','prompts','data','analysis','reports','notebooks']:
                self.assertTrue((base/section/'README.md').is_file(),str(base/section))
            notebook=json.loads((base/'notebooks/review_saved_results.ipynb').read_text())
            for cell in notebook['cells']:
                if cell['cell_type']=='code':
                    compile(''.join(cell['source']),str(base),mode='exec')

    def test_new_historical_navigation_links_resolve(self):
        files=[]
        for identifier,_,_ in migration.EXPERIMENTS.values():
            base=ROOT/'experiments'/identifier
            files.append(base/'README.md')
            files += [base/name/'README.md' for name in ['hypotheses','prompts','data','analysis','reports','notebooks']]
        files.append(ROOT/'maintenance/README.md')
        for path in files:
            text=re.sub(r'```.*?```','',path.read_text(),flags=re.S)
            for relative in re.findall(r'\]\(([^)]+)\)',text):
                self.assertTrue((path.parent/relative).exists(),f'{path}: {relative}')

    def test_recovery_requires_the_expected_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'copy.json'
            p.write_bytes(b'{\n  "a": 1\n}\n')
            original=p.read_bytes()
            expected=hashlib.sha256(original.replace(b'\n',b'\r\n')).hexdigest()
            receipt=legacy.hash_confirmed_recovery(p,expected)
            self.assertEqual(receipt['transformation'],'LF_to_CRLF')
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),expected)
            self.assertIsNone(legacy.hash_confirmed_recovery(p,expected))
            before=p.read_bytes()
            with self.assertRaises(ValueError):legacy.hash_confirmed_recovery(p,'0'*64)
            self.assertEqual(p.read_bytes(),before)

    def test_copy_rejects_escaping_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            for path in ['../secret','/etc/passwd','D:/secret','a/../../b','a\\b']:
                with self.assertRaises(ValueError):legacy.inside(Path(tmp),path)

    def test_materializer_does_not_modify_original_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'canonical';root.mkdir()
            path=root/'experiments/saved/prompt.txt';path.parent.mkdir(parents=True)
            path.write_bytes(b'prompt\n')
            expected=hashlib.sha256(path.read_bytes()).hexdigest()
            mapping=root/legacy.MAP;mapping.parent.mkdir(parents=True)
            mapping.write_text(json.dumps({'files':[{'old_path':'data/runs/a/prompt.txt',
                'new_path':'experiments/saved/prompt.txt','sha256':expected}]}))
            target,receipt=legacy.materialize(root,Path(tmp)/'copy')
            self.assertEqual((target/'data/runs/a/prompt.txt').read_bytes(),b'prompt\n')
            self.assertFalse((target/'data/runs/a/prompt.txt').is_symlink())
            (target/'data/runs/a/prompt.txt').write_bytes(b'different copy\n')
            self.assertEqual(path.read_bytes(),b'prompt\n')
            self.assertFalse(receipt['canonical_bytes_changed'])
            with self.assertRaises(ValueError):legacy.materialize(root,target)


if __name__=='__main__':unittest.main()
