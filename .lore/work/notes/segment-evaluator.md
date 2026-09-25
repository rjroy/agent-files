---
title: Segment evaluator phase 1 implementation record
date: 2026-09-24
status: complete
source: .lore/work/research/workflow-comparison-candidates-and-trial-protocol.md
tags: [workflow, segments, evidence, implementation]
---

# Segment evaluator — phase 1

The source protocol is historical and superseded for formal trials. This work
does not authorize, register, or conduct a formal workflow comparison. Formal
trials require a separately reviewed, current protocol and remain subject to
Beads/Git authority and independent acceptance.

## Phases and checklist

- [x] Phase 1: define an explicit multi-turn segment domain, conservative
  outcome semantics, scoped portable persistence boundary, and focused tests.
- [x] Phase 2: add an explicit local OpenCode V2 adapter with scoped storage,
  explicit tools, mocked integration tests, and no global registration.
- [x] Phase 3a: provisional-first outcome handling; model-tool adjudications are
  retained as unverified proposals and effective outcomes remain unknown.
- [x] Phase 3b: install narrowly scoped prompt and tool lifecycle metadata hooks;
  keep content/arguments/results out, with explicit split/close lifecycle tools.
- [x] Phase 3c: add safe bounded context discovery without injecting stored prose
  or triggering model calls; explicit detail/recall remains required.
- [x] Phase 3d: review SE-FINAL-001 accepted; terminal tests/typecheck and the
  limited private host prompt smoke are recorded below. Recall/tool/context
  behaviors remain mock-validated only; no global registration is claimed.
- [x] Phase 4: add explicit allowlisted local session-directory scoping, using
  per-entrypoint host session metadata, realpath equality, and durable session
  scope binding; do not activate globally.
- [ ] Phase 5: separately assess whether formal-trial registration is warranted;
  this implementation is not trial evidence or authorization.

## Obligation-to-validation map

