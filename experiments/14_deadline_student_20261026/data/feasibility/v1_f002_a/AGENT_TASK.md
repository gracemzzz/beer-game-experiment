You are an isolated experimental decision-maker, not a project maintainer. Requested model is gpt-6-astra and effort xhigh. Read EXACT_PROMPT.md in this folder and follow it. This is one chain/four fictional student roles, not ten chains in one context. Do not inspect any other files, source, CASE, private state, scoring keys, protocols, other runs or reports. No API calls, extra agents, order policy code, loops generating decisions, or outcome analysis.

Run folder: D:\beergame\experiments\14_deadline_student_20261026\data\feasibility\v1_f002_a
Python: D:\beergame\.venv\Scripts\python.exe
Transport: D:\beergame\scripts\run_exp14_agent.py

First read EXACT_PROMPT.md completely. For each opportunity use a separate tool call:
& 'D:\beergame\.venv\Scripts\python.exe' -X utf8 'D:\beergame\scripts\run_exp14_agent.py' show --run 'D:\beergame\experiments\14_deadline_student_20261026\data\feasibility\v1_f002_a'

Read the COMPLETE returned display, including the actual deadline clock and immutable decision_id. Set max_output_tokens at least10000, without output filters. Decide the literal values yourself. For game, stdin is a JSON list of four nonnegative integer orders; for probes, a JSON dictionary of the four displayed probe_id values to integer orders; for comprehension, a dictionary of question_id values to letters. Submit using the actual current ID and your literal JSON, not the placeholders:
@'
YOUR_LITERAL_JSON
'@ | & 'D:\beergame\.venv\Scripts\python.exe' -X utf8 'D:\beergame\scripts\run_exp14_agent.py' submit --run 'D:\beergame\experiments\14_deadline_student_20261026\data\feasibility\v1_f002_a' --decision-id 'CURRENT_DECISION_ID'

Submit returns acknowledgement only. After accepted:true, call show again for the next opportunity. There are no revisions. Choose only after its current full display; never precompute orders. Do not combine show and submit in one tool interaction, generate dictionaries with code, or bulk-submit future decisions. A repeated show never resets the timer. Deadline measures transport-inclusive wall time. Deliver the decision within the window; no explanatory prose or progress narration is needed while a decision is open.

If rejected, stopped, incomplete display or tool error occurs, STOP and report it honestly. No repairs, fallback or restarting. Otherwise continue through all gameweeks, all eight probe pages, then the untimed comprehension, until complete. Preserve all zero and constant choices you consider appropriate. Do not produce reasoning traces, p-values or treatment comparisons. Return RESULT.json path and observed deviations; it is a local execution record, not an authentic full transcript. Never fabricate a transcript.
