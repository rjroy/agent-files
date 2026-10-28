---
title: Crucible native-session execution boundary
date: 2026-10-27
status: draft
tags: [crucible, opencode-v2, native-sessions, tool-authorization, omo-slim]
related: [.lore/work/intents/crucible.md, .lore/work/research/crucible-feasibility.md, .lore/work/research/crucible-opencode-v2-host.md, .lore/work/research/crucible-reviewer-runtime.md]
---

# Crucible native-session execution boundary

## Decision in brief

Use dedicated **native V2 root sessions**, explicit configured models, and Crucible-owned tools and run supervision. Native sessions can supply the agent/tool loop; a separate OpenRouter loop is not needed by the verified APIs.

There are two important qualifications:

1. **Agent creation is supported through `AgentEditor.update`, not an invented `add` method.** The V2.2.0 implementation creates a default agent when the ID is absent. Crucible must replace its permissive defaults. [AGENT]
2. **The installed omo-slim 3.0.5 does not give these sessions an untouched execution boundary.** Distinct root sessions avoid its child-profile routing, but its V2 bridges still run global message and tool-result transformations. Recommend a small, explicit omo-slim exclusion contract before enabling same-host Crucible execution. Do not build a chain of later hooks that tries to undo another plugin's edits. This contract is a proposed compatibility prerequisite, not an existing API. [OMO]

The result is a **conditional native-session design**, not a claim that the current installation is ready to run Crucible unchanged. The condition concerns coexistence, not model/provider certification.

## Scope and evidence

This design addresses only the execution boundary. The approved intent supplies the seven stages, issue semantics, configuration precedence, one shared detached worktree, and origin-owned records. It supersedes the earlier research's direct-OpenRouter and Git-object-filesystem recommendations. This document does not redesign stages or settle detailed schemas, cleanup algorithms, or the implementation/test sequence. Budgets, provider certification, and restart survival remain out of scope.

Evidence checked on **2026-10-27**:

- `opencode --version` returned `opencode v2.2.0`; the installed `@opencode/cli/package.json` also says `2.2.0`.
- Current official V2 documentation now separates the plugin overview from the [server API][SERVER]. Relevant signatures were checked against public source at release tag `v2.2.0`, commit `1097e2668b1e08ad63bdf0b1c4860b9bc01e420c`. Source behavior is not a runtime test of the installed binary.
- The host log records omo-slim **3.0.5**, build time `2026-10-18T19:03:48.182Z`, setting up on host **2.2.0**. Its loaded package exports `./server` and a default object with `id`, V1 `server`, and V2 `setup`. The retained V1 dependencies do **not** make this a V1-only plugin. The older `packages/oh-my-opencode-slim@latest` cache contains **2.2.25** and is not the loaded artifact used here. [LOCAL]
- The readable, loaded 3.0.5 server bundle was inspected directly. Its SHA-256 is `e04dd74f4115c721a5fc2b31f14b129834120eb9fcf13d97285ab744eab42a3d`. Citations to its line numbers below refer to that artifact, not a presumed latest upstream implementation. [OMO]

The `design` skill and Lore frontmatter schema were read. Loading the requested `opencode` skill was denied by the tool; official V2 documentation and source supplied the API evidence instead. No private agent/profile prompt was read. No configuration changes, installs, inference, executable spike, or commits were performed.

## Verified V2 contracts

### Dedicated agents and model selection

The public plugin interface declares: [AGENT-API]

```ts
interface AgentEditor {
  list(): readonly Types.DeepMutable<Agent.Info>[]
  get(id: string): Types.DeepMutable<Agent.Info> | undefined
  default(id: string | undefined): void
  update(id: string, update: (agent: Types.DeepMutable<Agent.Info>) => void): void
  remove(id: string): void
}
```

There is no `AgentEditor.add`. Nevertheless, the implementation of `update` is explicitly an upsert:

```ts
const current = editor.agents.get(id) ?? (Info.default(id) as Types.DeepMutable<Info>)
if (!editor.agents.has(id)) editor.agents.set(id, current)
fn(current)
current.id = id
```