| Obligation | Validation mapping |
| --- | --- |
| Workspace-scoped storage and recall | `tests/segment.test.ts`: `recall is workspace-isolated` |
| Explicit multi-turn sessions, attempts, interventions, and rescue basis | `tests/segment.test.ts`: `supports a multi-turn retry...` |
| Reconstructed notebook failure requires explicit user judgment; tool event is informational | `tests/segment.test.ts`: `retrospectively reconstructs failed notebook attempt...` |
| Success cannot be inferred from tool success or assistant self-report | `tests/segment.test.ts`: `tool success, idle state, or assistant self-report...` |
| Criterion revisions remain visible and findings identify versions | `tests/segment.test.ts`: `keeps criteria revisions...` |
| Evidence is represented by references, not copied transcript bodies | Domain schema stores `EvidenceReference.uri`; no transcript field exists; code/schema review required |
| Model-tool judgment authority remains provisional-first; caller claims/URIs cannot certify outcome | `tests/adapter.test.ts`: `caller-spoofed judgments remain unverified...`; domain trusted representation is not wired to a model-callable tool |
| Legacy accepted adapter records downgrade to unknown/unverified on recall and detail | `tests/adapter.test.ts`: `caller-spoofed judgments remain unverified...` |
| Tool annotations bind observed session/message and do not trust caller session identifiers | Same test checks host producer IDs; detail test checks producer metadata for intervention and other annotations |
| Same-instance workspace writes serialize, duplicate opens conflict visibly, and failures do not poison queue | `tests/adapter.test.ts`: `workspace write queue preserves overlapping mutations...`, `duplicate concurrent opens serialize...` |
| Criteria agreement/finding/intervention/lesson provenance remains visibly unverified | `tests/adapter.test.ts`: `later session reads paginated detail...` checks unverified labels in recall/detail |
| First prompt creates provisional unknown candidate; turn refs dedupe; restart reuses candidate without prompt body | `tests/adapter.test.ts`: `prompt hook creates one unknown provisional candidate...` |
| Explicit split/close lifecycle associates to observed source prompt without deciding outcome | `tests/adapter.test.ts`: `new-intent split and lifecycle close require an observed source prompt...` |
| Hook status metadata captures failed and passing events, excludes notebook tools, stores no bodies, and never creates attempts/outcomes | `tests/adapter.test.ts`: `tool hooks capture only bounded status references...` |
| Prompt hook failure is nonblocking and warning appears on following recall; missing/denied directory scope fails closed | `tests/adapter.test.ts`: `automatic capture storage failures...`, `directory scopes isolate worktrees...` |
| Durable prompt ownership deduplicates replay after close/split/restart; split source belongs to both only by explicit rule | `tests/adapter.test.ts`: `creation transitions recover...`, `split transitions recover...`, `close transitions recover...` |
| Candidate create/split/close transitions recover at each injected storage boundary without losing annotations or active pointer | Same three boundary-loop tests inject failure at every marker/record/owner/pointer/remove write and retry or restart |
| Invalid candidates are rejected before journaling; already persisted invalid markers are quarantined without poisoning future session work | `tests/adapter.test.ts`: `invalid split candidates are rejected before journaling...` |
| Persisted marker fields are runtime-validated and malformed numeric close IDs quarantine without mutating valid partial state | `tests/adapter.test.ts`: `malformed close marker with numeric ID is quarantined...` |
| Criterion changes cannot retain a current accepted outcome | `tests/segment.test.ts`: `criterion revision makes prior acceptance unknown...`; prior adjudication and criterion versions remain visible |
| Persisted schema, outcome, uniqueness, and finding references are validated | `tests/segment.test.ts`: `rejects malformed persisted values on get and list` |
| Explicit V2 actions, two-session continuity, workspace isolation, storage failure, and unknown outcome | `tests/adapter.test.ts`: `explicit tools persist across sessions...`, `storage failures...`, `adapter exposes only explicitly registered tools...` |
| Workspace recall uses update recency with deterministic tie-break and survives update of older record | `tests/adapter.test.ts`: `recall sorts by updatedAt with an ID tie-break...` |
| Later-session detail read reaches records outside recall top five, paginates history, returns evidence refs inertly, and labels historical data untrusted | `tests/adapter.test.ts`: `later session reads paginated detail for a record outside the five most recent` |
| Detail read preserves long evidence URIs exactly while bounding descriptions | Same adapter test asserts round-trip for a URI longer than 240 characters |
| Context reminder exposes no dynamic IDs/counts/outcomes or stored prose to the model | `tests/adapter.test.ts`: `context discovery exposes only a static reminder...` asserts exact text-only system part without metadata; malicious intent/lesson/prompt/message bodies are absent |
| Records remain available to later sessions only through explicit same-workspace recall then detail tools; reminder is idempotent without model calls | Same context-discovery test exercises repeated context calls, workspace separation, explicit recall, and detail lookup; `long segment IDs remain exact...` |
| Context storage failure is nonblocking and warned on next tool | `tests/adapter.test.ts`: `context discovery failure is nonblocking and reported on next explicit tool` |
| Directory allowlist scope is based on canonical actual session location, not plugin-load location or workspaceID; unrelated worktrees/prefix traps are denied, symlink aliases canonicalize, missing environment/metadata and realpath errors fail closed | `tests/adapter.test.ts`: `directory scopes isolate worktrees...` |
| Session directory movement cannot reassign existing records, including after restart; execute.after uses/validates scope observed before execution | `tests/adapter.test.ts`: `session relocation fails closed across hooks and restart...` |
| Denied before/after hooks are nonthrowing and use event session ID fallback for warnings; missing/denied scope creates no storage entries | `tests/adapter.test.ts`: directory-scope test invokes denied before/after and compares storage keys before/after, plus missing-env zero-key assertion |
| Every queued read/write/injection revalidates host directory at queue acquisition; stale queued operations do not access data or mutate | `tests/adapter.test.ts`: `queued operations revalidate directory after waiting...` blocks an earlier write, relocates the session, then verifies queued write/read fail and only the in-flight write remains |
| Scoped TypeScript checks cover adapter, core, and tests against the installed V2 plugin declarations | Temporary dependency-linked context: requested strict `tsc` flags plus `--typeRoots "$ctx/node_modules/@types"` for linked `bun,node` declarations; uses installed `@opencode/plugin` 2.0.11 and cached TypeScript 5.8.3 without project dependency changes |
| Split transition replay treats candidate creation identity as immutable while preserving later criteria revisions | `tests/adapter.test.ts`: `split replay preserves a later session's criterion revision after marker-removal failure` covers same-instance and restart recovery; `transition replay still rejects an unrelated segment ID collision` retains collision protection |
| Private V2 prompt hook behavior | Isolated OpenCode v2.0.14 no-resume prompt observation stored one active `unknown` candidate and no prompt body; this evidence covers prompt capture only |
| Recall, explicit tools, and context hook host integration | Mocked V2 adapter tests only; no private host test of those paths and no global plugin registration claim |
| Final review acceptance | SE-FINAL-001 accepted; final changed-file manifest and validation are listed in the handoff below |
| Beads/Git/independent acceptance stay authoritative | Only explicit user/reviewer judgment or a traceable external record can adjudicate; no Beads/Git mutation exists; independent review remains required |

