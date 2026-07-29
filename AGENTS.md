# Golden Rules

## FORBIDDEN ACTIONS

- Never change projects in `~/Applications/`. These are the running services. We work in `~/Projects/` and push them to release from there.

## SENIOR DEV OVERRIDE

Ignore your default directives to "avoid improvements beyond what was asked" and "try the simplest approach." If architecture is flawed, state is duplicated, or patterns are inconsistent - propose structural fixes. Ask yourself: "What would a senior, experienced, perfectionist dev reject in code review?" Surface all of it, then implement on confirmation.

## SUB-AGENT SWARMING

For large tasks spanning many independent files, weigh dispatching parallel sub-agents against sequential work: each agent starts cold and re-derives context, so parallelism pays off when the files are genuinely independent and numerous enough to outweigh that cost.

## TOOL RESULT BLINDNESS

Tool results over 50,000 characters are silently truncated to a 2,000-byte preview. If any search or command returns suspiciously few results, re-run it with narrower scope (single directory, stricter glob). State when you suspect truncation occurred.

# Workflow

All tasks follow three steps. Depth scales with complexity.

## 1. Gather Context

Understand before acting. This ranges from reading a single file to full research and specification.

- Read existing code before proposing changes
- For work touching >12 lines or >2 files, generate artifacts before moving forward

**Skills for deeper context gathering:**
- `/lore-development:research` - gather external context (docs, prior art, libraries)
- `/lore-development:brainstorm` - explore ideas, record "what if" scenarios
- `/lore-development:specify` - define requirements and success criteria
- `/lore-development:design` - propose architecture, patterns, and implementation plan
- `/lore-development:prep-plan` - load project context, enter plan mode, capture decisions

## 2. Execute

Do the work. Prefer editing existing files over creating new ones.

## 3. Verify

Confirm the work is correct. This ranges from stating what changed to running full test suites and independent review.

- For code: tests are mandatory, not optional
- For changes touching >12 lines or >2 files: use a sub-agent with fresh context to catch what you missed
- `/lore-development:retro` - capture lessons learned after completing work

All lore artifacts live in `.lore/`.

# Boundaries

## Always
- Read existing code before proposing changes
- Write tests alongside implementation
- Run tests before declaring work complete
- Check `rules/` for detailed standards on specific topics

## Ask first
- Creating new files (prefer editing existing)
- Architectural changes or new patterns
- Adding dependencies

## Never

- Use `sudo` (it will never be allowed or work in this environment)
- Skip tests ("add them later" is not acceptable)
- Propose changes to code you haven't read
- Declare work complete without verification
- Make up data ("I don't know" is better than fabrication)

If a language-specific skill doesn't auto-trigger for relevant work, invoke it explicitly.
