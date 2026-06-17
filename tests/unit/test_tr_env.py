"""Unit tests for TR-ENV module."""

import time
import pytest
from trace_tests.modules.tr_env import check
from trace_tests.result import Status

_VALID = {
    "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
    "iat": int(time.time()) - 600,  # fresh: 10 minutes old
    "subject": "spiffe://example.org/agent/test",
    "cnf": {"jwk": {"kty": "OKP", "crv": "Ed25519", "x": "dGVzdA"}},
}


def test_all_pass_on_valid():
    findings = check(_VALID)
    assert all(f.passed() for f in findings), [f for f in findings if not f.passed()]


def test_wrong_eat_profile_fails():
    trace = {**_VALID, "eat_profile": "tag:wrong,2025:v1"}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-ENV-001" in codes


def test_missing_eat_profile_fails():
    trace = {k: v for k, v in _VALID.items() if k != "eat_profile"}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-ENV-001" in codes


def test_iat_too_small_fails():
    trace = {**_VALID, "iat": 100}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-ENV-002" in codes


def test_iat_in_future_fails():
    trace = {**_VALID, "iat": int(time.time()) + 3600}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-ENV-002" in codes


def test_iat_older_than_default_max_age_fails():
    trace = {**_VALID, "iat": int(time.time()) - (25 * 3600)}  # 25 hours old
    failed = [f for f in check(trace) if f.failed()]
    assert any(f.code == "TR-ENV-002" and "stale" in f.message for f in failed), failed


def test_iat_within_custom_max_age_passes():
    trace = {**_VALID, "iat": int(time.time()) - (25 * 3600)}
    findings = check(trace, max_age_seconds=48 * 3600)
    assert all(f.passed() for f in findings), [f for f in findings if not f.passed()]


def test_iat_beyond_custom_max_age_fails():
    trace = {**_VALID, "iat": int(time.time()) - 7200}  # 2 hours old
    failed = [f for f in check(trace, max_age_seconds=3600) if f.failed()]
    assert any(f.code == "TR-ENV-002" for f in failed)


def test_did_subject_passes():
    trace = {**_VALID, "subject": "did:key:z6MkhaXgBZDvotzL8oCYaXeFuJArwvX6mDMsKTJVjtN7R"}
    findings = check(trace)
    assert all(f.passed() for f in findings), [f for f in findings if not f.passed()]


def test_did_mesh_subject_passes():
    trace = {**_VALID, "subject": "did:mesh:spiffe://factory.example/agent/material-movement/dev"}
    findings = check(trace)
    assert all(f.passed() for f in findings), [f for f in findings if not f.passed()]


def test_non_spiffe_non_did_subject_fails():
    trace = {**_VALID, "subject": "https://example.org/agent"}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-ENV-003" in codes


def test_missing_cnf_jwk_fails():
    trace = {**_VALID, "cnf": {}}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-ENV-004" in codes
