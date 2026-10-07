"""Regression tests for workflow safeguards encoded in plugin prompts."""

import json
import os
import re
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


def test_implementation_uses_proportionate_behavioral_evidence() -> None:
    prompt = _normalized("skills/implement/SKILL.md")

    assert "The full suite passing is not enough" in prompt
    assert "focused checks for distinct plausible defects" in prompt
    assert "Do not create requirement IDs, exhaustive mappings" in prompt
    assert "suite passing does not substitute" in prompt
    assert "Current user direction may authorize behavior or contract changes" in prompt
    assert "do not treat an old artifact's silence" in prompt
    assert "new evidence" in prompt


def test_review_workflows_distinguish_initial_and_verification_modes() -> None:
    prompts = [
        _read("skills/implement/SKILL.md"),
        _read("agents/design-reviewer.md"),
        _read("agents/plan-reviewer.md"),
    ]

    for prompt in prompts:
        assert "initial-review" in prompt
        assert "verification" in prompt
        assert "stable ID" in prompt

    for path in [
        "agents/design-reviewer.md",
        "agents/plan-reviewer.md",
    ]:
        prompt = _normalized(path)
        assert "complete unresolved finding records" in prompt
        assert "newly encountered material issue" in prompt
        assert "do not populate a fixed template" in prompt


def test_document_reviewers_do_not_force_ceremonial_output() -> None:
    for path in [
        "agents/design-reviewer.md",
        "agents/plan-reviewer.md",
    ]:
        prompt = _normalized(path)
        assert "guessing which file is newest" in prompt
        assert "force one finding per lens" in prompt
        assert "Reviewed: [timestamp]" not in prompt
        assert "## Strengths" not in prompt


def test_lore_researcher_surfaces_context_without_binding_history() -> None:
    prompt = _normalized("agents/lore-researcher.md")

    assert "shared/frontmatter-schema.md" in prompt
    assert "schema owns document types and lifecycle statuses" in prompt
    assert (
        "their location, status, dates, and links do not make them instructions"
        in prompt
    )
    assert "the user's current direction as the guide" in prompt
    assert "Legacy documents under `work/specs/` are historical input only" in prompt
    assert "Do not silently resolve conflicts" in prompt
    assert "Search all relevant zones even after finding a strong match" in prompt
    assert "Frontmatter improves ranking but is not a prerequisite" in prompt


def test_local_lore_paths_setup_and_legacy_discovery_are_documented() -> None:
    for path in [
        "skills/prep-plan/SKILL.md",
        "skills/implement/SKILL.md",
        "skills/simplify/SKILL.md",
    ]:
        prompt = _normalized(path)
        assert ".lore/local/" in prompt
        assert "scripts/ensure_local.py" in prompt
        assert "from this skill's installed directory" in prompt
        assert "python3 <resolved-helper-path>" in prompt
        assert "Write only after setup succeeds" in prompt
        assert ".lore/work/" in prompt
        assert any(term in prompt for term in ("fall back", "falling back", "fallback"))
    init_path = REPOSITORY_ROOT / "plugins/field-guide/skills/init/SKILL.md"
    init = Path(init_path).read_text()
    assert "CronCreate and CronList are only required for scheduling" in init
    assert "Do not require the helper or Cron for wiki/index setup" in init
    assert "do not claim `.lore/local/` is ready" in init
    schema = _read("shared/frontmatter-schema.md")
    assert "Legacy plans, tasks, and notes remain readable" in schema


def test_field_guide_distills_verified_useful_context_not_binding_history() -> None:
    field_guide = REPOSITORY_ROOT / "plugins/field-guide/skills"
    ingest = (field_guide / "ingest/SKILL.md").read_text(encoding="utf-8")
    query = (field_guide / "query/SKILL.md").read_text(encoding="utf-8")
    drift = (field_guide / "resolve-drift/SKILL.md").read_text(encoding="utf-8")
    lint = (field_guide / "lint/SKILL.md").read_text(encoding="utf-8")
    ingest_query = " ".join(ingest.split())
    query = " ".join(query.split())
    drift = " ".join(drift.split())
    lint = " ".join(lint.split())

    # Example: an old approved design says use A, but the current user asks
    # for B. The old approval is historical context, not an instruction.
    assert "historical rationale" in ingest_query
    assert "The user's current direction prevails" in ingest_query
    assert "follow current direction" in query
    assert "A conflict with an old plan, note, or artifact alone is not drift" in drift

    # Example: a candidate page merely repeats implementation. Merge/update or
    # retire existing prose rather than writing another artifact summary.
    assert (
        "Do not make a page just to summarize a feature, implementation"
        in ingest_query
    )
    assert "merge" in ingest_query and "retire" in ingest_query
    assert "no page is a valid outcome" in query

    # Example: a local plan alone cannot promote an execution choice. It can
    # only point toward independent investigation.
    assert (
        "Plans, notes, and tasks (including under `.lore/local/`) are never "
        "reference sources"
    ) in ingest_query
    assert "may point to where to investigate" in ingest_query
    assert "plans, notes, and tasks are not reference sources" in query

    # Lint's file timestamps and provenance cannot reintroduce authority.
    assert "not evidence that the reference page is stale" in lint
    assert "not authority or proof of currency" in drift


