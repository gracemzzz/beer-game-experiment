# Exact collection prompts

All 20 frozen prompts, in planned collection order. Each box contains the complete prompt text, including the assigned profiles, demand paths and output schema. No text inside a box has been summarized or changed.

**Recorded model/mode:** GPT-6 / Pro, as reported by the user. These were manual website chats, not API calls. Actual backend, mode, full-prompt submission and fresh-chat execution were not independently verified. Prompt hashes match the accepted-response records.

Rounds 1 and 2 repeat the same assignments in separate chats; neither prompt contains previous answers. Brief means 10 seconds and ample means 180 seconds in the fictional student scenario. These are not measured model deadlines.

| Order | Task | Round | Scenario |
| ---: | --- | ---: | --- |
| 1 | `b0001_g01_brief` | 1 | 10 seconds |
| 2 | `b0001_g01_ample` | 1 | 180 seconds |
| 3 | `b0002_g01_ample` | 1 | 180 seconds |
| 4 | `b0002_g01_brief` | 1 | 10 seconds |
| 5 | `b0003_g01_brief` | 1 | 10 seconds |
| 6 | `b0003_g01_ample` | 1 | 180 seconds |
| 7 | `b0004_g01_ample` | 1 | 180 seconds |
| 8 | `b0004_g01_brief` | 1 | 10 seconds |
| 9 | `b0005_g01_brief` | 1 | 10 seconds |
| 10 | `b0005_g01_ample` | 1 | 180 seconds |
| 11 | `b0001_g02_ample` | 2 | 180 seconds |
| 12 | `b0001_g02_brief` | 2 | 10 seconds |
| 13 | `b0002_g02_brief` | 2 | 10 seconds |
| 14 | `b0002_g02_ample` | 2 | 180 seconds |
| 15 | `b0003_g02_ample` | 2 | 180 seconds |
| 16 | `b0003_g02_brief` | 2 | 10 seconds |
| 17 | `b0004_g02_brief` | 2 | 10 seconds |
| 18 | `b0004_g02_ample` | 2 | 180 seconds |
| 19 | `b0005_g02_ample` | 2 | 180 seconds |
| 20 | `b0005_g02_brief` | 2 | 10 seconds |

## 01. b0001_g01_brief

Batch b0001; round 1; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0001_g01_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00001","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,7,2,4,7,0,1,6,1,6,0,7,8,0,6,1,0,8,6,8]},{"chain_id":"c00002","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,5,1,0,7,7,7,0,6,2,4,0,1,0,0,5,2,3,4,7,5]},{"chain_id":"c00003","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,3,3,2,2,1,7,6,0,8,0,3,3,8,3,1,7,7,8,4]},{"chain_id":"c00004","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,2,0,2,8,7,5,6,2,8,4,0,3,8,1,8,4,5,8,8,5]},{"chain_id":"c00005","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,3,6,1,6,7,7,8,4,7,0,7,7,7,1,4,0,6,5,4,5]},{"chain_id":"c00006","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,8,0,6,7,5,4,7,5,2,3,2,0,2,2,5,1,5,5,0]},{"chain_id":"c00007","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,5,7,3,5,3,6,0,0,6,5,1,4,3,7,3,3,0,1,3]},{"chain_id":"c00008","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,0,5,5,7,7,0,5,2,6,3,5,7,6,7,0,0,7,6,7]},{"chain_id":"c00009","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,8,1,6,3,2,2,7,0,6,4,5,5,7,5,0,1,0,3,2]},{"chain_id":"c00010","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,3,6,3,0,8,5,7,6,8,8,5,5,0,5,0,0,3,2,0,0]},{"chain_id":"c00011","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,7,3,8,8,2,1,4,8,6,5,3,3,3,8,4,0,4,4,3,7]},{"chain_id":"c00012","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,7,5,4,3,6,7,0,8,4,0,5,7,6,5,5,1,4,7,7]},{"chain_id":"c00013","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,2,5,0,6,8,5,5,0,6,4,8,7,2,2,8,1,2,1,1]},{"chain_id":"c00014","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,2,7,7,5,3,4,4,0,2,6,7,4,7,5,7,0,2,5,2]},{"chain_id":"c00015","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,0,1,8,4,5,2,3,8,2,4,3,4,2,8,3,6,6,5,3]},{"chain_id":"c00016","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,4,5,6,3,0,3,0,8,0,2,8,0,3,4,1,6,8,5,0,1]},{"chain_id":"c00017","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,0,0,1,7,0,0,0,5,4,8,1,3,0,4,3,1,2,6,1]},{"chain_id":"c00018","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,5,5,3,7,7,4,1,5,4,8,2,2,6,0,8,3,5,2,5]},{"chain_id":"c00019","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,6,2,6,0,8,0,3,6,3,3,1,3,8,0,1,7,3,2,5,8]},{"chain_id":"c00020","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,3,3,5,6,4,6,8,4,2,7,0,0,5,8,3,0,7,2,8]},{"chain_id":"c00021","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,0,5,7,0,5,8,4,3,0,7,7,6,1,6,7,0,6,8,2]},{"chain_id":"c00022","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,1,1,1,5,4,7,8,1,5,4,8,6,0,8,4,5,8,8,5]},{"chain_id":"c00023","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,3,5,4,1,8,6,0,3,2,5,0,8,8,3,4,0,0,4,1]},{"chain_id":"c00024","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,6,2,1,5,7,4,1,2,0,4,4,8,4,6,2,8,3,0,3]},{"chain_id":"c00025","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,1,4,2,4,1,1,0,1,1,8,7,0,4,7,0,5,3,1,7]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 02. b0001_g01_ample

Batch b0001; round 1; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0001_g01_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00001","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,7,2,4,7,0,1,6,1,6,0,7,8,0,6,1,0,8,6,8]},{"chain_id":"c00002","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,5,1,0,7,7,7,0,6,2,4,0,1,0,0,5,2,3,4,7,5]},{"chain_id":"c00003","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,3,3,2,2,1,7,6,0,8,0,3,3,8,3,1,7,7,8,4]},{"chain_id":"c00004","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,2,0,2,8,7,5,6,2,8,4,0,3,8,1,8,4,5,8,8,5]},{"chain_id":"c00005","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,3,6,1,6,7,7,8,4,7,0,7,7,7,1,4,0,6,5,4,5]},{"chain_id":"c00006","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,8,0,6,7,5,4,7,5,2,3,2,0,2,2,5,1,5,5,0]},{"chain_id":"c00007","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,5,7,3,5,3,6,0,0,6,5,1,4,3,7,3,3,0,1,3]},{"chain_id":"c00008","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,0,5,5,7,7,0,5,2,6,3,5,7,6,7,0,0,7,6,7]},{"chain_id":"c00009","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,8,1,6,3,2,2,7,0,6,4,5,5,7,5,0,1,0,3,2]},{"chain_id":"c00010","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,3,6,3,0,8,5,7,6,8,8,5,5,0,5,0,0,3,2,0,0]},{"chain_id":"c00011","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,7,3,8,8,2,1,4,8,6,5,3,3,3,8,4,0,4,4,3,7]},{"chain_id":"c00012","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,7,5,4,3,6,7,0,8,4,0,5,7,6,5,5,1,4,7,7]},{"chain_id":"c00013","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,2,5,0,6,8,5,5,0,6,4,8,7,2,2,8,1,2,1,1]},{"chain_id":"c00014","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,2,7,7,5,3,4,4,0,2,6,7,4,7,5,7,0,2,5,2]},{"chain_id":"c00015","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,0,1,8,4,5,2,3,8,2,4,3,4,2,8,3,6,6,5,3]},{"chain_id":"c00016","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,4,5,6,3,0,3,0,8,0,2,8,0,3,4,1,6,8,5,0,1]},{"chain_id":"c00017","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,0,0,1,7,0,0,0,5,4,8,1,3,0,4,3,1,2,6,1]},{"chain_id":"c00018","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,5,5,3,7,7,4,1,5,4,8,2,2,6,0,8,3,5,2,5]},{"chain_id":"c00019","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,6,2,6,0,8,0,3,6,3,3,1,3,8,0,1,7,3,2,5,8]},{"chain_id":"c00020","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,3,3,5,6,4,6,8,4,2,7,0,0,5,8,3,0,7,2,8]},{"chain_id":"c00021","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,0,5,7,0,5,8,4,3,0,7,7,6,1,6,7,0,6,8,2]},{"chain_id":"c00022","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,1,1,1,5,4,7,8,1,5,4,8,6,0,8,4,5,8,8,5]},{"chain_id":"c00023","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,3,5,4,1,8,6,0,3,2,5,0,8,8,3,4,0,0,4,1]},{"chain_id":"c00024","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,6,2,1,5,7,4,1,2,0,4,4,8,4,6,2,8,3,0,3]},{"chain_id":"c00025","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,1,4,2,4,1,1,0,1,1,8,7,0,4,7,0,5,3,1,7]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 03. b0002_g01_ample

