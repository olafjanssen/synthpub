"""Shared utilities for GitLab feed connectors."""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests

from utils.logging import debug, error, info


def get_gitlab_token() -> str:
    """Get GitLab token from environment variables."""
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        error("GITLAB", "Missing API key", "GITLAB_TOKEN environment variable not found")
        raise ValueError("GITLAB_TOKEN environment variable not found")
    debug("GITLAB", "API key loaded", "Token available")
    return token


def get_api_base_url(host: str) -> str:
    """Get GitLab API base URL for the given host."""
    return f"https://{host}/api/v4"


def parse_gitlab_url(url: str) -> tuple[str, str]:
    """
    Parse a gitlab:// URL and return host and path components.
    
    Examples:
    - gitlab://gitlab.com/group-name -> (gitlab.com, group-name)
    - gitlab://gitlab.com/group-name/project-name -> (gitlab.com, group-name/project-name)
    """
    if not url.startswith("gitlab://"):
        error("GITLAB", "Invalid URL", f"URL must start with gitlab://, got {url}")
        raise ValueError("URL must start with gitlab://")
    
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path.strip("/")
    
    debug("GITLAB", "URL parsed", f"Host: {host}, Path: {path}")
    return host, path


def parse_gitlab_publisher_url(url: str) -> tuple[str, str, str, str]:
    """
    Parse a gitlab:// URL for publisher and return project components.
    Example URL: gitlab://gitlab_host/project_id/branch/path/to/file.md
    """
    if not url.startswith("gitlab://"):
        error("GITLAB", "Invalid URL", f"URL must start with gitlab://, got {url}")
        raise ValueError("URL must start with gitlab://")

    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    debug("GITLAB", "URL parsed", f"Host: {parsed.netloc}, Path parts: {len(parts)}")

    if len(parts) < 3:
        error(
            "GITLAB",
            "Invalid URL",
            "URL must include host, project, branch, and file path",
        )
        raise ValueError("URL must include host, project, branch, and file path")

    host = parsed.netloc
    project_id = parts[0]
    branch = parts[1]
    file_path = "/".join(parts[2:])

    debug(
        "GITLAB",
        "URL components",
        f"Host: {host}, Project: {project_id}, Branch: {branch}, Path: {file_path}",
    )
    return host, project_id, branch, file_path


