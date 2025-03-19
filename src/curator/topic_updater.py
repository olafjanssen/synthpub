import threading
import time
from queue import Queue

from api.db.cache_manager import get_all_connectors
from api.db.topic_db import get_topic
from api.models.feed_item import FeedItem
from api.signals import convert_requested, publish_requested
# Import the LangGraph-based implementation
from curator.graph_workflow import process_feed_item as graph_process_feed_item
from utils.logging import debug, error, info, warning

# Single processing queue for all items
# Each item is a tuple (topic_id, content, feed_item)
processing_queue = Queue()


def queue_topic_update(topic_id: str):
    """
    Queue a topic update by adding its feed URLs to the processing queue.

    Args:
        topic_id: The ID of the topic to update
        sender: The name of the component requesting the update
    """
    try:
        # Load topic
        topic = get_topic(topic_id)
        if not topic:
            warning("TOPIC", "Not found", topic_id)
            return

        info("TOPIC", "Queuing update", f"Topic: {topic.name}")

        # Queue each feed URL as a separate item
        for feed_url in topic.feed_urls:
            # Create a feed item for the URL with needs_further_processing=True
            feed_item = FeedItem.create(
                url=feed_url, content="", needs_further_processing=True
            )

            # Add to queue (topic_id, content=None, feed_item)
            processing_queue.put((topic_id, None, feed_item))
            debug("TOPIC", "Feed queued", f"Topic: {topic.name}, URL: {feed_url}")

    except Exception as e:
        error("TOPIC", "Update error", f"{topic_id}: {str(e)}")


def handle_topic_publishing(sender):
    """Signal handler for topic publishing requests."""
    info("TOPIC", "Publishing", sender.name)

    # Process feeds
    topic = sender
    for publish_url in topic.publish_urls:
        # split publish_url into piped elements
        commands = [cmd.strip() for cmd in publish_url.split("|")]

        debug("CONVERT", "Default conversion", "content")
        convert_requested.send(topic, type="content")

        for cmd in commands:
            if cmd.startswith("convert://"):
                conversion_type = cmd.split("://", 1)[1].strip()
                info("CONVERT", conversion_type, f"Topic: {topic.name}")
                convert_requested.send(topic, type=conversion_type)
            else:
                info("PUBLISH", cmd, f"Topic: {topic.name}")
                publish_requested.send(topic, publish_url=cmd)


def process_queue():
    """Process items from the unified processing queue."""
    while True:
        try:
            # Get the next item from the queue
            if not processing_queue.empty():
                topic_id, content, feed_item = processing_queue.get()

                if feed_item.needs_further_processing:
                    # Process the feed URL
                    debug("FEED", "Processing URL", feed_item.url)
                    process_feed_url(topic_id, feed_item.url)
                else:
                    # Process through curator chain
                    debug("FEED", "Processing content", feed_item.url)
                    process_feed_item(topic_id, content, feed_item)

                    # Trigger publishing after processing
                    topic = get_topic(topic_id)
                    if topic:
                        handle_topic_publishing(topic)
            else:
                # Small sleep to prevent CPU spinning
                time.sleep(0.1)

        except Exception as e:
            error("SYSTEM", "Queue processing error", str(e))


def add_feed_item_to_queue(topic_id: str, feed_item: FeedItem, content: str):
    """Add a feed item to the processing queue."""

    debug("FEED", "Queuing item", feed_item.url)

    # Add directly to queue using the uniform format
    processing_queue.put((topic_id, content, feed_item))


def start_update_processor():
    """Start the update processor thread."""
    # Start queue processor thread
    processor_thread = threading.Thread(target=process_queue, daemon=True)
    processor_thread.start()
    info("SYSTEM", "Content processor started", "Topic updater ready")

    return processor_thread


def process_feed_item(
    topic_id: str, feed_content: str = None, feed_item: FeedItem = None
) -> None:
    """
    Process a single feed item for a topic through the curator workflow.

    Args:
        topic_id: The ID of the topic
        feed_content: The content from the feed
        feed_item: The feed item being processed
    """
    # Use the new LangGraph implementation
    result = graph_process_feed_item(
        topic_id=topic_id, feed_content=feed_content, feed_item=feed_item
    )

    # Handle the result as needed (most handling is done in the graph implementation)
    if result.get("has_error"):
        debug(
            "CURATOR",
            "Processing failed",
            f"Step: {result.get('error_step')}, Error: {result.get('error_message')}",
        )


def process_feed_url(topic_id: str, feed_url: str):
    """
    Process a feed URL directly using available connectors.

    Args:
        topic_id: The ID of the topic
        feed_url: The URL to process
    """
    debug("FEED", "Processing URL", feed_url)

    # Get all available connectors
    connectors = get_all_connectors()

    # Find a connector that can handle this URL
    for connector_class in connectors:
        if connector_class.can_handle(feed_url):
            debug(
                "FEED", "Using connector", f"{connector_class.__name__} for {feed_url}"
            )
            try:
                # Directly call the handler method
                connector_class.handle_feed_update(topic_id, feed_url)
                return
            except Exception as e:
                error(
                    "FEED", "Connector error", f"{connector_class.__name__}: {str(e)}"
                )

    warning("FEED", "No connector found", f"URL: {feed_url}")
