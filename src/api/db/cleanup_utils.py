"""
Database cleanup utilities for maintaining data integrity.

This module provides utilities for cleaning up orphaned references
and maintaining consistency between related entities.
"""

from typing import List, Set
from utils.logging import debug, info, warning


def cleanup_orphaned_topic_references() -> int:
    """
    Remove orphaned topic references from projects.
    
    This function finds topics that are referenced in project.topic_ids
    but no longer exist in the database, and removes those references.
    
    Returns:
        Number of orphaned references cleaned up
    """
    from api.db.project_db import list_projects, save_project
    from api.db.topic_db import get_topic
    
    cleaned_count = 0
    
    # Get all projects
    projects = list_projects()
    if not projects:
        return cleaned_count
    
    # Get all existing topic IDs
    existing_topic_ids = set()
    for project in projects:
        for topic_id in project.topic_ids:
            topic = get_topic(topic_id)
            if topic:
                existing_topic_ids.add(topic_id)
    
    # Clean up each project
    for project in projects:
        original_topic_count = len(project.topic_ids)
        
        # Find orphaned topic IDs in this project
        orphaned_ids = []
        for topic_id in project.topic_ids:
            if topic_id not in existing_topic_ids:
                orphaned_ids.append(topic_id)
        
        # Remove orphaned references
        if orphaned_ids:
            project.topic_ids = [tid for tid in project.topic_ids if tid not in orphaned_ids]
            save_project(project)
            
            cleaned_count += len(orphaned_ids)
            
            warning("CLEANUP", "Removed orphaned topic references", 
                    f"Project: {project.title}, Removed: {orphaned_ids}")
    
    if cleaned_count > 0:
        info("CLEANUP", "Orphaned topic references cleaned", 
             f"Total removed: {cleaned_count}")
    
    return cleaned_count


def cleanup_orphaned_article_references() -> int:
    """
    Remove orphaned article references from topics.
    
    This function finds articles that are referenced in topic.article
    but no longer exist in the database, and removes those references.
    
    Returns:
        Number of orphaned references cleaned up
    """
    from api.db.topic_db import list_topics, save_topic
    from api.db.article_db import get_article
    
    cleaned_count = 0
    
    # Get all topics
    topics = list_topics()
    if not topics:
        return cleaned_count
    
    # Clean up each topic
    for topic in topics:
        if topic.article:
            article = get_article(topic.article)
            if not article:
                # Article doesn't exist, remove reference
                topic.article = None
                save_topic(topic)
                cleaned_count += 1
                
                warning("CLEANUP", "Removed orphaned article reference", 
                        f"Topic: {topic.name}, Article ID: {topic.article}")
    
    if cleaned_count > 0:
        info("CLEANUP", "Orphaned article references cleaned", 
             f"Total removed: {cleaned_count}")
    
    return cleaned_count


def cleanup_orphaned_feed_references() -> int:
    """
    Remove orphaned feed item references from topics.
    
    This function finds feed items that are referenced in topic.processed_feeds
    but have invalid IDs, and removes those references.
    
    Returns:
        Number of orphaned references cleaned up
    """
    from api.db.topic_db import list_topics, save_topic
    
    cleaned_count = 0
    
    # Get all topics
    topics = list_topics()
    if not topics:
        return cleaned_count
    
    # Clean up each topic
    for topic in topics:
        if topic.processed_feeds:
            original_count = len(topic.processed_feeds)
            
            # Filter out feed items with invalid IDs
            valid_feeds = []
            for feed_item in topic.processed_feeds:
                if feed_item.id and feed_item.id.strip():
                    # Feed item has a valid ID
                    valid_feeds.append(feed_item)
                else:
                    # Feed item has no ID or empty ID
                    cleaned_count += 1
            
            if len(valid_feeds) != original_count:
                topic.processed_feeds = valid_feeds
                save_topic(topic)
                
                removed_count = original_count - len(valid_feeds)
                cleaned_count += removed_count
                
                warning("CLEANUP", "Removed orphaned feed references", 
                        f"Topic: {topic.name}, Removed: {removed_count}")
    
    if cleaned_count > 0:
        info("CLEANUP", "Orphaned feed references cleaned", 
             f"Total removed: {cleaned_count}")
    
    return cleaned_count


def run_full_cleanup() -> dict:
    """
    Run all cleanup operations and return a summary.
    
    Returns:
        Dictionary with cleanup results
    """
    info("CLEANUP", "Starting full database cleanup", "Running all cleanup operations")
    
    results = {
        "orphaned_topics": cleanup_orphaned_topic_references(),
        "orphaned_articles": cleanup_orphaned_article_references(),
        "orphaned_feeds": cleanup_orphaned_feed_references()
    }
    
    total_cleaned = sum(results.values())
    
    if total_cleaned > 0:
        info("CLEANUP", "Full cleanup completed", 
             f"Total cleaned: {total_cleaned}, Details: {results}")
    else:
        info("CLEANUP", "Full cleanup completed", "No orphaned references found")
    
    return results
