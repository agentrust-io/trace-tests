# Quick Start

## Install

```
pip install agentrust-trace-tests
```

The distribution is `agentrust-trace-tests`; `trace-tests` is the command it installs. `pip install trace-tests` returns 404.

## Create a sample fixture

The test suite runs against a signed TRACE Trust Record. Generate a Level 0 development record with the `agentrust-trace` library:

```
pip install agentrust-trace
```

```
# generate_sample.py
import time, json
from agentrust_trace import generate_key, sign_record

key = generate_key()

record = {
    "eat_profile": "tag:agentrust-io.com,2026:trace-v0.2",
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
    "transparency": "https://registry.agentrust-io.com/claim/placeholder",
}

signed = sign_record(record, key)

with open("sample-record.json", "w") as f:
    json.dump(signed, f, indent=2)

print("Wrote sample-record.json")
```

```
python generate_sample.py
```

`software-only` platform and all-zero measurement are the correct values for Level 0 development records. `generate_key()` produces a fresh Ed25519 key on each run; for CI use, load a persisted key via the `TRACE_PRIVATE_KEY_PEM` environment variable instead.

## Run against a Trust Record

```
trace-tests verify --record sample-record.json --level 0
```

Level 0 is software-only (development). Level 1 requires TEE attestation. Level 2 adds transparency anchoring.

## Run all levels

```
trace-tests verify --record sample-record.json --level 0
trace-tests verify --record sample-record.json --level 1
trace-tests verify --record sample-record.json --level 2
```

The sample fixture passes Level 0. Levels 1 and 2 will fail on runtime attestation and transparency fields — that is expected. See [Trust Levels](https://tests.agentrust-io.com/docs/levels/index.md) for what each level requires.

## Exit codes

| Code | Meaning                    |
| ---- | -------------------------- |
| 0    | All required tests passed  |
| 1    | One or more tests failed   |
| 2    | Record could not be loaded |

## Output format

Each finding prints its **module**, its status, and its message:

```
  TR-ENV  PASS        eat_profile sentinel matches
  TR-ENV  PASS        cnf.jwk.kty present ('EC')
  TR-SIG  PASS        cnf.jwk key type is supported (kty='EC', crv='P-256')
  TR-SIG  UNVERIFIED  TR-SIG-005: no signature present; this record is NOT cryptographically verified
  TR-POL  PASS        policy.bundle_hash has valid digest format
```

Error codes follow the form `TR-<MODULE>-<NNN>`. A failing or unverified finding carries its code at the front of the message; a passing one usually does not, so the module column is what identifies a `PASS`. The JSON and HTML reports carry the code as its own field for every finding.

## Next steps

| What                             | Where                                                                                                                   |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Understand what each test checks | [Test Modules](https://tests.agentrust-io.com/docs/modules/index.md)                                                    |
| Look up a specific error code    | [Error Codes](https://tests.agentrust-io.com/docs/error-codes/index.md)                                                 |
| Write your own conformance tests | [Tutorial: Writing conformance tests](https://tests.agentrust-io.com/docs/tutorials/writing-conformance-tests/index.md) |
| Set up CI                        | [Tutorial: CI integration](https://tests.agentrust-io.com/docs/tutorials/ci-integration/index.md)                       |
