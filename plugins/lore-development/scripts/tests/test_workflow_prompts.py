"""Regression tests for workflow safeguards encoded in plugin prompts."""

import json
import os
import subprocess
from pathlib import Path

import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = PLUGIN_ROOT.parents[1]


def _read(relative_path: str) -> str:
    return (PLUGIN_ROOT / relative_path).read_text(encoding="utf-8")


def _normalized(relative_path: str) -> str:
    return " ".join(_read(relative_path).split())


def _frontmatter(relative_path: str) -> dict[str, object]:
    prompt = _read(relative_path)
    opening, frontmatter, _body = prompt.split("---", maxsplit=2)
    assert opening == ""
    parsed = yaml.safe_load(frontmatter)
    assert isinstance(parsed, dict)
    return parsed


def test_implementation_roles_are_serialized_and_read_only() -> None:
    prompt = _read("skills/implement/SKILL.md")

    assert "Only one agent may operate on a phase's files at a time" in prompt
    assert "Testing and review agents are read-only" in prompt
    assert "Await each result before" in prompt
    assert "dispatching the next role" in prompt


def test_implementation_requires_mapped_behavioral_evidence() -> None:
    prompt = _read("skills/implement/SKILL.md")

    assert "mapping every obligation" in prompt
    assert "task's exact Validation section" in prompt
    assert "obligation-to-evidence table" in prompt
    assert "suite passing does not substitute" in prompt


def test_review_workflows_distinguish_initial_and_verification_modes() -> None:
    prompts = [
        _read("skills/implement/SKILL.md"),
        _read("agents/design-reviewer.md"),
        _read("agents/spec-reviewer.md"),
        _read("agents/plan-reviewer.md"),
    ]

    for prompt in prompts:
        assert "initial-review" in prompt
        assert "verification" in prompt
        assert "stable ID" in prompt

    for path in [
        "agents/design-reviewer.md",
        "agents/spec-reviewer.md",
        "agents/plan-reviewer.md",
    ]:
        prompt = _normalized(path)
        assert "complete unresolved finding records" in prompt
        assert "newly encountered material issue" in prompt
        assert "do not populate a fixed template" in prompt


def test_document_reviewers_do_not_force_ceremonial_output() -> None:
    for path in [
        "agents/design-reviewer.md",
        "agents/spec-reviewer.md",
        "agents/plan-reviewer.md",
    ]:
        prompt = _normalized(path)
        assert "guessing which file is newest" in prompt
        assert "force one finding per lens" in prompt
        assert "Reviewed: [timestamp]" not in prompt
        assert "## Strengths" not in prompt


def test_lore_researcher_uses_lifecycle_aware_authority() -> None:
    prompt = _normalized("agents/lore-researcher.md")

    assert "shared/frontmatter-schema.md" in prompt
    assert "schema owns document types and lifecycle statuses" in prompt
    assert "check frontmatter status" in prompt
    assert "not as proof that a document is authoritative" in prompt
    assert "authoritative status or explicit supersession evidence" in prompt
    assert "links could establish authority" not in prompt
    assert "Do not silently resolve conflicts" in prompt
    assert "Search all three zones even after finding a strong match" in prompt
    assert "Frontmatter improves ranking but is not a prerequisite" in prompt


def test_bun_typescript_reviewer_requires_material_traceable_findings() -> None:
    reviewer = _normalized("agents/bun-typescript-reviewer.md")
    implementation = _normalized("skills/implement/SKILL.md")

    assert "A review that finds no material non-conformance is successful" in reviewer
    assert "Architecture concerns are investigative lenses, not a quota" in reviewer
    assert "Judge validation by whether it proves the requested outcome" in reviewer
    assert "Do not request a test merely because production code lacks" in reviewer
    assert "Raise a new finding only for a material defect introduced" in reviewer
    assert "If the implementation is adequate, say `Accept`" in reviewer
    assert "do not populate a fixed template" in reviewer
    assert "## Requirement Evidence" not in reviewer
    assert "## Findings" not in reviewer
    assert "use the bundled `bun-typescript-reviewer`" in implementation
    assert (
        "The reviewer may return a concise acceptance" in implementation
    )
    assert "A request for another test is not a finding unless" in implementation


def test_specification_prompt_is_human_first() -> None:
    prompt = _read("skills/specify/SKILL.md")
    reviewer = _read("agents/spec-reviewer.md")

    expected_order = [
        "Goal and user problem",
        "representative user-visible examples",
        "Plain-language explanation",
        "Visible behavior and important product choices",
        "Numbered requirements",
        "Optional Technical Contract",
    ]
    positions = [prompt.index(section) for section in expected_order]

    assert positions == sorted(positions)
    assert "Run the comprehension pass" in reviewer
    assert "legalistic repetition" in reviewer.lower()


