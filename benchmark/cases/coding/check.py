"""Check the settings fixture using results returned by a separate process."""

import json
from pathlib import Path
import subprocess
import sys


CHILD = r"""
import contextlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
workspace = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(workspace))
cases = json.load(sys.stdin)
with contextlib.redirect_stdout(sys.stderr):
    spec = importlib.util.spec_from_file_location("settings", workspace / "settings.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results = [module.effective_enabled(settings, default) for settings, default in cases]
print(json.dumps(results))
"""


def main():
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        print("usage: check.py WORKSPACE", file=sys.stderr)
        return 2

    cases = [
        ({}, True),
        ({}, False),
        ({"enabled": False}, True),
        ({"enabled": False}, False),
        ({"enabled": True}, True),
        ({"enabled": True}, False),
        ({"enabled": False, "other": "value"}, True),
    ]
    expected = [True, False, False, False, True, True, False]
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-c", CHILD, sys.argv[1]],
            input=json.dumps(cases), capture_output=True, text=True,
            timeout=10, check=False,
        )
    except OSError as exc:
        print(f"fixture execution failed: {exc}", file=sys.stderr)
        return 2
    except (subprocess.TimeoutExpired, UnicodeError) as exc:
        print(f"fixture execution failed: {exc}", file=sys.stderr)
        return 1
    if result.returncode:
        print(f"fixture execution failed: {result.stderr}", file=sys.stderr)
        return 1
    try:
        actual = json.loads(result.stdout)
    except (ValueError, UnicodeError):
        print("fixture did not return complete results", file=sys.stderr)
        return 1
    if (not isinstance(actual, list) or len(actual) != len(expected)
            or any(value is not wanted for value, wanted in zip(actual, expected))):
        print(f"expected {expected!r}, got {actual!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
