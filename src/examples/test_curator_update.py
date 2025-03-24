"""
Example script to test the curator chain with a test topic.

This script creates a test Topic and runs it through the curator chain
to verify that the chain works correctly.
"""

import os
import sys
from datetime import datetime, timezone

import yaml

from api.db.project_db import add_topic_to_project, save_project
from api.db.topic_db import save_topic
from api.models.feed_item import FeedItem
from api.models.project import Project
from api.models.topic import Topic
from curator.graph_workflow import create_curator_graph
from curator.topic_updater import queue_topic_update, start_update_processor
from utils.logging import debug, error, info

# Load environment variables from settings.yaml
if os.path.exists("settings.yaml"):
    with open("settings.yaml", "r") as f:
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

        project = Project(
            id="r4b-test-project",
            title="Radio 4 Brainport News for Expats",
            description="Continuously updated news items for international residents in the Eindhoven region, formatted for radio broadcasts.",
            topic_ids=[],
            thumbnail_url=None,
            slug="r4b-test-project",
            created_at=datetime.now(timezone.utc),
        )
        save_project(project)

        topic = Topic(
            id="test-r4b",
            name="Cultural Events",
            description="Information about upcoming cultural events, performances, exhibitions, and art installations in the region.",
            feed_urls=["feed://eindhovennews.com/feed"],
            publish_urls=[
                "file:///Users/olafjanssen/Documents/Radio4Brainport/cultural-events.md"
            ],
        )
        info("TEST", "Created test topic", topic.name)

        add_topic_to_project(project.id, topic.id)

        save_topic(topic)

        start_update_processor()
        queue_topic_update(topic.id)

        # Hold script ending until key is pressed
        input("Press Enter to end script...")

    except Exception as e:
        error("TEST", "Error running test", str(e))
        raise


if __name__ == "__main__":
    main()
