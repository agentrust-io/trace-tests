"""TR-ANC: Transparency anchoring checks (spec §3.2)."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from trace_tests.result import Finding, Status


def check(trace: dict[str, Any]) -> list[Finding]:
    """Return TR-ANC findings for the transparency claim."""
    findings: list[Finding] = []
    transparency = trace.get("transparency")

    if not transparency:
        return [Finding("TR-ANC-001", Status.FAIL, "TR-ANC-001: transparency field is required at Level 2")]

    if not isinstance(transparency, str):
        return [Finding("TR-ANC-001", Status.FAIL, f"TR-ANC-001: transparency must be a string URI, got {type(transparency).__name__}")]

    try:
        parsed = urlparse(transparency)
        if parsed.scheme == "https" and parsed.netloc:
            findings.append(Finding("TR-ANC-001", Status.PASS, f"transparency is a valid URI ({transparency[:80]})"))
        else:
            findings.append(Finding(
                "TR-ANC-001", Status.FAIL,
                f"TR-ANC-001: transparency must be an https URI, got scheme={parsed.scheme!r}",
            ))
    except Exception as exc:
        findings.append(Finding("TR-ANC-001", Status.FAIL, f"TR-ANC-001: could not parse transparency URI: {exc}"))

    return findings
