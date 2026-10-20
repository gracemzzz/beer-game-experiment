"""Separate education/deadline whole-cohort study; immutable, unpaid imports.

Jointly generated chains are dependent fictional observations.  This module
implements descriptive contrasts and never calculates student-level p-values.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

from .game import BeerGame, ROLES
from .manual_cohort_chat import INSTRUCTIONS, QUESTIONS, RULE_ANSWERS, parse_response
from .student_profiles import assignment, profiles

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = 'education-deadline-cohort-v1'
SCHEMA = 'education-deadline-trajectories-v1'
ARMS = {
    'a60_control': {'deadline_seconds': 60, 'lecture_id': 'control'},
    'b10_control': {'deadline_seconds': 10, 'lecture_id': 'control'},
    'c10_education': {'deadline_seconds': 10, 'lecture_id': 'causal'},
}
HYPOTHESES = {
    'H1': 'Within an information-sharing environment, a binding decision-time constraint increases the underweighting of outstanding replenishment orders relative to adequate decision time.',
    'H2': 'Within an information-sharing environment, supply chains operating under binding decision-time constraints incur higher total inventory-holding and backlog costs than supply chains operating with adequate decision time.',
    'H3': 'Within an information-sharing environment and under a binding decision-time constraint, participants receiving causal education about the origins and propagation of order fluctuations underweight outstanding replenishment orders less than participants receiving standard game instructions and a matched control lecture.',
    'H4': 'Within an information-sharing environment and under a binding decision-time constraint, supply chains receiving causal education about the origins and propagation of order fluctuations incur lower total inventory-holding and backlog costs than supply chains receiving standard game instructions and a matched control lecture.',
}
CONTRASTS = {
    'H1': ('a60_control', 'b10_control', 'sensitivity', -1),
    'H2': ('a60_control', 'b10_control', 'total_cost', 1),
    'H3': ('b10_control', 'c10_education', 'sensitivity', 1),
    'H4': ('b10_control', 'c10_education', 'total_cost', -1),
}
CONTINUATION_WEEKS = 12


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode('utf-8')).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save_new(path, value):
    """Write immutable bytes, permitting only a byte-identical recheck."""
    path = Path(path)
    if isinstance(value, bytes):
        data = value
    elif isinstance(value, str):
        data = value.encode('utf-8')
    else:
        data = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False).encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError('Refusing to overwrite frozen evidence: '+str(path))
    else:
        with path.open('xb') as stream:
            stream.write(data)


@dataclass(frozen=True)
class Config:
    students: int = 500
    weeks: int = 24
    repetitions: int = 2
    seed: int = 2026101901
    label: str = 'full-cohort-chat'
    model_label: str = 'GPT-6'
    effort_label: str = 'pro'
    collection: str = 'chat_ui'
    synthetic: bool = False

    def validate(self):
        if type(self.students) is not int or self.students < 4 or self.students % 4:
            raise ValueError('students must be a positive multiple of four.')
        if type(self.weeks) is not int or not 8 <= self.weeks <= 104:
            raise ValueError('Choose 8-104 weeks prospectively.')
        if type(self.repetitions) is not int or not 1 <= self.repetitions <= 50:
            raise ValueError('Choose 1-50 fixed repetitions prospectively.')
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ValueError('Invalid seed.')
        if self.collection not in ('chat_ui', 'isolated_assistant'):
            raise ValueError('Unsupported collection mode.')
        allowed = ('pro', 'high') if self.collection == 'chat_ui' else ('inherited',)
        if self.effort_label not in allowed or not isinstance(self.model_label, str) or not self.model_label.strip():
            raise ValueError('Record a fixed model and the literal setting for this collection mode.')
        if not isinstance(self.label, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', self.label):
            raise ValueError('Invalid study label.')
        if type(self.synthetic) is not bool:
            raise ValueError('synthetic must be a Boolean.')
        return self


def source_files():
    folder = Path(__file__).parent
    result = {name: folder/name for name in
              ('education_deadline_cohort.py', 'game.py', 'student_profiles.py', 'manual_cohort_chat.py')}
    result.update({'profiles/'+p.name: p for p in sorted((ROOT/'config/student_profiles').glob('*.json'))})
    result['protocol.md'] = ROOT/'docs/EDUCATION_DEADLINE_PROTOCOL_20261019.md'
    result['lectures/control.txt'] = ROOT/'docs/education_deadline_20261019/control_lecture.txt'
    result['lectures/causal.txt'] = ROOT/'docs/education_deadline_20261019/causal_lecture.txt'
    return result


def report_folder(run):
    run = Path(run)
    return run.parents[2]/'reports'/run.name


def prepare(config=Config(), root=ROOT):
    config.validate()
    sources = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in source_files().items()}
    identity = dict(protocol=PROTOCOL, config=asdict(config), sources=sources, profiles=profiles())
    study_id = 'education_deadline_'+digest(identity)[:16]
    run = Path(root)/'data/runs'/study_id
    chains = []
    for i in range(config.students//4):
        rng = np.random.default_rng(np.random.SeedSequence([config.seed, i, 1903]))
        chains.append(dict(chain_id=f'c{i+1:05d}', participant_ids=[f's{4*i+j+1:05d}' for j in range(4)],
                           profile_ids=assignment(config.seed, i),
                           customer_demand=[4]*4+rng.integers(0, 9, config.weeks-4).tolist()))
    tasks = []
    arm_ids = tuple(ARMS)
    for repetition in range(1, config.repetitions+1):
        # Rotate and reverse the order in successive blocks; every arm is fresh.
        offset = (repetition-1) % len(arm_ids)
        order = arm_ids[offset:]+arm_ids[:offset]
        if repetition % 2 == 0:
            order = tuple(reversed(order))
        for arm in order:
            tasks.append(dict(task_id=f'r{repetition:02d}_{arm}', repetition=repetition,
                              arm=arm, **ARMS[arm], chain_ids=[c['chain_id'] for c in chains]))
    plan = dict(chains=chains, tasks=tasks, arms=ARMS, expected_responses=len(tasks),
                fictional_identities=config.students, generation_role_trajectories=config.students*len(tasks),
                repetitions=config.repetitions, continuation_weeks=CONTINUATION_WEEKS,
                hypotheses=HYPOTHESES,
                contrasts={h: dict(reference_arm=a, treatment_arm=b, metric=metric, expected_sign=sign)
                           for h, (a, b, metric, sign) in CONTRASTS.items()},
                primary_cost='Total holding/backlog costs over practice, model and 12 fixed-last-order automatic weeks; report phases separately.',
                sensitivity='(order with 8 dispatched cases - order with 32 dispatched cases)/24, mean of four roles; proxy, not a structural underweighting coefficient.',
                inference='Descriptive only. Chains within a response are dependent; repeated roles/weeks are not independent students. No p-values.',
                stopping='Keep every prospectively fixed slot and all attempts. No outcome-selected extensions, replacements, clipping, imputation or conversion.',
                time_intervention='Fictional 10/60-second framing; actual model computation and deadline binding are unobserved.')
    for name, path in source_files().items():
        save_new(run/'source_implementation'/name, path.read_bytes())
    save_new(run/'plan.json', plan)
    manifest = identity | dict(study_id=study_id, schema_version=SCHEMA, plan_sha256=digest(plan),
                              human_observations=0, api_calls=0)
    save_new(run/'manifest.json', manifest)
    (run/'inbox').mkdir(parents=True, exist_ok=True)
    for task in tasks:
        write_prompt(run, task['task_id'])
    return run


def task_info(run, task_id):
    plan = read(Path(run)/'plan.json')
    matches = [t for t in plan['tasks'] if t['task_id'] == task_id]
    if len(matches) != 1:
        raise ValueError('Unknown task ID.')
    task = matches[0]
    return task, [c for c in plan['chains'] if c['chain_id'] in task['chain_ids']]


def prompt_text(run, task_id):
    run = Path(run)
    manifest = read(run/'manifest.json')
    task, chains = task_info(run, task_id)
    base = INSTRUCTIONS.split('OUTPUT\n', 1)[0].replace(
        'Do not force different outcomes between passes.', 'Do not target any aggregate result.')
    lecture = (run/'source_implementation/lectures'/f"{task['lecture_id']}.txt").read_text(encoding='utf-8')
    situation = (
        f"The student has {task['deadline_seconds']} seconds from seeing each decision display to submitting its order. "
        'The order is final when submitted. Represent the choice the described student would make within that deadline.\n'
        'This is the fictional student situation. It does not impose or measure chat-model computation time, '
        'actual per-decision elapsed time, deadline binding, or psychological pressure.\n')
    output = '''\nOUTPUT
Produce this one complete cohort response independently from the initial physical
states. Include only this classroom situation; use no earlier responses.
Return one complete JSON object, preferably as a downloadable response.json file.
If file delivery is unavailable, return the literal JSON object in the reply.
Do not return costs, statistics, explanations, hypothesis claims or another case.
The exact root fields are schema_version, study_id, task_id, deadline_seconds,
lecture_id, rules, chains and complete. Each chain has exactly chain_id, orders,
probes. orders contains one [retailer,wholesaler,distributor,factory] row per output
week. probes contains four [first_display_order,second_display_order] rows in role
order. Every choice must be a literal nonnegative JSON integer, not a float,
Boolean, string, null, range, repeated-policy description or omitted entry.
Answer the three common factual rules questions: use a literal JSON Boolean for
the backlog question and JSON numbers for the arrival-week and cost questions.
Include every assigned chain exactly once and every requested week/probe pair.
Set complete true only when the entire payload is present. No ellipses or filling.
Code may track physical states or serialize choices already explicitly made.
Do not let a shared heuristic, optimized policy, randomness, or other program
generate missing participant choices. An optional serialization source may contain
only explicit literal choices and JSON writing; it cannot replace the JSON output.
Identical choices, zero orders and identical cohort outcomes are allowed.
'''
    context = dict(schema_version=SCHEMA, study_id=manifest['study_id'], task_id=task_id,
                   deadline_seconds=task['deadline_seconds'], lecture_id=task['lecture_id'],
                   role_order=list(ROLES), output_weeks=list(range(5, manifest['config']['weeks']+1)),
                   participant_profiles=manifest['profiles'], chains=chains, rules_questions=QUESTIONS)
    return (base+'\nPRE-GAME READING\n'+lecture+'\n\nCLASSROOM SITUATION\n'+situation+output+
            '\nFROZEN INPUT DATA:\n'+json.dumps(context, separators=(',', ':'), ensure_ascii=False)+'\n')


def write_prompt(run, task_id):
    run = Path(run)
    text = prompt_text(run, task_id)
    save_new(run/'prompts'/(task_id+'.txt'), text)
    save_new(run/'prompts'/(task_id+'.sha256'), hashlib.sha256(text.encode('utf-8')).hexdigest()+'\n')
    return run/'prompts'/(task_id+'.txt')


def audit(run):
    run = Path(run)
    manifest = read(run/'manifest.json')
    identity = {key: manifest[key] for key in ('protocol', 'config', 'sources', 'profiles')}
    Config(**manifest['config']).validate()
    if (manifest['protocol'] != PROTOCOL or manifest['schema_version'] != SCHEMA or
            run.name != 'education_deadline_'+digest(identity)[:16] or manifest['study_id'] != run.name or
            manifest.get('human_observations') != 0 or manifest.get('api_calls') != 0):
        raise ValueError('Run fingerprint or evidence classification mismatch.')
    plan = read(run/'plan.json')
    if digest(plan) != manifest['plan_sha256']:
        raise ValueError('Frozen plan changed.')
    current = source_files()
    if set(current) != set(manifest['sources']):
        raise ValueError('Scientific source list changed; prepare a new run.')
    for name, expected in manifest['sources'].items():
        if (hashlib.sha256((run/'source_implementation'/name).read_bytes()).hexdigest() != expected or
                hashlib.sha256(current[name].read_bytes()).hexdigest() != expected):
            raise ValueError('Scientific source changed; prepare a new run: '+name)
    for task in plan['tasks']:
        text = prompt_text(run, task['task_id'])
        saved = run/'prompts'/(task['task_id']+'.txt')
        expected = hashlib.sha256(text.encode('utf-8')).hexdigest()+'\n'
        if saved.read_bytes() != text.encode('utf-8') or (saved.with_suffix('.sha256')).read_bytes() != expected.encode('ascii'):
            raise ValueError('Frozen prompt changed: '+task['task_id'])
    return manifest


def _keys(obj, expected, name):
    if not isinstance(obj, dict) or set(obj) != set(expected):
        raise ValueError(name+' must have exactly these fields: '+', '.join(expected))


def _matrix(value, rows, columns, name):
    if not isinstance(value, list) or len(value) != rows:
        raise ValueError(f'{name} needs exactly {rows} rows.')
    for row in value:
        if not isinstance(row, list) or len(row) != columns:
            raise ValueError(f'{name} needs exactly {columns} entries in each row.')
        if any(type(choice) is not int or choice < 0 for choice in row):
            raise ValueError(name+' accepts only literal nonnegative integers, not Booleans/floats/strings.')


def validate_response(run, task_id, text):
    manifest = read(Path(run)/'manifest.json')
    task, chains = task_info(run, task_id)
    payload = parse_response(text)
    _keys(payload, ('schema_version', 'study_id', 'task_id', 'deadline_seconds', 'lecture_id', 'rules', 'chains', 'complete'), 'Root')
    if (payload['schema_version'] != SCHEMA or payload['study_id'] != manifest['study_id'] or
            payload['task_id'] != task_id or type(payload['deadline_seconds']) is not int or
            payload['deadline_seconds'] != task['deadline_seconds'] or
            payload['lecture_id'] != task['lecture_id'] or payload['complete'] is not True):
        raise ValueError('Wrong identifiers, deadline, lecture, schema or incomplete response.')
    _keys(payload['rules'], RULE_ANSWERS, 'Rules')
    rules = payload['rules']
    if (rules != RULE_ANSWERS or type(rules['backlog_includes_current_unfilled_demand']) is not bool or
            type(rules['factory_order_week_7_arrival_week']) is not int or
            type(rules['three_week_backlog_cost']) not in (int, float)):
        raise ValueError('Factual game rules failed; no type conversions, corrections or automatic retry.')
    if not isinstance(payload['chains'], list) or len(payload['chains']) != len(chains):
        raise ValueError('Wrong number of chains.')
    ids = []
    for chain in payload['chains']:
        _keys(chain, ('chain_id', 'orders', 'probes'), 'Chain')
        ids.append(chain['chain_id'])
        _matrix(chain['orders'], manifest['config']['weeks']-4, 4, 'orders')
        _matrix(chain['probes'], 4, 2, 'probes')
    if any(type(value) is not str for value in ids) or len(set(ids)) != len(ids) or set(ids) != set(task['chain_ids']):
        raise ValueError('Missing, duplicate or unknown chain IDs.')
    return payload


def accepted_path(run, task_id):
    return Path(run)/'accepted'/(task_id+'.json')


def _replay_payload(manifest, task, chains, payload):
    rows, probes = [], []
    specs = {chain['chain_id']: chain for chain in chains}
    for choice in payload['chains']:
        spec = specs[choice['chain_id']]
        game, last = BeerGame(), [4]*4
        common = {key: task[key] for key in ('task_id', 'repetition', 'arm', 'deadline_seconds', 'lecture_id')}
        common['chain_id'] = choice['chain_id']
        for week in range(1, manifest['config']['weeks']+CONTINUATION_WEEKS+1):
            demand = int(spec['customer_demand'][min(week-1, manifest['config']['weeks']-1)])
            states = game.observe(demand)
            phase = 'practice' if week <= 4 else 'model' if week <= manifest['config']['weeks'] else 'automatic'
            orders = [4]*4 if phase == 'practice' else choice['orders'][week-5] if phase == 'model' else last
            if any(order > 100000 for order in orders):
                raise ValueError('Order exceeds simulator technical circuit breaker; retained replay failure, no clipping or substitution.')
            for index, state in enumerate(states):
                rows.append(state | common | dict(order=orders[index], customer_demand=demand, phase=phase,
                                                  profile_id=spec['profile_ids'][index], participant_id=spec['participant_ids'][index]))
            game.commit(orders)
            last = orders
        for index, role in enumerate(ROLES):
            low, high = choice['probes'][index]
            sensitivity = (low-high)/24
            if not np.isfinite(sensitivity):
                raise ValueError('Probe exceeds numeric reporting capacity; retained failure, no clipping.')
            probes.append(common | dict(role=role, profile_id=spec['profile_ids'][index],
                                        participant_id=spec['participant_ids'][index], low_order=low,
                                        high_order=high, sensitivity=sensitivity))
    return rows, probes


def import_response(run, task_id, response_path, *, model_label, effort_label, session_label,
                    confirm_full_prompt=False, evidence_kind='model_output'):
    run = Path(run)
    manifest = audit(run)
    task, chains = task_info(run, task_id)
    if accepted_path(run, task_id).exists():
        raise ValueError('Already locked; accepted results cannot be replaced.')
    config = manifest['config']
    if (model_label != config['model_label'] or effort_label != config['effort_label'] or
            not isinstance(session_label, str) or not session_label.strip() or confirm_full_prompt is not True):
        raise ValueError('Record matching model/settings, session and full-prompt confirmation.')
    expected_kind = 'synthetic_test' if config['synthetic'] else 'model_output'
    if evidence_kind != expected_kind:
        raise ValueError('Synthetic fixtures and model responses must stay separate.')
    response_path = Path(response_path)
    raw_bytes = response_path.read_bytes()
    number = len(list((run/'attempts').glob(task_id+'_*.txt')))+1
    raw = run/'attempts'/f'{task_id}_{number:03d}.txt'
    save_new(raw, raw_bytes)
    entry = dict(task_id=task_id, raw_path=raw.relative_to(run).as_posix(),
                 raw_sha256=hashlib.sha256(raw_bytes).hexdigest(), source_filename=response_path.name,
                 prompt_sha256=hashlib.sha256(prompt_text(run, task_id).encode('utf-8')).hexdigest(),
                 model_label=model_label, effort_label=effort_label, session_label=session_label,
                 evidence_kind=evidence_kind, full_prompt_confirmed=True,
                 received_utc=datetime.now(timezone.utc).isoformat(), actual_reasoning_tokens=None,
                 actual_wall_time_s=None, api_calls=0, formatting_edits=[])
    try:
        text = raw_bytes.decode('utf-8')
        payload = validate_response(run, task_id, text)
    except (UnicodeDecodeError, ValueError) as exc:
        save_new(raw.with_suffix('.json'), entry | dict(status='rejected', reason=str(exc)))
        raise ValueError('Response rejected; exact original retained: '+str(exc)) from exc
    try:
        _replay_payload(manifest, task, chains, payload)
    except (ValueError, AssertionError, OverflowError) as exc:
        save_new(raw.with_suffix('.json'), entry | dict(status='replay_failed', reason=str(exc), payload=payload))
        raise ValueError('Physical replay failed; exact original retained: '+str(exc)) from exc
    entry.update(status='accepted', payload=payload)
    save_new(raw.with_suffix('.json'), entry)
    save_new(accepted_path(run, task_id), entry)
    return entry


def _evidence_path(run, relative):
    if not isinstance(relative, str):
        raise ValueError('Invalid raw evidence path.')
    path = (Path(run)/relative).resolve()
    if not path.is_relative_to((Path(run)/'attempts').resolve()) or path.suffix != '.txt':
        raise ValueError('Raw evidence path leaves the attempts directory.')
    return path


def load_accepted(run, task_id):
    run = Path(run)
    manifest = audit(run)
    task, chains = task_info(run, task_id)
    entry_path = accepted_path(run, task_id)
    entry = read(entry_path)
    raw = _evidence_path(run, entry.get('raw_path'))
    if raw.with_suffix('.json').read_bytes() != entry_path.read_bytes():
        raise ValueError('Accepted record differs from immutable attempt receipt.')
    config = manifest['config']
    expected_kind = 'synthetic_test' if config['synthetic'] else 'model_output'
    expected_keys = ('task_id', 'raw_path', 'raw_sha256', 'source_filename', 'prompt_sha256', 'model_label',
                     'effort_label', 'session_label', 'evidence_kind', 'full_prompt_confirmed', 'received_utc',
                     'actual_reasoning_tokens', 'actual_wall_time_s', 'api_calls', 'formatting_edits', 'status', 'payload')
    _keys(entry, expected_keys, 'Accepted record')
    if (entry['task_id'] != task_id or entry['status'] != 'accepted' or entry['model_label'] != config['model_label'] or
            entry['effort_label'] != config['effort_label'] or entry['evidence_kind'] != expected_kind or
            entry['full_prompt_confirmed'] is not True or not isinstance(entry['session_label'], str) or
            not entry['session_label'].strip() or entry['formatting_edits'] != [] or
            entry['actual_reasoning_tokens'] is not None or entry['actual_wall_time_s'] is not None or entry['api_calls'] != 0):
        raise ValueError('Accepted provenance metadata changed.')
    data = raw.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry['raw_sha256']:
        raise ValueError('Raw response hash mismatch.')
    if (validate_response(run, task_id, data.decode('utf-8')) != entry['payload'] or
            hashlib.sha256(prompt_text(run, task_id).encode('utf-8')).hexdigest() != entry['prompt_sha256']):
        raise ValueError('Accepted payload or prompt hash mismatch.')
    _replay_payload(manifest, task, chains, entry['payload'])
    return entry


def progress(run):
    audit(run)
    return pd.DataFrame([task | dict(students=4*len(task['chain_ids']),
                                    accepted=accepted_path(run, task['task_id']).exists())
                         for task in read(Path(run)/'plan.json')['tasks']]).drop(columns=['chain_ids'])


def next_task(run):
    audit(run)
    for task in read(Path(run)/'plan.json')['tasks']:
        if not accepted_path(run, task['task_id']).exists():
            return task | dict(prompt=prompt_text(run, task['task_id']),
                               prompt_path=str(Path(run)/'prompts'/(task['task_id']+'.txt')))
    return None


def replay(run):
    run = Path(run)
    manifest = audit(run)
    rows, probes, imports = [], [], []
    for task in read(run/'plan.json')['tasks']:
        if not accepted_path(run, task['task_id']).exists():
            continue
        entry = load_accepted(run, task['task_id'])
        _, chains = task_info(run, task['task_id'])
        task_rows, task_probes = _replay_payload(manifest, task, chains, entry['payload'])
        rows.extend(task_rows)
        probes.extend(task_probes)
        imports.append({key: value for key, value in entry.items() if key != 'payload'})
    return pd.DataFrame(rows), pd.DataFrame(probes), imports


def summarize(run):
    rounds, probes, imports = replay(run)
    common = ['task_id', 'repetition', 'arm', 'deadline_seconds', 'lecture_id', 'chain_id']
    cost_columns = ['cost_practice', 'cost_model', 'cost_automatic', 'total_cost']
    contrast_columns = ['hypothesis', 'repetition', 'chain_id', 'metric', 'reference_arm', 'treatment_arm', 'estimate', 'expected_sign']
    if rounds.empty:
        return dict(rounds=rounds, probes=probes, imports=pd.DataFrame(imports),
                    roles=pd.DataFrame(columns=common+['role', 'profile_id', 'participant_id']+cost_columns+['sensitivity']),
                    chains=pd.DataFrame(columns=common+cost_columns+['sensitivity', 'automatic_cost_fraction']),
                    contrasts=pd.DataFrame(columns=contrast_columns))
    role_keys = common+['role', 'profile_id', 'participant_id']
    roles = rounds.groupby(role_keys+['phase'], sort=False)['cost'].sum().unstack('phase', fill_value=0)
    roles = roles.reindex(columns=['practice', 'model', 'automatic'], fill_value=0)
    roles.columns = ['cost_'+phase for phase in roles.columns]
    roles['total_cost'] = roles.sum(axis=1)
    roles = roles.reset_index().merge(probes[role_keys+['sensitivity']], on=role_keys, validate='one_to_one')
    chains = roles.groupby(common, sort=False)[cost_columns].sum().reset_index()
    chain_sensitivity = roles.groupby(common, sort=False)['sensitivity'].mean().reset_index()
    chains = chains.merge(chain_sensitivity, on=common, validate='one_to_one')
    chains['automatic_cost_fraction'] = np.divide(chains['cost_automatic'], chains['total_cost'],
                                                out=np.full(len(chains), np.nan), where=chains['total_cost'].to_numpy() != 0)
    contrasts = []
    for hypothesis, (reference, treatment, metric, sign) in CONTRASTS.items():
        left = chains.loc[chains.arm == reference, ['repetition', 'chain_id', metric]]
        right = chains.loc[chains.arm == treatment, ['repetition', 'chain_id', metric]]
        paired = left.merge(right, on=['repetition', 'chain_id'], suffixes=('_reference', '_treatment'), validate='one_to_one')
        for row in paired.to_dict('records'):
            contrasts.append(dict(hypothesis=hypothesis, repetition=row['repetition'], chain_id=row['chain_id'],
                                  metric=metric, reference_arm=reference, treatment_arm=treatment,
                                  estimate=row[metric+'_treatment']-row[metric+'_reference'], expected_sign=sign))
    return dict(rounds=rounds, probes=probes, imports=pd.DataFrame(imports), roles=roles, chains=chains,
                contrasts=pd.DataFrame(contrasts, columns=contrast_columns))


def synthetic_response(run, task_id):
    manifest = audit(run)
    if not manifest['config']['synthetic']:
        raise ValueError('Synthetic fixture forbidden in a model-output run.')
    task, chains = task_info(run, task_id)
    payload = dict(schema_version=SCHEMA, study_id=manifest['study_id'], task_id=task_id,
                   deadline_seconds=task['deadline_seconds'], lecture_id=task['lecture_id'], rules=RULE_ANSWERS,
                   chains=[dict(chain_id=chain['chain_id'], orders=[[4]*4 for _ in range(manifest['config']['weeks']-4)],
                                probes=[[8, 4] for _ in ROLES]) for chain in chains], complete=True)
    return json.dumps(payload, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
