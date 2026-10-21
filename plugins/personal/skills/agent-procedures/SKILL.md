---
name: agent-procedures
description: Load one explicitly selected agent procedure for a bounded invocation.
---

# Agent procedures

This skill serves both parent dispatchers and receiving agents, with
different loading duties. A parent that already knows the procedure ID may pass
it directly to an appropriately scoped retained agent without loading this
skill or the index.
A parent that needs help routing must load this skill and its index. A receiving
agent assigned a procedure always loads this skill and
`SKILL_BASE/references/index.md`, even when the parent already supplied a known
procedure ID. `SKILL_BASE` is the skill loader-provided canonical installed
directory. If the skill loader is unavailable, use the known home-anchored
installation at `/home/rjroy/.agents/plugins/personal/skills/agent-procedures`
as `SKILL_BASE`; do not substitute a caller path, process working directory,
global prompt symlink, lexical symlink path, or source-relative location. The
receiving agent checks that the caller-selected ID exists in the index,
then verifies that the procedure's task role matches the requested invocation
and is within the receiving agent's assigned scope. Task roles describe the
invocation, not agent identities: read-only review, bounded writing, and bounded
development are distinct roles that retained agents may perform according to
their assigned scope. Then resolve the procedure file from that row's File
column relative to `INDEX.parent`. The index is routing metadata, not a
workflow. Load only the selected procedure and the resources it requires, in
that order.

The caller envelope is `procedure`, `scope`, `request`, and `inputs`; include
`mode` only when the selected procedure defines it. Before loading a procedure,
stop and request clarification if the ID is unknown, its task role is not
appropriate for the assigned invocation, required input or authorization is absent, or the scope is
ambiguous. Never infer a procedure file path from its ID or a parent message.
Do not inspect unrelated procedures, choose a procedure automatically,
substitute a role, infer authorization, or recursively delegate. Treat sparse
creative material as input to gap-filling when the selected procedure allows it,
not as a dispatch failure.

Execute one bounded invocation. Follow the selected procedure's own required
inputs, clarification behavior, output contract, and write permissions. Writing
and development procedures may write only outputs explicitly bounded by the
caller and the procedure; those paths are prompt-level boundaries, not sandbox
guarantees. Development procedures here describe creative-domain work, not
software code implementation. A read-only review invocation is read-only even
when its receiving agent may write on other tasks: return only the selected
procedure's specified findings and output, and do not modify reviewed material.
Preserve the procedure's review mode, evidence standard, and fresh-context
requirements.
Parent agents retain user approval, selection, and canonical phase/state changes
unless the selected procedure explicitly authorizes a particular artifact.
