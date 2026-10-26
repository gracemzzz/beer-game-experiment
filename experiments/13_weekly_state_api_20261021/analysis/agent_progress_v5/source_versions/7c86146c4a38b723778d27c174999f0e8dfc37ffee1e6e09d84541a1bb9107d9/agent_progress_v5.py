"""Read-only live monitor for agent v5 collection; no model calls or decisions."""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from html import escape
import json
from pathlib import Path

from . import manual_batch_v5 as batch
from .pivot_inference_v2 import ENDPOINTS, holm_adjust, paired_inference

EXPERIMENT = Path('experiments/13_weekly_state_api_20261021')
COLLECTION = EXPERIMENT / 'data/assistant_v5_20261025'
MODEL_LABELS = {'gpt_astra': 'GPT-6 Astra', 'gpt_sol': 'GPT-6.1 Sol',
                'gpt_luna': 'GPT-6 Luna', 'claude_sonnet': 'Claude (manual, not started)'}
ENDPOINT_LABELS = {'H1': 'Pipeline sensitivity: B - A', 'H2': 'Total cost: B - A',
                   'H3': 'Pipeline sensitivity: C - B', 'H4a': 'Order variance: C - B',
                   'H4b': 'Bullwhip ratio: C - B'}


def read_json(path):
    # A writer may currently be replacing a checkpoint. Do not interpret a
    # truncated read as a failed experiment; the next refresh retries it.
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


@lru_cache(maxsize=256)
def audited_result(raw):
    return batch.audit(json.loads(raw))


def review_ok(folder, digest):
    """Require a result-bound external adherence review, not just game replay."""
    path = folder / 'ADHERENCE_REVIEW.json'
    if not path.exists():
        return False, 'Awaiting transcript review'
    try:
        r = read_json(path)
        if r.get('result_sha256') == digest and r.get('passed') is False and r.get('decision_final') is True:
            return False, 'Excluded: ' + r.get('exclusion_reason', 'adherence review failed')
        required = ('passed', 'full_public_context_reviewed', 'fresh_context_confirmed',
                    'literal_model_choices_confirmed', 'fixed_requested_settings_confirmed')
        if r.get('result_sha256') == digest and r.get('missing_evidence') and r.get('decision_final') is not True:
            return False, 'Pending: incomplete orchestration record'
        if r.get('result_sha256') != digest or not all(r.get(k) is True for k in required):
            return False, 'Review incomplete, failed, or for another checkpoint'
        transcript = folder / 'PUBLIC_TRANSCRIPT.jsonl'
        if not transcript.exists() or sha256(transcript.read_bytes()).hexdigest() != r.get('public_transcript_sha256'):
            return False, 'Transcript missing or changed'
        if not r.get('reviewer') or not r.get('review_note'):
            return False, 'Review lacks attribution'
        return True, 'Reviewed'
    except (OSError, ValueError, TypeError):
        return False, 'Review unreadable; retry on refresh'


