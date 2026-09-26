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

