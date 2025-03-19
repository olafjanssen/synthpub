"""Unit tests for project database operations."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from api.db.project_db import (DB_PATH, add_topic_to_project, create_project,
                               ensure_db_exists, get_project, list_projects,
                               mark_project_deleted, remove_topic_from_project,
                               save_project, update_project)
from api.models.project import Project


@pytest.fixture
def mock_project():
    """Create a mock project for testing."""
    return Project(
        id="test-project-123",
        title="Test Project",
        description="This is a test project",
        topic_ids=["topic-1", "topic-2"],
        created_at=datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime(2023, 1, 2, 12, 0, 0),
        thumbnail_url="http://example.com/thumbnail.jpg",
    )


@pytest.fixture
def mock_projects():
    """Create a list of mock projects for testing."""
    return [
        Project(
            id="test-project-123",
            title="Test Project 1",
            description="This is test project 1",
            topic_ids=["topic-1", "topic-2"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 2, 12, 0, 0),
            thumbnail_url="http://example.com/thumbnail1.jpg",
        ),
        Project(
            id="test-project-456",
            title="Test Project 2",
            description="This is test project 2",
            topic_ids=["topic-3"],
            created_at=datetime(2023, 1, 3, 12, 0, 0),
            updated_at=datetime(2023, 1, 4, 12, 0, 0),
            thumbnail_url="http://example.com/thumbnail2.jpg",
        ),
    ]


def test_db_path():
    """Test getting the database path."""
    with patch("api.db.project_db.get_db_path", return_value=Path("/mock/db/projects")):
        assert DB_PATH() == Path("/mock/db/projects")


def test_ensure_db_exists():
    """Test that the DB directory is created if it doesn't exist."""
    with patch("api.db.project_db.DB_PATH", return_value=Path("/mock/db/projects")):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            ensure_db_exists()
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_save_project(mock_project):
    """Test saving a project to file."""
    with patch("api.db.project_db.ensure_db_exists"), patch(
        "api.db.project_db.DB_PATH", return_value=Path("/mock/db/projects")
    ), patch("builtins.open", mock_open()) as mock_file:
        save_project(mock_project)
        mock_file.assert_called_once_with(
            Path("/mock/db/projects/test-project-123.yaml"),
            "w",
            encoding="utf-8",
        )


def test_get_project(mock_project):
    """Test retrieving a project."""
    mock_project_data = mock_project.model_dump()
    mock_project_data["created_at"] = mock_project_data["created_at"].isoformat()
    mock_project_data["updated_at"] = mock_project_data["updated_at"].isoformat()
    yaml_content = yaml.dump(mock_project_data)

    with patch(
        "api.db.project_db.DB_PATH", return_value=Path("/mock/db/projects")
    ), patch("pathlib.Path.exists", return_value=True), patch(
        "builtins.open", mock_open(read_data=yaml_content)
    ):
        result = get_project("test-project-123")
        assert result.id == mock_project.id
        assert result.title == mock_project.title
        assert result.description == mock_project.description
        assert result.topic_ids == mock_project.topic_ids


def test_get_project_not_found():
    """Test retrieving a non-existent project."""
    with patch(
        "api.db.project_db.DB_PATH", return_value=Path("/mock/db/projects")
    ), patch("pathlib.Path.exists", return_value=False):
        assert get_project("non-existent-id") is None


def test_list_projects(mock_projects):
    """Test listing all projects."""
    with patch("api.db.project_db.ensure_db_exists"), patch(
        "api.db.project_db.DB_PATH", return_value=Path("/mock/db/projects")
    ), patch("pathlib.Path.glob") as mock_glob, patch(
        "builtins.open", mock_open()
    ), patch(
        "yaml.safe_load"
    ) as mock_yaml_load:

        # Setup mock files
        mock_glob.return_value = [
            Path("/mock/db/projects/test-project-123.yaml"),
            Path("/mock/db/projects/test-project-456.yaml"),
        ]

        # Setup mock yaml loading to return project data
        mock_yaml_load.side_effect = [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "topic_ids": p.topic_ids,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
                "thumbnail_url": p.thumbnail_url,
            }
            for p in mock_projects
        ]

        result = list_projects()
        assert len(result) == 2
        project_ids = {project.id for project in result}
        expected_ids = {project.id for project in mock_projects}
        assert project_ids == expected_ids


