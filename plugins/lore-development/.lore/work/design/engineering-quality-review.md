---
title: Engineering quality review through progressive disclosure
date: 2026-11-03
status: draft
tags: [engineering-quality, implementation, review, progressive-disclosure]
---

# Engineering quality review through progressive disclosure

## Decision

Introduce an explicit engineering-quality assessment into substantive implementation, using dedicated guidance in lore-development rather than adding reviewer agents by default.

Use progressive disclosure: `COMMON.md` establishes the expectation and points to `implement`; `implement` owns sequencing and routing; a dedicated review skill owns the deeper judgment criteria. Reuse existing specialists in independent review invocations.

This document records the proposed design. It does not authorize edits to active instructions, skills, or agent configuration.

## Problem

Functional verification establishes whether the requested behavior works. It does not establish whether the implementation is a good engineering solution.

A working implementation can still introduce unnecessary complexity, obscure responsibilities, duplicate an existing mechanism, or create avoidable maintenance and performance costs. A process centered on generating a solution and validating acceptance can stop before examining those concerns.

The current `skills/implement/SKILL.md` includes independent review, but describes refactoring as optional and emphasizes concrete material defects or risks. That protects against speculative cleanup, but does not explicitly require considering a materially better approach after correctness is established.

The missing distinction is between:

| Activity | Question |
|---|---|
| Functional verification | Does the change behave correctly, and what evidence supports that? |
| Engineering-quality assessment | Is this a good solution under the actual constraints? |
| Targeted refinement | Which improvements justify changing the working implementation now? |

## Guidance layers

### COMMON.md: expectation and entry point

Add a short principle under engineering judgment, with a clear pointer to `implement`. Keep detailed process out of always-loaded instructions.

Suggested wording, subject to implementation review:

> When coordinating substantive implementation, follow the `implement` skill. Delegated workers execute their assigned roles within that workflow; they do not restart it. Correct behavior is necessary but not sufficient: assess the solution's maintainability, complexity, and relevant efficiency before declaring completion. Scale the depth to the change.

### implement: coordination and stopping rules

Make engineering-quality assessment explicit after functional verification. Keep correctness review and its existing safety and compatibility concerns intact.

`implement` determines the appropriate review scope, loads dedicated guidance, selects a suitable independent reviewer, routes accepted improvements to a writer, and requires renewed verification of changed behavior.

The coordinating invocation owns this entry-point obligation. Its delegated writers, testers, and reviewers follow their bounded assignments and applicable role guidance, rather than invoking `implement` as new coordinators. Delegation briefs carry the relevant quality expectations and evidence requirements to those workers.

Extract detailed review mechanics where practical rather than appending another large checklist. The coordinator should describe when and why to invoke deeper guidance, not reproduce it.

### Dedicated skill: engineering-quality review

Start with one skill focused on engineering judgment. Its final name is an implementation detail.

The skill should support read-only independent review and evaluate:

- **Problem and approach:** Does the solution address the underlying problem rather than accumulate patches around it?
- **Architectural fit:** Does it strengthen the agreed architecture and reuse appropriate existing capabilities?
- **Maintainability:** Are responsibilities and dependencies understandable? What will the next likely change require?
- **Complexity:** Can mechanisms, branches, duplication, or indirection be removed without sacrificing required capability?
- **Efficiency:** Are there avoidable operations, allocations, queries, dependencies, or boundary crossings?
- **Performance:** Are there credible bottlenecks, and which claims require measurement?
- **Alternatives:** Would a concrete alternative deliver enough benefit to justify the change and its risks?

Not every review needs findings in every category. These are lenses, not quotas.

Reuse existing implementation and behavior-preserving simplification guidance for resulting edits. Introduce a separate refinement skill only if a distinct reusable workflow proves necessary.

## Execution model

For substantive implementation:

**Build → functional verification → independent review of correctness and engineering quality → targeted refinement when worthwhile → renewed verification and focused review of corrections.**

Engineering quality is a distinct question, not necessarily a second reviewer invocation. A suitable independent reviewer can address both correctness and quality when its contract supports both. Preserve existing procedure contracts; do not silently override a defects-only reviewer with incompatible instructions.

Use existing technical reviewers such as `oracle` where appropriate. A separate review invocation is more important than a new agent name: it reduces attachment to author decisions, although shared model blind spots remain possible.

Give reviewers the current request, relevant constraints, implementation and affected consumers, and verification evidence. Do not supply an expected verdict. Reviewers return findings; writers make changes.

For small, obvious changes, use a lightweight quality check rather than a mandatory deep review. Increase depth for architectural changes, complex behavior, cross-boundary work, or performance-sensitive paths. Do not repeat broad review after every narrow correction unless the accepted scope materially changes.

## Review outcomes and refinement boundaries

A useful improvement recommendation identifies the observed cost, supporting evidence, a bounded alternative, expected benefit, and relevant trade-offs. Performance concerns distinguish measured facts from hypotheses and suggest focused measurement where needed.

Material defects remain correction obligations under the existing review process. Quality recommendations are not automatically blockers: select changes according to demonstrated benefit, implementation cost, regression risk, and the user's direction. Explain consequential recommendations that are deferred or rejected.

The reviewer may conclude that the implementation works but its approach should change. If that would depart from the agreed architecture or requires a consequential unresolved choice, discuss it with the user before proceeding.

The reviewer may also conclude that no worthwhile refinement is needed. Do not invent objections, demand speculative future-proofing, or turn personal style preferences into quality failures.

Retain bounded correction loops and escalation. The stopping criterion is not global optimality: the implementation is verified, material findings are resolved or explicitly escalated, and plausible worthwhile improvements have been considered and dispositioned.

## Alternatives considered

- **Add dedicated reviewer agents immediately:** Could provide durable permissions and role separation, but duplicates existing specialist capabilities without first fixing the process contract. Revisit if role separation proves difficult to sustain.
- **Expand COMMON.md with the complete process:** Highly visible, but increases always-loaded context and creates competing process authorities.
- **Only strengthen the existing defects checklist:** Smaller edit, but risks treating design quality as defect detection and missing justified alternative approaches.
- **Require refactoring after every change:** Forces edits even when review finds no worthwhile improvement and encourages polishing loops.

## Validation of the eventual guidance

Check representative tasks against the revised instructions:

- A correct but unnecessarily complex implementation receives an evidence-backed improvement recommendation, not automatic acceptance because tests pass.
- An adequate implementation can finish without manufactured findings or mandatory edits.
- A small change gets proportionate scrutiny rather than a heavyweight review pipeline.
- A speculative performance concern requests evidence instead of asserting a bottleneck.
- A refinement is reverified, while an architectural departure triggers discussion before implementation.
- Existing correctness review, project-selected reviewers, and procedure contracts remain intact.
- COMMON.md, implement, and the dedicated skill have clear ownership without duplicating the detailed workflow.
- A delegated implementation worker executes its assignment without restarting the orchestration workflow or recursively delegating because of the COMMON.md pointer.

These checks validate the intended behavior of the guidance. Static document checks alone cannot establish that agents will consistently exercise better engineering judgment.
