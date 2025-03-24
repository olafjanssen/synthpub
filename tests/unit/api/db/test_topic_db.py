"""Unit tests for topic database operations."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from api.db.topic_db import (
    _ensure_cache,
    _load_all_topics_from_disk,
    create_topic,
    ensure_db_exists,
    get_topic,
    list_topics,
    load_feed_items,
    load_topics,
    mark_topic_deleted,
    save_topic,
    update_topic,
)
from api.models import Topic


@pytest.fixture
def mock_topic():
    """Create a mock topic for testing."""
    return Topic(
        id="test-topic-123",
        name="Test Topic",
        title="Test Topic",
        description="This is a test topic",
        feed_urls=["http://example.com/feed1", "http://example.com/feed2"],
        created_at=datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime(2023, 1, 2, 12, 0, 0),
        deleted=False,
        feed_sources=[],
        feed_items=[],
    )


@pytest.fixture
def mock_topics():
    """Create a list of mock topics for testing."""
    return [
        Topic(
            id="test-topic-123",
            name="Test Topic 1",
            title="Test Topic 1",
            description="This is test topic 1",
            feed_urls=["http://example.com/feed1", "http://example.com/feed2"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 2, 12, 0, 0),
            deleted=False,
            feed_sources=[],
            feed_items=[],
        ),
        Topic(
            id="test-topic-456",
            name="Test Topic 2",
            title="Test Topic 2",
            description="This is test topic 2",
            feed_urls=["http://example.com/feed3", "http://example.com/feed4"],
            created_at=datetime(2023, 1, 3, 12, 0, 0),
            updated_at=datetime(2023, 1, 4, 12, 0, 0),
            deleted=False,
            feed_sources=[],
            feed_items=[],
        ),
    ]


def test_ensure_cache():
    """Test ensuring the topic cache is initialized."""
    mock_topics_list = [
        Topic(
            id="test-topic-123",
            name="Test Topic",
            title="Test Topic",
            description="This is a test topic",
            feed_urls=["http://example.com/feed1"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 2, 12, 0, 0),
            deleted=False,
            feed_sources=[],
            feed_items=[],
        )
    ]
    with patch("api.db.topic_db._cache_initialized", False):
        with patch(
            "api.db.topic_db._load_all_topics_from_disk", return_value=mock_topics_list
        ):
            with patch("api.db.topic_db._topic_cache", {}) as mock_cache:
                _ensure_cache()
                assert mock_cache == {mock_topics_list[0].id: mock_topics_list[0]}
                from api.db.topic_db import _cache_initialized

                assert _cache_initialized is True


def test_load_all_topics_from_disk(mock_topic):
    """Test loading all topics from disk."""
    yaml_content = yaml.dump(mock_topic.model_dump())
    with patch("api.db.topic_db.ensure_db_exists"):
        with patch("api.db.topic_db.db_path", return_value=Path("/mock/db/topics")):
            with patch(
                "pathlib.Path.glob",
                return_value=[Path("/mock/db/topics/test-topic.yaml")],
            ):
                with patch("builtins.open", mock_open(read_data=yaml_content)):
                    result = _load_all_topics_from_disk()
                    assert len(result) == 1
                    assert result[0].id == mock_topic.id
                    assert result[0].name == mock_topic.name


def test_ensure_db_exists():
    """Test that the DB directory is created if it doesn't exist."""
    with patch("api.db.topic_db.db_path", return_value=Path("/mock/db/topics")):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            ensure_db_exists()
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_save_topic(mock_topic):
    """Test saving a topic to file."""
    with patch("api.db.topic_db.ensure_db_exists"):
        with patch("api.db.topic_db.db_path", return_value=Path("/mock/db/topics")):
            with patch("builtins.open", mock_open()) as mock_file:
                save_topic(mock_topic)
                mock_file.assert_called_once_with(
                    Path("/mock/db/topics/test-topic-123.yaml"), "w", encoding="utf-8"
                )


def test_get_topic(mock_topic):
    """Test retrieving a topic."""
    with patch("api.db.topic_db._ensure_cache"):
        with patch("api.db.topic_db._topic_cache", {mock_topic.id: mock_topic}):
            result = get_topic(mock_topic.id)
            assert result == mock_topic


def test_get_topic_not_found():
    """Test retrieving a non-existent topic."""
    with patch("api.db.topic_db._ensure_cache"):
        with patch("api.db.topic_db._topic_cache", {}):
            result = get_topic("non-existent-id")
            assert result is None


