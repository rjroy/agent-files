---
title: Proposed isolated Forge and Factory comparison trial
date: 2026-09-11
status: draft-pending-review-and-approval
tags: [workflow, trial, preregistration, safety, opencode]
related: [workflow-comparison-safety-preflight.md, workflow-comparison-candidates-and-trial-protocol.md, workflow-comparison-decision-rubric.md]
---

# Draft isolated Forge and Factory comparison trial

## Status and decision boundary

This is a review draft, not a frozen execution protocol, authorization, a
measured result, or an adoption recommendation. Every choice below is
**PROPOSED pending approval**. Approval to prepare fixtures and verify the
isolation mechanism is distinct from approval to run any condition. Neither
approval has been given. No clone code, dependency, provider, OpenCode
configuration, hook, installer, or adapter may be executed or loaded until the
separate run authorization blockers are resolved.
The source preflight limits candidate behavior to Forge strict validation and
Factory's offline dry-run gate. It excludes their dispatch, A2A, telemetry,
provider smoke, model, resume-command, and host-loading paths.

## Proposed fixed work items and fixtures

No existing candidate-neutral product work item has been approved. The source
does contain focused, feasible unit-test fixtures, but using a candidate's own
tests as the sole product benchmark would bias the comparison. **PROPOSED:** an
independent protocol reviewer may prepare three tiny neutral fixtures in a new
disposable trial workspace, borrowing only their safe shape from the identified
source tests. This draft does not authorize creating them. Fixture hashes,
requirements, expected patches, check scripts, exact command arguments, and
candidate source hashes are **TBD**. Their absence blocks every condition.

| ID | Fixed task and fixture | Independent acceptance check | Purpose |
| --- | --- | --- | --- |
| T1 | Repair a one-function behavior defect plus focused regression test in a six-file Python fixture. Its small source/test/artifact layout follows Forge's strict-validation test fixture (`forge/tests/test_validation_strict.py`, lines 10-19), but contains no Forge imports or graph file initially. | A reviewer-owned Python check asserts the requested return value, runs only the fixture's focused test, verifies no files outside its allowlist changed, and maps each frozen requirement to output. | Small behavior change and regression. |
| T2 | Implement a two-file requirement change in a self-contained Python fixture: add a parser rule and connect it through its caller, with a positive and a regression input. The independent fixture must be frozen before any condition; no current repository task has been selected. | Reviewer-owned test invokes the public fixture entrypoint on both inputs, checks changed-file allowlist and requirement map, and rejects a passing helper that is not called by the entrypoint. | Cross-file completion and reachability. |
| T3 | Start from T2's frozen incomplete-worker checkpoint: one required test intentionally fails and the work note says `awaiting recovery`. The first agent must make one documented recovery attempt, then the session is stopped. A fresh agent receives only the frozen task, checkpoint, changed-state hash, and raw first-attempt log. | Reviewer verifies the initial failure occurred, recovery does not conceal it, the fresh session either reaches the same accepted checks or makes an honest blocked handoff, and no action repeats beyond the single declared recovery boundary. | Controlled failure and fresh resume without invoking the clone's Claude-only resume command. |

The reviewer must reject the fixture set if it requires network, credentials,
external services, package installation, a database, destructive commands, or
an unreviewed dependency. If an actual, candidate-neutral repository issue is
available before authorization, it may replace T1 or T2 only before results
exist and only with an amended, re-reviewed registration.

## Proposed conditions and isolation

Each condition runs T1, T2, and T3 from a fresh copy of the same frozen fixture
tree and same starting content hash.

| Condition | PROPOSED allowed delta | Prohibited delta |
| --- | --- | --- |
| B0 baseline | Existing instruction-and-artifact workflow, including its ordinary independent review. | No Forge/Factory command, candidate state, copied skill, or OpenCode change. |
| I1 Forge | One run-local Forge graph/evidence record and strict validation only. | No `scripts/a2a/`, Teamsters, provider, telemetry, automatic hook, or global state. |
| I2 Factory | One offline `run-factory-cycle.py --once` dry-run against reviewer-created sanitized fixtures, with reports redirected into the condition directory. Its verdict remains advisory. | No `--live`, provider smoke, dispatch, envelope signature key, provider config, worker, queue claim, or external integration. |
| H1 hybrid | I2 completes before I1; the handoff contains only task ID, requirement version, start hash, candidate version, and relative evidence paths. | No additional adapter, state authority, dispatch, hook, or reconciliation by ad hoc judgment. |

