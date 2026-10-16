# Repository setup scripts

## OpenCode and Slim setup

Requires Node.js 18 or later. From the repository root, inspect the default
preview first:

```sh
node scripts/setup-opencode.mjs
```

Preview performs no writes. Apply only after reviewing its plan:

```sh
node scripts/setup-opencode.mjs --apply
```

The setup requires an existing `opencode.json` or `opencode.jsonc` in
`$XDG_CONFIG_HOME/opencode/` (or `$HOME/.config/opencode/`). It refuses missing,
malformed, symlinked, or ambiguous config files. JSONC containing comments or
other extensions is refused without modification; strict JSON content in a
`.jsonc` file is accepted.

When needed, setup adds existing repository skill roots—`.agents/skills`,
`skills`, and plugin `skills` directories that contain a `SKILL.md`—to the
existing `skills.paths` array or `skills` array, preserving that config shape
and unrelated settings. A changed config is atomically replaced with a
recoverable backup beside the original. No-op applies preserve its bytes and
create no backup.

Setup manages exactly two links under the OpenCode config directory:

- `AGENTS.md` to this repository's `COMMON.md`;
- `oh-my-opencode-slim/` to `omo-slim-agents/`.

It does not link top-level JSON/JSONC, individual prompts, skills, commands, or
agent definitions, and it does not create an agent metadata registry. Agent
IDs, models, permissions, skill/MCP access, and routing remain owned by the
chezmoi-managed Slim config. If setup changes an effective config that
chezmoi manages, reconcile the corresponding chezmoi source before its next
apply. Restart OpenCode after applying changes.

Correct existing links are left alone. A conflicting file, directory, or
different/dangling link stops setup before writes; the installer never removes
or replaces it. For a repository relocation, inspect the exact old link target,
manually remove only a confirmed link to the former checkout (never its target),
then preview and apply setup from the new checkout. Setup does not remove
registrations left by older installers; review those separately before cleanup.

Run the isolated setup contract suite with:

```sh
node --test scripts/tests/setup-opencode.test.mjs
```
