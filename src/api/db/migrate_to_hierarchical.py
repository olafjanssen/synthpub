#!/usr/bin/env python3
"""
Migration script to transfer data from flat to hierarchical structure.
"""

import os
import sys
from pathlib import Path

# Set environment variable for flat DB
os.environ["DB_IMPLEMENTATION"] = "flat"

# Add the parent directory to the Python path
current_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(current_dir))

# Import hierarchical implementation directly
from api.db import article_db as hier_article_db
from api.db import project_db as hier_project_db
from api.db import topic_db as hier_topic_db
from api.db.common import (ensure_path_exists, get_article_path, get_db_path,
                           get_hierarchical_path)
from api.db.db_flat import article_db as flat_article_db
from api.db.db_flat import project_db as flat_project_db
from api.db.db_flat import topic_db as flat_topic_db


def ensure_vault_exists():
    """Create the vault directory and subdirectories."""
    vault_path = get_hierarchical_path()
    ensure_path_exists(vault_path)
    print(f"Created vault directory at: {vault_path}")


def migrate_projects():
    """Migrate all projects to hierarchical structure."""
    print("\nMigrating projects...")
    projects = flat_project_db.list_projects()
    print(f"Found {len(projects)} projects to migrate")
    
    for i, project in enumerate(projects, 1):
        print(f"Migrating project {i}/{len(projects)}: {project.title}")
        hier_project_db.save_project(project)
    
    print("Projects migration complete")


def migrate_topics():
    """Migrate all topics to hierarchical structure."""
    print("\nMigrating topics...")
    topics = flat_topic_db.list_topics()
    print(f"Found {len(topics)} topics to migrate")
    
    for i, topic in enumerate(topics, 1):
        print(f"Migrating topic {i}/{len(topics)}: {topic.name}")
        try:
            hier_topic_db.save_topic(topic)
        except ValueError as e:
            print(f"  Error: {e}")
            print("  This topic may not be associated with any project - skipping")
    
    print("Topics migration complete")


def migrate_articles():
    """Migrate all articles to hierarchical structure."""
    print("\nMigrating articles...")
    articles = flat_article_db.list_articles()
    print(f"Found {len(articles)} articles to migrate")
    
    # Group articles by topic_id for better organization
    articles_by_topic = {}
    for article in articles:
        if article.topic_id not in articles_by_topic:
            articles_by_topic[article.topic_id] = []
        articles_by_topic[article.topic_id].append(article)
    
    print(f"Articles belong to {len(articles_by_topic)} different topics")
    
    # Process each topic's articles
    for topic_id, topic_articles in articles_by_topic.items():
        print(f"Migrating {len(topic_articles)} articles for topic {topic_id}")
        
        # Find all articles that are part of version chains
        article_versions = {}
        standalone_articles = []
        
        for article in topic_articles:
            # Check if this article is part of a version chain
            if article.previous_version or article.next_version:
                # Get the root article ID (earliest version)
                root_id = article.id
                current = article
                while current.previous_version:
                    root_id = current.previous_version
                    # Find the previous version article in our list
                    for a in topic_articles:
                        if a.id == current.previous_version:
                            current = a
                            break
                    else:
                        # Previous version not found in our list
                        break
                
                # Add to the version chain
                if root_id not in article_versions:
                    article_versions[root_id] = []
                article_versions[root_id].append(article)
            else:
                # This is a standalone article
                standalone_articles.append(article)
        
        # Save all articles with appropriate versioning
        for root_id, versions in article_versions.items():
            # Sort versions by version number
            versions.sort(key=lambda a: a.version)
            
            # Save each version
            for article in versions:
                try:
                    hier_article_db.save_article(article)
                    print(f"  Migrated article: {article.title} (version {article.version})")
                except ValueError as e:
                    print(f"  Error: {e}")
        
        # Save standalone articles
        for article in standalone_articles:
            try:
                hier_article_db.save_article(article)
                print(f"  Migrated article: {article.title}")
            except ValueError as e:
                print(f"  Error: {e}")
    
    print("Articles migration complete")


def main():
    """Run the migration from flat to hierarchical DB structure."""
    print("Starting migration from flat to hierarchical DB structure")
    
    # Ensure vault directory exists
    ensure_vault_exists()
    
    # Migrate all data
    migrate_projects()
    migrate_topics()
    migrate_articles()
    
    print("\nMigration complete!")
    print("To use the hierarchical DB structure, set the DB_IMPLEMENTATION environment variable to 'hierarchical'")
    print("Example: export DB_IMPLEMENTATION=hierarchical")


if __name__ == "__main__":
    main() 