"""Reproduce notebook 06; its default execution makes no model calls."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
md=nbf.v4.new_markdown_cell
code=nbf.v4.new_code_cell
cells=[md('''# Beer Game: generate a student cohort by copy and paste

**No API key and no API calls.** Generate prompts here, send them to your chosen chat model, and paste its JSON response back. Python replays the physical game and calculates H1, H2 and H3.

Default: **500 fictional student identities**, 125 four-role chains, five batches of 100 identities. Each chain has an initial and a reconsidered trajectory: 1,000 role trajectories in total, not 1,000 independent students. Each batch needs two responses, so the default plan needs **10 copy/paste exchanges**. Set `BATCH_STUDENTS=500` before starting if you want one full-cohort response per pass; that output is much longer and may truncate.

This new protocol revises **whole trajectories**. It preserves the physical rules and outcome formulas, but does **not** preserve the API experiment's per-week thinking intervention or information isolation. Results describe generated data. Student-level p-values would create false precision, so this notebook shows directions and distributions without such tests. [Full protocol](../docs/MANUAL_COHORT_PROTOCOL_20261017.md).

## 1. Load the notebook
'''),code('''from pathlib import Path
import sys, json, html
ROOT = Path.cwd()
if not (ROOT / 'src').exists():
    ROOT = ROOT.parent
if not (ROOT / 'src/beergame_study').exists():
    raise RuntimeError('Open the notebook from the beergame project or notebooks folder.')
sys.path.insert(0, str(ROOT / 'src')) if str(ROOT / 'src') not in sys.path else None
from IPython.display import display, HTML, Markdown, FileLink, Image, clear_output
from beergame_study.manual_cohort import CohortConfig, prepare, read, progress, next_task, import_response
from beergame_study.manual_cohort_report import build_report, trajectory_figure
try:
    import ipywidgets as widgets
except ImportError:
    widgets = None
    print('For the paste form: install requirements.txt in this notebook kernel. File import below still works.')
print('No model connection is made by this notebook.')'''),md('''## 2. Freeze the plan before generating results

Keep the same model and **high** reasoning setting in every chat. Record the exact displayed model name below. My suggested starting model is **GPT-6 Astra**, if available in your account: OpenAI currently describes it as its most capable model. This is a capability recommendation, not validation of student realism. Chat availability and controls can differ from the API. [Official model guidance](https://developers.openai.com/api/docs/models/gpt-6-astra).

Use a fresh chat for each prompt, with memory/personalization disabled where available and no prior results or hypothesis directions supplied. Do not request a favorable pattern or select the best-looking generation. Hidden reasoning tokens and actual per-student effort are unobserved here. If the chat interface cannot expose high effort, record that limitation and choose a separate protocol before collection.

For a small formatting check, prospectively use `N_STUDENTS=4` and a different `STUDY_LABEL`. Its output is separate from the 500-student plan. Freeze batch size too: it changes how much data one generation produces.
'''),code('''N_STUDENTS = 500
BATCH_STUDENTS = 100
WEEKS = 24                    # four practice + twenty decision weeks
COHORT_REPETITIONS = 1
SEED = 20261017
STUDY_LABEL = 'cohort-500-first-plan'
MODEL_LABEL = 'GPT-6 Astra'    # exact label YOU select in the chat interface
EFFORT_LABEL = 'high'
EXISTING_RUN = None           # or ROOT / 'data/runs/manual_cohort_...'

if EXISTING_RUN is None:
    RUN = prepare(CohortConfig(students=N_STUDENTS, batch_students=BATCH_STUDENTS,
        weeks=WEEKS, repetitions=COHORT_REPETITIONS, seed=SEED, study_label=STUDY_LABEL,
        model_label=MODEL_LABEL, effort_label=EFFORT_LABEL))
else:
    RUN = Path(EXISTING_RUN)
    frozen = read(RUN / 'manifest.json')['config']
    MODEL_LABEL, EFFORT_LABEL = frozen['model_label'], frozen['effort_label']
PLAN = read(RUN / 'plan.json')
print('Saved plan:', RUN)
print(f"{PLAN['fictional_identities']:,} identities; {len(PLAN['chains']):,} paired chains; "
      f"{len(PLAN['batches'])} batches; {PLAN['expected_responses']} responses required.")
print('Each response contains weekly orders plus matched-state choices. No summary statistics are accepted.')'''),md('''## 3. Progress

The bar counts **accepted pasted responses**, not remote model activity. All initial batches are requested before revisions. A response becomes immutable once accepted. Missing batches remain missing in partial reports.
'''),code('''def show_progress():
    table = progress(RUN)
    done = int(table.initial.sum() + table.revision.sum())
    total = 2 * len(table)
    display(HTML(f'<div style="font:16px sans-serif;margin:12px 0"><b>{done} / {total} responses accepted</b><br>'
                 f'<progress value="{done}" max="{total}" style="width:100%;height:24px"></progress></div>'))
    display(table)
show_progress()'''),md('''## 4. Copy the next prompt

Run this cell. Click inside the text box, select all and copy. Send the entire prompt in a **fresh chat** using the fixed model and high effort. Save its response exactly as returned. The prompt file is also available for download.

The next prompt advances only after a response passes validation. The JSON arrays contain weekly orders in `[retailer, wholesaler, distributor, factory]` order. Do not replace them with model-written statistics or code.
'''),code('''TASK = next_task(RUN)
if TASK is None:
    print('All planned responses have been imported. Continue to analysis.')
else:
    print('Copy:', TASK['batch_id'], TASK['stage'])
    display(FileLink(str(TASK['prompt_path'])))
    display(HTML('<textarea readonly style="width:100%;height:380px;font:13px monospace">'
                 + html.escape(TASK['prompt']) + '</textarea>'))
    print('Prompt characters:', len(TASK['prompt']))'''),md('''## 5. Paste and import the model response

Paste into this form, enter a label identifying the chat, confirm the full prompt was sent, then click **Validate and save**. The form checks completeness, IDs, dimensions, factual answers and integer orders. No missing order is filled in and no large order is clipped. All rejected raw attempts are retained.

If a reply is truncated or malformed, retain it and retry the **same prompt** for a technical correction; do not ask for changed ordering behavior. A rules-check failure needs investigation, not answer coaching. A retry is still another generation and is recorded. Once saved, rerun sections **4 and 5** for the next prompt.
'''),code('''if widgets is None:
    print('Paste form unavailable. Use the file-import cell below, or install ipywidgets in this kernel.')
elif TASK is None:
    print('All responses are saved.')
else:
    captured_task = dict(TASK)
    response_box = widgets.Textarea(placeholder='Paste the complete JSON response here...',
                                   layout=widgets.Layout(width='100%', height='300px'))
    session_box = widgets.Text(description='Chat label:', placeholder='e.g. astra-chat-01',
                               layout=widgets.Layout(width='80%'))
    confirm_box = widgets.Checkbox(description='I sent the full prompt with this model and high effort', indent=False)
    save_button = widgets.Button(description='Validate and save', button_style='primary')
    save_output = widgets.Output()
    def save_paste(_):
        with save_output:
            clear_output(wait=True)
            try:
                import_response(RUN, captured_task['batch_id'], captured_task['stage'], response_box.value,
                    model_label=MODEL_LABEL, effort_label=EFFORT_LABEL, session_label=session_box.value,
                    confirm_full_prompt=confirm_box.value)
                save_button.disabled = True
                print('Saved and locked. Rerun sections 4 and 5 for the next prompt.')
                show_progress()
            except ValueError as exc:
                print('Not accepted:', exc)
    save_button.on_click(save_paste)
    display(widgets.VBox([widgets.HTML(f"<b>{captured_task['batch_id']} · {captured_task['stage']} · {html.escape(MODEL_LABEL)}</b>"),
                          response_box, session_box, confirm_box, save_button, save_output]))'''),md('''### Alternative: import a saved response file

Use this if the response is too long for convenient pasting. Save the exact reply as UTF-8 `.txt` or `.json` in the run's `inbox` folder. This cell is off until you supply a path and confirm the metadata. It never executes model-written code.
'''),code('''RESPONSE_FILE = None  # e.g. RUN / 'inbox/b0001_initial.txt'
FILE_BATCH_ID = 'b0001'
FILE_STAGE = 'initial'
FILE_CHAT_LABEL = ''
FILE_FULL_PROMPT_CONFIRMED = False
if RESPONSE_FILE is not None:
    import_response(RUN, FILE_BATCH_ID, FILE_STAGE, Path(RESPONSE_FILE).read_text(encoding='utf-8'),
        model_label=MODEL_LABEL, effort_label=EFFORT_LABEL, session_label=FILE_CHAT_LABEL,
        confirm_full_prompt=FILE_FULL_PROMPT_CONFIRMED)
    show_progress()
else:
    print('File import is off. Inbox:', RUN / 'inbox')'''),md('''## 6. Analyze H1, H2 and H3

Python computes every physical state and all outcome measures from the submitted orders. Only paired batches enter comparisons. Reports remain partial until all planned responses arrive.

- **H1:** initial choices have lower responsiveness to outstanding deliveries; measured by the matched-state probe.
- **H2:** initial trajectories have higher total inventory/backlog cost, including the disclosed 12-week continuation.
- **H3:** initial trajectories have a higher customer-referenced bullwhip ratio, averaged across roles.

These preserve the outcome directions while changing the intervention to whole-trajectory reconsideration. A direction is descriptive evidence about the generated dataset; it cannot verify or disprove human time-pressure hypotheses. A bullwhip ratio below one means no amplification by that measure. Weekly calls, generated students and chains within one response are not independent samples.
'''),code('''FIT_EXPLORATORY_BETA = False  # optional, can be slow for 500 identities; not the primary H1
RESULT = build_report(RUN, fit_beta=FIT_EXPLORATORY_BETA)
print('Report:', RESULT['report'])
display(FileLink(str(RESULT['report'])))
if RESULT['tables']['hypotheses'].empty:
    print('No paired model responses yet. No experimental conclusions have been produced.')
else:
    display(RESULT['tables']['hypotheses'])
    display(RESULT['tables']['quality'])
    for name in RESULT['images']:
        display(Image(filename=str(RESULT['folder'] / f'{name}.png')))
    display(FileLink(str(RESULT['folder'] / 'RESULTS.xlsx')))'''),md('''## 7. Explore a chain

Select any imported chain. Gray shading marks practice weeks; orange shading marks automatic continuation. The exported report also has PNG/PDF figures for publication layouts and an Excel workbook with underlying values. All figures retain their generated-data label.
'''),code('''if RESULT['rounds'].empty:
    print('Import both passes for at least one batch to explore a chain.')
elif widgets is None:
    display(trajectory_figure(RESULT['rounds'], RESULT['rounds'].iloc[0].chain_id))
else:
    chain_selector = widgets.Dropdown(options=sorted(RESULT['rounds'].chain_id.unique()), description='Chain:')
    def show_chain(chain_id):
        fig = trajectory_figure(RESULT['rounds'], chain_id)
        display(fig)
        import matplotlib.pyplot as plt
        plt.close(fig)
    output = widgets.interactive_output(show_chain, {'chain_id': chain_selector})
    display(chain_selector, output)''')]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
                                         'language_info':{'name':'python','version':'3'}})
path=ROOT/'notebooks/06_manual_cohort_simulation.ipynb'
nbf.write(nb,path)
print(path)
