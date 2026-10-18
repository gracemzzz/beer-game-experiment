"""Recheck the completed 18 October manual collection; no API calls or raw writes."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

import nbformat
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study.manual_cohort_chat import audit, load_accepted, next_task, read


def hashes(run):
    return {p.relative_to(run).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(run.rglob('*')) if p.is_file()}


def main():
    os.chdir(ROOT)
    run = ROOT / 'data/runs/manual_cohort_975b76e63e5b4882'
    pointer = ROOT / 'reports/LATEST_MANUAL_COHORT_REPORT.json'
    if Path(read(pointer)['run']).resolve() != run.resolve():
        raise ValueError('This dated check requires the completed October 18 run as the latest manual run.')
    before = hashes(run)
    audit(run)
    assert next_task(run) is None
    nb = nbformat.read(ROOT / 'notebooks/06_manual_cohort_simulation.ipynb', as_version=4)
    nbformat.validate(nb)
    cells = [c.source for c in nb.cells if c.cell_type == 'code']
    assert len(cells) == 8
    log = io.StringIO()
    ns = {'__name__': '__manual_completion_check__'}
    with patch('openai.OpenAI', side_effect=AssertionError('API forbidden')), \
         patch('anthropic.Anthropic', side_effect=AssertionError('API forbidden')), \
         patch('IPython.display.display'), redirect_stdout(log):
        for i, source in enumerate(cells):
            exec(compile(source, f'notebook06-cell-{i}', 'exec'), ns)
    assert ns['RUN'].resolve() == run.resolve() and ns['TASK'] is None
    assert ns['build_report'].__module__ == 'beergame_study.manual_response_formatting'
    result = ns['RESULT']
    assert result['complete'] and len(ns['chain_selector'].options) == 125
    tables, rounds = result['tables'], result['rounds']
    assert len(tables['contrasts']) == 125 and len(rounds) == 36000
    assert len(result['probes']) == 1000
    plan = read(run / 'plan.json')
    specs = {c['chain_id']: c for c in plan['chains']}
    direct, changes = [], []
    for batch in plan['batches']:
        bid = batch['batch_id']
        entries = {s: load_accepted(run, bid, s) for s in ('initial', 'revision')}
        by_stage = {s: {c['chain_id']: c for c in e['payload']['chains']}
                    for s, e in entries.items()}
        changed = dict(batch_id=bid, orders=0, probe_choices=0)
        for cid in batch['chain_ids']:
            initial, revision = (by_stage[s][cid] for s in ('initial', 'revision'))
            changed['orders'] += int(np.count_nonzero(np.array(initial['orders']) != revision['orders']))
            changed['probe_choices'] += int(np.count_nonzero(np.array(initial['probes']) != revision['probes']))
            for stage in ('initial', 'revision'):
                own = by_stage[stage][cid]
                q = np.asarray(own['orders'])
                probes = np.asarray(own['probes'])
                demand = np.asarray(specs[cid]['customer_demand'][4:])
                denominator = float(np.var(demand, ddof=1))
                frame = rounds[(rounds.chain_id == cid) & (rounds.condition == stage)]
                # Recheck the holding/backlog cost identity, independently of report aggregation.
                expected_cost = .5 * frame.inventory + frame.backlog
                np.testing.assert_allclose(frame.cost, expected_cost, rtol=0, atol=0)
                direct.append(dict(chain_id=cid, condition=stage,
                    sensitivity=float(np.mean((probes[:, 0] - probes[:, 1]) / 24)),
                    bullwhip=float(np.mean(np.var(q, axis=0, ddof=1) / denominator))
                             if denominator > 0 else float('nan'),
                    cost=float(expected_cost.sum())))
        changes.append(changed)
    direct = pd.DataFrame(direct)
    metrics = {'H1': 'sensitivity', 'H2': 'cost', 'H3': 'bullwhip'}
    for h, metric in metrics.items():
        actual = tables['hypotheses'].set_index('hypothesis').loc[h]
        paired = direct.pivot(index='chain_id', columns='condition', values=metric)
        for stage in ('initial', 'revision'):
            np.testing.assert_allclose(actual[stage], paired[stage].mean(), rtol=1e-12)
        np.testing.assert_allclose(actual.initial_minus_revision,
                                  (paired.initial - paired.revision).mean(), rtol=1e-12)
        assert int(actual.defined_chain_pairs) == 125
    assert tables['hypotheses'][['p_value', 'ci_lower', 'ci_upper']].isna().all().all()
    for metric in metrics.values():
        paired = direct.pivot(index='chain_id', columns='condition', values=metric)
        actual = tables['contrasts'].set_index('chain_id').loc[paired.index, metric + '_difference']
        np.testing.assert_allclose(actual, paired.initial - paired.revision, rtol=1e-12)
    folder = result['folder']
    assert len(result['images']) == 6
    for name in result['images']:
        assert (folder / (name + '.png')).read_bytes().startswith(b'\x89PNG')
        assert (folder / (name + '.pdf')).read_bytes().startswith(b'%PDF')
    for name, expected in tables.items():
        exported = pd.read_excel(folder / 'RESULTS.xlsx', sheet_name=name)
        # Normalize None and NaN only in comparison copies, not stored scientific tables.
        expected = expected.copy()
        for col in expected.columns:
            if expected[col].isna().all():
                expected[col] = np.nan
        pd.testing.assert_frame_equal(exported, expected, check_dtype=False, atol=1e-10, rtol=1e-10)
    assert len(pd.read_excel(folder / 'RESULTS.xlsx', sheet_name='rounds')) == 36000
    assert len(pd.read_excel(folder / 'RESULTS.xlsx', sheet_name='probes')) == 1000
    report = result['report'].read_text(encoding='utf-8')
    for bid, stage in [('b0001', 'revision'), ('b0002', 'revision'),
                       ('b0004', 'initial'), ('b0005', 'initial')]:
        assert f'**{bid} {stage}:**' in report
    assert '10/10' in report and '5/5' in report and '**complete**' in report
    assert hashes(run) == before
    audit(run)
    checks = dict(status='passed', date='2026-10-18', api_calls=0, notebook_cells=8,
        run_files_unchanged=len(before), accepted_responses=10, paired_batches=5,
        paired_chains=125, fictional_identities=500, submitted_weekly_orders=20000,
        replayed_role_states=36000, probe_pairs=1000, next_task=None,
        formatting_disclosures=4, figures=6, interactive_chains=125,
        workbook_tables_checked=len(tables) + 2, per_batch_changes=changes,
        changed_weekly_orders=sum(c['orders'] for c in changes),
        changed_probe_choices=sum(c['probe_choices'] for c in changes),
        direct_hypothesis_calculation='passed', cost_identity='passed',
        generated_student_inference_withheld=True, scientific_source_audit='passed',
        analysis_signature=folder.name, report=str(result['report']))
    (ROOT / 'reports/software_checks/manual_chat_complete_20261018.json').write_text(
        json.dumps(checks, indent=2), encoding='utf-8')
    log_folder = ROOT / 'reports/logs/manual_chat_20261018'
    log_folder.mkdir(parents=True, exist_ok=True)
    (log_folder / 'completion_notebook.log').write_text(log.getvalue(), encoding='utf-8')
    print(json.dumps(checks, indent=2))
    print(tables['hypotheses'].to_string(index=False))
    print(tables['quality'].to_string(index=False))
    print(tables['chains'].groupby('condition')[['practice_cost', 'model_cost', 'automatic_cost']].mean().to_string())
    print(tables['roles'].groupby(['condition', 'role']).bullwhip.mean().to_string())


if __name__ == '__main__':
    main()
