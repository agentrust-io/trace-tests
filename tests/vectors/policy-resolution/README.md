# Appraisal-resolution vectors

Candidate conformance vectors for one question: **when a record cites an
appraisal policy by URI, what can a second verifier confirm about what that URI
held?**

Today, nothing. `appraisal.policy_ref` is a bare URI. The record carries a
digest for the enforcement policy bundle (`policy.bundle_hash`) and none for the
appraisal policy that produced the verdict, so two verifiers resolving the same
`policy_ref` at different times can retrieve different documents and both report
`affirming` honestly.

## Why this set exists

`agentrust-io/trace-tests#63` proposed a conformance module for the `appraisal`
claim, noting that `policy_ref` can be checked for well-formedness only, "since
the record carries no digest to compare a resolved policy against." Building
those cases ran into the boundary itself, which was stated on
`agentrust-io/trace-spec#66` on 2026-08-18:

> `appraisal.policy_ref` can be checked for well-formedness, but not
> reproduced: the record carries nothing stating what the referent was, so a
> conformance module can confirm the URI parses and nothing more. Two verifiers
> resolving the same `policy_ref` at different times can retrieve different
> documents and both honestly report verified — the federation gap §1 names,
> one hop from the record.

Drafting candidate fixtures for it was accepted on that thread the same day,
with the shape asked for: candidates in `trace-tests`, one defect per vector,
expected outcomes committed beside the vectors, and the schema and
`verification.md` text left maintainer-authored. This set is that.

## What it does not do

**It does not propose a schema change.** `candidate_binding` is a *candidate
shape*, marked `CANDIDATE:` in every vector, and it lives in the vector's
`context` — never inside `record`. The packaged schema sets
`additionalProperties: false` on `appraisal`, so a record carrying an extra
field would be schema-invalid; whether a binding field lands, and what it is
called, is an editorial decision.

**It does not name an outcome value for the unresolvable case.** Vectors 05 and
06 are marked `deferred`, pointing at `agentrust-io/trace-spec#190`, which
tracks the open cross-surface question: *when a record cites something a
verifier cannot resolve, what does the verifier record, and where.*

Four surfaces face that question. Only one has answered it:
`build_provenance`, with a recorded field plus a floor
(`agentrust-io/trace-spec#173`, **merged**). Revocation states the prohibition
in prose with no field to record the outcome in
(`agentrust-io/trace-spec#187`, **merged**). Delegation links **propose**
`unverifiable` on a separate axis (`agentrust-io/trace-spec#184`, **an
explicitly non-normative draft** — a proposal facing the question, not an
established answer; its author has said so on
`agentrust-io/trace-spec#190`). And this one.

The divergence is a schema fact rather than four differing opinions:
`appraisal` is `additionalProperties: false`, and `#173` landed the only
claimed/verified pair that exists, so the other surfaces had no field to use.
Coining a fifth answer here is exactly what `agentrust-io/trace-spec#190`
exists to prevent — and a new field or a fifth `appraisal.status` value is
normative under `CONTRIBUTING.md`, which routes it through a Spec change
proposal with a sponsoring organization. It is not something a vector set
decides.

> **`deferred` is fixture bookkeeping, not a proposed appraisal vocabulary
> value.** It is a property of a *vector's expected block*, recording that the
> outcome is not yet decided upstream. It is **not** a candidate value for
> `appraisal.status`, which is closed at `affirming`, `warning`,
> `contraindicated`, `none`. A deferred vector asserts only what the outcome may
> **not** be — `must_not: "affirming"` — because reporting a check that was
> never performed as affirming is the one thing every reading of the merged text
> already rules out. `tests/test_policy_resolution_completeness.py` fails if
> any vector reuses a status value as an outcome.

## The vectors

Every record is identical except for `appraisal.policy_ref`, so the defect under
test is the only thing that varies. All records are unsigned and ASCII-only.

| # | Vector | Boundary | Expected |
|---|---|---|---|
| 01 | `no-binding-declared` | accept | `pass` |
| 02 | `resolved-and-matches` | accept | `pass` |
| 03 | `digest-mismatch-minimal-mutation` | contradicted | `reject` |
| 04 | `digest-mismatch-different-object` | contradicted | `reject` |
| 05 | `referent-unreachable` | unresolvable | `deferred` |
| 06 | `digest-algorithm-uncomputable` | unresolvable | `deferred` |
| 07 | `digest-bound-to-other-referent` | contradicted | `reject` |

