"""Service for fetching images from Pexels API."""

import os
import random
from typing import Any, Dict, Optional

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
        warning(
            "PEXELS",
            "Missing API key",
            "Pexels API key not found in environment variables",
        )
        return {}

    headers = {"Authorization": api_key}

    url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error("PEXELS", "API request failed", f"Error fetching images from Pexels: {e}")
        return {}


def _clean_search_terms(text: str) -> str:
    """Clean and extract key search terms from text."""
    # Remove common words and short terms
    stop_words = {
        "this",
        "that",
        "with",
        "from",
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
    }
    words = [
        word
        for word in text.split()
        if len(word) > 3 and word.lower() not in stop_words
    ]
    return " ".join(words)


def _get_default_search_terms() -> str:
    """Get default search terms when no good terms are found."""
    return "nature landscape"


def get_random_thumbnail(text: str) -> Dict[str, Optional[str]]:
    """Get a random thumbnail URL based on a search text."""
    # Clean up the search text - extract key terms
    search_terms = _clean_search_terms(text)

    # If we don't have good search terms, use defaults
    if not search_terms:
        search_terms = _get_default_search_terms()

    # Search for images
    results = search_images(search_terms, per_page=10)

    # Return random image URL if available
    if results and "photos" in results and results["photos"]:
        photo = random.choice(results["photos"])
        return {"thumbnail_url": photo.get("src", {}).get("medium")}

    return {"thumbnail_url": None}
