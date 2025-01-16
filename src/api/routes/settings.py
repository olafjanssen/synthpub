from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import tomli
import tomli_w
import webview
from typing import Dict, Optional

router = APIRouter()
SETTINGS_FILE = "settings.toml"

class DbPath(BaseModel):
    path: str

class EnvVars(BaseModel):
    variables: Dict[str, str]

class LLMTaskSettings(BaseModel):
    provider: str
    model_name: str
    max_tokens: int

class LLMSettings(BaseModel):
    settings: Dict[str, LLMTaskSettings]

def get_default_env_vars():
    """Get default environment variables"""
    return {
        "OPENAI_API_KEY": "",
        "MISTRAL_API_KEY": "",
        "YOUTUBE_API_KEY": "", 
        "GITLAB_TOKEN": ""
    }

def get_default_llm_settings():
    """Get default LLM settings"""
    return {
        "article_generation": {
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "max_tokens": 800
        },
        "article_refinement": {
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "max_tokens": 800
        }
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

            # Ensure all LLM settings exist
            default_llm = get_default_llm_settings()
            if "llm" not in settings:
                settings["llm"] = default_llm
            else:
                for task in default_llm:
                    if task not in settings["llm"]:
                        settings["llm"][task] = default_llm[task]
                    else:
                        for key in default_llm[task]:
                            if key not in settings["llm"][task]:
                                settings["llm"][task][key] = default_llm[task][key]
            return settings
    return {
        "db_path": "",
        "env_vars": get_default_env_vars(),
        "llm": get_default_llm_settings()
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

@router.get("/api/settings/llm")
async def get_llm_settings():
    """Get current LLM settings"""
    settings = load_settings()
    return {"settings": settings.get("llm", get_default_llm_settings())}

@router.post("/api/settings/llm")
async def update_llm_settings(llm_settings: LLMSettings):
    """Update LLM settings"""
    settings = load_settings()
    settings["llm"] = {
        task: task_settings.dict()
        for task, task_settings in llm_settings.settings.items()
    }
    save_settings(settings)
    return {"status": "success"}
