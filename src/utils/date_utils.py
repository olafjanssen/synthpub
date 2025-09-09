"""
Date and time utilities for the SynthPub application.

This module provides utilities for formatting dates and times
for use in LLM prompts and other contexts.
"""

from datetime import datetime
from typing import Dict, Optional


def get_current_datetime_context() -> Dict[str, str]:
    """
    Get current date and time information formatted for LLM context.
    
    Returns:
        Dictionary with formatted date/time information
    """
    now = datetime.now()
    utc_now = datetime.utcnow()
    
    return {
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M:%S"),
        "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "current_date_readable": now.strftime("%B %d, %Y"),
        "current_datetime_readable": now.strftime("%B %d, %Y at %H:%M:%S"),
        "current_year": str(now.year),
        "current_month": now.strftime("%B"),
        "current_day": now.strftime("%A"),
        "utc_date": utc_now.strftime("%Y-%m-%d"),
        "utc_time": utc_now.strftime("%H:%M:%S"),
        "utc_datetime": utc_now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": now.strftime("%Z") or "Local Time"
    }


def format_datetime_context_for_prompt(
    context: Optional[Dict[str, str]] = None,
    include_timezone: bool = True
) -> str:
    """
    Format date/time context for inclusion in LLM prompts.
    
    Args:
        context: Optional pre-computed date/time context
        include_timezone: Whether to include timezone information
        
    Returns:
        Formatted string for prompt inclusion
    """
    if context is None:
        context = get_current_datetime_context()
    
    parts = [
        f"**Current Date:** {context['current_date_readable']}",
        f"**Current Time:** {context['current_time']}",
        f"**Current DateTime:** {context['current_datetime_readable']}"
    ]
    
    if include_timezone and context.get('timezone'):
        parts.append(f"**Timezone:** {context['timezone']}")
    
    return "\n".join(parts)


def get_relative_time_context(
    target_date: str,
    context: Optional[Dict[str, str]] = None
) -> str:
    """
    Get relative time context (past/future) for a target date.
    
    Args:
        target_date: Target date in YYYY-MM-DD format
        context: Optional pre-computed date/time context
        
    Returns:
        Relative time description
    """
    if context is None:
        context = get_current_datetime_context()
    
    current_date = context['current_date']
    
    if target_date > current_date:
        return f"**Future Event:** {target_date} (after current date {current_date})"
    elif target_date < current_date:
        return f"**Past Event:** {target_date} (before current date {current_date})"
    else:
        return f"**Today's Event:** {target_date} (current date {current_date})"
