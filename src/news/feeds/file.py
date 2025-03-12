"""
File system connector for processing local files using glob patterns.
"""
from pathlib import Path
from typing import Dict, List
from urllib.parse import unquote, urlparse
import mimetypes
import glob
from .feed_connector import FeedConnector
from utils.logging import error, warning

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
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def fetch_files(url: str) -> List[Dict[str, str]]:
    """
    Fetch content from files matching the glob pattern.
    
    Args:
        url: file:// URL with optional glob pattern
        
    Returns:
        List of dicts containing file info and content, ordered by last modified date (oldest first)
    """
    path_pattern = parse_file_url(url)
    results = []
    
    # Handle both Windows and Unix paths
    if Path(path_pattern).is_absolute():
        glob_pattern = path_pattern
    else:
        # Relative paths are relative to current working directory
        glob_pattern = str(Path.cwd() / path_pattern)
    
    # Check if this is a glob pattern or a specific file
    is_glob_pattern = '*' in path_pattern or '?' in path_pattern
    
    # Find all matching files
    for filepath in glob.glob(glob_pattern, recursive=True):
        path = Path(filepath)
        
        # Skip directories
        if path.is_dir():
            continue
            
        # Determine mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        
        # Only process text files
        if mime_type and mime_type.startswith('text/'):
            try:
                if not is_glob_pattern:
                    # For single files, include the full content
                    content = read_text_file(filepath)
                    needs_processing = False
                else:
                    # For glob patterns, just include file info and let the file be processed individually
                    content = f"File: {path.name}"
                    needs_processing = True
                    
                results.append({
                    'title': path.name,
                    'content': content,
                    'url': f"file://{path.absolute()}",
                    'modified': path.stat().st_mtime,
                    'needs_further_processing': needs_processing
                })
            except Exception as e:
                error("FILE", "Read error", f"Error reading file {filepath}: {str(e)}")
        else:
            warning("FILE", "Skipping file", f"Skipping non-text file: {filepath}")
    
    # Sort by modified date and remove the modified field
    results.sort(key=lambda x: x['modified'])
    for result in results:
        del result['modified']
            
    return results

class FileConnector(FeedConnector):
    # Cache file listings indefinitely
    cache_expiration = -1
    # This is an aggregate connector when using glob patterns
    is_aggregate = False  # Default

    @classmethod
    def handle_feed_update(cls, sender, feed_url: str):
        """Override to dynamically set is_aggregate based on URL type."""
        if cls.can_handle(feed_url):
            # Check if it's a glob pattern
            path_pattern = parse_file_url(feed_url)
            if '*' in path_pattern or '?' in path_pattern:
                cls.is_aggregate = True
            else:
                cls.is_aggregate = False
                
            # Call parent implementation with correct flag set
            super().handle_feed_update(sender, feed_url)
            
            # Reset flag
            cls.is_aggregate = False
    
    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme == 'file'
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        try:
            return fetch_files(url)
        except Exception as e:
            error("FILE", "URL processing failed", f"Error processing file URL {url}: {str(e)}")
            return []