Batch b0002; round 1; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0002_g01_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00026","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,3,5,6,2,0,0,3,7,4,4,8,8,1,5,4,2,2,1,3,5]},{"chain_id":"c00027","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,3,2,4,1,4,6,3,3,8,5,6,4,4,4,3,2,5,3,7,7]},{"chain_id":"c00028","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,1,4,3,5,6,4,4,3,8,0,4,5,6,3,2,4,1,6,4]},{"chain_id":"c00029","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,5,8,7,8,3,2,4,3,1,6,4,3,8,4,6,1,6,6,0,3]},{"chain_id":"c00030","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,0,4,2,1,4,3,2,7,4,6,0,2,4,6,7,1,6,7,3,8]},{"chain_id":"c00031","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,8,4,1,8,5,2,0,6,1,6,4,5,6,1,7,3,6,3,8,5]},{"chain_id":"c00032","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,1,8,4,7,7,2,4,2,2,4,0,8,0,1,0,5,2,1,5]},{"chain_id":"c00033","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,4,1,7,8,8,6,0,6,5,8,1,3,1,4,7,4,4,1,0,7]},{"chain_id":"c00034","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,3,5,6,0,4,8,1,0,0,2,0,0,0,1,8,6,2,7,4,6]},{"chain_id":"c00035","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,8,8,1,4,4,3,6,0,1,6,5,6,5,1,2,1,7,2,3,4]},{"chain_id":"c00036","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,8,0,7,7,1,1,2,1,8,3,0,6,8,1,6,2,8,7,5]},{"chain_id":"c00037","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,6,6,5,6,1,3,2,7,2,0,7,8,2,0,1,0,8,6,5,1]},{"chain_id":"c00038","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,3,2,4,1,5,0,4,8,2,1,8,7,5,4,8,1,6,2,6,8]},{"chain_id":"c00039","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,5,6,8,4,6,3,0,7,4,8,4,0,7,8,5,7,1,4,7,2]},{"chain_id":"c00040","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,0,1,4,7,3,8,7,1,6,1,8,6,1,3,5,0,5,8,6]},{"chain_id":"c00041","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,5,4,7,8,3,5,8,4,6,1,5,1,6,5,7,2,5,1,4]},{"chain_id":"c00042","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,7,1,2,6,3,6,5,4,7,1,1,4,7,4,8,3,6,1,1]},{"chain_id":"c00043","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,5,3,8,8,6,8,3,5,0,1,2,5,6,5,2,6,1,4,7,8]},{"chain_id":"c00044","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,4,0,0,2,3,4,6,6,0,7,5,2,2,3,7,4,0,0,8]},{"chain_id":"c00045","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,3,0,5,7,3,1,7,1,3,0,5,4,0,6,0,3,2,3,4,7]},{"chain_id":"c00046","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,4,5,5,0,1,1,8,4,4,6,2,5,8,8,7,8,0,8,5,6]},{"chain_id":"c00047","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,0,3,5,1,0,8,5,3,2,3,5,1,8,6,2,6,8,4,7,6]},{"chain_id":"c00048","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,4,4,0,1,6,7,0,4,3,3,2,1,6,7,5,8,7,5,7,7]},{"chain_id":"c00049","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,4,8,2,7,2,7,4,8,8,7,4,0,3,6,6,3,2,1,5,7]},{"chain_id":"c00050","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,2,3,8,3,3,4,2,8,7,0,6,8,4,4,3,0,5,3,3]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 04. b0002_g01_brief

Batch b0002; round 1; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0002_g01_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00026","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,3,5,6,2,0,0,3,7,4,4,8,8,1,5,4,2,2,1,3,5]},{"chain_id":"c00027","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,3,2,4,1,4,6,3,3,8,5,6,4,4,4,3,2,5,3,7,7]},{"chain_id":"c00028","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,1,4,3,5,6,4,4,3,8,0,4,5,6,3,2,4,1,6,4]},{"chain_id":"c00029","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,5,8,7,8,3,2,4,3,1,6,4,3,8,4,6,1,6,6,0,3]},{"chain_id":"c00030","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,0,4,2,1,4,3,2,7,4,6,0,2,4,6,7,1,6,7,3,8]},{"chain_id":"c00031","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,8,4,1,8,5,2,0,6,1,6,4,5,6,1,7,3,6,3,8,5]},{"chain_id":"c00032","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,1,8,4,7,7,2,4,2,2,4,0,8,0,1,0,5,2,1,5]},{"chain_id":"c00033","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,4,1,7,8,8,6,0,6,5,8,1,3,1,4,7,4,4,1,0,7]},{"chain_id":"c00034","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,3,5,6,0,4,8,1,0,0,2,0,0,0,1,8,6,2,7,4,6]},{"chain_id":"c00035","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,8,8,1,4,4,3,6,0,1,6,5,6,5,1,2,1,7,2,3,4]},{"chain_id":"c00036","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,8,0,7,7,1,1,2,1,8,3,0,6,8,1,6,2,8,7,5]},{"chain_id":"c00037","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,6,6,5,6,1,3,2,7,2,0,7,8,2,0,1,0,8,6,5,1]},{"chain_id":"c00038","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,3,2,4,1,5,0,4,8,2,1,8,7,5,4,8,1,6,2,6,8]},{"chain_id":"c00039","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,5,6,8,4,6,3,0,7,4,8,4,0,7,8,5,7,1,4,7,2]},{"chain_id":"c00040","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,0,1,4,7,3,8,7,1,6,1,8,6,1,3,5,0,5,8,6]},{"chain_id":"c00041","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,5,4,7,8,3,5,8,4,6,1,5,1,6,5,7,2,5,1,4]},{"chain_id":"c00042","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,7,1,2,6,3,6,5,4,7,1,1,4,7,4,8,3,6,1,1]},{"chain_id":"c00043","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,5,3,8,8,6,8,3,5,0,1,2,5,6,5,2,6,1,4,7,8]},{"chain_id":"c00044","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,4,0,0,2,3,4,6,6,0,7,5,2,2,3,7,4,0,0,8]},{"chain_id":"c00045","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,3,0,5,7,3,1,7,1,3,0,5,4,0,6,0,3,2,3,4,7]},{"chain_id":"c00046","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,4,5,5,0,1,1,8,4,4,6,2,5,8,8,7,8,0,8,5,6]},{"chain_id":"c00047","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,0,3,5,1,0,8,5,3,2,3,5,1,8,6,2,6,8,4,7,6]},{"chain_id":"c00048","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,4,4,0,1,6,7,0,4,3,3,2,1,6,7,5,8,7,5,7,7]},{"chain_id":"c00049","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,4,8,2,7,2,7,4,8,8,7,4,0,3,6,6,3,2,1,5,7]},{"chain_id":"c00050","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,2,3,8,3,3,4,2,8,7,0,6,8,4,4,3,0,5,3,3]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 05. b0003_g01_brief

Batch b0003; round 1; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0003_g01_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00051","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,5,8,6,3,1,0,2,4,7,1,6,5,8,5,5,1,8,7,5]},{"chain_id":"c00052","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,3,8,7,0,2,7,4,2,3,1,3,8,5,3,1,3,8,1,4]},{"chain_id":"c00053","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,0,4,8,0,3,8,0,4,6,5,0,0,2,7,1,2,0,2,3,7]},{"chain_id":"c00054","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,2,1,4,6,4,7,2,7,6,8,1,3,5,6,5,1,6,8,5,3]},{"chain_id":"c00055","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,2,5,4,5,0,5,5,5,2,3,8,3,3,6,2,5,0,2,0]},{"chain_id":"c00056","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,5,2,7,6,4,5,3,3,2,6,2,6,2,4,6,2,1,8,3]},{"chain_id":"c00057","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,4,8,0,8,6,1,5,8,2,2,6,8,3,8,2,6,5,5,6]},{"chain_id":"c00058","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,3,1,8,6,7,1,1,1,8,7,2,6,8,2,7,5,1,2,7,2]},{"chain_id":"c00059","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,0,8,5,2,1,1,1,3,6,4,5,2,6,7,7,3,5,5,0,7]},{"chain_id":"c00060","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,8,7,6,1,2,0,1,5,4,1,0,0,2,5,4,6,2,5,8,6]},{"chain_id":"c00061","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,6,8,5,0,4,6,8,7,2,4,5,8,8,2,5,8,7,2,5]},{"chain_id":"c00062","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,2,8,7,6,8,2,6,6,4,3,6,5,4,0,7,3,4,2,4,8]},{"chain_id":"c00063","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,3,4,8,5,7,7,0,7,7,6,3,8,6,7,2,0,2,2,7,3]},{"chain_id":"c00064","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,2,0,6,5,6,6,2,4,4,7,7,6,7,4,6,0,2,5,7]},{"chain_id":"c00065","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,0,4,8,1,6,6,1,5,8,2,4,5,8,1,3,1,5,4,4]},{"chain_id":"c00066","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,7,0,0,2,8,5,8,1,2,1,8,2,3,0,4,0,6,6,0,5]},{"chain_id":"c00067","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,4,2,3,1,8,5,3,3,7,2,7,1,2,2,3,2,2,8,5]},{"chain_id":"c00068","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,5,2,2,5,3,7,8,6,8,8,6,7,6,4,7,1,8,1,5,0]},{"chain_id":"c00069","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,4,7,1,6,7,1,8,1,4,4,6,2,4,8,8,6,2,6,8,4]},{"chain_id":"c00070","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,4,4,8,8,0,4,8,8,6,3,2,6,4,3,4,1,5,8,5]},{"chain_id":"c00071","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,6,6,0,8,7,4,7,8,6,1,1,0,2,3,4,3,2,5,8]},{"chain_id":"c00072","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,8,0,2,5,1,0,8,5,6,6,2,7,8,7,1,2,4,6,7]},{"chain_id":"c00073","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,7,4,7,4,7,8,3,7,7,4,8,6,1,1,2,3,2,8,4]},{"chain_id":"c00074","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,7,5,3,0,6,0,5,3,7,3,1,8,7,8,1,5,4,6,4,0]},{"chain_id":"c00075","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,1,7,3,1,1,7,6,5,1,5,3,0,0,8,4,0,0,8,4]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 06. b0003_g01_ample

