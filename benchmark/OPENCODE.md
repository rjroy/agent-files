# OpenCode host adapter

The benchmark sends prompts through your **installed OpenCode CLI**, not
directly to provider APIs. OpenCode makes any inference requests using your
real setup: your authenticated providers (`opencode auth`), your agents,
plugins, skills, and configuration. `doctor` checks the CLI and the model
catalog without sending a prompt or creating a model session. `--demo`
remains the no-inference workflow rehearsal.

## Prerequisites and authentication

Install OpenCode normally (for example via mise or your package manager) and
authenticate the providers you want to benchmark with `opencode auth`. The
adapter resolves `opencode` from your `PATH`; if needed, point
`BENCHMARK_OPENCODE_BIN` at the CLI executable. No per-run configuration is
required, and no sandbox, temporary home, or generated config is used.

Use the exact OpenCode ID (`provider/model` or `provider/model#variant`).
`doctor` verifies the ID appears in your installed CLI's enabled model list
(`opencode models`). It cannot verify that a provider account has usable
funds or that a variant is currently selectable; that is confirmed by the
first live run.

From the repository root:

```sh
python -m benchmark doctor --model ollama-cloud/glm-5.3 --json
python -m benchmark doctor --model ollama-cloud/glm-5.3 --profile coding --json
python -m unittest discover -s benchmark/tests -p test_opencode_adapter.py -v
```

After choosing models and agreeing on a spend limit, place only the IDs in a
JSON file with the shape of `models.example.json`, then run:

```sh
python -m benchmark run --config /path/to/models.json --allow-live
```

`--allow-live` authorizes inference. It does not enforce a budget; use provider
limits and restrict the model and case lists before starting. Do not assume a
model is free based on its ID.

## How cases run

- Each case runs in the runner's disposable per-case workspace, but through
  your real OpenCode: the CLI inherits the ambient environment and uses your
  login, subscriptions, and configuration as-is.
- The first turn creates an **archived** session titled "Model benchmark" so
  benchmark sessions stay out of your normal session lists; follow-up turns
  continue that same session by ID.
- Coding cases pass `--auto` so workspace tool permissions are auto-approved
  unless your config explicitly denies them. Talking cases run without it.
- Tool use is recorded from the CLI's JSON event stream and reported as
  evidence for rubrics that need it. Any tool your configuration permits may
  appear in a coding trace; there is no benchmark-enforced tool allowlist.
- The provider you select necessarily receives the benchmark data and your
  account's normal billing applies.

## Comparability caveat

Unlike the previous isolated runtime, host-mode responses are influenced by
your ambient OpenCode configuration: custom agents, plugins, skills, and
instructions all apply. Scores from this adapter reflect how models behave
in *your* setup, which is the point — but they are not comparable to
sandboxed, config-free benchmark results from other harnesses.
