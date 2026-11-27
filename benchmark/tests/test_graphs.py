"""Black-box tests for the completed benchmark graphs report."""

import json
import os
from html.parser import HTMLParser
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.external_resources = []
        self.charts = {}
        self.chart = None
        self.row = None
        self.read_axis = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag in ("script", "link") and (attrs.get("src") or attrs.get("href")):
            self.external_resources.append(attrs.get("src") or attrs.get("href"))
        if tag == "article" and "chart" in attrs.get("class", "").split():
            key = (attrs["data-case"], attrs.get("data-rubric"))
            self.chart = {"rows": {}, "axis": []}
            self.charts[key] = self.chart
        if self.chart is not None:
            if attrs.get("class") in ("axis-labels", "plot-rows"):
                self.read_axis = attrs["class"] == "axis-labels"
            if tag == "li" and "data-model" in attrs:
                self.row = {"text": [], "marks": []}
                self.chart["rows"][attrs["data-model"]] = self.row
            if self.row is not None and tag in ("rect", "line", "circle"):
                self.row["marks"].append((tag, attrs))

    def handle_endtag(self, tag):
        if tag == "li":
            self.row = None
        if tag == "article":
            self.chart = None
            self.read_axis = False

    def handle_data(self, data):
        if self.row is not None:
            self.row["text"].append(data)
        if self.read_axis and data.strip():
            self.chart["axis"].append(data)


def synthetic_state(phase="complete"):
    models = ["test/alpha", "test/beta", "test/gamma"]
    cases = [
        {"id": "conversation", "role": "talking", "turns": ["Synthetic prompt"],
         "rubrics": [
             {"label": "clarity", "prompt": "Judge clarity", "evidence": False},
             {"label": "accuracy", "prompt": "Judge accuracy", "evidence": False},
         ]},
        {"id": "code-only", "role": "coding", "turns": ["Synthetic prompt"],
         "rubrics": []},
    ]
    runs = {
        "conversation": {
            models[0]: {"status": "ok", "check": "pass", "answers": [], "evidence": ""},
            models[1]: {"status": "ok", "check": "fail", "answers": [], "evidence": ""},
            models[2]: {"status": "error", "check": "not run", "answers": [],
                        "evidence": "", "error": "interrupted"},
        },
        "code-only": {
            models[0]: {"status": "ok", "check": "pass", "answers": [], "evidence": ""},
            models[1]: {"status": "ok", "check": "not configured", "answers": [],
                        "evidence": ""},
            models[2]: {"status": "error", "check": "not run", "answers": [],
                        "evidence": "", "error": "interrupted"},
        },
    }
    grades = {json.dumps(["conversation", model, index]): grade
              for model, index, grade in (
                  (models[0], 0, 1), (models[0], 1, 5),
                  (models[1], 0, 4), (models[1], 1, 2),
              )}
    review = [{"case": "conversation", "model": model, "rubric": index,
               "label": "Response"}
              for model in models[:2] for index in range(2)]
    return {"version": 1, "demo": False, "models": models, "cases": cases,
            "runs": runs, "review": review, "review_id": "synthetic",
            "grades": grades, "phase": phase}


def saved_preferences_state():
    state = synthetic_state()
    alpha, beta, _gamma = state["models"]
    delta = "test/delta"
    state["models"].append(delta)
    short_case = {"id": "short-case", "role": "talking", "turns": ["Synthetic prompt"],
                  "rubrics": [{"label": "depth", "prompt": "Judge depth", "evidence": False}]}
    state["cases"].append(short_case)
    state["runs"]["conversation"][delta] = state["runs"]["conversation"][alpha].copy()
    state["runs"]["short-case"] = {
        model: state["runs"]["conversation"][model].copy() for model in (alpha, beta)
    }
    for case, model, index, grade in (
        ("conversation", delta, 0, 1), ("conversation", delta, 1, 2),
        ("short-case", alpha, 0, 2), ("short-case", beta, 0, 3),
    ):
        state["grades"][json.dumps([case, model, index])] = grade
        state["review"].append({"case": case, "model": model, "rubric": index,
                                "label": "Response"})

    def row(wins, losses, ties, disagreements, score, rank):
        return {"wins": wins, "losses": losses, "ties": ties, "disagreements": disagreements,
                "games": wins + losses + ties + disagreements, "score": score, "rank": rank}

    state["auto_grades"] = {
        "version": 2, "grader": {"model": "d3:test"},
        "standings": {
            "conversation": {alpha: row(2, 0, 1, 1, 2, 1),
                             beta: row(0, 2, 1, 1, -2, 3),
                             delta: row(1, 1, 2, 0, 0, 2)},
            "code-only": {},
            "short-case": {alpha: row(1, 0, 0, 0, 1, 1),
                           beta: row(0, 1, 0, 0, -1, 2)},
        },
    }
    return state


