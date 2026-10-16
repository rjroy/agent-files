"""Dependency-free content checks for audio-analysis skill paths and scripts."""

import re
import unittest
from pathlib import Path


COLLECTION_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = COLLECTION_ROOT / "skills"


class SkillContentTests(unittest.TestCase):
    def assert_skill_paths_and_scripts(
        self, skill_name: str, family: str, expected_scripts: set[str], guide: str
    ) -> None:
        skill_path = SKILLS_ROOT / skill_name / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")

        self.assertIn("OpenCode skill loader", content)
        self.assertIn("canonical skill base", content)
        self.assertIn("two directories above", content)
        self.assertIn("rather than the process working directory", content)
        self.assertIn("OpenCode's shell tool", content)
        self.assertIn(
            f"reference/{guide}` relative to this loaded skill's canonical directory",
            content,
        )
        self.assertTrue((skill_path.parent / "reference" / guide).is_file())

        referenced_scripts = set(
            re.findall(
                rf"python3 <collection-root>/scripts/{family}/([\w-]+\.py)",
                content,
            )
        )
        self.assertEqual(referenced_scripts, expected_scripts)
        for script in expected_scripts:
            self.assertTrue(
                (COLLECTION_ROOT / "scripts" / family / script).is_file(), script
            )

    def test_audio_skill_uses_canonical_paths_for_all_eight_scripts(self) -> None:
        self.assert_skill_paths_and_scripts(
            "audio-analyzer",
            "audio",
            {
                "analyze_tempo.py",
                "analyze_key.py",
                "analyze_beats.py",
                "analyze_structure.py",
                "analyze_chroma.py",
                "generate_spectrogram.py",
                "analyze_hpss.py",
                "compare_audio.py",
            },
            "audio-script-guide.md",
        )

    def test_midi_skill_uses_canonical_paths_for_all_six_scripts(self) -> None:
        self.assert_skill_paths_and_scripts(
            "midi-analyzer",
            "midi",
            {
                "analyze_midi_key.py",
                "analyze_midi_chords.py",
                "analyze_midi_melody.py",
                "analyze_midi_rhythm.py",
                "analyze_midi_structure.py",
                "analyze_midi_metrics.py",
            },
            "midi-script-guide.md",
        )

    def test_skills_do_not_depend_on_client_specific_paths(self) -> None:
        for skill_name in ("audio-analyzer", "midi-analyzer"):
            with self.subTest(skill=skill_name):
                content = (SKILLS_ROOT / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertNotIn("CLAUDE_PLUGIN_ROOT", content)
                self.assertNotIn("Claude Code", content)


if __name__ == "__main__":
    unittest.main()
