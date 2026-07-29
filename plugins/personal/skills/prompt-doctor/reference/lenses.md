# The Six Lenses

Each lens is a then→now shift. Apply all six to every file in scope.

## 1. Rules → Judgment

**Flag:** absolute language ("never", "always", "must", "default to") guarding a preference rather than a worst-case outcome. Look for pairs of rules elsewhere in the same context stack that already contradict it — that's the signal it's a hedge, not a guardrail.

**Rewrite:** replace the absolute with a description of the judgment call. "Never write comments" → "Write code that reads like the surrounding code: match its comment density, naming, and idiom."

**Don't flag:** rules that prevent irreversible harm (destructive git ops, `sudo`, secrets, deleting user files) — see "What stays" below.

## 2. Examples → Interfaces

**Flag:** worked examples included to teach a tool or format, especially several examples showing the same shape of case.

**Rewrite:** strengthen the schema/description instead — better field names, an enum instead of a free string, a doc-comment on the parameter. One example is a spec; three examples are a cage. If the interface can't be made self-explanatory, keep at most one example and say why the others were cut.

## 3. Upfront → Progressive Disclosure

**Flag:** a file that bundles material only needed in specific circumstances (verification steps, edge-case handling, a rarely-touched sub-topic) into the always-loaded body.

**Rewrite:** split the conditional material into a `reference/`-style file or a separate skill, and leave a one-line pointer in the main file describing when to load it. Don't split a file that's already short (~under 100 lines) just to split it.

## 4. Repeat Yourself → Say It Once

**Flag:** the same instruction stated in more than one place in the stack (system prompt / CLAUDE.md / skill / tool description) — usually a sign it was added because an earlier instance seemed to be ignored.

**Rewrite:** keep the instance closest to where it's used (tool description over CLAUDE.md; skill over general instructions) and delete the rest. Note where each duplicate lived, in case the reason for the redundancy turns out to be intentional emphasis rather than drift.

## 5. CLAUDE.md-as-Memory → Auto-Memory

**Flag:** CLAUDE.md content that records facts about the user, prior decisions, or standing project state rather than durable, project-invariant instructions (e.g. "we're currently migrating X", "the user prefers Y", running logs of past choices).

**Rewrite:** note that this belongs in the memory system instead, and describe what memory type it maps to (user/feedback/project/reference) rather than moving it yourself — memory files aren't something this skill writes directly to CLAUDE.md's replacement.

**Don't flag:** genuinely static, project-invariant gotchas ("types live in one file, nowhere else") — those stay in CLAUDE.md because they're facts about the codebase's shape, not about a person or a moment in time.

## 6. Simple Specs → Rich References

**Flag:** a plan/spec described only in prose where a higher-fidelity artifact would remove ambiguity — a UI change described in words instead of an HTML mockup, a behavior described in words instead of a test.

**Rewrite:** suggest the richer reference (code, test, mockup, rubric) as a companion or replacement, without fabricating one — only propose this where the user can supply or approve the richer artifact.

---

## What stays

Never propose removing or softening:
- Anything preventing irreversible or destructive actions (force-push, `rm -rf`, `sudo`, credential/secret handling, deleting files/branches without confirmation).
- Anything scoping which directories or systems are off-limits (e.g. "never touch the running services directory").
- Product- or team-specific facts the model has no other way to learn (naming a specific tracker, a non-obvious build quirk, a compliance constraint).

If a rule is ambiguous between "hedge" and "guardrail," flag it as a question for the user rather than silently keeping or cutting it.
