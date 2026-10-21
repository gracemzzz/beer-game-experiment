"""Conclusions-first, read-only analysis of experiment 13; no model calls."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform

import pandas as pd

from . import weekly_pressure as study
from .batched_pressure import digest, read, save_new


def table(rows, columns):
    def cell(value):
        if value is None:
            return '—'
        if isinstance(value, float):
            return f'{value:,.4f}'
        return str(value).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(columns) + ' |',
                      '| ' + ' | '.join('---' for _ in columns) + ' |']
                     + ['| ' + ' | '.join(cell(row.get(k)) for k in columns) + ' |' for row in rows])


def build_report(run):
    run = Path(run).resolve()
    experiment = run.parent.parent
    result = study.analyze(run)
    budget_experiment = study.budget_experiment_for(run)
    ledger = read(budget_experiment / 'data/api_budget.json')
    attempts = [dict(attempt_id=k, **v) for k, v in ledger['attempts'].items()]
    spent = sum(row['charge_usd'] for row in attempts)
    status = read(run / 'api_status.json') if (run / 'api_status.json').exists() else {}
    identity = dict(result=result, status=status, attempts=attempts,
                    renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    python=platform.python_version(), pandas=pd.__version__)
    report_id = digest(identity)[:12]
    analysis = experiment / 'analysis' / run.name / report_id
    publication = experiment / 'reports/history' / report_id
    analysis.mkdir(parents=True, exist_ok=True)
    publication.mkdir(parents=True, exist_ok=True)
    names = ('model_status', 'hypotheses', 'contrasts', 'chains', 'rounds', 'probes', 'task_status')
    tables = {key: pd.DataFrame(result[key]) for key in names}
    tables['api_attempts_shared_budget'] = pd.DataFrame(attempts)
    if result.get('condition_means'):
        tables['condition_means'] = pd.DataFrame(result['condition_means'])
    for name, frame in tables.items():
        save_new(analysis / (name + '.csv'), frame.to_csv(index=False))
    save_new(analysis / 'analysis.json', result)
    workbook = analysis / 'RESULTS.xlsx'
    if not workbook.exists():
        with pd.ExcelWriter(workbook, engine='openpyxl') as writer:
            for name, frame in tables.items():
                frame.to_excel(writer, sheet_name=name[:31], index=False)
    complete = sum(bool(r.get('complete')) for r in result['model_status'])
    weeks = sum(r.get('accepted_weeks', 0) for r in result['model_status'])
    pilots = sum(r.get('accepted_pilot_responses', 0) for r in result['model_status'])
    probes = sum(r.get('accepted_probe_responses', 0) for r in result['model_status'])
    available = [r for r in result['hypotheses'] if r.get('mean_strong_minus_no') is not None]
    findings = ('No complete hypothesis comparisons yet. Software checks are not model results.' if not available else
                '; '.join(f"{r['model']} {r['hypothesis']}: {r['mean_strong_minus_no']:+.4f}"
                          for r in available) + '. These are descriptive strong-minus-no-pressure differences.')
    conclusions = [
        f'1. **Completion:** {complete}/4 models complete; {weeks}/96 weekly batches, {pilots}/4 pilots and {probes}/4 probe batches accepted.',
        '2. **H1/H2:** ' + findings,
        '3. **Accounting:** Python calculates all inventory, deliveries, backlog and costs from accepted orders. Missing decisions remain missing.',
        '4. **Meaning:** Imagined pressure framing, not an enforced deadline. H1 is a matched-state sensitivity proxy, not structural β. Batched fictional chains are dependent; no p-values are reported.',
        f'5. **Shared budget:** ${spent:.6f} charged/reserved across experiments 12 and 13; ${max(0, ledger["cap_usd"] - spent):.6f} remains within the original $5 cap.',
    ]
    link = lambda path: os.path.relpath(path, publication).replace(os.sep, '/')
    lines = ['# Experiment 13: conclusions first', '', *conclusions, '',
             '## Completion by model', '', table(result['model_status'], [
                 'model', 'accepted_pilot_responses', 'accepted_weeks', 'accepted_probe_responses', 'complete']), '',
             'A complete model has an accepted full-size format pilot, all 24 weekly batches and its probe batch. '
             'Pilot choices are excluded from the main outcomes. Partial games are exported for diagnosis but cannot supply 24-week H2 costs.', '',
             '## Hypotheses', '', table(result['hypotheses'], [
                 'model', 'hypothesis', 'paired_blocks', 'mean_strong_minus_no', 'descriptive_direction']), '',
             '**H1 proxy:** For otherwise matched states, (order with 8 outstanding cases − order with 32 outstanding cases) / 24. '
             'Average over roles and backlog states, then compare matched pressure conditions. A negative difference follows the predicted proxy direction. '
             'This does not identify an optimal weight or establish literal underweighting.', '',
             '**H2:** Sum of $0.50 × end-of-week inventory + $1.00 × backlog over four roles and exactly 24 weeks. '
             'A positive difference follows the prediction. There is no revenue or production fee. Terminal inventory, backlog and outstanding orders are reported; '
             'unplayed future weeks carry no invented costs.', '',
             'A null or opposite comparison is a valid result. The protocol does not change prompts, sample size, prices or ordering rules to obtain significance.', '',
             '## Means by condition', '', table(result.get('condition_means', []), [
                 'model', 'condition', 'chains', 'weeks_observed', 'sensitivity', 'total_cost', 'observed_cost_partial']), '',
             '## Chain performance', '', table(result['chains'], [
                 'model', 'block', 'condition', 'weeks_observed', 'complete', 'holding_cost', 'backlog_cost',
                 'total_cost', 'observed_cost_partial', 'sensitivity', 'zero_orders', 'max_order',
                 'final_inventory', 'final_backlog', 'final_supply_line', 'bullwhip']), '',
             'For an incomplete game, only observed partial costs are available. Do not compare them with full 24-week totals. '
             'Bullwhip tables use variance of a role’s weekly orders divided by variance of customer demand over the same observed weeks; '
             'a ratio above 1 indicates amplification. A zero denominator is undefined, not zero.', '',
             '## Execution and model provenance', '', table(result['task_status'], [
                 'task_id', 'model', 'phase', 'week', 'status', 'reason']), '',
             'Requested model IDs are fixed in the plan. Provider-returned IDs and token usage are retained in the request records. '
             'OpenAI uses reasoning effort none; Claude uses disabled thinking and low effort. '
             'Weekly/pilot output allowances are 2,048 tokens; probe allowance is 4,096. Both conditions use the same generation settings. '
             'No temperature override is sent. These settings affect the simulation and limit comparison with previous higher-effort collections.', '',
             'Only a transient transport, rate-limit or server failure can receive one further budgeted attempt. Invalid choices, refusals and incomplete outputs remain failures. '
             'A failed model blocks its remaining dependent tasks; other models can continue. Reopening the notebook reuses verified accepted responses. '
             'Unknown charges retain their reservation. Local accounting is a conservative estimate, not a provider invoice or account balance.', '',
             '## Design and limits', '',
             'Per model: 20 four-role chains, 10 matched pairs, 24 weeks. Python reveals current state and a short past history, '
             'then commits all submitted orders simultaneously. It does not reveal future demand to the model. '
             'The researcher scores 24 weeks, but the eventual stopping week is deliberately not revealed in the API prompts. '
             'All chain choices in a week are generated jointly; the model can see the whole batch. Prompted identity separation is not technical information isolation. '
             'No individual-agent or human replication is claimed.', '',
             *['- ' + str(item) for item in result['limitations']], '',
             '## Files', '',
             f'- [Excel workbook]({link(workbook)})',
             f'- [Weekly states and orders]({link(analysis / "rounds.csv")})',
             f'- [Chain performance]({link(analysis / "chains.csv")})',
             f'- [Probe choices]({link(analysis / "probes.csv")})',
             f'- [Matched comparisons]({link(analysis / "contrasts.csv")})',
             f'- [Frozen plan and execution evidence]({link(run)})',
             f'- [Exact prompt archive]({link(experiment / "prompts" / run.name)})',
             f'- [Raw API records]({link(experiment / "raw" / run.name)})',
             f'- [Original shared budget ledger]({link(budget_experiment / "data/api_budget.json")})',
             f'- [Prospective protocol]({link(experiment / "hypotheses/PROTOCOL.md")})', '',
             'API settings checked 21 October 2026: '
             '[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), '
             '[GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna), '
             '[GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol), '
             '[Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5).', '']
    report = publication / 'REPORT.md'
    save_new(report, '\n'.join(lines))
    landing = experiment / 'reports/REPORT.md'
    landing.write_text('# Experiment 13: latest findings\n\n' + '\n'.join(conclusions)
                       + f'\n\n[Full report and detailed data](history/{report_id}/REPORT.md).\n', encoding='utf-8')
    (experiment / 'reports/LATEST.json').write_text(json.dumps(dict(
        study=run.name, report=report.relative_to(experiment).as_posix(),
        analysis=analysis.relative_to(experiment).as_posix(), complete_models=complete,
        accepted_weeks=weeks, charged_or_reserved_usd=spent), indent=2) + '\n', encoding='utf-8')
    return dict(report=report, analysis=analysis, workbook=workbook, summary=result,
                charged_or_reserved_usd=spent)
