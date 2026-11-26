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

    def test_autograde_accepts_review_without_changing_human_state(self):
        state = make_state()
        state["phase"] = "review"
        state["grades"] = {json.dumps(["case1", "a/m1", 0]): 4}
        grades = state["grades"].copy()
        with tempfile.TemporaryDirectory() as temp:
            record, _ = grader.autograde(
                Path(temp), state, model="d3", decide=FakeDecide(["A", "B"] * 3))
            saved = json.loads((Path(temp) / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(len(record["comparisons"]), 3)
        self.assertEqual(state["phase"], "review")
        self.assertEqual(saved["phase"], "review")
        self.assertEqual(state["grades"], grades)
        self.assertEqual(saved["grades"], grades)

    def test_autograde_rejects_executing_runs(self):
        state = make_state()
        state["phase"] = "executing"
        decide = mock.Mock()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(grader.GraderError):
                grader.autograde(Path(temp), state, model="d3", decide=decide)
        decide.assert_not_called()

    def test_question_uses_rubric_decision_prompt_and_blinds_identities(self):
        rubric = {"label": "message", "prompt": "Rate 1-5.",
                  "decision_prompt": "Which answer by a/m1 is more helpful?",
                  "evidence": False}
        question = grader.question_for(rubric, MODELS)
        self.assertIn("more helpful", question)
        self.assertNotIn("a/m1", question)
        self.assertNotIn("1-5", question)

    def test_question_for_legacy_rubric_does_not_embed_human_scale(self):
        rubric = {"label": "message", "prompt": "Score 1-5: 1 is poor, 5 is best.",
                  "evidence": False}
        question = grader.question_for(rubric, MODELS)
        self.assertIn("response", question.lower())
        self.assertNotIn("1-5", question)
        self.assertNotIn("1 is poor", question)

    def test_autograde_records_ranking_and_preserves_human_grades(self):
        state = make_state()
        state["grades"] = {
            json.dumps(["case1", "a/m1", 0]): 5,
            json.dumps(["case1", "b/m2", 0]): 1,
            json.dumps(["case1", "c/m3", 0]): 3,
        }
        decide = FakeDecide([
            "A", "B",   # m1 beats m2 in both orders
            "A", "A",   # m1 vs m3: orders disagree
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
                          stats["a/m1"]["ties"], stats["a/m1"]["disagreements"]),
                         (1, 0, 0, 1))
        self.assertEqual((stats["c/m3"]["wins"], stats["c/m3"]["losses"],
                          stats["c/m3"]["ties"], stats["c/m3"]["disagreements"]),
                         (1, 0, 0, 1))
        self.assertEqual((stats["b/m2"]["wins"], stats["b/m2"]["losses"]), (0, 2))
        self.assertEqual(stats["a/m1"]["rank"], 1)
        self.assertEqual(stats["c/m3"]["rank"], 1)
        self.assertEqual(stats["b/m2"]["rank"], 3)
        outcomes = [entry["outcome"] for entry in record["comparisons"]]
        self.assertEqual(outcomes, ["a", "disagreement", "b"])
        self.assertEqual(saved["grades"], state["grades"])
        self.assertIn("Local second opinion", report)
        self.assertIn("Spearman vs human mean", report)
        self.assertIn("disagreement", report.lower())

    def test_no_clear_winner_and_order_disagreement_are_distinct(self):
        for choices, outcome, ties, disagreements in [
            (["C", "C"], "tie", 1, 0),
            (["A", "A"], "disagreement", 0, 1),
            (["A", "C"], "disagreement", 0, 1),
            (["C", "B"], "disagreement", 0, 1),
        ]:
            with self.subTest(choices=choices), tempfile.TemporaryDirectory() as temp:
                state = make_state()
                state["models"] = MODELS[:2]
                decide = FakeDecide(choices)
                record, report = grader.autograde(
                    Path(temp), state, model="d3", decide=decide)
                self.assertEqual(record["comparisons"][0]["outcome"], outcome)
                for model in state["models"]:
                    stats = record["standings"]["case1"][model]
                    self.assertEqual((stats["wins"], stats["losses"]), (0, 0))
                    self.assertEqual(stats["ties"], ties)
                    self.assertEqual(stats["disagreements"], disagreements)
                for _, _, options in decide.calls:
                    self.assertIn("C", [label for label, _ in options])
                    description = dict(options)["C"].lower()
                    self.assertTrue("clear" in description or "tie" in description)
                self.assertIn("disagreement", report.lower())

    def test_equal_scores_share_rank_for_ties_and_disagreements(self):
        for choices in (["C", "C"], ["A", "A"]):
            with self.subTest(choices=choices), tempfile.TemporaryDirectory() as temp:
                record, report = grader.autograde(
                    Path(temp), make_state(), model="d3",
                    decide=FakeDecide(choices * 3))
                stats = record["standings"]["case1"]
                self.assertEqual([stats[model]["rank"] for model in MODELS], [1, 1, 1])
                rows = [line for line in report.splitlines()
                        if any(f"| {model} |" in line for model in MODELS)]
                self.assertEqual(len(rows), 3)
                self.assertEqual(
                    [next(model for model in MODELS if f"| {model} |" in row)
                     for row in rows], MODELS)

    def test_agreement_excludes_models_with_incomplete_human_grades(self):
        case = {**CASE, "rubrics": [
            CASE["rubrics"][0],
            {"label": "clarity", "prompt": "Rate clarity.", "evidence": False},
        ]}
        state = make_state(case)
        state["grades"] = {
            json.dumps(["case1", "a/m1", 0]): 5,
            json.dumps(["case1", "a/m1", 1]): 5,
            json.dumps(["case1", "b/m2", 0]): 1,
            json.dumps(["case1", "b/m2", 1]): 1,
            json.dumps(["case1", "c/m3", 0]): 3,
        }
        with tempfile.TemporaryDirectory() as temp:
            record, report = grader.autograde(
                Path(temp), state, model="d3", decide=FakeDecide(["A", "B"] * 6))
        agreement = record["agreement"]["cases"]["case1"]
        self.assertLessEqual(agreement["n"], 2)
        self.assertNotIn("(n=3)", report)

    def test_no_agreement_claim_without_human_grades(self):
        with tempfile.TemporaryDirectory() as temp:
            record, report = grader.autograde(
                Path(temp), make_state(), model="d3", decide=FakeDecide(["A", "B"] * 3))
        self.assertIsNone(record["agreement"]["cases"]["case1"]["rho"])
        self.assertIsNone(record["agreement"]["overall"]["mean_rho"])
        self.assertNotIn("Spearman vs human mean:", report)

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
