import base64
import json
import pathlib
import time

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

VECTORS_DIR = pathlib.Path(__file__).parent / "vectors"
SCHEMAS_DIR = pathlib.Path(__file__).parent.parent / "schemas"


def load_vector(filename):
    return json.loads((VECTORS_DIR / filename).read_text())


def load_schema():
    return json.loads((SCHEMAS_DIR / "trace-claim.json").read_text())


def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def _canonical_json(d: dict) -> bytes:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _build_signed_cmcp_record(*, platform: str = "tpm2", nonce: str | None = None) -> tuple[dict, Ed25519PrivateKey]:
    """Return (record, private_key) for a fully-signed cmcp-runtime claim.

    The signature covers the canonical JSON of the envelope with the 'signature'
    field absent, matching the verification path in tr_sig.check_cmcp_runtime.
    """
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    pub_raw = pub.public_bytes_raw()
    x = _b64url(pub_raw)
    kid = f"test-{pub_raw[:4].hex()}"

    iat = int(time.time()) - 30  # fresh but not future-dated

    trace: dict = {
        "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
        "iat": iat,
        "subject": "spiffe://cmcp.gateway/session/conformance-test",
        "runtime": {
            "platform": platform,
            "measurement": "sha256:" + "a" * 64,
        },
        "policy": {
            "bundle_hash": "sha256:" + "b" * 64,
            "enforcement_mode": "enforce",
        },
        "data_class": "internal",
        "cnf": {"jwk": {"kty": "OKP", "crv": "Ed25519", "x": x, "kid": kid}},
    }

    if nonce is not None:
        trace["runtime"]["nonce"] = nonce

    record: dict = {
        "cmcp_version": "1.0",
        "trace": trace,
        "gateway": {"session_id": "conformance-test"},
        "signature": "",
    }

    body = _canonical_json({k: v for k, v in record.items() if k != "signature"})
    record["signature"] = _b64url(priv.sign(body))
    return record, priv


@pytest.fixture
def schema():
    return load_schema()


@pytest.fixture
def valid_level0():
    return load_vector("valid_level0.json")


@pytest.fixture
def valid_level0_with_transcript():
    return load_vector("valid_level0_with_transcript.json")


@pytest.fixture
def invalid_missing_runtime():
    return load_vector("invalid_missing_runtime.json")


@pytest.fixture
def invalid_wrong_profile():
    return load_vector("invalid_wrong_profile.json")


# ---------------------------------------------------------------------------
# Level 1 fixtures
# ---------------------------------------------------------------------------

_CHALLENGE_NONCE = _b64url(b"level1-conformance-nonce-01")


@pytest.fixture
def challenge_nonce() -> str:
    """A stable base64url nonce that the signed EAT fixture embeds in runtime.nonce."""
    return _CHALLENGE_NONCE


@pytest.fixture
def signed_eat_fixture() -> dict:
    """A valid, fully-signed cmcp-runtime envelope for Level 1 conformance tests."""
    record, _ = _build_signed_cmcp_record(platform="tpm2", nonce=_CHALLENGE_NONCE)
    return record


# ---------------------------------------------------------------------------
# Level 2 fixtures
# ---------------------------------------------------------------------------

# Measurement value used consistently across Level 2 fixtures.
_SW_MEASUREMENT = "sha256:" + "c" * 64


def _build_software_only_record() -> dict:
    """Build a signed cmcp-runtime record with platform='software-only' and a fixed measurement."""
    priv = Ed25519PrivateKey.generate()
    pub_raw = priv.public_key().public_bytes_raw()
    x = _b64url(pub_raw)
    kid = f"test-{pub_raw[:4].hex()}"
    iat = int(time.time()) - 30

    record: dict = {
        "cmcp_version": "1.0",
        "trace": {
            "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
            "iat": iat,
            "subject": "spiffe://cmcp.gateway/session/level2-test",
            "runtime": {
                "platform": "software-only",
                "measurement": _SW_MEASUREMENT,
            },
            "policy": {
                "bundle_hash": "sha256:" + "b" * 64,
                "enforcement_mode": "enforce",
            },
            "data_class": "internal",
            "cnf": {"jwk": {"kty": "OKP", "crv": "Ed25519", "x": x, "kid": kid}},
        },
        "gateway": {"session_id": "level2-test"},
        "signature": "",
    }
    body = _canonical_json({k: v for k, v in record.items() if k != "signature"})
    record["signature"] = _b64url(priv.sign(body))
    return record


@pytest.fixture
def trust_record() -> dict:
    """A software-only cmcp-runtime record for Level 2 fixture coverage.

    'software-only' is the development platform that carries no hardware TEE
    evidence. It is deliberately distinct from real attestation platforms so a
    consumer can never mistake it for hardware-backed evidence.
    """
    return _build_software_only_record()


@pytest.fixture
def attestation_report(trust_record: dict) -> dict:
    """A synthetic attestation report whose measurement matches trust_record.

    For software-only records there is no real TEE report; this fixture captures
    the structure that a hardware verifier would produce so Level 2 tests can
    exercise field-matching logic without real attestation hardware.
    """
    return {
        "platform": trust_record["trace"]["runtime"]["platform"],
        "measurement": trust_record["trace"]["runtime"]["measurement"],
        "freshness_nonce": _b64url(b"level2-freshness-nonce"),
        "timestamp": trust_record["trace"]["iat"],
        "cnf_key_x": trust_record["trace"]["cnf"]["jwk"]["x"],
    }
