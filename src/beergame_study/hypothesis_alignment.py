"""Post-collection H1-H4 reporting; the frozen experiment remains unchanged."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .deadline_cohort import audit, progress, read

STUDY = 'deadline_cohort_2800524c9b2e0729'
ANALYSIS = 'daa53a7e838a'
HYPOTHESES = {
    'H1': 'Within an information-sharing environment, a binding decision-time constraint increases the underweighting of outstanding replenishment orders relative to adequate decision time.',
    'H2': 'Within an information-sharing environment, supply chains operating under binding decision-time constraints incur higher total inventory-holding and backlog costs than supply chains operating with adequate decision time.',
    'H3': 'Within an information-sharing environment and under a binding decision-time constraint, participants receiving causal education about the origins and propagation of order fluctuations underweight outstanding replenishment orders less than participants receiving standard game instructions and a matched control lecture.',
    'H4': 'Within an information-sharing environment and under a binding decision-time constraint, supply chains receiving causal education about the origins and propagation of order fluctuations incur lower total inventory-holding and backlog costs than supply chains receiving standard game instructions and a matched control lecture.',
}
FIGURES = [
    ('hypothesis_coverage', 'What the data can assess', 'H3 and H4 have no education/control observations. Missing effects are not plotted as zero.'),
    ('deadline_outcomes', 'Available H1 proxy and H2 cost outcomes', 'Lines join matched team/round outcomes. Diamonds show descriptive means; the stated deadlines were not enforced.'),
    ('deadline_vs_repeat', 'Deadline differences and same-deadline repeat variation', 'These are absolute differences, not signed effects or significance tests.'),
    ('cost_phases', 'Inventory-holding and backlog costs by phase', 'The 12 automatic continuation weeks are scoring-rule actions, not further model decisions.'),
    ('example_chain', 'First planned team: both scenarios and rounds', 'This team was selected by plan order, not by the size or direction of its results.'),
    ('bullwhip_by_role', 'Supplementary bullwhip description', 'Bullwhip is supplementary here. It does not test the new education hypotheses H3 or H4.'),
]


def source_folder(root):
    return Path(root) / 'reports/archive/studies' / STUDY / 'analysis' / ANALYSIS


def assess(chains):
    means = chains.groupby('condition')[['sensitivity', 'cost']].mean()
    records = []
    for h, statement in HYPOTHESES.items():
        metric = {'H1': 'sensitivity', 'H2': 'cost'}.get(h)
        brief = float(means.loc['brief', metric]) if metric else np.nan
        ample = float(means.loc['ample', metric]) if metric else np.nan
        records.append(dict(hypothesis=h, statement=statement,
            metric=metric or ('education_effect_on_underweighting' if h == 'H3' else 'education_effect_on_cost'),
            brief_mean=brief, ample_mean=ample, available_proxy_difference=brief-ample,
            assessment={'H1': 'Exploratory proxy in predicted direction; binding-time claim untested',
                        'H2': 'Exploratory costs opposite prediction; binding-time claim untested',
                        'H3': 'Not tested: education and matched-control lecture groups absent',
                        'H4': 'Not tested: education and matched-control lecture groups absent'}[h],
            missing_design='Enforced and verified binding decision time' if metric else 'Causal education, matched control lecture, and verified binding time',
            inference='Descriptive only; no human or independent-student inference'))
    return pd.DataFrame(records)


def make_alignment_figures(target, chains, contrasts, repeats):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.spines.top': False, 'axes.spines.right': False})

    def save(fig, name, title):
        fig.suptitle(title, fontsize=16, fontweight='bold')
        fig.text(.02, .015, 'Generated cohorts | Fictional deadlines, not enforced time | Descriptive evidence', fontsize=9, color='#536573')
        fig.tight_layout(rect=(0, .06, 1, .92))
        for ext in ('png', 'pdf'):
            fig.savefig(target / (name + '.' + ext), dpi=180, bbox_inches='tight')
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis('off')
    messages = [
        ('H1', 'Underweighting outstanding orders', 'Proxy points in predicted direction; binding time unverified', '#DCEAF7'),
        ('H2', 'Total holding and backlog cost', 'Observed average points opposite prediction; binding time unverified', '#F8E7DD'),
        ('H3', 'Education reduces underweighting', 'NOT TESTED: no education or matched-control lecture groups', '#E9ECEF'),
        ('H4', 'Education reduces total cost', 'NOT TESTED: no education or matched-control lecture groups', '#E9ECEF'),
    ]
    for i, (h, title, status, color) in enumerate(messages):
        y = .88 - i * .23
        ax.text(.02, y, h, fontsize=18, fontweight='bold', va='center')
        ax.text(.10, y+.035, title, fontsize=12, fontweight='bold', va='center')
        ax.text(.10, y-.055, status, fontsize=11, va='center', bbox=dict(boxstyle='round,pad=.45', fc=color, ec='none'))
    save(fig, 'hypothesis_coverage', 'H1-H4: evidence available in the completed sample')

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, metric, label in zip(axes, ['sensitivity', 'cost'], ['H1 proxy: pipeline sensitivity', 'H2: full scored team cost']):
        for _, rows in chains.groupby(['batch_id', 'generation', 'chain_id']):
            v = rows.set_index('condition').loc[['brief', 'ample'], metric]
            ax.plot([0, 1], v, color='#91A1AF', alpha=.2, lw=.7)
        for x, condition, color in [(0, 'brief', '#2265AD'), (1, 'ample', '#D57928')]:
            v = chains.loc[chains.condition == condition, metric]
            ax.scatter([x]*len(v), v, s=14, alpha=.35, color=color)
            ax.scatter(x, v.mean(), marker='D', color='black', s=85, zorder=4)
            ax.annotate(f'{v.mean():.4f}' if metric == 'sensitivity' else f'{v.mean():,.3f}', (x, v.mean()), xytext=(12, 5), textcoords='offset points', fontsize=10)
        ax.set(title=label, xticks=[0, 1], xticklabels=['10-second scenario', '180-second scenario'], ylabel='Sensitivity proxy' if metric == 'sensitivity' else 'Simulated team cost')
    save(fig, 'deadline_outcomes', 'Available deadline comparisons for H1 and H2')

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, metric, label in zip(axes, ['sensitivity', 'cost'], ['H1 proxy', 'H2 cost']):
        groups = [contrasts[metric+'_difference'].abs()]
        groups += [repeats.loc[repeats.condition == c, metric+'_difference'].abs() for c in ['brief', 'ample']]
        for x, values, color in zip(range(3), groups, ['#694F9C', '#2265AD', '#D57928']):
            ax.scatter(np.full(len(values), x)+np.linspace(-.07, .07, len(values)), values, alpha=.3, s=17, color=color)
            ax.scatter(x, values.mean(), color='black', s=70, marker='D')
        ax.set(title=label, xticks=[0, 1, 2], xticklabels=['Between\ndeadlines', 'Repeat\n10 seconds', 'Repeat\n180 seconds'], ylabel='Absolute difference')
    save(fig, 'deadline_vs_repeat', 'Deadline differences alongside ordinary generation variation')


def publish_current(root):
    root = Path(root)
    folder = root / 'reports/CURRENT_BEER_GAME'
    if not (folder / 'results/provenance.json').exists():
        return
    meta = read(folder / 'results/provenance.json')
    if meta.get('hypothesis_framework') != 'user-H1-H4-post-collection-v1':
        return
    pointer = dict(run=str(root / 'data/runs' / STUDY), report=str(folder / 'REPORT.md'),
                   collection='chat_ui', complete=True, hypothesis_framework=meta['hypothesis_framework'])
    (root / 'reports/LATEST_DEADLINE_COHORT_REPORT.json').write_text(json.dumps(pointer, indent=2), encoding='utf-8')


def build_report(run):
    """Serve the corrected publication without regenerating the old H3 labels."""
    run = Path(run).resolve()
    if run.name != STUDY:
        from .deadline_cohort_report import build_report as original
        return original(run)
    audit(run)
    root = run.parents[2]
    folder = root / 'reports/CURRENT_BEER_GAME'
    meta = read(folder / 'results/provenance.json')
    for name, digest in meta['raw_run_inputs_sha256'].items():
        if hashlib.sha256((run / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Published report no longer matches raw evidence.')
    for name, digest in meta['packaged_files_sha256'].items():
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Published output changed: ' + name)
    from .deadline_cohort import replay
    from .deadline_cohort_report import summarize
    rounds, probes, imports = replay(run)
    legacy_tables = summarize(rounds, probes)
    assessment = assess(legacy_tables['chains'])
    pd.testing.assert_frame_equal(assessment, pd.read_csv(folder / 'results/hypotheses.csv'), check_dtype=False, atol=1e-12)
    tables = legacy_tables | {'hypotheses': assessment}
    publish_current(root)
    return dict(report=folder/'REPORT.md', folder=folder, complete=bool(progress(run).accepted.all()),
                images=['plots/'+name for name, _, _ in FIGURES], tables=tables,
                legacy_tables=legacy_tables, rounds=rounds, probes=probes, imports=imports,
                workbook=folder/'results/RESULTS.xlsx')
