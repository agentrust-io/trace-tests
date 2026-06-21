# TR-SIG — Signature

Tests Ed25519 signature binding on the TRACE Trust Record.

## Required at Level 0+

| Test ID | Description | Positive Case | Negative Case |
|---------|-------------|---------------|---------------|
| TR-SIG-001 | Signature algorithm is Ed25519 (OKP crv=Ed25519) | `{"kty":"OKP","crv":"Ed25519"}` | ES256, RS256, missing `alg` |
| TR-SIG-002 | `cnf.jwk` present and carries the public key | JWK with `x` member set | missing `cnf`, missing `jwk`, missing `x` |
| TR-SIG-003 | Signature verifies over the canonical record bytes (RFC 8785 JCS) | valid Ed25519 signature | bit-flipped signature, wrong key |
| TR-SIG-004 | `cnf.jwk` does not contain private key material (`d` member absent) | JWK with only `x` | JWK with `d` present |
