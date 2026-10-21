# Procedure index

Routing metadata only. Parent dispatchers with a known procedure ID can dispatch
directly to an appropriately scoped retained agent without loading this index;
parents needing routing help load it. Every receiving agent loads this index,
validates the caller-selected ID and the procedure task role against the
invocation, and resolves the file from the matching row's File column relative
to the index's directory. Task roles describe read-only review, bounded writing,
or bounded development; they are not agent identities. The parent selects a
retained agent whose assigned scope supports that task role. An ID supplied by
a parent does not bypass validation. Each ID maps to one file, required
invocation inputs, and dependent skills. Load only the selected procedure.

| Procedure ID | Task role | File | Required inputs | Dependent skills |
| --- | --- | --- | --- | --- |
| `design-reviewer` | read-only review | `procedures/design-reviewer.md` | design path; `initial-review` or `verification`; verification findings and changed sections | none |
| `intent-reviewer` | read-only review | `procedures/intent-reviewer.md` | intent path; `initial-review` or `verification`; verification findings and changed sections | none |
| `plan-reviewer` | read-only review | `procedures/plan-reviewer.md` | plan path; `initial-review` or `verification`; verification findings and changed sections | none |
| `music-engine-rowan-song-reviewer` | read-only review | `procedures/music-engine-rowan-song-reviewer.md` | song path; for a repeat review, prior findings and correction context | `music-engine-reference` |
| `story-engine-wyrd-story-reviewer` | read-only review | `procedures/story-engine-wyrd-story-reviewer.md` | one mode (`quality`, `continuity`, or `final-review`); story directory and mode-specific chapter/range/batch context | `story-engine-reference` (passive reference/path base only) |
| `bun-typescript-reviewer` | read-only review | `procedures/bun-typescript-reviewer.md` | current request; changed files/diff; relevant validation evidence; affected consumers/boundaries; `initial-review` or `verification` | none |
| `rust-daemon-cli-reviewer` | read-only review | `procedures/rust-daemon-cli-reviewer.md` | current request; changed files/diff; relevant validation evidence; affected consumers/boundaries; `initial-review` or `verification` | none |
| `music-engine-rowan-lyric-writer` | bounded writing | `procedures/music-engine-rowan-lyric-writer.md` | concept/song path and caller-authorized sample output scope | `music-engine-reference` |
| `story-engine-wyrd-prose-writer` | bounded writing | `procedures/story-engine-wyrd-prose-writer.md` | story directory; chapter number; caller-authorized sample output scope | `story-engine-reference` |
| `music-engine-rowan-production-designer` | bounded development | `procedures/music-engine-rowan-production-designer.md` | song path and caller-authorized sample output scope | `music-engine-reference` |
| `story-engine-wyrd-concept-developer` | bounded development | `procedures/story-engine-wyrd-concept-developer.md` | operation (`sampling` or `approved-concept-expansion`); sampling: user story input and authorized `concept-samples.md` path; expansion: selected approved concept, format, and explicitly authorized output paths | `story-engine-reference` |
| `story-engine-wyrd-character-builder` | bounded development | `procedures/story-engine-wyrd-character-builder.md` | story directory; one character name and role; caller-authorized character-sample output scope | `story-engine-reference` |
