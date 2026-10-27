---
title: Crucible reviewer runtime options in OpenCode V2
date: 2026-10-26
status: draft
tags: [crucible, opencode-v2, openrouter, model-tools, isolation]
related: [.lore/work/intents/crucible.md, .lore/work/openrouter-independent-review-notes.md]
---

# Crucible reviewer runtime options in OpenCode V2

## Key Findings

- **Feasible, but Crucible must own the review state machine and tool dispatcher.** OpenCode V2 exposes plugins, typed SDK/client APIs, model-generation and session primitives, tools, permission checks, and cancellation signals. It does not provide a ready-made multi-model peer-review/voting/arbitration workflow or reviewer identity/phase authorization contract.
- **The cleanest separation for Crucible's stated boundary is direct OpenRouter calls from its plugin, with Crucible-defined tools and a client-side tool loop.** OpenRouter returns suggested tool calls; only Crucible executes them. The API request's tool list is not the OpenCode global tool registry. That gives a natural separate tool surface, but all security properties still depend on validating each call and dispatching only Crucible's stage/role-allowed operations.
- **OpenCode session-based execution is possible, but less isolated by default.** V2 supports creating sessions, selecting model and agent, prompting, inspecting context, interrupting and waiting, and per-session permissions. However, an ordinary agent session invokes OpenCode's agent loop and configured tool system. Session permissions are not an identity system, and child sessions inherit the permissions set at creation. A dedicated agent plus carefully constrained tools and permissions could work, but it is not as inherently separate from the regular host tool catalog as direct API calls.
- **OpenRouter's built-in server tools are not a substitute for Crucible's controlled tools.** Some models/endpoints advertise OpenRouter-operated shell, web, panel, or other tools that execute outside Crucible's dispatcher. For a strict Crucible allowlist, send only function-type tools owned by Crucible and do not forward arbitrary or `openrouter:*` server tools.
- **OpenCode's transient `ctx.generate.text` is not suitable for tool-using reviewers:** its documented contract specifically says generation does not invoke tools. For native tool-using execution, use the session agent loop or implement tool execution outside it.
- **Independent context is implementable by separate requests/sessions constructed from the same immutable target snapshot, not by a built-in isolation guarantee.** Keep each reviewer's prompt/history private until first-pass review finishes. For later peer-vote and response stages, deliberately pass the relevant stored issue/evidence subset. Stable participant identity and tool access must be host-bound, never accepted from model-supplied fields.
- **Committed-object review fits a custom read-only Crucible tool layer better than OpenCode's regular filesystem tools.** V2 has VCS info/status/diff APIs and ordinary `read`, `glob`, `grep`, and `shell`, but the docs do not describe a pinned-commit, arbitrary-Git-object read API or guarantee that filesystem reads reflect the requested commit. To meet the intent's target/baseline guarantees, Crucible must implement object-addressed reads/search/list/diff or use a separately verified immutable checkout; avoid handing reviewer execution to shell.
- **Structured output can constrain the final shape but cannot replace application validation.** OpenRouter supports JSON Schema response formats only where the selected model/provider endpoint supports them; enforcement varies by endpoint. Tool schemas can standardize proposals, but malformed calls, unsupported capabilities, invalid source locations, and unauthorized actions remain host concerns.
- **A clean staged protocol is possible without relying on JSON-schema output for every step:** expose stage-specific mutation/read functions during tool-enabled stages, then make a separate final synthesis request with `tool_choice: "none"` and a JSON schema where the selected route supports it. Keep persisted issue/vote/arbitration state authoritative; final prose or JSON is only a projection to validate against that state.
- **Cancellation and retries need explicit run orchestration.** OpenCode client operations accept `AbortSignal`; plugin tools receive `context.signal`; session interruption is available. OpenRouter can cancel a streaming request by closing the connection only for supported provider endpoints. Non-streaming calls and unsupported stream endpoints may continue processing/billing. A cancelled run must fence late replies and preserve incomplete status; retry policy, idempotency, timeout, and partial-stage accounting are application logic.
- **Budget enforcement is explicitly out of scope** per the approved intent. This report does not recommend or design per-run/monthly limits, reservations, or cost admission. OpenRouter's provider/key limits and returned usage metadata are distinct from Crucible budget enforcement.

