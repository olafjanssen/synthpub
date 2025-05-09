"""Prompt-related API routes."""

from typing import List

from fastapi import APIRouter, HTTPException

from api.db.prompt_db import get_prompt, list_prompts
from api.models.prompt import Prompt
from utils.logging import debug, error

router = APIRouter()


@router.get(
    "/prompts",
    response_model=List[Prompt],
    summary="List Prompts",
    description="Returns a list of all available prompts for article generation",
    response_description="Array of all prompts with their details",
)
async def list_prompts_route():
    """List all prompts."""
    debug("PROMPT", "List requested", "Getting all prompts")
    return list_prompts()


@router.get(
    "/prompts/{prompt_id}",
    response_model=Prompt,
    summary="Get Prompt",
    description="Returns details of a specific prompt",
    response_description="The prompt with the specified ID",
    responses={404: {"description": "Prompt not found"}},
)
async def get_prompt_route(prompt_id: str):
    """Get a specific prompt by ID."""
    prompt = get_prompt(prompt_id)
    if not prompt:
        error("PROMPT", "Not found", f"ID: {prompt_id}")
        raise HTTPException(status_code=404, detail="Prompt not found")
    debug("PROMPT", "Retrieved", f"ID: {prompt_id}")
    return prompt
