---
title: Workflow comparison decision rubric
date: 2026-09-10
status: pre-results
tags: [workflow, comparison, rubric, evaluation, opencode]
---

# Workflow comparison decision rubric

## Purpose and boundary

This is the pre-results evaluation design for `agents-alv.3`. It defines how a later review may compare the unchanged current workflow, a hybrid, and a substantial replacement. It does not form candidates, run trials, change configuration, set a time or cost budget, or select an outcome.

The source baseline and lifecycle comparison are in [workflow-comparison-review.md](workflow-comparison-review.md). Their documented, implemented, tested, and observed labels remain the evidence vocabulary for this rubric. In particular, source presence and checked-in tests are not evidence that OpenCode loaded or effectively ran a workflow.

## Evaluation record and fair comparison

Before a candidate is exercised, the evaluator must create one evaluation record per task and condition. The record must include the task identifier and frozen requirements, repository revision and comparison-tree content identity, host and model/routing details, available tools and permissions, candidate version and configuration delta, start and end times, commands and outputs, changed files, test results, acceptance decision, and all intervention events. It must identify the independent reviewer and preserve raw artifacts or their stable locations.

The same pre-registered task set, requirements, starting revision, permitted tools, approvals, resource conditions, and acceptance checks apply to every condition. A task becomes non-comparable if any of these differ without a recorded reason. Non-comparable results may explain a condition but cannot rank it. Re-run all affected conditions from the same corrected starting point when the difference can be repaired.

| Condition | Required treatment |
|---|---|
| Unchanged baseline | Run the current workflow without workflow configuration or instruction changes. It is a full candidate, not a control to be discounted. |
| Hybrid | State every retained and borrowed mechanism, their integration boundary, and every configuration or operational delta. Credit only behavior attributable to the declared hybrid. |
| Replacement | State the replaced boundary, migration or adapter work, and rollback path. Do not credit features that are not available in the condition. |

Pre-existing project changes are held constant across conditions. Candidate-specific setup, migration, teardown, and repair work are recorded in that candidate's time, intervention, and maintainability evidence. A later task may add conditions, but it may not remove a condition or change a criterion after seeing that condition's results without marking the comparison exploratory.

### Pre-results registration

Before any condition starts, the evaluator records the following trial-design inputs in a dated, reviewable evaluation plan: the task set and requirement versions; starting revisions and comparison-tree identity; condition definitions and configuration deltas; permitted tools, permissions, and approvals; acceptance checks; intervention-log template; measurement method and unit for every metric; practical-improvement threshold, practical-regression threshold, and non-inferiority margin for every directionally compared metric; the directional primary metrics eligible to support dominance; minimum evidence grade; and minimum comparable-task and applicable-failure counts. The plan also records why each threshold and minimum is adequate for the task set. It must not substitute a budget or an unobserved result for a threshold.

Thresholds use the metric's declared unit, such as percentage points for a rate, events per task for intervention rate, or a count delta for regressions. A rate with a zero denominator is N/A, not zero; it cannot satisfy an evidence or sample minimum or support a favorable comparison. A comparison with fewer than the registered number of comparable tasks or applicable failures, or with evidence below the registered grade, is insufficient rather than favorable. The evaluator may add a new metric or revise a threshold only before seeing results for any condition. Otherwise, retain the original rule and label the added analysis exploratory.

## Gates

Gates are pass, fail, or inconclusive. A failed or inconclusive gate excludes a condition from adoption recommendation, but its observations remain reportable. No gate failure is silently converted into a score.

| Gate | Pass condition | Required evidence | Failure or inconclusive rule |
|---|---|---|---|
| Comparability | The evaluation record satisfies the common-condition requirements above. | Frozen task and environment records for every condition. | Do not rank the result; repair and rerun, or report it separately. |
| Safety | No unapproved irreversible, destructive, credential, privacy, network, permission, or external-service action occurs. Every planned sensitive action has an explicit approval and a traceable outcome. | Permission inventory, approval record, command/tool trace, and changed-state check. | Stop the condition, preserve evidence, and exclude it. Do not retry without an approved revised protocol. |
| OpenCode feasibility | The candidate's required instructions, skills, agents, tools, hooks, and configuration are supported by OpenCode or have a declared adapter. When a trial is authorized, the required pieces are shown in a reproducible host load/registration trace and complete their intended bounded task without a Claude-only substitute. | Source/API compatibility review before a trial; then versioned configuration and host trace when trials are authorized. | Missing adapter, unsupported dependency, or absent trace is inconclusive or fail, never proof from a manifest or README. |
| Correct completion | Each claimed completed requirement has a requirement-to-evidence mapping, meaningful check result, and independent acceptance review. No known required failure is hidden by a completion claim. | Requirement map, test/inspection outputs, failure log, and reviewer decision. | Mark the task incomplete or failed. It cannot contribute a successful completion. |
| Evidence integrity | Result claims have the minimum evidence grade specified below and retain enough provenance to reproduce the conclusion. | Raw outputs or stable references, version identifiers, timestamps, and actor attribution. | Downgrade the claim to unknown; do not infer a favorable result. |

