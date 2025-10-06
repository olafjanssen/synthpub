"""GitLab item connector for fetching individual commits and issues."""

from typing import Any, Dict, List
from urllib.parse import urlparse

from services.gitlab_service import (
    fetch_commit_details,
    fetch_issue_details,
    format_commit_content,
    format_issue_content,
    parse_gitlab_url,
    resolve_project_id,
)
from utils.logging import error, info

from .feed_connector import FeedConnector


class GitLabItemConnector(FeedConnector):
    """Connector for individual GitLab commits and issues."""
    
    # Cache individual items for 1 hour
    cache_expiration = 3600
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this connector can handle the given URL."""
        parsed = urlparse(url)
        
        # Check if it's a GitLab URL
        if not (parsed.netloc == "gitlab.com" or parsed.netloc.endswith(".gitlab.com")):
            return False
        
        # Check if it's a commit or issue URL
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 4:
            # Format: /group/project/-/commit/sha or /group/project/-/issues/number
            if len(path_parts) >= 5 and path_parts[-2] in ["commit", "issues"]:
                return True
        
        return False
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, Any]]:
        """
        Fetch detailed content from a GitLab commit or issue URL.
        
        Args:
            url: GitLab commit or issue URL
            
        Returns:
            List with single dict containing detailed content
        """
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip("/").split("/")
            
            if len(path_parts) < 5:
                error("GITLAB_ITEM", "Invalid URL format", f"URL: {url}")
                return []
            
            # Extract components from path like: group/project/-/commit/sha or group/project/-/issues/number
            project_path = "/".join(path_parts[:-3])  # Everything before /-/commit or /-/issues
            item_type = path_parts[-2]  # commit or issues
            item_id = path_parts[-1]  # SHA or issue number
            
            # Determine host
            host = parsed.netloc
            if host == "gitlab.com":
                host = "gitlab.com"
            
            info("GITLAB_ITEM", "Processing item", f"Type: {item_type}, ID: {item_id}, Project: {project_path}")
            
            # Resolve project path to project ID
            try:
                project_id = resolve_project_id(host, project_path)
                info("GITLAB_ITEM", "Project resolved", f"Path: {project_path} -> ID: {project_id}")
            except ValueError as e:
                error("GITLAB_ITEM", "Failed to resolve project", f"Path: {project_path}, Error: {str(e)}")
                return []
            
            if item_type == "commit":
                return GitLabItemConnector._fetch_commit_content(host, project_id, project_path, item_id, url)
            elif item_type == "issues":
                return GitLabItemConnector._fetch_issue_content(host, project_id, project_path, item_id, url)
            else:
                error("GITLAB_ITEM", "Unsupported item type", f"Type: {item_type}")
                return []
                
        except Exception as e:
            error("GITLAB_ITEM", "Fetch failed", f"URL: {url}, Error: {str(e)}")
            return []
    
    @staticmethod
    def _fetch_commit_content(host: str, project_id: str, project_path: str, commit_sha: str, url: str) -> List[Dict[str, Any]]:
        """Fetch detailed commit content."""
        try:
            # Fetch detailed commit information
            commit_details = fetch_commit_details(host, project_id, commit_sha)
            if not commit_details:
                error("GITLAB_ITEM", "Failed to fetch commit details", f"SHA: {commit_sha}")
                return []
            
            # Format the commit content
            project_name = project_path.split("/")[-1]
            content = format_commit_content(commit_details, project_name)
            
            # Extract metadata
            commit_message = commit_details.get("message", "")
            commit_date = commit_details.get("committed_date", "")
            commit_author = commit_details.get("author_name", "Unknown")
            
            return [{
                "url": url,
                "content": content,
                "title": f"Commit: {commit_message}",
                "needs_further_processing": False,  # This is the final content
                "type": "commit",
                "project": project_name,
                "author": commit_author,
                "date": commit_date
            }]
            
        except Exception as e:
            error("GITLAB_ITEM", "Failed to fetch commit content", f"SHA: {commit_sha}, Error: {str(e)}")
            return []
    
    @staticmethod
    def _fetch_issue_content(host: str, project_id: str, project_path: str, issue_number: str, url: str) -> List[Dict[str, Any]]:
        """Fetch detailed issue content."""
        try:
            # Convert issue number to int
            try:
                issue_num = int(issue_number)
            except ValueError:
                error("GITLAB_ITEM", "Invalid issue number", f"Number: {issue_number}")
                return []
            
            # Fetch detailed issue information
            issue_details = fetch_issue_details(host, project_id, issue_num)
            if not issue_details:
                error("GITLAB_ITEM", "Failed to fetch issue details", f"Number: {issue_num}")
                return []
            
            # Format the issue content
            project_name = project_path.split("/")[-1]
            content = format_issue_content(issue_details, project_name)
            
            # Extract metadata
            issue_title = issue_details.get("title", "")
            issue_date = issue_details.get("created_at", "")
            issue_author = issue_details.get("author", {}).get("name", "Unknown")
            
            return [{
                "url": url,
                "content": content,
                "title": f"Issue #{issue_num}: {issue_title}",
                "needs_further_processing": False,  # This is the final content
                "type": "issue",
                "project": project_name,
                "author": issue_author,
                "date": issue_date
            }]
            
        except Exception as e:
            error("GITLAB_ITEM", "Failed to fetch issue content", f"Number: {issue_number}, Error: {str(e)}")
            return []