class GraphsCLI(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="benchmark-graphs-")
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name)
        self.state_path = self.output / "state.json"
        self.report = self.output / "graphs.html"

    def write_state(self, state):
        self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return self.state_path.read_bytes()

    def graphs(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        return subprocess.run(
            [sys.executable, "-m", "benchmark", "graphs", "--output-dir", str(self.output)],
            cwd=self.output, env=env, text=True, capture_output=True,
            timeout=30, check=False,
        )

    def read_report(self):
        html = self.report.read_text(encoding="utf-8")
        parser = ReportParser()
        parser.feed(html)
        return html, parser

    def test_complete_report_plots_exact_human_grades_and_distinct_outcomes(self):
        before = self.write_state(synthetic_state())
        (self.output / "auto_scorecard.md").write_text("Not saved in state", encoding="utf-8")
        result = self.graphs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.state_path.read_bytes(), before)
        self.assertEqual(stat.S_IMODE(self.report.stat().st_mode), 0o600)
        html, parser = self.read_report()
        self.assertFalse(parser.external_resources, "Report must work standalone")
        self.assertNotIn("Pairwise preferences", html)
        self.assertEqual(set(parser.charts), {("conversation", "0"), ("conversation", "1")})
        for rubric, grades in enumerate(((1, 4), (5, 2))):
            chart = parser.charts["conversation", str(rubric)]
            self.assertEqual(chart["axis"], ["0", "5"])
            for model, grade in zip(("test/alpha", "test/beta"), grades):
                row = chart["rows"][model]
                self.assertEqual(row["marks"], [
                    ("rect", {"class": "mark-grade", "x": "0%", "width": f"{grade * 20}%",
                              "height": "12"}),
                ])
                self.assertEqual(row["text"][-1], str(grade))
            missing = chart["rows"]["test/gamma"]
            self.assertEqual(missing["marks"], [])
            self.assertIn("Missing grade", missing["text"])
        for label in ("conversation", "code-only", "clarity", "accuracy",
                       "test/alpha", "test/beta", "test/gamma"):
            self.assertIn(label, html)
        for outcome in ("pass", "fail", "not run", "not configured"):
            self.assertIn(outcome, html.lower())
        self.assertRegex(html.lower(), r"\b(?:error|interrupted)\b")

    def test_saved_preferences_show_signed_bars_and_keep_neutral_outcomes_distinct(self):
        before = self.write_state(saved_preferences_state())
        result = self.graphs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.state_path.read_bytes(), before)
        html, parser = self.read_report()
        self.assertIn("Pairwise preferences", html)
        self.assertIn("d3:test", html)
        self.assertIn("minus losses, not grades", html)
        machine = {case: chart for (case, rubric), chart in parser.charts.items()
                   if rubric is None}
        self.assertEqual(set(machine), {"conversation", "short-case"})
        for chart in machine.values():
            self.assertEqual(chart["axis"], ["−4", "0", "+4"])
        for case, model, direction, start, width, score in (
            ("conversation", "test/alpha", "ahead", "50%", "25%", "+2"),
            ("conversation", "test/beta", "behind", "25%", "25%", "−2"),
            ("short-case", "test/alpha", "ahead", "50%", "12.5%", "+1"),
            ("short-case", "test/beta", "behind", "37.5%", "12.5%", "−1"),
        ):
            row = machine[case]["rows"][model]
            self.assertEqual(row["marks"], [
                ("rect", {"class": f"mark-{direction}", "x": start, "width": width,
                          "height": "12"}),
            ])
            self.assertEqual(row["text"][-1], score)
        rows = machine["conversation"]["rows"]
        self.assertIn("Wins: 2; Losses: 0; Ties: 1; Disagreements: 1", rows["test/alpha"]["text"])
        self.assertEqual(rows["test/delta"]["marks"], [
            ("line", {"class": "mark-even", "x1": "50%", "x2": "50%", "y1": "1", "y2": "11"}),
        ])
        self.assertEqual(rows["test/delta"]["text"][-1], "0")
        self.assertEqual(rows["test/gamma"]["marks"], [])
        self.assertIn("Not compared", rows["test/gamma"]["text"])

    def test_saved_legacy_ties_do_not_invent_disagreement_counts(self):
        state = saved_preferences_state()
        state["auto_grades"]["version"] = 1
        for stats in state["auto_grades"]["standings"].values():
            for entry in stats.values():
                entry["ties"] += entry.pop("disagreements")
        self.write_state(state)
        result = self.graphs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html, parser = self.read_report()
        self.assertIn("T counts ties and order disagreements", html)
        alpha = parser.charts["conversation", None]["rows"]["test/alpha"]
        self.assertIn("Wins: 2; Losses: 0; Ties: 2", alpha["text"])
        self.assertFalse(any(text.endswith(" D") for text in alpha["text"]))

    def test_incomplete_state_is_rejected_without_changing_existing_report(self):
        for phase in ("executing", "review"):
            with self.subTest(phase=phase):
                before = self.write_state(synthetic_state(phase))
                self.report.write_text("existing report", encoding="utf-8")
                result = self.graphs()
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.state_path.read_bytes(), before)
                self.assertEqual(self.report.read_text(encoding="utf-8"), "existing report")
                self.assertTrue(result.stdout.strip() or result.stderr.strip())

    def test_labels_cannot_inject_html_or_break_out_of_embedded_data(self):
        state = synthetic_state()
        hostile = '</script><script id="injected">alert(1)</script>'
        state["cases"][0]["rubrics"][0]["label"] = hostile
        before = self.write_state(state)
        result = self.graphs()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.state_path.read_bytes(), before)
        parser = ReportParser()
        parser.feed(self.report.read_text(encoding="utf-8"))
        self.assertFalse(any(attrs.get("id") == "injected" for _, attrs in parser.tags))


if __name__ == "__main__":
    unittest.main()
