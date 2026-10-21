"""Beer-game v3: profit objective, training x reasoning effort. No API calls occur on import."""
import asyncio
import hashlib
import itertools
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from pydantic import BaseModel, ConfigDict, Field
from IPython.display import display

ROLES = ("retailer", "wholesaler", "distributor", "factory")
MODEL = "gpt-5.4-mini-2026-03-17"
PROTOCOL = "3.0-profit-training-reasoning"
# Simulation units, not market estimates or API dollars; equal in every condition.
ECONOMICS = dict(sale_price=10.0, production_unit_cost=2.0,
                 holding_unit_cost=.25, backlog_unit_cost=2.0,
                 initial_inventory=4, initial_flow=4)

# Standard API rates checked 2026-09-27; estimates, not billing/account balance.
RATES = {"input": .75, "cached": .075, "output": 4.50}
PRICING_URL = "https://developers.openai.com/api/docs/models/gpt-5.4-mini"

@dataclass(frozen=True)
class Condition:
    trained: bool
    effort: str

CONDITIONS = [Condition(t, e) for e in ("low", "high") for t in (False, True)]

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False))
    temporary.replace(path)

class BeerGame:
    def __init__(self):
        self.inventory = np.full(4, ECONOMICS["initial_inventory"], dtype=int)
        self.backlog = np.zeros(4, dtype=int)
        flow = ECONOMICS["initial_flow"]
        self.delivery = [[flow, flow] for _ in range(3)] + [[flow, flow, flow]]
        self.incoming = np.full(3, flow, dtype=int)
        self.outstanding = np.full(4, 3*flow, dtype=int)
        self.week = 0
        self.awaiting_orders = False

    def observe(self, customer_demand):
        assert not self.awaiting_orders, "Commit orders before advancing."
        self.week += 1
        receipts = np.array([queue.pop(0) for queue in self.delivery])
        self.inventory += receipts
        self.outstanding -= receipts
        demands = np.r_[customer_demand, self.incoming].astype(int)
        owed = self.backlog + demands
        shipped = np.minimum(self.inventory, owed)
        self.inventory -= shipped
        self.backlog = owed - shipped
        # Shipments made this week arrive two weeks later downstream.
        for downstream in range(3):
            self.delivery[downstream].append(int(shipped[downstream + 1]))
        self.awaiting_orders = True
        assert (self.inventory >= 0).all() and (self.outstanding >= 0).all()
        return [dict(week=self.week, role=ROLES[i], demand=int(demands[i]),
                     received=int(receipts[i]), shipped=int(shipped[i]),
                     inventory=int(self.inventory[i]), backlog=int(self.backlog[i]),
                     net_inventory=int(self.inventory[i] - self.backlog[i]),
                     supply_line=int(self.outstanding[i]),
                     holding_cost=float(ECONOMICS['holding_unit_cost'] * self.inventory[i]),
                     backlog_cost=float(ECONOMICS['backlog_unit_cost'] * self.backlog[i]),
                     sales_revenue=float(ECONOMICS['sale_price'] * shipped[i]) if i==0 else 0.,
                     production_cost=0.,
                     cost=float(ECONOMICS['holding_unit_cost'] * self.inventory[i] +
                                ECONOMICS['backlog_unit_cost'] * self.backlog[i]))
                for i in range(4)]

    def commit(self, orders):
        assert self.awaiting_orders
        assert len(orders) == 4 and all(isinstance(x, int) and x >= 0 for x in orders)
        self.outstanding += np.array(orders, dtype=int)
        self.incoming = np.array(orders[:3], dtype=int)
        self.delivery[3].append(orders[3])
        self.awaiting_orders = False
        # Outstanding goods = shipping queue + supplier backlog + order in transit.
        for i in range(3):
            assert self.outstanding[i] == sum(self.delivery[i]) + self.backlog[i+1] + orders[i]
        assert self.outstanding[3] == sum(self.delivery[3])

def predicted_orders(params, demands, net_inventory, supply_line):
    theta, alpha, beta, target = params
    forecast = 8.0
    expected = []
    for demand in demands:
        forecast = theta * demand + (1 - theta) * forecast
        expected.append(forecast)
    return np.maximum(0, np.asarray(expected) + alpha * (target - net_inventory - beta * supply_line))

def estimate_beta(frame, beta_upper=2.0):
    frame = frame.sort_values("week")
    y = frame.order.to_numpy(float)
    d = frame.demand.to_numpy(float)
    ni = frame.net_inventory.to_numpy(float)
    sl = frame.supply_line.to_numpy(float)
    blank = dict(theta=np.nan, alpha=np.nan, beta=np.nan, target=np.nan,
                 rmse=np.nan, r2=np.nan, jac_condition=np.nan, usable=False,
                 fit_flag="insufficient_variation", n=len(y))
    if len(y) < 16 or np.std(y) < 1e-8 or np.std(ni) < 1e-8 or np.std(sl) < 1e-8:
        return blank
    lo = np.array([0, 0, 0, 0.0])
    hi = np.array([1, 1, beta_upper, 10000.0])
    fits = []
    for theta in (.2, .8):
        for beta in (.15, min(.85, beta_upper * .85)):
            target = np.clip(np.median(ni + beta * sl), 1, 9999)
            fit = least_squares(lambda p: predicted_orders(p, d, ni, sl) - y,
                                [theta, .3, beta, target], bounds=(lo, hi),
                                x_scale="jac", max_nfev=3000)
            fits.append(fit)
    fit = min(fits, key=lambda f: np.sum(f.fun ** 2))
    theta, alpha, beta, target = fit.x
    norms = np.linalg.norm(fit.jac, axis=0)
    scaled = fit.jac / np.maximum(norms, 1e-12)
    jac_condition = float(np.linalg.cond(scaled))
    r2 = 1 - np.sum(fit.fun ** 2) / np.sum((y - y.mean()) ** 2)
    flags = []
    if not fit.success: flags.append("optimizer_failed")
    if alpha < .02: flags.append("weak_inventory_response")
    if np.linalg.matrix_rank(scaled) < 4 or jac_condition > 1e6:
        flags.append("weak_identification")
    # θ endpoints are allowed; α/β/target boundary fits get flagged.
    if any(np.isclose(fit.x[1:], lo[1:], atol=1e-5)) or any(np.isclose(fit.x[1:], hi[1:], atol=1e-5)):
        flags.append("parameter_boundary")
    if np.isclose(beta, beta_upper, atol=1e-5) or np.isclose(target, 10000, atol=1e-5):
        flags.append("upper_parameter_limit")
    if r2 < 0: flags.append("poor_fit")
    fatal_flags = set(flags) - {"parameter_boundary"}
    return dict(theta=theta, alpha=alpha, beta=beta, target=target,
                rmse=float(np.sqrt(np.mean(fit.fun ** 2))), r2=float(r2),
                jac_condition=jac_condition, usable=not fatal_flags,
                fit_flag=";".join(flags) or "ok", n=len(y))