def snapshot(repository):
    repository = Path(repository).resolve()
    root = repository / COLLECTION
    plan = read_json(root / 'COLLECTION_PLAN.json')
    models = [m['slot'] for m in plan['models']]
    amendment = root / 'REPLICATION_AMENDMENT_01.json'
    target_contexts = (read_json(amendment)['target_attempted_contexts_per_model']
                       if amendment.exists() else plan.get('batches_per_model_this_wave', 1))
    timebox_path = root / 'TIMEBOX_AMENDMENT_02.json'
    timebox = read_json(timebox_path) if timebox_path.exists() else None
    if timebox:
        target_contexts = None  # User's elapsed-time cap supersedes ten runs.
    stopping_path = root / 'STOP_AFTER_THREE_04.json'
    stopping = read_json(stopping_path) if stopping_path.exists() else None
    if stopping:
        target_contexts = stopping['complete_nonexcluded_contexts_per_model']
    runs = []
    for model in models:
        for folder in sorted((root / model).glob('run*')):
            if not (folder / 'CASE.json').is_file():
                continue
            record = dict(model=model, run=folder.name, path=str(folder), complete=False,
                          completed_pages=0, planned_pages=224, completed_weeks={a: 0 for a in 'ABC'},
                          eligible=False, outcomes=[], review='Pending', error=None)
            try:
                case = read_json(folder / 'CASE.json')
                status = read_json(folder / 'STATUS.json')
                record.update(status)
                record['requested_model'] = case['requested_model']
                record['requested_effort'] = case['requested_effort']
                if status['complete']:
                    raw = (folder / 'RESULT.json').read_bytes()
                    record['result_sha256'] = sha256(raw).hexdigest()
                    record['outcomes'] = audited_result(raw)
                    record['eligible'], record['review'] = review_ok(folder, record['result_sha256'])
                else:
                    record['review'] = 'Collecting decisions' if status['completed_pages'] else 'Prepared; awaiting first decision'
            except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
                record['eligible'] = False
                record['error'] = f'{type(exc).__name__}: {exc}'
            runs.append(record)

    # One row per MODEL x ENDPOINT, independent contexts averaged first.
    # Unreviewed full batches can show descriptive differences, never a p-value.
    estimates = []
    for model in models:
        completed = [r for r in runs if r['model'] == model and r['complete'] and r['outcomes'] and not r['error']]
        reviewed = [r for r in completed if r['eligible']]
        for name, metric, plus, minus, direction in ENDPOINTS:
            # Excluded attempts stay visible in the run list and raw report;
            # do not pool them into the current model estimate.
            provisional = [r for r in completed if not r['review'].startswith('Excluded:')]
            chosen = reviewed if reviewed else provisional
            differences = []
            for r in chosen:
                arms = {a['arm']: a for a in r['outcomes']}
                if arms[plus][metric] is not None and arms[minus][metric] is not None:
                    differences.append(arms[plus][metric] - arms[minus][metric])
            # Missing endpoints do not disappear from the planned family.
            ready = len(differences) == len(chosen)
            infer = len(reviewed) >= 2 and ready
            result = paired_inference(differences) if infer else dict(
                mean_difference=sum(differences) / len(differences) if differences and ready else None,
                ci95_low=None, ci95_high=None, p_two_sided=None)
            if not chosen:
                status = 'Waiting for complete A/B/C run'
            elif not ready:
                status = 'Missing endpoint; no inference'
            elif not reviewed:
                status = ('Descriptive; adherence exclusion' if any(r['review'].startswith('Excluded:') for r in chosen)
                          else 'Descriptive; transcript review pending')
            elif len(reviewed) == 1:
                status = 'Descriptive; 1 fresh context'
            else:
                status = 'Exploratory, pointwise analysis'
            estimates.append(dict(model=model, hypothesis=name, label=ENDPOINT_LABELS[name],
                expected_direction=direction, completed_contexts=len(completed), reviewed_contexts=len(reviewed),
                contexts_used=len(chosen), chains_per_condition=50 * len(chosen), status=status, **result))
    # The existing four-model, five-endpoint family remains 20, even though
    # Claude is not collected by these local agents.
    family = [(m, e[0]) for m in batch.SLOTS for e in ENDPOINTS]
    indexed = {(r['model'], r['hypothesis']): r for r in estimates}
    adjusted = holm_adjust([indexed[k]['p_two_sided'] if k in indexed else None for k in family])
    for key, p in zip(family, adjusted):
        if key in indexed:
            indexed[key]['p_holm_20'] = p
    return dict(refreshed_utc=datetime.now(timezone.utc).isoformat(), runs=runs,
                models=models, estimates=estimates, collection=str(root), target_contexts_per_model=target_contexts,
                timebox=timebox, stopping=stopping)


def number(value):
    return 'pending' if value is None else f'{value:,.4g}'


