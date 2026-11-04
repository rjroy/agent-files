"""Discoverability contracts for the engineering-quality review skill."""

import re
from pathlib import Path

import yaml

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SKILL_NAME = "engineering-quality-review"


def test_skill_metadata_matches_discoverable_directory() -> None:
    skill_path = PLUGIN_ROOT / "skills" / SKILL_NAME / "SKILL.md"
    document = skill_path.read_text(encoding="utf-8")
    opening, metadata, body = document.split("---", maxsplit=2)
    assert not opening.strip()
    frontmatter = yaml.safe_load(metadata)
    assert frontmatter["name"] == skill_path.parent.name
    assert isinstance(frontmatter["description"], str)
    assert frontmatter["description"].strip()
    assert body.strip()


def test_readme_skill_inventory_resolves_to_active_skills() -> None:
    readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    table = readme.split("## Skills", maxsplit=1)[1].split("## ", maxsplit=1)[0]
    listed = re.findall(r"`/lore-development:([^`]+)`", table)
    active = {path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")}
    assert len(listed) == len(set(listed))
    assert set(listed) == active
    assert SKILL_NAME in listed


def test_implement_resolves_quality_skill_from_installed_skill_directory() -> None:
    implement_dir = PLUGIN_ROOT / "skills" / "implement"
    document = (implement_dir / "SKILL.md").read_text(encoding="utf-8")
    references = re.findall(r"`(\.\./[^`]+/SKILL\.md)`", document)
    resolved = {(implement_dir / reference).resolve() for reference in references}
    assert (PLUGIN_ROOT / "skills" / SKILL_NAME / "SKILL.md").resolve() in resolved
    assert all(path.is_file() for path in resolved)
