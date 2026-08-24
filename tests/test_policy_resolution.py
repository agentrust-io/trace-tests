"""The policy-resolution set proves itself: digests, referents, schema.

No verifier resolves ``appraisal.policy_ref``, so there is no implementation to
run these against. What can be checked — and is checked here — is that the set
is internally what it claims to be:

  * every record is valid under the packaged schema on this branch's base, so
    the set describes conformant records rather than malformed ones;
  * every declared digest really is, or really is not, the SHA-256 of the bytes
    the vector says the citation resolved to, matching its expected outcome;
  * the unreachable vector really has no resolvable object;
  * vector 06's algorithm really is outside the digest set the schema admits.

A vector whose expected outcome and whose bytes disagree is worse than no
vector: it looks like coverage and argues for the wrong thing.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import jsonschema
import pytest

VECTOR_DIR = Path(__file__).parent / "vectors" / "policy-resolution"
SCHEMA_DIGEST_PATTERN = re.compile(r"^sha(256:[0-9a-f]{64}|384:[0-9a-f]{96})$")


def _vector_paths() -> list[Path]:
    return sorted(VECTOR_DIR.glob("[0-9][0-9]-*.json"))


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_of_file(rel: str) -> str:
    return "sha256:" + hashlib.sha256((VECTOR_DIR / rel).read_bytes()).hexdigest()


VECTORS = _vector_paths()


@pytest.mark.level0
def test_the_set_has_the_seven_vectors_it_documents() -> None:
    names = [p.name for p in VECTORS]
    assert len(names) == 7, names
    for n, path in enumerate(VECTORS, start=1):
        assert path.name.startswith(f"{n:02d}-"), (
            f"vectors must be contiguously numbered; got {path.name} at position {n}"
        )


@pytest.mark.level0
@pytest.mark.parametrize("path", VECTORS, ids=lambda p: p.stem)
def test_the_record_is_valid_under_the_packaged_schema(path: Path, schema) -> None:
    """Schema validity, so the set is about resolution and not about malformed input."""
    jsonschema.validate(_load(path)["record"], schema)


@pytest.mark.level0
@pytest.mark.parametrize("path", VECTORS, ids=lambda p: p.stem)
def test_the_record_carries_a_bare_policy_ref_and_no_invented_field(path: Path) -> None:
    """The candidate binding must never leak into the record.

    ``appraisal`` is ``additionalProperties: false`` in the packaged schema, so
    a record carrying the candidate field would be schema-invalid — and
    proposing it is a schema decision this set does not make.
    """
    appraisal = _load(path)["record"]["appraisal"]
    assert set(appraisal) <= {"status", "verifier", "policy_ref", "timestamp"}, (
        f"record appraisal carries an unexpected key: {sorted(appraisal)}"
    )
    for key in appraisal:
        assert "digest" not in key, f"record appraisal proposes a binding field: {key}"


@pytest.mark.level0
@pytest.mark.parametrize("path", VECTORS, ids=lambda p: p.stem)
def test_the_declared_resolution_matches_the_bytes_on_disk(path: Path) -> None:
    """Whatever the vector says resolution returned, the file must hash to it."""
    ctx = _load(path)["context"]
    resolution = ctx["resolution"]
    if resolution["outcome"] != "resolved":
        assert resolution.get("file") in (None,), (
            "a resolution that did not resolve must not name a file"
        )
        return
    rel = resolution["file"]
    assert (VECTOR_DIR / rel).is_file(), f"{rel} is missing from the set"
    assert resolution["actual_sha256"] == _sha256_of_file(rel), (
        f"{rel} does not hash to the digest the vector records for it"
    )


@pytest.mark.level0
@pytest.mark.negative
@pytest.mark.parametrize("path", VECTORS, ids=lambda p: p.stem)
def test_the_binding_agrees_with_the_expected_outcome(path: Path) -> None:
    """The load-bearing self-proof.

    accept  -> the declared binding equals the digest of what resolved
               (or no binding is declared at all)
    reject  -> a binding and a resolution both exist, and they disagree
    deferred-> the comparison could not be performed at all
    """
    vector = _load(path)
    ctx, outcome = vector["context"], vector["expected"]["outcome"]
    binding = ctx.get("candidate_binding")
    resolution = ctx["resolution"]
    resolved = resolution["outcome"] == "resolved"

    if outcome == "pass":
        if binding is None:
            # 01: nothing was declared, so there is nothing that could contradict.
            assert resolution["outcome"] == "not_attempted", (
                "a vector declaring no binding must not claim a resolution was "
                "attempted; the point is that there was nothing to check"
            )
            return
        assert resolved, "an accepting vector with a binding must have resolved"
        assert binding["value"] == resolution["actual_sha256"], (
            "accept requires the declared binding to equal what resolved"
        )

    elif outcome == "reject":
        assert binding is not None, "a rejecting vector must declare a binding"
        assert resolved, (
            "a rejecting vector must have resolved something; otherwise nothing "
            "was contradicted and the case is unresolvable, not contradicted"
        )
        assert SCHEMA_DIGEST_PATTERN.match(binding["value"]), (
            "a rejecting vector's binding must be well formed, so the rejection "
            "is about the referent and not about a malformed digest"
        )
        assert binding["value"] != resolution["actual_sha256"], (
            "reject requires the declared binding to differ from what resolved"
        )

    elif outcome == "deferred":
        computable = (
            binding is not None
            and SCHEMA_DIGEST_PATTERN.match(binding["value"]) is not None
        )
        assert not (resolved and computable), (
            "a deferred vector must be one the verifier could not complete: "
            "either the referent did not resolve, or the digest algorithm is "
            "outside the set the schema admits"
        )

    else:  # pragma: no cover - guarded by the completeness test
        raise AssertionError(f"unknown expected outcome {outcome!r}")


@pytest.mark.level0
@pytest.mark.negative
def test_05_really_has_no_resolvable_object() -> None:
    vector = _load(VECTOR_DIR / "05-referent-unreachable.json")
    assert vector["context"]["resolution"]["outcome"] == "unreachable"
    cited = vector["context"]["cited_uri"]
    tail = cited.rsplit("/", 1)[-1]
    assert not (VECTOR_DIR / "policies" / tail).exists(), (
        "05 claims the referent is unreachable, but a sibling file matches its URI"
    )


@pytest.mark.level0
@pytest.mark.negative
def test_06_names_an_algorithm_the_schema_does_not_admit() -> None:
    vector = _load(VECTOR_DIR / "06-digest-algorithm-uncomputable.json")
    value = vector["context"]["candidate_binding"]["value"]
    assert not SCHEMA_DIGEST_PATTERN.match(value), (
        "06 claims the algorithm is uncomputable, but the digest matches the "
        "pattern the schema admits"
    )
    assert vector["context"]["resolution"]["outcome"] == "resolved", (
        "06 must reach its referent; that is what separates it from 05"
    )


@pytest.mark.level0
def test_03_and_04_differ_in_kind_not_just_in_bytes() -> None:
    """The pair that keeps the contradicted boundary off a single vector."""
    minimal = _load(VECTOR_DIR / "03-digest-mismatch-minimal-mutation.json")
    wholesale = _load(VECTOR_DIR / "04-digest-mismatch-different-object.json")

    a = (VECTOR_DIR / minimal["context"]["resolution"]["file"]).read_bytes()
    b = (VECTOR_DIR / "policies" / "policy-bundle-base.json").read_bytes()
    assert len(a) == len(b), "03's mutation should not change the object's length"
    assert sum(x != y for x, y in zip(a, b)) == 1, (
        "03 is the minimal-mutation vector; it must differ from the appraised "
        "object in exactly one byte"
    )

    c = (VECTOR_DIR / wholesale["context"]["resolution"]["file"]).read_bytes()
    assert len(c) != len(b), (
        "04 is the wholesale-substitution vector; a verifier comparing lengths "
        "must be able to tell it from 03"
    )