def test_create_project():
    """Test creating a new project."""
    with patch("api.db.project_db.uuid.uuid4", return_value="test-uuid"), patch(
        "api.db.project_db.save_project"
    ) as mock_save, patch("api.db.project_db.datetime") as mock_datetime:

        mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)

        result = create_project(
            title="New Project",
            description="This is a new project",
            topic_ids=["topic-1", "topic-2"],
            thumbnail_url="http://example.com/thumbnail.jpg",
        )

        assert result.id == "test-uuid"
        assert result.title == "New Project"
        assert result.description == "This is a new project"
        assert result.topic_ids == ["topic-1", "topic-2"]
        assert result.thumbnail_url == "http://example.com/thumbnail.jpg"
        mock_save.assert_called_once()


def test_update_project(mock_project):
    """Test updating a project."""
    with patch("api.db.project_db.get_project", return_value=mock_project), patch(
        "api.db.project_db.save_project"
    ) as mock_save:

        updated_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "thumbnail_url": "http://example.com/updated_thumbnail.jpg",
        }

        result = update_project(mock_project.id, updated_data)

        assert result.title == "Updated Title"
        assert result.description == "Updated description"
        assert result.thumbnail_url == "http://example.com/updated_thumbnail.jpg"
        assert result.topic_ids == mock_project.topic_ids
        assert result.id == mock_project.id
        mock_save.assert_called_once()


def test_update_project_not_found():
    """Test updating a non-existent project."""
    with patch("api.db.project_db.get_project", return_value=None):
        assert update_project("non-existent-id", {"title": "Updated Title"}) is None


def test_mark_project_deleted(mock_project):
    """Test marking a project as deleted."""
    with patch("api.db.project_db.get_project", return_value=mock_project), patch(
        "api.db.project_db.DB_PATH", return_value=Path("/mock/db/projects")
    ), patch("pathlib.Path.exists", return_value=True), patch(
        "os.path.isdir", return_value=False
    ), patch(
        "os.rename"
    ) as mock_rename:

        assert mark_project_deleted(mock_project.id) is True
        mock_rename.assert_called_once()


def test_mark_project_deleted_not_found():
    """Test marking a non-existent project as deleted."""
    with patch("api.db.project_db.get_project", return_value=None):
        assert mark_project_deleted("non-existent-id") is False


def test_add_topic_to_project(mock_project):
    """Test adding a topic to a project."""
    # Create a project without "new-topic" in its topic_ids
    mock_project.topic_ids = ["topic-1", "topic-2"]
    original_length = len(mock_project.topic_ids)

    with patch("api.db.project_db.get_project", return_value=mock_project), patch(
        "api.db.topic_db.get_topic", return_value=True
    ), patch("api.db.project_db.save_project") as mock_save:

        result = add_topic_to_project(mock_project.id, "new-topic")

        assert "new-topic" in result.topic_ids
        assert len(result.topic_ids) == original_length + 1
        mock_save.assert_called_once()


def test_add_topic_to_project_already_exists(mock_project):
    """Test adding a topic that's already in the project."""
    with patch("api.db.project_db.get_project", return_value=mock_project), patch(
        "api.db.topic_db.get_topic", return_value=True
    ), patch("api.db.project_db.save_project") as mock_save:

        result = add_topic_to_project(mock_project.id, "topic-1")

        assert result.topic_ids == mock_project.topic_ids
        mock_save.assert_not_called()


def test_add_topic_to_project_not_found():
    """Test adding a topic to a non-existent project."""
    with patch("api.db.project_db.get_project", return_value=None):
        assert add_topic_to_project("non-existent-id", "topic-1") is None


def test_remove_topic_from_project(mock_project):
    """Test removing a topic from a project."""
    mock_project.topic_ids = ["topic-1", "topic-2"]
    original_length = len(mock_project.topic_ids)

    with patch("api.db.project_db.get_project", return_value=mock_project), patch(
        "api.db.project_db.save_project"
    ) as mock_save:

        result = remove_topic_from_project(mock_project.id, "topic-1")

        assert "topic-1" not in result.topic_ids
        assert len(result.topic_ids) == original_length - 1
        mock_save.assert_called_once()


def test_remove_topic_from_project_not_in_project(mock_project):
    """Test removing a topic that's not in the project."""
    with patch("api.db.project_db.get_project", return_value=mock_project), patch(
        "api.db.project_db.save_project"
    ) as mock_save:

        result = remove_topic_from_project(mock_project.id, "non-existent-topic")

        assert result.topic_ids == mock_project.topic_ids
        mock_save.assert_not_called()


def test_remove_topic_from_project_not_found():
    """Test removing a topic from a non-existent project."""
    with patch("api.db.project_db.get_project", return_value=None):
        assert remove_topic_from_project("non-existent-id", "topic-1") is None
