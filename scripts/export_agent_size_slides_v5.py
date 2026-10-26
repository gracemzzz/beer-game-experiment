"""Clean all-hypothesis chain-count and reviewed-context-count slides. Offline."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study.pivot_inference_v2 import paired_inference, holm_adjust

SOURCE=ROOT/'experiments/13_weekly_state_api_20261021/reports/agent_collection_v5'
OUT=SOURCE/'size_stability'
MODELS={'gpt_astra':('GPT-6 Astra','#245B8A','o'),
        'gpt_sol':('GPT-6.1 Sol','#9467AA','s'),
        'gpt_luna':('GPT-6 Luna','#B57222','D')}
PANELS=[('H1','Pipeline use','B − A (×10⁻⁴)',10000),
        ('H2','Total cost','B − A (cost)',1),
        ('H3','Pipeline use','C − B (×10⁻⁴)',10000),
        ('H4a','Order variance','C − B (cases²)',1),
        ('H4b','Bullwhip','C − B (ratio)',1)]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def context_prefixes(contrasts):
    """Chronological reviewed prefixes; no outcome-based subset selection."""
    rows=[]
    for model in MODELS:
        sub=contrasts[(contrasts.model==model)&contrasts.eligible.eq(True)]
        runs=sorted(sub.run.unique())
        for n in range(1,len(runs)+1):
            for h,*_ in PANELS:
                values=[float(sub[(sub.run==r)&(sub.hypothesis==h)].difference.iloc[0]) for r in runs[:n]]
                result=paired_inference(values) if n>=2 else dict(mean_difference=values[0],p_two_sided=None)
                rows.append(dict(model=model,hypothesis=h,reviewed_context_count=n,
                    included_runs=';'.join(runs[:n]),mean_difference=result['mean_difference'],
                    p_two_sided=result['p_two_sided']))
    # Preserve the original four-model/five-outcome family at every prefix.
    for n in sorted({r['reviewed_context_count'] for r in rows}):
        family=[(m,h) for m in [*MODELS,'claude_sonnet'] for h,*_ in PANELS]
        indexed={(r['model'],r['hypothesis']):r for r in rows if r['reviewed_context_count']==n}
        adjusted=holm_adjust([indexed[k]['p_two_sided'] if k in indexed else None for k in family])
        for k,p in zip(family,adjusted):
            if k in indexed:indexed[k]['p_holm_20']=p
    return pd.DataFrame(rows)


def draw(data,xcolumn,stem,title,xlabel,counts):
    fig,axes=plt.subplots(1,5,figsize=(16,9))
    fig.subplots_adjust(left=.065,right=.975,top=.735,bottom=.255,wspace=.60)
    fig.text(.055,.925,title,fontsize=31,weight='bold')
    handles=[Line2D([0],[0],color=color,marker=marker,lw=2.6,
             label=f'{label} (n={counts[model]})') for model,(label,color,marker) in MODELS.items()]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.51,.865),ncol=3,
               frameon=False,fontsize=13,handlelength=2,columnspacing=2)
    for ax,(h,label,unit,factor) in zip(axes,PANELS):
        for model,(_,color,marker) in MODELS.items():
            part=data[(data.model==model)&(data.hypothesis==h)].sort_values(xcolumn)
            ax.plot(part[xcolumn],part.mean_difference*factor,color=color,marker=marker,
                    lw=2.6,markersize=6,markerfacecolor='white',markeredgewidth=1.5)
        values=data[data.hypothesis==h].mean_difference.to_numpy()*factor
        low=min(0,float(values.min()));high=max(0,float(values.max()));pad=max(high-low,.05)*.18
        ax.set_ylim(low-pad,high+pad)
        ax.axhline(0,color='#A8B4BC',lw=1,ls='--')
        ax.set_title(h+'\n'+label,fontsize=16,weight='bold',pad=18)
        ax.set_ylabel(unit,fontsize=11,labelpad=5)
        if xcolumn=='chains_per_condition':
            ax.set_xticks([10,20,30,40,50]);ax.set_xlim(3,52)
        else:
            ax.set_xticks([1,2,3]);ax.set_xlim(.85,3.15)
        ax.tick_params(labelsize=11);ax.yaxis.set_major_locator(plt.MaxNLocator(4))
        ax.ticklabel_format(axis='y',style='plain',useOffset=False)
        ax.grid(axis='y',alpha=.10);ax.spines['left'].set_color('#C2CBD1');ax.spines['bottom'].set_color('#C2CBD1')
    fig.supxlabel(xlabel,y=.16,fontsize=16)
    fig.text(.055,.075,'Reviewed runs only · H1/H3 use ×10⁻⁴',fontsize=11.5,color='#536473')
    for ext in ('png','svg','pdf'):
        temporary=OUT/f'.{stem}.new.{ext}'
        fig.savefig(temporary,dpi=240,facecolor='white',format=ext)
        temporary.replace(OUT/f'{stem}.{ext}')
    plt.close(fig)


def main():
    sources=[SOURCE/'chain_size_stability/plotted_reviewed_model_means.csv',
             SOURCE/'descriptive_context_contrasts.csv',SOURCE/'current_context_inference.csv',
             SOURCE/'RESULTS.json',Path(__file__)]
    fingerprint={str(p.relative_to(ROOT)):sha(p) for p in sources}
    version=hashlib.sha256(json.dumps(fingerprint,sort_keys=True).encode()).hexdigest()[:16]
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=OUT/'MANIFEST.json'
    if manifest.exists():
        previous=json.loads(manifest.read_text(encoding='utf-8'))
        if previous['sources']==fingerprint:
            print(OUT/'README.md');return
        folder=OUT/'history'/previous['version'];folder.mkdir(parents=True,exist_ok=True)
        for p in OUT.iterdir():
            if p.is_file():
                q=folder/p.name
                if q.exists():assert q.read_bytes()==p.read_bytes()
                else:q.write_bytes(p.read_bytes())
    chain=pd.read_csv(sources[0]).rename(columns={'effect_difference':'mean_difference'})
    contexts=context_prefixes(pd.read_csv(sources[1]))
    stats=pd.read_csv(sources[2])
    counts={m:int(stats[(stats.model==m)&(stats.hypothesis=='H1')].reviewed_contexts.iloc[0]) for m in MODELS}
    for model in MODELS:
        for h,*_ in PANELS:
            expected=stats[(stats.model==model)&(stats.hypothesis==h)].iloc[0]
            last_chain=chain[(chain.model==model)&(chain.hypothesis==h)&(chain.chains_per_condition==50)].iloc[0]
            last_context=contexts[(contexts.model==model)&(contexts.hypothesis==h)&(contexts.reviewed_context_count==counts[model])].iloc[0]
            assert np.isclose(last_chain.mean_difference,expected.mean_difference,rtol=1e-12,atol=1e-12)
            assert np.isclose(last_context.mean_difference,expected.mean_difference,rtol=1e-12,atol=1e-12)
            assert np.isclose(last_context.p_two_sided,expected.p_two_sided,atol=1e-12)
            assert last_context.p_holm_20==expected.p_holm_20
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'text.color':'#173044',
        'axes.labelcolor':'#173044','axes.spines.top':False,'axes.spines.right':False,
        'svg.fonttype':'none','pdf.fonttype':42})
    chain.to_csv(OUT/'chain_count_values.csv',index=False)
    contexts.to_csv(OUT/'context_count_values.csv',index=False)
    draw(chain,'chains_per_condition','CHAIN_SIZE','H1–H4: Chain-size stability',
         'Chains per condition in each run',counts)
    draw(contexts,'reviewed_context_count','CONTEXT_COUNT','H1–H4: Context-count stability',
         'Reviewed contexts (cumulative)',counts)
    (OUT/'README.md').write_text('''# Presentation: chain size and context count

Both slides show H1, H2, H3, H4a and H4b with short labels and consistent model colors.

1. **[Chain-count PNG](CHAIN_SIZE.png)** · [SVG](CHAIN_SIZE.svg) · [PDF](CHAIN_SIZE.pdf). The x-axis uses the first 5–50 chains per condition in every reviewed run. Curves average the included contexts equally. Independent context counts stay at Astra2 / Sol2 / Luna3.
2. **[Context-count PNG](CONTEXT_COUNT.png)** · [SVG](CONTEXT_COUNT.svg) · [PDF](CONTEXT_COUNT.pdf). The x-axis adds reviewed fresh contexts chronologically. Curves are cumulative model means. Astra and Sol end at two reviewed contexts; Luna ends at three. No unobserved context is drawn.

H1/H3 use a magnified ×10⁻⁴ scale. Their underlying units are order reduction per additional outstanding case. H2 is 24-week cost per chain; H4a is order variance in cases squared; H4b is the order/customer-demand variance ratio. H1/H2 compare B−A, H3/H4 compare C−B. Group definitions and detailed p-values are in the [report](../REPORT.md).

**Data:** [Chain-prefix means](chain_count_values.csv) and [context-prefix means and p-values](context_count_values.csv). Context p-values are unavailable at n=1 and exploratory at later prefixes. No chain-level p-values are created.

Reviewed runs, in order: Astra run002/run003; Sol run002/run003; Luna run003/run004/run005. Pending and excluded attempts remain in the original report and raw records. Selection follows the existing procedure reviews, not effect direction. The final endpoints and p-values match the published statistics to 1e-12. The collection is closed; these exports make no new model calls.

Rebuild: `.venv/Scripts/python.exe scripts/export_agent_size_slides_v5.py`. Previous exports are preserved in history/. [Source/artifact hashes](MANIFEST.json).
''',encoding='utf-8')
    manifest.write_text(json.dumps(dict(version=version,created_utc=datetime.now(timezone.utc).isoformat(),
        sources=fingerprint,reviewed_contexts=counts,endpoint_checks=30,context_final_p_checks=15,
        artifacts={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='MANIFEST.json'}),indent=2)+'\n',encoding='utf-8')
    print(OUT/'README.md')


if __name__=='__main__':main()
