"""Structural checks for migrated skills, metadata, and file references."""

from pathlib import Path
import re


COLLECTION = Path(__file__).resolve().parents[1]
SKILLS = COLLECTION / "skills"
REPOSITORY_ROOT = COLLECTION.parents[1]
PROCEDURES = (
    REPOSITORY_ROOT
    / "plugins/personal/skills/agent-procedures/references/procedures"
)
MIGRATIONS = {
    "write-story": "story-write-story",
    "review-story": "story-review-story",
    "plan-plot": "story-plan-plot",
    "develop-character": "story-develop-character",
}


def test_migrated_commands_have_skill_files_and_matching_metadata() -> None:
    for old_name, skill_name in MIGRATIONS.items():
        assert not (COLLECTION / "commands" / f"{old_name}.md").exists()
        skill = SKILLS / skill_name / "SKILL.md"
        assert skill.is_file()
        content = skill.read_text(encoding="utf-8")
        frontmatter = content.split("---", 2)[1]
        name = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
        description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        assert name is not None and name.group(1) == skill_name
        assert description is not None and len(description.group(1)) >= 30


def test_story_reference_paths_resolve_from_their_skills() -> None:
    for skill_name, relative_path in (
        ("story-plan-plot", "../story-engine-reference/story/theory/theory-narrative-structure.md"),
        ("story-develop-character", "../story-engine-reference/story/theory/theory-character-development.md"),
        ("story-write-story", "../../utils/agent-error-pattern.md"),
    ):
        content = (SKILLS / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert relative_path in content
        assert (SKILLS / skill_name / relative_path).is_file()


def test_story_dispatch_references_have_procedure_files() -> None:
    writer = (SKILLS / "story-write-story" / "SKILL.md").read_text(encoding="utf-8")
    for procedure in (
        "story-engine-wyrd-concept-developer",
        "story-engine-wyrd-character-builder",
        "story-engine-wyrd-prose-writer",
        "story-engine-wyrd-story-reviewer",
    ):
        assert f"procedure: {procedure}" in writer
        assert (PROCEDURES / f"{procedure}.md").is_file()


def test_chapter_frontmatter_fields_match_schema() -> None:
    schema = (COLLECTION / "docs" / "story-bible-schema.md").read_text(encoding="utf-8")
    selection = (SKILLS / "story-write-story" / "sample-selection.md").read_text(encoding="utf-8")
    chapter_schema = schema.split("### Chapter File Schema", 1)[1].split("### Verbalized Sampling Files", 1)[0]
    template_start = selection.index("### Selected chapter frontmatter")
    template_start = selection.index("```yaml", template_start) + len("```yaml")
    template_end = selection.index("```", template_start)
    template = selection[template_start:template_end]
    for field in (
        "chapter_number", "chapter_title", "word_count", "target_word_count",
        "generated", "quality_checked", "quality_review_status", "status",
    ):
        assert f"{field}:" in chapter_schema
        assert re.search(rf"^\s*{field}:", template, re.MULTILINE)