from html import escape
from IPython.display import HTML


class RunProgress:
    """One live display, plus a small on-disk status file; no extra API requests."""
    def __init__(self, total, mode, status_path=None, render=True):
        self.total = total
        self.mode = mode
        self.status_path = status_path
        self.processed = self.successful = self.fallbacks = self.errors = self.cached = 0
        self.group = self.week = 0
        self.groups = self.weeks = 0
        self.phase = "Preparing"
        self.started = None
        self.finished_elapsed = None
        self.last_render = 0.0
        self.enabled = render
        self.handle = display(HTML(self.html()), display_id=True) if render else None
        self.refresh(force=True)

    @staticmethod
    def duration(seconds):
        if seconds is None:
            return "Estimating…"
        seconds = max(0, int(seconds))
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h}h {m:02d}m {s:02d}s" if h else f"{m}m {s:02d}s"

    def snapshot(self):
        elapsed = self.finished_elapsed
        if elapsed is None:
            elapsed = time.perf_counter() - self.started if self.started is not None else 0.0
        remaining = self.total - self.processed
        # Resume/cache speed is not representative of new API latency.
        fresh = self.processed - self.cached
        eta = (elapsed / fresh * remaining) if fresh >= 4 and not self.cached else None
        if remaining == 0:
            eta = 0.0
        if self.finished_elapsed is not None and remaining > 0:
            eta = None
        return dict(phase=self.phase, processed=self.processed, remaining=remaining,
                    total=self.total, successful=self.successful, fallbacks=self.fallbacks,
                    errors=self.errors, cached=self.cached, group=self.group, groups=self.groups,
                    week=self.week, weeks=self.weeks, elapsed_s=elapsed, eta_s=eta,
                    percent=100*self.processed/self.total if self.total else 0.0,
                    updated_utc=datetime.now(timezone.utc).isoformat())

    def html(self):
        s = self.snapshot()
        color = "#b54730" if self.phase in {"Stopped", "Interrupted"} else "#247a89"
        valid_label = "Successful GPT responses" if self.mode == "api" else "Synthetic responses"
        location = f"Group {self.group}/{self.groups} · Week {self.week}/{self.weeks}" if self.group else "Simulation has not started"
        eta = "Unavailable on resumed runs" if self.cached and s['remaining'] else self.duration(s['eta_s'])
        return f"""<div style="border:1px solid #cbd5e1;border-radius:8px;padding:14px;max-width:850px;font-family:system-ui">
        <div style="font-size:17px;font-weight:700;color:{color}">{escape(self.phase)} · {escape(self.mode.upper())}</div>
        <div style="font-size:21px;margin:8px 0"><b>{self.processed:,} / {self.total:,}</b> processed
          &nbsp;·&nbsp; <b>{s['remaining']:,}</b> remaining &nbsp;·&nbsp; {s['percent']:.1f}%</div>
        <progress value="{self.processed}" max="{self.total}" style="width:100%;height:22px;accent-color:{color}"></progress>
        <div style="margin-top:8px">{valid_label}: <b>{self.successful:,}</b> &nbsp;|&nbsp;
          Fallbacks: <b>{self.fallbacks:,}</b> &nbsp;|&nbsp; API errors: <b>{self.errors:,}</b> &nbsp;|&nbsp;
          Reused from cache: <b>{self.cached:,}</b></div>
        <div style="margin-top:7px">{location} &nbsp;·&nbsp; Elapsed: {self.duration(s['elapsed_s'])}
          &nbsp;·&nbsp; Estimated remaining: {eta}</div>
        <div style="margin-top:6px;font-size:12px;color:#526171">Processed includes successful and failed responses, including rules checks.
          Cached records are counted once. ETA is approximate; no replacement orders are used.</div></div>"""

    def refresh(self, force=False):
        now = time.perf_counter()
        if not force and now - self.last_render < .25:
            return
        self.last_render = now
        if self.handle is not None:
            self.handle.update(HTML(self.html()))
        if self.status_path is not None:
            atomic_json(self.status_path, self.snapshot())

    def set_phase(self, phase):
        self.phase = phase
        self.refresh(force=True)

    def start(self):
        self.started = time.perf_counter()
        self.set_phase("Running")

    def record(self, status, cached=False):
        if self.processed >= self.total:
            raise RuntimeError("Progress exceeds the planned number of decisions.")
        self.processed += 1
        self.cached += int(cached)
        if status in {"ok", "synthetic"}:
            self.successful += 1
        elif status == "api_error":
            self.errors += 1
        else:
            self.fallbacks += 1
        self.refresh()

    def finish(self, phase):
        self.finished_elapsed = self.snapshot()['elapsed_s']
        self.set_phase(phase)

    async def heartbeat(self):
        while True:
            await asyncio.sleep(1)
            self.refresh(force=True)