Batch b0003; round 1; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0003_g01_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00051","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,5,8,6,3,1,0,2,4,7,1,6,5,8,5,5,1,8,7,5]},{"chain_id":"c00052","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,3,8,7,0,2,7,4,2,3,1,3,8,5,3,1,3,8,1,4]},{"chain_id":"c00053","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,0,4,8,0,3,8,0,4,6,5,0,0,2,7,1,2,0,2,3,7]},{"chain_id":"c00054","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,2,1,4,6,4,7,2,7,6,8,1,3,5,6,5,1,6,8,5,3]},{"chain_id":"c00055","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,2,5,4,5,0,5,5,5,2,3,8,3,3,6,2,5,0,2,0]},{"chain_id":"c00056","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,5,2,7,6,4,5,3,3,2,6,2,6,2,4,6,2,1,8,3]},{"chain_id":"c00057","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,4,8,0,8,6,1,5,8,2,2,6,8,3,8,2,6,5,5,6]},{"chain_id":"c00058","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,3,1,8,6,7,1,1,1,8,7,2,6,8,2,7,5,1,2,7,2]},{"chain_id":"c00059","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,0,8,5,2,1,1,1,3,6,4,5,2,6,7,7,3,5,5,0,7]},{"chain_id":"c00060","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,8,7,6,1,2,0,1,5,4,1,0,0,2,5,4,6,2,5,8,6]},{"chain_id":"c00061","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,6,8,5,0,4,6,8,7,2,4,5,8,8,2,5,8,7,2,5]},{"chain_id":"c00062","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,2,8,7,6,8,2,6,6,4,3,6,5,4,0,7,3,4,2,4,8]},{"chain_id":"c00063","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,3,4,8,5,7,7,0,7,7,6,3,8,6,7,2,0,2,2,7,3]},{"chain_id":"c00064","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,2,0,6,5,6,6,2,4,4,7,7,6,7,4,6,0,2,5,7]},{"chain_id":"c00065","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,0,4,8,1,6,6,1,5,8,2,4,5,8,1,3,1,5,4,4]},{"chain_id":"c00066","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,7,0,0,2,8,5,8,1,2,1,8,2,3,0,4,0,6,6,0,5]},{"chain_id":"c00067","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,4,2,3,1,8,5,3,3,7,2,7,1,2,2,3,2,2,8,5]},{"chain_id":"c00068","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,5,2,2,5,3,7,8,6,8,8,6,7,6,4,7,1,8,1,5,0]},{"chain_id":"c00069","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,4,7,1,6,7,1,8,1,4,4,6,2,4,8,8,6,2,6,8,4]},{"chain_id":"c00070","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,4,4,8,8,0,4,8,8,6,3,2,6,4,3,4,1,5,8,5]},{"chain_id":"c00071","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,6,6,0,8,7,4,7,8,6,1,1,0,2,3,4,3,2,5,8]},{"chain_id":"c00072","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,8,0,2,5,1,0,8,5,6,6,2,7,8,7,1,2,4,6,7]},{"chain_id":"c00073","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,7,4,7,4,7,8,3,7,7,4,8,6,1,1,2,3,2,8,4]},{"chain_id":"c00074","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,7,5,3,0,6,0,5,3,7,3,1,8,7,8,1,5,4,6,4,0]},{"chain_id":"c00075","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,1,7,3,1,1,7,6,5,1,5,3,0,0,8,4,0,0,8,4]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 07. b0004_g01_ample

Batch b0004; round 1; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0004_g01_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00076","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,1,5,2,5,3,7,7,4,5,4,6,5,8,6,0,3,7,6,2]},{"chain_id":"c00077","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,5,7,0,5,3,8,6,0,3,6,1,2,1,4,1,6,1,0,3,0]},{"chain_id":"c00078","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,1,2,1,4,0,5,0,4,7,1,3,5,1,0,4,1,8,1,2]},{"chain_id":"c00079","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,0,3,3,6,2,5,1,4,6,5,6,3,1,8,1,1,2,6,3,3]},{"chain_id":"c00080","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,1,8,1,7,1,1,5,7,5,2,3,2,2,4,8,2,8,1,2,3]},{"chain_id":"c00081","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,8,5,2,0,5,2,6,7,3,4,1,6,8,3,0,0,6,1,2,4]},{"chain_id":"c00082","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,3,1,3,6,7,5,0,2,5,5,4,0,4,5,8,8,4,2,3,5]},{"chain_id":"c00083","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,1,8,2,3,7,8,0,3,5,1,0,4,0,0,5,6,6,3,8]},{"chain_id":"c00084","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,1,8,3,2,7,4,1,0,7,7,2,0,4,2,5,6,4,2,1,4]},{"chain_id":"c00085","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,0,1,8,5,1,2,3,8,4,0,0,7,0,5,6,4,8,0,1,7]},{"chain_id":"c00086","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,2,3,8,5,0,6,1,5,0,7,3,4,5,5,3,3,5,3,5]},{"chain_id":"c00087","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,6,1,5,5,5,7,5,2,3,1,7,8,8,5,6,1,7,6,0,2]},{"chain_id":"c00088","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,3,1,0,5,5,4,2,8,3,6,4,8,8,8,4,8,5,2,8]},{"chain_id":"c00089","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,2,1,7,5,6,7,6,1,1,8,8,1,7,0,6,2,1,2,4,1]},{"chain_id":"c00090","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,1,8,1,5,2,8,8,4,5,0,3,6,8,5,6,1,8,2,4,8]},{"chain_id":"c00091","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,1,7,1,2,5,8,8,4,2,7,3,1,4,4,8,5,4,5,2,4]},{"chain_id":"c00092","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,1,2,7,5,3,7,5,0,6,7,7,0,3,4,4,4,2,7,2,6]},{"chain_id":"c00093","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,1,2,4,0,6,7,3,7,0,7,3,2,5,7,5,3,7,4,7]},{"chain_id":"c00094","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,4,4,4,6,2,6,3,8,4,2,8,4,4,1,2,8,4,2,3]},{"chain_id":"c00095","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,4,3,8,6,6,5,6,5,3,3,8,2,7,3,2,1,3,8,3,4]},{"chain_id":"c00096","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,6,7,3,1,6,3,1,0,4,5,4,8,7,5,1,8,6,0,4,8]},{"chain_id":"c00097","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,5,0,8,6,0,7,2,5,5,5,8,6,1,6,4,2,6,3,4]},{"chain_id":"c00098","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,8,3,7,4,4,0,4,7,4,4,5,5,5,6,3,6,7,3,7]},{"chain_id":"c00099","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,8,5,6,2,3,3,8,6,7,1,6,0,6,7,7,3,4,0,2,8]},{"chain_id":"c00100","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,1,4,6,4,4,4,1,5,1,4,0,5,8,6,1,1,5,4,6]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 08. b0004_g01_brief

Batch b0004; round 1; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0004_g01_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00076","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,1,5,2,5,3,7,7,4,5,4,6,5,8,6,0,3,7,6,2]},{"chain_id":"c00077","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,5,7,0,5,3,8,6,0,3,6,1,2,1,4,1,6,1,0,3,0]},{"chain_id":"c00078","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,1,2,1,4,0,5,0,4,7,1,3,5,1,0,4,1,8,1,2]},{"chain_id":"c00079","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,0,3,3,6,2,5,1,4,6,5,6,3,1,8,1,1,2,6,3,3]},{"chain_id":"c00080","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,1,8,1,7,1,1,5,7,5,2,3,2,2,4,8,2,8,1,2,3]},{"chain_id":"c00081","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,8,5,2,0,5,2,6,7,3,4,1,6,8,3,0,0,6,1,2,4]},{"chain_id":"c00082","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,3,1,3,6,7,5,0,2,5,5,4,0,4,5,8,8,4,2,3,5]},{"chain_id":"c00083","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,1,8,2,3,7,8,0,3,5,1,0,4,0,0,5,6,6,3,8]},{"chain_id":"c00084","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,1,8,3,2,7,4,1,0,7,7,2,0,4,2,5,6,4,2,1,4]},{"chain_id":"c00085","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,0,1,8,5,1,2,3,8,4,0,0,7,0,5,6,4,8,0,1,7]},{"chain_id":"c00086","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,2,3,8,5,0,6,1,5,0,7,3,4,5,5,3,3,5,3,5]},{"chain_id":"c00087","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,6,1,5,5,5,7,5,2,3,1,7,8,8,5,6,1,7,6,0,2]},{"chain_id":"c00088","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,3,1,0,5,5,4,2,8,3,6,4,8,8,8,4,8,5,2,8]},{"chain_id":"c00089","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,2,1,7,5,6,7,6,1,1,8,8,1,7,0,6,2,1,2,4,1]},{"chain_id":"c00090","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,1,8,1,5,2,8,8,4,5,0,3,6,8,5,6,1,8,2,4,8]},{"chain_id":"c00091","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,1,7,1,2,5,8,8,4,2,7,3,1,4,4,8,5,4,5,2,4]},{"chain_id":"c00092","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,1,2,7,5,3,7,5,0,6,7,7,0,3,4,4,4,2,7,2,6]},{"chain_id":"c00093","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,1,2,4,0,6,7,3,7,0,7,3,2,5,7,5,3,7,4,7]},{"chain_id":"c00094","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,4,4,4,6,2,6,3,8,4,2,8,4,4,1,2,8,4,2,3]},{"chain_id":"c00095","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,4,3,8,6,6,5,6,5,3,3,8,2,7,3,2,1,3,8,3,4]},{"chain_id":"c00096","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,6,7,3,1,6,3,1,0,4,5,4,8,7,5,1,8,6,0,4,8]},{"chain_id":"c00097","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,5,0,8,6,0,7,2,5,5,5,8,6,1,6,4,2,6,3,4]},{"chain_id":"c00098","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,8,3,7,4,4,0,4,7,4,4,5,5,5,6,3,6,7,3,7]},{"chain_id":"c00099","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,8,5,6,2,3,3,8,6,7,1,6,0,6,7,7,3,4,0,2,8]},{"chain_id":"c00100","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,1,4,6,4,4,4,1,5,1,4,0,5,8,6,1,1,5,4,6]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 09. b0005_g01_brief

