"""Unit tests for common database utilities."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from api.db.common import get_base_db_path, get_db_path


@pytest.fixture
def mock_settings():
    return {"db_path": "/mock/db/path"}


def test_get_base_db_path_from_settings(mock_settings):
    """Test getting base db path from settings."""
    with patch("api.db.common.load_settings", return_value=mock_settings):
        result = get_base_db_path()
        assert result == Path("/mock/db/path")


def test_get_base_db_path_from_env():
    """Test getting base db path from environment variable."""
    with patch("api.db.common.load_settings", return_value={}):
        with patch.dict(os.environ, {"DB_PATH": "/env/db/path"}):
            result = get_base_db_path()
            assert result == Path("/env/db/path")


def test_get_base_db_path_default():
    """Test getting default base db path."""
    with patch("api.db.common.load_settings", return_value={}):
        with patch.dict(os.environ, {}, clear=True):
            result = get_base_db_path()
            assert result == Path("../db")


def test_get_db_path():
    """Test getting db path for a specific subfolder."""
    with patch("api.db.common.get_base_db_path", return_value=Path("/base/path")):
        result = get_db_path("test_subfolder")
        assert result == Path("/base/path/test_subfolder")
