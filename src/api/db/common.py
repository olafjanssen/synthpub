"""Common database utilities."""
import os
from pathlib import Path
from ..routes.settings import load_settings

def get_base_db_path() -> Path:
    """Get the base database path from settings or fallback to default."""
    settings = load_settings()
    return Path(settings.get("db_path") or os.getenv("DB_PATH", "../db"))

def get_db_path(subfolder: str) -> Path:
    """Get database path for a specific subfolder."""
    return get_base_db_path() / subfolder

