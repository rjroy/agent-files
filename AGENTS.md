## SENIOR DEV OVERRIDE

Good architecture balances three tensions: solve the actual problem, keep the solution maintainable, and leave room for obvious growth. Simplicity serves maintainability; it is not an end in itself. Exercise senior judgment rather than following rules mechanically.

## SUB-AGENT SWARMING

For large tasks across independent files, weigh parallel sub-agents against sequential work. Each starts cold and must re-derive context, so parallelism pays off only when the work is sufficiently independent and numerous.

## LOGGING

"Add logging" means more than one failure log around a call. Log state changes, their trigger, and enough context to reconstruct events. At service boundaries (API calls, database writes, queues, external processes, cache invalidation), log both the attempt and outcome. Prefer per-request or per-service-call logging over per-frame or per-loop logging. When in doubt, log where data or control crosses a boundary.

## NEVER

- Edit files in `~/Applications/`. These are the running services.
- Use `sudo`.
- Skip test writing ("add them later" is not acceptable).
- Propose changes to code you haven't read
- Declare work complete without verification
- Make up data. "I don't know" is often the right answer.

## BEADS WORK ROUTING

Label open Beads issues by what must happen next:

- `agentic`: The scope and acceptance criteria are settled; an agent can claim and complete the work without a user decision. This does not waive normal review or validation.
- `escalate`: A user conversation or decision is needed before execution, including discussion-only issues and work contingent on whether a feature will be kept. Do not treat these as implementation authorization.

Apply one of these routing labels when creating or triaging actionable open issues. If a decision resolves an `escalate` issue into executable work, change its label to `agentic` only after the scope is clear, or create a separately approved implementation issue. Keep parent issues consistent with their next required action; completed issues need no routing label. Use `bd list --status=open --label=agentic` and `bd list --status=open --label=escalate` to review the queues. These labels describe routing, not priority or Beads status.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:970c3bf2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` for the full workflow and command reference.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files
- Treat changes in a project's `.beads/` directory as part of the Beads workflow. When committing related work, include the relevant `.beads/` updates even if they were produced by `bd` or another agent process rather than directly edited by the current agent.

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Agent Context Profiles

This guidance is subordinate to explicit user, repository, and orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

When ending a Beads implementation workflow:

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->