def html(snapshot):
    s = snapshot
    chunks = ['<div style="font-family:Arial,sans-serif;line-height:1.5;max-width:1150px">',
        '<h2>Live Beer Game collection</h2>',
        '<p><b>Read-only monitor.</b> Refreshing does not start games or call an API. '
        'The running agents save a checkpoint after each decision page.</p>',
        f'<p>Last refresh (UTC): {escape(s["refreshed_utc"])}. '
        '50 chains per condition, 24 weeks, three conditions per fresh context.</p>']
    if s.get('stopping'):
        target=s['stopping']['complete_nonexcluded_contexts_per_model']
        finished=all(sum(r['complete'] and not r['review'].startswith('Excluded:')
                         for r in s['runs'] if r['model']==m)>=target for m in s['models'])
        chunks.append(f'<p><b>{"Collection finished" if finished else "Final collection stage"}: stop after {target} complete non-excluded contexts per GPT model.</b> '
            'No more contexts will be launched. Procedure-review eligibility is counted separately. '
            'Earlier excluded attempts remain visible below.</p>')
        if s.get('timebox'):
            chunks.append(f'<p>Earlier hard collection cutoff still applies: {escape(s["timebox"]["collection_cutoff_local"])}.</p>')
    elif s.get('timebox'):
        t = s['timebox']
        chunks.append('<p><b>User-set 90-minute maximum; ten-run target superseded.</b><br>'
            f'Collection stops: {escape(t["collection_cutoff_local"])}.<br>'
            f'Report deadline: {escape(t["delivery_deadline_local"])}.<br>'
            'Unfinished attempts are preserved. Bars cover prepared runs, not percent of the time window.</p>')
    else:
        chunks.append(f'<p><b>Fixed collection stage: {s["target_contexts_per_model"]} attempted fresh contexts per GPT model</b> '
            f'({50*s["target_contexts_per_model"]} chains per condition if all finish). '
            'Bars below cover contexts prepared so far; new contexts increase their denominator.</p>')
    for model in s['models']:
        runs = [r for r in s['runs'] if r['model'] == model]
        pages = sum(r['completed_pages'] for r in runs)
        total = sum(r['planned_pages'] for r in runs)
        complete = sum(r['complete'] for r in runs)
        chains = sum(50 for r in runs for w in r['completed_weeks'].values() if w == 24)
        chunks.append(f'<h3>{escape(MODEL_LABELS.get(model,model))}</h3>'
            f'<progress value="{pages}" max="{max(total,1)}" style="width:70%;height:22px"></progress> '
            f'<b>{pages}/{total} pages ({100*pages/total if total else 0:.1f}%)</b>'
            f'<p>{complete}/{len(runs)} complete fresh contexts; '
            f'{chains}/{150*len(runs)} chain-games finished (24 weeks; probes counted separately).</p>')
        for r in runs:
            weeks = ' | '.join(f'{a}: {r["completed_weeks"].get(a,0)}/24 weeks' for a in 'ABC')
            note = r['error'] or r['review']
            chunks.append(f'<p><b>{escape(r["run"])}</b> - {weeks}<br>'
                f'{escape(note)}. Last saved: {escape(r.get("updated_utc","pending"))}</p>')
    chunks.append('<p><b>Claude:</b> manual website route; no local Claude agent run.</p>'
        '<h3>H1-H4: observed differences and statistical status</h3>'
        '<p>A = control + separate revision; B = control + one decision; '
        'C = causal education + one decision. H4 has two outcomes.</p>'
        '<table style="border-collapse:collapse;width:100%"><thead><tr>')
    headers = ['Model', 'Hypothesis / contrast', 'Difference', '95% CI', 'Adjusted p', 'Reviewed contexts', 'Status']
    chunks.extend(f'<th style="text-align:left;border-bottom:1px solid #999;padding:6px">{h}</th>' for h in headers)
    chunks.append('</tr></thead><tbody>')
    for r in s['estimates']:
        interval = 'pending' if r['ci95_low'] is None else f'{number(r["ci95_low"])} to {number(r["ci95_high"])}'
        values = [MODEL_LABELS.get(r['model'],r['model']), r['hypothesis'] + ': ' + r['label'],
                  number(r['mean_difference']), interval, number(r.get('p_holm_20')),
                  str(r['reviewed_contexts']), r['status']]
        chunks.append('<tr>' + ''.join(f'<td style="padding:6px;border-bottom:1px solid #ddd">{escape(v)}</td>' for v in values) + '</tr>')
    chunks.append('</tbody></table><p><b>How to read this:</b> pending means not enough completed, '
        'reviewed data yet; it does not mean a hypothesis failed. Chains within a context are dependent. '
        'One completed context supplies descriptive results only. At two or more reviewed contexts, '
        'intervals and adjusted p-values become available; very small samples remain weak evidence.</p>'
        '<p>The treatment changes decision opportunities, not a measured clock deadline. '
        'Pipeline sensitivity is a proxy; these are fictional students. '
        'Live intervals and p-values are exploratory and pointwise, not a sequential stopping rule. '
        'Keep collecting to the predeclared target regardless of direction or significance.</p></div>')
    return ''.join(chunks)


