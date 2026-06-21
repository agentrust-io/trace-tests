# Error Codes

All TRACE test failures emit a structured error code of the form `TR-<MODULE>-<NNN>`.

## TR-ENV — Envelope

| Code | Description | How to fix |
|------|-------------|------------|
| TR-ENV-001 | Missing or invalid `eat_profile` URI | Set `eat_profile` to `"tag:agentrust.io,2026:trace-v0.1"` |
| TR-ENV-002 | `iat` is missing, not an integer, or out of range | Set `iat` to a Unix timestamp integer (e.g. `int(time.time())`) |
| TR-ENV-003 | `subject` does not match SPIFFE URI or DID pattern | Use `spiffe://<trust-domain>/<path>` or a `did:` URI |
| TR-ENV-004 | One or more required fields are absent | Add the missing field(s); check the [Schema Reference](https://trace.agentrust-io.com/schema) for the full required set |

## TR-SIG — Signature

| Code | Description | How to fix |
|------|-------------|------------|
| TR-SIG-001 | Signature algorithm is not Ed25519 | Generate an Ed25519 key (`generate_key()`) and re-sign; ES256 and RS256 are not accepted |
| TR-SIG-002 | `cnf.jwk` missing or malformed | Populate `cnf.jwk` with the OKP public key `{"kty":"OKP","crv":"Ed25519","x":"..."}` — `sign_record()` does this automatically |
| TR-SIG-003 | Signature verification failed | Re-sign the record with `sign_record(record, key)`; the record fields must not have changed after signing |
| TR-SIG-004 | Private key material (`d` member) found in `cnf.jwk` | Remove the `d` field before embedding the JWK; `key_to_jwk()` returns the public-only form |

## TR-RTE — Runtime

| Code | Description | How to fix |
|------|-------------|------------|
| TR-RTE-001 | `runtime.platform` is not a recognised TEE enum value | Use one of: `software-only`, `tpm2`, `sev-snp`, `tdx`, `opaque` |
| TR-RTE-002 | `runtime.measurement` is not a valid `sha256:` digest | Provide a 64-character hex digest prefixed with `sha256:`; for Level 0 all-zeros is conventional |
| TR-RTE-003 | RIM URI present but does not resolve to a valid reference image | Remove `runtime.rim_uri` if not using a RIM, or ensure the URI returns a valid reference manifest over HTTPS |

## TR-POL — Policy

| Code | Description | How to fix |
|------|-------------|------------|
| TR-POL-001 | `policy.bundle_hash` is not a valid `sha256:` digest | Compute `sha256:` + hex digest of your Cedar policy bundle bytes |
| TR-POL-002 | `policy.enforcement_mode` is not `enforce`, `advisory`, or `silent` | Replace `"strict"` or `"monitor"` with `"enforce"`, `"advisory"`, or `"silent"` |

## TR-TXN — Transcript

| Code | Description | How to fix |
|------|-------------|------------|
| TR-TXN-001 | `tool_transcript.hash` is not a valid `sha256:` digest | Set `tool_transcript.hash` to `sha256:` + 64 hex chars of the Merkle root of the tool call log |
| TR-TXN-002 | `tool_transcript.call_count` is negative or not an integer | Set `tool_transcript.call_count` to a non-negative integer (0 is valid for sessions with no tool calls) |

## TR-ANC — Transparency

| Code | Description | How to fix |
|------|-------------|------------|
| TR-ANC-001 | `transparency` field missing or empty | Submit the record to a SCITT transparency log and set `transparency` to the returned receipt URI |
| TR-ANC-002 | `transparency` URI does not use `https://` scheme | Only `https://` URIs are accepted; update the URI or use the agentrust registry at `https://registry.agentrust.io` |

## TR-SCA — Provenance

| Code | Description | How to fix |
|------|-------------|------------|
| TR-SCA-001 | `build_provenance.slsa_level` is not 0–4 | Set `build_provenance.slsa_level` to an integer 0–4 matching your SLSA build level |
| TR-SCA-002 | `build_provenance.digest` is not a valid `sha256:` digest | Set `build_provenance.digest` to `sha256:` + 64 hex chars of the container image or artifact digest |
