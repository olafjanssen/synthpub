"""
Example script to test the curator chain with a test topic.

This script creates a test Topic and runs it through the curator chain
to verify that the chain works correctly.
"""
import sys
import os

from api.models.topic import Topic
from api.models.feed_item import FeedItem
from curator.graph_workflow import create_curator_graph
from utils.logging import info, debug, error
from api.db.topic_db import save_topic
from api.db.article_db import get_article
from datetime import datetime, timezone
import yaml

# Load environment variables from settings.yaml
if os.path.exists("settings.yaml"):
    with open("settings.yaml", 'r') as f:
        settings = yaml.safe_load(f)
        env_vars = settings.get("env_vars", {})
        debug("CONFIG", "Environment variables", f"Found {len(env_vars)} variables")
        for key, value in env_vars.items():
            os.environ[key] = value
else:
    error("CONFIG", "Settings file not found", "settings.yaml")
    sys.exit(1)

def main():
    """Run the test script."""
    try:
        topic = Topic(
            id="test-topic-123",
            name="Climate Change",
            description="Information about climate change, its effects, and mitigation strategies.",
            feed_urls=["https://example.com/climate-feed"],
            publish_urls=["https://example.com/publish"]
        )
        info("TEST", "Created test topic", topic.name)
                    
        # Create test feed item and content
        feed_item = FeedItem(
            url="https://example.com/climate-article",
            content_hash="abc123",
            accessed_at=datetime.now(timezone.utc)
        )
        feed_content = """
        Recent research has shown that climate change is affecting ecosystems faster than previously thought.
        Ocean temperatures have risen by 0.5 degrees Celsius in the last decade, leading to coral bleaching
        and migration of marine species. Researchers at the University of Science have documented these changes
        in a new study published in the Journal of Climate Research.
        """

        # Create test feed item and content
        feed_item2 = FeedItem(
            url="https://example.com/climate-article2",
            content_hash="abc124",
            accessed_at=datetime.now(timezone.utc)
        )
        feed_content2 = """
        Recent research has shown that climate change is affecting ecosystems faster than previously thought.
        Ocean temperatures have risen by 0.5 degrees Celsius in the last decade, leading to coral bleaching
        and migration of marine species. Researchers at the University of Science have documented these changes
        in a new study published in the Journal of Climate Research.
        """

        save_topic(topic)

        # Create the curator chain
        graph = create_curator_graph()
        png = graph.get_graph().draw_mermaid_png()
        with open("curator_graph.png", "wb") as f:
            f.write(png)

        mm = graph.get_graph().draw_mermaid()
        with open("curator_graph.md", "w") as f:
            f.write(mm)

        exit()

        # Run the chain with our test data
        info("TEST", "Running content processing", "Starting process")
        result = graph.invoke({
            "topic_id": topic.id,
            "feed_content": feed_content,
            "feed_item": feed_item
        })
        
        # Display results
        info("TEST", "Chain completed", f"Result: {result.get('result', False)}")

        result = graph.invoke({
            "topic_id": topic.id,
            "feed_content": feed_content2,
            "feed_item": feed_item2
        })
                
    except Exception as e:
        error("TEST", "Error running test", str(e))
        raise

if __name__ == "__main__":
    main() 