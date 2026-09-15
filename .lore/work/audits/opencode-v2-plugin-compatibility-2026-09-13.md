---
title: "OpenCode V2 plugin compatibility audit"
date: 2026-09-13
status: complete
---

# Scope and verification boundary

This independently rechecked the nine collections under `plugins/`, active
local OpenCode integrations, the installed OpenCode `v2.0.1` runtime, and the
active model-router source at
`~/Applications/opencode-plugins/opencode-model-router/`. The `~/Applications`
restriction prohibits edits, not read-only inspection or tests; no source or
runtime configuration was modified.

OpenCode's V2 plugin documentation describes plugins as JavaScript or
TypeScript modules loaded from plugin directories or the `plugins` config, and
its current skills, agents, and commands documentation defines their supported
discovery locations. These pages are useful API-format evidence, but they are
not a behavioral test against the locally installed `v2.0.1` binary. A listed
or loaded definition is not proof that the skill, agent, command, hook, or
model dispatch completes successfully.

# Runtime inventory

* `opencode --version` reported `v2.0.1`; `/api/health` reported healthy
  version `2.0.1` in the original audit.
* `opencode plugin list` previously reported two active local server plugins:
  `herdr-agent-state` and `opencode-model-router`; the server log recorded both
  loading. This proves loading only, not every hook path.
* At the evaluated `/home/rjroy` location, the original runtime inventory found
  50 skills: all 47 repository `SKILL.md` definitions and three non-repository
  skills. It found 16 agents, including the six lore-development agents
  symlinked into `~/.config/opencode/agents`, and nine commands, none from the
  repository collections. The generic skills-path installer therefore makes
  skills available but does not itself place each collection's `agents/` and
  `commands/` in OpenCode's documented discovery directories.
* Global `~/.config/opencode/opencode.json:28-35` registers the repository
  plugins directory through `skills.paths` and configures the model router. The
  original runtime inspection found this legacy path normalized in memory.
* `~/.config/opencode/tui.jsonc:2` refers to `herdr-tui-session.js`. The
  original audit found this is dormant legacy TUI configuration, whereas
  `cli.json` is the active client configuration. The global config's `server`
  field also emitted a normalization warning for `$.server`.

# Collection verdicts

| Collection | Inventory | Verdict | Evidence / action needed |
| --- | --- | --- | --- |
| art-gen | 1 skill, 1 command, Bun scripts | **Partial** | Its skill is discovered and `bun test` passed, but `skills/generate-image/SKILL.md` and `commands/init.md` rely on `${CLAUDE_PLUGIN_ROOT}`, which is not an OpenCode documented placeholder. The command is not installed in an OpenCode command directory. |
| audio-analysis | 2 skills, Python scripts | **Functional failures confirmed** | Skills are discovered, but the complete isolated suite finished with 154 passed, 22 failed, 1 skipped. Failures include scalar conversion crashes, MIDI structure errors, and script/test interface mismatches. These are not established as V2 regressions. |
| field-guide | 7 skills | **Compatible by format; behavior unverified** | Skill-only collection with no Claude runtime placeholder or hook found in the original static scan. No collection runner is declared. |
| judgment-engine-virelan | 9 skills, 10 commands | **Partial** | Skills are discovered, but its commands are not placed in a documented OpenCode command directory. No plugin API/hook implementation or collection runner was found. |
| lore-development | 13 skills, 6 agents | **Partial** | Skills and the six installed agents are discovered; its Python suite previously passed. Skills and `lore-researcher.md` use `${CLAUDE_PLUGIN_ROOT}`; orchestration skills also instruct the obsolete `Task` tool. Port path resolution and tool workflow before treating those workflows as behaviorally compatible. |
| music-engine-rowan | 2 skills, 8 agents, 3 commands | **Partial** | Skills are discovered, but agents and commands are not installed in documented discovery directories. Its agents additionally name Claude/MCP tools including `mcp__plugin_art-gen-mcp_art-gen__*`, `TodoWrite`, `BashOutput`, and `AskUserQuestion`. |
| notify-hook | Claude hook and Python scripts | **Incompatible as installed** | `hooks/hooks.json` is a Claude `Notification` hook invoking `${CLAUDE_PLUGIN_ROOT}`. It is neither an OpenCode plugin module nor registered as one, so its notification behavior cannot run under this installation. |
| personal | 9 skills | **Compatible by format; behavior unverified** | Skill-only collection; no Claude runtime placeholder/hook was found in the original static scan. No collection runner is declared. |
| story-engine-wyrd | 2 skills, 7 agents, 4 commands | **Partial** | Skills are discovered; agents and commands are not installed in documented discovery directories. `commands/review-story.md` also calls the obsolete `Task` tool. |

# Active local integrations

| Integration | Verdict | Evidence and boundary |
| --- | --- | --- |
| `herdr-agent-state` | **V2-shaped and load-proven** | The original review found `id`/`setup(ctx)` plus `ctx.session.hook("prompt", ...)` and `ctx.event.subscribe(...)`; runtime inventory/logs prove it loaded. No end-to-end hook assertion was run. |
| `opencode-model-router` | **V2 API-shaped, typecheck-proven, load-proven** | Read-only source review found `src/index.ts` imports `@opencode/plugin` `2.0.3`, uses `Plugin.define({ id, async setup(ctx) })`, and its default export uses `EffectPlugin.define`. It registers agent/command transforms, session/context hooks, tool hooks, and event subscription through that SDK. `npm run typecheck` passed. This is stronger than load-only evidence, but does not prove provider routing, foreground/background subagent completion, guards, or every event path against the running server. |
| `herdr-tui-session` | **Dormant / incompatibility risk** | It exports V1 `tui: async (api)` and is referenced only by legacy `tui.jsonc`; the original audit found V2 does not load that layered TUI configuration. |

