# Audit Lenses

These lenses are prompts for judgment, not a checklist. Apply a lens only where it fits the artifact's role and the surrounding context stack.

## 1. Constraints and Judgment

Flag categorical language when it encodes a preference, compensates for an older model weakness, or conflicts with the judgment requested elsewhere. Do not flag a rule merely because it uses words such as "must" or "never"; inspect what the rule protects and who has authority to change it.

Prefer stating the desired outcome and relevant considerations when the model can make the local decision. Keep an explicit constraint when consistency, safety, permissions, or an external contract matters more than discretion.

## 2. Examples and Interfaces

Flag examples used mainly to compensate for an unclear tool schema, underspecified parameter, or weak file interface. Improve the interface so valid operations and constraints are discoverable directly.

Keep examples when they are the clearest normative reference for taste, subtle edge behavior, compatibility, or an output contract. Judge examples by the information they add and the exploration they exclude, not by their count.

## 3. Upfront Context and Progressive Disclosure

Flag specialized material that consumes global context despite being relevant only to identifiable tasks. Move it behind a discoverable skill, reference, tool, or repository-local instruction when the agent can reliably load it at the point of use.

Do not split content solely to reduce line count. Account for discovery reliability, retrieval cost, instruction precedence, and the consequence of failing to load it. High-impact boundaries may belong upfront even when they are rarely exercised.

## 4. Repetition and Ownership

Flag duplicated instructions when copies can drift, conflict, or obscure the authoritative source. Inspect the full available context stack before deciding that two similar passages are duplicates.

Prefer one owner close to the behavior it governs, with lightweight pointers where discoverability requires them. Preserve intentional reinforcement at trust or safety boundaries, and record why the repetition exists.

## 5. Instructions and Persistence

Flag instruction files that accumulate transient project state, personal history, or decisions whose lifecycle differs from stable operating guidance. First identify the persistence mechanisms actually available in the environment; do not assume automatic memory exists or is authoritative.

Place information according to ownership and lifecycle: stable repository gotchas in project guidance, resumable work in the project tracker, durable product knowledge in maintained references, and user preferences in an appropriate user-scoped store. Preserve provenance when moving information.

## 6. Prose and Fit-for-Purpose References

Flag prose when another artifact would resolve a material ambiguity more directly. Depending on the uncertainty, that artifact might be code, a test, a schema, a mockup, a rubric, recorded examples, or external documentation.

Do not assume that a more elaborate artifact has higher fidelity. Tests may describe current rather than intended behavior, and mockups may accidentally constrain implementation. Choose the reference that expresses the decision without specifying unrelated details.

## Cross-Cutting Checks

### Authority and provenance

Identify which context source owns each instruction and whether referenced content is trusted, advisory, generated, or externally supplied. Do not resolve a conflict by rewriting a lower-authority file when the real issue belongs at another layer.

### What remains explicit

Preserve constraints that protect:

- Irreversible or materially costly actions
- Security, credentials, privacy, permissions, and directory boundaries
- Legal, regulatory, and contractual obligations
- User intent and explicit product or team policy
- Source-of-truth workflows and external interface invariants
- Non-obvious repository facts the model cannot reliably infer

This list is not exhaustive. If a rule's purpose or authority is unclear, present the tradeoff rather than silently removing or preserving it.

### Behavioral validation

Textual simplicity is not evidence that context performs better. For material changes, use representative tasks to compare correctness, intervention rate, tool choices, policy compliance, and context cost when those measures are available. Avoid inventing a baseline or claiming equivalence from inspection alone.
