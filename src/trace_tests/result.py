"""Conformance finding types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


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
