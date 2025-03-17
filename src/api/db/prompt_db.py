"""
Simple database operations for prompts using plain Markdown files.
"""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from api.models import Prompt
from utils.logging import debug, error, info

from .common import get_db_path

# In-memory cache for prompts
_prompt_cache: Dict[str, Prompt] = {}
_cache_initialized = False

def _ensure_cache():
    """Initialize cache if not already done."""
    global _cache_initialized
    if not _cache_initialized:
        ensure_db_exists()
        _copy_default_prompts()
        prompts = _load_all_prompts_from_disk()
        _prompt_cache.update({prompt.id: prompt for prompt in prompts})
        _cache_initialized = True

def _copy_default_prompts():
    """Copy default prompts from resources/prompts to DB_PATH/prompts if they don't exist."""
    try:
        # Get the resources directory (assuming it's at project root or src level)
        resources_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "resources" / "prompts"
        # If resources/prompts doesn't exist, try one level up
        if not resources_path.exists():
            resources_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / "resources" / "prompts"
        
        if not resources_path.exists():
            debug("PROMPT_DB", "Default prompts not found", f"Path: {resources_path}")
            return
        
        # Get destination path
        dest_path = DB_PATH()
        
        # Copy each file if it doesn't exist in destination
        count = 0
        for src_file in resources_path.glob("*.md"):
            dest_file = dest_path / src_file.name
            if not dest_file.exists():
                shutil.copy2(src_file, dest_file)
                count += 1
                debug("PROMPT_DB", "Copied default prompt", f"File: {src_file.name}")
        
        if count > 0:
            info("PROMPT_DB", "Default prompts initialized", f"Copied {count} prompts")
    
    except Exception as e:
        error("PROMPT_DB", "Failed to copy default prompts", f"Error: {str(e)}")

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