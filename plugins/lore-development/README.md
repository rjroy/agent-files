# Lore Development

A lightweight plugin for building and organizing project context.

<img src="logo.webp" align="right" width="128" height="128" alt="Lore Development Logo">

## Philosophy

Modern LLMs have strong native planning and implementation capabilities. This plugin doesn't teach process - it helps build findable, organized context (the "lore" of your project) that informs better work.

Skills write into a three-directory `.lore/` tree (`work/`, `reference/`, `learned/`) — see **Artifact Storage** below for the full layout.

## Skills

| Skill | Purpose |
|-------|---------|
| `/lore-development:research` | Gather context from outside the project |
| `/lore-development:brainstorm` | Explore ideas, record "what if" thinking |
| `/lore-development:intent` | Think through what to build and why; record conversational intent |
| `/lore-development:design` | Make technical decisions when the "how" is the problem |
| `/lore-development:prep-plan` | Discuss an evidence-informed approach; optionally record a disposable working plan |
| `/lore-development:implement` | Orchestrate implementation from the current request, optionally informed by lore context |
| `/lore-development:simplify` | Orchestrate code cleanup with tests and review |
| `/lore-development:retro` | Capture what happened in a session as free-form notes |
| `/lore-development:learn` | Record a mistake worth not repeating; user-invoked dialog writing to `.lore/learned/` |
| `/lore-development:poke-holes` | Challenge ideas adversarially |
| `/lore-development:distill` | Promote what the code cannot say into reference docs (two seed modes: `code`, `work`) |
| `/lore-development:ddp` | **Draw the Damn Picture** - visualize flows and relationships with Mermaid |
| `/lore-development:define-validation` | Define AI validation criteria for work in progress |
| `/lore-development:install-formula` | Install the reusable Beads workflow formula in a project |
| `/lore-development:tend` | Periodic hygiene to maintain document status accuracy |
| `/lore-development:stratify` | Reorganize a stable lore directory into layered subdirectories with a navigational index |
| `/lore-development:update-stubs` | Scan legacy specs for stubs and generate an outstanding stub index |
| `/lore-development:update-lore-agents` | Build/update the project's agent registry |
| `/lore-development:review-ideas` | Process captured ideas into structured issues |

## Idea Capture

The plugin includes a hook that captures ideas without invoking the AI. Start any prompt with `idea:` and the text is appended to a daily file under `.lore/work/ideas/` (one file per date, e.g. `2026-04-24.md`). Use `/review-ideas` to process accumulated ideas into structured issues.

## Artifact Storage

Context lives in `.lore/` under three top-level directories. Each directory has a different purpose, audience, and lifetime. The only file at the `.lore/` root is `lore-agents.md`, a cross-plugin agent registry surface (see below).

```
.lore/
├── work/          # Work scaffolding — session-bound, written during a flow
│   ├── ideas/          # Captured ideas (via hook, one file per date)
│   ├── brainstorm/     # Recorded explorations
│   ├── intents/        # Conversational what/why context
│   ├── specs/          # Legacy historical specs; not active contracts
│   ├── design/         # Technical decisions
│   ├── plans/          # Implementation plans
│   ├── tasks/          # Historical task artifacts
│   ├── notes/          # Session notes, including optional implementation resumption context
│   ├── research/       # External findings
│   ├── retros/         # Free-form retrospective notes
│   ├── issues/         # Structured issues
│   ├── validation/     # Validation criteria
│   ├── stubs/          # Outstanding stub index from specs
│   ├── diagrams/       # Visual representations (Mermaid) — promote to reference/diagrams/ when stable
│   └── excavations/    # /distill session tracking
│
├── reference/      # Solidified, system-oriented — what the code cannot say
│   ├── vision.md       # Project vision (if defined)
│   ├── <feature>.md    # Distilled feature documentation
│   └── diagrams/       # Promoted, stable diagrams
│
├── learned/        # Mistakes worth not repeating — worker-oriented, born on first /learn
│
└── lore-agents.md  # Agent registry (optional, cross-plugin surface)
```

**Why three directories?** `work/` holds the work-in-progress: messy, conversational, tied to a specific session. `reference/` holds what survived: invariants, vision, distilled documentation that informs future work. `learned/` is narrowly scoped to mistakes — not lessons, not insights, not "what went well." Each has a different decay rate and a different reader.

Work artifacts are historical context, not binding instructions. The user's
current direction takes precedence; call out concrete safety or compatibility
consequences rather than treating disagreement with an old document as a blocker.
Legacy files under `.lore/work/specs/` remain discoverable historical material.

**Layered subdirectories in stable zones.** When `reference/` or `learned/` accumulates enough docs that "all in one place" hinders navigation, run `/lore-development:stratify <path>` to reorganize the directory into dependency-ordered subdirectories with a `README.md` index at the top. The index uses standard lore frontmatter (`title`, `date`, `status`, `tags`) and explains reading order, layer dependencies, and what each subdirectory holds.

### Migrating from the old layout

Pre-redesign projects had a flat `.lore/` with directories like `specs/`, `plans/`, `retros/` at the top level. Run `/lore-development:tend migrate` to move an existing tree into the three-directory model. The migrate mode rewrites internal links in frontmatter and prose, leaves guild-hall–owned paths alone, and is idempotent on re-run.

## Agents

The plugin ships with agents that skills invoke automatically:

| Agent | Purpose |
|-------|---------|
| `lore-researcher` | Search `.lore/` for useful historical context before intents or plans |
| `bun-typescript-reviewer` | Review Bun/TypeScript daemon, Unix-socket, CLI, Next.js, and React implementations against requested behavior |
| `design-reviewer` | Review design documents for weak decisions and gaps |
| `plan-reviewer` | Review plans for infeasible steps and scope creep |
| `intent-reviewer` | Check that intent notes faithfully capture what the user wants and why |
| `fresh-lore` | Fresh-context analysis when the current session is too deep in the weeds |
| `surface-surveyor` | Quick codebase reconnaissance to find entry points |

## Agent Registry

Beyond the built-in agents, skills can leverage project-specific agents for domain concerns (security, performance, architecture, etc.). Instead of hardcoding agent names into every skill, the plugin uses a project-level registry.

**How it works**:
1. Run `/lore-development:update-lore-agents` to scan available agents
2. The skill creates `.lore/lore-agents.md` with agents relevant to your project
3. Other skills check this file and invoke agents when appropriate

**Benefits**:
- Add new agents without updating the plugin
- Each project declares what's relevant to it
- Project-specific notes (e.g., "always use security-guidance for auth specs")

## Usage

Skills can run independently. Use what you need. For the recommended flow when building something new, see the **Workflow** section below.

## Workflow

Skills flow from exploration to implementation. The key decision is when to start a fresh session.

### Explore (same session)

Run `/brainstorm`, `/research`, `/intent`, and `/design` in the same conversation. These phases are conversational. The value is in the back-and-forth, the rejected ideas, the "not that because X" reasoning. Let context accumulate.

When `/design` or `/intent` completes, you have historical context in `.lore/`. Intent records what and why, not a contract. A disposable plan can explore implementation and validation, but is optional; `/implement` follows the user's current request.

### Plan (fresh session)

Start a new session. Run `/prep-plan` with the artifacts from the explore phase as context. Use them as suggestions, then plan in light of current user direction and evidence.

### Implement (fresh session)

Start a new session for substantial work. Run `/implement` with the current request and any useful context; an optional plan can help, but is not required. The implement skill delegates to sub-agents who get their own fresh context. The orchestrator shouldn't carry exploration history when it needs full attention on dispatching, testing, and reviewing.

### Capture (same session)

Run `/retro` at the end of any session where something worth capturing happened. Retro produces a free-form notes file with common frontmatter — no template, no demanded sections, no "lessons learned" header. The retro benefits from the messy context: what went wrong, what the LLM got confused by, which assumptions broke. A fresh context would lose exactly the things worth capturing.

Retros aren't only for implement sessions. An explore session that surfaced a surprising constraint, or a plan session that revealed a spec gap, are both worth a `/retro` before closing out.

If a specific mistake is worth not repeating, run `/learn` to record it. `/learn` is a user-invoked dialog that writes to `.lore/learned/`. It does not auto-trigger from `/retro` or any other skill, and it does not propose candidates from notes — the user names the mistake. See the skill itself for the framing.

### Why break context

Rolling context helps when work is exploratory. It hurts when work is procedural
and artifact-driven. Breaking context before `/prep-plan` can help focus planning;
the artifacts are context to reconsider against the user's present direction, not
a gate that must satisfy an old contract.

### Distilling existing code

Use `/distill code` when inheriting or joining an existing codebase, or `/distill work` when a spec, plan, or brainstorm holds invariants worth promoting. Both seeds run the same loop: read the seed, verify against current code, present reconciled candidates, let the user gate each one. Output goes to `.lore/reference/` and only contains what the code cannot tell a reader. Null output is a valid outcome.

## The Compound Loop

Knowledge compounds when past learnings inform new work. The plugin closes this loop automatically:

```
/intent or /prep-plan
        │
        ├─► lore-researcher agent searches .lore/ for related work
        │
        ▼
   useful historical context considered while shaping intent/plan
        │
        ... work happens ...
        │
        ▼
      /retro
        │
        └─► captures notes → writes to .lore/work/retros/
```

The `lore-researcher` agent runs at the start of `/intent`; `/prep-plan` uses it when prior context would help. It surfaces relevant retros, legacy specs, and brainstorms as historical context, not instructions for current work.

## Frontmatter Schema

All lore documents use YAML frontmatter for searchability. The schema is defined in `shared/frontmatter-schema.md`.

```yaml
---
title: Descriptive title
date: YYYY-MM-DD
status: draft|approved|complete|etc
tags: [relevant, keywords]
modules: [affected-modules]
---
```

The `lore-researcher` can find documents without frontmatter through body-text
search, but treats them as lower-confidence legacy material because lifecycle
and module metadata are unavailable. Use `/tend` to retrofit old documents, and
`/tend migrate` to move a flat-layout `.lore/` into the three-directory model.

Document bodies are Markdown by default. Embed raw inline HTML only where a visual carries meaning Markdown cannot (color-coding, inline-`<svg>` charts, side-by-side comparison) — never inside a fenced code block, and with no `<script>` or external resources. See the "Body Format" section of `shared/frontmatter-schema.md`.

To validate frontmatter across a tree (the schema's field and per-directory status rules), run the bundled checker. It scans `.md` files, emits one JSON finding per line, and exits non-zero when any document is invalid:

```bash
python scripts/validate_frontmatter.py .lore
```

## Principles

- **Light touch** - skills guide, they don't dictate
- **Context over process** - build lore, not bureaucracy
- **Independent but connected** - each skill works alone but knows about the others
- **Trust the LLM** - don't over-specify what modern AI already does well
- **Human checkpoints** - distillation gates each promotion candidate by user decision
- **Compound knowledge** - past learnings automatically surface for new work