## Scope and method

This report assesses isolated execution options for Crucible reviewers and arbiter against the official OpenCode V2 documentation available on 2026-10-26 and official OpenRouter API documentation. The approved intent is `.lore/work/intents/crucible.md`, especially its fixed-commit target, multiple independent reviewers, stage-based tools, attribution, votes, arbitration, honest abort/incomplete states, and explicit budget exclusion. The older `.lore/work/openrouter-independent-review-notes.md` is historical draft context; its packet-only, no-tools proposal is superseded by the approved intent.

No paid calls, installs, secrets, or configuration changes were used. No live model call was made. OpenCode documentation labels some APIs experimental and the V2 docs are an evolving versioned target; verify actual installed V2 package/API contracts during implementation. This is feasibility analysis, not implementation authorization.

## Execution choices

### Option A: Crucible plugin orchestrates direct OpenRouter calls

The official OpenRouter Chat Completions interface accepts a selected `model`, conversation `messages`, `tools`, `tool_choice`, and optional `response_format`. It returns assistant messages and any suggested `tool_calls`. OpenRouter documents a client-side loop: caller examines each request, executes its local functions, appends assistant call and tool-result messages, then requests the next turn. The tool list must be repeated in subsequent requests. Therefore the model proposes an operation; it does not itself execute local tools.

**What this supplies:** model inference over OpenRouter; a normalized tool-call message shape; optional structured-output formats; streamed/non-streamed responses; provider routing preferences; and usage fields in responses. A direct call can bypass OpenCode's regular session/tool execution path because Crucible's plugin itself makes the HTTP request and only advertises its own JSON tool definitions to the model.

**What Crucible must implement:** construct prompts/messages per participant and stage; isolate each participant's transcript; parse and validate tool-call arguments; dispatch only the allowlisted Crucible operations; bind actor/role/stage/run/commit context outside model input; return tool results; bound loop turns and output size as reliability behavior; validate final outputs; store state and coordinate stages; handle retries, timeouts, cancellation, and partial failures. Tool definitions are not ACLs. A model may request a tool it was shown with malicious/invalid arguments, or emit unexpected data; the dispatcher must reject calls outside the current stage and validate all fields against current authoritative state.

The direct route is the strongest conceptual fit for the approved requirement that Crucible owns participants/tools/results and does not turn ordinary omo-slim agents into a second review workforce. It avoids ordinary registered tools by architecture, not by trusting a prompt. Keep API keys out of project config and persisted run snapshots, as the intent requires.

### Option B: OpenCode V2 plugin uses sessions / agent loop

The V2 plugin context wraps the OpenCode server client and exposes session creation, model and agent switching, prompting, context reads, interrupt, wait, and plugin tool registration. A dedicated session per reviewer can separate histories and choose a model. Per-session permissions can constrain built-in actions; custom agents can have their own permission rules, and those are not merely a subset of a parent's. This offers OpenCode-managed agent loops and built-in tool calling.

But a session is an OpenCode agent execution context, not a bare model request. Its tool loop can expose OpenCode's normal tool catalog and configured extension tools unless the session's agent/permissions/tool setup prevents it. The docs do not establish that a plugin-created session automatically has only Crucible operations. The `ctx.generate.text` method is explicitly tool-free and cannot provide an agentic review loop on its own.

