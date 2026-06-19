# Conformance Levels

TRACE defines three conformance levels. Higher levels require all lower-level modules plus additional ones.

| Level | Required Modules | Use Case |
|-------|-----------------|----------|
| **0** | TR-ENV, TR-SIG, TR-POL | Software-only development and staging |
| **1** | Level 0 + TR-RTE, TR-SCA | Production TEE-attested records |
| **2** | Level 1 + TR-TXN, TR-ANC | Full records with transparency anchoring |

## Choosing a level

- Use **Level 0** during development. Records can use `runtime.platform: "software-only"` and `build_provenance.slsa_level: 0`.
- Use **Level 1** for production deployments in a TEE (AMD SEV-SNP, Intel TDX, NVIDIA H100).
- Use **Level 2** when you need an auditable, tamper-evident log with a SCITT transparency service.

The certification program (launching 2027) will require Level 1 at minimum.
