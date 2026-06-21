# TR-POL — Policy

Tests Cedar policy bundle binding.

## Required at Level 0+

| Test ID | Description | Positive Case | Negative Case |
|---------|-------------|---------------|---------------|
| TR-POL-001 | `policy.bundle_hash` is a valid `sha256:` digest | `sha256:` followed by 64 hex chars | missing, wrong prefix, wrong length |
| TR-POL-002 | `policy.enforcement_mode` is `enforce`, `advisory`, or `silent` | `enforce` | `strict`, `monitor`, absent |
