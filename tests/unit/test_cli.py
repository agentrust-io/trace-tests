"""End-to-end CLI tests for fail-closed behavior."""

import json
import pathlib
import time

import pytest
from click.testing import CliRunner

from trace_tests.cli import main

VECTORS_DIR = pathlib.Path(__file__).parent.parent / "vectors"


@pytest.fixture
def fresh_level0_path(tmp_path):
    vector = json.loads((VECTORS_DIR / "valid_level0.json").read_text())
    vector["iat"] = int(time.time()) - 60
    p = tmp_path / "record.json"
    p.write_text(json.dumps(vector))
    return str(p)


def test_unsigned_record_fails_level_2(fresh_level0_path):
    """Regression: unsigned plain JSON must never pass `verify --level 2`."""
    result = CliRunner().invoke(main, ["verify", "--record", fresh_level0_path, "--level", "2"])
    assert result.exit_code == 1, result.output
    assert "Result: FAIL" in result.output


def test_unsigned_record_fails_level_1(fresh_level0_path):
    result = CliRunner().invoke(main, ["verify", "--record", fresh_level0_path, "--level", "1"])
    assert result.exit_code == 1, result.output


def test_unsigned_record_level_0_reports_unverified(fresh_level0_path):
    result = CliRunner().invoke(main, ["verify", "--record", fresh_level0_path, "--level", "0"])
    assert result.exit_code == 0, result.output
    assert "UNVERIFIED" in result.output
    assert "NOT cryptographically verified" in result.output


def test_stale_record_fails(tmp_path):
    vector = json.loads((VECTORS_DIR / "valid_level0.json").read_text())
    vector["iat"] = int(time.time()) - (25 * 3600)
    p = tmp_path / "stale.json"
    p.write_text(json.dumps(vector))
    result = CliRunner().invoke(main, ["verify", "--record", str(p), "--level", "0"])
    assert result.exit_code == 1, result.output


def test_partial_cmcp_envelope_is_rejected(tmp_path):
    vector = json.loads((VECTORS_DIR / "valid_cmcp_runtime.json").read_text())
    del vector["cmcp_version"]
    p = tmp_path / "partial.json"
    p.write_text(json.dumps(vector))
    result = CliRunner().invoke(main, ["verify", "--record", str(p), "--level", "0"])
    assert result.exit_code == 2, result.output
    assert "partial cmcp-runtime envelope" in result.output
