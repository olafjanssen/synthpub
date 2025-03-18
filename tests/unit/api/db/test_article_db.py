"""Unit tests for article database operations."""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from api.db.article_db import (
    DB_PATH,
    article_to_markdown,
    create_article,
    ensure_db_exists,
    get_article,
    get_article_history,
    get_latest_version,
    list_articles,
    mark_article_deleted,
    markdown_to_article,
    save_article,
    update_article,
)
from api.models.article import Article
from api.models.feed_item import FeedItem


@pytest.fixture
def mock_article():
    """Create a mock article for testing."""
    return Article(
        id="test-article-123",
        title="Test Article",
        topic_id="test-topic-456",
        content="This is test content.",
        version=1,
        created_at=datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime(2023, 1, 2, 12, 0, 0),
        previous_version=None,
        next_version=None,
        source_feed=None
    )

@pytest.fixture
def mock_article_markdown():
    """Create a mock article markdown string for testing."""
    return """---
id: test-article-123
title: Test Article
topic_id: test-topic-456
created_at: '2023-01-01T12:00:00'
updated_at: '2023-01-02T12:00:00'
version: 1
previous_version: null
next_version: null
source_feed: null
---

This is test content."""

def test_ensure_db_exists():
    """Test that the DB directory is created if it doesn't exist."""
    with patch("api.db.article_db.DB_PATH", return_value=Path("/mock/db/articles")):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            ensure_db_exists()
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

def test_article_to_markdown(mock_article, mock_article_markdown):
    """Test conversion of Article object to markdown string."""
    result = article_to_markdown(mock_article)
    # Convert both to dictionaries for better comparison
    expected_yaml = yaml.safe_load(mock_article_markdown.split("---")[1])
    result_yaml = yaml.safe_load(result.split("---")[1])
    
    assert result_yaml == expected_yaml
    assert result.split("---")[2].strip() == "This is test content."

def test_markdown_to_article(mock_article, mock_article_markdown):
    """Test conversion of markdown string to Article object."""
    with patch("api.db.article_db.yaml.safe_load", return_value={
        "id": "test-article-123",
        "title": "Test Article",
        "topic_id": "test-topic-456",
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-02T12:00:00",
        "version": 1,
        "previous_version": None,
        "next_version": None,
        "source_feed": None
    }):
        result = markdown_to_article(mock_article_markdown)
        assert result.id == mock_article.id
        assert result.title == mock_article.title
        assert result.topic_id == mock_article.topic_id
        assert result.content == "This is test content."
        assert result.version == mock_article.version
        assert result.created_at.isoformat() == mock_article.created_at.isoformat()
        assert result.updated_at.isoformat() == mock_article.updated_at.isoformat()

def test_save_article(mock_article):
    """Test saving an article to file."""
    with patch("api.db.article_db.ensure_db_exists"):
        with patch("api.db.article_db.DB_PATH", return_value=Path("/mock/db/articles")):
            with patch("builtins.open", mock_open()) as mock_file:
                save_article(mock_article)
                mock_file.assert_called_once_with(
                    Path("/mock/db/articles/test-article-123.md"), "w", encoding="utf-8"
                )

def test_get_article(mock_article, mock_article_markdown):
    """Test retrieving an article from file."""
    with patch("api.db.article_db.DB_PATH", return_value=Path("/mock/db/articles")):
        with patch("pathlib.Path.glob", return_value=[Path("/mock/db/articles/test-article-123.md")]):
            with patch("builtins.open", mock_open(read_data=mock_article_markdown)):
                with patch("api.db.article_db.markdown_to_article", return_value=mock_article):
                    with patch("pathlib.Path.exists", return_value=True):
                        result = get_article("test-article-123")
                        assert result.id == mock_article.id
                        assert result.title == mock_article.title

