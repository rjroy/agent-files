---
title: Native bounded-delegation inventory and no-change decision
date: 2026-09-11
status: active
tags: [workflow, delegation, retries, acceptance, safety, evidence]
related: [workflow-comparison-review.md, workflow-comparison-baseline-evidence.md, workflow-comparison-opportunity-risk-register.md, ../design/native-admission-recovery-handoff.md]
---

# Native bounded-delegation inventory and no-change decision

## Decision

**No native bounded-parallel dispatch or partial-success mechanism should be
designed or added now.** The current workflow is deliberately phase-serial and
has one writer at a time. It already requires role-separated testing and review,
bounded correction, phase evidence, terminal independent acceptance, and an
accepted changed-state manifest. The installed router source separately contains
a conditional, verified delegation path with bounded attempts, honest unmet
results, session cleanup, acceptance gates, resumed-dispatch tracking, changed
file attribution, and subagent tool guards. Neither source demonstrates an
unmet, independent-parallel work unit nor a loaded and effective router path.

This is a source-only finding. It does not configure, invoke, or trial OpenCode
delegation, and does not import Teamsters or any marketplace execution layer.
It preserves Beads as task/dependency authority, Git as source authority, and
independent review as the acceptance boundary.

## Current workflow inventory

| Concern | Current source-backed mechanism | Boundary and conclusion |
| --- | --- | --- |
| Ownership | `implement` assigns implementation, testing, and review roles; only one agent may operate on a phase's files at once, while testing and review are read-only ([implement](../../../plugins/lore-development/skills/implement/SKILL.md), Execute Phases). | This intentionally prevents concurrent writers inside a phase. No evidence identifies independent, artifact-disjoint children that need a new coordinator. |
| Retry and partial result | Failed checks return to implementation; only failed checks are re-run; two failed attempts on one finding or three correction rounds require escalation ([implement](../../../plugins/lore-development/skills/implement/SKILL.md), Execute Phases and Escalation). | The source has bounded correction and honest escalation, but no aggregation contract for child partial success. That is not a demonstrated gap while work remains serial. |
| Acceptance | Each phase has mapped validation and review; after local gates, one terminal acceptance review reconciles all obligations ([implement](../../../plugins/lore-development/skills/implement/SKILL.md), Initialize, Execute Phases, Validate). | A child saying it is complete is insufficient. This remains the acceptance boundary. |
| Resumption and changed state | Notes carry phase progress, evidence, failures, and decisions; work reported already done must still be validated. After terminal acceptance, the manifest records porcelain status, index identity, and working-tree hash; later commits require manifest equality ([implement](../../../plugins/lore-development/skills/implement/SKILL.md), Output, Execute Phases, Validate, Finalize). | This protects accepted state and detects a later delta. It does not establish a universal pre-write idempotency rule, so a later concurrent/resume proposal must supply one without creating another task-state authority. |
| Task state and handoff | Beads owns issue status, ownership, dependencies, and blockers; Git owns source state; notes own progress evidence; independent review owns acceptance ([native admission/recovery handoff](../design/native-admission-recovery-handoff.md), Current, source-backed authority and handoff requirements). | A delegation receipt or partial-success summary must not become a second graph, completion store, or acceptance authority. |

## Installed router source inventory

The following is direct source evidence from installed package
`opencode-model-router`, not evidence that this host loads it.

