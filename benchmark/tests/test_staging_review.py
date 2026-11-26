"""Regression tests for fixture staging and blind review presentation."""

import json
import os
import subprocess
import sys
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from benchmark import runner


class StagingAndReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="benchmark-staging-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_nested_fixture_symlinks_are_rejected_before_host_content_is_copied(self):
        for target_kind in ("file", "directory"):
            with self.subTest(target_kind=target_kind):
                root = self.root / target_kind
                fixture = root / "case" / "fixture"
                nested = fixture / "nested"
                nested.mkdir(parents=True)
                host = root / "host"
                host.mkdir()
                sentinel = host / "sentinel.txt"
                sentinel.write_text("harmless test-owned sentinel", encoding="utf-8")
                target = sentinel if target_kind == "file" else host
                (nested / "linked").symlink_to(target, target_is_directory=target.is_dir())
                case = {
                    "_directory": str(root / "case"), "fixture": "fixture",
                    "role": "coding", "turns": ["Synthetic task."], "rubrics": [],
                }
                adapter_called = []
                copied_sentinel = []
                copytree = shutil.copytree

                def observe_copy(src, dst, *args, **kwargs):
                    result = copytree(src, dst, *args, **kwargs)
                    destination = Path(dst)
                    for path in destination.rglob("*"):
                        if path.is_file() and not path.is_symlink():
                            if path.read_bytes() == b"harmless test-owned sentinel":
                                copied_sentinel.append(path)
                    return result

                def adapter(*args):
                    adapter_called.append(True)
                    return {"answers": ["answer"], "evidence": "trace"}

                outcome = None
                try:
                    with patch.object(runner.shutil, "copytree", side_effect=observe_copy):
                        outcome = runner.run_one(case, "demo/alpha", adapter)
                except (OSError, ValueError, RuntimeError):
                    pass  # Rejection before an adapter is invoked is valid.
                if outcome is not None:
                    self.assertEqual(outcome["status"], "error", outcome)
                self.assertFalse(adapter_called, "Unsafe fixture reached the adapter")
                self.assertFalse(copied_sentinel, "Staging copied host content through a symlink")
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "harmless test-owned sentinel")

    def test_variant_model_aliases_are_blind_in_review_but_revealed_in_scorecard(self):
        models = ["openai/gpt-example#fast", "acme/othermodel#slow"]
        text = (
            "OPENAI/GPT-EXAMPLE and GpT-ExAmPlE; "
            "ACME/OTHERMODEL and OtHeRmOdEl. Keep the open discussion."
        )
        case = {
            "id": "case", "role": "handoff", "turns": [text],
            "rubrics": [
                {"label": "message", "prompt": text, "evidence": False},
                {"label": "evidence", "prompt": text, "evidence": True},
            ],
        }
        state = {
            "version": 1, "demo": True, "models": models, "cases": [case],
            "runs": {"case": {
                model: {"status": "ok", "answers": [text], "evidence": text,
                        "check": "not configured"}
                for model in models
            }},
            "review": [], "grades": {}, "phase": "executing",
        }
        runner.prepare_review(state)
        output = self.root / "review"
        output.mkdir()

        (output / "state.json").write_text(json.dumps(state), encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(runner.__file__).resolve().parent.parent)

        def cli(*args):
            return subprocess.run([sys.executable, "-m", "benchmark", *map(str, args)],
                                  input="", text=True, capture_output=True, env=env,
                                  timeout=30, check=False)

        result = cli("resume", "--output-dir", output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (output / "review.html").read_text(encoding="utf-8")
        self.assertIn("open discussion", html)
        for alias in ("openai/gpt-example", "gpt-example", "acme/othermodel", "othermodel"):
            self.assertNotIn(alias, (html + result.stdout + result.stderr).casefold(),
                             f"Leaked model alias {alias}")
        self.assertFalse((output / "scorecard.md").exists())

        # Reuse the black-box review-data parser shared by the CLI rehearsal.
        from benchmark.tests.test_cli_rehearsal import ReviewDataParser
        parser = ReviewDataParser()
        parser.feed(html)
        data = json.loads("".join(parser.parts))
        ids = [rubric["id"] for case in data["cases"]
               for response in case["responses"] for rubric in response["rubrics"]]
        self.assertEqual(len(ids), 4)
        grades = self.root / "grades.json"
        grades.write_text(json.dumps({"version": 1, "review_id": data["review_id"],
                                      "grades": dict.fromkeys(ids, 4)}), encoding="utf-8")
        imported = cli("import-grades", grades, "--output-dir", output)
        self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
        scorecard = (output / "scorecard.md").read_text(encoding="utf-8")
        for model in models:
            self.assertIn(model, scorecard)



if __name__ == "__main__":
    unittest.main()