## Measures and decision rules

Correctness, reliability, supervision, and maintainability are the primary dimensions. Before results, the evaluation plan must identify the directional metric or metrics within each primary dimension that may support dominance and state which direction is favorable. Maintainability counts are not automatically favorable; a count may support dominance only when the plan states the mechanism, direction, and rationale. Safety and OpenCode feasibility are gates. Time and cost are supporting metrics only. All rates report numerator, denominator, unit, and task identifiers. Do not combine dimensions into a weighted total. The evaluator classifies a difference as a practical improvement, practical regression, or non-inferior only against the registered threshold or margin for that metric, never by post-results judgment. A recommendation may consider a hybrid, replacement, or no change only after every applicable gate passes. Time and cost cannot compensate for a safety, feasibility, correctness, reliability, or evidence-integrity failure.

A condition is **decision-eligible** only when it passes every applicable gate and every compared metric meets its registered evidence and sample minimum. A non-baseline condition is **non-inferior** when no declared directional primary metric exceeds its registered non-inferiority margin relative to the unchanged baseline. It **dominates** the baseline when it is non-inferior and meets the registered practical-improvement threshold on at least one declared directional primary metric, with no practical regression on any other declared directional primary metric. The unchanged baseline remains the decision-eligible outcome only when it is itself decision-eligible and no alternative dominates it. If the baseline is not decision-eligible, this rubric supports no adoption recommendation. If more than one alternative dominates the baseline, one alternative is selected only if it also dominates every other decision-eligible alternative under the same pre-registered rules. Otherwise, mixed results require no decision yet; report the unresolved tradeoff and do not introduce a post-hoc tie-breaker.

| Dimension | Operational measure | Evidence and interpretation |
|---|---|---|
| Correctness | Requirement coverage = requirements with a mapped, passing acceptance check / applicable requirements. Meaningful-check rate = passing checks that exercise the stated behavior or a relevant failure path / passing checks cited for completion. Regression count = previously passing unchanged checks that fail under the condition. Honest-completion count = tasks whose stated status matches the evidence, including explicit incomplete or blocked status. | A requirement is covered only when the mapping names the check and its result. A broad suite alone does not cover a requirement unless it demonstrates that behavior. Report uncovered requirements, regressions, and any completion-status mismatch individually. |
| Reliability | Successful autonomous completion rate = tasks accepted without rescue / comparable tasks. Recoverable failure rate = encountered failures that reach a correct accepted or honestly blocked outcome through the declared recovery path / encountered failures. Repeated-failure count = the same unresolved failure recurring after a declared recovery attempt. | Record the initial failure, recovery action, outcome, and whether human rescue was needed. A blocked outcome can be reliable only if it is detected, contained, and honestly handed off; it is not a successful completion. |
| Supervision | Intervention events per task, rescue rate = tasks requiring human rescue / comparable tasks, approval-event rate = approval events / comparable tasks, approval-required task rate = tasks with one or more approval events / comparable tasks, handoff-event rate = handoff events / comparable tasks, appropriate-handoff rate = tasks with an appropriate handoff / tasks for which the registered design requires a handoff, and autonomous-success rate = tasks accepted without rescue / comparable tasks. Report event counts by category and the human elapsed time attached to each event. | Rates have the stated units and denominators. Required safety approvals remain visible even when expected. An approval alone is not completion evidence, but it does not disqualify a no-rescue autonomous success. An appropriate handoff occurs at the registered boundary with the information needed to act. |
| Maintainability | Relative to the unchanged baseline, count persistent state authorities, new runtime dependencies, configuration surfaces, setup and teardown steps, duplicated policy statements, manual debugging steps needed to reproduce a failure, and recurring upkeep actions. Also record whether an owner, update path, and removal or rollback path are documented for every added component. | Counts are deltas, not a claim that fewer is always better. A component is a moving part only if it must be installed, configured, operated, or maintained for the condition to work. Explain each delta and any reliability or safety benefit it buys. |
| Safety | Safety-gate failures, near misses, unapproved-action attempts, and approval-to-outcome trace completeness. | Safety is a gate, not a tradeable score. Near misses remain reported even when the gate passes. |
| OpenCode feasibility | Required-surface coverage = required OpenCode surfaces with supported implementation and host trace / required surfaces; unsupported or Claude-only dependency count; adapter completeness. | Feasibility is a gate. Source inspection may establish a candidate implementation path, but only an authorized host trace can establish loading or effectiveness. |
| Time and cost | Wall-clock elapsed time, autonomous active time when distinguishable, human elapsed time, setup/teardown time, token or provider usage and billed cost when available. | Report raw units and measurement source. Mark unavailable billing or usage data as unknown. No user budget, target, or threshold is assumed. |

