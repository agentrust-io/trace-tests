"""Conformance coverage for records imported from an OpenShell control plane."""

from __future__ import annotations

import copy
import time

import jsonschema
import pytest

from trace_tests.result import Status
from trace_tests.runner import run


def _failures(results):
    return [
        finding
        for findings in results.values()
        for finding in findings
        if finding.status is Status.FAIL
    ]


def test_openshell_import_is_level0_conformant(schema, load_vector) -> None:
    record = load_vector("valid_openshell_import.json")
    record["iat"] = int(time.time())

    jsonschema.validate(record, schema)
    assert _failures(run(record, "trace", 0)) == []


def test_imported_openshell_evidence_cannot_claim_hardware(schema, load_vector) -> None:
    record = copy.deepcopy(load_vector("valid_openshell_import.json"))
    record["runtime"]["platform"] = "intel-tdx"

    with pytest.raises(jsonschema.exceptions.ValidationError):
        jsonschema.validate(record, schema)


def test_openshell_import_does_not_require_transparency_at_level0(schema, load_vector) -> None:
    record = load_vector("valid_openshell_import.json")
    assert "transparency" not in record
    jsonschema.validate(record, schema)
