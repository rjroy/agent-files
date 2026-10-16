# Procedure index

Routing metadata only. Parent dispatchers with a known procedure ID can dispatch
directly to its role without loading this index; parents needing routing help
load it. Every receiving generic role agent loads this index, validates the
caller-selected ID and its own allowed role, and resolves the procedure file
from the matching row's File column relative to the index's directory. An ID
supplied by a parent does not bypass this check. Each ID maps to one file,
required invocation inputs, and dependent skills. Load only the selected
procedure.

| Procedure ID | Allowed role | File | Required inputs | Dependent skills |
| --- | --- | --- | --- | --- |
| `design-reviewer` | reviewer | `procedures/design-reviewer.md` | design path; `initial-review` or `verification`; verification findings and changed sections | none |
| `intent-reviewer` | reviewer | `procedures/intent-reviewer.md` | intent path; `initial-review` or `verification`; verification findings and changed sections | none |
| `plan-reviewer` | reviewer | `procedures/plan-reviewer.md` | plan path; `initial-review` or `verification`; verification findings and changed sections | none |
| `music-engine-rowan-song-reviewer` | reviewer | `procedures/music-engine-rowan-song-reviewer.md` | song path; for a repeat review, prior findings and correction context | `music-engine-reference` |
| `story-engine-wyrd-story-reviewer` | reviewer | `procedures/story-engine-wyrd-story-reviewer.md` | one mode (`quality`, `continuity`, or `final-review`); story directory and mode-specific chapter/range/batch context | `story-engine-reference` (passive reference/path base only) |
| `bun-typescript-reviewer` | code-reviewer | `procedures/bun-typescript-reviewer.md` | current request; changed files/diff; relevant validation evidence; affected consumers/boundaries; `initial-review` or `verification` | none |
| `rust-daemon-cli-reviewer` | code-reviewer | `procedures/rust-daemon-cli-reviewer.md` | current request; changed files/diff; relevant validation evidence; affected consumers/boundaries; `initial-review` or `verification` | none |
| `music-engine-rowan-lyric-writer` | writer | `procedures/music-engine-rowan-lyric-writer.md` | concept/song path and caller-authorized sample output scope | `music-engine-reference` |
| `story-engine-wyrd-prose-writer` | writer | `procedures/story-engine-wyrd-prose-writer.md` | story directory; chapter number; caller-authorized sample output scope | `story-engine-reference` |
| `music-engine-rowan-production-designer` | developer | `procedures/music-engine-rowan-production-designer.md` | song path and caller-authorized sample output scope | `music-engine-reference` |
| `story-engine-wyrd-concept-developer` | developer | `procedures/story-engine-wyrd-concept-developer.md` | operation (`sampling` or `approved-concept-expansion`); sampling: user story input and authorized `concept-samples.md` path; expansion: selected approved concept, format, and explicitly authorized output paths | `story-engine-reference` |
| `story-engine-wyrd-character-builder` | developer | `procedures/story-engine-wyrd-character-builder.md` | story directory; one character name and role; caller-authorized character-sample output scope | `story-engine-reference` |
