"""Offline tests of the OpenCode host adapter.

A fake CLI supplies the recorded OpenCode JSON protocol; no network access
or real inference is used. Run with ``python -B -m unittest discover -s
benchmark/tests -p test_opencode_adapter.py``.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODEL = "fixtureco/test-model"
OTHER_MODEL = "fixtureco/other-model"
VERSION = "fixture v9.9.9"
SESSION = "ses_fixture_first_turn"
TOOL = "edit"
TURNS = ("First fixture question?", "Follow-up: use the same session.")
ANSWERS = ("First fixture answer.", "Second fixture answer.")

FAKE_CLI = textwrap.dedent(f"""\
    import json
    import os
    import sys
    from pathlib import Path

    args = sys.argv[1:]
    with Path(os.environ["FAKE_CLI_LOG"]).open("a", encoding="utf-8") as log:
        print(json.dumps({{"argv": args, "cwd": os.getcwd()}}), file=log)

    if args[:1] == ["--version"]:
        print({VERSION!r})
    elif args[:1] == ["models"]:
        print({MODEL!r})
        print({OTHER_MODEL!r})
    elif args[:1] == ["run"]:
        answers = dict(zip({TURNS!r}, {ANSWERS!r}))
        turn = args[args.index("--") + 1]
        if turn not in answers:
            sys.exit("Unexpected turn: " + turn)
        events = [{{"type": "step_start", "sessionID": {SESSION!r},
                    "part": {{"type": "step-start"}}}}]
        if "--auto" in args:
            events.append({{"type": "tool_use", "sessionID": {SESSION!r},
                            "part": {{"tool": {TOOL!r}, "state": {{"status": "completed",
                                    "input": {{"path": "a.txt"}}, "output": "written"}}}}}})
        events += [
            {{"type": "text", "sessionID": {SESSION!r},
              "part": {{"type": "text", "text": answers[turn]}}}},
            {{"type": "step_finish", "sessionID": {SESSION!r},
              "part": {{"type": "step-finish", "reason": "stop"}}}},
        ]
        for event in events:
            print(json.dumps(event))
    else:
        sys.exit("Unexpected command: " + " ".join(args))
    """)


class HostAdapterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="benchmark-opencode-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.log = self.root / "invocations.jsonl"
        self.workspace = self.root / "case"
        self.workspace.mkdir()
        cli = self.root / "opencode-fixture"
        cli.write_text(f"#!{sys.executable}\n" + FAKE_CLI, encoding="utf-8")
        cli.chmod(0o700)
        self.env = {**os.environ,
                    "PYTHONPATH": str(ROOT),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "BENCHMARK_OPENCODE_BIN": str(cli),
                    "FAKE_CLI_LOG": str(self.log)}

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", *args], env=self.env,
                              cwd=str(self.root), input="", capture_output=True,
                              text=True, timeout=60, check=False)

    def doctor(self, *args):
        return self.cli("-m", "benchmark", "doctor", "--model", MODEL, "--json", *args)

    def run_case(self, coding):
        code = textwrap.dedent(f"""\
            import json
            from pathlib import Path
            from benchmark import opencode_adapter

            print(json.dumps(opencode_adapter.run_case(
                {MODEL!r}, list({TURNS!r}), Path({str(self.workspace)!r}), coding={coding!r})))
            """)
        return self.cli("-c", code)

    def invocations(self):
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def test_doctor_reports_installed_cli_and_model_availability(self):
        result = self.doctor()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertIs(report["ok"], True)
        self.assertEqual(report["model"], MODEL)
        self.assertEqual(report["version"], VERSION)
        self.assertEqual(report["profile"], "talking")
        self.assertEqual(Path(report["binary"]), Path(self.env["BENCHMARK_OPENCODE_BIN"]))

    def test_doctor_rejects_unavailable_model_profile_and_id(self):
        missing = self.cli("-m", "benchmark", "doctor", "--model",
                          "fixtureco/not-installed", "--json")
        self.assertNotEqual(missing.returncode, 0, missing.stdout + missing.stderr)
        profile = self.doctor("--profile", "bogus")
        self.assertNotEqual(profile.returncode, 0, profile.stdout + profile.stderr)
        malformed = self.cli("-m", "benchmark", "doctor", "--model", "no-slash", "--json")
        self.assertNotEqual(malformed.returncode, 0, malformed.stdout + malformed.stderr)

    def test_case_answers_turns_and_continues_one_session(self):
        result = self.run_case(coding=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["answers"], list(ANSWERS))
        self.assertIsInstance(report["evidence"], str)
        first, second = (record["argv"] for record in self.invocations())
        self.assertEqual(len(self.invocations()), 2)
        self.assertIn("--model", first)
        self.assertIn(MODEL, first)
        self.assertIn("--archived", first, "Benchmark sessions stay out of session lists")
        self.assertIn(TURNS[0], first)
        self.assertNotIn(TURNS[1], first, "Future turns must not reach the first prompt")
        self.assertIn("--session", second)
        self.assertIn(SESSION, second, "Follow-up must continue the original session")
        self.assertNotIn("--archived", second)
        self.assertIn(TURNS[1], second)
        self.assertNotIn("--auto", first, "Talking runs do not auto-approve permissions")
        self.assertEqual([Path(record["cwd"]).resolve() for record in self.invocations()],
                         [self.workspace] * 2)

    def test_coding_case_auto_approves_and_records_tool_events(self):
        result = self.run_case(coding=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["answers"], list(ANSWERS))
        self.assertIn(TOOL, report["evidence"], "Tool events must appear as evidence")
        for record in self.invocations():
            self.assertIn("--auto", record["argv"],
                          "Coding runs auto-approve workspace permissions")

    def test_case_rejects_empty_turns_without_invoking_the_cli(self):
        code = textwrap.dedent(f"""\
            from pathlib import Path
            from benchmark import opencode_adapter

            opencode_adapter.run_case({MODEL!r}, [], Path({str(self.workspace)!r}), coding=False)
            """)
        result = self.cli("-c", code)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("nonempty prompt turns", result.stderr)
        self.assertFalse(self.log.exists(), "Validation must reject before any CLI call")

    def test_case_reports_turn_errors_and_missing_answers(self):
        code = textwrap.dedent(f"""\
            import json
            from benchmark import opencode_adapter

            try:
                opencode_adapter._read_turn(json.dumps(
                    {{"type": "error", "sessionID": {SESSION!r}, "part": {{}}}}), None)
            except RuntimeError as error:
                print(error)
            try:
                opencode_adapter._read_turn(json.dumps(
                    {{"type": "text", "sessionID": {SESSION!r},
                      "part": {{"text": "no finish"}}}}), None)
            except RuntimeError as error:
                print(error)
            """)
        result = self.cli("-c", code)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("turn error", result.stdout)
        self.assertIn("no completed user-facing answer", result.stdout)


if __name__ == "__main__":
    unittest.main()
