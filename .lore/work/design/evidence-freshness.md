---
title: Evidence-freshness receipt decision
date: 2026-09-11
status: approved
tags: [workflow, evidence-freshness, validation, acceptance, no-change]
related: [.lore/work/research/workflow-comparison-review.md, .lore/work/research/workflow-comparison-baseline-evidence.md]
---

# Evidence-freshness receipt decision

## Decision

**Do not add a native evidence-freshness checker or receipt now.** A supplemental,
repository-owned checker could add value without replacing reviewer judgment or
becoming a completion authority. It could deterministically flag missing
obligation references, evidence that targets an older snapshot, and an
accepted-manifest mismatch. The record does not show a manual reconciliation
failure or a drift class that the required terminal review and commit-safety
process failed to catch. Its benefit is therefore prospective, while schema
upkeep and false blocks are immediate costs.

This is a no-change design decision, not a claim that a native checker exists or
that the current instructions have been exercised by OpenCode. The current
mechanisms are prose contracts in skill source. Their execution and effectiveness
remain unobserved. The only executable comparison source examined is Forge, and
it is not to be imported.

## Existing boundary and evidence

The current workflow already assigns the relevant responsibilities:

| Concern | Existing contract | What it enforces today |
| --- | --- | --- |
| Obligation coverage | `plan-breakdown` requires a requirement-to-task-to-evidence matrix, and `define-validation` requires an executable check and named evidence for every source requirement. | Planning and validation mapping, as authored instruction rather than executable validation. |
| Evidence and reviewer decision | `implement` requires an obligation-to-evidence table, phase-specific testing, an independent review role, correction verification, and one terminal acceptance review that reconciles every source obligation. | A reviewer, not a new receipt, is the authority that determines whether the evidence supports acceptance. |
| Evidence-to-terminal freshness | `implement` requires phase-specific tests, review, corrections, a complete obligation-to-evidence table, then a terminal acceptance review that reconciles every source obligation. | A manual, temporal reconciliation: terminal review must decide whether evidence and reviewer decisions still support the then-current accepted surface. This is an instruction, not machine enforcement. |
| Acceptance-to-commit equality | Only after acceptance, `implement` requires notes to record an accepted manifest containing changed paths, exact porcelain status, index identity or marker, and working-tree content hashes, including untracked files. Commit safety recomputes that same manifest and requires exact equality. | Equality detects drift after the accepted snapshot. It does not prove that earlier phase evidence remained applicable through later phases; terminal review has that manual responsibility. |

Sources: `plugins/lore-development/skills/plan-breakdown/SKILL.md` lines 18-27;
`plugins/lore-development/skills/define-validation/SKILL.md` lines 16-30; and
`plugins/lore-development/skills/implement/SKILL.md` lines 46-51, 63-84, and
98-103. The comparison review reaches the same bounded conclusion: any value
would only be an automated join, and it must be rejected if existing targeted
review and accepted-manifest equality already detect the relevant drift
(`.lore/work/research/workflow-comparison-review.md` lines 21-24).

## Potential value, retained manual responsibility, and cost

A native receipt would need to join four facts:

1. the source obligation identity and its task or phase;
2. the executable validation result and evidence;
3. the independent reviewer decision, including any correction verification;
4. the accepted manifest that binds the accepted result to Git index and
   working-tree content.

Those facts are already required in the implementation notes and task artifacts,
but their join is manual. A small checker could reliably detect mechanical
defects: an obligation with no evidence reference, an evidence record whose
declared target differs from the terminal snapshot, a reviewer record naming an
obsolete evidence target, or an accepted-manifest mismatch. It would report those
facts to the terminal reviewer and commit-safety operator. It would not accept,
reject, change Beads state, or decide whether a behavioral check is sufficient.

That boundary is potentially useful at a different time than manifest equality.
Before terminal acceptance, a later phase can alter a file relevant to an earlier
phase's evidence. Exact equality cannot detect this because no accepted manifest
exists yet. Terminal review must manually reconcile it. After terminal acceptance,
manifest equality detects a changed index or worktree before commit but does not
reconstruct whether the earlier evidence applied during terminal review.

