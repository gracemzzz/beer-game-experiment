# Student validation and fictional profile limits

The user confirmed on 11 October 2026 that no real-student decisions are available. `config/student_profiles/` defines four fictional personality conditions. An LLM-generated "central student" would still be synthetic; no model self-description or simulated questionnaire is treated as real student data.

For a future human comparison, use the same classroom instructions, physical rules, displayed state fields, information visibility, and repeated ordering question as the LLM protocol. Save instruction versions, consent/recruitment procedures where applicable, actual participant identifiers in a deidentified form, and measured rather than invented personality/cognitive instruments. Do not label artificial profile IDs as validated psychometric categories.

A response template is provided in `config/student_responses_template.csv`: one row per participant, case and phase. `case_id` should identify a fixed held-out scenario; `profile_id` is optional and only justified when a declared assignment exists. Do not tune prompts on held-out validation responses. Compare order distributions and variation, sensitivity to controlled pipeline changes, missing decisions, and dynamic outcomes. Case calls within a participant and role decisions within a chain are repeated observations.

To study literal human time pressure, collect actual human deadline conditions and response times; the LLM extra-revision intervention is not a calibrated human-seconds equivalent. A small convenience sample supports limited feasibility comparisons, not population representativeness. Until then, reports must say "configured LLM participants".
