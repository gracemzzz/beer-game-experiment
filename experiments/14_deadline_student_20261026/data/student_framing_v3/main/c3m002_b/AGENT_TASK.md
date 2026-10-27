You are one isolated experimental student-decision participant, not a maintainer. Requested model gpt-6-astra, effort xhigh. Read EXACT_PROMPT.md completely and portray the four supplied student profiles in the fictional classroom situation. No actual model wall-clock limit is imposed. Do not act as an expert optimizing the supply chain in place of those novices.

Run folder: D:\beergame\experiments\14_deadline_student_20261026\data\student_framing_v3\main\c3m002_b
Python: D:\beergame\.venv\Scripts\python.exe
Transport: D:\beergame\scripts\run_exp14_framing.py

Only read this AGENT_TASK.md and EXACT_PROMPT.md. Never read private CASE/state/source/scoring/protocol/report/other runs. No other agents, API calls, ordering-policy code, random generators, optimizers or precomputed future orders.

For EACH opportunity use a separate tool call with max_output_tokens>=10000:
& 'D:\beergame\.venv\Scripts\python.exe' -X utf8 'D:\beergame\scripts\run_exp14_framing.py' show --run 'D:\beergame\experiments\14_deadline_student_20261026\data\student_framing_v3\main\c3m002_b'

Read its COMPLETE public state. Decide your actual four literal answers reflecting the fictional students in that situation. Use a separate interaction to submit your real current JSON and decision_id:
@'
YOUR_LITERAL_JSON
'@ | & 'D:\beergame\.venv\Scripts\python.exe' -X utf8 'D:\beergame\scripts\run_exp14_framing.py' submit --run 'D:\beergame\experiments\14_deadline_student_20261026\data\student_framing_v3\main\c3m002_b' --decision-id 'CURRENT_DECISION_ID'

For game, JSON is a list of four nonnegative integer orders in displayed role_order. For probes it maps exactly the four displayed probe_id values to integer orders. For comprehension map all question_id values to letters. You must actually choose every requested order; never leave blanks, ask software to fill values, generate choices with code or copy future decisions. Zero and repeated choices are allowed. There is one accepted submission per opportunity, no second-round thinking/revision pass. The only time difference is the student's fictional classroom time in your prompt, not your own tool/runtime limit.

After accepted:true, call show for the next state. Continue all24weeks, all8 probe pages, then untimed questions until complete. No defaults, random filler, software fallback or late-answer substitution exists. If an input is rejected, a required tool fails or any public state is incomplete, STOP and disclose the technical deviation; never silently repair/restart/replace decisions. Never invent a missing transcript or claim provider-authenticated settings.

Return RESULT.json path and any observed deviations. Also report fictional_student_seconds from your assigned classroom framing as a short instruction-recall check (not a claim of actual model runtime or human pressure). Do not produce hidden reasoning, comparisons, p-values or outcome analysis.
