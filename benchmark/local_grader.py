"""Opt-in second opinion from a local Ollama decision model.

``d3`` is a zero-shot decision model, not a chat model: it answers questions
about supplied text and supports ``yes``/``no``, labelled choices, and ordered
levels. It cannot write a prose analysis. This pass therefore compares pairs of
responses and aggregates the choices into a ranking.

Machine results live under ``state["auto_grades"]`` and ``auto_scorecard.md``.
They never replace human grades and are only generated after human review is
complete, so model identities stay hidden while a person is grading.
"""

import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from .runner import atomic_write, blind, save_state


DEFAULT_GRADER = "d3:latest"
DEFAULT_MAX_CHARS = 14000
CHOICES = [("A", "the first response"), ("B", "the second response")]
ANSI = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]")


class GraderError(RuntimeError):
    """The local decision model is unavailable or returned unusable output."""


class ContextLengthError(GraderError):
    """The supplied text exceeds the model's available context."""


def _clean(text):
    return ANSI.sub("", text or "")


def _binary(path=None):
    if path:
        executable = Path(path)
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise GraderError(f"Ollama binary is not executable: {path}")
        return executable.resolve()
    found = shutil.which("ollama")
    if not found:
        raise GraderError("ollama not found on PATH; start Ollama or pass --ollama-bin")
    return Path(found).resolve()


def _version(binary):
    result = subprocess.run([str(binary), "--version"], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=30, check=False)
    if result.returncode:
        raise GraderError(f"ollama --version failed (exit {result.returncode})")
    return _clean(result.stdout).strip().removeprefix("ollama version is ").strip()


def _installed_models(binary):
    result = subprocess.run([str(binary), "list"], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=30, check=False)
    if result.returncode:
        raise GraderError(f"ollama list failed (exit {result.returncode})")
    names = []
    for line in _clean(result.stdout).splitlines()[1:]:
        line = line.strip()
        if line:
            names.append(line.split()[0])
    return names


def _resolve_model(model, names):
    if model in names:
        return model
    if ":" not in model:
        matches = [name for name in names if name.split(":")[0] == model]
        if len(matches) == 1:
            return matches[0]
    available = ", ".join(sorted(names)) or "none"
    raise GraderError(f"{model} is not installed locally; refusing to pull it. "
                      f"Installed models: {available}")


