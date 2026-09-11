---
title: Workflow comparison candidates and pre-results trial protocol
date: 2026-09-11
status: pre-results
tags: [workflow, opencode, candidates, trial-protocol, evidence]
related: [workflow-comparison-decision-rubric.md, workflow-comparison-opportunity-risk-register.md, workflow-comparison-review.md]
---

# Workflow comparison candidates and pre-results trial protocol

## Decision boundary and evidence basis

This is the design artifact for `agents-alv.5`. It forms candidates and a
pre-results protocol only. It records no trial, host-load observation,
configuration change, adoption decision, or result. The evidence terms and
gates in the [decision rubric](workflow-comparison-decision-rubric.md) govern
all later work. The [risk register](workflow-comparison-opportunity-risk-register.md)
establishes that Forge and Factory have inspectable source support for narrow
mechanisms, while OpenCode registration, actual loading, and effective
execution remain unknown. The [baseline review](workflow-comparison-baseline-evidence.md)
establishes the current instruction-and-artifact workflow and the Claude-only
boundary of Teamsters, Test Automation, and Ponytail hooks.

The decision set deliberately retains no change. A substantial replacement is
not currently justified because no complete OpenCode-compatible replacement,
adapter, state migration, or host trace is evidenced. It remains a possible
future condition only if the entry criteria below are met before the protocol
is amended, reviewed, and re-registered without trial results.

## Candidate matrix

All candidates retain repository instructions, Beads, source control, and the
existing independent-review requirement. A candidate may be exercised only in
an authorized later trial under the common-condition rules below. No candidate
permits unapproved network, credential, external-service, destructive, or
configuration action.

| ID and bounded condition | Hypothesis, mechanism, and integration cost | Observable risks and disconfirming evidence | Dependencies, port work, and state/instruction rule | Decision-changing purpose |
|---|---|---|---|---|
| **B0: unchanged baseline** | **Hypothesis:** retaining the current workflow can satisfy the registered task requirements and gates without added workflow machinery. **Mechanism:** current skills, `.lore/work` evidence, Beads task state, targeted validation, and role-separated review remain unchanged. **Cost:** no candidate-specific setup, migration, or teardown. | Missing requirement mapping, rescue, unreviewed acceptance, or a gate failure disproves the expected baseline behavior for that task. This condition does not receive discounted treatment. | Beads remains the sole authority for issue status and dependencies. Git remains source authority. `.lore/work` records evidence and is not task-state authority. Repository and host instructions take precedence over any candidate material. | Preserves a valid no-change outcome and gives every alternative the same comparison target. |
| **I1: isolated Forge evidence-validation transfer** | **Hypothesis:** a run-scoped, manually invoked Forge validation/evidence record improves detectable evidence drift or uncovered requirements at acceptable setup and upkeep cost. **Mechanism:** use only the inspected Forge graph/evidence/strict-validation path for the registered task, without Forge dispatch, Teamsters, Factory, hooks, or persistent adoption. **Cost:** candidate-specific graph/evidence declaration, command invocation, reviewer inspection, and cleanup are counted. | Incorrect declarations can block valid work; hashes can become stale after harmless edits; path checks can mistake declared files for semantic reachability; undeclared edits can evade collision checks. Disconfirming evidence includes no additional detected gap, a false block, state drift, failed acceptance, or inability to produce a reproducible command trace. | **Unavailable/port work:** no OpenCode command/tool registration or permission behavior is evidenced. A later trial must either invoke an approved bounded local command directly or supply a reviewed adapter and host trace. The candidate may create only a run-scoped trial artifact. Forge graph state is evidence-local and never changes Beads status or replaces `.lore/work`; its reconciliation rule is "Beads status plus independent acceptance prevail, graph disagreement is logged as a candidate failure." Forge instructions cannot override repository safety, validation, or Beads rules. | Can show whether deterministic evidence validation adds decision-relevant correctness or maintainability value without importing orchestration. |
| **I2: isolated Factory admission-gate transfer** | **Hypothesis:** a run-scoped Factory dry-run admission decision exposes missing approvals, provider readiness, or queue/agent ambiguity before work proceeds, at the cost of envelope preparation and explicit operator handoff. **Mechanism:** use only the schema-bound envelope and dry-run/gate decision, with no dispatch, provider call, Teamsters, telemetry export, or persistent Factory ledger adoption. **Cost:** envelope mapping, declared approval inventory, dry-run recording, reviewer inspection, and cleanup are counted. | Schema fields can create false assurance; hard-coded downstream integration names create coupling; a false block, missing required input, untraceable decision, or a gate that does not alter a permitted choice disconfirms usefulness. | **Unavailable/port work:** the envelope names Claude-oriented integrations and no OpenCode bridge is evidenced. A trial needs either a reviewed local-only invocation path that does not resolve providers or an adapter plus host trace. Factory ledger is run-local evidence only. Beads remains task authority, and any Factory verdict is advisory until independent acceptance. No telemetry, prompt/output capture, signature secret, provider config, or network transport is permitted. | Separates deterministic admission control from unproven dispatch, so an observed benefit could support a narrow transfer rather than a workflow replacement. |
| **H1: coherent evidence-and-admission hybrid** | **Hypothesis:** combining I1's evidence-validation record with I2's pre-work admission record improves requirement/evidence completeness and honest blocking more than either isolated transfer, while its extra state and setup remain non-inferior to B0. **Mechanism:** Factory dry-run gate precedes a single run-scoped Forge evidence record; the existing workflow performs implementation and independent review. No candidate dispatch, hooks, aliases, resume system, telemetry, or provider utility is included. **Cost:** all I1 and I2 costs, plus a documented handoff between their records and a reconciliation check. | Two records can disagree, duplicate policy, or add bureaucracy without improving completion. A disagreement, stale record, untraceable handoff, false block, increased rescue, or loss of independent review is recorded and can defeat the hybrid. | Both I1 and I2 availability gates apply. The sole cross-tool mapping is task ID, frozen requirements version, start revision, candidate version, and evidence locations. Beads is authoritative for task/dependency state; Git for source; Factory and Forge are ephemeral candidate evidence; `.lore/work` is the human-readable trial record. Instruction precedence is repository and host safety rules, then registered protocol, then candidate instructions. Conflicts stop the condition rather than being resolved ad hoc. | Tests the smallest coherent composition of the credible mechanisms. It can lose to B0 or either isolated transfer, so it is not presumed better because it is larger. |
| **R1: substantial replacement, withheld** | No hypothesis is eligible yet. A replacement would need to replace the current planning, implementation, validation, review, recovery, and task-state interfaces with a single declared OpenCode-compatible workflow. Its integration cost would include a version-pinned adapter, state migration and rollback, instruction-precedence design, host registration/load trace, privacy/telemetry controls, and independent acceptance mapping. | Claude-only dispatch/aliases/hooks, competing state authorities, incomplete rollback, missing host traces, unsafe telemetry or provider behavior, or a non-reproducible migration are blocking risks. | **Unavailable dependencies:** an OpenCode-specific Teamsters lifecycle adapter, model mapping, hook/command equivalents, Test Automation recovery port, Ponytail injection adapter, and a reconciliation/migration implementation are not evidenced. Open Wrapper is excluded because its source-confirmed interpolation vulnerability must be corrected and independently reviewed before any use, and it would add provider/network risk. | Excluded now. It may be added only when every unavailable dependency has a reviewed implementation, its required OpenCode surfaces have a reproducible host trace, its migration/rollback is reviewed, and an independent reviewer approves an amended pre-results protocol before any R1 result is seen. |

