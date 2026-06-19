# Error Codes

All TRACE test failures emit a structured error code of the form `TR-<MODULE>-<NNN>`.

## TR-ENV — Envelope

| Code | Description |
|------|-------------|
| TR-ENV-001 | Missing or invalid `eat_profile` URI |
| TR-ENV-002 | `iat` is missing, not an integer, or out of range |
| TR-ENV-003 | `subject` does not match SPIFFE URI or DID pattern |
| TR-ENV-004 | One or more required fields are absent |

## TR-SIG — Signature

| Code | Description |
|------|-------------|
| TR-SIG-001 | Signature algorithm is not Ed25519 |
| TR-SIG-002 | `cnf.jwk` missing or malformed |
| TR-SIG-003 | Signature verification failed |
| TR-SIG-004 | Private key material (`d` member) found in `cnf.jwk` |

## TR-RTE — Runtime

| Code | Description |
|------|-------------|
| TR-RTE-001 | `runtime.platform` is not a recognised TEE enum value |
| TR-RTE-002 | `runtime.measurement` is not a valid `sha256:` digest |

## TR-POL — Policy

| Code | Description |
|------|-------------|
| TR-POL-001 | `policy.bundle_hash` is not a valid `sha256:` digest |
| TR-POL-002 | `policy.enforcement_mode` is not `enforce` or `monitor` |

## TR-TXN — Transcript

| Code | Description |
|------|-------------|
| TR-TXN-001 | `tool_transcript.hash` is not a valid `sha256:` digest |
| TR-TXN-002 | `tool_transcript.call_count` is negative or not an integer |

## TR-ANC — Transparency

| Code | Description |
|------|-------------|
| TR-ANC-001 | `transparency` field missing or empty |
| TR-ANC-002 | `transparency` URI does not use `https://` scheme |

## TR-SCA — Provenance

| Code | Description |
|------|-------------|
| TR-SCA-001 | `build_provenance.slsa_level` is not 0–4 |
| TR-SCA-002 | `build_provenance.digest` is not a valid `sha256:` digest |
