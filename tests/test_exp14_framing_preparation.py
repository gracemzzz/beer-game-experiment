"""Synthetic preparation/gate binding tests; all writes stay in temporary folders."""
import copy
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import prepare_exp14_framing as prep
import qualify_exp14_framing as qualify


class FramingPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.exp = self.root / "experiment"
        self.plan_path = self.exp / "hypotheses/STUDENT_FRAMING_V3_PLAN.json"
        self.main_path = self.exp / "hypotheses/STUDENT_FRAMING_V3_MAIN_PLAN.json"
        files = ["src/beergame_study/exp14_framing.py", "scripts/run_exp14_framing.py",
                 "src/beergame_study/manual_weekly_v3.py", "scripts/audit_exp14_agent.py",
                 "scripts/audit_agent_public_trace_v5.py", "materials/protocol.md", "analysis/report.py"]
        self.hashes = {}
        for name in files:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = ("SYNTHETIC SOFTWARE FIXTURE: " + name + "\n").encode()
            path.write_bytes(raw)
            self.hashes[name] = hashlib.sha256(raw).hexdigest()
        self.sources = dict(controller=self.hashes[files[0]], transport=self.hashes[files[1]],
                            physics=self.hashes[files[2]])
        self.materials = {"materials/protocol.md": self.hashes["materials/protocol.md"]}
        self.analysis = {"analysis/report.py": self.hashes["analysis/report.py"]}
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(mock.patch.multiple(prep, ROOT=self.root, EXP=self.exp,
                                                PLAN=self.plan_path, MAIN_PLAN=self.main_path))
        stack.enter_context(mock.patch.object(prep, "source_hashes", return_value=self.sources))
        stack.enter_context(mock.patch.object(prep, "materials", return_value=self.materials))
        self.analysis_mock = stack.enter_context(mock.patch.object(prep, "analysis_sources", return_value=self.analysis))
        stack.enter_context(mock.patch.multiple(qualify, ROOT=self.root, EXP=self.exp, MAIN_PLAN=self.main_path))
        stack.enter_context(mock.patch.object(qualify, "PLAN", self.plan_path, create=True))
        stack.enter_context(mock.patch.object(qualify, "source_hashes", return_value=self.sources))
        stack.enter_context(mock.patch.object(qualify, "materials", return_value=self.materials))
        stack.enter_context(mock.patch.object(qualify, "analysis_sources", return_value=self.analysis))
        self.value = prep.plan(freeze_new=True)
        self.snapshot = self.exp / "data/student_framing_v3/protocols" / prep.digest(self.value)[:20]

    def assignment(self, arm="A"):
        stage = "development"
        block = self.value[stage]["block_id"]
        seed = self.value[stage]["seed"]
        return dict(schema_version=prep.SCHEMA,
                    case_id="E14SF3_" + prep.digest([stage, block, arm, seed])[:20],
                    arm=arm, stage=stage, block_id=block, seed=seed, weeks=24,
                    prompt_version=self.value["prompt_version"],
                    fictional_student_seconds=self.value["fictional_student_seconds"][arm],
                    model_runtime_limit_seconds=None, deadline_seconds=None,
                    phase_deadline_seconds={"game": None, "probes": None},
                    requested_model="gpt-6-astra", requested_effort="xhigh",
                    plan_sha256=prep.sha(self.plan_path), source_hashes=copy.deepcopy(self.sources),
                    material_hashes=copy.deepcopy(self.materials))

    def test_complete_frozen_snapshot_reopens_with_identical_plan(self):
        self.assertEqual(prep.plan(), self.value)
        self.assertEqual((self.snapshot / "PLAN.json").read_bytes(), self.plan_path.read_bytes())
        manifest = json.loads((self.snapshot / "SOURCE_HASHES.json").read_text(encoding="utf-8"))
        for name, expected in manifest.items():
            self.assertEqual(prep.sha(self.snapshot / name), expected)

    def test_changed_analysis_source_cannot_reopen_frozen_plan(self):
        changed = dict(self.analysis)
        changed["analysis/report.py"] = "0" * 64
        self.analysis_mock.return_value = changed
        with self.assertRaises(ValueError):
            prep.plan()

    def test_missing_snapshot_file_cannot_reopen_frozen_plan(self):
        (self.snapshot / "materials/protocol.md").unlink()
        with self.assertRaises((ValueError, FileNotFoundError)):
            prep.plan()

    def test_tampered_snapshot_bytes_and_plan_copy_are_rejected(self):
        snapshot_source = self.snapshot / "analysis/report.py"
        original = snapshot_source.read_bytes()
        snapshot_source.write_bytes(b"changed synthetic snapshot")
        with self.assertRaises(ValueError):
            prep.plan()
        snapshot_source.write_bytes(original)
        (self.snapshot / "PLAN.json").write_bytes(b"{}\n")
        with self.assertRaises(ValueError):
            prep.plan()

    def test_interrupted_snapshot_write_never_publishes_plan(self):
        self.plan_path.unlink()
        original_freeze = prep.freeze
        def fail_manifest(path, data):
            if path.name == "SOURCE_HASHES.json":
                raise OSError("Synthetic interrupted snapshot write")
            return original_freeze(path, data)
        with mock.patch.object(prep, "freeze", side_effect=fail_manifest):
            with self.assertRaisesRegex(OSError, "Synthetic interrupted"):
                prep.plan(freeze_new=True)
        self.assertFalse(self.plan_path.exists())

    def test_correct_development_assignments_accepted_for_all_arms(self):
        for arm in "ABC":
            qualify.verify_assignment(self.assignment(arm), arm, self.value)

    def test_swapped_development_arm_and_wrong_plan_hash_rejected(self):
        with self.assertRaises(ValueError):
            qualify.verify_assignment(self.assignment("A"), "B", self.value)
        wrong = self.assignment()
        wrong["plan_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            qualify.verify_assignment(wrong, "A", self.value)

    def test_assignment_seed_stage_material_source_and_framing_drift_rejected(self):
        changes = (("stage", "main"), ("block_id", "unregistered"), ("seed", 999),
                   ("prompt_version", "changed"), ("material_hashes", {}), ("source_hashes", {}),
                   ("fictional_student_seconds", 8), ("model_runtime_limit_seconds", 8))
        for key, value in changes:
            with self.subTest(key=key):
                wrong = self.assignment()
                wrong[key] = value
                with self.assertRaises(ValueError):
                    qualify.verify_assignment(wrong, "A", self.value)

    def test_unregistered_main_block_refused_before_case_or_transport(self):
        main = dict(frozen=True, qualification_passed=True,
                    block_ids=self.value["main"]["block_ids"],
                    source_hashes=self.sources, material_hashes=self.materials,
                    analysis_hashes=self.analysis)
        prep.freeze(self.main_path, main)
        with mock.patch.object(prep.subprocess, "run") as run:
            with self.assertRaisesRegex(ValueError, "Main block/qualification mismatch"):
                prep.prepare("main", "A", "c3m999")
            run.assert_not_called()
        self.assertFalse((self.exp / "data/student_framing_v3/main").exists())


if __name__ == "__main__":
    unittest.main()
