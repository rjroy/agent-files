"""Content contracts for the retained music agents and consolidated skills."""

from pathlib import Path
import re


COLLECTION = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = COLLECTION.parents[1]
SLIM_PROMPTS = REPOSITORY_ROOT / "omo-slim-agents"


def read_agent(agent_id: str) -> str:
    path = SLIM_PROMPTS / f"music-engine-rowan-{agent_id}.md"
    assert path.is_file(), f"missing retained agent prompt: {path}"
    return path.read_text(encoding="utf-8")


def read_skill(skill: str) -> str:
    path = COLLECTION / "skills" / skill / "SKILL.md"
    assert path.is_file(), f"missing skill: {path}"
    return path.read_text(encoding="utf-8")


def test_only_retained_three_slim_prompts_remain() -> None:
    retained = {"lyric-writer", "production-designer", "song-reviewer"}
    for agent_id in retained:
        text = read_agent(agent_id)
        assert text.strip()
        assert not text.startswith("---\n")

    for removed in {
        "sampling-curator",
        "suno-formatter",
        "studio-prep",
        "cover-art-generator",
        "hook-art-generator",
    }:
        assert not (SLIM_PROMPTS / f"music-engine-rowan-{removed}.md").exists()


def test_retained_agents_reference_supported_skills_and_resources() -> None:
    lyric = read_agent("lyric-writer")
    production = read_agent("production-designer")
    reviewer = read_agent("song-reviewer")
    assert "theory-lyrical-craft.md" in lyric
    assert "music-write-lyrics" in lyric
    assert "theory-production-atmosphere.md" in production
    assert "music-write-lyrics" in production
    assert "music-suno-output" in reviewer

    for agent, resources in {
        "lyric-writer": ("theory-lyrical-craft.md",),
        "production-designer": ("theory-production-atmosphere.md", "theory-genre-reference.md"),
        "song-reviewer": ("theory-lyrical-craft.md", "theory-production-atmosphere.md"),
    }.items():
        prompt = read_agent(agent)
        for resource in resources:
            assert resource in prompt
            reference_base = COLLECTION / "skills" / "music-engine-reference"
            assert (reference_base / "music" / "theory" / resource).is_file()
            assert f"music/theory/{resource}" in prompt
            assert "installed directory of the loaded `music-engine-reference` skill" in prompt
            assert "../plugins/music-engine-rowan/skills/music-engine-reference" not in prompt


def test_suno_output_modes_preserve_boundaries_and_outputs() -> None:
    text = read_skill("music-suno-output")
    for term in ("Suno output mode", "studio mode", "studio-prep.md", "same directory", "200–400", "800–1000", "phase: complete"):
        assert term in text
    assert "Do not confuse preparing prompts with generating audio" in text
    assert "music-engine-reference/music/theory/theory-suno-formatting.md" in text


def test_artwork_modes_gate_rendering_and_preserve_prompt_only_skills() -> None:
    text = read_skill("music-artwork")
    for term in ("Image mode", "Video mode", "music-image-prompt", "music-video-prompt", "aspect-ratio", "cover-*.*", "image-prompt-samples-*.md", "video-prompt-samples-*.md"):
        assert term in text
    lower = text.casefold()
    for phrase in ("explicit approval", "ask before retrying", "prompt selection alone is not generation approval", "confirm which source image"):
        assert phrase in lower
    assert "images/base.md" in text
    assert "video/video-prompting-guide.md" in text


