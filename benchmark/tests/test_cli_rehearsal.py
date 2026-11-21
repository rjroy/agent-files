"""Offline, black-box acceptance tests for the benchmark CLI.

Run from the repository root with ``python -m unittest discover -s benchmark/tests``.
The demo adapter is the only adapter exercised here.
"""

import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import time
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[2]
MODELS = ("demo/alpha", "demo/beta")


class BenchmarkCLIRehearsal(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="benchmark-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cases = self.root / "cases"
        self.output = self.root / "output"
        self.cases.mkdir()

    def cli(self, *args, stdin=""):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        return subprocess.run(
            [sys.executable, "-m", "benchmark", *map(str, args)],
            input=stdin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.root,
            env=env,
            timeout=30,
            check=False,
        )

    def assert_cli_available(self):
        result = self.cli("--help")
        self.assertEqual(
            result.returncode,
            0,
            "The benchmark CLI must exist and advertise its commands; "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}",
        )
        for command in ("run", "resume"):
            self.assertRegex(result.stdout, rf"\b{command}\b")

    def case(self, case_id, role, rubrics, passes):
        directory = self.cases / case_id
        directory.mkdir()
        fixture = directory / "fixture"
        fixture.mkdir()
        (fixture / "input.txt").write_text(
            "fixture-token\n" if passes else "other-token\n", encoding="utf-8"
        )
        manifest = {
            "version": 1,
            "id": case_id,
            "role": role,
            "turns": [f"Test-owned prompt for {case_id}."],
            "fixture": "fixture",
            "check": "check.py",
            "rubrics": rubrics,
        }
        (directory / "case.json").write_text(json.dumps(manifest), encoding="utf-8")
        # A fresh token in captured check output identifies each invocation
        # without requiring a sandboxed evaluator to write to the host.
        (directory / "check.py").write_text(
            "from pathlib import Path\n"
            "import sys, uuid\n"
            "print('check invocation:', uuid.uuid4(), flush=True)\n"
            "workspace = Path(sys.argv[1])\n"
            "assert Path.cwd() != workspace\n"
            "assert not (workspace / 'case.json').exists()\n"
            "assert not (workspace / 'check.py').exists()\n"
            "raise SystemExit(0 if (workspace / 'input.txt').read_text()"
            ".strip() == 'fixture-token' else 1)\n",
            encoding="utf-8",
        )

    def start_review(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        process = subprocess.Popen(
            [sys.executable, "-u", "-m", "benchmark", "run", "--demo",
             "--cases-dir", str(self.cases), "--output-dir", str(self.output)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=self.root, env=env,
        )
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        selector = selectors.DefaultSelector()
        self.addCleanup(selector.close)
        selector.register(process.stdout, selectors.EVENT_READ)
        prefix = b""
        deadline = time.monotonic() + 30
        while b"GRADING" not in prefix:
            remaining = deadline - time.monotonic()
            self.assertGreater(remaining, 0, "Timed out waiting for the first grading prompt")
            self.assertTrue(selector.select(remaining), "Timed out waiting for grading")
            chunk = os.read(process.stdout.fileno(), 4096)
            self.assertTrue(chunk, "CLI exited before the first grading prompt")
            prefix += chunk
        return process, prefix.decode("utf-8")

    def check_results(self):
        state = json.loads((self.output / "state.json").read_text(encoding="utf-8"))
        return {
            (case_id, model): (run["check"], run.get("check_detail", ""))
            for case_id, models in state["runs"].items()
            for model, run in models.items()
        }

    def assert_blind(self, text):
        for model in MODELS:
            self.assertNotIn(model, text, "Model identity leaked before grading finished")

    def test_commands_are_available_without_import_or_setup_failure(self):
        self.assert_cli_available()

    def test_two_models_complete_checks_before_review_and_resume_without_reruns(self):
        self.assert_cli_available()
        self.case(
            "a-conversation",
            "technical-brainstorm",
            [{"label": "originality", "prompt": "Judge originality.", "evidence": False}],
            True,
        )
        self.case(
            "b-conversation",
            "creative-brainstorm",
            [{"label": "usability", "prompt": "Judge usability.", "evidence": False}],
            False,
        )

        process, prefix = self.start_review()
        # Observe persisted checks while the first grading prompt is still
        # waiting for input, not merely after the review process exits.
        checks_before_review = self.check_results()
        self.assertEqual(len(checks_before_review), 4)
        tokens = []
        for (case_id, _), (outcome, detail) in checks_before_review.items():
            self.assertEqual(outcome, "pass" if case_id == "a-conversation" else "fail")
            self.assertIn("check invocation:", detail)
            tokens.append(detail.split("check invocation:", 1)[1].split()[0])
        self.assertEqual(len(set(tokens)), 4)
        for token in tokens:
            uuid.UUID(token)
        first_out, first_err = process.communicate(input=b"1\n", timeout=30)
        self.assert_blind(prefix + first_out.decode() + first_err.decode())
        self.assertFalse((self.output / "scorecard.md").exists())
        self.assertTrue((self.output / "state.json").is_file())

        # One grade was persisted; the remaining three finish the review.
        resumed = self.cli("resume", "--output-dir", self.output, stdin="2\n3\n4\n")
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(self.check_results(), checks_before_review,
                         "Resume must preserve the original check invocations")
        scorecard_path = self.output / "scorecard.md"
        self.assertTrue(scorecard_path.is_file(), resumed.stdout + resumed.stderr)
        scorecard = scorecard_path.read_text(encoding="utf-8")
        for model in MODELS:
            self.assertIn(model, scorecard)
            self.assertIn(model, resumed.stdout)
        for case_id in ("a-conversation", "b-conversation"):
            self.assertIn(case_id, scorecard)
        self.assertRegex(scorecard.lower(), r"\bpass(?:ed)?\b")
        self.assertRegex(scorecard.lower(), r"\bfail(?:ed)?\b")
        for grade in (1, 2, 3, 4):
            self.assertRegex(scorecard, rf"(?<!\d){grade}(?!\d)")

    def test_handoff_evidence_is_staged_after_message_grade(self):
        self.assert_cli_available()
        self.case(
            "handoff",
            "handoff",
            [
                {"label": "message", "prompt": "Judge the message alone.", "evidence": False},
                {"label": "claims", "prompt": "Verify claims against evidence.", "evidence": True},
            ],
            True,
        )
        first = self.cli("run", "--demo", "--cases-dir", self.cases,
                         "--output-dir", self.output)
        checks = self.check_results()
        self.assertEqual(len(checks), 2)
        self.assertTrue(all(outcome == "pass" for outcome, _ in checks.values()))
        self.assertIn("Judge the message alone.", first.stdout)
        self.assertNotIn("Verify claims against evidence.", first.stdout)
        self.assertNotIn("EVIDENCE", first.stdout)
        self.assert_blind(first.stdout + first.stderr)
        self.assertFalse((self.output / "scorecard.md").exists())

        resumed = self.cli("resume", "--output-dir", self.output, stdin="3\n")
        self.assertIn("EVIDENCE", resumed.stdout)
        self.assertIn("Verify claims against evidence.", resumed.stdout)
        self.assert_blind(resumed.stdout + resumed.stderr)
        self.assertFalse((self.output / "scorecard.md").exists())
        self.assertEqual(self.check_results(), checks)


if __name__ == "__main__":
    unittest.main()
