"""Unit tests for topic database operations."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from src.api.db.topic_db import (
    _ensure_cache,
    _load_all_topics_from_disk,
    create_topic,
    get_topic,
    get_topic_location,
    get_topic_path,
    list_topics,
    load_feed_items,
    load_topics,
    mark_topic_deleted,
    save_topic,
    update_topic,
)
from src.api.models.feed_item import FeedItem
from src.api.models.topic import Topic


@pytest.fixture
def mock_topic():
    """Create a mock topic for testing."""
    return Topic(
        id="test-topic-123",
        name="Test Topic",
        description="A test topic",
        feed_urls=["http://example.com/feed"],
        created_at=datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime(2023, 1, 2, 12, 0, 0),
        processed_feeds=[],
    )


@pytest.fixture
def mock_topics():
    """Create a list of mock topics for testing."""
    return [
        Topic(
            id="topic-1",
            name="Topic One",
            description="The first topic",
            feed_urls=["http://example.com/feed1"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 2, 12, 0, 0),
            processed_feeds=[],
        ),
        Topic(
            id="topic-2",
            name="Topic Two",
            description="The second topic",
            feed_urls=["http://example.com/feed2"],
            created_at=datetime(2023, 1, 3, 12, 0, 0),
            updated_at=datetime(2023, 1, 4, 12, 0, 0),
            processed_feeds=[],
        ),
    ]


def test_ensure_cache():
    """Test ensuring topic cache is populated."""
    with patch("src.api.db.topic_db._topic_cache", {"test-topic-1": MagicMock()}):
        with patch("src.api.db.topic_db._cache_initialized", False):
            with patch(
                "src.api.db.topic_db._load_all_topics_from_disk", return_value=[]
            ):
                # Call function
                _ensure_cache()

                # Verify cache initialization
                from src.api.db.topic_db import _cache_initialized

                assert _cache_initialized is True


def test_load_all_topics_from_disk(mock_topics):
    """Test loading all topics from disk."""
    with patch("src.api.db.topic_db.get_hierarchical_path") as mock_get_path:
        with patch("src.api.db.project_db._get_project_directories") as mock_get_dirs:
            # Setup vault path
            vault_path = Path("/mock/vault")
            mock_get_path.return_value = vault_path

            # Setup project directories
            project_dir1 = MagicMock(spec=Path)
            project_dir1.name = "project-1"
            project_dir1.is_dir.return_value = True

            project_dir2 = MagicMock(spec=Path)
            project_dir2.name = "project-2"
            project_dir2.is_dir.return_value = True

            mock_get_dirs.return_value = [project_dir1, project_dir2]

            # Setup topic directories within projects
            topic_dir1 = MagicMock(spec=Path)
            topic_dir1.is_dir.return_value = True
            topic_dir1.name = "topic-1"

            topic_dir2 = MagicMock(spec=Path)
            topic_dir2.is_dir.return_value = True
            topic_dir2.name = "topic-2"

            # Mock iterdir for project directories
            project_dir1.iterdir.return_value = [topic_dir1]
            project_dir2.iterdir.return_value = [topic_dir2]

            # Setup metadata files
            metadata_file1 = MagicMock(spec=Path)
            metadata_file1.exists.return_value = True
            metadata_file1.name = "metadata.yaml"

            metadata_file2 = MagicMock(spec=Path)
            metadata_file2.exists.return_value = True
            metadata_file2.name = "metadata.yaml"

            # Mock __truediv__ operator for topic directories
            topic_dir1.__truediv__.return_value = metadata_file1
            topic_dir2.__truediv__.return_value = metadata_file2

            # Setup topic data
            topic_data1 = mock_topics[0].model_dump()
            topic_data1["created_at"] = topic_data1["created_at"].isoformat()
            topic_data1["updated_at"] = topic_data1["updated_at"].isoformat()
            # Ensure required fields are present
            if "processed_feeds" not in topic_data1:
                topic_data1["processed_feeds"] = []
            # Add slug field
            topic_data1["slug"] = "topic-1"

            topic_data2 = mock_topics[1].model_dump()
            topic_data2["created_at"] = topic_data2["created_at"].isoformat()
            topic_data2["updated_at"] = topic_data2["updated_at"].isoformat()
            # Ensure required fields are present
            if "processed_feeds" not in topic_data2:
                topic_data2["processed_feeds"] = []
            # Add slug field
            topic_data2["slug"] = "topic-2"

            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", side_effect=[topic_data1, topic_data2]):
                    # Call function
                    result = _load_all_topics_from_disk()

                    # Check result
                    assert len(result) == 2
                    assert result[0].id == "topic-1"
                    assert result[1].id == "topic-2"


def test_get_topic_path():
    """Test getting the path to a topic directory."""
    with patch("src.api.db.topic_db.get_hierarchical_path") as mock_get_path:
        # Setup mock path
        mock_path = Path("/mock/vault/project-slug/topic-slug")
        mock_get_path.return_value = mock_path

        # Call function
        result = get_topic_path("project-slug", "topic-slug")

        # Check result
        assert result == mock_path


def test_get_topic_location(mock_topic):
    """Test getting the location of a topic."""
    with patch("src.api.db.topic_db.find_entity_by_id") as mock_find:
        # Test when topic is found through entity cache
        topic_path = Path("/mock/vault/project-slug/topic-slug")
        mock_find.return_value = (topic_path, "topic")

        # Call function
        project_slug, topic_slug = get_topic_location("test-topic-123")

        # Check result
        assert project_slug == "project-slug"
        assert topic_slug == "topic-slug"


def test_save_topic(mock_topic):
    """Test saving a topic to file."""
    # Create a mock project object
    mock_project = MagicMock()
    mock_project.id = "test-project-id"
    mock_project.topic_ids = ["test-topic-123"]

    with patch("src.api.db.project_db.list_projects", return_value=[mock_project]):
        with patch("src.api.db.project_db.get_project", return_value=mock_project):
            with patch("src.api.db.topic_db.create_slug") as mock_create_slug:
                with patch(
                    "src.api.db.topic_db.get_hierarchical_path"
                ) as mock_get_path:
                    with patch("src.api.db.topic_db.ensure_path_exists"):
                        with patch("builtins.open", mock_open()) as mock_file:
                            with patch("src.api.db.topic_db.add_to_entity_cache"):
                                # Setup mocks
                                mock_create_slug.side_effect = [
                                    "project-slug",
                                    "topic-slug",
                                ]
                                mock_path = Path("/mock/vault/project-slug/topic-slug")
                                mock_get_path.return_value = mock_path

                                # Call function
                                save_topic(mock_topic)

                                # Check result
                                path_arg = mock_file.call_args[0][0]
                                assert str(path_arg).endswith("metadata.yaml")
                                assert str(path_arg).startswith(str(mock_path))


def test_get_topic(mock_topic):
    """Test retrieving a topic by ID."""
    # Test using cache
    with patch("src.api.db.topic_db._topic_cache", {"test-topic-123": mock_topic}):
        with patch("src.api.db.topic_db._cache_initialized", True):
            result = get_topic("test-topic-123")
            assert result == mock_topic

    # Test loading from disk with entity cache
    with patch("src.api.db.topic_db._topic_cache", {}):
        with patch("src.api.db.topic_db._cache_initialized", True):
            with patch("src.api.db.topic_db.find_entity_by_id") as mock_find:
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("builtins.open", mock_open()):
                        with patch("yaml.safe_load") as mock_yaml_load:
                            # Setup mocks
                            topic_path = Path("/mock/vault/project-slug/topic-slug")
                            mock_find.return_value = (topic_path, "topic")

                            # Mock topic data
                            topic_data = mock_topic.model_dump()
                            topic_data["created_at"] = topic_data[
                                "created_at"
                            ].isoformat()
                            topic_data["updated_at"] = topic_data[
                                "updated_at"
                            ].isoformat()
                            mock_yaml_load.return_value = topic_data

                            # Call function
                            result = get_topic("test-topic-123")

                            # Check result
                            assert result is not None
                            assert result.id == mock_topic.id
                            assert result.name == mock_topic.name


def test_get_topic_not_found():
    """Test retrieving a non-existent topic."""
    # Test with empty cache
    with patch("src.api.db.topic_db._topic_cache", {}):
        with patch("src.api.db.topic_db._cache_initialized", True):
            with patch(
                "src.api.db.topic_db.find_entity_by_id", return_value=(None, None)
            ):
                result = get_topic("non-existent-topic")
                assert result is None


def test_list_topics(mock_topics):
    """Test listing all topics."""
    with patch("src.api.db.topic_db._ensure_cache"):
        with patch(
            "src.api.db.topic_db._topic_cache",
            {
                "topic-1": mock_topics[0],
                "topic-2": mock_topics[1],
            },
        ):
            # Call function
            result = list_topics()

            # Check result
            assert len(result) == 2
            assert result[0].id in ["topic-1", "topic-2"]
            assert result[1].id in ["topic-1", "topic-2"]


def test_load_topics(mock_topics):
    """Test loading all topics into a dictionary."""
    with patch("src.api.db.topic_db._ensure_cache"):
        with patch(
            "src.api.db.topic_db._topic_cache",
            {
                "topic-1": mock_topics[0],
                "topic-2": mock_topics[1],
            },
        ):
            # Call function
            result = load_topics()

            # Check result
            assert len(result) == 2
            assert "topic-1" in result
            assert "topic-2" in result
            assert result["topic-1"] == mock_topics[0]
            assert result["topic-2"] == mock_topics[1]


@patch("uuid.uuid4", return_value="test-uuid")
@patch("src.api.db.topic_db.save_topic")
@patch("src.api.db.topic_db.datetime")
@patch("src.api.db.project_db.get_project")
@patch("src.api.db.project_db.add_topic_to_project")
@patch("src.api.db.topic_db.Topic")
def test_create_topic(
    mock_topic_class,
    mock_add_topic,
    mock_get_project,
    mock_datetime,
    mock_save,
    mock_uuid,
):
    """Test creating a new topic."""
    # Setup mock datetime
    mock_date = datetime(2023, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = mock_date

    # Setup mock project
    mock_project = MagicMock()
    mock_project.id = "project-123"
    mock_project.topic_ids = []
    mock_project.slug = "project-slug"
    mock_get_project.return_value = mock_project
    mock_add_topic.return_value = mock_project

    # Setup mock Topic
    mock_topic = MagicMock()
    mock_topic.id = "test-uuid"
    mock_topic.name = "New Topic"
    mock_topic.description = "A new test topic"
    mock_topic.slug = "new-topic-slug"
    mock_topic_class.return_value = mock_topic

    # Mock ensure_unique_slug to return a predictable value
    with patch("src.api.db.topic_db.ensure_unique_slug", return_value="new-topic-slug"):
        # Call function with the correct parameters
        result = create_topic(
            name="New Topic",
            description="A new test topic",
            project_id="project-123",
        )

        # Check result
        assert result.id == "test-uuid"
        assert result.name == "New Topic"
        assert result.description == "A new test topic"
        assert result.slug == "new-topic-slug"
        mock_save.assert_called_once_with(mock_topic)
        mock_add_topic.assert_called_once_with("project-123", "test-uuid")


@patch("src.api.db.topic_db.find_entity_by_id")
@patch("pathlib.Path.exists", return_value=True)
@patch("src.api.db.topic_db.shutil.rmtree")
@patch("src.api.db.topic_db.remove_from_entity_cache")
def test_mark_topic_deleted(mock_remove, mock_rmtree, mock_exists, mock_find):
    """Test marking a topic as deleted."""
    # Setup mocks
    topic_path = Path("/mock/vault/project-slug/topic-slug")
    mock_find.return_value = (topic_path, "topic")

    # Call function
    result = mark_topic_deleted("test-topic-123")

    # Check result
    assert result is True
    mock_rmtree.assert_called_once_with(topic_path)
    mock_remove.assert_called_once()


def test_update_topic(mock_topic):
    """Test updating a topic."""
    with patch("src.api.db.topic_db.get_topic", return_value=mock_topic):
        with patch("src.api.db.topic_db.get_topic_location") as mock_get_location:
            with patch("src.api.db.topic_db.save_topic") as mock_save:
                # Setup mock location
                mock_get_location.return_value = ("project-slug", "topic-slug")

                # Define update data
                update_data = {
                    "name": "Updated Topic",
                    "description": "Updated description",
                    "feed_urls": ["http://example.com/new-feed"],
                }

                # Call function
                result = update_topic("test-topic-123", update_data)

                # Check result
                assert result is not None
                assert result.id == mock_topic.id
                assert result.name == "Updated Topic"
                assert result.description == "Updated description"
                assert result.feed_urls == ["http://example.com/new-feed"]
                mock_save.assert_called_once()


def test_update_topic_not_found():
    """Test updating a non-existent topic."""
    with patch("src.api.db.topic_db.get_topic", return_value=None):
        result = update_topic("non-existent-topic", {"name": "New Name"})
        assert result is None


def test_load_feed_items():
    """Test loading feed items from data."""
    # Create test data
    items_data = [
        {
            "url": "http://example.com/item1",
            "summary": "First item summary",
            "accessed_at": "2023-01-01T12:00:00",
            "content_hash": "hash1",
        },
        {
            "url": "http://example.com/item2",
            "summary": "Second item summary",
            "accessed_at": "2023-01-02T12:00:00",
            "content_hash": "hash2",
        },
    ]

    # Call function
    result = load_feed_items(items_data)

    # Check result
    assert len(result) == 2
    assert result[0].url == "http://example.com/item1"
    assert result[0].content_hash == "hash1"
    assert result[1].url == "http://example.com/item2"
    assert result[1].content_hash == "hash2"
