"""Offline/mocked scientific and spending invariants. Never construct a live client."""
import asyncio
import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from beergame_study.anytime_protocol import (AnytimeConfig, calibration_bank, demand_schedule,
    manipulation_screen, messages, selected_order, supply_line_probes)
from beergame_study.anytime_study import (campaign_allowance, paired_choices, prepare, run_study, load_calibration)
from beergame_study.anytime_transport import Gateway
from beergame_study.anytime_report import analyze, paired_inference, planned_pairs, variance_ratio
from beergame_study.reasoning_protocol import MODEL, RULE_ANSWERS, StudyStopped, save
from beergame_study.student_profiles import assignment, profiles


class MockClient:
    def __init__(self, truncate_initial=False, truncate_revision=False, revision_error=False):
        self.calls = []
        self.responses = SimpleNamespace(create=self.create)
        self.truncate_initial = truncate_initial
        self.truncate_revision = truncate_revision
        self.revision_error = revision_error

    async def create(self, **kwargs):
        self.calls.append(copy.deepcopy(kwargs))
        payload = json.loads(kwargs['input'][1]['content'])
        revision = 'submitted_order' in payload
        if revision and self.revision_error:
            raise ConnectionError('never persist a secret in this exception')
        rules = 'questions' in payload
        answer = RULE_ANSWERS if rules else {'order': payload['current_state']['demand']}
        truncate = not rules and ((revision and self.truncate_revision) or (not revision and self.truncate_initial))
        total = kwargs['max_output_tokens'] if truncate else 1500
        return dict(model=MODEL, status='incomplete' if truncate else 'completed',
                    incomplete_details={'reason': 'max_output_tokens'} if truncate else None,
                    output=[] if truncate else [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(answer)}]}],
                    usage=dict(input_tokens=1000, input_tokens_details={'cached_tokens': 0}, output_tokens=total,
                               output_tokens_details={'reasoning_tokens': total-12}))


