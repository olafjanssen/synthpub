"""
Database operations for articles using hierarchical folder structure with markdown files.
"""

import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from shutil import rmtree
from typing import List, Optional, Tuple

import yaml

from ..models.article import Article
from ..models.feed_item import FeedItem
from . import topic_db
from .common import (
    add_to_entity_cache,
    create_slug,
    ensure_path_exists,
    find_entity_by_id,
    get_article_path,
    get_hierarchical_path,
    remove_from_entity_cache,
)


def get_article_location(
    article_id: str,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Find where an article is stored in the hierarchical structure.

    Returns:
        Tuple of (project_slug, topic_slug, timestamp) or (None, None, None) if not found
    """
    # Use find_entity_by_id to locate the article
    article_path, entity_type = find_entity_by_id(article_id)

    if not article_path or entity_type != "article":
        return None, None, None

    # Extract path components
    # Structure is: vault/project/topic/timestamp
    timestamp = article_path.name
    topic_path = article_path.parent
    topic_slug = topic_path.name
    project_path = topic_path.parent
    project_slug = project_path.name

    return project_slug, topic_slug, timestamp


def article_to_files(article: Article, article_path: Path) -> None:
    """Save article as metadata.yaml and article.md files."""
    # Write metadata file
    metadata = {
        "id": article.id,
        "title": article.title,
        "topic_id": article.topic_id,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
        "version": article.version,
        "previous_version": article.previous_version,
        "next_version": article.next_version,
        "source_feed": (
            article.source_feed.model_dump() if article.source_feed else None
        ),
    }

    metadata_file = article_path / "metadata.yaml"
    with open(metadata_file, "w", encoding="utf-8") as f:
        yaml.dump(metadata, f, sort_keys=False)
        f.flush()

    # Write content file
    content_file = article_path / "article.md"
    with open(content_file, "w", encoding="utf-8") as f:
        f.write(article.content)
        f.flush()


def files_to_article(metadata_path: Path) -> Article:
    """Load article from metadata.yaml and article.md files."""
    # Read metadata
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = yaml.safe_load(f)

    # Read content
    content_path = metadata_path.parent / "article.md"
    with open(content_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Convert ISO strings back to datetime
    metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])
    if metadata["updated_at"]:
        metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"])

    # Convert source feed data if present
    if metadata.get("source_feed"):
        feed_data = metadata["source_feed"]
        # Handle accessed_at which might be string or datetime
        if isinstance(feed_data["accessed_at"], str):
            feed_data["accessed_at"] = datetime.fromisoformat(feed_data["accessed_at"])
        metadata["source_feed"] = FeedItem(**feed_data)

    return Article(content=content, **metadata)


def save_article(article: Article) -> None:
    """Save article to files in hierarchical structure."""
    # Get the topic
    topic = topic_db.get_topic(article.topic_id)
    if not topic:
        raise ValueError(
            f"Cannot save article for non-existent topic {article.topic_id}"
        )

    # Find project/topic location
    project_slug, topic_slug = topic_db.get_topic_location(article.topic_id)
    if not project_slug or not topic_slug:
        raise ValueError(f"Cannot find location for topic {article.topic_id}")

    # Get article directory path
    timestamp = article.updated_at or article.created_at
    article_path = get_article_path(project_slug, topic_slug, timestamp)

    # Save article to files
    article_to_files(article, article_path)

    # Check if the files were created
    metadata_file = article_path / "metadata.yaml"
    content_file = article_path / "article.md"
    if not metadata_file.exists() or not content_file.exists():
        raise ValueError(f"Failed to save article to {article_path}")

    # Update entity cache
    add_to_entity_cache(article.id, article_path, "article")

    # Update topic to reference this article if not already set
    if not topic.article:
        topic.article = article.id
        topic_db.save_topic(topic)


def get_article(article_id: str) -> Optional[Article]:
    """Retrieve article by id."""
    # Use find_entity_by_id to locate the article
    article_path, entity_type = find_entity_by_id(article_id)

    if not article_path or entity_type != "article":
        return None

    metadata_file = article_path / "metadata.yaml"
    if not metadata_file.exists():
        return None

    return files_to_article(metadata_file)


def get_article_by_slug(
    project_slug: str, topic_slug: str, timestamp: str
) -> Optional[Article]:
    """Retrieve article by its path slugs and timestamp."""
    article_path = get_hierarchical_path(project_slug, topic_slug, timestamp)
    metadata_file = article_path / "metadata.yaml"

    if not metadata_file.exists():
        return None

    return files_to_article(metadata_file)


def list_articles() -> List[Article]:
    """List all articles."""
    articles = []
    vault_path = get_hierarchical_path()

    # Find all article metadata files
    for metadata_file in vault_path.glob("**/metadata.yaml"):
        try:
            # Check if this is an article by looking at directory structure
            parent_dir = metadata_file.parent
            if parent_dir.parent.parent.parent == vault_path:
                # Structure is: vault/project/topic/timestamp/metadata.yaml
                article = files_to_article(metadata_file)
                articles.append(article)
        except Exception as e:
            print(f"Error loading article from {metadata_file}: {e}")

    return articles


def create_article(
    title: str,
    topic_id: str,
    content: str,
    version: int = 1,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
) -> Article:
    """Create and save a new article."""
    article = Article(
        id=str(uuid.uuid4()),
        title=title,
        topic_id=topic_id,
        content=content,
        version=version,
        created_at=created_at or datetime.now(UTC),
        updated_at=updated_at,
    )

    save_article(article)
    return article


def update_article(
    article_id: str, content: str, feed_item: Optional[FeedItem] = None
) -> Optional[Article]:
    """
    Update existing article by creating a new version.

    Args:
        article_id: ID of the article to update
        content: New content for the article
        feed_item: Feed item that triggered this update

    Returns:
        New Article object with incremented version number
    """
    # Get the current article
    current_article = get_article(article_id)
    if not current_article:
        return None

    # Create new article version
    new_article = Article(
        id=str(uuid.uuid4()),
        title=current_article.title,
        topic_id=current_article.topic_id,
        content=content,
        version=current_article.version + 1,
        created_at=current_article.created_at,
        updated_at=datetime.now(UTC),
        previous_version=current_article.id,
        next_version=None,  # This is the latest version
        source_feed=feed_item,  # Store the feed item that triggered this update
    )

    # Update the previous article to point to this new version
    current_article.next_version = new_article.id
    save_article(current_article)

    # Save the new version
    save_article(new_article)

    # Update the topic to point to the latest version
    topic = topic_db.get_topic(current_article.topic_id)
    if topic:
        topic.article = new_article.id
        topic_db.save_topic(topic)

    return new_article


def get_article_history(article_id: str) -> List[Article]:
    """
    Get the complete version history of an article.
    Returns list ordered from oldest to newest.
    """
    articles = []
    current = get_article(article_id)

    # First, go back to the earliest version
    while current and current.previous_version:
        prev = get_article(current.previous_version)
        if prev:
            current = prev
        else:
            break

    # Now collect all versions going forward
    while current:
        articles.append(current)
        if current.next_version:
            next_article = get_article(current.next_version)
            if next_article:
                current = next_article
            else:
                break
        else:
            break

    return articles


def get_latest_version(article_id: str) -> Optional[Article]:
    """Get the most recent version of an article."""
    current = get_article(article_id)
    if not current:
        return None

    while current.next_version:
        next_article = get_article(current.next_version)
        if next_article:
            current = next_article
        else:
            break

    return current


def mark_article_deleted(article_id: str) -> bool:
    """
    Mark an article as deleted by removing its directory.
    Returns True if successful, False if article not found.
    """
    article_path, entity_type = find_entity_by_id(article_id)

    if not article_path or entity_type != "article":
        return False

    # Remove the directory
    if article_path.exists():
        rmtree(article_path)

    # Remove from entity cache
    remove_from_entity_cache(article_id)

    # Also delete any old versions
    article = get_article(article_id)
    if article and article.previous_version:
        mark_article_deleted(article.previous_version)

    return True
