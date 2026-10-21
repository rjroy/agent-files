# OpenCode Slim agents

## Sources of truth

- [`config/oh-my-opencode-slim.json`](../config/oh-my-opencode-slim.json) owns the roster metadata: models, variants, explicit skill/MCP access, permissions, descriptions, and orchestrator routing. It is the repository source of truth; do not edit an installed duplicate.
- This directory owns prompt text only. The setup links it to `~/.config/opencode/oh-my-opencode-slim/` (or `$XDG_CONFIG_HOME/opencode/oh-my-opencode-slim/`) and installs the config symlink at the sibling `~/.config/opencode/oh-my-opencode-slim.json` (or `$XDG_CONFIG_HOME/opencode/oh-my-opencode-slim.json`). Setup does not register agents. See [`scripts/README.md`](../scripts/README.md#opencode-and-slim-setup) for preview/apply details.

## Roster

- **Orchestrator** coordinates tasks and delegates to the retained specialists.
- **Explorer** handles codebase discovery and research.
- **Oracle** handles technical reviews and senior problem-solving, including substantial or high-risk fixes.
- **Fixer** is the general technical builder for clear implementation work, from fixes to features.
- **Designer** handles UI/visual design and modeling where visual direction or design judgment matters.
- **Creator** produces direct creative work across prose, music, visual art, and modeling.
- **Craftsman** takes on difficult creative reviews and complex work needing imaginative, sustained refinement.

The technical pair shares relevant technical task skills; Creator and Craftsman share a broad creative skill set. Skills provide task methods, references, and approval gates—not agent identity or automatic authorization. The Orchestrator has parent-level skill access; specialists use explicit configured lists. Procedure task roles (read-only review, bounded writing, or bounded development) are separate from agent names. A receiving agent follows the selected procedure's contract; review remains read-only even for an agent that can write on other tasks. See the [agent-procedures index](../plugins/personal/skills/agent-procedures/references/index.md).

## Prompt files

OMO loads `<agent>.md` as a full prompt override and `<agent>_append.md` as an addition to the effective prompt. When both an inline config prompt and a full prompt file exist, the inline prompt wins; an append file is added to that effective base. This directory uses:

- `oracle.md` — Oracle's full role prompt.
- `fixer_append.md`, `designer_append.md`, `orchestrator_append.md` — focused additions to built-in prompts.
- `craftsman.md`, `creator.md` — canonical prompt bodies for these custom agents; their config entries intentionally have no duplicate inline prompt.

Prompt loading and config precedence are provided by the installed OMO plugin. Restart OpenCode after changing config or prompt files so the running session reloads them.
