# TRACE Test Suite

Conformance tests for [TRACE](https://trace.agentrust-io.com) (Trust, Runtime Attestation, and Compliance Evidence). Run this suite against your implementation to verify it meets the specification before claiming TRACE compliance.

**Seven modules cover the full specification: envelope structure, signature algorithms, TEE runtime claims, policy binding, tool-call transcripts, SCITT transparency anchoring, and supply-chain provenance.**

TL;DR

- `verify` answers a question for the person running it. `report` produces an artifact for somebody who was not there.
- `report` runs every level up to `--max-level`, because the useful answer is the highest level a record reaches, not whether it cleared the level someone happened to pick.
- The HTML report is self-contained: no scripts, no fonts, no external CSS, no badge service, nothing fetched when it is opened.
- The report is not evidence, and it says so on its face. It carries the record digest, the suite and library versions, and the command to reproduce the result.

```
pip install agentrust-trace-tests
trace-tests verify --record path/to/trust-record.jwt --level 1
```

## A report you can hand to someone else

```
trace-tests report --record trust-record.json --html report.html --json report.json --badge trace.svg
```

Use `--fail-under 1` to gate CI on a level. Without it the command always exits `0`, which is what you want when you are producing an artifact rather than enforcing a threshold. `report.json` is stable under `schema: agentrust-io/trace-tests/report/1` for dashboards and CI.

A conformance report that looks authoritative and cannot be checked is the same shape of thing as a control plane writing its own log. So the report tells a reader who does not trust the sender to go and check the record instead, and gives them what they need to do it.

## Where to start

- **Run it**

  ______________________________________________________________________

  Score a record, read the failures, and produce a report from the same run.

  [Getting Started](https://tests.agentrust-io.com/docs/quickstart/index.md)

- **Understand the levels**

  ______________________________________________________________________

  What each conformance level requires, and what a record has to carry to reach it.

  [Conformance Levels](https://tests.agentrust-io.com/docs/levels/index.md)

- **Read the modules**

  ______________________________________________________________________

  The seven test modules, the `TR-*` error codes they emit, and what each one checks.

  [Test Modules](https://tests.agentrust-io.com/docs/modules/index.md)

- **Wire it into CI**

  ______________________________________________________________________

  Gate a pipeline on a level, and write your own conformance tests against the suite.

  [CI integration](https://tests.agentrust-io.com/docs/tutorials/ci-integration/index.md)

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

The suite tracks [TRACE Spec v0.2](https://trace.agentrust-io.com). See [Changelog](https://tests.agentrust-io.com/CHANGELOG/index.md) for what moved between suite versions.
