"""Every copy of the digest-format pattern, compared against the schema.

The string `^sha(256:[0-9a-f]{64}|384:[0-9a-f]{96})$` exists in eleven places:
six `pattern` values in `schemas/trace-claim.json` and five compiled constants
in the modules and the tests. Eleven copies of one rule, and changing any one of
them is a silent change to what the suite accepts.

`test_enum_parity.py` is the same guard for the hand-written enums.
`measurement/scripts/enum_drift.py` is what discovers an unknown copy, but it
finds them by walking the AST for a set of string constants, so a compiled regex
is invisible to it by construction. That is why these eleven were unguarded
while the five enum copies were not.

The schema sites are named here rather than discovered by walking, so a seventh
digest field appearing later fails the count below instead of joining silently.

Near misses, deliberately not listed: src/trace_tests/inclusion.py
and tests/test_report.py each pin a sha256-only pattern. That is a
narrower rule than this one, not a twelfth copy of it.
"""

from __future__ import annotations

import pytest

from tests.test_level0 import DIGEST_RE
from trace_tests.modules.tr_pol import _DIGEST_RE as TR_POL_DIGEST_RE
from trace_tests.modules.tr_rte import _DIGEST_RE as TR_RTE_DIGEST_RE
from trace_tests.modules.tr_sca import _DIGEST_RE as TR_SCA_DIGEST_RE
from trace_tests.modules.tr_txn import _DIGEST_RE as TR_TXN_DIGEST_RE

# The schema properties whose `pattern` is the digest format, enumerated rather
# than searched for. A new digest-shaped field is a decision about what this
# suite pins, so it joins this list deliberately or fails
# `test_every_known_site_is_listed`.
SCHEMA_SITES = [
    ("model", "weights_digest"),
    ("runtime", "measurement"),
    ("policy", "bundle_hash"),
    ("tool_transcript", "hash"),
    ("delegation", "parent_record_hash"),
    ("build_provenance", "digest"),
]

# (label, the compiled copy). Lambdas for the same reason `test_enum_parity.py`
# uses them: the value is read when the case runs, not when this module loads.
COMPILED_COPIES = [
    ("tr_pol._DIGEST_RE", lambda: TR_POL_DIGEST_RE),
    ("tr_rte._DIGEST_RE", lambda: TR_RTE_DIGEST_RE),
    ("tr_sca._DIGEST_RE", lambda: TR_SCA_DIGEST_RE),
    ("tr_txn._DIGEST_RE", lambda: TR_TXN_DIGEST_RE),
    ("test_level0.DIGEST_RE", lambda: DIGEST_RE),
]


def _schema_pattern(schema: dict, parent: str, child: str) -> str:
    return str(schema["properties"][parent]["properties"][child]["pattern"])


def _reference(schema: dict) -> str:
    """The pattern the compiled copies are held to.

    Any of the six would serve; `test_every_schema_digest_site_holds_one_pattern`
    is what makes the choice arbitrary rather than load-bearing. Drift in this
    particular site therefore reds the copy cases too, which is true rather than
    noisy: the string they are all held to is the one that moved.
    """
    return _schema_pattern(schema, *SCHEMA_SITES[0])


def test_every_schema_digest_site_holds_one_pattern(schema) -> None:
    """The six schema copies, against each other.

    Grouped rather than compared pairwise so the failure says which sites hold
    which string, instead of naming one site and leaving the reader to find its
    partner.
    """
    by_pattern: dict[str, list[str]] = {}
    for parent, child in SCHEMA_SITES:
        site = f"{parent}.{child}"
        by_pattern.setdefault(_schema_pattern(schema, parent, child), []).append(site)

    assert len(by_pattern) == 1, "the schema's digest patterns have drifted apart\n" + "\n".join(
        f"  {pattern!r}\n    {', '.join(sites)}" for pattern, sites in sorted(by_pattern.items())
    )


@pytest.mark.parametrize(
    "label,get_copy", COMPILED_COPIES, ids=[c[0] for c in COMPILED_COPIES]
)
def test_a_compiled_digest_copy_matches_the_schema(label, get_copy, schema) -> None:
    """Byte equality against the schema string, not equivalence.

    Two patterns can accept the same inputs and still be different rules to the
    next person who edits one of them. The schema is the source; a copy that has
    been improved locally is still a copy that no longer says what the schema
    says.
    """
    declared = get_copy().pattern
    expected = _reference(schema)
    assert declared == expected, (
        f"{label} has drifted from the schema's digest pattern\n"
        f"  the copy:   {declared!r}\n"
        f"  the schema: {expected!r}"
    )


def test_every_known_site_is_listed() -> None:
    """A guard on the guard, in the shape `test_enum_parity.py` already uses.

    Eleven sites carry this pattern: six in the schema and five compiled. Adding
    a twelfth without listing it here would leave it unguarded, which is the
    state this file exists to end.
    """
    assert len(SCHEMA_SITES) == 6
    assert len(COMPILED_COPIES) == 5
