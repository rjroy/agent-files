#!/usr/bin/env python3
"""Preview or safely move legacy lore documents into current storage zones."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from ensure_local import ensure_local
from legacy_html import convert_html


@dataclass(frozen=True)
class Move:
    source: Path
    destination: Path
    legacy_spec: bool = False
    backup: Path | None = None
    converted_markdown: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Plan:
    root: Path
    moves: tuple[Move, ...]
    edits: tuple[tuple[Path, bytes, bytes], ...]
    unresolved: tuple[str, ...]
    tracked_local: tuple[Path, ...]
    warnings: tuple[str, ...] = ()


FLAT_DIRECTORY_MAP = {
    "specs": ("work/intents", True),
    "intents": ("work/intents", False),
    "brainstorm": ("work/brainstorm", False),
    "design": ("work/design", False),
    "research": ("work/research", False),
    "retros": ("work/retros", False),
    "issues": ("work/issues", False),
    "ideas": ("work/ideas", False),
    "validation": ("work/validation", False),
    "stubs": ("work/stubs", False),
    "diagrams": ("work/diagrams", False),
    "excavations": ("work/excavations", False),
    "plans": ("local/plans", False),
    "tasks": ("local/tasks", False),
    "notes": ("local/notes", False),
}
WORK_DIRECTORY_MAP = {
    "specs": ("work/intents", True),
    "plans": ("local/plans", False),
    "tasks": ("local/tasks", False),
    "notes": ("local/notes", False),
}
PRESERVED_ROOT_DIRS = {"work", "reference", "learned", "local"}
PRESERVED_ROOT_FILES = {
    "heartbeat.md",
    "lore-agents.md",
    "lore-config.md",
    "vision.md",
}


def _requires_local_storage(move: Move) -> bool:
    return ".lore/local/" in move.destination.as_posix() or move.backup is not None


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def _git_root(root: Path) -> bool:
    return _git(root, "rev-parse", "--show-toplevel").returncode == 0


def _check_no_symlink_chain(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes project root: {path}") from exc
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"refusing symlink path: {current}")


def _source_files(root: Path, source: Path) -> list[Path]:
    _check_no_symlink_chain(root, source)
    if not source.exists():
        return []
    if not source.is_dir():
        raise ValueError(f"source is not a directory: {source}")
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(source, followlinks=False):
        here = Path(current)
        for name in list(dirnames):
            entry = here / name
            if entry.is_symlink():
                raise ValueError(f"refusing symlink directory: {entry}")
        for name in filenames:
            entry = here / name
            if entry.is_symlink() or not entry.is_file():
                raise ValueError(f"refusing non-regular or symlink file: {entry}")
            files.append(entry)
    return sorted(files)


def _scan_lore_text(root: Path) -> list[Path]:
    lore = root / ".lore"
    _check_no_symlink_chain(root, lore)
    if not lore.exists():
        return []
    result: list[Path] = []
    for current, dirnames, filenames in os.walk(lore, followlinks=False):
        here = Path(current)
        relative_here = here.relative_to(lore)
        if relative_here == Path("local"):
            dirnames[:] = [name for name in dirnames if name != "migration-backups"]
        for name in list(dirnames):
            entry = here / name
            if entry.is_symlink():
                raise ValueError(
                    f"refusing symlink directory while scanning lore: {entry}"
                )
        for name in filenames:
            entry = here / name
            if entry.suffix.lower() not in {".md", ".html", ".htm"}:
                continue
            if entry.is_symlink() or not entry.is_file():
                raise ValueError(f"refusing unsafe lore document: {entry}")
            result.append(entry)
    return result


def _external_references(root: Path, mapping: dict[str, str]) -> list[str]:
    """Find resolvable or literal references outside .lore without editing them."""
    ignored = {
        ".git",
        ".lore",
        ".beads",
        ".venv",
        "node_modules",
        "vendor",
        "dist",
        "build",
    }
    findings: set[str] = set()
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        here = Path(current)
        dirnames[:] = [
            name
            for name in dirnames
            if name not in ignored and not (here / name).is_symlink()
        ]
        for name in filenames:
            document = here / name
            if document.suffix.lower() not in {".md", ".html", ".htm"}:
                continue
            if document.is_symlink() or not document.is_file():
                continue
            try:
                text = document.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            _rewritten, changed = _rewrite_document(document, text, root, mapping)
            for source in mapping:
                if source in text or source in changed:
                    findings.add(
                        f"{document.relative_to(root)} refers to moved path {source}; "
                        "external documents were not edited"
                    )
    return sorted(findings)


def _source_mapping(root: Path) -> tuple[list[Move], dict[str, str], tuple[str, ...]]:
    lore = root / ".lore"
    moves: list[Move] = []
    mappings: dict[str, str] = {}
    reserved: dict[Path, Path] = {}
    sources: list[tuple[Path, Path, bool]] = []
    for directory, (destination, is_spec) in FLAT_DIRECTORY_MAP.items():
        sources.append((lore / directory, lore / destination, is_spec))
    for directory, (destination, is_spec) in WORK_DIRECTORY_MAP.items():
        sources.append((lore / "work" / directory, lore / destination, is_spec))

    in_git = _git_root(root)
    for source_dir, destination_dir, legacy_spec in sources:
        for source in _source_files(root, source_dir):
            relative = source.relative_to(source_dir)
            destination = destination_dir / relative
            converted_markdown: str | None = None
            backup: Path | None = None
            warnings: tuple[str, ...] = ()
            if source.suffix.lower() in {".html", ".htm"}:
                try:
                    conversion = convert_html(
                        source.read_text(encoding="utf-8"), source.as_posix()
                    )
                except UnicodeDecodeError as exc:
                    raise ValueError(
                        f"cannot safely convert non-UTF-8 HTML before moving: {source}"
                    ) from exc
                converted_markdown = conversion.markdown
                if legacy_spec:
                    converted_markdown = _legacy_frontmatter(
                        converted_markdown, source.with_suffix(".md")
                    )
                warnings = conversion.warnings
                destination = destination.with_suffix(".md")
                backup = lore / "local/migration-backups" / source.relative_to(lore)
                _check_no_symlink_chain(root, backup.parent)
                if backup.exists() or backup.is_symlink() or backup in reserved:
                    raise ValueError(f"HTML backup collision; no files moved: {backup}")
                if (
                    in_git
                    and _git(
                        root,
                        "ls-files",
                        "--error-unmatch",
                        "--",
                        f":(literal){backup.relative_to(root).as_posix()}",
                    ).returncode
                    == 0
                ):
                    raise ValueError(f"HTML backup collision in Git index: {backup}")
            _check_no_symlink_chain(root, destination.parent)
            if (
                destination.exists()
                or destination.is_symlink()
                or destination in reserved
            ):
                raise ValueError(
                    f"destination collision; no files moved: {destination}"
                )
            if in_git:
                indexed = _git(
                    root,
                    "ls-files",
                    "--error-unmatch",
                    "--",
                    f":(literal){destination.relative_to(root).as_posix()}",
                )
                if indexed.returncode == 0:
                    raise ValueError(
                        "destination collision in Git index; no files moved: "
                        f"{destination}"
                    )
            move = Move(
                source, destination, legacy_spec, backup, converted_markdown, warnings
            )
            moves.append(move)
            reserved[destination] = source
            if backup is not None:
                if backup in reserved or backup.exists() or backup.is_symlink():
                    raise ValueError(f"HTML backup collision; no files moved: {backup}")
                reserved[backup] = source
            old = source.relative_to(root).as_posix()
            new = destination.relative_to(root).as_posix()
            mappings[old] = new
    unknowns: list[str] = []
    if lore.is_dir():
        for entry in sorted(lore.iterdir()):
            if entry.is_dir() and entry.name not in PRESERVED_ROOT_DIRS | set(
                FLAT_DIRECTORY_MAP
            ):
                unknowns.append(
                    f"unmapped legacy directory preserved: {entry.relative_to(root)}"
                )
            elif entry.is_file() and entry.name not in PRESERVED_ROOT_FILES:
                unknowns.append(
                    f"unmapped legacy file preserved: {entry.relative_to(root)}"
                )
    return moves, mappings, tuple(unknowns)


_FM_FIELD = re.compile(r"^([A-Za-z0-9_-]+)\s*:")
_MD_LINK = re.compile(r"(!?\[[^\]]*\]\()([^\s)]*)([^)]*\))")
_HTML_LINK = re.compile(r"(?i)(\b(?:href|src)\s*=\s*)([\"'])([^\"']+)([\"'])")
_CODE_SPAN = re.compile(r"(?s)(```.*?```|~~~.*?~~~|`[^`\n]*`)")
_HTML_META = re.compile(r"(?is)<meta\b[^>]*>")
_HTML_ATTRIBUTE = re.compile(r"(?i)(\b[A-Za-z0-9_-]+\s*=\s*)([\"'])([^\"']*)([\"'])")
_PATH_FIELDS = {"related", "source", "fg-sources", "migrated-from"}


def _is_legacy_spec_path(path: str) -> bool:
    return path.startswith((".lore/specs/", ".lore/work/specs/"))


def _link_target(document: Path, raw: str, root: Path) -> tuple[Path | None, str]:
    if raw.startswith(("http://", "https://", "mailto:", "#", "//")):
        return None, raw
    without_fragment, fragment_marker, fragment = raw.partition("#")
    path_part, query_marker, query = without_fragment.partition("?")
    suffix = (f"?{query}" if query_marker else "") + (
        f"#{fragment}" if fragment_marker else ""
    )
    if not path_part:
        return None, suffix
    if path_part.startswith(".lore/"):
        resolved = root / path_part
    else:
        resolved = document.parent / path_part
    try:
        relative = resolved.resolve(strict=False).relative_to(root)
    except ValueError:
        return None, raw
    return root / relative, suffix


def _rewrite_document(
    document: Path,
    text: str,
    root: Path,
    mapping: dict[str, str],
    destination_document: Path | None = None,
    unresolved_links: set[str] | None = None,
) -> tuple[str, set[str]]:
    destination_document = destination_document or document
    updated = text
    changed: set[str] = set()
    # Rewrite exact project-root lore paths only in known path-bearing metadata.
    lines = updated.splitlines(keepends=True)
    if lines and lines[0].rstrip("\r\n") == "---":
        closing = next(
            (i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"),
            None,
        )
        if closing is not None:
            field: str | None = None
            for index in range(1, closing):
                match = _FM_FIELD.match(lines[index])
                if match:
                    field = match.group(1)
                elif lines[index].strip() and not lines[index].lstrip().startswith("-"):
                    field = None
                if field in _PATH_FIELDS:
                    for old, new in mapping.items():
                        # Under the reference policy, old plans/notes/tasks are
                        # not durable source authority. Only legacy spec
                        # provenance is remapped; other fg-sources entries are
                        # left for explicit field-guide reassessment.
                        if field == "fg-sources" and not _is_legacy_spec_path(old):
                            continue
                        # Path values are YAML scalars/list entries; replace exact
                        # path tokens, not arbitrary prose or code examples.
                        pattern = re.compile(
                            rf"(?<![A-Za-z0-9_./-]){re.escape(old)}(?=$|[\s,\]}}\"'])"
                        )
                        if pattern.search(lines[index]):
                            lines[index] = pattern.sub(new, lines[index])
                            changed.add(old)
            updated = "".join(lines)

    def rewrite_link(match: re.Match[str], prefix: str, raw: str, suffix: str) -> str:
        target, url_suffix = _link_target(document, raw, root)
        if target is None:
            if (
                document != destination_document
                and not raw.startswith(("http://", "https://", "mailto:", "#", "//"))
                and unresolved_links is not None
            ):
                unresolved_links.add(
                    f"{document}: cannot rebase relative link {raw!r} "
                    "outside project root"
                )
            return match.group(0)
        old = target.relative_to(root).as_posix()
        moved_target = mapping.get(old)
        source_moved = document != destination_document
        if moved_target is None and not source_moved:
            return match.group(0)
        if moved_target is None:
            if not target.exists():
                if unresolved_links is not None:
                    unresolved_links.add(
                        f"{document}: cannot rebase unresolved relative link {raw!r}"
                    )
                return match.group(0)
            new_path = target
        else:
            new_path = root / moved_target
            changed.add(old)
        if raw.startswith(".lore/"):
            rewritten_path = new_path.relative_to(root).as_posix()
        else:
            rewritten_path = os.path.relpath(
                new_path, destination_document.parent
            ).replace(os.sep, "/")
        return f"{prefix}{rewritten_path}{url_suffix}{suffix}"

    def rewrite_meta(match: re.Match[str]) -> str:
        tag = match.group(0)
        attributes = {
            attribute.group(1).strip().split("=", 1)[0].lower(): attribute
            for attribute in _HTML_ATTRIBUTE.finditer(tag)
            if attribute.group(1).strip().split("=", 1)[0].lower()
            in {
                "name",
                "content",
            }
        }
        name_attr = attributes.get("name")
        content_attr = attributes.get("content")
        if name_attr is None or content_attr is None:
            return tag
        field = name_attr.group(3).lower()
        if field not in _PATH_FIELDS:
            return tag
        content = content_attr.group(3)
        for old, new in mapping.items():
            if field == "fg-sources" and not _is_legacy_spec_path(old):
                continue
            pattern = re.compile(
                rf"(?<![A-Za-z0-9_./-]){re.escape(old)}(?=$|[\s,\]}}\"'])"
            )
            if pattern.search(content):
                content = pattern.sub(new, content)
                changed.add(old)
        if content == content_attr.group(3):
            return tag
        start, end = content_attr.span(3)
        return tag[:start] + content + tag[end:]

    # Restrict link rewriting to prose; fenced and inline code may intentionally
    # show historical path strings and are not navigation references.
    chunks = _CODE_SPAN.split(updated)
    for index in range(0, len(chunks), 2):
        prose = _MD_LINK.sub(
            lambda m: rewrite_link(m, m.group(1), m.group(2), m.group(3)),
            chunks[index],
        )
        chunks[index] = _HTML_LINK.sub(
            lambda m: rewrite_link(m, m.group(1) + m.group(2), m.group(3), m.group(4)),
            prose,
        )
        chunks[index] = _HTML_META.sub(rewrite_meta, chunks[index])
    updated = "".join(chunks)
    return updated, changed


def _legacy_frontmatter(text: str, source: Path) -> str:
    if source.suffix.lower() != ".md" or not text.startswith(("---\n", "---\r\n")):
        return text
    newline = "\r\n" if text.startswith("---\r\n") else "\n"
    lines = text.splitlines(keepends=True)
    close = next(
        (i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"), None
    )
    if close is None or any(
        line.startswith("legacy_source_type:") for line in lines[1:close]
    ):
        return text
    lines.insert(close, f"legacy_source_type: spec{newline}")
    return "".join(lines)


def _assert_editable_reference(path: Path) -> None:
    try:
        mode = path.stat().st_mode
    except OSError as exc:
        raise ValueError(f"cannot preflight reference edit {path}: {exc}") from exc
    # Check mode bits as well as effective access: privileged processes may be
    # able to write a deliberately read-only file, but migration should not.
    writable = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    if not stat.S_ISREG(mode) or not mode & writable:
        raise ValueError(f"reference file is not writable: {path}")
    if not os.access(path, os.W_OK):
        raise ValueError(f"reference file is not writable: {path}")


def _clean_tracked_paths(root: Path, paths: set[Path]) -> set[Path]:
    if not _git_root(root):
        return set()
    tracked: list[Path] = []
    for path in sorted(paths):
        relative = path.relative_to(root).as_posix()
        literal = f":(literal){relative}"
        listed = _git(root, "ls-files", "--error-unmatch", "--", literal)
        if listed.returncode != 0:
            continue
        # Check both sides of the index separately. `git diff HEAD` alone misses
        # staged-only changes when the worktree has been restored to HEAD.
        index_matches_head = _git(
            root, "diff", "--cached", "--quiet", "HEAD", "--", literal
        )
        worktree_matches_index = _git(root, "diff", "--quiet", "--", literal)
        if index_matches_head.returncode != 0 or worktree_matches_index.returncode != 0:
            raise ValueError(
                f"tracked source has staged or unstaged changes (including "
                f"reference files): {relative}"
            )
        tracked.append(path)
    return set(tracked)


def build_plan(project_root: Path) -> Plan:
    root = project_root.resolve()
    if not root.is_dir():
        raise ValueError(f"project root is not a directory: {project_root}")
    moves, mapping, warnings = _source_mapping(root)
    if not moves:
        return Plan(root, (), (), (), (), warnings)
    edits: list[tuple[Path, bytes, bytes]] = []
    unresolved_mentions: set[str] = set()
    unresolved_links: set[str] = set()
    move_destinations = {move.source: move.destination for move in moves}
    moves_by_source = {move.source: move for move in moves}
    for document in _scan_lore_text(root):
        move = moves_by_source.get(document)
        if move is not None and move.converted_markdown is not None:
            original = move.converted_markdown
            original_bytes = original.encode("utf-8")
        else:
            try:
                original_bytes = document.read_bytes()
                original = original_bytes.decode("utf-8")
            except UnicodeDecodeError:
                continue
            if (
                move is not None
                and move.legacy_spec
                and move.destination.suffix.lower() == ".md"
            ):
                original = _legacy_frontmatter(original, move.destination)
        destination_document = move_destinations.get(document, document)
        replacement, changed = _rewrite_document(
            document, original, root, mapping, destination_document, unresolved_links
        )
        for old in mapping:
            if old in original and old not in changed:
                unresolved_mentions.add(old)
        replacement_bytes = replacement.encode("utf-8")
        if replacement_bytes != original_bytes:
            edits.append((destination_document, original_bytes, replacement_bytes))

    unresolved = tuple(
        f"{source}: literal reference found but not safely rewritten; review manually"
        for source in sorted(unresolved_mentions)
    )
    unresolved += tuple(sorted(unresolved_links))
    external = tuple(_external_references(root, mapping))
    move_sources = {move.source for move in moves}
    destination_to_source = {move.destination: move.source for move in moves}
    moves_by_destination = {move.destination: move for move in moves}
    affected = set(move_sources)
    for path, _original, _replacement in edits:
        source_path = destination_to_source.get(path, path)
        affected.add(source_path)
        move = moves_by_destination.get(path)
        # A normal rename carries the source mode to the edit destination. HTML
        # conversion creates a fresh Markdown output and leaves the source as a
        # read-only byte backup, so only its new output needs checking.
        if move is None or move.converted_markdown is None:
            _assert_editable_reference(source_path)
    tracked_paths = _clean_tracked_paths(root, affected)
    tracked = tuple(
        move.source
        for move in moves
        if move.source in tracked_paths
        and ".lore/local/" in move.destination.relative_to(root).as_posix()
    )
    move_warnings = tuple(
        f"{move.source.relative_to(root)}: {warning}"
        for move in moves
        for warning in move.warnings
    )
    return Plan(
        root,
        tuple(moves),
        tuple(edits),
        unresolved + external,
        tracked,
        warnings + move_warnings,
    )


def _print_plan(plan: Plan, apply: bool) -> None:
    mode = "APPLY" if apply else "PREVIEW (no files changed)"
    print(f"{mode}: {plan.root}")
    if not plan.moves:
        print("No legacy files found; already migrated or nothing to do.")
    for move in plan.moves:
        kind = (
            "legacy spec (history; not newly authored intent)"
            if move.legacy_spec
            else "local context"
        )
        tracked = (
            " [tracked; index removal requires --untrack]"
            if move.source in plan.tracked_local
            else ""
        )
        print(
            "MOVE "
            f"{move.source.relative_to(plan.root)} -> "
            f"{move.destination.relative_to(plan.root)} ({kind}){tracked}"
        )
        if move.backup is not None:
            print(
                f"CONVERT HTML -> Markdown {move.source.relative_to(plan.root)} -> "
                f"{move.destination.relative_to(plan.root)}; original backup: "
                f"{move.backup.relative_to(plan.root)}"
            )
    for document, _old, _new in plan.edits:
        print(f"UPDATE REFERENCES {document.relative_to(plan.root)}")
    for warning in plan.warnings:
        print(f"WARNING: {warning}")
    for warning in plan.unresolved:
        print(f"REVIEW: {warning}")
    if plan.tracked_local:
        print(
            "Tracked local files become ignored. Apply requires --untrack to "
            "stage only their index removals; file bytes remain in .lore/local/."
        )
    if any(_requires_local_storage(move) for move in plan.moves):
        print(
            "Local destinations are Git-ignored and machine-specific; "
            "collaborators may not have these files."
        )
    if not apply and plan.moves:
        print(
            "After reviewing this preview, rerun with --apply. Use --untrack "
            "only to authorize tracked local-source index removals."
        )


def apply_plan(plan: Plan, untrack: bool = False) -> None:
    if plan.tracked_local and not untrack:
        paths = ", ".join(
            path.relative_to(plan.root).as_posix() for path in plan.tracked_local
        )
        raise ValueError(
            f"tracked local sources require explicit --untrack approval: {paths}"
        )
    # Setup/ignore is deliberately after all preflight checks and before moves.
    if any(_requires_local_storage(move) for move in plan.moves):
        ensure_local(plan.root)
    started: list[Move] = []
    changed_refs: list[tuple[Path, bytes]] = []
    staged_actions: list[tuple[str, str]] = []
    try:
        for move in plan.moves:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            started.append(move)
            if move.converted_markdown is not None and move.backup is not None:
                move.backup.parent.mkdir(parents=True, exist_ok=True)
                with (
                    move.source.open("rb") as original,
                    move.backup.open("xb") as backup,
                ):
                    shutil.copyfileobj(original, backup)
                shutil.copystat(move.source, move.backup)
                with move.destination.open(
                    "x", encoding="utf-8", newline=""
                ) as converted:
                    converted.write(move.converted_markdown)
                move.source.unlink()
            else:
                os.replace(move.source, move.destination)
        for document, original, replacement in plan.edits:
            changed_refs.append((document, original))
            document.write_bytes(replacement)
        if untrack and plan.tracked_local:
            relative_paths = [
                source.relative_to(plan.root).as_posix()
                for source in plan.tracked_local
            ]
            staged_actions = [
                (
                    relative,
                    next(
                        move.destination.relative_to(plan.root).as_posix()
                        for move in plan.moves
                        if move.source == source
                    ),
                )
                for source, relative in zip(
                    plan.tracked_local, relative_paths, strict=True
                )
            ]
            literal_paths = [f":(literal){path}" for path in relative_paths]
            result = _git(plan.root, "rm", "--cached", "--quiet", "--", *literal_paths)
            if result.returncode != 0:
                raise ValueError(
                    "could not stage the exact tracked local index removals: "
                    f"{result.stderr.strip()}"
                )
    except Exception as failure:
        recovery_errors: list[str] = []
        for document, original in reversed(changed_refs):
            try:
                document.write_bytes(original)
            except Exception as rollback_error:
                recovery_errors.append(
                    f"could not restore reference {document}: {rollback_error}"
                )
        for move in reversed(started):
            if move.converted_markdown is not None and move.backup is not None:
                try:
                    if not move.source.exists() and move.backup.exists():
                        move.source.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(move.backup, move.source)
                except Exception as rollback_error:
                    recovery_errors.append(
                        f"could not restore source {move.source}: {rollback_error}"
                    )
                try:
                    if move.backup.exists() and move.source.exists():
                        move.backup.unlink()
                except Exception as rollback_error:
                    recovery_errors.append(
                        "could not remove migration backup "
                        f"{move.backup}: {rollback_error}"
                    )
                try:
                    if move.destination.exists():
                        move.destination.unlink()
                except Exception as rollback_error:
                    recovery_errors.append(
                        "could not remove destination "
                        f"{move.destination}: {rollback_error}"
                    )
            elif move.destination.exists():
                try:
                    move.source.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(move.destination, move.source)
                except Exception as rollback_error:
                    recovery_errors.append(
                        f"could not restore source {move.source}: {rollback_error}"
                    )
        if recovery_errors:
            details = "; ".join(recovery_errors)
            raise ValueError(f"{failure}; rollback incomplete: {details}") from failure
        raise
    for relative, destination in staged_actions:
        print(f"STAGED INDEX REMOVAL {relative}; file bytes remain at {destination}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_root", type=Path, help="project root containing .lore/"
    )
    parser.add_argument(
        "--apply", action="store_true", help="perform the reviewed migration"
    )
    parser.add_argument(
        "--untrack",
        action="store_true",
        help="explicitly authorize staged Git index removals for tracked local files",
    )
    args = parser.parse_args(argv)
    try:
        plan = build_plan(args.project_root)
        _print_plan(plan, args.apply)
        if args.apply:
            apply_plan(plan, untrack=args.untrack)
            print(
                "Migration applied; source bodies were preserved. Review Git "
                "status and reported links."
            )
    except (OSError, ValueError) as exc:
        print(f"migrate_lore: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
