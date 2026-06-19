# TR-SIG — Signature

Tests Ed25519 signature binding on the TRACE Trust Record.

## Required at Level 0+

| Test ID | Description |
|---------|-------------|
| TR-SIG-001 | Signature algorithm is Ed25519 (OKP crv=Ed25519) |
| TR-SIG-002 | `cnf.jwk` present and carries the public key |
| TR-SIG-003 | Signature verifies over the canonical record bytes (RFC 8785 JCS) |
| TR-SIG-004 | `cnf.jwk` does not contain private key material (`d` member absent) |
