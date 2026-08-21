"""The published error codes and record samples must agree with the modules.

Every check here comes from drift that was live in `main`, not from first principles.
`TR-SIG-005` was carried by every signature finding and documented nowhere. `TR-ANC-002`
was documented in three files and named by no module, with two descriptions that
disagreed. `docs/levels.md` showed an `anchor` object the closed schema does not define,
and a `runtime.platform` of `sev-snp`, which is not in the enum.

Documentation that disagrees with the code is worse than absent documentation: it reads
as verified. Nothing checked it, which is why all of it survived.
"""
from __future__ import annotations

import json
import pathlib
import re
from typing import Any

import jsonschema

REPO = pathlib.Path(__file__).resolve().parents[1]
MODULES = REPO / "src" / "trace_tests" / "modules"
ERROR_CODES = REPO / "docs" / "error-codes.md"
SCHEMA = REPO / "schemas" / "trace-claim.json"
DOCS = REPO / "docs"

_CODE = re.compile(r"TR-[A-Z]{3}-\d{3}")
_DOCUMENTED_ROW = re.compile(r"^\| (TR-[A-Z]{3}-\d{3}) ", re.M)
_JSON_BLOCK = re.compile(r"```json\n(.*?)```", re.S)


def _codes(text: str) -> set[str]:
    return set(_CODE.findall(text))


def test_the_code_set_named_by_the_modules_matches_the_code_set_documented() -> None:
    """Matched on codes *named in* module source, not on what a ``Finding`` carries.

    Those two sets differ today. ``TR-SIG-003`` appears only inside a message string
    that a ``TR-SIG-005`` finding carries, so it is never a ``Finding.code``. Matching
    on ``Finding.code`` would demand deleting a page entry that documents a real
    condition. Reconciling code and message is a change to the module rather than to
    the documentation, and is not attempted here.

    This is set membership in both directions and nothing more. It cannot tell whether
    a row describes what its code reports, which was a second kind of drift and was
    live here too: the ``TR-SIG-004`` row described private key material in ``cnf.jwk``,
    a condition the module never reports under that code. Catching that would mean
    comparing prose to behaviour, so the rows are checked by reading them.
    """
    named = set()
    for path in sorted(MODULES.glob("*.py")):
        named |= _codes(path.read_text(encoding="utf-8"))
    # A row, not a mention. A code named in passing somewhere on the page is not
    # documented, and treating it as documented would let the check be satisfied
    # by prose that tells a reader nothing.
    documented = set(_DOCUMENTED_ROW.findall(ERROR_CODES.read_text(encoding="utf-8")))

    assert named == documented, (
        f"named by a module, undocumented: {sorted(named - documented)}\n"
        f"documented, named by no module:  {sorted(documented - named)}\n"
        f"Add the row to {ERROR_CODES.relative_to(REPO)}, or delete it. A code in one "
        "place and not the other is a claim nobody checked."
    )


def _without_required(node: Any) -> Any:
    """The schema with every ``required`` list dropped, except inside ``if`` and ``not``.

    The documented samples are fragments: "changes from Level 1", not whole records.
    Validating them as published fails on absent fields and says nothing about the
    fields that are present. Dropping ``required`` leaves every statement about a value
    that *is* there: ``additionalProperties``, ``enum``, ``pattern``, ``type``.

    ``if`` and ``not`` are left intact deliberately. Stripping ``required`` from an
    ``if`` makes it vacuously true, which fires the matching ``then`` against records
    the condition was never meant to reach. The schema's ``origin`` rule does exactly
    that: strip its ``if`` and every sample is required to be ``software-only``.
    """
    if isinstance(node, dict):
        return {
            key: value if key in ("if", "not") else _without_required(value)
            for key, value in node.items()
            if key != "required"
        }
    if isinstance(node, list):
        return [_without_required(item) for item in node]
    return node


def _drop_elisions(node: Any) -> Any:
    """Remove string values that are visibly abbreviated for the page.

    A documented sample writes a signature as ``eyJhbGciOiJFZERTQSJ9...``. That is a
    reader's placeholder, not a claim about the format, and holding it to the schema's
    base64url pattern would report the page style as a defect.
    """
    if isinstance(node, dict):
        return {k: _drop_elisions(v) for k, v in node.items()
                if not (isinstance(v, str) and "..." in v)}
    if isinstance(node, list):
        return [_drop_elisions(v) for v in node]
    return node


def test_every_json_sample_in_the_docs_agrees_with_the_packaged_schema() -> None:
    """Two drifts lived here: an ``anchor`` object the closed schema does not define,
    and a ``runtime.platform`` of ``sev-snp``, which is not in the enum. A reader
    copying either sample produced a record this suite rejects.

    Every ``.md`` under ``docs/`` is scanned rather than a list of pages kept by hand,
    because a hand-maintained list of what gets checked is the same defect this exists
    to catch, in the one place it would not show.

    Prose lists of valid values are not checked, because checking them means reading
    them. ``docs/error-codes.md``, ``docs/levels.md`` and ``docs/modules/tr-rte.md`` all
    listed platform values that do not exist; only the sample was mechanically catchable.
    """
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema.get("additionalProperties") is False, (
        "This test assumes the packaged schema is closed. If that changed, an unknown "
        "field in a sample is no longer necessarily an error and this needs rewriting."
    )
    validator = jsonschema.Draft202012Validator(_without_required(schema))

    failures: dict[str, list[str]] = {}
    validated = 0
    unparsed = 0
    for page in sorted(DOCS.rglob("*.md")):
        for block in _JSON_BLOCK.findall(page.read_text(encoding="utf-8")):
            try:
                sample = json.loads(block)
            except json.JSONDecodeError:
                unparsed += 1
                continue  # prose-annotated fragment, not a record
            if not isinstance(sample, dict):
                continue
            validated += 1
            errors = [e.message for e in validator.iter_errors(_drop_elisions(sample))]
            if errors:
                failures.setdefault(str(page.relative_to(REPO)), []).extend(errors)

    assert not failures, (
        f"JSON samples in the documentation disagree with {SCHEMA.name}, so a reader "
        f"copying one gets a record this suite rejects: {failures}"
    )
    # Without this the check degrades to nothing the moment the samples stop parsing
    # or the fences change, and it degrades silently, reporting a pass over no work.
    assert validated, (
        f"no JSON object sample under {DOCS.relative_to(REPO)} was validated "
        f"({unparsed} block(s) did not parse). Either the samples are gone or the fence "
        "this reads has changed; a check over nothing must not report a pass."
    )
