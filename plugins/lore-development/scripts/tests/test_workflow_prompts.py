"""Structural reference and setup behavior checks for lore-development."""

import json
import os
import re
import subprocess
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = PLUGIN_ROOT.parents[1]


def _read(relative_path: str) -> str:
    return (PLUGIN_ROOT / relative_path).read_text(encoding="utf-8")


def _read_procedure(name: str) -> str:
    return (
        REPOSITORY_ROOT
        / "plugins/personal/skills/agent-procedures/references/procedures"
        / f"{name}.md"
    ).read_text(encoding="utf-8")


def _run_setup(config_home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["node", str(REPOSITORY_ROOT / "scripts/setup-opencode.mjs"), *args],
        capture_output=True,
        check=True,
        env={**os.environ, "XDG_CONFIG_HOME": str(config_home)},
        text=True,
    )


def _assert_setup_links(config_dir: Path) -> None:
    instructions = config_dir / "AGENTS.md"
    slim_prompts = config_dir / "oh-my-opencode-slim"
    assert instructions.is_symlink()
    assert instructions.resolve() == REPOSITORY_ROOT / "COMMON.md"
    assert slim_prompts.is_symlink()
    assert slim_prompts.resolve() == REPOSITORY_ROOT / "omo-slim-agents"


def test_procedure_catalog_references_existing_procedure_files() -> None:
    index = " ".join(
        (REPOSITORY_ROOT / "plugins/personal/skills/agent-procedures/references/index.md")
        .read_text(encoding="utf-8")
        .split()
    )

    for procedure in (
        "design-reviewer",
        "intent-reviewer",
        "plan-reviewer",
        "bun-typescript-reviewer",
        "rust-daemon-cli-reviewer",
    ):
        assert f"{procedure}.md" in index
        assert _read_procedure(procedure).strip()


def test_readme_skill_table_matches_active_inventory_and_referenced_files() -> None:
    readme = _read("README.md")

    table = readme.split("## Skills", maxsplit=1)[1].split("## ", maxsplit=1)[0]
    listed_skills = set(re.findall(r"`/lore-development:([^`]+)`", table))
    active_skills = {
        path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")
    }
    assert listed_skills == active_skills
    assert "`/field-guide:stratify`" in readme
    assert (PLUGIN_ROOT.parent / "field-guide/skills/stratify/SKILL.md").is_file()

def test_retired_plan_breakdown_is_not_an_active_skill_or_implement_path(
    tmp_path: Path,
) -> None:
    skill_dir = PLUGIN_ROOT / "skills/plan-breakdown"

    assert not skill_dir.exists()

    # Setup adds repository skill roots to existing config; it does not install
    # individual skill links or restore removed skills from stale registrations.
    config_home = tmp_path / "config"
    config_dir = config_home / "opencode"
    skills_dir = config_home / "opencode/skills"
    skills_dir.mkdir(parents=True)
    (config_dir / "opencode.json").write_text(json.dumps({"skills": []}), encoding="utf-8")
    stale_registration = skills_dir / "plan-breakdown"
    stale_registration.symlink_to(tmp_path / "missing-plan-breakdown")
    _run_setup(config_home, "--apply")

    assert stale_registration.is_symlink()
    assert not stale_registration.exists()
    _assert_setup_links(config_dir)


def test_active_claude_setup_packaging_is_removed() -> None:
    assert not (REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json").exists()
    assert not (REPOSITORY_ROOT / ".claude" / "settings.json").exists()
    assert not (REPOSITORY_ROOT / ".claude" / "settings.local.json").exists()
    assert not (REPOSITORY_ROOT / "scripts" / "setup-claude.sh").exists()
    for collection in (
        "lore-development",
        "judgment-engine-virelan",
        "music-engine-rowan",
        "story-engine-wyrd",
    ):
        assert not (PLUGIN_ROOT.parent / collection / ".claude-plugin" / "plugin.json").exists()


def test_setup_creates_only_shared_links_without_legacy_definition_installs(
    tmp_path: Path,
) -> None:
    config_home = tmp_path / "config"
    config_dir = config_home / "opencode"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "opencode.json"
    config_file.write_text(json.dumps({"skills": []}), encoding="utf-8")

    conflicting_agent = config_home / "opencode/agents/intent-reviewer.md"
    conflicting_agent.parent.mkdir(parents=True)
    conflicting_agent.write_text("user-owned\n", encoding="utf-8")
    conflicting_command = config_dir / "commands/init.md"
    conflicting_command.parent.mkdir(parents=True)
    conflicting_command.write_text("user-owned command\n", encoding="utf-8")

    _run_setup(config_home, "--apply")
    applied_config = config_file.read_bytes()
    _run_setup(config_home, "--apply")

    assert sorted(path.name for path in (config_dir / "agents").iterdir()) == ["intent-reviewer.md"]
    assert conflicting_agent.read_text(encoding="utf-8") == "user-owned\n"
    assert conflicting_command.read_text(encoding="utf-8") == "user-owned command\n"
    assert [path.name for path in (config_dir / "commands").iterdir()] == ["init.md"]
    assert not (config_dir / "skills").exists()
    assert config_file.read_bytes() == applied_config
    assert isinstance(json.loads(applied_config)["skills"], list)
    _assert_setup_links(config_dir)


def test_setup_preserves_skill_array_and_user_command_collision(
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

    _run_setup(config_home, "--apply")

    config = json.loads(config_file.read_text(encoding="utf-8"))
    assert isinstance(config["skills"], list)
    assert config["skills"][: len(skills)] == skills
    assert conflicting_command.read_text(encoding="utf-8") == "user-owned\n"
    assert sorted(path.name for path in (config_dir / "commands").iterdir()) == ["init.md"]
    assert not (config_dir / "skills").exists()
    _assert_setup_links(config_dir)


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

    (config_dir / "opencode.json").write_text(json.dumps({"skills": []}), encoding="utf-8")
    _run_setup(config_home, "--apply")

    assert dangling_agent.is_symlink()
    assert dangling_agent.readlink() == tmp_path / "missing-agent.md"
    assert dangling_skill.is_symlink()
    assert dangling_skill.readlink() == tmp_path / "missing-skill"
    _assert_setup_links(config_dir)