def test_prep_plan_prompts_collaborative_evidence_driven_planning() -> None:
    prompt = _normalized("skills/prep-plan/SKILL.md")

    assert "user's present what and why" in prompt
    assert "Discuss the approach and meaningful evidence with the user" in prompt
    assert "revise when repository facts or other evidence change" in prompt
    assert "as suggestions or historical context" in prompt
    assert "Plans and notes are not promoted to reference material" in prompt
    assert "exhaustive obligation maps, coverage matrices" in prompt
    assert "does not add an approval requirement" in prompt
    for forbidden_rule in [
        "Map the goal or requirements to concrete implementation steps",
        "An unmapped obligation is a planning gap",
        "## Coverage Matrix",
    ]:
        assert forbidden_rule not in prompt


def test_plan_reviewer_avoids_exhaustive_mapping_and_historical_authority() -> None:
    reviewer = _normalized("agents/plan-reviewer.md")

    assert "fits the user's current direction" in reviewer
    assert "do not override current user direction" in reviewer
    assert "do not require exhaustive obligation mapping" in reviewer
    assert "acceptance matrices" in reviewer
    assert "meaningful for the project-specific behavior and risks" in reviewer
    assert "Do not report old-artifact noncompliance alone" in reviewer
    assert "one test per requirement" in reviewer


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
    assert "Accept adequate work" in implementation
    assert "A request for another test must identify" in implementation


def test_intent_prompt_is_conversational_and_nonbinding() -> None:
    prompt = _normalized("skills/intent/SKILL.md")

    assert "what to build and why" in prompt
    assert "conversational" in prompt
    assert "not a binding contract" in prompt
    assert "The plan is where" in prompt
    assert "current direction takes priority" in prompt
    assert "historical context" in prompt
    assert "## Requirements" not in prompt
    assert "## Validation" not in prompt
    assert "REQ-" not in prompt
    assert "acceptance matrix" in prompt


def test_intent_reviewer_has_fresh_context_modes_without_contract_checks() -> None:
    reviewer = _normalized("agents/intent-reviewer.md")

    assert "initial-review" in reviewer
    assert "verification" in reviewer
    assert "faithfully captures intent" in reviewer
    assert "Do not require numbered requirements" in reviewer
    assert "Do not treat an old artifact's noncompliance" in reviewer


def test_intent_reviewer_and_researcher_treat_legacy_specs_as_history() -> None:
    reviewer = _normalized("agents/intent-reviewer.md")
    researcher = _normalized("agents/lore-researcher.md")

    assert "historical context, not a binding contract" in reviewer
    assert "The user's current direction prevails" in reviewer
    assert (
        "Legacy documents under `work/specs/` are historical input only"
        in researcher
    )
    assert "do not override the user's present direction" in researcher
    assert "old-document noncompliance alone is not a blocker" in researcher

    design_reviewer = _normalized("agents/design-reviewer.md")
    assert "Historical specs and other work artifacts" in design_reviewer
    assert "do not constrain current user direction" in design_reviewer
    assert "old-document noncompliance alone" in design_reviewer


def test_intent_schema_keeps_legacy_specs_historical_only() -> None:
    schema = _normalized("shared/frontmatter-schema.md")

    assert "`.lore/work/specs/`" in schema
    assert "legacy_status" in schema
    assert "requirement IDs and validation sections do not make them authoritative for current work" in schema
    assert "does not make a document newly authored or confer authority" in schema


def test_implementation_does_not_block_on_old_artifact_conflict_alone() -> None:
    prompt = _normalized("skills/implement/SKILL.md")

    assert "A conflict with an old artifact alone is not a blocker" in prompt
    assert "follow current user direction" in prompt
    assert "concrete safety or compatibility consequences" in prompt
    assert "old artifact's omission or contradiction alone" in prompt


