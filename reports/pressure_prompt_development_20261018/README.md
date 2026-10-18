# Pressure-prompt development — 18 October 2026

**Completed: eight development responses and four held-out responses.** [Read the results and every comparison](FINDINGS.md). Plain-deadline comparisons changed 9/32 and 5/32 orders during development, then 15/32 and 5/32 on held-out states. Repeat-condition variation was also substantial. This shows differing responses, not a verified or stable time-pressure mechanism. All twelve raw replies are retained; no external API calls were made.

**Purpose:** test candidate prompts on small examples before asking the user to collect another large cohort. This is exploratory development, separate from the completed 500-identity study. The initial preparation plan below is retained; the held-out extension was frozen after seeing development responses and before receiving any held-out response.

| Candidate | Brief deadline | Ample deadline |
| --- | --- | --- |
| Plain deadline | [10-second scenario](PLAIN_DEADLINE_BRIEF.md) | [180-second scenario](PLAIN_DEADLINE_AMPLE.md) |
| Visible countdown and instructor reminder | [10-second scenario](COUNTDOWN_BRIEF.md) | [180-second scenario](COUNTDOWN_AMPLE.md) |

Each prompt contains the same 32 decisions, using the existing four student profiles and eight states. The prompts give no earlier answers, future demand path, desired order direction or hypothesis. Within each candidate, the only experimental difference is the fictional deadline. No treatment-specific ordering rule, instruction to ignore deliveries, or deliberate-error requirement is supplied. Ten and 180 seconds are illustrative scenario values; they are not validated student deadlines or measured model runtime.

The bounded screen used two fresh responses per cell: eight outputs total. The user explicitly authorized isolated assistant instances. The simpler plain-deadline candidate then received a separately frozen four-response check on new states, with unchanged instructions. Collection stopped after these twelve responses. See [held-out plan](holdout/PLAN.json). No paid API calls were requested or made.

Save exact responses and settings, including failures. Compare choice changes across deadline conditions and variability between repetitions of the same condition. Report all candidates and both change/no-change outcomes. These small descriptive comparisons cannot separate a stable causal effect from model variability. A correct `deadline_seconds` field checks instruction recognition only; it does not establish perceived pressure or less computation.

If a candidate produces differences, retain it as a development candidate and freeze its wording before testing new held-out states in fresh contexts. Preserve the development sample separately. A candidate selected because it changed choices cannot use those same choices as confirmatory evidence. If both candidates produce identical choices, report that result and reconsider the mechanism rather than silently extending trials. No particular H1 sign is required or sought.

## What this can establish

This screen can show whether these deadline descriptions change the assistant's responses on these examples. It cannot establish actual human behavior, an enforced time/token constraint, or full-game H2/H3. A valid self-test here is not proof that the assistant backend equals the user's GPT-6 / Pro website selection. More wording alone cannot certify a resource limit.

An alternative manual mechanism is an external controller that permits a fixed number of information-inspection actions before an irreversible order. That can enforce different access budgets, but it changes information acquisition and must be studied under that name. It is not implemented by the four scenario prompts. Actual LLM computation limits require separately controlled and measured generation budgets; the old completed copy/paste run has none.

The scientific distinction matters: Kocher, Pahlke and Trautmann's human experiments found different time-pressure effects across gain/loss contexts, rather than a universal change in every decision. That motivates measuring responses instead of guaranteeing a direction. [Management Science, *Tempus Fugit*](https://pubsonline.informs.org/doi/10.1287/mnsc.2013.1711).

Beer Game research also treats problem-solving approach and information availability as experimental factors. My design inference is that restricting what can be inspected should not be mislabeled as a pure clock manipulation. [Journal of Operations Management, *Decision-making in the supply chain*](https://www.sciencedirect.com/science/article/abs/pii/S0272696308000612).

Synthetic respondent research documents limitations of replacing human survey responses with demographic-prompted LLM outputs; differences in this screen would not validate UB student realism. [Political Analysis, *Synthetic Replacements for Human Survey Data?*](https://www.cambridge.org/core/journals/political-analysis/article/synthetic-replacements-for-human-survey-data-the-perils-of-large-language-models/B92267DC26195C7F36E63EA04A47D2FE).

## Files and reproduction

[PLAN.json](PLAN.json) records the design, planned response count and exact prompt hashes. From `D:\beergame`, `python scripts/prepare_pressure_prompt_pilot.py` reproduces the four prompt boxes without a model connection. Existing changed prompts cannot be overwritten; later wording needs its own version. Do not import these outputs into notebook 06: its schema and completed sample belong to the earlier experiment.
