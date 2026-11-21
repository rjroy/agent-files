"""Regression tests for fixture staging and blind review presentation."""

from contextlib import redirect_stdout
import io
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

        first = io.StringIO()
        with redirect_stdout(first), patch("builtins.input", side_effect=EOFError):
            runner.review(output, state)
        self.assertFalse((output / "scorecard.md").exists())

        second = io.StringIO()
        with redirect_stdout(second), patch("builtins.input", side_effect=["4", EOFError]):
            runner.review(output, state)
        self.assertIn("EVIDENCE", second.getvalue())
        self.assertFalse((output / "scorecard.md").exists())

        final = io.StringIO()
        with redirect_stdout(final), patch("builtins.input", side_effect=["2", "3", "5"]):
            runner.review(output, state)
        displayed = final.getvalue()
        self.assertIn("# Benchmark scorecard", displayed)
        before_reveal = first.getvalue() + second.getvalue() + displayed.split(
            "# Benchmark scorecard", 1
        )[0]
        self.assertIn("open discussion", before_reveal)
        for alias in ("openai/gpt-example", "gpt-example", "acme/othermodel", "othermodel"):
            self.assertNotIn(alias, before_reveal.casefold(), f"Leaked model alias {alias}")
        scorecard = (output / "scorecard.md").read_text(encoding="utf-8")
        for model in models:
            self.assertIn(model, scorecard)
            self.assertIn(model, displayed.split("# Benchmark scorecard", 1)[1])


if __name__ == "__main__":
    unittest.main()
