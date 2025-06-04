"""
Unit tests for the Article model.
"""

from datetime import datetime, timezone

from src.api.models.article import Article
from src.api.models.feed_item import FeedItem


def test_article_creation():
    """Test creating an Article instance."""
    creation_time = datetime(2023, 1, 1)
    update_time = datetime(2023, 1, 2)

    article = Article(
        id="article-123",
        title="Test Article",
        topic_id="topic-456",
        content="This is a test article content.",
        version=1,
        created_at=creation_time,
        updated_at=update_time,
        previous_version=None,
        next_version=None,
    )

    assert article.id == "article-123"
    assert article.title == "Test Article"
    assert article.topic_id == "topic-456"
    assert article.content == "This is a test article content."
    assert article.version == 1
    assert article.created_at == creation_time
    assert article.updated_at == update_time
    assert article.previous_version is None
    assert article.next_version is None
    assert article.source_feed is None


def test_article_with_versions():
    """Test Article with version links."""
    article = Article(
        id="article-123",
        title="Test Article",
        topic_id="topic-456",
        content="This is version 2",
        version=2,
        created_at=datetime(2023, 1, 2),
        previous_version="article-122",
        next_version="article-124",
    )

    assert article.version == 2
    assert article.previous_version == "article-122"
    assert article.next_version == "article-124"


def test_article_with_source_feed():
    """Test Article with a source feed item."""
    feed_item = FeedItem(
        url="https://example.com/news/1",
        accessed_at=datetime.now(timezone.utc),
        content_hash="abc123",
        is_relevant=True,
        relevance_explanation="Highly relevant to the topic",
    )

    article = Article(
        id="article-123",
        title="Test Article",
        topic_id="topic-456",
        content="This is test content",
        version=1,
        created_at=datetime.now(),
        source_feed=feed_item,
    )

    assert article.source_feed is not None
    assert article.source_feed.url == "https://example.com/news/1"
    assert article.source_feed.is_relevant
    assert article.source_feed.relevance_explanation == "Highly relevant to the topic"


def test_article_from_fixture(sample_article_data):
    """Test creating an Article from fixture data."""
    article = Article(**sample_article_data)

    assert article.id == sample_article_data["id"]
    assert article.title == sample_article_data["title"]
    assert article.topic_id == sample_article_data["topic_id"]
    assert article.content == sample_article_data["content"]
    assert article.version == sample_article_data["version"]
    assert article.created_at == sample_article_data["created_at"]
    assert article.updated_at == sample_article_data["updated_at"]
    assert article.previous_version == sample_article_data["previous_version"]
    assert article.next_version == sample_article_data["next_version"]
