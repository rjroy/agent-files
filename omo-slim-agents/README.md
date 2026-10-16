# OpenCode Slim prompt bodies

This directory contains flat Markdown prompt bodies. The filename is the Slim
agent ID; each file contains prompt text only, without agent frontmatter or
runtime metadata. The approved prompt set contains 15 bodies: six lore
specialists, two existing modeler prompts, three music specialists, and four
story specialists. Collection workflow dispositions live in the transition
plan; this README is not a second agent roster.

Canonical agent metadata remains in the user's chezmoi-managed Slim
configuration: IDs and descriptions, model and variant, permissions, skills/MCP
access, and orchestrator routing. Do not copy that registry into this README or
these prompt files. The two `modeler-*` bodies here are exact extractions of the
existing inline prompts; their inline config values remain in place until the
separately scoped configuration migration.

The setup process links the global
`~/.config/opencode/oh-my-opencode-slim/` prompt directory to this repository
directory; it does not activate or register agent metadata. See
[`scripts/README.md`](../scripts/README.md#opencode-and-slim-setup) for preview,
apply, config ownership, and relocation guidance.
