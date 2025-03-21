"""
Database operations for projects using hierarchical folder structure.
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path
from shutil import rmtree
from typing import Dict, List, Optional

import yaml

from ..models.project import Project
from .common import (add_to_entity_cache, create_slug, ensure_path_exists,
                     find_entity_by_id, get_hierarchical_path,
                     remove_from_entity_cache)


def save_project(project: Project) -> None:
    """Save project to YAML file in its slug-named folder."""
    # Create slug from title
    project_slug = create_slug(project.title)
    
    # Build path
    project_path = get_hierarchical_path(project_slug)
    ensure_path_exists(project_path)
    
    # Create metadata file
    filename = project_path / "metadata.yaml"
    
    # Convert to dict and save
    project_dict = project.model_dump()
    
    # Convert datetime objects to ISO format
    project_dict["created_at"] = project_dict["created_at"].isoformat()
    if project_dict["updated_at"]:
        project_dict["updated_at"] = project_dict["updated_at"].isoformat()
    
    # Add the slug to metadata
    project_dict["slug"] = project_slug
    
    with open(filename, "w", encoding="utf-8") as f:
        yaml.safe_dump(project_dict, f, sort_keys=False, allow_unicode=True)
        f.flush()  # Ensure data is written to disk
    
    # Update the cache
    add_to_entity_cache(project.id, project_path, "project")


def get_project(project_id: str) -> Optional[Project]:
    """Retrieve project by id using the entity cache."""
    project_path, entity_type = find_entity_by_id(project_id)
    
    if not project_path or entity_type != "project":
        return None
    
    metadata_file = project_path / "metadata.yaml"
    if not metadata_file.exists():
        return None
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        # Convert ISO format strings back to datetime
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data["updated_at"]:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        return Project(**data)


def get_project_by_slug(slug: str) -> Optional[Project]:
    """Retrieve project by slug."""
    path = get_hierarchical_path(slug)
    filename = path / "metadata.yaml"
    
    if not filename.exists():
        return None
    
    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        # Convert ISO format strings back to datetime
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data["updated_at"]:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        return Project(**data)


def _get_project_directories() -> List[Path]:
    """Get all project directories."""
    vault_path = get_hierarchical_path()
    ensure_path_exists(vault_path)
    
    # Get all directories in the vault directory
    return [d for d in vault_path.iterdir() if d.is_dir()]


def list_projects() -> List[Project]:
    """List all projects by reading from hierarchical structure."""
    projects = []
    
    for project_dir in _get_project_directories():
        metadata_file = project_dir / "metadata.yaml"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
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
    """Update a project with new data."""
    project = get_project(project_id)
    if not project:
        return None
    
    # Get the current slug before updates
    old_slug = create_slug(project.title)
    
    # Update project fields
    for key, value in updated_data.items():
        if hasattr(project, key):
            setattr(project, key, value)
    
    # Update the timestamp
    project.updated_at = datetime.now(UTC)
    
    # Check if the slug changed due to title update
    new_slug = create_slug(project.title)
    if old_slug != new_slug:
        # If the slug changed, we need to move the directory
        old_path = get_hierarchical_path(old_slug)
        
        # Remove from cache with old path
        remove_from_entity_cache(project_id)
        
        # Save to new location (which will update cache)
        save_project(project)
        
        # Remove old directory if it exists
        if old_path.exists():
            rmtree(old_path)
            
        return project
    
    # If no slug change, just save
    save_project(project)
    return project


def mark_project_deleted(project_id: str) -> bool:
    """Mark a project as deleted by removing its directory."""
    project_path, entity_type = find_entity_by_id(project_id)
    
    if not project_path or entity_type != "project":
        return False
    
    if not project_path.exists():
        return False
    
    # Remove the directory and all contents
    rmtree(project_path)
    
    # Remove from cache
    remove_from_entity_cache(project_id)
    
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


def get_project_slug_map() -> Dict[str, str]:
    """Return a mapping of project IDs to their slugs."""
    projects = list_projects()
    return {project.id: create_slug(project.title) for project in projects} 