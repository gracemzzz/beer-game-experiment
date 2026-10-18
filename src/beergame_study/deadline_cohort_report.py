"""Descriptive deadline-framing reports with repeat-condition variation visible."""
import hashlib
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .game import ROLES
from .deadline_cohort import audit, read, replay, progress, report_folder, next_task

COLORS = {'brief':'#2265AD','ample':'#D57928'}
LABELS = {'brief':'10-second scenario','ample':'180-second scenario'}
METRICS = {'H1':'sensitivity','H2':'cost','H3':'bullwhip'}


def ratio(a,b):
    denominator = float(np.var(b,ddof=1)) if len(b)>1 else 0
    return float(np.var(a,ddof=1)/denominator) if denominator>0 else np.nan


def summarize(rounds,probes):
    names = ('roles','chains','contrasts','hypotheses','batches','repeat_variation','choice_changes','quality')
    if rounds.empty:
        return {n:pd.DataFrame() for n in names}
    records = []
    keys = ['batch_id','generation','chain_id','condition','role']
    for group,f in rounds.groupby(keys):
        model = f[f.phase=='model']
        records.append(dict(zip(keys,group)) | dict(profile_id=f.iloc[0].profile_id,
            bullwhip=ratio(model.order,model.customer_demand),local_bullwhip=ratio(model.order,model.demand),
            cost=float(f.cost.sum()),practice_cost=float(f.loc[f.phase=='practice','cost'].sum()),
            model_cost=float(model.cost.sum()),automatic_cost=float(f.loc[f.phase=='automatic','cost'].sum())))
    roles = pd.DataFrame(records)
    chainkeys = keys[:-1]
    chains = roles.groupby(chainkeys).agg(cost=('cost','sum'),practice_cost=('practice_cost','sum'),model_cost=('model_cost','sum'),
        automatic_cost=('automatic_cost','sum'),bullwhip=('bullwhip','mean'),defined_roles=('bullwhip','count')).reset_index()
    chains.loc[chains.defined_roles!=4,'bullwhip'] = np.nan
    sensitivity = probes.groupby(chainkeys).sensitivity.mean().reset_index()
    chains = chains.merge(sensitivity,on=chainkeys,validate='one_to_one')
    contrasts,paired = [],[]
    for (batch,g,chain),f in chains.groupby(['batch_id','generation','chain_id']):
        if set(f.condition) != {'brief','ample'}:
            continue
        paired.append(f);by=f.set_index('condition')
        contrasts.append(dict(batch_id=batch,generation=g,chain_id=chain) | {metric+'_difference':float(by.loc['brief',metric]-by.loc['ample',metric]) for metric in (*METRICS.values(),'model_cost','automatic_cost')})
    contrasts = pd.DataFrame(contrasts)
    hypotheses = []
    if paired:
        paired = pd.concat(paired)
        for h,metric in METRICS.items():
            valid = contrasts[metric+'_difference'].dropna();delta=float(valid.mean()) if len(valid) else np.nan
            sign = -1 if h=='H1' else 1
            direction = 'undefined' if not np.isfinite(delta) else 'zero observed difference' if delta==0 else 'predicted direction' if delta*sign>0 else 'opposite direction'
            hypotheses.append(dict(hypothesis=h,metric=metric,brief=float(paired[paired.condition=='brief'][metric].mean()),
                ample=float(paired[paired.condition=='ample'][metric].mean()),brief_minus_ample=delta,defined_chain_generation_pairs=len(valid),
                direction=direction,p_value=None,ci_lower=None,ci_upper=None))
    repeats = []
    for (batch,chain,condition),f in chains.groupby(['batch_id','chain_id','condition']):
        by = f.set_index('generation')
        for g1,g2 in itertools.combinations(sorted(by.index),2):
            repeats.append(dict(batch_id=batch,chain_id=chain,condition=condition,generation_a=g1,generation_b=g2) |
                {metric+'_difference':float(by.loc[g1,metric]-by.loc[g2,metric]) for metric in METRICS.values()})
    changes = []
    model = rounds[rounds.phase=='model']
    for (batch,g),f in model.groupby(['batch_id','generation']):
        q = f.pivot(index=['chain_id','role','week'],columns='condition',values='order')
        if set(q.columns)=={'brief','ample'}:
            q=q.dropna();d=q.brief-q.ample
            changes.append(dict(kind='between_deadlines',batch_id=batch,generation=str(g),condition='brief minus ample',choices=len(d),
                changed=int((d!=0).sum()),changed_fraction=float((d!=0).mean()),mean_absolute_change=float(abs(d).mean())))
    for (batch,condition),f in model.groupby(['batch_id','condition']):
        q=f.pivot(index=['chain_id','role','week'],columns='generation',values='order')
        for g1,g2 in itertools.combinations(sorted(q.columns),2):
            pair=q[[g1,g2]].dropna();d=pair[g1]-pair[g2]
            changes.append(dict(kind='repeat_same_deadline',batch_id=batch,generation=f'{g1}-{g2}',condition=condition,choices=len(d),
                changed=int((d!=0).sum()),changed_fraction=float((d!=0).mean()),mean_absolute_change=float(abs(d).mean())))
    quality=[]
    for (condition,g),f in model.groupby(['condition','generation']):
        paths=[tuple(x.sort_values('week').order) for _,x in f.groupby(['chain_id','role'])]
        quality.append(dict(condition=condition,generation=g,orders=len(f),zeros=int((f.order==0).sum()),zero_fraction=float((f.order==0).mean()),
            largest_order=int(f.order.max()),distinct_role_paths=len(set(paths)),role_paths=len(paths)))
    batches = contrasts.groupby(['batch_id','generation']).mean(numeric_only=True).reset_index() if not contrasts.empty else pd.DataFrame()
    return dict(roles=roles,chains=chains,contrasts=contrasts,hypotheses=pd.DataFrame(hypotheses),batches=batches,
                repeat_variation=pd.DataFrame(repeats),choice_changes=pd.DataFrame(changes),quality=pd.DataFrame(quality))