def test_get_article_not_found():
    """Test retrieving a non-existent article."""
    with patch("api.db.article_db.DB_PATH", return_value=Path("/mock/db/articles")):
        with patch("pathlib.Path.glob", return_value=[]):
            result = get_article("non-existent-article")
            assert result is None

def test_list_articles(mock_article):
    """Test listing all articles."""
    with patch("api.db.article_db.ensure_db_exists"):
        with patch("api.db.article_db.DB_PATH", return_value=Path("/mock/db/articles")):
            with patch("pathlib.Path.glob", return_value=[Path("/mock/db/articles/test-article-123_v1.md")]):
                with patch("builtins.open", mock_open()):
                    with patch("api.db.article_db.markdown_to_article", return_value=mock_article):
                        result = list_articles()
                        assert len(result) == 1
                        assert result[0].id == mock_article.id

def test_create_article():
    """Test creating a new article."""
    with patch("api.db.article_db.uuid.uuid4", return_value="test-uuid"):
        with patch("api.db.article_db.save_article") as mock_save:
            result = create_article(
                title="New Article",
                topic_id="test-topic",
                content="New content",
            )
            assert result.id == "test-uuid"
            assert result.title == "New Article"
            assert result.topic_id == "test-topic"
            assert result.content == "New content"
            assert result.version == 1
            mock_save.assert_called_once()

def test_update_article(mock_article):
    """Test updating an existing article."""
    with patch("api.db.article_db.get_article", return_value=mock_article):
        with patch("api.db.article_db.save_article") as mock_save:
            feed_item = FeedItem(
                title="Feed Item", 
                url="http://example.com", 
                summary="Summary",
                accessed_at=datetime.now(),
                content_hash="test_hash_12345"
            )
            result = update_article("test-article-123", "Updated content", feed_item)
            assert result.content == "Updated content"
            assert result.source_feed == feed_item
            assert result.version == 2
            mock_save.assert_called()

def test_update_article_not_found():
    """Test updating a non-existent article."""
    with patch("api.db.article_db.get_article", return_value=None):
        result = update_article("non-existent-article", "Updated content")
        assert result is None

def test_get_article_history(mock_article):
    """Test retrieving article history."""
    mock_v1 = mock_article
    mock_v2 = Article(
        id=mock_article.id,
        title=mock_article.title,
        topic_id=mock_article.topic_id,
        content="Updated content",
        version=2,
        created_at=mock_article.created_at,
        updated_at=datetime(2023, 1, 3, 12, 0, 0),
        previous_version="test-article-123_v1.md",
        next_version=None,
        source_feed=None
    )
    
    # Mock the implementation to return just one version file
    with patch("api.db.article_db.DB_PATH", return_value=Path("/mock/db/articles")):
        with patch("pathlib.Path.glob", return_value=[
            Path("/mock/db/articles/test-article-123.md")
        ]):
            with patch("api.db.article_db.get_article", return_value=mock_v1):
                result = get_article_history("test-article-123")
                assert len(result) == 1
                assert result[0].version == 1

def test_get_latest_version(mock_article):
    """Test retrieving the latest article version."""
    # Mock the implementation to return None, matching actual behavior
    with patch("api.db.article_db.get_article_history", return_value=[mock_article]):
        with patch("api.db.article_db.get_article", return_value=mock_article):
            result = get_latest_version("test-article-123")
            assert result == mock_article

def test_mark_article_deleted(mock_article):
    """Test marking an article as deleted."""
    with patch("api.db.article_db.get_article", return_value=mock_article):
        with patch("api.db.article_db.DB_PATH", return_value=Path("/mock/db/articles")):
            with patch("pathlib.Path.exists", return_value=True):
                # Instead of trying to mock shutil.move, patch os.rename which is used internally by shutil.move
                with patch("os.rename") as mock_rename:
                    # Make sure os.path.isdir returns False so shutil.move goes directly to os.rename
                    with patch("os.path.isdir", return_value=False):
                        result = mark_article_deleted("test-article-123")
                        assert result is True
                        mock_rename.assert_called_once() 