**What it supplies:** session lifecycle APIs, model selection, tool-registration transforms, per-session permission rules/assertions, request cancellation options, and agent-loop management. **What it does not supply:** participant identity binding, distinct reviewer's private prompt contexts by policy, stage-based author/voter permission, a commit-pinned Git reader, the Crucible vote/arbitration state machine, or proof that generic project filesystem access is bound to a selected commit. Those still require Crucible-owned state/logic and targeted integration testing.

### Option C: OpenCode provider/client as inference transport

OpenCode's V2 client is an HTTP client to an OpenCode server, not a general remote-model SDK. The plugin context is tied to the connected server and includes model/provider registries. OpenCode's provider documentation lists a native OpenRouter runtime and OpenAI-compatible custom providers. Using OpenCode's provider path can reuse connected credentials, model catalog, and provider dispatch. This is appropriate if Crucible intentionally wants OpenCode to own model transport and credential resolution.

However, the public docs reviewed do not expose a plugin API that takes arbitrary model message/tool-call turns and runs a standalone model-with-our-own-tool-loop without invoking the agent loop. The plugin API documents `ctx.generate.text` as no-tools, while sessions use the agent runtime. Thus native provider integration is not a turnkey isolated reviewer runtime. It remains a possible implementation route only if the actual V2 SDK/provider contracts offer lower-level model-call primitives beyond the reviewed documented plugin surface. Do not assume that they do.

## Capability matrix

| Concern | Native documented support | Crucible-specific work / limitation |
|---|---|---|
| Multiple model participants | V2 sessions can select models; OpenRouter accepts a model per request | Schedule configured participants, record actual model/provider, handle per-participant failures. Do not silently substitute a model if the intent forbids it. |
| Independent first-pass context | Separate sessions are available; direct calls carry caller-constructed messages | Create fresh independent histories and do not disclose other findings until the later stages. Same-model participants still need separate participant IDs. |
| Model tool calls | OpenRouter supports client-side function calling; OpenCode agent sessions run tool loops | Implement or constrain loop; tool call is an untrusted request, never permission. Validate JSON, tool names, arguments, call count, and state transitions. |
| Stage-specific tool catalog | OpenRouter accepts `tools` and `tool_choice` per request; its docs say resend schemas alongside tool results | Build only the current stage's function definitions on every turn. Dispatcher rechecks stage/actor/state at execution time. Do not expose OpenRouter server tools. |
| Per-stage tool allowlists | OpenCode custom tool registry and permissions exist; OpenRouter lets caller specify `tools` each request | Host must build the allowed schema set for participant role/stage and enforce it again in dispatcher. OpenRouter's request schema does not enforce business authorization. |
| Participant attribution | OpenCode sessions have IDs; OpenRouter supports a `user` value for abuse isolation | Generate stable Crucible participant IDs and bind each call server-side to run/role/stage. `user` is not a substitute for app authorization or tool identity. |
| Voting/abstention | No first-class peer review workflow documented | Validate one eligible vote per reviewer/issue; any reject contests; abstain and missing votes remain distinct from approval; reporter exclusions are host logic per intent. |
| Arbiter | Can select an arbiter model in configuration and call it via same model mechanisms | Role-restricted merge/priority/decision tools and recorded rationales are all Crucible-defined. Arbiter model text alone cannot authorize mutations. |
| Structured results | OpenRouter `response_format: json_schema` on compatible endpoints; OpenCode tools use schemas | Select supported model/provider route, validate response locally, handle refusals/truncation/unsupported structured output. Consider tool calls for incremental issue records and schema for terminal summary. |
| Read-only committed snapshot | V2 exposes filesystem and VCS tools, but docs do not promise object-pinned reads; OpenRouter itself has no local filesystem | Implement safe Git-object reads, searches, listings and baseline diff or verify an immutable checkout. Reject paths/symlink escapes; do not expose unrestricted shell or project writes. |
| Cancel | OpenCode client request options accept signals; tool executor gets signal; session interrupt exists. OpenRouter supports canceling streaming connections for some providers | Track each outstanding request; pass abort signal; persist cancel/incomplete state and reject late mutations. Non-streaming/unlisted provider calls might continue. |
| Retry/recovery | OpenCode provider docs describe transport timeout retry behavior; API exposes error statuses | Distinguish transport retry from workflow retry; define attempt IDs, deduplicate side effects, bounded attempts/timeouts, and coverage status. No automatic crash resume per intent. |

