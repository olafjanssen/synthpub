"""
Database operations for projects using individual YAML files.
"""

import uuid
from datetime import UTC, datetime
from shutil import move
from typing import List, Optional

import yaml

from api.models.project import Project

from . import topic_db
from .common import get_db_path


def DB_PATH():
    return get_db_path("projects")


def ensure_db_exists():
    """Create the projects directory if it doesn't exist."""
    DB_PATH().mkdir(parents=True, exist_ok=True)


def save_project(project: Project) -> None:
    """Save project to individual YAML file."""
    ensure_db_exists()

    # Generate filename from id
    filename = DB_PATH() / f"{project.id}.yaml"

    # Convert to dict and save
    project_dict = project.model_dump()

    # Convert datetime objects to ISO format
    project_dict["created_at"] = project_dict["created_at"].isoformat()
    if project_dict["updated_at"]:
        project_dict["updated_at"] = project_dict["updated_at"].isoformat()

    with open(filename, "w", encoding="utf-8") as f:
        yaml.safe_dump(project_dict, f, sort_keys=False, allow_unicode=True)


def get_project(project_id: str) -> Optional[Project]:
    """Retrieve project by id."""
    print(f"GET PROJECT FROM DBCALLED: {project_id}")
    filename = DB_PATH() / f"{project_id}.yaml"

    if not filename.exists():
        return None

    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        # Convert ISO format strings back to datetime
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data["updated_at"]:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return Project(**data)


def list_projects() -> List[Project]:
    """List all active (non-deleted) projects."""
    ensure_db_exists()
    print("LISTING PROJECTS SHOULD NOT BE CALLED IN TESTS")
    projects = []
    # Correctly exclude files that start with '_'
    for file in DB_PATH().glob("*.yaml"):
        if not file.name.startswith("_"):
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                # Convert ISO format strings back to datetime
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                if data["updated_at"]:
                    data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                projects.append(Project(**data))

    return projects


def create_project(
    title: str,
    description: str,
    topic_ids: Optional[List[str]] = None,
    thumbnail_url: Optional[str] = None,
) -> Project:
    """Create a new project."""
    project_id = str(uuid.uuid4())
    project = Project(
        id=project_id,
        title=title,
        description=description,
        topic_ids=topic_ids or [],
        thumbnail_url=thumbnail_url,
        created_at=datetime.now(UTC),
    )
    save_project(project)
    return project


def update_project(project_id: str, updated_data: dict) -> Optional[Project]:
    """
    Update a project with new data.
    Returns updated Project if successful, None if project not found.
    """
    project = get_project(project_id)
    if not project:
        return None

    # Update project fields
    for key, value in updated_data.items():
        if hasattr(project, key):
            setattr(project, key, value)

    # Filter out any topic IDs that no longer exist
    if hasattr(project, "topic_ids") and project.topic_ids:
        valid_topic_ids = []
        for topic_id in project.topic_ids:
            if topic_db.get_topic(topic_id) is not None:
                valid_topic_ids.append(topic_id)
        project.topic_ids = valid_topic_ids

    # Update the timestamp
    project.updated_at = datetime.now(UTC)

    save_project(project)
    return project


def mark_project_deleted(project_id: str) -> bool:
    """
    Mark a project as deleted by prefixing its filename with '_'.
    Returns True if successful, False if project not found.
    """
    filename = DB_PATH() / f"{project_id}.yaml"
    if not filename.exists():
        return False

    # New filename with '_' prefix
    new_filename = DB_PATH() / f"_{project_id}.yaml"

    # Move/rename the file
    move(filename, new_filename)
    return True


def add_topic_to_project(project_id: str, topic_id: str) -> Optional[Project]:
    """Add a topic to a project's topic list if the topic exists."""
    project = get_project(project_id)
    if not project:
        return None

    if topic_id not in project.topic_ids:
        project.topic_ids.append(topic_id)
        project.updated_at = datetime.now(UTC)
        save_project(project)

    return project


def remove_topic_from_project(project_id: str, topic_id: str) -> Optional[Project]:
    """Remove a topic from a project's topic list."""
    project = get_project(project_id)
    if not project:
        return None

    if topic_id in project.topic_ids:
        project.topic_ids.remove(topic_id)
        project.updated_at = datetime.now(UTC)
        save_project(project)

    return project
