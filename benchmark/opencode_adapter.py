"""Run benchmark cases through the user's installed OpenCode CLI.

The adapter uses the host OpenCode installation as-is: the ambient
environment, the user's authenticated providers, agents, plugins, and
skills all apply. Authentication and model availability come from the
user's normal OpenCode setup (``opencode auth`` and their config files),
never from per-run configuration.
"""

from pathlib import Path
import json
import logging
import os
import re
import shutil
import subprocess


LOG = logging.getLogger(__name__)
MODEL_PATTERN = re.compile(
    r"([a-z0-9][a-z0-9-]*)/([a-zA-Z0-9_.:-]+(?:/[a-zA-Z0-9_.:-]+)*)(?:#([a-zA-Z0-9_-]+))?")
PROBE_TIMEOUT = 60
TURN_TIMEOUT = 300


def _binary():
    override = os.environ.get("BENCHMARK_OPENCODE_BIN")
    if override:
        executable = Path(override)
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise RuntimeError(f"BENCHMARK_OPENCODE_BIN is not an executable file: {override}")
        return executable.resolve()
    found = shutil.which("opencode")
    if not found:
        raise RuntimeError("opencode not found on PATH; install OpenCode or set BENCHMARK_OPENCODE_BIN")
    return Path(found).resolve()


def _parse_model(model):
    match = MODEL_PATTERN.fullmatch(model)
    if not match:
        raise ValueError("Use an OpenCode provider/model or provider/model#variant ID")
    return match.groups()


def _cli(binary, args, cwd=None, timeout=PROBE_TIMEOUT):
    """Run the user's OpenCode CLI and return its standard output."""
    LOG.debug("Invoking OpenCode %s", args[0])
    try:
        result = subprocess.run(
            [str(binary), *args], cwd=cwd, env=os.environ.copy(),
            stdin=subprocess.DEVNULL, capture_output=True, encoding="utf-8",
            errors="replace", timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        LOG.debug("OpenCode %s timed out", args[0])
        raise RuntimeError(f"OpenCode {args[0]} timed out") from None
    except OSError as exc:
        raise RuntimeError(f"OpenCode {args[0]} could not start: {exc}") from None
    LOG.debug("OpenCode %s exited %d", args[0], result.returncode)
    if result.returncode:
        detail = (result.stderr or result.stdout or "").strip().splitlines()
        raise RuntimeError(f"OpenCode {args[0]} failed (exit {result.returncode}): "
                           + (detail[-1] if detail else "no diagnostic output"))
    return result.stdout


def doctor(model: str, profile: str = "talking") -> dict:
    """Check the installed CLI and the model's availability without inference."""
    if profile not in ("talking", "coding"):
        raise ValueError("Unknown OpenCode benchmark profile")
    provider, model_id, _variant = _parse_model(model)
    binary = _binary()
    version = _cli(binary, ["--version"]).strip()
    base = f"{provider}/{model_id}"
    catalog = {line.strip() for line in _cli(binary, ["models"]).splitlines() if line.strip()}
    if base not in catalog:
        raise RuntimeError(f"{base} is not in the installed OpenCode's enabled model list; "
                           "run `opencode models` and check provider authentication")
    return {"ok": True, "model": model, "version": version, "profile": profile,
            "agent": "default", "binary": str(binary)}


def _read_turn(raw, expected_session):
    step = []
    answer = None
    trace = []
    session = expected_session
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            LOG.debug("Ignoring non-JSON OpenCode output: %.120s", line)
            continue
        if not isinstance(event, dict):
            continue
        event_session = event.get("sessionID")
        if isinstance(event_session, str) and event_session.startswith("ses_"):
            if session is not None and event_session != session:
                raise RuntimeError("OpenCode did not continue the benchmark session")
            session = event_session
        kind = event.get("type")
        part = event.get("part") or {}
        if kind == "error":
            raise RuntimeError("OpenCode reported a turn error (check model authentication and availability)")
        if kind == "step_start":
            step = []
            answer = None
        elif kind == "text":
            step.append(part.get("text", ""))
        elif kind == "tool_use":
            state = part.get("state") or {}
            details = state.get("metadata", {}).get("metadata", {})
            trace.append({"tool": part.get("tool"), "status": state.get("status"),
                          "input": state.get("input"),
                          "output": state.get("output", state.get("error")),
                          "exit": details.get("exit")})
        elif kind == "step_finish" and part.get("reason") == "stop":
            answer = "".join(step).strip()
    if not answer:
        raise RuntimeError("OpenCode produced no completed user-facing answer")
    if not session:
        raise RuntimeError("OpenCode did not report a session ID for the turn")
    return answer, session, trace


def run_case(model: str, turns: list[str], workspace: Path, coding: bool) -> dict:
    """Run exactly the supplied turns in order in one OpenCode session.

    Each turn invokes ``opencode run`` with the ambient environment inside the
    case workspace, so the user's installed OpenCode, login, agents, and
    configuration apply. The first turn creates an archived session (kept out
    of normal session lists); follow-up turns continue that same session.
    """
    if not turns or not all(isinstance(turn, str) and turn.strip() for turn in turns):
        raise ValueError("OpenCode case needs nonempty prompt turns")
    _parse_model(model)
    binary = _binary()
    workspace = Path(workspace)
    session = None
    answers = []
    trace = []
    for number, turn in enumerate(turns, 1):
        args = ["run", "--format", "json", "--model", model]
        if coding:
            args.append("--auto")
        args += (["--session", session] if session
                 else ["--archived", "--title", "Model benchmark"])
        args += ["--", turn]
        raw = _cli(binary, args, cwd=str(workspace), timeout=TURN_TIMEOUT)
        try:
            answer, session, events = _read_turn(raw, session)
        except (KeyError, TypeError, ValueError):
            raise RuntimeError("OpenCode returned invalid JSON turn events") from None
        answers.append(answer)
        trace.extend({"turn": number, **event} for event in events)
    evidence = ("OpenCode tool events:\n" + json.dumps(trace, ensure_ascii=False, indent=2)
                if trace else "No OpenCode tool events were recorded.")
    return {"answers": answers, "evidence": evidence}
