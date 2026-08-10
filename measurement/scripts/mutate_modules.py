#!/usr/bin/env python3
"""Measure whether `trace-tests` notices when its own conformance checks break.

`trace-tests` is what stamps an implementation as conforming. This asks a question one
level up from what it verifies: **if a check inside a conformance module silently stopped
working, would the repository's own test suite catch it?**

Method. For every `Finding(..., Status.FAIL, ...)` construction in
`src/trace_tests/modules/tr_*.py`, rewrite that site so the check can never fail, run the
whole suite, and count how many tests notice. Restore, move to the next site.

A site whose removal nothing notices is a check whose failure path is unverified. A
regression there ships green.

Three things this script guards against, each of which produced a wrong answer during
development:

- **A green baseline is a precondition, not an assumption.** Mutating a suite that is
  already red measures nothing, so the baseline is run first and a non-green one aborts.
- **A mutation that did not apply looks exactly like a check that does not matter.** Each
  rewrite is verified to have changed the file before the suite is run. A no-op mutation
  that left the suite green would otherwise be recorded as "nothing notices".
- **An empty site list would report perfect coverage.** Zero sites aborts.

Counting fixtures that *name* a check is not this measurement, and gives a very different
answer: on the tree measured here the name-based proxy reported 12 unverified checks where
mutation found 3.

Usage:
    python mutate_modules.py [path-to-trace-tests]     # or set TRACE_TESTS
"""

from __future__ import annotations

import ast
import collections
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Default to the checkout this script lives in, derived from its own location rather
# than from the working directory. `Path("")` and `Path(".")` both resolve to wherever
# the caller happens to stand, which is how a measurement ends up reporting on the
# wrong tree.
_DEFAULT = Path(__file__).resolve().parent.parent.parent
TRACE_TESTS = Path(
    sys.argv[1] or _DEFAULT if len(sys.argv) > 1 else os.environ.get("TRACE_TESTS") or _DEFAULT
).expanduser()

if not TRACE_TESTS.is_dir() or not (TRACE_TESTS / "src" / "trace_tests").is_dir():
    sys.exit(
        f"trace-tests checkout not found: {TRACE_TESTS or '<unset>'}\n"
        "Pass it as argv[1] or set TRACE_TESTS. Exiting non-zero rather than measuring "
        "nothing: a coverage measurement that reports success over an empty corpus is "
        "the failure this script exists to find."
    )

MODULES = sorted((TRACE_TESTS / "src" / "trace_tests" / "modules").glob("tr_*.py"))
CODE_RE = re.compile(r"(TR-[A-Z]{3}-\d{3})")


@dataclass(frozen=True)
class Site:
    path: Path
    lineno: int          # line carrying `Status.FAIL`
    code: str


def fail_sites() -> list[Site]:
    """Every `Finding(..., Status.FAIL, ...)` construction, keyed to the line to rewrite.

    A `Finding(...)` call may span several lines, so the code is read from the first
    argument and the rewrite target is the line actually carrying `Status.FAIL`.
    """
    sites: list[Site] = []
    for path in MODULES:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for node in ast.walk(ast.parse(text)):
            if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "Finding"):
                continue
            if not any(isinstance(a, ast.Attribute) and a.attr == "FAIL" for a in node.args):
                continue
            code = ""
            if node.args and isinstance(node.args[0], ast.Constant):
                match = CODE_RE.match(str(node.args[0].value))
                code = match.group(1) if match else str(node.args[0].value)[:24]
            target = next(
                (
                    k + 1
                    for k in range(node.lineno - 1, min(node.lineno + 5, len(lines)))
                    if "Status.FAIL" in lines[k]
                ),
                None,
            )
            if target is None:
                sys.exit(
                    f"{path.name}:{node.lineno} constructs a FAIL Finding but no line "
                    "within reach carries `Status.FAIL`. Refusing to guess which line to "
                    "rewrite; a mis-targeted mutation is worse than none."
                )
            sites.append(Site(path, target, code))
    return sites


def run_suite() -> int:
    """Return the number of failing tests. No `-x`: the count is the margin."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "--tb=no", "-p", "no:cacheprovider"],
        cwd=TRACE_TESTS,
        capture_output=True,
        text=True,
    )
    match = re.search(r"(\d+) failed", result.stdout)
    return int(match.group(1)) if match else 0


def main() -> int:
    sites = fail_sites()
    if not sites:
        sys.exit("no FAIL sites found; the walk matched nothing and would report perfectly")

    print(f"checkout: {TRACE_TESTS}")
    print(f"modules:  {len(MODULES)}   FAIL sites: {len(sites)}\n")

    baseline = run_suite()
    if baseline:
        sys.exit(
            f"baseline is not green ({baseline} failing). Mutating a red suite measures "
            "nothing, because a failure cannot be attributed to the mutation."
        )
    print("baseline: green\n")

    margins: dict[str, list[int]] = collections.defaultdict(list)
    for site in sites:
        original = site.path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        mutated = lines[site.lineno - 1].replace("Status.FAIL", "Status.PASS", 1)
        if mutated == lines[site.lineno - 1]:
            sys.exit(
                f"{site.path.name}:{site.lineno} did not change under mutation. A no-op "
                "rewrite is indistinguishable from a check nothing notices, so this is a "
                "hard stop rather than a skipped site."
            )
        lines[site.lineno - 1] = mutated
        site.path.write_text("".join(lines), encoding="utf-8")
        try:
            noticed = run_suite()
        finally:
            site.path.write_text(original, encoding="utf-8")
            if site.path.read_text(encoding="utf-8") != original:
                sys.exit(f"failed to restore {site.path}; stopping before more damage")
        margins[site.code].append(noticed)
        flag = "" if noticed else "   <-- unverified"
        print(f"  {site.code:<12} {site.path.stem:<8} line {site.lineno:<4} margin {noticed}{flag}")

    print()
    unverified = sorted(code for code, values in margins.items() if max(values) == 0)
    thin = sorted(code for code, values in margins.items() if 0 < max(values) <= 1)
    print(f"  checks measured : {len(margins)}")
    print(f"  verified        : {len(margins) - len(unverified)}")
    print(f"  unverified      : {len(unverified)}  {unverified}")
    print(f"  margin 1 only   : {len(thin)}  {thin}")

    if unverified:
        print(
            "\nA check with margin 0 can be broken without any test failing. On a suite "
            "whose output is a conformance stamp, that is the failure worth naming."
        )
    return 1 if unverified else 0


if __name__ == "__main__":
    raise SystemExit(main())
