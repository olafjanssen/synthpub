"""
Cache manager for news feed items.

Provides functions to store and retrieve feed items from a file-based cache.
"""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional, Any, List
from .common import get_db_path
from utils.logging import error

# Cache configuration
MAX_CACHE_SIZE_MB = 500  # 500MB cache limit
CACHE_CLEANUP_THRESHOLD = 0.9  # Run cleanup when cache is 90% full

# In-memory tracking of cached items and their metadata
_cache_metadata: Dict[str, Dict[str, Any]] = {}
_cache_size_bytes = 0
_cache_initialized = False

def _sanitize_filename(url: str, max_length: int = 120) -> str:
    """
    Convert a URL to a safe filename.
    
    Args:
        url: The URL to convert
        max_length: Maximum filename length (excluding extension)
        
    Returns:
        A filesystem-safe string to use as filename
    """
    # Replace scheme:// with scheme_
    url = url.replace("://", "_")
    
    # Replace special characters with underscores
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ', '%', '&', '=', '+', '@', '#', ';', '!', '\'']:
        url = url.replace(char, '_')
    
    # Remove consecutive underscores
    while "__" in url:
        url = url.replace("__", "_")
    
    # Trim to max length
    if len(url) > max_length:
        # Keep the beginning and end, remove middle
        half_length = max_length // 2
        url = url[:half_length] + "___" + url[-half_length:]
    
    return url

def _get_cache_path(url: str) -> Path:
    """Generate a human-readable cache path from a URL."""
    # Create a readable filename based on the URL
    base_filename = _sanitize_filename(url)
    
    # Add a short hash suffix to avoid potential collisions
    url_short_hash = hashlib.md5(url.encode(), usedforsecurity=False).hexdigest()[:8]
    filename = f"{base_filename}_{url_short_hash}.json"
    
    return CACHE_PATH() / filename

def _initialize_cache():
    """Initialize the cache metadata by scanning cache directory."""
    global _cache_metadata, _cache_size_bytes, _cache_initialized
    
    if _cache_initialized:
        return
    
    _cache_metadata = {}
    _cache_size_bytes = 0
    
    # Ensure cache directory exists
    ensure_cache_exists()
    
    # Scan cache directory and build metadata
    for file_path in CACHE_PATH().glob("*.json"):
        if file_path.is_file():
            file_size = file_path.stat().st_size
            _cache_size_bytes += file_size
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    url = data.get("url")
                    if url:
                        _cache_metadata[url] = {
                            "path": file_path,
                            "size": file_size,
                            "added_at": file_path.stat().st_mtime,
                            "expires_at": data.get("expires_at", -1)
                        }
            except (json.JSONDecodeError, KeyError, TypeError):
                # Invalid file, remove from cache
                file_path.unlink(missing_ok=True)
                _cache_size_bytes -= file_size
    
    _cache_initialized = True

def _cleanup_cache():
    """Clean up expired and excess items when cache exceeds threshold."""
    global _cache_metadata, _cache_size_bytes
    
    # Current time for expiration check
    current_time = time.time()
    
    # First, remove expired items
    expired_urls = [
        url for url, metadata in _cache_metadata.items()
        if metadata["expires_at"] > 0 and metadata["expires_at"] < current_time
    ]
    
    for url in expired_urls:
        remove_from_cache(url)
    
    # If still above threshold, remove oldest items until below threshold
    max_size_bytes = MAX_CACHE_SIZE_MB * 1024 * 1024
    if _cache_size_bytes > max_size_bytes * CACHE_CLEANUP_THRESHOLD:
        # Sort by added_at (oldest first)
        urls_by_age = sorted(
            _cache_metadata.keys(),
            key=lambda url: _cache_metadata[url]["added_at"]
        )
        
        # Remove oldest items until below threshold or all items with expiration
        for url in urls_by_age:
            # Keep items with expiration time -1 (cache forever) unless absolutely necessary
            if _cache_size_bytes <= max_size_bytes * CACHE_CLEANUP_THRESHOLD:
                break
                
            if _cache_metadata[url]["expires_at"] != -1:
                remove_from_cache(url)

def CACHE_PATH() -> Path:
    """Get the cache directory path."""
    return get_db_path('_cache')

def ensure_cache_exists():
    """Create the cache directory if it doesn't exist."""
    CACHE_PATH().mkdir(parents=True, exist_ok=True)

