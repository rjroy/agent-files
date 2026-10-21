"""Dependency-free content contracts for the progressive agent prompts."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins/personal/skills/agent-procedures"
INDEX = SKILL / "references/index.md"
PROCEDURES = SKILL / "references/procedures"

TASK_ROLE_PROCEDURES = {
    "read-only review": [
        "design-reviewer", "intent-reviewer", "plan-reviewer",
        "music-engine-rowan-song-reviewer", "story-engine-wyrd-story-reviewer",
        "bun-typescript-reviewer", "rust-daemon-cli-reviewer",
    ],
    "bounded writing": [
        "music-engine-rowan-lyric-writer", "story-engine-wyrd-prose-writer",
    ],
    "bounded development": [
        "music-engine-rowan-production-designer",
        "story-engine-wyrd-concept-developer",
        "story-engine-wyrd-character-builder",
    ],
}


class AgentProcedureContracts(unittest.TestCase):
    def test_index_maps_procedures_to_canonical_files_and_task_roles(self):
        text = INDEX.read_text()
        rows = re.findall(
            r"^\| `([^`]+)` \| ([^|]+) \| `([^`]+)` \| ([^|]+) \| ([^|]+) \|$",
            text, re.MULTILINE,
        )
        self.assertTrue(rows)
        ids = [row[0] for row in rows]
        self.assertEqual(len(set(ids)), len(ids))
        self.assertEqual(set(ids), {p for group in TASK_ROLE_PROCEDURES.values() for p in group})
        self.assertEqual(set(PROCEDURES.glob("*.md")),
                         {PROCEDURES / f"{procedure}.md" for procedure in ids})
        for procedure, role, path, required, _skills in rows:
            self.assertIn(procedure, TASK_ROLE_PROCEDURES[role.strip()])
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

    def test_skill_advertises_only_generic_dispatch(self):
        skill = (SKILL / "SKILL.md").read_text()
        frontmatter = re.match(r"\A---\n(.*?)\n---", skill, re.DOTALL)
        self.assertIsNotNone(frontmatter)
        self.assertEqual(frontmatter.group(1).splitlines()[0], "name: agent-procedures")

if __name__ == "__main__":
    unittest.main()