Thus a plugin can create its own agent IDs through `ctx.agent.transform` → `editor.update`. This is **verified release-source behavior**, less explicit than the documentation's wording “update.” It should be a pinned compatibility assertion, not generalized to arbitrary future versions. The default agent permits all actions; do not inherit that policy accidentally. Explicit ID selection in this release does not apply the visibility/default-selection filter. [AGENT] [AGENT-SCHEMA]

`SessionCreateInput` contains optional `id`, `parentID`, `title`, `agent`, `model`, `location`, `metadata`, and `permissions`. `Model.Ref` uses `{ providerID, id, variant? }`, not V1's `modelID` request field. The creation API returns `Session.Info`. It does not itself prompt the model. A supplied `parentID` selects the parent's location and inherits metadata/permissions when omitted; creating a root with explicit `location` avoids that coupling. [API-TYPES] [SESSION-CREATE]

Native operations also include:

```text
ctx.session.switchAgent({ sessionID, agent })
ctx.session.switchModel({ sessionID, model: { providerID, id, variant? } })
ctx.session.prompt(...) -> Promise<Session.Inbox.User>
ctx.session.wait({ sessionID }) -> Promise<void>
ctx.session.interrupt({ sessionID, resume: false }) -> Promise<{ interrupted: boolean }>
ctx.session.get({ sessionID }) -> Promise<Session.Info>
ctx.session.context({ sessionID }) -> Promise<readonly Session.Message.Info[]>
```

These are V2 plugin/client operations; no V1 `promptAsync`, `body`, or `path` envelope is assumed. An explicit session model is resolved exactly or fails unavailable; agent/default selection is used only when no session model is set. Selecting an agent alone is therefore insufficient to pin a reviewer model. [SERVER] [MODEL]

### Hooks shape requests; they do not create private executors

The relevant hook type is:

```ts
interface SessionContext extends SessionRequest {
  readonly agent: Agent.ID
  tools: Record<string, { description: string; input: JsonSchema.JsonSchema }>
}
```

`SessionRequest` includes readonly `sessionID` and model, plus mutable system, messages, and options. Hook registration has optional **provider** scoping, not a `sessionID` option. A plugin implements session-specific behavior by checking `event.sessionID` inside a location/runtime hook. Multiple plugins' hooks run in registration order. There is no documented “exclusive session” or “skip other plugins” switch. [HOOK-TYPES] [HOOK-REGISTRATION] [SERVER]

Crucially, V2.2.0 matches post-hook tool descriptions to the original executable snapshot by definition-object identity or registered name. Entries matching neither are dropped. A context hook can remove, rename, or reshape registered definitions; **it cannot supply an independent session-only tool implementation**. Returning a new schema does not register an executor. [REQUEST]

Register executable tools through `ctx.tool.transform`. A later valid registration wins on the same effective name; namespaces are name prefixes, not exclusive ownership reservations. Every model request captures an executable snapshot. Removing a registration or changing a stage later does not revoke an already captured handler. [SERVER] [TOOLS]

### Prompt return and wait completion are different

`SessionPromptInput` takes `sessionID`, required `text`, and optional `id`, `files`, `agents`, `skills`, `metadata`, `delivery`, and `resume`. The operation **admits input and schedules execution** unless `resume` is false; it returns the admitted inbox item, not the completed review response. The source calls `execution.wake(sessionID)` before returning admission. [API-TYPES] [PROMPT]

`wait` waits for process-local execution to become idle. It neither starts execution nor reports its success: its coordinator deliberately ignores the execution's failure while waiting for settlement. `interrupt` acknowledges interruption before cleanup settles; compose it with a bounded wait when settlement matters. [EXECUTION] [COORDINATOR]

`Session.Info` exposes the last terminal `outcome` (`succeeded`, `failed`, `interrupted`) and `time.idle`. Native message context also includes an `idle` message with outcome, and assistant messages carry model, finish, error, and completion fields. These permit completion assessment without inventing a `wait` return payload. [SESSION-SCHEMA] [MESSAGE-SCHEMA]

## Recommended execution boundary

```text
caller session
  → public Crucible begin/status/abort/rerun/issue-read tools
  → plugin-owned run supervisor and serialized origin store
      → dedicated native root sessions, explicit agent + model
          → stage-filtered, globally registered Crucible tools
              → source reads: shared detached review checkout
              → review mutations: explicit origin store
```

