"""Read saved API evidence and replay a completed game. Never calls an API."""
import ast
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from beergame_study.game import BeerGame, ROLES, demand_path, continuation
from beergame_study.analysis import game_tables
from beergame_study.prompts import make_messages, validate_decision, SCHEMA, RULE_ANSWERS
from beergame_study.api import digest


def audit(run_dir, output):
    run_dir, output = Path(run_dir).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((run_dir / 'manifest.json').read_text())
    config = manifest['config']
    progress = json.loads((run_dir / 'progress.json').read_text())
    ledger = json.loads((run_dir / 'group_attempts.json').read_text())
    rules = json.loads((run_dir / 'rules_validation.json').read_text())
    assert config['mode'] == 'api' and config['stage'] == 'game'
    assert progress['phase'] == 'complete'
    source_matches = {name: hashlib.sha256((ROOT / 'src/beergame_study' / name).read_bytes()).hexdigest() == sha
                      for name, sha in manifest['source_sha256'].items()}
    assert all(source_matches.values()), 'Replay must use the recorded source version.'
    evidence_files = [run_dir / n for n in ('manifest.json', 'progress.json', 'group_attempts.json',
                     'rules_validation.json', 'rounds.csv', 'continuation.csv', 'all_candidate_rounds.csv', 'spending.json')]
    evidence_files += sorted((run_dir / 'requests').glob('*.json'))
    hashes = {str(p.relative_to(run_dir)): hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence_files}
    frame = pd.read_csv(run_dir / 'rounds.csv')
    tail = pd.read_csv(run_dir / 'continuation.csv')
    candidates = pd.read_csv(run_dir / 'all_candidate_rounds.csv')
    keys = ['group_id', 'week', 'role']
    pd.testing.assert_frame_equal(frame.sort_values(keys).reset_index(drop=True),
                                  candidates.sort_values(keys).reset_index(drop=True))
    assert not frame.duplicated(keys).any() and not tail.duplicated(keys).any()
    assert frame.group_id.nunique() == 2 * config['groups_per_condition']
    records = [json.loads(p.read_text()) | {'file': p.name} for p in sorted((run_dir / 'requests').glob('*.json'))]
    lookup = {}
    for r in records:
        i = r['identity']
        k = (i['group'], i['role'], i.get('week'), i['stage'])
        assert k not in lookup, 'Unexpected retries: inspect rather than silently deduplicate.'
        lookup[k] = r
        assert r['status'] == 'ok' and not r.get('synthetic', False) and not r.get('refused', False)
        assert r['response']['model'] == config['model']
        assert r['usage']['reasoning_tokens'] == 0
        assert r['usage']['output_tokens'] <= r['limit']
        raw = r['response']
        text = ''.join(c.get('text', '') for o in raw.get('output', []) if o.get('type') == 'message'
                       for c in o.get('content', []) if c.get('type') == 'output_text')
        assert text == r['text'] and raw['status'] == r['response_status']
        u = r['usage']; rates = manifest['rates']
        cost = ((u['input_tokens'] - u['cached_input_tokens']) * rates['input'] +
                u['cached_input_tokens'] * rates['cached'] + u['output_tokens'] * rates['output']) / 1e6
        assert abs(cost - r['charge_usd']) < 1e-12
        assert u['input_tokens'] == raw['usage']['input_tokens']
        assert u['output_tokens'] == raw['usage']['output_tokens']
    assert len({r['response']['id'] for r in records}) == len(records)
    assert all(x['passed'] and x['attempt'] == 1 for x in rules)
    for r in records:
        if r['identity']['stage'] == 'rules':
            assert json.loads(r['text']) == RULE_ANSWERS and r['response_status'] == 'completed'
    decisions, observed_rows, replayed_tail = 0, 0, 0
    for gid, g in frame.groupby('group_id'):
        game = BeerGame(); history = [[] for _ in ROLES]
        cond = g.condition.iloc[0]
        budget = config['short_tokens'] if cond == 'short' else config['adequate_tokens']
        assert len(g) == 4 * config['weeks']
        for week, demand in enumerate(demand_path(config['weeks']), 1):
            states = game.observe(demand); orders = []
            for ri, state in enumerate(states):
                row = g[(g.week == week) & (g.role == state['role'])].iloc[0]
                for name, value in state.items():
                    got = ast.literal_eval(row[name]) if name == 'shared_inventory' else row[name]
                    assert got == value, (gid, week, state['role'], name, got, value)
                observed_rows += 1
                q = int(row.order); orders.append(q)
                assert q == row.order and q >= 0
                if week <= config['warmup_weeks']:
                    assert q == 4 and row.phase == 'warmup'
                else:
                    ident = dict(group=gid, role=state['role'], week=week)
                    plan = lookup[(gid, state['role'], week, 'plan')]
                    final = lookup[(gid, state['role'], week, 'final')]
                    assert plan['messages'] == make_messages(state, history[ri], budget, 'plan', identity=digest(ident))
                    assert final['messages'] == make_messages(state, history[ri], budget, 'final', plan['text'], digest(ident))
                    assert plan['limit'] == budget and final['limit'] == config['final_tokens']
                    assert final['schema'] == SCHEMA
                    answer = json.loads(final['text'])
                    assert final['response_status'] == 'completed' and validate_decision(answer, state)
                    assert answer['order'] == q
                    assert row.plan_tokens == plan['usage']['output_tokens']
                    assert row.final_tokens == final['usage']['output_tokens']
                    assert bool(row.plan_truncated) == (plan['response_status'] == 'incomplete')
                    if row.plan_truncated: assert plan['incomplete_reason'] == 'max_output_tokens'
                    decisions += 1
                history[ri].append({k: (q if k == 'order' else state[k]) for k in
                                   ('week', 'demand', 'inventory', 'backlog', 'supply_line', 'order', 'shared_inventory')})
            game.commit(orders)
        for state in continuation(game, demand, config['continuation_weeks']):
            row = tail[(tail.group_id == gid) & (tail.week == state['week']) & (tail.role == state['role'])].iloc[0]
            for name, value in state.items():
                got = ast.literal_eval(row[name]) if name == 'shared_inventory' else row[name]
                assert got == value, (gid, 'continuation', name)
            replayed_tail += 1
    assert len(records) == decisions * 2 + len(rules)
    role, beta, groups, hypotheses = game_tables(frame, tail, config, True, any(x['replacement'] for x in ledger))
    for name, df in [('role_metrics', role), ('beta_fits', beta), ('group_outcomes', groups), ('hypotheses', hypotheses)]:
        # Validate the notebook-generated statistics independently from saved tables.
        old = pd.read_csv(run_dir / (name + '.csv'))
        numeric = [c for c in df if pd.api.types.is_numeric_dtype(df[c]) and c in old]
        for c in numeric:
            assert np.allclose(df[c].to_numpy(float), old[c].to_numpy(float), equal_nan=True), (name, c)
        df.to_csv(output / (name + '.csv'), index=False)
    agent = frame[frame.phase == 'agent']
    zero_flags = agent[(agent.order == 0) & (agent.inventory == 0) & (agent.backlog > 0) & (agent.supply_line == 0)]
    zero_flags.to_csv(output / 'zero_order_review.csv', index=False)
    request_index = pd.DataFrame([dict(file=r['file'], group_id=r['identity']['group'],
          condition=r['identity']['group'].split('_')[1], role=r['identity']['role'],
          week=r['identity'].get('week'), stage=r['identity']['stage'], status=r['response_status'],
          limit=r['limit'], **r['usage'], charge_usd=r['charge_usd'], elapsed_s=r['elapsed_s'],
          created_utc=r['created_utc'], text=r['text']) for r in records])
    request_index.to_csv(output / 'request_index.csv', index=False)
    # Offline mechanical comparisons, explicitly not extra LLM observations or a treatment estimate.
    comparisons = []
    def simulate(policy=None, override=None):
        game = BeerGame(); rows = []
        short = frame[frame.condition == 'short']
        for w, demand in enumerate(demand_path(config['weeks']), 1):
            states = game.observe(demand)
            if w <= config['warmup_weeks']: orders = [4] * 4
            elif policy == 'incoming_demand': orders = [s['demand'] for s in states]
            elif policy == 'always_zero': orders = [0] * 4
            elif policy == 'always_40': orders = [40] * 4
            else: orders = [int(short[(short.week == w) & (short.role == r)].order.iloc[0]) for r in ROLES]
            if override and w == override[0]: orders[3] = override[1]
            rows.extend(states); game.commit(orders)
        scored = rows + continuation(game, demand, config['continuation_weeks'])
        return sum(s['cost'] for s in scored)
    for policy in ('incoming_demand', 'always_zero', 'always_40'):
        comparisons.append(dict(scenario=policy, total_cost=simulate(policy=policy), kind='offline deterministic policy'))
    comparisons.append(dict(scenario='Recorded short orders replay', total_cost=simulate(), kind='exact factual replay'))
    comparisons.append(dict(scenario='Factory week 29: produce 276 instead of 0; all later agent orders held fixed',
                            total_cost=simulate(override=(29, 276)), kind='post hoc mechanical sensitivity, not adaptive agent rerun'))
    pd.DataFrame(comparisons).to_csv(output / 'offline_comparisons.csv', index=False)
    result = dict(run_id=run_dir.name, live_calls_by_this_audit=0, source_matches=source_matches,
        groups=int(frame.group_id.nunique()), roles=int(frame.groupby(['group_id', 'role']).ngroups),
        decisions_verified=decisions, game_state_rows_replayed=observed_rows,
        continuation_state_rows_replayed=replayed_tail, saved_api_responses_verified=len(records),
        rules_passed_first_attempt=len(rules), failed_requests=0, replacements=0,
        estimated_api_cost_usd=sum(r['charge_usd'] for r in records), elapsed_s=progress['elapsed_s'],
        tokens={k:sum(r['usage'][k] for r in records) for k in ('input_tokens','output_tokens','cached_input_tokens','reasoning_tokens')},
        progress_counter_note=f"progress.json decisions={progress['decisions']} is a stale display field; verified {decisions} actual final responses and committed orders.",
        matched_prompt_and_state_payloads=decisions*2, zero_order_review_count=len(zero_flags),
        offline_comparisons=comparisons, immutable_evidence_sha256=hashes)
    assert abs(result['estimated_api_cost_usd'] - progress['estimated_cost_usd']) < 1e-10
    (output / 'audit.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    assert all(hashlib.sha256((run_dir / p).read_bytes()).hexdigest() == sha for p, sha in hashes.items())
    return result


if __name__ == '__main__':
    if len(sys.argv) != 3: raise SystemExit('Usage: audit_completed_game.py RUN_DIRECTORY OUTPUT_DIRECTORY')
    result = audit(sys.argv[1], sys.argv[2])
    print(json.dumps({k:v for k,v in result.items() if k not in ('immutable_evidence_sha256', 'source_matches')}, indent=2))
