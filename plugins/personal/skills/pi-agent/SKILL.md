---
name: pi-agent
description: This skill should be used when the user is writing, reviewing, or debugging code that imports from @earendil-works/pi-coding-agent or @earendil-works/pi-agent-core. Triggers when the user asks to "initialize a pi-agent session", "set up pi-agent", "create an AgentSession", "configure a model with pi-agent", "add a custom tool to pi-agent", "gate tool calls in pi-agent", or encounters errors like model not found, prompt() failing, or bindExtensions not working.
---

# Pi-Agent

## Mandatory Initialization Sequence

This order is not optional. Deviating from it causes silent failures.

```typescript
// 1. SessionManager — inMemory for one-shots, create/continueRecent for persistence
const manager = SessionManager.inMemory(cwd);

// 2. ResourceLoader — reload() is mandatory even with no extensions
const loader = new DefaultResourceLoader({ cwd, agentDir: getAgentDir() });
await loader.reload();

// 3. createAgentSession — destructure the result (see Critical Gotchas)
const { session, modelFallbackMessage } = await createAgentSession({
  cwd,
  resourceLoader: loader,
  sessionManager: manager,
});

// 4. bindExtensions — pass {} when there is no UI (see Critical Gotchas)
await session.bindExtensions({});

// 5. setModel — look up from session.modelRegistry (see Critical Gotchas)
const model = session.modelRegistry.find("openrouter", "openrouter/free");
if (!model) throw new Error("model not found in session registry");
await session.setModel(model);

// 6. prompt — resolves after ALL internal tool turns complete. No outer loop needed.
await session.prompt(prompt);
```

## Critical Gotchas

**`createAgentSession` returns `{ session, extensionsResult, modelFallbackMessage }`**, not just `session`. Destructure it — never assign the return value directly to `session`.

**The `model:` option on `createAgentSession` does not wire the model in.** The session starts model-less; `prompt()` will fail. Call `setModel()` after `bindExtensions()`.

**`bindExtensions` is not just for UI.** It runs queued `registerProvider()`, `pi.on()`, and `registerCommand()` calls from extension factories. Skip it and extension-registered models won't appear in `session.modelRegistry`, and `tool_call` / `before_agent_start` hooks never fire.

**`session.modelRegistry` vs `ModelRegistry.create()`.** A standalone registry only sees built-in models and `~/.pi/agent/models.json` overrides. Extension-contributed providers only exist on `session.modelRegistry`, and only after `bindExtensions`. Use `session.modelRegistry` to find dynamic models — not a standalone instance.

**Tool output events are snapshots, not deltas.** `tool_execution_update.partialResult.content[].text` is accumulated output. Replace, never append.

**`AgentMessage` lives in `@earendil-works/pi-agent-core`, not `pi-coding-agent`.** Import from the right package.

**`session.prompt()` resolves when the entire tool loop finishes.** Don't write an outer loop. Pi handles tool call → execute → feed back → continue internally.

## Common Patterns

For extracting final assistant text, constraining/disabling tools, defining a custom tool, setting a custom system prompt, gating tool calls, aborting mid-turn, or subscribing to streaming events, load `reference/common-patterns.md`.

## Session Strategies

| Strategy | When |
|---|---|
| `SessionManager.inMemory(cwd)` | One-shots, stateless processing |
| `SessionManager.create(cwd)` | Persist this run to `.jsonl` |
| `SessionManager.continueRecent(cwd)` | Resume most recent session for this cwd |
| `SessionManager.open(path)` | Resume a specific `.jsonl` file |

Avoid `continueRecent` when multiple processes share a cwd — it grabs whichever session file is newest, which may belong to another process.

## Credentials

Credentials live in `~/.pi/agent/auth.json` by default, managed by `pi auth`. The model registry can fall back to env vars, but `pi auth` is the expected path on a clean install.
