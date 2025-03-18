"""
Integration tests for project endpoints.
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import app
from src.api.models.project import Project


@pytest.fixture
def mock_project_db():
    """Mock project database for testing."""
    test_projects = {
        "test-project-id": {
            "id": "test-project-id",
            "title": "Test Project",
            "description": "A test project for testing",
            "topic_ids": ["test-topic-id"],
            "thumbnail_url": "https://example.com/thumbnail.jpg",
            "created_at": datetime.now(),
            "updated_at": None
        }
    }
    
    def mock_get_project(project_id):
        """Mock get_project function."""
        if project_id in test_projects:
            return Project(**test_projects[project_id])
        return None
    
    def mock_list_projects():
        """Mock list_projects function."""
        return [Project(**project) for project in test_projects.values()]
    
    def mock_create_project(title, description, topic_ids=None, thumbnail_url=None):
        """Mock create_project function."""
        project_id = str(uuid.uuid4())
        project_data = {
            "id": project_id,
            "title": title,
            "description": description,
            "topic_ids": topic_ids or [],
            "thumbnail_url": thumbnail_url,
            "created_at": datetime.now(),
            "updated_at": None
        }
        test_projects[project_id] = project_data
        return Project(**project_data)
    
    def mock_update_project(project_id, update_data):
        """Mock update_project function."""
        if project_id not in test_projects:
            return None
        project = test_projects[project_id].copy()
        for key, value in update_data.items():
            project[key] = value
        project["updated_at"] = datetime.now()
        test_projects[project_id] = project
        return Project(**project)
    
    def mock_mark_project_deleted(project_id):
        """Mock mark_project_deleted function."""
        if project_id in test_projects:
            del test_projects[project_id]
            return True
        return False
    
    def mock_add_topic_to_project(project_id, topic_id):
        """Mock add_topic_to_project function."""
        if project_id not in test_projects:
            return None
        project = test_projects[project_id].copy()
        if "topic_ids" not in project:
            project["topic_ids"] = []
        if topic_id not in project["topic_ids"]:
            project["topic_ids"].append(topic_id)
        project["updated_at"] = datetime.now()
        test_projects[project_id] = project
        return Project(**project)
    
    def mock_remove_topic_from_project(project_id, topic_id):
        """Mock remove_topic_from_project function."""
        if project_id not in test_projects:
            return None
        project = test_projects[project_id].copy()
        if "topic_ids" in project and topic_id in project["topic_ids"]:
            project["topic_ids"].remove(topic_id)
        project["updated_at"] = datetime.now()
        test_projects[project_id] = project
        return Project(**project)
    
    # Return mock functions and test data
    return {
        "data": test_projects,
        "get_project": mock_get_project,
        "list_projects": mock_list_projects,
        "create_project": mock_create_project,
        "update_project": mock_update_project,
        "mark_project_deleted": mock_mark_project_deleted,
        "add_topic_to_project": mock_add_topic_to_project,
        "remove_topic_from_project": mock_remove_topic_from_project
    }


@pytest.fixture
def client(mock_project_db):
    """
    Create a test client with mocked project DB functions.
    
    This fixture creates a FastAPI TestClient with database functions patched.
    The critical part is patching the exact import paths used in the actual routes,
    not the absolute import paths from the project root.
    """
    # Create patches for all project_db functions with the exact import paths
    # used in the routes file
    with patch("api.db.project_db.get_project", mock_project_db["get_project"]), \
         patch("api.db.project_db.list_projects", mock_project_db["list_projects"]), \
         patch("api.db.project_db.create_project", mock_project_db["create_project"]), \
         patch("api.db.project_db.update_project", mock_project_db["update_project"]), \
         patch("api.db.project_db.mark_project_deleted", mock_project_db["mark_project_deleted"]), \
         patch("api.db.project_db.add_topic_to_project", mock_project_db["add_topic_to_project"]), \
         patch("api.db.project_db.remove_topic_from_project", mock_project_db["remove_topic_from_project"]), \
         patch("uuid.uuid4", return_value=uuid.UUID("12345678-1234-5678-1234-567812345678")):
        
        # Create test client
        with TestClient(app) as test_client:
            yield test_client


def test_list_projects(client, mock_project_db):
    """Test that the projects endpoint returns a list of projects."""
    response = client.get("/api/projects/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_project(client, mock_project_db):
    """Test getting a specific project by ID."""
    # Additional patch at the route level to ensure the mocking works correctly
    with patch("api.routes.project_routes.get_project", 
              return_value=Project(
                  id="test-project-id",
                  title="Test Project",
                  description="A test project for testing",
                  topic_ids=["test-topic-id"],
                  thumbnail_url="https://example.com/thumbnail.jpg",
                  created_at=datetime.now(),
                  updated_at=None
              )):
        response = client.get("/api/projects/test-project-id")
        assert response.status_code == 200
        assert response.json()["id"] == "test-project-id"
        assert response.json()["title"] == "Test Project"


def test_get_nonexistent_project(client, mock_project_db):
    """Test requesting a non-existent project."""
    response = client.get("/api/projects/nonexistent-project-id")
    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


def test_create_project(client, mock_project_db):
    """Test creating a new project."""
    response = client.post(
        "/api/projects/",
        json={
            "title": "New Project",
            "description": "A new test project",
            "topic_ids": ["test-topic-id"]
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Project"
    assert response.json()["id"] == "12345678-1234-5678-1234-567812345678"


def test_update_project(client, mock_project_db):
    """Test updating a project's details."""
    response = client.put(
        "/api/projects/test-project-id",
        json={
            "title": "Updated Project",
            "description": "An updated test project"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Project"
    assert response.json()["description"] == "An updated test project"


def test_delete_project(client, mock_project_db):
    """Test deleting a project."""
    response = client.delete("/api/projects/test-project-id")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]
    
    # Verify project is gone
    response = client.get("/api/projects/test-project-id")
    assert response.status_code == 404


def test_add_topic_to_project(client, mock_project_db):
    """Test adding a topic to a project."""
    response = client.post("/api/projects/test-project-id/topics/new-topic-id")
    assert response.status_code == 200
    assert "new-topic-id" in response.json()["topic_ids"]


def test_remove_topic_from_project(client, mock_project_db):
    """Test removing a topic from a project."""
    response = client.delete("/api/projects/test-project-id/topics/test-topic-id")
    assert response.status_code == 200
    assert "test-topic-id" not in response.json()["topic_ids"] 