"""
Demo script for database cleanup functionality.

This script demonstrates how orphaned references are cleaned up
from projects and topics.
"""

from pathlib import Path

# Add the src directory to the path so we can import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.db.cleanup_utils import (
    cleanup_orphaned_topic_references,
    cleanup_orphaned_article_references,
    cleanup_orphaned_feed_references,
    run_full_cleanup
)
from api.db.project_db import list_projects
from api.db.topic_db import list_topics


def demo_cleanup_functions():
    """Demonstrate the cleanup functions."""
    print("=== Database Cleanup Demo ===\n")
    
    # Show current state
    print("Current Database State:")
    print("-" * 40)
    
    projects = list_projects()
    topics = list_topics()
    
    print(f"Projects: {len(projects)}")
    for project in projects:
        print(f"  - {project.title}: {len(project.topic_ids)} topics")
    
    print(f"\nTopics: {len(topics)}")
    for topic in topics:
        print(f"  - {topic.name}: article={topic.article is not None}, feeds={len(topic.processed_feeds)}")
    
    print("\n" + "=" * 60)
    
    # Run cleanup operations
    print("Running Cleanup Operations:")
    print("-" * 40)
    
    # Clean up orphaned topic references
    print("1. Cleaning orphaned topic references...")
    topic_cleaned = cleanup_orphaned_topic_references()
    print(f"   Removed {topic_cleaned} orphaned topic references")
    
    # Clean up orphaned article references
    print("2. Cleaning orphaned article references...")
    article_cleaned = cleanup_orphaned_article_references()
    print(f"   Removed {article_cleaned} orphaned article references")
    
    # Clean up orphaned feed references
    print("3. Cleaning orphaned feed references...")
    feed_cleaned = cleanup_orphaned_feed_references()
    print(f"   Removed {feed_cleaned} orphaned feed references")
    
    total_cleaned = topic_cleaned + article_cleaned + feed_cleaned
    
    print(f"\nTotal cleaned: {total_cleaned}")
    
    if total_cleaned > 0:
        print("\n✅ Cleanup completed successfully!")
        print("The database now has consistent references.")
    else:
        print("\n✅ No orphaned references found!")
        print("The database is already clean.")


def demo_full_cleanup():
    """Demonstrate the full cleanup function."""
    print("\n=== Full Cleanup Demo ===\n")
    
    print("Running full cleanup...")
    results = run_full_cleanup()
    
    print("\nCleanup Results:")
    print("-" * 40)
    for operation, count in results.items():
        print(f"{operation}: {count}")
    
    total = sum(results.values())
    print(f"\nTotal cleaned: {total}")
    
    if total > 0:
        print("\n✅ Full cleanup completed successfully!")
    else:
        print("\n✅ No cleanup needed - database is clean!")


def demo_cleanup_scenarios():
    """Show different cleanup scenarios."""
    print("\n=== Cleanup Scenarios ===\n")
    
    scenarios = [
        {
            "name": "Orphaned Topic References",
            "description": "Project references a topic that no longer exists",
            "example": "Project 'AI Research' has topic_ids: ['topic-1', 'topic-2', 'deleted-topic']",
            "solution": "Remove 'deleted-topic' from project.topic_ids"
        },
        {
            "name": "Orphaned Article References", 
            "description": "Topic references an article that no longer exists",
            "example": "Topic 'Machine Learning' has article: 'deleted-article-id'",
            "solution": "Set topic.article to None"
        },
        {
            "name": "Orphaned Feed References",
            "description": "Topic references feed items that no longer exist",
            "example": "Topic has processed_feeds with invalid feed item IDs",
            "solution": "Remove invalid feed items from topic.processed_feeds"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Example: {scenario['example']}")
        print(f"   Solution: {scenario['solution']}")
        print()
    
    print("Benefits of Cleanup:")
    print("✓ Prevents 'Topic not found' errors")
    print("✓ Maintains data consistency")
    print("✓ Improves performance by removing invalid references")
    print("✓ Prevents UI errors from missing data")
    print("✓ Keeps database clean and organized")


if __name__ == "__main__":
    print("Database Cleanup Demo")
    print("=" * 60)
    print()
    
    demo_cleanup_functions()
    demo_full_cleanup()
    demo_cleanup_scenarios()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("The cleanup system automatically removes orphaned references")
    print("to prevent 'Topic not found' errors and maintain data consistency.")
    print("Cleanup can be triggered manually via the API or automatically")
    print("when a topic is not found.")