def get_from_cache(url: str) -> Optional[Dict[str, Any]]:
    """
    Get an item from the cache.
    
    Args:
        url: The URL to retrieve from cache
        
    Returns:
        The cached content or None if not found or expired
    """
    _initialize_cache()
    
    # Check if item exists in cache metadata
    if url not in _cache_metadata:
        return None
    
    metadata = _cache_metadata[url]
    
    # Check if item has expired
    if metadata["expires_at"] > 0 and metadata["expires_at"] < time.time():
        # Item has expired, remove it
        remove_from_cache(url)
        return None
    
    # Load item from disk
    try:
        with open(metadata["path"], "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # File doesn't exist or is invalid, remove from metadata
        remove_from_cache(url)
        return None

def add_to_cache(url: str, content: Dict[str, Any], expiration_time: int = -1):
    """
    Add an item to the cache.
    
    Args:
        url: The URL as the unique identifier
        content: The content to cache (must be JSON serializable)
        expiration_time: Cache expiration time in seconds
            -1: cache forever (default)
            0: never cache
            >0: seconds to cache
    """
    # Never cache if expiration_time is 0
    if expiration_time == 0:
        return
    
    _initialize_cache()
    
    # Add expiration timestamp if needed
    if expiration_time > 0:
        content["expires_at"] = time.time() + expiration_time
    else:
        content["expires_at"] = expiration_time  # -1 for forever
    
    # Add URL to content
    content["url"] = url
    
    # Generate cache path
    cache_path = _get_cache_path(url)
    
    # Write to cache
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False)
    
    # Update metadata
    file_size = cache_path.stat().st_size
    _cache_metadata[url] = {
        "path": cache_path,
        "size": file_size,
        "added_at": time.time(),
        "expires_at": content["expires_at"]
    }
    
    # Update total cache size
    global _cache_size_bytes
    if url in _cache_metadata:
        _cache_size_bytes -= _cache_metadata[url]["size"]
    _cache_size_bytes += file_size
    
    # Check if cleanup needed
    if _cache_size_bytes > MAX_CACHE_SIZE_MB * 1024 * 1024 * CACHE_CLEANUP_THRESHOLD:
        _cleanup_cache()

def remove_from_cache(url: str):
    """
    Remove an item from the cache.
    
    Args:
        url: The URL to remove from cache
    """
    global _cache_metadata, _cache_size_bytes
    
    if url in _cache_metadata:
        # Get metadata before removing
        metadata = _cache_metadata[url]
        
        # Remove file
        try:
            metadata["path"].unlink(missing_ok=True)
        except (PermissionError, OSError):
            pass  # Ignore errors on deletion
        
        # Update cache size
        _cache_size_bytes -= metadata["size"]
        
        # Remove from metadata
        del _cache_metadata[url]

def clear_cache():
    """Clear the entire cache."""
    global _cache_metadata, _cache_size_bytes, _cache_initialized
    
    # Remove all files
    for file_path in CACHE_PATH().glob("*.json"):
        try:
            file_path.unlink(missing_ok=True)
        except (PermissionError, OSError):
            pass  # Ignore errors on deletion
    
    # Reset metadata
    _cache_metadata = {}
    _cache_size_bytes = 0
    _cache_initialized = False

def find_cache_files(url_pattern: str = None) -> List[Dict[str, Any]]:
    """
    Find cache files matching a URL pattern.
    
    Args:
        url_pattern: Optional substring to match in cache filenames
                    (None returns all cache files)
    
    Returns:
        List of dicts with information about matching cache files:
        - path: Full path to the cache file
        - filename: Name of the cache file
        - url_part: The human-readable part of the filename (without hash)
        - size: Size of the file in bytes
        - age: Age of the file in seconds
    """
    ensure_cache_exists()
    cache_dir = CACHE_PATH()
    results = []
    
    for file_path in cache_dir.glob("*.json"):
        if url_pattern is None or url_pattern.lower() in file_path.name.lower():
            # Get file info
            stat = file_path.stat()
            url_part = file_path.stem.rsplit('_', 1)[0]  # Remove hash suffix
            
            results.append({
                'path': str(file_path),
                'filename': file_path.name,
                'url_part': url_part,
                'size': stat.st_size,
                'age': time.time() - stat.st_mtime
            })
    
    # Sort by age (newest first)
    results.sort(key=lambda x: x['age'])
    return results

def get_cache_info(url: str) -> Optional[Dict[str, Any]]:
    """
    Get information about cached content for a specific URL.
    
    Args:
        url: The URL to check
        
    Returns:
        Dict with cache info or None if not cached:
        - path: Path to the cache file
        - exists: Whether the cache exists and is valid
        - filename: Name of the cache file
        - age: Age of the cached content in seconds
        - size: Size of the cache file in bytes
        - item_count: Number of items in the cache
        - expired: Whether the cache has expired
    """
    ensure_cache_exists()
    cache_path = _get_cache_path(url)
    
    if not cache_path.exists():
        return None
    
    try:
        stat = cache_path.stat()
        age = time.time() - stat.st_mtime
        
        # Try to read the cache
        cache_data = get_from_cache(url)
        item_count = len(cache_data.get('items', [])) if cache_data else 0
        
        # Determine the expiration time
        expiration_time = -1
        for connector_class in get_all_connectors():
            if hasattr(connector_class, 'can_handle') and callable(connector_class.can_handle):
                if connector_class.can_handle(url) and hasattr(connector_class, 'cache_expiration'):
                    expiration_time = connector_class.cache_expiration
                    break
        
        # Check if expired
        is_expired = expiration_time > 0 and age > expiration_time
        
        return {
            'path': str(cache_path),
            'exists': cache_data is not None,
            'filename': cache_path.name,
            'age': age,
            'size': stat.st_size,
            'item_count': item_count,
            'expired': is_expired
        }
    except Exception as e:
        error("CACHE", "Info retrieval failed", f"Error getting cache info for {url}: {str(e)}")
        return None

def get_all_connectors():
    """Get all feed connector classes."""
    try:
        from news.feeds import CONNECTORS
        return CONNECTORS
    except ImportError:
        return [] 