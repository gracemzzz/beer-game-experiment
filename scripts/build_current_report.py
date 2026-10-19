"""Publish the completed sample against the user's H1-H4; no new model calls."""
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study.deadline_cohort import audit, load_accepted, read, save_new
from beergame_study.game import ROLES
from beergame_study.hypothesis_alignment import (
    STUDY, ANALYSIS, HYPOTHESES, FIGURES, assess, make_alignment_figures, source_folder, publish_current)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    run = ROOT / 'data/runs' / STUDY
    audit(run)
    raw_hashes = {p.relative_to(run).as_posix(): digest(p.read_bytes()) for p in run.rglob('*') if p.is_file()}
    source = source_folder(ROOT)
    assert read(source/'provenance.json')['inputs_sha256'] == raw_hashes
    old = ROOT / 'reports/archive/hypothesis_alignment_20261018' / STUDY / 'final'
    target = ROOT / 'reports/CURRENT_BEER_GAME'
    target.mkdir(parents=True, exist_ok=True)
    if (target/'results/provenance.json').exists():
        from beergame_study.hypothesis_alignment import build_report
        result = build_report(run)
        print('Verified existing current report:', result['report'])
        return
    files = {}
    sources = {}

    def put(name, content):
        raw = content.encode('utf-8') if isinstance(content, str) else content
        save_new(target/name, raw)
        files[name] = digest(raw)

    def copy(name, path):
        raw = path.read_bytes()
        put(name, raw)
        sources[path.relative_to(ROOT).as_posix()] = digest(raw)

    names = ['batches','chains','roles','contrasts','repeat_variation','choice_changes','quality','probes','rounds']
    tables = {name: pd.read_csv(source/(name+'.csv'), dtype={'generation': str} if name=='choice_changes' else None) for name in names}
    for name in names:
        copy('results/'+name+'.csv', source/(name+'.csv'))
    tables['hypotheses'] = assess(tables['chains'])
    put('results/hypotheses.csv', tables['hypotheses'].to_csv(index=False))
    workbook = io.BytesIO()
    with pd.ExcelWriter(workbook, engine='openpyxl') as writer:
        for name in ['hypotheses'] + names:
            tables[name].to_excel(writer, sheet_name=name, index=False)
    put('results/RESULTS.xlsx', workbook.getvalue())
    for name in ['weekly_orders.csv','task_provenance.csv']:
        copy('results/'+name, old/'results'/name)
    copy('EXACT_PROMPTS.md', old/'EXACT_PROMPTS.md')

    # Independently verify every prompt box and all 40,000 extracted decisions.
    plan = read(run/'plan.json')
    boxes = re.findall(r'```text\n(.*?)```', (target/'EXACT_PROMPTS.md').read_text(encoding='utf-8'), flags=re.S)
    expected = []
    assert len(boxes) == len(plan['tasks']) == 20
    for text, task in zip(boxes, plan['tasks']):
        entry = load_accepted(run, task['task_id'])
        assert digest(text.encode('utf-8')) == entry['prompt_sha256']
        for chain in entry['payload']['chains']:
            for week, orders in enumerate(chain['orders'], start=5):
                for role, order in zip(ROLES, orders):
                    expected.append(dict(task_id=task['task_id'], chain_id=chain['chain_id'], week=week, role=role, order=order))
    keys = ['task_id','chain_id','week','role']
    orders = pd.read_csv(target/'results/weekly_orders.csv')
    pd.testing.assert_frame_equal(orders.set_index(keys)[['order']].sort_index(), pd.DataFrame(expected).set_index(keys).sort_index())
    assert tables['hypotheses'].loc[2:, ['brief_mean','ample_mean','available_proxy_difference']].isna().all().all()

    make_alignment_figures(target/'plots', tables['chains'], tables['contrasts'], tables['repeat_variation'])
    for name in ['hypothesis_coverage','deadline_outcomes','deadline_vs_repeat']:
        for ext in ['png','pdf']:
            path = target/'plots'/(name+'.'+ext)
            files[path.relative_to(target).as_posix()] = digest(path.read_bytes())
    for name in ['cost_phases','example_chain','bullwhip_by_role']:
        for ext in ['png','pdf']:
            copy('plots/'+name+'.'+ext, source/(name+'.'+ext))

    report = '''# Beer Game report: your four hypotheses

**Completed data:** 20 replies, 500 fictional student identities, 125 teams and 40,000 weekly orders. Recorded setting: user-reported GPT-6 / Pro.

**Main conclusion:** the existing sample gives exploratory information for H1 and H2. It cannot test H3 or H4 because no causal-education or matched-control-lecture groups were collected. A new experiment is needed to test all four hypotheses as written.

## The four hypotheses

'''
    report += '\n\n'.join('**'+h+'.** '+text for h,text in HYPOTHESES.items())
    report += '''

## What the existing results say

| Hypothesis | Available evidence | Conclusion |
| --- | --- | --- |
| H1 | Pipeline sensitivity: 0.5800 in the 10-second scenario versus 0.8017 in the 180-second scenario; difference -0.2217 | Consistent with relatively less response to outstanding orders, using a proxy. The binding-time hypothesis is not established. |
| H2 | Mean full team cost: 1,038.968 versus 1,071.472; difference -32.504 | Opposite the predicted cost increase in this sample. The binding-time hypothesis is not established. |
| H3 | No education or matched-control lecture groups | Not tested. No effect estimate is available. |
| H4 | No education or matched-control lecture groups | Not tested. No effect estimate is available. |

For H1, the proxy is `(order with 8 dispatched cases - order with 32)/24`, averaged across roles. It measures response sensitivity; it does not estimate the original structural coefficient or establish an optimal benchmark for underweighting. The H1 proxy difference is negative in both generations (-0.2733 and -0.1700). H2 cost differences are also negative in both (-8.448 and -56.560).

The environment shared all four inventories while other roles' orders/backlogs remained hidden. The model generated whole trajectories with access to the full demand paths; genuine role-level information isolation was not verified. The prompt's 10/180-second deadlines were neither enforced nor timed. Therefore the sample cannot establish the effect of a **binding** decision-time constraint.

The four hypotheses were supplied after these data had been collected and reviewed. This is a transparent post-collection assessment, not a claim that education contrasts were planned or observed. The previous bullwhip outcome is now supplementary; it is not the new H3 or H4.

## Cost and repeat checks

H2 counts holding costs at $0.50 and backlog costs at $1 per case-week, including four practice, 20 model and 12 automatic continuation weeks. The mean cost difference is -0.698 during model weeks and -31.806 during automatic continuation: about 98% of the total difference comes from the scoring continuation.

Changing deadline scenarios changed 49.78% of paired orders. Repeating the same scenario changed 47.09% under 10 seconds and 51.87% under 180 seconds. Ordinary generation variation is substantial. These rows and repeated identities are not independent human students; no student-level p-values are reported.

The separately stored Claude API experiment compared an initial choice with an extra revision opportunity. It also showed lower pipeline sensitivity; cost results were inconclusive. It included no education/control lecture comparison and does not supply the missing H3/H4 data. Its outcomes are not pooled with this website sample.

## Do you need to rerun?

**To describe the existing sample: no. To test all four hypotheses as written: yes.** More replies to the old prompts cannot create an education treatment or validate binding time.

A minimal new design has three groups, all with the same specified information sharing:

| Group | Decision time | Instruction/lecture |
| --- | --- | --- |
| A | Adequate | Standard game instructions + matched control lecture |
| B | Binding | Standard game instructions + matched control lecture |
| C | Binding | Standard game instructions + causal education |

Compare B with A for H1/H2, and C with B for H3/H4. Randomize at the chain level, match lecture length/format, freeze the sample and demand paths before outcomes, and verify that the time constraint actually binds. For LLM work, a calibrated computation restriction is an explicitly model-specific intervention; a typed deadline alone is insufficient. Claims about real students require human validation.

## Plots

'''
    for i,(name,title,caption) in enumerate(FIGURES, start=1):
        report += f'### {i}. {title}\n\n{caption}\n\n![{title}](plots/{name}.png)\n\n[PDF](plots/{name}.pdf).\n\n'
    report += '[Exact prompts](EXACT_PROMPTS.md) · [Results and column guide](results/README.md) · [Excel](results/RESULTS.xlsx).\n'
    put('REPORT.md', report)
    put('README.md', '''# Current Beer Game report

This is the **one current reader-facing report**. Superseded reports are archived.

| What to open | File |
| --- | --- |
| Report for your H1-H4, with six plots | [REPORT.md](REPORT.md) |
| All 20 exact prompts | [EXACT_PROMPTS.md](EXACT_PROMPTS.md) |
| Excel results | [RESULTS.xlsx](results/RESULTS.xlsx) |
| Only the 40,000 submitted orders | [weekly_orders.csv](results/weekly_orders.csv) |
| Column meanings and evidence limitations | [Results guide](results/README.md) |

**Finding:** H1 has a descriptive proxy pattern in its predicted direction. H2's observed costs point the other way. H3/H4 were not tested: education and matched-control lecture groups are absent. Binding decision time was not enforced in this sample.

Read the report for the exact hypotheses and the three-group rerun needed to test them. The data, prompts and original decisions were preserved; this update adds no model calls. The H1-H4 assessment was made after collection. The six plots are available as PNG and PDF in `plots/`. Download `Beer_Game_H1_H4.zip` from this folder to share the complete package.
''')
    put('results/README.md', '''# Results for the H1-H4 assessment

Start with [RESULTS.xlsx](RESULTS.xlsx), or [weekly_orders.csv](weekly_orders.csv) for the 40,000 model orders. The workbook has ten sheets. Its `hypotheses` sheet now contains the four user-specified hypotheses, not the earlier three-outcome labels.

| File/sheet | Meaning |
| --- | --- |
| `hypotheses` | Four exact hypotheses, available proxy means, missing design elements and assessment. H3/H4 estimates are blank because the groups do not exist. |
| `chains`, `roles` | 500 team-condition/round outcomes and 2,000 role trajectories; repeated identities are not additional people. |
| `batches`, `contrasts` | Ten batch comparisons and 250 matched team/round comparisons. |
| `repeat_variation`, `choice_changes` | Same-deadline repeats and order changes. |
| `probes` | 2,000 order pairs underlying the H1 sensitivity proxy. |
| `quality` | Four condition/round summaries. |
| `rounds` | 72,000 Python-replayed states, including practice and automatic continuation. |
| `weekly_orders.csv` | Model weeks 5-24 only; excludes practice and continuation orders. |
| `task_provenance.csv` | Twenty task IDs, reported model/mode and prompt/response hashes. |

`brief` means the fictional 10-second scenario and `ample` the 180-second scenario. `generation` is round 1 or 2. A team has retailer, wholesaler, distributor and factory roles. `fictional_student_id` is an export label formed from team + role, not a real student record.

Sensitivity is `(probe order with 8 dispatched cases - order with 32)/24`. Lower sensitivity is only a proxy consistent with relatively less response to the supply line; it is not an identified structural underweighting coefficient. `cost` includes all scoring phases; `model_cost` and `automatic_cost` distinguish them. Inventory/backlog/shipment states were computed by Python.

`bullwhip` and `bullwhip_difference` are preserved supplementary outcome columns. **They do not measure the new education hypotheses H3 or H4.** Deadline differences are brief minus ample. Repeat differences are round 1 minus round 2. No education/control assignment or verified binding-time variable exists in the source data.

The nine accounting/decision CSVs retain their source values. The hypothesis assessment and workbook were republished for the new framework. [Provenance](provenance.json) records the unchanged raw evidence and the post-collection reporting update.
''')
    for path in [ROOT/'src/beergame_study/hypothesis_alignment.py', Path(__file__)]:
        sources[path.relative_to(ROOT).as_posix()] = digest(path.read_bytes())
    meta = dict(package_version=2, hypothesis_framework='user-H1-H4-post-collection-v1',
        statement_timing='Supplied after collection/results review; not retroactive preregistration',
        study_id=STUDY, analysis_signature=ANALYSIS, accepted_responses=20, fictional_identities=500,
        model_orders=40000, verified_binding_time=False, education_groups_observed=False,
        raw_run_inputs_sha256=raw_hashes, source_artifacts_sha256=sources,
        packaged_files_sha256=files.copy(), api_calls=0)
    put('results/provenance.json', json.dumps(meta, indent=2, allow_nan=False)+'\n')
    for path in target.rglob('*.md'):
        text = re.sub(r'```.*?```','',path.read_text(encoding='utf-8'),flags=re.S)
        for link in re.findall(r'\]\(([^)]+)\)',text):
            assert (path.parent/link).exists(), (path,link)
    zipped = io.BytesIO()
    with zipfile.ZipFile(zipped,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):
            info=zipfile.ZipInfo('Beer_Game_H1_H4/'+name,(2026,10,18,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(target/name).read_bytes())
    put('Beer_Game_H1_H4.zip',zipped.getvalue())
    with zipfile.ZipFile(io.BytesIO(zipped.getvalue())) as z:
        assert z.testzip() is None
        for name in z.namelist():
            rel=name.split('/',1)[1];assert digest(z.read(name))==files[rel]
    publish_current(ROOT)
    audit(run)
    assert raw_hashes == {p.relative_to(run).as_posix():digest(p.read_bytes()) for p in run.rglob('*') if p.is_file()}
    print('Current report:',target/'REPORT.md')
    print('H1-H4 rows:',len(tables['hypotheses']),'; H3/H4 estimates absent; exact prompts: 20; raw orders checked:',len(expected))


if __name__ == '__main__':
    main()
