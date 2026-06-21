# Quick Start

## Install

```bash
pip install trace-tests
```

## Create a sample fixture

The test suite runs against a signed TRACE Trust Record. Generate a Level 0 development record with the `agentrust-trace` library:

```bash
pip install agentrust-trace
```

```python
# generate_sample.py
import time, json
from agentrust_trace import generate_key, sign_record

key = generate_key()

record = {
    "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
    "iat": int(time.time()),
    "subject": "spiffe://trust.example.org/agent/sample",
    "model": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-6",
        "version": "20251001",
    },
    "runtime": {
        "platform": "software-only",
        "measurement": "sha256:" + "0" * 64,
    },
    "policy": {
        "bundle_hash": "sha256:b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7"
                       "f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
        "enforcement_mode": "enforce",
    },
    "data_class": "internal",
    "build_provenance": {
        "slsa_level": 1,
        "digest": "sha256:e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
                  "c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6",
    },
    "appraisal": {
        "status": "none",
        "verifier": "https://verifier.example.org",
    },
    "transparency": "https://registry.agentrust.io/claim/placeholder",
}

signed = sign_record(record, key)

with open("sample-record.json", "w") as f:
    json.dump(signed, f, indent=2)

print("Wrote sample-record.json")
```

```bash
python generate_sample.py
```

`software-only` platform and all-zero measurement are the correct values for Level 0 development records. `generate_key()` produces a fresh Ed25519 key on each run; for CI use, load a persisted key via the `TRACE_PRIVATE_KEY_PEM` environment variable instead.

## Run against a Trust Record

```bash
trace-tests verify --record sample-record.json --level 0
```

Level 0 is software-only (development). Level 1 requires TEE attestation. Level 2 adds transparency anchoring.

## Run all levels

```bash
trace-tests verify --record sample-record.json --level 0
trace-tests verify --record sample-record.json --level 1
trace-tests verify --record sample-record.json --level 2
```

The sample fixture passes Level 0. Levels 1 and 2 will fail on runtime attestation and transparency fields — that is expected. See [Trust Levels](levels.md) for what each level requires.

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

## Next steps

| What | Where |
|------|-------|
| Understand what each test checks | [Test Modules](modules/index.md) |
| Look up a specific error code | [Error Codes](error-codes.md) |
| Write your own conformance tests | [Tutorial: Writing conformance tests](tutorials/writing-conformance-tests.md) |
| Set up CI | [Tutorial: CI integration](tutorials/ci-integration.md) |
