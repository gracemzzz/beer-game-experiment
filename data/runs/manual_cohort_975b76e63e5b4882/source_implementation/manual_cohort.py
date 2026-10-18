"""Manual cohort generation: prompt files, immutable imports and physical replay.

No API client, network access, paid calls or execution of pasted model code.
This protocol compares initial and reconsidered whole trajectories, not weekly
reasoning budgets. Rows generated together are not independent respondents.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .game import BeerGame, ROLES
from .student_profiles import profiles, assignment

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = 'manual-cohort-trajectories-v1'
STAGES = ('initial', 'revision')
RULE_ANSWERS = {'backlog_includes_current_unfilled_demand': True,
                'factory_order_week_7_arrival_week': 10, 'three_week_backlog_cost': 15}
QUESTIONS = {
    'backlog_includes_current_unfilled_demand': 'Does current backlog already include unfilled demand from this week?',
    'factory_order_week_7_arrival_week': 'When does factory production started in week 7 arrive?',
    'three_week_backlog_cost': 'What is the cost of five backlogged cases at the end of each of three weeks?'}
INSTRUCTIONS = """Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not force different outcomes between passes.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.

OUTPUT
Return only one complete JSON object, optionally in one JSON code block. No prose,
code, costs, statistical summaries or claims about hypotheses. Answer the factual
rules questions, then supply every assigned chain exactly once. `orders` contains
one four-integer row per requested week, in role order. `probes` contains four
[first_display_order, second_display_order] rows, one per role in the same order.
Use literal nonnegative integers, no nulls, omitted rows, ellipses or range notation.
Keep the required study_id, batch_id and stage unchanged. Set complete to true only
when every required entry is present. Never fill omissions with invented summaries.
"""
INITIAL = """INITIAL PASS
Produce the cohort's initial weekly trajectories and matched-state choices.
Generate each role's submitted order using the evolving state of its own chain.
Do not add a second reconsideration pass or target any aggregate result.
"""
REVISION = """RECONSIDERATION PASS
You have one opportunity to reconsider the supplied initial cohort trajectories
and matched-state choices. Keep or change any choices. Return every revised weekly
order and every probe choice in full, even if unchanged. Keep each personality,
initial physical state and customer-demand path fixed. Recompute each chain from
week 1 using its revised orders; later states may differ from the initial trajectory.
This is revision of whole trajectories, not independent revisions at unchanged
weekly states. Do not force improvements, differences or a particular outcome.
"""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save_new(path, value):
    path = Path(path)
    text = value if isinstance(value, str) else json.dumps(value, indent=2, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding='utf-8') != text:
            raise ValueError(f'Refusing to overwrite frozen evidence: {path.name}')
        return
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)


@dataclass(frozen=True)
class CohortConfig:
    students: int = 500
    batch_students: int = 100
    weeks: int = 24
    repetitions: int = 1
    seed: int = 20261017
    study_label: str = 'cohort-500-first-plan'
    model_label: str = 'GPT-6 Astra'
    effort_label: str = 'high'
    synthetic: bool = False

    def validate(self):
        for name in ('students', 'batch_students'):
            n = getattr(self, name)
            if type(n) is not int or n < 4 or n % 4:
                raise ValueError(f'{name} must be a positive multiple of four, at least 4.')
        if type(self.weeks) is not int or not 8 <= self.weeks <= 104:
            raise ValueError('Choose 8-104 weeks prospectively, including four practice weeks.')
        if type(self.repetitions) is not int or not 1 <= self.repetitions <= 100:
            raise ValueError('Choose 1-100 cohort repetitions prospectively.')
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ValueError('seed must be an integer in [0, 2**32).')
        if self.students * self.repetitions > 100000:
            raise ValueError('Local planning limit is 100,000 fictional identities.')
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', self.study_label):
            raise ValueError('Use a simple study label of letters, digits, underscores and hyphens.')
        if not self.model_label.strip() or self.effort_label != 'high':
            raise ValueError('Record a model label and keep effort high throughout this protocol.')
        if type(self.synthetic) is not bool:
            raise ValueError('synthetic must be Boolean.')
        return self


def source_files():
    folder = Path(__file__).parent
    files = {p.name: p for p in [folder/'manual_cohort.py', folder/'manual_cohort_report.py',
                                folder/'game.py', folder/'student_profiles.py', folder/'estimation.py']}
    files.update({'profiles/'+p.name: p for p in (ROOT/'config/student_profiles').glob('*.json')})
    return files


def prepare(config=CohortConfig(), root=ROOT):
    config.validate()
    sources = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in source_files().items()}
    identity = dict(protocol=PROTOCOL, config=asdict(config), sources=sources, profiles=profiles())
    study_id = 'manual_cohort_' + digest(identity)[:16]
    run = Path(root)/'data/runs'/study_id
    manifest = identity | {'study_id': study_id, 'schema_version': PROTOCOL,
                           'human_observations': 0, 'api_calls': 0}
    for name, path in source_files().items():
        dest = run/'source_implementation'/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if dest.read_bytes() != path.read_bytes():
                raise ValueError('Frozen source changed.')
        else:
            with dest.open('xb') as f:
                f.write(path.read_bytes())
    chains, batches = [], []
    per_batch = config.batch_students//4
    for rep in range(config.repetitions):
        own = []
        for index in range(config.students//4):
            rng = np.random.default_rng(np.random.SeedSequence([config.seed, rep, index, 719]))
            chain = dict(chain_id=f'r{rep+1:03d}_c{index+1:05d}', repetition=rep+1,
                         profile_ids=assignment(config.seed + rep*100003, index),
                         customer_demand=[4]*4 + rng.integers(0, 9, config.weeks-4).tolist())
            chains.append(chain)
            own.append(chain['chain_id'])
        for start in range(0, len(own), per_batch):
            batches.append(dict(batch_id=f'b{len(batches)+1:04d}', repetition=rep+1,
                                chain_ids=own[start:start+per_batch]))
    plan = dict(chains=chains, batches=batches, expected_responses=2*len(batches),
                fictional_identities=config.students*config.repetitions,
                condition_trajectories=2*config.students*config.repetitions,
                hypotheses=dict(H1='Initial has lower matched-state pipeline sensitivity than revision.',
                                H2='Initial has higher full scored chain cost than revision.',
                                H3='Initial has higher mean role order/customer-demand variance ratio than revision.'),
                inference='Descriptive generated-cohort comparisons only; no independent-human or weekly-token-budget inference.')
    manifest['plan_sha256'] = digest(plan)
    save_new(run/'manifest.json', manifest)
    save_new(run/'plan.json', plan)
    (run/'inbox').mkdir(exist_ok=True)
    report = Path(root)/'reports'/study_id
    report.mkdir(parents=True, exist_ok=True)
    for batch in batches:
        write_prompt(run, batch['batch_id'], 'initial')
    return run


def audit(run):
    run = Path(run)
    m = read(run/'manifest.json')
    if m['protocol'] != PROTOCOL or m['study_id'] != run.name:
        raise ValueError('Wrong manual cohort protocol/run.')
    identity = {k: m[k] for k in ('protocol', 'config', 'sources', 'profiles')}
    if 'manual_cohort_'+digest(identity)[:16] != run.name:
        raise ValueError('Manifest fingerprint mismatch.')
    if digest(read(run/'plan.json')) != m['plan_sha256']:
        raise ValueError('Frozen cohort plan changed.')
    for name, expected in m['sources'].items():
        if hashlib.sha256((run/'source_implementation'/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen source hash mismatch: '+name)
        if name in source_files() and hashlib.sha256(source_files()[name].read_bytes()).hexdigest() != expected:
            raise ValueError('Working source differs from this plan. Use the frozen implementation or a new prospective plan.')
    return m


def get_batch(run, batch_id):
    plan = read(Path(run)/'plan.json')
    batch = next((b for b in plan['batches'] if b['batch_id'] == batch_id), None)
    if batch is None:
        raise ValueError('Unknown batch ID.')
    return batch, [c for c in plan['chains'] if c['chain_id'] in batch['chain_ids']]


def accepted_path(run, batch_id, stage):
    if stage not in STAGES or not re.fullmatch(r'b\d{4,}', batch_id):
        raise ValueError('Invalid stage or batch ID.')
    return Path(run)/'accepted'/f'{batch_id}_{stage}.json'


def load_accepted(run, batch_id, stage):
    entry = read(accepted_path(run, batch_id, stage))
    raw = Path(run)/entry['raw_path']
    if hashlib.sha256(raw.read_bytes()).hexdigest() != entry['raw_sha256']:
        raise ValueError('Raw response hash mismatch.')
    payload = validate_response(run, batch_id, stage, raw.read_text(encoding='utf-8'))
    if payload != entry['payload']:
        raise ValueError('Accepted payload differs from saved raw text.')
    if hashlib.sha256(prompt_text(run, batch_id, stage).encode()).hexdigest() != entry['prompt_sha256']:
        raise ValueError('Accepted prompt fingerprint mismatch.')
    return entry


def prompt_text(run, batch_id, stage):
    if stage not in STAGES:
        raise ValueError('Unknown stage.')
    run = Path(run)
    m = read(run/'manifest.json')
    batch, chains = get_batch(run, batch_id)
    context = dict(study_id=m['study_id'], batch_id=batch_id, stage=stage,
                   role_order=list(ROLES), output_weeks=list(range(5, m['config']['weeks']+1)),
                   participant_profiles=m['profiles'], chains=chains, rules_questions=QUESTIONS)
    if stage == 'revision':
        context['initial_submission'] = load_accepted(run, batch_id, 'initial')['payload']['chains']
    contract = {'schema_version': PROTOCOL, 'study_id': m['study_id'], 'batch_id': batch_id,
                'stage': stage, 'rules': {k: '<your answer>' for k in QUESTIONS},
                'chains': [{'chain_id': '<assigned chain_id>',
                            'orders': '<one [retailer,wholesaler,distributor,factory] integer row per output week>',
                            'probes': '<four [first_display_order,second_display_order] integer rows, one per role>'}],
                'complete': True}
    return (INSTRUCTIONS+'\n'+(INITIAL if stage == 'initial' else REVISION)+
            '\nREQUIRED JSON STRUCTURE (replace descriptions with actual arrays/answers):\n'+
            json.dumps(contract, indent=2)+'\n\nFROZEN INPUT DATA:\n'+
            json.dumps(context, separators=(',', ':'), ensure_ascii=False)+'\n')


def write_prompt(run, batch_id, stage):
    run = Path(run)
    prompt = prompt_text(run, batch_id, stage)
    save_new(run/'prompts'/f'{batch_id}_{stage}.txt', prompt)
    report = run.parents[2]/'reports'/run.name
    path = report/'prompts'/f'{batch_id}_{stage.upper()}.md'
    save_new(path, f'# {batch_id}: {stage}\n\nCopy the entire box into a fresh chat using the fixed model and high effort.\n\n```text\n{prompt}```\n')
    return path


def _unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('Duplicate JSON key: '+key)
        obj[key] = value
    return obj


def parse_response(text):
    stripped = text.strip()
    fenced = re.fullmatch(r'```(?:json)?\s*\n(.*?)\n```', stripped, flags=re.S)
    if fenced:
        stripped = fenced.group(1)
    try:
        return json.loads(stripped, object_pairs_hook=_unique,
                          parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite JSON number.')))
    except (ValueError, TypeError) as exc:
        raise ValueError('Response must be complete JSON, with no extra prose, duplicate keys or nonfinite numbers.') from exc


def _keys(obj, keys, name):
    if not isinstance(obj, dict) or set(obj) != set(keys):
        raise ValueError(f'{name} must have exactly these fields: {", ".join(keys)}')


def _matrix(value, rows, cols, name):
    if not isinstance(value, list) or len(value) != rows:
        raise ValueError(f'{name} needs exactly {rows} rows.')
    for row in value:
        if not isinstance(row, list) or len(row) != cols:
            raise ValueError(f'{name} needs {cols} entries per row.')
        if any(type(q) is not int or q < 0 for q in row):
            raise ValueError(f'{name} accepts only nonnegative integer orders (not booleans/floats).')
        if any(q > 100000 for q in row):
            raise ValueError('An order exceeds the simulator technical circuit breaker. No clipping or substitution.')


def validate_response(run, batch_id, stage, text):
    m = read(Path(run)/'manifest.json')
    batch, chains = get_batch(run, batch_id)
    obj = parse_response(text)
    _keys(obj, ('schema_version', 'study_id', 'batch_id', 'stage', 'rules', 'chains', 'complete'), 'Root object')
    expected = dict(schema_version=PROTOCOL, study_id=m['study_id'], batch_id=batch_id, stage=stage)
    if any(obj[k] != v for k, v in expected.items()) or obj['complete'] is not True:
        raise ValueError('Wrong study, batch, stage, schema or incomplete output.')
    _keys(obj['rules'], RULE_ANSWERS, 'Rules answers')
    if (obj['rules'] != RULE_ANSWERS or type(obj['rules']['backlog_includes_current_unfilled_demand']) is not bool
            or type(obj['rules']['factory_order_week_7_arrival_week']) is not int
            or type(obj['rules']['three_week_backlog_cost']) not in (int, float)):
        raise ValueError('Factual rules screen failed; no strategy coaching or automatic replacement.')
    if not isinstance(obj['chains'], list) or len(obj['chains']) != len(chains):
        raise ValueError('Missing or extra chains in response.')
    ids = []
    for chain in obj['chains']:
        _keys(chain, ('chain_id', 'orders', 'probes'), 'Chain')
        ids.append(chain['chain_id'])
        _matrix(chain['orders'], m['config']['weeks']-4, 4, 'orders')
        _matrix(chain['probes'], 4, 2, 'probes')
    if any(type(i) is not str for i in ids) or len(set(ids)) != len(ids) or set(ids) != set(batch['chain_ids']):
        raise ValueError('Duplicate, missing or unknown chain IDs.')
    return obj


def import_response(run, batch_id, stage, text, *, model_label, effort_label, session_label,
                    evidence_kind='model_output', confirm_full_prompt=False):
    run = Path(run)
    m = audit(run)
    get_batch(run, batch_id)
    target = accepted_path(run, batch_id, stage)
    if target.exists():
        raise ValueError('This submission is already locked. Do not select a replacement after seeing outcomes.')
    if model_label != m['config']['model_label'] or effort_label != m['config']['effort_label']:
        raise ValueError('Model/effort differs from the frozen plan. Use a separate prospective study.')
    if not session_label.strip() or not confirm_full_prompt:
        raise ValueError('Record the chat/session label and confirm you sent the full generated prompt.')
    if evidence_kind != ('synthetic_test' if m['config']['synthetic'] else 'model_output'):
        raise ValueError('Synthetic controls and imported model output must be kept in separate studies.')
    if stage == 'revision' and not accepted_path(run, batch_id, 'initial').exists():
        raise ValueError('Import the initial response before its revision.')
    if stage == 'revision' and not progress(run).initial.all():
        raise ValueError('Import every planned initial batch before revisions.')
    prompt = prompt_text(run, batch_id, stage)
    write_prompt(run, batch_id, stage)
    folder = run/'attempts'
    folder.mkdir(exist_ok=True)
    attempt = len(list(folder.glob(f'{batch_id}_{stage}_*.txt')))+1
    raw = folder/f'{batch_id}_{stage}_{attempt:03d}.txt'
    save_new(raw, text)
    entry = dict(batch_id=batch_id, stage=stage, raw_path=raw.relative_to(run).as_posix(),
                 raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                 prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                 model_display_label=model_label, effort_display_label=effort_label,
                 session_label=session_label.strip(), evidence_kind=evidence_kind,
                 full_prompt_confirmed=True, imported_utc=datetime.now(timezone.utc).isoformat(),
                 actual_reasoning_tokens=None, actual_wall_time_s=None, api_calls=0)
    try:
        payload = validate_response(run, batch_id, stage, text)
    except ValueError as exc:
        save_new(raw.with_suffix('.json'), entry | {'status': 'rejected', 'reason': str(exc)})
        raise
    entry.update(status='accepted', payload=payload)
    save_new(raw.with_suffix('.json'), entry)
    save_new(target, entry)
    if stage == 'initial':
        write_prompt(run, batch_id, 'revision')
    return entry


def progress(run):
    run = Path(run)
    m, plan = read(run/'manifest.json'), read(run/'plan.json')
    rows = []
    for b in plan['batches']:
        rows.append(dict(batch_id=b['batch_id'], repetition=b['repetition'], students=4*len(b['chain_ids']),
                         initial=accepted_path(run,b['batch_id'],'initial').exists(),
                         revision=accepted_path(run,b['batch_id'],'revision').exists()))
    return pd.DataFrame(rows)


def next_task(run):
    table = progress(run)
    for stage in STAGES:
        pending = table[~table[stage]]
        if len(pending):
            batch_id = pending.iloc[0].batch_id
            return dict(batch_id=batch_id, stage=stage, prompt_path=write_prompt(run,batch_id,stage),
                        prompt=prompt_text(run,batch_id,stage))
    return None


def replay(run, paired_only=True):
    """Recompute all physical quantities; model-supplied summary statistics are never used."""
    run = Path(run)
    m = audit(run)
    plan = read(run/'plan.json')
    rows, probes, imported = [], [], []
    chain_plan = {c['chain_id']: c for c in plan['chains']}
    for b in plan['batches']:
        present = [s for s in STAGES if accepted_path(run,b['batch_id'],s).exists()]
        if paired_only and len(present) != 2:
            continue
        for stage in present:
            entry = load_accepted(run,b['batch_id'],stage)
            imported.append({k:v for k,v in entry.items() if k!='payload'})
            for choice in entry['payload']['chains']:
                spec = chain_plan[choice['chain_id']]
                game = BeerGame()
                last = [4]*4
                for week in range(1, m['config']['weeks']+13):
                    demand = spec['customer_demand'][min(week-1,m['config']['weeks']-1)]
                    states = game.observe(int(demand))
                    phase = 'practice' if week <= 4 else ('model' if week <= m['config']['weeks'] else 'automatic')
                    orders = [4]*4 if phase=='practice' else (choice['orders'][week-5] if phase=='model' else last)
                    for i, state in enumerate(states):
                        rows.append(state | dict(order=orders[i], customer_demand=demand, phase=phase,
                                    batch_id=b['batch_id'], repetition=b['repetition'], chain_id=spec['chain_id'],
                                    profile_id=spec['profile_ids'][i], condition=stage))
                    game.commit(orders)
                    last = orders
                for i, role in enumerate(ROLES):
                    low, high = choice['probes'][i]
                    probes.append(dict(batch_id=b['batch_id'], repetition=b['repetition'], chain_id=spec['chain_id'],
                                       condition=stage, role=role, profile_id=spec['profile_ids'][i],
                                       low_order=low, high_order=high, sensitivity=(low-high)/24))
    return pd.DataFrame(rows), pd.DataFrame(probes), imported


def synthetic_response(run, batch_id, stage):
    """Deterministic test data only; never a replacement for a model response."""
    m = read(Path(run)/'manifest.json')
    if not m['config']['synthetic']:
        raise ValueError('Synthetic fixtures may only be generated for an explicitly synthetic plan.')
    _, specs = get_batch(run,batch_id)
    chains = []
    for spec in specs:
        game, orders = BeerGame(), []
        for week, demand in enumerate(spec['customer_demand'],1):
            states = game.observe(demand)
            q = [4]*4 if week<=4 else [max(0, int(s['demand']+.15*(12-s['net_inventory']))) for s in states]
            if week>4:
                orders.append(q)
            game.commit(q)
        chains.append(dict(chain_id=spec['chain_id'], orders=orders, probes=[[8,4]]*4))
    return json.dumps(dict(schema_version=PROTOCOL,study_id=m['study_id'],batch_id=batch_id,
                           stage=stage,rules=RULE_ANSWERS,chains=chains,complete=True))
