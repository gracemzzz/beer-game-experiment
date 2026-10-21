"""Saved-data reports for experiment 12. This module never makes API calls."""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import platform

import pandas as pd

from . import batched_pressure as study
from .batched_pressure_api import estimate


def _table(rows, columns):
    def cell(value):
        if value is None:
            return '—'
        if isinstance(value, float):
            return f'{value:,.4f}'
        return str(value).replace('|', '/')
    return '\n'.join(['| ' + ' | '.join(columns) + ' |',
                       '| ' + ' | '.join('---' for _ in columns) + ' |']
                     + ['| ' + ' | '.join(cell(r.get(c)) for c in columns) + ' |' for r in rows])


def build_report(run):
    run = Path(run).resolve()
    experiment = run.parent.parent
    result = study.analyze(run)
    plan = study.loadplan(run)
    ledger_path = experiment / 'data' / 'api_budget.json'
    ledger = study.read(ledger_path) if ledger_path.exists() else {'cap_usd': 5, 'attempts': {}}
    status_path = run / 'api_status.json'
    status = study.read(status_path) if status_path.exists() else {'tasks': {}, 'returned_models': {}}
    attempts = [dict(attempt_id=k, **v) for k, v in ledger['attempts'].items()]
    spent = sum(a['charge_usd'] for a in attempts)
    projections = estimate(run)
    report_id = study.digest(dict(result=result, attempts=attempts, status=status,
                                  renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                  python=platform.python_version(), pandas=pd.__version__))[:12]
    analysis = experiment / 'analysis' / run.name / report_id
    publication = experiment / 'reports' / 'history' / report_id
    analysis.mkdir(parents=True, exist_ok=True)
    publication.mkdir(parents=True, exist_ok=True)
    tables = {name: pd.DataFrame(result[name]) for name in (
        'hypotheses', 'contrasts', 'chains', 'rounds', 'probes', 'task_status', 'model_status')}
    tables['api_attempts'] = pd.DataFrame(attempts)
    tables['budget_estimate'] = pd.DataFrame(projections)
    for name, table in tables.items():
        study.save_new(analysis / (name + '.csv'), table.to_csv(index=False))
    workbook = analysis / 'RESULTS.xlsx'
    if not workbook.exists():
        with pd.ExcelWriter(workbook, engine='openpyxl') as writer:
            for name, table in tables.items():
                table.to_excel(writer, sheet_name=name, index=False)
    study.save_new(analysis / 'analysis.json', result)
    available = [r for r in result['hypotheses'] if r['mean_strong_minus_no'] is not None]
    main_responses = sum(r['accepted_main_responses'] for r in result['model_status'])
    pilot_responses = sum(r['accepted_pilot_responses'] for r in result['model_status'])
    link = lambda p: os.path.relpath(p, publication).replace(os.sep, '/')
    conclusions = [
        f'1. **Collection:** {main_responses}/4 main responses and {pilot_responses}/4 pilot responses accepted.',
        ('2. **H1/H2 findings:** No main API results have been collected. Software checks do not provide hypothesis evidence.'
         if not available else
         '2. **H1/H2 findings:** ' + '; '.join(
             f"{r['model']} {r['hypothesis']}: {r['mean_strong_minus_no']:+.4f} ({r['descriptive_direction']})"
             for r in available) + '. Differences are strong pressure minus no pressure; these are descriptive findings.'),
        '3. **Interpretation:** This tests imagined pressure framing. It does not establish a binding deadline, original structural β, or effects on real students.',
        '4. **Statistical independence:** All 20 chains and both conditions share one main response per model. No p-values or inferential confidence intervals are reported.',
        f'5. **Budget:** ${spent:.4f} charged or conservatively reserved out of the authorized $5 total across this experiment, including pilot and retries.',
    ]
    lines = ['# Experiment 12: conclusions first', '', *conclusions, '',
             '## Design', '',
             'Each model represents 80 fictional students in 20 four-role chains: 10 no-pressure and 10 strong-pressure chains. '
             'Each chain submits all 24 weeks at once. H2 includes only those 24 weeks; there are no automatic continuation costs. '
             'Matched chains share demand paths and profile assignments. Four disjoint two-chain pilot responses are outside the main sample.', '',
             'All models use low effort; the same settings apply to both conditions. The pilot cap is 8,192 output tokens and the main cap is 16,384, including hidden reasoning. '
             'These are completion allowances, not the experimental pressure manipulation. Provider effort labels are not equivalent measurements of computation.', '',
             '## Findings by model', '',
             _table(result['hypotheses'], ['model', 'hypothesis', 'paired_blocks', 'mean_strong_minus_no', 'descriptive_direction']), '',
             '**H1:** mean reduction in order divided by a 24-case increase in outstanding dispatched replenishment, over eight matched probes per chain. '
             'A smaller sensitivity under strong pressure is consistent with the predicted proxy direction. This does not identify an optimal benchmark or the original structural coefficient.', '',
             '**H2:** cumulative chain holding cost ($0.50 per case-week) plus backlog cost ($1 per case-week). '
             'A positive strong-minus-no-pressure difference follows the prediction. There is no revenue or factory production fee.', '',
             '## Completion and technical checks', '',
             _table(result['model_status'], ['model', 'accepted_pilot_responses', 'accepted_main_responses', 'accepted_main', 'complete']), '',
             'Acceptance requires all chain IDs, 24 order rows, probes, factual rules and inventory readbacks at weeks 1, 12 and 24. '
             'The four pilots must all pass before any main call. An incorrect or incomplete response is retained; no semantic retries, replacement cohorts, clipping or filled-in orders are used. '
             'At most one retry is allowed for a transient transport/rate/server error, with its cost reserved.', '']
    execution = [dict(task_id=k, **v) for k, v in status.get('tasks', {}).items()]
    if execution:
        lines += [_table(execution, ['task_id', 'status', 'reason']), '']
    main_chains = [r for r in result['chains'] if r['phase'] == 'main']
    if main_chains:
        lines += ['## All chain results', '', _table(main_chains, [
            'model', 'block', 'condition', 'holding_cost', 'backlog_cost', 'total_cost',
            'sensitivity', 'zero_orders', 'max_order', 'final_backlog', 'final_supply_line']), '']
    lines += ['## Spending and models', '',
              f'First-attempt conservative reservation for all eight planned calls: **${sum(r["first_attempt_reservation_ceiling_usd"] for r in projections):.4f}**. '
              'This assumes every output cap is filled and uses a conservative input byte bound. Actual token usage settles each reservation; an uncertain charge keeps its full reservation. '
              'Prices were checked on 20 October 2026. The local ledger is not an account balance.', '',
              _table(projections, ['model', 'pilot_calls', 'main_calls', 'first_attempt_reservation_ceiling_usd']), '',
              'Returned model IDs: ' + (json.dumps(status.get('returned_models', {})) if status.get('returned_models') else 'No provider responses yet.'), '',
              '## Limits', '', *['- ' + item for item in result['limitations']], '',
              'A directionally null result is a zero or small descriptive contrast in this generated sample; it does not prove no effect. '
              'More generated identities within one reply cannot supply independent replication. Testing literal H1/H2 requires a separate enforced-time/computation design and independent collection.', '',
              '## Files', '',
              f'- [Excel: results and costs]({link(workbook)})',
              f'- [All weekly states and orders]({link(analysis / "rounds.csv")})',
              f'- [Hypotheses and comparisons]({link(analysis / "hypotheses.csv")})',
              f'- [Exact prompts and schemas]({link(experiment / "prompts" / run.name)})',
              f'- [Frozen plan]({link(run / "plan.json")})',
              f'- [Original API records]({link(experiment / "raw" / run.name)})',
              f'- [Protocol]({link(experiment / "hypotheses" / "PROTOCOL.md")})', '']
    report = publication / 'REPORT.md'
    study.save_new(report, '\n'.join(lines))
    landing = experiment / 'reports' / 'REPORT.md'
    landing.write_text('# Experiment 12: latest findings\n\n' + '\n'.join(conclusions)
                       + f'\n\n[Open the full report](history/{report_id}/REPORT.md).\n', encoding='utf-8')
    (experiment / 'reports' / 'LATEST.json').write_text(json.dumps(dict(
        run=run.name, report=str(report.relative_to(experiment)),
        analysis=str(analysis.relative_to(experiment)), main_responses=main_responses,
        pilot_responses=pilot_responses, charged_or_reserved_usd=spent), indent=2) + '\n', encoding='utf-8')
    return dict(report=report, analysis=analysis, workbook=workbook, summary=result,
                charged_or_reserved_usd=spent, reservation_ceiling_usd=sum(
                    r['first_attempt_reservation_ceiling_usd'] for r in projections))