Batch b0005; round 1; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0005_g01_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00101","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,3,3,1,0,7,1,2,3,6,4,1,0,1,7,1,6,4,5,3]},{"chain_id":"c00102","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,1,8,1,1,2,1,2,0,7,8,6,6,7,3,1,4,3,3,4]},{"chain_id":"c00103","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,5,0,1,8,1,6,1,5,4,0,1,3,6,3,4,5,8,4,3]},{"chain_id":"c00104","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,6,7,6,3,8,1,6,5,7,4,8,4,7,1,1,8,6,2,1,3]},{"chain_id":"c00105","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,5,4,1,5,8,6,6,8,1,6,2,4,1,0,5,1,0,0,4,2]},{"chain_id":"c00106","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,2,2,2,6,0,5,5,0,7,4,1,0,3,1,1,8,7,0,2,5]},{"chain_id":"c00107","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,0,4,5,8,6,0,2,5,1,8,6,1,3,6,4,5,8,7,3]},{"chain_id":"c00108","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,2,0,6,1,7,0,7,4,1,1,7,7,1,5,8,7,5,0,1,2]},{"chain_id":"c00109","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,8,5,8,1,3,6,6,1,3,2,3,0,7,1,6,5,2,4,1]},{"chain_id":"c00110","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,8,7,7,4,6,4,2,4,5,5,8,0,0,6,3,6,3,4,5,6]},{"chain_id":"c00111","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,6,4,6,0,7,6,3,0,3,2,0,3,7,8,0,5,0,8,0]},{"chain_id":"c00112","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,4,7,0,4,0,7,0,1,3,7,7,7,8,5,1,3,4,3,6]},{"chain_id":"c00113","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,6,5,3,6,2,6,5,8,2,3,1,8,6,4,2,2,3,0,1]},{"chain_id":"c00114","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,0,5,8,3,7,5,0,2,3,7,4,8,5,1,5,8,6,7,4,8]},{"chain_id":"c00115","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,3,6,1,7,4,3,0,3,0,2,6,1,1,2,7,8,5,3,0]},{"chain_id":"c00116","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,7,5,2,0,0,5,8,8,0,5,0,0,8,3,3,8,3,5,6]},{"chain_id":"c00117","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,5,2,4,1,4,0,2,2,0,4,7,2,8,8,8,3,2,1,8,3]},{"chain_id":"c00118","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,7,6,8,0,0,4,1,4,7,1,7,8,4,8,2,1,3,4,7,3]},{"chain_id":"c00119","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,4,1,1,8,4,7,7,6,2,2,1,5,5,1,6,5,7,3,7]},{"chain_id":"c00120","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,2,8,2,2,8,5,2,0,2,0,2,2,6,4,3,4,4,7,5,5]},{"chain_id":"c00121","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,6,1,2,6,2,0,3,2,0,7,1,0,1,6,5,0,3,0,1,6]},{"chain_id":"c00122","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,3,7,7,8,4,1,2,0,0,6,5,0,6,4,3,8,5,8,5,8]},{"chain_id":"c00123","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,8,7,4,6,3,0,8,4,5,6,2,5,3,2,4,5,0,1,3]},{"chain_id":"c00124","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,3,2,7,7,6,5,5,2,1,4,1,5,8,5,8,5,1,0,3]},{"chain_id":"c00125","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,6,2,8,0,7,1,4,7,3,4,6,3,2,3,6,8,7,6,7]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 10. b0005_g01_ample

Batch b0005; round 1; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0005_g01_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00101","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,3,3,1,0,7,1,2,3,6,4,1,0,1,7,1,6,4,5,3]},{"chain_id":"c00102","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,1,8,1,1,2,1,2,0,7,8,6,6,7,3,1,4,3,3,4]},{"chain_id":"c00103","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,5,0,1,8,1,6,1,5,4,0,1,3,6,3,4,5,8,4,3]},{"chain_id":"c00104","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,6,7,6,3,8,1,6,5,7,4,8,4,7,1,1,8,6,2,1,3]},{"chain_id":"c00105","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,5,4,1,5,8,6,6,8,1,6,2,4,1,0,5,1,0,0,4,2]},{"chain_id":"c00106","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,2,2,2,6,0,5,5,0,7,4,1,0,3,1,1,8,7,0,2,5]},{"chain_id":"c00107","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,0,4,5,8,6,0,2,5,1,8,6,1,3,6,4,5,8,7,3]},{"chain_id":"c00108","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,2,0,6,1,7,0,7,4,1,1,7,7,1,5,8,7,5,0,1,2]},{"chain_id":"c00109","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,8,5,8,1,3,6,6,1,3,2,3,0,7,1,6,5,2,4,1]},{"chain_id":"c00110","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,8,7,7,4,6,4,2,4,5,5,8,0,0,6,3,6,3,4,5,6]},{"chain_id":"c00111","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,6,4,6,0,7,6,3,0,3,2,0,3,7,8,0,5,0,8,0]},{"chain_id":"c00112","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,4,7,0,4,0,7,0,1,3,7,7,7,8,5,1,3,4,3,6]},{"chain_id":"c00113","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,6,5,3,6,2,6,5,8,2,3,1,8,6,4,2,2,3,0,1]},{"chain_id":"c00114","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,0,5,8,3,7,5,0,2,3,7,4,8,5,1,5,8,6,7,4,8]},{"chain_id":"c00115","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,3,6,1,7,4,3,0,3,0,2,6,1,1,2,7,8,5,3,0]},{"chain_id":"c00116","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,7,5,2,0,0,5,8,8,0,5,0,0,8,3,3,8,3,5,6]},{"chain_id":"c00117","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,5,2,4,1,4,0,2,2,0,4,7,2,8,8,8,3,2,1,8,3]},{"chain_id":"c00118","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,7,6,8,0,0,4,1,4,7,1,7,8,4,8,2,1,3,4,7,3]},{"chain_id":"c00119","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,4,1,1,8,4,7,7,6,2,2,1,5,5,1,6,5,7,3,7]},{"chain_id":"c00120","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,2,8,2,2,8,5,2,0,2,0,2,2,6,4,3,4,4,7,5,5]},{"chain_id":"c00121","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,6,1,2,6,2,0,3,2,0,7,1,0,1,6,5,0,3,0,1,6]},{"chain_id":"c00122","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,3,7,7,8,4,1,2,0,0,6,5,0,6,4,3,8,5,8,5,8]},{"chain_id":"c00123","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,8,7,4,6,3,0,8,4,5,6,2,5,3,2,4,5,0,1,3]},{"chain_id":"c00124","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,3,2,7,7,6,5,5,2,1,4,1,5,8,5,8,5,1,0,3]},{"chain_id":"c00125","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,6,2,8,0,7,1,4,7,3,4,6,3,2,3,6,8,7,6,7]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 11. b0001_g02_ample

Batch b0001; round 2; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0001_g02_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00001","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,7,2,4,7,0,1,6,1,6,0,7,8,0,6,1,0,8,6,8]},{"chain_id":"c00002","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,5,1,0,7,7,7,0,6,2,4,0,1,0,0,5,2,3,4,7,5]},{"chain_id":"c00003","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,3,3,2,2,1,7,6,0,8,0,3,3,8,3,1,7,7,8,4]},{"chain_id":"c00004","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,2,0,2,8,7,5,6,2,8,4,0,3,8,1,8,4,5,8,8,5]},{"chain_id":"c00005","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,3,6,1,6,7,7,8,4,7,0,7,7,7,1,4,0,6,5,4,5]},{"chain_id":"c00006","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,8,0,6,7,5,4,7,5,2,3,2,0,2,2,5,1,5,5,0]},{"chain_id":"c00007","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,5,7,3,5,3,6,0,0,6,5,1,4,3,7,3,3,0,1,3]},{"chain_id":"c00008","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,0,5,5,7,7,0,5,2,6,3,5,7,6,7,0,0,7,6,7]},{"chain_id":"c00009","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,8,1,6,3,2,2,7,0,6,4,5,5,7,5,0,1,0,3,2]},{"chain_id":"c00010","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,3,6,3,0,8,5,7,6,8,8,5,5,0,5,0,0,3,2,0,0]},{"chain_id":"c00011","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,7,3,8,8,2,1,4,8,6,5,3,3,3,8,4,0,4,4,3,7]},{"chain_id":"c00012","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,7,5,4,3,6,7,0,8,4,0,5,7,6,5,5,1,4,7,7]},{"chain_id":"c00013","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,2,5,0,6,8,5,5,0,6,4,8,7,2,2,8,1,2,1,1]},{"chain_id":"c00014","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,2,7,7,5,3,4,4,0,2,6,7,4,7,5,7,0,2,5,2]},{"chain_id":"c00015","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,0,1,8,4,5,2,3,8,2,4,3,4,2,8,3,6,6,5,3]},{"chain_id":"c00016","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,4,5,6,3,0,3,0,8,0,2,8,0,3,4,1,6,8,5,0,1]},{"chain_id":"c00017","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,0,0,1,7,0,0,0,5,4,8,1,3,0,4,3,1,2,6,1]},{"chain_id":"c00018","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,5,5,3,7,7,4,1,5,4,8,2,2,6,0,8,3,5,2,5]},{"chain_id":"c00019","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,6,2,6,0,8,0,3,6,3,3,1,3,8,0,1,7,3,2,5,8]},{"chain_id":"c00020","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,3,3,5,6,4,6,8,4,2,7,0,0,5,8,3,0,7,2,8]},{"chain_id":"c00021","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,0,5,7,0,5,8,4,3,0,7,7,6,1,6,7,0,6,8,2]},{"chain_id":"c00022","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,1,1,1,5,4,7,8,1,5,4,8,6,0,8,4,5,8,8,5]},{"chain_id":"c00023","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,3,5,4,1,8,6,0,3,2,5,0,8,8,3,4,0,0,4,1]},{"chain_id":"c00024","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,6,2,1,5,7,4,1,2,0,4,4,8,4,6,2,8,3,0,3]},{"chain_id":"c00025","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,1,4,2,4,1,1,0,1,1,8,7,0,4,7,0,5,3,1,7]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 12. b0001_g02_brief

