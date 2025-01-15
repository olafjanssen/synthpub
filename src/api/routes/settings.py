from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import tomli
import tomli_w
import webview
from typing import Dict

router = APIRouter()
SETTINGS_FILE = "settings.toml"

class DbPath(BaseModel):
    path: str

class EnvVars(BaseModel):
    variables: Dict[str, str]

def get_default_env_vars():
    """Get default environment variables"""
    return {
        "OPENAI_API_KEY": "",
        "YOUTUBE_API_KEY": "", 
        "GITLAB_TOKEN": ""
    }

def load_settings():
    """Load settings from TOML file"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'rb') as f:
            settings = tomli.load(f)
            # Ensure all env vars exist
            default_vars = get_default_env_vars()
            if "env_vars" not in settings:
                settings["env_vars"] = default_vars
            else:
                for key in default_vars:
                    if key not in settings["env_vars"]:
                        settings["env_vars"][key] = default_vars[key]
            return settings
    return {
        "db_path": "",
        "env_vars": get_default_env_vars()
    }

def save_settings(settings):
    """Save settings to TOML file"""
    with open(SETTINGS_FILE, 'wb') as f:
        tomli_w.dump(settings, f)

@router.get("/api/settings/db-path")
async def get_db_path():
    """Get current database path"""
    settings = load_settings()
    return {"path": settings.get("db_path", "")}

@router.post("/api/settings/select-folder")
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

@router.get("/api/settings/env-vars")
async def get_env_vars():
    """Get current environment variables"""
    settings = load_settings()
    return {"variables": settings.get("env_vars", get_default_env_vars())}

@router.post("/api/settings/env-vars")
async def update_env_vars(env_vars: EnvVars):
    """Update environment variables"""
    settings = load_settings()
    # Ensure all default keys exist
    default_vars = get_default_env_vars()
    for key in default_vars:
        if key not in env_vars.variables:
            env_vars.variables[key] = default_vars[key]
            
    settings["env_vars"] = env_vars.variables
    save_settings(settings)
    
    # Update current process environment variables
    for key, value in env_vars.variables.items():
        os.environ[key] = value
        
    return {"status": "success"}
