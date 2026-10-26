"""Observed H1--H4 contrasts versus first-k chains within complete contexts.

Descriptive only: no independent-chain tests, confidence intervals or extrapolation.
Raw decisions and prior publications remain unchanged. Only final procedural
exclusions are omitted from these curves; the manifest retains their reasons.
"""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study.pivot_inference_v2 import ENDPOINTS

SOURCE = ROOT/'experiments/13_weekly_state_api_20261021/reports/agent_collection_v5'
OUT = SOURCE/'chain_size_stability'
SIZES = (5, 10, 20, 30, 40, 50)
LABELS = {'gpt_astra':'GPT-6 Astra', 'gpt_sol':'GPT-6.1 Sol', 'gpt_luna':'GPT-6 Luna'}
COLORS = {'gpt_astra':'#245B8A', 'gpt_sol':'#9467AA', 'gpt_luna':'#B57222'}
MARKERS = {'gpt_astra':'o', 'gpt_sol':'s', 'gpt_luna':'x'}
TITLES = {'H1':'H1  Outstanding-order sensitivity', 'H2':'H2  Total inventory + backlog cost',
          'H3':'H3  Outstanding-order sensitivity', 'H4a':'H4a  Individual order variation',
          'H4b':'H4b  Bullwhip ratio'}
