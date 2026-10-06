---
name: migrate
description: Preview and, after explicit user confirmation, migrate pre-work and .lore/work lore layouts into historical intents, shared work, and gitignored local paths, converting legacy HTML artifacts to Markdown with original-byte backups. Does not migrate project files automatically.
---

# Migrate

Help a project transition legacy lore folders into the current storage layout without rewriting their history. This skill is optional; existing files remain readable if the user does not migrate them.

## Scope and safety

The helper is `scripts/migrate_lore.py`, resolved from this skill's installed plugin directory. It supports flat legacy directories directly under `.lore/` and equivalent legacy subdirectories under `.lore/work/`:

- `specs/**` → `.lore/work/intents/**` (legacy specs under `.lore/work/` use the same destination)
- `intents`, `brainstorm`, `design`, `research`, `retros`, `issues`, `ideas`, `validation`, `stubs`, `diagrams`, and `excavations` → matching `.lore/work/` directories
- `plans`, `tasks`, and `notes` → matching `.lore/local/` directories

Preserve nested names, file bytes, numbering, and historical status. Moved specs receive `legacy_source_type: spec`; their existing `status` remains a historical label, and validator support in `work/intents` does not approve or reactivate them. They remain historical context, not newly authored intents or binding requirements. Never add a new approval or alter old document bodies to make them look newly written.

Unmapped root directories/files are reported and left untouched; current `work/`, `reference/`, `learned/`, and `local/` trees are not flattened or moved. The helper moves regular files of any extension, so unsupported non-HTML formats are preserved rather than discarded. Migrating `.html`/`.htm` artifacts converts ordinary headings, paragraphs, lists, links, and code to Markdown and backs up the original bytes under `.lore/local/migration-backups/`. Tables, SVG/complex styled markup remain raw inline HTML where possible. Scripts/styles are preserved only as escaped, inert source and their runtime/rendering behavior is not preserved. Conversion warnings and backup destinations appear in preview; it is conservative, not a promise of complete fidelity. Destination and backup collisions block the entire migration.

The helper rewrites only resolvable Markdown/HTML links and known path-bearing frontmatter fields in `.lore/` documents. Legacy-spec `fg-sources` provenance follows moved specs; `fg-sources` entries for plans/tasks/notes are deliberately not repointed into reference provenance and are reported for field-guide reassessment. It reports external document references but does not edit them. Unresolved literal references must be reviewed; do not claim they were fixed. Local paths may be unavailable to collaborators.

## Workflow

1. Resolve the helper relative to this installed skill directory. Run `python3 <resolved-helper-path> <project-root>` for a no-write preview. The preview checks the complete move set for symlinks and collisions and lists reference updates, tracked-file actions, and unresolved references. It creates neither `.lore/local/` nor ignore rules.
2. Explain that moving to `.lore/local/` makes these artifacts machine-local/ignored and that existing users/collaborators may not have them. Ask the user whether to apply this exact preview.
3. Only after the user confirms, rerun with `--apply`. When moving local files, apply ensures `.lore/local/` is effectively Git-ignored before moving any file. If setup fails, stop without moving files.
4. If a local destination source is tracked, normal apply refuses. Explain the exact paths and ask separately whether to stage only their Git index removals. Only if explicitly approved rerun with `--apply --untrack`. The files remain in `.lore/local/`; this option never uses `git rm` on file data and does not stage unrelated changes. Dirty or staged changes to affected tracked sources are a blocker.
5. Report the resulting moves, rewritten references, unresolved references, and any tracked index removals. Ask the user to inspect Git status. Do not stage other changes or run the migration on repository artifacts without the user's explicit request.

The helper is idempotent: after a successful run, rerunning it reports no legacy files to move. A collision or unsafe symlink anywhere in the planned source/destination paths blocks the full migration before moves begin. Never work around a blocker by overwriting or deleting a destination.
