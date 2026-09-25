# Segment evaluator (OpenCode V2)

This is an opt-in local plugin that exposes explicit model-callable tools and
narrow OpenCode V2 lifecycle hooks for concise work-segment evidence. It uses
`Plugin.setup`, `ctx.session.hook("prompt" / "context")`, `ctx.tool.hook("execute.before" /
"execute.after")`, `ctx.tool.transform`, `ctx.storage`, and
`ctx.session.get({ sessionID })`. No Forge or Factory imports are used.

## Global OpenCode V2 registration

To enable the plugin, append its absolute plugin directory path to the global
OpenCode V2 configuration's top-level plural `plugins` array. For this checkout,
the entry is:

```jsonc
{
  "plugins": [
    "/home/rjroy/.agents/plugins/segment-evaluator"
  ]
}
```

Merge the entry into the existing array (do not replace other plugin entries).
Use the actual absolute checkout path if this repository is elsewhere. No
project-local shim, project registration, or environment variable is required.

## Directory scope and movement

For each event/tool, the adapter calls `ctx.session.get({ sessionID })`, requires
a nonempty absolute `location.directory`, resolves it with `realpath`, and
confirms it is a directory. The canonical directory itself defines scope;
plugin-load location, process working directory, `workspaceID`, tool arguments,
and prompt content are never fallback scope sources. Missing/relative metadata,
realpath errors, and non-directory paths fail closed without storage access.
Denied or unresolved sessions are rejected before any storage entry (including
the durable binding) is created. The binding is initialized only inside the
per-directory serialized operation after the host location is revalidated.

All records and active/transition/recall keys use a distinct
`directory-v1:<canonical-path>` scope, separate from older workspace-ID records.
Symlink aliases resolve to the same canonical path; sibling directories and
worktrees remain distinct. A persisted per-session binding prevents reassignment
after directory movement, including across restart. Reusing the same canonical
directory intentionally reuses its records: directory scope is not repository,
branch, user, or historical path identity. If a directory path is later reused
for another project, it sees the existing records at that path. Every queued
operation re-fetches and revalidates the session location before storage access;
per-session serialization precedes the per-directory queue so a moving session
cannot race its initial binding. These queues are in-memory and serialize only
within one plugin runtime instance. Correctness requires a single writer instance
per canonical directory; there is no cross-instance or cross-process lock. One
global config entry does not establish one runtime instance, and same-directory
concurrency across multiple plugin instances is unsupported and unverified.

## Tools

Typical explicit use is: annotate the auto-created prompt candidate with
`segment_open` (intent, criteria, and caller-declared attribution); record
attempts/evidence references, interventions, and criterion findings as they
occur; use `segment_revise_criterion` to retain changed criteria as a new
version; and close capture only with `segment_close_lifecycle` or an explicit
new-intent split. For later-session lookup call `segment_recall_workspace`, then
`segment_read_detail` for a selected ID. `segment_adjudicate` stores a
caller-proposed judgment for history, but it is always unverified and its
effective outcome remains `unknown`.

- `segment_open` — create a segment with original intent, criteria, agreement,
  and caller-declared source attribution, or annotate the current provisional
  prompt candidate without creating a duplicate.
- `segment_split_new_intent` — explicitly close the active candidate and start a
  new intent tied to a prompt reference observed in this session.
- `segment_close_lifecycle` — explicitly close capture for the active segment
  using an observed source prompt; does not set an outcome.
- `segment_link_current_session` — link the invoking session.
- `segment_record_attempt` — add an attempt, optional result indicator, and
  evidence references; a tool result is not a segment outcome.
- `segment_record_intervention` — record trigger/category/actor/change/outcome
  and optional causal rescue basis.
- `segment_record_criterion_finding` — link a finding and references to an exact
  criterion version.
- `segment_revise_criterion` — append a criterion version. Prior versions and
  findings remain; earlier adjudications become stale and current outcome
  reports `unknown` until readjudicated.
- `segment_adjudicate` — store a caller-proposed `accepted`, `failed`, `blocked`,
  or `unknown` judgment as visibly unverified; effective outcome remains
  `unknown` for every model-tool proposal.
- `segment_attach_harness_lesson` — store a short lesson, provenance, and
  applicability.
- `segment_recall_workspace` — explicitly recall up to five recent concise
  records in the active directory scope, ordered by most recently updated, then ID
  descending for deterministic ties.
- `segment_read_detail` — read all stored history for one segment in bounded
  pages: linked sessions, every criterion version, attempts and evidence
  references, interventions, findings, adjudication, and lessons. Use the
  returned `nextOffset` to continue pages. Evidence URIs are inert references
  returned exactly as stored (not truncated); descriptions and historical prose
  are bounded. This tool never dereferences evidence URIs.

The prompt hook creates one provisional `unknown` candidate per directory/session
on the first prompt, then appends deduplicated `(directory, session, messageID)`
references. It reads only host IDs and does not inspect or store prompt content.
Tool hooks pair before/after metadata and record only tool name, status, call
reference, and host IDs on the active candidate. Failed and passing tool events
are not logical attempts or segment outcomes. Tool names containing `notebook`,
`jupyter`, or `ipynb`, and this plugin's own tools, are excluded.