STANDARD = f"""You manage one role in a four-role beer supply chain: retailer,
wholesaler, distributor, factory. Maximize total TEAM profit over repeated weeks.
Team profit = actual customer sales revenue - committed factory production cost
- inventory holding cost at every role - backlog penalties at every role.
Each unit actually delivered by the retailer to an external customer earns
{ECONOMICS['sale_price']} revenue. Merely receiving an order earns no revenue.
Each new factory production order commits {ECONOMICS['production_unit_cost']} per unit
immediately, even if delivery is later. Internal transfers create no team revenue
and no additional purchase cost. Holding costs {ECONOMICS['holding_unit_cost']} per unit
per week; unfilled demand costs {ECONOMICS['backlog_unit_cost']} per unit per week.
Unfilled demand is backlogged, not lost; late delivery earns revenue when delivered
but backlog penalties already incurred remain. Initial stocks and initial pipeline
are sunk endowments. No terminal salvage value is credited to surplus stock or pipeline.
Demand continues across weeks and may change. Orders support future deliveries;
ordering nothing repeatedly can cause shortages, delayed sales, and penalties.
Ordering too much can waste production and holding costs. Choose economically
justified orders; there is no minimum order or prescribed strategy.
Only your local state and your own past rounds are available. No communication
with other roles. Orders take one week upstream, shipping takes two weeks
downstream, and factory production takes three weeks. Capacity is unlimited.
Orders cannot be canceled. Inventory is available stock; backlog is unfilled
customer demand; net inventory = inventory - backlog. Supply line is everything
previously ordered but not yet received. The state is AFTER this week's receipts
and shipments, BEFORE your new order. Future demand and the final week are unknown.
Return a nonnegative integer order and the requested structured fields.
The observed_* fields must copy the current observations, not predictions.
For a rules-check task, answer the questions instead of placing an order."""

TRAINING = """Preparation lesson: delayed replenishment.
Goods already ordered can be in transit, production, or waiting at a supplier.
They remain outstanding until received. A delay alone does not erase an order.
Evaluate available stock, unfilled demand, and outstanding replenishment together.
Example: 10 units were outstanding and 3 arrive. Before another order, 7 remain
outstanding. Those 7 are not available for immediate shipment, but may arrive later.
Practice example with feedback: 18 outstanding units, 6 received, then 4 newly
ordered means 16 outstanding afterward: 18 - 6 + 4. Counting the old order as
lost would overstate the replenishment needed. Conversely, goods still pending
cannot fill today's backlog immediately. Consider both timing and quantities.
This lesson does not prescribe an order rule. Choose orders using the game goal."""

CONTROL = """Preparation lesson: game organization and record keeping.
The game has four positions. A retailer serves the final customer. A wholesaler
serves the retailer, a distributor serves the wholesaler, and a factory supplies
the distributor. Each position records its own weekly activity.
Example: a record labeled retailer, week 7 describes the retailer in week 7.
It is not a record of the factory's activity or a prediction of week 8.
Practice example with feedback: a wholesaler's week 9 record followed by its
week 10 record describes two observations for the same role, in chronological
order. A distributor's week 10 record belongs to another role. Keep role and week
labels consistent when reviewing history. The game goal is total team profit.
This lesson does not prescribe an order rule. Choose orders using the game goal."""

class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order: int = Field(ge=0, le=1000000)
    observed_demand: int
    observed_inventory: int
    observed_backlog: int
    observed_supply_line: int

class RulesCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    net_inventory: int
    holding_cost: float
    shipping_weeks: int
    production_weeks: int
    team_profit: float

CHECK_TASK = {"task": "rules_check", "questions": [
    "What is net inventory when inventory is 9 and backlog is 3?",
    "What is the one-week holding cost for 8 units (ignore backlog)?",
    "How many weeks does downstream shipping take?",
    "How many weeks does factory production take?",
    "If the retailer delivers 3 units, the factory orders 4 units, total holding cost is 2 and total backlog cost is 6, what is team profit for the week?"]}
CHECK_ANSWERS = dict(net_inventory=6, holding_cost=2.0, shipping_weeks=2, production_weeks=3, team_profit=14.0)

def messages(condition, task, history=None):
    return [dict(role="system", content=STANDARD + "\n\n" +
                 (TRAINING if condition.trained else CONTROL)),
            dict(role="user", content=json.dumps(
                dict(task=task, your_past_rounds=history or []), sort_keys=True))]

def validate_answer(answer, state=None):
    if state is None:
        return answer == CHECK_ANSWERS
    return all(answer.get("observed_" + field) == state[field]
               for field in ("demand", "inventory", "backlog", "supply_line"))

def demand_path(block, weeks, seed):
    # Same prespecified path for all four conditions in a block; independent blocks.
    rng = np.random.default_rng(seed + 104729 * block)
    demand = [8] * 4
    level = 8
    for week in range(4, weeks):
        if (week - 4) % 6 == 0:
            level = int(rng.choice([8, 12, 16]))
        demand.append(int(np.clip(level + rng.integers(-2, 3), 4, 20)))
    return demand[:weeks]