def markdown(df):
    if df.empty:return '_No eligible saved comparisons yet._\n'
    def value(v):
        if isinstance(v,float):return 'undefined' if not np.isfinite(v) else f'{v:.6g}'
        return str(v).replace('|','/')
    return '| '+' | '.join(df.columns)+' |\n| '+' | '.join(['---']*len(df.columns))+' |\n'+''.join('| '+' | '.join(value(v) for v in row)+' |\n' for row in df.itertuples(index=False,name=None))


def trajectory_figure(rounds,chain_id):
    own=rounds[rounds.chain_id==chain_id];fig,axes=plt.subplots(2,2,figsize=(12,7),sharex=True)
    end=int(own.loc[own.phase=='model','week'].max())
    for ax,role in zip(axes.flat,ROLES):
        f=own[own.role==role]
        for (condition,g),rows in f.groupby(['condition','generation']):
            rows=rows.sort_values('week')
            ax.plot(rows.week,rows.order,color=COLORS[condition],ls=['-','--',':','-.'][(g-1)%4],alpha=.85,label=f'{LABELS[condition]}, run {g}')
        rows=f.drop_duplicates('week').sort_values('week');ax.plot(rows.week,rows.customer_demand,color='#253746',ls=':',lw=1,label='Customer demand')
        ax.axvspan(.5,4.5,color='#E9EEF2');ax.axvspan(end+.5,own.week.max()+.5,color='#FFF0D9')
        ax.set(title=role.capitalize(),xlabel='Week',ylabel='Ordered cases');ax.grid(alpha=.16)
    axes[0,0].legend(fontsize=7);fig.tight_layout();return fig