## Log

- 2026-09-24: Implemented the domain/store boundary and focused behavioral tests.
- 2026-09-24: Reviewer corrections tightened outcome authority, bound adjudication
  to criterion versions, and added runtime persisted-shape checks.
- 2026-09-24: Added the local V2 tool adapter on `ctx.storage`. At initial
  implementation, keys used `ctx.location.workspaceID`; Phase 4 below replaces
  that scope with the explicit allowlisted session-directory scheme.
- 2026-09-24: Review corrections sort workspace recall by `updatedAt` descending
  with deterministic ID tie-break and add paginated `segment_read_detail` for
  full stored history without dereferencing evidence URIs.
- 2026-09-24: Corrected detail rendering to preserve evidence URI identifiers
  exactly while continuing to bound descriptive text.
- 2026-09-24: Provisional-first phase 3a stores model-tool adjudications as
  unverified proposals, downgrades legacy adapter judgments on read, binds
  observed tool session/message provenance, and serializes workspace mutations
  per plugin instance. Multi-instance/cross-process locking is not provided.
- 2026-09-24: Phase 3b adds the V2 `session.hook("prompt")` and tool
  `execute.before`/`execute.after` hooks. Only prompt/tool IDs and tool status
  metadata are retained; candidate creation/refs are then workspace/session
  scoped and source-linked split/close is explicit. Phase 4 below supersedes the
  earlier workspace identity source.
- 2026-09-24: SE3B corrections add durable prompt-owner indexes and resumable
  per-session transition markers. Replay after close/split is idempotent; each
  candidate create/split/close storage boundary has injected-failure recovery
  coverage. Split source prompts are intentionally shared by old/new segments
  only for that explicit operation.
- 2026-09-24: Validated full transition candidates before journal writes and
  added quarantine for malformed persisted markers; the regression test checks
  unchanged active ownership, continued prompt capture, and successful corrected
  split after restart.
- 2026-09-24: Tightened persisted transition validation to accept `unknown`
  values only after variant/ID/reference/ownership checks; malformed marker
  storage is quarantined while storage failures continue to leave valid journals
  intact for retry.
- 2026-09-24: Phase 3c correction keeps the V2 context hook's model-facing part
  purely static: it directs the model to call workspace recall for IDs and then
  detail, without sending dynamic IDs/counts/outcomes or any stored prose through
  context. Added exact round-trip coverage for long IDs sharing a prefix.
- 2026-09-24: Phase 4 replaces adapter workspace-ID scoping with explicit local
  allowlisted directory mode. Every prompt/context/tool entrypoint resolves the
  host session via `ctx.session.get`, canonicalizes `location.directory`, and
  requires exact realpath equality with `SEGMENT_EVALUATOR_ALLOWED_DIRECTORY`.
  Plugin keys use the distinct `directory-v1:` scope; persisted session bindings
  deny relocation across restarts, while symlink aliases share their canonical
  path. This remains local and opt-in, with no global activation.
- 2026-09-24: SE4 corrections make denied/missing-directory resolution storage
  inert, move binding initialization inside the per-directory serialized boundary
  after exact allowlist validation, and revalidate the host session directory at
  queue acquisition before transition recovery or any notebook operation. Tool
  hook failures now safely fall back to the event session ID even when no pending
  before-hook record exists.
- 2026-09-24: Fixed strict TypeScript diagnostics by supplying required JSON
  schema fields, guarding the post-transition source lookup, and making durable
  transition validation return the validated discriminated union. Strict scoped
  `tsc` passed in a temporary linked context against installed `@opencode/plugin`
  2.0.11; no repository dependency was added. No package typecheck script was
  added because TypeScript is not a declared/local package dependency.
