# Quick Start

## Install

```bash
pip install agentrust-trace-tests
```

## Run against a Trust Record

```bash
trace-tests verify --record path/to/trust-record.json --level 1
```

Level 0 is software-only (development). Level 1 requires TEE attestation. Level 2 adds transparency anchoring.

## Run all levels

```bash
trace-tests verify --record trust-record.json --level 0
trace-tests verify --record trust-record.json --level 1
trace-tests verify --record trust-record.json --level 2
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | All required tests passed |
| 1    | One or more tests failed |
| 2    | Record could not be loaded |

## Output format

Each test emits a structured result:

```
TR-ENV-001  PASS  EAT envelope: eat_profile present
TR-SIG-001  PASS  Signature: Ed25519 algorithm confirmed
TR-RTE-001  FAIL  Runtime: TEE measurement missing (required at level 1)
```

Error codes follow the form `TR-<MODULE>-<NNN>`.
