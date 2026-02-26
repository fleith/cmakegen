"""Tests for cmakegen.invocation_log."""

import os
import tempfile

import pytest

from cmakegen.invocation_log import clear_log, log_invocation, read_invocations


@pytest.fixture
def log_path(tmp_path):
    return str(tmp_path / "test_log.jsonl")


def test_append_and_read(log_path):
    inv = {"source_files": ["main.cpp"], "compile_only": True}
    log_invocation(log_path, inv)
    result = read_invocations(log_path)
    assert len(result) == 1
    assert result[0] == inv


def test_multiple_entries(log_path):
    inv1 = {"source_files": ["main.cpp"], "compile_only": True}
    inv2 = {"source_files": ["impl0.cpp"], "compile_only": True}
    log_invocation(log_path, inv1)
    log_invocation(log_path, inv2)
    result = read_invocations(log_path)
    assert len(result) == 2
    assert result[0] == inv1
    assert result[1] == inv2


def test_clear(log_path):
    log_invocation(log_path, {"source_files": ["main.cpp"]})
    clear_log(log_path)
    result = read_invocations(log_path)
    assert result == []


def test_read_nonexistent(log_path):
    result = read_invocations(log_path)
    assert result == []


def test_clear_nonexistent(log_path):
    # Should not raise
    clear_log(log_path)