Batch b0001; round 2; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0001_g02_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00001","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,7,2,4,7,0,1,6,1,6,0,7,8,0,6,1,0,8,6,8]},{"chain_id":"c00002","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,5,1,0,7,7,7,0,6,2,4,0,1,0,0,5,2,3,4,7,5]},{"chain_id":"c00003","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,3,3,2,2,1,7,6,0,8,0,3,3,8,3,1,7,7,8,4]},{"chain_id":"c00004","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,2,0,2,8,7,5,6,2,8,4,0,3,8,1,8,4,5,8,8,5]},{"chain_id":"c00005","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,3,6,1,6,7,7,8,4,7,0,7,7,7,1,4,0,6,5,4,5]},{"chain_id":"c00006","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,8,0,6,7,5,4,7,5,2,3,2,0,2,2,5,1,5,5,0]},{"chain_id":"c00007","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,5,7,3,5,3,6,0,0,6,5,1,4,3,7,3,3,0,1,3]},{"chain_id":"c00008","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,0,5,5,7,7,0,5,2,6,3,5,7,6,7,0,0,7,6,7]},{"chain_id":"c00009","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,8,1,6,3,2,2,7,0,6,4,5,5,7,5,0,1,0,3,2]},{"chain_id":"c00010","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,3,6,3,0,8,5,7,6,8,8,5,5,0,5,0,0,3,2,0,0]},{"chain_id":"c00011","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,7,3,8,8,2,1,4,8,6,5,3,3,3,8,4,0,4,4,3,7]},{"chain_id":"c00012","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,7,5,4,3,6,7,0,8,4,0,5,7,6,5,5,1,4,7,7]},{"chain_id":"c00013","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,2,5,0,6,8,5,5,0,6,4,8,7,2,2,8,1,2,1,1]},{"chain_id":"c00014","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,2,7,7,5,3,4,4,0,2,6,7,4,7,5,7,0,2,5,2]},{"chain_id":"c00015","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,0,1,8,4,5,2,3,8,2,4,3,4,2,8,3,6,6,5,3]},{"chain_id":"c00016","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,4,5,6,3,0,3,0,8,0,2,8,0,3,4,1,6,8,5,0,1]},{"chain_id":"c00017","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,0,0,1,7,0,0,0,5,4,8,1,3,0,4,3,1,2,6,1]},{"chain_id":"c00018","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,5,5,3,7,7,4,1,5,4,8,2,2,6,0,8,3,5,2,5]},{"chain_id":"c00019","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,6,2,6,0,8,0,3,6,3,3,1,3,8,0,1,7,3,2,5,8]},{"chain_id":"c00020","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,3,3,5,6,4,6,8,4,2,7,0,0,5,8,3,0,7,2,8]},{"chain_id":"c00021","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,0,5,7,0,5,8,4,3,0,7,7,6,1,6,7,0,6,8,2]},{"chain_id":"c00022","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,1,1,1,5,4,7,8,1,5,4,8,6,0,8,4,5,8,8,5]},{"chain_id":"c00023","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,3,5,4,1,8,6,0,3,2,5,0,8,8,3,4,0,0,4,1]},{"chain_id":"c00024","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,6,2,1,5,7,4,1,2,0,4,4,8,4,6,2,8,3,0,3]},{"chain_id":"c00025","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,1,4,2,4,1,1,0,1,1,8,7,0,4,7,0,5,3,1,7]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 13. b0002_g02_brief

Batch b0002; round 2; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0002_g02_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00026","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,3,5,6,2,0,0,3,7,4,4,8,8,1,5,4,2,2,1,3,5]},{"chain_id":"c00027","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,3,2,4,1,4,6,3,3,8,5,6,4,4,4,3,2,5,3,7,7]},{"chain_id":"c00028","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,1,4,3,5,6,4,4,3,8,0,4,5,6,3,2,4,1,6,4]},{"chain_id":"c00029","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,5,8,7,8,3,2,4,3,1,6,4,3,8,4,6,1,6,6,0,3]},{"chain_id":"c00030","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,0,4,2,1,4,3,2,7,4,6,0,2,4,6,7,1,6,7,3,8]},{"chain_id":"c00031","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,8,4,1,8,5,2,0,6,1,6,4,5,6,1,7,3,6,3,8,5]},{"chain_id":"c00032","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,1,8,4,7,7,2,4,2,2,4,0,8,0,1,0,5,2,1,5]},{"chain_id":"c00033","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,4,1,7,8,8,6,0,6,5,8,1,3,1,4,7,4,4,1,0,7]},{"chain_id":"c00034","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,3,5,6,0,4,8,1,0,0,2,0,0,0,1,8,6,2,7,4,6]},{"chain_id":"c00035","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,8,8,1,4,4,3,6,0,1,6,5,6,5,1,2,1,7,2,3,4]},{"chain_id":"c00036","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,8,0,7,7,1,1,2,1,8,3,0,6,8,1,6,2,8,7,5]},{"chain_id":"c00037","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,6,6,5,6,1,3,2,7,2,0,7,8,2,0,1,0,8,6,5,1]},{"chain_id":"c00038","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,3,2,4,1,5,0,4,8,2,1,8,7,5,4,8,1,6,2,6,8]},{"chain_id":"c00039","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,5,6,8,4,6,3,0,7,4,8,4,0,7,8,5,7,1,4,7,2]},{"chain_id":"c00040","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,0,1,4,7,3,8,7,1,6,1,8,6,1,3,5,0,5,8,6]},{"chain_id":"c00041","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,5,4,7,8,3,5,8,4,6,1,5,1,6,5,7,2,5,1,4]},{"chain_id":"c00042","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,7,1,2,6,3,6,5,4,7,1,1,4,7,4,8,3,6,1,1]},{"chain_id":"c00043","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,5,3,8,8,6,8,3,5,0,1,2,5,6,5,2,6,1,4,7,8]},{"chain_id":"c00044","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,4,0,0,2,3,4,6,6,0,7,5,2,2,3,7,4,0,0,8]},{"chain_id":"c00045","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,3,0,5,7,3,1,7,1,3,0,5,4,0,6,0,3,2,3,4,7]},{"chain_id":"c00046","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,4,5,5,0,1,1,8,4,4,6,2,5,8,8,7,8,0,8,5,6]},{"chain_id":"c00047","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,0,3,5,1,0,8,5,3,2,3,5,1,8,6,2,6,8,4,7,6]},{"chain_id":"c00048","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,4,4,0,1,6,7,0,4,3,3,2,1,6,7,5,8,7,5,7,7]},{"chain_id":"c00049","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,4,8,2,7,2,7,4,8,8,7,4,0,3,6,6,3,2,1,5,7]},{"chain_id":"c00050","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,2,3,8,3,3,4,2,8,7,0,6,8,4,4,3,0,5,3,3]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 14. b0002_g02_ample

Batch b0002; round 2; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0002_g02_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00026","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,3,5,6,2,0,0,3,7,4,4,8,8,1,5,4,2,2,1,3,5]},{"chain_id":"c00027","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,3,2,4,1,4,6,3,3,8,5,6,4,4,4,3,2,5,3,7,7]},{"chain_id":"c00028","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,1,4,3,5,6,4,4,3,8,0,4,5,6,3,2,4,1,6,4]},{"chain_id":"c00029","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,5,8,7,8,3,2,4,3,1,6,4,3,8,4,6,1,6,6,0,3]},{"chain_id":"c00030","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,0,4,2,1,4,3,2,7,4,6,0,2,4,6,7,1,6,7,3,8]},{"chain_id":"c00031","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,8,4,1,8,5,2,0,6,1,6,4,5,6,1,7,3,6,3,8,5]},{"chain_id":"c00032","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,1,8,4,7,7,2,4,2,2,4,0,8,0,1,0,5,2,1,5]},{"chain_id":"c00033","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,4,1,7,8,8,6,0,6,5,8,1,3,1,4,7,4,4,1,0,7]},{"chain_id":"c00034","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,3,5,6,0,4,8,1,0,0,2,0,0,0,1,8,6,2,7,4,6]},{"chain_id":"c00035","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,8,8,1,4,4,3,6,0,1,6,5,6,5,1,2,1,7,2,3,4]},{"chain_id":"c00036","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,8,0,7,7,1,1,2,1,8,3,0,6,8,1,6,2,8,7,5]},{"chain_id":"c00037","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,6,6,5,6,1,3,2,7,2,0,7,8,2,0,1,0,8,6,5,1]},{"chain_id":"c00038","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,3,2,4,1,5,0,4,8,2,1,8,7,5,4,8,1,6,2,6,8]},{"chain_id":"c00039","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,5,6,8,4,6,3,0,7,4,8,4,0,7,8,5,7,1,4,7,2]},{"chain_id":"c00040","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,0,1,4,7,3,8,7,1,6,1,8,6,1,3,5,0,5,8,6]},{"chain_id":"c00041","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,5,4,7,8,3,5,8,4,6,1,5,1,6,5,7,2,5,1,4]},{"chain_id":"c00042","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,7,1,2,6,3,6,5,4,7,1,1,4,7,4,8,3,6,1,1]},{"chain_id":"c00043","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,5,3,8,8,6,8,3,5,0,1,2,5,6,5,2,6,1,4,7,8]},{"chain_id":"c00044","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,4,0,0,2,3,4,6,6,0,7,5,2,2,3,7,4,0,0,8]},{"chain_id":"c00045","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,3,0,5,7,3,1,7,1,3,0,5,4,0,6,0,3,2,3,4,7]},{"chain_id":"c00046","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,4,5,5,0,1,1,8,4,4,6,2,5,8,8,7,8,0,8,5,6]},{"chain_id":"c00047","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,0,3,5,1,0,8,5,3,2,3,5,1,8,6,2,6,8,4,7,6]},{"chain_id":"c00048","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,4,4,0,1,6,7,0,4,3,3,2,1,6,7,5,8,7,5,7,7]},{"chain_id":"c00049","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,4,8,2,7,2,7,4,8,8,7,4,0,3,6,6,3,2,1,5,7]},{"chain_id":"c00050","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,2,3,8,3,3,4,2,8,7,0,6,8,4,4,3,0,5,3,3]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 15. b0003_g02_ample

