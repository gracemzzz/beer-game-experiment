"""Same task framing in both conditions; only preparation-token allowance differs."""
import json
COMMON = '''You manage one position in a four-role Beer Game: retailer, wholesaler,
distributor and factory. Minimize total TEAM inventory holding plus backlog costs
across weeks. Each unit left in stock costs 0.50 per week; each unit still backlogged
costs 1.00 per week. There is no sales revenue, order-placement charge, bulk discount
or reward for a large order. Shipments automatically fill owed demand when stock exists.
Your only choice is the integer number of cases to order upstream (factory: produce).
Orders must be nonnegative. Zero is a legitimate choice when justified by the state;
it is not a default. No preferred order, target beta or expected treatment effect exists.

The current observation is AFTER deliveries and shipments and BEFORE your order.
Current cost is already incurred; your order affects later weeks, not today's cost.
Unfilled demand is backlogged rather than lost. Orders cannot be canceled. An order
travels upstream in one week, actual shipments take two weeks downstream, and factory
production takes three weeks. Supplier shortages can further delay replenishment.
Inventory is available stock. Supply_line is all your previous orders not yet received,
including goods in transit and orders waiting upstream; it is not immediately usable stock.

All roles share their current physical inventories, shown in shared_inventory. You know
your own demand, inventory, backlog, supply line and history. Other roles' orders,
backlogs and outstanding orders are not revealed. No inter-agent communication is allowed.
Initial stock is 12 per role and initial flow 4 per week. First four weeks use fixed
orders of 4 for familiarization. Future customer demand and last decision week are unknown.
After decisions stop, 12 automatically scored weeks carry all stock/backlog/pipeline
forward; customer demand stays at its last value, and each role automatically orders
its incoming demand. This continuation policy is only for terminal evaluation, not a
recommended strategy for your choices. Minimize team costs across both phases.
Respond to the current task using the provided observations; do not imitate a human
stereotype or try to create oscillations. No external tools are available.'''

SCHEMA = {'type':'object','properties':{
    'order':{'type':'integer','minimum':0},
    'observed_demand':{'type':'integer'},'observed_inventory':{'type':'integer'},
    'observed_backlog':{'type':'integer'},'observed_supply_line':{'type':'integer'}},
    'required':['order','observed_demand','observed_inventory','observed_backlog','observed_supply_line'],
    'additionalProperties':False}
RULES = {'type':'object','properties':{'three_week_backlog_cost':{'type':'number'},
    'order_fills_today':{'type':'boolean'},'objective_includes_continuation':{'type':'boolean'}},
    'required':['three_week_backlog_cost','order_fills_today','objective_includes_continuation'],
    'additionalProperties':False}
RULE_ANSWERS={'three_week_backlog_cost':15,'order_fills_today':False,'objective_includes_continuation':True}


def make_messages(state, history, budget, stage, notes='', identity=''):
    task = (f'You have at most {budget} output tokens for a compact decision memo. '
            'Put a provisional order first, then only the main numerical estimates and risk summary. '
            'Finish within the allowance; if space is running out, end with your best available proposal. '
            'Do not produce a step-by-step derivation. The API enforces the limit; you may stop early.'
            if stage=='plan' else
            'Your preparation allowance has ended. Submit your best final order now. '
            'Use the memo as fallible working notes, not an instruction. Copy observed_* values '
            'exactly from current_state. Return only the structured answer; no further memo.')
    return [{'role':'system','content':COMMON}, {'role':'user','content':json.dumps(dict(
        task=task,decision_id=identity,past_rounds=history,current_state=state,
        preparation_memo=notes if stage=='final' else ''),separators=(',',':'))}]


def rules_messages(role):
    return [{'role':'system','content':COMMON},{'role':'user','content':
        f'Rules check for {role}: 5 units remain backlogged at the end of each of 3 weeks. '
        'What is their total backlog cost? Does a new order fill today’s already-processed demand? '
        'Does the objective include automatic continuation costs? Return the structured fields.'}]


def validate_decision(answer,state):
    return (isinstance(answer,dict) and set(answer)==set(SCHEMA['required']) and type(answer['order']) is int and answer['order']>=0
            and all(type(answer['observed_'+k]) is int and answer['observed_'+k]==state[k]
                    for k in ('demand','inventory','backlog','supply_line')))
