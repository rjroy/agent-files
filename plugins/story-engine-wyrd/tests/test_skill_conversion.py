"""Narrow contract checks for the command-to-skill prompt migration."""

from pathlib import Path
import re


COLLECTION = Path(__file__).resolve().parents[1]
SKILLS = COLLECTION / "skills"
REPOSITORY_ROOT = COLLECTION.parents[1]
SLIM_PROMPTS = REPOSITORY_ROOT / "omo-slim-agents"
MIGRATIONS = {
    "write-story": "story-write-story",
    "review-story": "story-review-story",
    "plan-plot": "story-plan-plot",
    "develop-character": "story-develop-character",
}


def test_old_commands_are_replaced_by_discoverable_skills() -> None:
    for old_name, skill_name in MIGRATIONS.items():
        assert not (COLLECTION / "commands" / f"{old_name}.md").exists()
        prompt = SKILLS / skill_name / "SKILL.md"
        assert prompt.is_file()
        content = prompt.read_text(encoding="utf-8")
        frontmatter = content.split("---", 2)[1]
        name = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
        description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        assert name is not None and name.group(1) == skill_name
        assert description is not None and len(description.group(1)) >= 30
        assert "Conversational use" in content


def test_story_creation_preserves_approval_and_resume_contract() -> None:
    content = (SKILLS / "story-write-story" / "SKILL.md").read_text(encoding="utf-8")
    for contract in (
        "wait for the user's explicit choice",
        "Present Plan for User Approval",
        "[Yes - Proceed] [No - Revise] [Cancel]",
        "Resume Workflow",
        "metadata.json",
        "chapter_generation",
    ):
        assert contract in content
    assert "story-engine-wyrd-story-reviewer" in content
    assert "story-engine-wyrd-concept-developer" in content
    assert "Please resume .story-state/example/PLAN.md" in content
    assert content.index("explicit continuation or resume intent") < content.index("File Reference")


def test_story_reference_paths_are_skill_relative() -> None:
    for skill_name, relative_path in (
        ("story-plan-plot", "../story-engine-reference/story/theory/theory-narrative-structure.md"),
        ("story-develop-character", "../story-engine-reference/story/theory/theory-character-development.md"),
        ("story-write-story", "../../utils/agent-error-pattern.md"),
    ):
        content = (SKILLS / skill_name / "SKILL.md").read_text(encoding="utf-8")
        assert relative_path in content
        assert (SKILLS / skill_name / relative_path).is_file()


def test_review_skill_remains_informational_and_read_only() -> None:
    content = (SKILLS / "story-review-story" / "SKILL.md").read_text(encoding="utf-8")
    assert "informational only" in content.lower()
    assert "never blocks" in content.lower()
    assert "No modification to story bible files" in content


def test_story_slim_prompts_and_referenced_resources_are_relocated() -> None:
    agent_ids = (
        "story-engine-wyrd-prose-writer",
        "story-engine-wyrd-concept-developer",
        "story-engine-wyrd-character-builder",
        "story-engine-wyrd-story-reviewer",
    )
    for agent_id in agent_ids:
        source = COLLECTION / "agents" / f"{agent_id.removeprefix('story-engine-wyrd-')}.md"
        prompt = SLIM_PROMPTS / f"{agent_id}.md"
        assert not source.exists()
        assert prompt.is_file()
        content = prompt.read_text(encoding="utf-8")
        assert content.strip()
        assert not content.startswith("---\n")

    prompts = {
        "story-engine-wyrd-concept-developer": (
            "story/theory/theory-narrative-structure.md",
            "../../docs/story-bible-schema.md",
            "../../utils/agent-error-pattern.md",
        ),
        "story-engine-wyrd-character-builder": (
            "story/theory/theory-character-development.md",
            "../../utils/agent-error-pattern.md",
        ),
        "story-engine-wyrd-prose-writer": (
            "story/theory/theory-prose-craft.md",
            "../../utils/agent-error-pattern.md",
        ),
    }
    for agent_id, resources in prompts.items():
        content = (SLIM_PROMPTS / f"{agent_id}.md").read_text(encoding="utf-8")
        assert "loader-provided canonical installed directory as `REFERENCE_BASE`" in content
        assert "lexical symlink path" in content
        assert "current working directory" in content
        assert "../plugins/story-engine-wyrd" not in content
        for resource in resources:
            assert f"REFERENCE_BASE/{resource}" in content

    reference_base = SKILLS / "story-engine-reference"
    for resource in ("story/theory/theory-narrative-structure.md", "story/theory/theory-character-development.md", "story/theory/theory-prose-craft.md"):
        assert (reference_base / resource).is_file()
    for resource in ("docs/story-bible-schema.md", "utils/agent-error-pattern.md"):
        assert (COLLECTION / resource).is_file()

    character = (SLIM_PROMPTS / "story-engine-wyrd-character-builder.md").read_text(encoding="utf-8")
    prose = (SLIM_PROMPTS / "story-engine-wyrd-prose-writer.md").read_text(encoding="utf-8")
    for prompt in (character, prose):
        assert "REFERENCE_BASE/../story-write-story/sample-selection.md" in prompt
    assert (reference_base / "../story-write-story/sample-selection.md").is_file()
    for removed_id in (
        "story-engine-wyrd-sampling-curator",
        "story-engine-wyrd-quality-checker",
        "story-engine-wyrd-continuity-validator",
        "story-engine-wyrd-final-review",
    ):
        assert not (SLIM_PROMPTS / f"{removed_id}.md").exists()


