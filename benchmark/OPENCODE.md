# Isolated OpenCode adapter

The benchmark sends prompts to a fresh local **OpenCode v2.3.2** server, not
directly to provider APIs. OpenCode makes any inference requests. `doctor`
starts the local runtime, but never sends a prompt or creates a model session.
`--demo` remains the no-inference workflow rehearsal.

## Prerequisites and authentication

Use Linux with Bubblewrap, working unprivileged user namespaces, and
`libseccomp.so.2`. The adapter uses the installed mise-pinned native OpenCode
2.3.2 if present; otherwise it looks on `PATH`. If necessary, point
`BENCHMARK_OPENCODE_BIN` at the absolute path of the native executable, **not**
a shell, package-manager, or mise shim. A version mismatch or sandbox failure
stops the run.

Use the exact OpenCode ID (`provider/model` or `provider/model#variant`).
Only the credential for the selected provider is passed to its private server:

| Provider ID | API key environment variable | Example ID for `doctor` |
| --- | --- | --- |
| `opencode` | `OPENCODE_API_KEY` (optional for public models) | `opencode/beam-free` |
| `opencode-go` | `OPENCODE_API_KEY` | `opencode-go/beam-free` |
| `openai` | `OPENAI_API_KEY` | `openai/gpt-4.1` |
| `anthropic` | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4-6` |
| `google` | `GOOGLE_GENERATIVE_AI_API_KEY` | `google/gemini-2.5-flash` |
| `openrouter` | `OPENROUTER_API_KEY` | `openrouter/anthropic/claude-sonnet-4.6` |

Supply keys from a trusted secret manager or read them into the launch shell
without echo. Do not put a key in the model list, arguments, fixtures, or results.
For OpenCode and Go, the adapter substitutes an environment value into private
provider settings without enabling Console account configuration discovery.
Normal OpenCode logins, OAuth sessions, custom provider configuration, and
provider accounts outside this table are not imported. `doctor` checks the
bundled model catalog and what appears enabled in the isolated runtime; it
cannot verify a key, subscription, remote model access, current price, or
provider reachability. It also does not refresh the catalog.

From the repository root:

```sh
python -m benchmark doctor --model opencode/beam-free --json
python -m benchmark doctor --model opencode/beam-free --profile coding --json
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

## What is isolated

- The pinned native server and client use a restricted Linux filesystem view, not
  the repository or user home. They get a temporary case workspace and fresh
  private home, XDG state, data, cache, and config. They use an explicit
  password-protected, ephemeral loopback endpoint, not the shared service.
  The workspace path in `doctor` is diagnostic; its files are removed on exit.
  If calling `run_case` directly, create the case under a caller-owned private
  temporary directory, not under a shared or existing project directory.
- `doctor` checks the server version and location, exact config sources and
  contents, stock agent inventory, applied deny-by-default rules, active plugin
  inventory, absence of skills/MCP servers/saved permissions/sessions, and model
  availability. It checks the actual nested shell sandbox for the coding profile
  without inference. Case execution repeats these checks on its own runtime.
  The instruction plugin, delegation, skills, external plugins, MCP, web tools,
  and OpenCode worktree/session tools are excluded. The stock agent's own built-in
  prompt is still part of the benchmark.
- Talking has no tools and a read-only workspace. Coding permits OpenCode's
  workspace file/search/edit tools and shell (the model may receive edit or patch
  depending on OpenCode's model-family selection). Shell uses a separate mount,
  PID, IPC, and network namespace, a cleared environment, and no access to the
  private OpenCode runtime or its credentials. It can use host system binaries
  and libraries mounted read-only, scratch space, and the writable case only.
  The adapter rejects pre-existing links, special files, mounts, and config or
  instruction files in cases; shell link and device-node creation are blocked.
- The OpenCode server itself needs outbound networking for live inference. Its
  selected provider necessarily receives its own key and the benchmark data.
  This is not a defense against a compromised OpenCode binary, provider,
  kernel, or another process under the same host user account. There are no
  disk/process quotas. Use only disposable, synthetic cases. Exact configured
  secret strings are redacted from returned answers and evidence; server logs
  are not included. The runner records captured OpenCode tool events separately
  from its own checks and diff.

For testing only, `BENCHMARK_OPENCODE_LOOPBACK_URL=http://127.0.0.1:PORT/v1`
redirects `opencode` inference to a fixture. Put the fixture and benchmark
inside a private network namespace so a broken fixture cannot reach a live
provider. An explicitly selected **non-ELF** `BENCHMARK_OPENCODE_BIN` is a
trusted test launcher and its client side runs outside the native client
sandbox. Before executing it, including for diagnostics, the adapter requires
an explicit `http://127.0.0.1:PORT/v1` fixture for an `opencode/...` model and
rejects any nonempty benchmark provider API key, even for another provider.
Use a credential-free test environment. Never use an untrusted launcher or
this seam for live benchmarks. A normal `PATH` wrapper is rejected, not run
in reduced isolation. Native OpenCode can still use the credentials above.