def diagnostic_states():
    # Optional screen includes shortages, balance and surplus; never game trajectories.
    return [dict(week=10, role="retailer", demand=8, received=8, shipped=8,
                 inventory=max(ni,0), backlog=max(-ni,0), net_inventory=ni, supply_line=sl,
                 holding_cost=ECONOMICS['holding_unit_cost']*max(ni,0),
                 backlog_cost=ECONOMICS['backlog_unit_cost']*max(-ni,0),
                 sales_revenue=8*ECONOMICS['sale_price'],production_cost=0.,
                 cost=ECONOMICS['holding_unit_cost']*max(ni,0)+ECONOMICS['backlog_unit_cost']*max(-ni,0))
            for ni in (-8, -4, 0, 4, 8, 16) for sl in (0, 8, 16, 24)]


def settle_week(states, orders):
    """Assign factory commitment cost once. Sum of role contributions = team profit."""
    for i, state in enumerate(states):
        state['production_cost'] = ECONOMICS['production_unit_cost']*orders[i] if i==3 else 0.
        state['cost'] = state['holding_cost']+state['backlog_cost']+state['production_cost']
        state['profit_contribution'] = state['sales_revenue']-state['cost']
    return states

class ExperimentStopped(RuntimeError):
    pass

def token_cost(usage):
    tokens = usage or {}
    cached = tokens.get("cached_input_tokens", 0)
    return ((tokens.get("input_tokens", 0) - cached) * RATES['input'] +
            cached * RATES['cached'] + tokens.get("output_tokens", 0) * RATES['output']) / 1e6

class Runner:
    def __init__(self, directory, config, client=None, render=True):
        self.directory, self.config, self.client = Path(directory), config, client
        self.cache = self.directory / 'requests'
        self.cache.mkdir(parents=True, exist_ok=True)
        self.progress = None
        self.render = render
        self.charged = sum(json.loads(p.read_text()).get('budget_charge_usd', 0)
                           for p in self.cache.glob('*.json'))

    async def request(self, condition, identity, task, state=None, history=None):
        prompt = messages(condition, task, history)
        schema = RulesCheck if state is None else Decision
        key = digest(dict(identity=identity, prompt=prompt, effort=condition.effort,
                          model=self.config['model'], schema=schema.model_json_schema(),
                          max_output_tokens=self.config['max_output_tokens']))
        path = self.cache / (key + '.json')
        if path.exists():
            record = json.loads(path.read_text())
            if record['status'] not in ('ok', 'synthetic'):
                raise ExperimentStopped('A saved failed request remains in this run. Review its record; '
                                        'fix access/settings and use a fresh REPLICATE_ID. No order was substituted.')
            self.progress.record(record['status'], cached=True)
            return record
        record = dict(identity=identity, condition=asdict(condition), messages=prompt,
                      status='pending', answer=None, elapsed_s=0., usage={},
                      budget_charge_usd=0., request_key=key)
        if self.config['mode'] == 'offline':
            if state is None:
                answer = CHECK_ANSWERS.copy()
            else:
                rng = np.random.default_rng(int(key[:16], 16))
                q = state['demand'] + .35 * (48-state['net_inventory']-.65*state['supply_line'])
                answer = dict(order=max(0, int(round(q + rng.normal(0, .8)))),
                              **{'observed_'+k: state[k] for k in
                                 ('demand', 'inventory', 'backlog', 'supply_line')})
            record.update(answer=answer, status='synthetic')
        else:
            # Conservative local reservation: UTF-8 byte count + overhead for input;
            # full output allowance, including reasoning. Not an account billing cap.
            input_allowance = len(json.dumps(prompt).encode()) + len(json.dumps(schema.model_json_schema()).encode()) + 2048
            reserve = (input_allowance*RATES['input'] + self.config['max_output_tokens']*RATES['output'])/1e6
            if self.charged + reserve > self.config['budget_usd']:
                raise ExperimentStopped(f"Local spending guard: ${self.charged:.3f} charged/reserved; "
                    f"next request reserves ${reserve:.3f}. Increase BUDGET_USD and rerun to continue. "
                    "This is not your OpenAI account balance.")
            self.charged += reserve
            record['budget_charge_usd'] = reserve
            # Persist before sending: interruption/unknown usage keeps this reservation.
            atomic_json(path, record)
            started = time.perf_counter()
            try:
                response = await asyncio.wait_for(self.client.responses.parse(
                    model=self.config['model'], input=prompt, text_format=schema,
                    reasoning={'effort': condition.effort},
                    max_output_tokens=self.config['max_output_tokens'], store=False),
                    timeout=self.config['timeout_s'])
                record['response'] = response.model_dump(mode='json', warnings=False)
                record['response_model'] = response.model
                if response.usage:
                    u = response.usage
                    record['usage'] = dict(input_tokens=u.input_tokens, output_tokens=u.output_tokens,
                        cached_input_tokens=getattr(u.input_tokens_details, 'cached_tokens', 0) or 0,
                        reasoning_tokens=getattr(u.output_tokens_details, 'reasoning_tokens', 0) or 0)
                    actual = token_cost(record['usage'])
                    self.charged += actual-reserve
                    record['budget_charge_usd'] = actual
                if response.status != 'completed' or response.output_parsed is None:
                    record['status'] = 'incomplete_or_refused'
                else:
                    record['answer'] = response.output_parsed.model_dump()
                    record['status'] = 'ok' if validate_answer(record['answer'], state) else 'comprehension_failed'
            except Exception as exc:
                # Never persist exception messages, which may contain sensitive text.
                record.update(status='api_error', error_type=type(exc).__name__,
                              http_status=getattr(exc, 'status_code', None))
            finally:
                record['elapsed_s'] = time.perf_counter()-started
                atomic_json(path, record)
            if record['status'] != 'ok':
                self.progress.record('api_error')
                raise ExperimentStopped(f"Stopped: {record['status']} ({record.get('error_type', '')}, "
                    f"HTTP {record.get('http_status')}). See {path.name}. "
                    "No fabricated order or retry-until-correct was used. "
                    "For HTTP 429 check API credits/rate limits; for 401 check the key; "
                    "for incomplete responses review the output allowance. Preserve this failed pilot.")
        atomic_json(path, record)
        self.progress.record(record['status'])
        return record

