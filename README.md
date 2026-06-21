<p align="center">
  <img src="docs/assets/icon.svg" width="96" height="96" alt="TRACE Tests"/>
</p>

# TRACE Conformance Test Suite

### Verify your TRACE implementation before shipping

<p align="center">
  <a href="https://tests.agentrust-io.com">
    <img src="https://img.shields.io/badge/%F0%9F%93%96_Full_Documentation-tests.agentrust--io.com-C17817?style=for-the-badge&logoColor=white" alt="Full Documentation" height="40">
  </a>
</p>

<p align="center">
  <a href="docs/quickstart.md">Quick Start</a> &nbsp;|&nbsp;
  <a href="docs/modules.md">Test Modules</a> &nbsp;|&nbsp;
  <a href="docs/levels.md">Conformance Levels</a> &nbsp;|&nbsp;
  <a href="CHANGELOG.md">Changelog</a>
</p>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![TRACE Spec](https://img.shields.io/badge/TRACE-Spec_v0.2-0ea5e9)](https://github.com/agentrust-io/trace-spec)
[![Tests](https://img.shields.io/badge/Conformance_Tests-7_modules-green)]()
[![CI](https://github.com/agentrust-io/trace-tests/actions/workflows/ci.yml/badge.svg)](https://github.com/agentrust-io/trace-tests/actions/workflows/ci.yml)
[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white&style=flat)](https://discord.gg/9JWNpH7E)

> **Test suite v0.2.** Tracks [TRACE Spec v0.2](https://github.com/agentrust-io/trace-spec).

Conformance tests for TRACE — Trust Runtime Attestation and Compliance Evidence. Run this suite against your implementation to verify it meets the spec before claiming TRACE compliance.

Seven test modules covering the full specification: envelope structure, signature algorithms, TEE runtime claims, policy binding, tool-call transcripts, SCITT transparency anchoring, and supply chain provenance.

## Quick start

```bash
pip install trace-tests
trace-tests verify --record path/to/trust-record.jwt --level 1
```

## Test modules

| Module | ID | Tests |
|---|---|---|
| Envelope | `TR-ENV` | EAT structure, required fields, `iat` validity |
| Signature | `TR-SIG` | ES256/ES384/EdDSA, key binding, chain |
| Runtime | `TR-RTE` | TEE platform, measurement format, RIM URI |
| Policy | `TR-POL` | Bundle hash, enforcement mode, TEE binding |
| Transcript | `TR-TXN` | Tool-call transcript hash binding (Phase 2+) |
| Transparency | `TR-ANC` | SCITT receipt URI, inclusion proof |
| Provenance | `TR-SCA` | SLSA level, builder URI, digest format |

## Resources

| | |
|---|---|
| 📖 Full documentation | [tests.agentrust-io.com](https://tests.agentrust-io.com) |
| 📄 TRACE Specification | [trace-spec](https://github.com/agentrust-io/trace-spec) |
| 🗂 Test schemas | [schemas/](schemas/) |
| 💬 Discussions | [GitHub Discussions](https://github.com/orgs/agentrust-io/discussions) |
| 📋 Changelog | [CHANGELOG.md](CHANGELOG.md) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New test cases must include a normative spec reference, a positive case, and a negative case with a structured error code (`TR-<MODULE>-<NNN>`).
