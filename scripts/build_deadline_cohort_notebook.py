"""Build notebook 07 for the independent deadline-framing rerun."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]
md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
cells=[md('''# Beer Game rerun: separate deadline scenarios

Use this notebook for the **new** study. Notebook 06 and its original results are preserved.
Each fresh chat simulates students with either **10 seconds** or **180 seconds** to decide.
The conditions never receive one another's answers. We repeat both conditions to show ordinary generation variability.

The prepared plan has **500 fictional identities**, five batches, two deadline conditions and two generation repeats: **20 responses**. Repeats reuse the same identities and demand paths; they are not another 500 students.

**Simple steps:** run sections 1–4, copy the displayed prompt into a fresh **GPT-6 / Pro** chat, then paste the entire JSON into section 5. Repeat with the next prompt. Section 7 updates the report and plots, including partial results. No API key or API calls are involved.

These are fictional deadline instructions, not measured model runtimes. Hypothesis contrasts remain descriptive. [Protocol](../docs/DEADLINE_COHORT_PROTOCOL_20261018.md).

## 1. Load'''),code('''from pathlib import Path
import sys, json, html
ROOT=Path.cwd()
if not (ROOT/'src').exists(): ROOT=ROOT.parent
if not (ROOT/'src/beergame_study').exists(): raise RuntimeError('Open from the project or notebooks folder.')
sys.path.insert(0,str(ROOT/'src')) if str(ROOT/'src') not in sys.path else None
from IPython.display import display,HTML,FileLink,Image,clear_output
from beergame_study.deadline_cohort import DeadlineConfig,prepare,read,progress,next_task,import_response,audit
from beergame_study.deadline_cohort_report import build_report,trajectory_figure
try:
    import ipywidgets as widgets
except ImportError:
    widgets=None
print('No model connection is made by this notebook.')'''),md('''## 2. Open the new collection

Leave the existing run selected to continue. Preparing a different experiment requires a new plan; changing inputs cannot replace accepted results.'''),code('''POINTER=ROOT/'reports/LATEST_DEADLINE_COHORT_REPORT.json'
EXISTING_RUN=Path(read(POINTER)['run']) if POINTER.exists() else None
if EXISTING_RUN is None:
    RUN=prepare(DeadlineConfig())
else:
    RUN=EXISTING_RUN
MANIFEST=audit(RUN)
MODEL_LABEL=MANIFEST['config']['model_label']
EFFORT_LABEL=MANIFEST['config']['effort_label']
PLAN=read(RUN/'plan.json')
print('Run:',RUN)
print('Use:',MODEL_LABEL,'/',EFFORT_LABEL)
print(PLAN['fictional_identities'],'fictional identities;',PLAN['expected_responses'],'responses planned.')
pilot=ROOT/'reports/LATEST_DEADLINE_PILOT_REPORT.json'
if pilot.exists():
    print('Separate assistant pilot:')
    display(FileLink(read(pilot)['report']))'''),md('''## 3. Progress

The bar counts accepted responses. It cannot monitor the other website's generation progress.'''),code('''def show_progress():
    status=progress(RUN);done=int(status.accepted.sum());total=len(status)
    display(HTML(f'<b>{done}/{total} responses accepted</b><br><progress value="{done}" max="{total}" style="width:100%;height:25px"></progress>'))
    display(status)
show_progress()'''),md('''## 4. Copy the next prompt

Copy the **entire box** into a **fresh chat** using the saved model/mode. Do not include earlier replies or ask for a particular result. The generation number is a repeat of the same scenario, not a revision.'''),code('''TASK=next_task(RUN)
if TASK is None:
    print('All responses are saved. Continue to analysis.')
else:
    print('Next:',TASK['task_id'])
    display(FileLink(str(TASK['prompt_path'])))
    display(HTML('<textarea readonly style="width:100%;height:400px;font:13px monospace">'+html.escape(TASK['prompt'])+'</textarea>'))'''),md('''## 5. Paste the full JSON response

Enter a chat label, confirm the full prompt/settings, and click **Validate and save**. A valid response is locked even if choices are unchanged. Original text is retained. Unambiguous rule-answer type conversions are documented; orders are never repaired. After saving, rerun sections 3–5 for the next prompt. You can also return the response in the original assistant conversation.'''),code('''if TASK is None:
    print('Collection complete.')
elif widgets is None:
    print('Install ipywidgets for the paste form, or use the file cell below.')
else:
    captured=dict(TASK)
    response_box=widgets.Textarea(placeholder='Paste complete JSON here',layout=widgets.Layout(width='100%',height='300px'))
    session_box=widgets.Text(description='Chat label:')
    confirm_box=widgets.Checkbox(description=f'Full prompt sent with {MODEL_LABEL} / {EFFORT_LABEL}',indent=False)
    save_button=widgets.Button(description='Validate and save',button_style='primary')
    save_output=widgets.Output()
    def save_paste(_):
        with save_output:
            clear_output(wait=True)
            try:
                import_response(RUN,captured['task_id'],response_box.value,model_label=MODEL_LABEL,
                    effort_label=EFFORT_LABEL,session_label=session_box.value,confirm_full_prompt=confirm_box.value)
                save_button.disabled=True
                print('Saved. Rerun sections 3-5, or section 7 to update analysis.')
                show_progress()
            except ValueError as exc:
                print('Not accepted:',exc)
    save_button.on_click(save_paste)
    display(widgets.VBox([response_box,session_box,confirm_box,save_button,save_output]))'''),md('''## 6. Optional file import

Use this instead of the form if you saved the response as UTF-8 text. It is off by default.'''),code('''RESPONSE_FILE=None
FILE_TASK_ID=TASK['task_id'] if TASK else ''
FILE_CHAT_LABEL=''
FILE_FULL_PROMPT_CONFIRMED=False
if RESPONSE_FILE is not None:
    import_response(RUN,FILE_TASK_ID,Path(RESPONSE_FILE).read_bytes().decode('utf-8'),
        model_label=MODEL_LABEL,effort_label=EFFORT_LABEL,session_label=FILE_CHAT_LABEL,
        confirm_full_prompt=FILE_FULL_PROMPT_CONFIRMED)
    show_progress()
else:
    print('File import is off.')'''),md('''## 7. H1, H2, H3 and the new plots

H1 predicts lower pipeline sensitivity in the brief-deadline scenario; H2 predicts higher full cost; H3 predicts higher bullwhip. Python calculates these from submitted decisions. The report shows actual outcome levels, order trajectories, cost phases, and **deadline differences alongside same-deadline repeat variation**. It never forces a nonzero effect or treats generated identities as independent human observations.'''),code('''RESULT=build_report(RUN)
print('Report:',RESULT['report'])
display(FileLink(str(RESULT['report'])))
if RESULT['tables']['hypotheses'].empty:
    print('Awaiting matched deadline conditions; no hypothesis comparison yet.')
else:
    display(RESULT['tables']['hypotheses'])
    display(RESULT['tables']['choice_changes'])
for name in RESULT['images']:
    display(Image(filename=str(RESULT['folder']/(name+'.png'))))
if RESULT['images']:display(FileLink(str(RESULT['folder']/'RESULTS.xlsx')))'''),md('''## 8. Explore a chain

Blue and orange identify deadlines. Line styles identify repeated generations. Gray shading marks practice, and pale orange marks automatic continuation.'''),code('''if RESULT['rounds'].empty:
    print('Save a response to explore its chains.')
elif widgets is None:
    display(trajectory_figure(RESULT['rounds'],str(RESULT['rounds'].iloc[0].chain_id)))
else:
    chain_selector=widgets.Dropdown(options=sorted(RESULT['rounds'].chain_id.unique()),description='Chain:')
    def show_chain(chain_id):
        fig=trajectory_figure(RESULT['rounds'],chain_id)
        display(fig)
        import matplotlib.pyplot as plt
        plt.close(fig)
    chart=widgets.interactive_output(show_chain,{'chain_id':chain_selector})
    display(chain_selector,chart)''')]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
path=ROOT/'notebooks/07_deadline_cohort_rerun.ipynb'
nbf.write(nb,path);print(path)
