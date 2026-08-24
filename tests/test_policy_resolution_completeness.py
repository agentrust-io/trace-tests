"""Adequacy of the policy-resolution set, per the criteria on trace-spec#186.

agentrust-io/trace-spec#186 (merged 2026-08-20) states what a conformance
vector set is claiming: *a verifier that does not implement these rules will
fail this set*. Three of its four criteria are checkable here and are checked;
the fourth is about repository-wide bookkeeping and is noted below.

It merged into trace-spec, where it grades that repository's ``examples/``.
This repository has no adequacy harness, so nothing here is subject to it.
These criteria are a standard this set was built to by choice, and the tests
below are this set holding itself to them.

    1. A set must fail BOTH unconditional implementations.
       A set of all-rejections is passed by a verifier that rejects everything,
       exactly as a set of all-acceptances is passed by one that accepts
       everything. This set's three decided-reject vectors would, alone, be the
       first failure. Vectors 01 and 02 exist to close it.
    2. Every boundary needs more than one vector.
       One vector cannot separate a check that reads a prefix from one that
       reads the whole object.
    3. Every set on disk is measured, or named with the test that measures it.
       Repository-wide; trace-tests has no registry to add to, so it cannot be
       asserted from inside one set. Recorded in the set's README instead.
    4. Shortfalls are recorded exactly.
       See KNOWN_SHORTFALLS below.

These tests grade the set, not a verifier. No verifier resolves
``appraisal.policy_ref`` today — that is the gap the set documents — so nothing
here claims an implementation was exercised.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

VECTOR_DIR = Path(__file__).parent / "vectors" / "policy-resolution"

DECIDED_OUTCOMES = {"pass", "reject"}
ALL_OUTCOMES = DECIDED_OUTCOMES | {"deferred"}

# Criterion 4: shortfalls asserted to their exact extent, so they cannot widen
# quietly. Delete an entry when the shortfall is closed, not when it is excused.
KNOWN_SHORTFALLS = {
    "no_verifier_exercised": (
        "No implementation resolves appraisal.policy_ref, so every expected "
        "outcome is a claim about what a verifier should do, not a recording of "
        "what one did. The set is a specification argument with runnable "
        "internal consistency, not a conformance run."
    ),
    "unresolvable_outcome_unnamed": (
        "Vectors 05 and 06 assert only that the outcome is not affirming. The "
        "value a verifier should record is open on agentrust-io/trace-spec#190 "
        "and is deliberately not proposed here."
    ),
}


def _vectors() -> list[dict]:
    out = []
    for path in sorted(VECTOR_DIR.glob("[0-9][0-9]-*.json")):
        out.append(json.loads(path.read_text(encoding="utf-8")))
    return out


def _outcome(vector: dict) -> str:
    return vector["expected"]["outcome"]


@pytest.mark.level0
def test_the_set_is_not_empty() -> None:
    assert len(_vectors()) == 7, "the set is seven vectors, 01 through 07"


@pytest.mark.level0
def test_criterion_1_the_set_fails_an_accept_everything_verifier() -> None:
    """At least one vector a conformant verifier must reject."""
    rejects = [v for v in _vectors() if _outcome(v) == "reject"]
    assert rejects, (
        "every vector expects acceptance, so a verifier that accepts "
        "unconditionally passes the set"
    )


@pytest.mark.level0
def test_criterion_1_the_set_fails_a_reject_everything_verifier() -> None:
    """At least one vector a conformant verifier must accept.

    This is the criterion the set would otherwise fail. Its subject is a family
    of resolution failures, so every vector written from the motivating problem
    alone is a reject or a deferral.
    """
    accepts = [v for v in _vectors() if _outcome(v) == "pass"]
    assert accepts, (
        "no vector expects acceptance, so a verifier that rejects "
        "unconditionally passes the set"
    )
    assert len(accepts) >= 2, (
        "one must-accept vector cannot separate a verifier that accepts only "
        "records declaring no binding from one that also checks a matching "
        "binding; 01 and 02 are that pair"
    )


@pytest.mark.level0
def test_criterion_2_every_boundary_carries_at_least_two_vectors() -> None:
    counts = Counter(v["boundary"] for v in _vectors())
    thin = {b: n for b, n in counts.items() if n < 2}
    assert not thin, f"boundaries carried by a single vector: {thin}"
    assert set(counts) == {"accept", "contradicted", "unresolvable"}, (
        f"unexpected boundary set: {sorted(counts)}"
    )


@pytest.mark.level0
def test_no_two_vectors_share_a_defect() -> None:
    defects = [v["defect"] for v in _vectors()]
    dupes = [d for d, n in Counter(defects).items() if n > 1 and d != "none"]
    assert not dupes, f"defect exercised by more than one vector: {dupes}"


@pytest.mark.level0
def test_every_expected_block_is_well_formed() -> None:
    for v in _vectors():
        name = v["name"]
        exp = v["expected"]
        assert exp["outcome"] in ALL_OUTCOMES, f"{name}: bad outcome {exp['outcome']!r}"
        assert exp.get("reason"), f"{name}: expected block carries no reason"
        if exp["outcome"] == "deferred":
            assert exp.get("deferred_pending") == "agentrust-io/trace-spec#190", (
                f"{name}: a deferred vector must name the issue it defers to"
            )
            assert exp.get("must_not") == "affirming", (
                f"{name}: a deferred vector must still assert what it may not be"
            )
        else:
            assert "deferred_pending" not in exp, (
                f"{name}: a decided vector must not carry a deferral pointer"
            )


@pytest.mark.level0
def test_no_vector_proposes_an_appraisal_status_value() -> None:
    """The set must not coin the vocabulary trace-spec#190 exists to decide.

    ``deferred`` is fixture bookkeeping. It must never appear as an
    ``appraisal.status``, and no vector may assert a status for the
    unresolvable case.
    """
    schema_enum = {"affirming", "warning", "contraindicated", "none"}
    for v in _vectors():
        status = v["record"]["appraisal"]["status"]
        assert status in schema_enum, f"{v['name']}: invented status {status!r}"
        exp = v["expected"]
        assert exp["outcome"] not in schema_enum, (
            f"{v['name']}: expected.outcome reuses an appraisal.status value, "
            "which reads as proposing that value for this case"
        )
        if exp["outcome"] == "deferred":
            assert "status" not in exp, (
                f"{v['name']}: a deferred vector must not name a status to record"
            )


@pytest.mark.level0
def test_candidate_binding_is_marked_candidate_everywhere_it_appears() -> None:
    for v in _vectors():
        binding = v["context"].get("candidate_binding")
        if binding is None:
            continue
        assert binding["field"].startswith("CANDIDATE:"), (
            f"{v['name']}: the binding field must be marked CANDIDATE, so it is "
            "never read as a proposed schema field"
        )


@pytest.mark.level0
def test_known_shortfalls_are_recorded_not_silent() -> None:
    """Criterion 4: the gaps are asserted to their exact extent."""
    assert set(KNOWN_SHORTFALLS) == {
        "no_verifier_exercised",
        "unresolvable_outcome_unnamed",
    }, (
        "the recorded shortfalls changed; update the README in the same commit "
        "so the set never claims more coverage than it has"
    )
    deferred = [v for v in _vectors() if _outcome(v) == "deferred"]
    assert len(deferred) == 2, (
        "unresolvable_outcome_unnamed is recorded as covering exactly two "
        f"vectors; found {len(deferred)}"
    )
