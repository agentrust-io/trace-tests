"""Regenerate the policy-resolution vector set, byte for byte.

Deterministic by construction: no keys, no clock, no randomness, no network.
Running this on any machine with the same CPython minor version reproduces
every file in this directory exactly, which is what
``tests/test_policy_resolution_reproduces.py`` asserts.

    python tests/vectors/policy-resolution/gen_policy_resolution.py

The digests in the vectors are SHA-256 over the exact bytes of the sibling
files under ``policies/``. Anyone holding only this directory can recompute
them; nothing here depends on another repository being checked out.

WHAT THIS SET IS FOR
    ``appraisal.policy_ref`` is a bare URI. A record says which appraisal
    policy produced its verdict, but carries nothing stating what that URI
    resolved to at appraisal time, so a second verifier cannot confirm it
    retrieved the same document. See the set's README.md.

WHAT IT DELIBERATELY DOES NOT DO
    It does not name an outcome value for the unresolvable case. That is the
    open cross-surface question tracked by agentrust-io/trace-spec#190, and
    coining a value here is precisely what that issue exists to prevent.
    Vectors 05 and 06 carry the fixture-bookkeeping state ``deferred``.

    ``candidate_binding`` is a CANDIDATE shape, not a proposed schema change.
    It lives in the vector's ``context``, never inside ``record``: the
    packaged schema sets ``additionalProperties: false`` on ``appraisal``, so
    a record carrying an extra field would be schema-invalid, and proposing
    one is a schema decision that belongs to the editorial process.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).parent
POLICIES = HERE / "policies"

# --- house serialization, fixed so bytes are stable across platforms -------
INDENT = 2


def write_json(path: Path, obj: object) -> bytes:
    """Write *obj* as UTF-8 JSON with LF endings; return the exact bytes."""
    text = json.dumps(obj, indent=INDENT, ensure_ascii=True) + "\n"
    data = text.encode("utf-8")
    path.write_bytes(data)
    return data


def sha256_of(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha3_512_of(data: bytes) -> str:
    """A *correct* digest in an algorithm the profile's schema does not admit.

    Vector 06 turns on the verifier being unable to compute the comparison, not
    on the digest being wrong. A placeholder value would confound the two: a
    reader could not tell whether the vector is deferred because the algorithm
    is unsupported or because the digest is obviously bogus. This is the real
    SHA3-512 of the referent, so the algorithm is the only variable.
    """
    return "sha3-512:" + hashlib.sha3_512(data).hexdigest()


# --- the cited objects -----------------------------------------------------
# Small, ASCII-only, and shaped like an appraisal policy rather than a
# placeholder, so a reader can see why swapping one for another matters.

POLICY_BASE = {
    "policy_id": "appraisal/baseline",
    "version": "1.0.0",
    "rules": [
        {"claim": "runtime.platform",
         "must_be_one_of": ["intel-tdx", "amd-sev-snp", "tpm2"]},
        {"claim": "build_provenance.slsa_level", "minimum": 2},
    ],
}

# One character apart from V1: the SLSA floor moves 2 -> 3. A verifier
# applying this instead of V1 reaches a different verdict on the same record,
# which is why a minimal mutation is the honest test rather than a cosmetic one.
POLICY_ONEBYTE = {
    "policy_id": "appraisal/baseline",
    "version": "1.0.0",
    "rules": [
        {"claim": "runtime.platform",
         "must_be_one_of": ["intel-tdx", "amd-sev-snp", "tpm2"]},
        {"claim": "build_provenance.slsa_level", "minimum": 3},
    ],
}

# A legitimate later version, published at its own URI.
POLICY_OTHER = {
    "policy_id": "appraisal/baseline",
    "version": "2.0.0",
    "rules": [
        {"claim": "runtime.platform",
         "must_be_one_of": ["intel-tdx", "amd-sev-snp"]},
        {"claim": "build_provenance.slsa_level", "minimum": 3},
        {"claim": "transparency", "must_be_present": True},
    ],
}

# A different policy entirely, not a version of the baseline.
POLICY_UNRELATED = {
    "policy_id": "retention/pii-90d",
    "version": "1.4.2",
    "rules": [
        {"claim": "data_class", "must_be_one_of": ["public", "internal"]},
    ],
}

POLICY_FILES = {
    "policy-bundle-base.json": POLICY_BASE,
    "policy-bundle-onebyte.json": POLICY_ONEBYTE,
    "policy-bundle-other.json": POLICY_OTHER,
    "policy-bundle-unrelated.json": POLICY_UNRELATED,
}

BASE_URI = "https://policy.example.org/bundles/"

# --- the record ------------------------------------------------------------
# Every vector's record is identical except for appraisal.policy_ref, so the
# defect under test is the only thing that varies. Modelled on the repository's
# tests/vectors/valid_level0.json: unsigned, ASCII-only, fixed iat.

RECORD_IAT = 1748000000
APPRAISAL_TIMESTAMP = 1748000042


def record_with(policy_ref: str | None) -> dict[str, object]:
    appraisal: dict[str, object] = {
        "status": "affirming",
        "verifier": "https://verifier.example.org",
    }
    if policy_ref is not None:
        appraisal["policy_ref"] = policy_ref
    appraisal["timestamp"] = APPRAISAL_TIMESTAMP
    return {
        "eat_profile": "tag:agentrust-io.com,2026:trace-v0.2",
        "iat": RECORD_IAT,
        "subject": "spiffe://example.org/agent/credit-risk/01926b4c-1234-7abc-9def-000000000001",
        "model": {"provider": "anthropic", "model_id": "claude-sonnet-4-5"},
        "runtime": {
            "platform": "intel-tdx",
            "measurement":
                "sha256:a3f8d2b4e1c9f7a5b2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8",
        },
        "policy": {
            "bundle_hash":
                "sha256:b4e1c9f7a5b2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4",
            "enforcement_mode": "enforce",
        },
        "data_class": "confidential",
        "build_provenance": {
            "slsa_level": 2,
            "digest": "sha256:c9f7a5b2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a6b8c0d2e4f6a8",
        },
        "appraisal": appraisal,
        "transparency": "https://scitt.example.org/receipts/abc123def456",
        "cnf": {
            "jwk": {
                "kty": "EC",
                "crv": "P-256",
                "x": "dGhpcyBpcyBhIHRlc3QgeA",
                "y": "dGhpcyBpcyBhIHRlc3QgeQ",
                "kid": "tee-key-001",
            }
        },
    }


CANDIDATE_FIELD = "CANDIDATE:appraisal.policy_digest"
DEFERRED_PENDING = "agentrust-io/trace-spec#190"

SPEC_DECIDED = (
    "agentrust-io/trace-spec docs/verification.md - a verifier records what it "
    "actually resolved, and evidence that resolves and contradicts fails the "
    "appraisal. Applied here to appraisal.policy_ref, which carries no digest."
)
SPEC_DEFERRED = (
    "agentrust-io/trace-spec docs/verification.md - evidence that does not "
    "resolve downgrades honestly rather than failing. Which value records that "
    "for appraisal.policy_ref is open: agentrust-io/trace-spec#190. This vector "
    "asserts only what the outcome may NOT be."
)


def main(out_dir: Path | None = None) -> int:
    """Write the set into *out_dir* (default: this directory).

    The parameter exists so the byte-reproduction guard can regenerate into a
    temporary directory and compare, rather than overwriting the committed
    files and comparing them to themselves — which would agree no matter what.
    """
    here = Path(out_dir) if out_dir is not None else HERE
    policies = here / "policies"
    here.mkdir(parents=True, exist_ok=True)
    policies.mkdir(exist_ok=True)

    # 1. Write the cited objects and digest their exact bytes.
    digests: dict[str, str] = {}
    raw: dict[str, bytes] = {}
    for name, obj in POLICY_FILES.items():
        raw[name] = write_json(policies / name, obj)
        digests[name] = sha256_of(raw[name])

    d_base = digests["policy-bundle-base.json"]
    d_onebyte = digests["policy-bundle-onebyte.json"]
    d_other = digests["policy-bundle-other.json"]
    d_unrelated = digests["policy-bundle-unrelated.json"]

    uri_base = BASE_URI + "policy-bundle-base.json"
    uri_other = BASE_URI + "policy-bundle-other.json"
    uri_withdrawn = BASE_URI + "policy-bundle-withdrawn.json"

    def resolved(file_name: str, digest: str) -> dict[str, object]:
        return {
            "outcome": "resolved",
            "file": f"policies/{file_name}",
            "actual_sha256": digest,
        }

    vectors: list[tuple[str, dict[str, object]]] = [
        ("01-no-binding-declared.json", {
            "name": "no-binding-declared",
            "description": (
                "The record cites an appraisal policy by bare URI and declares no "
                "binding to what that URI held. This is every conformant record "
                "today, so it must keep verifying: a set that rejected it would be "
                "proposing a breaking change rather than describing a gap."
            ),
            "boundary": "accept",
            "defect": "none - backward-compatibility control",
            "spec": (
                "Mirrors the merged treatment of an undeclared depth in "
                "agentrust-io/trace-spec#173, where a record that never declared is "
                "read as surface rather than as a failure."
            ),
            "record": record_with(uri_base),
            "context": {
                "cited_uri": uri_base,
                "resolution": {
                    "outcome": "not_attempted",
                    "note": "No binding is declared, so there is nothing to check.",
                },
                "candidate_binding": None,
            },
            "expected": {
                "outcome": "pass",
                "reason": "No binding declared; nothing to contradict.",
            },
        }),
        ("02-resolved-and-matches.json", {
            "name": "resolved-and-matches",
            "description": (
                "The cited URI resolves and its bytes hash to exactly the declared "
                "candidate binding. The second must-accept vector, and the only one "
                "in which a resolution actually succeeds."
            ),
            "boundary": "accept",
            "defect": "none - positive control",
            "spec": SPEC_DECIDED,
            "record": record_with(uri_base),
            "context": {
                "cited_uri": uri_base,
                "resolution": resolved("policy-bundle-base.json", d_base),
                "candidate_binding": {"field": CANDIDATE_FIELD, "value": d_base},
            },
            "expected": {
                "outcome": "pass",
                "reason": "Declared binding equals the digest of what resolved.",
            },
        }),
        ("03-digest-mismatch-minimal-mutation.json", {
            "name": "digest-mismatch-minimal-mutation",
            "description": (
                "The cited URI now serves a document one character from the one "
                "appraised: the SLSA floor moved from 2 to 3. The record still "
                "declares the original digest. A verifier that compares only the "
                "URI sees no change; a verifier that compares bytes sees the "
                "substitution that flips this record's verdict."
            ),
            "boundary": "contradicted",
            "defect": "cited object mutated minimally after appraisal",
            "spec": SPEC_DECIDED,
            "record": record_with(uri_base),
            "context": {
                "cited_uri": uri_base,
                "resolution": resolved("policy-bundle-onebyte.json", d_onebyte),
                "candidate_binding": {"field": CANDIDATE_FIELD, "value": d_base},
                "note": (
                    "policies/policy-bundle-base.json and "
                    "policies/policy-bundle-onebyte.json differ in one character."
                ),
            },
            "expected": {
                "outcome": "reject",
                "reason": "Resolved bytes contradict the declared binding.",
            },
        }),
        ("04-digest-mismatch-different-object.json", {
            "name": "digest-mismatch-different-object",
            "description": (
                "The cited URI resolves to an unrelated policy document. Paired with "
                "03 so the boundary is not carried by a single vector: a verifier "
                "that only samples a prefix of the document, or compares lengths, "
                "passes one of these two and fails the other."
            ),
            "boundary": "contradicted",
            "defect": "cited object wholly replaced after appraisal",
            "spec": SPEC_DECIDED,
            "record": record_with(uri_base),
            "context": {
                "cited_uri": uri_base,
                "resolution": resolved("policy-bundle-unrelated.json", d_unrelated),
                "candidate_binding": {"field": CANDIDATE_FIELD, "value": d_base},
            },
            "expected": {
                "outcome": "reject",
                "reason": "Resolved bytes contradict the declared binding.",
            },
        }),
        ("05-referent-unreachable.json", {
            "name": "referent-unreachable",
            "description": (
                "The cited URI does not resolve; no object under policies/ "
                "corresponds to it. Nothing was contradicted, because nothing was "
                "read. This vector asserts only that the outcome is not affirming."
            ),
            "boundary": "unresolvable",
            "defect": "referent unreachable at verification time",
            "spec": SPEC_DEFERRED,
            "record": record_with(uri_withdrawn),
            "context": {
                "cited_uri": uri_withdrawn,
                "resolution": {
                    "outcome": "unreachable",
                    "file": None,
                    "note": "No sibling file corresponds to this URI, by construction.",
                },
                "candidate_binding": {"field": CANDIDATE_FIELD, "value": d_base},
            },
            "expected": {
                "outcome": "deferred",
                "deferred_pending": DEFERRED_PENDING,
                "must_not": "affirming",
                "reason": (
                    "Reporting a check that was never performed as affirming is the "
                    "failure this set exists to name. Which value is reported "
                    "instead is not decided here."
                ),
            },
        }),
        ("06-digest-algorithm-uncomputable.json", {
            "name": "digest-algorithm-uncomputable",
            "description": (
                "The referent resolves, but the declared binding names a digest "
                "algorithm outside the set this profile's schema admits "
                "(sha256 and sha384). The verifier cannot compute the comparison, "
                "so it has not checked - which is distinct from having checked and "
                "disagreed. Paired with 05: one cannot reach the object, the other "
                "reaches it and cannot compute over it."
            ),
            "boundary": "unresolvable",
            "defect": "digest algorithm the verifier cannot compute",
            "spec": (
                SPEC_DEFERRED
                + " Deliberately rhymes with the unverifiable / "
                "digest_algorithm_unsupported classification PROPOSED in "
                "agentrust-io/trace-spec#184 - an explicitly non-normative "
                "draft, a surface facing this question rather than an "
                "established answer to it - without adopting its vocabulary."
            ),
            "record": record_with(uri_other),
            "context": {
                "cited_uri": uri_other,
                "resolution": resolved("policy-bundle-other.json", d_other),
                "candidate_binding": {
                    "field": CANDIDATE_FIELD,
                    "value": sha3_512_of(raw["policy-bundle-other.json"]),
                    "note": (
                        "This is the correct SHA3-512 of the referent. It is "
                        "outside the schema's digest pattern "
                        "^sha(256:[0-9a-f]{64}|384:[0-9a-f]{96})$, so no conformant "
                        "verifier is required to compute it - which is the only "
                        "reason this vector is undecided."
                    ),
                },
            },
            "expected": {
                "outcome": "deferred",
                "deferred_pending": DEFERRED_PENDING,
                "must_not": "affirming",
                "reason": (
                    "The comparison was not performed, so the result is not a "
                    "contradiction. Which value records that is not decided here."
                ),
            },
        }),
        ("07-digest-bound-to-other-referent.json", {
            "name": "digest-bound-to-other-referent",
            "description": (
                "The declared binding is well formed and is the true digest of a "
                "real object in this set - version 2 - while policy_ref cites "
                "version 1. Both halves are individually valid and the pair is not. "
                "A verifier that checks the digest is well formed, or that it "
                "matches something it holds, passes this; only one that checks the "
                "digest against what this URI resolved to rejects it."
            ),
            "boundary": "contradicted",
            "defect": "binding well formed but bound to a different referent",
            "spec": SPEC_DECIDED,
            "record": record_with(uri_base),
            "context": {
                "cited_uri": uri_base,
                "resolution": resolved("policy-bundle-base.json", d_base),
                "candidate_binding": {
                    "field": CANDIDATE_FIELD,
                    "value": d_other,
                    "note": (
                        "This is the digest of policies/policy-bundle-other.json, "
                        "which is not what cited_uri resolves to."
                    ),
                },
            },
            "expected": {
                "outcome": "reject",
                "reason": (
                    "The binding does not describe the object the record cites, "
                    "even though it describes some object."
                ),
            },
        }),
    ]

    for filename, vector in vectors:
        write_json(here / filename, vector)

    print(f"wrote {len(POLICY_FILES)} policy objects and {len(vectors)} vectors")
    for name, digest in digests.items():
        print(f"  policies/{name}  {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
