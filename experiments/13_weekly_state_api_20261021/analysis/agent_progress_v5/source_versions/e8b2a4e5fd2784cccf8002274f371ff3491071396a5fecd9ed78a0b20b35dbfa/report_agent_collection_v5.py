"""Offline report of actually completed local-agent contexts, kept separate from websites."""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from beergame_study.agent_progress_v5 import snapshot, MODEL_LABELS
from beergame_study import manual_batch_v5 as batch
from beergame_study import manual_batch_analysis_v5 as analysis
from beergame_study.pivot_inference_v2 import ENDPOINTS, paired_inference, holm_adjust
import pandas as pd
import matplotlib.pyplot as plt

EXP=ROOT/'experiments/13_weekly_state_api_20261021'
OUT=EXP/'reports/agent_collection_v5'


def write_csv(rows,path,columns=()):
    frame=pd.DataFrame(rows)
    if frame.empty and columns:
        frame=pd.DataFrame(columns=columns)
    frame.to_csv(path,index=False)
    return frame


def main():
    analysis.verify_manifest(EXP/'data/manual_batch_v5_614dfdfeb3f15acf')
    state=snapshot(ROOT)
    completed=[r for r in state['runs'] if r['complete'] and r['outcomes'] and not r['error']]
    evidence=[dict(model=r['model'],run=r['run'],result_sha256=r['result_sha256'],eligible=r['eligible'],review=r['review']) for r in completed]
    # New reporting definitions get a distinct publication fingerprint while
    # every original model response and frozen game protocol remains unchanged.
    report_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    evidence_id=hashlib.sha256(json.dumps(dict(observations=evidence,report_source_sha256=report_source_sha256),sort_keys=True).encode()).hexdigest()[:16]
    OUT.mkdir(parents=True,exist_ok=True)
    pointer=OUT/'RESULTS.json'
    if pointer.exists() and json.loads(pointer.read_text())['evidence_id']==evidence_id:
        print('Completed evidence unchanged; existing report preserved.')
        return
    analysis.preserve_previous_report(OUT,evidence_id)
    per_chain=[]
    aggregates=[]
    for r in completed:
        raw=json.loads((Path(r['path'])/'RESULT.json').read_bytes())
        for row in analysis.chain_metrics(raw):
            per_chain.append(dict(**row,run=r['run'],adherence_review_passed=r['eligible']))
        for row in r['outcomes']:
            extracted=dict(row)
            extracted['controller_inherited_provider_label']=extracted.pop('provider',None)
            extracted['controller_inherited_reasoning_setting']=extracted.pop('reasoning_setting',None)
            aggregates.append(dict(**extracted,run=r['run'],adherence_review_passed=r['eligible'],
                requested_client_model=r['requested_model'],requested_client_effort=r['requested_effort'],
                collection_source='local_assistant_agent',provider_api_identity_authenticated=False))
    write_csv(aggregates,OUT/'context_arm_results.csv',('model','run','arm','chain_total_cost','pipeline_sensitivity'))
    write_csv(per_chain,OUT/'per_chain_results.csv',('model','run','arm','chain_id'))
    prefixes=analysis.chain_prefix_summary(per_chain)
    prefixes.to_csv(OUT/'within_context_chain_prefixes.csv',index=False)
    if not prefixes.empty:
        analysis.plot_chain_prefixes(prefixes,OUT)

    # Fixed attempted-run prefixes, not the first k favorable or eligible runs.
    sweep=[]
    for prefix in (1,2,5,10):
        group=[]
        for model in state['models']:
            attempted=[r for r in state['runs'] if r['model']==model][:prefix]
            if len(attempted)!=prefix or not all(r['complete'] for r in attempted):
                continue
            eligible=[r for r in attempted if r['eligible'] and not r['error']]
            for name,metric,plus,minus,direction in ENDPOINTS:
                diffs=[]
                for r in eligible:
                    arms={a['arm']:a for a in r['outcomes']}
                    if arms[plus][metric] is not None and arms[minus][metric] is not None:
                        diffs.append(arms[plus][metric]-arms[minus][metric])
                if len(diffs)!=len(eligible):
                    continue
                stats=paired_inference(diffs) if len(diffs)>=2 else dict(mean_difference=diffs[0] if diffs else None,
                    ci95_low=None,ci95_high=None,p_two_sided=None,n_pairs=len(diffs))
                group.append(dict(model=model,hypothesis=name,attempted_context_prefix=prefix,
                    eligible_contexts=len(eligible),chains_per_condition=50*len(eligible),
                    contrast=plus+'-'+minus,expected_direction=direction,**stats))
        indexed={(r['model'],r['hypothesis']):r for r in group}
        family=[(m,e[0]) for m in batch.SLOTS for e in ENDPOINTS]
        adj=holm_adjust([indexed[k]['p_two_sided'] if k in indexed else None for k in family])
        for k,p in zip(family,adj):
            if k in indexed:indexed[k]['p_holm_20']=p
        sweep.extend(group)
    sweep_frame=write_csv(sweep,OUT/'observed_context_size_sweep.csv',('model','hypothesis','attempted_context_prefix','eligible_contexts','p_holm_20'))
    if not sweep_frame.empty and sweep_frame.p_holm_20.notna().any():
        analysis.plot_p_values(sweep_frame,OUT)

    # The first-run figure is descriptive and visibly distinct from inference.
    effects=[]
    for r in completed:
        arms={a['arm']:a for a in r['outcomes']}
        for name,metric,plus,minus,direction in ENDPOINTS:
            a,b=arms[plus][metric],arms[minus][metric]
            effects.append(dict(model=r['model'],run=r['run'],hypothesis=name,
                difference=a-b if a is not None and b is not None else None,review=r['review'],eligible=r['eligible']))
    write_csv(effects,OUT/'descriptive_context_contrasts.csv',('model','run','hypothesis','difference','eligible'))
    if effects:
        fig,axes=plt.subplots(2,3,figsize=(15,8))
        for ax,(name,*_) in zip(axes.flat,ENDPOINTS):
            rows=[r for r in effects if r['hypothesis']==name and r['difference'] is not None]
            ax.scatter([MODEL_LABELS.get(r['model'],r['model'])+' / '+r['run'] for r in rows],
                       [r['difference'] for r in rows],color='#2454ce')
            ax.axhline(0,color='grey',linestyle='--',linewidth=1)
            ax.set_title(name)
            ax.set_ylabel('Observed paired condition difference')
            ax.tick_params(axis='x',labelrotation=25)
        axes.flat[-1].axis('off')
        axes.flat[-1].text(0,.9,'One dot = one complete context\n\nDescriptive, not an independent\nstudent-level test.\n\nReview status is in the CSV/report.\nNo p-value is inferred from\nthe 50 dependent chains.',va='top',fontsize=12)
        fig.suptitle('Observed H1-H4 contrasts in completed agent contexts\nExploratory AI simulation; incomplete collection / adherence review')
        fig.tight_layout()
        analysis.save_figure(fig,OUT,'DESCRIPTIVE_H1_H4')

    def fmt(x): return 'pending' if x is None else f'{x:.4g}'
    lines=['# Agent Beer Game results (v5)','',
        f'1. **{len(completed)} complete agent contexts received; {sum(r["eligible"] for r in completed)} have passed the full adherence gate.** Collection target: 10 attempted fresh contexts per GPT model.',
        '2. **H1-H4 are not established by incomplete collection or a single context.** The table below contains observed differences only; null and opposite results are retained.',
        '3. **Fifty chains inside one context are dependent.** Additional fresh contexts provide replication; increasing a within-context prefix does not create independent students.',
        '4. **This tests decision opportunities in fictional students.** It does not establish binding human clock pressure, normative underweighting, or real student behavior.','',
        '## Observed H1-H4 differences','',
        '| Requested model | Run | H1: B-A sensitivity | H2: B-A cost | H3: C-B sensitivity | H4a: C-B variance | H4b: C-B bullwhip | Review |',
        '|---|---|---:|---:|---:|---:|---:|---|']
    for r in completed:
        values={e['hypothesis']:e['difference'] for e in effects if e['model']==r['model'] and e['run']==r['run']}
        lines.append('| '+ ' | '.join([MODEL_LABELS.get(r['model'],r['model']),r['run'],*[fmt(values.get(n)) for n,*_ in ENDPOINTS],r['review']])+' |')
    if not completed:lines.append('| No complete three-condition contexts yet | | | | | | | Pending |')
    lines += ['','Expected directions are H1 negative, H2 positive, H3 positive, and H4a/b negative. A difference in that direction alone is not significance. H1/H3 use pipeline sensitivity as a proxy.','',
        '## Open these files','',
        '- [Live notebook](../../notebooks/AGENT_PROGRESS.ipynb): run all cells and tick Auto-refresh (10 s).',
        '- [Per-context / condition results](context_arm_results.csv) and [per-chain extracted results](per_chain_results.csv).',
        '- [Within-context size table](within_context_chain_prefixes.csv): first 5/10/20/30/40/50 chains, descriptive only.',
        '- [Fresh-context size table](observed_context_size_sweep.csv): fixed attempted prefixes 1/2/5/10; eligible counts and missingness remain explicit.',
        '- [Exact tasks, prompts, decisions and public trace reviews](../../data/assistant_v5_20261025/).']
    if effects:lines += ['','![Observed contrasts](DESCRIPTIVE_H1_H4.png)']
    lines += ['','## Collection and limits','',
        'Requested agent models are GPT-6 Astra, GPT-6.1 Sol and GPT-6 Luna, all high effort. Client model labels/settings are recorded separately from provider authentication. These agent observations are not pooled with manual website or historical API data. Claude is still a manual route.',
        '', 'A has a matched control reading plus a separate revision opportunity; B has the control reading and one committed decision; C has causal education and one decision. All three arms share a context, allowing carryover. Python computes state; the model supplies literal order pages. Full games replay before extraction. A code execution log does not by itself prove prompt adherence.',
        '', 'Full adherence requires review of visible prompts and tool interactions, complete public state exposure, and actual literal decisions. Encrypted orchestration messages in local session records are recorded as provenance gaps, not silently reconstructed as authenticated transcripts. Deviating attempts are preserved and do not disappear from the attempted sample.',
        '', 'When eligible replication exists, the exploratory tests use paired context differences, two-sided sign flips and pointwise bootstrap intervals. The Holm family retains all 20 model-by-endpoint tests, including missing Claude tests. These assumptions do not make model contexts equivalent to real human samples. Repeated live looks are not a stopping rule.',
        '', 'No new direct API calls are made by this monitor, analysis or local transport. The shared API ledger is unchanged; agent-service usage is separate.',
        '',f'Report generated UTC: {datetime.now(timezone.utc).isoformat()}. Evidence ID: `{evidence_id}`. Earlier current-report bytes are preserved in `history/` before changed evidence is published.']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (OUT/'RESULTS.json').write_text(json.dumps(dict(evidence_id=evidence_id,evidence=evidence,completed_contexts=len(completed),
        reviewed_contexts=sum(r['eligible'] for r in completed),contrasts=effects,source_kind='local_assistant_agents',
        report_source_sha256=report_source_sha256),indent=2,allow_nan=False),encoding='utf-8')
    print(OUT/'REPORT.md')


if __name__=='__main__':main()
