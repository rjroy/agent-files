Show current system state and available moves in the current context.

Display:
1. Active scope (if any)
2. Loaded context files and modes
3. Always-on posture files in play
4. Current conversation state
5. Available next moves based on context

Suggest possible modes or skills that would be useful given the current conversation direction.

Output format:
```
### System State
**Active context**: [what's loaded]
**Conversation state**: [where we are]

### Available Moves
- [Skill/mode suggestion 1] - useful because [reason]
- [Skill/mode suggestion 2] - useful because [reason]
- [Command suggestion] - useful because [reason]

### Active Posture
[Current tone/stance of responses]
```
