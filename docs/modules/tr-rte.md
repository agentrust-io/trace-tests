# TR-RTE — Runtime

Tests TEE platform attestation in the `runtime` field.

## Required at Level 1+

| Test ID | Description |
|---------|-------------|
| TR-RTE-001 | `runtime.platform` is a known TEE enum value |
| TR-RTE-002 | `runtime.measurement` is a valid `sha256:` digest |
| TR-RTE-003 | RIM URI (if present) resolves to a valid reference image |