### Sessions are control contexts, not filesystem authority

**Design choice:** keep participant sessions at the initiating, trusted OpenCode location in the **origin**, not at the detached checkout. Every participant receives the review checkout as its source root through Crucible's tools and instructions. Native OpenCode still runs inference and tools; “native execution” does not require exposing the stock filesystem tools or making the source checkout an OpenCode location.

This separation avoids loading the selected commit's `.opencode` plugins/configuration as executable host configuration. The official discovery rules load project plugins from applicable directories; prompt preparation waits for plugin activation before its hook. Likewise, the native `worktree.create` implementation can execute the project's `commands.start`; it is not an inert detached-checkout API. Do not use either mechanism blindly for an untrusted review target. [PLUGINS] [PROMPT-PREPARE] [WORKTREE]

Resolve the invoking session through `ctx.session.get`, not the plugin instance's `ctx.location` alone. Freeze separately:

- **Origin root:** the consuming checkout's project root, owning configuration and `.crucible` output. A linked-worktree caller must not silently redirect output to a different canonical checkout.
- **Review root:** the single owned detached checkout at the resolved full commit ID, shared by all participants through summary.
- **Host location:** the trusted location whose V2 services execute the participant sessions. Validate that it is the expected origin location; never move participants into the review root.

These locations are server-owned run data, not model arguments. Storage handlers receive an origin-store capability when the run is constructed and never derive a write path from a participant's location. Public tools called from an unrelated project must not select a run merely because its commit string matches.

Create the checkout using constrained, plugin-owned Git operations, with repository hook/filter/startup execution prevented, no submodule fetching, and no repository code execution. The exact safe checkout construction and cleanup belong in planning; a plain default `git worktree add` is not asserted to satisfy those conditions. This is still a shared Git worktree, not a custom Git-object filesystem.

Expose bounded Crucible read/list/search/diff operations rooted in that checkout. Deny traversal and external symlink access; Git metadata, origin records, and arbitrary host paths are not source-read targets. Baseline/deleted content comes through a bounded controlled Git operation, with the approved parent/empty-tree/first-parent rule. Do not expose shell, source writes, generic host filesystem access, subagents, MCP, web tools, skills, or host-management tools to participants. Stock `read` also discovers nearby `AGENTS.md` and loads instructions, another reason not to treat it as a neutral snapshot reader. [READ]

The checkout is capability-read-only, not an OS sandbox against other trusted host plugins or the user. Validate target ownership/integrity and report interference rather than claiming the host's full filesystem authority has disappeared.

### Agent and session allocation

Register reserved `crucible-reviewer` and `crucible-arbiter` agents with the verified upsert. Give them explicit Crucible system instructions, `mode: primary`, hidden discovery, bounded steps, and a replaced default-deny policy. Do not change the default agent or repurpose omo-slim's existing agents. Hidden discovery is convenience, not authorization. [AGENT] [AGENT-SCHEMA]

Create **fresh root sessions per participant-stage execution**, with no `parentID` and no forked history. Bind each to the same stable logical participant across stages. This is an execution/context choice, not a change to the seven stages: later contexts are built from the approved stored evidence, not incidental previous chat history. It also avoids changing a live session from one tool authority to another.

At creation, set the exact configured session model, dedicated agent, title, host location, and session permissions. Validate their returned state before any prompt. Missing/changed models fail visibly; never fall back to an ordinary agent or different model. Create and register the session-to-participant binding before scheduling its first prompt. No model-supplied identity is needed.

The context hook supplies Crucible's role/stage instructions and an exact tool allowlist on **every continuation**. Replace ambient implementation/delegation instructions rather than appending a competing review request to them, accounting for instruction additions in messages as well as `system`. Repository instructions can be read as source evidence, not accepted as new tool authority. First-pass contexts and read handlers must not expose other participants' findings. Later evidence comes through role/stage-filtered record access.

The supervisor pre-registers each planned input ID. Unexpected prompt admission, changed agent/model/location, or other external session control fails the execution rather than becoming new review authority. Session metadata is not an admission credential. Native context shaping must preserve the session's own tool-call/result pairs; it is not a replacement model/tool loop.

