"""
Simple model for prompts.
"""

from pydantic import BaseModel


class Prompt(BaseModel):
    """Simple model for a template prompt used in content conversion."""

    id: str
    name: str
    template: str