Each condition is proposed to use a new non-shared directory beneath an
approved disposable trial root. The required boundary is: a temporary `HOME`,
a minimal explicit environment allowlist, no configured credentials, a
read-only candidate-source mount/copy, one writable condition root, a disabled
network namespace, `PYTHONDONTWRITEBYTECODE=1`, and child processes confined to
the same namespace with no writable host mount. Beads is not touched by
condition tooling.

**Isolation feasibility is pending.** A reviewer must select and verify a
host-available sandbox mechanism, proposed as `bwrap` with a network namespace
and read-only binds, or an equivalent container/VM mechanism. The verification
must be read-only and must not execute clone code. It must demonstrate the
temporary HOME, denied network, read-only candidate path, writable condition
root, and child-process confinement. If no such mechanism is available and
verified, preparation stops and no trial runs. Exact sandbox argv, interpreter
version, candidate hash, fixture hash, environment allowlist, and allowed write
paths are TBD and are mandatory execution blockers, not frozen facts.

## Proposed permissions and command inventory

**PROPOSED allowed commands after run authorization only:** a version-pinned
approved interpreter already present on the host; the reviewer-owned fixture
test command; a reviewer-owned file-manifest check; and, only for registered
candidate conditions, an exact absolute-path Forge strict-validation invocation
or Factory `run-factory-cycle.py --once`. The actual argv are TBD and therefore
no command is presently allowed to execute.

**PROPOSED denied commands/actions:** package managers and installation;
OpenCode startup/load/registration; `git` mutation, remote operations, clone,
push, fetch, or sync; all network clients and `--live`; shells or arbitrary
subprocess arguments supplied by a task; home/global config paths; credential,
environment, keychain, or secret-file reads; services; `sudo`; and any path
outside the disposable root and read-only candidate source. The candidate
commands are permitted only after a reviewer verifies their exact argv and
write paths from the static inspection.

## Proposed sample, resource, and stopping budget

**PROPOSED exploratory sample:** 3 tasks × 4 conditions × 2 independent repeats = 24
condition-runs. T3 supplies 8 applicable controlled-failure/resume observations
(one per condition/repeat). Repeats use separately copied fixtures and a
counterbalanced condition order. A corrected fixture invalidates all affected
conditions and requires a complete rerun from the same correction.

**PROPOSED caps:** each condition-run has at most 20 active agent minutes, 10
minutes candidate setup/teardown, 12 human-review minutes, and 12,000 model
tokens. With six runs per condition, this is at most 120 active agent minutes,
60 setup/teardown minutes, 72 human-review minutes, and 72,000 tokens per
condition. Across 24 runs, the proposed maximum is 480 active agent minutes,
240 setup/teardown minutes, 288 human-review minutes, and 288,000 tokens.
The proposed model allocation is one identical, user-approved, version-pinned
primary model/route per run, with no subagent allocation. The model identity is
TBD. The proposed aggregate monetary cap is USD 60 in billed provider charges;
billing availability is unknown, and missing cost data makes cost comparison
insufficient rather than zero. Stop the affected run on any per-run cap and
stop all remaining runs on an aggregate cap, unapproved request, sensitive
action attempt, lost raw log, or repeated unresolved failure after T3's one
recovery attempt. Stopped runs remain evidence but are non-comparable and
cannot support ranking.

## Proposed measures, thresholds, and evidence minima

All acceptance checks are independently owned and frozen before the first
condition. Safety and OpenCode feasibility remain gates, not scored benefits.