def test_list_topics(mock_topics):
    """Test listing all topics."""
    topic_dict = {topic.id: topic for topic in mock_topics}
    with patch("api.db.topic_db._ensure_cache"):
        with patch("api.db.topic_db._topic_cache", topic_dict):
            result = list_topics()
            assert len(result) == 2
            assert result[0].id in [mock_topics[0].id, mock_topics[1].id]
            assert result[1].id in [mock_topics[0].id, mock_topics[1].id]
            assert result[0].id != result[1].id


def test_load_topics(mock_topics):
    """Test loading topics as a dictionary."""
    topic_dict = {topic.id: topic for topic in mock_topics}
    with patch("api.db.topic_db._ensure_cache"):
        with patch("api.db.topic_db._topic_cache", topic_dict):
            result = load_topics()
            assert result == topic_dict


def test_create_topic():
    """Test creating a new topic."""
    with patch("api.db.topic_db.uuid.uuid4", return_value="test-uuid"):
        with patch("api.db.topic_db.save_topic") as mock_save:
            with patch("api.db.topic_db.Topic") as mock_topic_class:
                # Setup the mock to return a properly configured Topic object
                mock_topic = MagicMock()
                mock_topic.id = "test-uuid"
                mock_topic.title = "New Topic"
                mock_topic.description = "This is a new topic"
                mock_topic_class.return_value = mock_topic

                result = create_topic(
                    title="New Topic", description="This is a new topic"
                )

                # Verify we tried to create a Topic with the right parameters
                mock_topic_class.assert_called_once()

                assert result.id == "test-uuid"
                assert result.title == "New Topic"
                assert result.description == "This is a new topic"
                mock_save.assert_called_once()
                # Cache invalidation is not directly called in create_topic


def test_mark_topic_deleted(mock_topic):
    """Test marking a topic as deleted."""
    with patch("api.db.topic_db.get_topic", return_value=mock_topic):
        with patch("api.db.topic_db.db_path", return_value=Path("/mock/db/topics")):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("os.rename") as mock_rename:
                    with patch("os.path.isdir", return_value=False):
                        # Mock article_db's mark_article_deleted to avoid that call
                        with patch(
                            "api.db.article_db.mark_article_deleted", return_value=True
                        ):
                            # Use MagicMock for project_db with list_projects method
                            mock_project_db = MagicMock()
                            mock_project_db.list_projects.return_value = []

                            # Patch the import statement used in mark_topic_deleted
                            with patch.dict(
                                "sys.modules", {"api.db.project_db": mock_project_db}
                            ):
                                result = mark_topic_deleted(mock_topic.id)
                                assert result is True
                                # We no longer expect save_topic to be called
                                mock_rename.assert_called_once()
                                # Cache handling is done directly by popping from _topic_cache dict


def test_update_topic(mock_topic):
    """Test updating a topic."""
    # Keep a reference to the original description
    original_description = mock_topic.description

    with patch("api.db.topic_db.get_topic", return_value=mock_topic):
        with patch("api.db.topic_db.save_topic") as mock_save:
            # Simulate topic being modified in place
            updated_data = {"description": "Updated description"}

            # When update_topic is called, it will directly modify the mock_topic instance
            # So we need to verify this happens
            def assert_topic_modified(*args, **kwargs):
                assert mock_topic.description == "Updated description"
                return None

            # Mock save_topic to also verify the updated mock_topic
            mock_save.side_effect = assert_topic_modified

            # Run the test
            result = update_topic(mock_topic.id, updated_data)

            # Verify results
            assert result.description == "Updated description"
            assert original_description != result.description
            mock_save.assert_called_once_with(mock_topic)
            # Cache invalidation is handled by save_topic, not directly


def test_update_topic_not_found():
    """Test updating a non-existent topic."""
    with patch("api.db.topic_db.get_topic", return_value=None):
        result = update_topic("non-existent-id", {"title": "Updated Title"})
        assert result is None


def test_load_feed_items():
    """Test loading feed items from data."""
    items_data = [
        {
            "title": "Test Item 1",
            "url": "http://example.com/1",
            "summary": "Test summary 1",
            "published": "2023-01-01T12:00:00",
            "image_url": "http://example.com/image1.jpg",
            "accessed_at": "2023-01-01T12:30:00",
            "content_hash": "hash1234567890",
        },
        {
            "title": "Test Item 2",
            "url": "http://example.com/2",
            "summary": "Test summary 2",
            "published": "2023-01-02T12:00:00",
            "image_url": "http://example.com/image2.jpg",
            "accessed_at": "2023-01-02T12:30:00",
            "content_hash": "hash0987654321",
        },
    ]
    result = load_feed_items(items_data)
    assert len(result) == 2
    assert result[0].url == "http://example.com/1"
    assert result[1].url == "http://example.com/2"
