# Changelog

## Unreleased

- Add machine-readable execution accounting for the bounded `TR-APR-001`,
  `TR-POL-003`, and `TR-SCA-002` pilot to CLI JSON reports. Accounted findings
  and accounting come from one immutable execution snapshot; unreconciled
  accounting is rejected on that path, the operational policy-correspondence rule
  is separated from supporting schema locators and all carry value digests for
  comparison against the referenced trace-spec bytes, scheduler non-execution
  carries a reason, and existing verdict policy and CLI exit behavior are unchanged.

## v0.5.1 — 2026-08-22

- Level 1 and Level 2 verification now requires a verifier-issued challenge via
  `--expected-nonce` and checks it against the signed `runtime.nonce` using
  constant-time comparison. Previously nonce binding existed only as an
  assertion over the repository's own pytest fixture; the shipped runner and
  CLI could report conformance for a fresh signed record containing an
  attacker-chosen or replayed nonce.

## v0.5.0 — 2026-08-09

### Added

- **`trace-tests report`: conformance results as an artifact somebody can forward.** `verify` answers a question for whoever ran it; a pass/fail in a terminal is useless to an auditor, a counterparty or an acquirer. The new command emits self-contained HTML, a machine-readable JSON document (`schema: agentrust-io/trace-tests/report/1`), and an SVG level badge.

  It runs every level up to `--max-level` instead of one, because the answer a reader needs is the highest level the record reaches, not whether it cleared the level the person running the tool happened to choose. `--fail-under N` gates CI on a level; without it the command exits `0`, since producing an artifact and enforcing a threshold are different jobs.

  **The report states that it is not evidence.** It is unsigned HTML describing one run of one suite version, and anyone can edit it, so every report carries the record's digest, the suite and authoring-library versions, and the command to reproduce the result — and tells a reader who does not trust the sender to go check the record instead. A conformance report that looks authoritative and cannot be checked is the same shape of thing as a control plane writing its own log, which is the problem this project exists to fix.

  Self-contained by construction: no scripts, no external CSS, no fonts, no badge service. A badge served from someone else's infrastructure would add a dependency to an artifact whose whole point is needing none. A test asserts the HTML fetches nothing.

  The HTML and the JSON are rendered from one assembled structure so they cannot disagree about the verdict, and unverified findings count as failures from Level 1 up exactly as they do in `verify`.

## v0.4.1 — 2026-08-03

### Fixed

- **`--version` reported the wrong version.** `__version__` was a second hardcoded literal alongside `pyproject.toml` and never moved, so it sat at `0.2.0` through both the 0.3.0 and 0.4.0 releases: `trace-tests --version` printed `0.2.0` from a 0.4.0 install while `importlib.metadata` correctly returned `0.4.0`. It is now read from installed distribution metadata, so there is one source of truth and the value cannot fall behind a release again.

  This mattered more than a wrong string usually would. The v0.2 profile cutover shipped in 0.4.0, and a 0.2.x suite rejects every v0.2 record, so `--version` is exactly the command someone runs to work out whether their suite matches their producer. It was the one command that could not answer.

## v0.4.0 — 2026-07-28

### Changed

- **BREAKING: the suite now conforms to TRACE v0.2.** `TR-ENV` requires the profile `tag:agentrust-io.com,2026:trace-v0.2` and fails a record carrying the v0.1 identifier. The v0.1 URI named `agentrust.io`, a domain this project never controlled, which RFC 4151 does not permit for a tag URI; see agentrust-io/trace-spec#107. Nothing else about the record format changed, so a producer migrates by updating the profile string and bumping `agentrust-trace` to 0.5.0.

  This is a deliberate cutover rather than dual acceptance: a conformance suite that passed both identifiers would certify records minted under a domain we do not own. A v0.1 record is checked with the 0.3.x releases of this suite, which stay published.

- Registry, verifier, and documentation hosts moved from `agentrust.io` to `agentrust-io.com`.

## v0.3.0 — 2026-07-21

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
