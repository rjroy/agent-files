---
title: Native admission and recovery handoff decision
date: 2026-09-11
status: draft
tags: [workflow, admission, recovery, handoff, beads, evidence]
related: [.lore/work/research/workflow-comparison-review.md, .lore/work/research/workflow-comparison-baseline-evidence.md, .lore/work/research/workflow-comparison-opportunity-risk-register.md]
---

# Native admission and recovery handoff decision

## Decision

**No new durable admission verdict or recovery checkpoint is justified now.**

The current `implement` contract already requires prior-work research, an
obligation-to-evidence map before work, a stale-plan decision, phase-by-phase
notes, bounded correction and escalation, targeted re-test and verification
review, an accepted Git-content manifest, and resumption from notes
([implement](../../../plugins/lore-development/skills/implement/SKILL.md),
Input, lines 10-18; Initialize, lines 24-51; Execute Phases, "Handle failures"
and "Record", lines 67-71; Validate, lines 79-84).
The workflow comparison reached the same conditional conclusion: compare real
notes and handoffs first and prefer no change when existing artifacts carry the
needed facts ([review](../research/workflow-comparison-review.md), "P2: compare
current admission/recovery", lines 23-24).

The actual work tree currently contains research and design artifacts but no
`.lore/work/notes/` directory, so there is no completed native implementation
note from which to demonstrate that its required progress, failure, or resume
facts are lost. The recent authoritative Beads handoff for closed dependency
`agents-alv.8` records its review result, changed decision, validation, and
follow-up issue IDs. It therefore demonstrates a usable task-level handoff,
not a missing checkpoint. Its close record also makes clear that the next work
is a bounded investigation rather than implementation.

This is an evidence-limited decision, not a claim that resumed writes are safe
in every future execution. The baseline says current resumption and note
quality are documented rather than observed in a workflow run
([baseline](../research/workflow-comparison-baseline-evidence.md), "Current
lifecycle map", lines 376-388; "Comparative lifecycle evidence matrix",
Failure and interruption recovery and Resume, lines 463-468).
The risk register identifies stale, incomplete, contradictory state and
repeated writes as a possible risk, but explicitly requires a recovery design
and resumed-write safety check before assigning capability credit
([risk register](../research/workflow-comparison-opportunity-risk-register.md),
"Test Automation resume and working context", line 80).

## Current, source-backed authority and handoff requirements

| Subject | Authority | Current source-backed record | Not authoritative for |
| --- | --- | --- | --- |
| Issue status, ownership, dependencies, and blockers | Beads | Issue state, dependency links, and issue notes or close reason | Source content, test result, or acceptance decision |
| Source and changed state | Git working tree and index | Current status plus the accepted manifest when terminal acceptance has passed | Issue readiness or dependency state |
| Progress, phase evidence, failures, decisions, and resume context | The implementation notes file | Progress tracker and log updated after each phase | Task completion or independent acceptance |
| Acceptance | Independent review | Phase review evidence and one terminal acceptance result | Beads completion by itself |

These assignments retain the current repository rule that Beads is the task and
dependency authority and `issues.jsonl` is only a passive export
([baseline](../research/workflow-comparison-baseline-evidence.md), "Observed
state, ownership overlap, and instruction conflicts", lines 471-485).
They also retain Git as source authority and independent review as the
acceptance boundary. A note may report a blocked verdict or handoff, but must
not change Beads status, declare Git state current, or substitute for review.

The current `implement` instruction requires a notes progress tracker and log,
updated after every phase, and records phase evidence and failures. It requires
the accepted manifest only after terminal acceptance
([implement](../../../plugins/lore-development/skills/implement/SKILL.md),
Output, lines 14-20; Execute Phases, "Record", lines 67-71; Validate,
lines 79-84). It does not prescribe a separate admission verdict, a mandatory
handoff field list, or a universal pre-write Beads/Git inspection rule. This
document does not add any of those requirements.

### Non-operative future handoff checklist

The following is a candidate checklist only if the conditional trigger below
is demonstrated and a later design approves it. It is not a current handoff
contract and does not govern current implementations. That later design could
ask a handoff to name the source artifact and phase, mapped obligations,
failed check or finding IDs and correction count, next safe action, manifest
status where applicable, Beads issue/dependencies, and stop reason. It could
also require a recipient to inspect the named notes, Beads, and Git state before
writing. Until then, the existing notes and review requirements above are the
only source-backed process obligations stated here.

## Conditional future checkpoint, only if a demonstrated trigger occurs

No field or file is added by this design. If a future, independently reviewed
execution demonstrates one of the triggers below, the smallest candidate is a
section in the existing notes file, not a Factory ledger, Test Automation
state file, provider call, dispatch mechanism, or separate completion store.

### Trigger

Open a follow-up design only when one of these is evidenced from an actual
native run or handoff:

1. A blocked or transferred phase lacks a durable reason, next action, or
   unresolved finding record in its existing notes and Beads handoff.
2. A notes file is malformed, partial, stale against its source artifact, or
   contradicts current Beads or Git state, and normal re-inspection cannot
   safely resolve it.
3. A resumed write cannot determine whether the intended change already exists
   or whether the accepted manifest is stale, creating a plausible duplicate or
   destructive write.

The trigger must cite the affected notes path, Beads issue, source artifact,
Git observation, and the observed consequence. A hypothetical interruption,
the existence of Factory or Test Automation state, or unobserved host behavior
does not qualify. This preserves the comparison's warning that parallel
durable stores create conflicting authorities
([risk register](../research/workflow-comparison-opportunity-risk-register.md),
"State and instruction conflicts requiring an explicit authority rule",
lines 85-101).

### Candidate fields and handling rules

If triggered, the proposed notes section has only these fields:

| Field | Purpose and rule |
| --- | --- |
| `checkpoint-phase` | Existing phase or task identifier. Must match the notes progress tracker. |
| `verdict` | `proceed`, `blocked`, `handoff`, or `resume-review-required`. Advisory only. |
| `reason` | Concrete blocking, transfer, or uncertainty reason, including finding/check IDs where applicable. |
| `source-revision` | Source artifact path plus observed content identity or modification observation used when recording the checkpoint. |
| `beads-issue` | Existing issue ID only. Beads remains the sole task-state authority. |
| `git-observation` | Exact observed porcelain status and, when present, the accepted-manifest reference. |
| `intended-write` | Files and operation the next writer proposes, sufficient to compare before writing. |
| `resume-checks` | Required re-checks and their results, including changed-state/idempotency outcome. |
| `recorded-at` | Timestamp and recorder identity for staleness assessment. |

The checkpoint is corrupt if a required field is absent, a phase or issue does
not resolve, field syntax cannot be parsed, or its claimed source or Git
observation cannot be reproduced. It is stale if the source changed, Beads
status or dependencies changed, Git observation differs, a referenced finding
closed or changed, or later notes supersede it. Corrupt or stale checkpoints
are never repaired by inference and never authorize a write. Mark the notes
entry `resume-review-required`, preserve the original text as evidence, inspect
the authorities in the table above, and obtain a new independent review of the
recovery plan when the inconsistency affects acceptance or a write.

Before a resumed write, the writer must: re-read the source and notes; inspect
the named Beads issue and current Git status; compare the intended-write paths
with current content and any accepted manifest; verify whether the requested
semantic change is already present; and run only the recorded prerequisite
checks. If the desired state already exists, record a no-op with evidence and
continue to validation rather than write again. If the state differs or cannot
be determined, stop for a focused plan-divergence or recovery decision. After
a legitimate write, refresh phase evidence and require targeted test and
verification review before replacing an accepted manifest. These safeguards
extend, rather than replace, the existing instruction to validate work reported
as already done and to require manifest equality before commit
([implement](../../../plugins/lore-development/skills/implement/SKILL.md),
Execute Phases, lines 71; Validate and Finalize, lines 79-103).

## Acceptance scenarios for this decision

1. **Current no-change acceptance:** a reviewer can confirm that this document
   cites the current initialization, notes, failure, resumption, manifest, and
   Beads handoff evidence; records the absence of actual native notes as a
   limitation; and adds no operational skill, runtime, provider, dispatch,
   OpenCode configuration, Factory, Test Automation, or marketplace change.
2. **Ordinary handoff:** an interrupted multi-phase execution retains the
   source-backed notes progress tracker and log, including phase evidence and
   failures, plus its existing Beads issue state. It is not rejected for omitting
   the non-operative future checklist, and no checkpoint is required.
3. **Stale-plan path:** an implementation plan is newer than its tasks. The
   existing stale-plan choices are used and documented. No admission verdict is
   created merely to restate that decision.
4. **Future corrupt-checkpoint path:** if the conditional section is adopted
   after a qualifying trigger, a malformed or contradictory entry blocks a
   resumed write, is preserved, and is reconciled against Beads, Git, notes,
   and independent review before work continues.
5. **Future idempotent-resume path:** if the conditional section is adopted,
   a resume detects an already-present intended semantic change, records a
   no-op, runs targeted validation and review, and does not repeat the write.

Independent review of this document is the final acceptance check. It must
confirm that the no-change decision remains justified, that the conditional
fields remain advisory within notes, and that Beads task status/dependencies,
Git source state, and independent acceptance have not been displaced.
