"""Simple test file that always passes."""

import pytest


def test_always_passes():
    """Test that always passes."""
    assert True


def test_basic_math():
    """Test basic math operations."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """Test string operations."""
    assert "hello" + " world" == "hello world"
    assert len("test") == 4


def test_list_operations():
    """Test list operations."""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert test_list[0] == 1


def test_dict_operations():
    """Test dictionary operations."""
    test_dict = {"key": "value"}
    assert test_dict["key"] == "value"
    assert "key" in test_dict
