"""Behavioral tests for independent evaluation and its execution boundary."""

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from benchmark import runner


class CheckBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="benchmark-boundary-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.cases = self.root / "cases"
        self.cases.mkdir()

    def make_case(self, case_id, check_source, fixture_files=None):
        directory = self.cases / case_id
        directory.mkdir()
        fixture = directory / "fixture"
        fixture.mkdir()
        for name, contents in (fixture_files or {}).items():
            (fixture / name).write_text(contents, encoding="utf-8")
        (directory / "check.py").write_text(check_source, encoding="utf-8")
        manifest = {
            "version": 1,
            "id": case_id,
            "role": "coding",
            "turns": ["Perform the synthetic task."],
            "fixture": "fixture",
            "check": "check.py",
            "rubrics": [],
        }
        (directory / "case.json").write_text(json.dumps(manifest), encoding="utf-8")
        return {**manifest, "_directory": str(directory)}

    @staticmethod
    def successful_adapter(model, turns, workspace, coding):
        return {"answers": ["Synthetic answer"], "evidence": "Synthetic trace"}

    def test_adapter_error_does_not_hide_independent_pass_or_failure(self):
        for expected, exit_code in (("pass", 0), ("fail", 1)):
            with self.subTest(expected=expected):
                case = self.make_case(
                    f"adapter-error-{expected}",
                    "from pathlib import Path\n"
                    "import sys\n"
                    "assert (Path(sys.argv[1]) / 'work.txt').read_text() == 'partial work'\n"
                    f"raise SystemExit({exit_code})\n",
                )

                def failing_adapter(model, turns, workspace, coding):
                    (workspace / "work.txt").write_text("partial work", encoding="utf-8")
                    raise RuntimeError("synthetic adapter failure")

                result = runner.run_one(case, "demo/alpha", failing_adapter)
                self.assertEqual(result["status"], "error")
                self.assertIn("synthetic adapter failure", result["error"])
                self.assertEqual(
                    result["check"], expected,
                    "A usable partial workspace still needs its independent check; "
                    "the agent error and check outcome are separate facts.",
                )

    def test_non_utf8_check_output_does_not_stop_the_campaign(self):
        self.make_case(
            "a-binary-output",
            "import os\n"
            "os.write(1, b'check output: \\xff\\xfe\\n')\n"
            "os.write(2, b'check diagnostic: \\x80\\n')\n",
        )
        self.make_case("b-later-case", "print('later check completed')\n")
        output = self.root / "results"
        args = argparse.Namespace(
            output_dir=output, cases_dir=self.cases, demo=True,
            config=None, allow_live=False,
        )

        runner.execute_run(args)

        state = json.loads((output / "state.json").read_text(encoding="utf-8"))
        for model in ("demo/alpha", "demo/beta"):
            binary = state["runs"]["a-binary-output"][model]
            later = state["runs"]["b-later-case"][model]
            self.assertEqual(binary["status"], "ok")
            self.assertEqual(binary["check"], "pass")
            self.assertIn("check output:", binary["check_detail"])
            self.assertEqual(later["status"], "ok")
            self.assertEqual(later["check"], "pass")
            self.assertIn("later check completed", later["check_detail"])
        self.assertTrue((output / "review.html").is_file())
        self.assertFalse((output / "scorecard.md").exists())

    def test_checker_cannot_consume_grader_stdin(self):
        case = self.make_case(
            "stdin-boundary",
            "import sys\n"
            "print('checker stdin:', repr(sys.stdin.read()))\n",
        )
        # A real pipe supplies input to the runner. The checker must see EOF,
        # leaving the same input available for the runner's grader.
        program = (
            "import json, sys\n"
            "from benchmark import runner\n"
            f"case = {case!r}\n"
            "result = runner.run_one(case, 'demo/alpha', runner.demo_run)\n"
            "print(json.dumps({'result': result, 'remaining': sys.stdin.read()}))\n"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(runner.__file__).resolve().parent.parent)
        process = subprocess.run(
            [sys.executable, "-c", program],
            input="synthetic-grader-input\n", text=True,
            capture_output=True, env=env, timeout=20, check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        observed = json.loads(process.stdout)
        self.assertEqual(observed["remaining"], "synthetic-grader-input\n")
        self.assertEqual(observed["result"]["check"], "pass")
        self.assertNotIn("synthetic-grader-input", observed["result"]["check_detail"])

    def test_resume_after_execution_interrupt_preserves_completed_work_without_reruns(self):
        self.make_case("interrupted", "print('check completed')\n")
        output = self.root / "results"
        args = argparse.Namespace(
            output_dir=output, cases_dir=self.cases, demo=True,
            config=None, allow_live=False,
        )
        original = runner.run_one
        calls = []

        def interrupt_after_first(*args):
            calls.append(args[1])
            if len(calls) == 2:
                raise KeyboardInterrupt
            return original(*args)

        with patch.object(runner, "run_one", side_effect=interrupt_after_first):
            with self.assertRaises(KeyboardInterrupt):
                runner.execute_run(args)
        before = json.loads((output / "state.json").read_text(encoding="utf-8"))
        completed_model = calls[0]
        completed = before["runs"]["interrupted"][completed_model]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(runner.__file__).resolve().parent.parent)
        resumed = subprocess.run(
            [sys.executable, "-m", "benchmark", "resume", "--output-dir", str(output)],
            input="", text=True, capture_output=True, env=env, timeout=30, check=False,
        )
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        after = json.loads((output / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(after["runs"]["interrupted"][completed_model], completed)
        self.assertEqual(after["runs"]["interrupted"][calls[1]]["status"], "error")
        self.assertTrue((output / "review.html").is_file())
        self.assertFalse((output / "scorecard.md").exists())

    def test_post_adapter_snapshot_error_does_not_skip_independent_check(self):
        case = self.make_case(
            "snapshot-error",
            "from pathlib import Path\n"
            "import sys\n"
            "assert (Path(sys.argv[1]) / 'work.txt').read_text() == 'completed work'\n"
            "print('independent check completed')\n",
        )

        def adapter(model, turns, workspace, coding):
            (workspace / "work.txt").write_text("completed work", encoding="utf-8")
            return self.successful_adapter(model, turns, workspace, coding)

        with patch.object(runner, "snapshot", side_effect=[{}, OSError("synthetic snapshot failure")]):
            result = runner.run_one(case, "demo/alpha", adapter)

        self.assertEqual(result["check"], "pass")
        self.assertIn("independent check completed", result.get("check_detail", ""))
        self.assertIn("synthetic snapshot failure", json.dumps(result))

    def test_deep_workspace_recursion_preserves_check_and_records_failures(self):
        self.make_case(
            "deep-workspace",
            "from pathlib import Path\n"
            "import sys\n"
            "assert (Path(sys.argv[1]) / 'work.txt').read_text() == 'completed work'\n"
            "print('deep workspace check completed')\n",
        )

        def adapter(model, turns, workspace, coding):
            (workspace / "work.txt").write_text("completed work", encoding="utf-8")
            return self.successful_adapter(model, turns, workspace, coding)

        temporary_directory = tempfile.TemporaryDirectory

        class CleanupRecursion(temporary_directory):
            def cleanup(self):
                # Remove the test directory first, then simulate the Python 3.11
                # recursive cleanup failure without leaving a deep tree behind.
                super().cleanup()
                raise RecursionError("synthetic deep cleanup failure")

        output = self.root / "results"
        args = argparse.Namespace(
            output_dir=output, cases_dir=self.cases, demo=True,
            config=None, allow_live=False,
        )
        with (
            patch.object(runner, "snapshot", side_effect=[
                {}, RecursionError("synthetic deep snapshot failure"),
                {}, RecursionError("synthetic deep snapshot failure"),
            ]),
            patch.object(runner.tempfile, "TemporaryDirectory", CleanupRecursion),
            patch.object(runner, "demo_run", adapter),
        ):
            runner.execute_run(args)

        state = json.loads((output / "state.json").read_text(encoding="utf-8"))
        for model in ("demo/alpha", "demo/beta"):
            result = state["runs"]["deep-workspace"][model]
            self.assertEqual(result["check"], "pass")
            self.assertIn("deep workspace check completed", result.get("check_detail", ""))
            recorded = json.dumps(result)
            self.assertIn("synthetic deep snapshot failure", recorded)
            self.assertIn("synthetic deep cleanup failure", recorded)

    def test_concurrent_resume_cannot_reveal_an_in_progress_run(self):
        self.make_case("contention", "print('check complete')\n")
        output = self.root / "results"
        args = argparse.Namespace(
            output_dir=output, cases_dir=self.cases, demo=True,
            config=None, allow_live=False,
        )
        entered = threading.Event()
        release = threading.Event()
        errors = []

        def waiting_adapter(model, turns, workspace, coding):
            entered.set()
            if not release.wait(15):
                raise RuntimeError("test did not release the adapter")
            return self.successful_adapter(model, turns, workspace, coding)

        def execute():
            try:
                runner.execute_run(args)
            except Exception as exc:
                errors.append(exc)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(runner.__file__).resolve().parent.parent)
        with patch.object(runner, "demo_run", waiting_adapter):
            worker = threading.Thread(target=execute, daemon=True)
            worker.start()
            try:
                self.assertTrue(entered.wait(10), "Execution did not reach the adapter")
                resume = subprocess.Popen(
                    [sys.executable, "-m", "benchmark", "resume", "--output-dir", str(output)],
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    env=env,
                )
                try:
                    try:
                        early_return = resume.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        early_return = None  # Waiting for the output lock is also valid.
                    self.assertFalse(
                        (output / "scorecard.md").exists(),
                        "A concurrent resume revealed an incomplete run",
                    )
                    if early_return is not None:
                        stdout, stderr = resume.communicate(timeout=5)
                        self.assertNotEqual(early_return, 0, (stdout, stderr))
                        self.assertNotIn(b"demo/alpha", stdout)
                        self.assertNotIn(b"demo/beta", stdout)
                finally:
                    release.set()
                    worker.join(timeout=15)
                    if resume.poll() is None:
                        try:
                            resume.communicate(timeout=10)
                        except subprocess.TimeoutExpired:
                            resume.kill()
                            resume.communicate()
                            self.fail("Concurrent resume did not finish after execution")
            finally:
                release.set()
                worker.join(timeout=15)
        self.assertFalse(worker.is_alive(), "Execution did not finish")
        self.assertEqual(errors, [])

    def test_coding_check_cannot_pass_when_fixture_exits_during_import(self):
        source = Path(runner.__file__).parent / "cases" / "coding" / "check.py"
        for name, fixture, expected in (
            ("normal", "def effective_enabled(settings, default):\n"
             "    return settings.get('enabled', default)\n", "pass"),
            ("early-exit", "raise SystemExit(0)\n", "not-pass"),
        ):
            with self.subTest(name=name):
                case = self.make_case(name, source.read_text(encoding="utf-8"),
                                      {"settings.py": fixture})
                result = runner.run_one(case, "demo/alpha", self.successful_adapter)
                if expected == "pass":
                    self.assertEqual(result["check"], "pass", result.get("check_detail"))
                else:
                    self.assertIn(
                        result["check"], ("fail", "error"),
                        "A clean process exit is not proof that assertions ran",
                    )

    def test_handoff_check_covers_string_ids_and_rejects_mutated_records(self):
        source = (Path(runner.__file__).parent / "cases" / "handoff" /
                  "check.py").read_text(encoding="utf-8")
        candidates = {
            "correct": (
                "def customer_report(customers, orders):\n"
                "    ids = {order['customer_id'] for order in orders}\n"
                "    return [customer for customer in customers if customer['id'] in ids]\n"
            ),
            "numeric-only": (
                "def customer_report(customers, orders):\n"
                "    ids = {order['customer_id'] for order in orders}\n"
                "    return [c for c in customers if isinstance(c['id'], int) and c['id'] in ids]\n"
            ),
            "mutates-input": (
                "def customer_report(customers, orders):\n"
                "    ids = {order['customer_id'] for order in orders}\n"
                "    for customer in customers:\n"
                "        customer['name'] = 'incorrectly changed'\n"
                "    return [customer for customer in customers if customer['id'] in ids]\n"
            ),
        }
        for name, candidate in candidates.items():
            with self.subTest(name=name):
                case = self.make_case(name, source, {"report.py": candidate})
                result = runner.run_one(case, "demo/alpha", self.successful_adapter)
                if name == "correct":
                    self.assertEqual(result["check"], "pass", result.get("check_detail"))
                else:
                    self.assertIn(
                        result["check"], ("fail", "error"),
                        f"Handoff check accepted {name}: {result.get('check_detail')}",
                    )

    def test_generated_fixture_runs_without_host_access_or_fails_closed(self):
        fake_home = self.root / "host-home"
        fake_home.mkdir()
        home_marker = fake_home / "private-marker"
        home_marker.write_text("synthetic private marker", encoding="utf-8")
        fake_checkout = self.root / "host-checkout"
        fake_checkout.mkdir()
        checkout_marker = fake_checkout / "unwanted-write"

        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(listener.close)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        # This synthetic generated file attempts only harmless operations
        # against test-owned paths and a test-owned loopback listener.
        generated = f"""
import json
import os
from pathlib import Path
import socket

observed = {{}}
observed['home_visible'] = Path({str(home_marker)!r}).exists()
observed['secret_visible'] = os.environ.get('BENCHMARK_TEST_SECRET') == 'synthetic-secret'
try:
    Path({str(checkout_marker)!r}).write_text('synthetic write', encoding='utf-8')
    observed['checkout_writable'] = True
except OSError:
    observed['checkout_writable'] = False
try:
    with socket.create_connection(('127.0.0.1', {port}), timeout=0.5):
        observed['network_available'] = True
except OSError:
    observed['network_available'] = False
print(json.dumps(observed))
"""
        check = """
import json
from pathlib import Path
import subprocess
import sys

result = subprocess.run(
    [sys.executable, str(Path(sys.argv[1]) / 'generated.py')],
    capture_output=True, text=True, check=True, timeout=5,
)
observed = json.loads(result.stdout)
print('boundary observations:', json.dumps(observed))
raise SystemExit(1 if any(observed.values()) else 0)
"""
        case = self.make_case("boundary", check, {"generated.py": generated})
        with patch.dict(os.environ, {
            "HOME": str(fake_home), "BENCHMARK_TEST_SECRET": "synthetic-secret",
        }):
            result = runner.run_one(case, "demo/alpha", self.successful_adapter)

        self.assertEqual(result["status"], "ok")
        self.assertFalse(checkout_marker.exists(), "Evaluation wrote outside the workspace")
        if result["check"] == "error":
            self.assertRegex(
                result.get("check_detail", "").lower(),
                r"sandbox|isolat",
                "If safe evaluation is unavailable, report an isolation error",
            )
        else:
            self.assertEqual(
                result["check"], "pass",
                "Untrusted generated code must not see host home, inherited secrets, "
                f"network, or writable checkout: {result.get('check_detail')}",
            )
            self.assertIn("boundary observations:", result.get("check_detail", ""))


if __name__ == "__main__":
    unittest.main()
