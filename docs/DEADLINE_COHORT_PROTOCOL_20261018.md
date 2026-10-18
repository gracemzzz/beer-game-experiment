# Independent deadline-framing rerun — 18 October 2026

The user requested a fresh full-game study using the pressure prompts tested in twelve isolated assistant contexts. This protocol is a new study, not a replacement or reanalysis that changes earlier accepted responses. The earlier 500-identity initial/revision sample and both prompt-development sets remain preserved.

## Intervention and population

Each generation portrays hypothetical second-year UB business students using the existing four personality descriptions. One condition says the student has **10 seconds** to submit each order; the other says **180 seconds**. The wording is the plain-deadline version from the development screen. These values describe fictional classroom scenarios, not enforced or measured model compute, actual student deadlines or validated psychological pressure. A difference is an outcome to measure, not an acceptance requirement.

Both conditions independently generate whole trajectories from the same physical initial states and matched demand paths. Neither receives prior answers, the competing condition, desired hypothesis directions or a revision request. The inherited rules/profile text is kept fixed. This removes the previous answer exposure, but whole-trajectory generation still exposes the generator to the full demand path and all roles. Local information isolation, chronological internal computation and persona realism cannot be verified. This design studies deadline framing in generated cohorts, not an actual human-time intervention.

The user-facing study records the user-reported **GPT-6 / Pro** UI selection in every fresh chat. Actual provider snapshots, per-person tokens and elapsed time remain unknown. A separately fingerprinted assistant pilot uses the same inherited assistant model/effort across its conditions, without overrides. That setting is recorded literally as inherited, not asserted to be API high or website Pro. These two collections cannot be pooled.

## Fixed collection plans

- **Assistant full-game pilot:** 16 fictional identities, four chains, 24 weeks, two conditions and two generation repeats. Four isolated responses, each containing 320 weekly orders and 16 probe pairs. No paid API calls. This is a prospectively specified extension after the static prompt-development results, not additional trials in that completed screen.
- **Manual website collection:** 500 fictional identities, 125 chains, five batches of 100 identities, two conditions and two generation repeats. Twenty fresh-chat responses, each with 2,000 weekly orders and 100 probe pairs. Repeats reuse identical identity/profile/demand assignments, so there are 500 unique fictional identities, 2,000 generation-specific role trajectories and 40,000 submitted weekly orders.

New seeds and source fingerprints separate these collections from earlier data and from each other. Conditions are counterbalanced in collection order across batches and generations. All twenty manual prompts exist before collection; no prompt embeds an accepted answer. Generations are repeated samples of the model's cohort response, not revisions or new human subjects. No extra repetitions, outcome-based replacements, order clipping, positive floors or preferred maxima are permitted. Report partial data if collection stops.

## Game and outcomes

The existing four-role simulator is unchanged: inventory starts at 12, backlog at zero, outstanding cases at 12; four practice weeks order four cases. Model choices cover weeks 5–24 with iid uniform integer customer demand 0–8. New orders arrive no earlier than three weeks later; upstream shortages may delay shipments. Holding cost is $0.50 and backlog cost $1 per case-week. Twelve scoring continuation weeks hold customer demand and each role's order at its respective final value. The scoring continuation is not model-generated decision evidence.

H1 predicts lower matched-state pipeline sensitivity under the brief deadline: `(order with 8 dispatched cases - order with 32)/24`, averaged across four roles. This remains a separate proxy, not the original fitted structural beta. H2 predicts higher full chain cost under the brief deadline, with practice/model/automatic phases shown separately. H3 predicts higher mean role order/customer-demand sample-variance ratio during the model weeks; zero demand variance yields undefined values, never zero substitution.

Comparisons match chain identity and generation across conditions. Repeated generations within each condition supply descriptive variation checks. Chains within a cohort response are dependent, generations reuse states, and none are observed human students; no student-level p-values or confidence intervals are produced. Differences across conditions can coexist with considerable variation within the same condition. A sign in the predicted direction alone neither establishes a reliable framing effect nor validates a human mechanism. The original structural beta is not fitted or substituted for H1 in this protocol.

## Integrity and reports

Schema `deadline-cohort-trajectories-v1` requires exact study/task IDs, the scenario deadline, rules answers, every chain's weekly order array, probe arrays and completeness. Raw UTF-8 text is retained byte-for-byte; accepted payloads are locked. All rejected attempts are retained. A technical retry uses the same frozen prompt and counts as another generation attempt, not an independent cohort replication.

Prospectively, the existing field-specific formatter may convert unambiguous quoted Boolean, week or currency rule answers to JSON types. It never supplies a correct answer, changes an order or repairs missing data. Original and derived text, transformation edits and hashes are retained and disclosed. Rules remain numerically validated. Correct rule answers and physical replay establish accounting/format validity, not the model's internal process or student fidelity.

Scientific code, profiles, plan and prompts are frozen under `data/runs/deadline_cohort_<fingerprint>/`. Reports and six PNG/PDF plots go under `reports/deadline_cohort_<fingerprint>/analysis/<input-signature>/`, retaining earlier report versions. New pointers are `LATEST_DEADLINE_COHORT_REPORT.json` for website collection and `LATEST_DEADLINE_PILOT_REPORT.json` for the assistant pilot. Notebook 07 opens the website collection; notebook 06 and its pointer remain unchanged.

The new figures show actual outcome levels, absolute deadline differences alongside same-condition repeat differences, role bullwhip, cost phases, every order trajectory, and an example chain with both generations. Figures display generated-data labels and do not exaggerate a zero effect into a nonzero one. Excel/CSV tables contain the underlying values.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -p test_deadline_cohort.py -v
.\.venv\Scripts\python.exe -X utf8 scripts/build_deadline_cohort_notebook.py
```

Open `notebooks/07_deadline_cohort_rerun.ipynb`, keep its prepared run selected, run sections 1–4, send the displayed full prompt in a fresh GPT-6 / Pro chat, and paste the entire response into section 5 or return it in the assistant conversation. Section 7 regenerates the partial/full report. No API key is needed. The CLI `scripts/import_deadline_response.py` imports an exact saved reply into the same immutable slots.

The [prompt-development findings](../reports/pressure_prompt_development_20261018/FINDINGS.md) record why plain deadline wording was selected, its held-out outcomes and the substantial same-condition variation. This rerun is designed after those exploratory observations; it is not a claim of prior registration before prompt development. Existing [manual-method limitations](MANUAL_COHORT_PROTOCOL_20261017.md) and [literature/design review](../reports/revised_design_20261011/REPORT.md) remain relevant; no human validation has been added.
