"""Database operations for articles using markdown files with YAML front matter."""
import os
from datetime import datetime
import yaml
from pathlib import Path
from typing import List, Optional
import uuid

from .models import Article

DB_PATH = Path("db/articles")

def ensure_db_exists():
    """Create the articles directory if it doesn't exist."""
    DB_PATH.mkdir(parents=True, exist_ok=True)

def article_to_markdown(article: Article) -> str:
    """Convert article to markdown with YAML front matter."""
    metadata = {
        "id": article.id,
        "title": article.title,
        "topic_id": article.topic_id,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
        "version": article.version
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
    
    return Article(content=content.strip(), **metadata)

def save_article(article: Article) -> None:
    """Save article to markdown file."""
    ensure_db_exists()
    
    # Generate filename from id
    filename = DB_PATH / f"{article.id}.md"
    
    # Convert to markdown and save
    markdown = article_to_markdown(article)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown)

def get_article(article_id: str) -> Optional[Article]:
    """Retrieve article by id."""
    filename = DB_PATH / f"{article_id}.md"
    
    if not filename.exists():
        return None
        
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
        
    return markdown_to_article(content)

def list_articles() -> List[Article]:
    """List all articles."""
    ensure_db_exists()
    
    articles = []
    for file in DB_PATH.glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            articles.append(markdown_to_article(f.read()))
            
    return articles

def create_article(title: str, topic_id: str, content: str) -> Article:
    """Create and save a new article."""
    article = Article(
        id=str(uuid.uuid4()),
        title=title,
        topic_id=topic_id,
        content=content,
        created_at=datetime.utcnow()
    )
    
    save_article(article)
    return article

def update_article(article_id: str, content: str) -> Optional[Article]:
    """Update existing article with new content."""
    article = get_article(article_id)
    if not article:
        return None
        
    article.content = content
    article.updated_at = datetime.utcnow()
    article.version += 1
    
    save_article(article)
    return article