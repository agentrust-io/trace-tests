# TRACE Conformance Test Suite

### Verify your TRACE implementation before shipping

[Quick Start](https://tests.agentrust-io.com/docs/quickstart.md)  |  [Test Modules](https://tests.agentrust-io.com/docs/modules.md)  |  [Conformance Levels](https://tests.agentrust-io.com/docs/levels.md)  |  [Changelog](https://tests.agentrust-io.com/CHANGELOG.md)

> **Test suite v0.2.** Tracks [TRACE Spec v0.2](https://github.com/agentrust-io/trace-spec).

Conformance tests for TRACE (Trust Runtime Attestation and Compliance Evidence). Run this suite against your implementation to verify it meets the spec before claiming TRACE compliance.

Seven test modules covering the full specification: envelope structure, signature algorithms, TEE runtime claims, policy binding, tool-call transcripts, SCITT transparency anchoring, and supply chain provenance.

## Quick start

```
pip install agentrust-trace-tests
trace-tests verify --record path/to/trust-record.jwt --level 1
```

## Test modules

| Module       | ID       | Tests                                          |
| ------------ | -------- | ---------------------------------------------- |
| Envelope     | `TR-ENV` | EAT structure, required fields, `iat` validity |
| Signature    | `TR-SIG` | ES256/ES384/EdDSA, key binding, chain          |
| Runtime      | `TR-RTE` | TEE platform, measurement format, RIM URI      |
| Policy       | `TR-POL` | Bundle hash, enforcement mode, TEE binding     |
| Transcript   | `TR-TXN` | Tool-call transcript hash binding (Phase 2+)   |
| Transparency | `TR-ANC` | SCITT receipt URI, inclusion proof             |
| Provenance   | `TR-SCA` | SLSA level, builder URI, digest format         |

## Resources

|                        |                                                                        |
| ---------------------- | ---------------------------------------------------------------------- |
| 📖 Full documentation  | [tests.agentrust-io.com](https://tests.agentrust-io.com)               |
| 📄 TRACE Specification | [trace-spec](https://github.com/agentrust-io/trace-spec)               |
| 🗂 Test schemas         | [schemas/](https://tests.agentrust-io.com/schemas/index.md)            |
| 💬 Discussions         | [GitHub Discussions](https://github.com/orgs/agentrust-io/discussions) |
| 📋 Changelog           | [CHANGELOG.md](https://tests.agentrust-io.com/CHANGELOG/index.md)      |

## Contributing

See [CONTRIBUTING.md](https://tests.agentrust-io.com/CONTRIBUTING/index.md). New test cases must include a normative spec reference, a positive case, and a negative case with a structured error code (`TR-<MODULE>-<NNN>`).
