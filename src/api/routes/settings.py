from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import tomli
import tomli_w
import webview

router = APIRouter()
SETTINGS_FILE = "settings.toml"

class DbPath(BaseModel):
    path: str

def load_settings():
    """Load settings from TOML file"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'rb') as f:
            return tomli.load(f)
    return {"db_path": ""}

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