async def run_study(base, config, client=None, render=True):
    assert config['mode'] in ('offline', 'api')
    assert config['stage'] in ('diagnostics', 'game')
    assert config['groups_per_cell'] >= 1 and config['weeks'] >= 16
    if config['model'] != MODEL:
        raise ValueError('This protocol pins a verified model and its price. Model changes require a new protocol/rates review.')
    # Budget may be raised for a checkpoint resume; experimental settings may not change.
    immutable = {k:v for k,v in config.items() if k != 'budget_usd'}
    immutable.update(protocol=PROTOCOL, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     standard=STANDARD, training=TRAINING, control=CONTROL, economics=ECONOMICS)
    directory = Path(base)/'results'/('v3_'+config['mode']+'_'+digest(immutable)[:16])
    directory.mkdir(parents=True, exist_ok=True)
    if not (directory/'manifest.json').exists():
        atomic_json(directory/'manifest.json', dict(config=immutable,
            created_utc=datetime.now(timezone.utc).isoformat(), pricing=RATES, pricing_url=PRICING_URL))
    runner = Runner(directory, config, client, render)
    blocks = 1 if config['stage']=='diagnostics' else config['groups_per_cell']
    total = 4*(4+len(diagnostic_states())) if config['stage']=='diagnostics' else blocks*4*4*(1+config['weeks'])
    runner.progress = RunProgress(total, config['mode'], directory/'progress.json', render)
    runner.progress.groups = blocks*4
    runner.progress.weeks = len(diagnostic_states()) if config['stage']=='diagnostics' else config['weeks']
    heartbeat = asyncio.create_task(runner.progress.heartbeat())
    rows, checks = [], []
    schedule = [(b, c) for b in range(blocks) for c in CONDITIONS]
    np.random.default_rng(config['seed']).shuffle(schedule)
    runner.progress.start()
    try:
        for number, (block, condition) in enumerate(schedule, 1):
            group = f"b{block:03d}_{'trained' if condition.trained else 'control'}_{condition.effort}"
            runner.progress.group = number
            for role in ROLES:
                record = await runner.request(condition, dict(group=group, role=role, kind='rules'), CHECK_TASK)
                checks.append(dict(group_id=group, block=block, role=role, **asdict(condition),
                                   passed=validate_answer(record['answer']), **record['usage']))
            pd.DataFrame(checks).to_csv(directory/'rules_checks.csv', index=False)
            if config['stage']=='diagnostics':
                states = diagnostic_states()
                np.random.default_rng(config['seed']).shuffle(states)
                for index, state in enumerate(states):
                    runner.progress.week = index+1
                    record = await runner.request(condition, dict(group=group, kind='diagnostic', item=index),
                        {'kind':'independent_hypothetical_state', 'current_state':state}, state)
                    rows.append(dict(group_id=group, block=block, **asdict(condition), **state,
                                     order=record['answer']['order'], status=record['status'],
                                     elapsed_s=record['elapsed_s'], **record['usage']))
            else:
                game = BeerGame()
                histories = [[] for _ in ROLES]
                for week, demand in enumerate(demand_path(block, config['weeks'], config['seed']), 1):
                    runner.progress.week = week
                    states = game.observe(demand)
                    records = []
                    # Sequential requests limit budget exposure. All four see the same
                    # pre-commit snapshot, so game decisions are simultaneous in game time.
                    for i, state in enumerate(states):
                        records.append(await runner.request(condition,
                            dict(group=group, role=ROLES[i], week=week, kind='game'),
                            {'kind':'game_decision', 'current_state':state}, state, histories[i]))
                    orders = [r['answer']['order'] for r in records]
                    game.commit(orders)
                    settle_week(states, orders)
                    for i, r in enumerate(records):
                        row = dict(group_id=group, agent_id=group+'_'+ROLES[i], block=block,
                            **asdict(condition), **states[i], order=r['answer']['order'],
                            status=r['status'], elapsed_s=r['elapsed_s'], **r['usage'])
                        rows.append(row)
                        histories[i].append(dict(states[i], order=r['answer']['order']))
                    pd.DataFrame(rows).to_csv(directory/'rounds.csv', index=False)
        frame = pd.DataFrame(rows)
        frame.to_csv(directory/('diagnostics.csv' if config['stage']=='diagnostics' else 'rounds.csv'), index=False)
        runner.progress.finish('Complete')
        return frame, directory
    except BaseException:
        if rows:
            pd.DataFrame(rows).to_csv(directory/'partial_rows.csv', index=False)
        runner.progress.finish('Stopped')
        raise
    finally:
        heartbeat.cancel()
        try:
            await heartbeat
        except asyncio.CancelledError:
            pass
        atomic_json(directory/'spending.json', dict(charged_or_reserved_usd=runner.charged,
            local_budget_usd=config['budget_usd'], note='Estimated standard API cost; includes reservations for unknown usage. Not an invoice.'))

def signflip_pvalue(differences, seed=1, draws=20000):
    """Two-sided paired sign randomization; block is unit. Exact through 16 blocks.
    Requires sign exchangeability under the sharp null, not normality of orders.
    """
    d = np.asarray(differences, dtype=float)
    if len(d) == 0 or not np.isfinite(d).all():
        return np.nan
    observed = abs(d.mean())
    if len(d) <= 16:
        signs = np.asarray(list(itertools.product((-1, 1), repeat=len(d))))
        permuted = abs((signs*d).mean(axis=1))
        return float(np.mean(permuted >= observed-1e-12))
    rng = np.random.default_rng(seed)
    permuted = abs((rng.choice([-1, 1], size=(draws, len(d)))*d).mean(axis=1))
    return float((1+np.sum(permuted >= observed-1e-12))/(draws+1))

