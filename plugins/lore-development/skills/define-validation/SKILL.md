---
name: define-validation
description: Use to add validation criteria to a spec or plan. Triggers include "define validation", "how will we validate", "what should the AI check", and "add validation to this".
---

# Define Validation

Validation answers: "How will the AI know this is done?"

It must be behavioral and actionable — something the AI can actually run or observe, like "run the CLI with these args and confirm the output contains X." Not "verify the UX feels right." See "What counts" below for the range of forms this can take.

Add a validation section to an existing spec or plan. If none exists, save standalone to `.lore/work/validation/[topic].md`. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields before writing.

When saving standalone, write the body in Markdown per the "Body Format" section of `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`. Reach for embedded inline HTML only when a visual carries meaning prose can't, such as a diagram separating automated from manual steps.

## What counts

- Unit or integration tests
- CLI invocations with expected output
- Browser automation steps
- Manual steps the AI can follow and report on
- Lint and type checks when behavior depends on them

Structural assertions ("verify this function appears only once") don't count. If a regression must not recur, write a test that fails when the behavior regresses, not when lines move.
