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


def build_report(run, *, recovery=None, followup=None):
    run = Path(run).resolve()
    experiment = run.parent.parent
    plan = study.loadplan(run)
    stage = Path(followup or recovery).resolve() if (followup or recovery) else None
    if stage is None:
        result = study.analyze(run)
        projections = estimate(run)
        status_path = run / 'api_status.json'
        report_label = run.name
    else:
        if followup:
            from . import batched_pressure_followup as recovery_study
        else:
            from . import batched_pressure_recovery as recovery_study
        recovery_manifest = recovery_study.load(stage)
        if stage.parent.parent != run:
            raise ValueError('Collection stage belongs to a different parent run.')
        result = recovery_study.analyze(stage)
        projections = recovery_study.estimate(stage)
        status_path = stage / 'api_status.json'
        report_label = run.name + '__' + stage.name
    ledger_path = experiment / 'data' / 'api_budget.json'
    ledger = study.read(ledger_path) if ledger_path.exists() else {'cap_usd': 5, 'attempts': {}}
    status = study.read(status_path) if status_path.exists() else {'tasks': {}, 'returned_models': {}}
    if stage is not None:
        for entry in recovery_manifest['inherited_pilots'].values():
            status.setdefault('returned_models', {}).setdefault(entry['model'], entry['returned_model'])
    attempts = [dict(attempt_id=k, **v) for k, v in ledger['attempts'].items()]
    spent = sum(a['charge_usd'] for a in attempts)
    report_id = study.digest(dict(result=result, attempts=attempts, status=status, report_label=report_label,
                                  renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                  python=platform.python_version(), pandas=pd.__version__))[:12]
    analysis = experiment / 'analysis' / report_label / report_id
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
    failed = [(key, row) for key, row in status.get('tasks', {}).items()
              if row.get('status') in ('invalid', 'failed', 'interrupted')]
    blocked = sum(row.get('status') == 'pilot_blocked' for row in status.get('tasks', {}).values())
    def failure_reason(row):
        if any('Physical inventory readback mismatch' in issue for issue in row.get('issues', [])):
            return 'inventory calculations disagree with the game engine'
        return str(row.get('reason', row.get('status', 'unknown failure'))).replace('_', ' ')
    failure_summary = (' **Current failure:** ' + '; '.join(
        f"{row.get('model', key)}: {failure_reason(row)}" for key, row in failed)
        + f'. {blocked} main calls blocked.' if failed else '')
    conclusions = [
        f'1. **Collection:** {main_responses}/4 main responses and {pilot_responses}/4 pilot responses accepted.' + failure_summary,
        ('2. **H1/H2 findings:** No main API results have been collected. Software checks do not provide hypothesis evidence.'
         if not available else
         '2. **H1/H2 findings:** ' + '; '.join(
             f"{r['model']} {r['hypothesis']}: {r['mean_strong_minus_no']:+.4f} ({r['descriptive_direction']})"
             for r in available) + '. Differences are strong pressure minus no pressure; these are descriptive findings.'),
        '3. **Interpretation:** This tests imagined pressure framing. It does not establish a binding deadline, original structural β, or effects on real students.',
        '4. **Statistical independence:** All 20 chains and both conditions share one main response per model. No p-values or inferential confidence intervals are reported.',
        f'5. **Budget:** ${spent:.4f} charged or conservatively reserved out of the authorized $5 total across this experiment, including pilot and retries.',
    ]
    if followup:
        conclusions.append('6. **Claude follow-up:** Three accepted GPT pilots are reused. One revised Claude pilot is scheduled with medium effort and explicit physical bookkeeping; both earlier Claude failures remain preserved.')
    elif recovery is not None:
        conclusions.append('6. **Recovery:** Two previously accepted GPT-5.6 pilots are reused. The original GPT-6 inventory failure and Claude token-limit failure remain preserved; recovery changes are recorded separately.')
    settings = (
        'All models use low effort; the same settings apply to both conditions. The pilot cap is 8,192 output tokens and the main cap is 16,384, including hidden reasoning.'
        if stage is None else
        'Recovery settings: GPT-6 Luna uses medium effort with 16,384 pilot / 32,768 main output tokens and an explicit accounting algorithm. Claude Haiku keeps adaptive thinking at low effort with 32,768 pilot / 65,536 main output tokens and a concise-completion reminder. Both GPT-5.6 models retain low effort and their original settings. Settings are identical across pressure conditions within each model, but differ across models; model comparisons therefore include settings differences.')
    if followup:
        settings = settings.replace('Claude Haiku keeps adaptive thinking at low effort', 'Claude Haiku uses adaptive thinking at medium effort').replace('and a concise-completion reminder', 'and explicit physical queue bookkeeping plus a concise-completion reminder')
    acceptance = (
        'The four pilots must all pass before any main call. An incorrect or incomplete response is retained; no semantic retries, replacement cohorts, clipping or filled-in orders are used. '
        if stage is None else
        'All four pilot slots must pass before main collection, including the two inherited accepted pilots. The user-authorized recovery provides one revised generation for each of the two failed pilots. Original failures are retained. Further semantic retries, replacements, clipping and filled-in orders are not used. ')
    if followup:
        acceptance = ('All four pilot slots must pass before main collection, including the three inherited accepted GPT pilots. '
                      'This follow-up provides one revised Claude pilot generation. Prior failures are retained. '
                      'Further semantic retries, replacements, clipping and filled-in orders are not used. ')
    lines = ['# Experiment 12: conclusions first', '', *conclusions, '',
             '## Design', '',
             'Each model represents 80 fictional students in 20 four-role chains: 10 no-pressure and 10 strong-pressure chains. '
             'Each chain submits all 24 weeks at once. H2 includes only those 24 weeks; there are no automatic continuation costs. '
             'Matched chains share demand paths and profile assignments. Four disjoint two-chain pilot responses are outside the main sample.', '',
             settings + ' These are completion allowances, not the experimental pressure manipulation. Provider effort labels are not equivalent measurements of computation.', '',
             '## Findings by model', '',
             _table(result['hypotheses'], ['model', 'hypothesis', 'paired_blocks', 'mean_strong_minus_no', 'descriptive_direction']), '',
             '**H1:** mean reduction in order divided by a 24-case increase in outstanding dispatched replenishment, over eight matched probes per chain. '
             'A smaller sensitivity under strong pressure is consistent with the predicted proxy direction. This does not identify an optimal benchmark or the original structural coefficient.', '',
             '**H2:** cumulative chain holding cost ($0.50 per case-week) plus backlog cost ($1 per case-week). '
             'A positive strong-minus-no-pressure difference follows the prediction. There is no revenue or factory production fee.', '',
             '## Completion and technical checks', '',
             _table(result['model_status'], ['model', 'accepted_pilot_responses', 'accepted_main_responses', 'accepted_main', 'complete']), '',
             'Acceptance requires all chain IDs, 24 order rows, probes, factual rules and inventory readbacks at weeks 1, 12 and 24. '
             + acceptance + 'At most one retry is allowed for a transient transport/rate/server error, with its cost reserved.', '']
    if stage is not None:
        lines += ['## Preserved pilot diagnosis', '',
                  '- GPT-6 Luna returned complete choices, but its week-12 and week-24 inventory readbacks disagreed with independent game replay. It was not an API connection or balance failure.',
                  '- Claude Haiku returned HTTP 200 with `stop_reason=max_tokens`: all 8,192 output tokens were reasoning tokens and there was no answer text. This was truncation, not a refusal.',
                  '- Original recorded charge estimate: $0.0716918. All old charges remain in the shared $5 ledger. The first recovery scheduled two pilot calls and four main calls before possible transient retries.',
                  '- Software verification cannot guarantee the next model-generated trajectories pass. A new failure remains visible and does not become a fabricated participant.', '',
                  f'[Recovery amendment]({link(experiment / "hypotheses/RECOVERY_20261021.md")}) · [Frozen current inputs and status]({link(stage)})', '']
    if followup:
        lines += ['### Outcome of the first recovery', '',
                  'GPT-6 Luna passed. Claude finished JSON normally using 3,519 of 32,768 output tokens, but four inventory checkpoints were incorrect. '
                  'This follow-up addresses state bookkeeping rather than increasing the cap again. Three accepted pilots are inherited; only Claude receives another pilot generation. '
                  'Cumulative recorded spending before this stage was $0.07590755.', '',
                  f'[Claude follow-up amendment]({link(experiment / "hypotheses/CLAUDE_FOLLOWUP_20261021.md")})', '']
    execution = [dict(task_id=k, **v) for k, v in status.get('tasks', {}).items()]
    if execution:
        lines += [_table(execution, ['task_id', 'status', 'reason']), '']
    if failed:
        lines += ['### Current failed checks', '']
        for key, row in failed:
            lines += [f"**{row.get('model', key)} ({row.get('phase', 'unknown phase')}):** {failure_reason(row)}.", '']
            lines += ['- ' + issue for issue in row.get('issues', [])]
            lines += ['']
        lines += ['The current stage retains these failures. Re-running the same collection cell does not buy another generated response for a failed slot. '
                  'Any further change to settings, pilot attempts or the all-model gate requires a separate recorded amendment; already accepted pilots remain available for reuse.', '']
    main_chains = [r for r in result['chains'] if r['phase'] == 'main']
    if main_chains:
        lines += ['## All chain results', '', _table(main_chains, [
            'model', 'block', 'condition', 'holding_cost', 'backlog_cost', 'total_cost',
            'sensitivity', 'zero_orders', 'max_order', 'final_backlog', 'final_supply_line']), '']
    lines += ['## Spending and models', '',
              f'First-attempt conservative reservation for the {sum(r["pilot_calls"] + r["main_calls"] for r in projections)} planned calls in this collection stage: **${sum(r["first_attempt_reservation_ceiling_usd"] for r in projections):.4f}**. '
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
        pilot_responses=pilot_responses, charged_or_reserved_usd=spent,
        recovery=str(Path(recovery).resolve().relative_to(experiment)) if recovery else None,
        followup=str(Path(followup).resolve().relative_to(experiment)) if followup else None), indent=2) + '\n', encoding='utf-8')
    return dict(report=report, analysis=analysis, workbook=workbook, summary=result,
                charged_or_reserved_usd=spent, reservation_ceiling_usd=sum(
                    r['first_attempt_reservation_ceiling_usd'] for r in projections))
