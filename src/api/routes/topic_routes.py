"""Topic-related API routes."""

from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from api.db.topic_db import (get_topic, get_topic_location, get_topic_path, load_topics, mark_topic_deleted,
                             save_topic, update_topic)
from api.models.topic import Topic, TopicCreate, TopicUpdate
from curator.graph_workflow import create_curator_graph
from curator.topic_updater import (handle_topic_publishing, process_feed_item,
                                   queue_topic_update)
from services.pexels_service import get_random_thumbnail
from utils.logging import debug, error, info

from ..db.project_db import add_topic_to_project

router = APIRouter()


def request_article_generation(topic_id: str):
    """Background task to request article generation."""
    process_feed_item(topic_id)


def request_topic_update(topic_id: str):
    """Background task to request topic update."""
    debug("TOPIC", "Update requested", f"ID: {topic_id}")
    queue_topic_update(topic_id)


def request_topic_publish(topic):
    """Background task to request topic publishing."""
    debug("TOPIC", "Publish requested", topic.name)
    handle_topic_publishing(topic)


@router.post(
    "/projects/{project_id}/topics",
    response_model=Topic,
    summary="Create Topic for a Project",
    description="Creates a new topic and optionally triggers content generation",
    response_description="The newly created topic with its unique ID",
    responses={500: {"description": "Internal server error"}},
)
async def create_topic_for_project(
    project_id: str, topic: TopicCreate, background_tasks: BackgroundTasks
):
    """Create a new topic for a specific project and optionally generate an article."""
    try:
        topic_id = str(uuid4())

        thumbnail_url = topic.thumbnail_url
        if not thumbnail_url or thumbnail_url.lower() in ["auto", "none", ""]:
            thumbnail_data = get_random_thumbnail(f"{topic.name} {topic.description}")
            thumbnail_url = thumbnail_data.get("thumbnail_url")
            
        # Handle empty prompt_id
        prompt_id = topic.prompt_id
        if prompt_id == "":
            prompt_id = None

        topic_data = Topic(
            id=topic_id,
            name=topic.name,
            description=topic.description,
            feed_urls=topic.feed_urls,
            publish_urls=topic.publish_urls,
            article=None,
            processed_feeds=[],
            thumbnail_url=thumbnail_url,
            prompt_id=prompt_id,
        )

        add_topic_to_project(project_id, topic_id)

        save_topic(topic_data)
        info("TOPIC", "Created", topic.name)

        if topic.feed_urls:
            background_tasks.add_task(request_topic_update, topic_id)
        else:
            background_tasks.add_task(request_article_generation, topic_id)

        return topic_data
    except Exception as e:
        error("TOPIC", "Creation error", str(e))
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        ) from e


@router.get(
    "/topics/",
    response_model=list[Topic],
    summary="List Topics",
    description="Returns a list of all available topics",
    response_description="Array of all topics with their details",
)
async def list_topics_route():
    """List all topics."""
    debug("TOPIC", "List requested", "Getting all topics")
    topics_dict = load_topics()
    return list(topics_dict.values())


@router.get(
    "/topics/{topic_id}",
    response_model=Topic,
    summary="Get Topic",
    description="Returns details of a specific topic",
    response_description="The topic with the specified ID, including its metadata",
    responses={404: {"description": "Topic not found"}},
)
async def get_topic_route(topic_id: str):
    """Get a specific topic by ID."""
    topic = get_topic(topic_id)
    if not topic:
        error("TOPIC", "Not found", f"ID: {topic_id}")
        raise HTTPException(status_code=404, detail="Topic not found")
    debug("TOPIC", "Retrieved", topic.name)
    return topic


