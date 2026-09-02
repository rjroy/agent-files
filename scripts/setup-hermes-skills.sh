#!/usr/bin/env bash
set -euo pipefail

# Reusable setup for Hermes skill discovery from external skill directories.
# Usage:
#   setup-hermes-skills.sh
#   setup-hermes-skills.sh --source /path/to/plugins --source /other/plugins
#   HERMES_HOME=/path/to/home setup-hermes-skills.sh
#
# Idempotent: rerun and it only adds missing entries.

usage() {
  cat <<'EOF'
Usage: setup-hermes-skills.sh [options]

Options:
  -h, --help                  Show this help
  -H, --hermes-home PATH      Hermes home directory (default: $HOME/.hermes)
  -s, --source PATH           Add a skill search root (repeatable)
  -n, --dry-run               Show what would be changed, then exit

Environment:
  HERMES_BIN     Override hermes executable (default: hermes)
  HERMES_HOME    Override Hermes home path

Examples:
  ./setup-hermes-skills.sh
  ./setup-hermes-skills.sh -s "$HOME/.agents/plugins" -s "/opt/team-skills"
EOF
}

HERMES_BIN="${HERMES_BIN:-hermes}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
DRY_RUN=0
SOURCES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -H|--hermes-home)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      HERMES_HOME="$2"
      shift 2
      ;;
    -s|--source)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      SOURCES+=("$2")
      shift 2
      ;;
    -n|--dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ${#SOURCES[@]} -eq 0 ]]; then
  SOURCES+=("$HOME/.agents/plugins")
fi

if ! command -v "$HERMES_BIN" >/dev/null 2>&1; then
  echo "Cannot find executable: $HERMES_BIN" >&2
  exit 1
fi

if [[ ! -f "$HERMES_HOME/config.yaml" ]]; then
  echo "Config file not found at: $HERMES_HOME/config.yaml" >&2
  echo "Set HERMES_HOME correctly or create your Hermes profile first." >&2
  exit 1
fi

# Pass current roots through python for stable YAML parsing and merge.
python - "$HERMES_BIN" "$DRY_RUN" "$HERMES_HOME" "${SOURCES[@]}" <<'PY'
import subprocess
import sys
from pathlib import Path

import yaml

hermes = sys.argv[1]
dry_run = sys.argv[2] == "1"
hermes_home = sys.argv[3]
requested = [Path(p).expanduser() for p in sys.argv[4:]]

proc = subprocess.run(
    [hermes, 'config', 'get', 'skills.external_dirs'],
    capture_output=True,
    text=True,
)
if proc.returncode == 0:
    raw = proc.stdout.strip()
    parsed = yaml.safe_load(raw) if raw else []
    if parsed is None:
        parsed = []
else:
    parsed = []

if isinstance(parsed, str):
    current = [parsed]
elif isinstance(parsed, list):
    current = list(parsed)
else:
    current = []

seen = set()
merged = []
for item in current + [str(p) for p in requested]:
    p = str(Path(str(item)).expanduser())
    if not p:
        continue
    try:
        norm = Path(p).resolve()
    except OSError:
        norm = Path(p)
    norm_key = str(norm)
    if norm_key in seen:
        continue
    seen.add(norm_key)
    merged.append(p)

value = yaml.safe_dump(merged, default_flow_style=True).strip()
print(f"skills.external_dirs = {value}")

def _norm(val: str):
    return str(Path(val).expanduser().resolve())

current_norm = [_norm(str(v)) for v in current]
merged_norm = [_norm(str(v)) for v in merged]

if current_norm == merged_norm:
    print('No changes needed: skills.external_dirs already includes the requested roots.')
    if not dry_run:
        print(f"Updated {hermes_home}/config.yaml")
    sys.exit(0)

missing = [str(Path(p).expanduser().resolve()) for p in merged if not Path(p).expanduser().exists()]
if missing:
    print('Warning: some configured roots do not exist yet:')
    for m in missing:
        print(f"  - {m}")

if dry_run:
    print('DRY-RUN: would run:')
    print(f"{hermes} config set skills.external_dirs '{value}'")
    sys.exit(0)

subprocess.run([hermes, 'config', 'set', 'skills.external_dirs', value], check=True)
print(f"Updated {hermes_home}/config.yaml")
PY

echo
echo "=== Verify ==="
"${HERMES_BIN}" config get skills.external_dirs
