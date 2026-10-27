---
title: Crucible feasibility in OpenCode V2
date: 2026-10-26
status: completed
tags: [crucible, opencode-v2, openrouter, feasibility]
related: [.lore/work/intents/crucible.md, .lore/work/research/crucible-opencode-v2-host.md, .lore/work/research/crucible-reviewer-runtime.md]
---

# Crucible feasibility in OpenCode V2

## Key Findings

Crucible's intended behavior appears implementable as an OpenCode V2 server plugin. No reviewed requirement establishes a fundamental platform incompatibility. This is documentation-based feasibility, not a tested compatibility claim for the installed host.

OpenCode provides the extension surface: plugin setup/cleanup, custom tools, skills, permission assertions, integration connections, and optional RPC. Crucible must supply the review engine: per-participant OpenRouter tool loops, immutable project reads, identity and authorization, seven-stage orchestration, issue persistence, and cancellation state.

The cleanest fit is public OpenCode tools backed by a Crucible-owned runner, with direct OpenRouter requests and private participant-facing function tools. Do not route reviewers through ordinary omo-slim subagents. RPC is optional for future non-model consumers, not required to expose begin/status/abort and not a durability mechanism.

The largest remaining host uncertainty is correct project/worktree scoping combined with lifecycle behavior on reload. The largest provider uncertainty is the exact selected endpoint's tool-call behavior. Both warrant small focused probes before a full implementation.

Budget enforcement remains explicitly outside the plugin's scope.

## Requirement mapping

| Intent | Feasibility and what is needed |
|---|---|
| Global `crucible.json` and project override | Ordinary plugin-owned file loading and validation. OpenCode does not automatically discover this custom filename. Read at begin/rerun, apply the approved replacement rules, and freeze effective configuration. Verify global config-directory and project-root discovery. |
| Configurable reviewers and arbiter | Send a selected model on each OpenRouter request. Crucible owns stable participant IDs and independent transcripts. Model/provider support needs checking for the configured routes. |
| Read-only project access at a commit | Implement a controlled Git-object reader for target and baseline. Ordinary working-directory read tools are not sufficient. No general shell is exposed to models; internal validated Git subprocesses are a different matter and must avoid arbitrary command construction and external diff/text-conversion behavior. |
| Reviewer tools explained per stage | Supply private JSON function definitions and stage instructions in each participant request. Crucible parses, authorizes, and executes returned tool calls. Do not register participant mutation tools in the public OpenCode registry. |
| Attribution without reviewer-supplied ID | Bind the dispatcher to the run/participant/role/stage before inference. Model arguments cannot override that identity. OpenCode caller session identity and Crucible reviewer identity are different concepts. |
| Duplicate merging, votes, withdrawal, arbitration | Implement the approved state transitions and eligibility rules in application code. Model conclusions are proposals; handlers validate and persist them. No platform voting API is needed. |
| Final summary and issue reads | Compute open issue IDs from persisted state. Give the arbiter a read-only summary task and validate its response. Strict structured output is optional assistance where supported, not the authority for issue state. |
| Begin returns promptly; status/abort/rerun | Public custom tools can delegate to a plugin-owned runner and persisted run registry. Run-owned cancellation must be separate from the invocation signal. Test continuation after tool return and cleanup behavior. |
| JSON files and retained history | Use ordinary filesystem persistence at the approved paths, atomic writes, serialized mutations, and active-run ownership. Native plugin JSON storage does not replace the required visible project files or establish locking guarantees. |
| Ignore review artifacts | Create/update `.crucible/.gitignore` before output, verify effective exclusion, and detect already tracked artifacts. This is ordinary Git/filesystem work, not a missing OpenCode capability. |
| Companion skill | V2 documents both normal skill discovery and `ctx.skill.transform`. Package/discover the skill without asking it to drive the internal review stages. |
| Coexistence with omo-slim | Direct model requests avoid ordinary agent delegation hooks/tool loops. The initial public tool still needs to remain discoverable and permitted under the installed plugin configuration; coexistence requires a host check. |

## Recommended architecture

```text
OpenCode caller / companion skill
    → public Crucible tools: begin, status, abort, rerun, issue read
    → Crucible run manager and persisted review state
        → independent participant OpenRouter request loops
        → private stage-scoped tool dispatcher
            → pinned Git target/baseline reader
            → validated issue/vote/arbiter operations
    → state-derived report and open issue IDs
```

This creates two separate tool surfaces. A main-session model can request a review or inspect its results. A reviewer can access only the private operations supplied to its current request and authorized by its bound dispatcher. The caller cannot impersonate a reviewer merely by invoking a globally registered `review_issue_add`, because that mutation is not part of the public registry.

OpenRouter supplies inference and proposed function calls. Crucible executes the functions and sends results back. Neither OpenRouter nor OpenCode supplies Crucible's stage machine, canonicalization policy, participant permissions, or exactly-once mutation handling.

## What will not work as assumed

### A tool-free generation helper cannot run a tool-using review

