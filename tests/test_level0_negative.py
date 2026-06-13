"""Level 0 negative conformance tests.

Each test mutates one field of a valid fixture and asserts that either the
JSON Schema validator or the relevant conformance module rejects it. All
assertions check for FAIL / ValidationError -- never PASS.

Coverage:
- Bad digest format on build_provenance.digest (sha512 prefix; wrong hex length)
- Bad digest format on tool_transcript.hash (sha512 prefix; wrong hex length)
- iat in the future (now + 3600) rejected by TR-ENV-002
- Unknown platform value rejected by schema enum and TR-RTE-001
- slsa_level out of range (4 and -1) rejected by schema and TR-SCA-001
- transparency with http:// rejected by TR-ANC-001
- Missing build_provenance rejected by schema (runtime already covered in test_schema.py)
"""

from __future__ import annotations

import copy
import time

import jsonschema
import pytest

from trace_tests.modules import tr_anc, tr_env, tr_rte, tr_sca
from trace_tests.result import Status


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mutate(base: dict, *path_and_value) -> dict:
    """Return a deep copy of *base* with one nested key replaced.

    Usage: _mutate(base, "runtime", "platform", "bad-value")
    The last argument is the value; all preceding arguments are keys.
    """
    *keys, value = path_and_value
    record = copy.deepcopy(base)
    node = record
    for k in keys[:-1]:
        node = node[k]
    node[keys[-1]] = value
    return record


def _delete(base: dict, *keys) -> dict:
    """Return a deep copy of *base* with the nested key at *keys removed."""
    record = copy.deepcopy(base)
    node = record
    for k in keys[:-1]:
        node = node[k]
    del node[keys[-1]]
    return record


# ---------------------------------------------------------------------------
# Bad digest format
# ---------------------------------------------------------------------------

@pytest.mark.level0
@pytest.mark.negative
class TestBadDigestFormat:
    """Digest fields must match sha256:<64hex> or sha384:<96hex> exactly."""

    # -- build_provenance.digest --

    def test_build_digest_sha512_prefix_fails_schema(self, schema, valid_level0):
        bad = _mutate(valid_level0, "build_provenance", "digest",
                      "sha512:" + "a" * 128)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)

    def test_build_digest_wrong_hex_length_fails_schema(self, schema, valid_level0):
        # sha256 prefix but only 32 hex chars (should be 64)
        bad = _mutate(valid_level0, "build_provenance", "digest",
                      "sha256:" + "a" * 32)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)

    def test_build_digest_sha512_prefix_fails_conformance(self, valid_level0):
        bad = _mutate(valid_level0, "build_provenance", "digest",
                      "sha512:" + "a" * 128)
        findings = tr_sca.check(bad)
        digest_findings = [f for f in findings if f.code == "TR-SCA-002"]
        assert digest_findings, "TR-SCA-002 finding expected"
        assert all(f.failed() for f in digest_findings), (
            f"sha512-prefixed digest must fail TR-SCA-002; got {digest_findings}"
        )

    def test_build_digest_wrong_hex_length_fails_conformance(self, valid_level0):
        bad = _mutate(valid_level0, "build_provenance", "digest",
                      "sha256:" + "a" * 32)
        findings = tr_sca.check(bad)
        digest_findings = [f for f in findings if f.code == "TR-SCA-002"]
        assert digest_findings, "TR-SCA-002 finding expected"
        assert all(f.failed() for f in digest_findings), (
            f"Wrong-length digest must fail TR-SCA-002; got {digest_findings}"
        )

    # -- tool_transcript.hash --

    def test_transcript_hash_sha512_prefix_fails_schema(self, schema, valid_level0_with_transcript):
        bad = _mutate(valid_level0_with_transcript, "tool_transcript", "hash",
                      "sha512:" + "a" * 128)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)

    def test_transcript_hash_wrong_hex_length_fails_schema(self, schema, valid_level0_with_transcript):
        bad = _mutate(valid_level0_with_transcript, "tool_transcript", "hash",
                      "sha256:" + "a" * 32)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)


# ---------------------------------------------------------------------------
# iat in the future
# ---------------------------------------------------------------------------

@pytest.mark.level0
@pytest.mark.negative
class TestFutureIat:
    """iat more than 60 seconds in the future must be rejected by TR-ENV-002."""

    def test_future_iat_fails_conformance(self, valid_level0):
        future_iat = int(time.time()) + 3600
        bad = _mutate(valid_level0, "iat", future_iat)
        findings = tr_env.check(bad)
        iat_findings = [f for f in findings if f.code == "TR-ENV-002"]
        assert iat_findings, "TR-ENV-002 finding expected"
        assert all(f.failed() for f in iat_findings), (
            f"Future iat must fail TR-ENV-002; got {iat_findings}"
        )

    def test_future_iat_finding_mentions_future(self, valid_level0):
        future_iat = int(time.time()) + 3600
        bad = _mutate(valid_level0, "iat", future_iat)
        findings = tr_env.check(bad)
        iat_findings = [f for f in findings if f.code == "TR-ENV-002" and f.failed()]
        assert iat_findings, "Expected a TR-ENV-002 FAIL finding"
        assert any("future" in f.message.lower() for f in iat_findings), (
            "TR-ENV-002 failure message must mention 'future'"
        )


