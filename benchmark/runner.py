"""Execute cases, persist review state, and reveal results after human grading."""

import argparse
from contextlib import contextmanager
import difflib
import fcntl
import json
import os
from pathlib import Path
import random
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = Path(__file__).resolve().parent / "cases"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "results" / "latest"
DEMO_MODELS = ["demo/alpha", "demo/beta"]


@contextmanager
def output_lock(output):
    """Hold one exclusive lock across execution or the whole review session."""
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".lock").open("a", encoding="utf-8") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another benchmark process holds the output lock") from exc
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def save_state(output, state):
    atomic_write(output / "state.json", json.dumps(state, indent=2) + "\n")


def contained(directory, name):
    path = (directory / name).resolve()
    if not path.is_relative_to(directory.resolve()):
        raise ValueError(f"case path escapes its directory: {name}")
    return path


def load_cases(root):
    cases = []
    for manifest in sorted(root.glob("*/case.json")):
        case = json.loads(manifest.read_text(encoding="utf-8"))
        if (case.get("version") != 1 or case.get("id") != manifest.parent.name
                or not isinstance(case.get("role"), str)
                or not isinstance(case.get("turns"), list) or not case["turns"]
                or not all(isinstance(t, str) and t for t in case["turns"])
                or not isinstance(case.get("rubrics"), list)):
            raise ValueError(f"invalid manifest: {manifest}")
        for rubric in case["rubrics"]:
            if (not isinstance(rubric, dict) or not isinstance(rubric.get("label"), str)
                    or not isinstance(rubric.get("prompt"), str)
                    or not isinstance(rubric.get("evidence"), bool)
                    or ("decision_prompt" in rubric and
                        (not isinstance(rubric["decision_prompt"], str)
                         or not rubric["decision_prompt"].strip()))):
                raise ValueError(f"invalid rubric: {manifest}")
        # Evidence must never appear before all message-only judgments for a response.
        flags = [r["evidence"] for r in case["rubrics"]]
        if flags != sorted(flags):
            raise ValueError(f"evidence rubrics must follow message rubrics: {manifest}")
        for field in ("fixture", "check"):
            if field in case:
                if not isinstance(case[field], str):
                    raise ValueError(f"invalid {field}: {manifest}")
                contained(manifest.parent, case[field])
        case["_directory"] = str(manifest.parent.resolve())
        cases.append(case)
    if not cases:
        raise ValueError(f"no case manifests found in {root}")
    return cases


def snapshot(workspace):
    files = {}
    def raise_walk_error(error):
        raise error

    root_fd = os.open(workspace, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for directory, _, names, directory_fd in os.fwalk(
                ".", dir_fd=root_fd, follow_symlinks=False, onerror=raise_walk_error):
            for name in sorted(names):
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode):
                    continue
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory_fd)
                try:
                    if not stat.S_ISREG(os.fstat(fd).st_mode):
                        raise OSError(f"snapshot file changed type: {name}")
                    with os.fdopen(fd, "rb") as stream:
                        fd = -1
                        data = stream.read()
                finally:
                    if fd != -1:
                        os.close(fd)
                files[str(Path(directory) / name)] = data.decode("utf-8", errors="replace")
    finally:
        os.close(root_fd)
    return files


def stage_fixture(directory, fixture, workspace):
    """Reject unsafe entries, then copy via directory descriptors without following links."""
    parts = Path(fixture).parts
    if not parts or Path(fixture).is_absolute() or any(p in (".", "..") for p in parts):
        raise ValueError("invalid fixture path")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    root = os.open(directory, flags)
    try:
        for part in parts:
            child = os.open(part, flags, dir_fd=root)
            os.close(root)
            root = child

        def visit(source_fd, destination=None):
            with os.scandir(source_fd) as entries:
                names = sorted(entry.name for entry in entries)
            for name in names:
                mode = os.stat(name, dir_fd=source_fd, follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    child_fd = os.open(name, flags, dir_fd=source_fd)
                    try:
                        target = destination / name if destination is not None else None
                        if target is not None:
                            target.mkdir()
                        visit(child_fd, target)
                        if target is not None:
                            target.chmod(stat.S_IMODE(os.fstat(child_fd).st_mode) & 0o777)
                    finally:
                        os.close(child_fd)
                elif stat.S_ISREG(mode):
                    if destination is not None:
                        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                     dir_fd=source_fd)
                        try:
                            if not stat.S_ISREG(os.fstat(fd).st_mode):
                                raise ValueError(f"unsafe fixture entry: {name}")
                            with os.fdopen(fd, "rb") as source:
                                fd = -1
                                with (destination / name).open("xb") as target:
                                    shutil.copyfileobj(source, target)
                                    os.fchmod(target.fileno(),
                                              stat.S_IMODE(os.fstat(source.fileno()).st_mode) & 0o777)
                        finally:
                            if fd != -1:
                                os.close(fd)
                else:
                    raise ValueError(f"unsafe fixture entry: {name}")

        visit(root)
        workspace.mkdir()
        visit(root, workspace)
    finally:
        os.close(root)


