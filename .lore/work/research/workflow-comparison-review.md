---
title: Workflow comparison baseline review
date: 2026-09-10
status: in-progress
tags: [workflow, opencode, baseline, evidence]
---

# Workflow comparison baseline review

## Key Findings

This is an evidence-gathering baseline for `agents-alv.1`, not an adoption
recommendation or a workflow trial. Both requested paths exist. The comparison
tree at `/home/rjroy/.agents/tmp/local-marketplace` is an ordinary directory
inside the current Git worktree, not an independently identifiable Git clone.
All claims below distinguish source presence from host loading and observed
runtime effect.

## Evidence convention

- **Exists**: a source file or directory was observed at the cited path.
- **Loaded**: the host's documented loader rules and local configuration support
  loading it. This is not a claim that a running session loaded it.
- **Effective**: behavior was observed in the running host. No effectiveness
  observations are made in this task because trials are out of scope.
- **Unknown**: no sufficient source or host evidence was available.

## Snapshot and repository identity

| Subject | Identity | Classification | Evidence |
|---|---|---|---|
| Current workspace | `/home/rjroy/.agents` | Git worktree at `f1931c39bba631b7daf4ef6584be3992997cb97b`; review artifact untracked | `git rev-parse --show-toplevel`, `git rev-parse HEAD`, and `git status --short --branch`, 2026-09-10 |
| Comparison tree | `/home/rjroy/.agents/tmp/local-marketplace` | Not an independent Git worktree: Git resolves its top level to `/home/rjroy/.agents`. Independent byte snapshot: SHA-256 `70daf1ea1c30e6bfb26fff52396753a62eb82d3e29cd6b5665899716bf94648f` over 5,773 sorted regular files, hashing each relative path, a NUL separator, then file bytes; `__pycache__` and any `.git` path excluded. | Git commands plus the documented Python snapshot command, 2026-09-10 |

At capture time, both `git status --short` invocations reported this new review
document as the sole untracked path (from the clone as `../../.lore/work/research/workflow-comparison-review.md`). That result is evidence that the
clone path is within, or otherwise resolves to, the current repository's Git
worktree rather than an independently identified clone. A separate clone
commit identity cannot presently be claimed.

The independent comparison-tree identity was computed without writing into the
tree:

```sh
python -c 'from pathlib import Path; import hashlib; root=Path("tmp/local-marketplace"); files=sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts); h=hashlib.sha256(); [(h.update(p.relative_to(root).as_posix().encode()+b"\0"),h.update(p.read_bytes())) for p in files]; print(f"clone-content-sha256 {h.hexdigest()} files={len(files)}")'
```

This is a reproducible content snapshot for comparison, not an upstream commit
or provenance claim. It intentionally includes authored files and checked-in or
local generated artifacts other than `__pycache__`, so later reviewers should
rerun the same command before assuming the comparison tree is unchanged.

## Current baseline, initial observations

`AGENTS.md` exists and carries repository-wide operating constraints, including
Beads task tracking and the conservative no-commit/no-push policy
([AGENTS.md](../../../AGENTS.md), lines 1-101). The current workspace has
authored plugin source under `plugins/`, workflow state under `.beads/`, and
likely generated/cache/runtime directories (`audio_cache/`, `image_cache/`,
`logs/`, `sessions/`, `memories/`); their exact provenance remains to be
verified.

The prior context-engineering research describes this repository as using
progressive disclosure through skills, while noting duplicated global
instruction content as a candidate for future measurement rather than an
established defect ([claude-5-context-engineering.md](claude-5-context-engineering.md),
lines 53-64).

Global OpenCode configuration exists at
`/home/rjroy/.config/opencode/opencode.json`. It declares an external skill
path of `/home/rjroy/.agents/plugins` and the `opencode-model-router` plugin
([opencode.json](../../../../.config/opencode/opencode.json), lines 28-35).
This makes plugin-contained `SKILL.md` files **load candidates** under the
documented OpenCode loader, but does not establish that any named skill was
loaded by this running session. Its router override selects the `openai`
preset and defines fast, medium, heavy, and ultra tiers
([opencode-model-router.overrides.jsonc](../../../../.config/opencode/opencode-model-router.overrides.jsonc),
lines 1-8, 46-98); plugin-source inspection is still required before claiming
that those rules are effective routing behavior.

