"""Unit tests for TR-ENV module."""

import time
import pytest
from trace_tests.modules.tr_env import check
from trace_tests.result import Status

_VALID = {
    "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
    "iat": 1748000000,
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


def test_non_spiffe_subject_fails():
    trace = {**_VALID, "subject": "https://example.org/agent"}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-ENV-003" in codes


def test_missing_cnf_jwk_fails():
    trace = {**_VALID, "cnf": {}}
    codes = {f.code for f in check(trace) if f.failed()}
    assert "TR-ENV-004" in codes
