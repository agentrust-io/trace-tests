"""trace-tests CLI."""

from __future__ import annotations

import datetime as _dt
import json
import importlib.metadata
import pathlib
import sys
from typing import Any

import click

from trace_tests import __version__
from trace_tests import report as report_mod
from trace_tests.loader import LoadError, load_record
from trace_tests.modules.tr_env import DEFAULT_MAX_AGE_SECONDS
from trace_tests.result import Status
from trace_tests.runner import run


def _library_version() -> str | None:
    """Version of the authoring library, when it is installed alongside the suite.

    Recorded on the report because the two cut over to the v0.2 profile together
    and neither dual-accepts, so a mismatched pair produces a confident failure on
    a record that is fine. A reader of the report should be able to see the pair.
    """
    try:
        return importlib.metadata.version("agentrust-trace")
    except importlib.metadata.PackageNotFoundError:
        return None


def _fmt_status(status: Status) -> str:
    return status.value.upper().ljust(10)


def _print_report(path: str, fmt: str, level: int, results: dict[str, list[Any]]) -> int:
    """Print the conformance report and return exit code (0=pass, 1=fail)."""
    click.echo(f"\nTRACE Conformance Report -- Level {level}")
    click.echo(f"Format : {fmt}")
    click.echo(f"Record : {path}")
    click.echo("")

    failures = 0
    skips = 0
    passes = 0
    unverified = 0

    for module, findings in results.items():
        for f in findings:
            prefix = _fmt_status(f.status)
            click.echo(f"  {module}  {prefix}  {f.message}")
            if f.failed():
                failures += 1
            elif f.passed():
                passes += 1
            elif f.unverified():
                unverified += 1
            else:
                skips += 1

    # Defense in depth: unverified findings must fail the run at any level that
    # requires signatures, even if a module forgot to emit a hard FAIL.
    if unverified and level >= 1:
        failures += unverified

    total = passes + failures + skips + (unverified if level == 0 else 0)
    click.echo("")
    if failures == 0:
        if unverified:
            click.echo(
                f"Result: PASS  ({total} checks, {skips} skipped, {unverified} UNVERIFIED "
                f"-- record is NOT cryptographically verified)"
            )
        else:
            click.echo(f"Result: PASS  ({total} checks, {skips} skipped)")
        return 0
    else:
        click.echo(f"Result: FAIL  ({total} checks, {failures} failure(s), {skips} skipped)")
        return 1



def _load_receipt(path: str | None) -> dict | None:
    """Load and shape-check an anchor receipt, or return None when not supplied."""
    if path is None:
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        click.echo(f"Error: cannot read receipt {path}: {exc}", err=True)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: receipt {path} is not valid JSON: {exc}", err=True)
        sys.exit(2)
    if not isinstance(data, dict):
        click.echo(
            f"Error: receipt {path} must be a JSON object, got {type(data).__name__}",
            err=True,
        )
        sys.exit(2)
    return data

@click.group()
@click.version_option(__version__)
def main() -> None:
    """TRACE conformance test suite."""


@main.command()
@click.option("--record", required=True, type=click.Path(), help="Path to the trust record (JSON)")
@click.option(
    "--level",
    default=0,
    type=click.IntRange(0, 2),
    show_default=True,
    help="Conformance level to check (0, 1, or 2)",
)
@click.option(
    "--max-age",
    "max_age",
    default=DEFAULT_MAX_AGE_SECONDS,
    type=click.IntRange(min=1),
    show_default=True,
    help="Maximum allowed record age in seconds (iat freshness window)",
)
@click.option(
    "--expected-nonce",
    default=None,
    help="Verifier-issued challenge nonce; required for Level 1 and Level 2.",
)
@click.option(
    "--receipt",
    default=None,
    type=click.Path(),
    help=(
        "Path to the anchor receipt (JSON) proving the record is included in the "
        "transparency log. Required for TR-ANC-002 at Level 2: the transparency URI "
        "says where the anchor lives, the receipt is what proves the record is in it."
    ),
)
def verify(record: str, level: int, max_age: int, expected_nonce: str | None, receipt: str | None) -> None:
    """Verify a TRACE trust record against the conformance suite."""
    try:
        data, fmt = load_record(record)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    receipt_data = _load_receipt(receipt)

    results = run(
        data,
        fmt,
        level,
        max_age_seconds=max_age,
        expected_nonce=expected_nonce,
        receipt=receipt_data,
    )
    exit_code = _print_report(record, fmt, level, results)
    sys.exit(exit_code)


@main.command()
@click.option("--record", required=True, type=click.Path(), help="Path to the trust record (JSON)")
@click.option(
    "--max-level",
    default=2,
    type=click.IntRange(0, 2),
    show_default=True,
    help="Highest level to attempt; every level up to it is run",
)
@click.option(
    "--max-age",
    "max_age",
    default=DEFAULT_MAX_AGE_SECONDS,
    type=click.IntRange(min=1),
    show_default=True,
)
@click.option(
    "--html", "html_out", type=click.Path(), help="Write a self-contained HTML report here"
)
@click.option(
    "--json", "json_out", type=click.Path(), help="Write the machine-readable report here"
)
@click.option("--badge", "badge_out", type=click.Path(), help="Write a level badge (SVG) here")
@click.option(
    "--fail-under",
    type=click.IntRange(0, 2),
    help="Exit non-zero unless the record reaches this level. Omit to always exit 0, "
    "which is what you want when generating an artifact rather than gating on one.",
)
@click.option(
    "--expected-nonce",
    default=None,
    help="Verifier-issued challenge nonce; required for Level 1 and Level 2.",
)
@click.option(
    "--receipt",
    default=None,
    type=click.Path(),
    help="Path to the anchor receipt (JSON). Required for TR-ANC-002 at Level 2.",
)
def report(
    record: str,
    max_level: int,
    max_age: int,
    html_out: str | None,
    json_out: str | None,
    badge_out: str | None,
    fail_under: int | None,
    expected_nonce: str | None,
    receipt: str | None,
) -> None:
    """Produce a conformance report you can hand to someone else.

    Runs every level up to --max-level rather than one, because the useful answer
    for a reader is the highest level the record reaches, not whether it cleared
    the single level the person running the tool happened to pick.
    """
    try:
        data, fmt = load_record(record)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    receipt_data = _load_receipt(receipt)

    results_by_level = {
        level: run(
            data,
            fmt,
            level,
            max_age_seconds=max_age,
            expected_nonce=expected_nonce,
            receipt=receipt_data,
        )
        for level in range(max_level + 1)
    }

    built = report_mod.build(
        record=data,
        record_path=record,
        record_format=fmt,
        results_by_level=results_by_level,
        suite_version=__version__,
        library_version=_library_version(),
        generated_at=_dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )

    wrote = []
    for path, render in (
        (html_out, report_mod.to_html),
        (json_out, report_mod.to_json),
        (badge_out, report_mod.badge_svg),
    ):
        if path:
            pathlib.Path(path).write_text(render(built), encoding="utf-8")
            wrote.append(path)

    click.echo(f"TRACE Conformance Report -- {built.verdict}")
    click.echo(f"Record : {record}")
    click.echo(f"Digest : {built.digest}")
    for lv in built.levels:
        mark = "PASS" if lv.passed else "FAIL"
        click.echo(f"  Level {lv.level}  {mark}")
    for path in wrote:
        click.echo(f"Wrote  : {path}")
    if not wrote:
        click.echo("")
        click.echo(report_mod.to_json(built))

    if fail_under is not None:
        top = built.highest_level
        if top is None or top < fail_under:
            click.echo(f"Result: below the required Level {fail_under}", err=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
