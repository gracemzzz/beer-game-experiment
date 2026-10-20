"""Offline controls for the separate three-arm, whole-cohort H1-H4 workflow.

All submitted trajectories here are explicitly synthetic software fixtures.  These
checks test data integrity and replay arithmetic; they are not model observations
and do not establish any hypothesis, treatment effect, or statistical power.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from beergame_study.education_deadline_cohort import (
    Config, audit, import_response, load_accepted, next_task, prepare, progress,
    prompt_text, read, replay, summarize, synthetic_response, task_info,
    validate_response,
)


ARMS = ("a60_control", "b10_control", "c10_education")


def independent_physical_replay(demand_path, choices, weeks):
    """Recompute the stated queueing rules without the production BeerGame class."""
    inventory, backlog, outstanding = [12] * 4, [0] * 4, [12] * 4
    deliveries = [[4, 4], [4, 4], [4, 4], [4, 4, 4]]
    incoming, last = [4] * 3, [4] * 4
    states = []
    for week in range(1, weeks + 13):
        customer = demand_path[min(week - 1, weeks - 1)]
        demand = [customer] + incoming
        receipts = [queue.pop(0) for queue in deliveries]
        shipped = []
        for role in range(4):
            inventory[role] += receipts[role]
            outstanding[role] -= receipts[role]
            owed = backlog[role] + demand[role]
            shipped.append(min(inventory[role], owed))
            inventory[role] -= shipped[role]
            backlog[role] = owed - shipped[role]
            states.append(dict(week=week, role=role,
                inventory=inventory[role], backlog=backlog[role],
                received=receipts[role], demand=demand[role],
                shipped=shipped[role], supply_line=outstanding[role],
                cost=inventory[role] / 2 + backlog[role]))
        for role in range(3):
            deliveries[role].append(shipped[role + 1])
        orders = [4] * 4 if week <= 4 else choices[week - 5] if week <= weeks else last
        outstanding = [outstanding[i] + orders[i] for i in range(4)]
        incoming = orders[:3]
        deliveries[3].append(orders[3])
        last = orders
    return states


class EducationDeadlineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cfg = Config(students=16, repetitions=2, synthetic=True, label="software-test")
        self.run = prepare(self.cfg, root=self.root)
        self.plan = read(self.run / "plan.json")
        self.sequence = 0

    def tearDown(self):
        self.tmp.cleanup()

    def task(self, arm=ARMS[0], repetition=1):
        return next(t for t in self.plan["tasks"]
                    if t["arm"] == arm and t["repetition"] == repetition)

    def payload(self, task_id):
        return json.loads(synthetic_response(self.run, task_id))

    def put(self, task_id, payload=None, *, raw=None, **overrides):
        self.sequence += 1
        source = self.root / ("submission_" + str(self.sequence) + ".json")
        data = raw if raw is not None else json.dumps(
            self.payload(task_id) if payload is None else payload).encode("utf-8")
        source.write_bytes(data)
        options = dict(model_label=self.cfg.model_label, effort_label=self.cfg.effort_label,
                       session_label="synthetic-session-" + str(self.sequence),
                       confirm_full_prompt=True, evidence_kind="synthetic_test")
        options.update(overrides)
        return import_response(self.run, task_id, source, **options)

    def test_whole_cohort_plan_has_three_arms_and_fixed_repeats(self):
        self.assertEqual(self.plan["fictional_identities"], 16)
        self.assertEqual(self.plan["generation_role_trajectories"], 96)
        self.assertEqual(self.plan["expected_responses"], 6)
        self.assertEqual(len(self.plan["chains"]), 4)
        expected_ids = {c["chain_id"] for c in self.plan["chains"]}
        for task in self.plan["tasks"]:
            self.assertEqual(set(task["chain_ids"]), expected_ids)
            self.assertTrue((self.run / "prompts" / (task["task_id"] + ".txt")).exists())
            _, chains = task_info(self.run, task["task_id"])
            self.assertEqual({c["chain_id"] for c in chains}, expected_ids)
        self.assertEqual(prepare(self.cfg, root=self.root), self.run)
        other = prepare(Config(students=16, repetitions=2, synthetic=True,
                               label="software-test", seed=self.cfg.seed + 1), root=self.root)
        self.assertNotEqual(other, self.run)

    def test_invalid_configuration_and_synthetic_gate(self):
        for kwargs in ({"students": 501}, {"students": True}, {"weeks": 4},
                       {"repetitions": 0}, {"effort_label": "low"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Config(**kwargs).validate()
        actual = prepare(Config(students=16, repetitions=1, label="not-a-fixture"), root=self.root)
        task_id = read(actual / "plan.json")["tasks"][0]["task_id"]
        with self.assertRaises(ValueError):
            synthetic_response(actual, task_id)

    def test_case_prompts_and_lectures_do_not_depend_on_accepted_outputs(self):
        task = self.task(ARMS[2])
        before = prompt_text(self.run, task["task_id"])
        self.put(task["task_id"])
        self.assertEqual(prompt_text(self.run, task["task_id"]), before)
        self.assertEqual(next_task(self.run)["task_id"], self.plan["tasks"][0]["task_id"])
        self.assertEqual(self.task(ARMS[0])["deadline_seconds"], 60)
        self.assertEqual(self.task(ARMS[1])["deadline_seconds"], 10)
        self.assertEqual(self.task(ARMS[2])["deadline_seconds"], 10)
        self.assertEqual(self.task(ARMS[0])["lecture_id"], self.task(ARMS[1])["lecture_id"])
        self.assertNotEqual(self.task(ARMS[1])["lecture_id"], self.task(ARMS[2])["lecture_id"])

    def test_strict_chain_shape_and_order_types(self):
        task_id = self.task()["task_id"]
        base = self.payload(task_id)
        mutations = [
            lambda p: p["chains"].pop(),
            lambda p: p["chains"][0]["orders"].pop(),
            lambda p: p["chains"][0]["orders"][0].pop(),
            lambda p: p["chains"][0]["probes"].pop(),
            lambda p: p["chains"][1].update(chain_id=p["chains"][0]["chain_id"]),
            lambda p: p["chains"][0].update(chain_id="unknown-chain"),
        ]
        for value in (-1, 1.5, True, None, "4"):
            mutations.append(lambda p, value=value: p["chains"][0]["orders"][0].__setitem__(0, value))
            mutations.append(lambda p, value=value: p["chains"][0]["probes"][0].__setitem__(0, value))
        for index, mutate in enumerate(mutations):
            payload = copy.deepcopy(base)
            mutate(payload)
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                validate_response(self.run, task_id, json.dumps(payload))

    def test_identifiers_lecture_rules_and_extra_metrics_are_strict(self):
        task_id = self.task()["task_id"]
        base = self.payload(task_id)
        mutations = [
            lambda p: p.update(study_id="other-run"),
            lambda p: p.update(task_id="other-task"),
            lambda p: p.update(deadline_seconds=True),
            lambda p: p.update(deadline_seconds=180),
            lambda p: p.update(lecture_id="other-lecture"),
            lambda p: p.update(complete=False),
            lambda p: p.update(cost=42),
            lambda p: p["rules"].update(backlog_includes_current_unfilled_demand="true"),
            lambda p: p["rules"].update(factory_order_week_7_arrival_week="Week 10"),
            lambda p: p["rules"].update(three_week_backlog_cost="$15"),
        ]
        for index, mutate in enumerate(mutations):
            payload = copy.deepcopy(base)
            mutate(payload)
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                validate_response(self.run, task_id, json.dumps(payload))

    def test_duplicate_keys_truncation_and_explanatory_text_rejected(self):
        task_id = self.task()["task_id"]
        text = json.dumps(self.payload(task_id))
        bad = (text[:-1], "Here is the result: " + text,
               text.replace('"complete": true', '"complete": true, "complete": true'))
        for response in bad:
            with self.subTest(response=response[-60:]), self.assertRaises(ValueError):
                validate_response(self.run, task_id, response)

    def test_original_bytes_locked_acceptance_and_raw_tamper(self):
        task_id = self.task()["task_id"]
        raw = ("\r\n```json\r\n" + json.dumps(self.payload(task_id), indent=2)
               + "\r\n```\r\n  ").encode("utf-8")
        entry = self.put(task_id, raw=raw)
        path = self.run / entry["raw_path"]
        self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(entry["raw_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(load_accepted(self.run, task_id)["payload"], self.payload(task_id))
        with self.assertRaises(ValueError):
            self.put(task_id)
        self.assertEqual(path.read_bytes(), raw)
        path.write_bytes(raw + b" ")
        with self.assertRaises(ValueError):
            load_accepted(self.run, task_id)

    def test_bad_rule_import_retains_original_without_normalization(self):
        task_id = self.task()["task_id"]
        payload = self.payload(task_id)
        payload["rules"]["three_week_backlog_cost"] = "$15"
        raw = json.dumps(payload).encode("utf-8")
        with self.assertRaises(ValueError):
            self.put(task_id, raw=raw)
        attempts = list((self.run / "attempts").glob("*.txt"))
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].read_bytes(), raw)
        self.assertFalse((self.run / "accepted" / (task_id + ".json")).exists())
        self.assertFalse((self.run / "derived").exists())

    def test_non_utf8_rejection_retains_exact_original_bytes(self):
        task_id = self.task()["task_id"]
        raw = b"\xff\xfe\x00not JSON\r\n"
        with self.assertRaises(ValueError):
            self.put(task_id, raw=raw)
        attempt = next((self.run / "attempts").glob("*.txt"))
        self.assertEqual(attempt.read_bytes(), raw)
        self.assertEqual(read(attempt.with_suffix(".json"))["status"], "rejected")
        self.assertFalse((self.run / "accepted" / (task_id + ".json")).exists())

    def test_technical_circuit_breaker_retains_unclipped_response(self):
        task_id = self.task()["task_id"]
        payload = self.payload(task_id)
        payload["chains"][0]["orders"][0][0] = 100001
        text = json.dumps(payload)
        # The schema has no behavioral order cap. Replay can separately refuse
        # a scale beyond its numeric capacity while retaining the entire reply.
        self.assertEqual(validate_response(self.run, task_id, text), payload)
        with self.assertRaises(ValueError):
            self.put(task_id, raw=text.encode("utf-8"))
        attempt = next((self.run / "attempts").glob("*.txt"))
        receipt = read(attempt.with_suffix(".json"))
        self.assertEqual(attempt.read_bytes(), text.encode("utf-8"))
        self.assertEqual(receipt["status"], "replay_failed")
        self.assertEqual(receipt["payload"]["chains"][0]["orders"][0][0], 100001)
        self.assertFalse((self.run / "accepted" / (task_id + ".json")).exists())

    def test_provenance_and_evidence_kind_required(self):
        task_id = self.task()["task_id"]
        for overrides in ({"model_label": "different"}, {"effort_label": "high"},
                          {"session_label": " "}, {"confirm_full_prompt": False},
                          {"evidence_kind": "model_output"}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.put(task_id, **overrides)
        self.assertFalse((self.run / "accepted" / (task_id + ".json")).exists())

    def test_plan_source_and_prompt_tamper_detected(self):
        candidates = [self.run / "plan.json",
                      next(p for p in (self.run / "source_implementation").rglob("*") if p.is_file()),
                      self.run / "prompts" / (self.task()["task_id"] + ".txt")]
        for path in candidates:
            original = path.read_bytes()
            with self.subTest(path=path.name):
                if path.name == "plan.json":
                    changed = json.loads(original)
                    changed["fictional_identities"] += 4
                    path.write_text(json.dumps(changed), encoding="utf-8")
                else:
                    path.write_bytes(original + b" ")
                try:
                    with self.assertRaises(ValueError):
                        audit(self.run)
                finally:
                    path.write_bytes(original)
        audit(self.run)

    def test_accepted_payload_tamper_detected(self):
        task_id = self.task()["task_id"]
        self.put(task_id)
        path = self.run / "accepted" / (task_id + ".json")
        accepted = read(path)
        accepted["payload"]["chains"][0]["orders"][0][0] += 1
        path.write_text(json.dumps(accepted), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_accepted(self.run, task_id)

    def test_coherent_provenance_tamper_cannot_claim_measured_time(self):
        task_id = self.task()["task_id"]
        entry = self.put(task_id)
        accepted_path = self.run / "accepted" / (task_id + ".json")
        receipt_path = (self.run / entry["raw_path"]).with_suffix(".json")
        changed = copy.deepcopy(entry)
        changed["actual_wall_time_s"] = 10
        data = json.dumps(changed).encode("utf-8")
        accepted_path.write_bytes(data)
        receipt_path.write_bytes(data)
        with self.assertRaises(ValueError):
            load_accepted(self.run, task_id)

    def test_partial_comparisons_require_the_actual_matched_arms(self):
        self.put(self.task(ARMS[0])["task_id"])
        self.assertTrue(summarize(self.run)["contrasts"].empty)
        self.put(self.task(ARMS[1])["task_id"])
        partial = summarize(self.run)["contrasts"]
        self.assertEqual(set(partial.hypothesis), {"H1", "H2"})
        self.assertEqual(len(partial), 8)  # Four matched chains, two outcomes.
        self.assertEqual(set(partial.repetition), {1})
        self.put(self.task(ARMS[2])["task_id"])
        complete_repetition = summarize(self.run)["contrasts"]
        self.assertEqual(set(complete_repetition.hypothesis), {"H1", "H2", "H3", "H4"})
        self.assertEqual(len(complete_repetition), 16)

    def test_complete_null_controls_and_identity_reuse(self):
        for task in self.plan["tasks"]:
            self.put(task["task_id"])
        rounds, probes, imports = replay(self.run)
        tables = summarize(self.run)
        self.assertEqual(len(rounds), 6 * 16 * 36)
        self.assertEqual(len(probes), 6 * 16)
        self.assertEqual(len(imports), 6)
        self.assertEqual(len(tables["chains"]), 24)
        self.assertEqual(len(tables["roles"]), 96)
        self.assertEqual(rounds.participant_id.nunique(), 16)
        self.assertEqual(len(tables["contrasts"]), 32)
        self.assertTrue((tables["contrasts"].estimate == 0).all())
        np.testing.assert_array_equal(rounds.cost, .5 * rounds.inventory + rounds.backlog)
        for table in tables.values():
            if "p_value" in table.columns:
                self.assertTrue(table.p_value.isna().all())
        self.assertTrue(progress(self.run).accepted.all())
        self.assertIsNone(next_task(self.run))

    def test_known_proxy_contrasts_and_independent_cost_replay(self):
        orders = {ARMS[0]: 4, ARMS[1]: 8, ARMS[2]: 2}
        probes = {ARMS[0]: [8, 4], ARMS[1]: [8, 8], ARMS[2]: [12, 0]}
        payloads = {}
        for arm in ARMS:
            task_id = self.task(arm)["task_id"]
            payload = self.payload(task_id)
            for chain in payload["chains"]:
                chain["orders"] = [[orders[arm]] * 4 for _ in range(self.cfg.weeks - 4)]
                chain["probes"] = [probes[arm][:] for _ in range(4)]
            payloads[arm] = payload
            self.put(task_id, payload)
        tables = summarize(self.run)
        contrasts = tables["contrasts"]
        np.testing.assert_allclose(contrasts.loc[contrasts.hypothesis == "H1", "estimate"], -4 / 24)
        np.testing.assert_allclose(contrasts.loc[contrasts.hypothesis == "H3", "estimate"], 12 / 24)
        self.assertEqual(contrasts.groupby("hypothesis").expected_sign.first().to_dict(),
                         {"H1": -1, "H2": 1, "H3": 1, "H4": -1})
        role_names = ("retailer", "wholesaler", "distributor", "factory")
        totals = {}
        for arm in ARMS:
            for spec, choice in zip(self.plan["chains"], payloads[arm]["chains"]):
                expected = independent_physical_replay(spec["customer_demand"], choice["orders"], self.cfg.weeks)
                chain_id = spec["chain_id"]
                actual = tables["rounds"].query("arm == @arm and chain_id == @chain_id")
                for state in expected:
                    row = actual[(actual.week == state["week"]) & (actual.role == role_names[state["role"]])].iloc[0]
                    for field in ("inventory", "backlog", "received", "demand", "shipped", "supply_line", "cost"):
                        self.assertEqual(row[field], state[field], (arm, spec["chain_id"], state["week"], field))
                total = sum(s["cost"] for s in expected)
                totals[arm, spec["chain_id"]] = total
                chain_row = tables["chains"].query("arm == @arm and chain_id == @chain_id").iloc[0]
                self.assertEqual(chain_row.total_cost, total)
                self.assertEqual(chain_row.cost_practice + chain_row.cost_model + chain_row.cost_automatic, total)
        for contrast in contrasts.itertuples(index=False):
            if contrast.hypothesis in ("H2", "H4"):
                self.assertEqual(contrast.estimate, totals[contrast.treatment_arm, contrast.chain_id]
                                 - totals[contrast.reference_arm, contrast.chain_id])

    def test_full_500_identity_case_files_round_trip_and_replay(self):
        cfg = Config(students=500, repetitions=1, synthetic=True, label="full-scale-software-test")
        run = prepare(cfg, root=self.root)
        plan = read(run / "plan.json")
        self.assertEqual(len(plan["tasks"]), 3)
        for task in plan["tasks"]:
            payload = synthetic_response(run, task["task_id"])
            self.assertEqual(len(json.loads(payload)["chains"]), 125)
            source = self.root / (task["task_id"] + ".json")
            source.write_text(payload, encoding="utf-8")
            import_response(run, task["task_id"], source, model_label=cfg.model_label,
                            effort_label=cfg.effort_label, session_label="500-identity-software-test",
                            confirm_full_prompt=True, evidence_kind="synthetic_test")
        tables = summarize(run)
        self.assertEqual(len(tables["rounds"]), 3 * 500 * 36)
        self.assertEqual(len(tables["probes"]), 1500)
        self.assertEqual(tables["rounds"].participant_id.nunique(), 500)
        self.assertEqual(len(tables["chains"]), 375)
        self.assertEqual(len(tables["contrasts"]), 500)
        self.assertTrue((tables["contrasts"].estimate == 0).all())


if __name__ == "__main__":
    unittest.main()
