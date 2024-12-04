"""
File system connector for processing local files using glob patterns.
"""
from pathlib import Path
from typing import Dict, List
from urllib.parse import unquote
import mimetypes
import glob

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
                content = read_text_file(filepath)
                results.append({
                    'title': path.name,
                    'content': content,
                    'url': f"file://{path.absolute()}",
                    'modified': path.stat().st_mtime
                })
            except Exception as e:
                print(f"Error reading file {filepath}: {str(e)}")
        else:
            print(f"Skipping non-text file: {filepath}")
    
    # Sort by modified date and remove the modified field
    results.sort(key=lambda x: x['modified'])
    for result in results:
        del result['modified']
            
    return results