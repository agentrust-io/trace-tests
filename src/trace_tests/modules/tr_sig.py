"""TR-SIG: Signature verification (spec §3.2.1).

For cmcp-runtime records: Ed25519 over canonical JSON (sorted keys, no whitespace,
excluding the ``signature`` field). Key is in ``trace.cnf.jwk``.

For plain trace records: checks key type and algorithm alignment. Full JWS/COSE
verification is not yet implemented for this format.
"""

from __future__ import annotations

import base64
import json
from typing import Any

from trace_tests.result import Finding, Status

_SUPPORTED_KTY = {"OKP", "EC"}
_ED25519_CRV = "Ed25519"


def _b64url_decode(s: str) -> bytes:
    pad = 4 - len(s) % 4
    if pad != 4:
        s += "=" * pad
    return base64.urlsafe_b64decode(s)


def _canonical_json(d: dict[str, Any]) -> bytes:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _verify_ed25519(pub_x: str, sig_b64: str, body: bytes) -> tuple[bool, str]:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
    except ImportError:
        return False, "cryptography library not installed; run: pip install cryptography"

    try:
        pub_bytes = _b64url_decode(pub_x)
        pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
    except Exception as exc:
        return False, f"TR-SIG-002: invalid public key in cnf.jwk.x: {exc}"

    try:
        sig_bytes = _b64url_decode(sig_b64)
    except Exception as exc:
        return False, f"TR-SIG-003: invalid base64url signature: {exc}"

    try:
        pub_key.verify(sig_bytes, body)
        return True, "Ed25519 signature verified"
    except InvalidSignature:
        return False, "TR-SIG-001: signature verification failed"


def check_cmcp_runtime(record: dict[str, Any]) -> list[Finding]:
    """Verify the Ed25519 signature on a cmcp RuntimeClaim."""
    findings: list[Finding] = []

    sig = record.get("signature", "")
    if not sig:
        findings.append(Finding("TR-SIG-001", Status.FAIL, "TR-SIG-001: signature field is missing or empty"))
        return findings

    jwk = record.get("trace", {}).get("cnf", {}).get("jwk", {})
    kty = jwk.get("kty")
    crv = jwk.get("crv")
    x = jwk.get("x")

    if kty != "OKP" or crv != _ED25519_CRV:
        findings.append(Finding("TR-SIG-002", Status.FAIL, f"TR-SIG-002: expected OKP/Ed25519 key, got kty={kty!r} crv={crv!r}"))
        return findings

    if not x:
        findings.append(Finding("TR-SIG-002", Status.FAIL, "TR-SIG-002: cnf.jwk.x is missing"))
        return findings

    body = _canonical_json({k: v for k, v in record.items() if k != "signature"})
    ok, msg = _verify_ed25519(x, sig, body)
    status = Status.PASS if ok else Status.FAIL
    findings.append(Finding("TR-SIG-001", status, msg))
    return findings


def check(trace: dict[str, Any], record: dict[str, Any], fmt: str) -> list[Finding]:
    """Return TR-SIG findings. *record* is the full raw dict, *trace* is the extracted TRACE fields."""
    if fmt == "cmcp-runtime":
        return check_cmcp_runtime(record)

    # Plain trace format: verify key type alignment only; JWS/COSE verification not yet implemented.
    jwk = trace.get("cnf", {}).get("jwk", {})
    kty = jwk.get("kty")
    crv = jwk.get("crv")

    if kty in _SUPPORTED_KTY:
        label = f"kty={kty!r}" + (f", crv={crv!r}" if crv else "")
        return [
            Finding("TR-SIG-004", Status.PASS, f"cnf.jwk key type is supported ({label})"),
            Finding(
                "TR-SIG-005",
                Status.SKIP,
                "Full JWS/COSE signature verification requires a signed EAT token (not a plain JSON record)",
            ),
        ]

    if kty is None:
        return [Finding("TR-SIG-004", Status.FAIL, "TR-SIG-004: cnf.jwk.kty is missing")]

    return [Finding("TR-SIG-004", Status.FAIL, f"TR-SIG-004: unsupported key type {kty!r}; expected one of {sorted(_SUPPORTED_KTY)}")]
