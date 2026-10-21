"""Build human navigation for the organized historical experiments; no API calls."""
from __future__ import annotations
import json
from pathlib import Path
from reorganize_experiments import EXPERIMENTS, ROOT

PRIMARY = {
 'early': 'data/pre_token_budget_20261004/README.md',
 'nano': 'reports/archive/20261005/pilot_02_game_api_8236a9c840b29d36/Pilot_Report.docx',
 'budget': 'reports/archive/20261005/budget_followup_20261005/Budget_Followup_Report.docx',
 'student': 'reports/archive/studies/student_pilot_20261011/REPORT.md',
 'anytime': 'reports/archive/studies/anytime_api_206b831bd7eab63e/REPORT.md',
 'economy': 'reports/archive/studies/economy_api_a80275c58f2c07e0/FINDINGS.md',
 'claude': 'reports/archive/studies/claude_api_fd5533fef5828d96/FINDINGS.md',
 'manual': 'reports/archive/studies/manual_cohort_975b76e63e5b4882/FINDINGS.md',
 'pressure': 'reports/archive/studies/pressure_prompt_development_20261018/FINDINGS.md',
 'deadline': 'reports/current/REPORT.md',
 'education': 'reports/website_astra_extra_high/REPORT.md',
}
SECTIONS = {
 'hypotheses': 'The hypotheses, protocol, design notes and settings amendments.',
 'prompts': 'Exact instructions and where to find the saved request payloads.',
 'data': 'Raw responses, attempts, run settings, manifests and frozen source snapshots.',
 'analysis': 'Analysis versions, validation receipts and software checks.',
 'reports': 'Human-readable reports, figures, numerical tables and original publication packages.',
 'notebooks': 'A safe saved-results notebook and the preserved original notebooks.',
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def model_records(base):
    records=[]
    for p in sorted((base/'data').rglob('manifest.json')):
        if 'source_implementation' in p.parts or 'prepared_parent' in p.parts:
            continue
        try:
            data=json.loads(p.read_text(encoding='utf-8'))
        except (ValueError, UnicodeError):
            continue
        cfg=data.get('config', data)
        if not isinstance(cfg, dict):
            continue
        records.append(dict(run=p.parent.name, manifest=p.relative_to(base).as_posix(),
            protocol=data.get('protocol', data.get('protocol_version')),
            model=cfg.get('model', cfg.get('model_label')),
            effort=cfg.get('reasoning_effort', cfg.get('effort_label', cfg.get('effort'))),
            mode=cfg.get('mode', cfg.get('collection')),
            settings_are_literal_saved_labels=True))
    return records


def notebook(identifier, title):
    md='# '+title+' — saved results\n\nRun the cells in order. They read saved files and make no API calls. Historical original notebooks remain alongside this review notebook; their old paths require the compatibility workspace.'
    code='''from pathlib import Path
import json
from IPython.display import display, Markdown, FileLink
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / "maintenance/reorganization_20261020/FILE_MAP.json").is_file())
EXPERIMENT = ROOT / "experiments" / IDENTIFIER
settings = json.loads((EXPERIMENT / "EXPERIMENT.json").read_text())
display(Markdown("## " + settings["title"]))
print(settings["model_and_design"])
display(FileLink(str(EXPERIMENT / settings["primary_report"])))
display(FileLink(str(EXPERIMENT / "README.md")))
'''.replace('IDENTIFIER',repr(identifier))
    table='''records = settings["saved_runs"]
try:
    import pandas as pd
    display(pd.DataFrame(records))
except ImportError:
    for record in records:
        print(record)
print("Raw data:", EXPERIMENT / "data")
print("Exact prompt guide:", EXPERIMENT / "prompts/README.md")
print("Analysis guide:", EXPERIMENT / "analysis/README.md")
'''
    def cell(kind, text):
        result=dict(cell_type=kind, metadata={}, source=text.splitlines(keepends=True))
        if kind=='code': result.update(execution_count=None,outputs=[])
        return result
    cells=[cell('markdown',md),cell('code',code),cell('code',table)]
    for index,entry in enumerate(cells):
        entry['id']='saved-review-'+str(index)
    return dict(nbformat=4,nbformat_minor=5,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3'}},
                cells=cells)


def build(root=ROOT):
    root=Path(root)
    catalog=[]
    for key,(identifier,title,description) in EXPERIMENTS.items():
        base=root/'experiments'/identifier
        for section in SECTIONS:
            (base/section).mkdir(parents=True,exist_ok=True)
        primary=PRIMARY[key]
        if not (base/primary).exists(): raise AssertionError('Missing main report: '+str(base/primary))
        settings=dict(experiment_id=identifier,title=title,model_and_design=description,
            status='historical; preserve the saved completed, stopped and software-only runs separately',
            primary_report=primary,saved_runs=model_records(base),
            evidence_policy='Original file bytes retained. New navigation is separate from frozen evidence.',
            original_checkout_integrity='Preexisting LF/CRLF discrepancies are documented in maintenance/reorganization_20261020.')
        write(base/'EXPERIMENT.json',json.dumps(settings,indent=2)+'\n')
        notebook_path='notebooks/review_saved_results.ipynb'
        write(base/notebook_path,json.dumps(notebook(identifier,title),indent=2)+'\n')
        lines=[f'# {title}', '', description+'.', '',
               f'**Start here: [main report or historical overview]({primary}).**', '',
               f'[Open the saved-results notebook]({notebook_path}) · [Model and run settings](EXPERIMENT.json)', '',
               '| What you need | Where |','| --- | --- |']
        for section,meaning in SECTIONS.items():
            lines.append(f'| {meaning} | [{section}/]({section}/README.md) |')
        lines += ['', 'Each raw run keeps its original fingerprint and internal file arrangement. Completed samples, failed attempts, preparations and software checks remain distinct; this folder does not pool them.', '',
                  'Original report packages keep their exact bytes. Internal links within a package still work; historical links to the former repository layout can require the [compatibility copy](../../maintenance/README.md). The original notebooks are preserved; use the review notebook above for ordinary reading.', '',
                  '[All experiments](../README.md) · [Repository guide](../../README.md)', '']
        write(base/'README.md','\n'.join(lines))
        for section,meaning in SECTIONS.items():
            folder=base/section
            entries=[p for p in sorted(folder.iterdir()) if p.name!='README.md']
            text=[f'# {title}: {section}', '', meaning, '', '[Experiment overview](../README.md)', '']
            if section=='prompts':
                paths=sorted(set(list((base/'data').rglob('prompts'))+list((base/'reports').rglob('EXACT_PROMPTS.md'))+
                    list((base/'reports').rglob('*API_PROMPTS.md'))+list((base/'data').rglob('requests'))))
                if key=='pressure': paths+=sorted((base/'data/development/pressure_prompt_development_20261018').glob('*BRIEF.md'))+sorted((base/'data/development/pressure_prompt_development_20261018').glob('*AMPLE.md'))
                text += ['Exact prompts remain inside each immutable run or request bundle. API request JSON stores the actual messages sent to the model. A notebook is not the sole record of the prompt.', '']
                for p in paths[:40]:
                    rel=p.relative_to(base).as_posix();text.append(f'- [{rel}](../{rel})')
                if len(paths)>40:text.append('- Additional archived requests are in [data/](../data/README.md).')
            if section=='analysis':
                paths=sorted(set(list((base/'reports').rglob('results'))+list((base/'reports').rglob('analysis'))+
                    [p.parent for p in (base/'data').rglob('beta_fits.csv')]))
                if paths:text+=['Canonical tables and analyses retained within their original bundles:', '']
                for p in paths[:30]:
                    rel=p.relative_to(base).as_posix();text.append(f'- [{rel}](../{rel})')
                text+=['','Shared analysis and audit implementations are in [scripts/](../../../scripts/) and [src/](../../../src/). Use the [legacy workspace](../../../maintenance/README.md) for frozen historical checks.']
            if section=='notebooks':
                text+=['**Use [review_saved_results.ipynb](review_saved_results.ipynb) to inspect the organized files.** Other notebooks retain their original code and old paths for provenance; execute them only inside a reconstructed historical workspace. Reviewing this folder does not authorize historical paid reruns.', '']
            if section=='data':
                text+=['Read each `manifest.json` for the exact model, protocol and settings. `api`, `offline`, prepared and accepted collections must remain distinct. The education study’s prepared parent remains 0/6; its received Astra collection is separately complete at 6/6.', ''] if key=='education' else ['Run names distinguish API evidence, software checks and separate preparations. Manifests record the exact protocol and settings; failed attempts are retained.', '']
            if not entries and section=='hypotheses':
                text+=['For this early/development study, the design is recorded in the [raw saved plans and manifests](../data/README.md) and [original report](../'+primary+').', '']
            if entries:text+=['Files and folders:', '']+[f'- [{p.name}{"/" if p.is_dir() else ""}]({p.name}{"/" if p.is_dir() else ""})' for p in entries]
            write(folder/'README.md','\n'.join(text)+'\n')
        catalog.append({k:settings[k] for k in ('experiment_id','title','model_and_design','primary_report')})
    write(root/'experiments/CATALOG.json',json.dumps(catalog,indent=2)+'\n')
    lines=['# Experiment index','','Each experiment has its own hypotheses, prompts, data, analysis, reports and notebooks. Shared code lives at the repository root.','','| Experiment | Model / design |','| --- | --- |']
    lines += [f'| [{item["title"]}]({item["experiment_id"]}/README.md) | {item["model_and_design"]} |' for item in catalog]
    lines+=['| [New pressure-framing API experiment](12_pressure_framing_api_20261020/README.md) | Four models; 80 fictional testers / 20 chains / 24 decision weeks per model; one joint response per model |','',
            'The historical folders preserve distinct protocols and evidence. The new experiment has its own sample and budget; historical samples are closed.', '', '[Repository guide](../README.md)', '']
    write(root/'experiments/README.md','\n'.join(lines))
    return catalog


if __name__=='__main__':
    print(json.dumps({'historical_experiment_folders':len(build()),'api_calls':0}))
