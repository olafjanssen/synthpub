"""Project-related API routes."""
from typing import List

from fastapi import APIRouter, HTTPException

from api.db.project_db import (
    add_topic_to_project,
    create_project,
    get_project,
    list_projects,
    mark_project_deleted,
    remove_topic_from_project,
    update_project,
)
from api.models.project import Project, ProjectCreate, ProjectUpdate
from services.pexels_service import get_random_thumbnail
from utils.logging import error, warning

router = APIRouter()

@router.post("/projects/", response_model=Project)
async def create_project_route(project: ProjectCreate):
    """Create a new project."""
    try:
        # Check if we should generate a thumbnail
        thumbnail_url = project.thumbnail_url
        
        # Generate a thumbnail if:
        # 1. Field is None (not provided in request)
        # 2. Field is an empty string (user left the field blank)
        # 3. Field is "auto" or "none" (explicit request for auto-generation)
        should_generate = (
            thumbnail_url is None or 
            (isinstance(thumbnail_url, str) and (
                thumbnail_url.strip() == "" or
                thumbnail_url.lower().strip() in ["auto", "none"]
            ))
        )
        
        if should_generate:
            search_text = f"{project.title} {project.description}"
            thumbnail_data = get_random_thumbnail(search_text)
            thumbnail_url = thumbnail_data.get("thumbnail_url")
        
        # At this point thumbnail_url is either:
        # - A URL from Pexels (if auto-generated)
        # - A custom URL provided by the user (if not auto-generated)
        # - None if thumbnail generation failed
        
        project_data = create_project(
            title=project.title,
            description=project.description,
            topic_ids=project.topic_ids,
            thumbnail_url=thumbnail_url
        )
        return project_data
    except Exception as e:
        error("PROJECT", "Creation error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/projects/", response_model=List[Project])
async def list_projects_route():
    """List all projects."""
    return list_projects()

@router.get("/projects/{project_id}", response_model=Project)
async def get_project_route(project_id: str):
    """Get a specific project by ID."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/projects/{project_id}", response_model=Project)
async def update_project_route(project_id: str, project_update: ProjectUpdate):
    """Update a project's details."""
    try:
        # Update project with non-null values
        updated_data = {
            k: v for k, v in project_update.model_dump().items() 
            if v is not None
        }
        
        # Special handling for thumbnail_url
        if hasattr(project_update, 'thumbnail_url') and project_update.thumbnail_url is not None:
            thumbnail_url = project_update.thumbnail_url.strip()
            
            # Check if we should generate a new thumbnail
            if thumbnail_url == "" or thumbnail_url.lower() in ["auto", "none"]:
                search_text = f"{project_update.title or ''} {project_update.description or ''}"
                
                # If title and description aren't being updated, get them from the existing project
                if not search_text.strip():
                    existing_project = get_project(project_id)
                    if existing_project:
                        search_text = f"{existing_project.title} {existing_project.description}"
                
                thumbnail_data = get_random_thumbnail(search_text)
                updated_data['thumbnail_url'] = thumbnail_data.get("thumbnail_url")
            else:
                # Use the provided URL
                updated_data['thumbnail_url'] = thumbnail_url
        
        updated_project = update_project(project_id, updated_data)
        
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found or update failed")
        
        return updated_project
    except Exception as e:
        error("PROJECT", "Update error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/projects/{project_id}")
async def delete_project_route(project_id: str):
    """Mark a project and all its associated topics as deleted (soft delete)."""
    try:
        # First get the project to retrieve its topics
        project = get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        # Mark all associated topics as deleted
        from api.db.topic_db import mark_topic_deleted
        
        for topic_id in project.topic_ids:
            try:
                mark_topic_deleted(topic_id)
            except Exception as e:
                warning("PROJECT", "Topic deletion error", f"ID: {topic_id}, Error: {str(e)}")
                # Continue with other topics even if one fails
                
        # Then delete the project itself
        success = mark_project_deleted(project_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete project")
            
        return {"message": "Project and its topics deleted successfully"}
        
    except Exception as e:
        error("PROJECT", "Deletion error", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/projects/{project_id}/topics/{topic_id}", response_model=Project)
async def add_topic_route(project_id: str, topic_id: str):
    """Add a topic to a project."""
    updated_project = add_topic_to_project(project_id, topic_id)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@router.delete("/projects/{project_id}/topics/{topic_id}", response_model=Project)
async def remove_topic_route(project_id: str, topic_id: str):
    """Remove a topic from a project."""
    updated_project = remove_topic_from_project(project_id, topic_id)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project 