"""Check the customer report fixture in a separate process."""

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
    spec = importlib.util.spec_from_file_location("report", workspace / "report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results = []
    for customers, orders in cases:
        value = module.customer_report(customers, orders)
        results.append({"is_list": isinstance(value, list), "value": value})
print(json.dumps(results))
"""


def main():
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        print("usage: check.py WORKSPACE", file=sys.stderr)
        return 2

    customers = [
        {"id": "cust-1", "name": "Ada", "email": "shared@example.com"},
        {"id": "cust-2", "name": "Bea", "email": "shared@example.com"},
        {"id": "cust-3", "name": "Cal", "email": "cal@example.com"},
        {"id": "cust-4", "name": "Dee", "email": "dee@example.com"},
    ]
    orders = [
        {"id": "order-1", "customer_id": "cust-1"},
        {"id": "order-2", "customer_id": "cust-1"},
        {"id": "order-3", "customer_id": "cust-2"},
        {"id": "order-4", "customer_id": "cust-4"},
        {"id": "order-5", "customer_id": "missing"},
    ]
    cases = [
        (customers, orders),
        (customers, []),
        ([], orders),
        ([customers[0]], orders[:2]),
    ]
    # These values stay in the checker process, independent of candidate inputs.
    expected = [
        [
            {"id": "cust-1", "name": "Ada", "email": "shared@example.com"},
            {"id": "cust-2", "name": "Bea", "email": "shared@example.com"},
            {"id": "cust-4", "name": "Dee", "email": "dee@example.com"},
        ],
        [],
        [],
        [{"id": "cust-1", "name": "Ada", "email": "shared@example.com"}],
    ]
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
    if not isinstance(actual, list) or len(actual) != len(expected):
        print(f"expected {len(expected)} results, got {actual!r}", file=sys.stderr)
        return 1
    for entry, wanted in zip(actual, expected):
        if not isinstance(entry, dict) or entry.get("is_list") is not True:
            print(f"expected a list, got {entry!r}", file=sys.stderr)
            return 1
        received = entry.get("value")
        if (not isinstance(received, list) or len(received) != len(wanted)
                or any(received.count(customer) != 1 for customer in wanted)):
            print(f"expected {wanted!r}, got {received!r}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
