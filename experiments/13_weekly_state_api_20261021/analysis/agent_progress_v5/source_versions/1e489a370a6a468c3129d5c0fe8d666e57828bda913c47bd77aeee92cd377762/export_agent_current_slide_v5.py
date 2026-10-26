"""Current descriptive replication slide; freeze prior exports before replacing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/13_weekly_state_api_20261021/reports/agent_collection_v5'
OUT=SOURCE/'slides_current'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def save_figure(fig,stem):
    # Replace finished files so an image preview never sees a truncated PNG.
    for ext in ('png','svg','pdf'):
        path=OUT/f'{stem}.{ext}'
        temporary=OUT/f'.{stem}.new.{ext}'
        fig.savefig(temporary,dpi=240,facecolor='white',format=ext)
        temporary.replace(path)


def hypothesis_slide(evidence):
    """Five outcomes and all reviewed model estimates; no best-run selection."""
    data=pd.read_csv(SOURCE/'current_context_inference.csv')
    models=['gpt_astra','gpt_sol','gpt_luna']
    endpoints=['H1','H2','H3','H4a','H4b']
    labels=['H1  Constraint → pipeline sensitivity','H2  Constraint → total cost',
        'H3  Education → pipeline sensitivity','H4a  Education → order variance','H4b  Education → bullwhip']
    directions=[-1,1,1,-1,-1]
    fig=plt.figure(figsize=(16,9));ax=fig.add_axes([.035,.29,.93,.48]);ax.axis('off')
    fig.text(.045,.925,'H1–H4: observed effects and p-values',fontsize=29,weight='bold')
    fig.text(.045,.86,'Reviewed contexts only. Δ = mean difference; p = raw two-sided p; Holm = adjustment across 20 tests.',fontsize=15,color='#536473')
    rows=[];plotted=[]
    for h,label,direction in zip(endpoints,labels,directions):
        values=[]
        for model in models:
            r=data[(data.model==model)&(data.hypothesis==h)].iloc[0]
            n=int(r.reviewed_contexts)
            p=f'{r.p_two_sided:.3g}' if pd.notna(r.p_two_sided) else '—'
            adjusted=f'{r.p_holm_20:.3g}' if pd.notna(r.p_holm_20) else '—'
            values.append(f'Δ {r.mean_difference:+.3g}\np {p} | Holm {adjusted}' if n else 'Pending review')
            plotted.append(dict(model=model,hypothesis=h,mean_difference=float(r.mean_difference),reviewed_contexts=n,
                p_two_sided=float(r.p_two_sided) if pd.notna(r.p_two_sided) else None,
                p_holm_20=float(r.p_holm_20) if pd.notna(r.p_holm_20) else None))
        rows.append([label,'Below 0' if direction<0 else 'Above 0',*values])
    counts=[int(data[(data.model==m)&(data.hypothesis=='H1')].reviewed_contexts.iloc[0]) for m in models]
    table=ax.table(cellText=rows,colLabels=['Outcome','Predicted',*[f'{label}\nn = {n} contexts' for label,n in zip(['GPT-6 Astra','GPT-6.1 Sol','GPT-6 Luna'],counts)]],
        cellLoc='center',colWidths=[.31,.1,.197,.197,.196],bbox=[0,0,1,1])
    table.auto_set_font_size(False);table.set_fontsize(13)
    for (r,c),cell in table.get_celld().items():
        cell.set_edgecolor('white');cell.set_linewidth(2)
        if r==0:cell.set_facecolor('#173044');cell.set_text_props(color='white',weight='bold')
        else:
            cell.set_facecolor('#F0F4F6' if r%2 else '#FAFBFC')
            if c==0:cell.set_text_props(ha='left')
    sensitivity=data[data.hypothesis.isin(['H1','H3']) & (data.reviewed_contexts>0)]
    sensitivity_text=('H1 / H3: no observed treatment differences in the reviewed pipeline-sensitivity measurements.'
        if (sensitivity.mean_difference.abs()<1e-10).all() else
        'H1 / H3: observed pipeline-sensitivity changes and their p-values appear in the table.')
    fig.text(.045,.215,sensitivity_text,fontsize=15)
    fig.text(.045,.165,'H2 / H4: observed signs differ across models and repeated contexts.',fontsize=15)
    fig.text(.045,.10,'A = control + revision     B = control + one decision     C = causal education + one decision',fontsize=12)
    fig.text(.045,.045,'n = reviewed independent contexts. — = p unavailable with one context. H1/H3 use pipeline sensitivity as a proxy.',fontsize=11.5,color='#536473')
    save_figure(fig,'HYPOTHESIS_CONCLUSIONS')
    plt.close(fig)
    pd.DataFrame(plotted).to_csv(OUT/'plotted_hypothesis_means.csv',index=False)


def main():
    evidence=json.loads((SOURCE/'RESULTS.json').read_text(encoding='utf-8'))
    selected=[r for r in evidence['evidence'] if not r['review'].startswith('Excluded:')]
    table=pd.read_csv(SOURCE/'descriptive_context_contrasts.csv')
    fingerprint=dict(source_sha256=sha(SOURCE/'RESULTS.json'),table_sha256=sha(SOURCE/'descriptive_context_contrasts.csv'),inference_sha256=sha(SOURCE/'current_context_inference.csv'),generator_sha256=sha(Path(__file__)))
    version=hashlib.sha256(json.dumps(fingerprint,sort_keys=True).encode()).hexdigest()[:16]
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'MANIFEST.json').exists():
        previous=json.loads((OUT/'MANIFEST.json').read_text(encoding='utf-8'))
        if previous['fingerprint']==fingerprint:
            print(OUT/'README.md');return
        archive=OUT/'history'/previous['version'];archive.mkdir(parents=True,exist_ok=True)
        for p in OUT.iterdir():
            if p.is_file():
                q=archive/p.name
                if q.exists():assert q.read_bytes()==p.read_bytes()
                else:q.write_bytes(p.read_bytes())
    styles={'gpt_astra':('GPT-6 Astra','#245B8A','o'),'gpt_sol':('GPT-6.1 Sol','#9467AA','s'),'gpt_luna':('GPT-6 Luna','#B57222','D')}
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'text.color':'#173044',
        'axes.labelcolor':'#173044','axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
    fig,axes=plt.subplots(1,3,figsize=(16,9))
    fig.subplots_adjust(left=.065,right=.97,bottom=.3,top=.72,wspace=.36)
    fig.text(.045,.925,'Observed model differences across repeated runs',fontsize=28,weight='bold')
    fig.text(.045,.865,'One point = one completed context, with 50 chains per condition and 24 weeks.',fontsize=16,color='#536473')
    plotted=[]
    for ax,h,title,ylabel,direction in zip(axes,['H2','H4a','H4b'],
        ['H2  Cost difference','H4a  Order-variance difference','H4b  Bullwhip difference'],
        ['B − A: game cost units / chain','C − B: variance (units²)','C − B: bullwhip ratio'],[1,-1,-1]):
        allvals=[];maxn=0
        for m,(label,color,marker) in styles.items():
            runs=[r for r in selected if r['model']==m]
            vals=[]
            for n,r in enumerate(runs,1):
                value=float(table[(table.model==m)&(table.run==r['run'])&(table.hypothesis==h)].difference.iloc[0])
                vals.append(value)
                ax.scatter(n,value,color=color,marker=marker,s=85,facecolors=color if r['eligible'] else 'white',linewidths=2,zorder=4)
                plotted.append(dict(model=m,run=r['run'],completion_index_excluding_excluded=n,hypothesis=h,value=value,review=r['review'],reviewed=r['eligible']))
            if vals:ax.plot(range(1,len(vals)+1),vals,color=color,lw=2.8,label=label,zorder=3)
            maxn=max(maxn,len(vals));allvals.extend(vals)
        lo=min(0,min(allvals));hi=max(0,max(allvals));pad=max(hi-lo,.1)*.18
        ax.set_ylim(lo-pad,hi+pad);ax.axhspan(0,hi+pad if direction>0 else lo-pad,color='#EDF6EF',zorder=0)
        ax.axhline(0,color='#667986',lw=1,ls='--')
        ax.set_xticks(range(1,maxn+1),[f'Context {n}' for n in range(1,maxn+1)])
        ax.set_xlim(.7,maxn+.3);ax.set_title(title,fontsize=17,weight='bold',pad=20)
        ax.set_ylabel(ylabel,fontsize=12);ax.yaxis.grid(True,alpha=.15)
        ax.text(.03,.97,'Predicted '+('above' if direction>0 else 'below')+' zero',transform=ax.transAxes,va='top',fontsize=11,color='#477654')
    fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.5,.19),ncol=3,frameon=False,fontsize=15)
    fig.text(.045,.145,'Filled markers: procedure reviewed. Open markers: provenance review incomplete. Excluded runs are omitted.',fontsize=11.5,color='#536473')
    fig.text(.045,.098,'A = control + revision     B = control + one decision     C = causal education + one decision',fontsize=11.5)
    fig.text(.045,.045,'Descriptive AI simulation. Reviewed-context effect sizes and exact p-values are provided in the H1–H4 summary slide.',fontsize=11.5,color='#536473')
    save_figure(fig,'CURRENT_REPLICATION_RESULTS')
    plt.close(fig)
    pd.DataFrame(plotted).to_csv(OUT/'plotted_replication_values.csv',index=False)
    hypothesis_slide(evidence)
    lines=['# Current figures for your slides','',
        '1. **Use this current export rather than the frozen first-run slides for the latest evidence.**',
        '2. **Show the observed effect with its p-value.** Full tables, raw p-values and Holm-adjusted p-values are in the [current report](../REPORT.md).',
        '3. **Both review status and individual repeats are visible.** Opposite or zero results are retained.','',
        '## Slide 1 — Conclusions for H1, H2, H3, H4a and H4b','',
        '[PNG](HYPOTHESIS_CONCLUSIONS.png) · [SVG](HYPOTHESIS_CONCLUSIONS.svg) · [PDF](HYPOTHESIS_CONCLUSIONS.pdf)','',
        '**Caption:** H1/H3 measure response to outstanding orders, H2 measures total cost, and H4 measures order variance and bullwhip. The table reports signed mean differences, raw two-sided p-values and Holm-adjusted p-values. Values average reviewed contexts only; review counts remain explicit.','',
        '## Slide 2 — Replication stability','',
        '[PNG](CURRENT_REPLICATION_RESULTS.png) · [SVG](CURRENT_REPLICATION_RESULTS.svg) · [PDF](CURRENT_REPLICATION_RESULTS.pdf)','',
        '**Caption:** Each point is one complete AI context with 50 chains per condition. The H2 and H4 contrasts vary across repeated contexts; the early Sol directions reverse in its second completed run. Open markers have incomplete provenance review, and filled markers passed the recorded procedure review. These are descriptive observations.','',
        '## Slide 3 — H1–H4 effects versus chain count','',
        '[PNG](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.png) · [SVG](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.svg) · [PDF](../chain_size_stability/H1_H4_VS_CHAIN_SIZE.pdf)','',
        '**Caption:** Each curve recomputes a context\'s H1–H4 contrast using its first 5–50 chains per condition. Green marks the predicted direction. Stability along a curve describes sensitivity to chain count; agreement across separate curves describes repeatability across contexts. Neither substitutes for an independent-context significance test.','',
        '## What the quantities mean','',
        '- **H1/H3 pipeline sensitivity:** how much the order falls for each extra case already on the way. Zero means no reaction; one means one fewer case ordered per additional outstanding case.',
        '- **H2 cost:** 24-week holding plus backlog costs, summed across all four roles and averaged per chain.',
        '- **H4a order variance:** how much weekly orders fluctuate; averaged over roles and chains, in cases squared.',
        '- **H4b bullwhip:** order variance divided by external customer-demand variance; a ratio of two means twice the demand variance.',
        '- **Comparisons:** H1/H2 = B−A; H3/H4 = C−B. Predicted signs: H1 negative, H2 positive, H3 positive, H4 negative.','',
        '[Exact slide data](plotted_replication_values.csv) · [Current report and all extracted results](../REPORT.md) · [Export hashes](MANIFEST.json).','',
        'Model labels/settings are client-requested, all high effort. A/B/C share one context; the intervention changes revision opportunities rather than enforcing a clock deadline. No real-student validation is available.','',
        'Rebuild: `.venv/Scripts/python.exe scripts/export_agent_current_slide_v5.py` after refreshing the report. Prior exports are preserved in history/.','']
    (OUT/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    (OUT/'MANIFEST.json').write_text(json.dumps(dict(version=version,created_utc=datetime.now(timezone.utc).isoformat(),fingerprint=fingerprint,contexts=selected,
        artifacts={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='MANIFEST.json'}),indent=2),encoding='utf-8')
    print(OUT/'README.md')


if __name__=='__main__':main()