def test_story_reviewer_modes_load_independent_read_only_procedures() -> None:
    reviewer = (SLIM_PROMPTS / "story-engine-wyrd-story-reviewer.md").read_text(encoding="utf-8")
    procedures = {
        "quality": "REFERENCE_BASE/../story-review-story/references/quality-review.md",
        "continuity": "REFERENCE_BASE/../story-review-story/references/continuity-review.md",
        "final-review": "REFERENCE_BASE/../story-review-story/references/final-review.md",
    }
    for mode, resource in procedures.items():
        assert f"`{mode}`" in reviewer
        assert resource in reviewer
        relative_resource = resource.removeprefix("REFERENCE_BASE/")
        assert (SKILLS / "story-engine-reference" / relative_resource).is_file()
    assert "read-only" in reviewer.lower()
    assert "Do not update frontmatter or `metadata.json`" in reviewer
    assert "separate fresh invocation" in reviewer
    assert "passive `story-engine-reference` skill" in reviewer
    assert "loader-provided canonical installed directory as `REFERENCE_BASE`" in reviewer
    assert "Load the `story-review-story` skill" not in reviewer
    assert "lexical symlink path" in reviewer
    assert "../plugins/story-engine-wyrd" not in reviewer

    readme = (COLLECTION / "README.md").read_text(encoding="utf-8")
    for agent_id in (
        "story-engine-wyrd-concept-developer",
        "story-engine-wyrd-character-builder",
        "story-engine-wyrd-prose-writer",
        "story-engine-wyrd-story-reviewer",
    ):
        assert agent_id in readme
    assert "Sampling Curator" not in readme
    assert "Quality Checker" not in readme
    assert "Continuity Validator" not in readme

    writer = (SKILLS / "story-write-story" / "SKILL.md").read_text(encoding="utf-8")
    selection = SKILLS / "story-write-story" / "sample-selection.md"
    assert selection.is_file()
    assert "sample-selection.md" in writer
    assert "concept" in selection.read_text(encoding="utf-8").lower()
    assert "character" in selection.read_text(encoding="utf-8").lower()
    selection_text = selection.read_text(encoding="utf-8")
    assert re.search(r"highest[-\s]probability candidate", selection_text)
    phase_rules = selection_text.split("## Choose by phase", 1)[1].split("For interactive choices", 1)[0]
    assert "Concept" in phase_rules and "Never choose automatically" in phase_rules
    assert "Character" in phase_rules and "Never choose automatically" in phase_rules
    assert "Prose" in phase_rules and "without prompting by default" in phase_rules
    assert "Only after a successful chosen-content write" in selection_text
    for mode in procedures:
        assert f"Mode: {mode}" in writer
    assert "sequentially" in writer
    assert "contiguous batches of 3-5 chapters sequentially" in writer
    assert "recover the latest carry-forward notes" in writer
    assert "final-review-notes.md" in writer


