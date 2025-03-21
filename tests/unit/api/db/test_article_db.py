"""Unit tests for article database operations."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import yaml

from src.api.db.article_db import (
    article_to_files,
    create_article,
    files_to_article,
    get_article,
    get_article_history,
    get_latest_version,
    list_articles,
    mark_article_deleted,
    save_article,
    update_article,
)
from src.api.models.article import Article
from src.api.models.feed_item import FeedItem
from src.api.models.topic import Topic


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
        source_feed=None,
    )


@pytest.fixture
def mock_topic():
    """Create a mock topic for testing."""
    return Topic(
        id="test-topic-456",
        name="Test Topic",
        description="A topic for testing",
        feed_urls=["http://example.com/feed"],
        article=None,
    )


@pytest.fixture
def mock_article_files(tmp_path):
    """Create mock article files for testing."""
    article_path = tmp_path / "test-article"
    article_path.mkdir()

    metadata = {
        "id": "test-article-123",
        "title": "Test Article",
        "topic_id": "test-topic-456",
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-02T12:00:00",
        "version": 1,
        "previous_version": None,
        "next_version": None,
        "source_feed": None,
    }

    metadata_file = article_path / "metadata.yaml"
    with open(metadata_file, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f)

    content_file = article_path / "article.md"
    with open(content_file, "w", encoding="utf-8") as f:
        f.write("This is test content.")

    return article_path


def test_article_to_files(mock_article, tmp_path):
    """Test saving an article to files."""
    article_path = tmp_path / "article"
    article_path.mkdir()

    article_to_files(mock_article, article_path)

    metadata_file = article_path / "metadata.yaml"
    content_file = article_path / "article.md"

    assert metadata_file.exists()
    assert content_file.exists()

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = yaml.safe_load(f)
        assert metadata["id"] == mock_article.id
        assert metadata["title"] == mock_article.title

    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert content == mock_article.content


def test_files_to_article(mock_article_files):
    """Test loading an article from files."""
    metadata_file = mock_article_files / "metadata.yaml"

    article = files_to_article(metadata_file)

    assert article.id == "test-article-123"
    assert article.title == "Test Article"
    assert article.content == "This is test content."
    assert article.version == 1
    assert article.created_at.isoformat() == "2023-01-01T12:00:00"
    assert article.updated_at.isoformat() == "2023-01-02T12:00:00"


def test_save_article(mock_article, mock_topic):
    """Test saving an article."""
    with patch("src.api.db.topic_db.get_topic") as mock_get_topic:
        with patch("src.api.db.topic_db.get_topic_location") as mock_get_location:
            with patch("src.api.db.article_db.get_article_path") as mock_get_path:
                with patch("src.api.db.article_db.article_to_files") as mock_to_files:
                    with patch("pathlib.Path.exists", return_value=True):
                        with patch("src.api.db.article_db.add_to_entity_cache"):
                            with patch("src.api.db.topic_db.save_topic"):
                                # Setup mocks
                                mock_get_topic.return_value = mock_topic
                                mock_get_location.return_value = (
                                    "project-slug",
                                    "topic-slug",
                                )
                                mock_path = Path("/mock/path")
                                mock_get_path.return_value = mock_path

                                # Test function
                                save_article(mock_article)

                                # Verify calls
                                mock_get_topic.assert_called_once_with(
                                    mock_article.topic_id
                                )
                                mock_get_location.assert_called_once_with(
                                    mock_article.topic_id
                                )
                                mock_get_path.assert_called_once()
                                mock_to_files.assert_called_once_with(
                                    mock_article, mock_path
                                )


def test_get_article():
    """Test retrieving an article."""
    with patch("src.api.db.article_db.find_entity_by_id") as mock_find:
        with patch("src.api.db.article_db.files_to_article") as mock_to_article:
            # Setup mocks
            mock_path = Path("/mock/path")
            mock_find.return_value = (mock_path, "article")
            mock_article = Article(
                id="test-article-123",
                title="Test Article",
                topic_id="test-topic-456",
                content="This is test content.",
                version=1,
                created_at=datetime(2023, 1, 1, 12, 0, 0),
            )
            mock_to_article.return_value = mock_article

            # Test function with path.exists=True
            with patch("pathlib.Path.exists", return_value=True):
                article = get_article("test-article-123")
                assert article == mock_article

            # Test function with path.exists=False
            with patch("pathlib.Path.exists", return_value=False):
                article = get_article("non-existent-article")
                assert article is None


def test_list_articles():
    """Test listing all articles."""
    with patch("src.api.db.article_db.get_hierarchical_path") as mock_get_path:
        with patch("pathlib.Path.glob") as mock_glob:
            with patch("src.api.db.article_db.files_to_article") as mock_to_article:
                # Setup mocks
                mock_path = Path("/mock/vault")
                mock_get_path.return_value = mock_path

                # Create Mock paths with proper parent structure
                metadata_file1 = MagicMock(spec=Path)
                metadata_file1.parent.parent.parent.parent = mock_path

                metadata_file2 = MagicMock(spec=Path)
                metadata_file2.parent.parent.parent.parent = mock_path

                mock_glob.return_value = [metadata_file1, metadata_file2]

                mock_article1 = Article(
                    id="article1",
                    title="Article 1",
                    topic_id="topic1",
                    content="Content 1",
                    version=1,
                    created_at=datetime(2023, 1, 1, 12, 0, 0),
                )

                mock_article2 = Article(
                    id="article2",
                    title="Article 2",
                    topic_id="topic2",
                    content="Content 2",
                    version=1,
                    created_at=datetime(2023, 1, 2, 12, 0, 0),
                )

                mock_to_article.side_effect = [mock_article1, mock_article2]

                # Test function
                articles = list_articles()
                assert len(articles) == 2
                assert articles[0] == mock_article1
                assert articles[1] == mock_article2


def test_create_article():
    """Test creating a new article."""
    with patch("src.api.db.article_db.uuid.uuid4", return_value="test-uuid"):
        with patch("src.api.db.article_db.save_article") as mock_save:
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


def test_update_article(mock_article, mock_topic):
    """Test updating an existing article."""
    with patch("src.api.db.article_db.get_article", return_value=mock_article):
        with patch("src.api.db.article_db.save_article") as mock_save:
            with patch("src.api.db.topic_db.get_topic") as mock_get_topic:
                with patch("src.api.db.topic_db.save_topic") as mock_save_topic:
                    # Setup topic mock
                    mock_get_topic.return_value = mock_topic

                    # Test function
                    feed_item = FeedItem(
                        title="Feed Item",
                        url="http://example.com",
                        summary="Summary",
                        accessed_at=datetime.now(),
                        content_hash="test_hash_12345",
                    )
                    result = update_article(
                        "test-article-123", "Updated content", feed_item
                    )

                    # Verify result
                    assert result.content == "Updated content"
                    assert result.source_feed == feed_item
                    assert result.version == 2

                    # Verify calls
                    assert mock_save.call_count == 2  # Save both old and new article
                    mock_get_topic.assert_called_once()
                    mock_save_topic.assert_called_once()


def test_update_article_not_found():
    """Test updating a non-existent article."""
    with patch("src.api.db.article_db.get_article", return_value=None):
        result = update_article("non-existent-article", "Updated content")
        assert result is None


def test_get_article_history(mock_article):
    """Test retrieving article history."""
    # Create mock articles for different versions
    mock_v1 = mock_article
    mock_v1.next_version = "article-v2"

    mock_v2 = Article(
        id="article-v2",
        title=mock_article.title,
        topic_id=mock_article.topic_id,
        content="Updated content",
        version=2,
        created_at=mock_article.created_at,
        updated_at=datetime(2023, 1, 3, 12, 0, 0),
        previous_version=mock_v1.id,
        next_version=None,
        source_feed=None,
    )

    with patch("src.api.db.article_db.get_article") as mock_get:
        # Mock get_article to return different versions
        mock_get.side_effect = lambda id: {
            mock_v1.id: mock_v1,
            mock_v2.id: mock_v2,
        }.get(id)

        # Test function
        result = get_article_history(mock_v1.id)
        assert len(result) == 2
        assert result[0].id == mock_v1.id
        assert result[1].id == mock_v2.id


def test_get_latest_version(mock_article):
    """Test retrieving the latest article version."""
    # Create mock articles for different versions
    mock_v1 = mock_article
    mock_v1.next_version = "article-v2"

    mock_v2 = Article(
        id="article-v2",
        title=mock_article.title,
        topic_id=mock_article.topic_id,
        content="Updated content",
        version=2,
        created_at=mock_article.created_at,
        updated_at=datetime(2023, 1, 3, 12, 0, 0),
        previous_version=mock_v1.id,
        next_version=None,
        source_feed=None,
    )

    with patch("src.api.db.article_db.get_article") as mock_get:
        # Mock get_article to return different versions
        mock_get.side_effect = lambda id: {
            mock_v1.id: mock_v1,
            mock_v2.id: mock_v2,
        }.get(id)

        # Test function
        result = get_latest_version(mock_v1.id)
        assert result.id == mock_v2.id
        assert result.version == 2


def test_mark_article_deleted():
    """Test marking an article as deleted."""
    with patch("src.api.db.article_db.find_entity_by_id") as mock_find:
        with patch("src.api.db.article_db.remove_from_entity_cache") as mock_remove:
            with patch("src.api.db.article_db.get_article", return_value=None):
                # Create a properly mocked path that won't try to use the real file system
                mock_path = MagicMock(spec=Path)
                mock_path.exists.return_value = True
                mock_find.return_value = (mock_path, "article")

                # Mock the rmtree function to avoid actually removing files
                with patch("src.api.db.article_db.rmtree") as mock_rmtree:
                    # Test function
                    result = mark_article_deleted("test-article-123")

                    # Verify results
                    assert result is True
                    mock_rmtree.assert_called_once_with(mock_path)
                    mock_remove.assert_called_once_with("test-article-123")
