"""Descriptive analysis and figures for manually imported generated cohorts."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .game import ROLES
from .manual_cohort import read, replay, progress, STAGES, audit

COLORS = {'initial': '#3B6FB6', 'revision': '#D77A36'}
LABELS = {'initial': 'Initial trajectories', 'revision': 'Reconsidered trajectories'}
DISCLAIMER = ('Generated fictional cohorts; no human observations. These are descriptive contrasts, '
              'not tests of per-decision token pressure or independent students. Whole trajectories '
              'from the same response share a generator. No inferential p-values or confidence intervals '
              'are assigned to the generated student rows.')


def ratio(values, reference):
    denominator = float(np.var(reference, ddof=1)) if len(reference)>1 else 0
    return float(np.var(values, ddof=1)/denominator) if denominator>0 else np.nan


def summarize(rounds, probes):
    if rounds.empty:
        return {k:pd.DataFrame() for k in ('roles','chains','contrasts','hypotheses','batches','quality','phases')}
    roles=[]
    for (batch,rep,chain,condition,role), frame in rounds.groupby(['batch_id','repetition','chain_id','condition','role']):
        model=frame[frame.phase=='model']
        roles.append(dict(batch_id=batch,repetition=rep,chain_id=chain,condition=condition,role=role,
                    profile_id=frame.iloc[0].profile_id,
                    bullwhip=ratio(model.order,model.customer_demand),
                    local_bullwhip=ratio(model.order,model.demand),
                    cost=float(frame.cost.sum()), model_cost=float(model.cost.sum()),
                    automatic_cost=float(frame.loc[frame.phase=='automatic','cost'].sum()),
                    practice_cost=float(frame.loc[frame.phase=='practice','cost'].sum()),
                    zero_fraction=float((model.order==0).mean()),max_order=int(model.order.max()),
                    undefined_bullwhip=bool(model.customer_demand.var(ddof=1)==0)))
    roles=pd.DataFrame(roles)
    chains=roles.groupby(['batch_id','repetition','chain_id','condition']).agg(
        cost=('cost','sum'),model_cost=('model_cost','sum'),automatic_cost=('automatic_cost','sum'),
        practice_cost=('practice_cost','sum'),bullwhip=('bullwhip','mean'),
        defined_roles=('bullwhip','count')).reset_index()
    chains.loc[chains.defined_roles!=4,'bullwhip']=np.nan
    sensitivity=probes.groupby(['chain_id','condition']).sensitivity.mean().rename('sensitivity').reset_index()
    chains=chains.merge(sensitivity,on=['chain_id','condition'],validate='one_to_one')
    contrasts=[]
    for chain, frame in chains.groupby('chain_id'):
        if set(frame.condition)!=set(STAGES):
            continue
        by=frame.set_index('condition')
        row=dict(chain_id=chain,batch_id=frame.iloc[0].batch_id,repetition=int(frame.iloc[0].repetition))
        row.update({f'{metric}_difference':float(by.loc['initial',metric]-by.loc['revision',metric])
                    for metric in ('sensitivity','cost','bullwhip','model_cost','automatic_cost')})
        contrasts.append(row)
    contrasts=pd.DataFrame(contrasts)
    hypotheses=[]
    for h,metric,sign,definition in [
        ('H1','sensitivity',-1,'Lower pipeline sensitivity in the initial pass'),
        ('H2','cost',1,'Higher full scored cost in the initial pass'),
        ('H3','bullwhip',1,'Higher customer-referenced bullwhip in the initial pass')]:
        valid=contrasts[f'{metric}_difference'].dropna()
        delta=float(valid.mean()) if len(valid) else np.nan
        direction=('undefined' if not np.isfinite(delta) else 'no mean difference' if delta==0
                   else 'predicted direction' if delta*sign>0 else 'opposite direction')
        hypotheses.append(dict(hypothesis=h,definition=definition,
                               initial=float(chains.loc[chains.condition=='initial',metric].mean()),
                               revision=float(chains.loc[chains.condition=='revision',metric].mean()),
                               initial_minus_revision=delta,defined_chain_pairs=len(valid),
                               direction=direction,conclusion='Descriptive only; hypothesis not established',
                               p_value=None,ci_lower=None,ci_upper=None))
    batches=contrasts.groupby(['batch_id','repetition']).mean(numeric_only=True).reset_index()
    q=[]
    for condition in STAGES:
        frame=rounds[(rounds.condition==condition)&(rounds.phase=='model')]
        paths=[tuple(g.sort_values('week').order) for _,g in frame.groupby(['chain_id','role'])]
        q.append(dict(condition=condition,weekly_orders=len(frame),zero_fraction=float((frame.order==0).mean()),
                      largest_order=int(frame.order.max()),distinct_role_trajectories=len(set(paths)),
                      total_role_trajectories=len(paths),duplicate_trajectory_fraction=1-len(set(paths))/len(paths)))
    phases=rounds.groupby(['condition','phase']).cost.sum().reset_index()
    return dict(roles=roles,chains=chains,contrasts=contrasts,hypotheses=pd.DataFrame(hypotheses),
                batches=batches,quality=pd.DataFrame(q),phases=phases)


def _style():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                        'axes.spines.right':False,'axes.titleweight':'bold',
                        'axes.labelcolor':'#26384A','text.color':'#26384A',
                        'figure.facecolor':'white','savefig.facecolor':'white'})


def _save(fig,path,title,synthetic):
    prefix='SOFTWARE TEST — ' if synthetic else 'MODEL-GENERATED COHORT — '
    fig.suptitle(prefix+title,fontsize=15,fontweight='bold',x=.05,ha='left')
    fig.text(.05,.012,'Descriptive simulation results · initial minus reconsidered · rows within a batch are dependent',
             fontsize=8,color='#62758A')
    fig.tight_layout(rect=(0,.04,1,.93))
    for suffix in ('.png','.pdf'):
        fig.savefig(path.with_suffix(suffix),dpi=190,bbox_inches='tight')
    plt.close(fig)


def trajectory_figure(rounds,chain_id):
    _style()
    own=rounds[rounds.chain_id==chain_id]
    fig,axes=plt.subplots(2,2,figsize=(12,7),sharex=True)
    if own.empty:
        raise ValueError('No imported chain with this ID.')
    end=int(own.loc[own.phase=='model','week'].max())
    for ax,role in zip(axes.flat,ROLES):
        for condition in STAGES:
            f=own[(own.role==role)&(own.condition==condition)].sort_values('week')
            ax.plot(f.week,f.order,label=LABELS[condition],color=COLORS[condition],linewidth=1.7)
        f=own[(own.role==role)&(own.condition=='initial')].sort_values('week')
        ax.plot(f.week,f.customer_demand,color='#283640',ls=':',label='Customer demand',linewidth=1.3)
        ax.axvspan(.5,4.5,color='#EEF1F5');ax.axvspan(end+.5,own.week.max()+.5,color='#FFF1DE')
        ax.set(title=role.capitalize(),xlabel='Week',ylabel='Cases');ax.grid(alpha=.18)
    axes[0,0].legend(fontsize=8)
    fig.tight_layout()
    return fig


def make_figures(folder,rounds,probes,tables,synthetic=False):
    _style()
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    out=[]
    contrasts=tables['contrasts'];batches=tables['batches']
    fig,axes=plt.subplots(1,3,figsize=(13,4.2))
    for ax,h,metric,title in zip(axes,['H1','H2','H3'],['sensitivity','cost','bullwhip'],
                                ['Pipeline sensitivity','Full scored cost','Bullwhip ratio']):
        vals=contrasts[metric+'_difference'].dropna().to_numpy()
        ax.axvline(0,color='#596C80',lw=1,ls='--')
        if len(vals):
            y=np.linspace(-.28,.28,len(vals))
            ax.scatter(vals,y,s=14,alpha=.35,color='#849BB6',label='Generated chain pairs')
            bs=batches[metric+'_difference'].dropna()
            ax.scatter(bs,np.zeros(len(bs)),marker='D',s=45,color='#3B6FB6',label='Batch means')
            ax.scatter([vals.mean()],[.48],marker='*',s=150,color='#D77A36',label='Overall mean')
        ax.set(title=f'{h} · {title}',xlabel='Initial − reconsidered',yticks=[],ylim=(-.55,.7))
    axes[0].legend(loc='lower left',fontsize=7)
    _save(fig,folder/'hypothesis_contrasts','H1 / H2 / H3 contrasts',synthetic);out.append('hypothesis_contrasts')
    fig,ax=plt.subplots(figsize=(10,5))
    for i,role in enumerate(ROLES):
        for j,condition in enumerate(STAGES):
            vals=tables['roles'].loc[(tables['roles'].role==role)&(tables['roles'].condition==condition),'bullwhip'].dropna()
            if len(vals):
                box=ax.boxplot([vals],positions=[i+(j-.5)*.32],widths=.26,patch_artist=True,manage_ticks=False,
                               showfliers=False,medianprops={'color':'#202F40'})
                box['boxes'][0].set_facecolor(COLORS[condition]);box['boxes'][0].set_alpha(.7)
    ax.axhline(1,color='#9B3444',ls='--',label='Amplification threshold = 1')
    for c in STAGES:ax.plot([],[],color=COLORS[c],lw=6,label=LABELS[c])
    ax.set(xticks=range(4),xticklabels=[r.capitalize() for r in ROLES],ylabel='Var(role orders) / Var(customer demand)')
    ax.legend(fontsize=8);ax.grid(axis='y',alpha=.2)
    _save(fig,folder/'bullwhip_by_role','Order amplification by role',synthetic);out.append('bullwhip_by_role')
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    phase_colors={'practice':'#A6B6C8','model':'#3B6FB6','automatic':'#D77A36'}
    for x,condition in enumerate(STAGES):
        base=0
        chains=tables['chains'][tables['chains'].condition==condition]
        for phase in ('practice','model','automatic'):
            value=float(chains[phase+'_cost'].mean())
            axes[0].bar(x,value,bottom=base,color=phase_colors[phase],label=phase if x==0 else None)
            base+=value
    axes[0].set(xticks=[0,1],xticklabels=['Initial','Reconsidered'],ylabel='Mean cost per four-role chain')
    axes[0].legend(title='Scored weeks',fontsize=8)
    for condition in STAGES:
        f=rounds[rounds.condition==condition].groupby(['chain_id','week']).cost.sum().groupby('week').mean().cumsum()
        axes[1].plot(f.index,f.values,label=LABELS[condition],color=COLORS[condition],lw=2)
    axes[1].set(xlabel='Week',ylabel='Mean cumulative cost per chain');axes[1].legend(fontsize=8)
    _save(fig,folder/'cost_phases','Costs and automatic continuation',synthetic);out.append('cost_phases')
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    for ax,condition in zip(axes,STAGES):
        f=probes[probes.condition==condition]
        ax.scatter(f.low_order,f.high_order,s=20,alpha=.4,color=COLORS[condition])
        top=max(1,int(max(f.low_order.max(),f.high_order.max())))
        ax.plot([0,top],[0,top],ls='--',color='#8795A4',lw=1)
        ax.set(title=LABELS[condition],xlabel='Order with 8 dispatched cases',ylabel='Order with 32 dispatched cases')
    _save(fig,folder/'pipeline_probes','Matched-state pipeline responses',synthetic);out.append('pipeline_probes')
    fig,axes=plt.subplots(1,2,figsize=(12,6),sharey=True)
    model=rounds[rounds.phase=='model']
    vmax=max(1,int(model.order.max()))
    for ax,condition in zip(axes,STAGES):
        matrix=model[model.condition==condition].pivot(index=['chain_id','role'],columns='week',values='order').sort_index()
        im=ax.imshow(matrix.to_numpy(),aspect='auto',interpolation='nearest',cmap='cividis',vmin=0,vmax=vmax,
                     extent=[matrix.columns.min()-.5,matrix.columns.max()+.5,len(matrix),0])
        ax.set(title=LABELS[condition],xlabel='Decision week',ylabel='Generated role trajectory (sorted)')
    fig.colorbar(im,ax=axes.ravel().tolist(),label='Ordered cases',fraction=.025,pad=.02)
    # Explicit layout leaves room for the shared color bar.
    fig.subplots_adjust(left=.08,right=.88,bottom=.11,top=.84,wspace=.18)
    fig.suptitle(('SOFTWARE TEST — ' if synthetic else 'MODEL-GENERATED COHORT — ')+'Every imported order trajectory',fontsize=14)
    for suffix in ('.png','.pdf'):fig.savefig((folder/'order_heatmap').with_suffix(suffix),dpi=190,bbox_inches='tight')
    plt.close(fig);out.append('order_heatmap')
    fig=trajectory_figure(rounds,str(rounds.iloc[0].chain_id))
    _save(fig,folder/'example_chain','First chain: orders, practice and continuation',synthetic);out.append('example_chain')
    return out


def _markdown(frame):
    # Avoid a new tabulate dependency.
    def cell(v):
        if isinstance(v,float):return '—' if not np.isfinite(v) else f'{v:.5g}'
        return str(v).replace('|','/')
    if frame.empty:return '_No paired responses imported yet._\n'
    return '| '+' | '.join(frame.columns)+' |\n| '+' | '.join(['---']*len(frame.columns))+' |\n'+''.join(
        '| '+' | '.join(cell(v) for v in row)+' |\n' for row in frame.itertuples(index=False,name=None))


def build_report(run, *, fit_beta=False):
    run=Path(run);m=audit(run);plan=read(run/'plan.json');status=progress(run)
    rounds,probes,imports=replay(run)
    tables=summarize(rounds,probes)
    folder=run.parents[2]/'reports'/run.name;folder.mkdir(parents=True,exist_ok=True)
    # Snapshot the exact inputs and analysis source for this export. Different inputs
    # use separate version folders, while REPORT.md remains a small latest pointer.
    evidence={p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(run.rglob('*')) if p.is_file() and 'inbox' not in p.parts}
    signature=hashlib.sha256(json.dumps({'evidence':evidence,'fit_beta':fit_beta},sort_keys=True).encode()).hexdigest()[:12]
    version=folder/'analysis'/signature;version.mkdir(parents=True,exist_ok=True)
    images=make_figures(version,rounds,probes,tables,m['config']['synthetic']) if not rounds.empty else []
    for name,frame in tables.items():frame.to_csv(version/(name+'.csv'),index=False)
    rounds.to_csv(version/'rounds.csv',index=False);probes.to_csv(version/'probes.csv',index=False)
    beta=pd.DataFrame()
    if fit_beta and not rounds.empty:
        from .estimation import estimate_beta
        beta=pd.DataFrame([dict(chain_id=chain,condition=condition,role=role,**estimate_beta(frame))
                           for (chain,condition,role),frame in rounds[rounds.phase=='model'].groupby(['chain_id','condition','role'])])
        beta.to_csv(version/'exploratory_beta.csv',index=False)
    complete=bool(status.initial.all() and status.revision.all())
    n_paired=int((status.initial & status.revision).sum())
    paragraphs=[f"# {'SOFTWARE TEST: ' if m['config']['synthetic'] else ''}Manual cohort comparison\n\n",
                f"Status: **{'complete' if complete else 'partial / awaiting pasted responses'}**. "
                f"{int(status.initial.sum()+status.revision.sum())}/{plan['expected_responses']} responses accepted; "
                f"{n_paired}/{len(status)} batches have both passes.\n\n",
                f"Planned fictional identities: **{plan['fictional_identities']:,}**; "
                f"condition-specific role trajectories: **{plan['condition_trajectories']:,}**. "
                f"Model label recorded by the operator: **{m['config']['model_label']}**, effort **high**.\n\n",
                DISCLAIMER+'\n\n',
                '## H1, H2 and H3\n\n',
                _markdown(tables['hypotheses'][['hypothesis','initial','revision','initial_minus_revision','defined_chain_pairs','direction']]
                          if not tables['hypotheses'].empty else pd.DataFrame()),
                '\nH1 is the matched-state sensitivity proxy: (order with 8 dispatched cases − order with 32)/24. '
                'H2 sums holding/backlog costs over practice, model and 12 continuation weeks. '
                'H3 averages the four role order/customer-demand sample-variance ratios during model weeks. '
                'A zero customer-demand variance makes H3 undefined; it is never replaced by zero. '
                'The original structural beta is separate and optional.\n\n',
                'A predicted direction describes this generated dataset. It does not verify the student-time hypothesis. '
                'An opposite direction does not disprove that hypothesis. No actual per-student reasoning tokens or '
                'wall-clock budgets were observed. The generator sees the horizon and future demand paths; '
                'prompt instructions cannot prove decentralized information use.\n\n',
                '## Completion and data quality\n\n',_markdown(status), '\n',_markdown(tables['quality']),
                '\nOnly batches with both accepted passes enter paired comparisons. Missing outputs remain missing; '
                'no order is filled in or clipped. Rejected raw responses are retained. Identical paths and valid zero '
                'orders are reported, not removed. A correct rules answer and successful physical replay validate '
                'format and accounting, not human behavior or the model’s internal state tracking.\n\n']
    for image in images:paragraphs.append(f'![{image.replace("_"," ")}]({image}.png)\n\n')
    if fit_beta:paragraphs.append(f'Exploratory structural beta: {int(beta.usable.sum()) if len(beta) else 0}/{len(beta)} usable role fits. '
                                   'No beta hypothesis conclusion is substituted for H1.\n\n')
    if not rounds.empty:
        with pd.ExcelWriter(version/'RESULTS.xlsx',engine='openpyxl') as writer:
            for name,frame in tables.items():frame.to_excel(writer,sheet_name=name,index=False)
            rounds.to_excel(writer,sheet_name='rounds',index=False)
            probes.to_excel(writer,sheet_name='probes',index=False)
        paragraphs.append('Tables: [RESULTS.xlsx](RESULTS.xlsx); figures are available as PNG and PDF.\n')
    (version/'REPORT.md').write_text(''.join(paragraphs),encoding='utf-8')
    (version/'provenance.json').write_text(json.dumps(dict(inputs_sha256=evidence,api_calls=0,
        imported_responses=len(imports),analysis_signature=signature,synthetic=m['config']['synthetic']),indent=2),encoding='utf-8')
    (folder/'REPORT.md').write_text(f'# Manual cohort report\n\n[Open the latest report](analysis/{signature}/REPORT.md).\n\n'
                                   +DISCLAIMER+'\n',encoding='utf-8')
    prompt_links=[]
    for path in sorted((folder/'prompts').glob('*.md')):
        prompt_links.append(f'- [{path.stem}](prompts/{path.name})\n')
    (folder/'PROMPTS.md').write_text('# Copy-and-paste prompts\n\nCopy one complete prompt box per fresh chat. '
        'Use the same selected model and high effort throughout. Import every initial batch before moving to revisions. '
        'Revision prompts appear after their initial output is accepted.\n\n'+''.join(prompt_links),encoding='utf-8')
    pointer=dict(run=str(run.resolve()),report=str((version/'REPORT.md').resolve()),synthetic=m['config']['synthetic'])
    if not m['config']['synthetic']:
        (folder.parent/'LATEST_MANUAL_COHORT_REPORT.json').write_text(json.dumps(pointer,indent=2),encoding='utf-8')
    return dict(folder=version,report=version/'REPORT.md',tables=tables,rounds=rounds,probes=probes,
                complete=complete,images=images)
