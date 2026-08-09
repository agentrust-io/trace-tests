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

## A report you can hand to someone else

`verify` answers a question for the person running it. `report` produces an artifact for somebody who was not there: an auditor, a counterparty, an acquirer.

```
trace-tests report --record trust-record.json   --html report.html --json report.json --badge trace.svg
```

It runs **every** level up to `--max-level` rather than one, because the useful answer for a reader is the highest level the record reaches, not whether it cleared the level someone happened to pick. The HTML is self-contained: no scripts, no fonts, no external CSS, no badge service, nothing fetched at open time.

Use `--fail-under 1` to gate CI on a level. Without it the command always exits `0`, which is what you want when you are producing an artifact rather than enforcing a threshold.

**The report is not evidence, and it says so on its face.** It is unsigned HTML describing one run of one suite version, and anybody can edit it. So it carries the record's digest, the suite and library versions, and the exact command to reproduce the result. A reader who does not trust the sender is told, in the artifact, to go check the record instead. A conformance report that looks authoritative and cannot be checked is the same shape of thing as a control plane writing its own log.

`report.json` is stable under `schema: agentrust-io/trace-tests/report/1` for dashboards and CI.

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
