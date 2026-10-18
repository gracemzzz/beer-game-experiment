# API prompts used in the latest completed Claude run

Documentation date: **17 October 2026**. Run: **`claude_api_fd5533fef5828d96`**, completed 11 October 2026. Protocol: `student-high-claude-revision-v4`. Model requested and returned: **`claude-haiku-5-5`**, direct Anthropic, fixed **high** effort.

This file collects all fixed prompt wording, all four personality profiles, the three user-message forms, and the response schemas used in this run. It maps them to the notebook and code sections. Dynamic inventories, histories and submitted orders vary by request; templates and exact saved examples show how those values enter the prompts. This is a catalog of all prompt forms, rather than a duplicate of all 2,060 fully expanded request bodies. Every expanded body remains in the [saved requests](../../data/runs/claude_api_fd5533fef5828d96/requests/). No historical prompt versions are included.

Contents: [usage map](#1-where-each-prompt-is-used), [shared system prompt](#2-shared-system-prompt), [four profiles](#3-the-four-participant-profiles), [initial decision](#4-initial-order-prompt), [revision](#5-revision-prompt), [rules check](#6-rules-check-prompt), [stage inputs](#7-how-calibration-probes-and-games-fill-the-prompts), [exact examples](#8-exact-saved-user-message-examples), [API settings](#9-api-settings-and-response-schemas), [verification](#10-provenance-and-regeneration).

## 1. Where each prompt is used

Notebook: [05_claude_deliberation_study.ipynb](../../notebooks/05_claude_deliberation_study.ipynb). The linked code files below are the frozen source from this completed run. Their maintained counterparts are under `src/beergame_study/`. Line numbers refer to the frozen files.

| Stage / notebook section | Prompt sent | Saved API calls | Code section |
| --- | --- | ---: | --- |
| Calibration / Calibration | System + profile + initial decision | 16 | [run_study, line 228; initial_call, line 95](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_study.py) |
| Calibration / Calibration | System + same profile/state/history + revision | 16 | [run_study, line 233; revision_call, line 100](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_study.py) |
| Onboarding / Paired games | System + profile + three rules questions | 32 | [run_study, line 309](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_study.py) |
| Matched-state H1 probes / Paired games | System + profile + initial decision | 64 | [run_study, line 322; paired_choices, line 108](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_study.py) |
| Matched-state H1 probes / Paired games | System + same probe + revision | 64 | [paired_choices, line 124](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_study.py) |
| Dynamic Beer Game / Paired games | System + profile + initial decision | 1,228 | [run_study, line 344; initial_call, line 95](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_study.py) |
| Dynamic Beer Game / Paired games | System + same weekly state/history + revision | 640 | [paired_choices, line 124; revision_call, line 100](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_study.py) |
| **Total** | | **2,060** | |

Every call uses the same system prompt and exactly one JSON user message. The four personality profiles are locally stored prompt content; they were not generated through a separate API call. Practice rounds, automatic scoring, progress monitoring, hypothesis calculations and report writing use no API prompts.

## 2. Shared system prompt

Exact text of `COMMON`, [claude_protocol.py, line 22](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_protocol.py). Sent in the native Anthropic `system` field on every call, including the rules check.

```text
You are a hypothetical second-year undergraduate business student at
the University at Buffalo taking part in a classroom Beer Game. You have ordinary
introductory business knowledge and have not previously played this game. Make
the decisions you would submit in this role, trying to minimize the team's total
inventory holding and backlog costs. This is a fictional participant. Do not
invent personal characteristics, deliberate mistakes, or a particular bias.
Your participant_profile supplies your consistent personality and background.
Use that same fictional profile throughout the game, without inventing other traits.

The positions are retailer, wholesaler, distributor and factory. Each week you
order cases from your supplier; the factory instead starts production. Submit a
nonnegative integer. Zero is allowed. There is no suggested quantity or maximum.
Inventory costs $0.50 per case per week and backlog costs $1 per case per week.
There is no sales revenue, ordering fee, bulk discount or production capacity limit.

Your display is after this week's deliveries and automatic shipments, before
your new order. Backlog already contains all unfilled current and previous demand
and persists until supplied. Inventory is remaining available stock. Outstanding
orders cannot be canceled and are not inventory. Deliveries_due lists cases
already dispatched, arriving next week then the following week; for the factory
these are production completions. Awaiting_dispatch lists your other outstanding
cases still awaiting shipment. These are separate quantities, not extra demand.
A new order reaches the supplier next week and shipment takes two more weeks;
earliest arrival is week t+3, with further delays when the supplier has shortages.
Factory production started in week t arrives in week t+3 even when current stock
and outstanding production are zero. A new order cannot change today's shipments.

You see all positions' remaining inventories, your local state, and your own
previous rounds. Other positions' orders and backlogs and future customer demand
are hidden. There is no communication or outside tool use. Initially each position
has 12 cases and the flow is 4 cases per week. The first four practice rounds
automatically order 4. Thereafter, end-customer demand is drawn independently
each week: integers 0 through 8 are equally likely. Everyone knows this
distribution, but future draws are hidden and only the retailer observes current
end-customer demand directly. The last decision week is not disclosed. After decisions
end, 12 automatic weeks are scored with customer demand held at its last value
and each position's order held at its own last submitted quantity.

Submit a current choice first. If a revision opportunity is provided, you may
keep or change that choice. Your latest completed submission for this same week
is the order that will be placed. An unfinished revision leaves that submission
in force. Return only the structured order.
```

## 3. The four participant profiles

Exactly one complete object below is inserted as `participant_profile` in each user message. All fields, including the fictional-profile status, are visible to the model. Profiles are assigned before game outcomes and stay fixed for a role within a block; the short and adequate conditions receive the same assigned profile.

### `methodical_calm`

Source: [methodical_calm.json](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/profiles/methodical_calm.json).

```json
{
  "id": "methodical_calm",
  "label": "Methodical, emotionally steady",
  "status": "Fictional experimental profile; not measured from UB students",
  "background": "Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.",
  "description": "In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."
}
```

### `methodical_concerned`

Source: [methodical_concerned.json](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/profiles/methodical_concerned.json).

```json
{
  "id": "methodical_concerned",
  "label": "Methodical, uncertainty-sensitive",
  "status": "Fictional experimental profile; not measured from UB students",
  "background": "Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.",
  "description": "In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."
}
```

### `flexible_calm`

Source: [flexible_calm.json](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/profiles/flexible_calm.json).

```json
{
  "id": "flexible_calm",
  "label": "Flexible, emotionally steady",
  "status": "Fictional experimental profile; not measured from UB students",
  "background": "Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.",
  "description": "In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."
}
```

### `flexible_concerned`

Source: [flexible_concerned.json](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/profiles/flexible_concerned.json).

```json
{
  "id": "flexible_concerned",
  "label": "Flexible, uncertainty-sensitive",
  "status": "Fictional experimental profile; not measured from UB students",
  "background": "Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.",
  "description": "In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."
}
```

These are fictional personality instructions. There are no observations from actual UB students in this run, and repeated calls are not independent human respondents.

## 4. Initial order prompt

Used for calibration, probes and both conditions in the dynamic game. The exact question is:

```text
How many cases do you order this week? Return the integer in the order field.
```

User-message template (angle-bracket values are explanatory placeholders, not literal strings sent to Claude):

```json
{
  "task": "How many cases do you order this week? Return the integer in the order field.",
  "participant_profile": "<one complete profile object from section 3>",
  "past_rounds": "<array of this role's prior displayed states and submitted orders>",
  "current_state": "<current displayed state object; see section 7>"
}
```

The initial prompt has no short/adequate condition label, token allowance, hypothesis, or suggested order. There is no separate instruction to rush, to ignore the pipeline, or to produce a particular bias. The short condition keeps this initial order; the adequate condition receives the additional prompt below.

## 5. Revision prompt

Uses the same system prompt, profile, task, history and current state as that decision's initial call. Two fields are appended to the user object:

```json
{
  "submitted_order": "<integer returned by the completed initial call>",
  "opportunity": "You have one opportunity to reconsider. Keep or change your submitted order."
}
```

Exact extra instruction:

```text
You have one opportunity to reconsider. Keep or change your submitted order.
```

Used for every calibration case, and only the adequate condition in probes and games. The revision is a fresh API call containing the prior integer choice, with no assistant turn or prior reasoning text. The model may keep or change that choice.

The following exact frozen function constructs both initial and revision messages ([claude_protocol.py, line 132](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_protocol.py)):

```python
def messages(state, history, previous_order=None):
    profile_id = state.get('profile_id', PROFILE_IDS[0])
    payload = dict(task=TASK, participant_profile=profiles()[profile_id], past_rounds=history,
                   current_state={k: v for k, v in state.items() if k != 'profile_id'})
    if previous_order is not None:
        payload.update(submitted_order=previous_order,
                       opportunity='You have one opportunity to reconsider. Keep or change your submitted order.')
    return [{'role': 'system', 'content': COMMON},
            {'role': 'user', 'content': json.dumps(payload, separators=(',', ':'), allow_nan=False)}]
```

Decision JSON is serialized with `separators=(',', ':')` and `allow_nan=False`. The local system/user representation is translated to Anthropic's native fields in section 9.

## 6. Rules-check prompt

Before each paired block, each of its four assigned roles receives these three factual questions once. This is an onboarding check shared across conditions. The actual latest-run user payload has the following form; the role and profile placeholders are replaced by their assigned values:

```json
{
  "role": "<retailer, wholesaler, distributor or factory>",
  "participant_profile": "<assigned complete profile object>",
  "questions": {
    "backlog_includes_current_unfilled_demand": "Does current backlog already include unfilled demand from this week?",
    "factory_order_week_7_arrival_week": "When does factory production started in week 7 arrive?",
    "three_week_backlog_cost": "What is the cost of five backlogged cases at the end of each of three weeks?"
  }
}
```

Code: [claude_study.py, line 309](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_study.py). It uses ordinary `json.dumps(...)` spacing. There is no `task` field in this rules-check message. Expected answers are local validation data, not supplied to the model. The order response schema is replaced by the rules-answer schema shown in section 9. The shared system prompt still ends with the instruction about returning a structured order; that wording is reproduced here exactly as it was sent.

## 7. How calibration, probes and games fill the prompts

### Displayed state and history

Built by [display_state, line 122](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_protocol.py). An actual initial probe state illustrates every current-state field:

```json
{
  "week": 12,
  "role": "retailer",
  "demand": 8,
  "received": 4,
  "shipped": 4,
  "inventory": 0,
  "backlog": 8,
  "shared_inventory": {
    "retailer": 0,
    "wholesaler": 12,
    "distributor": 12,
    "factory": 12
  },
  "deliveries_due": [
    4,
    4
  ],
  "awaiting_dispatch": 0
}
```

| Field | Meaning in the prompt |
| --- | --- |
| `week`, `role` | Current simulated week and supply-chain position |
| `demand` | Orders arriving at this role this week; retailer sees current customer demand |
| `received`, `shipped` | Cases received and automatically shipped this week |
| `inventory`, `backlog` | Remaining stock and total unfilled demand after shipments |
| `shared_inventory` | Remaining inventory at each of the four positions |
| `deliveries_due` | Already dispatched cases arriving next week, then the following week |
| `awaiting_dispatch` | Other outstanding cases still awaiting shipment |

`past_rounds` contains this role's entire available display history, with its submitted `order` added to each round. Dynamic-game history also retains `profile_id`; calibration history does not. `profile_id` is removed from `current_state`, because the full profile is supplied separately. No computed `supply_line`, `net_inventory` or `cost` field appears in the displayed state. Future demand, other roles' orders/backlogs and the final decision week are not supplied.

### Calibration / notebook Calibration

The same initial and revision prompt forms are applied to 16 prespecified states: eight development and eight holdout cases. The first four development cases also serve as the quick screen, without additional prompt types or extra calls. Scenario histories come from deterministic simulator policies; their recorded prior orders are shown, but the generating policy formula is not. The split, scenario identifier and desired test results are not added to the user payload.

Source: [calibration_bank, line 168](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_protocol.py); exact states and histories: [manifest.json](../../data/runs/claude_api_fd5533fef5828d96/manifest.json), `calibration_bank`.

| Case | Role | Displayed week | Profile | Prior rounds |
| --- | --- | ---: | --- | ---: |
| `development-0-retailer` | retailer | 5 | `methodical_calm` | 4 |
| `development-0-wholesaler` | wholesaler | 10 | `methodical_concerned` | 9 |
| `development-0-distributor` | distributor | 19 | `flexible_calm` | 18 |
| `development-0-factory` | factory | 28 | `flexible_concerned` | 27 |
| `development-1-retailer` | retailer | 8 | `methodical_concerned` | 7 |
| `development-1-wholesaler` | wholesaler | 15 | `flexible_calm` | 14 |
| `development-1-distributor` | distributor | 24 | `flexible_concerned` | 23 |
| `development-1-factory` | factory | 31 | `methodical_calm` | 30 |
| `holdout-0-retailer` | retailer | 5 | `methodical_calm` | 4 |
| `holdout-0-wholesaler` | wholesaler | 10 | `methodical_concerned` | 9 |
| `holdout-0-distributor` | distributor | 19 | `flexible_calm` | 18 |
| `holdout-0-factory` | factory | 28 | `flexible_concerned` | 27 |
| `holdout-1-retailer` | retailer | 8 | `methodical_concerned` | 7 |
| `holdout-1-wholesaler` | wholesaler | 15 | `flexible_calm` | 14 |
| `holdout-1-distributor` | distributor | 24 | `flexible_concerned` | 23 |
| `holdout-1-factory` | factory | 31 | `methodical_calm` | 30 |

### Matched-state probes / notebook Paired games

Each block presents two states per role, with `past_rounds=[]`. Both have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8 and awaiting dispatch 0. Shared inventory is 0 for the focal role and 12 for each other role. Only deliveries differ.

| Roles | Local case label | `deliveries_due` | Total dispatched cases |
| --- | --- | --- | ---: |
| Retailer, wholesaler, distributor, factory | `low` | `[4, 4]` | 8 |
| Retailer, wholesaler, distributor, factory | `high` | `[16, 16]` | 32 |

The `low`/`high` labels and H1 hypothesis are logging/analysis information, not prompt instructions. The initial choice is shared across the two conditions because their prompts match; adequate then gets one revision. Probe responses are not inserted into subsequent game history. Source: [supply_line_probes, line 195](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_protocol.py).

### Dynamic games / notebook Paired games

There are 8 paired blocks, each with a short and an adequate four-role chain. Weeks 1–4 automatically order 4; weeks 5–24 use the initial/revision prompts. The following 12 automatic scoring weeks repeat each role's own last order and make no API calls. Each role sees its own condition's evolving state and past rounds. Identical complete initial messages share one call only within the same paired block/week/role; once their histories differ, both conditions get separate initial calls. There is no sharing across blocks.

This run had **52 shared game initial calls**, yielding 1,228 actual initial API calls for 1,280 model-controlled orders, plus 640 adequate revisions.

The frozen profile assignments below apply to the rules checks, probes and games. Block numbers here are the zero-based indices in saved requests.

| Block | Retailer | Wholesaler | Distributor | Factory |
| ---: | --- | --- | --- | --- |
| 0 | `flexible_concerned` | `methodical_concerned` | `flexible_calm` | `methodical_calm` |
| 1 | `methodical_concerned` | `flexible_calm` | `methodical_calm` | `flexible_concerned` |
| 2 | `flexible_calm` | `methodical_calm` | `flexible_concerned` | `methodical_concerned` |
| 3 | `methodical_calm` | `flexible_concerned` | `methodical_concerned` | `flexible_calm` |
| 4 | `methodical_concerned` | `methodical_calm` | `flexible_calm` | `flexible_concerned` |
| 5 | `methodical_calm` | `flexible_calm` | `flexible_concerned` | `methodical_concerned` |
| 6 | `flexible_calm` | `flexible_concerned` | `methodical_concerned` | `methodical_calm` |
| 7 | `flexible_concerned` | `methodical_concerned` | `methodical_calm` | `flexible_calm` |

## 8. Exact saved user-message examples

These code blocks preserve the complete saved user strings, including JSON spacing. For every example the system text is exactly section 2. The long single-line decision JSON is the actual transmitted format; enable line wrapping in your Markdown viewer if needed. The source links include the full native `api_request` and the resulting response.

### Rules check: first block, retailer

Saved request: [62dee0d90972a4d154af6fcd70dc997fa8496c4c9544b143eaef761fcd58cc60](../../data/runs/claude_api_fd5533fef5828d96/requests/62dee0d90972a4d154af6fcd70dc997fa8496c4c9544b143eaef761fcd58cc60.json). Identity (logging metadata, not prompt text): `{"stage": "rules", "block": 0, "role": "retailer"}`.

```json
{"role": "retailer", "participant_profile": {"id": "flexible_concerned", "label": "Flexible, uncertainty-sensitive", "status": "Fictional experimental profile; not measured from UB students", "background": "Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.", "description": "In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}, "questions": {"backlog_includes_current_unfilled_demand": "Does current backlog already include unfilled demand from this week?", "factory_order_week_7_arrival_week": "When does factory production started in week 7 arrive?", "three_week_backlog_cost": "What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

### Calibration: first development initial choice

Saved request: [33059de4069e904cb93f9a6f1e31f23d5d4014beaa1dd021d5ee196af87f5cd8](../../data/runs/claude_api_fd5533fef5828d96/requests/33059de4069e904cb93f9a6f1e31f23d5d4014beaa1dd021d5ee196af87f5cd8.json). Identity (logging metadata, not prompt text): `{"stage": "calibration", "item": "development-0-retailer", "phase": "initial"}`.

```json
{"task":"How many cases do you order this week? Return the integer in the order field.","participant_profile":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"past_rounds":[{"week":1,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"order":4},{"week":2,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"order":4},{"week":3,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"order":4},{"week":4,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"order":4}],"current_state":{"week":5,"role":"retailer","demand":8,"received":4,"shipped":8,"inventory":8,"backlog":0,"shared_inventory":{"retailer":8,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0}}
```

### Matched probe: retailer, low deliveries, initial choice

Saved request: [d20273fba8cb8a16358ae06f6b1e1e71c782878a84c44227348f8c5d11dd4e29](../../data/runs/claude_api_fd5533fef5828d96/requests/d20273fba8cb8a16358ae06f6b1e1e71c782878a84c44227348f8c5d11dd4e29.json). Identity (logging metadata, not prompt text): `{"stage": "probe", "block": 0, "item": "retailer-low", "condition": "shared", "phase": "initial"}`.

```json
{"task":"How many cases do you order this week? Return the integer in the order field.","participant_profile":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"past_rounds":[],"current_state":{"week":12,"role":"retailer","demand":8,"received":4,"shipped":4,"inventory":0,"backlog":8,"shared_inventory":{"retailer":0,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0}}
```

### Matched probe: retailer, high deliveries, initial choice

Saved request: [618360abc8278effb579074b4958b95aed557f29bd636519150c45d56c2e3200](../../data/runs/claude_api_fd5533fef5828d96/requests/618360abc8278effb579074b4958b95aed557f29bd636519150c45d56c2e3200.json). Identity (logging metadata, not prompt text): `{"stage": "probe", "block": 0, "item": "retailer-high", "condition": "shared", "phase": "initial"}`.

```json
{"task":"How many cases do you order this week? Return the integer in the order field.","participant_profile":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"past_rounds":[],"current_state":{"week":12,"role":"retailer","demand":8,"received":4,"shipped":4,"inventory":0,"backlog":8,"shared_inventory":{"retailer":0,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[16,16],"awaiting_dispatch":0}}
```

### Game: first block, week 5, retailer, shared initial choice

Saved request: [689fbbd615ccc1d857c363eaa53f9578e1d199a9535c0d8c1ccbef07678bd7ac](../../data/runs/claude_api_fd5533fef5828d96/requests/689fbbd615ccc1d857c363eaa53f9578e1d199a9535c0d8c1ccbef07678bd7ac.json). Identity (logging metadata, not prompt text): `{"stage": "game", "block": 0, "week": 5, "role": "retailer", "condition": "shared", "phase": "initial"}`.

```json
{"task":"How many cases do you order this week? Return the integer in the order field.","participant_profile":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"past_rounds":[{"week":1,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"profile_id":"flexible_concerned","order":4},{"week":2,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"profile_id":"flexible_concerned","order":4},{"week":3,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"profile_id":"flexible_concerned","order":4},{"week":4,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"profile_id":"flexible_concerned","order":4}],"current_state":{"week":5,"role":"retailer","demand":3,"received":4,"shipped":3,"inventory":13,"backlog":0,"shared_inventory":{"retailer":13,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0}}
```

### Game: same week and role, adequate revision

Saved request: [7b135ed1f07811ae56c64588f7900bf7f8e1ecd6dfee1dacdae08d926a30811e](../../data/runs/claude_api_fd5533fef5828d96/requests/7b135ed1f07811ae56c64588f7900bf7f8e1ecd6dfee1dacdae08d926a30811e.json). Identity (logging metadata, not prompt text): `{"stage": "game", "block": 0, "week": 5, "role": "retailer", "condition": "adequate", "phase": "revision"}`.

```json
{"task":"How many cases do you order this week? Return the integer in the order field.","participant_profile":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"past_rounds":[{"week":1,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"profile_id":"flexible_concerned","order":4},{"week":2,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"profile_id":"flexible_concerned","order":4},{"week":3,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"profile_id":"flexible_concerned","order":4},{"week":4,"role":"retailer","demand":4,"received":4,"shipped":4,"inventory":12,"backlog":0,"shared_inventory":{"retailer":12,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0,"profile_id":"flexible_concerned","order":4}],"current_state":{"week":5,"role":"retailer","demand":3,"received":4,"shipped":3,"inventory":13,"backlog":0,"shared_inventory":{"retailer":13,"wholesaler":12,"distributor":12,"factory":12},"deliveries_due":[4,4],"awaiting_dispatch":0},"submitted_order":4,"opportunity":"You have one opportunity to reconsider. Keep or change your submitted order."}
```

## 9. API settings and response schemas

These are API parameters rather than extra natural-language prompts. The initial-choice settings below also apply to rules checks. Revisions use `max_tokens=8192` with the same model and effort.

```json
{
  "model": "claude-haiku-5-5",
  "max_tokens": 16384,
  "thinking": {
    "type": "adaptive",
    "display": "omitted"
  },
  "service_tier": "standard_only",
  "inference_geo": "global",
  "output_config": {
    "effort": "high"
  }
}
```

`max_tokens=16384` is the initial/rules ceiling, not an instruction to consume that many tokens. Adequate receives the initial call plus a revision; short receives the initial call. Temperature, top-p and top-k are omitted in every saved request. The common client timeout is 900 seconds and is an infrastructure limit.

The native message fields have this structure (placeholders are explanatory):

```json
{
  "system": [
    {
      "type": "text",
      "text": "<exact system prompt from section 2>",
      "cache_control": {
        "type": "ephemeral",
        "ttl": "5m"
      }
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": "<one serialized JSON user string>"
    }
  ]
}
```

There are no developer or assistant messages, tools, extra hidden prompt fields or persistent conversation messages in the saved application payloads. Native formatting: [request_parameters, line 21](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/claude_transport.py).

### Initial/revision response format actually sent

Included in `output_config.format` alongside `output_config.effort="high"`:

```json
{
  "type": "json_schema",
  "schema": {
    "type": "object",
    "properties": {
      "order": {
        "type": "integer"
      }
    },
    "required": [
      "order"
    ],
    "additionalProperties": false
  }
}
```

The source schema additionally has `properties.order.minimum=0`. The Anthropic adapter removes that unsupported numeric grammar constraint; the system prompt and local validation still require a nonnegative integer. There is no maximum, positive floor, rationale or explanation field.

### Rules-check response format actually sent

```json
{
  "type": "json_schema",
  "schema": {
    "type": "object",
    "properties": {
      "backlog_includes_current_unfilled_demand": {
        "type": "boolean"
      },
      "factory_order_week_7_arrival_week": {
        "type": "integer"
      },
      "three_week_backlog_cost": {
        "type": "number"
      }
    },
    "required": [
      "backlog_includes_current_unfilled_demand",
      "factory_order_week_7_arrival_week",
      "three_week_backlog_cost"
    ],
    "additionalProperties": false
  }
}
```

## 10. Provenance and regeneration

- [Run manifest](../../data/runs/claude_api_fd5533fef5828d96/manifest.json): configuration, common prompt, four profiles, calibration bank and probes.
- [Frozen source](../../data/runs/claude_api_fd5533fef5828d96/source_implementation/): the implementation used to produce the saved run.
- [Native requests](../../data/runs/claude_api_fd5533fef5828d96/requests/): exact per-call `api_request`, original `messages`, schema, identity, requested/returned model and response.
- [Completed-run raw-file hashes](findings_provenance.json): earlier immutable-evidence baseline.
- Configuration fingerprint: `515cb72b6644436bd6fa9039c2df55aea0f755a06de3b933b63395168200e94c`.
- Shared system text SHA-256 (UTF-8): `6b469aae2a60680f3a40dc854a7af4e15401bb97ea86204db91c737d0ff1d06d`.

Export checks covered **all 2,060 request records**, **all 4 profile objects**, and **all 14 frozen source/profile hashes**. Each saved prompt and native payload was reconstructed with the frozen formatters and compared for exact equality. Rules wording, calibration inputs, probe inputs, profile assignments, full game-history lengths, fixed model/effort/schemas, and every revision's initial integer were checked. All **2,082 raw files** match the completed findings audit and remained unchanged during export.

Regenerate from the project root without an API key or any paid calls:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/export_claude_prompts.py --run data/runs/claude_api_fd5533fef5828d96
```

The exporter only writes this catalog under the existing report folder. It reads the completed evidence and frozen source, so subsequent edits to working prompts cannot silently change what this file says was used. The catalog documents the existing experiment; it does not validate fictional profiles as real students or extra revision as human time pressure.
