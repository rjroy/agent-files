"""Dependency-free content contracts for the progressive agent prompts."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins/personal/skills/agent-procedures"
INDEX = SKILL / "references/index.md"
PROCEDURES = SKILL / "references/procedures"
PROMPTS = ROOT / "omo-slim-agents"
ACTIVE_PROMPT_BODIES = {
    "reviewer", "code-reviewer", "writer", "developer",
    "lore-researcher", "modeler-sol", "modeler-astra",
}

ROLE_PROCEDURES = {
    "reviewer": [
        "design-reviewer", "intent-reviewer", "plan-reviewer",
        "music-engine-rowan-song-reviewer", "story-engine-wyrd-story-reviewer",
    ],
    "code-reviewer": ["bun-typescript-reviewer", "rust-daemon-cli-reviewer"],
    "writer": ["music-engine-rowan-lyric-writer", "story-engine-wyrd-prose-writer"],
    "developer": ["music-engine-rowan-production-designer",
                   "story-engine-wyrd-concept-developer",
                   "story-engine-wyrd-character-builder"],
}


class AgentProcedureContracts(unittest.TestCase):
    def test_index_maps_exactly_twelve_procedures_to_files_and_roles(self):
        text = INDEX.read_text()
        rows = re.findall(
            r"^\| `([^`]+)` \| ([^|]+) \| `([^`]+)` \| ([^|]+) \| ([^|]+) \|$",
            text, re.MULTILINE,
        )
        self.assertEqual(len(rows), 12)
        ids = [row[0] for row in rows]
        self.assertEqual(len(set(ids)), 12)
        self.assertEqual(set(ids), {p for group in ROLE_PROCEDURES.values() for p in group})
        self.assertEqual(set(PROCEDURES.glob("*.md")),
                         {PROCEDURES / f"{procedure}.md" for procedure in ids})
        for procedure, role, path, required, _skills in rows:
            self.assertIn(procedure, ROLE_PROCEDURES[role.strip()])
            self.assertEqual(path, f"procedures/{procedure}.md")
            self.assertTrue(required.strip())
            resolved_target = (INDEX.parent / path).resolve()
            self.assertTrue(resolved_target.is_file())
            self.assertEqual(resolved_target, (PROCEDURES / f"{procedure}.md").resolve())

    def test_index_paths_are_relative_and_not_registry_metadata(self):
        text = INDEX.read_text()
        self.assertNotRegex(text, r"(?:^|\s)/")
        self.assertNotIn("model:", text.lower())
        self.assertNotIn("permission", text.lower())
        self.assertNotIn("variant", text.lower())

    def test_four_dispatchers_are_short_and_generic(self):
        forbidden = {p for group in ROLE_PROCEDURES.values() for p in group}
        for role in ROLE_PROCEDURES:
            prompt = (PROMPTS / f"{role}.md").read_text()
            self.assertLessEqual(len(prompt.splitlines()), 20)
            self.assertIn("agent-procedures", prompt)
            self.assertFalse(any(proc in prompt for proc in forbidden))

    def test_root_prompt_directory_contains_only_the_seven_active_bodies(self):
        bodies = {
            path.stem for path in PROMPTS.glob("*.md")
            if path.name != "README.md"
        }
        self.assertEqual(bodies, ACTIVE_PROMPT_BODIES)
        for name in ACTIVE_PROMPT_BODIES:
            self.assertTrue((PROMPTS / f"{name}.md").is_file())

    def test_skill_advertises_only_generic_dispatch(self):
        skill = (SKILL / "SKILL.md").read_text()
        frontmatter = re.match(r"\A---\n(.*?)\n---", skill, re.DOTALL)
        self.assertIsNotNone(frontmatter)
        self.assertEqual(frontmatter.group(1).splitlines()[0], "name: agent-procedures")
        self.assertNotIn("design-reviewer", skill)

    def test_song_reviewer_invocation_is_not_a_mode_based_procedure(self):
        row = next(
            line for line in INDEX.read_text().splitlines()
            if "`music-engine-rowan-song-reviewer`" in line
        )
        self.assertIn("song path", row)
        self.assertIn("repeat review", row)
        self.assertIn("prior findings and correction context", row)
        self.assertNotIn("initial-review", row)
        self.assertNotIn("verification", row)

    def test_concept_procedure_has_two_scoped_operations(self):
        procedure = (PROCEDURES / "story-engine-wyrd-concept-developer.md").read_text()
        index_row = next(
            line for line in INDEX.read_text().splitlines()
            if "`story-engine-wyrd-concept-developer`" in line
        )
        self.assertRegex(index_row, r"\| developer \|")
        self.assertRegex(index_row, r"procedures/story-engine-wyrd-concept-developer\.md")
        self.assertIn("sampling", index_row)
        self.assertIn("approved-concept-expansion", index_row)

if __name__ == "__main__":
    unittest.main()
