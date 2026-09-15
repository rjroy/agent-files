---
name: design
description: Use when the user has a specific architecture, tool, or technique in mind and wants to explore whether and how it applies. Not full-feature design but a focused technical investigation of one element. Triggers include "design this", "I want to use X for this", "how should this work technically", and "explore this approach".
---

# Design

The user has something specific in mind: an architecture, a tool, a technique. This skill explores it technically — whether it fits, how it would work, what the tradeoffs are. It can be a slice of a feature, not necessarily the whole thing.

End with a decision. A design without one is just research.

## Saving

Save to `.lore/work/design/[topic].md` using kebab-case. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields before writing.

Write the body Markdown-first per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML when topology or trade-offs need it — inline-SVG architecture or flow diagrams that beat prose, and side-by-side visual comparison of competing options.

After saving, invoke the `design-reviewer` subagent with the host's subagent capability in
`initial-review` mode on the saved design. If unavailable, dispatch the host's
general-purpose subagent with the role from `agents/design-reviewer.md`. If
findings are corrected, invoke `verification` mode with the complete unresolved
finding records and changed sections. After those findings close, run one
terminal broad acceptance review. Corrections from that review receive targeted
verification with their complete finding records; do not run another broad
review unless accepted scope changed.
