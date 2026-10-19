"""Check completed repeat comparisons directly against saved decisions; no model calls."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from beergame_study.deadline_cohort import audit, load_accepted, next_task, progress, read


def hashes(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--before', type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    root = run.parents[2]
    before = read(args.before)
    current = hashes(run)
    audit(run)
    assert progress(run).accepted.all() and next_task(run) is None
    for name, digest in before['run_files'].items():
        assert current[name] == digest, name
    for name, digest in before['previous_report_pointers'].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name

    record = read(root / 'reports/software_checks' / (run.name + '_audit.json'))
    assert record['complete'] and record['status'] == 'passed'
    folder = Path(record['report']).parent
    assert read(folder / 'provenance.json')['inputs_sha256'] == {
        k: v for k, v in current.items() if 'inbox' not in Path(k).parts}
    old = folder.parent / before['prior_analysis']
    chains = pd.read_csv(folder / 'chains.csv')
    contrasts = pd.read_csv(folder / 'contrasts.csv')
    repeats = pd.read_csv(folder / 'repeat_variation.csv')
    changes = pd.read_csv(folder / 'choice_changes.csv', dtype={'generation': str})
    for name in ('chains', 'contrasts', 'batches', 'choice_changes', 'quality'):
        frame = pd.read_csv(folder / (name + '.csv'), dtype={'generation': str})
        previous = pd.read_csv(old / (name + '.csv'), dtype={'generation': str})
        first = frame[frame.generation.astype(str) == '1'].reset_index(drop=True)
        pd.testing.assert_frame_equal(first, previous, check_dtype=False)

    plan = read(run / 'plan.json')
    entries = {t['task_id']: load_accepted(run, t['task_id']) for t in plan['tasks']}
    by_task = {}
    for task in plan['tasks']:
        choices = entries[task['task_id']]['payload']['chains']
        by_id = {c['chain_id']: c for c in choices}
        by_task[(task['batch_id'], task['generation'], task['condition'])] = np.asarray(
            [by_id[c]['orders'] for c in sorted(task['chain_ids'])])
    for row in changes.itertuples(index=False):
        if row.kind == 'between_deadlines':
            a = by_task[(row.batch_id, int(row.generation), 'brief')]
            b = by_task[(row.batch_id, int(row.generation), 'ample')]
        else:
            ga, gb = map(int, row.generation.split('-'))
            a = by_task[(row.batch_id, ga, row.condition)]
            b = by_task[(row.batch_id, gb, row.condition)]
        difference = a - b
        assert row.choices == difference.size
        assert row.changed == np.count_nonzero(difference)
        np.testing.assert_allclose(row.changed_fraction, np.mean(difference != 0))
        np.testing.assert_allclose(row.mean_absolute_change, np.mean(abs(difference)))

    metrics = ['sensitivity', 'cost', 'bullwhip']
    indexed = chains.set_index(['batch_id', 'chain_id', 'condition', 'generation'])
    expected_keys = set()
    for key, group in chains.groupby(['batch_id', 'chain_id', 'condition']):
        for ga, gb in itertools.combinations(sorted(group.generation), 2):
            expected_keys.add((*key, ga, gb))
    actual_keys = set()
    for row in repeats.itertuples(index=False):
        key = (row.batch_id, row.chain_id, row.condition)
        actual_keys.add((*key, row.generation_a, row.generation_b))
        for metric in metrics:
            delta = indexed.loc[(*key, row.generation_a), metric] - indexed.loc[(*key, row.generation_b), metric]
            np.testing.assert_allclose(getattr(row, metric + '_difference'), delta, atol=1e-12)
    assert actual_keys == expected_keys and len(actual_keys) == len(repeats)

    for item in before['attachments']:
        entry = entries[item['task_id']]
        assert entry['raw_sha256'] == item['sha256']
        assert not entry['formatting_edits']
        assert (run / entry['raw_path']).stat().st_size == item['bytes']
    assert hashes(run) == current
    differences = [m + '_difference' for m in metrics]
    output = dict(status='passed', run=str(run), report=str(folder / 'REPORT.md'),
        accepted_responses=len(entries), prior_files_preserved=len(before['run_files']),
        raw_files_unchanged=len(current), prior_pointers_unchanged=True,
        first_generation_tables_unchanged=True, exact_new_attachments=len(before['attachments']),
        direct_order_comparisons=len(changes), repeat_metric_rows=len(repeats),
        generation_mean_differences=contrasts.groupby('generation')[differences].mean().to_dict('index'),
        absolute_deadline_differences=contrasts[differences].abs().mean().to_dict(),
        absolute_repeat_differences=repeats.groupby('condition')[differences].agg(lambda x: x.abs().mean()).to_dict('index'),
        cost_phase_means=chains.groupby('condition')[['practice_cost', 'model_cost', 'automatic_cost']].mean().to_dict('index'),
        api_calls=0)
    target = root / 'reports/software_checks' / (run.name + '_completion.json')
    target.write_text(json.dumps(output, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