| Dimension | PROPOSED primary unit, direction, and rule | Minimum evidence |
| --- | --- | --- |
| Correctness | Accepted-completion rate, favorable higher: independently accepted scheduled runs / all 6 scheduled runs, including stopped and failed runs. Non-inferior: no more than 1/6 below B0. Practical improvement: at least 2/6 above B0. Practical regression: at least 2/6 below B0. An unmet requirement, failed required check, or regression is not accepted. | Grade A raw output, frozen requirement map, file manifest, and independent acceptance for all six runs. |
| Reliability | Honest-outcome rate, favorable higher: accepted or correctly blocked scheduled runs / all 6 scheduled runs. A correctly blocked outcome is one where the independent reviewer confirms the frozen prerequisite checklist was not met and the handoff identifies the missing prerequisite and preserves the raw failure evidence. T3 recovery rate is reported separately as correct accepted-or-blocked outcomes / its 2 scheduled failure runs. A condition is comparable on reliability only when all 6 scheduled runs, including both T3 runs, have retained outcomes; otherwise reliability is insufficient. Non-inferiority, improvement, and regression use the same 1/6, 2/6, and 2/6 boundaries for the all-run rate. Repeated unresolved failure after the declared recovery is a gate failure. | Six scheduled runs and two T3 runs per condition, including missing/aborted outcomes. |
| Supervision | Autonomous-completion rate, favorable higher: accepted runs with no rescue / all 6 scheduled runs. Intervention density, favorable lower: intervention events / all 6 scheduled runs. Autonomous non-inferiority is B0 minus 1/6; improvement/regression are plus/minus 2/6. Intervention non-inferiority is B0 + 1 event/run; practical improvement/regression are respectively at least 2 fewer/more events over six runs. | Complete intervention log with trigger, actor, category, causal basis, elapsed time, and every scheduled run. |
| Admission quality | Candidate-only descriptive/gating measure, not B0-relative: false-block rate is Factory/Hybrid blocked verdicts that the independent reviewer finds had all frozen prerequisites / all 6 scheduled runs. A correctly blocked verdict has at least one frozen prerequisite absent and names it in the raw gate output. Any false block is a candidate gate failure. Report correctly blocked verdicts / all 6 scheduled runs separately; do not use either admission count for cross-condition noninferiority, practical improvement, regression, or dominance. | Raw gate output plus independent prerequisite checklist. N/A or missing data cannot support a favorable comparison. |
| Maintainability | Persistent-authority/dependency/configuration delta, favorable lower: count of required durable moving parts beyond B0. Any unapproved persistent authority, runtime dependency, global configuration surface, or recurring upkeep action is a gate failure. This exploratory count cannot establish superiority by itself. | Candidate setup/teardown record and reviewer explanation of each delta. |

An **intervention** is a human action or decision after a condition starts that
changes authority, task interpretation, state, or execution path. A **rescue**
is an intervention without which valid progress could not continue or would end
incorrectly. **Autonomous completion** means independent acceptance with no
rescue, not merely no human approval. A **false block** is a candidate blocked
verdict despite the independently frozen checklist showing every required
prerequisite was present. Missing output, unavailable billing, an aborted run,
or a zero denominator is unknown/N/A, never favorable.

The numerical margins are deliberately small-sample operational rules for this
24-run exploratory pilot. They make no statistical-superiority or production
claim. A condition is decision-eligible
only if every applicable gate passes, every named minimum is met, and raw
artifacts remain independently inspectable. An alternative can dominate B0 only
under the existing rubric's non-inferiority and practical-improvement rule.

## Proposed independent roles and approval blockers

- **Protocol reviewer:** freezes fixture hashes, requirements, order, exact
  argv, environment allowlist, resource allocation, and metric record before
  results.
- **Safety reviewer:** confirms source version, isolation boundary, write
  paths, no-secret/no-network controls, and stop decision for every near miss.
- **Acceptance reviewer:** owns fixture checks and evaluates outputs and
  intervention logs. This person cannot be the run implementer or a
  candidate-specific rescuer.
- **Trial operator:** creates copies and collects raw outputs only. The operator
  cannot alter fixtures after the first result.

Approval remains blocked on the user's selection of named people for these
roles. No assignment is implied by this draft. Approval to prepare requires
selection of the proposed sandbox mechanism, preparation root, and reviewers;
the sandbox verification is the preparation output and a run blocker, not a
preparation-approval prerequisite. Separate approval to run is blocked on
successful sandbox verification, frozen fixtures/hashes, exact argv and
paths, pinned interpreter/model/route, permissions, all budgets, safety
boundary, data-retention/deletion plan, and acceptance scripts. This proposal
requests no OpenCode load trace. Standalone Forge/Factory results cannot support
OpenCode adoption or replacement. Any such conclusion requires a separately
authorized, version-pinned compatibility and host registration/load trace.
