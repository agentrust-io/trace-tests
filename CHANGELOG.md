# Changelog

## Unreleased

- `azure-cvm-sev-snp` platform accepted (`runtime.platform`): Azure confidential VMs run SEV-SNP behind a Hyper-V paravisor (vTPM-rooted). Added to the bundled schema enum and the TR-RTE valid-platform set so Azure TRACE records pass conformance. Matches `agentrust-trace>=0.4`.

## v0.2.0 — 2026-06-19

- DID subject support: `subject` now accepts `did:` URIs in addition to `spiffe://`.
- Embedded signature verification: plain TRACE records signed with `agentrust-trace sign_record()` are now cryptographically verified at all levels.
- SLSA Level 0: `build_provenance.slsa_level: 0` is now valid for software-only / development records.
- Software-only platform: `runtime.platform: "software-only"` accepted at Level 0.
- Private key leak detection: TR-SIG now fails records that embed a private key (`d` member) in `cnf.jwk`.

## v0.1.0 — 2026-05-01

- Initial release with 7 test modules: TR-ENV, TR-SIG, TR-RTE, TR-POL, TR-TXN, TR-ANC, TR-SCA.
- Conformance levels 0, 1, 2.