Batch b0003; round 2; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0003_g02_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00051","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,5,8,6,3,1,0,2,4,7,1,6,5,8,5,5,1,8,7,5]},{"chain_id":"c00052","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,3,8,7,0,2,7,4,2,3,1,3,8,5,3,1,3,8,1,4]},{"chain_id":"c00053","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,0,4,8,0,3,8,0,4,6,5,0,0,2,7,1,2,0,2,3,7]},{"chain_id":"c00054","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,2,1,4,6,4,7,2,7,6,8,1,3,5,6,5,1,6,8,5,3]},{"chain_id":"c00055","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,2,5,4,5,0,5,5,5,2,3,8,3,3,6,2,5,0,2,0]},{"chain_id":"c00056","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,5,2,7,6,4,5,3,3,2,6,2,6,2,4,6,2,1,8,3]},{"chain_id":"c00057","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,4,8,0,8,6,1,5,8,2,2,6,8,3,8,2,6,5,5,6]},{"chain_id":"c00058","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,3,1,8,6,7,1,1,1,8,7,2,6,8,2,7,5,1,2,7,2]},{"chain_id":"c00059","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,0,8,5,2,1,1,1,3,6,4,5,2,6,7,7,3,5,5,0,7]},{"chain_id":"c00060","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,8,7,6,1,2,0,1,5,4,1,0,0,2,5,4,6,2,5,8,6]},{"chain_id":"c00061","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,6,8,5,0,4,6,8,7,2,4,5,8,8,2,5,8,7,2,5]},{"chain_id":"c00062","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,2,8,7,6,8,2,6,6,4,3,6,5,4,0,7,3,4,2,4,8]},{"chain_id":"c00063","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,3,4,8,5,7,7,0,7,7,6,3,8,6,7,2,0,2,2,7,3]},{"chain_id":"c00064","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,2,0,6,5,6,6,2,4,4,7,7,6,7,4,6,0,2,5,7]},{"chain_id":"c00065","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,0,4,8,1,6,6,1,5,8,2,4,5,8,1,3,1,5,4,4]},{"chain_id":"c00066","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,7,0,0,2,8,5,8,1,2,1,8,2,3,0,4,0,6,6,0,5]},{"chain_id":"c00067","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,4,2,3,1,8,5,3,3,7,2,7,1,2,2,3,2,2,8,5]},{"chain_id":"c00068","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,5,2,2,5,3,7,8,6,8,8,6,7,6,4,7,1,8,1,5,0]},{"chain_id":"c00069","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,4,7,1,6,7,1,8,1,4,4,6,2,4,8,8,6,2,6,8,4]},{"chain_id":"c00070","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,4,4,8,8,0,4,8,8,6,3,2,6,4,3,4,1,5,8,5]},{"chain_id":"c00071","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,6,6,0,8,7,4,7,8,6,1,1,0,2,3,4,3,2,5,8]},{"chain_id":"c00072","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,8,0,2,5,1,0,8,5,6,6,2,7,8,7,1,2,4,6,7]},{"chain_id":"c00073","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,7,4,7,4,7,8,3,7,7,4,8,6,1,1,2,3,2,8,4]},{"chain_id":"c00074","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,7,5,3,0,6,0,5,3,7,3,1,8,7,8,1,5,4,6,4,0]},{"chain_id":"c00075","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,1,7,3,1,1,7,6,5,1,5,3,0,0,8,4,0,0,8,4]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 16. b0003_g02_brief

Batch b0003; round 2; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0003_g02_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00051","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,5,8,6,3,1,0,2,4,7,1,6,5,8,5,5,1,8,7,5]},{"chain_id":"c00052","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,3,8,7,0,2,7,4,2,3,1,3,8,5,3,1,3,8,1,4]},{"chain_id":"c00053","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,0,4,8,0,3,8,0,4,6,5,0,0,2,7,1,2,0,2,3,7]},{"chain_id":"c00054","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,2,1,4,6,4,7,2,7,6,8,1,3,5,6,5,1,6,8,5,3]},{"chain_id":"c00055","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,8,2,5,4,5,0,5,5,5,2,3,8,3,3,6,2,5,0,2,0]},{"chain_id":"c00056","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,5,2,7,6,4,5,3,3,2,6,2,6,2,4,6,2,1,8,3]},{"chain_id":"c00057","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,4,8,0,8,6,1,5,8,2,2,6,8,3,8,2,6,5,5,6]},{"chain_id":"c00058","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,3,1,8,6,7,1,1,1,8,7,2,6,8,2,7,5,1,2,7,2]},{"chain_id":"c00059","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,0,8,5,2,1,1,1,3,6,4,5,2,6,7,7,3,5,5,0,7]},{"chain_id":"c00060","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,8,7,6,1,2,0,1,5,4,1,0,0,2,5,4,6,2,5,8,6]},{"chain_id":"c00061","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,6,8,5,0,4,6,8,7,2,4,5,8,8,2,5,8,7,2,5]},{"chain_id":"c00062","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,2,8,7,6,8,2,6,6,4,3,6,5,4,0,7,3,4,2,4,8]},{"chain_id":"c00063","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,3,4,8,5,7,7,0,7,7,6,3,8,6,7,2,0,2,2,7,3]},{"chain_id":"c00064","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,2,0,6,5,6,6,2,4,4,7,7,6,7,4,6,0,2,5,7]},{"chain_id":"c00065","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,0,4,8,1,6,6,1,5,8,2,4,5,8,1,3,1,5,4,4]},{"chain_id":"c00066","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,7,0,0,2,8,5,8,1,2,1,8,2,3,0,4,0,6,6,0,5]},{"chain_id":"c00067","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,4,2,3,1,8,5,3,3,7,2,7,1,2,2,3,2,2,8,5]},{"chain_id":"c00068","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,5,2,2,5,3,7,8,6,8,8,6,7,6,4,7,1,8,1,5,0]},{"chain_id":"c00069","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,4,7,1,6,7,1,8,1,4,4,6,2,4,8,8,6,2,6,8,4]},{"chain_id":"c00070","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,4,4,8,8,0,4,8,8,6,3,2,6,4,3,4,1,5,8,5]},{"chain_id":"c00071","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,6,6,0,8,7,4,7,8,6,1,1,0,2,3,4,3,2,5,8]},{"chain_id":"c00072","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,8,0,2,5,1,0,8,5,6,6,2,7,8,7,1,2,4,6,7]},{"chain_id":"c00073","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,7,4,7,4,7,8,3,7,7,4,8,6,1,1,2,3,2,8,4]},{"chain_id":"c00074","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,7,5,3,0,6,0,5,3,7,3,1,8,7,8,1,5,4,6,4,0]},{"chain_id":"c00075","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,8,1,7,3,1,1,7,6,5,1,5,3,0,0,8,4,0,0,8,4]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 17. b0004_g02_brief

Batch b0004; round 2; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0004_g02_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00076","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,1,5,2,5,3,7,7,4,5,4,6,5,8,6,0,3,7,6,2]},{"chain_id":"c00077","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,5,7,0,5,3,8,6,0,3,6,1,2,1,4,1,6,1,0,3,0]},{"chain_id":"c00078","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,1,2,1,4,0,5,0,4,7,1,3,5,1,0,4,1,8,1,2]},{"chain_id":"c00079","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,0,3,3,6,2,5,1,4,6,5,6,3,1,8,1,1,2,6,3,3]},{"chain_id":"c00080","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,1,8,1,7,1,1,5,7,5,2,3,2,2,4,8,2,8,1,2,3]},{"chain_id":"c00081","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,8,5,2,0,5,2,6,7,3,4,1,6,8,3,0,0,6,1,2,4]},{"chain_id":"c00082","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,3,1,3,6,7,5,0,2,5,5,4,0,4,5,8,8,4,2,3,5]},{"chain_id":"c00083","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,1,8,2,3,7,8,0,3,5,1,0,4,0,0,5,6,6,3,8]},{"chain_id":"c00084","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,1,8,3,2,7,4,1,0,7,7,2,0,4,2,5,6,4,2,1,4]},{"chain_id":"c00085","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,0,1,8,5,1,2,3,8,4,0,0,7,0,5,6,4,8,0,1,7]},{"chain_id":"c00086","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,2,3,8,5,0,6,1,5,0,7,3,4,5,5,3,3,5,3,5]},{"chain_id":"c00087","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,6,1,5,5,5,7,5,2,3,1,7,8,8,5,6,1,7,6,0,2]},{"chain_id":"c00088","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,3,1,0,5,5,4,2,8,3,6,4,8,8,8,4,8,5,2,8]},{"chain_id":"c00089","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,2,1,7,5,6,7,6,1,1,8,8,1,7,0,6,2,1,2,4,1]},{"chain_id":"c00090","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,1,8,1,5,2,8,8,4,5,0,3,6,8,5,6,1,8,2,4,8]},{"chain_id":"c00091","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,1,7,1,2,5,8,8,4,2,7,3,1,4,4,8,5,4,5,2,4]},{"chain_id":"c00092","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,1,2,7,5,3,7,5,0,6,7,7,0,3,4,4,4,2,7,2,6]},{"chain_id":"c00093","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,1,2,4,0,6,7,3,7,0,7,3,2,5,7,5,3,7,4,7]},{"chain_id":"c00094","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,4,4,4,6,2,6,3,8,4,2,8,4,4,1,2,8,4,2,3]},{"chain_id":"c00095","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,4,3,8,6,6,5,6,5,3,3,8,2,7,3,2,1,3,8,3,4]},{"chain_id":"c00096","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,6,7,3,1,6,3,1,0,4,5,4,8,7,5,1,8,6,0,4,8]},{"chain_id":"c00097","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,5,0,8,6,0,7,2,5,5,5,8,6,1,6,4,2,6,3,4]},{"chain_id":"c00098","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,8,3,7,4,4,0,4,7,4,4,5,5,5,6,3,6,7,3,7]},{"chain_id":"c00099","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,8,5,6,2,3,3,8,6,7,1,6,0,6,7,7,3,4,0,2,8]},{"chain_id":"c00100","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,1,4,6,4,4,4,1,5,1,4,0,5,8,6,1,1,5,4,6]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 18. b0004_g02_ample

