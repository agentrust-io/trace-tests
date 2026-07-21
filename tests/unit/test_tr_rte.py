"""Unit tests for TR-RTE module."""

import pytest
from trace_tests.modules.tr_rte import check
from trace_tests.result import Status

_VALID = {
    "runtime": {
        "platform": "amd-sev-snp",
        "measurement": "sha256:" + "a" * 64,
    }
}


def test_valid_runtime_passes():
    findings = check(_VALID)
    assert all(not f.failed() for f in findings), findings


def test_azure_cvm_platform_passes():
    """azure-cvm-sev-snp is a recognized hardware platform (vTPM-rooted SEV-SNP)."""
    trace = {"runtime": {"platform": "azure-cvm-sev-snp", "measurement": "sha384:" + "a" * 96}}
    findings = check(trace, level=2)
    assert all(not f.failed() for f in findings), findings


def test_invalid_platform_fails():
    trace = {"runtime": {**_VALID["runtime"], "platform": "unknown-tee"}}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-RTE-001" in codes


def test_invalid_measurement_format_fails():
    trace = {"runtime": {**_VALID["runtime"], "measurement": "notadigest"}}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-RTE-002" in codes


def test_sha384_measurement_passes():
    trace = {"runtime": {**_VALID["runtime"], "measurement": "sha384:" + "a" * 96}}
    findings = check(trace)
    assert all(not f.failed() for f in findings)


def test_missing_runtime_fails():
    findings = check({})
    assert any(f.failed() for f in findings)


def test_rim_uri_skip_when_absent():
    findings = check(_VALID)
    skipped = [f for f in findings if f.skipped()]
    assert any("rim_uri" in f.message for f in skipped)


def test_valid_rim_uri_passes():
    trace = {"runtime": {**_VALID["runtime"], "rim_uri": "https://example.org/rim/tdx-v1"}}
    findings = check(trace)
    assert all(not f.failed() for f in findings)


def test_invalid_rim_uri_fails():
    trace = {"runtime": {**_VALID["runtime"], "rim_uri": "ftp://bad"}}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-RTE-003" in codes


def test_http_rim_uri_fails():
    trace = {"runtime": {**_VALID["runtime"], "rim_uri": "http://example.org/rim/tdx-v1"}}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-RTE-003" in codes, "plain http rim_uri must be rejected; https only"
