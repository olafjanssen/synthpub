"""Service for fetching images from Pexels API."""
import os
import random
from typing import Any, Dict, List, Optional

import requests

from utils.logging import error, warning


def get_pexels_key() -> str:
    """Get Pexels API key from environment variables."""
    return os.environ.get("PEXELS_API_KEY", "")

def search_images(query: str, per_page: int = 10) -> Dict[str, Any]:
    """
    Search for images using Pexels API.
    
    Args:
        query: Search term
        per_page: Number of images to return (max 80)
        
    Returns:
        Dict containing search results or empty dict if error
    """
    api_key = get_pexels_key()
    
    if not api_key:
        warning("PEXELS", "Missing API key", "Pexels API key not found in environment variables")
        return {}
        
    headers = {
        "Authorization": api_key
    }
    
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error("PEXELS", "API request failed", f"Error fetching images from Pexels: {e}")
        return {}

def get_random_thumbnail(text: str) -> Dict[str, Optional[str]]:
    """
    Get a random thumbnail URL based on a search text.
    
    Args:
        text: Text to use for image search (title or description)
        
    Returns:
        Dict with thumbnail_url
    """
    # Clean up the search text - extract key terms
    search_terms = " ".join([word for word in text.split() 
                     if len(word) > 3 and word.lower() not in ["this", "that", "with", "from"]])
    
    # If we don't have good search terms, use some defaults
    if not search_terms or len(search_terms) < 5:
        search_terms = "abstract colorful pattern"
    
    # Search for images
    results = search_images(search_terms)
    
    if not results or "photos" not in results or not results["photos"]:
        # Fallback to abstract patterns if no results
        results = search_images("abstract colorful pattern")
    
    # Select a random image if we have results
    if results and "photos" in results and results["photos"]:
        photo = random.choice(results["photos"])
        thumbnail_url = photo.get("src", {}).get("medium", "")
        
        return {
            "thumbnail_url": thumbnail_url
        }
    
    # Return empty values if no images found
    return {
        "thumbnail_url": None
    } 