@router.post(
    "/topics/{topic_id}/update",
    response_model=dict,
    summary="Update Topic Content",
    description="Requests a topic update by fetching feeds and generating new content",
    response_description="Confirmation message that update has been scheduled",
    responses={
        404: {"description": "Topic not found"},
        500: {"description": "Internal server error"},
    },
)
async def schedule_topic_update_route(topic_id: str, background_tasks: BackgroundTasks):
    """Request a topic update (fetch feeds and process)."""
    try:
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")

        background_tasks.add_task(request_topic_update, topic_id)
        debug("TOPIC", "Update scheduled", topic.name)
        return {"message": f"Update scheduled for topic {topic_id}"}
    except Exception as e:
        error("TOPIC", "Update scheduling error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete(
    "/topics/{topic_id}",
    response_model=dict,
    summary="Delete Topic",
    description="Marks a topic as deleted (soft delete)",
    response_description="Confirmation message that topic has been deleted",
    responses={
        404: {"description": "Topic not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_topic_route(topic_id: str):
    """Delete a specific topic."""
    try:
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")

        mark_topic_deleted(topic_id)
        info("TOPIC", "Deleted", topic.name)
        return {"message": f"Topic {topic_id} deleted"}
    except Exception as e:
        error("TOPIC", "Deletion error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put(
    "/topics/{topic_id}",
    response_model=Topic,
    summary="Update Topic",
    description="Updates details of an existing topic",
    response_description="The updated topic with its new values",
    responses={
        404: {"description": "Topic not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_topic_route(topic_id: str, topic_update: TopicUpdate):
    """Update a topic's details."""
    try:
        # Get existing topic
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")

        # Update only non-null values
        update_data = topic_update.model_dump(exclude_unset=True)

        # Special handling for thumbnail_url
        if "thumbnail_url" in update_data:
            thumbnail_url = update_data["thumbnail_url"]
            if not thumbnail_url or thumbnail_url.lower() in ["auto", "none", ""]:
                # Generate new thumbnail
                thumbnail_data = get_random_thumbnail(
                    f"{topic.name} {topic.description}"
                )
                update_data["thumbnail_url"] = thumbnail_data.get("thumbnail_url")
                
        # Special handling for prompt_id
        if "prompt_id" in update_data and update_data["prompt_id"] == "":
            # Convert empty string to None to use default prompt
            update_data["prompt_id"] = None

        # Update topic
        for key, value in update_data.items():
            setattr(topic, key, value)

        # Save updated topic
        updated_topic = update_topic(topic_id, update_data)
        info("TOPIC", "Updated", topic.name)
        return updated_topic
    except Exception as e:
        error("TOPIC", "Update error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/topics/{topic_id}/publish",
    response_model=dict,
    summary="Publish Topic",
    description="Publishes a topic's content to its configured destinations",
    response_description="Confirmation message that publishing has been scheduled",
    responses={
        404: {"description": "Topic not found"},
        500: {"description": "Internal server error"},
    },
)
async def publish_topic_route(topic_id: str, background_tasks: BackgroundTasks):
    """Publish a topic to its configured destinations."""
    try:
        topic = get_topic(topic_id)
        if not topic:
            error("TOPIC", "Not found", f"ID: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")

        background_tasks.add_task(request_topic_publish, topic)
        debug("TOPIC", "Publishing scheduled", topic.name)
        return {"message": f"Publishing scheduled for topic {topic_id}"}
    except Exception as e:
        error("TOPIC", "Publishing error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/topics/{topic_id}/workflow",
    summary="Get Workflow Visualization",
    description="Generates and returns a visualization of the curator workflow for a topic",
    responses={
        404: {"description": "Topic not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_workflow_visualization(topic_id: str, format: str = "png"):
    """
    Generate and return a visualization of the curator workflow for a topic.
    
    Args:
        topic_id: The ID of the topic
        format: The format of the visualization (png or md)
    
    Returns:
        The visualization file
    """
    try:
        # Get the topic location
        project_slug, topic_slug = get_topic_location(topic_id)
        if not project_slug or not topic_slug:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Get the topic path
        topic_path = get_topic_path(project_slug, topic_slug)
        if not topic_path:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Create the graph
        graph = create_curator_graph()
        
        # Generate the visualization
        if format == "png":
            # Generate and save the PNG visualization
            png_data = graph.get_graph().draw_mermaid_png()
            png_file = topic_path / "workflow.png"
            with open(png_file, "wb") as f:
                f.write(png_data)
            return FileResponse(png_file, media_type="image/png")
        elif format == "md":
            # Generate and save the Mermaid diagram
            mermaid_diagram = graph.get_graph().draw_mermaid()
            md_file = topic_path / "workflow.md"
            with open(md_file, "w", encoding="utf-8") as f:
                f.write("```mermaid\n")
                f.write(mermaid_diagram)
                f.write("\n```")
            return FileResponse(md_file, media_type="text/markdown")
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'png' or 'md'")

    except Exception as e:
        error("TOPIC", "Failed to generate workflow visualization", str(e))
        raise HTTPException(status_code=500, detail=str(e))
