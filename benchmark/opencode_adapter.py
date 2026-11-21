"""Run benchmark cases through a disposable OpenCode v2.3.2 runtime."""

from contextlib import ExitStack, contextmanager
import json
import logging
import os
from pathlib import Path
import pwd
import re
import secrets
import shutil
import subprocess
import tempfile
import time

from ._opencode_sandbox import (
    SYSTEM_PATH, bubblewrap, check_workspace, server_command, shell_launcher,
)


VERSION = "2.3.2"
REPOSITORY = Path(__file__).resolve().parents[1]
AGENT = "build"
STOCK_AGENTS = {"build", "general", "explore", "compaction", "title", "summary", "plan"}
CODING_TOOLS = ("read", "edit", "write", "glob", "grep", "patch", "shell")
TOOL_PLUGINS = {"opencode.tool." + tool for tool in CODING_TOOLS}
DISABLED_PLUGINS = ("opencode.tools", "opencode.browser", "opencode.config.instruction")
PROVIDER_KEY_ENV = "BENCHMARK_PRIVATE_OPENCODE_PROVIDER_KEY"
PROVIDER_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_GENERATIVE_AI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "opencode": "OPENCODE_API_KEY",
    "opencode-go": "OPENCODE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}
MODEL_PATTERN = re.compile(r"([a-z0-9][a-z0-9-]*)/([a-zA-Z0-9_.:-]+(?:/[a-zA-Z0-9_.:-]+)*)(?:#([a-zA-Z0-9_-]+))?")
LISTEN_PATTERN = re.compile(r"server listening on (http://127\.0\.0\.1:[1-9][0-9]{0,4})")
FIXTURE_PATTERN = re.compile(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})/v1")
PROBE_TIMEOUT = 15
TURN_TIMEOUT = 300
LOG = logging.getLogger(__name__)


def _isolated(condition, reason):
    if not condition:
        raise RuntimeError(f"OpenCode isolation: {reason}")


def _native_binary():
    # The host's `opencode` may be a mise shim depending on user config. Prefer
    # its installed, pinned native package instead of mounting that user config.
    home = Path(pwd.getpwuid(os.getuid()).pw_dir)
    packages = home / f".local/share/mise/installs/npm-opencode-cli/{VERSION}/node_modules/.mise"
    for path in sorted(packages.glob(f"@opencode+cli-linux-*@{VERSION}/node_modules/"
                                     "@opencode/cli-linux-*/bin/opencode")):
        if "-baseline" not in str(path) and "-musl" not in str(path):
            if os.access(path, os.X_OK):
                return path.resolve()
    executable = shutil.which("opencode")
    return Path(executable).resolve() if executable else None


def _loopback_fixture(provider):
    url = os.environ.get("BENCHMARK_OPENCODE_LOOPBACK_URL")
    if not url:
        return None
    endpoint = FIXTURE_PATTERN.fullmatch(url)
    _isolated(provider == "opencode" and endpoint and int(endpoint[1]) <= 65535,
              "fixture URL must be http://127.0.0.1:PORT/v1 for an opencode model")
    return url


def _binary(fixture_url):
    native = _native_binary()
    override = os.environ.get("BENCHMARK_OPENCODE_BIN")
    if override:
        binary = Path(override)
        _isolated(binary.is_absolute(), "BENCHMARK_OPENCODE_BIN must be an absolute path")
        binary = binary.resolve()
    else:
        binary = native
    _isolated(binary and binary.is_file() and os.access(binary, os.X_OK),
              "set BENCHMARK_OPENCODE_BIN to the installed native OpenCode executable")
    # A trusted adapter test launcher may exec the installed CLI by its native
    # absolute path. No containing package or home directory is mounted.
    with binary.open("rb") as executable:
        is_native = executable.read(4) == b"\x7fELF"
    if not is_native:
        _isolated(override and fixture_url,
                  "non-ELF OpenCode launchers require an explicit loopback fixture")
        _isolated(not any(os.environ.get(name) for name in {*PROVIDER_ENV.values(), PROVIDER_KEY_ENV}),
                  "non-ELF OpenCode launchers require an environment without provider credentials")
    return binary, is_native, (native if not is_native and native != binary else None)