def holm_two(pvalues):
    p = np.asarray(pvalues, dtype=float)
    if len(p) != 2 or not np.isfinite(p).all():
        return np.full(2, np.nan)
    order = np.argsort(p)
    adjusted = np.empty(2)
    adjusted[order[0]] = min(1., 2*p[order[0]])
    adjusted[order[1]] = min(1., max(adjusted[order[0]], p[order[1]]))
    return adjusted

def analyze_game(rounds, config):
    records = []
    for agent, frame in rounds.groupby('agent_id'):
        first = frame.iloc[0]
        records.append(dict(agent_id=agent, group_id=first.group_id, block=int(first.block),
            trained=bool(first.trained), effort=first.effort,
            copies_demand=bool((frame.order == frame.demand).all()),
            **estimate_beta(frame)))
    fits = pd.DataFrame(records)
    groups = fits.groupby(['group_id','block','trained','effort']).agg(
        beta=('beta','mean'), roles=('agent_id','nunique'), all_usable=('usable','all')).reset_index()
    groups['included'] = (groups.roles == 4) & groups.all_usable
    groups['analysis_beta'] = groups.beta.where(groups.included)
    # The full table stays visible. Never treat unidentified beta as zero.
    pivot = groups.pivot(index='block', columns=['trained','effort'], values='analysis_beta')
    pivot = pivot.reindex(columns=pd.MultiIndex.from_tuples([(c.trained,c.effort) for c in CONDITIONS]))
    complete = pivot.dropna()
    d1 = ((complete[(True,'low')]-complete[(False,'low')])+
          (complete[(True,'high')]-complete[(False,'high')]))/2
    d2 = complete[(True,'low')]-complete[(True,'high')]
    expected = config['groups_per_cell']
    all_complete = len(complete)==expected and len(rounds)==expected*16*config['weeks']
    # Do not test selected complete cases if behavior-dependent identification excluded any block.
    allow = all_complete and len(complete)>=8 and config['mode']=='api'
    raw = [signflip_pvalue(d1), signflip_pvalue(d2)] if allow else [np.nan, np.nan]
    adjusted = holm_two(raw)
    rng = np.random.default_rng(config['seed']+43)
    rows = []
    for i, (name, d, direction) in enumerate([
            ('H1_training_average', d1, 'positive'), ('H2_API_low_minus_high_trained', d2, 'negative')]):
        ci = [np.nan, np.nan]
        if allow:
            ci = np.quantile(rng.choice(d.to_numpy(), size=(5000,len(d)), replace=True).mean(axis=1), [.025,.975])
        rows.append(dict(hypothesis=name, estimate=float(d.mean()) if len(d) else np.nan,
            complete_blocks=len(complete), planned_blocks=expected, p_two_sided=raw[i],
            p_holm=adjusted[i], ci95_low=ci[0], ci95_high=ci[1], predicted_direction=direction,
            status='exploratory GPT test' if allow else
                   'withheld: offline, fewer than 8 complete blocks, or excluded/incomplete data'))
    return fits, groups, pd.DataFrame(rows)

def diagnostic_summary(frame):
    rows = []
    for (trained, effort), f in frame.groupby(['trained','effort']):
        # These are direct finite differences, not a structural beta estimate.
        p = f.pivot(index='net_inventory', columns='supply_line', values='order')
        sl_change = float((p[p.columns.max()]-p[p.columns.min()]).mean())
        ni_change = float((p.loc[p.index.max()]-p.loc[p.index.min()]).mean())
        rows.append(dict(trained=trained, effort=effort,
            mean_order_change_supply_line_0_to_24=sl_change,
            mean_order_change_net_inventory_minus8_to16=ni_change,
            copies_demand_all_states=bool((f.order==f.demand).all()),
            zero_orders=int((f.order==0).sum()),
            median_reasoning_tokens=float(f.get('reasoning_tokens', pd.Series([0])).median()),
            note='Descriptive retailer sensitivity screen; not a beta estimate or hypothesis test'))
    return pd.DataFrame(rows)