Batch b0004; round 2; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0004_g02_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00076","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,1,1,5,2,5,3,7,7,4,5,4,6,5,8,6,0,3,7,6,2]},{"chain_id":"c00077","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,5,7,0,5,3,8,6,0,3,6,1,2,1,4,1,6,1,0,3,0]},{"chain_id":"c00078","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,1,2,1,4,0,5,0,4,7,1,3,5,1,0,4,1,8,1,2]},{"chain_id":"c00079","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,0,3,3,6,2,5,1,4,6,5,6,3,1,8,1,1,2,6,3,3]},{"chain_id":"c00080","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,1,8,1,7,1,1,5,7,5,2,3,2,2,4,8,2,8,1,2,3]},{"chain_id":"c00081","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,8,5,2,0,5,2,6,7,3,4,1,6,8,3,0,0,6,1,2,4]},{"chain_id":"c00082","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,3,1,3,6,7,5,0,2,5,5,4,0,4,5,8,8,4,2,3,5]},{"chain_id":"c00083","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,0,1,8,2,3,7,8,0,3,5,1,0,4,0,0,5,6,6,3,8]},{"chain_id":"c00084","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,1,8,3,2,7,4,1,0,7,7,2,0,4,2,5,6,4,2,1,4]},{"chain_id":"c00085","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,0,1,8,5,1,2,3,8,4,0,0,7,0,5,6,4,8,0,1,7]},{"chain_id":"c00086","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,2,3,8,5,0,6,1,5,0,7,3,4,5,5,3,3,5,3,5]},{"chain_id":"c00087","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,6,1,5,5,5,7,5,2,3,1,7,8,8,5,6,1,7,6,0,2]},{"chain_id":"c00088","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,4,3,1,0,5,5,4,2,8,3,6,4,8,8,8,4,8,5,2,8]},{"chain_id":"c00089","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,2,1,7,5,6,7,6,1,1,8,8,1,7,0,6,2,1,2,4,1]},{"chain_id":"c00090","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,1,8,1,5,2,8,8,4,5,0,3,6,8,5,6,1,8,2,4,8]},{"chain_id":"c00091","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,1,7,1,2,5,8,8,4,2,7,3,1,4,4,8,5,4,5,2,4]},{"chain_id":"c00092","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,1,2,7,5,3,7,5,0,6,7,7,0,3,4,4,4,2,7,2,6]},{"chain_id":"c00093","profile_ids":["methodical_concerned","flexible_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,1,2,4,0,6,7,3,7,0,7,3,2,5,7,5,3,7,4,7]},{"chain_id":"c00094","profile_ids":["flexible_concerned","methodical_calm","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,6,4,4,4,6,2,6,3,8,4,2,8,4,4,1,2,8,4,2,3]},{"chain_id":"c00095","profile_ids":["methodical_calm","flexible_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,4,3,8,6,6,5,6,5,3,3,8,2,7,3,2,1,3,8,3,4]},{"chain_id":"c00096","profile_ids":["flexible_calm","methodical_concerned","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,6,7,3,1,6,3,1,0,4,5,4,8,7,5,1,8,6,0,4,8]},{"chain_id":"c00097","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,0,5,0,8,6,0,7,2,5,5,5,8,6,1,6,4,2,6,3,4]},{"chain_id":"c00098","profile_ids":["flexible_concerned","flexible_calm","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,2,8,3,7,4,4,0,4,7,4,4,5,5,5,6,3,6,7,3,7]},{"chain_id":"c00099","profile_ids":["flexible_calm","methodical_concerned","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,8,5,6,2,3,3,8,6,7,1,6,0,6,7,7,3,4,0,2,8]},{"chain_id":"c00100","profile_ids":["methodical_concerned","methodical_calm","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,2,1,4,6,4,4,4,1,5,1,4,0,5,8,6,1,1,5,4,6]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 19. b0005_g02_ample

Batch b0005; round 2; 180-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 180 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0005_g02_ample","deadline_seconds":180,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00101","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,3,3,1,0,7,1,2,3,6,4,1,0,1,7,1,6,4,5,3]},{"chain_id":"c00102","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,1,8,1,1,2,1,2,0,7,8,6,6,7,3,1,4,3,3,4]},{"chain_id":"c00103","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,5,0,1,8,1,6,1,5,4,0,1,3,6,3,4,5,8,4,3]},{"chain_id":"c00104","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,6,7,6,3,8,1,6,5,7,4,8,4,7,1,1,8,6,2,1,3]},{"chain_id":"c00105","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,5,4,1,5,8,6,6,8,1,6,2,4,1,0,5,1,0,0,4,2]},{"chain_id":"c00106","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,2,2,2,6,0,5,5,0,7,4,1,0,3,1,1,8,7,0,2,5]},{"chain_id":"c00107","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,0,4,5,8,6,0,2,5,1,8,6,1,3,6,4,5,8,7,3]},{"chain_id":"c00108","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,2,0,6,1,7,0,7,4,1,1,7,7,1,5,8,7,5,0,1,2]},{"chain_id":"c00109","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,8,5,8,1,3,6,6,1,3,2,3,0,7,1,6,5,2,4,1]},{"chain_id":"c00110","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,8,7,7,4,6,4,2,4,5,5,8,0,0,6,3,6,3,4,5,6]},{"chain_id":"c00111","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,6,4,6,0,7,6,3,0,3,2,0,3,7,8,0,5,0,8,0]},{"chain_id":"c00112","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,4,7,0,4,0,7,0,1,3,7,7,7,8,5,1,3,4,3,6]},{"chain_id":"c00113","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,6,5,3,6,2,6,5,8,2,3,1,8,6,4,2,2,3,0,1]},{"chain_id":"c00114","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,0,5,8,3,7,5,0,2,3,7,4,8,5,1,5,8,6,7,4,8]},{"chain_id":"c00115","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,3,6,1,7,4,3,0,3,0,2,6,1,1,2,7,8,5,3,0]},{"chain_id":"c00116","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,7,5,2,0,0,5,8,8,0,5,0,0,8,3,3,8,3,5,6]},{"chain_id":"c00117","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,5,2,4,1,4,0,2,2,0,4,7,2,8,8,8,3,2,1,8,3]},{"chain_id":"c00118","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,7,6,8,0,0,4,1,4,7,1,7,8,4,8,2,1,3,4,7,3]},{"chain_id":"c00119","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,4,1,1,8,4,7,7,6,2,2,1,5,5,1,6,5,7,3,7]},{"chain_id":"c00120","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,2,8,2,2,8,5,2,0,2,0,2,2,6,4,3,4,4,7,5,5]},{"chain_id":"c00121","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,6,1,2,6,2,0,3,2,0,7,1,0,1,6,5,0,3,0,1,6]},{"chain_id":"c00122","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,3,7,7,8,4,1,2,0,0,6,5,0,6,4,3,8,5,8,5,8]},{"chain_id":"c00123","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,8,7,4,6,3,0,8,4,5,6,2,5,3,2,4,5,0,1,3]},{"chain_id":"c00124","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,3,2,7,7,6,5,5,2,1,4,1,5,8,5,8,5,1,0,3]},{"chain_id":"c00125","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,6,2,8,0,7,1,4,7,3,4,6,3,2,3,6,8,7,6,7]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

## 20. b0005_g02_brief

Batch b0005; round 2; 10-second scenario. Generates 25 teams' weekly orders and matched-state answers.

```text
Simulate the Beer Game decisions of the fictional student cohort specified below.
For each assigned participant, act as a hypothetical second-year undergraduate
business student at the University at Buffalo, with introductory business knowledge,
no prior Beer Game experience and no specialist inventory training. Use the assigned
personality consistently. Try to minimize the team's inventory and backlog costs.
These are fictional students. Do not invent demographic traits, deliberate mistakes,
a particular bias, a desired treatment effect, or artificial variation. Identical
choices and zero orders are allowed. Do not target any aggregate result.

GAME RULES
The four positions, in fixed array order, are retailer, wholesaler, distributor,
factory. Each week each position orders a nonnegative integer number of cases from
its supplier; the factory starts production. There is no suggested order or maximum,
revenue, ordering fee, bulk discount or capacity limit. Holding cost is $0.50 per
remaining case per week; backlog cost is $1 per unfilled case per week.

Each week: receive deliveries; observe incoming demand; ship as much as available
toward old backlog plus new demand; assess costs; then submit this week's orders.
Backlog persists and already includes unfilled current demand. Outstanding orders
cannot be canceled and are not inventory. A new order reaches the supplier next week
and dispatched cases take two more weeks to arrive. Earliest arrival is t+3, later
when suppliers have shortages. Factory production started at t arrives at t+3.
New orders cannot change today's shipments. Track each chain separately.

Initially each role has inventory 12, backlog 0 and outstanding cases 12. The retailer,
wholesaler and distributor each have deliveries [4,4] due over the next two weeks and
another 4 outstanding cases awaiting dispatch. Factory production completions are
[4,4,4] over the next three weeks. Incoming orders at each upstream role initially
equal 4. Weeks 1-4 have customer demand 4 and automatically order 4 at every role.
Subsequent customer demand is iid uniform integers 0 through 8; use the exact supplied
realization for each chain. Generate only the requested post-practice weekly orders.
After the final submitted week, 12 automatic weeks are scored with customer demand
held at its last value and each role's order held at its own last submitted quantity.

Each simulated student may use its local state, its own prior rounds, and all four
remaining inventories. Other roles' orders/backlogs, future customer demand, and
the final decision week are not information available to the fictional student.
You, the cohort generator, see paths and the output horizon to construct the data;
do not intentionally give that future information to the fictional decision maker.
This instruction cannot create actual information isolation between generated roles.
You may use arithmetic or code to track physical state and format the answer, but
do not substitute a single optimized policy for all student choices.

MATCHED-STATE QUESTIONS
For each role also give two independent order choices, separate from game history.
Both displays have week 12, demand 8, received 4, shipped 4, inventory 0, backlog 8,
awaiting_dispatch 0, and no past rounds. Shared inventory is 0 at the focal role
and 12 at the other roles. The first display has deliveries_due [4,4]; the second
has [16,16]. Apply the same assigned personality. Do not change any other quantity.


CLASSROOM SITUATION
The student has 10 seconds from seeing each decision display to submitting its order. The order is final when submitted. Represent the choice the described student would make within that deadline.
This describes the fictional student; it does not impose or measure chat-model computation time.

OUTPUT
Produce the complete weekly trajectories and matched-state choices for this one
classroom situation. Start each chain from the stated initial physical state.
Return only JSON. No code, reasoning, costs, summary statistics or hypothesis claims.
The root fields must be exactly schema_version, study_id, task_id, deadline_seconds,
rules, chains and complete. Use the exact identifiers and deadline below.
rules must answer the three supplied questions: the backlog answer is a JSON
Boolean (true or false); the two other answers are JSON numbers. Do not quote
answers or add Week/currency units. Each chain has exactly chain_id, orders and
probes. orders has one [retailer, wholesaler, distributor, factory] row per output
week. probes has four [first_display_order, second_display_order] rows in role
order. Every order is a nonnegative integer, not a string, float, Boolean or null.
Include every assigned chain once, no missing weeks or ellipses. complete is true
only for a full response. Do not return another condition's choices.

FROZEN INPUT DATA:
{"schema_version":"deadline-cohort-trajectories-v1","study_id":"deadline_cohort_2800524c9b2e0729","task_id":"b0005_g02_brief","deadline_seconds":10,"role_order":["retailer","wholesaler","distributor","factory"],"output_weeks":[5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],"participant_profiles":{"methodical_calm":{"id":"methodical_calm","label":"Methodical, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"methodical_concerned":{"id":"methodical_concerned","label":"Methodical, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are organized, dependable, and prefer working systematically. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_calm":{"id":"flexible_calm","label":"Flexible, emotionally steady","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You usually remain emotionally steady when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."},"flexible_concerned":{"id":"flexible_concerned","label":"Flexible, uncertainty-sensitive","status":"Fictional experimental profile; not measured from UB students","background":"Second-year undergraduate business student at the University at Buffalo; introductory business coursework; no prior Beer Game experience or specialist inventory training.","description":"In ordinary coursework you are flexible, informal, and prefer adapting as you go. You tend to feel concerned when a classroom task is uncertain. These preferences describe your personality; they do not prescribe any particular ordering strategy or decision."}},"chains":[{"chain_id":"c00101","profile_ids":["flexible_calm","flexible_concerned","methodical_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,3,3,1,0,7,1,2,3,6,4,1,0,1,7,1,6,4,5,3]},{"chain_id":"c00102","profile_ids":["flexible_concerned","methodical_concerned","methodical_calm","flexible_calm"],"customer_demand":[4,4,4,4,7,1,8,1,1,2,1,2,0,7,8,6,6,7,3,1,4,3,3,4]},{"chain_id":"c00103","profile_ids":["methodical_concerned","methodical_calm","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,5,0,1,8,1,6,1,5,4,0,1,3,6,3,4,5,8,4,3]},{"chain_id":"c00104","profile_ids":["methodical_calm","flexible_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,6,7,6,3,8,1,6,5,7,4,8,4,7,1,1,8,6,2,1,3]},{"chain_id":"c00105","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,5,4,1,5,8,6,6,8,1,6,2,4,1,0,5,1,0,0,4,2]},{"chain_id":"c00106","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,2,2,2,6,0,5,5,0,7,4,1,0,3,1,1,8,7,0,2,5]},{"chain_id":"c00107","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,0,4,5,8,6,0,2,5,1,8,6,1,3,6,4,5,8,7,3]},{"chain_id":"c00108","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,2,0,6,1,7,0,7,4,1,1,7,7,1,5,8,7,5,0,1,2]},{"chain_id":"c00109","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,7,8,5,8,1,3,6,6,1,3,2,3,0,7,1,6,5,2,4,1]},{"chain_id":"c00110","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,8,7,7,4,6,4,2,4,5,5,8,0,0,6,3,6,3,4,5,6]},{"chain_id":"c00111","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,7,6,4,6,0,7,6,3,0,3,2,0,3,7,8,0,5,0,8,0]},{"chain_id":"c00112","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,7,4,7,0,4,0,7,0,1,3,7,7,7,8,5,1,3,4,3,6]},{"chain_id":"c00113","profile_ids":["flexible_calm","flexible_concerned","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,6,5,3,6,2,6,5,8,2,3,1,8,6,4,2,2,3,0,1]},{"chain_id":"c00114","profile_ids":["flexible_concerned","methodical_calm","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,0,5,8,3,7,5,0,2,3,7,4,8,5,1,5,8,6,7,4,8]},{"chain_id":"c00115","profile_ids":["methodical_calm","methodical_concerned","flexible_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,3,6,1,7,4,3,0,3,0,2,6,1,1,2,7,8,5,3,0]},{"chain_id":"c00116","profile_ids":["methodical_concerned","flexible_calm","flexible_concerned","methodical_calm"],"customer_demand":[4,4,4,4,3,7,5,2,0,0,5,8,8,0,5,0,0,8,3,3,8,3,5,6]},{"chain_id":"c00117","profile_ids":["methodical_calm","methodical_concerned","flexible_concerned","flexible_calm"],"customer_demand":[4,4,4,4,5,2,4,1,4,0,2,2,0,4,7,2,8,8,8,3,2,1,8,3]},{"chain_id":"c00118","profile_ids":["methodical_concerned","flexible_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,7,6,8,0,0,4,1,4,7,1,7,8,4,8,2,1,3,4,7,3]},{"chain_id":"c00119","profile_ids":["flexible_concerned","flexible_calm","methodical_calm","methodical_concerned"],"customer_demand":[4,4,4,4,2,4,1,1,8,4,7,7,6,2,2,1,5,5,1,6,5,7,3,7]},{"chain_id":"c00120","profile_ids":["flexible_calm","methodical_calm","methodical_concerned","flexible_concerned"],"customer_demand":[4,4,4,4,2,8,2,2,8,5,2,0,2,0,2,2,6,4,3,4,4,7,5,5]},{"chain_id":"c00121","profile_ids":["methodical_calm","flexible_concerned","methodical_concerned","flexible_calm"],"customer_demand":[4,4,4,4,6,1,2,6,2,0,3,2,0,7,1,0,1,6,5,0,3,0,1,6]},{"chain_id":"c00122","profile_ids":["flexible_concerned","methodical_concerned","flexible_calm","methodical_calm"],"customer_demand":[4,4,4,4,3,7,7,8,4,1,2,0,0,6,5,0,6,4,3,8,5,8,5,8]},{"chain_id":"c00123","profile_ids":["methodical_concerned","flexible_calm","methodical_calm","flexible_concerned"],"customer_demand":[4,4,4,4,6,8,7,4,6,3,0,8,4,5,6,2,5,3,2,4,5,0,1,3]},{"chain_id":"c00124","profile_ids":["flexible_calm","methodical_calm","flexible_concerned","methodical_concerned"],"customer_demand":[4,4,4,4,1,3,2,7,7,6,5,5,2,1,4,1,5,8,5,8,5,1,0,3]},{"chain_id":"c00125","profile_ids":["methodical_calm","flexible_concerned","flexible_calm","methodical_concerned"],"customer_demand":[4,4,4,4,5,6,2,8,0,7,1,4,7,3,4,6,3,2,3,6,8,7,6,7]}],"rules_questions":{"backlog_includes_current_unfilled_demand":"Does current backlog already include unfilled demand from this week?","factory_order_week_7_arrival_week":"When does factory production started in week 7 arrive?","three_week_backlog_cost":"What is the cost of five backlogged cases at the end of each of three weeks?"}}
```

