"""Structural checks for active music procedures and referenced resources."""

from pathlib import Path


COLLECTION = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = COLLECTION.parents[1]
SLIM_PROMPTS = REPOSITORY_ROOT / "omo-slim-agents"
PROCEDURES = (
    REPOSITORY_ROOT
    / "plugins/personal/skills/agent-procedures/references/procedures"
)


def test_retained_procedures_and_generic_handlers_exist() -> None:
    for procedure in (
        "music-engine-rowan-lyric-writer",
        "music-engine-rowan-production-designer",
        "music-engine-rowan-song-reviewer",
    ):
        assert (PROCEDURES / f"{procedure}.md").is_file()

    for role in ("writer", "developer", "reviewer"):
        assert (SLIM_PROMPTS / f"{role}.md").is_file()


def test_music_reference_resources_exist() -> None:
    reference_base = COLLECTION / "skills" / "music-engine-reference"
    for resource in (
        "music/theory/theory-lyrical-craft.md",
        "music/theory/theory-production-atmosphere.md",
        "music/theory/theory-genre-reference.md",
        "music/theory/theory-suno-formatting.md",
    ):
        assert (reference_base / resource).is_file()


def test_active_music_skills_exist() -> None:
    for skill in (
        "music-write-lyrics",
        "music-suno-output",
        "music-artwork",
        "music-image-prompt",
        "music-video-prompt",
    ):
        assert (COLLECTION / "skills" / skill / "SKILL.md").is_file()
