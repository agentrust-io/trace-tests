"""Unit tests for TR-ANC module."""

from trace_tests.modules.tr_anc import check


def test_https_transparency_passes():
    findings = check({"transparency": "https://scitt.example.org/receipts/abc123"})
    assert all(f.passed() for f in findings), findings


def test_http_transparency_fails():
    failed = [f for f in check({"transparency": "http://scitt.example.org/receipts/abc123"}) if f.failed()]
    assert any(f.code == "TR-ANC-001" for f in failed), "plain http transparency URI must be rejected; https only"


def test_missing_transparency_fails():
    failed = [f for f in check({}) if f.failed()]
    assert any(f.code == "TR-ANC-001" for f in failed)


def test_non_string_transparency_fails():
    failed = [f for f in check({"transparency": 42}) if f.failed()]
    assert any(f.code == "TR-ANC-001" for f in failed)


def test_non_uri_scheme_fails():
    failed = [f for f in check({"transparency": "ftp://example.org/log"}) if f.failed()]
    assert any(f.code == "TR-ANC-001" for f in failed)