## Fixed trial design, pending authorization

### Common conditions and task set

Before the first condition starts, an independent protocol reviewer freezes a
dated evaluation record for every task and condition as required by rubric
sections "Evaluation record and fair comparison" and "Pre-results
registration." The frozen record includes task ID, requirements version,
starting revision and comparison-tree content identity, host/version and
model-routing details, allowed tools and permissions, candidate version and
delta, start/end times, commands and outputs, changed files, acceptance
evidence, reviewer identity, and the intervention log.

The task set must contain these representative, candidate-neutral classes, all
drawn from ordinary repository work and all safe under the approved permission
inventory:

1. a small behavior change with a focused automated check;
2. a cross-file defect or requirement change with an explicit regression check;
3. a task with a predeclared, safe failure or blocked-path check that can test
   recovery or honest handoff without creating a destructive condition.

The actual task identifiers, frozen requirements, fixtures, acceptance checks,
starting revision, and comparison-tree hash are unresolved inputs. The
independent reviewer must select them before any condition, using the same
tasks for B0, I1, I2, and H1. Tasks requiring credentials, network access,
external services, irreversible actions, or unavailable host features are not
eligible. A candidate may not select a different task after a result is seen.

Each eligible condition runs every registered task for the same pre-registered
repeat count. The repeat count is an unresolved user-approved input, must be
at least sufficient to meet the rubric's registered comparable-task and
applicable-failure minima, and must be frozen before the first condition. Any
environment repair, fixture correction, or candidate setup makes affected runs
non-comparable until every affected condition is rerun from the same corrected
starting point. Candidate-specific setup, migration, teardown, and repair stay
in that candidate's evidence and time.

### Resource and authorization gate

No resource budget, wall-clock limit, token allowance, billing rate, or
provider cost has been supplied. The user must approve, before trials begin:

- the number of tasks and repeats, maximum human elapsed time, maximum
  candidate-specific setup/teardown time, and any token/provider budget;
- the local resource limits, tool/permission inventory, and whether any
  non-network local command may be invoked;
- the approved task set and the independent protocol reviewer and acceptance
  reviewer; and
