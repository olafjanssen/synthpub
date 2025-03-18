"""
Integration tests for article endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.models.article import Article


@pytest.fixture
def mock_article():
    """Mock article data for testing."""
    return {
        "id": "test-article-id",
        "title": "Test Article",
        "content": "Test content",
        "author": "Test Author",
        "created_at": "2024-03-20T10:00:00",
        "updated_at": None,
        "topic_id": "test-topic-id",
        "version": 1,
        "previous_version": None,
        "next_version": None,
        "source_feed": {
            "url": "https://example.com/feed",
            "title": "Test Feed",
            "content_hash": "test-content-hash",
            "last_updated": "2024-03-20T10:00:00",
            "accessed_at": "2024-03-20T10:00:00"
        }
    }


@pytest.fixture
def mock_article_db(monkeypatch, mock_article):
    """Mock article database functions."""
    def mock_get_article(article_id: str):
        """Mock get_article function."""
        if article_id == "test-article-id":
            return Article(**mock_article)
        return None
    
    # Mock the get_article function
    monkeypatch.setattr("api.routes.article_routes.get_article", mock_get_article)
    return mock_article


def test_get_article(client, mock_article_db):
    """Test getting a specific article."""
    response = client.get("/api/articles/test-article-id")
    assert response.status_code == 200
    assert response.json()["id"] == "test-article-id"
    assert response.json()["title"] == "Test Article"


def test_get_nonexistent_article(client, mock_article_db):
    """Test getting a nonexistent article."""
    response = client.get("/api/articles/nonexistent-id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() 