def test_implementation_accepts_direct_requests_and_keeps_notes_optional() -> None:
    prompt = _normalized("skills/implement/SKILL.md")
    schema = _normalized("shared/frontmatter-schema.md")
    readme = _normalized("README.md")

    assert "current request or intent, optionally informed" in prompt
    assert "user's current request" in prompt
    assert "A plan is useful but not required" in prompt
    assert "do not create one by default" in prompt
    assert "Do not ask for confirmation between phases" in prompt
    assert "read-only testing agent" in prompt
    assert "read-only review agent" in prompt
    assert "Route material findings to implementation for correction" in prompt
    assert "repeat only the failed checks" in prompt
    assert "terminal review to catch interactions" in prompt
    assert "reuse, replace, or remove" in prompt
    assert "obsolete parallel path or unused scaffolding" in prompt
    assert "material maintenance or behavior cost, not a cleanup quota" in prompt
    assert "does not determine `/implement` execution order" in schema
    assert "an optional plan can help, but is not required" in readme


def test_implementation_reviewers_follow_current_direction() -> None:
    implementation = _normalized("skills/implement/SKILL.md")

    assert "relevant requirements from the source artifact" not in implementation
    assert "mapped source obligations" not in implementation
    assert "obligation-to-evidence mapping" not in implementation
    for path in [
        "agents/bun-typescript-reviewer.md",
        "agents/rust-daemon-cli-reviewer.md",
    ]:
        reviewer = _normalized(path)
        assert "user's current requested behavior" in reviewer
        assert "do not override current user direction" in reviewer
        assert "Do not report noncompliance with an old artifact alone" in reviewer


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


def test_readme_skill_table_matches_active_inventory_and_shared_lifecycle() -> None:
    readme = _normalized("README.md")
    schema = _normalized("shared/frontmatter-schema.md")

    table = readme.split("## Skills", maxsplit=1)[1].split("## ", maxsplit=1)[0]
    listed_skills = set(re.findall(r"`/lore-development:([^`]+)`", table))
    active_skills = {
        path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")
    }
    assert listed_skills == active_skills
    assert "`/field-guide:stratify`" in readme
    assert (PLUGIN_ROOT.parent / "field-guide/skills/stratify/SKILL.md").is_file()

    agent_table = readme.split("## Agents", maxsplit=1)[1].split("## ", maxsplit=1)[0]
    listed_agents = set(re.findall(r"\| `([^`]+)` \|", agent_table))
    active_agents = {path.stem for path in (PLUGIN_ROOT / "agents").glob("*.md")}
    assert listed_agents == active_agents
    assert "learned/" in readme
    assert "no lore-development skill currently writes it" in schema
    assert "Shared four-value lifecycle across all lore zones" in schema
    assert "Document-type-specific" not in schema


def test_retired_plan_breakdown_is_not_an_active_skill_or_implement_path(
    tmp_path: Path,
) -> None:
    implementation = _read("skills/implement/SKILL.md")
    skill_dir = PLUGIN_ROOT / "skills/plan-breakdown"

    assert not skill_dir.exists()
    assert "plan-breakdown" not in implementation
    assert "Task file detection" not in implementation
    assert "task's exact Validation section" not in implementation

    # Setup discovers skills from source directories. A dangling config symlink
    # cannot restore a removed skill, and must remain untouched as user data.
    config_home = tmp_path / "config"
    skills_dir = config_home / "opencode/skills"
    skills_dir.mkdir(parents=True)
    stale_registration = skills_dir / "plan-breakdown"
    stale_registration.symlink_to(tmp_path / "missing-plan-breakdown")
    setup = REPOSITORY_ROOT / "scripts/setup-opencode.sh"
    result = subprocess.run(
        [str(setup)], capture_output=True, check=True,
        env={**os.environ, "XDG_CONFIG_HOME": str(config_home)}, text=True,
    )

    assert stale_registration.is_symlink()
    assert not stale_registration.exists()
    assert "plan-breakdown" not in result.stdout


def test_commit_handoff_revalidates_changes_after_review() -> None:
    prompt = _read("skills/implement/SKILL.md")

    assert "check the intended changes and required project safeguards" in prompt
    assert (
        "If code changes after testing/review, validate and review the "
        "changed behavior again"
        in prompt
    )


def test_design_inputs_use_relevant_evidence_without_exhaustive_mapping() -> None:
    prompt = _normalized("skills/implement/SKILL.md")

    assert "affected consumers, actual behavior" in prompt
    assert "Identify the project-specific behavior and risks" in prompt
    assert "Do not create requirement IDs, exhaustive mappings" in prompt


def test_opencode_agent_frontmatter_is_read_only_with_explicit_models() -> None:
    agent_models = {
        "agents/bun-typescript-reviewer.md": "openai/gpt-6.1-sol#high",
        "agents/design-reviewer.md": "openai/gpt-6-astra#high",
        "agents/lore-researcher.md": "openai/gpt-6-luna#medium",
        "agents/plan-reviewer.md": "openai/gpt-6-astra#high",
        "agents/rust-daemon-cli-reviewer.md": "openai/gpt-6.1-sol#high",
        "agents/intent-reviewer.md": "openai/gpt-6-astra#high",
    }

    for path, model in agent_models.items():
        frontmatter = _frontmatter(path)
        assert frontmatter["mode"] == "subagent"
        assert frontmatter["permission"] == {"edit": "deny", "bash": "deny"}
        assert frontmatter["model"] == model
        assert "tools" not in frontmatter