def test_selected_chapters_follow_schema_and_review_results_never_fake_passes() -> None:
    schema = (COLLECTION / "docs" / "story-bible-schema.md").read_text(encoding="utf-8")
    selection = (SKILLS / "story-write-story" / "sample-selection.md").read_text(encoding="utf-8")
    selection_text = selection
    writer = (SKILLS / "story-write-story" / "SKILL.md").read_text(encoding="utf-8")

    chapter_schema = schema.split("### Chapter File Schema", 1)[1].split("### Verbalized Sampling Files", 1)[0]
    required_chapter_fields = (
        "chapter_number",
        "chapter_title",
        "word_count",
        "target_word_count",
        "generated",
        "quality_checked",
        "quality_review_status",
        "status",
    )
    for field in required_chapter_fields:
        assert f"{field}:" in chapter_schema
        assert f"{field}:" in selection

    character_schema = schema.split("### Character File Schema", 1)[1].split("### metadata.json Schema", 1)[0]
    for field in ("name", "role", "created", "last_updated"):
        assert f"{field}:" in character_schema
        assert f"{field}" in selection
    character_template_start = selection_text.index("### Selected character frontmatter")
    character_template_start = selection_text.index("```yaml", character_template_start) + len("```yaml")
    character_template_end = selection_text.index("```", character_template_start)
    character_template = selection_text[character_template_start:character_template_end]
    for field in ("name", "role", "created", "last_updated"):
        assert re.search(rf"^\s*{field}:", character_template, re.MULTILINE)

    assert "load `../../docs/story-bible-schema.md`" in selection
    assert "complete selected candidate body" in selection
    assert "Do not summarize, truncate, or rewrite" in selection
    assert "quality_checked: false" in selection
    assert "quality_review_status: pending" in selection
    chapter_template_start = selection_text.index("### Selected chapter frontmatter")
    chapter_template_start = selection_text.index("```yaml", chapter_template_start) + len("```yaml")
    chapter_template_end = selection_text.index("```", chapter_template_start)
    chapter_template = selection_text[chapter_template_start:chapter_template_end]
    for field in required_chapter_fields:
        assert re.search(rf"^\s*{field}:", chapter_template, re.MULTILINE)
    assert re.search(r"^quality_checked:\s*false\s*$", chapter_template, re.MULTILINE)
    assert re.search(r"^quality_review_status:\s*pending\s*$", chapter_template, re.MULTILINE)

    assert 'quality_checked: true`, `quality_review_status: "passed"' in writer
    assert 'quality_checked: false`, `quality_review_status: "revision_needed"`' in writer
    assert 'quality_review_status: "accepted_with_issues"' in writer
    assert "Never convert the reviewer result to PASS" in writer
    assert 'status: "needs_revision"' in writer
    assert 'status: "accepted_with_issues"' in writer
    assert "Never record an accepted or failed checkpoint as `passed`" in writer
    quality_acceptance = writer.split("**User accepts a failed review as-is**", 1)[1].split("**Error Handling**", 1)[0]
    assert 'quality_checked` remains `false`' in quality_acceptance
    assert '`quality_review_status: "accepted_with_issues"`' in quality_acceptance
    assert '`status: "complete"`' in quality_acceptance
    assert "retain the issue count and failure details" in quality_acceptance
    assert "explicit acceptance" in quality_acceptance
    assert "only when its quality failure is the sole unresolved cause" in quality_acceptance
    assert "preserve its incomplete marker if another cause remains" in quality_acceptance
    assert "never clear unrelated incomplete entries" in quality_acceptance
    assert "Increment `completed_chapters` only after quality findings were passed or explicitly accepted" in writer
    assert '"status": "accepted_with_issues"' in schema
    assert '"needs_revision"' in schema
    assert 'quality_review_status: "pending"' in schema or 'quality_review_status: "passed"' in schema


def test_continuity_explicit_range_overrides_checkpoint_history() -> None:
    procedure = (SKILLS / "story-review-story" / "references" / "continuity-review.md").read_text(encoding="utf-8")
    scope_rules = procedure.split("### Step 1: Determine Validation Scope", 1)[1].split("### Step 2:", 1)[0]
    assert re.search(
        r"If the caller supplied a range.{0,200}exact start and end for every read, search, report heading, and finding",
        scope_rules,
        re.DOTALL,
    )
    assert re.search(r"Do not narrow it by `continuity_checkpoints`", scope_rules)
    assert "12 completed chapters and a checkpoint at 12, an explicit on-demand request for chapters 1–12 still reviews chapters 1–12" in procedure
    assert re.search(
        r"automatic checkpoint and no range was supplied.{0,180}last automatic checkpoint",
        scope_rules,
        re.DOTALL,
    )

    on_demand = (SKILLS / "story-review-story" / "SKILL.md").read_text(encoding="utf-8")
    assert "story-engine-wyrd-story-reviewer" in on_demand
    assert "continuity mode" in on_demand
    assert "informational" in on_demand.lower()