def changes(before, after):
    lines = []
    for name in sorted(before.keys() | after.keys()):
        if before.get(name) != after.get(name):
            lines.extend(difflib.unified_diff(
                before.get(name, "").splitlines(keepends=True),
                after.get(name, "").splitlines(keepends=True),
                fromfile="before/" + name, tofile="after/" + name))
    return "".join(lines) or "(no file changes)"


def demo_run(model, turns, workspace, coding):
    # Deliberately synthetic: this is a workflow rehearsal, not model output.
    return {"answers": [f"Demo response {i + 1} (synthetic, not a model result)."
                        for i in range(len(turns))],
            "evidence": "Demo adapter: no model or tools were invoked. Trace unverified."}


def run_check(checker, workspace):
    """Evaluate untrusted workspace code without host or network access."""
    bwrap = shutil.which("bwrap")
    if not bwrap or not Path("/usr/bin/python3").is_file():
        return "error", "Sandbox isolation unavailable: bubblewrap or system Python missing."
    if checker.resolve().is_relative_to("/usr") or workspace.resolve().is_relative_to("/usr"):
        return "error", "Sandbox isolation unavailable: case or workspace is under /usr."
    command = [bwrap, "--unshare-all", "--die-with-parent", "--new-session",
               "--ro-bind", "/usr", "/usr"]
    # Provide the system dynamic loader without exposing the host root.
    for name in ("/bin", "/lib", "/lib64"):
        path = Path(name)
        if path.is_symlink():
            command += ["--symlink", os.readlink(path), name]
        elif path.is_dir():
            command += ["--ro-bind", name, name]
    command += ["--proc", "/proc", "--dev", "/dev",
                "--tmpfs", "/tmp", "--dir", "/home", "--dir", "/evaluator",
                "--ro-bind", str(checker), "/evaluator/check.py",
                "--ro-bind", str(workspace), "/workspace",
                "--chdir", "/tmp", "--clearenv",
                "--setenv", "HOME", "/home", "--setenv", "PATH", "/usr/bin:/bin",
                "--setenv", "LANG", "C.UTF-8",
                "--", "/usr/bin/python3", "-B", "/evaluator/check.py", "/workspace"]
    try:
        proc = subprocess.run(command, cwd="/", env={"PATH": "/usr/bin:/bin"},
                              stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return "error", f"Sandbox isolation or check execution failed: {exc}"
    # Bubblewrap setup failures must not masquerade as an assertion failure.
    if proc.stderr.startswith("bwrap:"):
        return "error", "Sandbox isolation failed:\n" + proc.stderr
    return ({0: "pass", 1: "fail"}.get(proc.returncode, "error"),
            f"exit {proc.returncode}\n{proc.stdout}{proc.stderr}")


@contextmanager
def temporary_workspace(diagnostics):
    temporary = tempfile.TemporaryDirectory(prefix="model-benchmark-")
    try:
        yield temporary.name
    finally:
        try:
            temporary.cleanup()
        except RecursionError as exc:
            diagnostics.append(f"Temporary workspace cleanup recursion failed: {exc}")
            # GNU rm traverses deep trees without Python's recursion limit and
            # does not follow directory symlinks. Only target our private root.
            try:
                result = subprocess.run(
                    ["/usr/bin/rm", "-rf", "--", temporary.name],
                    stdin=subprocess.DEVNULL, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=120, check=False)
                if result.returncode:
                    diagnostics.append(
                        f"Cleanup fallback failed for {temporary.name}: {result.stderr}")
                else:
                    diagnostics.append("Cleanup fallback removed the temporary workspace.")
            except (OSError, subprocess.TimeoutExpired) as fallback_error:
                diagnostics.append(
                    f"Cleanup fallback failed for {temporary.name}: {fallback_error}")


def run_one(case, model, adapter):
    directory = Path(case["_directory"])
    cleanup_diagnostics = []
    with temporary_workspace(cleanup_diagnostics) as temp:
        base = Path(temp).resolve()
        if base.is_relative_to(ROOT):
            raise RuntimeError("temporary workspace is inside the repository")
        workspace = base / "workspace"
        fixture = case.get("fixture")
        try:
            if fixture:
                stage_fixture(directory, fixture, workspace)
            else:
                workspace.mkdir()
        except (OSError, ValueError, RecursionError) as exc:
            return {"status": "error", "error": f"fixture staging failed: {exc}",
                    "check": "not run", "answers": [], "evidence": ""}
        snapshot_errors = []
        try:
            before = snapshot(workspace)
        except (OSError, RecursionError) as exc:
            before = None
            snapshot_errors.append(f"Before snapshot failed: {exc}")
        coding = case["role"] in ("coding", "handoff", "orchestrator")
        error = None
        try:
            result = adapter(model, case["turns"], workspace, coding)
            if (not isinstance(result, dict) or not isinstance(result.get("answers"), list)
                    or len(result["answers"]) != len(case["turns"])
                    or not all(isinstance(a, str) and a for a in result["answers"])
                    or not isinstance(result.get("evidence"), str)):
                raise ValueError("adapter returned an invalid result")
        except Exception as exc:
            error = str(exc)
            result = {"answers": [], "evidence": "Adapter failed; trace unverified."}
        try:
            after = snapshot(workspace)
        except (OSError, RecursionError) as exc:
            after = None
            snapshot_errors.append(f"After snapshot failed: {exc}")
        diff = ("\n".join(snapshot_errors) + "\nWorkspace changes unverified."
                if snapshot_errors else changes(before, after))
        check = "not configured"
        check_detail = ""
        if case.get("check"):
            check, check_detail = run_check(contained(directory, case["check"]), workspace)
        outcome = {"status": "error" if error is not None else "ok", "answers": result["answers"],
                "check": check, "check_detail": check_detail,
                "evidence": (result["evidence"] or "Trace unverified.") +
                            "\n\nWorkspace changes:\n" + diff +
                            "\n\nIndependent check: " + check + "\n" + check_detail}
        if error is not None:
            outcome["error"] = error
    if cleanup_diagnostics:
        outcome["evidence"] += "\n\n" + "\n".join(cleanup_diagnostics)
    return outcome


def preflight(models, cases):
    from .opencode_adapter import doctor
    profiles = {"coding" if c["role"] in ("coding", "handoff", "orchestrator")
                else "talking" for c in cases}
    for model in models:
        for profile in sorted(profiles):
            result = doctor(model, profile=profile)
            if not isinstance(result, dict) or not result.get("ok"):
                raise RuntimeError(f"doctor failed for {model} ({profile}): {result}")


def execute_run(args):
    output = args.output_dir.resolve()
    with output_lock(output):
        execute_locked(args, output)


def execute_locked(args, output):
    if output.is_relative_to("/usr"):
        raise ValueError("output under /usr would be visible to the check sandbox")
    if (output / "state.json").exists() or (output / "scorecard.md").exists():
        raise ValueError("output already contains a run; use resume or choose a new directory")
    cases = load_cases(args.cases_dir.resolve())
    if args.demo:
        models = DEMO_MODELS
        adapter = demo_run
    else:
        if not args.config or not args.allow_live:
            raise ValueError("live runs require --config and --allow-live")
        config = json.loads(args.config.read_text(encoding="utf-8"))
        models = config.get("models")
        if (not isinstance(models, list) or not models
                or not all(isinstance(m, str) and m for m in models)
                or len(set(models)) != len(models)):
            raise ValueError("config models must be a nonempty list of unique model IDs")
        preflight(models, cases)
        from .opencode_adapter import run_case
        adapter = run_case
    state = {"version": 1, "demo": args.demo, "models": models,
             "cases": cases, "runs": {c["id"]: {} for c in cases}, "review": [], "grades": {},
             "phase": "executing"}
    output.mkdir(parents=True, exist_ok=True)
    save_state(output, state)
    for case in cases:
        for model in models:
            state["runs"][case["id"]][model] = run_one(case, model, adapter)
            save_state(output, state)
    prepare_review(state)
    save_state(output, state)
    review(output, state)


def prepare_review(state):
    """Mark interrupted work missing rather than repeating potentially paid calls."""
    cases = state["cases"]
    models = state["models"]
    for case in cases:
        for model in models:
            state["runs"][case["id"]].setdefault(
                model, {"status": "error", "error": "execution interrupted; outcome unavailable",
                        "check": "not run", "answers": [], "evidence": ""})
    for case in cases:
        available = [m for m in models if state["runs"][case["id"]][m]["status"] == "ok"]
        random.SystemRandom().shuffle(available)
        for index, model in enumerate(available):
            for rubric_index in range(len(case["rubrics"])):
                state["review"].append({"case": case["id"], "model": model,
                                        "label": f"Response {index + 1}",
                                        "rubric": rubric_index})
    state["phase"] = "review"


def blind(text, models):
    aliases = set()
    for model in models:
        for name in (model, model.split("#", 1)[0]):
            parts = name.split("/")
            aliases.update("/".join(parts[i:]) for i in range(len(parts)) if parts[i])
    if not aliases:
        return text
    alternatives = "|".join(re.escape(alias) for alias in sorted(aliases, key=len, reverse=True))
    return re.sub(r"(?<![\w-])(?:" + alternatives + r")(?![\w-])",
                  "[model identity hidden]", text, flags=re.IGNORECASE)


def scorecard(state):
    lines = ["# Benchmark scorecard", "",
             "Demo rehearsal: synthetic responses, not model performance." if state["demo"]
             else "Human grades are subjective. Checks are independent outcomes.", ""]
    for case in state["cases"]:
        lines += [f"## {case['id']} ({case['role']})", ""]
        for model in state["models"]:
            run = state["runs"][case["id"]][model]
            lines.append(f"- {model}: run {run['status']}; check {run['check']}")
            if run["status"] == "error":
                lines.append(f"  - Missing response: {run['error']}")
            for index, rubric in enumerate(case["rubrics"]):
                key = json.dumps([case["id"], model, index])
                if key in state["grades"]:
                    lines.append(f"  - {rubric['label']}: {state['grades'][key]}/5")
        lines.append("")
    return "\n".join(lines) + "\n"


def review(output, state):
    if state.get("phase") == "executing":
        prepare_review(state)
    if not state.get("review_id"):
        state["review_id"] = secrets.token_urlsafe(24)
    for item in state["review"]:
        if not item.get("id"):
            item["id"] = secrets.token_urlsafe(24)
    save_state(output, state)
    if state["phase"] == "complete":
        publish_reports(output, state)
        print("Review complete. Reports saved in the output directory.")
        return
    data = review_data(state)
    template = (Path(__file__).resolve().parent / "review.html").read_text(encoding="utf-8")
    marker = '<script type="application/json" id="review-data">__REVIEW_DATA__</script>'
    if template.count(marker) != 1:
        raise ValueError("review template has an invalid data placeholder")
    encoded = json.dumps(data, ensure_ascii=True).replace("<", "\\u003c").replace(
        ">", "\\u003e").replace("&", "\\u0026")
    atomic_write(output / "review.html", template.replace(
        marker, '<script type="application/json" id="review-data">' + encoded + "</script>"))
    publish_machine_report(output, state)
    print(f"Open {output / 'review.html'} to grade, then import the downloaded grades.")


def review_data(state):
    redact = lambda value: blind(value, state["models"])
    cases = []
    for case in state["cases"]:
        responses = []
        grouped = {}
        for item in state["review"]:
            if item["case"] != case["id"]:
                continue
            model = item["model"]
            if model not in grouped:
                run = state["runs"][case["id"]][model]
                response = {"label": redact(item["label"]),
                            "answers": [redact(answer) for answer in run["answers"]],
                            "evidence": redact(run["evidence"]), "rubrics": []}
                grouped[model] = response
                responses.append(response)
            rubric = case["rubrics"][item["rubric"]]
            displayed = {"id": item["id"], "label": redact(rubric["label"]),
                         "prompt": redact(rubric["prompt"]), "evidence": rubric["evidence"]}
            key = json.dumps([item["case"], model, item["rubric"]])
            if key in state["grades"]:
                displayed["grade"] = state["grades"][key]
            grouped[model]["rubrics"].append(displayed)
        cases.append({"id": redact(case["id"]), "role": redact(case["role"]),
                      "turns": [redact(turn) for turn in case["turns"]],
                      "responses": responses, "deterministic_only": not case["rubrics"]})
    return {"version": 1, "review_id": state["review_id"],
            "demo": state["demo"], "cases": cases}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def publish_machine_report(output, state):
    if state.get("auto_grades"):
        from .local_grader import auto_scorecard
        atomic_write(output / "auto_scorecard.md", auto_scorecard(state["auto_grades"], state))


def publish_reports(output, state):
    """Rebuild derived reports from persisted state without running inference."""
    result = scorecard(state)
    atomic_write(output / "scorecard.md", result)
    publish_machine_report(output, state)
    return result


def import_grades(output, path):
    state = json.loads((output / "state.json").read_text(encoding="utf-8"))
    payload = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if (not isinstance(payload, dict) or type(payload.get("version")) is not int
            or payload["version"] != 1 or not isinstance(payload.get("review_id"), str)
            or not state.get("review_id") or payload["review_id"] != state["review_id"]
            or not isinstance(payload.get("grades"), dict)
            or state.get("phase") not in ("review", "complete")):
        raise ValueError("invalid grades file or review identity")
    items = state["review"]
    ids = [item.get("id") for item in items]
    grades = payload["grades"]
    if (any(not isinstance(key, str) or not key for key in ids)
            or len(set(ids)) != len(ids) or set(grades) != set(ids)
            or any(type(value) is not int or not 1 <= value <= 5
                   for value in grades.values())):
        raise ValueError("grades must contain exactly one integer from 1 to 5 per rubric")
    imported = {json.dumps([item["case"], item["model"], item["rubric"]]):
                grades[item["id"]] for item in items}
    if state["phase"] == "complete":
        if imported != state["grades"]:
            raise ValueError("review is complete; finalized grades cannot be changed")
        print("\n" + publish_reports(output, state))
        return
    state["grades"].update(imported)
    state["phase"] = "complete"
    if "auto_grades" in state:
        from .local_grader import refresh_agreement
        refresh_agreement(state)
    save_state(output, state)
    result = publish_reports(output, state)
    print("\n" + result)


def main():
    parser = argparse.ArgumentParser(description="Blind, human-graded model benchmark")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="execute cases, then review")
    run.add_argument("--demo", action="store_true", help="offline synthetic rehearsal")
    run.add_argument("--config", type=Path, help="live model configuration JSON")
    run.add_argument("--allow-live", action="store_true", help="explicitly allow live model calls")
    run.add_argument("--cases-dir", type=Path, default=DEFAULT_CASES)
    run.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    resume = sub.add_parser("resume", help="continue a saved review without rerunning")
    resume.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    grades = sub.add_parser("import-grades", help="import downloaded review grades")
    grades.add_argument("path", type=Path)
    grades.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    auto = sub.add_parser("autograde", help="add a local decision-model second opinion")
    auto.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    auto.add_argument("--grader", default="d3:latest")
    auto.add_argument("--ollama-bin", help="path to the Ollama executable")
    auto.add_argument("--max-chars", type=int, default=12000,
                      help="input budget per comparison; shrinks on context errors")
    graphs = sub.add_parser("graphs", help="render graphs for a completed run")
    graphs.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    doc = sub.add_parser("doctor", help="verify OpenCode execution")
    doc.add_argument("--model", required=True)
    doc.add_argument("--profile", choices=["talking", "coding"], default="talking")
    doc.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "run":
            execute_run(args)
        elif args.command == "resume":
            output = args.output_dir.resolve()
            with output_lock(output):
                state = json.loads((output / "state.json").read_text(encoding="utf-8"))
                review(output, state)
        elif args.command == "import-grades":
            output = args.output_dir.resolve()
            with output_lock(output):
                import_grades(output, args.path)
        elif args.command == "autograde":
            output = args.output_dir.resolve()
            with output_lock(output):
                state = json.loads((output / "state.json").read_text(encoding="utf-8"))
                from .local_grader import autograde
                _record, report = autograde(
                    output, state, model=args.grader, binary=args.ollama_bin,
                    max_chars=args.max_chars)
                print("\n" + report)
        elif args.command == "graphs":
            output = args.output_dir.resolve()
            with output_lock(output):
                state = json.loads((output / "state.json").read_text(encoding="utf-8"))
                if state.get("phase") != "complete":
                    raise ValueError("graphs require a completed review")
                from .graphs import render_graphs
                atomic_write(output / "graphs.html", render_graphs(state))
                print(f"Wrote {output / 'graphs.html'}")
        else:
            from .opencode_adapter import doctor
            result = doctor(args.model, profile=args.profile)
            print(json.dumps(result, indent=2) if args.json else str(result))
            return 0 if result.get("ok") else 1
    except (ValueError, OSError, RuntimeError, ImportError, json.JSONDecodeError) as exc:
        print(f"benchmark: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted. Review progress is saved.", file=sys.stderr)
        return 130
    return 0
