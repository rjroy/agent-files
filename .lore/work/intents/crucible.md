---
title: Crucible committed-change review
date: 2026-10-26
status: approved
tags: [crucible, independent-review, openrouter, opencode, arbitration]
related: [.lore/work/openrouter-independent-review-notes.md]
---

# Crucible committed-change review

## Purpose and motivation

Crucible is a dedicated OpenCode review plugin with its own controlled review process. It brings independent model perspectives to a committed change, subjects reported issues to challenge and arbitration, and returns a coherent report of the issues that remain open.

The user wants independent challenge without making the calling model configure special subagents or negotiate exceptions to oh-my-opencode-slim's delegation rules. The caller requests a review; Crucible owns reviewer execution, tools, stage progression, attribution, and results. Existing agents remain responsible for ordinary implementation and for acting on the report. Crucible is not a replacement workforce or permission to modify project source.

The earlier discussion included a comfortable initial OpenRouter budget of $25–50/month. That is conversational context, not a Crucible requirement. The user explicitly chose to control spending elsewhere to avoid complicating the plugin. Crucible does not own budget enforcement, monthly allowances, per-run financial admission, reservations, or shared spending ledgers. Useful findings and defensible decisions matter more than a volume of objections or model consensus.

## Configuration is a first-class capability

The most important configuration outcome is a file users can load from their global OpenCode configuration directory, with a project-specific configuration file overriding it. Users must be able to configure:

- The list of models participating as reviewers.
- A model serving as arbiter.

The caller should not have to choose or construct these roles for every invocation. Model selection belongs in user-owned configuration rather than being buried in prompts or hardcoded in the plugin.

Use `crucible.json` in the resolved global OpenCode configuration directory and `<project-root>/.opencode/crucible.json` for project overrides. These are Crucible's configuration locations, not a claim that OpenCode automatically loads them. Missing project fields inherit global values; a project reviewer list replaces the global list, and a project arbiter entry replaces the complete global arbiter entry. Do not concatenate reviewer lists. Validate configuration before model calls and freeze the effective configuration for each run.

Use OpenCode's existing model/provider integration and credential handling rather than building a separate provider layer. Credentials stay outside Crucible project configuration and persisted snapshots. Budget settings and enforcement are outside Crucible's scope. Exact configuration schemas belong in planning.

The user's preferred candidate models are GLM-5.3 and DeepSeek V4.1 Flash, with Sonnet 5.5 or possibly Opus 5.5 also under consideration. No fixed reviewer lineup or arbiter assignment has been chosen. Configure models supported by the user's OpenCode installation. Provider certification, compatibility probes, and repair of model integrations are outside Crucible's scope; report ordinary model execution errors rather than building a provider-testing framework.

## One committed change, one shared review target

Crucible reviews committed changes only. Uncommitted edits are not an eligible review target. The user should be able to identify a commit and know that every participant is reviewing the same change.

Each reviewer has read-only access to the project and receives the tools needed for its current review stage, explained as part of that stage. Read-only project access does not prevent the reviewer from recording issues or votes through Crucible's controlled tools. It does prevent source modification and use of ordinary implementation capabilities.

A necessary consequence of the shared-target goal is that project reads must correspond to the selected committed snapshot, not silently follow a changing working directory. Resolve the supplied commit to its full object ID and create one shared detached worktree per review run at that commit. Reviewers and the arbiter read that checkout; separate worktrees per reviewer are unnecessary while all participants are read-only. A custom Git-object filesystem is not required.

Keep two locations explicit throughout the run: the origin project owns configuration and persistent `.crucible` records; the review worktree supplies source context. Storage handlers always write to the origin, never infer their destination from a reviewer's working directory. The checkout is disposable, but participants still receive no source-write or arbitrary shell capabilities. Do not execute repository code, follow external symlinks, or automatically fetch submodules.

Keep the review worktree for the whole run, including arbitration and summary, then clean it up. On interruption, retain ownership information sufficient for safe later cleanup without deleting unrelated worktrees. Provide bounded baseline comparisons and access to previous or deleted content through a controlled Git operation or a separate baseline checkout; the exact mechanism remains a planning choice.

Compare a normal commit with its parent, a root commit with the empty tree, and a merge commit with its first parent. Disclose the baseline, especially for merges. Unrelated dirty working-tree changes are neither read nor reviewed and do not prevent review. The intent is review of the committed change with sufficient surrounding context, not an unrestricted audit of every pre-existing project issue.

## User-facing lifecycle

The proposed public entry points are:

```text
review_begin(commit_id)
review_rerun(commit_id)
review_abort(commit_id)
review_status(commit_id)
review_issue_read(commit_id, issue_id)
```

Starting a review should initiate the configured process without requiring the calling model to manage its participants. Status should make progress and incomplete or failed outcomes visible. Abort should stop further review work as far as the underlying execution permits and leave an honest record of what completed; it must not present partial work as a finished review.

