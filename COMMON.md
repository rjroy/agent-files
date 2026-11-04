## ENGINEERING JUDGMENT

Good architecture balances three tensions: solve the actual problem, keep the solution maintainable, and leave room for obvious growth. Simplicity serves maintainability; it is not an end in itself. Exercise senior judgment rather than following rules mechanically.

Build incrementally toward the agreed architecture. Reduce scope, not architectural integrity: an MVP must be viable, not a disposable substitute for the planned system. Build a proof of concept only when explicitly requested. If the architecture needs to change, discuss it before departing from the plan.

When coordinating substantive implementation, follow the `implement` skill. Delegated workers execute their bounded assignments without restarting it. Correct behavior is necessary but not sufficient: assess maintainability, complexity, and relevant efficiency before declaring completion, with depth proportionate to the change.

## COMMUNICATION

Use plain, direct language and concrete verbs. State findings, recommendations, and needed permissions. Avoid unnecessary specialist terminology. Adjust to feedback without lecturing.

## SUB-AGENT SWARMING

Use parallel agents when independent work outweighs their context-loading cost.

## LOGGING

Log state changes, their triggers, and enough context to reconstruct events. At service boundaries (API calls, database writes, queues, external processes, cache invalidation), log both the attempt and outcome. Prefer per-request or per-service-call logging over per-frame or per-loop logging. When in doubt, log where data or control crosses a boundary.

## TESTING

- Do not skip or defer test writing.
- Unit tests must verify algorithms with controlled, test-owned inputs and mocked dependencies, not mutable production configuration or live project data.
- Integration tests may use real configuration and data to verify contracts and that the system works together. They must not hardcode current tuning choices as permanent requirements.
- Valid configuration or content changes must not break unit tests. When they do, fix the test isolation rather than reverting user settings, replacing expected constants with today's values, or weakening coverage.
- Choose the correct testing boundary over the quickest way to make tests pass.
- Cleaning up tests is as important as adding them. Inspect existing coverage first; improve or replace inadequate tests rather than automatically adding another.
- Remove redundant or superseded tests, fixtures, and test infrastructure. Retain overlapping or combination tests when they protect distinct failure modes or integration boundaries, not merely because they already exist.
- Preserve meaningful coverage, not test counts. Ask what failure would escape if a test were removed; do not weaken assertions or delete useful coverage just to reduce code.

## NEVER

- Edit files in `~/Applications/` unless working from `~/.dotfiles` on a user-requested deployment or service-configuration change. These are running services; the dotfiles agent may make the necessary production configuration and deployment changes, preserving private data and unrelated settings, and verifying the result. This exception does not authorize unrelated application development in production.
- Use `sudo`.
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

Apply one of these routing labels when creating or triaging actionable open issues. If a decision resolves an `escalate` issue into executable work, change its label to `agentic` only after the scope is clear, or create a separately approved implementation issue. Keep parent issues consistent with their next required action; completed issues need no routing label. These labels describe routing, not priority or Beads status.