def _runtime_config(model, provider, tools, shell, opencode_key, fixture_url):
    actions = ["edit" if tool == "write" else tool for tool in tools]
    permissions = [{"action": "*", "resource": "*", "effect": "deny"}]
    permissions += [{"action": action, "resource": "*", "effect": "allow"}
                    for action in dict.fromkeys(actions)]
    plugins = ["-opencode.tool.*", "-opencode.tools.*", *("-" + name for name in DISABLED_PLUGINS)]
    plugins += sorted(TOOL_PLUGINS) if tools else []
    policies = [{"action": action, "resource": "*", "effect": "deny"}
                for action in ("skill.use", "mcp.use", "plugin.use", "websearch.use")]
    policies.extend(({"action": "provider.use", "resource": "*", "effect": "deny"},
                     {"action": "provider.use", "resource": provider, "effect": "allow"}))
    config = {
        "model": model,
        "default_agent": AGENT,
        "update": "disable",
        "share": "disabled",
        "permissions": permissions,
        "policies": policies,
        "plugins": plugins,
        "lsp": False,
        "formatter": False,
        "snapshots": False,
        "compaction": {"auto": False, "background": False},
        "warming": False,
    }
    if shell:
        config["shell"] = str(shell)
    if opencode_key:
        # A process-wide OPENCODE_API_KEY starts the Console integration's
        # remote configuration bootstrap before local plugins finish loading.
        # Scope the key to the selected provider without enabling that account.
        config["providers"] = {provider: {"settings": {"apiKey": "{env:" + PROVIDER_KEY_ENV + "}"}}}
    if fixture_url:
        settings = config.setdefault("providers", {}).setdefault(provider, {}).setdefault("settings", {})
        settings["baseURL"] = fixture_url
    return config


def _environment(runtime, secret):
    return {
        "PATH": SYSTEM_PATH,
        "HOME": str(runtime / "home"),
        "XDG_CONFIG_HOME": str(runtime / "config"),
        "XDG_DATA_HOME": str(runtime / "data"),
        "XDG_CACHE_HOME": str(runtime / "cache"),
        "XDG_STATE_HOME": str(runtime / "state"),
        "TMPDIR": str(runtime / "tmp"),
        "XDG_RUNTIME_DIR": str(runtime / "run"),
        "OPENCODE_SERVER_PASSWORD": secret,
        "OPENCODE_DISABLE_AUTOUPDATE": "true",
        "OPENCODE_DISABLE_MODELS_FETCH": "true",
        "OPENCODE_DISABLE_CLAUDE_CODE": "true",
        "OPENCODE_CONFIG_PROJECT_DISABLE": "true",
        "OPENCODE_FILEWATCHER_DISABLE": "true",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }


@contextmanager
def _server(cmd, env, workspace):
    # Keep the child's pipe drained to a private file after startup; its
    # diagnostic text can include provider data and is never returned to users.
    with tempfile.TemporaryFile(mode="w+b") as diagnostics:
        process = subprocess.Popen(
            [*cmd, "serve", "--hostname", "127.0.0.1", "--port", "0"],
            cwd=workspace, env=env, stdin=subprocess.DEVNULL,
            stdout=diagnostics, stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + PROBE_TIMEOUT
            while time.monotonic() < deadline:
                # pread does not change the file offset shared with the server.
                startup = os.pread(diagnostics.fileno(), 8192, 0).decode(errors="replace")
                endpoint = next((m[1] for line in startup.splitlines()
                                 if (m := LISTEN_PATTERN.fullmatch(line))), None)
                if endpoint:
                    yield endpoint
                    return
                if process.poll() is not None:
                    break
                time.sleep(0.02)
            raise RuntimeError("OpenCode isolation: private server did not start")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


class _Runtime:
    def __init__(self, client_command, endpoint, env, workspace, secrets_to_hide):
        self.client_command = client_command
        self.endpoint = endpoint
        self.env = env
        self.workspace = workspace
        self.secrets = secrets_to_hide

    def invoke(self, command, *args, timeout=PROBE_TIMEOUT):
        LOG.debug("Invoking private OpenCode %s", command)
        try:
            result = subprocess.run(
                [*self.client_command, command, "--server", self.endpoint, *args],
                cwd=self.workspace, env=self.env, stdin=subprocess.DEVNULL,
                capture_output=True, encoding="utf-8", errors="replace", timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            LOG.debug("Private OpenCode %s timed out", command)
            raise RuntimeError(f"OpenCode {command} timed out") from None
        LOG.debug("Private OpenCode %s exited %d", command, result.returncode)
        if result.returncode:
            raise RuntimeError(f"OpenCode {command} failed (exit {result.returncode})")
        return result.stdout

    def api(self, operation):
        data = json.loads(self.invoke("api", operation))
        if isinstance(data, dict) and "_tag" in data:
            raise RuntimeError(f"OpenCode isolation: runtime rejected {operation}")
        return data

    def redact(self, text):
        for value in self.secrets:
            if value:
                text = text.replace(value, "[redacted]")
        return text


def _verify_runtime(runtime, config_file, expected, tools, provider, model_id, variant):
    identity = runtime.api("server.info")
    _isolated(identity["version"] == VERSION and identity["urls"] == [runtime.endpoint],
              f"expected a private OpenCode {VERSION} server")
    location = runtime.api("location.get")
    directory = str(runtime.workspace)
    _isolated(location["directory"] == directory
              and location["project"]["directory"] == directory
              and location["project"]["canonical"] == directory,
              "unexpected workspace or project root")
    entries = runtime.api("config.get")
    documents = [entry for entry in entries if entry.get("type") == "document"]
    _isolated(len(documents) == 1 and documents[0].get("path") == str(config_file) and all(
        entry.get("type") == "document" or
        (entry.get("type") == "directory" and entry.get("path") == str(config_file.parent))
        for entry in entries), "unexpected config source")
    expected = {**expected, "model": {"providerID": provider, "model": model_id}}
    if variant:
        expected["model"]["variant"] = variant
    _isolated(documents[0]["info"] == expected, "unexpected effective config")
    _verify_agent(runtime, directory, expected["permissions"])
    plugins = runtime.api("plugin.list")["data"]
    _isolated(all(item["source"]["type"] == "builtin" and item["state"]["status"] == "active"
                  for item in plugins), "unexpected external or failed plugin")
    ids = {item["id"] for item in plugins}
    _isolated({item for item in ids if item.startswith("opencode.tool.")}
              == (TOOL_PLUGINS if tools else set())
              and not any(item.startswith("opencode.tools.") for item in ids)
              and not ids.intersection(DISABLED_PLUGINS), "unexpected tool or instruction plugin")
    for operation in ("skill.list", "mcp.list", "permission.saved.list", "session.list"):
        payload = runtime.api(operation)
        _isolated((payload["data"] if isinstance(payload, dict) else payload) == [],
                  f"unexpected runtime state in {operation}")
    models = runtime.api("model.list")
    _isolated(all(item["providerID"] == provider for item in models["data"]),
              "unexpected provider in the model catalog")
    exact = next((item for item in models["data"]
                  if item["providerID"] == provider and item["id"] == model_id and item["enabled"]), None)
    if not exact or (variant and variant not in {"default", *(v["id"] for v in exact["variants"])}):
        raise RuntimeError("Requested OpenCode model/variant is not enabled in the isolated runtime; "
                           "check the selected provider's benchmark authentication")
    if tools and not exact["capabilities"].get("tools"):
        raise RuntimeError("Requested OpenCode model does not advertise tool support")


def _verify_agent(runtime, directory, rules):
    # v2.3.2 initially returns the built-in defaults while its location
    # transform is loading. Wait only for the checked config's merged rules.
    deadline = time.monotonic() + 3
    while True:
        agents = runtime.api("agent.list")
        _isolated(agents["location"]["directory"] == directory
                  and {item["id"] for item in agents["data"]} == STOCK_AGENTS,
                  "unexpected agent inventory")
        build = next(item for item in agents["data"] if item["id"] == AGENT)
        _isolated(build["mode"] == "primary" and not build["hidden"] and not build.get("system")
                  and not any(build["request"].values()), "unexpected stock-agent overrides")
        permissions = build["permissions"]
        fallback = max((i for i, rule in enumerate(permissions) if rule == rules[0]), default=-1)
        if fallback >= 0:
            after_fallback = permissions[fallback + 1:]
            _isolated([rule for rule in after_fallback if rule["effect"] == "allow"] == rules[1:]
                      and not any(rule["effect"] == "ask" for rule in after_fallback),
                      "effective agent permissions are not default-deny")
            return
        _isolated(time.monotonic() < deadline, "effective agent permissions did not become default-deny")
        time.sleep(0.05)


@contextmanager
def _runtime(model, profile, workspace=None):
    match = MODEL_PATTERN.fullmatch(model)
    if not match:
        raise ValueError("Use an OpenCode provider/model or provider/model#variant ID")
    if profile not in ("talking", "coding"):
        raise ValueError("Unknown OpenCode benchmark profile")
    provider, model_id, variant = match.groups()
    if provider not in PROVIDER_ENV:
        raise ValueError("Provider is not in the benchmark's explicit authentication allowlist")
    if workspace is not None:
        workspace = Path(workspace)
        _isolated(workspace.is_absolute() and workspace.resolve() == workspace
                  and not workspace.is_mount(), "workspace must be a canonical disposable directory")
        check_workspace(workspace, REPOSITORY)
    tools = CODING_TOOLS if profile == "coding" else ()
    fixture_url = _loopback_fixture(provider)
    binary, is_native, guest_native = _binary(fixture_url)
    _isolated(not workspace or not binary.is_relative_to(workspace),
              "OpenCode executable must be outside the writable workspace")
    bwrap = bubblewrap()
    with ExitStack() as stack:
        # Share a temporary parent with neither the repo nor any ambient config.
        # Respect the caller's temporary root so a no-egress harness can mount it.
        root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="opencode-bench-"))).resolve()
        _isolated(not root.is_relative_to(REPOSITORY) and not (workspace and root.is_relative_to(workspace)),
                  "temporary runtime is inside the repository or case")
        if workspace is None:
            # Siblings keep the credential-bearing server runtime outside the case.
            workspace = root / "workspace"
            workspace.mkdir()
        private = root / "runtime"
        private.mkdir(mode=0o700)
        for name in ("home", "config", "data", "cache", "state", "tmp", "run"):
            (private / name).mkdir(mode=0o700)
        secret = secrets.token_urlsafe(32)
        env = _environment(private, secret)
        provider_key = os.environ.get(PROVIDER_ENV[provider], "") if is_native else ""
        engine_key = provider_key if provider in ("opencode", "opencode-go") else ""
        server_env = dict(env)
        if provider_key:
            server_env[PROVIDER_KEY_ENV if engine_key else PROVIDER_ENV[provider]] = provider_key
        shell = shell_launcher(bwrap, private, workspace) if tools else None
        config = _runtime_config(model, provider, tools, shell, engine_key, fixture_url)
        config_file = private / "config/opencode/opencode.json"
        config_file.parent.mkdir(mode=0o700)
        fd = os.open(config_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(config, output)
        command = server_command(bwrap, binary, private, workspace, bool(tools))
        if guest_native:
            command[1:1] = ["--ro-bind", str(guest_native), str(guest_native)]
        if shell:
            proof = subprocess.run(
                [*command[:-1], str(shell), "-c",
                 'test -z "$OPENCODE_SERVER_PASSWORD" && test ! -e "$1" && test "$PWD" = "$2"',
                 "benchmark", str(private), str(workspace)],
                env=server_env, cwd=workspace, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=PROBE_TIMEOUT,
            )
            _isolated(proof.returncode == 0, "workspace shell sandbox failed its no-inference check")
        endpoint = stack.enter_context(_server(command, server_env, workspace))
        # The native CLI gets the same limited filesystem but its own PID
        # namespace and no provider credential. A deliberately supplied
        # non-ELF test launcher is trusted caller code, not a live harness.
        client = command if is_native else [str(binary)]
        runtime = _Runtime(client, endpoint, env, workspace, (provider_key, secret))
        expected = dict(config)
        if engine_key:
            settings = {**config["providers"][provider]["settings"], "apiKey": engine_key}
            expected["providers"] = {provider: {"settings": settings}}
        try:
            _verify_runtime(runtime, config_file, expected, tools, provider, model_id, variant)
        except (KeyError, TypeError, ValueError, StopIteration):
            raise RuntimeError("OpenCode isolation: runtime metadata did not match v2.3.2") from None
        yield runtime, tools


def doctor(model: str, profile: str = "talking") -> dict:
    """Check a fresh runtime's metadata and permissions without issuing a prompt."""
    with _runtime(model, profile) as (runtime, tools):
        return {"ok": True, "model": model, "version": VERSION, "profile": profile,
                "workspace": str(runtime.workspace), "agent": AGENT, "allowed_tools": list(tools)}


def _read_turn(raw, expected_session, tools):
    step = []
    answer = None
    trace = []
    session = expected_session
    for line in raw.splitlines():
        event = json.loads(line)
        event_session = event.get("sessionID")
        if not isinstance(event_session, str) or not event_session.startswith("ses_"):
            raise RuntimeError("OpenCode emitted an event without a valid session ID")
        if session is not None and event_session != session:
            raise RuntimeError("OpenCode did not continue the benchmark session")
        session = event_session
        kind = event["type"]
        part = event.get("part", {})
        if kind == "error":
            raise RuntimeError("OpenCode reported a turn error (check model authentication and availability)")
        if kind == "step_start":
            step = []
            answer = None
        elif kind == "text":
            step.append(part["text"])
        elif kind == "tool_use":
            tool = part["tool"]
            if tool not in tools:
                raise RuntimeError("OpenCode isolation: turn ran a tool outside its allowlist")
            state = part["state"]
            details = state.get("metadata", {}).get("metadata", {})
            trace.append({"tool": tool, "status": state["status"], "input": state.get("input"),
                          "output": state.get("output", state.get("error")),
                          "exit": details.get("exit")})
        elif kind == "step_finish" and part.get("reason") == "stop":
            answer = "".join(step).strip()
    if not answer or not session:
        raise RuntimeError("OpenCode produced no completed user-facing answer")
    return answer, session, trace


def run_case(model: str, turns: list[str], workspace: Path, coding: bool) -> dict:
    """Run exactly the supplied turns in order in one fresh OpenCode session."""
    if not turns or not all(isinstance(turn, str) and turn.strip() for turn in turns):
        raise ValueError("OpenCode case needs nonempty prompt turns")
    with _runtime(model, "coding" if coding else "talking", workspace) as (runtime, tools):
        session = None
        answers, trace = [], []
        for number, turn in enumerate(turns, 1):
            selector = ("--session", session) if session else ("--title", "Model benchmark")
            raw = runtime.invoke("run", "--format", "json", "--agent", AGENT, "--model", model,
                                 *selector, "--", turn, timeout=TURN_TIMEOUT)
            try:
                answer, session, events = _read_turn(raw, session, tools)
            except (KeyError, TypeError, ValueError):
                raise RuntimeError("OpenCode returned invalid JSON turn events") from None
            answers.append(runtime.redact(answer))
            trace.extend({"turn": number, **event} for event in events)
            if coding:
                check_workspace(runtime.workspace, REPOSITORY)
        evidence = ("OpenCode tool events:\n" + json.dumps(trace, ensure_ascii=False, indent=2)
                    if trace else "No OpenCode tool events were recorded.")
        return {"answers": answers, "evidence": runtime.redact(evidence)}
