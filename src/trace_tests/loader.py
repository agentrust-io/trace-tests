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
    - ``"cmcp-runtime"``: cmcp RuntimeClaim envelope (has ``gateway`` + ``trace`` + ``signature``)
    - ``"trace"``: canonical TRACE Trust Record (fields at top level)
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

    fmt = "cmcp-runtime" if ("gateway" in data and "trace" in data) else "trace"
    return data, fmt


def extract_trace(record: dict[str, Any], fmt: str) -> dict[str, Any]:
    """Return the TRACE fields dict from *record*."""
    if fmt == "cmcp-runtime":
        return record["trace"]
    return record
