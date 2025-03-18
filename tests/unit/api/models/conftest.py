"""
Fixtures for unit tests.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Add the src directory to the Python path if not already there
src_dir = Path(__file__).parents[3].parent / 'src'
if os.path.exists(src_dir) and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


@pytest.fixture
def sample_topic_data():
    """Return sample data for creating a Topic."""
    return {
        "id": "topic-sample",
        "name": "Sample Topic",
        "description": "This is a sample topic for testing",
        "feed_urls": ["https://example.com/feed1", "https://example.com/feed2"],
        "publish_urls": ["https://example.com/publish1"],
        "thumbnail_url": "https://example.com/thumbnail.jpg",
    }


@pytest.fixture
def sample_project_data():
    """Return sample data for creating a Project."""
    return {
        "id": "project-sample",
        "title": "Sample Project",
        "description": "This is a sample project for testing",
        "topic_ids": ["topic-1", "topic-2"],
        "thumbnail_url": "https://example.com/project-thumbnail.jpg",
        "created_at": datetime(2023, 1, 1),
        "updated_at": datetime(2023, 1, 2),
    }


@pytest.fixture
def sample_article_data():
    """Return sample data for creating an Article."""
    return {
        "id": "article-sample",
        "title": "Sample Article",
        "topic_id": "topic-sample",
        "content": "This is sample article content for testing purposes.",
        "version": 1,
        "created_at": datetime(2023, 1, 1),
        "updated_at": None,
        "previous_version": None,
        "next_version": None,
    }


@pytest.fixture
def sample_feed_item_data():
    """Return sample data for creating a FeedItem."""
    return {
        "url": "https://example.com/feed-item",
        "accessed_at": datetime.now(timezone.utc),
        "content_hash": "sample-hash-123456",
        "is_relevant": True,
        "relevance_explanation": "Sample relevance explanation",
        "needs_further_processing": False,
        "new_information": "Sample new information",
        "enforcing_information": "Sample enforcing information",
        "contradicting_information": "Sample contradicting information",
        "article_id": "article-sample",
    }


@pytest.fixture
def sample_prompt_data():
    """Return sample data for creating a Prompt."""
    return {
        "id": "prompt-sample",
        "name": "Sample Prompt",
        "template": "This is a sample template for {topic} with {placeholder}",
    }