def make_figures(folder,rounds,tables,synthetic=False):
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'font.size':10})
    images=[]
    def save(fig,name,title):
        fig.suptitle(('SOFTWARE TEST: ' if synthetic else 'GENERATED STUDENT SCENARIOS: ')+title,fontsize=14,fontweight='bold')
        fig.text(.02,.01,'Descriptive only | Fictional deadlines, not measured runtime | Repeats are not new students',fontsize=8,color='#536573')
        fig.tight_layout(rect=(0,.045,1,.93))
        for ext in ('png','pdf'):fig.savefig(folder/(name+'.'+ext),dpi=180,bbox_inches='tight')
        plt.close(fig);images.append(name)
    if rounds.empty:return images
    chains=tables['chains']
    fig,axes=plt.subplots(1,3,figsize=(13,4.8))
    for ax,(h,metric) in zip(axes,METRICS.items()):
        for (_,g,chain),f in chains.groupby(['batch_id','generation','chain_id']):
            if set(f.condition)=={'brief','ample'}:
                vals=f.set_index('condition').loc[['brief','ample'],metric]
                ax.plot([0,1],vals,color='#8398AC',alpha=.25,lw=.7)
        for i,condition in enumerate(('brief','ample')):
            vals=chains.loc[chains.condition==condition,metric].dropna()
            if len(vals):ax.scatter([i]*len(vals),vals,s=13,color=COLORS[condition],alpha=.4);ax.scatter(i,vals.mean(),s=100,marker='D',color='black',zorder=5)
        ax.set(title=f'{h}: {metric}',xticks=[0,1],xticklabels=['10 seconds','180 seconds'],ylabel='Chain value; diamond = mean')
    save(fig,'hypothesis_levels','Actual H1 / H2 / H3 values')
    fig,axes=plt.subplots(1,3,figsize=(13,4.8))
    for ax,(h,metric) in zip(axes,METRICS.items()):
        groups=[]
        c=tables['contrasts'];r=tables['repeat_variation']
        groups.append(c[metric+'_difference'].abs().dropna() if not c.empty else pd.Series(dtype=float))
        groups.extend(r.loc[r.condition==s,metric+'_difference'].abs().dropna() if not r.empty else pd.Series(dtype=float) for s in ('brief','ample'))
        for x,v in enumerate(groups):
            if len(v):
                ax.scatter(np.full(len(v),x)+np.linspace(-.08,.08,len(v)),v,alpha=.35,s=17,color=['#694F9C',COLORS['brief'],COLORS['ample']][x])
                ax.scatter(x,v.mean(),marker='D',s=70,color='black')
        ax.set(title=h+': '+metric,xticks=[0,1,2],xticklabels=['Between\ndeadlines','Repeat\n10 seconds','Repeat\n180 seconds'],ylabel='Absolute difference')
    save(fig,'effect_and_repeat_variation','Deadline differences alongside repeat variation')
    fig,ax=plt.subplots(figsize=(10,4.7))
    for i,condition in enumerate(('brief','ample')):
        values=tables['roles'][tables['roles'].condition==condition].groupby('role').bullwhip.mean().reindex(ROLES)
        ax.plot(range(4),values,'o-',color=COLORS[condition],label=LABELS[condition])
    ax.axhline(1,ls='--',color='#8D4444',label='Amplification = 1');ax.set(xticks=range(4),xticklabels=ROLES,ylabel='Mean Var(orders) / Var(customer demand)');ax.legend()
    save(fig,'bullwhip_by_role','Order amplification by position')
    fig,ax=plt.subplots(figsize=(10,4.7))
    for x,condition in enumerate(('brief','ample')):
        bottom=0
        for phase,color in [('practice','#9EAFBF'),('model','#3573AE'),('automatic','#D57928')]:
            value=float(chains.loc[chains.condition==condition,phase+'_cost'].mean())
            if np.isfinite(value):ax.bar(x,value,bottom=bottom,color=color,label=phase if x==0 else None);bottom+=value
    ax.set(xticks=[0,1],xticklabels=list(LABELS.values()),ylabel='Mean simulated cost per chain');ax.legend()
    save(fig,'cost_phases','Model weeks and automatic continuation')
    model=rounds[rounds.phase=='model'];fig,axes=plt.subplots(1,2,figsize=(13,6),layout='constrained')
    vmax=max(1,int(model.order.max()));im=None
    for ax,condition in zip(axes,('brief','ample')):
        f=model[model.condition==condition]
        if f.empty:ax.text(.5,.5,'Awaiting response',ha='center');continue
        mat=f.pivot(index=['generation','chain_id','role'],columns='week',values='order').sort_index()
        im=ax.imshow(mat,aspect='auto',interpolation='nearest',cmap='cividis',vmin=0,vmax=vmax,extent=[mat.columns.min()-.5,mat.columns.max()+.5,len(mat),0])
        ax.set(title=LABELS[condition],xlabel='Decision week',ylabel='Role trajectory, grouped by generation')
    if im is not None:fig.colorbar(im,ax=list(axes),label='Ordered cases',shrink=.75)
    fig.suptitle(('SOFTWARE TEST: ' if synthetic else 'GENERATED STUDENT SCENARIOS: ')+'Every submitted weekly order')
    for ext in ('png','pdf'):fig.savefig(folder/('all_orders.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig);images.append('all_orders')
    save(trajectory_figure(rounds,str(rounds.iloc[0].chain_id)),'example_chain','First chain, all conditions and repeat generations')
    return images


def build_report(run):
    run=Path(run);m=audit(run);plan=read(run/'plan.json');status=progress(run)
    rounds,probes,imports=replay(run);tables=summarize(rounds,probes)
    evidence={p.relative_to(run).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(run.rglob('*')) if p.is_file() and 'inbox' not in p.parts}
    signature=hashlib.sha256(json.dumps(evidence,sort_keys=True).encode()).hexdigest()[:12]
    folder=report_folder(run);version=folder/'analysis'/signature;version.mkdir(parents=True,exist_ok=True)
    images=make_figures(version,rounds,tables,m['config']['synthetic'])
    for name,frame in tables.items():frame.to_csv(version/(name+'.csv'),index=False)
    rounds.to_csv(version/'rounds.csv',index=False);probes.to_csv(version/'probes.csv',index=False)
    if not rounds.empty:
        with pd.ExcelWriter(version/'RESULTS.xlsx') as writer:
            for name,frame in tables.items():frame.to_excel(writer,sheet_name=name,index=False)
            rounds.to_excel(writer,sheet_name='rounds',index=False);probes.to_excel(writer,sheet_name='probes',index=False)
    complete=bool(status.accepted.all());task=next_task(run)
    parts=['# Deadline-framed Beer Game study\n\n',f"Status: **{'complete' if complete else 'partial / awaiting responses'}**; {int(status.accepted.sum())}/{len(status)} responses accepted.\n\n",
        f"**{plan['fictional_identities']} fictional identities**, {len(plan['chains'])} chains, {m['config']['generations']} repeated generations per deadline. Repeats reuse the same identities, profiles and demand paths. Model label: **{m['config']['model_label']} / {m['config']['effort_label']}**; collection: {m['config']['collection']}. Backend equivalence to other studies is unverified.\n\n",
        'The manipulation is a fictional 10-second versus 180-second student deadline. No actual per-decision model token budget, runtime or experienced pressure is measured. Conditions are generated independently without earlier answers. Whole trajectories still expose the generator to future demand and all roles; decentralized information use is not verified. No human observations, independent-student tests or inferential p-values are reported.\n\n',
        '## H1 / H2 / H3\n\n',markdown(tables['hypotheses'].drop(columns=['p_value','ci_lower','ci_upper'],errors='ignore')),
        '\nH1 = (probe order with 8 dispatched cases minus order with 32) / 24, averaged across roles. It is not the original structural beta. H2 = full chain cost, including four practice and twelve automatic continuation weeks. H3 = mean of four role order/customer-demand sample-variance ratios during model weeks. Zero demand variance makes the ratio undefined. Contrasts use only matched chain/generation pairs; a predicted direction describes these outputs and does not confirm a human-time hypothesis.\n\n',
        '## How many orders changed?\n\n',markdown(tables['choice_changes']),
        '\nWithin-condition repeat changes are shown alongside deadline changes. Different orders alone do not prove a pressure mechanism. Repeat generations and rows within a response are dependent generated data, not new students.\n\n',
        '## Data quality\n\n',markdown(tables['quality']),
        '\nNo missing decisions are filled in, no order is clipped and no valid zero is removed. Automatic continuation holds each role at its own final submitted order and demand at its final value; these are scoring-rule actions, not new model decisions.\n\n',
        '## Provenance and completion\n\n',markdown(status),
        '\nExact prompts, raw responses, settings, plan and source snapshots are preserved in the run. Mechanical conversion of unambiguous rule-answer JSON types is allowed prospectively, with original and derived text retained. No incorrect answer or order is corrected.\n\n']
    for e in imports:
        if e['formatting_edits']:parts.append(f"- {e['task_id']}: {len(e['formatting_edits'])} rule value types converted; original reply and derivative retained.\n")
    if not complete:parts.append(f"\nNext prompt: [{task['task_id']}](../../prompts/{task['task_id']}.md).\n")
    for name in images:parts.append(f'\n![{name.replace("_"," ")}]({name}.png)\n')
    if images:parts.append('\n[Excel tables and replayed data](RESULTS.xlsx). All six figures are available as PNG/PDF.\n')
    parts.append('\n[Protocol and limitations](../../../../docs/DEADLINE_COHORT_PROTOCOL_20261018.md). The previous initial/revision study is preserved separately. No response replacement or sample extension based on outcomes is permitted.\n')
    (version/'REPORT.md').write_text(''.join(parts),encoding='utf-8')
    (version/'provenance.json').write_text(json.dumps(dict(inputs_sha256=evidence,imported_responses=len(imports),analysis_signature=signature,api_calls=0),indent=2),encoding='utf-8')
    (folder/'REPORT.md').write_text(f'# Deadline study\n\n[Open current report and figures](analysis/{signature}/REPORT.md).\n',encoding='utf-8')
    (folder/'PROMPTS.md').write_text('# Fresh-chat collection sequence\n\nOne complete box per fresh chat. Return the full JSON. Do not attach other answers.\n\n'+''.join(f"- [{'saved' if r.accepted else 'pending'}: {r.task_id}](prompts/{r.task_id}.md)\n" for r in status.itertuples()),encoding='utf-8')
    pointer=dict(run=str(run.resolve()),report=str((version/'REPORT.md').resolve()),collection=m['config']['collection'],complete=complete)
    if not m['config']['synthetic']:
        name='LATEST_DEADLINE_COHORT_REPORT.json' if m['config']['collection']=='chat_ui' else 'LATEST_DEADLINE_PILOT_REPORT.json'
        (folder.parent/name).write_text(json.dumps(pointer,indent=2),encoding='utf-8')
    return dict(folder=version,report=version/'REPORT.md',tables=tables,rounds=rounds,probes=probes,complete=complete,images=images)
