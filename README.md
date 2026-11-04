# Agent Files

A personal toolkit for AI-assisted development and creative work. This repository brings together shared instructions, specialist agent prompts, reusable skills, and setup scripts so those workflows can be maintained in one place rather than copied between projects.

The main integration is **OpenCode with oh-my-opencode-slim**. Some collections also support other agent tools, including an optional Hermes setup script. This is configuration and workflow content, not a standalone agent application.

## How it fits together

- **Shared instructions** establish engineering, communication, testing, and task-tracking conventions.
- **Specialist agents** divide work between coordination, research, implementation, technical review, design, creative production, and refinement.
- **Skills** supply task-specific methods, references, scripts, and approval gates. Collections cover software development, project knowledge, UI and assets, storytelling, music, and audio analysis.
- **Setup scripts** connect the local checkout to supported tools. Collection-specific dependencies are installed separately when needed.

The configured roster is Orchestrator, Explorer, Fixer, Oracle, Designer, Creator, and Craftsman. Agent names describe capabilities; the selected workflow still determines whether a task may write files, only review them, or needs user approval.

## Get started with OpenCode

### Prerequisites

- An existing OpenCode installation with oh-my-opencode-slim configured.
- Node.js 18 or later for the setup script.
- An existing regular `opencode.json` or `opencode.jsonc` in `$XDG_CONFIG_HOME/opencode/`, or `~/.config/opencode/` when `XDG_CONFIG_HOME` is unset.
- Model providers and any MCP services required by your chosen agent configuration.

The checked-in Slim configuration contains personal model selections and tool access settings. Review [`config/oh-my-opencode-slim.json`](config/oh-my-opencode-slim.json) before adopting it.

### Preview, then apply

Clone the repository into a stable location. `~/.agents` is the conventional location for this collection; use another location if that directory already contains your own setup.

```sh
git clone https://github.com/rjroy/agent-files.git ~/.agents
cd ~/.agents

# Inspect the plan without writing files.
node scripts/setup-opencode.mjs

# Apply after reviewing the plan.
node scripts/setup-opencode.mjs --apply
```

Setup registers discovered skill roots in your existing OpenCode configuration and creates these links under the OpenCode config directory:

| Installed path | Repository source |
| --- | --- |
| `AGENTS.md` | `COMMON.md` |
| `oh-my-opencode-slim/` | `omo-slim-agents/` |
| `oh-my-opencode-slim.json` | `config/oh-my-opencode-slim.json` |

Restart OpenCode after applying changes. The script does not install OpenCode, the Slim plugin, providers, MCP servers, or individual collection dependencies.

**Safety notes:** setup refuses conflicting paths rather than overwriting them, and keeps a recoverable backup when it changes the OpenCode config. It accepts strict JSON only, even for `.jsonc` files, and refuses missing, malformed, symlinked, or ambiguous configs. If chezmoi manages your configuration, reconcile its source before the next chezmoi apply. Keep the checkout in place because the installed links point to it.

## Everyday usage

Work in your target project with OpenCode and describe the outcome you want. The orchestrator coordinates specialist work, while skills provide the relevant task workflow. Requests might include:

- “Research how this library handles retries.”
- “Plan the implementation before changing code.”
- “Implement this feature and verify it.”
- “Review this change without editing files.”
- “Help me develop a song concept.”

Available skills and services depend on the tool and agent configuration. A skill does not install its dependencies or authorize paid generation, destructive actions, or integration work. Check the relevant `SKILL.md` and collection README before using a new workflow.

For optional Hermes skill registration, start with a preview:

```sh
./scripts/setup-hermes-skills.sh --dry-run
```

That integration requires an existing Hermes configuration and its own dependencies. It is not needed for OpenCode.

## Repository layout

| Path | Purpose |
| --- | --- |
| [`COMMON.md`](COMMON.md) | Shared instructions linked into OpenCode. |
| [`AGENTS.md`](AGENTS.md) | Repository-local agent guidance and Beads task-tracking instructions. |
| [`config/`](config/) | Slim agent roster, models, permissions, and skill/tool access. |
| [`omo-slim-agents/`](omo-slim-agents/) | Agent prompt bodies and additions to built-in prompts. |
| [`plugins/`](plugins/) | Skill collections, supporting tools, and plugin code. Not every collection is a runtime plugin. |
| [`skills/`](skills/) | Additional standalone skills. |
| [`scripts/`](scripts/) | Setup helpers and their tests. |
| [`recipes/`](recipes/) | Tool-specific recipes, including a skill-audit recipe. |

See the [agent guide](omo-slim-agents/README.md) for prompt ownership and precedence. Collection-specific README files describe additional requirements, such as Python packages for audio analysis or Bun and API credentials for art generation.

## Maintaining the toolkit

Edit shared guidance in `COMMON.md`, roster settings in `config/oh-my-opencode-slim.json`, and prompt text in `omo-slim-agents/`. Skills keep their instructions in `SKILL.md` alongside supporting resources. Preview setup again after adding skills or moving the checkout, and restart OpenCode after config or prompt changes.

Run the isolated OpenCode setup tests with:

```sh
node --test scripts/tests/setup-opencode.test.mjs
```

This checks the installer contract, not every skill collection. Use each collection's own validation instructions when changing its code or workflows.
