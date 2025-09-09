"""Shared utilities for GitHub feed connectors."""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests

from utils.logging import debug, error, info


def get_github_token() -> Optional[str]:
    """
    Get GitHub token from environment variables.
    
    Returns:
        GitHub API token if found, None otherwise
    """
    token = os.getenv("GITHUB_TOKEN")
    if token:
        debug("GITHUB", "API key loaded", "GitHub token found in environment")
        return token
    else:
        debug("GITHUB", "API key missing", "No GitHub token found in environment")
        return None


def get_github_headers() -> Dict[str, str]:
    """
    Get standard headers for GitHub API requests.
    
    Returns:
        Dictionary of headers including authentication if token is available
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "SynthPub/1.0"
    }
    
    token = get_github_token()
    if token:
        headers["Authorization"] = f"token {token}"
    
    return headers


def parse_github_url(url: str) -> tuple[str, str]:
    """
    Parse a GitHub URL to extract host and repository path.
    
    Args:
        url: GitHub URL in format github://host/owner/repo or https://host/owner/repo
        
    Returns:
        Tuple of (host, repository_path) where repository_path is "owner/repo"
        
    Raises:
        ValueError: If URL format is invalid
    """
    if url.startswith("github://"):
        # Remove the github:// prefix
        url = url[9:]
    elif url.startswith("https://github.com/") or url.startswith("http://github.com/"):
        # Handle standard GitHub URLs - extract owner/repo from the path
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")  # Remove leading slash
        if "/" not in path:
            raise ValueError(f"Invalid GitHub URL format: {url}")
        return "github.com", path
    else:
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    # Split by first slash to separate host from path
    if "/" not in url:
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    parts = url.split("/", 1)
    host = parts[0]
    repo_path = parts[1]
    
    # Validate that we have owner/repo format
    if "/" not in repo_path:
        raise ValueError(f"Repository path must be in owner/repo format: {repo_path}")
    
    return host, repo_path


def get_github_api_url(host: str, endpoint: str) -> str:
    """
    Build GitHub API URL for the given host and endpoint.
    
    Args:
        host: GitHub hostname (e.g., 'github.com')
        endpoint: API endpoint (e.g., 'repos/owner/repo/commits')
        
    Returns:
        Full GitHub API URL
    """
    if host == "github.com":
        return f"https://api.github.com/{endpoint}"
    else:
        return f"https://{host}/api/v3/{endpoint}"


def fetch_repository_commits(host: str, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch commits from a GitHub repository.
    
    Args:
        host: GitHub hostname
        owner: Repository owner
        repo: Repository name
        per_page: Number of commits per page (max 100)
        
    Returns:
        List of commit dictionaries
    """
    try:
        endpoint = f"repos/{owner}/{repo}/commits"
        url = get_github_api_url(host, endpoint)
        
        params = {
            "per_page": min(per_page, 100),  # GitHub API limit
            "page": 1
        }
        
        headers = get_github_headers()
        
        info("GITHUB", "Fetching commits", f"Repository: {owner}/{repo}")
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        # Handle rate limit errors
        if response.status_code == 403:
            rate_limit_info = response.headers.get('X-RateLimit-Remaining', 'Unknown')
            if 'rate limit' in response.text.lower():
                error("GITHUB", "Rate limit exceeded", f"Remaining requests: {rate_limit_info}")
                return []
        
        response.raise_for_status()
        
        commits = response.json()
        info("GITHUB", "Commits fetched", f"Count: {len(commits)}")
        
        return commits
        
    except requests.exceptions.RequestException as e:
        error("GITHUB", "Failed to fetch commits", f"Repository: {owner}/{repo}, Error: {str(e)}")
        return []
    except Exception as e:
        error("GITHUB", "Unexpected error fetching commits", f"Repository: {owner}/{repo}, Error: {str(e)}")
        return []