**01 and 02 are the must-accept pair, and they are why this set is not
one-directional.** `agentrust-io/trace-spec#186` (merged 2026-08-20) states
the criterion: a set must fail *both* unconditional implementations. A set
written from the motivating problem alone would be all rejections and
deferrals, and a verifier that rejects everything would pass it. 01 is the
backward-compatibility control — every conformant record today declares no
binding, and must keep verifying, or this set would be proposing a breaking
change rather than describing a gap. 02 is the only vector in which a
resolution succeeds.

**03 and 04 keep the contradicted boundary off a single vector.** 03 differs
from the appraised object in exactly one byte — the SLSA floor moves 2 → 3,
which flips this record's verdict. 04 substitutes an unrelated document of a
different length. A verifier comparing lengths, or sampling a prefix, passes one
and fails the other.

**05 and 06 are both unresolvable, by different mechanisms.** 05 cannot reach
the object; 06 reaches it and cannot compute over it, because the declared
algorithm (`sha3-512`) is outside the set the schema admits
(`^sha(256:[0-9a-f]{64}|384:[0-9a-f]{96})$`). The distinction deliberately
rhymes with the `digest_algorithm_unsupported` classification **proposed** in
`agentrust-io/trace-spec#184` — a non-normative draft — without adopting that
vocabulary.

**07 is the one a well-formedness check passes.** The binding is a valid
`sha256:` digest and is the true digest of a real object in this set — version 2
— while `policy_ref` cites version 1. Both halves are individually valid; the
pair is not.

## Reproducing it

```
python tests/vectors/policy-resolution/gen_policy_resolution.py
```

Deterministic: no keys, no clock, no randomness, no network. The digests are
SHA-256 over the exact bytes of the sibling files under `policies/`, so anyone
holding only this directory can recompute every number in the set.

`tests/test_policy_resolution_reproduces.py` holds the generator to
byte-reproduction by regenerating into a temporary directory and comparing —
not in place, which would compare the files to themselves and agree regardless.

The guard is **self-contained**. `agentrust-io/trace-spec#171` provides the
equivalent for that repository's `examples/`, and `trace-tests` has no such
registry; `agentrust-io/trace-tests#66` gives the reason not to reach across for
one — *"a guard that needs another repository checked out is a guard that gets
skipped."*

`.gitattributes` in this directory pins `eol=lf`. This is load-bearing rather
than tidy: with `core.autocrlf=true`, a checkout rewrites LF to CRLF, every
policy digest stops matching, and the set fails on a clean clone.

## What this set does not establish

- **No verifier was exercised.** Nothing in `trace-tests` resolves
  `appraisal.policy_ref` today — that is the gap — so every expected outcome is
  a claim about what a verifier should do, not a recording of what one did. The
  tests grade the set's internal consistency: that each declared digest really
  is, or really is not, the digest of the bytes the vector says resolution
  returned.
- **The unresolvable outcome is unnamed**, by choice, pending
  `agentrust-io/trace-spec#190`.

Both are recorded as exact shortfalls in
`tests/test_policy_resolution_completeness.py::KNOWN_SHORTFALLS`, which fails
if the list changes without this file changing with it.

## Related

- `agentrust-io/trace-tests#63` — the module proposal these cases were built for
- `agentrust-io/trace-spec#66` — where the gap was raised and the fixtures accepted
- `agentrust-io/trace-spec#190` — the deferred cross-surface question
- `agentrust-io/trace-spec#173` — merged: recorded field plus a policy floor
- `agentrust-io/trace-spec#184` — open, **draft, explicitly non-normative**:
  *proposes* `unverifiable` on the delegation surface
- `agentrust-io/trace-spec#186` — merged: the adequacy criteria this set was
  built to. It grades trace-spec's `examples/`; this repository has no adequacy
  harness, so the standard is one this set chose, not one imposed on it
- `agentrust-io/trace-tests#66` — merged: `tr_sig` canonicalizes with RFC 8785;
  source of the self-containment principle quoted above
- `agentrust-io/trace-tests#68` — merged: packaged schema resynced to the
  normative v0.2 copy these records validate against
