# Conformance Levels

TRACE defines three conformance levels. Higher levels require all lower-level modules plus additional ones.

| Level | Required Modules | Use Case |
|-------|-----------------|----------|
| **0** | TR-ENV, TR-SIG, TR-POL | Software-only development and staging |
| **1** | Level 0 + TR-RTE, TR-SCA | Production TEE-attested records |
| **2** | Level 1 + TR-TXN, TR-ANC | Full records with transparency anchoring |

## Level 0 — Software-only

Level 0 records are signed with a software key. The `runtime.platform` must be `"software-only"`. All-zero measurement is conventional for development use.

**Minimum conformant Level 0 record:**

```json
{
  "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
  "iat": 1750000000,
  "subject": "spiffe://trust.example.org/agent/my-agent",
  "model": {
    "provider": "anthropic",
    "model_id": "claude-sonnet-4-6",
    "version": "20251001"
  },
  "runtime": {
    "platform": "software-only",
    "measurement": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
  },
  "policy": {
    "bundle_hash": "sha256:b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
    "enforcement_mode": "enforce"
  },
  "data_class": "internal",
  "build_provenance": {
    "slsa_level": 1,
    "digest": "sha256:e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6"
  },
  "appraisal": {
    "status": "none",
    "verifier": "https://verifier.example.org"
  },
  "transparency": "https://registry.agentrust.io/claim/placeholder",
  "cnf": {
    "jwk": {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo"
    }
  },
  "signature": "eyJhbGciOiJFZERTQSJ9..."
}
```

**Modules tested:** TR-ENV, TR-SIG, TR-POL

**What causes a Level 0 failure:**

- `eat_profile` missing or wrong value — TR-ENV-001
- `runtime.platform` is a TEE value (e.g. `sev-snp`) but Level 0 is requested — TR-RTE-001 does not apply, but TR-ENV still checks the envelope
- `policy.enforcement_mode` is `"strict"` or `"monitor"` — TR-POL-002
- `cnf.jwk` missing or contains private key material (`d` field) — TR-SIG-002, TR-SIG-004
- Signature does not verify against `cnf.jwk` — TR-SIG-003

---

## Level 1 — TEE Attestation

Level 1 adds hardware attestation. `runtime.platform` must be one of: `tpm2`, `sev-snp`, `tdx`, `opaque`. The measurement must be non-zero. `appraisal.status` must be `"affirming"`.

**Minimum conformant Level 1 record** (changes from Level 0 in bold context):

```json
{
  "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
  "iat": 1750000000,
  "subject": "spiffe://trust.example.org/agent/my-agent",
  "model": {
    "provider": "anthropic",
    "model_id": "claude-sonnet-4-6",
    "version": "20251001"
  },
  "runtime": {
    "platform": "sev-snp",
    "measurement": "sha256:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
  },
  "policy": {
    "bundle_hash": "sha256:b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
    "enforcement_mode": "enforce"
  },
  "data_class": "confidential",
  "build_provenance": {
    "slsa_level": 2,
    "digest": "sha256:e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6"
  },
  "appraisal": {
    "status": "affirming",
    "verifier": "https://verifier.agentrust.io"
  },
  "transparency": "https://registry.agentrust.io/claim/placeholder",
  "cnf": {
    "jwk": {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo"
    }
  },
  "signature": "eyJhbGciOiJFZERTQSJ9..."
}
```

**Modules tested:** TR-ENV, TR-SIG, TR-POL, TR-RTE, TR-SCA

**What causes a Level 1 failure over Level 0:**

- `runtime.platform` is `"software-only"` — TR-RTE-001
- `runtime.measurement` is all zeros — TR-RTE-002 (all-zero is invalid at Level 1)
- `build_provenance` missing entirely — TR-SCA-001, TR-SCA-002
- `appraisal.status` is `"none"` — while not a hard schema violation, a conformant Level 1 record should carry `"affirming"`

---

## Level 2 — Transparency Anchoring

Level 2 adds tool transcript and transparency anchor requirements. The `transparency` field must be a resolvable HTTPS URI pointing to a SCITT receipt, not the placeholder value.

**Minimum conformant Level 2 record** (additional fields over Level 1):

```json
{
  "tool_transcript": {
    "hash": "sha256:c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
    "call_count": 4
  },
  "transparency": "https://registry.agentrust.io/claim/01J3XKWP4NQZ8R5HT6YD7VMBCE",
  "anchor": {
    "log_id": "https://registry.agentrust.io",
    "leaf_hash": "sha256:f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5"
  }
}
```

**Modules tested:** TR-ENV, TR-SIG, TR-POL, TR-RTE, TR-SCA, TR-TXN, TR-ANC

**What causes a Level 2 failure over Level 1:**

- `tool_transcript.hash` missing or not a valid `sha256:` digest — TR-TXN-001
- `tool_transcript.call_count` negative or not an integer — TR-TXN-002
- `transparency` is the placeholder URI, missing, or not HTTPS — TR-ANC-001
- `anchor.leaf_hash` missing or not a valid `sha256:` digest — TR-ANC-002

---

## Choosing a level

- Use **Level 0** during development. Records can use `runtime.platform: "software-only"` and `build_provenance.slsa_level: 0`.
- Use **Level 1** for production deployments in a TEE (AMD SEV-SNP, Intel TDX, NVIDIA H100).
- Use **Level 2** when you need an auditable, tamper-evident log with a SCITT transparency service.

The certification program (launching 2027) will require Level 1 at minimum.

## Related

- [Error Codes](error-codes.md) — every TR-* error with description and fix
- [Test Modules](modules/index.md) — per-module test lists with positive and negative cases
- [TRACE Trust Levels](https://trace.agentrust-io.com/trust-levels) — full specification of what each level proves