Account separately for auxiliary requests: `context` does not cover `title`, `generate`, or `compaction`. Supply a deterministic title with the documented title-hook `result`; do not use transient generate as the review loop. For this bounded initial design, context exhaustion/automatic compaction can end the stage as incomplete rather than introduce a second summary-authority mechanism. Apply the ownership checks to auxiliary hooks too. [SERVER] [HOOK-TYPES]

### Global visibility versus server-side authority

Register a fixed superset of Crucible tools once per plugin runtime. Use a reserved namespace, for example effective names `crucible_review_begin` and `crucible_review_issue_add`; these implement the intent's logical `review_*` operations. Mark participant tools `codemode: false` and deny Code Mode `execute`, avoiding a second discovery/execution path. Exact schemas remain a planning artifact. [TOOLS]

For ordinary sessions, the context hook removes participant-only definitions. For owned sessions, it removes public lifecycle tools and everything outside the current stage allowlist. Session permissions independently deny `*` with exact Crucible-action exceptions. Host policy denials remain denials; a hook must not try to resurrect a tool missing from the executable snapshot.

Public lifecycle/read handlers resolve the caller's origin project and reject calls from mapped participant sessions. This prevents nested review starts and public issue reads from bypassing first-pass evidence restrictions.

**None of those presentation controls grants review authority.** Every participant read/mutation handler:

1. Looks up the host-provided `context.sessionID` in Crucible's active binding map.
2. Resolves run, stable participant, role, immutable target, stage/attempt, and plugin generation from that map.
3. Under the run's mutation serialization, checks the run is active, the binding is current, the operation is stage/role-allowed, and issue eligibility holds. It checks a retained logical operation/call key before applying a repeated mutation.
4. Rejects conflicting commit/run arguments, self-votes, other-run writes, or unbound sessions without side effects. The actor is never inferred from model, agent name, metadata, or tool arguments.
5. Uses the already bound origin store; performs atomic persistence only after authorization and the required ignore/tracked-path checks.

Use `context.agent`, `messageID`, and tool-call `id` for consistency checks and audit. The authoritative invocation identity fields exist in `Tool.Context`; they are not inferred from prompt text. Custom tools should perform their appropriate `ctx.permission.assert` as well as Crucible's application authorization; registration/schema visibility alone is not a permission assertion. [TOOL-CONTEXT] [SERVER]

The tool-execution-before hook rejects any non-allowlisted operation for an owned session; handlers repeat the authorization because captured executors survive catalog changes. When a stage/run ends, invalidate its binding before advancing or aborting. A late call from an old snapshot remains powerless.

Fail on an already occupied reserved effective name when registering. Inspect the effective catalog before running, but do not claim that name/schema inspection proves executor ownership: V2 provides no exclusive namespace reservation. Supporting a known, trusted plugin set is a deployment assumption. A hostile co-plugin already has host privileges and is not contained by this design.

## omo-slim coexistence: what actually needs changing

The inspected 3.0.5 bundle establishes both useful separation and reachable interference paths. These are source findings, not claims that every optional hook is enabled or that a particular live request was rewritten; private profile/configuration contents were not inspected.

| Installed source behavior | Consequence |
| --- | --- |
| `createSessionProfileBridge` ignores root sessions and child agents outside its plugin-agent set (lines 83822–83847). The permission bridge likewise classifies an identified root as unmanaged (84372–84379). | Root sessions with dedicated IDs avoid managed-child model/profile and permission replacement. Do not use the ordinary `subagent` path. |
| Agent-specific fallback lookup returns an empty chain for a known agent name absent from its chains (49151–49172). The V2 retry event carries the agent and registers it before selection (48200–48255). | An unrelated dedicated ID does not intentionally borrow the orchestrator's fallback chain in this source. Still verify selected model at each primary request and fail on substitution. |
| Orchestrator system-prompt injection checks the requested agent, but `collapseSystemInPlace` runs afterward for all requests (87153–87175). | A different name prevents orchestrator injection, not every transformation. |
| The context bridge calls message transforms without a Crucible exclusion (84052–84165). User text is passed through `rewriteDisplayNameMentions` irrespective of agent (87177–87196). | Saved evidence placed in user text can be rewritten even in a dedicated root session. |
| V2 tool-after bridging forwards results into generic guards (84840–84885, 87246–87254). When enabled, JSON recovery appends imperative instructions whenever a non-excluded tool's output matches a JSON-error phrase (49226–49240). | A Crucible source-read result containing such a phrase can acquire unrelated instructions. This is a concrete source path, not merely speculation about delegation prompts. |
| Hooks are registered for prompt, context, model request, compaction, retry, tools, and events (85303–85536). | There is no inspected general per-session opt-out. A marker in a Crucible prompt does not disable these hooks. |