The clone root exists and contains all entrypoint families named in the epic:
`factory-plugin/`, `forge/`, `teamsters-plugin/`, `test-automation-plugin/`,
`dream-mentor-plugin/`, `open-wrapper-plugin/`, `ponytail/`, `opencode.jsonc`,
and `docs/` (directory listing of
`/home/rjroy/.agents/tmp/local-marketplace`, 2026-09-10). Contents and runtime
claims remain unreviewed at this stage.

### Current host-adjacent mechanics

| Mechanism | Exists | Loaded | Effective | Evidence and limits |
|---|---|---|---|---|
| Current repository instructions | Yes: `AGENTS.md`, `CLAUDE.md` | Unknown for OpenCode; present in this agent context | Unknown | `AGENTS.md` lines 1-101; host loader configuration has no explicit `instructions` entry so far. |
| Plugin skills | Yes: `plugins/lore-development/`, `plugins/field-guide/`, `plugins/personal/` contain `SKILL.md` files | Candidate: global `skills.paths` targets `plugins/` | Unknown | plugin directories and global config lines 28-31. |
| Claude session-start hook | Yes | Unknown, not an OpenCode mechanism | Unknown | `.claude/settings.json` lines 2-14 calls `bd prime --hook-json`. |
| Codex hooks | Yes | Unknown, not an OpenCode mechanism | Unknown | `.codex/config.toml` line 2 enables hooks; `.codex/hooks.json` lines 2-50 configures Beads hooks for start, prompt, and compaction. |
| Beads work state | Yes: `.beads/` and local embedded Dolt storage | Loaded by `bd` command when workspace resolves; host integration unknown | Effective for this task only: `bd show` and claim succeeded | `.beads/config.yaml` lines 1-68; task command outputs recorded in task evidence. |

The Beads configuration names a remote but does not itself prove a sync has
occurred; no sync command was run ([.beads/config.yaml](../../../.beads/config.yaml),
lines 39-54, 68).

The inspected global OpenCode file has no `instructions`, `agent`, `command`,
`permission`, or session-hook key. It does configure an Ollama-compatible model
endpoint, an empty MCP map, a listening server, one external skill path, and the
`opencode-model-router` plugin ([opencode.json](../../../../.config/opencode/opencode.json),
lines 1-35). Absence from this one file does not prove absence after OpenCode
merges defaults, project config, plugins, and environment. It does bound what
this user-authored global file contributes.

The router override is user-authored policy data. It chooses the `openai` preset,
sets tier caps, maps task patterns, defines escalation, and assigns concrete
models to `fast`, `medium`, `heavy`, and `ultra`
([router overrides](../../../../.config/opencode/opencode-model-router.overrides.jsonc),
lines 1-45, 46-98). These declarations explain the tier and model information
provided to this session, but source inspection of the installed router remains
necessary before attributing actual selection behavior to the plugin.

The accessible host binary is
`/home/rjroy/.local/share/mise/installs/opencode/latest/opencode`, and
`opencode --version` reports `1.18.29`. Version discovery is read-only host
evidence, not a workflow trial. It does not reveal the merged runtime config or
prove that any particular plugin hook fired.

The configured router is installed globally as `opencode-model-router@1.11.1`.
Its package manifest points directly at authored TypeScript `src/index.ts`,
requires `@opencode-ai/plugin` 1.x, and declares test, smoke, and typecheck
commands ([package.json](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/package.json),
lines 1-17, 41-56). The installed package includes router config, agent catalog,
subagent/session tracking, enforcement, escalation, guard, telemetry, and
verification modules. This establishes inspectable implementation presence. It
does not yet establish that the plugin initialized in this session.

