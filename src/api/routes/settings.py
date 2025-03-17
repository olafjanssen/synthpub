import os
import sys
from pathlib import Path
from typing import Dict, Optional

import webview
import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
SETTINGS_FILE = "settings.yaml"


class LLMTaskSettings(BaseModel):
    provider: str
    model_name: str
    max_tokens: int
    model_config = {"protected_namespaces": ()}  # Disable protected namespace checks


class LLMSettings(BaseModel):
    settings: Dict[str, LLMTaskSettings]


def load_settings():
    """Load settings from YAML file"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_settings(settings):
    """Save settings to YAML file"""
    # Convert any Path objects to strings before saving
    serializable_settings = {}
    for key, value in settings.items():
        if isinstance(value, Path):
            serializable_settings[key] = str(value)
        elif isinstance(value, dict):
            serializable_settings[key] = value
        else:
            serializable_settings[key] = str(value)

    with open(SETTINGS_FILE, "w") as f:
        yaml.safe_dump(serializable_settings, f, sort_keys=False, allow_unicode=True)


@router.get("/settings/db-path")
async def get_db_path():
    """Get the database path"""
    # Check if running in desktop environment
    is_desktop = "webview" in sys.modules and len(webview.windows) > 0

    # Don't return the actual path in web environment for security
    if not is_desktop:
        return {"path": "Path only available in desktop application"}

    settings = load_settings()
    return {"path": settings.get("db_path", "")}


@router.post("/settings/select-folder")
async def select_folder():
    """Open folder selection dialog using PyWebView"""
    # Check if running in desktop environment
    is_desktop = "webview" in sys.modules and len(webview.windows) > 0

    if not is_desktop:
        raise HTTPException(
            status_code=403,
            detail="Folder selection is only available in desktop application mode",
        )

    window = webview.windows[0]
    result = window.create_file_dialog(
        webview.FOLDER_DIALOG, directory="", allow_multiple=False
    )

    if result and len(result) > 0:
        folder_path = result[0]
        settings = load_settings()
        settings["db_path"] = folder_path
        save_settings(settings)
        return {"path": folder_path}

    raise HTTPException(status_code=400, detail="No folder selected")


@router.get("/settings/env-vars")
async def get_env_vars():
    """Get environment variables"""
    # Check if running in desktop environment
    is_desktop = "webview" in sys.modules and len(webview.windows) > 0

    settings = load_settings()

    # Only return real values in desktop environment
    if not is_desktop:
        # Return masked values for security
        env_vars = settings.get("env_vars", {})
        masked_vars = {
            key: "********" if value else "" for key, value in env_vars.items()
        }
        return {"variables": masked_vars}

    return {
        "variables": settings.get(
            "env_vars",
            {
                "OPENAI_API_KEY": "",
                "MISTRAL_API_KEY": "",
                "YOUTUBE_API_KEY": "",
                "GITLAB_TOKEN": "",
                "FTP_USERNAME": "",
                "FTP_PASSWORD": "",
            },
        )
    }


@router.post("/settings/env-vars")
async def update_env_vars(variables: Dict[str, str]):
    """Update environment variables"""
    # Check if running in desktop environment
    is_desktop = "webview" in sys.modules and len(webview.windows) > 0

    if not is_desktop:
        raise HTTPException(
            status_code=403,
            detail="Environment variables can only be updated in desktop application",
        )

    settings = load_settings()
    settings["env_vars"] = variables
    save_settings(settings)
    return {"status": "success"}


@router.get("/settings/llm")
async def get_llm_settings():
    """Get LLM settings"""
    # Check if running in desktop environment
    is_desktop = "webview" in sys.modules and len(webview.windows) > 0

    settings = load_settings()
    llm_settings = settings.get("llm_settings", {})

    # If not in desktop environment, mask potentially sensitive model names
    if not is_desktop and llm_settings:
        masked_settings = {}
        for task, task_settings in llm_settings.items():
            # Create a copy of the settings with masked model name
            masked_task_settings = task_settings.copy()
            # Model names could contain API keys or endpoints, so mask them
            if (
                "model_name" in masked_task_settings
                and masked_task_settings["model_name"]
            ):
                masked_task_settings["model_name"] = "********"
            masked_settings[task] = masked_task_settings

        return {"settings": masked_settings}

    # Default LLM settings if none exist yet
    if not llm_settings:
        llm_settings = {
            "article_generation": {
                "provider": "openai",
                "model_name": "gpt-4-1106-preview",
                "max_tokens": 4000,
            },
            "article_refinement": {
                "provider": "openai",
                "model_name": "gpt-4-1106-preview",
                "max_tokens": 4000,
            },
        }

    return {"settings": llm_settings}


@router.post("/settings/llm")
async def update_llm_settings(llm_settings: LLMSettings):
    """Update LLM settings"""
    # Check if running in desktop environment
    is_desktop = "webview" in sys.modules and len(webview.windows) > 0

    if not is_desktop:
        raise HTTPException(
            status_code=403,
            detail="LLM settings can only be updated in desktop application",
        )

    settings = load_settings()
    settings["llm_settings"] = {
        task: task_settings.dict()
        for task, task_settings in llm_settings.settings.items()
    }
    save_settings(settings)
    return {"status": "success"}


@router.get("/settings/environment")
async def get_environment():
    """Check if running in desktop or browser environment"""
    # PyWebView will be available in desktop environment
    is_desktop = "webview" in sys.modules and len(webview.windows) > 0
    return {"is_desktop": is_desktop}


class SchedulerSettings(BaseModel):
    enabled: bool
    update_interval_minutes: int
    update_threshold_hours: int


@router.get("/settings/scheduler")
async def get_scheduler_settings():
    """Get scheduler settings"""
    settings = load_settings()
    scheduler_settings = settings.get(
        "scheduler",
        {"enabled": True, "update_interval_minutes": 15, "update_threshold_hours": 1},
    )
    return {"settings": scheduler_settings}


@router.post("/settings/scheduler")
async def update_scheduler_settings(scheduler_settings: SchedulerSettings):
    """Update scheduler settings"""
    # Check if running in desktop environment
    is_desktop = "webview" in sys.modules and len(webview.windows) > 0

    if not is_desktop:
        raise HTTPException(
            status_code=403,
            detail="Scheduler settings can only be updated in desktop application",
        )

    # Get current settings to check if enabled state is changing
    current_settings = load_settings()
    current_enabled = current_settings.get("scheduler", {}).get("enabled", False)

    # Save the new settings
    settings = load_settings()
    settings["scheduler"] = scheduler_settings.model_dump()
    save_settings(settings)

    # Update the scheduler based on settings changes
    try:
        from news.news_scheduler import start_scheduler_thread, stop_scheduler_thread

        # Always stop and restart the scheduler to apply new settings
        stop_scheduler_thread()

        # Restart the scheduler with new settings
        start_scheduler_thread()
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error updating scheduler: {e}")
    return {"status": "success"}
