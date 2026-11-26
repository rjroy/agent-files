"""Offline, black-box acceptance tests for the benchmark CLI.

Run from the repository root with ``python -m unittest discover -s benchmark/tests``.
The demo adapter is the only adapter exercised here.
"""

import json
from html.parser import HTMLParser
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from benchmark import local_grader, runner


ROOT = Path(__file__).resolve().parents[2]
MODELS = ("demo/alpha", "demo/beta")


class ReviewDataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_data = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("id") == "review-data":
            if attrs.get("type") != "application/json":
                raise AssertionError("review-data must be application/json")
            self.in_data = True

    def handle_data(self, data):
        if self.in_data:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_data = False


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
        for command in ("run", "resume", "import-grades"):
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

    def review_data(self):
        html = (self.output / "review.html").read_text(encoding="utf-8")
        parser = ReviewDataParser()
        parser.feed(html)
        self.assertTrue(parser.parts, "Missing review-data JSON script")
        data = json.loads("".join(parser.parts))
        self.assertIsInstance(data["review_id"], str)
        self.assertTrue(data["review_id"])
        ids = [rubric["id"] for case in data["cases"]
               for response in case["responses"] for rubric in response["rubrics"]]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(isinstance(value, str) and value for value in ids))
        return html, data, ids

    def import_grades(self, payload):
        path = self.root / "grades.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return self.cli("import-grades", path, "--output-dir", self.output)

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

    def test_run_resume_and_import_complete_blind_review_without_reruns(self):
        self.case("a-conversation", "technical-brainstorm", [
            {"label": "originality", "prompt": "Judge originality.", "evidence": False}], True)
        self.case("b-conversation", "creative-brainstorm", [
            {"label": "usability", "prompt": "Judge usability.", "evidence": False}], False)
        first = self.cli("run", "--demo", "--cases-dir", self.cases,
                         "--output-dir", self.output)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assert_blind(first.stdout + first.stderr)
        self.assertFalse((self.output / "scorecard.md").exists())
        html, data, ids = self.review_data()
        self.assert_blind(html)
        self.assertEqual(len(ids), 4)
        checks = self.check_results()
        self.assertEqual(len(checks), 4)
        for (case_id, _), (outcome, detail) in checks.items():
            self.assertEqual(outcome, "pass" if case_id == "a-conversation" else "fail")
            self.assertIn("check invocation:", detail)

        resumed = self.cli("resume", "--output-dir", self.output)
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assert_blind(resumed.stdout + resumed.stderr)
        self.assertFalse((self.output / "scorecard.md").exists())
        self.assertEqual(self.check_results(), checks)
        _, resumed_data, resumed_ids = self.review_data()
        self.assertEqual(resumed_data["review_id"], data["review_id"])
        self.assertEqual(set(resumed_ids), set(ids))

        payload = {"version": 1, "review_id": data["review_id"],
                   "grades": dict(zip(ids, (1, 2, 3, 4)))}
        imported = self.import_grades(payload)
        self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
        scorecard_path = self.output / "scorecard.md"
        scorecard = scorecard_path.read_text(encoding="utf-8")
        for model in MODELS:
            self.assertIn(model, scorecard)
        for case_id in ("a-conversation", "b-conversation"):
            self.assertIn(case_id, scorecard)
        self.assertRegex(scorecard.lower(), r"\bpass(?:ed)?\b")
        self.assertRegex(scorecard.lower(), r"\bfail(?:ed)?\b")
        for grade in (1, 2, 3, 4):
            self.assertRegex(scorecard, rf"(?<!\d){grade}(?!\d)")
        self.assertEqual(self.check_results(), checks)

        repeated = self.import_grades(payload)
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertEqual(scorecard_path.read_text(encoding="utf-8"), scorecard)
        state_before_change = (self.output / "state.json").read_bytes()
        changed = {**payload, "grades": {**payload["grades"], ids[0]: 5}}
        rejected = self.import_grades(changed)
        self.assertNotEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
        self.assertEqual((self.output / "state.json").read_bytes(), state_before_change)
        self.assertEqual(scorecard_path.read_text(encoding="utf-8"), scorecard)

    def test_invalid_imports_do_not_reveal_or_change_state(self):
        self.case("handoff", "handoff", [
            {"label": "message", "prompt": "Judge the message alone.", "evidence": False},
            {"label": "claims", "prompt": "Verify claims against evidence.", "evidence": True},
        ], True)
        self.case("coding", "coding", [], True)
        run = self.cli("run", "--demo", "--cases-dir", self.cases,
                       "--output-dir", self.output)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        html, data, ids = self.review_data()
        self.assert_blind(html)
        self.assertIn("Judge the message alone.", html)
        self.assertIn("Verify claims against evidence.", html)
        self.assertEqual(len(ids), 4)
        cases_by_role = {case["role"]: case for case in data["cases"]}
        self.assertIs(cases_by_role["coding"]["deterministic_only"], True)
        self.assertIs(cases_by_role["handoff"]["deterministic_only"], False)
        valid = {key: 3 for key in ids}
        invalid = [
            {"version": 2, "review_id": data["review_id"], "grades": valid},
            {"version": 1, "review_id": "different-review", "grades": valid},
            {"version": 1, "review_id": data["review_id"], "grades": {ids[0]: 3}},
            {"version": 1, "review_id": data["review_id"], "grades": {**valid, "unknown": 3}},
            *[{"version": 1, "review_id": data["review_id"],
               "grades": {**valid, ids[0]: bad}} for bad in (0, 6, 2.5, True, "3", None)],
        ]
        before = (self.output / "state.json").read_bytes()
        for payload in invalid:
            with self.subTest(payload=payload):
                result = self.import_grades(payload)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse((self.output / "scorecard.md").exists())
                self.assertEqual((self.output / "state.json").read_bytes(), before)
                self.assert_blind(result.stdout + result.stderr)

    def test_import_refreshes_existing_machine_agreement_without_new_model_calls(self):
        self.case("agreement", "technical-brainstorm", [
            {"label": "quality", "prompt": "Judge quality.", "evidence": False}], True)
        run = self.cli("run", "--demo", "--cases-dir", self.cases,
                       "--output-dir", self.output)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        _, data, ids = self.review_data()
        self.assertEqual(len(ids), 2)
        self.assertFalse((self.output / "scorecard.md").exists())

        # Probe plus two ordered comparisons; the fake records every model call.
        calls = self.root / "ollama-calls"
        binary = self.root / "fake-ollama"
        binary.write_text(
            f"#!{sys.executable}\n"
            "import json, sys\n"
            "from pathlib import Path\n"
            f"calls = Path({str(calls)!r})\n"
            "if sys.argv[1:] == ['list']:\n"
            "    print('NAME ID\\nd3:latest fake')\n"
            "elif sys.argv[1:] == ['--version']:\n"
            "    print('ollama version is test')\n"
            "elif sys.argv[1] == 'run':\n"
            "    previous = calls.read_text().splitlines() if calls.exists() else []\n"
            "    with calls.open('a') as log:\n"
            "        log.write('run\\n')\n"
            "    choice = 'B' if len(previous) == 2 else 'A'\n"
            "    print(json.dumps({'answers': {'q1': {'type': 'choice', 'choice': choice}}}))\n"
            "else:\n"
            "    raise SystemExit(1)\n",
            encoding="utf-8",
        )
        binary.chmod(0o755)
        auto = self.cli("autograde", "--output-dir", self.output, "--ollama-bin", binary)
        self.assertEqual(auto.returncode, 0, auto.stdout + auto.stderr)
        calls_before = calls.read_text(encoding="utf-8")
        self.assertEqual(calls_before.splitlines(), ["run", "run", "run"])
        state_before = json.loads((self.output / "state.json").read_text(encoding="utf-8"))
        machine_before = state_before["auto_grades"]
        self.assertEqual(state_before["grades"], {})
        self.assertEqual(machine_before["agreement"]["cases"]["agreement"]["n"], 0)
        self.assertIsNone(machine_before["agreement"]["cases"]["agreement"]["rho"])
        report_path = self.output / "auto_scorecard.md"
        report_before = report_path.read_text(encoding="utf-8")
        self.assertNotIn("Spearman vs human mean", report_before)
        self.assertNotIn("Human mean", report_before)
        self.assertFalse((self.output / "scorecard.md").exists())

        report_path.unlink()
        resumed = self.cli("resume", "--output-dir", self.output)
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertTrue(report_path.is_file(), "Resume must rebuild the machine report")
        self.assertEqual(report_path.read_text(encoding="utf-8"), report_before)
        self.assertEqual(calls.read_text(encoding="utf-8"), calls_before)
        resumed_state = json.loads((self.output / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(resumed_state["grades"], {})
        self.assertEqual(resumed_state["auto_grades"]["comparisons"],
                         machine_before["comparisons"])
        self.assertFalse((self.output / "scorecard.md").exists())

        imported = self.import_grades({"version": 1, "review_id": data["review_id"],
                                       "grades": {ids[0]: 1, ids[1]: 5}})
        self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
        state_after = json.loads((self.output / "state.json").read_text(encoding="utf-8"))
        machine_after = state_after["auto_grades"]
        self.assertEqual(calls.read_text(encoding="utf-8"), calls_before)
        self.assertEqual(machine_after["comparisons"], machine_before["comparisons"])
        self.assertEqual(machine_after["standings"], machine_before["standings"])
        agreement = machine_after["agreement"]["cases"]["agreement"]
        self.assertEqual(agreement["n"], 2)
        self.assertAlmostEqual(abs(agreement["rho"]), 1.0)
        report_after = report_path.read_text(encoding="utf-8")
        self.assertNotEqual(report_after, report_before)
        self.assertIn("Human mean", report_after)
        self.assertIn("Spearman vs human mean", report_after)
        self.assertTrue((self.output / "scorecard.md").is_file())

    def prepare_machine_review_for_fault(self):
        self.case("fault", "technical-brainstorm", [
            {"label": "quality", "prompt": "Judge quality.", "evidence": False}], True)
        run = self.cli("run", "--demo", "--cases-dir", self.cases,
                       "--output-dir", self.output)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        _, data, ids = self.review_data()
        self.assertEqual(len(ids), 2)
        state = json.loads((self.output / "state.json").read_text(encoding="utf-8"))
        calls = []

        def decide(question, text, choices):
            calls.append((question, text))
            return {"choice": "A" if len(calls) == 1 else "B",
                    "probabilities": {}, "confidence": None}

        local_grader.autograde(self.output, state, model="fake", decide=decide)
        self.assertEqual(len(calls), 2)
        grades = self.root / "fault-grades.json"
        grades.write_text(json.dumps({"version": 1, "review_id": data["review_id"],
                                      "grades": {ids[0]: 1, ids[1]: 5}}),
                          encoding="utf-8")
        return grades, calls

    def test_import_save_failure_leaves_persisted_state_and_reports_unchanged(self):
        grades, calls = self.prepare_machine_review_for_fault()
        state_path = self.output / "state.json"
        machine_path = self.output / "auto_scorecard.md"
        human_path = self.output / "scorecard.md"
        before_state = state_path.read_bytes()
        before_machine = machine_path.read_bytes()
        self.assertFalse(human_path.exists())

        with patch.object(runner, "save_state", side_effect=OSError("synthetic save failure")):
            with self.assertRaisesRegex(OSError, "synthetic save failure"):
                runner.import_grades(self.output, grades)

        self.assertEqual(state_path.read_bytes(), before_state)
        self.assertEqual(machine_path.read_bytes(), before_machine)
        self.assertFalse(human_path.exists())
        self.assertEqual(len(calls), 2)

    def test_resume_rebuilds_reports_after_import_report_write_failure(self):
        grades, calls = self.prepare_machine_review_for_fault()
        machine_path = self.output / "auto_scorecard.md"
        human_path = self.output / "scorecard.md"
        old_machine = machine_path.read_bytes()
        original_runner_write = runner.atomic_write
        original_grader_write = local_grader.atomic_write

        def fail_report(write):
            def wrapped(path, content):
                if path.name in ("auto_scorecard.md", "scorecard.md"):
                    raise OSError("synthetic report failure")
                return write(path, content)
            return wrapped

        with (patch.object(runner, "atomic_write", side_effect=fail_report(original_runner_write)),
              patch.object(local_grader, "atomic_write",
                           side_effect=fail_report(original_grader_write))):
            with self.assertRaisesRegex(OSError, "synthetic report failure"):
                runner.import_grades(self.output, grades)

        saved = json.loads((self.output / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["phase"], "complete")
        self.assertEqual(sorted(saved["grades"].values()), [1, 5])
        comparisons = saved["auto_grades"]["comparisons"]
        self.assertEqual(machine_path.read_bytes(), old_machine)
        self.assertFalse(human_path.exists())
        with patch.object(local_grader, "OllamaDecision",
                          side_effect=AssertionError("unexpected inference")):
            runner.review(self.output, saved)
        repaired = json.loads((self.output / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(repaired["auto_grades"]["comparisons"], comparisons)
        self.assertEqual(len(calls), 2)
        self.assertIn("Spearman vs human mean", machine_path.read_text(encoding="utf-8"))
        self.assertIn("Human mean", machine_path.read_text(encoding="utf-8"))
        self.assertIn("# Benchmark scorecard", human_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