### Intervention counting protocol

An intervention is a human action or decision that changes the candidate's execution, available authority, task interpretation, state, or path to completion after the condition starts. Log the trigger, category, actor, time, what changed, and resulting outcome.

- Count one event for one human response to one trigger before the candidate's next attempt. A bundled response to that same trigger is one event and lists every category it contains. A later response after a new attempt is a new event.
- Categorize each event as requirement clarification, scope or priority decision, permission or safety approval, environment/tool repair, diagnosis or debugging, manual execution, recovery direction, acceptance/handoff, or other with an explanation.
- A **rescue** is an intervention without which the candidate could not make valid progress or would end incorrectly. Mark the causal basis in the log. A predeclared mandatory approval is counted as an approval event but not a rescue unless it adds diagnosis, changes scope, or repairs a failure.
- Do not count pre-condition task briefing, shared test-fixture preparation, or independent review that follows the same predeclared protocol for every condition. Do count candidate-specific setup, correction, and teardown.
- An autonomous-success claim requires no rescue and independent completion evidence. It may contain a predeclared approval or a proper handoff, which must be reported separately; neither alone establishes completion.

## Evidence quality and uncertainty

Each metric cell and gate decision receives its strongest supported grade. A higher grade may cite lower-grade evidence, but lower-grade evidence cannot be upgraded by repetition.

| Grade | Evidence | Permitted use |
|---|---|---|
| A, observed and reproducible | Versioned input and environment, direct host/tool trace, raw result, and an independent reviewer can rerun or inspect it. | Supports a trial result and gate decision. |
| B, directly inspectable implementation or test source | Source code, configuration, or a checked-in test directly implements or asserts the behavior, with revision and path. | Supports feasibility hypotheses and trial design, not host loading or effective behavior. |
| C, documented claim | README, instruction, manifest, issue, or vendor documentation. | Records an assertion or planned behavior only. |
| D, unknown or conflicting | Missing provenance, indirect assertion, stale evidence, or unresolved contradiction. | Cannot support a favorable comparison or gate pass. |

If results conflict, preserve both artifacts, classify the claim as D until the conflict is resolved, and record the attempted resolution. Missing logs, changed conditions, unavailable cost data, and unexecuted tests are unknown, not zero. An independent reviewer checks acceptance evidence and the intervention log; the same actor may not both perform a candidate-specific rescue and independently validate that rescue's necessity.

## Pre-results decision record

After a later authorized evaluation, the reviewer completes this table without selecting a winner by score:

| Condition | Applicable gates | Correctness and reliability | Supervision | Maintainability | Safety and OpenCode findings | Time and cost | Evidence gaps | Recommendation eligibility |
|---|---|---|---|---|---|---|---|---|
| Unchanged baseline | Pending | Pending | Pending | Reference condition | Pending | Pending | Pending | Pending |
| Hybrid | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Replacement | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

The final reviewer must state whether the evidence supports retaining the unchanged baseline, a defined hybrid, a defined replacement, or no decision yet. If multiple conditions pass with different tradeoffs, report the tradeoff rather than manufacturing a single ranking. If none is eligible, retain the baseline operationally or defer a decision, subject to the separate final-review task.
