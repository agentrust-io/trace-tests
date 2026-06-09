"""Run conformance modules for a given level against a trust record."""

from __future__ import annotations

from typing import Any

from trace_tests.loader import extract_trace
from trace_tests.modules import tr_anc, tr_env, tr_pol, tr_rte, tr_sca, tr_sig, tr_txn
from trace_tests.result import Finding

# Modules that run at each level (cumulative).
_LEVEL_MODULES: dict[int, list[str]] = {
    0: ["TR-ENV", "TR-SIG", "TR-POL"],
    1: ["TR-ENV", "TR-SIG", "TR-POL", "TR-RTE", "TR-SCA"],
    2: ["TR-ENV", "TR-SIG", "TR-POL", "TR-RTE", "TR-SCA", "TR-TXN", "TR-ANC"],
}


def run(record: dict[str, Any], fmt: str, level: int) -> dict[str, list[Finding]]:
    """Run all modules required for *level* and return findings keyed by module ID."""
    if level not in _LEVEL_MODULES:
        raise ValueError(f"Unknown conformance level {level!r}; valid: 0, 1, 2")

    trace = extract_trace(record, fmt)
    results: dict[str, list[Finding]] = {}

    active = set(_LEVEL_MODULES[level])

    if "TR-ENV" in active:
        results["TR-ENV"] = tr_env.check(trace)

    if "TR-SIG" in active:
        results["TR-SIG"] = tr_sig.check(trace, record, fmt)

    if "TR-POL" in active:
        results["TR-POL"] = tr_pol.check(trace)

    if "TR-RTE" in active:
        results["TR-RTE"] = tr_rte.check(trace)

    if "TR-SCA" in active:
        results["TR-SCA"] = tr_sca.check(trace)

    if "TR-TXN" in active:
        results["TR-TXN"] = tr_txn.check(trace)

    if "TR-ANC" in active:
        results["TR-ANC"] = tr_anc.check(trace)

    return results