class AnytimeTests(unittest.TestCase):
    def config(self, **kwargs):
        return AnytimeConfig(mode='api', weeks=24, request_interval_s=0, **kwargs)

    def test_varying_iid_demand_prespecified_and_paired(self):
        path = demand_schedule(40, 17)
        self.assertEqual(path[:4], [4]*4)
        self.assertEqual(path, demand_schedule(40, 17))
        self.assertTrue(all(0 <= d <= 8 for d in path[4:]))
        self.assertGreater(np.var(path[4:]), 0)
        self.assertNotEqual(path, demand_schedule(40, 18))

    def test_personalities_balanced_across_roles_and_in_prompt(self):
        assignments = [assignment(17, block) for block in range(4)]
        for role in range(4):
            self.assertEqual({a[role] for a in assignments}, set(profiles()))
        state = supply_line_probes()[0]['state']
        texts = [messages(state | {'profile_id': key}, []) for key in profiles()]
        self.assertEqual(len({m[1]['content'] for m in texts}), 4)
        self.assertEqual(len({m[0]['content'] for m in texts}), 1)

    def test_calibration_has_disjoint_full_histories(self):
        cases = calibration_bank()
        self.assertEqual(len(cases), 16)
        self.assertEqual(len({c['case_id'] for c in cases}), 16)
        self.assertTrue(all(len(c['history']) == c['state']['week']-1 for c in cases))
        self.assertGreater(max(len(c['history']) for c in cases), 25)
        self.assertTrue(all('supply_line' not in c['state'] and len(c['state']['deliveries_due']) == 2 for c in cases))

    def test_fixed_high_temperature_omitted_and_shared_initial(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient()
            g = Gateway(folder, self.config(), client)
            state = supply_line_probes()[0]['state']
            choices = asyncio.run(paired_choices(g, [state, state], [[], []], {'block': 0, 'week': 5}))
            self.assertEqual(len(client.calls), 2)
            self.assertEqual(choices[0]['initial_request_key'], choices[1]['initial_request_key'])
            self.assertEqual(choices[0]['total_output_tokens'], 1500)
            self.assertEqual(choices[1]['total_output_tokens'], 3000)
            self.assertTrue(all(c['reasoning'] == {'effort': 'high'} and 'temperature' not in c for c in client.calls))

    def test_different_histories_not_deduplicated(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient()
            g = Gateway(folder, self.config(), client)
            s = supply_line_probes()[0]['state']
            result = asyncio.run(paired_choices(g, [s, s], [[], [{'week': 1, 'order': 7}]], {'block': 0}))
            self.assertEqual(len(client.calls), 3)
            self.assertFalse(result[0]['shared_initial'])

    def test_independent_blocks_never_reuse_draws(self):
        async def exercise(folder):
            client = MockClient()
            g = Gateway(folder, self.config(), client)
            s = supply_line_probes()[0]['state']
            for block in (0, 1, 0):
                await paired_choices(g, [s, s], [[], []], {'block': block})
            return len(client.calls)
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(asyncio.run(exercise(folder)), 4)

    def test_truncated_revision_retains_current_submission_not_previous_week(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient(truncate_revision=True)
            g = Gateway(folder, self.config(), client)
            s = supply_line_probes()[0]['state'] | {'demand': 23}
            result = asyncio.run(paired_choices(g, [s, s], [[], []], {'block': 0}))
            self.assertEqual(result[1]['order'], 23)
            self.assertFalse(result[1]['fallback'])
            self.assertEqual(result[1]['order_source'], 'initial')
            self.assertEqual(result[1]['total_output_tokens'], 1500+8192)

    def test_missing_initial_stops_without_revision(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient(truncate_initial=True)
            g = Gateway(folder, self.config(), client)
            s = supply_line_probes()[0]['state']
            with self.assertRaises(StudyStopped):
                asyncio.run(paired_choices(g, [s, s], [[], []], {'block': 0}))
            self.assertEqual(len(client.calls), 1)

    def test_technical_revision_failure_is_not_token_treatment(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient(revision_error=True)
            g = Gateway(folder, self.config(), client)
            s = supply_line_probes()[0]['state']
            with self.assertRaises(StudyStopped):
                asyncio.run(paired_choices(g, [s, s], [[], []], {'block': 0}))
            self.assertNotIn('never persist a secret', ''.join(p.read_text() for p in (Path(folder)/'requests').glob('*.json')))

    def test_zero_is_a_model_choice(self):
        with tempfile.TemporaryDirectory() as folder:
            g = Gateway(folder, self.config(), MockClient())
            s = supply_line_probes()[0]['state'] | {'demand': 0}
            result = asyncio.run(paired_choices(g, [s, s], [[], []], {'block': 0}))
            self.assertEqual([r['order'] for r in result], [0, 0])

    def test_hard_cap_before_call_and_campaign_includes_prior_spend(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient()
            g = Gateway(folder, self.config(budget_usd=.0001), client)
            s = supply_line_probes()[0]['state']
            with self.assertRaises(StudyStopped):
                asyncio.run(paired_choices(g, [s, s], [[], []], {'block': 0}))
            self.assertEqual(len(client.calls), 0)
            root = Path(folder)
            cfg = self.config(budget_usd=20)
            directory = prepare(cfg, root)
            effective, prior = campaign_allowance(cfg, directory, root)
            self.assertAlmostEqual(effective.budget_usd, 4.80639325)
            self.assertAlmostEqual(prior, 5.19360675)

    def test_known_probe_sensitivity_recoverable_without_nonlinear_fit(self):
        cases = supply_line_probes()
        for beta in (0, .5, 1):
            quantities = [max(0, int(48-beta*sum(c['state']['deliveries_due']))) for c in cases]
            self.assertTrue(all((quantities[i]-quantities[i+1])/24 == beta for i in range(0, 8, 2)))

    def test_power_and_degenerate_inference(self):
        self.assertIsNone(paired_inference([0]*12, True)['p_raw'])
        self.assertIsNone(paired_inference([1, 2], True)['p_raw'])
        self.assertGreater(planned_pairs(.5)['pairs'], planned_pairs(.8)['pairs'])
        self.assertIsNone(variance_ratio([1, 2], [4, 4]))

    def test_failed_calibration_buys_no_games_and_exports_partial_report(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient(truncate_initial=True)
            run = asyncio.run(run_study(self.config(), client, root=folder))
            progress = json.loads((run/'progress.json').read_text())
            self.assertEqual(progress['phase'], 'stopped')
            self.assertFalse((run/'rounds.csv').exists())
            self.assertEqual(len(client.calls), 16)
            self.assertTrue((Path(folder)/'reports'/run.name/'Anytime_Study_Report.docx').exists())

    def test_full_mocked_game_report_and_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient()
            run = asyncio.run(run_study(self.config(), client, root=folder))
            result = analyze(run)
            self.assertEqual(result['progress']['phase'], 'complete')
            self.assertTrue(result['screen']['passed'])
            self.assertTrue(result['main_manipulation_passed'])
            self.assertEqual(result['audit']['physical_states_replayed'], 2*36*4)
            self.assertEqual(len(result['rounds'][result['rounds'].phase == 'model']), 160)
            self.assertTrue(result['hypotheses'].p_raw.isna().all())
            bought = len(client.calls)
            asyncio.run(run_study(self.config(), client, root=folder))
            self.assertEqual(len(client.calls), bought)
            frame = pd.read_csv(run/'rounds.csv')
            frame.loc[frame.phase == 'model', 'order'] += 1
            frame.to_csv(run/'rounds.csv', index=False)
            with self.assertRaises(ValueError):
                analyze(run)

    def test_calibration_reuse_revalidates_raw_prompts(self):
        with tempfile.TemporaryDirectory() as folder:
            client = MockClient()
            run = asyncio.run(run_study(self.config(), client, root=folder, calibration_only=True))
            self.assertEqual(len(load_calibration(run, self.config())), 16)
            record_path = next((run/'requests').glob('*.json'))
            record = json.loads(record_path.read_text())
            record['messages'][0]['content'] = 'tampered'
            save(record_path, record)
            with self.assertRaises(StudyStopped):
                load_calibration(run, self.config())


if __name__ == '__main__':
    unittest.main()