def make_gitlab_request(url: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Make a request to GitLab API with authentication.
    
    Args:
        url: Full API URL
        params: Query parameters
        
    Returns:
        List of response items
    """
    token = get_gitlab_token()
    headers = {"PRIVATE-TOKEN": token}
    
    all_items = []
    page = 1
    per_page = 100
    
    while True:
        request_params = {"page": page, "per_page": per_page}
        if params:
            request_params.update(params)
        
        try:
            response = requests.get(url, headers=headers, params=request_params, timeout=30)
            response.raise_for_status()
            
            items = response.json()
            if not items:  # No more items
                break
                
            all_items.extend(items)
            
            # Check if we got fewer items than requested (last page)
            if len(items) < per_page:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            error("GITLAB", "API request failed", f"URL: {url}, Error: {str(e)}")
            break
    
    return all_items


def fetch_group_projects(host: str, group_path: str, include_subgroups: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch all projects in a GitLab group.
    
    Args:
        host: GitLab host
        group_path: Group path or ID
        include_subgroups: Whether to include projects from subgroups
        
    Returns:
        List of project dictionaries
    """
    api_base = get_api_base_url(host)
    url = f"{api_base}/groups/{group_path}/projects"
    
    params = {
        "include_subgroups": include_subgroups,
        "order_by": "last_activity_at",
        "sort": "desc"
    }
    
    info("GITLAB", "Fetching group projects", f"Group: {group_path}, Include subgroups: {include_subgroups}")
    return make_gitlab_request(url, params)


def fetch_project_commits(host: str, project_id: str, since_days: int = 7) -> List[Dict[str, Any]]:
    """
    Fetch recent commits from a GitLab project.
    
    Args:
        host: GitLab host
        project_id: Project ID
        since_days: Number of days to look back for commits
        
    Returns:
        List of commit dictionaries
    """
    api_base = get_api_base_url(host)
    url = f"{api_base}/projects/{project_id}/repository/commits"
    
    since_date = datetime.now() - timedelta(days=since_days)
    params = {
        "since": since_date.isoformat(),
        "order": "default"
    }
    
    debug("GITLAB", "Fetching project commits", f"Project: {project_id}, Since: {since_date}")
    return make_gitlab_request(url, params)


def fetch_project_issues(host: str, project_id: str, since_days: int = 7) -> List[Dict[str, Any]]:
    """
    Fetch recent issues from a GitLab project.
    
    Args:
        host: GitLab host
        project_id: Project ID
        since_days: Number of days to look back for issues
        
    Returns:
        List of issue dictionaries
    """
    api_base = get_api_base_url(host)
    url = f"{api_base}/projects/{project_id}/issues"
    
    since_date = datetime.now() - timedelta(days=since_days)
    params = {
        "created_after": since_date.isoformat(),
        "state": "opened",
        "order_by": "created_at",
        "sort": "desc"
    }
    
    debug("GITLAB", "Fetching project issues", f"Project: {project_id}, Since: {since_date}")
    return make_gitlab_request(url, params)


def fetch_commit_details(host: str, project_id: str, commit_sha: str) -> Dict[str, Any]:
    """
    Fetch detailed information about a specific commit.
    
    Args:
        host: GitLab host
        project_id: Project ID
        commit_sha: Commit SHA
        
    Returns:
        Detailed commit information including diff
    """
    api_base = get_api_base_url(host)
    
    # Fetch commit details
    commit_url = f"{api_base}/projects/{project_id}/repository/commits/{commit_sha}"
    commit_details = make_gitlab_request(commit_url)
    
    if not commit_details:
        return {}
    
    commit_data = commit_details[0]
    
    # Fetch commit diff
    diff_url = f"{api_base}/projects/{project_id}/repository/commits/{commit_sha}/diff"
    diff_data = make_gitlab_request(diff_url)
    
    # Add diff to commit data
    commit_data["diff"] = diff_data
    
    return commit_data


def fetch_issue_details(host: str, project_id: str, issue_iid: int) -> Dict[str, Any]:
    """
    Fetch detailed information about a specific issue.
    
    Args:
        host: GitLab host
        project_id: Project ID
        issue_iid: Issue internal ID
        
    Returns:
        Detailed issue information including discussions
    """
    api_base = get_api_base_url(host)
    
    # Fetch issue details
    issue_url = f"{api_base}/projects/{project_id}/issues/{issue_iid}"
    issue_details = make_gitlab_request(issue_url)
    
    if not issue_details:
        return {}
    
    issue_data = issue_details[0]
    
    # Fetch issue discussions (comments)
    discussions_url = f"{api_base}/projects/{project_id}/issues/{issue_iid}/discussions"
    discussions_data = make_gitlab_request(discussions_url)
    
    # Add discussions to issue data
    issue_data["discussions"] = discussions_data
    
    return issue_data


def format_commit_content(commit: Dict[str, Any], project_name: str) -> str:
    """Format commit data into readable content with full details."""
    author = commit.get("author_name", "Unknown")
    message = commit.get("message", "").strip()
    date = commit.get("committed_date", "")
    commit_id = commit.get("id", "")
    
    # Clean up commit message (remove merge commit noise)
    if message.startswith("Merge branch") or message.startswith("Merge remote-tracking branch"):
        return ""
    
    content = f"Commit in {project_name}\n"
    content += f"Author: {author}\n"
    content += f"Date: {date}\n"
    content += f"Commit ID: {commit_id}\n"
    content += f"Message: {message}\n"
    
    # Add diff if available
    diff = commit.get("diff", [])
    if diff:
        content += "\nChanges:\n"
        for change in diff:
            file_path = change.get("new_path", change.get("old_path", "Unknown"))
            content += f"\n--- {file_path} ---\n"
            content += change.get("diff", "")
    
    return content


def format_issue_content(issue: Dict[str, Any], project_name: str) -> str:
    """Format issue data into readable content with full details."""
    title = issue.get("title", "")
    description = issue.get("description", "")
    author = issue.get("author", {}).get("name", "Unknown")
    created_at = issue.get("created_at", "")
    state = issue.get("state", "unknown")
    labels = issue.get("labels", [])
    issue_iid = issue.get("iid", "")
    
    content = f"Issue in {project_name}\n"
    content += f"Title: {title}\n"
    content += f"Author: {author}\n"
    content += f"State: {state}\n"
    content += f"Created: {created_at}\n"
    content += f"Issue #: {issue_iid}\n"
    
    if labels:
        content += f"Labels: {', '.join(labels)}\n"
    
    if description:
        content += f"\nDescription:\n{description}\n"
    
    # Add discussions if available
    discussions = issue.get("discussions", [])
    if discussions:
        content += "\n--- Discussions ---\n"
        for discussion in discussions:
            notes = discussion.get("notes", [])
            for note in notes:
                note_author = note.get("author", {}).get("name", "Unknown")
                note_body = note.get("body", "")
                note_created = note.get("created_at", "")
                content += f"\n{note_author} ({note_created}):\n{note_body}\n"
    
    return content