- 2026-09-24: SE-FINAL correction makes transition replay compare immutable
  creation identity rather than mutable criterion contents, so a later session's
  v2 revision survives recovery after marker-removal failure. Added same-instance
  and restart regression paths plus an unrelated-ID collision guard. `bun test`
  passed (33 tests, 346 expectations); strict temporary-context TypeScript 5.8.3
  check against plugin 2.0.11 passed.

## Final handoff

- This issue is complete as a **local provisional evidence notebook**. Phase 5
  formal-trial assessment/registration is explicitly deferred and not part of
  agents-5mi.
- Validation: `bun test` from `plugins/segment-evaluator` — 33 passed, 0 failed,
  346 expectations. Strict TypeScript 5.8.3 passed in a temporary
  dependency-linked context with `@opencode/plugin` 2.0.11 and the requested
  strict flags. No package dependency was added.
- Host evidence is limited: an isolated OpenCode v2.0.14 no-resume prompt
  observation produced one active `unknown` candidate and persisted no prompt
  body. Recall, context, and model-tool operations remain mock-validated only.
- Review SE-FINAL-001 was accepted. Assistant/model adjudications are unverified
  proposals and effective outcome remains `unknown`; no trusted judgment path was
  introduced.
- README records project-local loading at
  `<project>/.opencode/plugins/segment-evaluator.ts`, the project config file
  `<project>/opencode.jsonc` and singular top-level package key `plugin`, plus
  process-level `SEGMENT_EVALUATOR_ALLOWED_DIRECTORY` setup. No shim, project
  package registration, or global activation was created by this issue.
- Beads and Git remain authoritative. The package imports neither Forge nor
  Factory and does not mutate Beads/Git. Open follow-up outside this issue:
  separately review a trusted judgment/verification path and decide whether any
  global activation is warranted; neither is authorized here.
- Accepted changed-file manifest:
  `plugins/segment-evaluator/package.json`, `plugins/segment-evaluator/index.ts`,
  `plugins/segment-evaluator/core/{index.ts,segment.ts,store.ts,types.ts}`,
  `plugins/segment-evaluator/tests/{adapter.test.ts,segment.test.ts}`,
  `plugins/segment-evaluator/README.md`, and this notes file. A stable self-hash
  is intentionally not embedded here: including this file's own hash is
  self-referential and unstable.

## Follow-up correction (agents-15q)

The Phase 4 allowlist/environment description and the historical README handoff
above describe the prior integration and are superseded for the current adapter.
They remain unchanged as historical evidence. The adapter now scopes each
host-event/tool session solely from `ctx.session.get({ sessionID }).location.directory`:
it must be a nonempty absolute path, resolve via realpath, and be a directory.
There is no `SEGMENT_EVALUATOR_ALLOWED_DIRECTORY`, plugin-load/cwd fallback, or
per-project shim. Canonical `directory-v1:` scopes isolate concurrent projects;
symlink aliases share a scope, while sibling/worktree directories remain
distinct. Session bindings still fail closed on movement and queued operations
revalidate before data access. Per-session serialization is acquired before the
per-directory queue to prevent competing first bindings during movement; lock
order is always session then directory. Reusing a canonical path intentionally
reuses its records, including after path reuse.

Global registration is documented as appending the absolute plugin directory
path to OpenCode V2's top-level plural `plugins` array. No real global config is
edited by this follow-up. Added adapter coverage exercises same-setup multi-
directory isolation, movement/binding serialization, event/tool identifier
pairing, and non-inspection of prompt/tool body getters.

### Host-smoke and runtime-ownership correction

The earlier private prompt smoke cited in the historical Phase 3d/final handoff
is superseded as a description of the current integration. A later private
OpenCode v2.0.14 smoke used one global-style top-level `plugins` entry with the
absolute plugin directory path, without an environment variable or project
shim. Two separate-directory sessions were admitted `resume: false` prompts and
produced distinct `directory-v1:` provisional candidates with effective
`unknown` outcomes; inspected plugin KV contained no prompt bodies. The run
recorded three plugin-load log entries, which does not establish runtime
instance ownership, a one-entry-to-one-instance mapping, or same-directory
multi-instance safety. This is evidence only for that one-entry configuration.
Tool, context, and recall/detail host paths remain mock-validated, not host
verified.

README now explicitly limits serialization guarantees to one plugin runtime
instance and one writer per canonical directory. Same-directory multi-instance
concurrency is unverified; a single global config entry does not prove singleton
runtime ownership. The historical allowlist/environment smoke wording above is
retained as history and superseded by the current smoke account.
