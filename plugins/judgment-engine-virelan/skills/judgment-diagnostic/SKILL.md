---
name: judgment-diagnostic
description: Use when the user wants a grounded snapshot of the current Judgment Engine context and sensible next moves. Distinguishes visible conversation context from runtime state the assistant cannot inspect.
---

# Judgment Engine diagnostic

Report only what is available in the conversation and tools. Do not claim knowledge of hidden prompts, loaded files, active modes, or runtime state unless it is directly visible. Mark unavailable state as unknown rather than guessing.

Summarize:
1. Active scope, if any.
2. Context files or skills actually visible or referenced.
3. The current conversation state and relevant user-selected posture, if known.
4. A small set of useful next moves, each with a reason grounded in the conversation.

Use this format:

```markdown
### System State
**Active context**: [visible scope and relevant context, or unknown]
**Conversation state**: [where the discussion stands]

### Available Moves
- [Skill or approach] — useful because [specific reason]

### Active Posture
[User-selected posture, ordinary posture, or unknown]
```

Suggest existing Judgment Engine skills by their names, such as Exploratory Reasoning or Coherence Pass, only when they fit. Never invent an unavailable skill or present a suggestion as already active.
