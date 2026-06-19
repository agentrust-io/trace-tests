# TR-ENV — Envelope

Tests the top-level EAT envelope structure of a TRACE Trust Record.

## Required at Level 0+

| Test ID | Description | Positive Case | Negative Case |
|---------|-------------|---------------|---------------|
| TR-ENV-001 | `eat_profile` present and correct URI | `tag:agentrust.io,2026:trace-v0.1` | missing or wrong |
| TR-ENV-002 | `iat` is a valid Unix timestamp | integer, reasonable range | string, future date |
| TR-ENV-003 | `subject` matches SPIFFE URI or DID | `spiffe://trust.example/agent/x` or `did:key:z6Mk...` | bare string |
| TR-ENV-004 | Required fields present | all of: eat_profile, iat, subject, model, runtime, policy, data_class, build_provenance, appraisal | missing any |
