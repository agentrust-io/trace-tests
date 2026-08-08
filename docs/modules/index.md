# Test Modules

The TRACE conformance suite is divided into seven modules. Each module maps to a section of the TRACE specification.

| Module                                                                      | ID Prefix | Spec Section | What It Tests                                                              |
| --------------------------------------------------------------------------- | --------- | ------------ | -------------------------------------------------------------------------- |
| [Envelope](https://tests.agentrust-io.com/docs/modules/tr-env/index.md)     | TR-ENV    | §3.2         | EAT envelope structure, `eat_profile` URI, required fields, `iat` validity |
| [Signature](https://tests.agentrust-io.com/docs/modules/tr-sig/index.md)    | TR-SIG    | §3.2.1       | Algorithm conformance (Ed25519), key binding, private key leak detection   |
| [Runtime](https://tests.agentrust-io.com/docs/modules/tr-rte/index.md)      | TR-RTE    | §3.1         | TEE platform enum, measurement format, RIM URI resolution                  |
| [Policy](https://tests.agentrust-io.com/docs/modules/tr-pol/index.md)       | TR-POL    | §3.1         | Policy bundle hash format, enforcement mode values                         |
| [Transcript](https://tests.agentrust-io.com/docs/modules/tr-txn/index.md)   | TR-TXN    | §3.1         | Tool-call transcript hash binding                                          |
| [Transparency](https://tests.agentrust-io.com/docs/modules/tr-anc/index.md) | TR-ANC    | §3.2         | SCITT receipt URI format, inclusion proof structure                        |
| [Provenance](https://tests.agentrust-io.com/docs/modules/tr-sca/index.md)   | TR-SCA    | §3.1         | SLSA provenance level, builder URI, digest format                          |