Begin returns promptly with the resolved commit ID, run ID, and initial status. It is idempotent: repeated calls return the existing active or latest terminal review, rather than starting another run. `review_rerun(commit_id)` explicitly creates a fresh review after the previous run ends. Permit only one active run per commit; retain previous results rather than overwriting them.

Restart survival and automatic crash resumption are not requirements. If OpenCode stops or plugin execution is lost, preserve the records, mark the run interrupted, and let the user explicitly rerun it. Abort stops scheduling new work, interrupts participants where supported, and fences late responses against further review mutations. Stopping remote provider computation is not a Crucible guarantee or a separate research concern. Commit-only status and abort target the current run; precise stale-caller protection using a run-ID guard remains a possible interface refinement.

## Review process

### 1. Independent issue reporting

Each configured reviewer is told about the committed change and asked to review it using read-only project access. Findings are recorded through:

```text
review_issue_add(commit_id, summary, priority, code_source_list, description)
```

Reports should identify a material concern, supporting code locations, and enough explanation for another participant to assess it. A reviewer may find no issues; the process must not manufacture findings to fill a quota. The intended independent first stage should not anchor reviewers on one another's initial findings.

### 2. Deduplication and priority validation

The arbiter examines recorded issues, identifies duplicates, and validates priority before voting begins.

Represent duplicates as one canonical issue while retaining every original report, reporter, original priority, and source evidence. Keep links from duplicate issue IDs to the canonical issue and record the merge rationale. This preserves independent corroboration without counting the same defect multiple times. All originating reporters count as reporters of the canonical issue and cannot vote on it.

Provide an arbiter-only internal `review_issue_merge(...)` operation; its exact argument schema remains to be designed. Merge only the same underlying defect, not merely findings at the same source location. Deduplication must not erase distinct failure modes.

### 3. Peer voting

Each reviewer evaluates issues it did not report and records a vote through:

```text
review_issue_vote(commit_id, issue_id, verdict, reason)
```

The user selected **any reject vote** as the trigger for reporter response. This is not majority voting: one reasoned objection is enough to mark an issue contested and send it to the next stage. It is not enough to silently discard the issue.

Use `approve`, `reject`, or `abstain` as the verdict. Votes need reasons that can be examined. Approval is a review opinion, not proof that an issue is valid. Every eligible reviewer approving leaves the issue open as peer-supported. Abstention records an evidence gap; a failed reviewer or missing vote records missing coverage, never approval. If no non-reporting reviewer is eligible, the arbiter explicitly assesses validity.

Distinguish a priority objection from a validity rejection: disagreement about severity must not silently reject the underlying defect. The exact representation belongs in tool-schema design. Keep run completeness separate from issue disposition: the arbiter may resolve an issue despite missing votes but cannot substitute for a failed participant's independent review.

### 4. Reporter response

Reporters examine rejected/contested issues. They either agree with the rejection:

```text
review_issue_remove(commit_id, issue_id, reason)
```

or request arbitration:

```text
review_issue_arbitrate(commit_id, issue_id, reason)
```

The user selected **retained history** for removal. Despite its name, remove means closing an issue as withdrawn or rejected and omitting it from the open-issue report, not physically deleting its JSON or losing reports, votes, and decisions.

For an issue with multiple reporters, reporter removal withdraws only that reporter's endorsement. Automatically close as withdrawn only when all reporters explicitly withdraw. Any reporter can preserve the issue for arbitration; missing responses are not withdrawals. One reporter must not erase another reporter's attribution. Keep the initial process to one reporter-response round and one arbitration round, retaining dissent rather than introducing appeal loops.

### 5. Arbitration

The arbiter reviews issues referred for arbitration, including the issue evidence, rejection reasons, and reporter responses. Rejections the arbiter validates are closed through `review_issue_remove(commit_id, issue_id, reason)` with history preserved. Issues upheld by the arbiter remain open. The arbiter receives the same read-only target/baseline access as reviewers plus all reports, votes, responses, and coverage limitations.

Provide an arbiter-only internal `review_issue_decide(...)` operation for priority validation/change and explicit upholding. Its exact schema remains to be designed. Decisions retain actor, stage, rationale, and supporting evidence; preserve original priorities alongside changes. The arbiter may overrule reviewers but must explain why. These decisions must remain inspectable, not exist only in a transient model response. Arbitration concerns issue validity and disposition; it does not approve a code change or authorize a fix.

### 6. Summary

The arbiter generates a summary from all remaining open issues. Compute the open-issue list from stored state so summary prose cannot silently omit a finding. The summary must agree with that state, explain material unresolved limitations, and distinguish a completed review with no open findings from an incomplete review.

### 7. Report delivery

Crucible returns the report and the list of open issues. The caller can retrieve each issue using `review_issue_read(commit_id, issue_id)` and decide what follow-up work is appropriate. Closed issue history remains retained even though the final actionable list contains open issues only.

## Attribution and tool authority

Crucible assigns a stable participant identity and binds each tool invocation to run, participant, role, and stage. Store the configured model separately. Do not add a model-supplied `reviewer_id` as authority for authorship or voting eligibility.

