"""Operational file-save retry checks; never call a model or edit study sources."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, call, patch

from beergame_study import operational_io, reasoning_protocol, student_study


class OperationalIoTests(unittest.TestCase):
    def setUp(self):
        self.original_save = reasoning_protocol.save
        self.original_study_save = student_study.save
        scientific = Path(reasoning_protocol.__file__).parent
        self.sources = {scientific / (name + ".py"): (scientific / (name + ".py")).read_bytes()
                        for name in ("reasoning_protocol", "student_study", "student_report", "game", "estimation")}

    def tearDown(self):
        reasoning_protocol.save = self.original_save
        student_study.save = self.original_study_save
        for source, contents in self.sources.items():
            self.assertEqual(source.read_bytes(), contents)

    def test_transient_failure_and_idempotent_shared_install(self):
        original = Mock(side_effect=[PermissionError("locked"), PermissionError("locked"), "saved"])
        reasoning_protocol.save = original
        value = {"order": 4}
        with patch.object(operational_io.time, "sleep") as sleep:
            behavior = operational_io.install_windows_file_retry()
            wrapper = reasoning_protocol.save
            self.assertIs(wrapper, student_study.save)
            self.assertEqual(wrapper("target.json", value), "saved")
            operational_io.install_windows_file_retry()
            self.assertIs(reasoning_protocol.save, wrapper)
        self.assertEqual(original.call_args_list, [call("target.json", value)] * 3)
        self.assertIs(original.call_args.args[1], value)
        self.assertEqual(sleep.call_args_list, [call(0.02), call(0.05)])
        self.assertFalse(behavior["api_requests_retried"])

    def test_persistent_permission_error_is_bounded_and_propagated(self):
        error = PermissionError("persistent")
        original = Mock(side_effect=error)
        reasoning_protocol.save = original
        with patch.object(operational_io.time, "sleep") as sleep:
            operational_io.install_windows_file_retry()
            with self.assertRaises(PermissionError) as raised:
                reasoning_protocol.save("target.json", {"order": 0})
        self.assertIs(raised.exception, error)
        self.assertEqual(original.call_count, 7)
        self.assertEqual(sleep.call_args_list, [call(delay) for delay in operational_io.BACKOFF_SECONDS])
        self.assertAlmostEqual(sum(operational_io.BACKOFF_SECONDS), 1.57)

    def test_other_exceptions_are_not_retried(self):
        for error in (OSError("disk"), ValueError("json"), TypeError("type")):
            with self.subTest(error=type(error).__name__):
                original = Mock(side_effect=error)
                reasoning_protocol.save = original
                with patch.object(operational_io.time, "sleep") as sleep:
                    operational_io.install_windows_file_retry()
                    with self.assertRaises(type(error)) as raised:
                        reasoning_protocol.save("target.json", {"order": 1})
                self.assertIs(raised.exception, error)
                self.assertEqual(original.call_count, 1)
                sleep.assert_not_called()

    def test_real_save_bytes_preserved_without_any_api_call(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            baseline, retried = directory / "baseline.json", directory / "retried.json"
            value = {"text": "牛鞭效应", "order": 0, "nested": [True, 4.5]}
            self.original_save(baseline, value)
            unrelated = directory / "existing_raw.json"
            unrelated.write_bytes(b"existing raw provenance")
            replace = Path.replace
            attempts = []

            def transient_replace(path, target):
                if path == retried.with_suffix(".json.tmp"):
                    attempts.append(path)
                    if len(attempts) <= 2:
                        raise PermissionError("reader")
                return replace(path, target)

            with patch.object(Path, "replace", transient_replace), \
                    patch.object(operational_io.time, "sleep"), \
                    patch.object(student_study, "run_campaign", side_effect=AssertionError("API forbidden")) as campaign:
                operational_io.install_windows_file_retry()
                reasoning_protocol.save(retried, value)
                campaign.assert_not_called()
            self.assertEqual(retried.read_bytes(), baseline.read_bytes())
            self.assertEqual(unrelated.read_bytes(), b"existing raw provenance")
            self.assertEqual(len(attempts), 3)
            self.assertFalse(retried.with_suffix(".json.tmp").exists())

    def test_append_only_provenance_records_actual_resume_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            operational_io.install_windows_file_retry()
            first = operational_io.record_operational_io(temporary, {"concurrency": 2, "request_interval_s": 2})
            before = first.read_bytes()
            second = operational_io.record_operational_io(temporary, {"concurrency": 8, "request_interval_s": 1})
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_bytes(), before)
            self.assertEqual(len(list(first.parent.glob("*.json"))), 2)
            self.assertEqual(len(list(first.parent.glob("implementation_*.py"))), 1)
            original_source = Path(operational_io.__file__).read_bytes()
            for record_path, concurrency in ((first, 2), (second, 8)):
                record = json.loads(record_path.read_text(encoding="utf-8"))
                self.assertEqual(record["run_settings"]["concurrency"], concurrency)
                self.assertTrue(record["installed"])
                self.assertEqual(record["retry_behavior"]["maximum_file_save_attempts"], 7)
                self.assertAlmostEqual(record["retry_behavior"]["maximum_backoff_seconds"], 1.57)
                implementation = record_path.parent / record["implementation_copy"]
                self.assertEqual(implementation.read_bytes(), original_source)
                self.assertEqual(record["implementation_sha256"], hashlib.sha256(original_source).hexdigest())

    @unittest.skipUnless(os.name == "nt", "Windows file-sharing behavior")
    def test_windows_target_reader_lock_releases_and_save_succeeds(self):
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                      wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "active.json"
            self.original_save(target, {"old": True})
            # FILE_SHARE_READ | FILE_SHARE_WRITE permits writing but denies deletion/replacement.
            handle = kernel.CreateFileW(str(target), 0x80000000, 0x00000001 | 0x00000002,
                                        None, 3, 0x80, None)
            self.assertNotEqual(handle, ctypes.c_void_p(-1).value, ctypes.WinError(ctypes.get_last_error()))
            released = threading.Event()

            def release():
                kernel.CloseHandle(handle)
                released.set()

            timer = threading.Timer(0.10, release)
            timer.start()
            replace = Path.replace
            failures = []

            def observe_replace(path, destination):
                try:
                    return replace(path, destination)
                except PermissionError as error:
                    failures.append(error)
                    raise

            try:
                operational_io.install_windows_file_retry()
                with patch.object(Path, "replace", observe_replace):
                    reasoning_protocol.save(target, {"new": "unchanged bytes"})
                self.assertTrue(released.wait(1))
                self.assertGreaterEqual(len(failures), 1)
                self.assertTrue(all(error.winerror in (5, 32) for error in failures))
                self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"new": "unchanged bytes"})
                self.assertFalse(target.with_suffix(".json.tmp").exists())
            finally:
                timer.join()
                if not released.is_set():
                    kernel.CloseHandle(handle)


if __name__ == "__main__":
    unittest.main()