# ---------------------------------------------------------------------------
# Unknown platform
# ---------------------------------------------------------------------------

@pytest.mark.level0
@pytest.mark.negative
class TestUnknownPlatform:
    """runtime.platform must be one of the registered values."""

    def test_unknown_platform_fails_schema(self, schema, valid_level0):
        bad = _mutate(valid_level0, "runtime", "platform", "quantum-chip")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)

    def test_unknown_platform_fails_conformance(self, valid_level0):
        bad = _mutate(valid_level0, "runtime", "platform", "quantum-chip")
        findings = tr_rte.check(bad)
        platform_findings = [f for f in findings if f.code == "TR-RTE-001"]
        assert platform_findings, "TR-RTE-001 finding expected"
        assert all(f.failed() for f in platform_findings), (
            f"Unknown platform must fail TR-RTE-001; got {platform_findings}"
        )


# ---------------------------------------------------------------------------
# slsa_level out of range
# ---------------------------------------------------------------------------

@pytest.mark.level0
@pytest.mark.negative
class TestSlsaLevelOutOfRange:
    """build_provenance.slsa_level must be 1, 2, or 3."""

    def test_slsa_level_4_fails_schema(self, schema, valid_level0):
        bad = _mutate(valid_level0, "build_provenance", "slsa_level", 4)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)

    def test_slsa_level_negative_fails_schema(self, schema, valid_level0):
        bad = _mutate(valid_level0, "build_provenance", "slsa_level", -1)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)

    def test_slsa_level_4_fails_conformance(self, valid_level0):
        bad = _mutate(valid_level0, "build_provenance", "slsa_level", 4)
        findings = tr_sca.check(bad)
        slsa_findings = [f for f in findings if f.code == "TR-SCA-001"]
        assert slsa_findings, "TR-SCA-001 finding expected"
        assert all(f.failed() for f in slsa_findings), (
            f"slsa_level=4 must fail TR-SCA-001; got {slsa_findings}"
        )

    def test_slsa_level_negative_fails_conformance(self, valid_level0):
        bad = _mutate(valid_level0, "build_provenance", "slsa_level", -1)
        findings = tr_sca.check(bad)
        slsa_findings = [f for f in findings if f.code == "TR-SCA-001"]
        assert slsa_findings, "TR-SCA-001 finding expected"
        assert all(f.failed() for f in slsa_findings), (
            f"slsa_level=-1 must fail TR-SCA-001; got {slsa_findings}"
        )


# ---------------------------------------------------------------------------
# transparency URI with http://
# ---------------------------------------------------------------------------

@pytest.mark.level0
@pytest.mark.negative
class TestTransparencyHttpUri:
    """transparency must be an https URI; bare http must be rejected."""

    def test_http_transparency_fails_conformance(self, valid_level0):
        bad = _mutate(valid_level0, "transparency",
                      "http://scitt.example.org/receipts/abc123")
        findings = tr_anc.check(bad)
        anc_findings = [f for f in findings if f.code == "TR-ANC-001"]
        assert anc_findings, "TR-ANC-001 finding expected"
        assert all(f.failed() for f in anc_findings), (
            f"http transparency URI must fail TR-ANC-001; got {anc_findings}"
        )

    def test_http_transparency_finding_mentions_scheme(self, valid_level0):
        bad = _mutate(valid_level0, "transparency",
                      "http://scitt.example.org/receipts/abc123")
        findings = tr_anc.check(bad)
        fail_findings = [f for f in findings if f.code == "TR-ANC-001" and f.failed()]
        assert fail_findings, "Expected a TR-ANC-001 FAIL finding"
        assert any("http" in f.message.lower() for f in fail_findings), (
            "TR-ANC-001 failure message must reference the invalid scheme"
        )


# ---------------------------------------------------------------------------
# Missing required field: build_provenance
# (runtime is already covered in test_schema.py::test_missing_runtime_rejected)
# ---------------------------------------------------------------------------

@pytest.mark.level0
@pytest.mark.negative
class TestMissingRequiredFields:
    """Records missing required top-level fields must fail schema validation."""

    def test_missing_build_provenance_fails_schema(self, schema, valid_level0):
        bad = _delete(valid_level0, "build_provenance")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)

    def test_missing_build_provenance_fails_conformance(self, valid_level0):
        bad = _delete(valid_level0, "build_provenance")
        findings = tr_sca.check(bad)
        assert findings, "TR-SCA findings expected when build_provenance is absent"
        assert all(f.failed() for f in findings), (
            f"Missing build_provenance must produce only FAIL findings; got {findings}"
        )

    def test_missing_transparency_fails_conformance(self, valid_level0):
        bad = _delete(valid_level0, "transparency")
        findings = tr_anc.check(bad)
        assert findings, "TR-ANC findings expected when transparency is absent"
        assert all(f.failed() for f in findings), (
            f"Missing transparency must produce only FAIL findings; got {findings}"
        )
