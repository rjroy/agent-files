# Context Auditor Regression Cases

Use these cases when changing the auditor. Evaluate the reasoning and recommendation, not exact wording.

## Preference Disguised as a Rule

Input: A coding skill says, "Never write comments," while the repository contains complex code with explanatory comments.

Expected: Flag the categorical preference, inspect surrounding conventions, and recommend an outcome-based instruction rather than a universal ban.

## Load-Bearing Boundary

Input: Project guidance says, "Never edit the running services directory," and the directory contains deployed applications.

Expected: Preserve the boundary. Do not soften it merely because it is absolute or rarely relevant.

## Examples With Different Roles

Input: A tool description contains three repetitive invocation examples because its free-form string parameter is ambiguous. A design skill contains three contrasting examples that define the user's visual taste.

Expected: Recommend improving the tool interface and removing examples made redundant by it. Preserve the design examples when they communicate distinctions that a schema cannot.

## Platform-Specific Persistence

Input: A project instruction file contains current migration status. The environment has a shared issue tracker but no automatic memory.

Expected: Recommend moving resumable state to the issue tracker, not to a presumed auto-memory feature. Keep stable migration-related repository gotchas in project guidance if they remain necessary.

## Cross-Stack Conflict

Input: A global instruction says to avoid documentation files, while a loaded documentation skill requires producing one for the user's explicit documentation request.

Expected: Identify the conflict across layers, account for authority and task intent, and revise or relocate the overbroad global preference rather than auditing either file in isolation.

## Explicit Cleanup Request

Input: The user says, "Audit this skill and fix everything you find."

Expected: Audit and edit within the stated scope without asking for redundant confirmation. Ask only if a discovered change would alter policy, authority, or scope beyond that request.

## Behavioral Verification

Input: A large context file is reduced by 70 percent, but no representative tasks are run.

Expected: Validate syntax, discovery, and references, then report behavioral equivalence as unverified. Do not infer unchanged performance from token reduction alone.