def test_design_skill_runs_fresh_context_review() -> None:
    prompt = _normalized("skills/design/SKILL.md")

    assert "invoke the `design-reviewer` subagent" in prompt
    assert "`initial-review` mode" in prompt
    assert "complete unresolved finding records" in prompt
    assert "`verification` mode" in prompt
    assert "terminal broad acceptance review" in prompt
    assert "do not run another broad review unless accepted scope changed" in prompt


def test_lore_search_contract_includes_lower_confidence_body_matches() -> None:
    schema = _normalized("shared/frontmatter-schema.md")
    readme = _normalized("README.md")

    for document in (schema, readme):
        assert "body" in document
        assert "lower-confidence legacy material" in document


def test_tracker_rules_prevent_duplicates_and_parent_dependency_cycles() -> None:
    breakdown = _read("skills/plan-breakdown/SKILL.md")
    implementation = _read("skills/implement/SKILL.md")

    assert "reconcile existing" in breakdown
    assert "children before creating any" in breakdown
    assert "never make a" in breakdown
    assert "parent depend on its own descendant" in breakdown
    assert "regenerate any passive export" in implementation


def test_commit_handoff_does_not_reopen_accepted_work() -> None:
    prompt = _read("skills/implement/SKILL.md")

    assert "do not reopen implementation or" in prompt
    assert "Perform only commit safety checks" in prompt
    assert "accepted-manifest equality" in prompt
    assert "record an accepted manifest" in prompt
    assert "exact porcelain status" in prompt
    assert "index blob identity or absent/unmerged marker" in prompt
    assert "working-tree SHA-256 content hash or deletion marker" in prompt
    assert "index and working-tree content separately" in prompt
    assert "Include untracked files" in prompt
    assert "requires exact equality" in prompt
    assert "instead of rerunning the workflow" in prompt


def test_design_inputs_map_decisions_to_evidence() -> None:
    prompt = _normalized("skills/implement/SKILL.md")

    assert "decisions and interface commitments from a design" in prompt
    assert "mapping every obligation" in prompt
    assert "reconcile every source obligation" in prompt


def test_opencode_agent_frontmatter_is_read_only_and_model_agnostic() -> None:
    agent_paths = [
        "agents/bun-typescript-reviewer.md",
        "agents/design-reviewer.md",
        "agents/lore-researcher.md",
        "agents/plan-reviewer.md",
        "agents/spec-reviewer.md",
    ]

    for path in agent_paths:
        frontmatter = _frontmatter(path)
        assert frontmatter["mode"] == "subagent"
        assert frontmatter["permission"] == {"edit": "deny", "bash": "deny"}
        assert "model" not in frontmatter
        assert "tools" not in frontmatter


def test_setup_registers_lore_agents_without_overwriting(tmp_path: Path) -> None:
    config_home = tmp_path / "config"
    env = {**os.environ, "XDG_CONFIG_HOME": str(config_home)}
    setup = REPOSITORY_ROOT / "scripts/setup-opencode.sh"

    conflicting_agent = config_home / "opencode/agents/spec-reviewer.md"
    conflicting_agent.parent.mkdir(parents=True)
    conflicting_agent.write_text("user-owned\n", encoding="utf-8")

    first = subprocess.run(
        [str(setup)], capture_output=True, check=True, env=env, text=True
    )
    second = subprocess.run(
        [str(setup)], capture_output=True, check=True, env=env, text=True
    )

    config = json.loads(
        (config_home / "opencode/opencode.json").read_text(encoding="utf-8")
    )
    registered = sorted((config_home / "opencode/agents").iterdir())
    source_agents = sorted((PLUGIN_ROOT / "agents").iterdir())

    assert str(REPOSITORY_ROOT / "plugins") in config["skills"]["paths"]
    assert [path.name for path in registered] == [path.name for path in source_agents]
    assert conflicting_agent.read_text(encoding="utf-8") == "user-owned\n"
    assert all(path.is_symlink() for path in registered if path != conflicting_agent)
    registered_count = sum(path.is_symlink() for path in registered)
    expected = f"Registered {registered_count} lore-development agent definition(s)"
    assert expected in first.stdout
    assert expected in second.stdout
    assert "preserving existing OpenCode agent" in first.stderr
