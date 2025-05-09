"""Utility functions shared by multiple publishers."""

import re
from datetime import datetime

from utils.logging import debug


def process_filename_template(filename: str, publisher: str = "PUBLISHER") -> str:
    """
    Process a filename template by replacing placeholders with dynamic values.

    Currently supported placeholders:
    - {date} - Current date in YYYY-MM-DD format
    - {time} - Current time in HHMMSS format
    - {datetime} - Current date and time in YYYYMMDD_HHMMSS format
    - {year} - Current year (YYYY)
    - {month} - Current month (MM)
    - {day} - Current day (DD)

    Args:
        filename: The filename template with potential placeholders
        publisher: The name of the publisher for logging purposes

    Returns:
        Processed filename with placeholders replaced by actual values
    """
    if not re.search(r"{.*?}", filename):
        return filename

    now = datetime.now()

    # Define template replacements
    replacements = {
        "{date}": now.strftime("%Y-%m-%d"),
        "{time}": now.strftime("%H%M%S"),
        "{datetime}": now.strftime("%Y%m%d_%H%M%S"),
        "{year}": now.strftime("%Y"),
        "{month}": now.strftime("%m"),
        "{day}": now.strftime("%d"),
    }

    # Apply template replacements
    processed_filename = filename
    for token, value in replacements.items():
        processed_filename = processed_filename.replace(token, value)

    debug(
        publisher,
        "Filename template processed",
        f"Original: {filename}, Processed: {processed_filename}",
    )
    return processed_filename
