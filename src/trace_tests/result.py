"""Conformance finding types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    # No cryptographic verification was possible. Distinct from SKIP so callers
    # can never mistake an unverified record for a benign omission. Treated as
    # a failure at any conformance level that requires signatures (level >= 1).
    UNVERIFIED = "unverified"


@dataclass
class Finding:
    code: str
    status: Status
    message: str

    def passed(self) -> bool:
        return self.status == Status.PASS

    def failed(self) -> bool:
        return self.status == Status.FAIL

    def skipped(self) -> bool:
        return self.status == Status.SKIP

    def unverified(self) -> bool:
        return self.status == Status.UNVERIFIED
