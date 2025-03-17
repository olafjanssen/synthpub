"""
File system connector for processing local files using glob patterns.
"""

import glob
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import unquote, urlparse

from utils.logging import error, warning

from .feed_connector import FeedConnector


def parse_file_url(url: str) -> str:
    """
    Parse a file:// URL and return the filesystem path with glob pattern.

    Args:
        url: file:// URL (e.g., file:///path/to/*.md)

    Returns:
        Decoded filesystem path
    """
    # Remove file:// prefix and decode URL encoding
    if not url.startswith("file://"):
        raise ValueError("URL must start with file://")

    path = url[7:]  # Remove file://
    return unquote(path)  # Handle URL encoding


def read_text_file(path: str) -> str:
    """
    Read content from a text file.

    Args:
        path: Path to the text file

    Returns:
        File content as string
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _get_glob_pattern(path_pattern: str) -> str:
    """Get the glob pattern for file search."""
    if Path(path_pattern).is_absolute():
        return path_pattern
    return str(Path.cwd() / path_pattern)


def _process_file(file_path: Path) -> Optional[Dict[str, str]]:
    """Process a single file and return its content."""
    try:
        content = read_text_file(str(file_path))
        return {
            "url": f"file://{file_path}",
            "content": content,
            "needs_further_processing": False,
        }
    except Exception as e:
        error("FILE", "File processing failed", f"File: {file_path}, Error: {str(e)}")
        return None


def fetch_files(url: str) -> List[Dict[str, str]]:
    """Fetch content from files matching the glob pattern."""
    path_pattern = parse_file_url(url)
    results = []

    # Get the glob pattern
    glob_pattern = _get_glob_pattern(path_pattern)

    # Check if this is a glob pattern or a specific file
    is_glob_pattern = "*" in path_pattern or "?" in path_pattern

    try:
        if is_glob_pattern:
            # Handle glob pattern
            for file_path in sorted(Path().glob(glob_pattern)):
                if file_path.is_file():
                    result = _process_file(file_path)
                    if result:
                        results.append(result)
        else:
            # Handle single file
            file_path = Path(glob_pattern)
            if file_path.is_file():
                result = _process_file(file_path)
                if result:
                    results.append(result)

        return results

    except Exception as e:
        error("FILE", "File fetch failed", f"URL: {url}, Error: {str(e)}")
        return []


class FileConnector(FeedConnector):
    # Cache file listings indefinitely
    cache_expiration = -1

    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme == "file"

    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        try:
            return fetch_files(url)
        except Exception as e:
            error(
                "FILE",
                "URL processing failed",
                f"Error processing file URL {url}: {str(e)}",
            )
            return []