The benefit is more reliable and repeatable reconciliation of declared links, not
replacement of the reviewer. The cost is defining stable IDs and snapshot targets
across specs, plans, tasks, notes, test reports, review records, partially staged
paths, and untracked files. A missing optional reference, an intentional
documentation-only change, or a generated tracker export can cause a false block
unless the checker has narrowly defined exemptions. Given no observed manual
reconciliation failure, no executed current workflow, and no evidence that this
mechanical check catches a failure missed by terminal review, that tradeoff does
not justify a new schema and checker now.

Forge demonstrates why a machine receipt can be useful in a different system,
not why it is needed here. Its strict validator hashes report, source, graph, and
artifacts; it rejects stale verification and stale acceptance receipts
(`tmp/local-marketplace/forge/scripts/forge/validation.py` lines 85-146). Its
checked-in tests cover bare passing claims, missing acceptance, and artifact drift
(`tmp/local-marketplace/forge/tests/test_validation_strict.py` lines 25-42,
73-126). Forge also owns a graph and verification state model. This repository
does not have that model, and importing its graph, state, schema, or validator is
out of scope. The comparison evidence explicitly classifies current workflow
mechanisms as instruction source, not observed runtime enforcement
(`.lore/work/research/workflow-comparison-baseline-evidence.md` lines 489-504).

## Acceptance-criterion disposition

| Criterion | Disposition under no change |
| --- | --- |
| Authoritative inputs | No new inputs or authority are introduced. Beads remains task/dependency authority, Git remains source authority, source/task/notes artifacts carry obligations and evidence, and terminal independent review remains the acceptance decision. |
| Obligation, reviewer, and manifest join | The required manual join is the `implement` obligation-to-evidence table, evidence and reviewer decisions, terminal acceptance review, and accepted manifest. A potential supplemental receipt could verify declared references and snapshot targets, but would report to, not replace, the reviewer. No receipt is added because a manual-reconciliation failure has not been evidenced. |
| Relevant-change invalidation | Before terminal acceptance, the reviewer manually determines whether later changes stale earlier evidence. After acceptance, exact accepted-manifest inequality invalidates commit readiness and requires validation and review of the delta. No checker-specific rule is introduced. |
| False-block handling | Existing handling is narrow: if a later hook changes only a generated tracker export, inspect and report that change narrowly rather than rerunning the workflow. A new checker would need comparable exception policy and therefore creates false-block risk without demonstrated benefit. |
| Rollback or removal | No artifact, schema, command, or configuration is added, so rollback is unnecessary. The decision is reversible: a later, evidenced design can supersede this document without data migration or cleanup. |
| Focused behavioral validation | No runtime implementation is authorized, so no checker test is applicable. A later proposal must test missing references, obsolete evidence/reviewer targets after a relevant later-phase change, manifest mismatch after acceptance, permitted generated-export handling, and removal with no effect on Beads, Git, or terminal review. |

## Guardrails and revisit threshold

This decision does not relax the existing contracts. Planning still maps each
requirement to executable evidence, and implementation still records obligation
coverage, testing, independent review, terminal acceptance, and an accepted
manifest. It also does not assert that these instructions were loaded or followed
in any particular host session.

Reopen this design after repository evidence shows either a repeated, material
manual reconciliation failure or a concrete mechanical drift case that a receipt
would have caught. The evidence must distinguish a later-phase evidence-to-terminal
freshness failure from post-acceptance manifest inequality, and show why the
existing terminal review or commit-safety step did not catch it at the relevant
time. A follow-up must define Git- and notes-derived inputs, reviewer reporting
only (not another acceptance authority), false-block exceptions, removal path,
and the focused behavioral tests listed above. It must not import Forge, run a
workflow trial under this issue, or change OpenCode.
