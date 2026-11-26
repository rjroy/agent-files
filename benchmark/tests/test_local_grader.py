"""Offline tests for the opt-in local decision-model second opinion."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from benchmark import local_grader as grader


MODELS = ["a/m1", "b/m2", "c/m3"]
CASE = {
    "id": "case1",
    "role": "talk",
    "turns": ["Question one?"],
    "rubrics": [{"label": "message", "prompt": "Rate the message.", "evidence": False}],
}
EVIDENCE_CASE = {
    "id": "case1",
    "role": "handoff",
    "turns": ["Question one?"],
    "rubrics": [{"label": "evidence", "prompt": "Rate the evidence.", "evidence": True}],
}


def make_state(case=CASE):
    return {
        "version": 1,
        "demo": False,
        "models": list(MODELS),
        "cases": [case],
        "runs": {case["id"]: {
            model: {"status": "ok", "answers": [f"answer from {model}"],
                    "evidence": f"evidence from {model}", "check": "not configured"}
            for model in MODELS}},
        "review": [],
        "grades": {},
        "phase": "complete",
    }


class FakeDecide:
    def __init__(self, choices):
        self.choices = list(choices)
        self.calls = []

    def __call__(self, question, text, choices):
        self.calls.append((question, text, choices))
        return {"choice": self.choices.pop(0), "probabilities": {}, "confidence": 0.9}


class LocalGraderTests(unittest.TestCase):
    def test_extract_json_ignores_ansi_and_spinner(self):
        raw = ('\x1b[?25l noise\n'
               '{"model":"d3","answers":{"q1":{"type":"choice","choice":"B",'
               '"probabilities":{"A":0.1,"B":0.9},"confidence":0.8}}}\n⠙')
        self.assertEqual(grader._extract_json(raw)["answers"]["q1"]["choice"], "B")

    def test_extract_json_rejects_missing_object(self):
        with self.assertRaises(grader.GraderError):
            grader._extract_json("not json")

    def test_resolve_model_accepts_untagged_name(self):
        self.assertEqual(grader._resolve_model("d3", ["d3:latest", "other:9b"]),
                         "d3:latest")

    def test_resolve_model_refuses_missing(self):
        with self.assertRaises(grader.GraderError) as caught:
            grader._resolve_model("missing", ["d3:latest"])
        self.assertIn("refusing to pull", str(caught.exception))

    def test_pair_text_blinds_identity_and_omits_evidence_by_default(self):
        state = make_state()
        run = state["runs"]["case1"]["a/m1"]
        run["answers"] = ["answer from a/m1"]
        text, truncated = grader.pair_text(
            CASE, run, state["runs"]["case1"]["b/m2"], CASE["rubrics"][0], MODELS)
        self.assertFalse(truncated)
        self.assertNotIn("a/m1", text)
        self.assertIn("[model identity hidden]", text)
        self.assertNotIn("EVIDENCE", text)

    def test_pair_text_includes_evidence_for_evidence_rubric(self):
        state = make_state(EVIDENCE_CASE)
        text, _ = grader.pair_text(
            EVIDENCE_CASE, state["runs"]["case1"]["a/m1"],
            state["runs"]["case1"]["b/m2"], EVIDENCE_CASE["rubrics"][0], MODELS)
        self.assertIn("EVIDENCE", text)

    def test_pair_text_truncates_with_marker(self):
        state = make_state()
        for run in state["runs"]["case1"].values():
            run["answers"] = ["word " * 400]
        text, truncated = grader.pair_text(
            CASE, state["runs"]["case1"]["a/m1"], state["runs"]["case1"]["b/m2"],
            CASE["rubrics"][0], MODELS, max_chars=600)
        self.assertTrue(truncated)
        self.assertIn("truncated", text.lower())

    def test_spearman(self):
        self.assertAlmostEqual(grader._spearman([1, 2, 3], [10, 20, 30]), 1.0)
        self.assertAlmostEqual(grader._spearman([1, 2, 3], [30, 20, 10]), -1.0)
        self.assertIsNone(grader._spearman([1, 1, 1], [1, 2, 3]))

    def test_autograde_requires_completed_review(self):
        state = make_state()
        state["phase"] = "review"
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(grader.GraderError):
                grader.autograde(Path(temp), state, model="d3", decide=FakeDecide([]))

    def test_autograde_records_ranking_and_preserves_human_grades(self):
        state = make_state()
        state["grades"] = {
            json.dumps(["case1", "a/m1", 0]): 5,
            json.dumps(["case1", "b/m2", 0]): 1,
            json.dumps(["case1", "c/m3", 0]): 3,
        }
        decide = FakeDecide([
            "A", "B",   # m1 beats m2 in both orders
            "A", "A",   # m1 vs m3: both orders pick first position -> tie
            "B", "A",   # m3 beats m2 in both orders
        ])
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            record, report = grader.autograde(
                output, state, model="d3", decide=decide, max_chars=12000)
            saved = json.loads((output / "state.json").read_text(encoding="utf-8"))
            self.assertTrue((output / "auto_scorecard.md").is_file())

        stats = record["standings"]["case1"]
        self.assertEqual((stats["a/m1"]["wins"], stats["a/m1"]["losses"],
                          stats["a/m1"]["ties"]), (1, 0, 1))
        self.assertEqual((stats["c/m3"]["wins"], stats["c/m3"]["losses"],
                          stats["c/m3"]["ties"]), (1, 0, 1))
        self.assertEqual((stats["b/m2"]["wins"], stats["b/m2"]["losses"]), (0, 2))
        self.assertEqual(stats["a/m1"]["rank"], 1)
        self.assertEqual(stats["c/m3"]["rank"], 2)
        self.assertEqual(stats["b/m2"]["rank"], 3)
        outcomes = [entry["outcome"] for entry in record["comparisons"]]
        self.assertEqual(outcomes, ["a", "tie", "b"])
        self.assertEqual(saved["grades"], state["grades"])
        self.assertIn("Local second opinion", report)
        self.assertIn("Spearman vs human mean", report)

    def test_autograde_skips_cases_without_rubrics(self):
        case = {"id": "case1", "role": "coding", "turns": ["Fix it."], "rubrics": []}
        decide = mock.Mock(side_effect=AssertionError("must not compare"))
        with tempfile.TemporaryDirectory() as temp:
            record, report = grader.autograde(
                Path(temp), make_state(case), model="d3", decide=decide)
        decide.assert_not_called()
        self.assertEqual(record["standings"]["case1"], {})
        self.assertIn("Deterministic-only case", report)

    def test_autograde_shrinks_budget_after_context_error(self):
        class FlakyDecide:
            def __init__(self):
                self.calls = 0

            def __call__(self, question, text, choices):
                self.calls += 1
                if self.calls == 1:
                    raise grader.ContextLengthError("too long")
                return {"choice": "A", "probabilities": {}, "confidence": 0.9}

        decide = FlakyDecide()
        with tempfile.TemporaryDirectory() as temp:
            record, _ = grader.autograde(
                Path(temp), make_state(), model="d3", decide=decide, max_chars=9000)
        self.assertEqual(record["limits"]["budget_by_case"]["case1"], 4500)
        self.assertEqual(record["comparisons"][0]["budget"], 4500)

    def test_probe_checks_installed_list_before_running(self):
        with mock.patch.object(grader, "_installed_models", return_value=["other:9b"]), \
             mock.patch.object(grader, "_binary", return_value=Path("/bin/true")), \
             mock.patch.object(grader.OllamaDecision, "ask") as ask:
            with self.assertRaises(grader.GraderError):
                grader.probe("d3")
            ask.assert_not_called()

    def test_decision_ask_parses_stdout_and_flags_failure(self):
        completed = mock.Mock(returncode=0, stdout=json.dumps({
            "answers": {"q1": {"type": "choice", "choice": "A",
                                "probabilities": {"A": 1.0}, "confidence": 0.9}}}),
            stderr="\x1b[?25l")
        with mock.patch.object(grader.subprocess, "run", return_value=completed) as run, \
             mock.patch.object(grader, "_binary", return_value=Path("/bin/true")):
            result = grader.OllamaDecision("d3:latest").ask("Which?", "A: x\nB: y")
        self.assertEqual(result["choice"], "A")
        self.assertIn("--format", run.call_args.args[0])
        self.assertIn("json", run.call_args.args[0])

        failed = mock.Mock(returncode=1, stdout="", stderr="\x1b[?25lmodel not found")
        with mock.patch.object(grader.subprocess, "run", return_value=failed), \
             mock.patch.object(grader, "_binary", return_value=Path("/bin/true")):
            with self.assertRaises(grader.GraderError) as caught:
                grader.OllamaDecision("d3:latest").ask("Which?", "text")
        self.assertIn("model not found", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
