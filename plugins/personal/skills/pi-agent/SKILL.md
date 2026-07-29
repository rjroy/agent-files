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

// 3. createAgentSession — destructure the result, it is NOT just `session`
const { session, modelFallbackMessage } = await createAgentSession({
  cwd,
  resourceLoader: loader,
  sessionManager: manager,
});

// 4. bindExtensions — runs queued extension work: providers, hooks, event handlers
//    Pass {} when there is no UI. Without this, extension-registered models won't exist.
await session.bindExtensions({});

// 5. setModel — look up from session.modelRegistry (NOT a standalone ModelRegistry.create())
//    Only session.modelRegistry sees extension-registered providers after bindExtensions.
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

### Extract final assistant text
```typescript
import type { AgentMessage } from "@earendil-works/pi-agent-core";

function finalText(messages: AgentMessage[]): string {
  const last = [...messages].reverse().find((m) => m.role === "assistant");
  if (!last) return "";
  return last.content
    .filter((b) => b.type === "text")
    .map((b) => (b as { type: "text"; text: string }).text)
    .join("\n");
}
```

### Constrain tools
```typescript
// Allowlist by name
const { session } = await createAgentSession({
  cwd, resourceLoader: loader, sessionManager: manager,
  tools: ["read", "grep", "find", "ls"],
});

// Disable builtins, use only custom tools
const { session } = await createAgentSession({
  cwd, resourceLoader: loader, sessionManager: manager,
  noTools: "builtin",
  customTools: [myToolDefinition],
});
```

### Custom tool
```typescript
import { defineTool } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

const myTool = defineTool({
  name: "lookup_record",
  description: "Fetch a record by id",
  inputSchema: Type.Object({ id: Type.String() }),
  async execute({ args }) {
    const record = await db.get(args.id);
    return { content: [{ type: "text", text: JSON.stringify(record) }] };
  },
});
```

### Custom system prompt
Pass `systemPrompt` to `DefaultResourceLoader`, not to `createAgentSession` — that option doesn't exist on the session.
```typescript
const loader = new DefaultResourceLoader({
  cwd, agentDir: getAgentDir(),
  systemPrompt: "You are a specialist in...",
});
```

### Gate tool calls
```typescript
function gatingExtension(): ExtensionFactory {
  return (pi) => {
    pi.on("tool_call", async (event) => {
      if (event.toolName === "bash" && /rm -rf/.test(event.args.command ?? "")) {
        return { block: true, reason: "rm -rf is not allowed" };
      }
    });
  };
}

const loader = new DefaultResourceLoader({
  cwd, agentDir: getAgentDir(),
  extensionFactories: [gatingExtension()],
});
await loader.reload();
```

### Abort mid-turn
```typescript
setTimeout(() => session.abort(), 30_000);
await session.prompt(input); // resolves on abort, does not throw
```

### Streaming visibility
Subscribe **before** calling `prompt()`. Returns an unsubscribe function.
```typescript
const unsubscribe = session.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
  if (event.type === "tool_execution_start") console.error(`[tool] ${event.toolName}`);
});
try {
  await session.prompt(prompt);
} finally {
  unsubscribe();
}
```

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
