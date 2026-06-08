import json
import pathlib
import pytest

VECTORS_DIR = pathlib.Path(__file__).parent / "vectors"
SCHEMAS_DIR = pathlib.Path(__file__).parent.parent / "schemas"


def load_vector(filename):
    return json.loads((VECTORS_DIR / filename).read_text())


def load_schema():
    return json.loads((SCHEMAS_DIR / "trace-claim.json").read_text())


@pytest.fixture
def schema():
    return load_schema()


@pytest.fixture
def valid_level0():
    return load_vector("valid_level0.json")


@pytest.fixture
def valid_level0_with_transcript():
    return load_vector("valid_level0_with_transcript.json")


@pytest.fixture
def invalid_missing_runtime():
    return load_vector("invalid_missing_runtime.json")


@pytest.fixture
def invalid_wrong_profile():
    return load_vector("invalid_wrong_profile.json")
