---
name: development-standards
description: Development standards covering root-cause fixes, project setup, framework selection, code quality, reproducible builds, testing, and code review. Apply when writing or reviewing code, setting up or configuring projects, or establishing build/test practices.
---

# Development Standards

## Fix the Problem, Not the Symptom

Workarounds hide problems, and hidden problems compound. Each workaround becomes a constraint that shapes future decisions until the codebase is a maze of special cases.

Signs you're treating symptoms: adding flags to skip code paths, orchestrating execution order to avoid conflicts, catching and suppressing errors, creating "temporary" fixes.

When a fix feels like it's fighting the code, the friction is signal. A real fix removes the condition that caused the problem.

## Project Setup

- Follow language-specific conventions for directory structure and project config (`pyproject.toml`, not `setup.py`, etc.)
- Configure appropriate linters for every file type
- Document the style guide being followed — consistency matters more than which one
- `.gitignore` must cover the language, build artifacts, editor files, and secrets
- Never commit secrets, credentials, or `.env` files

### Reproducible Builds

Same code, same binary. Pin all dependency versions, commit lock files, and document build steps in the README.

## Framework Selection

Choose based on what you're building, not how small it is now. The migration trap: starting with lightweight tools because "we don't need all that yet" creates debt when you inevitably do. If you can't articulate why this project will stay simple, assume it won't.

Signs you chose too light: building auth/routing/data layer from scratch, wiring 5+ libraries to do what a framework provides, greenfield rewrites of working features to accommodate growth.

## Code Quality

Code should read like the surrounding code: match its density, naming, and idiom.

### Size

If a function or file is too large to understand at a glance, investigate splitting it. Size limits are heuristics, not hard limits — if you exceed one and leave it, explain why.

### Self-documenting Code

Names should describe behavior. Code flow should read top-to-bottom. Comments earn their place when something is clever, looks wrong but shouldn't change, or encodes business logic that isn't obvious from the code.

Don't sacrifice clarity for brevity. If syntax hides what's happening, use plainer constructs.

## Testing

Tests are part of implementation, not a separate phase. A task is not complete until tests exist and pass. "Tests can be added later" is not acceptable.

### Unit Tests

All production code requires unit tests, written alongside the code. Coverage percentage is a useful proxy when code is structured for testability (small functions that do one thing) — treat a coverage gap as a prompt to look closer, not a target to chase for its own sake.

### Mocking

Mock external resources: time, network, filesystem, RNG. These are non-deterministic; a test that depends on them can't tell if your code is broken or the world didn't cooperate.

Don't mock modules. Use dependency injection instead. If you need to patch an import, that's a signal the code needs a seam for injection. A function that takes a `clock` parameter is testable without patching; one that calls `datetime.now()` internally requires test infrastructure to fight the language.

### Integration Tests

Focus on golden path first, add known edge cases next, let bugs drive expansion. Integration tests must be non-destructive: undo persistent state changes even on failure, and alert if changes can't be undone.

## Review

Code review is mandatory. Use a sub-agent with fresh context at critical points — the reviewer catches issues the implementer missed from being too close to the work.

## Decision Capture

Significant design decisions must be captured with rationale. Use lore-development skills (`/brainstorm`, `/specify`, `/retro`) to externalize decisions. Artifacts live in `.lore/`. The goal: when revisiting a decision later, the *why* is recoverable.