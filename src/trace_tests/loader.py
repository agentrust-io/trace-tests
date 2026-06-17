"""Load and normalize trust records from disk."""

from __future__ import annotations

import json
import pathlib
from typing import Any


class LoadError(Exception):
    pass


def load_record(path: str) -> tuple[dict[str, Any], str]:
    """Load a trust record from *path*.

    Returns ``(record_dict, format_string)`` where format is one of:
    - ``"cmcp-runtime"``: cmcp RuntimeClaim envelope (positive marker: ``cmcp_version``)
    - ``"trace"``: canonical TRACE Trust Record (fields at top level)

    Format detection is based on positive structural markers so an attacker cannot
    downgrade a cmcp envelope to the weaker plain-trace path by stripping fields.
    Records that look like partial cmcp envelopes are rejected outright.
    """
    p = pathlib.Path(path)
    if not p.exists():
        raise LoadError(f"File not found: {path}")

    try:
        data: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LoadError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise LoadError("Record must be a JSON object")

    if "cmcp_version" in data:
        if not isinstance(data.get("trace"), dict):
            raise LoadError(
                "Record declares cmcp_version but has no 'trace' object; refusing malformed cmcp-runtime envelope"
            )
        return data, "cmcp-runtime"

    # Envelope-only keys present without cmcp_version: this is a partial/stripped
    # cmcp envelope, not a canonical TRACE record. Reject rather than silently
    # downgrading to the weaker plain-trace verification path.
    # Note: "signature" alone is allowed -- plain TRACE records may carry an
    # embedded Ed25519 signature field (agentrust-trace sign_record() output).
    partial_markers = sorted(k for k in ("trace", "gateway") if k in data)
    if partial_markers:
        raise LoadError(
            f"Record contains cmcp envelope field(s) {partial_markers} but no 'cmcp_version'; "
            "refusing to treat a partial cmcp-runtime envelope as a plain trace record"
        )

    return data, "trace"


def extract_trace(record: dict[str, Any], fmt: str) -> dict[str, Any]:
    """Return the TRACE fields dict from *record*."""
    if fmt == "cmcp-runtime":
        return record["trace"]
    return record