def fetch_repository_issues(host: str, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch issues from a GitHub repository.
    
    Args:
        host: GitHub hostname
        owner: Repository owner
        repo: Repository name
        per_page: Number of issues per page (max 100)
        
    Returns:
        List of issue dictionaries
    """
    try:
        endpoint = f"repos/{owner}/{repo}/issues"
        url = get_github_api_url(host, endpoint)
        
        params = {
            "per_page": min(per_page, 100),  # GitHub API limit
            "page": 1,
            "state": "all"  # Get both open and closed issues
        }
        
        headers = get_github_headers()
        
        info("GITHUB", "Fetching issues", f"Repository: {owner}/{repo}")
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        # Handle rate limit errors
        if response.status_code == 403:
            rate_limit_info = response.headers.get('X-RateLimit-Remaining', 'Unknown')
            if 'rate limit' in response.text.lower():
                error("GITHUB", "Rate limit exceeded", f"Remaining requests: {rate_limit_info}")
                return []
        
        response.raise_for_status()
        
        issues = response.json()
        info("GITHUB", "Issues fetched", f"Count: {len(issues)}")
        
        return issues
        
    except requests.exceptions.RequestException as e:
        error("GITHUB", "Failed to fetch issues", f"Repository: {owner}/{repo}, Error: {str(e)}")
        return []
    except Exception as e:
        error("GITHUB", "Unexpected error fetching issues", f"Repository: {owner}/{repo}, Error: {str(e)}")
        return []


def fetch_commit_details(host: str, owner: str, repo: str, commit_sha: str) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed information about a specific commit.
    
    Args:
        host: GitHub hostname
        owner: Repository owner
        repo: Repository name
        commit_sha: Commit SHA hash
        
    Returns:
        Detailed commit information or None if failed
    """
    try:
        endpoint = f"repos/{owner}/{repo}/commits/{commit_sha}"
        url = get_github_api_url(host, endpoint)
        
        headers = get_github_headers()
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        error("GITHUB", "Failed to fetch commit details", f"Commit: {commit_sha}, Error: {str(e)}")
        return None
    except Exception as e:
        error("GITHUB", "Unexpected error fetching commit details", f"Commit: {commit_sha}, Error: {str(e)}")
        return None


def fetch_issue_details(host: str, owner: str, repo: str, issue_number: int) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed information about a specific issue.
    
    Args:
        host: GitHub hostname
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        
    Returns:
        Detailed issue information or None if failed
    """
    try:
        endpoint = f"repos/{owner}/{repo}/issues/{issue_number}"
        url = get_github_api_url(host, endpoint)
        
        headers = get_github_headers()
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        error("GITHUB", "Failed to fetch issue details", f"Issue: #{issue_number}, Error: {str(e)}")
        return None
    except Exception as e:
        error("GITHUB", "Unexpected error fetching issue details", f"Issue: #{issue_number}, Error: {str(e)}")
        return None


def format_commit_content(commit: Dict[str, Any], repo_name: str) -> str:
    """
    Format commit information into readable content.
    
    Args:
        commit: Commit dictionary from GitHub API
        repo_name: Repository name for context
        
    Returns:
        Raw JSON string of the commit data
    """
    try:
        import json
        
        # Return the raw JSON string with proper formatting
        return json.dumps(commit, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error("GITHUB", "Failed to format commit content", f"Error: {str(e)}")
        return f"# Commit: {commit.get('commit', {}).get('message', 'Unknown')}"


def format_issue_content(issue: Dict[str, Any], repo_name: str) -> str:
    """
    Format issue information into readable content.
    
    Args:
        issue: Issue dictionary from GitHub API
        repo_name: Repository name for context
        
    Returns:
        Raw JSON string of the issue data
    """
    try:
        import json
        
        # Return the raw JSON string with proper formatting
        return json.dumps(issue, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error("GITHUB", "Failed to format issue content", f"Error: {str(e)}")
        return f"# Issue: {issue.get('title', 'Unknown')}"


def get_rate_limit_status(host: str = "github.com") -> Dict[str, Any]:
    """
    Get current GitHub API rate limit status.
    
    Args:
        host: GitHub hostname (defaults to github.com)
    
    Returns:
        Dictionary with rate limit information
    """
    try:
        if host == "github.com":
            url = "https://api.github.com/rate_limit"
        else:
            url = f"https://{host}/api/v3/rate_limit"
        
        headers = get_github_headers()
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        debug("GITHUB", "Rate limit check failed", f"Error: {str(e)}")
        return {}


def check_repository_exists(host: str, owner: str, repo: str) -> bool:
    """
    Check if a GitHub repository exists and is accessible.
    
    Args:
        host: GitHub hostname
        owner: Repository owner
        repo: Repository name
        
    Returns:
        True if repository exists and is accessible, False otherwise
    """
    try:
        endpoint = f"repos/{owner}/{repo}"
        url = get_github_api_url(host, endpoint)
        
        headers = get_github_headers()
        
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        debug("GITHUB", "Repository check failed", f"Repository: {owner}/{repo}, Error: {str(e)}")
        return False