**Recommended compatibility seam, proposed rather than existing:** omo-slim recognizes explicitly marked Crucible root sessions with the reserved agent IDs and excludes them from its prompt/context rewriting, profiles, fallback, tool guards/result rewriting, and workflow-driving event handlers. Retaining passive diagnostics is acceptable; mutating or resuming their workflow is not. The exclusion must occur before side effects, not after a result has been rewritten. It must also handle unknown/retired Crucible session generations conservatively.

The marker can live in native session metadata for cooperation/discovery. It is **not** authority to mutate Crucible records: an ordinary session with copied metadata or the same agent name still fails the binding-map checks. The caller uses the public review tool; it does not negotiate workforce exceptions or construct these sessions itself.

No such seam is asserted to exist in installed 3.0.5. Its implementation or adoption in a compatible upstream release needs separate authorization. Do not patch the installed service bundle or globally disable omo-slim hooks. Do not use its private internal-session title sentinel as an undocumented bypass. A separate, deliberately configured review host is an alternative requiring an explicit deployment decision, not a hidden service started by this design.

## Native stage completion and plugin-owned runner

### One stage execution

For a bound fresh session, the supervisor records the intended stage input, calls `prompt` with a stable input ID and normal execution enabled, and retains the returned admission ID. It then waits with a **run-owned timeout/cancellation signal**, not the public begin invocation's signal. Native OpenCode owns tool dispatch and continuations.

After `wait`, read `session.get` and `session.context`. Require the intended admitted input to have been delivered and a subsequent terminal native outcome; examine assistant errors/finish and actual model, plus the stage's stored obligations. Idleness alone, step exhaustion, a permission rejection, or an empty assistant response is not successful review completion. A legitimate explicit no-findings result can complete initial reporting; missing votes or a failed reviewer cannot become approval. Use native events for progress/diagnostics, not as the only completion record. [PROMPT] [EXECUTION] [SESSION-SCHEMA] [MESSAGE-SCHEMA]

Finish the native execution and settle authorized mutations before retiring the stage binding. Only then may the existing seven-stage controller admit the next stage. Bound stage time/steps and ordinary retries; operational failures remain visible. No selected-provider capability probes or compatibility repair framework belongs here.

### Begin, status, abort, and interruption

The plugin setup owns a run supervisor, controllers, and caught worker promises. Public begin validates origin/configuration/target, establishes one-active-run ownership, creates the ignore-protected manifest, schedules the supervisor, and returns the full commit ID, run ID, and initial status **without waiting for reviewer execution**. The worker promise is retained and its rejection updates incomplete/failed state; it is not an unobserved `void` task or a promise owned by the tool invocation. The V2 setup/cleanup and background-subscription examples support this ownership pattern, not a durable-job guarantee. [SERVER]

Use separate cancellation lifetimes:

- The invocation signal cancels admission work that has not been handed off.
- A run-owned controller governs admitted native work. Ending/stopping the caller's turn after begin returns does not implicitly abort it.
- Explicit abort serializes an abort/fence transition first, stops new scheduling, then calls `session.interrupt({ sessionID, resume: false })` for owned sessions and waits boundedly for settlement. Aborting a `wait` request alone is not session interruption. Late tool calls and worker completions recheck the fence before any write.

Status reads origin records and reconciles with the live supervisor; stale active-looking records whose recorded owner is known gone must surface as interrupted, not finished. Absence from the calling plugin instance's map alone does not establish owner loss. Begin is idempotent and rerun is explicit as required by the intent. Disk serialization/ownership details are deferred, not replaced by a process-global commit-string map or plugin storage.