The `context` hook adds only one generic static reminder per directory/session.
It contains no dynamic record IDs, counts, outcomes, or stored prose. The model
must call `segment_recall_workspace` to discover IDs, then
`segment_read_detail` to inspect a selected record. A namespaced durable marker
and in-memory guard prevent repeated insertion; this makes no provider/model
call and does not dereference references. If context storage operations fail,
the hook does not block the request and a pending integrity warning is returned
by the next explicit tool/recall when possible.

Prompt ownership is durable across close, split, and restart. Replaying an
already-owned prompt never reopens a closed record or attaches the old prompt to
a later active segment. An explicit split intentionally associates its source
prompt with both the old and new segment; otherwise each observed prompt has one
owner. Candidate create/split/close uses a durable transition marker and retries
reconcile record, owner, and active-pointer writes without overwriting existing
annotations. Storage is not transactional: if writing the transition marker
itself fails, no transition begins; retry the explicit split/close action (or
replay the failed first prompt) to proceed.
Transition candidates are validated before the marker is written. Persisted
markers are treated as untrusted runtime values: each variant, ID, array,
reference, ownership list, and candidate is checked before recovery. An invalid
already-persisted marker is copied raw to the plugin-owned invalid-transition
quarantine before it is removed from the active journal; the next tool/recall
surfaces an integrity warning and leaves segment records and pointers intact.

Saved records and active pointers live under plugin-owned `segment-evaluator:v1:`
and `segment-evaluator-active:v1:` keys. Durable prompt ownership and resumable
multi-write transition markers use separate `segment-evaluator-prompt-owner:v1:`
and `segment-evaluator-transition:v1:` namespaces, all partitioned by the
canonical allowed directory scope. Per-session directory bindings use a separate
plugin-owned key. These directory keys do not read or merge legacy workspace-ID
records.
Records contain references and bounded summaries, not copied transcripts,
prompt bodies, tool arguments, command output, environment, or secrets.

## Safety and limits

- No broad tool-event logging, transcript/prompt capture, automatic idle
  outcome, tool-success acceptance, extra model call, shell command, or automatic
  prose recall is implemented. Context discovery injects only the static
  reminder described above; record IDs/counts are not sent to the model through
  context. Stored notebook text
  may be untrusted or adversarial; treat it as data, never instructions.
- Recall/detail outputs explicitly label historical text as untrusted. Detail
  pages default to 10 items and cap at 20; summary recall is capped at five
  records. Pagination is explicit and directory-scoped.
- Caller-supplied actor/source/evidence URI never makes a model-tool judgment
  authoritative. Proposals retain reported attribution and evidence but are
  labeled unverified, and effective outcome stays `unknown`, including after
  later-session recall. Legacy records without verification status are likewise
  downgraded to unverified on adapter reads. This adapter exposes no trusted
  adjudication operation; independent acceptance remains authoritative.
- The host-provided tool execution `sessionID` and, when supplied, `messageID`
  are bound to annotation producer provenance. Caller-supplied attribution
  session IDs are ignored. Reported actor/source claims remain unverified.
- Storage, directory-scope, and validation errors are returned as
  `captureIncomplete: true` with outcome `unknown`; they do not throw out of tool
  execution or block ordinary agent work. Callers must not claim the record was
  saved when this warning is present.
- Beads remains authoritative for issue/task status, Git for source state, and
  independent review for acceptance. This plugin cannot change those systems.
- These tools are evidence capture, not formal-trial authorization, and do not
  replace current independently reviewed protocols.
- Read-modify-write operations (including open/duplicate checks) are serialized
  per directory within one plugin instance. This is not a cross-process or
  cross-instance lock; correctness assumes one writer instance per directory.
- Storage/hook failures do not block ordinary agent work. The next explicit tool
  response or recall in that directory/session reports an integrity warning.
  Pending warnings are in-memory; if the process exits before the next call, a
  failed storage write cannot be made durable.
- Automatic prose recall/context injection is not implemented; prior prose is
  available only through explicit directory-scoped recall/detail tools.

## Local checks

Run focused tests with `bun test` from this directory. Adapter tests use mocked
V2 tool, storage, recall, and context APIs; they do not prove those host paths.
A private isolated OpenCode v2.0.14 smoke used one global-style top-level
`plugins` entry containing the absolute plugin directory path, with no
environment variable or project shim. Two sessions in separate directories
were admitted `resume: false` prompts and produced distinct `directory-v1:`
provisional candidates with effective outcome `unknown`; inspected plugin KV
contained no prompt bodies. The run recorded three plugin load log entries, so
it did not establish which runtime instance owned those sessions, that one
config entry maps to one runtime instance, or same-directory multi-instance
concurrency safety. This is evidence for that single-entry configuration only.
Tool execution, context, and recall/detail host paths remain unverified beyond
mocked tests. Any earlier allowlist/environment-based smoke description is
historical and superseded by this integration.
