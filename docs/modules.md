# Test Modules

The TRACE conformance suite is divided into seven modules. Each module maps to a section of the TRACE specification.

| Module | ID Prefix | Spec Section | What It Tests |
|--------|-----------|--------------|---------------|
| [Envelope](modules/tr-env.md) | TR-ENV | §3.2 | EAT envelope structure, `eat_profile` URI, required fields, `iat` validity |
| [Signature](modules/tr-sig.md) | TR-SIG | §3.2.1 | Algorithm conformance (Ed25519), key binding, private key leak detection |
| [Runtime](modules/tr-rte.md) | TR-RTE | §3.1 | TEE platform enum, measurement format, RIM URI resolution |
| [Policy](modules/tr-pol.md) | TR-POL | §3.1 | Policy bundle hash format, enforcement mode values |
| [Transcript](modules/tr-txn.md) | TR-TXN | §3.1 | Tool-call transcript hash binding |
| [Transparency](modules/tr-anc.md) | TR-ANC | §3.2 | SCITT receipt URI format, inclusion proof structure |
| [Provenance](modules/tr-sca.md) | TR-SCA | §3.1 | SLSA provenance level, builder URI, digest format |
