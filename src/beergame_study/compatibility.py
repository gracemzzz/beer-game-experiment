"""Audited calibration portability for changes confined to onboarding/reporting."""
import ast,hashlib,json
from pathlib import Path

def decision_fingerprint(source=None):
    source=Path(source) if source else Path(__file__).parent
    parts={}
    selectors={'prompts.py':{'COMMON','SCHEMA','make_messages','validate_decision'},
               'runner.py':{'decision'},'config.py':{'MODEL','PROTOCOL','RATES'}}
    for file,names in selectors.items():
        nodes=ast.parse((source/file).read_text()).body
        for name in sorted(names):
            found=[n for n in nodes if getattr(n,'name',None)==name or
                   isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
            if len(found)!=1:raise ValueError(f'Cannot identify {file}:{name}')
            parts[file+':'+name]=ast.dump(found[0],include_attributes=False)
    for file in ('api.py','game.py'):
        parts[file]=hashlib.sha256((source/file).read_bytes()).hexdigest()
    return hashlib.sha256(json.dumps(parts,sort_keys=True).encode()).hexdigest()


def calibration_code_compatible(directory, manifest):
    """Never relabel an old calibration as if it ran the new onboarding code."""
    current=decision_fingerprint()
    if manifest.get('decision_fingerprint')==current:return True
    exact={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}
    if manifest.get('source_sha256')==exact:return True
    bridge=Path(directory)/'onboarding_compatibility.json'
    if not bridge.exists():return False
    record=json.loads(bridge.read_text())
    return (record.get('decision_fingerprint')==current and
            record.get('calibration_source_sha256')==manifest.get('source_sha256'))
