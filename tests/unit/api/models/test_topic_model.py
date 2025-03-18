"""
Unit tests for the Topic model.
"""

from datetime import datetime

from api.models.topic import (Representation, Topic, TopicBase,
                                  TopicCreate, TopicUpdate)


def test_topic_base_creation():
    """Test creating a TopicBase instance."""
    topic_base = TopicBase(
        name="Test Topic",
        description="This is a test topic",
        feed_urls=["https://example.com/feed1", "https://example.com/feed2"],
    )

    assert topic_base.name == "Test Topic"
    assert topic_base.description == "This is a test topic"
    assert len(topic_base.feed_urls) == 2
    assert topic_base.feed_urls[0] == "https://example.com/feed1"
    assert len(topic_base.publish_urls) == 0
    assert topic_base.thumbnail_url is None


def test_topic_create():
    """Test TopicCreate model."""
    topic_create = TopicCreate(
        name="Test Topic",
        description="This is a test topic",
        feed_urls=["https://example.com/feed1"],
        publish_urls=["https://example.com/publish"],
        thumbnail_url="https://example.com/thumbnail.jpg",
    )

    assert topic_create.name == "Test Topic"
    assert topic_create.publish_urls == ["https://example.com/publish"]
    assert topic_create.thumbnail_url == "https://example.com/thumbnail.jpg"


def test_topic_update():
    """Test TopicUpdate model."""
    topic_update = TopicUpdate(
        name="Updated Topic",
        description=None,
        feed_urls=["https://example.com/newfeed"],
    )

    assert topic_update.name == "Updated Topic"
    assert topic_update.description is None
    assert topic_update.feed_urls == ["https://example.com/newfeed"]
    assert topic_update.publish_urls is None
    assert topic_update.thumbnail_url is None


def test_representation_creation():
    """Test creating a Representation instance."""
    metadata = {"source": "test", "confidence": 0.95}
    representation = Representation(
        type="summary", content="This is a summary", metadata=metadata
    )

    assert representation.type == "summary"
    assert representation.content == "This is a summary"
    assert representation.metadata == metadata
    assert isinstance(representation.created_at, datetime)


def test_topic_creation():
    """Test creating a Topic instance."""
    topic = Topic(
        id="topic-123",
        name="Test Topic",
        description="This is a test topic",
        feed_urls=["https://example.com/feed1"],
        article="article-456",
        created_at=datetime(2023, 1, 1),
    )

    assert topic.id == "topic-123"
    assert topic.name == "Test Topic"
    assert topic.article == "article-456"
    assert isinstance(topic.created_at, datetime)
    assert len(topic.representations) == 0
    assert len(topic.processed_feeds) == 0


def test_add_representation():
    """Test adding a representation to a topic."""
    topic = Topic(
        id="topic-123",
        name="Test Topic",
        description="This is a test topic",
        feed_urls=["https://example.com/feed1"],
    )

    metadata = {"source": "test"}
    topic.add_representation("summary", "This is a summary", metadata)

    assert len(topic.representations) == 1
    assert topic.representations[0].type == "summary"
    assert topic.representations[0].content == "This is a summary"
    assert topic.representations[0].metadata == metadata


def test_topic_from_fixture(sample_topic_data):
    """Test creating a Topic from fixture data."""
    topic = Topic(**sample_topic_data)

    assert topic.id == sample_topic_data["id"]
    assert topic.name == sample_topic_data["name"]
    assert topic.description == sample_topic_data["description"]
    assert topic.feed_urls == sample_topic_data["feed_urls"]
    assert topic.publish_urls == sample_topic_data["publish_urls"]
    assert topic.thumbnail_url == sample_topic_data["thumbnail_url"]
