"""
Simple database operations for prompts using plain Markdown files.
"""
from pathlib import Path
from typing import Dict, Optional, List
from api.models import Prompt
from .common import get_db_path
from utils.logging import error, debug

# In-memory cache for prompts
_prompt_cache: Dict[str, Prompt] = {}
_cache_initialized = False

def _ensure_cache():
    """Initialize cache if not already done."""
    global _cache_initialized
    if not _cache_initialized:
        prompts = _load_all_prompts_from_disk()
        _prompt_cache.update({prompt.id: prompt for prompt in prompts})
        _cache_initialized = True

def _load_all_prompts_from_disk() -> List[Prompt]:
    """Internal function to load prompts directly from disk."""
    ensure_db_exists()
    prompts = []
    for file in DB_PATH().glob("*.md"):
        try:
            # Use the filename as the ID and name
            prompt_id = file.stem
            # Read the file content as the template
            template = file.read_text(encoding="utf-8")
            # Create a simple prompt object
            prompts.append(Prompt(
                id=prompt_id,
                name=prompt_id.replace('-', ' ').title(),
                template=template
            ))
        except Exception as e:
            error("PROMPT_DB", "Loading prompt failed", f"File: {file.name}, Error: {str(e)}")
    return prompts

def DB_PATH():
    """Get the path to the prompts database directory."""
    return get_db_path('prompts')

def ensure_db_exists():
    """Create the prompts directory if it doesn't exist."""
    DB_PATH().mkdir(parents=True, exist_ok=True)

def get_prompt(prompt_id: str) -> Optional[Prompt]:
    """Retrieve prompt by id from cache."""
    _ensure_cache()
    return _prompt_cache.get(prompt_id)

def list_prompts() -> List[Prompt]:
    """List all prompts from cache."""
    _ensure_cache()
    return list(_prompt_cache.values()) 