## Host boundary: model-requested tools are not general host tools

The two tool concepts must stay separate:

1. **OpenCode tools** are registered in its effective tool registry and executed by OpenCode's agent loop, with OpenCode permissions and (for plugins) plugin executor code.
2. **OpenRouter client tools** are JSON function descriptions sent in an API request. The model returns a tool call; the API caller executes it locally and sends the result back.

Thus passing `review_issue_add` to OpenRouter does not register that function as an OpenCode tool, and direct OpenRouter requests do not automatically gain OpenCode's registered shell/read/edit/MCP tools. Conversely, if Crucible runs a normal OpenCode session, the existence of an OpenRouter configuration does not isolate that session from normal OpenCode tools. Isolation must be designed around the chosen execution path.

For either route, map every tool request through host-controlled context:

```text
validated run snapshot + participant record + current stage
    -> construct allowed tool definitions
    -> receive proposed tool call
    -> parse/validate name and arguments
    -> authorize from host participant/role/stage/state, not model text
    -> execute only the narrow handler
    -> append result to that participant's context
```

The model must never choose its authoritative participant ID, reporter status, current stage, or permissions. Never let an input property such as `reviewer_id` override the participant identity already bound to the request. If a call is disallowed, record/return a safe tool error and do not mutate state. For a participant with multiple roles in different phases, derive allowed operations from the host stage record each call.

### Concrete direct-call stage loop

OpenRouter Chat Completions defines a model request with `messages`, optional `tools`, and `tool_choice`; the response carries assistant `tool_calls` and a finish reason such as `tool_calls`, `stop`, `length`, `content_filter`, or `error`. Its official guide demonstrates: append the assistant tool-call message, execute client-side, append one `tool` result keyed to `tool_call_id`, and call again with the tools schema repeated. This maps naturally onto Crucible stages:

1. **Initial reviewer pass:** start an independent transcript for each participant. Supply only read-only snapshot tools and `review_issue_add` (or a narrowly defined report tool). Do not include vote or arbitration calls. Persist only after host validation.
2. **Arbiter validation/deduplication:** start an arbiter context containing independently recorded reports. Advertise arbiter-only merge/priority operations. Host validates canonical issue references and duplicate-preservation rules.
3. **Peer voting:** each eligible reviewer receives its own vote context and only `review_issue_vote` for issues it did not report. The host checks issue eligibility and one-vote rules regardless of prompt content.
4. **Reporter response/arbitration:** report authors receive only response/appeal operations for their own canonical issue; arbiter receives the decision/close/priority tools. Enforce per-reporter withdrawal and canonical issue state in Crucible.
5. **Final synthesis:** provide the arbiter with a computed read-only snapshot of current open issues, outcomes, and coverage limitations. Send no mutation tools and set `tool_choice: "none"`; request strict JSON output if supported by that exact endpoint. Independently validate and ensure the final item list matches stored open state.

This is ordinary application code around a documented inference/tool protocol, not a capability the API supplies. JSON tool parameter schemas are guidance/API-level shape; they do not assert Crucible authorization. Each request/continuation can be reconstructed with the appropriate tools list, so tool availability need not be global. Use non-parallel tool calls for state-changing operations unless the application implements a safe serialized transaction path; OpenRouter documents `parallel_tool_calls` but provider support varies. If multiple calls arrive in a single response, validate/serialize each against state as it changes, not against a stale copy.

