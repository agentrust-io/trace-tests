"""trace-tests CLI."""

from __future__ import annotations

import sys
from typing import Any

import click

from trace_tests import __version__
from trace_tests.loader import LoadError, load_record
from trace_tests.result import Status
from trace_tests.runner import run


def _fmt_status(status: Status) -> str:
    return status.value.upper().ljust(4)


def _print_report(path: str, fmt: str, level: int, results: dict[str, list[Any]]) -> int:
    """Print the conformance report and return exit code (0=pass, 1=fail)."""
    click.echo(f"\nTRACE Conformance Report -- Level {level}")
    click.echo(f"Format : {fmt}")
    click.echo(f"Record : {path}")
    click.echo("")

    failures = 0
    skips = 0
    passes = 0

    for module, findings in results.items():
        for f in findings:
            prefix = _fmt_status(f.status)
            click.echo(f"  {module}  {prefix}  {f.message}")
            if f.failed():
                failures += 1
            elif f.passed():
                passes += 1
            else:
                skips += 1

    total = passes + failures + skips
    click.echo("")
    if failures == 0:
        click.echo(f"Result: PASS  ({total} checks, {skips} skipped)")
        return 0
    else:
        click.echo(f"Result: FAIL  ({total} checks, {failures} failure(s), {skips} skipped)")
        return 1


@click.group()
@click.version_option(__version__)
def main() -> None:
    """TRACE conformance test suite."""


@main.command()
@click.option("--record", required=True, type=click.Path(), help="Path to the trust record (JSON)")
@click.option("--level", default=0, type=click.IntRange(0, 2), show_default=True, help="Conformance level to check (0, 1, or 2)")
def verify(record: str, level: int) -> None:
    """Verify a TRACE trust record against the conformance suite."""
    try:
        data, fmt = load_record(record)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    results = run(data, fmt, level)
    exit_code = _print_report(record, fmt, level, results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