- whether an OpenCode load/registration trace is authorized for a candidate
  that needs one.

Until these inputs are recorded, this protocol is design-complete but not
trial-authorized. Missing cost or usage data is reported as unknown, never as
zero. A budget exhaustion or unapproved resource request stops the affected
condition and cannot be repaired by silently changing its limit.

### Gates, stop conditions, and intervention logging

Every condition must pass the rubric's comparability, safety, OpenCode
feasibility, correct-completion, and evidence-integrity gates. B0 has no new
OpenCode surface to credit. I1, I2, and H1 must show each required new surface
through the pre-trial compatibility review and, when authorized, a versioned
host registration/load trace. Source presence, a manifest, or a checked-in test
is not a feasibility pass.

Stop the condition immediately, preserve raw evidence and changed-state
information, and exclude it from adoption recommendation if any of the
following occurs:

- an unapproved sensitive action, credential exposure, network/external-service
  action, destructive or irreversible operation, or permission escalation;
- a missing adapter, unavailable dependency, instruction conflict, absent host
  trace, or state-authority disagreement that lacks the registered
  reconciliation rule;
- a failure of frozen common conditions, missing raw outputs, lost provenance,
  inability to retain independent review, or an unregistered candidate/config
  delta;
- budget exhaustion, an unapproved resource request, or a stop request from the
  user or safety authority; or
- a repeated failure after the registered recovery attempt, where continuing
  would repeat the same unresolved action rather than produce new evidence.

Log every human intervention using the rubric's required trigger, category,
actor, time, change, outcome, and rescue causal basis. The registered categories
are requirement clarification, scope/priority decision, permission/safety
approval, environment/tool repair, diagnosis/debugging, manual execution,
recovery direction, acceptance/handoff, and explained other. An independent
reviewer must inspect both acceptance evidence and the intervention log. An
actor who performs a candidate-specific rescue cannot independently validate
that rescue's necessity.

### Measurements and pre-registration inputs

The later evaluation plan must use the rubric's operational definitions for
requirement coverage, meaningful-check rate, regression count,
honest-completion count, successful autonomous completion, recoverable and
repeated failures, intervention/rescue/approval/handoff measures, and
maintainability deltas. It also records safety findings, required-surface
coverage, elapsed times, and cost/usage when available. Every rate includes its
numerator, denominator, unit, and task IDs. Zero denominators are N/A.

Before results exist for **any** condition, the independent protocol reviewer
must register, with rationale tied to the chosen task set:

1. directional primary metrics for correctness, reliability, supervision, and
   maintainability, including why each maintainability direction is favorable;
2. unit-bearing practical-improvement and practical-regression thresholds and
   non-inferiority margin for every directional metric;
3. minimum evidence grade, minimum comparable-task count, and minimum
   applicable-failure count for every compared metric; and
4. the recovery attempt boundary, acceptance checks, and data-capture locations.

These values are intentionally unresolved rather than invented. No condition
may start before they are set. They may change only before any result is seen;
otherwise the original rule remains primary and a changed analysis is labeled
exploratory. This prevents post-hoc thresholds and ensures each experiment can
change the decision.

### Selection rule and limitations

Apply the rubric without a weighted total. A condition is decision-eligible
only if every applicable gate passes and every compared metric meets its
registered evidence and sample minimum. An alternative is non-inferior only
within its registered margins. It dominates B0 only when non-inferior, it meets
at least one declared practical-improvement threshold, and it has no practical
regression on another declared directional primary metric. B0 remains eligible
when it passes its gates and no alternative dominates it. If multiple
alternatives dominate B0, select one only if it dominates every other eligible
alternative. Otherwise report the unresolved tradeoff or no decision yet.

This protocol cannot establish production effectiveness from a small bounded
task set. It cannot generalize from source evidence to OpenCode loading, model
behavior, provider behavior, parallelism, or long-term maintenance. It excludes
Teamsters dispatch, Test Automation resume, Ponytail hooks, Dream Mentor,
telemetry/webhooks, and Open Wrapper from credit, so it cannot measure their
claimed benefits. Results from stopped, non-comparable, or below-grade
conditions remain reportable as limitations but cannot rank candidates.

## Independent-review handoff

The next independent reviewer should verify that B0, I1, I2, and H1 are all
present; R1 is withheld for stated evidence reasons; no result, budget, or
threshold was fabricated; the state and instruction rules match the rubric and
risk register; and every authorization input is resolved before `agents-alv.6`
starts a trial. Independent design review confirmed coverage of the issue's
acceptance criteria and grounding in the rubric and risk register. Trial
authorization remains pending the inputs above.
> **Superseded for the current assessment:** This protocol is historical planning. See [the documentation capability assessment](local-marketplace-documentation-capability-assessment.md); no trial is required unless a later decision identifies a specific critical claim for an explicitly authorized targeted smoke test.
