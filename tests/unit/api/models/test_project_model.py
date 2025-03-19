"""
Unit tests for the Project model.
"""

from datetime import datetime

from api.models.project import (Project, ProjectBase, ProjectCreate,
                                ProjectUpdate)


def test_project_base_creation():
    """Test creating a ProjectBase instance."""
    project_base = ProjectBase(
        title="Test Project",
        description="This is a test project",
        topic_ids=["topic-123", "topic-456"],
    )

    assert project_base.title == "Test Project"
    assert project_base.description == "This is a test project"
    assert len(project_base.topic_ids) == 2
    assert project_base.topic_ids[0] == "topic-123"
    assert project_base.thumbnail_url is None


def test_project_create():
    """Test ProjectCreate model."""
    project_create = ProjectCreate(
        title="Test Project",
        description="This is a test project",
        topic_ids=["topic-123"],
        thumbnail_url="https://example.com/thumbnail.jpg",
    )

    assert project_create.title == "Test Project"
    assert project_create.description == "This is a test project"
    assert project_create.topic_ids == ["topic-123"]
    assert project_create.thumbnail_url == "https://example.com/thumbnail.jpg"


def test_project_update():
    """Test ProjectUpdate model."""
    project_update = ProjectUpdate(
        title="Updated Project", description=None, topic_ids=["topic-789"]
    )

    assert project_update.title == "Updated Project"
    assert project_update.description is None
    assert project_update.topic_ids == ["topic-789"]
    assert project_update.thumbnail_url is None


def test_project_creation():
    """Test creating a Project instance."""
    creation_time = datetime(2023, 1, 1)
    update_time = datetime(2023, 1, 2)

    project = Project(
        id="project-123",
        title="Test Project",
        description="This is a test project",
        topic_ids=["topic-123", "topic-456"],
        thumbnail_url="https://example.com/thumbnail.jpg",
        created_at=creation_time,
        updated_at=update_time,
    )

    assert project.id == "project-123"
    assert project.title == "Test Project"
    assert project.description == "This is a test project"
    assert len(project.topic_ids) == 2
    assert project.thumbnail_url == "https://example.com/thumbnail.jpg"
    assert project.created_at == creation_time
    assert project.updated_at == update_time


def test_project_default_values():
    """Test default values for Project model."""
    project = Project(
        id="project-123", title="Test Project", description="This is a test project"
    )

    assert project.topic_ids == []
    assert project.thumbnail_url is None
    assert isinstance(project.created_at, datetime)
    assert project.updated_at is None


def test_project_from_fixture(sample_project_data):
    """Test creating a Project from fixture data."""
    project = Project(**sample_project_data)

    assert project.id == sample_project_data["id"]
    assert project.title == sample_project_data["title"]
    assert project.description == sample_project_data["description"]
    assert project.topic_ids == sample_project_data["topic_ids"]
    assert project.thumbnail_url == sample_project_data["thumbnail_url"]
    assert project.created_at == sample_project_data["created_at"]
    assert project.updated_at == sample_project_data["updated_at"]
