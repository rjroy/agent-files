# Judgment Engine of Virelan

<img src="assets/logo.png" width="200" align="right" />

A strategic thinking partner for Claude Code. Surfaces tensions, challenges assumptions, and sharpens judgment through reflective pressure rather than prescriptive solutions.

The engine doesn't resolve. It endures pressure and reflects what survives.

---

## Philosophy

Three principles drive every interaction:

**Rigor over resolution.** Provisional answers are welcome; polished ones are suspect. The engine treats smooth answers as structurally suspicious until they've been tested.

**Ownership stays with you.** The engine probes; it doesn't decide. Judgment lives with you.

**Friction is productive.** Tension is where insight forms. The system invites it rather than smoothing it away.

---

## Commands

Commands are user-invoked via `/judgment-engine-virelan:[command]`.

### Posture Commands

Switch the engine's stance mid-session. Each posture shapes tone and approach until you explicitly switch or the conversation ends.

| Command | Role | Use when |
|---------|------|----------|
| `/judgment-engine-virelan:quinn` | Quinn 🦆 | You need structural clarity without emotional weight. Retrospective-quality framing. |
| `/judgment-engine-virelan:max` | Max 🪓 | Agreement feels too easy. Something sounds good but you don't trust it. |
| `/judgment-engine-virelan:mara` | Mara 🧘 | Friction is productive but overwhelming. Emotional charge is obscuring signal. |
| `/judgment-engine-virelan:herald` | Herald 📣 | Stakes need to be visible. Ideas have survived scrutiny and need projection. |
| `/judgment-engine-virelan:echo` | Echo 🪞 | Your voice must be protected absolutely. Authorship is paramount. |

### Utility Commands

| Command | What it does |
|---------|-------------|
| `/judgment-engine-virelan:primer` | Extracts 3 sharp questions from current context. Only outputs when genuine judgment pressure exists; refuses to manufacture importance. |
| `/judgment-engine-virelan:digest` | Compresses a conversation or thought thread into portable signal: root question, key shifts, revealed assumptions, emergent tensions, what's worth keeping. |
| `/judgment-engine-virelan:sharpen` | Identifies vague or abstract language. Names the vagueness, asks what's actually meant, offers sharper framing without replacing your voice. |
| `/judgment-engine-virelan:trim` | Cuts 10-15% from a draft. Marks hedging language, redundant explanations, and scaffolding that doesn't carry weight. Shows what to cut and why. |
| `/judgment-engine-virelan:diagnostic` | Shows current system state: active context, loaded modes, available next moves given where the conversation is. |

---

## Skills

Skills are invoked autonomously by Claude based on task context. You can also invoke them explicitly by name.

### Foundational

**`init-engine`** — Loads core posture, system roles, and glossary at the start of any Judgment Engine session. Runs automatically before other skills execute.

### Surfacing

**`exploratory-reasoning`** — Breaks open big questions by generating multiple distinct reasoning paths. Each path gets its assumptions, risks, and conditions for being right named explicitly. Use when answers feel fluent but hollow, or when you're circling the same frame.

**`simulated-debate`** — Runs a structured multi-voice argument when two ideas both feel right but won't fit together. Frames the disagreement, argues both positions with equal rigor, cross-examines for false splits and hidden overlap, then surfaces synthesis prompts (not forced resolution).

**`idea-crucible`** — Puts ideas under pressure before building them. Demands the core claim in one sentence, extracts foundational assumptions, applies pressure to each, surfaces what's being avoided, and only compiles proto-requirements from what survives.

### Accelerating

**`qa-runner`** — Interactive interrogation, one question at a time. Accepts a target context, optional posture (Quinn, Max, Librarian, etc.), and asks focused questions until you export, exit, or change topic. Includes pre-built question banks for planning, API review, 1:1 prep, and leadership assessment.

**`convergence-move`** — Helps you act when thinking is stretched but nothing fully resolves. Scans for structural tensions, assesses whether movement is ready, premature, or whether the contradiction itself is the answer. Won't fake alignment.

### Integrating

**`coherence-pass`** — Finds genuine patterns in rich notes or scattered thinking. Reality-checks whether coherence actually exists before claiming it. If patterns aren't there, says so and offers productive next moves instead.

**`writing-workshop`** — Strengthens drafts without surrendering authorship. Identifies structural weaknesses, asks targeted questions you must answer to proceed, and only rewrites on explicit request (always marked as "example only").

### Meta

**`judgment-traceback`** — Explains why the system produced its last output: which mode was active, what context was loaded, what decision branches were taken, and what would change the outcome if re-run.

---

## Roles Reference

Beyond the five posture commands, the engine includes technical and fantasy authorial roles invoked by name:

**Technical**: Archivist (compress sessions into signal), Librarian (flag ambiguity and naming drift), Systems Analyst (surface architectural misassumptions), Field Guide (procedural clarity for runbooks and guides).

**Fantasy authorial**: Tolkien (lore as architecture), Sanderson (systems that earn trust), Jemisin (collapse as intimacy), Le Guin (ethics as ecosystem), Pratchett (satire as system diagnosis), Wyrd (mood as structural work).

Invoke any role by naming it: "Run Quinn", "Give me the Max perspective", "Switch to Librarian mode".

---

## Key Vocabulary

**Fluency masks fragility** — What sounds polished might be structurally weak. The engine treats smooth answers as suspicious until pressure-tested.

**Fracture** — Where an argument breaks under pressure. A signal, not a flaw.

**Surface before synthesis** — Reveal structure and contradiction before moving to convergence.

**Hold tension over resolution** — Maintain productive ambiguity rather than forcing premature clarity.

**Anti-ghosting** — Never return fully polished work without your participation. Prompts over final phrasing, always.

---

## Getting Started

Load the engine and set a posture:

```
/judgment-engine-virelan:quinn
```

Surface questions from your current thinking:

```
/judgment-engine-virelan:primer
```

Run an idea through pressure before building it:

```
Use Idea Crucible to test this concept: [idea]
```

Compress a long session into portable signal:

```
/judgment-engine-virelan:digest
```
