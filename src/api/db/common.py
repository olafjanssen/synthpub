"""Common database utilities."""

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

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
    name = re.sub(r"[^a-z0-9]+", "-", name)
    # Remove leading/trailing hyphens
    name = name.strip("-")
    # Ensure we have a valid slug (no empty string)
    if not name:
        name = "untitled"
    return name


def ensure_unique_slug(
    name: str, entity_type: str, parent_path: Optional[Path] = None
) -> str:
    """
    Create a unique slug for the given name and entity type.

    Args:
        name: The name to create a slug from
        entity_type: Type of entity ('project', 'topic', or 'article')
        parent_path: For topics, the parent project path; None for projects

    Returns:
        A unique slug string
    """
    base_slug = create_slug(name)
    slug = base_slug
    counter = 1

    # For projects, we check at the vault level
    if entity_type == "project":
        base_path = get_hierarchical_path()
        while (base_path / slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
    # For topics, we check within the parent project
    elif entity_type == "topic" and parent_path:
        while (parent_path / slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
    # For articles, we don't need to check as they use timestamps

    return slug


def get_hierarchical_path(
    project_slug: Optional[str] = None,
    topic_slug: Optional[str] = None,
    article_timestamp: Optional[str] = None,
) -> Path:
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


def get_archive_path(
    project_slug: Optional[str] = None,
    topic_slug: Optional[str] = None,
    article_timestamp: Optional[str] = None,
) -> Path:
    """
    Build a hierarchical path for the archive storage.

    Args:
        project_slug: The slug for the project directory
        topic_slug: The slug for the topic directory
        article_timestamp: The timestamp folder for the article

    Returns:
        Path object with the appropriate hierarchy in the archive folder
    """
    base_path = get_db_path("archive")

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
    timestamp_prefix = (
        timestamp.strftime("%Y-%m-%d-%H%M%S")
        if timestamp
        else datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    )

    # Get article directory path
    article_path = get_hierarchical_path(project_slug, topic_slug, timestamp_prefix)
    ensure_path_exists(article_path)

    return article_path


# Cache for entity lookups
_entity_id_cache = {}  # Maps entity_id to (path, entity_type)
_cache_initialized = False


def _initialize_entity_cache():
    """
    Initialize the entity cache by scanning all metadata.yaml files once.
    This improves subsequent lookups significantly.
    """
    global _cache_initialized

    if _cache_initialized:
        return

    # Check both vault and archive paths
    paths_to_check = [
        get_hierarchical_path(),  # vault
        get_archive_path(),       # archive
    ]
    
    for base_path in paths_to_check:
        if not base_path.exists():
            continue
        
        # Use recursive glob to find all metadata.yaml files
        for metadata_file in base_path.glob("**/metadata.yaml"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "id" in data:
                        entity_id = data["id"]
                        parent_dir = metadata_file.parent

                        # Determine entity type based on directory structure
                        if parent_dir.parent.parent == base_path:
                            # Structure is: vault/project/topic/metadata.yaml
                            # Or: archive/project/topic/metadata.yaml
                            _entity_id_cache[entity_id] = (parent_dir, "topic")
                        elif parent_dir.parent == base_path:
                            # Structure is: vault/project/metadata.yaml
                            # Or: archive/project/metadata.yaml
                            _entity_id_cache[entity_id] = (parent_dir, "project")
                        else:
                            # Structure is: vault/project/topic/timestamp/metadata.yaml
                            # Or: archive/project/topic/timestamp/metadata.yaml
                            _entity_id_cache[entity_id] = (parent_dir, "article")
            except (yaml.YAMLError, IOError):
                # Skip files with errors
                continue

    _cache_initialized = True


def invalidate_entity_cache():
    """Clear the entity cache to force reloading on next request."""
    global _cache_initialized
    _entity_id_cache.clear()
    _cache_initialized = False


def add_to_entity_cache(entity_id: str, path: Path, entity_type: str):
    """
    Add an entity to the cache after creating or updating it.

    Args:
        entity_id: The unique ID of the entity
        path: Path to the entity's directory
        entity_type: Type of entity ('project', 'topic', or 'article')
    """
    _initialize_entity_cache()
    _entity_id_cache[entity_id] = (path, entity_type)


def remove_from_entity_cache(entity_id: str):
    """
    Remove an entity from the cache when it's deleted.

    Args:
        entity_id: The unique ID of the entity to remove
    """
    _initialize_entity_cache()
    if entity_id in _entity_id_cache:
        del _entity_id_cache[entity_id]


def find_entity_by_id(entity_id: str) -> Tuple[Optional[Path], Optional[str]]:
    """
    Find any entity (project, topic, article) by its ID using cache.

    Args:
        entity_id: The unique ID to search for

    Returns:
        Tuple of (path to entity directory, entity type)
        where entity type is one of 'project', 'topic', 'article'
    """
    # Initialize cache if not already done
    _initialize_entity_cache()

    # Check if entity is in cache
    if entity_id in _entity_id_cache:
        return _entity_id_cache[entity_id]

    # If not in cache, scan files again (could be a new entity)
    # Check both vault and archive paths
    paths_to_check = [
        get_hierarchical_path(),  # vault
        get_archive_path(),       # archive
    ]
    
    for base_path in paths_to_check:
        if not base_path.exists():
            continue
            
        for metadata_file in base_path.glob("**/metadata.yaml"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "id" in data and data["id"] == entity_id:
                        # Determine entity type based on directory structure
                        parent_dir = metadata_file.parent

                        if parent_dir.parent.parent == base_path:
                            # Structure is: vault/project/topic/metadata.yaml
                            # Or: archive/project/topic/metadata.yaml
                            _entity_id_cache[entity_id] = (parent_dir, "topic")
                            return parent_dir, "topic"
                        elif parent_dir.parent == base_path:
                            # Structure is: vault/project/metadata.yaml
                            # Or: archive/project/metadata.yaml
                            _entity_id_cache[entity_id] = (parent_dir, "project")
                            return parent_dir, "project"
                        else:
                            # Structure is: vault/project/topic/timestamp/metadata.yaml
                            # Or: archive/project/topic/timestamp/metadata.yaml
                            _entity_id_cache[entity_id] = (parent_dir, "article")
                            return parent_dir, "article"
            except (yaml.YAMLError, IOError):
                # Skip files with errors
                continue
                
    return None, None
