"""
Logging module for SynthPub using loguru.

This module provides two main types of logging:
1. System logging - for debugging and system operations (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. User logging - for displaying to end users in the web interface (USER_INFO, USER_WARNING, USER_ERROR)
"""
import os
import sys
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from loguru import logger
from blinker import signal

# Try to import from api.signals if available, otherwise create a new signal
try:
    from api.signals import log_event
except ImportError:
    # Create signal for log events
    log_event = signal('log-event')

# Custom log levels for user-facing logs
USER_INFO = 25     # Between INFO and WARNING
USER_WARNING = 35  # Between WARNING and ERROR
USER_ERROR = 45    # Between ERROR and CRITICAL

# Define log level names
logger.level("USER_INFO", no=USER_INFO, color="<blue>", icon="🔵")
logger.level("USER_WARNING", no=USER_WARNING, color="<yellow>", icon="🟡")
logger.level("USER_ERROR", no=USER_ERROR, color="<red>", icon="🔴")

# Configure system log file
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Remove default logger
logger.remove()

# Add console logger for development
logger.add(sys.stderr, level="INFO")

# Add file logger for system logs with rotation
logger.add(
    str(log_dir / "system.log"), 
    rotation="10 MB", 
    retention="1 week", 
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Add file logger for user logs with rotation
logger.add(
    str(log_dir / "user.log"), 
    rotation="10 MB", 
    retention="1 week", 
    level="USER_INFO",
    filter=lambda record: record["level"].no >= USER_INFO,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Print initialization message
print(f"Logging system initialized with custom levels: USER_INFO={USER_INFO}, USER_WARNING={USER_WARNING}, USER_ERROR={USER_ERROR}")
print(f"Log files will be stored in: {log_dir.absolute()}")

# Store recent logs in memory for quick retrieval
MAX_LOGS = 100
recent_logs: List[Dict[str, Any]] = []

def format_log_entry(record: Dict[str, Any]) -> Dict[str, Any]:
    """Format a log record for the web interface."""
    return {
        "timestamp": datetime.now().isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "level_no": record["level"].no
    }

def log_with_signal(level: str, message: str, **kwargs) -> None:
    """Log a message and emit a signal for real-time updates."""
    # Get the log level number
    level_no = logger.level(level).no
    
    # Log the message using loguru
    logger.log(level, message, **kwargs)
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "level_no": level_no,
        "extra": kwargs
    }
    
    # Store in recent logs
    recent_logs.append(log_entry)
    if len(recent_logs) > MAX_LOGS:
        recent_logs.pop(0)
    
    # Emit signal for WebSocket - sending all user-facing logs
    if level_no >= USER_INFO:  # Only emit signal for user-facing logs
        # Send log entry to all handlers
        log_event.send(log_entry=log_entry)  # Use 'log_entry' as a named parameter

# Define convenience functions for logging
def debug(message: str, **kwargs) -> None:
    """Log a debug message (system only)."""
    log_with_signal("DEBUG", message, **kwargs)

def info(message: str, **kwargs) -> None:
    """Log an info message (system only)."""
    log_with_signal("INFO", message, **kwargs)

def warning(message: str, **kwargs) -> None:
    """Log a warning message (system only)."""
    log_with_signal("WARNING", message, **kwargs)

def error(message: str, **kwargs) -> None:
    """Log an error message (system only)."""
    log_with_signal("ERROR", message, **kwargs)

def critical(message: str, **kwargs) -> None:
    """Log a critical message (system only)."""
    log_with_signal("CRITICAL", message, **kwargs)

def user_info(message: str, **kwargs) -> None:
    """Log a user-facing info message."""
    log_with_signal("USER_INFO", message, **kwargs)

def user_warning(message: str, **kwargs) -> None:
    """Log a user-facing warning message."""
    log_with_signal("USER_WARNING", message, **kwargs)

def user_error(message: str, **kwargs) -> None:
    """Log a user-facing error message."""
    log_with_signal("USER_ERROR", message, **kwargs)

def get_recent_logs(min_level: int = 0) -> List[Dict[str, Any]]:
    """Get recent logs, optionally filtered by minimum level."""
    return [log for log in recent_logs if log["level_no"] >= min_level]

def get_user_logs() -> List[Dict[str, Any]]:
    """Get recent user-facing logs."""
    return get_recent_logs(min_level=USER_INFO) 