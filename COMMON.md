## SENIOR DEV OVERRIDE

Good architecture balances three tensions: solve the actual problem, keep the solution maintainable, and leave room for obvious growth. Simplicity serves maintainability; it is not an end in itself. Exercise senior judgment rather than following rules mechanically.

## COMMUNICATION

Use plain, direct language. Explain what you found, what you recommend, and what needs my permission. Prefer concrete verbs: “copy the file,” “keep the original,” “change its status.” Don’t repeat terminology from tools or specialists unless it is necessary. Don’t turn criticism of your communication into a glossary or a lesson.

## SUB-AGENT SWARMING

For large tasks across independent files, weigh parallel sub-agents against sequential work. Each starts cold and must re-derive context, so parallelism pays off only when the work is sufficiently independent and numerous.

## LOGGING

"Add logging" means more than one failure log around a call. Log state changes, their trigger, and enough context to reconstruct events. At service boundaries (API calls, database writes, queues, external processes, cache invalidation), log both the attempt and outcome. Prefer per-request or per-service-call logging over per-frame or per-loop logging. When in doubt, log where data or control crosses a boundary.

## TEST ISOLATION

- Unit tests must verify algorithms with controlled, test-owned inputs and mocked dependencies, not mutable production configuration or live project data.
- Integration tests may use real configuration and data to verify contracts and that the system works together. They must not hardcode current tuning choices as permanent requirements.
- Valid configuration or content changes must not break unit tests. When they do, fix the test isolation rather than reverting user settings, replacing expected constants with today's values, or weakening coverage.
- Choose the correct testing boundary over the quickest way to make tests pass. This is a standing requirement across projects.

## NEVER

- Edit files in `~/Applications/`. These are the running services.
- Use `sudo`.
- Skip test writing ("add them later" is not acceptable).
- Propose changes to code you haven't read
- Declare work complete without verification
- Make up data. "I don't know" is often the right answer.

## BEADS WORK ROUTING

### Branches and checkpoints

- Before implementing a sequence of Beads issues, create or switch to a dedicated working branch. Keep the sequence on that branch; do not implement directly on the repository's default branch.
- After each bead is completed and verified, create a checkpoint commit before starting the next bead. Include only that bead's changes and relevant `.beads/` updates, leaving unrelated work untouched. Reference the bead ID in the commit message.
- This rule authorizes local checkpoint commits for the sequence, overriding the default requirement to ask before committing. An explicit "do not commit" instruction still wins. Pushing, merging, and remote sync require separate authorization.
- If validation or committing is blocked, stop and report the blocker rather than continuing to the next bead. If a bead produces no file changes, record its completion in Beads without creating an empty commit.

### Routing labels

Label open Beads issues by what must happen next:

- `agentic`: The scope and acceptance criteria are settled; an agent can claim and complete the work without a user decision. This does not waive normal review or validation.
- `escalate`: A user conversation or decision is needed before execution, including discussion-only issues and work contingent on whether a feature will be kept. Do not treat these as implementation authorization.

Apply one of these routing labels when creating or triaging actionable open issues. If a decision resolves an `escalate` issue into executable work, change its label to `agentic` only after the scope is clear, or create a separately approved implementation issue. Keep parent issues consistent with their next required action; completed issues need no routing label. Use `bd list --status=open --label=agentic` and `bd list --status=open --label=escalate` to review the queues. These labels describe routing, not priority or Beads status.
