"""
Unit tests for the FeedItem model.
"""

import hashlib
from datetime import datetime, timezone

from src.api.models.feed_item import FeedItem


def test_feed_item_creation():
    """Test creating a FeedItem instance manually."""
    current_time = datetime.now(timezone.utc)

    feed_item = FeedItem(
        url="https://example.com/feed/1",
        accessed_at=current_time,
        content_hash="abc123",
        is_relevant=True,
        relevance_explanation="This is relevant to our topic",
        needs_further_processing=False,
    )

    assert feed_item.url == "https://example.com/feed/1"
    assert feed_item.accessed_at == current_time
    assert feed_item.content_hash == "abc123"
    assert feed_item.is_relevant
    assert feed_item.relevance_explanation == "This is relevant to our topic"
    assert not feed_item.needs_further_processing
    assert feed_item.new_information == ""
    assert feed_item.enforcing_information == ""
    assert feed_item.contradicting_information == ""
    assert feed_item.article_id is None


def test_feed_item_factory_method():
    """Test the create factory method for FeedItem."""
    url = "https://example.com/news/1"
    content = "This is some test content for a feed item"
    expected_hash = hashlib.sha256(content.encode()).hexdigest()

    feed_item = FeedItem.create(url, content)

    assert feed_item.url == url
    assert feed_item.content_hash == expected_hash
    assert isinstance(feed_item.accessed_at, datetime)
    assert not feed_item.is_relevant
    assert feed_item.relevance_explanation == ""
    assert not feed_item.needs_further_processing


def test_feed_item_factory_with_processing_flag():
    """Test creating a FeedItem that needs further processing."""
    url = "https://example.com/news/2"
    content = "More test content"

    feed_item = FeedItem.create(url, content, needs_further_processing=True)

    assert feed_item.url == url
    assert feed_item.needs_further_processing
    assert not feed_item.is_relevant


def test_feed_item_with_substance_extraction():
    """Test FeedItem with substance extraction information."""
    feed_item = FeedItem(
        url="https://example.com/news/3",
        accessed_at=datetime.now(timezone.utc),
        content_hash="def456",
        is_relevant=True,
        new_information="This is new information",
        enforcing_information="This reinforces existing information",
        contradicting_information="This contradicts previous information",
    )

    assert feed_item.new_information == "This is new information"
    assert feed_item.enforcing_information == "This reinforces existing information"
    assert (
        feed_item.contradicting_information == "This contradicts previous information"
    )


def test_feed_item_with_article_reference():
    """Test FeedItem with article reference."""
    feed_item = FeedItem(
        url="https://example.com/news/4",
        accessed_at=datetime.now(timezone.utc),
        content_hash="ghi789",
        is_relevant=True,
        article_id="article-123",
    )

    assert feed_item.article_id == "article-123"


def test_feed_item_from_fixture(sample_feed_item_data):
    """Test creating a FeedItem from fixture data."""
    feed_item = FeedItem(**sample_feed_item_data)

    assert feed_item.url == sample_feed_item_data["url"]
    assert feed_item.accessed_at == sample_feed_item_data["accessed_at"]
    assert feed_item.content_hash == sample_feed_item_data["content_hash"]
    assert feed_item.is_relevant == sample_feed_item_data["is_relevant"]
    assert (
        feed_item.relevance_explanation
        == sample_feed_item_data["relevance_explanation"]
    )
    assert (
        feed_item.needs_further_processing
        == sample_feed_item_data["needs_further_processing"]
    )
    assert feed_item.new_information == sample_feed_item_data["new_information"]
    assert (
        feed_item.enforcing_information
        == sample_feed_item_data["enforcing_information"]
    )
    assert (
        feed_item.contradicting_information
        == sample_feed_item_data["contradicting_information"]
    )
    assert feed_item.article_id == sample_feed_item_data["article_id"]
