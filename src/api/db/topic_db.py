"""
Database operations for topics using hierarchical folder structure.
"""

import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, cast

import yaml

from ..models.project import Project
from ..models.topic import FeedItem, Topic
from . import article_db, project_db
from .common import (add_to_entity_cache, create_slug, ensure_path_exists,
                     ensure_unique_slug, find_entity_by_id,
                     get_hierarchical_path, remove_from_entity_cache)

# In-memory cache for topics
_topic_cache: Dict[str, Topic] = {}
_cache_initialized = False


def _ensure_cache():
    """Initialize cache if not already done."""
    global _cache_initialized
    if not _cache_initialized:
        topics = _load_all_topics_from_disk()
        _topic_cache.update({topic.id: topic for topic in topics})
        _cache_initialized = True


def _load_all_topics_from_disk() -> List[Topic]:
    """Internal function to load topics directly from disk."""
    topics = []

    # For each project directory
    for project_dir in project_db._get_project_directories():
        # Get subdirectories which are topics
        for topic_dir in [d for d in project_dir.iterdir() if d.is_dir()]:
            metadata_file = topic_dir / "metadata.yaml"
            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    topic_data = yaml.safe_load(f)

                    # Process feed items if present
                    if "processed_feeds" in topic_data:
                        processed_feeds = []
                        for feed_item in topic_data["processed_feeds"]:
                            if "accessed_at" in feed_item and isinstance(
                                feed_item["accessed_at"], str
                            ):
                                feed_item["accessed_at"] = datetime.fromisoformat(
                                    feed_item["accessed_at"]
                                )
                            processed_feeds.append(FeedItem(**feed_item))
                        topic_data["processed_feeds"] = processed_feeds

                    # Set slug from directory name if not already set
                    if not topic_data.get("slug"):
                        topic_data["slug"] = topic_dir.name
                        
                    topics.append(Topic(**topic_data))

    return topics


def get_topic_path(project_slug: str, topic_slug: str) -> Path:
    """Get path to a topic's directory within a project."""
    return get_hierarchical_path(project_slug, topic_slug)