The V2 plugin guide explicitly describes `ctx.generate.text` as generation without invoking tools. It may be useful for tool-free text generation, but does not itself implement the reviewer protocol. Normal OpenCode sessions do provide an agent loop, but reintroduce host tool and agent configuration concerns. Direct OpenRouter requests are the cleaner boundary for this intent.

### A commit ID does not pin ordinary filesystem reads

Reviewing a fixed diff while reading surrounding code from the working directory can expose different evidence to different reviewers. Read target and baseline Git objects through Crucible's controlled tools instead. Missing native snapshot APIs are not evidence that this is impossible to implement.

### Tool schemas and hidden tools are not authorization

The model can return malformed or unauthorized calls. Validate run, role, stage, issue eligibility, arguments, and source references independently of the advertised tool list. Repository content is evidence, not authority to change instructions or access.

### Asynchronous work is not restart durability

The official plugin guide demonstrates background event subscriptions and timers with cleanup, so plugin-owned asynchronous activity is an established pattern. It does not promise arbitrary work survives plugin reload or process exit. Persist progress, cancel/fence work on cleanup, and mark abandoned runs interrupted. This matches the approved exclusion of automatic crash resumption.

The exact behavior after a begin tool returns and when its calling session stops still needs testing. Adding RPC does not solve this lifecycle question.

### Cancellation cannot guarantee remote compute stops

Crucible can stop scheduling and accepting mutations immediately. Whether an outstanding model request stops computing depends on transport and provider behavior. Preserve incomplete state and fence late replies rather than treating a local abort as proof of remote cancellation.

### Model-family support is not endpoint support

Provider endpoints may differ in function-calling options and structured output. Catalog flags are useful discovery data, not an end-to-end guarantee. Do not freeze earlier GLM/DeepSeek aliases or reported capabilities into the design without rechecking the chosen routes. Avoid requiring forced tool choice or strict final JSON where an otherwise suitable route does not support it; always validate the actual output.

## Important host evidence and qualifications

The current official plugin guide documents `ctx.tool.transform`, input schemas, progress reporting, and `context.signal`. Its permission example also uses `context.sessionID`, `context.agent`, `context.messageID`, and `context.id`. Thus caller identity is not wholly undocumented. The exact installed type contract and mapping from caller session to project/worktree still need validation.

`ctx.location` describes the plugin instance's location, explicitly not every session it can access. Do not equate that field with the invoking session's directory without checking. A global installation must place configuration and review output in the right project even when sessions move or multiple projects are open.

The guide documents `ctx.integration.connection.active` and `.resolve`, providing a candidate path to reuse a configured credential. Whether the installed OpenRouter integration yields the credential form needed for direct calls remains to be established without exposing secrets. An explicitly supplied environment credential is an alternative design choice, not an excuse to inspect or copy credential stores.

Existing model requests capture executable tool snapshots. Removing a tool registration is therefore not enough to invalidate an already captured executor. Run/stage checks and cancellation fencing must live inside handlers.

## Smallest useful feasibility probes

Before building the full workflow, a separate authorized spike should establish:

1. A public begin tool returns immediately while a mock run continues, with status and explicit abort working correctly.
2. Session stop, plugin reload, and service restart each produce the intended interruption semantics and no late issue mutations.
3. Two projects, nested directories, and worktrees resolve the correct configuration and output paths. Concurrent begin calls cannot create duplicate active runs.
4. A synthetic Git fixture remains stable under dirty working-tree changes; root, merge, deleted-file, and symlink cases obey the snapshot policy.
5. Mock model tool calls cannot impersonate participants, vote on authored issues, mutate in the wrong stage, or replay a mutation.
6. After separate approval for actual inference, each selected provider route performs a small non-sensitive function-call round trip and final response. Test capability failures and cancellation honestly.

Most probes can use mock inference and test-owned repositories. None were performed during this research. No paid calls, runtime configuration changes, installations, or implementation were authorized or undertaken.

## Sources and companion reports

- [OpenCode V2 plugin guide](https://opencode.ai/v2/docs/build/plugins/) directly inspected during synthesis: lifecycle, background examples, tools, captured tool snapshots, credentials, skills, permissions, session identity examples, and tool-free generation.
- [OpenCode V2 configuration](https://opencode.ai/v2/docs/config/).
- [OpenCode V2 plugin RPC](https://opencode.ai/v2/docs/build/plugins/rpc/).
- [OpenRouter client-side function calling](https://openrouter.ai/docs/guides/features/tool-calling.md).
- [OpenRouter streaming/cancellation](https://openrouter.ai/docs/api_reference/streaming.md).
- [OpenRouter provider selection](https://openrouter.ai/docs/guides/routing/provider-selection.md).
- Host evidence and detailed probes: [crucible-opencode-v2-host.md](crucible-opencode-v2-host.md).
- Reviewer protocol and provider evidence: [crucible-reviewer-runtime.md](crucible-reviewer-runtime.md).

The detailed reports distinguish documentation findings from implementation inferences. This synthesis does not authorize implementation or amend the approved intent.