OpenRouter separately offers *server tools* whose execution can be OpenRouter-side, provider-native, or another backend. Its official docs identify `openrouter:*` tool types and note endpoint native tools. These are not the ordinary client-executed function calls. Because they bypass Crucible's own handlers and may introduce separate privacy/retention policies, do not include them in reviewer requests when the approved design demands Crucible-controlled project reads and mutation authority.

## Preferred model discovery: snapshot as of 2026-10-26

The catalog and endpoint listing are live and change over time. These are metadata observations only, not paid generation tests. OpenRouter's model-list API returns `supported_parameters` at model level and a model's `/endpoints` listing exposes provider-specific supported parameters and tool-choice modes. The catalog can therefore narrow candidates but cannot prove the exact prompt/tool loop works without a non-production capability test.

| Requested model | Model ID observed | Tool calling at listed endpoint(s) | Structured output notes |
|---|---|---|---|
| GLM-5.3 | `z-ai/glm-5.3-prime` (not plain `z-ai/glm-5.3` in this snapshot) | Alibaba endpoint advertises `tools` and `tool_choice`, but only `none`/`auto`, not forced `required`/function selection. | Advertises `response_format`; endpoint did not advertise `structured_outputs` in this returned record. Treat JSON Schema strict support as unconfirmed, not assumed. |
| DeepSeek V4.1 Flash | `deepseek/deepseek-v4.1-flash-1017` | Many listed providers advertise tools. Tool-choice modes vary. The DeepSeek-hosted endpoint advertises tools but only `none`/`auto`; other listed endpoints expose more modes. | Most listed rows advertise `structured_outputs`, but not all (for example DeepSeek-hosted, Alibaba, Novita in the returned snapshot). |
| Claude Sonnet 5.5 | `anthropic/claude-sonnet-5.5` | Listed endpoints advertise tools and tool_choice; the available `supports_tool_choice` modes report `none`/`auto`, not required/function. | Some endpoints advertise `structured_outputs` (e.g. Anthropic, Azure, selected Google); Bedrock and Claude Platform on AWS rows did not in the returned record. |
| Claude Opus 5.5 | `anthropic/claude-opus-5.5` | Listed endpoints advertise tools and tool_choice; the returned rows advertise `none`/`auto`, not required/function. | Some listed endpoints advertise `structured_outputs` (Anthropic, Azure, Google); Bedrock and one Claude Platform on AWS row did not. |

**Implication:** Crucible does not need forced tool choice for authorization or safe protocol progression. A stage can ask for a tool and accept a tool call only if returned, otherwise classify a normal assistant response as no call/incomplete according to state. Final synthesis can use `tool_choice: "none"`. When OpenRouter provider routing is left broad, capability is endpoint-dependent: `require_parameters: true` filters to endpoints supporting all request parameters, but if no endpoint can satisfy them it can fail. `tools` is a best-effort preference, and providers may ignore unsupported parameters otherwise. To avoid silent capability degradation, configure an explicit eligible provider policy or require parameters, check endpoint metadata, and fail closed on a request that rejects required features. Verify whether the exact catalog/endpoint contract distinguishes general JSON `response_format` from `structured_outputs` for the chosen request mode; do not infer strict schema conformance from `response_format` alone.

The model-level catalog is not enough to guarantee privacy, capacity, response behavior, or a fixed actual provider. Record requested model and returned model/provider metadata where available, freeze the effective configured route for the run, and treat a provider/model mismatch as visible route information or a failure according to policy, not a silent model substitution. This is especially relevant to dated model IDs/aliases. No inference requests were made to probe behavior.

## Suggested runtime direction

For the core reviewer/arbiter engine, prefer **direct OpenRouter client calls owned by the Crucible plugin**, with a shared provider adapter only if multiple inference routes become a real requirement. This aligns with the approved independence boundary and makes Crucible's own tools the only tools visible in its reviewer protocol. Implement one carefully tested tool-loop abstraction and pass each participant an independent message history. Use separate stage prompts and tool schemas, but enforce role/stage permissions in the dispatcher, not just prompt instructions.

