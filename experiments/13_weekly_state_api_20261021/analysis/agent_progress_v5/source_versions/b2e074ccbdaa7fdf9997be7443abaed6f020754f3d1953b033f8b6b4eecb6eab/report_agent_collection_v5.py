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
    evidence_id=hashlib.sha256(json.dumps(dict(observations=evidence,report_source_sha256=report_source_sha256,
        timebox=state.get('timebox'),stopping=state.get('stopping')),sort_keys=True).encode()).hexdigest()[:16]
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
    # Retain original reporting prefixes plus the user's time-cutoff sample.
    # Prefix length is determined by completed attempts, never effect size.
    cutoff_sizes={sum(r['model']==m and r['complete'] for r in state['runs']) for m in state['models']}
    for prefix in sorted({1,2,5,10}|({n for n in cutoff_sizes if n>0} if state.get('timebox') else set())):
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
    write_csv(state['estimates'],OUT/'current_context_inference.csv')
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
    final_stage=state.get('stopping')
    stopped=bool(final_stage) and all(sum(r['model']==m and not r['review'].startswith('Excluded:')
        for r in completed)>=final_stage['complete_nonexcluded_contexts_per_model'] for m in state['models'])
    collection_text=(('Collection stopped after three complete non-excluded contexts per GPT model. No further rounds will run.'
        if stopped else 'Final round still collecting; stop after three complete non-excluded contexts per GPT model. No additional contexts will start.')
        if final_stage else (f'User time cap: collection stops {state["timebox"]["collection_cutoff_local"]}; '
        f'report deadline {state["timebox"]["delivery_deadline_local"]}. The ten-run target is superseded.'
        if state.get('timebox') else 'Collection target: 10 attempted fresh contexts per GPT model.'))
    conclusion_rows=[]
    for name,metric,plus,minus,direction in ENDPOINTS:
        reviewed_effects=[e['difference'] for e in effects if e['hypothesis']==name and e['eligible'] and e['difference'] is not None]
        estimates=[e for e in state['estimates'] if e['hypothesis']==name and e['reviewed_contexts'] and e['mean_difference'] is not None]
        supported=[e for e in estimates if e.get('p_holm_20') is not None and e['p_holm_20']<.05 and e['mean_difference']*direction>0]
        if not reviewed_effects:
            observation='No reviewed observations yet.'
        elif all(abs(v)<1e-10 for v in reviewed_effects):
            observation='No observed difference in any reviewed context.'
        else:
            signs={1 if e['mean_difference']*direction>1e-10 else -1 if e['mean_difference']*direction < -1e-10 else 0 for e in estimates}
            observation=('Model means point in opposite directions.' if 1 in signs and -1 in signs else
                'Observed model means point in the predicted direction.' if signs=={1} else
                'Observed means include zero or opposite-direction effects.')
        values='; '.join(f'{MODEL_LABELS[e["model"]]} {e["mean_difference"]:+.4g} (n={e["reviewed_contexts"]})' for e in estimates)
        conclusion_rows.append(dict(hypothesis=name,observation=observation,reviewed_model_means=values,
            conclusion=('Supported in this AI analogue for '+', '.join(MODEL_LABELS[e['model']] for e in supported)) if supported else 'Not statistically established'))
    write_csv(conclusion_rows,OUT/'hypothesis_conclusions.csv')
    descriptions={'H1':'Constraint increases underweighting','H2':'Constraint increases holding + backlog costs',
        'H3':'Education reduces underweighting','H4a':'Education reduces individual order variance','H4b':'Education reduces bullwhip ratio'}
    lines=['# Agent Beer Game results (v5)','',
        f'1. **{len(completed)} complete agent contexts received; {sum(r["eligible"] for r in completed)} have passed the recorded procedure review.** '+collection_text,
        '2. **H1:** '+next(r['observation'] for r in conclusion_rows if r['hypothesis']=='H1')+' **H3:** '+next(r['observation'] for r in conclusion_rows if r['hypothesis']=='H3')+' Neither hypothesis is statistically established.',
        '3. **H2:** '+next(r['observation'] for r in conclusion_rows if r['hypothesis']=='H2')+' A reliable cost increase is not established.',
        '4. **H4a and H4b:** Education effects vary across models and contexts. Neither reduction is statistically established.',
        '5. **Three rounds are a pilot, not a significance result.** With three independent contexts, the smallest possible two-sided exact sign-flip p-value is 0.25, before adjustment. No further data will be collected under the current stopping instruction.','',
        '## Conclusions for each hypothesis','',
        '| Hypothesis | Reviewed results | Conclusion |','|---|---|---|']
    for row in conclusion_rows:
        lines.append(f'| {row["hypothesis"]}: {descriptions[row["hypothesis"]]} | {row["observation"]} {row["reviewed_model_means"]} | **{row["conclusion"]}** |')
    lines += ['','Here n is reviewed fresh contexts, not chains. Values are condition differences: H1/H2 = B−A; H3/H4 = C−B. H1/H3 use outstanding-order sensitivity as a proxy for underweighting. A zero contrast means no treatment difference in this measurement; it does not prove that students are unaffected. The absence of statistical support does not disprove H1–H4.','',
        'Absolute sensitivity helps explain the zero H1/H3 contrasts. The table below averages each arm over reviewed contexts. Identical sensitivity across arms leaves no measured effect for the constraint or education. These probe slopes do not establish normative underweighting or validate student behavior.','',
        '| Model | A: control + revision | B: control, one decision | C: education, one decision |','|---|---:|---:|---:|']
    sensitivity=[]
    for model in state['models']:
        row={'model':model}
        for arm in 'ABC':
            values=[r['pipeline_sensitivity'] for r in aggregates if r['model']==model and r['arm']==arm and r['adherence_review_passed']]
            row[arm]=sum(values)/len(values) if values else None
        sensitivity.append(row)
        lines.append('| '+' | '.join([MODEL_LABELS[model],*[fmt(row[a]) for a in 'ABC']])+' |')
    write_csv(sensitivity,OUT/'absolute_pipeline_sensitivity.csv')
    lines += ['',
        '## Collection status','',
        '| Model | Complete non-excluded contexts | Reviewed for inference | Complete excluded attempts |','|---|---:|---:|---:|']
    for model in state['models']:
        rows=[r for r in completed if r['model']==model]
        lines.append(f'| {MODEL_LABELS[model]} | {sum(not r["review"].startswith("Excluded:") for r in rows)}/3 | {sum(r["eligible"] for r in rows)} | {sum(r["review"].startswith("Excluded:") for r in rows)} |')
    lines += ['',
        '**Fifty chains inside one context are dependent.** Additional fresh contexts provide replication; increasing a within-context prefix does not create independent students.',
        '**This tests decision opportunities in fictional students.** It does not establish binding human clock pressure, normative underweighting, or real student behavior.','',
        '## Observed H1-H4 differences','',
        '| Requested model | Run | H1: B-A sensitivity | H2: B-A cost | H3: C-B sensitivity | H4a: C-B variance | H4b: C-B bullwhip | Review |',
        '|---|---|---:|---:|---:|---:|---:|---|']
    for r in completed:
        values={e['hypothesis']:e['difference'] for e in effects if e['model']==r['model'] and e['run']==r['run']}
        lines.append('| '+ ' | '.join([MODEL_LABELS.get(r['model'],r['model']),r['run'],*[fmt(values.get(n)) for n,*_ in ENDPOINTS],r['review']])+' |')
    if not completed:lines.append('| No complete three-condition contexts yet | | | | | | | Pending |')
    lines += ['','Expected directions are H1 negative, H2 positive, H3 positive, and H4a/b negative. A difference in that direction alone is not significance. H1/H3 use pipeline sensitivity as a proxy.','',
        '## Open these files','',
        '- [Current presentation figures, PDF/SVG exports and short captions](slides_current/README.md).',
        '- [Short extracted hypothesis conclusions](hypothesis_conclusions.csv).',
        '- [Live notebook](../../notebooks/AGENT_PROGRESS.ipynb): run all cells and tick Auto-refresh (10 s).',
        '- [Per-context / condition results](context_arm_results.csv) and [per-chain extracted results](per_chain_results.csv).',
        '- [Current reviewed-context estimates, intervals and adjusted p-values](current_context_inference.csv). Missing p-values mean replication or review is insufficient.',
        '- [Within-context size table](within_context_chain_prefixes.csv): first 5/10/20/30/40/50 chains, descriptive only.',
        '- [Fresh-context size table](observed_context_size_sweep.csv): original attempted prefixes 1/2/5/10 plus observed time-cutoff sizes; eligible counts and missingness remain explicit.',
        '- [H1-H4 versus chain-count plot and data](chain_size_stability/README.md): observed direction stability within contexts.',
        '- [Exact tasks, prompts, decisions and public trace reviews](../../data/assistant_v5_20261025/).']
    if effects:lines += ['','![Observed contrasts](DESCRIPTIVE_H1_H4.png)']
    lines += ['','## Collection and limits','',
        'Requested agent models are GPT-6 Astra, GPT-6.1 Sol and GPT-6 Luna, all high effort. Client model labels/settings are recorded separately from provider authentication. These agent observations are not pooled with manual website or historical API data. Claude is still a manual route.',
        '', 'A has a matched control reading plus a separate revision opportunity; B has the control reading and one committed decision; C has causal education and one decision. All three arms share a context, allowing carryover. Python computes state; the model supplies literal order pages. Full games replay before extraction. A code execution log does not by itself prove prompt adherence.',
        '', 'Procedure review covers visible prompts and tool interactions, complete public state exposure, and actual literal decisions. Encrypted parent-message bodies are covered only where exact operator-saved plaintext receipts exist; these are operator attestations, not decrypted or independently authenticated provider transcripts. Missing receipts remain explicit review gaps. This review does not validate student fidelity or clock pressure. Deviating attempts are preserved and do not disappear from the attempted sample.',
        '', 'When eligible replication exists, the exploratory tests use paired context differences, two-sided sign flips and pointwise bootstrap intervals. The Holm family retains all 20 model-by-endpoint tests, including missing Claude tests. These assumptions do not make model contexts equivalent to real human samples. Repeated live looks are not a stopping rule.',
        '', 'No new direct API calls are made by this monitor, analysis or local transport. The shared API ledger is unchanged; agent-service usage is separate.',
        '',f'Report generated UTC: {datetime.now(timezone.utc).isoformat()}. Evidence ID: `{evidence_id}`. Earlier current-report bytes are preserved in `history/` before changed evidence is published.']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (OUT/'RESULTS.json').write_text(json.dumps(dict(evidence_id=evidence_id,evidence=evidence,completed_contexts=len(completed),
        reviewed_contexts=sum(r['eligible'] for r in completed),contrasts=effects,source_kind='local_assistant_agents',
        report_source_sha256=report_source_sha256,timebox=state.get('timebox'),stopping=state.get('stopping'),
        collection_stopped=stopped,hypothesis_conclusions=conclusion_rows),indent=2,allow_nan=False),encoding='utf-8')
    print(OUT/'REPORT.md')


if __name__=='__main__':main()
