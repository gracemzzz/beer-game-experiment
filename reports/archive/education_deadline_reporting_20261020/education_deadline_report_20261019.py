"""Immutable, descriptive publications for the separate education/deadline study.

This reporting layer performs no generation and no inferential hypothesis tests.
It deliberately keeps cohort-response replication distinct from fictional rows.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from io import BytesIO
import itertools
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .education_deadline_cohort import (
    ARMS, CONTRASTS, audit, digest, progress, read, save_new, summarize,
)


LABELS = {
    'a60_control': 'A: 60 seconds / control',
    'b10_control': 'B: 10 seconds / control',
    'c10_education': 'C: 10 seconds / education',
}
COLORS = {'a60_control': '#3575A5', 'b10_control': '#D58B33', 'c10_education': '#6A8E59'}
FIXED_DATE = datetime(2026, 10, 19, tzinfo=timezone.utc)


def _markdown(frame):
    if frame.empty:
        return '_No eligible saved observations._\n'

    def show(value):
        if pd.isna(value):
            return 'absent / undefined'
        if isinstance(value, (float, np.floating)):
            return f'{value:.6g}' if np.isfinite(value) else 'undefined'
        return str(value).replace('|', '/').replace('\n', ' ')

    return ('| '+' | '.join(map(str, frame.columns))+' |\n| '+
            ' | '.join(['---']*len(frame.columns))+' |\n'+
            ''.join('| '+' | '.join(show(value) for value in row)+' |\n'
                    for row in frame.itertuples(index=False, name=None)))


def _direction(value, sign, observations):
    if not observations or not np.isfinite(value):
        return 'absent / undefined'
    if value == 0:
        return 'zero observed difference'
    return 'predicted direction' if value*sign > 0 else 'opposite direction'


def _hypotheses(contrasts, repetitions):
    records = []
    for hypothesis, (reference, treatment, metric, sign) in CONTRASTS.items():
        own = contrasts[contrasts.hypothesis == hypothesis]
        for repetition in [*range(1, repetitions+1), 'overall']:
            selected = own if repetition == 'overall' else own[own.repetition == repetition]
            values = selected.estimate.dropna()
            mean = float(values.mean()) if len(values) else np.nan
            records.append(dict(
                hypothesis=hypothesis, repetition=repetition, metric=metric,
                reference_arm=reference, treatment_arm=treatment,
                mean_difference=mean,
                median_difference=float(values.median()) if len(values) else np.nan,
                mean_absolute_difference=float(values.abs().mean()) if len(values) else np.nan,
                minimum_difference=float(values.min()) if len(values) else np.nan,
                maximum_difference=float(values.max()) if len(values) else np.nan,
                matched_chain_generation_pairs=len(values),
                distinct_generation_pairs=int(selected.repetition.nunique()) if len(values) else 0,
                expected_sign=sign, direction=_direction(mean, sign, len(values))))
    return pd.DataFrame(records)


def _outcomes(chains, repetitions):
    records = []
    metrics = ['sensitivity', 'total_cost', 'cost_practice', 'cost_model', 'cost_automatic',
               'automatic_cost_fraction']
    for arm in ARMS:
        own = chains[chains.arm == arm]
        for repetition in [*range(1, repetitions+1), 'overall']:
            frame = own if repetition == 'overall' else own[own.repetition == repetition]
            records.append(dict(arm=arm, repetition=repetition, chain_generation_rows=len(frame),
                                accepted_generations=int(frame.repetition.nunique()),
                                **{metric: float(frame[metric].mean()) if len(frame) else np.nan
                                   for metric in metrics}))
    return pd.DataFrame(records)


def _choice_changes(rounds):
    columns = ['comparison', 'arm_or_contrast', 'repetition_a', 'repetition_b',
               'matched_weekly_choices', 'changed_choices', 'changed_fraction',
               'mean_absolute_change', 'mean_signed_change']
    if rounds.empty:
        return pd.DataFrame(columns=columns)
    model = rounds[rounds.phase == 'model']
    records = []

    def compare(left, right, kind, label, repetition_a, repetition_b):
        paired = left.merge(right, on=['chain_id', 'role', 'week'],
                            suffixes=('_reference', '_treatment'), validate='one_to_one')
        if paired.empty:
            return
        delta = paired.order_treatment-paired.order_reference
        records.append(dict(comparison=kind, arm_or_contrast=label,
                            repetition_a=repetition_a, repetition_b=repetition_b,
                            matched_weekly_choices=len(delta), changed_choices=int((delta != 0).sum()),
                            changed_fraction=float((delta != 0).mean()),
                            mean_absolute_change=float(delta.abs().mean()),
                            mean_signed_change=float(delta.mean())))

    keys = ['chain_id', 'role', 'week', 'order']
    for repetition, frame in model.groupby('repetition', sort=True):
        for label, reference, treatment in [('H1/H2: B minus A', 'a60_control', 'b10_control'),
                                            ('H3/H4: C minus B', 'b10_control', 'c10_education')]:
            compare(frame.loc[frame.arm == reference, keys], frame.loc[frame.arm == treatment, keys],
                    'between_arms', label, int(repetition), int(repetition))
    for arm, frame in model.groupby('arm', sort=True):
        for first, second in itertools.combinations(sorted(frame.repetition.unique()), 2):
            compare(frame.loc[frame.repetition == first, keys], frame.loc[frame.repetition == second, keys],
                    'same_arm_repeat', arm, int(first), int(second))
    return pd.DataFrame(records, columns=columns)


def _repeat_outcomes(chains):
    columns = ['arm', 'repetition_a', 'repetition_b', 'chain_id', 'metric', 'difference']
    records = []
    for arm, frame in chains.groupby('arm', sort=True):
        for first, second in itertools.combinations(sorted(frame.repetition.unique()), 2):
            metrics = ['sensitivity', 'total_cost', 'cost_model', 'cost_automatic']
            left = frame.loc[frame.repetition == first, ['chain_id']+metrics]
            right = frame.loc[frame.repetition == second, ['chain_id']+metrics]
            pairs = left.merge(right, on='chain_id', suffixes=('_a', '_b'), validate='one_to_one')
            for row in pairs.to_dict('records'):
                for metric in metrics:
                    records.append(dict(arm=arm, repetition_a=int(first), repetition_b=int(second),
                                        chain_id=row['chain_id'], metric=metric,
                                        difference=row[metric+'_b']-row[metric+'_a']))
    return pd.DataFrame(records, columns=columns)


def _cost_contrasts(chains, repetitions):
    columns = ['hypothesis', 'repetition', 'matched_chain_generation_pairs',
               'cost_practice_difference', 'cost_model_difference',
               'cost_automatic_difference', 'total_cost_difference',
               'automatic_difference_over_total_difference']
    records = []
    costs = ['cost_practice', 'cost_model', 'cost_automatic', 'total_cost']
    for hypothesis in ('H2', 'H4'):
        reference, treatment, _, _ = CONTRASTS[hypothesis]
        left = chains.loc[chains.arm == reference, ['repetition', 'chain_id']+costs]
        right = chains.loc[chains.arm == treatment, ['repetition', 'chain_id']+costs]
        pairs = left.merge(right, on=['repetition', 'chain_id'], suffixes=('_a', '_b'), validate='one_to_one')
        for repetition in [*range(1, repetitions+1), 'overall']:
            frame = pairs if repetition == 'overall' else pairs[pairs.repetition == repetition]
            values = {cost+'_difference': float((frame[cost+'_b']-frame[cost+'_a']).mean())
                      if len(frame) else np.nan for cost in costs}
            total = values['total_cost_difference']
            ratio = values['cost_automatic_difference']/total if np.isfinite(total) and total != 0 else np.nan
            records.append(dict(hypothesis=hypothesis, repetition=repetition,
                                matched_chain_generation_pairs=len(frame),
                                **values, automatic_difference_over_total_difference=ratio))
    return pd.DataFrame(records, columns=columns)


def _excel(tables):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for name, frame in tables.items():
            # Excel has a fixed row limit; CSV exports always retain every row.
            if len(frame) < 1048576:
                frame.to_excel(writer, sheet_name=name[:31], index=False)
            else:
                pd.DataFrame([{'notice': 'Complete table exceeds Excel row limit; use '+name+'.csv',
                               'rows': len(frame)}]).to_excel(writer, sheet_name=name[:31], index=False)
        writer.book.properties.created = FIXED_DATE.replace(tzinfo=None)
        writer.book.properties.modified = FIXED_DATE.replace(tzinfo=None)
    # Normalize container timestamps and properties for byte-identical rebuilds.
    result = BytesIO()
    with ZipFile(BytesIO(buffer.getvalue()), 'r') as source, ZipFile(result, 'w', compression=ZIP_DEFLATED) as target:
        for name in sorted(source.namelist()):
            data = source.read(name)
            if name == 'docProps/core.xml':
                import re
                data = re.sub(rb'(<dcterms:modified[^>]*>).*?(</dcterms:modified>)',
                              rb'\g<1>2026-10-19T00:00:00Z\g<2>', data)
            info = ZipInfo(name, date_time=(2026, 10, 19, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            target.writestr(info, data)
    return result.getvalue()


def _figures(chains, contrasts, repeat_outcomes, label):
    if chains.empty:
        return {}
    files = {}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False,
                         'axes.spines.right': False, 'font.size': 9})

    def save(figure, name, title):
        figure.suptitle(label+'\n'+title, fontsize=12, fontweight='bold')
        figure.text(.02, .015, 'Fictional cohorts | Deadline framing only | Spread is descriptive, not sampling uncertainty',
                    fontsize=8, color='#536573')
        figure.tight_layout(rect=(0, .06, 1, .90))
        for extension in ('png', 'pdf'):
            buffer = BytesIO()
            metadata = ({'Software': 'beergame_study education_deadline_report'} if extension == 'png' else
                        {'Creator': 'beergame_study education_deadline_report',
                         'CreationDate': FIXED_DATE, 'ModDate': FIXED_DATE})
            figure.savefig(buffer, format=extension, dpi=160, bbox_inches='tight', metadata=metadata)
            files['plots/'+name+'.'+extension] = buffer.getvalue()
        plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for axis, metric, title in zip(axes, ('sensitivity', 'total_cost'),
                                   ('Matched-state pipeline sensitivity proxy', 'Total holding and backlog cost')):
        for position, arm in enumerate(ARMS):
            own = chains[chains.arm == arm]
            values = own[metric].dropna()
            if len(values):
                axis.scatter(position+np.linspace(-.08, .08, len(values)), values,
                             s=14, alpha=.30, color=COLORS[arm])
                for repetition, rows in own.groupby('repetition', sort=True):
                    offset = (int(repetition)-1)*.035
                    axis.scatter(position+offset, rows[metric].mean(), s=65,
                                 marker='D', edgecolors='white', color=COLORS[arm], zorder=5)
            else:
                axis.text(position, .5, 'Absent', transform=axis.get_xaxis_transform(), ha='center')
        axis.set(title=title, xticks=range(3), xticklabels=['A: 60s\ncontrol', 'B: 10s\ncontrol', 'C: 10s\neducation'])
        axis.set_ylabel('Sensitivity; diamonds = generation means' if metric == 'sensitivity' else 'Cost per chain; diamonds = generation means')
        axis.grid(axis='y', alpha=.15)
    save(figure, 'outcome_levels', 'Observed levels by case; missing cases remain absent')

    figure, axis = plt.subplots(figsize=(10, 4.8))
    phase_labels = [('cost_practice', 'Practice', '#A5B3BF'), ('cost_model', 'Model decisions', '#387BA8'),
                    ('cost_automatic', 'Automatic continuation', '#D58B33')]
    for position, arm in enumerate(ARMS):
        own = chains[chains.arm == arm]
        if own.empty:
            axis.text(position, .5, 'Absent', transform=axis.get_xaxis_transform(), ha='center')
            continue
        bottom = 0
        for column, phase, color in phase_labels:
            value = float(own[column].mean())
            axis.bar(position, value, bottom=bottom, color=color)
            bottom += value
    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for _, _, color in phase_labels]
    axis.legend(handles, [phase for _, phase, _ in phase_labels], fontsize=9)
    axis.set(xticks=range(3), xticklabels=['A: 60s / control', 'B: 10s / control', 'C: 10s / education'],
             ylabel='Mean reconstructed cost per chain')
    save(figure, 'cost_phases', 'Practice, submitted decisions, and automatic continuation')

    if not contrasts.empty or not repeat_outcomes.empty:
        figure, axes = plt.subplots(1, 2, figsize=(12, 4.8))
        for axis, metric in zip(axes, ('sensitivity', 'total_cost')):
            groups = []
            for hypothesis in (('H1', 'H3') if metric == 'sensitivity' else ('H2', 'H4')):
                values = contrasts.loc[contrasts.hypothesis == hypothesis, 'estimate'].abs().dropna()
                if len(values):
                    groups.append((hypothesis+'\ncross-case', values, '#755B93'))
            for arm in ARMS:
                values = repeat_outcomes.loc[(repeat_outcomes.arm == arm) &
                                             (repeat_outcomes.metric == metric), 'difference'].abs().dropna()
                if len(values):
                    groups.append((arm[0].upper()+'\nrepeat', values, COLORS[arm]))
            for position, (_, values, color) in enumerate(groups):
                axis.scatter(position+np.linspace(-.08, .08, len(values)), values, s=15, alpha=.3, color=color)
                axis.scatter(position, values.mean(), marker='D', color='black', s=45)
            axis.set(title=metric, xticks=range(len(groups)), xticklabels=[group[0] for group in groups],
                     ylabel='Absolute matched-chain difference; diamond = mean')
            if not groups:
                axis.text(.5, .5, 'No eligible pairs', transform=axis.transAxes, ha='center')
        save(figure, 'contrasts_and_repeats', 'Cross-case differences alongside variation between same-case repeats')
    return files


def build_report(run, output):
    """Publish one immutable report directory; reject any differing overwrite.

    Caller chooses a new/versioned output when new evidence is added. Rebuilding
    the identical evidence and implementation produces byte-identical artifacts.
    """
    run, output = Path(run), Path(output)
    manifest = audit(run)
    plan = read(run/'plan.json')
    config = manifest['config']
    status = progress(run)
    tables = summarize(run)
    repetitions = config['repetitions']
    for name, columns in {
        'rounds': ['task_id', 'repetition', 'arm', 'chain_id', 'role', 'week', 'phase', 'order', 'cost'],
        'probes': ['task_id', 'repetition', 'arm', 'chain_id', 'role', 'low_order', 'high_order', 'sensitivity'],
        'imports': ['task_id', 'raw_path', 'raw_sha256', 'prompt_sha256', 'model_label', 'effort_label',
                    'session_label', 'evidence_kind', 'received_utc', 'api_calls'],
    }.items():
        if tables[name].empty and not len(tables[name].columns):
            tables[name] = pd.DataFrame(columns=columns)
    tables['hypothesis_summary'] = _hypotheses(tables['contrasts'], repetitions)
    tables['outcome_summary'] = _outcomes(tables['chains'], repetitions)
    tables['choice_changes'] = _choice_changes(tables['rounds'])
    tables['repeat_outcomes'] = _repeat_outcomes(tables['chains'])
    tables['cost_contrasts'] = _cost_contrasts(tables['chains'], repetitions)
    tables['progress'] = status
    evidence = {path.relative_to(run).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(run.rglob('*')) if path.is_file() and 'inbox' not in path.relative_to(run).parts}
    signature = digest(evidence)[:16]
    accepted = int(status.accepted.sum())
    complete = bool(status.accepted.all())
    if config['synthetic']:
        label = 'SYNTHETIC SOFTWARE CHECK — NOT MODEL RESULTS'
    elif config['collection'] == 'isolated_assistant':
        label = 'FICTIONAL COHORTS — ISOLATED ASSISTANT PREFLIGHT'
    else:
        label = 'FICTIONAL COHORTS — WEBSITE COLLECTION'
    files = _figures(tables['chains'], tables['contrasts'], tables['repeat_outcomes'], label)
    for name, frame in tables.items():
        files['results/'+name+'.csv'] = frame.to_csv(index=False, lineterminator='\n').encode('utf-8')
    files['results/RESULTS.xlsx'] = _excel(tables)
    matched = tables['hypothesis_summary']
    summary_columns = ['hypothesis', 'repetition', 'mean_difference', 'matched_chain_generation_pairs', 'direction']
    evidence_kind = ('Synthetic software fixtures; no model decisions or human observations.' if config['synthetic'] else
                     'Model-generated fictional identities; zero observed human participants.')
    backend = ('The isolated assistant uses its inherited model and reasoning setting. It is not verified to match '
               'the website GPT-6 / Pro backend.' if config['collection'] == 'isolated_assistant' else
               'Website model/settings are operator reports, not independent verification of provider identity or compute.')
    parts = [
        '# Education and 10s/60s deadline-framing study\n\n',
        '**'+label+'**\n\n',
        f"Status: **{'complete' if complete else 'partial / awaiting responses'}**; **{accepted}/{len(status)}** planned responses accepted. {evidence_kind}\n\n",
        f"The fixed plan contains **{plan['fictional_identities']} fictional identities** in **{len(plan['chains'])} four-role chains**, "
        f"three cases and **{repetitions} repeated generation(s) per case**. Repeats and cases reuse identities, profiles and demand paths. "
        f"Accepted responses contain **{len(tables['roles'])} role trajectories** and "
        f"**{int((tables['rounds'].phase == 'model').sum()) if not tables['rounds'].empty else 0} submitted weekly orders**. "
        'These counts are not independent students.\n\n',
        f"Recorded model: **{config['model_label']} / {config['effort_label']}**; collection: **{config['collection']}**. {backend}\n\n",
        '## Cases and measurement\n\n',
        '| Case | Fictional decision allowance | Reading |\n| --- | --- | --- |\n'
        '| A | 60 seconds | Standard rules plus matched control text |\n'
        '| B | 10 seconds | Standard rules plus matched control text |\n'
        '| C | 10 seconds | Standard rules plus causal education text |\n\n',
        'No actual per-decision elapsed time or compute budget is imposed or measured. Neither bindingness of 10 seconds '
        'nor adequacy of 60 seconds is established. A textual reading is not a verified 20-minute lecture or measured learning. '
        'All cases keep the information-sharing rules fixed; whole-cohort generation nevertheless exposes the generator to '
        'future demand and all roles. Decentralized information use and human persona fidelity are unverified.\n\n',
        'Pipeline sensitivity is `(order with 8 dispatched cases − order with 32 dispatched cases) / 24`, averaged across four roles. '
        'It is a matched-state proxy, not an identified structural underweighting coefficient. Lower sensitivity alone can also '
        'reflect ordering boundaries or policy differences. Costs reconstruct holding and backlog charges over four practice weeks, '
        'submitted model decisions, and twelve automatic continuation weeks. Continuation repeats each role’s last submitted order '
        'and final customer demand; those automatic actions are not model decisions.\n\n',
        '## Descriptive H1–H4 contrasts\n\n',
        'H1: B minus A sensitivity, predicted negative. H2: B minus A total cost, predicted positive. '
        'H3: C minus B sensitivity, predicted positive. H4: C minus B total cost, predicted negative.\n\n',
        _markdown(matched[summary_columns]),
        '\nOnly actual matched chain/repetition pairs enter these contrasts. Absent cases stay absent, and no missing choices are imputed. '
        'The overall mean pools eligible chain-generation pairs. A direction label describes these saved outputs and does not confirm '
        'the stated human-time hypothesis. No result direction or significance is an acceptance criterion.\n\n',
        'Two repetitions provide two response-level generation units per case, regardless of the number of fictional chains. '
        'With two paired independent replication contrasts, an exact sign-flip test has only four assignments and a minimum '
        'one-sided p-value of .25. No inferential p-values, confidence intervals, or statistical-significance claims are computed here. '
        'More jointly generated student rows do not repair this replication limit.\n\n' if repetitions == 2 else
        'Chains within one generated response are dependent; identities and demand paths repeat across cases. '
        'No inferential p-values, confidence intervals, or statistical-significance claims are computed here.\n\n',
        '## Same-case variation and changed weekly choices\n\n',
        _markdown(tables['choice_changes']),
        '\nRepeat differences are shown alongside cross-case differences. Changed orders alone do not establish a deadline mechanism. '
        'Chain distributions and their ranges describe these generated outputs, not sampling uncertainty for human students.\n\n',
        '## Cost phases\n\n',
        _markdown(tables['cost_contrasts']),
        '\nThe automatic-to-total contrast ratio is signed and undefined when the total contrast is zero; '
        'it can exceed one when phases oppose each other. The CSV and workbook retain each chain and each phase.\n\n',
        '## Completion and provenance\n\n',
        _markdown(status[['task_id', 'repetition', 'arm', 'students', 'accepted']]),
        '\nAll accepted responses, exact original bytes, attempt receipts, frozen prompts, profile assignments, demand paths and '
        'scientific source hashes remain in the source run. Rejected attempts are retained. No accepted result is replaced, '
        'no choice is clipped, no missing decision is filled, and no format conversion is performed.\n\n',
        f"Source run: `{run.resolve()}`. Evidence signature: `{signature}`. This report makes **zero API calls**.\n\n",
        '[Excel workbook](results/RESULTS.xlsx). Individual tables are available as CSV in `results/`. '
        'The `hypothesis_summary` table includes medians, ranges and absolute differences; '
        '`repeat_outcomes` preserves each matched same-case chain difference.\n\n',
    ]
    if not accepted:
        parts.append('**Prepared only: no model output has been collected for this run, so no experimental result is available.**\n\n')
    elif tables['contrasts'].empty:
        parts.append('**No requested case contrast is available. A single-case capacity/format check supplies no H1–H4 conclusion.**\n\n')
    for relative in sorted(name for name in files if name.endswith('.png')):
        parts.append(f'![{Path(relative).stem.replace("_", " ")}]({relative})\n\n')
    files['REPORT.md'] = ''.join(parts).encode('utf-8')
    provenance = dict(study_id=manifest['study_id'], source_run=str(run.resolve()),
                      analysis_signature=signature, accepted_responses=accepted, expected_responses=len(status),
                      complete=complete, human_observations=0, api_calls=0,
                      report_implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      inputs_sha256=evidence,
                      outputs_sha256={name: hashlib.sha256(data).hexdigest() for name, data in files.items()})
    files['provenance.json'] = json.dumps(provenance, ensure_ascii=False, indent=2, allow_nan=False).encode('utf-8')
    # Check every target before publishing any file, avoiding a partial replacement.
    for relative, data in files.items():
        target = output/relative
        if target.exists() and target.read_bytes() != data:
            raise ValueError('Refusing to overwrite a differing publication; choose a new output directory: '+str(target))
    for relative, data in files.items():
        save_new(output/relative, data)
    return dict(folder=output, report=output/'REPORT.md', tables=tables, complete=complete,
                images=sorted(Path(name).stem for name in files if name.endswith('.png')),
                analysis_signature=signature, accepted_responses=accepted)