On unload/reload, fence the generation before registrations disappear, stop scheduling, interrupt participants, and preserve honest interruption/cleanup ownership records. Do not delete a checkout while unsettled source reads still use it. Exact bounded cleanup behavior belongs in planning.

There is an additional source fact worth respecting without expanding scope: V2.2.0 itself can automatically resume suspended native sessions after server restart. Crucible must not interpret that as resuming a review. A dedicated-agent session without a current live run binding must be rejected at request/tool boundaries; the new plugin generation marks its old run interrupted and does not adopt it. This is a minimal stale-session safety fence, not restart-survival engineering. No guarantee is made that already dispatched remote computation stops. [RESTART]

## Smallest acceptance probe before implementation proceeds

No probe was executed in this author pass. Once separately authorized, use one isolated, test-owned V2 fixture with the intended omo-slim exclusion contract and a scripted local model transport that emits fixed tool calls and a terminal response. This is a test of Crucible's boundary, not inference or certification of any configured provider. Do not change the user's running service configuration.

The fixture needs only reviewer and arbiter identities, a tiny origin repository, one shared target checkout, and a normal run plus an aborted run. Establish:

1. The supported host actually upserts/selects the dedicated agent, creates root sessions at the trusted origin, and retains the explicitly selected model. Record the effective registered tool names and outgoing request catalog. A made-up hook-only tool has no executor; unrelated host tools cannot execute.
2. The exclusion leaves Crucible instructions, admitted stage text, and tool-result evidence untouched. Include a configured display-name mention and a literal JSON-error phrase in inert evidence to exercise the concrete 3.0.5 conflicts. Verify no ordinary delegation, model switch, or workflow wake is introduced. Ordinary workforce sessions still follow omo-slim normally.
3. Public begin returns while the mock native loop continues. Prompt admission is distinct from terminal outcome; status observes the right run. An attempted unbound, wrong-role, or stale-session mutation leaves records unchanged.
4. Reads use the pinned checkout despite unrelated dirty origin content; records appear only at the origin. Abort fences first and interrupts the correct sessions; a deliberately late call cannot mutate the run.

**Stop condition:** if the exclusion cannot be provided/verified, agent upsert differs from the pinned source, required tools cannot survive the native snapshot path, or begin/abort ownership fails, do not enable same-host execution or write the full implementation around a guessed signature. Report the one failed contract and seek the smallest host/omo-slim correction or an explicit separate-host decision. Do not automatically replace native sessions with a direct-provider loop. Detailed schemas and the full implementation tests remain the next planning work.

## Sources and author checks

Official pages and source files linked below were directly retrieved (source through `raw.githubusercontent.com`); relevant public source is pinned to `v2.2.0` rather than V1 or an unversioned SDK example.

- [SERVER] — official V2 server plugin API: agent/editor reference, sessions, context and auxiliary hooks, tool snapshots, permissions, lifecycle/background examples.
- [API-TYPES] — `SessionCreateInput` lines 215–226, `SessionPromptInput` 285–297, and `SessionWaitInput` 349–351; Promise adapters use these endpoint contracts. [ADAPTER] lines 599–619 shows native plugin method wiring.
- [AGENT-API] — public plugin editor signature, with `update` but no `add`. [AGENT] lines 71–85 prove upsert; 99–106 distinguish explicit ID selection from default visibility filtering. [AGENT-SCHEMA] lines 39–51 show permissive defaults.
- [HOOK-TYPES] — `SessionRequest`/`SessionContext` and auxiliary events; [HOOK-REGISTRATION] lines 5–19 shows provider-only scoping. [REQUEST] lines 240–271 drops invented tools; 390–404 executes the surviving snapshot.
- [TOOLS] — lines 249–263 builds the permission-filtered direct/Code Mode catalog; 297–317 resolves calls against surviving definitions. [TOOL-CONTEXT] lines 14–20 supplies identity fields. These are stronger evidence than assuming a visible schema is an authorization boundary.
- [SESSION-CREATE] — lines 297–324 selects location and inheritance. [MODEL] lines 77–98 resolves explicit session models without default fallback.
- [PROMPT] — lines 155–188 admits then wakes; 278–280 waits for idle; 328–330 forwards interrupt. [EXECUTION] lines 26–39 defines interruption acknowledgment and process-local idle. [COORDINATOR] lines 164–170 ignores execution failure while waiting.
- [SESSION-SCHEMA] — lines 39–58: model, outcome, time, location, permissions. [MESSAGE-SCHEMA] lines 220–246: assistant outcome evidence; 297–302: terminal idle outcome.
- [PLUGINS] — project discovery and ordered plugin registrations. [PROMPT-PREPARE] lines 39–42 waits for activation before the prompt hook. [WORKTREE] lines 236–249 runs a configured startup command. [READ] lines 82–103 discovers and loads nearby instructions.
- [RESTART] — lines 192–227 recovers suspended executions. Cited only for stale-session fencing, not as a requested recovery feature.
- [LOCAL] — local installed metadata and load log listed below. [OMO] — readable installed bundle; exact function/line evidence is in the coexistence table.