Router implementation detail narrows the boundary. The plugin factory loads
configuration, creates per-plugin-instance session, trajectory, guard, changed-
file, and verification stores, and opportunistically sweeps idle state without
a timer ([router `index.ts`](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/index.ts),
lines 211-250). Its config source deep-merges a stable global override with a
project override found by a bounded upward walk; the project override wins
([router `config.ts`](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/router/config.ts),
lines 209-260). The current repository contains no identified project override,
so this baseline observed only the global override. The router can repoint only
explicitly mapped pre-existing subagents, skips its own tier agents and known
primary agents, and admits that Markdown agents are loaded separately and may
not be visible during this check
([router `subagents.ts`](../../../../.local/share/mise/installs/node/25.2.1/lib/node_modules/opencode-model-router/src/router/subagents.ts),
lines 18-66). These constraints matter when separating host-loaded agents from
plugin-generated tier agents.

Source discovery also found the concrete OpenCode hook surface in the router
entrypoint: a returned `tool` map, `chat.message`, `tool.execute.before`,
`tool.execute.after`, and `experimental.chat.system.transform`. Agent option and
prompt construction occurs near lines 1009-1060 of `src/index.ts`. The next
subsection distinguishes that installed implementation from what this already
running session exposes.

## Remaining questions after baseline inspection

Unknowns that require runtime trials remain deferred by scope. Feasible source
inspection, including clone entrypoints and local OpenCode/router code, is
reported below rather than left as a placeholder.

## Clone baseline, source observations

The clone presents multiple plugin-shaped packages. Each named package has
source directories for some combination of skills, commands, agents, teams,
tests, scripts, manifests, and documentation. This is an **exists** inventory
only, based on direct directory listings:

| Package | Observed authored-looking source | Observed generated/cache/runtime material | Loaded / effective |
|---|---|---|---|
| `factory-plugin` | `.claude-plugin/`, `.codex-plugin/`, `agents/`, `commands/`, `skills/`, `teams/`, `schemas/`, `scripts/`, `tests/` | `experiments/` requires inspection | Unknown |
| `forge` | plugin manifests, agents, capabilities, commands, skills, `scripts/forge/` graph engine, `scripts/a2a/` broker/runtime, TypeScript A2A extension, evals, tests | eval result artifacts are authored or captured evidence, not runtime installation | Unknown |
| `teamsters-plugin` | plugin manifests, agents, commands, skills, teams | none identified from root listing | Unknown |
| `test-automation-plugin` | plugin manifests, agents, commands, skills, subagents, teams, RPC scaffold | `assets/`, `examples/`, `research/` need classification | Unknown |
| `dream-mentor-plugin` | plugin manifests, agents, commands, skills, teams | none identified from root listing | Unknown |
| `open-wrapper-plugin` | plugin manifests, commands, skills, `bin/`, `sandboxes/` | sandboxes need classification | Unknown |
| `ponytail` | plugin manifests, commands, skills, hooks, package metadata | `assets/` needs classification | Unknown |

Directory names alone are not implementation. Direct source discovery found the
Factory executable spine in `scripts/factory.py`, `plan_graph.py`,
`run-factory-cycle.py`, `implement-node.py`, and `project-runtime-state.py`, and
the Forge engine split across `scripts/forge/{model,states,algorithms,mutate,
sync,validation,store,evidence}.py` with a separate `scripts/a2a/` runtime.
Their behavior and representative tests are cited below. Teamsters, Test
Automation, and Dream Mentor primarily encode orchestration as Markdown command,
agent, team, and skill instructions. That authored instruction source is not an
equivalent executable host adapter.

