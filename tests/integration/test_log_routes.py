"""
Integration tests for log endpoints.
"""

import pytest
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

import utils.logging as logging
from api.app import app


@pytest.fixture
def mock_logs():
    """Mock log data for testing."""
    return [
        {
            "id": "log1",
            "timestamp": "2024-03-20T10:00:00",
            "level": "INFO",
            "module": "test",
            "action": "Test Action",
            "details": "Test log details"
        },
        {
            "id": "log2",
            "timestamp": "2024-03-20T10:01:00",
            "level": "ERROR",
            "module": "test",
            "action": "Error Action",
            "details": "Test error details"
        },
        {
            "id": "log3",
            "timestamp": "2024-03-20T10:02:00",
            "level": "WARNING",
            "module": "test",
            "action": "Warning Action",
            "details": "Test warning details"
        }
    ]


@pytest.fixture
def mock_log_db(monkeypatch, mock_logs):
    """Mock log database functions."""
    def mock_get_recent_logs(min_level=None, max_count=None):
        """Mock get_recent_logs function."""
        filtered_logs = mock_logs
        if min_level:
            # Filter by minimum level
            level_order = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
            min_level_value = level_order.get(min_level.upper(), 0)
            filtered_logs = [
                log for log in filtered_logs
                if level_order.get(log["level"].upper(), 0) >= min_level_value
            ]
        if max_count:
            # Limit the number of logs
            filtered_logs = filtered_logs[:max_count]
        return filtered_logs
    
    # Mock the get_recent_logs function
    monkeypatch.setattr("utils.logging.get_recent_logs", mock_get_recent_logs)
    return mock_logs


def test_get_logs(client, mock_log_db):
    """Test retrieving logs."""
    response = client.get("/api/logs/logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 3  # All logs should be returned by default


def test_get_logs_with_level_filter(client, mock_log_db):
    """Test retrieving logs with level filter."""
    response = client.get("/api/logs/logs?min_level=ERROR")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1  # Only ERROR level logs


def test_get_logs_with_count_limit(client, mock_log_db):
    """Test retrieving logs with count limit."""
    response = client.get("/api/logs/logs?count=2")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2  # Only 2 logs should be returned


# WebSocket tests are more complex in FastAPI and typically require
# special testing setup. These tests demonstrate the basic approach
# but may need additional configuration in a real environment.

@pytest.mark.skip(reason="WebSocket tests require additional setup")
def test_log_websocket(client, mock_log_db):
    """Test WebSocket connection for real-time logs."""
    # WebSocket tests are more complex in FastAPI
    # This is a placeholder for future WebSocket testing
    pass 