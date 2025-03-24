#!/usr/bin/env python3
"""
Script to create a Radio 4 Brainport project with topics for expats in Eindhoven region.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.db.project_db import add_topic_to_project, create_project
from src.api.db.topic_db import save_topic
# Adjust imports to use the correct paths
from src.api.models.project import ProjectCreate
from src.api.models.topic import Topic, TopicCreate

# Common feed sources for all topics
FEED_SOURCES = [
    "feed://ioplus.nl/en/feed",
    "feed://www.eindhoven.nl/nieuws/rss",
    "feed://eindhovennews.com/feed"
]

# Publishing pipeline for all topics
PUBLISH_PIPELINE = [
    "convert://prompt/radio-transcript | convert://piper-tts/en_US-kristin-medium | file:///Users/olafjanssen/Documents/Radio4Brainport/topic-title.mp3"
]

# Define topics based on stakeholder requirements
TOPICS = [
    {
        "name": "Housing in Eindhoven",
        "description": "Updates on housing availability, regulations, and market trends for expats in the Eindhoven region."
    },
    {
        "name": "Public Transportation",
        "description": "News about public transportation services, changes, and developments in the Brainport region."
    },
    {
        "name": "Education Updates",
        "description": "Latest news from Fontys, Eindhoven University of Technology, Design Academy, and other educational institutions."
    },
    {
        "name": "Healthcare Services",
        "description": "Information about healthcare services, insurance, and medical facilities for internationals in the region."
    },
    {
        "name": "Local Politics",
        "description": "Political updates from Eindhoven, Veldhoven, Geldrop, Helmond, Best, Son and Breughel, Waalre, and other municipalities."
    },
    {
        "name": "Dutch Legislation for Expats",
        "description": "News about national Dutch policies, laws, and regulations that specifically affect international residents."
    },
    {
        "name": "Innovation & Technology",
        "description": "Updates on technological innovations from local companies like ASML, Philips, NXP, VDL, and research institutions."
    },
    {
        "name": "Environment & Weather",
        "description": "News about nature, weather conditions, and environmental events affecting the Brainport region."
    },
    {
        "name": "Cultural Events",
        "description": "Information about upcoming cultural events, performances, exhibitions, and art installations in the region."
    }
]

def main():
    """Create project and topics for Radio 4 Brainport."""
    print("Creating Radio 4 Brainport project...")
    
    # Create project first
    project = create_project(
        title="Radio 4 Brainport News for Expats", 
        description="Continuously updated news items for international residents in the Eindhoven region, formatted for radio broadcasts.",
        topic_ids=[], 
        thumbnail_url=None  # Auto-generate thumbnail
    )
    
    print(f"Created project: {project.title} (ID: {project.id})")
    
    # Create topics and add to project
    topic_ids = []
    for topic_data in TOPICS:
        try:
            # Create topic with necessary fields
            topic_id = str(uuid4())
            topic = Topic(
                id=topic_id,
                name=topic_data["name"],
                description=topic_data["description"],
                feed_urls=FEED_SOURCES,
                publish_urls=PUBLISH_PIPELINE
            )
            
            # Add topic to project first
            add_topic_to_project(project.id, topic_id)
            
            # Then save the topic
            save_topic(topic)
            topic_ids.append(topic_id)
            print(f"Created topic: {topic_data['name']} (ID: {topic_id})")
        except Exception as e:
            print(f"Error creating topic {topic_data['name']}: {e}")
    
    print(f"Successfully created project with {len(topic_ids)} topics")

if __name__ == "__main__":
    main()
    