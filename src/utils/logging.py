"""
Logging module for SynthPub using loguru.

A unified logging approach that provides clear, structured logs for both
developers and users without unnecessary duplication.
"""
import sys
from datetime import datetime
from typing import Any, Dict, List

from loguru import logger

from api.db.common import get_db_path
from api.routes.log_routes import handle_log


def db_path():
    return get_db_path('logs')

# Configure log directory in the database folder
db_path().mkdir(exist_ok=True, parents=True)

# Remove default logger
logger.remove()

# Add console logger for development
logger.add(sys.stderr, level="DEBUG", 
          format="<level>{level}</level> | <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>")

# Add file logger with rotation
logger.add(
    str(db_path() / "synthpub.log"), 
    rotation="10 MB", 
    retention="1 week", 
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Print initialization message
logger.info("Logging system initialized")

# Store recent logs in memory for quick retrieval
MAX_LOGS = 200
recent_logs: List[Dict[str, Any]] = []

def log(component: str, action: str, detail: str = "", level: str = "INFO", **kwargs) -> None:
    """
    Log a message with a consistent format.
    
    Args:
        component: The system component (e.g., TOPIC, ARTICLE)
        action: The action being performed (e.g., Created, Updated)
        detail: Additional details about the action
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        **kwargs: Additional data to store with the log
    """
    # Create message with consistent format
    message = f"{component} - {action}"
    if detail:
        message += f": {detail}"
    
    # Log using loguru
    logger.log(level, message)
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "component": component,
        "action": action,
        "detail": detail,
        "message": message,
        "extra": kwargs
    }
    
    # Store in recent logs
    recent_logs.append(log_entry)
    if len(recent_logs) > MAX_LOGS:
        recent_logs.pop(0)
    
    # Emit WebSocket message
    handle_log(log_entry)

# Convenience functions
def debug(component: str, action: str, detail: str = "", **kwargs) -> None:
    """Log a debug message."""
    log(component, action, detail, "DEBUG", **kwargs)

def info(component: str, action: str, detail: str = "", **kwargs) -> None:
    """Log an info message."""
    log(component, action, detail, "INFO", **kwargs)

def warning(component: str, action: str, detail: str = "", **kwargs) -> None:
    """Log a warning message."""
    log(component, action, detail, "WARNING", **kwargs)

def error(component: str, action: str, detail: str = "", **kwargs) -> None:
    """Log an error message."""
    log(component, action, detail, "ERROR", **kwargs)

def critical(component: str, action: str, detail: str = "", **kwargs) -> None:
    """Log a critical message."""
    log(component, action, detail, "CRITICAL", **kwargs)

# Function to get recent logs
def get_recent_logs(min_level: str = "DEBUG", max_count: int = 100) -> List[Dict[str, Any]]:
    """Get recent logs, optionally filtered by minimum level."""
    logs = [log for log in recent_logs if logger.level(log["level"]).no >= logger.level(min_level).no]
    return logs[-max_count:] if max_count > 0 else logs 