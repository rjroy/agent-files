# OpenCode Slim prompt bodies

This directory contains the seven active Slim prompt bodies: four generic role
handlers (`reviewer`, `code-reviewer`, `writer`, and `developer`), plus
`lore-researcher`, `modeler-sol`, and `modeler-astra`. Each file contains prompt
text only, without agent frontmatter or runtime metadata. The twelve specialist
workflows are passive procedures under
`plugins/personal/skills/agent-procedures/`; their IDs are not registered
agents or prompt files.

Canonical agent metadata remains in the user's chezmoi-managed Slim
configuration: IDs and descriptions, model and variant, permissions, skills/MCP
access, and orchestrator routing. Do not copy that registry into this README or
these prompt files. The three retained standalone agents remain unchanged.
Parent dispatchers may route a known procedure ID directly, or load the index
when they need routing help. Every receiving generic role prompt loads the
index and validates the selected ID and role before loading that one procedure.
The passive index maps procedure IDs to role prompts and required inputs; it
does not configure models or permissions.

The setup process links the global
`~/.config/opencode/oh-my-opencode-slim/` prompt directory to this repository
directory; it does not activate or register agent metadata. See
[`scripts/README.md`](../scripts/README.md#opencode-and-slim-setup) for preview,
apply, config ownership, and relocation guidance.
