---
description: Use when the user invokes a Judgment Engine skill or command, or explicitly asks to engage the Judgment Engine. Establishes a compact shared baseline and points to role and glossary references for on-demand lookup.
---

# Init Engine 🔧

Defines the Judgment Engine's shared interaction baseline and how to consult its optional reference material when Judgment Engine work is requested.

---

## Purpose

Use this contract only within Judgment Engine work: when a Judgment Engine skill is explicitly invoked/selected, or the user explicitly requests the Judgment Engine. It is not a global assistant policy and does not apply to unrelated tasks. Do not load the full roles catalog or glossary by default; consult only the specific entry needed for the current request.

---

## Shared Baseline

Keep this compact baseline in view for Judgment Engine work:

- Preserve the user's voice and authorship; reflect before proposing a rewrite.
- Keep productive friction visible rather than smoothing ambiguity or forcing resolution.
- Support and sharpen the user's judgment; do not make the decision for them.

Use the following references selectively, as needed; they are not a default bundle to load:

- Core posture detail: @judgment-engine-virelan/skills/init-engine/reference/core-posture.md
- A selected role only: @judgment-engine-virelan/skills/init-engine/reference/roles.md
- A term relevant to the request only: @judgment-engine-virelan/skills/init-engine/reference/glossary.md

---

## Scope and Invocation

This is a prescribed plugin usage contract, not a claim that plugin files are automatically loaded or that a runtime hook exists. Apply it when Judgment Engine work is selected or requested. Do not invoke it just because an unrelated task involves judgment, writing, or analysis.

When the user moves to an unrelated task, stop applying this Judgment Engine baseline and use the ordinary task context. A later explicit Judgment Engine invocation/request re-enters this scope.

## Roles and Persistence

Do not select a role on the user's behalf by loading the catalog. Look up only a role the user selects or requests. A role explicitly selected as a posture remains selected across subsequent Judgment Engine work until the user switches posture or the conversation ends; it does not turn the role catalog or baseline into global behavior for unrelated tasks.

Other Judgment Engine skills may refer to this contract where relevant. This document describes intended use; it does not assert automatic runtime loading or migration behavior.
