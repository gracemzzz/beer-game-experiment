"""Notebook rendering only; no model requests and no scientific settings."""
import html
import json
from pathlib import Path


class NotebookProgress:
    def __init__(self):
        from IPython.display import HTML, display
        self._HTML = HTML
        self._display = display
        self._handle = None

    def __call__(self, state):
        overall_done = int(state.get('completed_steps', state.get('requests_done', 0)))
        overall_total = max(1, int(state.get('planned_requests', 1)))
        stage = str(state.get('stage', 'waiting'))
        if stage.startswith('calibration'):
            done = int(state.get('calibration_completed', 0))
            total = max(1, int(state.get('calibration_expected', 144)))
            bar_label = 'calibration decisions'
        elif stage == 'onboarding':
            done = int(state.get('onboarding_completed', 0))
            total = max(1, int(state.get('planned_groups', 0))*4)
            bar_label = 'rules checks'
        else:
            done, total = overall_done, overall_total
            bar_label = 'overall planned steps'
        label = html.escape(str(state.get('stage', 'waiting')).replace('_', ' '))
        phase = html.escape(str(state.get('phase', 'running')))
        cost = float(state.get('estimated_charged_or_reserved_usd', 0))
        budget = float(state.get('budget_usd', 0))
        directory = html.escape(str(state.get('run_directory', '')))
        reason = html.escape(str(state.get('reason', '')))
        progress_note = ('the game bar advances when all roles finish a week'
                         if stage == 'games' else 'the bar advances when the batch finishes')
        content = (
            f'<div style="border:1px solid #ccc;padding:14px;border-radius:8px">'
            f'<b>{label}</b> — {phase}<br>'
            f'<progress value="{min(done, total)}" max="{total}" style="width:100%;height:24px"></progress>'
            f'<div>{done:,} / {total:,} {bar_label} · '
            f'API attempts/cache reads: {state.get("requests_done", 0):,} · '
            f'Cached: {state.get("cached_requests", 0):,}</div>'
            f'<small>Overall plan: {overall_done:,} / {overall_total:,} steps; '
            f'game count is finalized after calibration.</small>'
            f'<div>Requests currently processing: {state.get("active_requests", 0)} '
            f'({progress_note})</div>'
            f'<div>Calibration: {state.get("calibration_completed", 0)} / '
            f'{state.get("calibration_expected", 144)} · '
            f'Game week: {state.get("current_week", 0)} · '
            f'Completed chains: {state.get("groups_complete", 0)} / {state.get("planned_groups", 0)}</div>'
            f'<div>Charged/reserved: <b>${cost:.3f} / ${budget:.2f}</b> · '
            f'Flagged fallback orders: {state.get("fallback_decisions", 0)}</div>'
            f'<small>{directory}<br>{html.escape(str(state.get("updated_utc", "")))}</small>'
            f'<div>{reason}</div></div>')
        if self._handle is None:
            self._handle = self._display(self._HTML(content), display_id=True)
        else:
            self._handle.update(self._HTML(content))


async def watch_progress(root, interval_s=2):
    """Watch the last active CLI/notebook run; interrupt the cell to stop watching."""
    import asyncio
    renderer = NotebookProgress()
    root = Path(root)
    while True:
        pointer = root/'reports/ACTIVE_STUDENT_RUN.json'
        if not pointer.exists():
            print('No student run has started yet.')
            return
        active = json.loads(pointer.read_text(encoding='utf-8'))
        state = json.loads(Path(active['progress']).read_text(encoding='utf-8'))
        renderer(state)
        if state.get('phase') in ('complete', 'stopped'):
            return state
        await asyncio.sleep(interval_s)