UNITS = {'H1':'Sensitivity difference: B − A', 'H2':'Cost difference / chain: B − A',
         'H3':'Sensitivity difference: C − B', 'H4a':'Variance difference (units²): C − B',
         'H4b':'Bullwhip-ratio difference: C − B'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify(value, direction):
    if abs(value) < 1e-10:
        return 'Zero difference'
    return 'Predicted direction' if value*direction > 0 else 'Opposite direction'


def main():
    sources = ('RESULTS.json','per_chain_results.csv','context_arm_results.csv','within_context_chain_prefixes.csv')
    inputs = {name:sha(SOURCE/name) for name in sources}
    evidence = json.loads((SOURCE/'RESULTS.json').read_text(encoding='utf-8'))
    selected = [r for r in evidence['evidence'] if not r['review'].startswith('Excluded:')]
    excluded = [r for r in evidence['evidence'] if r['review'].startswith('Excluded:')]
    if not selected:
        raise ValueError('No complete non-excluded contexts available')
    fingerprint = dict(sources=inputs, generator_sha256=sha(__file__), sizes=SIZES,
        selection='All complete, physically replayed, not procedurally excluded contexts; pending reviews marked provisional')
    fingerprint = json.loads(json.dumps(fingerprint))
    version = hashlib.sha256(json.dumps(fingerprint,sort_keys=True).encode()).hexdigest()[:16]
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'MANIFEST.json').exists():
        old = json.loads((OUT/'MANIFEST.json').read_text(encoding='utf-8'))
        if old['fingerprint']==fingerprint:
            print('Existing figure matches current evidence: '+str(OUT/'H1_H4_VS_CHAIN_SIZE.png'))
            return
        archive=OUT/'history'/old['version']
        archive.mkdir(parents=True,exist_ok=True)
        for p in OUT.iterdir():
            if p.is_file():
                q=archive/p.name
                if q.exists():
                    assert q.read_bytes()==p.read_bytes()
                else:
                    q.write_bytes(p.read_bytes())
    chains=pd.read_csv(SOURCE/'per_chain_results.csv')
    aggregate=pd.read_csv(SOURCE/'context_arm_results.csv')
    prefixes=pd.read_csv(SOURCE/'within_context_chain_prefixes.csv')
    rows=[]
    provenance=[]
    for r in selected:
        model,run=r['model'],r['run']
        data=chains[(chains.model==model)&(chains.run==run)]
        summary=aggregate[(aggregate.model==model)&(aggregate.run==run)].set_index('arm')
        assert len(data)==150 and data.batch_id.nunique()==1
        bid=data.batch_id.iloc[0]
        recorded=prefixes[(prefixes.model==model)&(prefixes.batch_id==bid)]
        for arm in 'ABC':
            arm_data=data[data.arm==arm].sort_values('chain_index')
            assert list(arm_data.chain_index)==list(range(1,51)), (model,run,arm)
        for name,metric,plus,minus,direction in ENDPOINTS:
            for n in SIZES:
                values={}
                for arm in (plus,minus):
                    part=data[(data.arm==arm)&(data.chain_index<=n)]
                    assert len(part)==n and part[metric].notna().all()
                    values[arm]=float(part[metric].mean())
                    expected=recorded[(recorded.arm==arm)&(recorded.chains_per_condition==n)].iloc[0][metric]
                    assert np.isclose(values[arm],expected,rtol=1e-12,atol=1e-12)
                    if n==50:
                        assert np.isclose(values[arm],summary.loc[arm,metric],rtol=1e-12,atol=1e-12)
                effect=values[plus]-values[minus]
                # ENDPOINTS stores signed numeric directions in the frozen analysis.
                sign=1 if direction in (1,'positive','>0') else -1
                rows.append(dict(model=model,run=run,batch_id=bid,hypothesis=name,
                    metric=metric,chains_per_condition=n,plus_condition=plus,minus_condition=minus,
                    plus_mean=values[plus],minus_mean=values[minus],effect_difference=effect,
                    predicted_sign=sign,descriptive_direction=classify(effect,sign),
                    independent_contexts_in_this_line=1,review_status=r['review'],
                    adherence_review_passed=r['eligible']))
        provenance.append(r)
    table=pd.DataFrame(rows)
    table.to_csv(OUT/'plotted_metrics.csv',index=False)
    stability=[]
    for (model,run,h),sub in table.groupby(['model','run','hypothesis'],sort=False):
        sub=sub.sort_values('chains_per_condition')
        labels=list(sub.descriptive_direction)
        stability.append(dict(model=model,run=run,hypothesis=h,
            same_direction_at_all_six_sizes=len(set(labels))==1,
            direction_at_50=labels[-1],prefixes_matching_direction_at_50=sum(v==labels[-1] for v in labels),
            prefixes_in_predicted_direction=sum(v=='Predicted direction' for v in labels),
            total_prefixes=6,min_effect=sub.effect_difference.min(),max_effect=sub.effect_difference.max(),
            effect_at_50=float(sub.effect_difference.iloc[-1])))
    pd.DataFrame(stability).to_csv(OUT/'direction_stability.csv',index=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,
        'axes.spines.right':False,'axes.edgecolor':'#AFBCC5','text.color':'#173044',
        'axes.labelcolor':'#173044','xtick.color':'#536473','ytick.color':'#536473',
        'svg.fonttype':'none','pdf.fonttype':42})
    fig,axes=plt.subplots(2,3,figsize=(18,10.125))
    fig.subplots_adjust(left=.075,right=.975,top=.815,bottom=.16,wspace=.33,hspace=.55)
    fig.text(.04,.944,'Do the H1–H4 patterns stay stable as chain count increases?',fontsize=25,weight='bold')
    fig.text(.04,.893,'X: first k chains per condition   ·   Y: observed condition difference   ·   Green region: predicted direction',
             fontsize=15,color='#536473')
    pending=any(not r['eligible'] for r in selected)
    # Keep separate contexts visible so opposite replicates cannot be hidden
    # by averaging. Dashed lines denote incomplete provenance review.
    styles={}
    for model in LABELS:
        runs=[r for r in selected if r['model']==model]
        reviewed_index=0
        for r in runs:
            if not r['eligible']:
                styles[(model,r['run'])]='--'
            else:
                styles[(model,r['run'])]=('-',':','-.')[reviewed_index%3]
                reviewed_index+=1
    for ax,(name,metric,plus,minus,direction) in zip(axes.flat,ENDPOINTS):
        sub=table[table.hypothesis==name]
        values=sub.effect_difference.to_numpy()
        lo=min(0,float(values.min()));hi=max(0,float(values.max()))
        spread=max(hi-lo,.05 if 'sensitivity' in metric else 1)
        lo-=spread*.17;hi+=spread*.17
        ax.set_ylim(lo,hi)
        sign=int(sub.predicted_sign.iloc[0])
        ax.axhspan(0,hi if sign>0 else lo,color='#EDF6EF',zorder=0)
        ax.axhline(0,color='#60717D',lw=1.2,ls='--',zorder=1)
        for r in selected:
            m,run=r['model'],r['run']
            vals=sub[(sub.model==m)&(sub.run==run)].sort_values('chains_per_condition')
            ax.plot(vals.chains_per_condition,vals.effect_difference,color=COLORS[m],
                marker=MARKERS[m],ms=7 if m!='gpt_sol' else 8,markerfacecolor='white',
                markeredgewidth=1.6,lw=2.4,ls=styles[(m,run)],
                label=LABELS[m]+' / '+run,zorder=3)
        ax.set_title(TITLES[name],loc='left',fontsize=15,weight='bold',pad=22)
        ax.text(0,1.035,'Predicted: '+('above' if sign>0 else 'below')+' zero',
                transform=ax.transAxes,fontsize=10,color='#477654')
        ax.set_ylabel(UNITS[name],fontsize=11)
        ax.set_xlabel('Chains per condition',fontsize=11,labelpad=5)
        ax.set_xticks(SIZES)
        ax.set_xlim(3,52)
        ax.grid(axis='y',alpha=.13)
        ax.ticklabel_format(axis='y',style='plain',useOffset=False)
    key=axes.flat[-1]
    key.axis('off')
    handles=[Line2D([0],[0],color=COLORS[r['model']],marker=MARKERS[r['model']],
        markerfacecolor='white',markeredgewidth=1.6,lw=2.4,ls=styles[(r['model'],r['run'])],
        label=LABELS[r['model']]+' / '+r['run']+(' (reviewed)' if r['eligible'] else ' (review pending)')) for r in selected]
    key.legend(handles=handles,loc='upper left',bbox_to_anchor=(-.02,1.12),frameon=False,
               fontsize=9 if len(handles)>7 else 10.5,labelspacing=.35)
    key.text(0,.38,'Read both kinds of stability',fontsize=13,weight='bold')
    key.text(0,.28,'Along a curve: sensitivity to chain count\nAcross curves: repeatability across contexts\nZero = no observed condition difference',
             fontsize=11,va='top',linespacing=1.55)
    fig.text(.04,.077,'A = control + revision     B = control + one decision     C = causal education + one decision',fontsize=12)
    fig.text(.04,.035,('Provisional; transcript review pending. ' if pending else 'Descriptive analysis. ')+
        'Each curve is ONE context with dependent chains. Direction stability is not statistical significance.',fontsize=11.5,color='#536473')
    for ext in ('png','svg','pdf'):
        fig.savefig(OUT/f'H1_H4_VS_CHAIN_SIZE.{ext}',dpi=240,facecolor='white')
    plt.close(fig)
    lines=['# H1–H4: chain count versus conclusion stability','',
        '1. **The x-axis is 5, 10, 20, 30, 40 and 50 chains per condition.** Each point uses the same first-k chain IDs in A, B and C.',
        '2. **The y-axis is the effect relevant to each hypothesis:** B−A for H1/H2; C−B for H3/H4a/H4b. Green marks the predicted direction; zero means no observed difference.',
        '3. **These are descriptive direction checks.** The chains in a curve share one context; adding chains to a prefix does not add independent model replications. No chain-level p-values or confidence intervals are computed.','',
        '[Presentation PNG](H1_H4_VS_CHAIN_SIZE.png) · [Scalable SVG](H1_H4_VS_CHAIN_SIZE.svg) · [PDF](H1_H4_VS_CHAIN_SIZE.pdf)','',
        '![H1–H4 versus chain count](H1_H4_VS_CHAIN_SIZE.png)','',
        '## What the observed curves say','',
        '| Model / context | Hypothesis | Direction at 50 chains | Same direction at all six sizes? |',
        '|---|---|---|---|']
    for r in stability:
        lines.append(f"| {LABELS[r['model']]} / {r['run']} | {r['hypothesis']} | {r['direction_at_50']} | {'Yes' if r['same_direction_at_all_six_sizes'] else 'No'} |")
    lines+=['','**Suggested slide caption:** Within each completed AI context, H1–H4 effects were recalculated using the first 5–50 chains per condition. A consistently signed curve indicates descriptive directional stability; a zero crossing indicates sensitivity to the included chains. These curves do not establish statistical significance or student-level replication.','',
        'A = control reading + separate revision; B = control + one committed decision; C = causal education + one decision. H1/H3 measure response to outstanding replenishment orders using probe sensitivity, a proxy for pipeline use. H2 is 24-week holding plus backlog cost per chain. H4a is mean role order variance; H4b is mean role order variance divided by external demand variance. The intervention changes revision opportunities; all three conditions share a context.','',
        '## Included evidence','']
    for r in selected:
        lines.append(f"- {LABELS[r['model']]} / {r['run']}: {r['review']}. Complete physical replay passed.")
    for r in excluded:
        lines.append(f"- Excluded and preserved: {LABELS[r['model']]} / {r['run']}: {r['review']}.")
    lines+=['- Claude has no collected local-agent results.','',
        '[Exact plotted metrics](plotted_metrics.csv) · [Direction stability table](direction_stability.csv) · [Source hashes](MANIFEST.json).', '',
        'Rebuild after new completed results: first run `scripts/report_agent_collection_v5.py`, then `scripts/plot_agent_chain_size_stability_v5.py`, using `.venv/Scripts/python.exe`. Previous chart versions are preserved in `history/`. No API calls or order decisions are made. All calculated prefix means are checked against the report, and the 50-chain endpoints against full condition summaries.','']
    (OUT/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    manifest=dict(version=version,fingerprint=fingerprint,created_utc=datetime.now(timezone.utc).isoformat(),
        selected=provenance,excluded=excluded,source_evidence_id=evidence['evidence_id'],
        validation='150 chain rows/context; identical first-k indices in each condition; every prefix matches published data; 50-chain endpoints match full summaries, tolerances1e-12',
        interpretation='Descriptive sign stability, not significance or independent-chain inference',
        artifacts={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='MANIFEST.json'})
    (OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(OUT/'H1_H4_VS_CHAIN_SIZE.png')


if __name__=='__main__':main()
