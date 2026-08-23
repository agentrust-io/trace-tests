# Error Codes

All TRACE test failures emit a structured error code of the form `TR-<MODULE>-<NNN>`.

## TR-ENV — Envelope

| Code       | Description                                                                                        | How to fix                                                                                                                                 |
| ---------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| TR-ENV-001 | Missing or invalid `eat_profile` URI                                                               | Set `eat_profile` to `"tag:agentrust-io.com,2026:trace-v0.2"`                                                                              |
| TR-ENV-002 | `iat` is missing, not an integer, or out of range                                                  | Set `iat` to a Unix timestamp integer (e.g. `int(time.time())`)                                                                            |
| TR-ENV-003 | `subject` does not match SPIFFE URI or DID pattern                                                 | Use `spiffe://<trust-domain>/<path>` or a `did:` URI                                                                                       |
| TR-ENV-004 | `cnf` is absent or not an object, `cnf.jwk` is absent or not an object, or `cnf.jwk.kty` is absent | Populate `cnf.jwk` with at least `kty`. This checks that one field, not the schema's full required set, which structural validation covers |

## TR-SIG — Signature

| Code       | Description                                                                                                                                                                                                                   | How to fix                                                                                                                                                                                                  |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TR-SIG-001 | Signature algorithm is not Ed25519                                                                                                                                                                                            | Generate an Ed25519 key (`generate_key()`) and re-sign; ES256 and RS256 are not accepted                                                                                                                    |
| TR-SIG-002 | `cnf.jwk` missing or malformed                                                                                                                                                                                                | Populate `cnf.jwk` with the OKP public key `{"kty":"OKP","crv":"Ed25519","x":"..."}` — `sign_record()` does this automatically                                                                              |
| TR-SIG-003 | Signature verification failed                                                                                                                                                                                                 | Re-sign the record with `sign_record(record, key)`; the record fields must not have changed after signing                                                                                                   |
| TR-SIG-004 | `cnf.jwk.kty` is missing, or names a key type this suite does not support (`OKP` and `EC` are accepted)                                                                                                                       | Embed a supported public JWK. Ed25519 signature verification additionally requires `kty: "OKP"` with `crv: "Ed25519"`; a supported key that is not that pair passes this check and fails TR-SIG-005         |
| TR-SIG-005 | The signature check outcome: the Ed25519 verification result, a signature that cannot be verified, or no signature at all. With no signature it is FAIL at Level 1 and above and `UNVERIFIED` at Level 0, which is not a pass | Sign the record with `sign_record(record, key)` and do not change the signed fields afterwards. An unsigned record is reported as unverified rather than skipped, so it cannot be read as a benign omission |

## TR-RTE — Runtime

| Code       | Description                                                                                                                           | How to fix                                                                                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TR-RTE-001 | `runtime` is missing or not an object, or `runtime.platform` is not in the registered set, or is `software-only` at Level 1 and above | Use a value from the `runtime.platform` enum in `schemas/trace-claim.json`. `software-only` carries no hardware attestation evidence and is accepted only at Level 0   |
| TR-RTE-002 | `runtime.measurement` is not a valid `sha256:` digest                                                                                 | Provide a 64-character hex digest prefixed with `sha256:`; for Level 0 all-zeros is conventional                                                                       |
| TR-RTE-003 | `runtime.rim_uri` is present and is not an `https://` URI                                                                             | Remove `runtime.rim_uri` if not using a RIM, or set it to an `https://` URI. The URI is not resolved and the manifest behind it is not checked; this is a format check |

## TR-POL — Policy

| Code       | Description                                                                     | How to fix                                                                                                                                                        |
| ---------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TR-POL-001 | `policy.bundle_hash` is not a valid `sha256:` digest                            | Compute `sha256:` + hex digest of your Cedar policy bundle bytes                                                                                                  |
| TR-POL-002 | `policy.enforcement_mode` is not `enforce`, `advisory`, `silent`, or `declared` | Replace `"strict"` or `"monitor"` with one of the four accepted values; `"declared"` is the honest value for a producer that binds a policy without evaluating it |

## TR-TXN — Transcript

| Code       | Description                                                | How to fix                                                                                              |
| ---------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| TR-TXN-001 | `tool_transcript.hash` is not a valid `sha256:` digest     | Set `tool_transcript.hash` to `sha256:` + 64 hex chars of the Merkle root of the tool call log          |
| TR-TXN-002 | `tool_transcript.call_count` is negative or not an integer | Set `tool_transcript.call_count` to a non-negative integer (0 is valid for sessions with no tool calls) |

## TR-ANC — Transparency

| Code       | Description                                                                                 | How to fix                                                                                                                                                                                 |
| ---------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| TR-ANC-001 | `transparency` is absent or empty, is not a string, or is not an `https://` URI with a host | Submit the record to a SCITT transparency log and set `transparency` to the returned receipt URI. The URI is not resolved and the receipt behind it is not fetched; this is a format check |

## TR-SCA — Provenance

| Code       | Description                                               | How to fix                                                                                          |
| ---------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| TR-SCA-001 | `build_provenance.slsa_level` is not 0–3                  | Set `build_provenance.slsa_level` to an integer 0–3 matching your SLSA build level                  |
| TR-SCA-002 | `build_provenance.digest` is not a valid `sha256:` digest | Set `build_provenance.digest` to `sha256:` + 64 hex chars of the container image or artifact digest |
