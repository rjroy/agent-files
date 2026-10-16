# Agent Error Handling Pattern

## Purpose

This document defines the standard error handling pattern for all Story Engine agents. Reference this pattern instead of duplicating retry/escalation logic inline.

## Pattern: Retry-Once-Then-Escalate

When an operation fails, follow this sequence:

1. **First Attempt Fails** → Log the error and retry once with same parameters
2. **Retry Fails** → Escalate to user with diagnostic information and recovery options

## Diagnostic Information Format

When escalating to user, provide:

```
ERROR: [Clear description of what failed]

Context:
- Operation: [What was being attempted]
- Location: [Relevant file path or state]
- Error Type: [Category: spawn failure, write failure, validation failure, etc.]

Diagnostic Details:
[Technical details that help identify root cause]
```

## User Choice Presentation Template

After presenting diagnostic information, offer recovery options:

```
Recovery Options:
1. [Primary recovery action - usually retry with modification]
2. [Alternative action - workaround or skip]
3. [Manual intervention option - user fixes and resumes]

Please choose option 1, 2, or 3, or type 'abort' to stop.
```

## Specific Error Scenarios

### Agent Spawn Failure (REQ-F-45)
```
First attempt fails → Retry once → If retry fails:

ERROR: Agent spawn failed

Context:
- Operation: Spawning [agent-name] for [purpose]
- Slim role prompt: repository-root `omo-slim-agents/[reviewer|code-reviewer|writer|developer].md`
- Procedure: resolve the selected ID through `agent-procedures` and its canonical index; specialist procedures are not root prompt files

Diagnostic Details:
- First attempt: [error message]
- Retry attempt: [error message]

Recovery Options:
1. Retry with fresh context (I will simplify the task description)
2. Skip this agent and continue workflow (may affect quality)
3. Pause and allow manual inspection of agent file

Please choose option 1, 2, or 3, or type 'abort' to stop.
```

### File Write Failure (REQ-F-47, REQ-F-53)
```
Write fails → Preserve in-memory state → Offer recovery:

ERROR: File write operation failed

Context:
- Operation: Writing [file type]
- Target Path: [full path]
- Content Size: [approximate size]

Diagnostic Details:
- Error: [filesystem error message]
- Possible Causes: Insufficient disk space, permission denied, filesystem error

Recovery Options:
1. Retry write to same location (check disk space first)
2. Write to alternate location [suggest path]
3. Save content to temporary file and continue (you can move it manually later)

In-memory state preserved and ready for retry.

Please choose option 1, 2, or 3, or type 'abort' to stop.
```

### Empty/Invalid Output (REQ-F-50)
```
Agent produces empty/invalid output → Retry with explicit instruction → If retry fails:

ERROR: Agent produced invalid output

Context:
- Operation: [agent-name] generating [output type]
- Expected: [what should have been produced]
- Received: [what was actually produced - empty, malformed, etc.]

Diagnostic Details:
- First attempt: [description of invalid output]
- Retry with explicit instruction: [description of retry result]

Recovery Options:
1. Manual generation (provide input context and I'll generate inline)
2. Skip this element and mark for manual completion later
3. Adjust requirements and retry (reduce complexity)

Please choose option 1, 2, or 3, or type 'abort' to stop.
```

### Corrupted/Malformed Files (REQ-F-46, REQ-F-48)
```
File validation fails → Report specific errors → Offer recovery:

ERROR: Story state file corrupted or malformed

Context:
- File: [specific file path]
- File Type: [PLAN.md, character profile, chapter, etc.]
- Validation Step: [when detected - on load, during operation]

Diagnostic Details:
[Specific formatting errors with line numbers]
Example: "Line 15: Missing required frontmatter field 'total_chapters'"

Recovery Options:
1. Reinitialize from last valid checkpoint [specify checkpoint]
2. Continue with valid portions only (invalid sections ignored)
3. Manual repair (I'll guide you through fixing the file)

Please choose option 1, 2, or 3, or type 'abort' to stop.
```

### Continuity Contradictions (REQ-F-51)
```
Contradiction detected that cannot be auto-resolved → Present options:

ERROR: Continuity contradiction detected

Context:
- Contradiction: [clear description]
- Affected Chapters: [list chapters with line references]

Example:
Chapter 5, lines 245-248: "Aria escapes from the cell and runs into the forest"
Chapter 6, lines 12-15: "The interrogator enters Aria's cell for questioning"

Diagnostic Details:
This creates a spatial/timeline contradiction - Aria cannot both be escaped and still imprisoned.

Resolution Options:
1. Revise Chapter [later number] to fix continuity
2. Revise Chapter [earlier number] to fix continuity
3. Mark as intentional (explain narrative mechanism - flashback, parallel timeline, etc.)

Please choose option 1, 2, or 3.
```

### Conflicting State (REQ-F-49, REQ-F-52)
```
Multiple valid sources conflict → Ask user for source of truth:

ERROR: Conflicting story state detected

Context:
- Conflict Type: [missing directory, conflicting plans, etc.]
- Sources: [list conflicting sources]

Diagnostic Details:
[Specific differences between sources]

Resolution Options:
1. Use [source A] as canonical
2. Use [source B] as canonical
3. Merge both (I will reconcile differences and show you the result)
4. Start fresh (reinitialize story state)

Please choose option 1, 2, 3, or 4.
```

## Usage in Agent Files

In agent definitions, reference this pattern instead of implementing inline:

```markdown
## Error Handling

**Agent Spawn Failures**: Follow retry-once-then-escalate pattern from `utils/agent-error-pattern.md`

**File Write Failures**: Follow file write failure pattern from `utils/agent-error-pattern.md`

**Invalid Output**: Follow empty/invalid output pattern from `utils/agent-error-pattern.md`
```

In command orchestrators, reference this pattern when spawning agents:

```markdown
If agent spawn fails, follow the Agent Spawn Failure pattern from `utils/agent-error-pattern.md`:
- Retry once with same parameters
- On second failure, present diagnostic information and recovery options to user
```

This reduces each error handling section from ~50 lines to ~5-10 lines of reference.
