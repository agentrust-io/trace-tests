# Test Modules

The TRACE conformance suite is divided into seven modules. Each module maps to a section of the TRACE specification.

| Module | ID Prefix | Spec Section | What It Tests |
|--------|-----------|--------------|---------------|
| [Envelope](modules/tr-env.md) | TR-ENV | §3.2 | `eat_profile` URI, `iat` validity, `subject` form, presence of `cnf.jwk.kty` |
| [Signature](modules/tr-sig.md) | TR-SIG | §3.2.1 | Key type support, and the Ed25519 signature verification outcome |
| [Runtime](modules/tr-rte.md) | TR-RTE | §3.1 | TEE platform enum, measurement format, RIM URI scheme |
| [Policy](modules/tr-pol.md) | TR-POL | §3.1 | Policy bundle hash format, enforcement mode values |
| [Transcript](modules/tr-txn.md) | TR-TXN | §3.1 | Tool-call transcript hash binding |
| [Transparency](modules/tr-anc.md) | TR-ANC | §3.2 | SCITT receipt URI form. The URI is not resolved and no inclusion proof is checked |
| [Provenance](modules/tr-sca.md) | TR-SCA | §3.1 | SLSA provenance level and digest format |
