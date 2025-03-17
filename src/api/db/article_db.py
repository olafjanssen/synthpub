"""Database operations for articles using markdown files with YAML front matter."""
from datetime import datetime
import yaml
from typing import List, Optional
import uuid
from shutil import move

from ..models.article import Article
from ..models.feed_item import FeedItem
from .common import get_db_path

def DB_PATH():
    return get_db_path('articles')

def ensure_db_exists():
    """Create the articles directory if it doesn't exist."""
    DB_PATH().mkdir(parents=True, exist_ok=True)

def article_to_markdown(article: Article) -> str:
    """Convert article to markdown with YAML front matter."""
    metadata = {
        "id": article.id,
        "title": article.title,
        "topic_id": article.topic_id,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
        "version": article.version,
        "previous_version": article.previous_version,
        "next_version": article.next_version,
        "source_feed": article.source_feed.model_dump() if article.source_feed else None
    }
    return f"""---
{yaml.dump(metadata, sort_keys=False)}---

{article.content}
"""

def markdown_to_article(content: str) -> Article:
    """Parse markdown with YAML front matter into Article object."""
    # Split front matter and content
    _, front_matter, content = content.split("---", 2)
    
    # Parse YAML front matter
    metadata = yaml.safe_load(front_matter)
    
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
    
    return Article(content=content.strip(), **metadata)

def save_article(article: Article) -> None:
    """Save article to markdown file."""
    ensure_db_exists()
    
    # Generate filename from id
    filename = DB_PATH() / f"{article.id}.md"
    
    # Convert to markdown and save
    markdown = article_to_markdown(article)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown)

def get_article(article_id: str) -> Optional[Article]:
    """Retrieve article by id."""
    filename = DB_PATH() / f"{article_id}.md"
    
    if not filename.exists():
        return None
        
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
        
    return markdown_to_article(content)

def list_articles() -> List[Article]:
    """List all articles."""
    ensure_db_exists()
    
    articles = []
    for file in DB_PATH().glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            articles.append(markdown_to_article(f.read()))
            
    return articles

def create_article(
    title: str, 
    topic_id: str, 
    content: str,
    version: int = 1,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None
) -> Article:
    """Create and save a new article."""
    article = Article(
        id=str(uuid.uuid4()),
        title=title,
        topic_id=topic_id,
        content=content,
        version=version,
        created_at=created_at or datetime.utcnow(),  # Use provided date or current time
        updated_at=updated_at  # Use provided update date or None for new articles
    )
    
    save_article(article)
    return article

def update_article(article_id: str, content: str, feed_item: Optional[FeedItem] = None) -> Optional[Article]:
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
        updated_at=datetime.utcnow(),
        previous_version=current_article.id,
        next_version=None,  # This is the latest version
        source_feed=feed_item  # Store the feed item that triggered this update
    )
    
    # Update the previous article to point to this new version
    current_article.next_version = new_article.id
    save_article(current_article)
    
    # Save the new version
    save_article(new_article)
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
        current = get_article(current.previous_version)
    
    # Now collect all versions going forward
    while current:
        articles.append(current)
        if current.next_version:
            current = get_article(current.next_version)
        else:
            break
    
    return articles

def get_latest_version(article_id: str) -> Optional[Article]:
    """Get the most recent version of an article."""
    current = get_article(article_id)
    if not current:
        return None
        
    while current.next_version:
        current = get_article(current.next_version)
    
    return current

def mark_article_deleted(article_id: str) -> bool:
    """
    Mark an article as deleted by prefixing its filename with '_'.
    Returns True if successful, False if article not found.
    """
    filename = DB_PATH() / f"{article_id}.md"
    if not filename.exists():
        return False
    
    # New filename with '_' prefix
    new_filename = DB_PATH() / f"_{article_id}.md"
    
    # Move/rename the file
    move(filename, new_filename)
    return True