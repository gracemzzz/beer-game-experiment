"""Freeze readable presentation figures from the first completed agent contexts.

Offline descriptive export only; no model calls, inferred missing values, or tests
on dependent chains. Existing exports are never overwritten with new evidence.
"""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'experiments/13_weekly_state_api_20261021/reports/agent_collection_v5'
OUT = SOURCE / 'slides_first_context'
MODELS = ('gpt_astra', 'gpt_sol')
LABELS = {'gpt_astra': 'GPT-6 Astra', 'gpt_sol': 'GPT-6.1 Sol'}
COLORS = {'A': '#51789A', 'B': '#D5813D', 'C': '#348C7A'}
INK = '#173044'
GREY = '#61717F'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    raw = pd.read_csv(SOURCE / 'context_arm_results.csv')
    prefixes = pd.read_csv(SOURCE / 'within_context_chain_prefixes.csv')
    evidence = json.loads((SOURCE / 'RESULTS.json').read_text(encoding='utf-8'))
    # This is an explicitly named first-context snapshot, not a best-run filter.
    selected = raw[raw['model'].isin(MODELS) & (raw['run'] == 'run001')].copy()
    if len(selected) != 6 or set(selected.arm) != {'A', 'B', 'C'}:
        raise ValueError('Both first contexts must contain all three complete conditions')
    identities = {(r['model'], r['run']): r for r in evidence['evidence']}
    for model in MODELS:
        if identities[(model, 'run001')]['review'].startswith('Excluded:'):
            raise ValueError('Do not plot an excluded context as a provisional result')
    # Match prefixes to the same raw contexts, never pool separate runs.
    selected_prefixes = prefixes[prefixes.batch_id.isin(selected.block_id)].copy()
    assert len(selected_prefixes) == 36
    for _, row in selected.iterrows():
        p = selected_prefixes[(selected_prefixes.batch_id == row.block_id) &
                              (selected_prefixes.arm == row.arm) &
                              (selected_prefixes.chains_per_condition == 50)].iloc[0]
        for metric in ('chain_total_cost', 'mean_role_order_variance',
                       'mean_role_bullwhip', 'pipeline_sensitivity'):
            assert np.isclose(row[metric], p[metric], rtol=1e-12, atol=1e-12)
    source_hashes = {f: digest(SOURCE / f) for f in (
        'context_arm_results.csv', 'within_context_chain_prefixes.csv', 'RESULTS.json')}
    fingerprint = dict(source_hashes=source_hashes, generator_sha256=digest(__file__))
    if (OUT / 'MANIFEST.json').exists():
        old = json.loads((OUT / 'MANIFEST.json').read_text(encoding='utf-8'))
        if old['fingerprint'] == fingerprint:
            print(f'Existing frozen slide snapshot: {OUT}')
            return
        raise FileExistsError('This first-context snapshot is frozen; use a new export for later evidence')
    OUT.mkdir(parents=True, exist_ok=True)
    selected.to_csv(OUT / 'plotted_condition_values.csv', index=False)
    selected_prefixes.to_csv(OUT / 'plotted_chain_prefixes.csv', index=False)
    (OUT / 'SOURCE_RESULTS.json').write_bytes((SOURCE / 'RESULTS.json').read_bytes())
    frames = {m: selected[selected.model == m].set_index('arm') for m in MODELS}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 14,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.edgecolor': '#B5C0C8', 'axes.labelcolor': INK,
        'text.color': INK, 'xtick.color': GREY, 'ytick.color': GREY,
        'svg.fonttype': 'none', 'pdf.fonttype': 42})
    pending = any(not identities[(m, 'run001')]['eligible'] for m in MODELS)
    review_note = 'Transcript review pending' if pending else 'One reviewed context per model'
    footer = ('First context per model | 50 dependent chains/condition | 24 weeks | requested high effort\n'
              f'{review_note}. Descriptive simulation; no significance claim or measured clock deadline.')
    status = ('Luna: 2 completed attempts excluded for procedural deviations.  Claude: not collected.')
    figures = []

    def base(title, subtitle, ncols):
        fig, axes = plt.subplots(1, ncols, figsize=(16, 9), squeeze=False)
        fig.subplots_adjust(left=.065, right=.97, bottom=.29, top=.69, wspace=.36)
        fig.text(.045, .925, title, fontsize=28, weight='bold')
        fig.text(.045, .868, subtitle, fontsize=16, color=GREY)
        fig.text(.045, .105, footer, fontsize=12, color=GREY, linespacing=1.6)
        fig.text(.045, .045, status, fontsize=11, color=GREY)
        return fig, list(axes[0])

    fig, axes = base('Costs and order fluctuations: first observed runs',
        'H2 and H4 show the predicted direction in Astra and Sol; replication is still underway.', 3)
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[a]) for a in 'ABC']
    fig.legend(handles, ['A  Control + revision', 'B  Control + one decision',
                        'C  Causal education + one decision'],
               loc='upper left', bbox_to_anchor=(.04, .82), ncol=3, frameon=False, fontsize=13)
    for ax, metric, title, unit in zip(axes,
        ('chain_total_cost', 'mean_role_order_variance', 'mean_role_bullwhip'),
        ('H2  Total cost', 'H4a  Order variation', 'H4b  Bullwhip ratio'),
        ('Game cost units / chain', 'Weekly order variance (units²)', 'Order variance / demand variance')):
        x = np.arange(2)
        for k, a in enumerate('ABC'):
            vals = [frames[m].loc[a, metric] for m in MODELS]
            bars = ax.bar(x + (k - 1)*.24, vals, width=.22, color=COLORS[a])
            ax.bar_label(bars, labels=[f'{v:.1f}' if metric != 'mean_role_bullwhip' else f'{v:.2f}' for v in vals],
                         padding=5, fontsize=11)
        ax.set_xticks(x, [LABELS[m] for m in MODELS], fontsize=12)
        ax.set_title(title, fontsize=18, weight='bold', pad=18)
        ax.set_ylabel(unit, fontsize=12)
        ax.set_ylim(0, ax.get_ylim()[1]*1.20)
        ax.yaxis.grid(True, alpha=.14)
        ax.set_axisbelow(True)
        plus, minus = ('B', 'A') if metric == 'chain_total_cost' else ('C', 'B')
        changes = [100*(frames[m].loc[plus, metric]/frames[m].loc[minus, metric]-1) for m in MODELS]
        ax.text(.5, -.23, f'{plus} vs {minus}:  Astra {changes[0]:+.1f}%  |  Sol {changes[1]:+.1f}%',
                transform=ax.transAxes, ha='center', fontsize=12, weight='bold')
    figures.append(('01_costs_and_fluctuations', fig))

    fig, axes = base('Outstanding orders: H1 and H3 patterns not observed',
        'H1 and H3 use pipeline-response sensitivity as a proxy; neither is established.', 2)
    fig.legend(handles, ['A  Control + revision', 'B  Control + one decision',
                        'C  Causal education + one decision'],
               loc='upper left', bbox_to_anchor=(.04, .82), ncol=3, frameon=False, fontsize=13)
    for ax, m in zip(axes, MODELS):
        f = frames[m]
        vals = [f.loc[a, 'pipeline_sensitivity'] for a in 'ABC']
        bars = ax.bar(np.arange(3), vals, color=[COLORS[a] for a in 'ABC'], width=.58)
        ax.bar_label(bars, labels=[f'{v:.3f}' for v in vals], padding=7, fontsize=16)
        ax.set_xticks(np.arange(3), ['A', 'B', 'C'])
        ax.set_ylim(0, 1.19)
        ax.set_yticks([0, .25, .5, .75, 1])
        ax.set_ylabel('Pipeline-response sensitivity', fontsize=13)
        ax.set_title(LABELS[m], fontsize=19, weight='bold', pad=18)
        ax.yaxis.grid(True, alpha=.14)
        ax.set_axisbelow(True)
        ax.text(.5, -.23, f'H1: B−A = {vals[1]-vals[0]:+.4f} (predicted < 0)\n'
                f'H3: C−B = {vals[2]-vals[1]:+.4f} (predicted > 0)',
                transform=ax.transAxes, ha='center', fontsize=14, linespacing=1.6)
    figures.append(('02_outstanding_order_response', fig))

    fig, axes = base('Observed effects as more chains enter the calculation',
        'First 5, 10, 20, 30, 40 and 50 chains from the same context; a descriptive size check.', 3)
    model_colors = {'gpt_astra': '#245B8A', 'gpt_sol': '#9066A8'}
    fig.legend([Line2D([0], [0], color=model_colors[m], marker='o', lw=3) for m in MODELS],
               [LABELS[m] for m in MODELS], loc='upper left', bbox_to_anchor=(.04, .82),
               ncol=2, frameon=False, fontsize=14)
    for ax, metric, title, plus, minus, unit in zip(axes,
        ('chain_total_cost', 'mean_role_order_variance', 'mean_role_bullwhip'),
        ('H2  Cost difference', 'H4a  Variance difference', 'H4b  Bullwhip difference'),
        ('B', 'C', 'C'), ('A', 'B', 'B'),
        ('B − A: game cost units / chain', 'C − B: order variance (units²)', 'C − B: bullwhip ratio')):
        for m in MODELS:
            f = selected_prefixes[selected_prefixes.model == m].pivot(index='chains_per_condition', columns='arm', values=metric)
            ax.plot(f.index, f[plus]-f[minus], color=model_colors[m], marker='o', lw=2.8, ms=7)
        ax.axhline(0, color='#89949E', lw=1, ls='--')
        ax.set_title(title, fontsize=18, weight='bold', pad=18)
        ax.set_xlabel('Chains per condition (same context)', fontsize=12, labelpad=12)
        ax.set_ylabel(unit, fontsize=12)
        ax.set_xticks([5, 10, 20, 30, 40, 50])
        ax.yaxis.grid(True, alpha=.14)
    fig.text(.5, .18, 'Each point still uses ONE context per model. These curves do not estimate statistical significance.',
             ha='center', fontsize=13, weight='bold')
    figures.append(('03_effects_vs_chain_count', fig))

    with PdfPages(OUT / 'ALL_THREE_SLIDES.pdf') as pdf:
        for stem, fig in figures:
            for ext in ('png', 'svg', 'pdf'):
                fig.savefig(OUT / f'{stem}.{ext}', dpi=240, facecolor='white')
            pdf.savefig(fig, facecolor='white')
            plt.close(fig)
    lines = ['# First-context presentation figures', '',
        '1. **H2 and H4 have the predicted direction in the first Astra and Sol contexts.**',
        '2. **H1 and H3 do not show the predicted pattern. No hypothesis is statistically established.**',
        f'3. **{review_note}.** Each model has one displayed context, containing 50 dependent chains per condition and 24 weeks. These are provisional descriptive results.', '',
        '[Open all three slides as PDF](ALL_THREE_SLIDES.pdf). Use the PNGs directly in PowerPoint, or SVGs for scalable graphics.', '',
        '## Slide 1 — Costs and order fluctuations', '',
        '[PNG](01_costs_and_fluctuations.png) · [SVG](01_costs_and_fluctuations.svg) · [PDF](01_costs_and_fluctuations.pdf)', '',
        '**Caption:** In the first completed Astra and Sol contexts, the one-decision control condition had higher costs than the condition with a separate revision. Causal education was associated with lower order variation and bullwhip than the one-decision control. These are observed simulation differences, not significance results.', '',
        '| Model | H2: cost B vs A | H4a: variance C vs B | H4b: bullwhip C vs B |',
        '|---|---:|---:|---:|']
    for m in MODELS:
        f=frames[m]
        changes=[100*(f.loc[p,k]/f.loc[n,k]-1) for k,p,n in (
            ('chain_total_cost','B','A'),('mean_role_order_variance','C','B'),('mean_role_bullwhip','C','B'))]
        lines.append('| '+LABELS[m]+' | '+' | '.join(f'{v:+.1f}%' for v in changes)+' |')
    lines += ['', '## Slide 2 — Outstanding replenishment orders', '',
        '[PNG](02_outstanding_order_response.png) · [SVG](02_outstanding_order_response.svg) · [PDF](02_outstanding_order_response.pdf)', '',
        '**Caption:** Restricting revision did not reduce sensitivity to outstanding orders in these first contexts. Education did not increase sensitivity either. Thus the observed H2/H4 directions are not accompanied by the proposed H1/H3 mechanism.', '',
        '## Slide 3 — Effects versus the number of chains', '',
        '[PNG](03_effects_vs_chain_count.png) · [SVG](03_effects_vs_chain_count.svg) · [PDF](03_effects_vs_chain_count.pdf)', '',
        '**Caption:** Effects are recomputed using the first 5 to 50 chains in each context. This shows within-context stability; it does not add independent replications. A valid observed significance-versus-size curve requires more eligible fresh contexts.', '',
        '## What these figures include', '',
        'First completed context from each non-excluded model (Astra and Sol); all three conditions are shown. The two completed Luna attempts are excluded because of filtered state displays (run001) and programmatically generated choices (run002), not their effect directions. Claude has no collected local-agent data. Additional contexts are still being collected.', '',
        'A = control reading + initial decision and separate revision. B = control + one decision. C = causal education + one decision. All conditions share a context, so carryover is possible. All models requested high reasoning effort; client labels are not provider-authenticated model identity. This tests revision opportunities, not a timed human deadline; sensitivity is a proxy, not a calibrated underweighting coefficient.', '',
        'H2 is mean 24-week holding plus backlog cost per chain. H4a averages weekly order variance over roles and chains; H4b averages role order variance divided by external demand variance. These quantities are not comparisons of model accuracy against human data.', '',
        '[Plotted values](plotted_condition_values.csv) · [Plotted size prefixes](plotted_chain_prefixes.csv) · [Source evidence](SOURCE_RESULTS.json) · [Hashes and provenance](MANIFEST.json).', '',
        'This is a frozen first-context slide snapshot. For newer completed runs, see the [live report](../REPORT.md) and [progress notebook](../../../notebooks/AGENT_PROGRESS.ipynb).', '',
        'Export: `.venv/Scripts/python.exe scripts/export_agent_slides_v5.py`. The script verifies that the 50-chain endpoints equal the condition summaries and refuses to overwrite a snapshot with different evidence. No API calls or new decisions are made.', '']
    (OUT/'README.md').write_text('\n'.join(lines), encoding='utf-8')
    manifest=dict(fingerprint=fingerprint, created_utc=datetime.now(timezone.utc).isoformat(),
        source_evidence_id=evidence['evidence_id'], selection='First context only, all non-excluded models; descriptive',
        plotted_contexts=[identities[(m, 'run001')] for m in MODELS],
        inference='None: one context per model, transcript review status visible',
        validation='All 50-chain prefix endpoints equal plotted condition summaries at rtol/atol 1e-12',
        artifacts={p.name:digest(p) for p in sorted(OUT.iterdir()) if p.is_file()})
    (OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(OUT / 'README.md')


if __name__ == '__main__':
    main()
