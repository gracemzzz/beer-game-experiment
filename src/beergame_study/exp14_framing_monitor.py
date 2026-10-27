"""Read-only progress for the current simulated-student pressure study."""
from pathlib import Path
from html import escape
import asyncio
import json


def snapshot(repository):
    base = Path(repository) / "experiments/14_deadline_student_20261026/data/student_framing_v3"
    rows = []
    for stage in ("development", "main"):
        for path in sorted((base / stage).glob("*/STATUS.json")):
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
                rows.append(dict(row, stage=stage, run=path.parent.name,
                                 launched=(path.parent / "ORCHESTRATOR_MESSAGES.jsonl").exists()))
            except (OSError, ValueError):
                pass
    return rows


def render(repository):
    rows = snapshot(repository)
    out = ['<div style="font-family:Arial;max-width:1050px"><h2>Experiment 14: simulated student pressure</h2>',
           '<p>GPT-6 Astra / extra high. Fictional student time: A 120 s; B/C 8 s. '
           '<b>No actual model timer or fallback.</b></p>']
    for stage, target in (("development", 3), ("main", 30)):
        selected = [r for r in rows if r["stage"] == stage]
        out.append(f'<h3>{stage.title()}: {sum(bool(r["complete"]) for r in selected)}/{target} contexts complete</h3>')
        if not selected:
            out.append('<p>No contexts prepared yet.</p>')
        for row in selected:
            value = row["completed_weeks"] + row["completed_probe_pages"] + int(row["comprehension_complete"])
            total = row["planned_weeks"] + row["planned_probe_pages"] + 1
            color = '#b64a42' if row["stopped"] else '#2d7a58' if row["complete"] else '#245b8a'
            phase = row["phase"] if row["launched"] else "queued; not launched"
            out.append(f'<p><b>{escape(row["run"])}</b>: {escape(phase)} '
                       f'({value}/{total})<br><progress max="{total}" value="{value}" '
                       f'style="width:80%;accent-color:{color}"></progress><br>'
                       f'{row["completed_weeks"]}/{row["planned_weeks"]} weeks; '
                       f'{row["completed_probe_pages"]}/{row["planned_probe_pages"]} probe pages</p>')
    out.append('<p>Ten matched main chain blocks; four roles per chain. Development is separate. '
               'This display reads saved files and launches no agents or API calls.</p></div>')
    return ''.join(out)


def notebook_monitor(repository, seconds=10):
    from IPython.display import HTML, display
    handle = display(HTML(render(repository)), display_id=True)
    state = {"closed": False}
    def refresh():
        if not state["closed"]:
            handle.update(HTML(render(repository)))
    async def loop():
        while not state["closed"]:
            await asyncio.sleep(seconds)
            refresh()
    task = asyncio.create_task(loop())
    def close():
        state["closed"] = True
        task.cancel()
    return dict(refresh=refresh, close=close, state=state, task=task)
