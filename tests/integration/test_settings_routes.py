"""
Integration tests for settings endpoints.
"""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    test_settings = {
        "db_path": "/test/path/to/db",
        "env_vars": {
            "OPENAI_API_KEY": "test-api-key",
            "MISTRAL_API_KEY": "test-mistralai-key",
            "YOUTUBE_API_KEY": "test-youtube-key",
            "GITLAB_TOKEN": "test-gitlab-token",
            "FTP_USERNAME": "test-ftp-user",
            "FTP_PASSWORD": "test-ftp-password",
        },
        "llm_settings": {
            "article_generation": {
                "provider": "openai",
                "model_name": "gpt-4",
                "max_tokens": 4000,
            },
            "article_refinement": {
                "provider": "mistralai",
                "model_name": "mistral-medium",
                "max_tokens": 3000,
            },
        },
        "scheduler": {
            "enabled": True,
            "update_interval_minutes": 15,
            "update_threshold_hours": 1,
        },
    }

    def mock_load_settings():
        """Mock load_settings function."""
        return test_settings.copy()

    def mock_save_settings(settings):
        """Mock save_settings function."""
        for key, value in settings.items():
            test_settings[key] = value

    monkeypatch.setattr("api.routes.settings.load_settings", mock_load_settings)
    monkeypatch.setattr("api.routes.settings.save_settings", mock_save_settings)

    return test_settings


@pytest.fixture
def mock_webview(monkeypatch):
    """Mock webview module for testing."""
    mock_window = MagicMock()
    mock_window.create_file_dialog.return_value = ["/new/path/to/db"]

    mock_webview = MagicMock()
    mock_webview.windows = [mock_window]
    mock_webview.FOLDER_DIALOG = "folder_dialog"

    # Mock the webview module
    monkeypatch.setattr("api.routes.settings.webview", mock_webview)
    return mock_webview


@pytest.mark.parametrize("is_desktop", [True, False])
def test_get_db_path(client, mock_settings, mock_webview, is_desktop):
    """Test getting the database path."""
    # Configure whether we're in desktop mode
    mock_webview.windows = [mock_webview] if is_desktop else []

    response = client.get("/api/settings/db-path")
    assert response.status_code == 200
    if is_desktop:
        assert response.json()["path"] == "/test/path/to/db"
    else:
        assert "only available in desktop" in response.json()["path"]


def test_get_env_vars_desktop(client, mock_settings, mock_webview):
    """Test getting environment variables in desktop mode."""
    mock_webview.windows = [mock_webview]

    response = client.get("/api/settings/env-vars")
    assert response.status_code == 200
    assert response.json()["variables"]["OPENAI_API_KEY"] == "test-api-key"
    assert response.json()["variables"]["MISTRAL_API_KEY"] == "test-mistralai-key"


def test_get_env_vars_web(client, mock_settings, mock_webview):
    """Test getting environment variables in web mode (masked)."""
    mock_webview.windows = []

    response = client.get("/api/settings/env-vars")
    assert response.status_code == 200
    assert response.json()["variables"]["OPENAI_API_KEY"] == "********"
    assert response.json()["variables"]["MISTRAL_API_KEY"] == "********"


def test_update_env_vars_desktop(client, mock_settings, mock_webview):
    """Test updating environment variables in desktop mode."""
    mock_webview.windows = [mock_webview]

    new_vars = {"OPENAI_API_KEY": "new-api-key", "MISTRAL_API_KEY": "new-mistralai-key"}

    response = client.post("/api/settings/env-vars", json=new_vars)
    assert response.status_code == 200
    assert mock_settings["env_vars"]["OPENAI_API_KEY"] == "new-api-key"
    assert mock_settings["env_vars"]["MISTRAL_API_KEY"] == "new-mistralai-key"


def test_update_env_vars_web(client, mock_settings, mock_webview):
    """Test updating environment variables in web mode (should be forbidden)."""
    mock_webview.windows = []

    new_vars = {"OPENAI_API_KEY": "new-api-key", "MISTRAL_API_KEY": "new-mistralai-key"}

    response = client.post("/api/settings/env-vars", json=new_vars)
    assert response.status_code == 403
    assert "desktop application" in response.json()["detail"]


def test_get_scheduler_settings(client, mock_settings):
    """Test getting scheduler settings."""
    response = client.get("/api/settings/scheduler")
    assert response.status_code == 200
    settings = response.json()["settings"]
    assert settings["enabled"] is True
    assert settings["update_interval_minutes"] == 15
    assert settings["update_threshold_hours"] == 1


def test_update_scheduler_settings_desktop(client, mock_settings, mock_webview):
    """Test updating scheduler settings in desktop mode."""
    mock_webview.windows = [mock_webview]

    new_settings = {
        "enabled": False,
        "update_interval_minutes": 30,
        "update_threshold_hours": 2,
    }

    response = client.post("/api/settings/scheduler", json=new_settings)
    assert response.status_code == 200
    assert mock_settings["scheduler"]["enabled"] is False
    assert mock_settings["scheduler"]["update_interval_minutes"] == 30
    assert mock_settings["scheduler"]["update_threshold_hours"] == 2


def test_update_scheduler_settings_web(client, mock_settings, mock_webview):
    """Test updating scheduler settings in web mode (should be forbidden)."""
    mock_webview.windows = []

    new_settings = {
        "enabled": False,
        "update_interval_minutes": 30,
        "update_threshold_hours": 2,
    }

    response = client.post("/api/settings/scheduler", json=new_settings)
    assert response.status_code == 403
    assert "desktop application" in response.json()["detail"]


def test_get_environment(client, mock_settings, mock_webview):
    """Test checking if running in desktop or browser environment."""
    mock_webview.windows = [mock_webview]  # Simulate desktop mode
    response = client.get("/api/settings/environment")
    assert response.status_code == 200
    assert response.json()["is_desktop"] is True