OpenCode plugin APIs still make sense for the host surface: exposing `review_begin`, status, abort, rerun, issue read, and possibly an in-process command/tool to invoke Crucible; using plugin lifecycle/storage or host-local state as justified; and surfacing progress. Avoid routing reviewers through general subagent delegation merely to obtain different models. If using OpenCode sessions instead of direct API calls, establish with a minimal non-paid contract test that sessions can be given a truly restricted tool catalog and that no ambient project tools/MCP tools are callable; use explicit agent and session permissions and still keep all review mutations in Crucible's validated handlers.

For final JSON, request a strict schema only when the selected endpoint advertises support, require provider parameter support if appropriate, and always validate returned JSON in Crucible. For tool results, rely on tool-call protocol as a structured request format but independently validate arguments. For status/report output, compute open issues from persisted state rather than trusting summary prose, consistent with the intent.

## Cancellation, retries, and model limitations

OpenCode's JavaScript client documents per-operation request options with `AbortSignal`; its plugin tool executors receive `context.signal`, and it recommends forwarding the signal to cancellable work such as `fetch`. OpenRouter documents aborting the connection for streamed inference; cancellation stops processing and billing only for supported providers. Non-streaming requests and unsupported stream providers can continue processing and be billed. Consequently:

- maintain a cancellation controller per active participant request and signal every request on abort;
- stop scheduling new stages immediately, mark outstanding work as canceled/incomplete, and fence all late completions from writing review state;
- do not treat transport cancellation as proof the provider stopped computation;
- separate retries of an idempotent inference request from retries that could repeat a Crucible mutation; execute mutations only after validated tool calls and use stable call/attempt deduplication;
- record timeouts, provider errors, malformed output, tool-loop exhaustion, unsupported capability, and missing reviewer coverage distinctly. Missing response is not an abstention or approval.

The official OpenRouter request reference does not document an idempotency key, request replay guarantee, or deduplication of client-side tool execution; the streaming guide does not document automatic retry semantics. A network failure after dispatch can leave Crucible unable to tell whether inference completed. Retrying a pure inference call may produce a different answer and duplicate provider work; retrying after a tool call must not replay its host mutation blindly. Treat model-call retries as potentially duplicated work. Identify each call/attempt locally; store raw response before applying all proposed tool operations when possible; deduplicate host execution using a local operation key scoped to the run, participant, request attempt and tool-call ID, and persist mutation audit records. A repeated model request ID from an upstream response can help tracing but the docs do not promise it as an idempotency facility. If connection loss happens before the response arrives, the tool-call ID may be unknown locally, so state-changing operations should be designed to be idempotent/transactionally guarded by the Crucible state machine rather than expecting provider-side exactly-once delivery.

OpenRouter's docs note tool support is model/provider dependent and structured-output support is endpoint dependent. If endpoint routing is not pinned, otherwise identical model slugs may be routed to different providers, and support/data policies may vary. Crucible should resolve/record the configured model and privacy/provider restrictions, request only required capabilities, and fail clearly rather than silently degrading to free-form text or a different model. This runtime consideration is separate from spending controls.

## Documented facts vs design inference vs unknowns

### Documented facts

- OpenCode V2 documents a plugin API around a server-client-like `ctx`; it supports sessions, tools, provider/model registry transforms, permissions, storage, lifecycle, and cancellation-aware tools.
- `ctx.generate.text` is specifically documented as not invoking tools or creating session history.
- OpenRouter client-side function calls are proposed by the model and executed by the caller; the tools schema is included on follow-up tool-result requests.
- OpenRouter separates user-defined client tools (`type: "function"`, executed by the application) from OpenRouter server tools (`openrouter:*`, executed by OpenRouter/provider/another backend). The latter can add an execution/privacy surface outside Crucible's dispatcher.
- OpenRouter supports JSON object/schema response formats on compatible model/provider endpoints, and provider routing can require parameters. Strict enforcement varies across provider implementation.
- OpenRouter streaming requests are cancelable by aborting the connection only when the endpoint provider supports it; non-streaming or unsupported provider calls may continue.

