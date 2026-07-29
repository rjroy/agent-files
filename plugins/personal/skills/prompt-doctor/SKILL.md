---
name: prompt-doctor
description: Audits and converts skills, agents, and CLAUDE.md files to the newer context-engineering paradigm for Claude 5 generation models — trading hard-coded rules for model judgment, examples for well-designed interfaces, upfront bulk for progressive disclosure, and CLAUDE.md-as-memory for auto-memory. Use when asked to "run prompt doctor", "modernize this skill/agent/CLAUDE.md", "reduce over-constraint", or "apply the new context engineering rules".
---

# Prompt Doctor

Audits context files (SKILL.md, agent definitions, CLAUDE.md) against six lenses and proposes edits. It reports and confirms — it does not silently rewrite.

Full lens definitions with before/after examples: `reference/lenses.md`. Load it before producing findings.

## Workflow

1. **Scope.** Confirm which file(s) are in play: a single named file, or every skill/agent/CLAUDE.md under a directory. Read each one in full before judging it — never propose changes to a file you haven't read.
2. **Load the lenses.** Read `reference/lenses.md`.
3. **Audit each file against all six lenses.** For every hit, note: the passage, which lens it trips, and a concrete rewrite (not just "consider softening this").
4. **Triage before proposing.** Not every rule is a myth. Keep as-is anything that guards an irreversible or destructive action (data loss, force-push, credential exposure, `sudo`, deleting user work), or that encodes a team/product-specific gotcha the model can't derive from the surrounding files. The paradigm shift targets hedges and repetition, not safety rails — see "What stays" in the reference file before flagging anything as removable.
5. **Report findings grouped by lens**, each with the passage, the rewrite, and one line on why. Skip lenses with no hits rather than padding the report.
6. **Apply only on confirmation.** Architecture/pattern changes to CLAUDE.md and skills fall under "ask first" — get explicit sign-off per file (or per batch) before editing. Editing >2 files still means editing, not creating new ones; keep existing file structure unless the user asks to reorganize it.
7. **Verify.** After edits, re-read the changed file and confirm nothing load-bearing (the "what stays" category) got cut alongside the hedges.