def make_report(frame, directory, config):
    directory = Path(directory)
    synthetic = config['mode']=='offline'
    title = 'SYNTHETIC SOFTWARE CHECK' if synthetic else 'GPT AGENT PILOT'
    lines = [f'# {title}: v3 profit results', '', '## Conclusions', '']
    if synthetic:
        lines.append('1. These are synthetic decisions, not GPT results. No hypothesis conclusion or API cost follows from them.')
    else:
        lines.append(f'1. Completed {len(frame):,} decision records with validated state readbacks; no replacement orders.')
    if config['stage']=='diagnostics':
        summary = diagnostic_summary(frame)
        summary.to_csv(directory/'diagnostic_summary.csv', index=False)
        flat = int(summary.copies_demand_all_states.sum())
        lines += [f'2. {flat}/4 condition screens copied demand in every diagnostic state.',
                  '3. H1 and H2 have not been tested. Review inventory/supply-line sensitivity before running the game.',
                  '4. Diagnostic states are separate hypothetical retailer decisions; they are not four-role game trajectories.',
                  '', '## Diagnostic results', '', '```', summary.to_string(index=False), '```']
    else:
        fits, groups, hypotheses = analyze_game(frame, config)
        fits['beta_for_interpretation'] = fits.beta.where(fits.usable)
        fits.to_csv(directory/'agent_beta_fits.csv', index=False)
        groups.to_csv(directory/'group_beta.csv', index=False)
        hypotheses.to_csv(directory/'hypothesis_tests.csv', index=False)
        lines += [f'2. {int(groups.included.sum())}/{len(groups)} groups have four usable beta estimates; '
                  f'{int(fits.copies_demand.sum())}/{len(fits)} roles copied demand every week.',
                  '3. H1 tests the training effect. H2_API tests reasoning effort, not 60/120-second human time pressure.']
        for h in hypotheses.itertuples():
            if pd.isna(h.p_holm):
                conclusion = h.status + '; no significance conclusion.'
            else:
                correct_sign = h.estimate>0 if h.predicted_direction=='positive' else h.estimate<0
                if h.p_holm < .05 and correct_sign:
                    conclusion = 'exploratory evidence in the predicted direction'
                elif h.p_holm < .05:
                    conclusion = 'significant effect opposite to the prediction; hypothesis not supported'
                else:
                    conclusion = 'hypothesis not supported at the corrected .05 threshold'
                conclusion += f'; two-sided Holm-adjusted p={h.p_holm:.4g}. GPT-specific, not human evidence.'
            lines.append(f'- {h.hypothesis}: {conclusion}')
        roles, performance_groups, performance_conditions = save_game_dashboard(frame, directory, config)
        lines += ['', '## Supply-chain performance (all groups)', '', '```',
                  performance_conditions.round(3).to_string(index=False), '```',
                  'Profit and cost are in simulation units, not API dollars. Team profit counts retailer revenue once, minus factory commitments and all role costs. '
                  'Customer fulfillment is cumulative retailer shipments / cumulative customer demand; '
                  'it includes late deliveries and is not an on-time service measure. '
                  'Bullwhip is sample variance of role orders / variance of incoming demand; '
                  'it is undefined when incoming demand has zero variance. No terminal inventory penalty is added.',
                  '', '## Beta measurement coverage', '', '```',
                  fits.groupby(['trained','effort']).agg(roles=('agent_id','size'),usable_beta=('usable','sum')).to_string(),
                  '```', 'See agent_beta_fits.csv: beta_for_interpretation is blank when beta is unreliable. '
                  'The raw optimizer beta is retained for audit only. See group_beta.csv for analysis_beta. '
                  'Missing beta means unidentified, not zero and not a failed hypothesis.',
                  '', '![Supply-chain performance](supply_chain_performance.png)']
        lines += ['', '## Hypothesis results', '', '```', hypotheses.to_string(index=False), '```',
                  '', 'CIs are descriptive paired bootstrap 95% intervals, not multiplicity-adjusted. '
                  'The two planned p-values are Holm-adjusted. No p-values are computed after excluding '
                  'any planned block; identification failures depend on behavior and can bias selection. '
                  'Eight blocks is a reporting floor, not a power calculation.']
    if 'reasoning_tokens' in frame:
        effort = frame.groupby('effort').agg(mean_reasoning_tokens=('reasoning_tokens','mean'),
            median_reasoning_tokens=('reasoning_tokens','median'), median_latency_s=('elapsed_s','median'))
        effort.to_csv(directory/'effort_check.csv')
        lines += ['', '## Reasoning manipulation check', '', '```', effort.to_string(), '```',
                  'Reasoning tokens and latency describe resource use, not human thinking time. '
                  'Overlapping low/high resource use weakens the mechanism interpretation.']
    spending = json.loads((directory/'spending.json').read_text())
    lines += ['', '## Spending and interpretation', '',
              f"Recorded estimated charges/reservations: ${spending['charged_or_reserved_usd']:.4f}. Not an invoice or account balance.",
              'The original pilot remains separate. This redesigned protocol cannot confirm effects in humans. '
              'Do not repeatedly change prompts, exclusions, sample size, or models until p < .05. '
              'Use the pilot to fix measurement, then freeze a new protocol and collect independent confirmation data.']
    (directory/'RESULTS_REPORT.md').write_text('\n'.join(lines)+'\n')
    return '\n'.join(lines)

def sample_size_scenarios():
    from scipy.stats import norm
    # Conservative two-sided Bonferroni alpha .025 per hypothesis, 80% power.
    # d_z = meaningful paired block contrast / SD of that block contrast.
    factor = (norm.ppf(1-.025/2)+norm.ppf(.8))**2
    return pd.DataFrame([dict(standardized_paired_effect=d,
        approximate_groups_per_cell=max(8,int(np.ceil(factor/d**2))),
        total_groups=4*max(8,int(np.ceil(factor/d**2))),
        agents=16*max(8,int(np.ceil(factor/d**2)))) for d in (.3,.5,.8,1.)])

