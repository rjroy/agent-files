# Common Patterns

Situational code patterns for pi-agent. Load this when the task needs one of the specific patterns below — not required for basic session setup (see main SKILL.md for that).

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