def get_topic_location(topic_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Find where a topic is stored in the hierarchical structure.

    Returns:
        Tuple of (project_slug, topic_slug) or (None, None) if not found
    """
    # First check if we can find it directly using the entity cache
    topic_path, entity_type = find_entity_by_id(topic_id)

    if topic_path is not None and entity_type == "topic":
        # Extract slugs from path
        # Structure is: vault/project_slug/topic_slug
        topic_slug = topic_path.name
        project_slug = topic_path.parent.name
        # Ensure we're returning strings, not Path objects
        return str(project_slug), str(topic_slug)

    # Fallback to checking projects
    project_slug_map = project_db.get_project_slug_map()

    # For each project
    for project in project_db.list_projects():
        if topic_id in project.topic_ids:
            # Topic belongs to this project
            project_slug = project_slug_map.get(project.id, "")
            if project_slug:  # Check if we got a valid slug
                # Find the topic within this project
                topic = get_topic(topic_id)
                if topic:
                    # Create a topic slug (either use existing or generate new one)
                    if topic.slug:
                        return project_slug, topic.slug
                    else:
                        return project_slug, create_slug(topic.name)

    return None, None


def save_topic(topic: Topic) -> None:
    """Save topic to YAML file in its project and slug-named folder."""
    # Find the project this topic belongs to
    project_id = None
    for project in project_db.list_projects():
        if topic.id in project.topic_ids:
            project_id = project.id
            break

    if not project_id:
        raise ValueError(
            f"Cannot save topic {topic.id}: not associated with any project"
        )

    # Get project slug
    project_result = project_db.get_project(project_id)
    if project_result is None:
        raise ValueError(f"Cannot find project {project_id}")

    # At this point we know project is not None
    project = project_result  # Now project has the type Project, not Optional[Project]

    # Create safe project slug - always use a string
    safe_project_slug: str = project.slug if project.slug else create_slug(project.title)
    
    # Use existing topic slug if available, otherwise create a new one
    if topic.slug:
        topic_slug = topic.slug
    else:
        # Get the project path for passing to ensure_unique_slug
        project_path = get_hierarchical_path(safe_project_slug)
        # Create unique topic slug
        topic_slug = ensure_unique_slug(topic.name, "topic", project_path)
        topic.slug = topic_slug

    # Build path
    topic_path = get_hierarchical_path(safe_project_slug, topic_slug)
    ensure_path_exists(topic_path)

    # Create metadata file
    filename = topic_path / "metadata.yaml"

    # Convert to dict and save
    topic_dict = topic.model_dump()

    # Process feed items if present
    if "processed_feeds" in topic_dict:
        for item in topic_dict["processed_feeds"]:
            if "needs_further_processing" in item:
                del item["needs_further_processing"]
            if "accessed_at" in item and not isinstance(item["accessed_at"], str):
                item["accessed_at"] = item["accessed_at"].isoformat()

    with open(filename, "w", encoding="utf-8") as f:
        yaml.safe_dump(topic_dict, f, sort_keys=False, allow_unicode=True)
        f.flush()  # Ensure data is written to disk

    # Update cache
    _topic_cache[topic.id] = topic
    add_to_entity_cache(topic.id, topic_path, "topic")


def get_topic(topic_id: str) -> Optional[Topic]:
    """Retrieve topic by id from cache or disk."""
    _ensure_cache()

    # First check in-memory cache
    if topic_id in _topic_cache:
        return _topic_cache[topic_id]

    # If not in memory cache, try to find using entity cache
    topic_path, entity_type = find_entity_by_id(topic_id)

    if topic_path and entity_type == "topic":
        metadata_file = topic_path / "metadata.yaml"

        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

                # Process feed items if present
                if "processed_feeds" in data:
                    processed_feeds = []
                    for feed_item in data["processed_feeds"]:
                        if "accessed_at" in feed_item and isinstance(
                            feed_item["accessed_at"], str
                        ):
                            feed_item["accessed_at"] = datetime.fromisoformat(
                                feed_item["accessed_at"]
                            )
                        processed_feeds.append(FeedItem(**feed_item))
                    data["processed_feeds"] = processed_feeds

                # Set slug from directory name if not already set
                if not data.get("slug"):
                    data["slug"] = topic_path.name
                    
                topic = Topic(**data)
                _topic_cache[topic_id] = topic
                return topic

    return None


def get_topic_by_slug(project_slug: str, topic_slug: str) -> Optional[Topic]:
    """Retrieve topic by project slug and topic slug."""
    path = get_hierarchical_path(project_slug, topic_slug)
    filename = path / "metadata.yaml"

    if not filename.exists():
        return None

    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

        # Process feed items if present
        if "processed_feeds" in data:
            processed_feeds = []
            for feed_item in data["processed_feeds"]:
                if "accessed_at" in feed_item and isinstance(
                    feed_item["accessed_at"], str
                ):
                    feed_item["accessed_at"] = datetime.fromisoformat(
                        feed_item["accessed_at"]
                    )
                processed_feeds.append(FeedItem(**feed_item))
            data["processed_feeds"] = processed_feeds

        # Set slug from path if not already set
        if not data.get("slug"):
            data["slug"] = topic_slug
            
        topic = Topic(**data)
        _topic_cache[topic.id] = topic
        return topic


def list_topics() -> List[Topic]:
    """List all active topics from cache."""
    _ensure_cache()
    return list(_topic_cache.values())


def load_topics() -> Dict[str, Topic]:
    """Load all topics into a dictionary from cache."""
    _ensure_cache()
    return dict(_topic_cache)


def create_topic(name: str, description: str, project_id: str) -> Topic:
    """Create a new topic and add to cache."""
    topic_id = str(uuid.uuid4())
    
    # Get project to determine where topic should be stored
    project = project_db.get_project(project_id)
    if not project:
        raise ValueError(f"Project with ID {project_id} not found")
    
    # Create safe project slug - ensure it's a string
    project_slug: str = project.slug if project.slug else create_slug(project.title)
    
    # Get project path for generating unique topic slug
    project_path = get_hierarchical_path(project_slug)
    topic_slug = ensure_unique_slug(name, "topic", project_path)
    
    topic = Topic(id=topic_id, name=name, description=description, slug=topic_slug)

    # Add this topic to the project
    project = project_db.add_topic_to_project(project_id, topic_id)
    if not project:
        raise ValueError(f"Cannot add topic to project {project_id}: project not found")

    save_topic(topic)
    return topic


def mark_topic_deleted(topic_id: str) -> bool:
    """Mark a topic as deleted and remove its directory."""
    # Get the topic to find its article ID before deleting
    topic = get_topic(topic_id)
    if not topic:
        return False

    # Mark the associated article as deleted if it exists
    if topic.article:
        try:
            article_db.mark_article_deleted(topic.article)
        except Exception as e:
            print(f"Failed to delete article {topic.article}: {str(e)}")
            # Continue with topic deletion even if article deletion fails

    # Find where the topic is stored using the entity cache
    topic_path, entity_type = find_entity_by_id(topic_id)

    if not topic_path or entity_type != "topic" or not topic_path.exists():
        return False

    # Remove the directory
    shutil.rmtree(topic_path)

    # Remove from caches
    _topic_cache.pop(topic_id, None)
    remove_from_entity_cache(topic_id)

    # Remove this topic from all projects that reference it
    projects = project_db.list_projects()
    for project in projects:
        if topic_id in project.topic_ids:
            project.topic_ids.remove(topic_id)
            project_db.save_project(project)

    return True


def update_topic(topic_id: str, updated_data: dict) -> Optional[Topic]:
    """Update a topic with new data."""
    topic = get_topic(topic_id)
    if not topic:
        return None

    # Get project and topic info before update
    project_slug, old_topic_slug = get_topic_location(topic_id)
    if not project_slug or not old_topic_slug:
        return None

    # Update topic fields
    for key, value in updated_data.items():
        if hasattr(topic, key):
            setattr(topic, key, value)


    # Just save in place
    save_topic(topic)

    return topic


def load_feed_items(items_data: List[dict]) -> List[FeedItem]:
    """Convert feed item dictionaries to FeedItem objects."""
    feed_items = []
    for item in items_data:
        try:
            if "accessed_at" in item and isinstance(item["accessed_at"], str):
                item["accessed_at"] = datetime.fromisoformat(item["accessed_at"])
            feed_items.append(FeedItem(**item))
        except Exception as e:
            print(f"Error parsing feed item: {e}")
    return feed_items