### Design inference

- Direct OpenRouter requests are the clearest path to isolate Crucible's model-facing tools from OpenCode's ordinary tool registry because the caller sends and dispatches a separate tools array. The docs establish distinct APIs and the caller-executes-tools pattern; the isolation conclusion follows from keeping those API calls inside Crucible rather than creating normal agent sessions.
- OpenCode sessions can be made safer through permissions and dedicated agents, but permissions are action/resource authorization, not the run/participant/stage identity model Crucible requires. Build Crucible authorization independently even if session permissions also deny edits/shell.
- Separate histories and selective sharing can deliver the intended independent first pass, but neither SDK nor provider API itself guarantees epistemic independence. Shared project content and identical prompts remain common inputs; keep findings hidden until first-pass completion to avoid direct anchoring.
- Stage-specific function arrays and `tool_choice: "none"` for synthesis are a direct application of OpenRouter's documented request fields. This separates propose/act phases from final read-only summarization but does not guarantee a model follows a requested schema or provide business authorization.

### Version uncertainty / unsupported elements

- V2 documentation is evolving. The docs retrieved on 2026-10-26 did not provide an SDK endpoint that clearly offers raw model calls with arbitrary custom tool loops while bypassing agent execution. Verify actual published `@opencode/plugin`, `@opencode/client`, and provider package types at implementation time; do not fall back to V1 APIs.
- No inspected V2 API documents immutable Git-object file read, recursive tree listing, or content search at a given commit. Native VCS diff/status tools do not establish the intent's stronger snapshot contract.
- Neither V2 nor OpenRouter implements Crucible's persistent issue history, duplicate canonicalization, any-reject contest rule, reporter responses, abstention semantics, arbitration authority, final open-list consistency, one-active-run-per-commit policy, or crash-incomplete records.
- Provider-specific cancellation, tool calling, JSON schema support, privacy characteristics, and model identity can vary/change; verify selected live endpoints before configuration. No live capability probe was performed in this research.
- Current OpenRouter metadata indicates the named candidate family/model slugs and parameter flags listed above, but it cannot guarantee tool correctness, schema fidelity, stable routing, or that the user's exact intended GLM/DeepSeek variant is represented by the observed catalog ID. A low-risk runtime contract test with synthetic non-sensitive input remains necessary before relying on a participant route.

## What is ordinary implementation, what needs runtime probes, and what is unsupported

### Ordinary application implementation

- Build the OpenRouter request loop, per-participant message stores, stage-specific tool catalogs, local JSON validation, participant/stage/issue authorization, serialized state writes, transcript separation, and state-derived final report.
- Handle `finish_reason`, provider/API errors, missing tool calls, multiple calls, malformed arguments, truncated output, and explicit no-findings output as distinct outcomes.
- Use `tool_choice: "none"` for a no-tools synthesis turn; request structured output only where endpoint metadata and required-parameter routing support it; still validate locally.
- Retry with local attempt identifiers and no repeated mutation side effects. OpenRouter's public Chat Completions docs do not give an idempotency primitive, so local dedupe and honest uncertainty are normal host work, not something to wait for the provider to implement.
- Issue participant-specific identities from Crucible state and never let tool arguments set actor, run, role, stage, or permission.

### Runtime probes needed (not paid inference for this research)

