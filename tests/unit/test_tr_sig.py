"""Unit tests for TR-SIG module."""

import base64
import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from trace_tests.modules.tr_sig import check
from trace_tests.result import Status


def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _canonical_json(d: dict) -> bytes:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _make_signed_record() -> dict:
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    pub_raw = pub.public_bytes_raw()
    x = _b64url(pub_raw)
    kid = f"test-{pub_raw[:4].hex()}"

    record = {
        "cmcp_version": "1.0",
        "trace": {
            "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
            "iat": 1748000000,
            "subject": "spiffe://cmcp.gateway/session/unit-test",
            "runtime": {
                "platform": "tpm2",
                "measurement": "sha256:a" * 0 + "sha256:" + "a" * 64,
            },
            "policy": {
                "bundle_hash": "sha256:" + "b" * 64,
                "enforcement_mode": "enforce",
            },
            "data_class": "internal",
            "cnf": {"jwk": {"kty": "OKP", "crv": "Ed25519", "x": x, "kid": kid}},
        },
        "gateway": {"session_id": "unit-test"},
        "signature": "",
    }

    body = _canonical_json({k: v for k, v in record.items() if k != "signature"})
    sig = priv.sign(body)
    record["signature"] = _b64url(sig)
    return record


def test_valid_ed25519_signature_passes():
    record = _make_signed_record()
    trace = record["trace"]
    findings = check(trace, record, "cmcp-runtime")
    assert all(f.passed() for f in findings), findings


def test_tampered_body_fails():
    record = _make_signed_record()
    record["trace"]["iat"] = 1748000001  # tamper
    trace = record["trace"]
    findings = check(trace, record, "cmcp-runtime")
    assert any(f.failed() and "TR-SIG-001" in f.code for f in findings)


def test_missing_signature_fails():
    record = _make_signed_record()
    record["signature"] = ""
    trace = record["trace"]
    findings = check(trace, record, "cmcp-runtime")
    assert any(f.failed() for f in findings)


def test_trace_format_level0_is_unverified_never_pass_only():
    trace = {
        "cnf": {"jwk": {"kty": "EC", "crv": "P-256", "x": "test", "y": "test"}},
    }
    findings = check(trace, trace, "trace", level=0)
    statuses = {f.status for f in findings}
    assert Status.UNVERIFIED in statuses, "plain trace records must be marked UNVERIFIED"
    assert Status.SKIP not in statuses, "missing crypto must not be reported as a benign skip"
    assert Status.FAIL not in statuses


@pytest.mark.parametrize("level", [1, 2])
def test_trace_format_fails_at_signature_requiring_levels(level):
    trace = {
        "cnf": {"jwk": {"kty": "EC", "crv": "P-256", "x": "test", "y": "test"}},
    }
    findings = check(trace, trace, "trace", level=level)
    failed = [f for f in findings if f.failed()]
    assert any("TR-SIG-005" in f.code for f in failed), (
        f"plain trace record must FAIL TR-SIG at level {level}: {findings}"
    )


def test_trace_format_missing_kty_fails():
    trace = {"cnf": {"jwk": {}}}
    findings = check(trace, trace, "trace")
    assert any(f.failed() for f in findings)