# Validation results and exact commands

* PASS (original audit): `bun test` in `plugins/art-gen` — **52 passed, 0 failed**.
* PASS (original audit): `plugins/lore-development/.venv/bin/python -m pytest` — **95 passed**; pytest warned that configured `testpaths` initially found no files before recursive collection.
* PASS (this review): `cd ~/Applications/opencode-plugins/opencode-model-router && npm run typecheck` — exit 0. This read-only type check validates the installed router source against its installed SDK types.
* PASS (this review): `cd ~/Applications/opencode-plugins/opencode-model-router && npm test` — **66 files passed, 1,373 tests passed, 2 skipped**. This includes `integration/grader-temperature.test.ts` (2 passing) and `integration/v2.test.ts` (15 passing). The suite is mocked/in-process, not a live provider/server dispatch test.
* FAIL (live session): all three audit subagent returns were followed by `[router ⚠ NOT ACCEPTED]` with `grader dispatch failed: Error: Router session failed`. The worker sessions completed, but automatic independent grading did not. Root cause and whether V2 caused this remain unverified. The orchestrator directly reran the audio and notification suites and reviewed this report as a fallback.
* FAIL (this review): `plugins/lore-development/.venv/bin/python -m pytest -c /dev/null plugins/notify-hook/tests -q` — **74 passed, 12 failed**. Failures include `generate_topic("myuser", "myrepo")` treating the first positional string as `config`, default/override configuration assertions, and notification pipeline tests that report `Info: All backends disabled` instead of dispatching. This is a suite/source contract failure independent of the legacy-hook incompatibility, not evidence that an OpenCode hook ran.
* INCOMPLETE (this review): `plugins/lore-development/.venv/bin/python -m pytest plugins/audio-analysis/tests plugins/notify-hook/tests -q` initially selects audio-analysis configuration and fails before collection because its configured `--cov` options require the absent `pytest-cov` plugin. The same venv has `pytest`, but not `librosa`, `music21`, `soundfile`, `numpy`, `scipy`, or `mido`. A clean `/tmp/opencode/audio-analysis-venv` with `pip install -e 'plugins/audio-analysis[dev]'` installed successfully. Its full `pytest plugins/audio-analysis/tests -q` run collected 177 tests, showed failures in acceptance/audio-script/MIDI-script files, and exceeded the 120-second audit timeout before completion. It is not a passing suite.
* PASS (original audit): `python3 -m compileall -q scripts` in both audio-analysis and notify-hook.
* FAIL (final direct verification): `/tmp/opencode/audio-analysis-venv/bin/python -m pytest plugins/audio-analysis/tests -q --tb=short` completed in 88.44 seconds: **154 passed, 22 failed, 1 skipped**. Tempo, beat, and comparison paths reported `only 0-dimensional arrays can be converted to Python scalars`; MIDI structure reported `'list' object has no attribute 'get'`. Other failures involve CLI arguments and output shapes. Coverage reported no collected data.
* FAIL (final direct verification): `plugins/lore-development/.venv/bin/python -m pytest -c /dev/null plugins/notify-hook/tests -q --tb=line` independently reproduced **74 passed, 12 failed**. The `/dev/null` config also caused harmless pytest cache permission warnings.

Safe, explicit follow-up commands (the tests use mocks and pytest temporary
paths for network/filesystem cases, but audio tests also invoke local scripts):

```bash
# Router unit suite, without Jest-only options
cd ~/Applications/opencode-plugins/opencode-model-router && npm test

# Notify tests, ignoring audio-analysis pytest configuration
cd /home/rjroy/.agents
plugins/lore-development/.venv/bin/python -m pytest -c /dev/null plugins/notify-hook/tests -q

# Audio suite after installing declared project and dev dependencies into an
# isolated /tmp/opencode virtualenv, never system Python
python3 -m venv /tmp/opencode/audio-analysis-venv
/tmp/opencode/audio-analysis-venv/bin/python -m pip install -e 'plugins/audio-analysis[dev]'
/tmp/opencode/audio-analysis-venv/bin/python -m pytest plugins/audio-analysis/tests -q
```

# Recommended follow-ups

1. Replace `${CLAUDE_PLUGIN_ROOT}` in art-gen and lore-development with an
   OpenCode-supported location strategy.
2. Install intended agents and commands in OpenCode discovery directories, or
   explicitly register them, for the collections that expect them.
3. Port Claude tool names and `Task` workflow instructions to actual OpenCode
   tool names and contracts.
4. Reimplement notify-hook as a registered OpenCode JavaScript/TypeScript
   plugin, or retire its legacy hook manifest.
5. Investigate the live router grader dispatch failures and run controlled
   runtime dispatch scenarios before claiming router behavioral compatibility.
6. Resolve the confirmed audio-analysis and notify-hook suite failures.

Durable follow-ups created from this review: `agents-39y` (repair notify-hook
pytest contract) and `agents-2kl` (investigate audio-analysis failures and test
duration). The prior audit issue `agents-hjo` remains closed.
V2 registration, Claude-specific instructions, notification integration, and
live router grading follow-up are tracked in `agents-zbj` (P1).