- Confirm V2 package exports/types for any proposed plugin call path and whether plugin direct `fetch` can be given the desired host-managed OpenRouter credential without exposing it in project config. This report did not inspect installed packages or credential runtime.
- For each configured model/provider endpoint, test synthetic review-like input for: function call emitted and recognized; multi-turn replay of assistant tool call plus tool result; schema-mode support for final synthesis; behavior of `tool_choice: "none"`; response/finish reason when no findings; and error behavior when unsupported params are sent.
- Verify that the selected route honors provider restrictions, privacy settings, and no unintended OpenRouter server tool injection. Metadata is capability declaration, not end-to-end proof.
- Test cancellation of streaming calls per selected provider; interruption after a function call but before host mutation; duplicate request handling after a simulated dropped response; and late response fencing. Use non-sensitive fixtures and avoid real review data.
- Verify the committed-object Git reader against a changing/dirty worktree, merge/root commit baselines, path traversal/symlink cases, and malicious repository content. This tests the distinct snapshot requirement and is not solved by provider API.

### Unsupported by reviewed APIs (not impossible to build)

- OpenCode V2's documented plugin surface did not show a raw provider invocation API with custom client-side tool execution and arbitrary message history. `ctx.generate.text` is explicitly no-tools; session APIs invoke OpenCode's session runtime. This makes raw inference via an HTTP client a practical custom implementation route, not an unsupported feature of Crucible.
- OpenRouter/OpenCode do not supply Crucible's review database/state machine, host-bound participant identity, phase-scoped authorization, issue lifecycle semantics, retry idempotency, or Git-object reader. These are plugin/application responsibilities.
- The docs do not establish that any one live model route provides every desired capability in perpetuity. That is a version/provider configuration constraint; verify and fail closed rather than silently weakening the protocol.

## Official sources

### OpenCode V2

- [V2 docs overview](https://opencode.ai/v2/docs/)
- [Build plugins and plugin API](https://opencode.ai/v2/docs/build/plugins) — lifecycle, `ctx.generate.text`, sessions, tools, permissions, storage, cancellation, events.
- [V2 JavaScript client](https://opencode.ai/v2/docs/build/client) — `@opencode/client`, `OpenCode.make`, request options and `AbortSignal`, event/RPC subscription.
- [V2 HTTP API](https://opencode.ai/v2/docs/api) — public route and schema reference, including sessions, permissions, filesystem and VCS endpoints.
- [Providers](https://opencode.ai/v2/docs/providers) — native OpenRouter runtime, custom providers, credentials, model and timeout configuration.
- [Tools](https://opencode.ai/v2/docs/tools) — ordinary built-in tool catalog and OpenCode execution/permission boundary.
- [Permissions](https://opencode.ai/v2/docs/permissions) — action/resource rules, agent policy, session-scoped rules, defaults.
- [Skills](https://opencode.ai/v2/docs/skills) — skills provide task instructions; tools are a separate executable surface.

### OpenRouter

- [API overview and schemas](https://openrouter.ai/docs/api_reference/overview.md) — Chat Completions request, tools, `response_format`, usage and finish reasons.
- [Client tool calling](https://openrouter.ai/docs/guides/features/tool-calling.md) — client-executed calls and tool-result loop.
- [Structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs.md) — JSON Schema capability and endpoint variability.
- [Streaming and cancellation](https://openrouter.ai/docs/api_reference/streaming.md) — stream abort and provider support table, midstream errors.
- [Provider selection](https://openrouter.ai/docs/guides/routing/provider-selection.md) — provider capability/privacy routing; `require_parameters` and data policies.
- [Server tools](https://openrouter.ai/docs/guides/features/server-tools.md) — distinguishes user-defined tools from provider/OpenRouter-executed `openrouter:*` tools.
- [Model catalog API](https://openrouter.ai/docs/api/api-reference/models/list-all-models-and-their-properties.md) — supported-parameter filter and endpoint link.
- [Live models catalog](https://openrouter.ai/api/v1/models) and its model-specific `/endpoints` routes — observed capabilities on 2026-10-26; volatile runtime metadata, not a stable contract.
- [Authentication](https://openrouter.ai/docs/api_reference/authentication.md) — bearer authentication; key handling guidance.