def performance_tables(rounds):
    """Operational outcomes remain reportable even when beta is unidentified."""
    rows = []
    for agent, f in rounds.groupby('agent_id'):
        f = f.sort_values('week')
        meta = f.iloc[0]
        variance = float(f.demand.var(ddof=1))
        incoming = float(f.demand.sum())
        rows.append(dict(agent_id=agent,group_id=meta.group_id,role=meta.role,
            trained=bool(meta.trained),effort=meta.effort,
            holding_cost=float(f.holding_cost.sum()),backlog_cost=float(f.backlog_cost.sum()),
            sales_revenue=float(f.sales_revenue.sum()),production_cost=float(f.production_cost.sum()),
            profit_contribution=float(f.profit_contribution.sum()),zero_order_rate=float((f.order==0).mean()),
            total_cost=float(f.cost.sum()),mean_inventory=float(f.inventory.mean()),
            mean_backlog=float(f.backlog.mean()),max_backlog=int(f.backlog.max()),
            terminal_backlog=int(f.backlog.iloc[-1]),terminal_inventory=int(f.inventory.iloc[-1]),
            cumulative_fulfillment=float(f.shipped.sum()/incoming) if incoming else np.nan,
            order_variance=float(f.order.var(ddof=1)),incoming_variance=variance,
            bullwhip_ratio=float(f.order.var(ddof=1)/variance) if variance>0 else np.nan))
    roles=pd.DataFrame(rows)
    groups=roles.groupby(['group_id','trained','effort']).agg(
        total_cost=('total_cost','sum'),total_profit=('profit_contribution','sum'),
        sales_revenue=('sales_revenue','sum'),production_cost=('production_cost','sum'),
        mean_zero_order_rate=('zero_order_rate','mean'),holding_cost=('holding_cost','sum'),
        backlog_cost=('backlog_cost','sum'),terminal_backlog_all_roles=('terminal_backlog','sum')).reset_index()
    retailers=roles[roles.role=='retailer'][['group_id','cumulative_fulfillment']].rename(
        columns={'cumulative_fulfillment':'customer_cumulative_fulfillment'})
    groups=groups.merge(retailers,on='group_id',validate='one_to_one')
    conditions=groups.groupby(['trained','effort']).agg(groups=('group_id','size'),
        mean_team_profit=('total_profit','mean'),median_team_profit=('total_profit','median'),
        mean_zero_order_rate=('mean_zero_order_rate','mean'),mean_team_cost=('total_cost','mean'),median_team_cost=('total_cost','median'),
        min_team_cost=('total_cost','min'),max_team_cost=('total_cost','max'),
        mean_backlog_cost=('backlog_cost','mean'),
        mean_customer_fulfillment=('customer_cumulative_fulfillment','mean')).reset_index()
    return roles,groups,conditions


def measurement_self_check():
    """Free known-answer estimator check plus a nonidentifiable counterexample.
    Not proof that GPT obeys this structural model or that game data identify beta.
    """
    rng=np.random.default_rng(12)
    n=150
    d=rng.uniform(2,20,n);ni=rng.uniform(-30,70,n);sl=rng.uniform(0,70,n)
    frame=pd.DataFrame(dict(week=np.arange(n),demand=d,net_inventory=ni,supply_line=sl))
    records=[]
    for beta in (0.,.3,.65,1.):
        frame['order']=predicted_orders([.55,.4,beta,45],d,ni,sl)
        fit=estimate_beta(frame)
        records.append(dict(case=f'known beta {beta}',true_beta=beta,estimated_beta=fit['beta'],
            usable=fit['usable'],passed=bool(fit['usable'] and abs(fit['beta']-beta)<.001)))
    frame['order']=d
    fit=estimate_beta(frame)
    records.append(dict(case='copy demand: beta must be unidentified',true_beta=np.nan,
        estimated_beta=np.nan,usable=fit['usable'],passed=not fit['usable']))
    return pd.DataFrame(records)


def save_game_dashboard(frame,directory,config):
    import matplotlib.pyplot as plt
    directory=Path(directory)
    roles,groups,conditions=performance_tables(frame)
    for name,table in [('role_performance',roles),('group_performance',groups),('condition_performance',conditions)]:
        table.to_csv(directory/(name+'.csv'),index=False)
    # Game snapshots occur after shipping, before ordering; costs match the simulator.
    weekly=frame.groupby(['trained','effort','week']).agg(
        mean_inventory=('inventory','mean'),mean_backlog=('backlog','mean'),
        mean_order=('order','mean'),mean_role_profit=('profit_contribution','mean')).reset_index()
    weekly.to_csv(directory/'weekly_performance.csv',index=False)
    fig,axes=plt.subplots(2,2,figsize=(11,7))
    for (trained,effort),f in weekly.groupby(['trained','effort']):
        label=('Trained' if trained else 'Control')+' / '+effort
        for ax,field,title in zip(axes.ravel(),['mean_inventory','mean_backlog','mean_order','mean_role_profit'],
                                ['Inventory','Backlog','Orders','Weekly profit contribution per role']):
            ax.plot(f.week,f[field],label=label);ax.set_title(title);ax.set_xlabel('Week');ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8)
    fig.suptitle('SYNTHETIC software check' if config['mode']=='offline' else 'GPT beer-game performance')
    fig.tight_layout();fig.savefig(directory/'supply_chain_performance.png',dpi=160);plt.close(fig)
    return roles,groups,conditions

def economic_sanity_check(weeks=36,seed=20260927):
    """Deterministic policy comparison to audit incentives; NOT GPT outcomes."""
    output=[]
    for label in ('never_order','replenish','order_100_each_week'):
        game=BeerGame();records=[]
        for demand in demand_path(0,weeks,seed):
            states=game.observe(demand)
            if label=='never_order':orders=[0]*4
            elif label=='order_100_each_week':orders=[100]*4
            else:
                orders=[max(0,int(round(s['demand']+.35*(48-s['net_inventory']-.65*s['supply_line'])))) for s in states]
            game.commit(orders);settle_week(states,orders)
            records.extend(dict(s,order=orders[i]) for i,s in enumerate(states))
        f=pd.DataFrame(records);retailer=f[f.role=='retailer']
        output.append(dict(policy=label,team_profit=float(f.profit_contribution.sum()),
            revenue=float(f.sales_revenue.sum()),production_cost=float(f.production_cost.sum()),
            holding_cost=float(f.holding_cost.sum()),backlog_cost=float(f.backlog_cost.sum()),
            zero_order_rate=float((f.order==0).mean()),
            customer_fulfillment=float(retailer.shipped.sum()/retailer.demand.sum())))
    return pd.DataFrame(output)
