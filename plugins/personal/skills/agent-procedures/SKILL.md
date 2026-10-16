---
name: agent-procedures
description: Load one explicitly selected agent procedure for a bounded invocation.
---

# Agent procedures

This skill serves both parent dispatchers and receiving role agents, with
different loading duties. A parent that already knows the procedure ID may pass
it directly to the matching role agent without loading this skill or the index.
A parent that needs help routing must load this skill and its index. A receiving
generic role agent always loads this skill and
`SKILL_BASE/references/index.md`, even when the parent already supplied a known
procedure ID. `SKILL_BASE` is the loader-provided canonical installed directory;
do not use a caller-supplied path, process working directory, global prompt
symlink, or lexical symlink path as the base. The receiving agent validates that
the ID exists in the index and its allowed role matches, then resolves the
procedure file from the row's File column relative to `INDEX.parent`. The index
is routing metadata, not a workflow. Load only the selected procedure and the
resources that procedure requires, in that order.

The caller envelope is `procedure`, `scope`, `request`, and `inputs`; `mode` is
included only when defined by the selected procedure. Before loading a procedure,
stop and request clarification if the ID is unknown in the index, its allowed
role does not match yours, required input or authorization is absent, or the
scope is ambiguous. Never infer a procedure file path from its ID or a parent
message. Do not inspect unrelated procedures, choose a procedure automatically,
substitute a role, infer authorization, or recursively delegate. Treat sparse
creative material as input to gap-filling when the selected procedure allows it,
not as a dispatch failure.

Execute one bounded invocation. Follow the selected procedure's own required
inputs, clarification behavior, output contract, and write permissions. Writers
and developers may write only outputs explicitly bounded by the caller and the
procedure; those paths are prompt-level boundaries, not sandbox guarantees.
Parent agents retain user approval, selection, and canonical phase/state changes
unless the selected procedure explicitly authorizes a particular artifact.
