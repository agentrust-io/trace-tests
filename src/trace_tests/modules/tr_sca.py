"""TR-SCA: Supply-chain provenance checks (spec §3.1)."""

from __future__ import annotations

import re
from typing import Any

from trace_tests.result import Finding, Status

_DIGEST_RE = re.compile(r"^sha(256:[0-9a-f]{64}|384:[0-9a-f]{96})$")
_SLSA_LEVELS = frozenset({0,1, 2, 3})


def check(trace: dict[str, Any]) -> list[Finding]:
    """Return TR-SCA findings for the build provenance claim."""
    findings: list[Finding] = []
    prov = trace.get("build_provenance")

    if prov is None:
        return [Finding("TR-SCA-001", Status.FAIL, "TR-SCA-001: build_provenance is required at Level 1+")]

    if not isinstance(prov, dict):
        return [Finding("TR-SCA-001", Status.FAIL, "TR-SCA-001: build_provenance must be an object")]

    slsa_level = prov.get("slsa_level")
    if slsa_level in _SLSA_LEVELS:
        findings.append(Finding("TR-SCA-001", Status.PASS, f"build_provenance.slsa_level is valid ({slsa_level})"))
    else:
        findings.append(Finding(
            "TR-SCA-001", Status.FAIL,
            f"TR-SCA-001: build_provenance.slsa_level must be 0,1, 2, or 3, got {slsa_level!r}",
        ))

    digest = prov.get("digest", "")
    if _DIGEST_RE.match(str(digest)):
        findings.append(Finding("TR-SCA-002", Status.PASS, "build_provenance.digest has valid digest format"))
    else:
        findings.append(Finding(
            "TR-SCA-002", Status.FAIL,
            f"TR-SCA-002: build_provenance.digest must match sha256:<64hex> or sha384:<96hex>, got {digest!r}",
        ))

    return findings
