"""TR-POL: Policy bundle checks (spec §3.1)."""

from __future__ import annotations

import re
from typing import Any

from trace_tests.result import Finding, Status

_DIGEST_RE = re.compile(r"^sha(256:[0-9a-f]{64}|384:[0-9a-f]{96})$")
_VALID_ENFORCEMENT = frozenset({"enforce", "advisory", "silent"})


def check(trace: dict[str, Any]) -> list[Finding]:
    """Return TR-POL findings for the policy bundle claim."""
    findings: list[Finding] = []
    policy = trace.get("policy")

    if not isinstance(policy, dict):
        return [Finding("TR-POL-001", Status.FAIL, "TR-POL-001: policy field is missing or not an object")]

    bundle_hash = policy.get("bundle_hash", "")
    if _DIGEST_RE.match(str(bundle_hash)):
        findings.append(Finding("TR-POL-001", Status.PASS, "policy.bundle_hash has valid digest format"))
    else:
        findings.append(Finding(
            "TR-POL-001", Status.FAIL,
            f"TR-POL-001: policy.bundle_hash must match sha256:<64hex> or sha384:<96hex>, got {bundle_hash!r}",
        ))

    enforcement = policy.get("enforcement_mode")
    if enforcement in _VALID_ENFORCEMENT:
        findings.append(Finding("TR-POL-002", Status.PASS, f"policy.enforcement_mode is valid ({enforcement!r})"))
    else:
        findings.append(Finding(
            "TR-POL-002", Status.FAIL,
            f"TR-POL-002: policy.enforcement_mode must be one of {sorted(_VALID_ENFORCEMENT)}, got {enforcement!r}",
        ))

    return findings
