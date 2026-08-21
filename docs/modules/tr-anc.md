# TR-ANC — Transparency

Tests transparency anchoring via SCITT.

## Required at Level 2+

| Test ID | Description | Positive Case | Negative Case |
|---------|-------------|---------------|---------------|
| TR-ANC-001 | `transparency` is an `https://` URI with a host. Not resolved | `https://transparency.example/entries/abc123` | missing field, empty string, non-string, `http://`, bare path, `ipfs://` |
