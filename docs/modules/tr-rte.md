# TR-RTE — Runtime

Tests TEE platform attestation in the `runtime` field.

## Required at Level 1+

| Test ID | Description | Positive Case | Negative Case |
|---------|-------------|---------------|---------------|
| TR-RTE-001 | `runtime.platform` is a known TEE enum value | `tpm2`, `sev-snp`, `tdx`, `opaque` | `"software"`, `"cloud"`, absent |
| TR-RTE-002 | `runtime.measurement` is a valid `sha256:` digest | `sha256:` followed by 64 hex chars | missing, wrong prefix, all zeros |
| TR-RTE-003 | RIM URI (if present) resolves to a valid reference image | valid `https://` URI returning a reference manifest | non-HTTPS URI, 404 response |
