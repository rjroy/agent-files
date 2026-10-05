---
name: simplify
description: This skill should be used when the user wants to clean up code without changing behavior. Dispatches cleanup agents, runs tests to verify behavior is preserved, then runs code review. Triggers include "simplify this", "clean up this code", "refactor without changing behavior", "reduce complexity".
---

# Simplify

Orchestrate a bounded code cleanup through agent delegation. Preserve retained externally observable behavior; do not edit code directly.

## Input and scope

Accept any of these inputs:

- **No args:** First use an explicit work artifact identified by the invocation or current conversation. Otherwise, use an integration/target branch only when identified by authoritative repository metadata or user context; find its unique merge-base with `HEAD` and use that as the committed work boundary. Ask if the merge-base is ambiguous. An explicit work-base commit established by user context is itself the boundary. Distinguish the target branch from a tracking upstream: a feature branch's upstream may point to that same feature branch, making its merge-base `HEAD` and hiding committed work. Never infer the work boundary solely from a unique merge-base with `@{upstream}`. Also include relevant staged, unstaged, and untracked changes. If no reliable artifact, target branch, or explicit work base is known, ask the user for an artifact, Git base/range, or files. Never assume `HEAD`, the latest commit, or the whole repository, and never silently reduce the scope to dirty files.
- **Artifact:** A plan, design, spec, notes file, or other explicitly named work artifact. Use its scope, including committed manifests and replacement/deletion references, to identify the affected surface.
- **Git base/range:** Explicit user-specified refs are supported. Include committed changes in the named range and relevant pending changes. Resolve and inspect the range before dispatch.
- **File pattern or paths:** Preserve the existing file-pattern input. Resolve repo-relative paths against the repository root; notes paths remain valid resume inputs.

Before dispatch, report the resolved scope: source artifact or Git refs, included files (including deleted-file references), and relevant supporting code/tests. Follow replacement references to the retained file; do not recreate deleted files. Include supporting code and tests where needed to understand and protect behavior, but do not expand into unrelated files. Do not mutate commits or revert unrelated changes.

Simplify redundant implementation, obsolete unused scaffolding, duplicate tests, and incidental implementation assertions only within that scope. Retire behavior only when the source artifact explicitly approves the retirement; test count or apparent lack of use is not evidence that public behavior is obsolete. Keep every retained contract protected. Expand beyond the resolved surface only when necessary and authorized; avoid broad cleanup.

## Process

Only one agent may operate on target files at a time. Await cleanup before testing and testing before review. Testing and review agents are read-only and return findings rather than editing files.

**Cleanup.** Select a simplification agent from `.lore/lore-agents.md` when available; otherwise dispatch the host's general-purpose subagent. Give the role compact context: governing artifact, resolved scope, retained behavior, approved retirements, and validation criteria. Preserve retained contracts, not conflicting behavior explicitly retired by the artifact.

**Test.** Dispatch a testing agent with the same compact artifact/contract context, changed files, validation criteria, and how to run relevant tests. Test retained behavior and changed contracts proportionally; do not demand broad suites for a narrowly scoped cleanup. If tests fail, diagnose and route back to cleanup. After two failed attempts on the same issue, escalate to the user.

**Review.** Dispatch a review agent with the same compact artifact/contract context and files to review. Assess retained behavior against the governing artifact and validation criteria, honoring only its approved retirements. Give each finding a stable ID. Route findings back to cleanup, then request verification with complete unresolved finding records and the correction diff. Inspect the changed surface and report newly encountered material issues without reopening unrelated accepted surfaces. After two failed attempts on one finding or three total correction rounds, escalate to the user.

## Output

Record what happened in `.lore/work/notes/simplify-<identifier>.md`. Load `../../shared/frontmatter-schema.md` resolved from this skill's base directory for frontmatter fields and body-format requirements. Capture the resolved scope, files processed, what was simplified, and failures/resolutions.

## Escalation

Ask the user when scope cannot be reliably resolved, when a behavior change is detected rather than a cleanup regression, or when the correction-loop limit is reached.
