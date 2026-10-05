"""Regression checks for simplify scope and behavior-preservation contracts."""

from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def _prompt() -> str:
    return " ".join(
        (PLUGIN_ROOT / "skills/simplify/SKILL.md")
        .read_text(encoding="utf-8")
        .split()
    )


def test_simplify_scope_includes_committed_and_pending_changes() -> None:
    prompt = _prompt()

    assert "use an integration/target branch only when identified" in prompt
    assert "find its unique merge-base with `HEAD`" in prompt
    assert "Ask if the merge-base is ambiguous" in prompt
    assert "include relevant staged, unstaged, and untracked changes" in prompt
    assert (
        "explicit work artifact identified by the invocation or current conversation"
        in prompt
    )
    assert "Git base/range" in prompt
    assert "ask the user for an artifact, Git base/range, or files" in prompt
    assert "Never assume `HEAD`, the latest commit, or the whole repository" in prompt
    assert "Resolve repo-relative paths against the repository root" in prompt
    assert "tracking upstream" in prompt
    assert "Never infer the work boundary solely" in prompt
    assert "Explicit user-specified refs are supported" in prompt


def test_simplify_preserves_retained_contracts_and_limits_expansion() -> None:
    prompt = _prompt()

    assert "Retire behavior only when the source artifact explicitly approves" in prompt
    assert "test count or apparent lack of use is not evidence" in prompt
    assert "Keep every retained contract protected" in prompt
    assert (
        "Expand beyond the resolved surface only when necessary and authorized"
        in prompt
    )
    for role in ("Cleanup.", "Test.", "Review."):
        assert f"**{role}**" in prompt
    assert (
        "governing artifact, resolved scope, retained behavior, approved retirements"
        in prompt
    )
    assert "validation criteria" in prompt
