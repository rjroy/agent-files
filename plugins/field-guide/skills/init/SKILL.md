---
name: init
description: Use when setting up the field-guide wiki on a project for the first time. Triggers include "init field-guide", "set up field-guide", and "bootstrap the wiki".
---

# Init

Bootstrap the project wiki and ensure disposable local lore output is ignored
when the lore-development setup helper is available. Scheduled lint is not
available through the supported OpenCode tools; lint remains a manual skill.

## Dependencies

Project/wiki setup does not depend on scheduling. OpenCode does not provide the
CronCreate/CronList scheduling tools expected by the legacy workflow; do not
attempt to call them, emulate them, or claim a recurring job was registered.
The local-lore ignore setup is provided
by lore-development's `scripts/ensure_local.py`; when plugins are installed as
siblings, resolve `../../../lore-development/scripts/ensure_local.py` relative
to this skill's installed location, then run it with `python3 <resolved-helper-path>
<explicit-project-root>`.
Do not guess the project root or a global helper path. If lore-development is
installed separately and the sibling helper is unavailable, report that the
optional helper is unavailable; users can run `python3 <path-to-lore-development>/scripts/ensure_local.py <project-root>` directly. This standalone
helper requires Python's standard library only.

## Steps

**1. Create the wiki directory.**

If the lore-development helper is available as described above, run it for the
project before creating any local lore output. This creates `.lore/local/` and
adds the root-anchored `/.lore/local/` rule to `.gitignore` without replacing
existing contents. Do not require the helper or Cron for wiki/index setup.
If the helper is unavailable or exits with an error, say local-lore setup did
not succeed and do not claim `.lore/local/` is ready. Continue the independent
reference wiki/index setup; users can retry the helper directly.

Check whether `.lore/reference/` exists. If not, create it. Then check whether `.lore/reference/index.md` or `.lore/reference/index.html` exists.

If neither index exists, write a minimal Markdown file at `.lore/reference/index.md`:

```markdown
---
title: Field Guide Index
date: YYYY-MM-DD
status: draft
tags: [index, field-guide]
---

# Field Guide Index
```

Never overwrite an existing index. If `index.html` already exists and `index.md` does not, leave it in place; the other field-guide skills can read either format.

Use the shared lore lifecycle values: new agent-created documents start `draft`; `approved` requires explicit user approval (including editing to approve) or a request for the relevant next process step; arbitrary edits are not approval. `completed` records completed agent work, not user approval. Lifecycle `status` is separate from field-guide `fg-status` freshness. Current direction can revise approved artifacts; do not ask for approval on minor transitions or every document.

**2. Report wiki setup and manual lint availability.**

Confirm whether the directory and index were created or already existed. If an
existing HTML index was found, mention that it was preserved for compatibility.
Tell the user that recurring lint scheduling is unavailable in this OpenCode
environment and that `/field-guide:lint` can be run manually when useful. Do
not create or update `.field-guide.json` for scheduling; preserve any existing
file without treating it as evidence that a job is active.
