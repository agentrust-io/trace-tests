# Test Modules

The TRACE conformance suite is divided into seven modules. Each module maps to a section of the TRACE specification.

| Module                                                                      | ID Prefix | Spec Section | What It Tests                                                                     |
| --------------------------------------------------------------------------- | --------- | ------------ | --------------------------------------------------------------------------------- |
| [Envelope](https://tests.agentrust-io.com/docs/modules/tr-env/index.md)     | TR-ENV    | §3.2         | `eat_profile` URI, `iat` validity, `subject` form, presence of `cnf.jwk.kty`      |
| [Signature](https://tests.agentrust-io.com/docs/modules/tr-sig/index.md)    | TR-SIG    | §3.2.1       | Key type support, and the Ed25519 signature verification outcome                  |
| [Runtime](https://tests.agentrust-io.com/docs/modules/tr-rte/index.md)      | TR-RTE    | §3.1         | TEE platform enum, measurement format, RIM URI scheme                             |
| [Policy](https://tests.agentrust-io.com/docs/modules/tr-pol/index.md)       | TR-POL    | §3.1         | Policy bundle hash format, enforcement mode values                                |
| [Transcript](https://tests.agentrust-io.com/docs/modules/tr-txn/index.md)   | TR-TXN    | §3.1         | Tool-call transcript hash binding                                                 |
| [Transparency](https://tests.agentrust-io.com/docs/modules/tr-anc/index.md) | TR-ANC    | §3.2         | SCITT receipt URI form. The URI is not resolved and no inclusion proof is checked |
| [Provenance](https://tests.agentrust-io.com/docs/modules/tr-sca/index.md)   | TR-SCA    | §3.1         | SLSA provenance level and digest format                                           |
