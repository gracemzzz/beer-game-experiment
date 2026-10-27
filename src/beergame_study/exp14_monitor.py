"""Read-only experiment14 progress display; no widgets, agents or API calls."""
from pathlib import Path
import asyncio
from html import escape
import json


def snapshot(root):
    experiment=Path(root)/'experiments/14_deadline_student_20261026'
    rows=[]
    for stage in ['latency','feasibility','main']:
        for p in sorted((experiment/'data'/stage).glob('*/STATUS.json')):
            try:
                r=json.loads(p.read_text(encoding='utf-8'));r.update(stage=stage,name=p.parent.name)
                rows.append(r)
            except (OSError,ValueError):pass
    return rows


def render(root):
    rows=snapshot(root)
    pieces=['<div style="font-family:Arial;max-width:1100px"><h2>Experiment 14</h2>',
            '<p>GPT-6 Astra · extra high · read-only progress</p>']
    feasibility=[r for r in rows if r['stage']=='feasibility']
    if len(feasibility)==12 and all(r['complete'] or r['stopped'] for r in feasibility):
        pieces.append('<p><b>Development finished. Main study has not started.</b> '
                      'Both tested strict-deadline wordings failed the completion gate. '
                      '<a href="../reports/REPORT.pdf">Open the current PDF report</a>.</p>')
    for stage in ['latency','feasibility','main']:
        part=[r for r in rows if r['stage']==stage]
        target=30 if stage=='main' else len(part)
        pieces.append(f'<h3>{stage.title()}: {sum(r["complete"] for r in part)}/{target} complete</h3>')
        if not part:pieces.append('<p>No cases launched.</p>')
        for r in part:
            done=r['completed_weeks']+r['completed_probe_pages']+int(r['comprehension_complete'])
            total=r['planned_weeks']+r['planned_probe_pages']+1
            color='#B64A42' if r['stopped'] else '#2D7A58' if r['complete'] else '#245B8A'
            pieces.append(f'<p><b>{escape(r["name"])}</b> — {escape(r["phase"])} '
                f'({done}/{total} decisions)<br><progress value="{done}" max="{total}" style="width:75%;accent-color:{color}"></progress>'
                f'<br>{r["completed_weeks"]}/{r["planned_weeks"]} weeks · {r["completed_probe_pages"]}/{r["planned_probe_pages"]} probe pages'
                f'{" · "+escape(r["terminal_reason"]) if r.get("terminal_reason") else ""}</p>')
    pieces.append('<p>Each case is one chain in one fresh context. Main target: 10 paired blocks, 30 contexts. '
                  'Development stays separate; no order or missing response is filled in.</p></div>')
    return ''.join(pieces)


def notebook_monitor(root,seconds=10):
    from IPython.display import HTML,display
    handle=display(HTML(render(root)),display_id=True)
    state={'closed':False}
    def refresh():
        if not state['closed']:handle.update(HTML(render(root)))
    async def loop():
        while not state['closed']:
            await asyncio.sleep(seconds)
            refresh()
    task=asyncio.create_task(loop())
    def close():state['closed']=True;task.cancel()
    return {'refresh':refresh,'close':close,'state':state,'task':task}
