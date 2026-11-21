# Agentic evolution

Two prompt-only skills capture possible improvements to skills and review them on
request. `suggest-learning` records a small observation without interrupting the
current task. `review-learnings` audits the inbox and recommends action or no
action; it does not implement changes.

Notes live in this checkout at `plugins/agentic-evolution/.inbox/`, regardless
of the project in which a skill is invoked. The directory is gitignored and
should be private to the local user, but it is not a secret store. Do not put
credentials, tokens, private user content, or other sensitive material in notes.
Removing or relocating the checkout affects access to the inbox.

OpenCode setup discovers this collection like other `plugins/*/skills` roots.
After adding it, preview and apply the repository's setup procedure and restart
OpenCode. Merely adding this directory does not update an existing configuration.
