"""Prepare a separate, unpaid pressure-framing development packet; no responses invented."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study.student_profiles import profiles


def main():
    folder = ROOT / 'reports/pressure_prompt_development_20261018'
    folder.mkdir(parents=True, exist_ok=True)
    descriptions = {k: v['description'] for k, v in profiles().items()}
    scenarios = [
        (0, 8, [4, 4]), (0, 8, [16, 16]),
        (12, 0, [4, 4]), (12, 0, [16, 16]),
        (0, 16, [0, 0]), (0, 16, [12, 12]),
        (24, 0, [0, 0]), (24, 0, [12, 12]),
    ]
    trials = []
    roles = ['retailer', 'wholesaler', 'distributor', 'factory']
    for pi, profile in enumerate(descriptions):
        for si, (inventory, backlog, deliveries) in enumerate(scenarios):
            role = roles[(pi + si // 2) % 4]
            trials.append(dict(id=f't{len(trials)+1:02d}', profile=profile, role=role,
                week=12, demand=8, inventory=inventory, backlog=backlog,
                deliveries_due_next_two_weeks=deliveries,
                delivery_due_third_week=0, awaiting_dispatch=0,
                previous_demands=[8, 8, 8, 8],
                shared_inventory={r: inventory if r == role else 12 for r in roles}))
    data = json.dumps(dict(profiles=descriptions, trials=trials), indent=2)
    common = '''You are portraying hypothetical second-year business students at the
University at Buffalo. Each has introductory business knowledge, no prior Beer
Game experience and no specialist inventory training. Use the supplied personality
description. These are fictional choices, not observations of actual students.

For each separate case, give the order that this student would submit in the
classroom situation below. Try to minimize the team's inventory and backlog costs.
Do not deliberately insert mistakes, force variety, invent demographic traits,
or optimize all cases with a single imposed ordering formula. A repeated choice
or a zero order is allowed. Cases are independent scenarios, not consecutive weeks.

GAME: retailer, wholesaler, distributor and factory form a serial supply chain.
Orders are nonnegative integer cases. No suggested maximum, order fee, revenue,
bulk discount or capacity limit applies. Remaining inventory costs $0.50 per case
per week; unfilled backlog costs $1 per case per week. The supplied inventory and
backlog are after this week's shipments; backlog already includes current unmet
demand. Existing deliveries cannot be canceled. New orders cannot change today's
shipments; earliest arrival is three weeks later, longer if the supplier is short.
Factory orders start production that arrives three weeks later. Delivered cases
first serve any backlog and new demand. The table shows all dispatched deliveries
and orders awaiting dispatch. Customer demand is iid uniform integers 0 through 8;
upstream participants observe their own incoming orders. Future realizations and
other roles' orders/backlogs are unavailable. Do not invent them as known facts.

CLASSROOM SITUATION
{situation}
This describes the fictional student's decision environment. It is not a claim
that the chat interface enforces that many seconds of model computation.

Return only JSON with this structure, listing each of the 32 trial IDs once:
{{"schema_version":"pressure-framing-development-v1", "deadline_seconds":{seconds},
 "choices":[{{"id":"t01","order":<nonnegative integer>}}, ...], "complete":true}}
Replace the illustration with all 32 choices; no ellipses, explanations or summaries.

INPUT CASES
{data}
'''
    texts = {}
    for candidate in ('plain_deadline', 'countdown'):
        for condition, seconds in [('brief', 10), ('ample', 180)]:
            if candidate == 'plain_deadline':
                situation = (f'The student has {seconds} seconds from seeing each decision display '
                             'to submitting its order. The order is final when submitted. '
                             'Represent the choice the described student would make within that deadline.')
            else:
                situation = (f'As the student sees each decision display, a countdown shows {seconds} seconds '
                             f'remaining. The instructor says, "{seconds} seconds left to submit this order." '
                             'The order is final when submitted. Represent the choice the described student '
                             'would make in this situation.')
            text = common.format(situation=situation, seconds=seconds, data=data)
            name = f'{candidate}_{condition}'
            texts[name] = text
            path = folder / f'{name.upper()}.md'
            body = ('# Development prompt: '+name.replace('_', ' ')+'\n\n'
                    'Copy only the box. This is a new 32-choice exploratory screen, not a full game '
                    'or an input for notebook 06. Use a fresh context and retain the entire response.\n\n'
                    '```text\n'+text+'```\n')
            if path.exists() and path.read_text(encoding='utf-8') != body:
                raise ValueError('Do not overwrite a prepared prompt; version the development packet.')
            path.write_text(body, encoding='utf-8')
    plan = dict(version='pressure-framing-development-v1', prepared_date='2026-10-18',
        status='prepared_no_model_responses', trials_per_response=32,
        candidates=['plain_deadline', 'countdown'], conditions=['brief', 'ample'],
        proposed_repetitions_per_cell=2, maximum_development_responses=8,
        seconds={'brief':10,'ample':180}, deadline_basis='Illustrative role-play values, not human-calibrated or enforced.',
        backend='Current assistant inheritance if explicitly authorized; not verified GPT-6 / Pro equivalence.',
        api_calls=0, observed_model_outputs=0,
        prompts_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in texts.items()},
        treatment='Fictional deadline wording; no actual token/time manipulation.',
        collection='Independent contexts, one prompt each, retain first complete output and all failures.',
        analysis='Report every choice and within/between-condition differences; no p-values or H2/H3 conclusions.',
        stopping='At most eight development responses; never rerun selectively until a favored sign appears.',
        future_validation='Freeze any candidate and use new held-out states/contexts before a full-game study.',
        prohibited='No changes to the completed manual run, no response fabrication, no forced orders.')
    plan_path = folder / 'PLAN.json'
    if not plan_path.exists():
        plan_path.write_text(json.dumps(plan, indent=2), encoding='utf-8')
    print(folder)
    print('Four prompts prepared; no model responses generated or claimed.')


if __name__ == '__main__':
    main()
