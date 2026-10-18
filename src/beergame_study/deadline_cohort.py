"""Separate whole-cohort deadline-framing study; no API calls or outcome replacement."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

from .game import BeerGame, ROLES
from .student_profiles import profiles, assignment
from .manual_cohort_chat import INSTRUCTIONS, QUESTIONS, RULE_ANSWERS, parse_response, _keys, _matrix
from .manual_response_formatting import normalize_rule_types

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = 'deadline-framed-cohort-v1'
SCHEMA = 'deadline-cohort-trajectories-v1'
CONDITIONS = ('brief', 'ample')
DEADLINES = {'brief': 10, 'ample': 180}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save_new(path, value):
    path = Path(path)
    data = value if isinstance(value, bytes) else (value if isinstance(value, str) else json.dumps(value, indent=2, allow_nan=False)).encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Refusing to overwrite frozen evidence: '+str(path))
    else:
        with path.open('xb') as stream:
            stream.write(data)


@dataclass(frozen=True)
class DeadlineConfig:
    students: int = 500
    batch_students: int = 100
    weeks: int = 24
    generations: int = 2
    seed: int = 2026101802
    study_label: str = 'deadline-500-chat-pro'
    model_label: str = 'GPT-6'
    effort_label: str = 'pro'
    collection: str = 'chat_ui'
    synthetic: bool = False

    def validate(self):
        for name in ('students', 'batch_students'):
            if type(getattr(self, name)) is not int or getattr(self, name) < 4 or getattr(self, name) % 4:
                raise ValueError(name+' must be a positive multiple of four.')
        if type(self.weeks) is not int or not 8 <= self.weeks <= 104:
            raise ValueError('Choose 8-104 weeks prospectively.')
        if type(self.generations) is not int or not 2 <= self.generations <= 10:
            raise ValueError('Use at least two generation repeats, at most ten.')
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ValueError('Invalid seed.')
        if self.collection not in ('chat_ui', 'isolated_assistant') or not self.model_label.strip():
            raise ValueError('Record collection mode and model label.')
        if self.effort_label not in (('high', 'pro') if self.collection == 'chat_ui' else ('inherited',)):
            raise ValueError('Use a fixed reported setting; inherited assistant settings are not UI Pro.')
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', self.study_label) or type(self.synthetic) is not bool:
            raise ValueError('Invalid study label or synthetic flag.')
        return self


def source_files():
    folder = Path(__file__).parent
    names = ['deadline_cohort.py', 'deadline_cohort_report.py', 'manual_cohort_chat.py',
             'manual_response_formatting.py', 'game.py', 'student_profiles.py']
    result = {name: folder/name for name in names}
    result.update({'profiles/'+p.name: p for p in (ROOT/'config/student_profiles').glob('*.json')})
    result['protocol.md'] = ROOT/'docs/DEADLINE_COHORT_PROTOCOL_20261018.md'
    return result


def report_folder(run):
    run = Path(run)
    return run.parents[2]/'reports'/run.name


def prepare(config=DeadlineConfig(), root=ROOT):
    config.validate()
    sources = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n,p in source_files().items()}
    identity = dict(protocol=PROTOCOL, config=asdict(config), sources=sources, profiles=profiles())
    study_id = 'deadline_cohort_'+digest(identity)[:16]
    run = Path(root)/'data/runs'/study_id
    chains = []
    for i in range(config.students//4):
        rng = np.random.default_rng(np.random.SeedSequence([config.seed, i, 8821]))
        chains.append(dict(chain_id=f'c{i+1:05d}',profile_ids=assignment(config.seed,i),
                           customer_demand=[4]*4+rng.integers(0,9,config.weeks-4).tolist()))
    batches = [dict(batch_id=f'b{j+1:04d}',chain_ids=[c['chain_id'] for c in chains[start:start+config.batch_students//4]])
               for j,start in enumerate(range(0,len(chains),config.batch_students//4))]
    tasks = []
    for g in range(1,config.generations+1):
        for bi,b in enumerate(batches):
            order = CONDITIONS if (bi+g)%2 else tuple(reversed(CONDITIONS))
            for condition in order:
                tasks.append(dict(task_id=f"{b['batch_id']}_g{g:02d}_{condition}",batch_id=b['batch_id'],
                                  generation=g,condition=condition,chain_ids=b['chain_ids']))
    plan = dict(chains=chains,batches=batches,tasks=tasks,expected_responses=len(tasks),
        fictional_identities=config.students,generation_role_trajectories=config.students*config.generations*2,
        hypotheses={'H1':'Brief deadline has lower matched-state pipeline sensitivity.',
                    'H2':'Brief deadline has higher full scored chain cost.',
                    'H3':'Brief deadline has higher mean role order/customer-demand variance ratio.'},
        rule_type_normalization='Prospectively allow only mechanical field-specific conversions from the saved formatter; preserve original and derivative.',
        inference='Descriptive only. Repeated generations are not new student identities; no student-level p-values.',
        stopping='Collect every planned slot once; no additional sampling or replacement based on effects.')
    for n,p in source_files().items():
        save_new(run/'source_implementation'/n,p.read_bytes())
    save_new(run/'manifest.json',identity | dict(study_id=study_id,schema_version=SCHEMA,plan_sha256=digest(plan),human_observations=0,api_calls=0))
    save_new(run/'plan.json',plan)
    (run/'inbox').mkdir(exist_ok=True)
    for task in tasks:
        write_prompt(run,task['task_id'])
    return run


def audit(run):
    run = Path(run);m = read(run/'manifest.json')
    identity = {k:m[k] for k in ('protocol','config','sources','profiles')}
    if m['protocol'] != PROTOCOL or run.name != 'deadline_cohort_'+digest(identity)[:16] or m['study_id'] != run.name:
        raise ValueError('Run fingerprint mismatch.')
    if digest(read(run/'plan.json')) != m['plan_sha256']:
        raise ValueError('Frozen plan changed.')
    current = source_files()
    for n,h in m['sources'].items():
        if hashlib.sha256((run/'source_implementation'/n).read_bytes()).hexdigest() != h or hashlib.sha256(current[n].read_bytes()).hexdigest() != h:
            raise ValueError('Scientific source changed; use a new protocol/run: '+n)
    return m


def task_info(run, task_id):
    plan = read(Path(run)/'plan.json')
    matches = [t for t in plan['tasks'] if t['task_id'] == task_id]
    if len(matches) != 1:
        raise ValueError('Unknown task ID.')
    task = matches[0]
    return task,[c for c in plan['chains'] if c['chain_id'] in task['chain_ids']]


def prompt_text(run, task_id):
    m = read(Path(run)/'manifest.json');task,chains = task_info(run,task_id)
    seconds = DEADLINES[task['condition']]
    base = INSTRUCTIONS.split('OUTPUT\n',1)[0].replace('Do not force different outcomes between passes.','Do not target any aggregate result.')
    situation = (f'The student has {seconds} seconds from seeing each decision display to submitting its order. '
                 'The order is final when submitted. Represent the choice the described student would make within that deadline.')
    output = '''\nOUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.
'''
    context = dict(schema_version=SCHEMA,study_id=m['study_id'],task_id=task_id,deadline_seconds=seconds,
                   role_order=list(ROLES),output_weeks=list(range(5,m['config']['weeks']+1)),
                   participant_profiles=m['profiles'],chains=chains,rules_questions=QUESTIONS)
    return base+'\nCLASSROOM SITUATION\n'+situation+'\nThis describes the fictional student; it does not impose or measure chat-model computation time.\n'+output+'\nFROZEN INPUT DATA:\n'+json.dumps(context,separators=(',',':'),ensure_ascii=False)+'\n'


def write_prompt(run, task_id):
    text = prompt_text(run,task_id)
    save_new(Path(run)/'prompts'/(task_id+'.txt'),text)
    path = report_folder(run)/'prompts'/(task_id+'.md')
    cfg = read(Path(run)/'manifest.json')['config']
    save_new(path,f"# {task_id}\n\nCopy the entire box into a fresh **{cfg['model_label']} / {cfg['effort_label']}** chat. Include no earlier responses.\n\n```text\n{text}```\n")
    return path


def accepted_path(run,task_id):
    return Path(run)/'accepted'/(task_id+'.json')


def validate_response(run,task_id,text):
    m = read(Path(run)/'manifest.json');task,chains = task_info(run,task_id)
    obj = parse_response(text)
    _keys(obj,('schema_version','study_id','task_id','deadline_seconds','rules','chains','complete'),'Root')
    if (obj['schema_version'] != SCHEMA or obj['study_id'] != m['study_id'] or obj['task_id'] != task_id
        or type(obj['deadline_seconds']) is not int or obj['deadline_seconds'] != DEADLINES[task['condition']] or obj['complete'] is not True):
        raise ValueError('Wrong identifiers, deadline or incomplete output.')
    _keys(obj['rules'],RULE_ANSWERS,'Rules')
    if obj['rules'] != RULE_ANSWERS or type(obj['rules']['backlog_includes_current_unfilled_demand']) is not bool or type(obj['rules']['factory_order_week_7_arrival_week']) is not int or type(obj['rules']['three_week_backlog_cost']) not in (int,float):
        raise ValueError('Rules answers failed; no answer correction.')
    if not isinstance(obj['chains'],list) or len(obj['chains']) != len(chains):
        raise ValueError('Wrong number of chains.')
    ids = []
    for c in obj['chains']:
        _keys(c,('chain_id','orders','probes'),'Chain')
        ids.append(c['chain_id'])
        _matrix(c['orders'],m['config']['weeks']-4,4,'orders');_matrix(c['probes'],4,2,'probes')
    if any(type(i) is not str for i in ids) or len(set(ids)) != len(ids) or set(ids) != set(task['chain_ids']):
        raise ValueError('Missing/duplicate/unknown chain IDs.')
    return obj


def import_response(run,task_id,text,*,model_label,effort_label,session_label,confirm_full_prompt=False,evidence_kind='model_output'):
    run = Path(run);m = audit(run);task_info(run,task_id)
    if accepted_path(run,task_id).exists():
        raise ValueError('Already locked; accepted results cannot be replaced.')
    cfg = m['config']
    if model_label != cfg['model_label'] or effort_label != cfg['effort_label'] or not session_label.strip() or not confirm_full_prompt:
        raise ValueError('Record matching model/settings, a session label and full-prompt provenance.')
    if evidence_kind != ('synthetic_test' if cfg['synthetic'] else 'model_output'):
        raise ValueError('Synthetic controls and model responses must stay separate.')
    attempt = len(list((run/'attempts').glob(task_id+'_*.txt')))+1
    raw = run/'attempts'/f'{task_id}_{attempt:03d}.txt'
    save_new(raw,text)
    entry = dict(task_id=task_id,raw_path=raw.relative_to(run).as_posix(),raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
        prompt_sha256=hashlib.sha256(prompt_text(run,task_id).encode()).hexdigest(),model_label=model_label,effort_label=effort_label,
        session_label=session_label,evidence_kind=evidence_kind,full_prompt_confirmed=True,
        received_utc=datetime.now(timezone.utc).isoformat(),actual_reasoning_tokens=None,actual_wall_time_s=None,api_calls=0)
    normalized,edits = text,[]
    try:
        try:
            obj = validate_response(run,task_id,text)
        except ValueError as original:
            try:
                normalized,edits = normalize_rule_types(text)
                obj = validate_response(run,task_id,normalized)
            except ValueError:
                raise original
        if edits:
            derived = run/'derived'/f'{task_id}_{attempt:03d}.txt';save_new(derived,normalized)
            entry.update(derived_path=derived.relative_to(run).as_posix(),derived_sha256=hashlib.sha256(derived.read_bytes()).hexdigest())
        entry.update(status='accepted',payload=obj,formatting_edits=edits)
    except ValueError as exc:
        save_new(raw.with_suffix('.json'),entry | dict(status='rejected',reason=str(exc)))
        raise
    save_new(raw.with_suffix('.json'),entry);save_new(accepted_path(run,task_id),entry)
    return entry


def load_accepted(run,task_id):
    run = Path(run);e = read(accepted_path(run,task_id));raw = (run/e['raw_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != e['raw_sha256']:
        raise ValueError('Raw reply hash mismatch.')
    text = raw.decode('utf-8')
    if e['formatting_edits']:
        text,edits = normalize_rule_types(text)
        if edits != e['formatting_edits'] or (run/e['derived_path']).read_bytes() != text.encode() or hashlib.sha256(text.encode()).hexdigest() != e['derived_sha256']:
            raise ValueError('Formatting derivative mismatch.')
    if validate_response(run,task_id,text) != e['payload'] or hashlib.sha256(prompt_text(run,task_id).encode()).hexdigest() != e['prompt_sha256']:
        raise ValueError('Payload or prompt hash mismatch.')
    return e


def progress(run):
    return pd.DataFrame([dict(task_id=t['task_id'],batch_id=t['batch_id'],generation=t['generation'],condition=t['condition'],
        students=4*len(t['chain_ids']),accepted=accepted_path(run,t['task_id']).exists()) for t in read(Path(run)/'plan.json')['tasks']])


def next_task(run):
    for task in read(Path(run)/'plan.json')['tasks']:
        if not accepted_path(run,task['task_id']).exists():
            return task | dict(prompt_path=write_prompt(run,task['task_id']),prompt=prompt_text(run,task['task_id']))
    return None


def replay(run):
    m = audit(run);plan = read(Path(run)/'plan.json');specs = {c['chain_id']:c for c in plan['chains']}
    rows,probes,imports = [],[],[]
    for task in plan['tasks']:
        if not accepted_path(run,task['task_id']).exists():
            continue
        entry = load_accepted(run,task['task_id']);imports.append({k:v for k,v in entry.items() if k!='payload'})
        for choice in entry['payload']['chains']:
            spec = specs[choice['chain_id']];game = BeerGame();last = [4]*4
            common = {k:task[k] for k in ('task_id','batch_id','generation','condition')}
            common['chain_id'] = choice['chain_id']
            for week in range(1,m['config']['weeks']+13):
                demand = spec['customer_demand'][min(week-1,m['config']['weeks']-1)]
                states = game.observe(int(demand));phase = 'practice' if week <= 4 else 'model' if week <= m['config']['weeks'] else 'automatic'
                orders = [4]*4 if phase == 'practice' else choice['orders'][week-5] if phase == 'model' else last
                for i,state in enumerate(states):
                    rows.append(state | common | dict(order=orders[i],customer_demand=demand,phase=phase,profile_id=spec['profile_ids'][i]))
                game.commit(orders);last = orders
            for i,role in enumerate(ROLES):
                low,high = choice['probes'][i]
                probes.append(common | dict(role=role,profile_id=spec['profile_ids'][i],low_order=low,high_order=high,sensitivity=(low-high)/24))
    return pd.DataFrame(rows),pd.DataFrame(probes),imports


def synthetic_response(run,task_id):
    m = audit(run)
    if not m['config']['synthetic']:
        raise ValueError('Synthetic fixture forbidden in a model-output run.')
    task,chains = task_info(run,task_id)
    return json.dumps(dict(schema_version=SCHEMA,study_id=m['study_id'],task_id=task_id,deadline_seconds=DEADLINES[task['condition']],
        rules=RULE_ANSWERS,chains=[dict(chain_id=c['chain_id'],orders=[[4]*4 for _ in range(m['config']['weeks']-4)],probes=[[8,4]]*4) for c in chains],complete=True))