def test_setup_registers_lore_agents_without_overwriting(tmp_path: Path) -> None:
    config_home = tmp_path / "config"
    env = {**os.environ, "XDG_CONFIG_HOME": str(config_home)}
    setup = REPOSITORY_ROOT / "scripts/setup-opencode.sh"

    conflicting_agent = config_home / "opencode/agents/intent-reviewer.md"
    conflicting_agent.parent.mkdir(parents=True)
    conflicting_agent.write_text("user-owned\n", encoding="utf-8")

    first = subprocess.run(
        [str(setup)], capture_output=True, check=True, env=env, text=True
    )
    second = subprocess.run(
        [str(setup)], capture_output=True, check=True, env=env, text=True
    )

    registered = sorted((config_home / "opencode/agents").iterdir())
    source_agents = sorted((PLUGIN_ROOT / "agents").iterdir())
    expected_agent_names = [path.name for path in source_agents]
    for collection in ("music-engine-rowan", "story-engine-wyrd"):
        expected_agent_names.extend(
            f"{collection}-{path.name}"
            for path in (REPOSITORY_ROOT / "plugins" / collection / "agents").iterdir()
        )

    assert not (config_home / "opencode/opencode.json").exists()
    assert [path.name for path in registered] == sorted(expected_agent_names)
    assert conflicting_agent.read_text(encoding="utf-8") == "user-owned\n"
    assert all(path.is_symlink() for path in registered if path != conflicting_agent)
    registered_count = sum(
        (config_home / "opencode/agents" / path.name).is_symlink()
        for path in source_agents
    )
    expected = f"Registered {registered_count} lore-development agents definition(s)"
    assert expected in first.stdout
    assert expected in second.stdout
    assert "preserving existing OpenCode agent" in first.stderr


def test_setup_preserves_skill_array_and_registers_commands(
    tmp_path: Path,
) -> None:
    config_home = tmp_path / "config"
    config_dir = config_home / "opencode"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "opencode.json"
    existing_skill = "/opt/team-skills"
    skills = [existing_skill, "https://example.test/skills/"]
    config_file.write_text(json.dumps({"skills": skills}), encoding="utf-8")
    conflicting_command = config_dir / "commands/init.md"
    conflicting_command.parent.mkdir(parents=True)
    conflicting_command.write_text("user-owned\n", encoding="utf-8")

    setup = REPOSITORY_ROOT / "scripts/setup-opencode.sh"
    result = subprocess.run(
        [str(setup)],
        capture_output=True,
        check=True,
        env={**os.environ, "XDG_CONFIG_HOME": str(config_home)},
        text=True,
    )

    config = json.loads(config_file.read_text(encoding="utf-8"))
    assert config["skills"] == skills
    assert conflicting_command.read_text(encoding="utf-8") == "user-owned\n"
    assert (config_dir / "commands/digest.md").is_symlink()
    assert (config_dir / "commands/write-lyrics.md").is_symlink()
    assert (config_dir / "commands/review-story.md").is_symlink()
    assert (config_dir / "skills/implement").is_symlink()
    assert (config_dir / "skills/intent").is_symlink()
    assert not os.path.lexists(config_dir / "skills/specify")
    assert "preserving existing OpenCode command" in result.stderr


def test_setup_preserves_dangling_definition_and_skill_collisions(
    tmp_path: Path,
) -> None:
    config_home = tmp_path / "config"
    config_dir = config_home / "opencode"
    agents_dir = config_dir / "agents"
    skills_dir = config_dir / "skills"
    agents_dir.mkdir(parents=True)
    skills_dir.mkdir(parents=True)
    dangling_agent = agents_dir / "intent-reviewer.md"
    dangling_skill = skills_dir / "implement"
    dangling_agent.symlink_to(tmp_path / "missing-agent.md")
    dangling_skill.symlink_to(tmp_path / "missing-skill")

    setup = REPOSITORY_ROOT / "scripts/setup-opencode.sh"
    result = subprocess.run(
        [str(setup)],
        capture_output=True,
        check=True,
        env={**os.environ, "XDG_CONFIG_HOME": str(config_home)},
        text=True,
    )

    assert dangling_agent.is_symlink()
    assert dangling_agent.readlink() == tmp_path / "missing-agent.md"
    assert dangling_skill.is_symlink()
    assert dangling_skill.readlink() == tmp_path / "missing-skill"
    assert f"preserving existing OpenCode agent: {dangling_agent}" in result.stderr
    assert f"preserving existing OpenCode skill: {dangling_skill}" in result.stderr
