"""Common database utilities."""

import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, Tuple, Union

import yaml

from ..routes.settings import load_settings


def get_base_db_path() -> Path:
    """Get the base database path from settings or fallback to default."""
    settings = load_settings()
    return Path(settings.get("db_path") or os.getenv("DB_PATH", "../db"))


def get_db_path(subfolder: str) -> Path:
    """Get database path for a specific subfolder."""
    return get_base_db_path() / subfolder


def create_slug(name: str) -> str:
    """Create a URL-friendly slug from a name."""
    # Convert to lowercase
    name = name.lower()
    # Replace spaces and special chars with hyphens
    name = re.sub(r'[^a-z0-9]+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Ensure we have a valid slug (no empty string)
    if not name:
        name = "untitled"
    return name


def get_hierarchical_path(project_slug: Optional[str] = None, 
                          topic_slug: Optional[str] = None,
                          article_timestamp: Optional[str] = None) -> Path:
    """
    Build a hierarchical path for the vault storage.
    
    Args:
        project_slug: The slug for the project directory
        topic_slug: The slug for the topic directory
        article_timestamp: The timestamp folder for the article
        
    Returns:
        Path object with the appropriate hierarchy
    """
    base_path = get_db_path("vault")
    
    if project_slug:
        base_path = base_path / project_slug
        if topic_slug:
            base_path = base_path / topic_slug
            if article_timestamp:
                base_path = base_path / article_timestamp
            
    return base_path


def ensure_path_exists(path: Path) -> None:
    """Create the directory path if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def get_article_path(project_slug: str, topic_slug: str, timestamp: datetime) -> Path:
    """
    Generate a canonical article path with consistent timestamp format.
    
    Args:
        project_slug: The slug for the project
        topic_slug: The slug for the topic
        timestamp: The timestamp to use (typically article.updated_at or article.created_at)
    
    Returns:
        Path to the article directory
    """
    # Format timestamp as YYYY-MM-DD-HHMMSS
    timestamp_prefix = timestamp.strftime("%Y-%m-%d-%H%M%S") if timestamp else datetime.now(UTC).strftime("%Y-%m-%d-%H%M%S")
    
    # Get article directory path
    article_path = get_hierarchical_path(project_slug, topic_slug, timestamp_prefix)
    ensure_path_exists(article_path)
    
    return article_path


def find_entity_by_id(entity_id: str) -> Tuple[Optional[Path], Optional[str]]:
    """
    Find any entity (project, topic, article) by its ID.
    
    Args:
        entity_id: The unique ID to search for
    
    Returns:
        Tuple of (path to entity directory, entity type)
        where entity type is one of 'project', 'topic', 'article'
    """
    # Search through all metadata.yaml files in the vault
    vault_path = get_hierarchical_path()
    
    # Use recursive glob to find all metadata.yaml files
    for metadata_file in vault_path.glob("**/metadata.yaml"):
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "id" in data and data["id"] == entity_id:
                    # Determine entity type based on directory structure
                    parent_dir = metadata_file.parent
                    
                    if parent_dir.parent.parent == vault_path:
                        # Structure is: vault/project/topic/metadata.yaml
                        return parent_dir, "topic"
                    elif parent_dir.parent == vault_path:
                        # Structure is: vault/project/metadata.yaml
                        return parent_dir, "project"
                    else:
                        # Structure is: vault/project/topic/timestamp/metadata.yaml
                        return parent_dir, "article"
        except (yaml.YAMLError, IOError):
            # Skip files with errors
            continue
    
    return None, None
