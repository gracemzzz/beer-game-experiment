"""Audit and describe isolated prompt-development outputs; never call a model."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def analyze_holdout(raw, folder):
    plan = json.loads((raw / 'PLAN.json').read_text(encoding='utf-8'))
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir() if p.is_file()}
    rows, transcript = [], ['# Held-out responses\n\nFour new isolated contexts; same plain-deadline wording, new states.\n\n']
    for response, (condition, repetition) in plan['responses'].items():
        path = raw / (response + '.json')
        if not path.exists():
            print('Holdout still awaiting', response)
            return
        text = path.read_text(encoding='utf-8')
        obj = json.loads(text)
        seconds = 10 if condition == 'brief' else 180
        assert set(obj) == {'schema_version','deadline_seconds','choices','complete'}
        assert obj['schema_version'] == 'pressure-framing-development-v1' and obj['complete'] is True
        assert type(obj['deadline_seconds']) is int and obj['deadline_seconds'] == seconds
        assert len(obj['choices']) == 32
        assert {c['id'] for c in obj['choices']} == {f't{i:02d}' for i in range(1,33)}
        for c in obj['choices']:
            assert set(c) == {'id','order'} and type(c['order']) is int and c['order'] >= 0
            rows.append(dict(response_id=response,condition=condition,repetition=repetition,case_id=c['id'],order=c['order']))
        name = condition.upper() + '.md'
        content = (raw / name).read_bytes()
        assert hashlib.sha256(content).hexdigest() == plan['prompts_md_sha256'][name]
        assert content == (folder / name).read_bytes()
        # Instructions remain exactly those of the selected development candidate.
        original = (folder.parent / ('PLAIN_DEADLINE_' + condition.upper() + '.md')).read_text(encoding='utf-8')
        assert content.decode().split('```text\n',1)[1].split('INPUT CASES\n')[0] == original.split('```text\n',1)[1].split('INPUT CASES\n')[0]
        transcript += [f'## {response}: {condition}, repetition {repetition}\n\nPrompt: [{name}]({name}).\n\n```json\n{text.rstrip()}\n```\n\n']
    df = pd.DataFrame(rows)
    stats = []
    for repetition in (1,2):
        q = df[df.repetition == repetition].pivot(index='case_id',columns='condition',values='order')
        delta = q.brief - q.ample
        stats.append(dict(comparison=f'brief vs ample, repetition {repetition}',kind='between_conditions',
            changed_choices=int((delta != 0).sum()),choices=32,
            mean_signed_difference=float(delta.mean()),mean_absolute_difference=float(abs(delta).mean())))
    for condition in ('brief','ample'):
        q = df[df.condition == condition].pivot(index='case_id',columns='repetition',values='order')
        delta = q[1] - q[2]
        stats.append(dict(comparison=f'{condition}, repetition 1 vs 2',kind='within_condition',
            changed_choices=int((delta != 0).sum()),choices=32,
            mean_signed_difference=float(delta.mean()),mean_absolute_difference=float(abs(delta).mean())))
    stats = pd.DataFrame(stats)
    df.to_csv(folder / 'CHOICES.csv',index=False)
    stats.to_csv(folder / 'COMPARISONS.csv',index=False)
    (folder / 'TRANSCRIPTS.md').write_text(''.join(transcript),encoding='utf-8')
    with pd.ExcelWriter(folder.parent / 'DEVELOPMENT_RESULTS.xlsx', mode='a',engine='openpyxl',if_sheet_exists='replace') as writer:
        df.to_excel(writer,sheet_name='holdout_choices',index=False)
        stats.to_excel(writer,sheet_name='holdout_comparisons',index=False)
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir() if p.is_file()}
    assert before == after
    check = dict(status='passed',responses=4,total_choices=128,all_prompts_unchanged_from_selected_candidate=True,
        raw_sha256=after,comparisons=stats.to_dict(orient='records'),explicit_api_calls=0,
        inferential_statistics=False,measured_time_pressure=False)
    (folder / 'CHECKS.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
    print('\nHELD-OUT STATES\n'+stats.to_string(index=False))


def main():
    raw = ROOT / 'data/development/pressure_prompt_development_20261018'
    folder = ROOT / 'reports/pressure_prompt_development_20261018'
    provenance = json.loads((raw / 'PROVENANCE.json').read_text(encoding='utf-8'))
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir() if p.is_file()}
    rows, transcripts = [], ['# Exact development prompts and returned choices\n\n'
        'Eight isolated assistant responses, two per condition/candidate. No parent conversation was passed. '
        'These are development outputs, not GPT-6 / Pro website measurements or human observations.\n\n']
    for trial, (candidate, condition, repetition) in provenance['trials'].items():
        path = raw / (trial + '.json')
        if not path.exists():
            raise ValueError('Still awaiting '+trial+'; do not silently reduce the planned screen.')
        text = path.read_text(encoding='utf-8')
        obj = json.loads(text)
        assert set(obj) == {'schema_version', 'deadline_seconds', 'choices', 'complete'}
        assert obj['schema_version'] == 'pressure-framing-development-v1' and obj['complete'] is True
        seconds = 10 if condition == 'brief' else 180
        assert type(obj['deadline_seconds']) is int and obj['deadline_seconds'] == seconds
        choices = obj['choices']
        assert len(choices) == 32 and {c['id'] for c in choices} == {f't{i:02d}' for i in range(1,33)}
        assert all(set(c) == {'id','order'} and type(c['order']) is int and c['order'] >= 0 for c in choices)
        prompt_name = (candidate + '_' + condition).upper() + '.md'
        prompt_bytes = (raw / prompt_name).read_bytes()
        assert hashlib.sha256(prompt_bytes).hexdigest() == provenance['prompts_md_sha256'][prompt_name]
        assert prompt_bytes == (folder / prompt_name).read_bytes()
        for c in choices:
            rows.append(dict(response_id=trial,candidate=candidate,condition=condition,
                             repetition=repetition,deadline_seconds=seconds,case_id=c['id'],order=c['order']))
        transcripts += [f'## {trial}: {candidate}, {condition}, repetition {repetition}\n\n',
                        f'Exact prompt: [{prompt_name}]({prompt_name}). Raw response:\n\n```json\n{text.rstrip()}\n```\n\n']
    df = pd.DataFrame(rows)
    comparisons = []
    for candidate, frame in df.groupby('candidate', sort=False):
        for repetition in (1,2):
            table = frame[frame.repetition == repetition].pivot(index='case_id', columns='condition', values='order')
            delta = table.brief - table.ample
            comparisons.append(dict(candidate=candidate,comparison=f'brief vs ample, repetition {repetition}',
                kind='between_conditions',changed_choices=int((delta != 0).sum()),choices=32,
                mean_signed_difference=float(delta.mean()),mean_absolute_difference=float(abs(delta).mean())))
        for condition in ('brief','ample'):
            table = frame[frame.condition == condition].pivot(index='case_id',columns='repetition',values='order')
            delta = table[1] - table[2]
            comparisons.append(dict(candidate=candidate,comparison=f'{condition}, repetition 1 vs 2',
                kind='within_condition',changed_choices=int((delta != 0).sum()),choices=32,
                mean_signed_difference=float(delta.mean()),mean_absolute_difference=float(abs(delta).mean())))
    contrasts = pd.DataFrame(comparisons)
    df.to_csv(folder / 'CHOICES.csv', index=False)
    contrasts.to_csv(folder / 'COMPARISONS.csv', index=False)
    with pd.ExcelWriter(folder / 'DEVELOPMENT_RESULTS.xlsx') as writer:
        df.to_excel(writer, sheet_name='choices', index=False)
        contrasts.to_excel(writer, sheet_name='comparisons', index=False)
    (folder / 'TRANSCRIPTS.md').write_text(''.join(transcripts), encoding='utf-8')
    matrix = df.pivot(index='response_id',columns='case_id',values='order')
    fig, ax = plt.subplots(figsize=(14,4.7))
    im = ax.imshow(matrix.values, aspect='auto', cmap='cividis', vmin=0)
    ax.set(xticks=range(32), xticklabels=matrix.columns, yticks=range(8),
           yticklabels=[f'{r} | {provenance["trials"][r][0]} | {provenance["trials"][r][1]}' for r in matrix.index],
           xlabel='Identical profile/state cases', title='Exploratory assistant responses: all eight retained')
    ax.tick_params(axis='x',labelsize=8)
    fig.colorbar(im, ax=ax,label='Ordered cases')
    fig.text(.02,.01,'Fictional deadlines; no enforced runtime or independent-student inference.',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,1))
    for ext in ('png','pdf'):fig.savefig(folder / ('ALL_CHOICES.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig)
    assert hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir() if p.is_file()}
    check = dict(status='passed',responses=8,choices_per_response=32,total_choices=256,
        raw_files_unchanged=len(hashes),raw_sha256=hashes,explicit_api_calls=0,
        inferential_statistics=False,verified_ui_backend=False,measured_time_pressure=False,
        comparisons=comparisons)
    (folder / 'CHECKS.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
    print(contrasts.to_string(index=False))
    print('All eight responses, prompt hashes, schemas and raw-file preservation checked.')
    if (raw / 'holdout/PLAN.json').exists():
        analyze_holdout(raw / 'holdout', folder / 'holdout')


if __name__ == '__main__':
    main()
