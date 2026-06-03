# TRACE Compliance Tests

Conformance test suite for TRACE — Trust Runtime Attestation and Compliance Evidence. Governance tools that pass this suite qualify for TRACE Certification.

## What Is Tested

| Category | Tests |
|----------|-------|
| Claim format | JSON Schema validation, required fields, version compatibility |
| Chain integrity | Merkle chain verification, tamper detection, gap detection |
| Policy attestation | Policy bundle hash binding, enforcement mode verification |
| Provider coverage | Per-provider attestation report verification (TPM, SEV-SNP, TDX, OPAQUE) |
| Tamper detection | Injected tamper scenarios at entry 1, mid-chain, and final entry |

## Running the Tests

```bash
pip install trace-verify
trace-tests run --implementation ./my-governance-tool --output results.json
```

## TRACE Certification

Tools that pass the full conformance suite can apply for TRACE Certification. See [CERTIFICATION.md](CERTIFICATION.md) for process and fee schedule (Q2 2027).

## Status

Private. Test suite in development. Certification program launching Q2 2027.

## License

Apache 2.0