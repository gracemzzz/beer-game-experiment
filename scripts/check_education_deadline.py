"""Audit frozen full-cohort prompts, new evidence and preservation of older files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from beergame_study import education_deadline_cohort as study


def independent_states(run, tables, manifest, plan):
    """Check saved model choices using the separate queue implementation in tests."""
    sys.path.insert(0, str(ROOT/'tests'))
    from test_education_deadline_cohort import independent_physical_replay
    verified = 0
    specs = {chain['chain_id']: chain for chain in plan['chains']}
    roles = ('retailer', 'wholesaler', 'distributor', 'factory')
    for task in plan['tasks']:
        if not study.accepted_path(run, task['task_id']).exists():
            continue
        payload = study.load_accepted(run, task['task_id'])['payload']
        for choice in payload['chains']:
            actual = tables['rounds'].loc[(tables['rounds'].task_id == task['task_id']) &
                                          (tables['rounds'].chain_id == choice['chain_id'])]
            actual = actual.set_index(['week', 'role'])
            expected = independent_physical_replay(specs[choice['chain_id']]['customer_demand'],
                                                   choice['orders'], manifest['config']['weeks'])
            assert len(actual) == len(expected)
            for state in expected:
                observed = actual.loc[(state['week'], roles[state['role']])]
                for key in ('inventory', 'backlog', 'received', 'demand', 'shipped', 'supply_line', 'cost'):
                    assert observed[key] == state[key], (task['task_id'], choice['chain_id'], state['week'], key)
                verified += 1
    return verified


def check():
    folder = ROOT/'reports/EDUCATION_DEADLINE_10S_60S'
    index = study.read(folder/'PLAN_INDEX.json')
    preflight = study.read(ROOT/'data/development/education_deadline_preflight_20261019/PLAN.json')
    result = dict(date='2026-10-19', human_observations=0, paid_api_calls=0,
                  independent_student_p_values=False, runs={})
    for category in ('website', 'pilot', 'capacity'):
        run = ROOT/index[category+'_run']
        manifest = study.audit(run)
        plan = study.read(run/'plan.json')
        tables = study.summarize(run)
        progress = study.progress(run)
        for row in tables['chains'].to_dict('records'):
            assert row['total_cost'] == row['cost_practice']+row['cost_model']+row['cost_automatic']
        expected_orders = (manifest['config']['weeks']-4)*manifest['config']['students']
        accepted = int(progress.accepted.sum())
        orders = int((tables['rounds'].phase == 'model').sum()) if not tables['rounds'].empty else 0
        assert orders == expected_orders*accepted
        assert len(tables['probes']) == manifest['config']['students']*accepted
        if category == 'website':
            assert len(plan['chains']) == 125 and plan['expected_responses'] == 6
        result['runs'][category] = dict(study_id=run.name, accepted=accepted,
            prepared_slots=len(progress), submitted_weekly_orders=orders,
            probe_pairs=len(tables['probes']), replayed_role_week_states=len(tables['rounds']),
            matched_contrast_rows=len(tables['contrasts']),
            independently_recomputed_states=independent_states(run, tables, manifest, plan))
    website = ROOT/index['website_run']
    plan = study.read(website/'plan.json')
    hashes = {}
    with ZipFile(folder/'Beer_Game_10s_60s_Prompts.zip') as archive:
        for task in plan['tasks']:
            filename = task['task_id']+'.txt'
            data = (website/'prompts'/filename).read_bytes()
            assert archive.read('prompts/'+filename) == data
            assert (folder/'prompts'/filename).read_bytes() == data
            prompt = data.decode('utf-8')
            context = json.loads(prompt.split('FROZEN INPUT DATA:\n')[1])
            assert len(context['chains']) == 125
            assert 'H1:' not in prompt and 'statistically significant' not in prompt
            hashes[task['task_id']] = hashlib.sha256(data).hexdigest()
    result['website_prompt_sha256'] = hashes
    readings = ROOT/'docs/education_deadline_20261019'
    counts = {name: len((readings/(name+'_lecture.txt')).read_text().split())
              for name in ('causal', 'control')}
    assert counts['causal'] == counts['control'] == 254
    result['lecture_words'] = counts
    slots = preflight['slots']
    assert len(slots) == 7
    assert len([s for s in slots if s['category'] == 'pilot']) == 6
    assert len([s for s in slots if s['category'] == 'capacity']) == 1
    for slot in slots:
        prompt = ROOT/slot['run']/'prompts'/(slot['task_id']+'.txt')
        assert hashlib.sha256(prompt.read_bytes()).hexdigest() == slot['prompt_sha256']
        assert slot['fork_turns'] == 'none' and slot['model_override'] is None and slot['effort_override'] is None
    result['preflight_slots_with_raw_output'] = sum((ROOT/s['response_path']).exists() for s in slots)
    receipts_file = ROOT/'data/development/education_deadline_preflight_20261019/CHECKS.json'
    if receipts_file.exists():
        receipts = study.read(receipts_file)
        for receipt in receipts['receipts']:
            slot = next(s for s in slots if s['category'] == receipt['category'] and s['task_id'] == receipt['task_id'])
            assert hashlib.sha256((ROOT/slot['response_path']).read_bytes()).hexdigest() == receipt['response_sha256']
            source_hash = receipt['source_inspection'].get('source_sha256')
            if source_hash:
                assert hashlib.sha256((ROOT/slot['serialization_path']).read_bytes()).hexdigest() == source_hash
        assert receipts['paid_api_calls'] == receipts['human_observations'] == 0
    # An observed technical failure is a finding, not a license to erase or refill it.
    baseline = study.read(ROOT/'reports/software_checks/education_deadline_before_20261019.json')['files']
    altered = []
    for filename, expected in baseline.items():
        path = ROOT/filename
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            altered.append(filename)
    assert not altered, 'Preserved evidence changed: '+str(altered[:10])
    result['prior_files_verified_unchanged'] = len(baseline)
    for category, output_name in [('pilot', 'pilot'), ('capacity', 'capacity_check'), ('website', 'website')]:
        output = folder/output_name
        if (output/'provenance.json').exists():
            provenance = study.read(output/'provenance.json')
            run = ROOT/index[category+'_run']
            for filename, expected in provenance['inputs_sha256'].items():
                assert hashlib.sha256((run/filename).read_bytes()).hexdigest() == expected
            for filename, expected in provenance['outputs_sha256'].items():
                assert hashlib.sha256((output/filename).read_bytes()).hexdigest() == expected
            assert provenance['api_calls'] == provenance['human_observations'] == 0
            assert (output/'results/RESULTS.xlsx').exists()
    return result


def main():
    checks = check()
    result = subprocess.run([sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover', '-s', 'tests',
                             '-p', 'test_education_deadline*.py', '-v'], cwd=ROOT,
                            capture_output=True, encoding='utf-8')
    log = ROOT/'reports/logs/education_deadline_20261019'
    log.mkdir(parents=True, exist_ok=True)
    (log/'offline_tests.log').write_text(result.stdout+result.stderr, encoding='utf-8')
    checks['offline_tests_exit_code'] = result.returncode
    destination = ROOT/'reports/software_checks/education_deadline_20261019.json'
    destination.write_text(json.dumps(checks, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(checks, indent=2))
    if result.returncode:
        print(result.stdout+result.stderr)
        raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