Local evidence paths:

```text
/home/rjroy/.local/share/mise/installs/npm-opencode-cli/2.2.0/node_modules/@opencode/cli/package.json
/home/rjroy/.cache/opencode/npm/oh-my-opencode-slim@latest/1792548650360/node_modules/oh-my-opencode-slim/package.json
/home/rjroy/.local/share/opencode/log/oh-my-opencode-slim.20261027T134441-1252682.log:1-24
```

Author checks: current intent and all three requested historical reports read; source claims and installed artifact identity checked as described above. The Lore frontmatter validator returned zero findings; source-reference, related-path, whitespace, and final-newline checks passed, as did `git diff --no-index --check /dev/null .lore/work/design/crucible-session-boundary.md`. Six focused text assertions against pinned source passed for upsert, editor shape, tool-snapshot matching, prompt admission, idle waiting, and outcome fields. These are document/source checks, not runtime validation. The parent owns the fresh independent `design-reviewer` invocation; no nested review was launched.

[SERVER]: https://opencode.ai/v2/docs/build/plugins/server/
[PLUGINS]: https://opencode.ai/v2/docs/plugins/
[API-TYPES]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/client/src/effect/api/api.ts
[ADAPTER]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/plugin/src/promise/adapter.ts
[AGENT-API]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/plugin/src/promise/agent.ts
[AGENT]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/agent.ts
[AGENT-SCHEMA]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/schema/src/agent.ts
[HOOK-TYPES]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/plugin/src/promise/session.ts
[HOOK-REGISTRATION]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/plugin/src/promise/registration.ts
[REQUEST]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/model-request.ts
[TOOLS]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/tool.ts
[TOOL-CONTEXT]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/schema/src/tool.ts
[SESSION-CREATE]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session.ts
[MODEL]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/runner/model.ts
[PROMPT]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/session.ts
[PROMPT-PREPARE]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/prompt.ts
[EXECUTION]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/execution.ts
[COORDINATOR]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/run-coordinator.ts
[SESSION-SCHEMA]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/schema/src/session.ts
[MESSAGE-SCHEMA]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/schema/src/session-message.ts
[WORKTREE]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/worktree.ts
[READ]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/tool/plugin/read.ts
[RESTART]: https://github.com/anomalyco/opencode/blob/v2.2.0/packages/core/src/session/execution/restart.ts
[OMO]: file:///home/rjroy/.cache/opencode/npm/oh-my-opencode-slim@latest/1792548650360/node_modules/oh-my-opencode-slim/dist/server/index.js
[LOCAL]: file:///home/rjroy/.local/share/opencode/log/oh-my-opencode-slim.20261027T134441-1252682.log

## Recommended decision

**Adopt the native V2 session boundary, using source-verified agent upsert and globally registered, server-authorized Crucible tools. Keep source reads pinned to the shared checkout and persistence pinned to the origin. Do not enable it beside installed omo-slim 3.0.5 unchanged: first authorize/provide the narrow session-exclusion seam and pass the focused no-inference coexistence/lifecycle probe. If that gate fails, stop at the failed contract rather than invent APIs, fight hook ordering, or silently change the approved runtime direction.**
