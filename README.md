# TRACE Conformance Test Suite

Conformance tests for TRACE v0.1 — Trust, Runtime Attestation, and Compliance Evidence. An implementation producing Trust Records must pass all tests in the applicable level before using the "TRACE-conformant" mark.

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
- A **positive case** — valid input, expected result: `PASS`
- A **negative case** — invalid input, expected result: `FAIL` with a structured error code

Error codes follow the form `TR-<MODULE>-<NNN>` (e.g., `TR-ENV-001`: missing `eat_profile`).

## Status

Test suite v0.1 — in development. Targeting initial release alongside the TRACE spec at Confidential Computing Summit, June 23 2026. Certification program launching 2027.

## Contributing

Open an issue or PR. New tests must include the normative spec reference, a positive case, and a negative case.

## License

Apache 2.0
