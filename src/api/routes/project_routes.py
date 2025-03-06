"""Project-related API routes."""
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from typing import List

from api.models.project import Project, ProjectCreate, ProjectUpdate
from api.db.project_db import (
    create_project,
    get_project,
    list_projects,
    update_project,
    mark_project_deleted,
    add_topic_to_project,
    remove_topic_from_project
)
from services.pexels_service import get_random_thumbnail

router = APIRouter()

@router.post("/projects/", response_model=Project)
async def create_project_route(project: ProjectCreate):
    """Create a new project."""
    try:
        # Get thumbnail from Pexels
        search_text = f"{project.title} {project.description}"
        thumbnail_data = get_random_thumbnail(search_text)
        
        project_data = create_project(
            title=project.title,
            description=project.description,
            topic_ids=project.topic_ids,
            thumbnail_url=thumbnail_data.get("thumbnail_url")
        )
        return project_data
    except Exception as e:
        print(f"Error creating project: {str(e)}")
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
        
        updated_project = update_project(project_id, updated_data)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        return updated_project
        
    except Exception as e:
        print(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/projects/{project_id}")
async def delete_project_route(project_id: str):
    """Mark a project as deleted (soft delete)."""
    try:
        success = mark_project_deleted(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
            
        return {"message": "Project deleted successfully"}
        
    except Exception as e:
        print(f"Error deleting project: {str(e)}")
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