For native OpenCode reviewer sessions, map the tool invocation's session ID to the Crucible run, participant, and role. Agent names alone are insufficient because several sessions may use the same agent or model. Use this execution context for normal author/voter validation; a model-supplied identity is unnecessary. Exact session creation and tool restriction integration still need to be established during planning.

Stage-appropriate tools enforce participant and phase permissions, not merely describe them in a prompt. Reviewers must not vote on their own reports, impersonate another participant, or mutate unrelated review records. Arbiter merge and decision operations are role-restricted; neither role can modify project source.

## Local, inspectable, uncommitted review records

Issue records live in the original consuming project, not the temporary review worktree, at:

```text
.crucible/reviews/<commit_id>/<issue_id>.json
```

When Crucible first saves files, it must create or safely update `.crucible/.gitignore` so the reviews directory is ignored. Within that file, an anchored `/reviews/` rule expresses the requested exclusion. Ignore protection must be in place before review artifacts are left on disk.

The user intends review output to remain local and not enter Git. Ignore rules do not remove already tracked files; an existing tracked review path must be surfaced rather than silently treated as protected. Crucible should not alter unrelated ignore rules or remove files from Git without authorization.

Use issue IDs unique across reruns. Store run manifests and summaries at `.crucible/reviews/<commit_id>/_runs/<run_id>.json`, retaining old issue records and links. Persist sufficient non-secret configuration, participant, stage, and decision context to reconstruct the review. All generated review state remains beneath `reviews/`.

Only Crucible writes these records; reviewers request mutations through tools rather than writing JSON directly. Serialize mutations and use atomic writes so concurrent reporting cannot lose state. Verify ignore protection before persistence and surface already tracked artifacts as a blocker rather than silently treating them as ignored. `.crucible/.gitignore` itself may remain trackable; the plugin does not commit it or decide the repository's tracking policy.

## Boundaries and what success means

Success means the user can configure reviewers and an arbiter globally, override that configuration for a project, start a review of a commit, inspect or abort progress, and receive a defensible list of open findings without orchestrating the participants manually.

Every issue should remain traceable to its reporters, source evidence, votes, and disposition. Reviewers see the same committed content and cannot modify project source. Duplicate handling preserves useful attribution. A single objection receives consideration without automatically invalidating the report. Removed findings remain auditable locally.

The plugin should remain compatible with the existing workforce boundary: omo-slim coordinates ordinary agents; Crucible conducts its own bounded review. Prefer dedicated native OpenCode reviewer and arbiter sessions so OpenCode owns model integration and the agent/tool loop. Crucible owns their instructions, role/stage permissions, session-to-participant mapping, workflow, and records. These sessions must not be redirected into omo-slim's ordinary delegation workflow. How to establish that isolation is the remaining host integration question, not a reason to assume native sessions cannot work.

The documented `ctx.generate.text` helper does not invoke tools, so it is not itself a reviewer execution loop. Use tool-capable session execution rather than equating text generation with agent execution. Direct OpenRouter calls are an alternative only if a concrete native-session limitation requires revisiting the direction; they are not the settled default. A companion skill explains invocation and interpretation, not orchestration of internal stages through ordinary subagent calls.

Budget management is explicitly out of scope. Do not add per-run dollar allowances, monthly application budgets, budget reservations, financial admission checks, or cross-project spending ledgers. The user controls spending outside Crucible.

Bounded execution and incomplete-run handling remain Crucible responsibilities. Do not silently substitute configured models. Operational timeouts and retry limits are reliability controls, not a reason to reintroduce financial enforcement. A minimal initial configuration can use two reviewers and one arbiter, while the actual lineup remains user-configurable.

Integration checks should verify Crucible's own behavior: records go to the origin rather than the review checkout, work continues after begin returns, and status/abort address the correct run. Do not expand these into general tests of whether OpenCode works, provider certification, or a restart-durable worker system. Use existing OpenCode model/provider capabilities and surface failures honestly.

## Relationship to prior notes

The earlier OpenRouter notes remain useful motivation, especially independent challenge and separation from omo-slim delegation. Current direction supersedes their single-response, packet-only reviewer with no filesystem tools: Crucible now has multiple participants, staged project-read access, voting, arbitration, and persisted issue records. Their proposed in-plugin financial controls are also superseded: budget management remains external.

The user accepted the recommended defaults with the explicit exception of budget management, which is excluded. Subsequent clarification selects a shared detached review worktree with records in the origin, favors native OpenCode reviewer sessions, and excludes provider certification and restart survival. These choices supersede the research's earlier preference for a custom Git-object reader and direct OpenRouter tool loops. This document captures present direction for planning, not an implementation plan, finalized tool schema, or authorization to build or configure the plugin. Remaining planning details include exact tool and configuration schemas, priority-objection representation, native-session isolation from omo-slim, worktree cleanup/baseline access, and operational failure handling.
