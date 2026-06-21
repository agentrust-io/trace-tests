# TR-ANC — Transparency

Tests transparency anchoring via SCITT.

## Required at Level 2+

| Test ID | Description | Positive Case | Negative Case |
|---------|-------------|---------------|---------------|
| TR-ANC-001 | `transparency` is a non-empty URI | `https://transparency.example/entries/abc123` | missing field, empty string |
| TR-ANC-002 | URI scheme is `https://` | `https://` prefix | `http://`, bare path, `ipfs://` |