def notebook_monitor(repository):
    """Create a widget with an optional cancellable ten-second refresh task."""
    import asyncio
    try:
        import ipywidgets as widgets
    except ImportError:
        return plain_notebook_monitor(repository)
    from IPython.display import display

    panel = widgets.HTML()
    button = widgets.Button(description='Refresh now', button_style='primary')
    auto = widgets.Checkbox(value=False, description='Auto-refresh (10 s)', indent=False)
    state = {'task': None, 'closed': False}

    def refresh(_=None):
        try:
            panel.value = html(snapshot(repository))
        except Exception as exc:
            panel.value = '<p>Refresh could not finish: ' + escape(str(exc)) + '. Click Refresh now to retry.</p>'

    async def loop():
        try:
            while auto.value and not state['closed']:
                await asyncio.sleep(10)
                if auto.value and not state['closed']:
                    refresh()
        except asyncio.CancelledError:
            pass

    def changed(change):
        task = state['task']
        if task is not None:
            task.cancel()
        state['task'] = None
        if change['new']:
            refresh()
            state['task'] = asyncio.get_running_loop().create_task(loop())

    def close():
        state['closed'] = True
        if state['task'] is not None:
            state['task'].cancel()
        auto.value = False

    button.on_click(refresh)
    auto.observe(changed, names='value')
    refresh()
    display(widgets.VBox([widgets.HBox([button, auto]), panel]))
    return dict(refresh=refresh, close=close, auto=auto, panel=panel)


def plain_notebook_monitor(repository):
    """HTML progress bars with async refresh; no optional widget dependency."""
    import asyncio
    from IPython.display import HTML, display

    state = {'task': None, 'closed': False}
    try:
        event_loop = asyncio.get_running_loop()
    except RuntimeError:
        event_loop = None
    note = ('<p><b>Auto-refresh is running every 10 seconds.</b> '
            'This display works without ipywidgets. '
            'To stop refreshing, run <code>monitor["close"]()</code> in a cell. '
            'To refresh immediately, run <code>monitor["refresh"]()</code>.</p>'
            if event_loop else
            '<p><b>Progress snapshot.</b> Re-run this cell to refresh. '
            'Automatic refresh requires an active Jupyter event loop.</p>')
    handle = display(HTML(note + '<p>Reading saved progress...</p>'), display_id=True)

    def refresh(_=None):
        try:
            content = note + html(snapshot(repository))
        except Exception as exc:
            content = note + '<p>Refresh could not finish: ' + escape(str(exc)) + '. The next refresh will retry.</p>'
        if handle is not None:
            handle.update(HTML(content))
        else:
            display(HTML(content))

    async def loop():
        try:
            while not state['closed']:
                await asyncio.sleep(10)
                if not state['closed']:
                    refresh()
        except asyncio.CancelledError:
            pass

    def close():
        state['closed'] = True
        if state['task'] is not None:
            state['task'].cancel()

    refresh()
    if event_loop is not None:
        state['task'] = event_loop.create_task(loop())
    return dict(refresh=refresh, close=close, auto=event_loop is not None,
                panel=handle, mode='plain_html', state=state)