Factory's command parser in `scripts/factory.py` registers concrete `plan
create`, `run`, `status`, `close`, and `gate` subcommands (lines 2042-2130), plus
graph-run, run-state, and worker-state commands later in the same parser. The
cycle's halt decision is implemented by `derive_reasons` in
`scripts/run-factory-cycle.py` (line 171), rather than existing only in its
documentation. Representative tests directly cover the CLI, compiler and graph,
supervised envelope, delivery guards, replay trace, run state, and recovery
surfaces under `factory-plugin/tests/`; no tests were executed because this
child forbids workflow trials.

The fail-closed claim is visible in code. `run-factory-cycle.py` adds explicit
block reasons for a dead or stale control plane, missing or unready provider,
pending approval, blocked queue, and unknown eligible-agent state, and only
returns `would_dispatch` when none apply (lines 171-185, 222-239). Forge likewise
recomputes scheduling state from structure and observations rather than storing
it, filters parallel work to artifact-disjoint nodes, and requires acceptance
for terminal, manual-acceptance, or user-entrypoint nodes
([states.py](../../../tmp/local-marketplace/forge/scripts/forge/states.py), lines
1-6, 35-86, 89-113). Its delivery state is derived from verification evidence,
the current graph hash, and acceptance receipt (lines 116-147). Strict validation
then checks selected capability gaps/quarantine, test and artifact existence,
entrypoint reachability, exact report/source/graph hashes, command and exit code,
and current acceptance evidence
([validation.py](../../../tmp/local-marketplace/forge/scripts/forge/validation.py),
lines 27-46, 48-89, 92-146).

### Implemented clone lifecycle spine

The comparison tree does not contain one monolithic lifecycle. Its most complete
development spine composes three independently implemented packages:

1. **Contract and supervised envelope:** Factory's stated core loop is `load
   contracts -> gather read-only snapshots -> decide from plain data -> validate
   dry-run report -> stop at supervised handoff` ([factory README](../../../tmp/local-marketplace/factory-plugin/README.md),
   lines 3-12). Its CLI then creates or amends a bounded envelope, runs a command
   while recording a report and ledger, gates the result, emits a replay trace,
   and closes to `ready_for_human_review` or a blocked verdict (lines 97-110).
   The README also assigns crash recovery for in-flight graph nodes to the runner
   through lease expiry before frontier recomputation (lines 264-280). These are
   implementation-facing contracts, not OpenCode loading evidence.
2. **Plan and test gates:** Forge turns a spec into a dependency DAG of test-gated
   nodes and walks or replans it as evidence changes ([Forge README](../../../tmp/local-marketplace/forge/README.md),
   lines 1-18). It derives node status from observations (`BLOCKED`, `READY`,
   `RED`, `GREEN`, and `STALE`) while tracking a separate delivery progression
   through `ACCEPTED`; strict validation rejects missing reachability, drifted
   evidence, uncovered capabilities, and unaccepted user journeys (lines 50-65).
   The engine is the sole writer of `.forge/plan.graph.json`, and a material node
   update invalidates prior verification and acceptance (lines 91-104).
   This is backed by executable modules rather than README prose alone:
   `scripts/forge/states.py` defines `STALE`, derives graph states and a separate
   delivery lifecycle; `scripts/forge/sync.py` implements evidence sync;
   `scripts/forge/mutate.py` implements atomic node updates;
   `scripts/forge/validation.py` implements strict validation; and
   `scripts/forge/store.py` owns graph load/save. Focused tests cover each surface
   in `forge/tests/test_{states,sync,mutate,validation_strict,store}.py`.
3. **Optional parallel execution:** Teamsters describes load/validation, resource
   registration, topological planning, pre-execution approval, Task-tool agent
   execution with limits and retries, aggregation, post-completion approval, and
   cleanup ([Teamsters README](../../../tmp/local-marketplace/teamsters-plugin/README.md),
   lines 249-283). The same source explicitly targets Claude Code, invokes its
   `Task` tool, and uses Claude model aliases (lines 1-3, 269-272, 504-533), so
   this execution layer cannot be treated as OpenCode-compatible merely because
   its Markdown files exist.

Factory says Teamsters, Dream Mentor, and test engineering enter only at the
supervised-envelope boundary and are not required for contract loading, gather,
decision, or dry-run validation ([factory README](../../../tmp/local-marketplace/factory-plugin/README.md),
lines 221-229). That boundary is important: the comparison baseline has a
host-neutral-looking file/CLI core plus Claude-coupled orchestration adapters,
not one uniformly portable plugin.

The remaining epic entrypoints supply narrower lifecycle capabilities:

- **Test Automation** declares analyze, plan, generate, execute, bounded
  auto-heal, lint, and report stages, with persistent state and `/test-resume`
  as the interruption path ([test automation README](../../../tmp/local-marketplace/test-automation-plugin/README.md),
  lines 10-22, 70-101). Its own title, prerequisites, install location, command
  registration, and subagent architecture identify it as Claude Code source,
  not an installed OpenCode adapter (lines 1-8, 24-52, 103-127).
- **Dream Mentor** resolves a local or GitHub reference, runs three analysis
  agents, writes five memory files beneath `.claude/dreams/<name>/`, records a
  source commit, and deletes a temporary clone ([Dream Mentor README](../../../tmp/local-marketplace/dream-mentor-plugin/README.md),
  lines 125-149, 178-193). It contributes reference acquisition, staleness,
  comparison, and update/forget operations, not task execution or acceptance.
  Its lifecycle depends on Claude command registration and, for GitHub input,
  authenticated `gh` (lines 15-31).
- **Ponytail** is an always-on code-minimization policy plus review/audit/debt
  commands, not a plan or state engine. It explicitly preserves validation,
  security, data-loss handling, and accessibility ([Ponytail README](../../../tmp/local-marketplace/ponytail/README.md),
  lines 78-93, 210-221). Its README *claims* an OpenCode adapter at
  `.opencode/plugins/ponytail.mjs` and separate `.opencode/command/*` command
  files (lines 149-162). The source snapshot does not contain either claimed
  `.opencode/` path: the checkout's observed hidden integration files are
  `.claude-plugin/`, `.codex-plugin/`, and `.agents/`. Consequently no Ponytail
  OpenCode adapter implementation is available to inspect here. The shared
  `hooks/ponytail-instructions.js` is instead a CommonJS instruction builder for
  Claude hooks and Pi: it reads `skills/ponytail/SKILL.md`, filters it by mode,
  and falls back to embedded text ([ponytail-instructions.js](../../../tmp/local-marketplace/ponytail/hooks/ponytail-instructions.js),
  lines 1-10, 71-92). That proves reusable policy construction, not an OpenCode
  plugin export, loading, command registration, or per-turn injection.

- **Open Wrapper** is a shell CLI and host-specific instruction collection, not
  an OpenCode adapter. Its only executable entrypoint, `bin/open-wrapper`,
  dispatches `status`, `models`, and `ask` to an Ollama HTTP endpoint, using
  `OLLAMA_HOST` and `OLLAMA_MODEL`; it has no OpenCode plugin API, manifest, or
  lifecycle hook ([open-wrapper](../../../tmp/local-marketplace/open-wrapper-plugin/bin/open-wrapper),
  lines 1-35, 48-103). `ollama-events` is a skill document that instructs an
  agent to POST dashboard events to `localhost:18081`, rather than code that
  intercepts requests ([ollama-events/SKILL.md](../../../tmp/local-marketplace/open-wrapper-plugin/skills/ollama-events/SKILL.md),
  lines 1-31, 86-170). `model-selection` is likewise a recommendation table
  containing machine- and project-specific model assertions, and explicitly
  tells a user to check the live list before relying on it (lines 10-21, 91-99).
  Those files are **exists** evidence only. They are neither configured in the
  current OpenCode skill path nor evidence that an Ollama server, dashboard, or
  listed model is present. No network or CLI invocation was performed.

The clone's top-level `opencode.jsonc` explicitly calls itself a proof of
concept and says its skill-copy/symlink preparation must happen before it can
be run ([opencode.jsonc](../../../tmp/local-marketplace/opencode.jsonc), lines
1-19). Therefore it **exists** but is not evidence of installation, loading,
or effectiveness. Its declared model and `small_model` target local vLLM
([opencode.jsonc](../../../tmp/local-marketplace/opencode.jsonc), lines 23-43),
which differs from the current global configuration's Ollama provider and
model-router plugin.

The portability document is a dated POC/adapter claim, not host verification.
It identifies skill files, pure scripts, and schemas as portable candidates,
but calls command frontmatter, Teamsters dispatch, model aliases, and Ponytail
hooks runtime-coupled ([opencode-portability.md](../../../tmp/local-marketplace/docs/opencode-portability.md),
lines 7-26). It further says an OpenCode manifest and adaptations would be
needed for several packages (lines 55-65), and names tool-calling reliability
as a central risk (lines 78-93). No listed smoke or MVP step was run in this
task.

### Clone lifecycle map and load/runtime separation

The clone's lifecycle is a composition map, not a single installable workflow:

| Lifecycle need | Implemented/source candidate | Host/load boundary | Runtime/effect evidence |
|---|---|---|---|
| Plan and contract | Factory `plan create` and Forge's spec-to-DAG engine | Factory is a CLI; Forge is Python source. Neither is configured by the current OpenCode file. | Unknown: no command was run. |
| Dispatch / implementation | Factory supervised envelope; Teamsters Markdown Task-tool orchestration | Teamsters explicitly targets Claude Code and its `Task` tool. | Unknown; its Markdown cannot establish OpenCode dispatch. |
| Validation | Factory gates and Forge strict validation | Executable Python exists, but host-independent execution still requires an invoked command. | Unknown: no tests or validation command was run. |
| Acceptance / completion | Factory close verdict and Forge acceptance receipt | Artifact/state semantics are implemented by their respective CLI/engine. | Unknown: no state was created or accepted. |
| Resume / recovery | Factory leases/recovery and Test Automation `/test-resume` instructions | Factory recovery is CLI code; Test Automation command registration is Claude-oriented. | Unknown: no interruption or resumption was exercised. |
| Reference learning | Dream Mentor memory files and source-commit record | Its command lifecycle depends on Claude registration and potentially `gh`. | Unknown: no reference was acquired. |
| Policy / simplification | Ponytail `SKILL.md` plus hook helper | No claimed `.opencode/` adapter file exists in this snapshot. | Unknown: no host loaded the policy. |
| Local-model utility | Open Wrapper CLI and skill documents | No OpenCode adapter/configuration source exists in the package. | Unknown: no Ollama/dashboard interaction was attempted. |

Thus **implemented** means executable code or authored instructions exist at the
cited source path; it does not mean OpenCode has discovered, loaded, or invoked
them. The current global OpenCode configuration contributes only its declared
provider, server, empty MCP map, one skill path, and router plugin
([opencode.json](../../../../.config/opencode/opencode.json), lines 1-36). It
does not name any clone package, Ponytail adapter, Open Wrapper adapter, command
directory, permission rule, or project configuration. This is a read-only source
finding, not a statement about OpenCode defaults, merged configuration,
environment variables, or a running server.

## Current lifecycle map

The following is a source-supported intended workflow, not a claim that a host
automatically selects every skill or that every delegated action succeeds.

1. **Planning:** `prep-plan` directs a context and lore search, gap surfacing,
   saved reviewable plan, and fresh-eyes plan review
   ([prep-plan/SKILL.md](../../../plugins/lore-development/skills/prep-plan/SKILL.md),
   lines 8-28).
2. **Task gating (optional):** `plan-breakdown` reads a plan, maps requirements
   to executable checks, and writes sequenced task files. It explicitly stops
   before implementation ([plan-breakdown/SKILL.md](../../../plugins/lore-development/skills/plan-breakdown/SKILL.md),
   lines 8-47).
3. **Implementation:** `implement` directs an orchestrator to read source
   artifacts, select implementation/testing/review roles, create a resumable
   notes artifact, and execute one stable phase at a time
   ([implement/SKILL.md](../../../plugins/lore-development/skills/implement/SKILL.md),
   lines 8-69).
4. **Validation and acceptance:** the same skill directs phase-specific testing
   and review, targeted correction, then one terminal acceptance review
   ([implement/SKILL.md](../../../plugins/lore-development/skills/implement/SKILL.md),
   lines 61-85). `define-validation` separately requires each source
   requirement map to actionable behavioral evidence
   ([define-validation/SKILL.md](../../../plugins/lore-development/skills/define-validation/SKILL.md),
   lines 8-30).
5. **Completion and resumption:** accepted work is recorded in a notes file;
   task files can become `complete`; the notes file is marked complete at
   finalization. A later `/implement` invocation may resume from notes
   ([implement/SKILL.md](../../../plugins/lore-development/skills/implement/SKILL.md),
   lines 10-18, 69-71, 86-114). A separate retrospective records observations
   for later discovery ([retro/SKILL.md](../../../plugins/lore-development/skills/retro/SKILL.md),
   lines 8-30).

This lifecycle is **exists** as authored skill instruction and is a **load
candidate** through the current global OpenCode `skills.paths`. It is not
verified **loaded** for this session, because no OpenCode loader trace or
session inspection was available. It is not verified **effective**, because
no workflow trial was authorized or run.

## Authored versus generated, cache, and runtime inventory

| Location | Classification | Basis / uncertainty |
|---|---|---|
| `AGENTS.md`, `CLAUDE.md`, `plugins/**`, `.claude/`, `.codex/` | Authored configuration/instruction source | Direct file and directory observation. `CLAUDE.md` content equality was not independently checked. |
| `.lore/work/research/` | Authored work artifact | Document schema calls `.lore/work/` session-bound work scaffolding ([frontmatter-schema.md](../../../plugins/lore-development/shared/frontmatter-schema.md), lines 41-49). |
| `.beads/embeddeddolt/`, `.beads/backup/`, `.beads/interactions.jsonl`, `.beads/last-touched` | Runtime, database, backup, and audit material | Names and Beads configuration support this classification; individual generation mechanisms were not inspected. |
| `plugins/lore-development/.pytest_cache/`, `.ruff_cache/`, `.venv/`, `scripts/__pycache__/` | Cache or local runtime/dependency material | Conventional paths and direct listing; not compared against ignore rules. |
| `audio_cache/`, `image_cache/`, `logs/`, `sessions/`, `memories/` | Presumptive cache/runtime material | Direct root listing only. Producer, loader, retention, and host effect are unknown. |
| Clone `assets/`, `examples/`, `experiments/`, `research/`, `sandboxes/` | Mixed/unknown | Direct listings do not establish whether individual contents are authored fixtures, generated output, or runtime state. |

## OpenCode and host boundary inventory

| Surface | Current evidence | Exists | Loaded | Effective |
|---|---|---|---|---|
| Configuration | Global config at `/home/rjroy/.config/opencode/opencode.json` declares an Ollama provider, empty MCP map, external skills path, and `opencode-model-router` plugin | Yes | Global configuration is eligible under documented OpenCode scope rules; actual merged config unknown | Unknown |
| Instructions | Repository `AGENTS.md` is present; no project OpenCode config was found in the initial file inventory | Yes | Unknown: OpenCode instruction discovery/merge was not traced in a running process | Unknown |
| Skills | `plugins/` contains lore-development, field-guide, personal, and other `SKILL.md` trees; config points at `plugins/` | Yes | Candidate, subject to valid skill metadata and host scan | Unknown |
| Agents and commands | Current lore-development has authored `agents/`; no OpenCode agent/command directory was observed in global config directory listing | Yes for lore source; unknown for OpenCode registration | Unknown | Unknown |
| Tools and permissions | Current global config has empty `mcp` and no `permission` field | Yes for config facts | Unknown whether defaults or plugins supply additional tools/permissions | Unknown |
| Model routing | Router plugin configured; an override file declares the active preset and tier rules | Yes | Plugin load and override-file consumption require plugin-source/runtime evidence | Unknown |
| Session behavior | Claude and Codex Beads hooks are configured | Yes | Unknown for their respective hosts; no OpenCode session hook source observed | Unknown |

The clone's POC also makes source claims about OpenCode skill loading and its
absence of equivalents for selected hooks and dispatch mechanisms. Those are
explicitly treated here as **documented claims**, not proof of current-host
behavior ([opencode.jsonc](../../../tmp/local-marketplace/opencode.jsonc),
lines 7-19; [opencode-portability.md](../../../tmp/local-marketplace/docs/opencode-portability.md),
lines 9-12, 115-140).

## Limits and independent-review handoff

This baseline does not recommend adoption, execute a clone workflow, alter
configuration, or establish production runtime behavior. It leaves the
following evidence explicitly unresolved for the next independent reviewer:

- whether a separately versioned clone was intended, since the requested clone
  path resolves to the current worktree's Git revision;
- valid OpenCode merged configuration and startup/load traces, including any
  implicit instruction discovery, plugin internals, permissions, tool
  registration, and session-resume behavior;
- package-level file classification beyond root directory names;
- clone skill/agent/command source contents, host adapters, and tests;
- whether current and clone source snapshots remain stable while later child
  tasks compare them.

The document is ready for independent source review. It preserves the POC
document's stated uncertainty and requires source and host evidence before any
later recommendation treats a mechanism as loaded or effective.