def _extract_json(text):
    for line in reversed(_clean(text).splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    raise GraderError("decision model returned no JSON object")


class OllamaDecision:
    """Run one ``ollama run --ask --choice`` decision and parse its JSON."""

    def __init__(self, model, binary=None, timeout=180):
        self.model = model
        self.binary = _binary(binary)
        self.timeout = timeout

    def ask(self, question, text, choices=CHOICES):
        labels = [label for label, _ in choices]
        command = [str(self.binary), "run", self.model, "--ask", question]
        for label, description in choices:
            command += ["--choice", f"{label}={description}"]
        command += ["--format", "json"]
        try:
            result = subprocess.run(command, input=text, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace",
                                    timeout=self.timeout, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GraderError(f"decision model could not run: {exc}") from None
        if result.returncode:
            detail = [line for line in _clean(result.stderr).splitlines() if line.strip()]
            reason = detail[-1] if detail else "no diagnostic output"
            combined = (_clean(result.stderr) + "\n" + _clean(result.stdout)).lower()
            if "context length" in combined or "longer than" in combined:
                raise ContextLengthError(f"decision model context exceeded: {reason}")
            raise GraderError(f"decision model failed (exit {result.returncode}): {reason}")
        answer = _extract_json(result.stdout).get("answers", {}).get("q1")
        if not isinstance(answer, dict) or answer.get("type") != "choice":
            raise GraderError("decision model did not return a choice")
        choice = answer.get("choice")
        if choice not in labels:
            raise GraderError(f"decision model returned an unknown choice: {choice!r}")
        probabilities = answer.get("probabilities")
        confidence = answer.get("confidence")
        return {"choice": choice,
                "probabilities": probabilities if isinstance(probabilities, dict) else {},
                "confidence": confidence if isinstance(confidence, (int, float)) else None}


def probe(model=DEFAULT_GRADER, binary=None):
    """Verify the model is installed and answers a choice without pulling."""
    executable = _binary(binary)
    names = _installed_models(executable)
    resolved = _resolve_model(model, names)
    version = _version(executable)
    OllamaDecision(resolved, executable).ask(
        "Does this text contain words?",
        "hello world",
        [("A", "it contains words"), ("B", "it does not")])
    return {"ok": True, "model": resolved, "version": version, "binary": str(executable)}


def _clip(text, limit):
    if len(text) <= limit:
        return text, False
    head = max(int(limit * 0.7), 1)
    tail = max(limit - head, 0)
    return text[:head] + "\n...[truncated]...\n" + (text[-tail:] if tail else ""), True


def _side(run, rubric, models):
    parts = [f"RESPONSE TURN {index + 1}:\n{blind(answer, models)}"
             for index, answer in enumerate(run["answers"])]
    if rubric["evidence"]:
        parts.append("EVIDENCE:\n" + blind(run.get("evidence") or "Trace unverified.", models))
    return "\n\n".join(parts)


def question_for(rubric, models):
    prompt = blind(rubric["prompt"], models)
    if len(prompt) > 600:
        prompt = prompt[:597] + "..."
    return "Which response better satisfies this rubric: " + prompt


def pair_text(case, run_a, run_b, rubric, models, max_chars=DEFAULT_MAX_CHARS):
    """Build a blinded A/B comparison within a character budget.

    The rubric is always kept intact. Each response side gets an equal share of
    the remaining budget, and evidence appears only for evidence rubrics.
    """
    shared = "\n\n".join(f"PROMPT {index + 1}:\n{blind(turn, models)}"
                         for index, turn in enumerate(case["turns"]))
    rubric_text = "RUBRIC:\n" + blind(rubric["prompt"], models)
    overhead = len(shared) + len(rubric_text) + 64
    budget = max(max_chars - overhead, 400)
    half = max(budget // 2, 200)
    side_a, truncated_a = _clip(_side(run_a, rubric, models), half)
    side_b, truncated_b = _clip(_side(run_b, rubric, models), half)
    text = (f"{shared}\n\nRESPONSE A:\n{side_a}\n\nRESPONSE B:\n{side_b}"
            f"\n\n{rubric_text}")
    return text, truncated_a or truncated_b


def _human_means(state, case, models):
    grades = state.get("grades", {})
    means = {}
    for model in models:
        values = [grades[json.dumps([case["id"], model, index])]
                  for index in range(len(case["rubrics"]))
                  if json.dumps([case["id"], model, index]) in grades]
        if values:
            means[model] = sum(values) / len(values)
    return means


def _rank(values):
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index
        while end + 1 < len(order) and values[order[end + 1]] == values[order[index]]:
            end += 1
        rank = (index + end) / 2 + 1
        for position in range(index, end + 1):
            ranks[order[position]] = rank
        index = end + 1
    return ranks


def _spearman(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    rx, ry = _rank(xs), _rank(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    numerator = sum((x - mx) * (y - my) for x, y in zip(rx, ry))
    left = sum((x - mx) ** 2 for x in rx) ** 0.5
    right = sum((y - my) ** 2 for y in ry) ** 0.5
    if not left or not right:
        return None
    return numerator / (left * right)


def _agreement(state, standings):
    cases = {}
    for case in state["cases"]:
        stats = standings.get(case["id"], {})
        means = _human_means(state, case, stats)
        common = [model for model in stats if model in means]
        rho = _spearman([stats[model]["score"] for model in common],
                        [means[model] for model in common]) if len(common) >= 2 else None
        cases[case["id"]] = {"n": len(common), "rho": rho}
    rhos = [entry["rho"] for entry in cases.values() if entry["rho"] is not None]
    return {"cases": cases,
            "overall": {"cases": len(rhos),
                        "mean_rho": sum(rhos) / len(rhos) if rhos else None}}


def _compare(decide, case, runs, first, second, rubric, models, budget):
    question = question_for(rubric, models)
    text, truncated = pair_text(case, runs[first], runs[second], rubric, models, budget)
    forward = decide(question, text, CHOICES)
    text, reverse_truncated = pair_text(
        case, runs[second], runs[first], rubric, models, budget)
    reverse = decide(question, text, CHOICES)
    forward_winner = first if forward["choice"] == "A" else second
    reverse_winner = second if reverse["choice"] == "A" else first
    if forward_winner == reverse_winner:
        outcome = "a" if forward_winner == first else "b"
    else:
        outcome = "tie"
    return {
        "case": case["id"], "rubric": rubric["label"], "a": first, "b": second,
        "outcome": outcome, "forward": forward, "reverse": reverse,
        "truncated": truncated or reverse_truncated, "budget": budget,
    }


def autograde(output, state, model=DEFAULT_GRADER, binary=None,
              decide=None, max_chars=DEFAULT_MAX_CHARS):
    """Compare completed runs pairwise and save a separate machine report."""
    if state.get("phase") != "complete":
        raise GraderError("human review must be complete before autograde reveals identities; "
                          "run `resume` first")
    if max_chars < 600:
        raise GraderError("max_chars must be at least 600")

    if decide is None:
        info = probe(model, binary)
        resolved = info["model"]
        version = info["version"]
        decide = OllamaDecision(resolved, info["binary"]).ask
    else:
        resolved = model
        version = "test"

    models = state["models"]
    comparisons = []
    standings = {}
    budgets = {}
    truncated_comparisons = 0
    for case in state["cases"]:
        if not case["rubrics"]:
            standings[case["id"]] = {}
            continue
        runs = state["runs"].get(case["id"], {})
        available = [name for name in models
                     if runs.get(name, {}).get("status") == "ok"]
        if len(available) < 2:
            standings[case["id"]] = {}
            continue
        stats = {name: {"wins": 0, "losses": 0, "ties": 0, "games": 0}
                 for name in available}
        case_budget = max_chars
        for rubric in case["rubrics"]:
            for left in range(len(available)):
                for right in range(left + 1, len(available)):
                    first, second = available[left], available[right]
                    while True:
                        try:
                            entry = _compare(decide, case, runs,
                                             first, second, rubric, models, case_budget)
                            break
                        except ContextLengthError:
                            if case_budget <= 800:
                                raise
                            case_budget = max(800, case_budget // 2)
                    truncated_comparisons += int(entry["truncated"])
                    if entry["outcome"] == "a":
                        winner, loser = first, second
                    elif entry["outcome"] == "b":
                        winner, loser = second, first
                    else:
                        winner = loser = None
                    if winner:
                        stats[winner]["wins"] += 1
                        stats[loser]["losses"] += 1
                    else:
                        stats[first]["ties"] += 1
                        stats[second]["ties"] += 1
                    stats[first]["games"] += 1
                    stats[second]["games"] += 1
                    comparisons.append(entry)
        budgets[case["id"]] = case_budget
        for entry in stats.values():
            entry["score"] = entry["wins"] - entry["losses"]
        ranked = sorted(stats, key=lambda name: (
            -stats[name]["score"], -stats[name]["wins"], stats[name]["losses"], name))
        for position, name in enumerate(ranked, 1):
            stats[name]["rank"] = position
        standings[case["id"]] = stats

    record = {
        "version": 1,
        "grader": {"model": resolved, "ollama": version},
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="seconds"),
        "comparisons": comparisons,
        "standings": standings,
        "agreement": _agreement(state, standings),
        "limits": {"max_chars": max_chars,
                   "budget_by_case": budgets,
                   "truncated_comparisons": truncated_comparisons},
        "note": ("Machine second opinion. Pairwise choices from a zero-shot decision "
                 "model, not human grades."),
    }
    state["auto_grades"] = record
    save_state(output, state)
    report = auto_scorecard(record, state)
    atomic_write(output / "auto_scorecard.md", report)
    return record, report


def auto_scorecard(record, state):
    lines = [
        "# Local second opinion",
        "",
        f"Grader: `{record['grader']['model']}` on Ollama {record['grader']['ollama']}. "
        "Zero-shot decision model; pairwise preferences only, not a human grade.",
        f"Generated: {record['generated_at']}",
        f"Comparisons: {len(record['comparisons'])} (each run in both orders). "
        f"Truncated comparisons: {record['limits']['truncated_comparisons']}.",
        "",
        "Human grades remain the benchmark result. This report is supplementary.",
        "",
    ]
    for case in state["cases"]:
        stats = record["standings"].get(case["id"], {})
        lines += [f"## {case['id']} ({case['role']})", ""]
        if not stats:
            lines += ["Deterministic-only case; no subjective rubrics to compare."
                      if not case["rubrics"] else
                      "Not enough completed runs to compare.", ""]
            continue
        human = _human_means(state, case, stats)
        header = "| Rank | Model | W | L | T | Score |" + (" Human mean |" if human else "")
        separator = "|---:|---|---:|---:|---:|---:|" + ("---:|" if human else "")
        lines += [header, separator]
        for name in sorted(stats, key=lambda item: stats[item]["rank"]):
            entry = stats[name]
            row = (f"| {entry['rank']} | {name} | {entry['wins']} | {entry['losses']} "
                   f"| {entry['ties']} | {entry['score']} |")
            if human:
                mean = human.get(name)
                row += f" {mean:.1f} |" if mean is not None else " - |"
            lines.append(row)
        agreement = record["agreement"]["cases"].get(case["id"], {})
        if agreement.get("rho") is not None:
            lines += ["", f"Spearman vs human mean: {agreement['rho']:.2f} "
                          f"(n={agreement['n']})."]
        elif human:
            lines += ["", "Spearman unavailable (too few comparable models or no variance)."]
        lines.append("")
    overall = record["agreement"]["overall"]
    if overall.get("mean_rho") is not None:
        lines += [f"Overall mean Spearman: {overall['mean_rho']:.2f} "
                  f"across {overall['cases']} cases.", ""]
    lines += [
        "## Caveats",
        "",
        "- d3 is a 4.8B zero-shot decision model, not a chat model. It makes "
        "pairwise choices, not prose analysis.",
        "- Both orders are run; when the orders disagree, the pair is recorded as "
        "a tie (position bias).",
        "- Absolute 1-5 machine scores are deliberately not produced; probes "
        "showed upward miscalibration.",
        "- Inputs are blinded and truncated to the model's 4096-token context; "
        "truncation is counted above.",
        "",
    ]
    return "\n".join(lines)