def test_parent_owns_confirmed_selection_and_cleanup() -> None:
    text = read_skill("music-write-lyrics")
    flows = (
        ("### Step 9: Select Lyrics", "### Step 10:", "lyrics-drafted", "full selected lyrics", "lyrics-samples.md"),
        ("### Step 11: Select Production", "### Step 12:", "production-designed", "full selected design", "production-samples.md"),
    )
    for start, end, phase, content_label, samples_file in flows:
        flow = text.split(start, 1)[1].split(end, 1)[0]
        assert "explicit user selection" in flow
        assert "let the user confirm or select another" in flow
        assert content_label in flow
        assert "cancel or defer" in flow
        assert "leave the song file, phase, and samples untouched" in flow

        phase_update = flow.index(f"phase: {phase}")
        verification = flow.index(f"Verify the destination contains the {content_label}, metadata, and updated phase")
        cleanup = flow.index(f"deleting `{samples_file}`")
        assert phase_update < verification < cleanup
        assert f"Never delete the samples before the complete content write and phase update are verified" in flow

    assert re.search(r"(?i)\b(?:re-run|rerun|auto-recommend via|spawn|delegate to)\b.{0,50}\bcurator\b", text) is None
    assert "music-engine-rowan-sampling-curator" not in text
    assert "music-suno-output" in text
    assert "music-artwork" in text


def test_pending_sample_resume_routes_to_selection_without_regeneration() -> None:
    text = read_skill("music-write-lyrics")
    routing = text.split("| Current phase | Existing pending sample file | Resume action |", 1)[1].split("\n\n", 1)[0]
    routes = [line.strip() for line in routing.splitlines() if line.strip().startswith("|") and "---" not in line]
    assert any("`concept-approved`" in line and "`lyrics-samples.md`" in line and "Step 9" in line and "do not spawn" in line for line in routes)
    assert any("`lyrics-drafted`" in line and "`production-samples.md`" in line and "Step 11" in line and "do not spawn" in line for line in routes)
    assert any("`concept-approved`" in line and "none" in line and "Generate lyric samples" in line for line in routes)
    assert any("`lyrics-drafted`" in line and "none" in line and "Generate production samples" in line for line in routes)

    for sample_file, step, next_step, agent in (
        ("lyrics-samples.md", "Step 8", "Step 9", "music-engine-rowan-lyric-writer"),
        ("production-samples.md", "Step 10", "Step 11", "music-engine-rowan-production-designer"),
    ):
        generation = text.split(f"### {step}:", 1)[1].split(f"### {next_step}:", 1)[0]
        assert f"`[song-directory]/{sample_file}` already exists" in generation
        assert f"resume at {next_step}" in generation
        assert "do not regenerate" in generation
        assert "only on the user's request" in generation
        assert "confirming that the existing samples may be replaced" in generation
        assert agent in generation


def test_phase_two_delegation_is_limited_to_retained_specialists() -> None:
    text = read_skill("music-write-lyrics")
    assert "NEVER execute Phase 2 yourself" not in text
    assert "Delegate only creative generation and review" in text
    assert "parent owns stage selection, sample selection, state transitions" in text
    assert "music-suno-output" in text


def test_song_reviewer_is_read_only_and_parent_owns_user_approved_edits() -> None:
    reviewer = read_agent("song-reviewer")
    lower = reviewer.casefold()
    parent = read_skill("music-write-lyrics")

    assert "read-only" in lower
    assert "return the full review report and proposed fixes to the parent" in lower
    assert "the parent presents findings, gets user direction" in lower
    assert "only the parent may apply fixes after the user requests them" in lower
    assert "only the parent" in lower and "phase: reviewed" in lower
    assert re.search(
        r"\*{0,2}changes made:\*{0,2}\s*none — reviewer is read-only", lower
    )
    assert "make edits directly to the song file" not in lower
    assert "update phase and confirm ready for formatting" not in lower
    assert "after any edits:" not in lower
    assert "make quick fixes" not in lower
    assert "proceed to the `music-suno-output` skill" not in lower
    assert "present findings and apply fixes only as requested" in parent


def test_prompt_only_skills_do_not_delegate_to_removed_curator() -> None:
    for skill in ("music-image-prompt", "music-video-prompt"):
        text = read_skill(skill)
        assert "music-engine-rowan-sampling-curator" not in text
        assert "prompt selection does not authorize" in text