| Concern | Source-backed behavior | Limit relevant to a future native seam |
| --- | --- | --- |
| Admission and producer isolation | `delegate` exists only when `experimental.verifiedDelegateTool` is true or `MODEL_ROUTER_VERIFIED_DELEGATE=1`; each ladder attempt creates a child producer session, optionally linked to its parent ([index.ts](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/index.ts), lines 324-434). | Feature enablement, plugin initialization, tool registration, actual permissions, and child isolation are unobserved. The optional `cwd` scopes verification only, not the producer (lines 354-359). |
| Retry ceiling and cancellation | The ladder has configured attempt accounting plus an independent safety ceiling; producer prompts and gates are time-bounded; timed-out gate graders are aborted; producer sessions are disposed after attempts and again in `finally` ([index.ts](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/index.ts), lines 395-400, 452-570, 575-641). | This bounds router-managed sessions, not duplicate external side effects. Abort is best-effort, so a future design cannot call cancellation a rollback guarantee. |
| Acceptance and honest unmet | A producer error and gate error fail closed. Accepted output returns only after the gate passes. Exhausted attempts return `[router status: unmet]` with attempt/escalation information and forcing reasons ([index.ts](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/index.ts), lines 496-553, 603-632). | This is per delegated result. It does not define a parent-level partial-success aggregation, rollback, or acceptance of a subset of children. |
| Changed-file attribution | A per-plugin changed-file store is created; the after hook records edit-tool arguments by session; delegated artifacts pass the producer session's recorded files into acceptance and clear them after processing ([index.ts](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/index.ts), lines 215-240, 480-486, 557-570, 824-833). | Attribution is tool-observation data, not proof of semantic ownership, exclusivity, clean Git state, or absence of undeclared shared-file changes. A future writer must compare actual Git/content state before retrying or aggregating. |
| Resumption and tool guards | Re-registration of a same-session same-tier dispatch starts a new guard round and records a resume. Before hooks can hard-block tracked-subagent tool calls; after hooks record calls, file changes, and guard observations ([index.ts](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/index.ts), lines 677-715, 774-853). | The source documents a residual same-session/different-tier guard-state desynchronization that is stricter rather than laxer (lines 704-710). Guard behavior, permission enforcement, and its match to host tools require a host trace. |
| Native task path | For an already-finished built-in `task`, verification can append a forcing note after a failed gate but cannot retry that task call ([index.ts](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/index.ts), lines 855-936). | This cannot furnish a reliable retry or rollback protocol for side-effecting child work. |
| Configuration and agent scope | Global and project router overrides merge, with the project file winning; project lookup is bounded by repository/home/depth limits ([config.ts](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/router/config.ts), lines 209-307). Existing subagent overrides skip tier collisions and non-subagent primary agents, while Markdown-defined agents may be invisible ([subagents.ts](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/router/subagents.ts), lines 18-66). | Source cannot decide effective configuration, Markdown-agent registration, or which tools/permissions a loaded child receives. |

## Required decision gate before any later design

A new native boundary is justified only when an observed repository task has at
least two independent children with declared non-overlapping write sets and a
real need to return a useful parent result when only some children pass. The
evidence must identify the parent issue and source artifact, each child,
dependency order, intended write paths, side effects, acceptance checks, and
the serial workflow's concrete cost or failure.

If that trigger occurs, the smallest candidate is an advisory section in the
existing implementation notes, not a task graph or a persistent router store.
It may summarize each child as `accepted`, `unmet`, `cancelled`, or `not-run`,
but cannot mark the parent accepted. The parent remains unmet until its mapped
obligations, Git state, targeted validation, and independent review pass.

Before any retry or resumed write, the coordinator must re-read the source and
notes; inspect current Beads status/dependencies and Git state; compare intended
paths and semantic change against current content and any accepted manifest; and
record a no-op when the desired change already exists. It must stop rather than
infer when ownership, changed state, or side-effect completion is ambiguous.
Only idempotent or compensatable operations may be retried. Cancellation stops
future dispatch and requests best-effort child abort, but does not erase writes;
rollback requires an explicit, reviewed Git/content restoration plan and fresh
targeted validation and acceptance.

Any future host-dependent proposal additionally requires authorized evidence of
the exact OpenCode version, merged effective configuration, router initialization
and feature flag, registered delegate/task tool, child permissions and working
directory, session-create/prompt/abort behavior, guard behavior, changed-file
attribution against actual Git state, timeout cleanup, and pass/fail/partial/
cancelled outcomes. A source inspection cannot supply this evidence.

## Explicit exclusions

This inventory excludes Teamsters aliases and dispatch, webhook telemetry,
prompt/output/environment capture, and a new task graph. It does not recommend
provider calls, router configuration, host registration changes, runtime trials,
or import of marketplace code. Router scorecard and trajectory facilities are
not adopted as telemetry requirements.

## Acceptance of this inventory

The source-backed no-change decision is defensible when an independent reviewer
can verify the citations above, confirm that current serial ownership and
acceptance remain authoritative, and confirm that no router/configuration/code
or runtime delegation change accompanies this artifact. Reopen design only with
the observed trigger and host evidence described above; otherwise retain no
change.
