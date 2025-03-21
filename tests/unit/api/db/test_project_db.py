"""Unit tests for the project database module."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from src.api.db.project_db import (_get_project_directories,
                                   add_topic_to_project, create_project,
                                   get_project, get_project_by_slug,
                                   list_projects, mark_project_deleted,
                                   remove_topic_from_project, save_project,
                                   update_project)
from src.api.models.project import Project


@pytest.fixture
def mock_project():
    """Create a mock project for testing."""
    return Project(
        id="test-project-123",
        title="Test Project",
        description="A test project",
        topic_ids=["topic-1", "topic-2"],
        created_at=datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime(2023, 1, 2, 12, 0, 0),
    )


@pytest.fixture
def mock_projects():
    """Create a list of mock projects for testing."""
    return [
        Project(
            id="project-1",
            title="Project One",
            description="The first project",
            topic_ids=["topic-1", "topic-2"],
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 2, 12, 0, 0),
        ),
        Project(
            id="project-2",
            title="Project Two",
            description="The second project",
            topic_ids=["topic-3"],
            created_at=datetime(2023, 1, 3, 12, 0, 0),
            updated_at=datetime(2023, 1, 4, 12, 0, 0),
        ),
    ]


def test_get_project_directories():
    """Test getting all project directories."""
    with patch("src.api.db.project_db.get_hierarchical_path") as mock_get_path:
        with patch("src.api.db.project_db.ensure_path_exists"):
            with patch("pathlib.Path.iterdir") as mock_iterdir:
                # Setup mocks
                vault_path = Path("/mock/vault")
                mock_get_path.return_value = vault_path
                
                dir1 = MagicMock(spec=Path)
                dir1.is_dir.return_value = True
                dir2 = MagicMock(spec=Path)
                dir2.is_dir.return_value = True
                file1 = MagicMock(spec=Path)
                file1.is_dir.return_value = False
                
                mock_iterdir.return_value = [dir1, file1, dir2]
                
                # Call function
                result = _get_project_directories()
                
                # Check result
                assert len(result) == 2
                assert dir1 in result
                assert dir2 in result
                assert file1 not in result


def test_save_project(mock_project):
    """Test saving a project to file."""
    with patch("src.api.db.project_db.get_hierarchical_path") as mock_get_path:
        with patch("src.api.db.project_db.ensure_path_exists"):
            with patch("builtins.open", mock_open()) as mock_file:
                with patch("src.api.db.project_db.add_to_entity_cache"):
                    with patch("src.api.db.project_db.create_slug", return_value="test-project"):
                        # Setup mock path
                        mock_path = Path("/mock/vault/test-project")
                        mock_get_path.return_value = mock_path
                        
                        # Call function
                        save_project(mock_project)
                        
                        # Check result
                        path_arg = mock_file.call_args[0][0]
                        assert str(path_arg).endswith("metadata.yaml")
                        assert str(path_arg).startswith(str(mock_path))


def test_get_project(mock_project):
    """Test retrieving a project by ID."""
    with patch("src.api.db.project_db.find_entity_by_id") as mock_find:
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load") as mock_yaml_load:
                    # Setup mocks
                    project_path = Path("/mock/vault/test-project")
                    mock_find.return_value = (project_path, "project")
                    
                    # Mock project data
                    project_data = mock_project.model_dump()
                    project_data["created_at"] = project_data["created_at"].isoformat()
                    project_data["updated_at"] = project_data["updated_at"].isoformat()
                    mock_yaml_load.return_value = project_data
                    
                    # Call function
                    result = get_project("test-project-123")
                    
                    # Check result
                    assert result is not None
                    assert result.id == mock_project.id
                    assert result.title == mock_project.title
                    assert result.topic_ids == mock_project.topic_ids


def test_get_project_not_found():
    """Test retrieving a non-existent project."""
    with patch("src.api.db.project_db.find_entity_by_id", return_value=(None, None)):
        result = get_project("non-existent-project")
        assert result is None


def test_get_project_by_slug(mock_project):
    """Test retrieving a project by slug."""
    with patch("src.api.db.project_db.get_hierarchical_path") as mock_get_path:
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load") as mock_yaml_load:
                    # Setup mocks
                    project_path = Path("/mock/vault/test-project")
                    mock_get_path.return_value = project_path
                    
                    # Mock project data
                    project_data = mock_project.model_dump()
                    project_data["created_at"] = project_data["created_at"].isoformat()
                    project_data["updated_at"] = project_data["updated_at"].isoformat()
                    mock_yaml_load.return_value = project_data
                    
                    # Call function
                    result = get_project_by_slug("test-project")
                    
                    # Check result
                    assert result is not None
                    assert result.id == mock_project.id
                    assert result.title == mock_project.title


def test_list_projects(mock_projects):
    """Test listing all projects."""
    with patch("src.api.db.project_db._get_project_directories") as mock_get_dirs:
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open()):
                with patch("yaml.safe_load", side_effect=[
                    {
                        "id": "project-1",
                        "title": "Project One",
                        "description": "The first project",
                        "topic_ids": ["topic-1", "topic-2"],
                        "created_at": "2023-01-01T12:00:00",
                        "updated_at": "2023-01-02T12:00:00",
                    },
                    {
                        "id": "project-2",
                        "title": "Project Two",
                        "description": "The second project",
                        "topic_ids": ["topic-3"],
                        "created_at": "2023-01-03T12:00:00",
                        "updated_at": "2023-01-04T12:00:00",
                    },
                ]):
                    # Setup mocked project directories
                    project_dir1 = MagicMock(spec=Path)
                    project_dir1.__truediv__.return_value = Path("/mock/vault/project-1/metadata.yaml")
                    project_dir2 = MagicMock(spec=Path)
                    project_dir2.__truediv__.return_value = Path("/mock/vault/project-2/metadata.yaml")
                    
                    mock_get_dirs.return_value = [project_dir1, project_dir2]
                    
                    # Call function
                    result = list_projects()
                    
                    # Check result
                    assert len(result) == 2
                    assert result[0].id == "project-1"
                    assert result[1].id == "project-2"


def test_create_project():
    """Test creating a new project."""
    with patch("uuid.uuid4", return_value="test-uuid"):
        with patch("src.api.db.project_db.save_project") as mock_save:
            # Call function
            result = create_project(
                title="New Project",
                description="A new test project",
                topic_ids=["topic-1"],
                thumbnail_url="http://example.com/image.png",
            )
            
            # Check result
            assert result.id == "test-uuid"
            assert result.title == "New Project"
            assert result.description == "A new test project"
            assert result.topic_ids == ["topic-1"]
            assert result.thumbnail_url == "http://example.com/image.png"
            mock_save.assert_called_once()


def test_mark_project_deleted(mock_project):
    """Test marking a project as deleted."""
    with patch("src.api.db.project_db.find_entity_by_id") as mock_find:
        with patch("pathlib.Path.exists", return_value=True):
            with patch("src.api.db.project_db.rmtree") as mock_rmtree:
                with patch("src.api.db.project_db.remove_from_entity_cache") as mock_remove:
                    # Setup mock path
                    mock_path = MagicMock(spec=Path)
                    mock_path.exists.return_value = True
                    mock_find.return_value = (mock_path, "project")
                    
                    # Call function
                    result = mark_project_deleted("test-project-123")
                    
                    # Check result
                    assert result is True
                    mock_rmtree.assert_called_once_with(mock_path)
                    mock_remove.assert_called_once_with("test-project-123")


def test_mark_project_deleted_not_found():
    """Test marking a non-existent project as deleted."""
    with patch("src.api.db.project_db.find_entity_by_id", return_value=(None, None)):
        result = mark_project_deleted("non-existent-project")
        assert result is False


def test_update_project(mock_project):
    """Test updating a project."""
    with patch("src.api.db.project_db.get_project", return_value=mock_project):
        with patch("src.api.db.project_db.save_project") as mock_save:
            with patch("src.api.db.project_db.create_slug", return_value="test-project"):
                # Define update data
                update_data = {
                    "title": "Updated Project",
                    "description": "Updated description",
                    "topic_ids": ["topic-3"],
                    "thumbnail_url": "http://example.com/new-image.png",
                }
                
                # Call function
                result = update_project("test-project-123", update_data)
                
                # Check result
                assert result is not None
                assert result.id == mock_project.id
                assert result.title == "Updated Project"
                assert result.description == "Updated description"
                assert result.topic_ids == ["topic-3"]
                assert result.thumbnail_url == "http://example.com/new-image.png"
                mock_save.assert_called_once()


def test_update_project_with_slug_change(mock_project):
    """Test updating a project with a title change that affects the slug."""
    with patch("src.api.db.project_db.get_project", return_value=mock_project):
        with patch("src.api.db.project_db.save_project") as mock_save:
            with patch("src.api.db.project_db.create_slug") as mock_create_slug:
                with patch("src.api.db.project_db.get_hierarchical_path") as mock_get_path:
                    with patch("pathlib.Path.exists", return_value=True):
                        with patch("src.api.db.project_db.rmtree") as mock_rmtree:
                            with patch("src.api.db.project_db.remove_from_entity_cache") as mock_remove:
                                # Setup mocks for slug change
                                mock_create_slug.side_effect = ["old-slug", "new-slug"]
                                old_path = Path("/mock/vault/old-slug")
                                mock_get_path.return_value = old_path
                                
                                # Define update data
                                update_data = {
                                    "title": "New Title",
                                }
                                
                                # Call function
                                result = update_project("test-project-123", update_data)
                                
                                # Check result
                                assert result is not None
                                assert result.title == "New Title"
                                mock_remove.assert_called_once_with("test-project-123")
                                mock_save.assert_called_once_with(result)
                                mock_rmtree.assert_called_once_with(old_path)


def test_update_project_not_found():
    """Test updating a non-existent project."""
    with patch("src.api.db.project_db.get_project", return_value=None):
        result = update_project("non-existent-project", {"title": "New Title"})
        assert result is None


def test_add_topic_to_project(mock_project):
    """Test adding a topic to a project."""
    # Create a copy of mock_project without the new topic
    project_without_topic = Project(
        id=mock_project.id,
        title=mock_project.title,
        description=mock_project.description,
        topic_ids=["existing-topic"],
        created_at=mock_project.created_at,
        updated_at=mock_project.updated_at,
    )
    
    with patch("src.api.db.project_db.get_project", return_value=project_without_topic):
        with patch("src.api.db.project_db.save_project") as mock_save:
            # Call function with a new topic ID
            result = add_topic_to_project(mock_project.id, "new-topic")
            
            # Check result
            assert result is not None
            assert "existing-topic" in result.topic_ids
            assert "new-topic" in result.topic_ids
            mock_save.assert_called_once()


def test_add_topic_to_project_already_exists(mock_project):
    """Test adding a topic that already exists in the project."""
    with patch("src.api.db.project_db.get_project", return_value=mock_project):
        with patch("src.api.db.project_db.save_project") as mock_save:
            # Call function with an existing topic ID
            result = add_topic_to_project(mock_project.id, "topic-1")
            
            # Check result - topic should only appear once
            assert result is not None
            assert result.topic_ids.count("topic-1") == 1
            # Should not save since nothing changed
            mock_save.assert_not_called()


def test_add_topic_to_project_not_found():
    """Test adding a topic to a non-existent project."""
    with patch("src.api.db.project_db.get_project", return_value=None):
        result = add_topic_to_project("non-existent-project", "topic-1")
        assert result is None


def test_remove_topic_from_project(mock_project):
    """Test removing a topic from a project."""
    with patch("src.api.db.project_db.get_project", return_value=mock_project):
        with patch("src.api.db.project_db.save_project") as mock_save:
            # Call function with an existing topic ID
            result = remove_topic_from_project(mock_project.id, "topic-1")
            
            # Check result
            assert result is not None
            assert "topic-1" not in result.topic_ids
            assert "topic-2" in result.topic_ids
            mock_save.assert_called_once()


def test_remove_topic_from_project_not_in_project(mock_project):
    """Test removing a topic that is not in the project."""
    with patch("src.api.db.project_db.get_project", return_value=mock_project):
        with patch("src.api.db.project_db.save_project") as mock_save:
            # Call function with a non-existent topic ID
            result = remove_topic_from_project(mock_project.id, "non-existent-topic")
            
            # Check result - project should be unchanged
            assert result is not None
            assert "topic-1" in result.topic_ids
            assert "topic-2" in result.topic_ids
            # Should not save since nothing changed
            mock_save.assert_not_called()


def test_remove_topic_from_project_not_found():
    """Test removing a topic from a non-existent project."""
    with patch("src.api.db.project_db.get_project", return_value=None):
        result = remove_topic_from_project("non-existent-project", "topic-1")
        assert result is None
