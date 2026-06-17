[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![TRACE Spec](https://img.shields.io/badge/TRACE-Spec_v0.2-0ea5e9)](https://github.com/agentrust-io/trace-spec)
[![Tests](https://img.shields.io/badge/Conformance_Tests-7_modules-green)]()
[![Discord](https://dcbadge.limes.pink/api/server/9JWNpH7E?style=flat)](https://discord.gg/9JWNpH7E)

# TRACE Conformance Test Suite

Conformance tests for TRACE v0.2 - Trust, Runtime Attestation, and Compliance Evidence. An implementation producing Trust Records must pass all tests in the applicable level before using the "TRACE-conformant" mark.

If you are building a gateway, agent runtime, or orchestration layer that produces TRACE records, run this suite against your output to verify conformance before claiming TRACE compliance.

## Test modules

| Module | ID prefix | Spec section | What it tests |
|---|---|---|---|
| Envelope | `TR-ENV` | §3.2 | EAT envelope structure, `eat_profile` URI, required fields, `iat` validity |
| Signature | `TR-SIG` | §3.2.1 | Algorithm conformance (ES256/ES384/EdDSA), key binding, chain verification |
| Runtime | `TR-RTE` | §3.1 | TEE platform enum, measurement format, RIM URI resolution |
| Policy | `TR-POL` | §3.1 | Policy bundle hash format, enforcement mode values, TEE binding |
| Transcript | `TR-TXN` | §3.1 | Tool-call transcript hash binding (Phase 2+ records) |
| Transparency | `TR-ANC` | §3.2 | SCITT receipt URI format, inclusion proof structure |
| Provenance | `TR-SCA` | §3.1 | SLSA provenance level, builder URI, digest format |

## Conformance levels

| Level | Required modules | Use case |
|---|---|---|
| 0 | TR-ENV, TR-SIG, TR-POL | Software-only development and staging |
| 1 | Level 0 + TR-RTE, TR-SCA | Production TEE-attested records |
| 2 | Level 1 + TR-TXN, TR-ANC | Full records with transparency anchoring |

## Running

```bash
pip install trace-tests
trace-tests verify --record path/to/trust-record.jwt --level 1
```

## Test structure

Each test case includes:
- A normative reference to the spec section it exercises
- A **positive case** - valid input, expected result: `PASS`
- A **negative case** - invalid input, expected result: `FAIL` with a structured error code

Error codes follow the form `TR-<MODULE>-<NNN>` (e.g., `TR-ENV-001`: missing `eat_profile`).

## What changed in v0.2

- **DID subject support**: `subject` now accepts `did:` URIs in addition to `spiffe://`. TR-ENV-003 passes for both.
- **Embedded signature verification**: plain TRACE records signed with `agentrust-trace sign_record()` (Ed25519 embedded `signature` field) are now cryptographically verified at all levels. Previously marked UNVERIFIED.
- **SLSA Level 0**: `build_provenance.slsa_level: 0` is now valid (software-only / development records).
- **Software-only platform**: `runtime.platform: "software-only"` accepted at Level 0.

## Status

Test suite v0.2. The TRACE spec published at Confidential Computing Summit, June 23 2026. The certification program is on a separate timeline, launching 2027.

## Contributing

Open an issue or PR. New tests must include the normative spec reference, a positive case, and a negative case.

Join the community on [Discord](https://discord.gg/9JWNpH7E).

## License

Apache 2.0