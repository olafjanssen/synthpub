from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import os
import yaml
import webview
from pathlib import Path

router = APIRouter()
SETTINGS_FILE = "settings.yaml"

class LLMTaskSettings(BaseModel):
    provider: str
    model_name: str
    max_tokens: int

class LLMSettings(BaseModel):
    settings: Dict[str, LLMTaskSettings]

def load_settings():
    """Load settings from YAML file"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
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

    with open(SETTINGS_FILE, 'w') as f:
        yaml.safe_dump(serializable_settings, f, sort_keys=False, allow_unicode=True)

@router.get("/settings/db-path")
async def get_db_path():
    """Get current database path"""
    settings = load_settings()
    return {"path": settings.get("db_path", "")}

@router.post("/settings/select-folder")
async def select_folder():
    """Open folder selection dialog using PyWebView"""
    window = webview.windows[0]
    result = window.create_file_dialog(
        webview.FOLDER_DIALOG,
        directory='',
        allow_multiple=False
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
    settings = load_settings()
    return {"variables": settings.get("env_vars", {
        "OPENAI_API_KEY": "",
        "MISTRAL_API_KEY": "",
        "YOUTUBE_API_KEY": "", 
        "GITLAB_TOKEN": ""
    })}

@router.post("/settings/env-vars")
async def update_env_vars(variables: Dict[str, str]):
    """Update environment variables"""
    settings = load_settings()
    settings["env_vars"] = variables
    save_settings(settings)
    return {"status": "success"}

@router.get("/settings/llm")
async def get_llm_settings():
    """Get LLM settings"""
    settings = load_settings()
    return {"settings": settings.get("llm", {
        "article_generation": {
            "provider": "openai",
            "model_name": "gpt-4",
            "max_tokens": 800
        },
        "article_refinement": {
            "provider": "openai",
            "model_name": "gpt-4",
            "max_tokens": 800
        }
    })}

@router.post("/settings/llm")
async def update_llm_settings(llm_settings: LLMSettings):
    """Update LLM settings"""
    settings = load_settings()
    settings["llm"] = {
        task: task_settings.dict()
        for task, task_settings in llm_settings.settings.items()
    }
    save_settings(settings)
    return {"status": "success"}
