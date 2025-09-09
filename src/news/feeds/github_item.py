"""GitHub item connector for fetching individual commits and issues."""

from typing import Any, Dict, List
from urllib.parse import urlparse

from services.github_service import (
    fetch_commit_details,
    fetch_issue_details,
    format_commit_content,
    format_issue_content,
    parse_github_url,
)
from utils.logging import error, info

from .feed_connector import FeedConnector


class GitHubItemConnector(FeedConnector):
    """Connector for individual GitHub commits and issues."""
    
    # Cache individual items for 1 hour
    cache_expiration = 3600
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this connector can handle the given URL."""
        parsed = urlparse(url)
        
        # Check if it's a GitHub URL
        if not (parsed.netloc == "github.com" or parsed.netloc.endswith(".github.com")):
            return False
        
        # Check if it's a commit or issue URL
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 4:
            # Format: /owner/repo/commit/sha or /owner/repo/issues/number
            if path_parts[2] in ["commit", "issues"]:
                return True
        
        return False
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, Any]]:
        """
        Fetch detailed content from a GitHub commit or issue URL.
        
        Args:
            url: GitHub commit or issue URL
            
        Returns:
            List with single dict containing detailed content
        """
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip("/").split("/")
            
            if len(path_parts) < 4:
                error("GITHUB_ITEM", "Invalid URL format", f"URL: {url}")
                return []
            
            owner = path_parts[0]
            repo = path_parts[1]
            item_type = path_parts[2]
            item_id = path_parts[3]
            
            # Determine host
            host = parsed.netloc
            if host == "github.com":
                host = "github.com"
            
            info("GITHUB_ITEM", "Processing item", f"Type: {item_type}, ID: {item_id}, Repository: {owner}/{repo}")
            
            if item_type == "commit":
                return GitHubItemConnector._fetch_commit_content(host, owner, repo, item_id, url)
            elif item_type == "issues":
                return GitHubItemConnector._fetch_issue_content(host, owner, repo, item_id, url)
            else:
                error("GITHUB_ITEM", "Unsupported item type", f"Type: {item_type}")
                return []
                
        except Exception as e:
            error("GITHUB_ITEM", "Fetch failed", f"URL: {url}, Error: {str(e)}")
            return []
    
    @staticmethod
    def _fetch_commit_content(host: str, owner: str, repo: str, commit_sha: str, url: str) -> List[Dict[str, Any]]:
        """Fetch detailed commit content."""
        try:
            # Fetch detailed commit information
            commit_details = fetch_commit_details(host, owner, repo, commit_sha)
            if not commit_details:
                error("GITHUB_ITEM", "Failed to fetch commit details", f"SHA: {commit_sha}")
                return []
            
            # Format the commit content
            content = format_commit_content(commit_details, repo)
            
            # Extract metadata
            commit_message = commit_details.get("commit", {}).get("message", "")
            commit_date = commit_details.get("commit", {}).get("author", {}).get("date", "")
            commit_author = commit_details.get("commit", {}).get("author", {}).get("name", "Unknown")
            
            return [{
                "url": url,
                "content": content,
                "title": f"Commit: {commit_message}",
                "needs_further_processing": False,  # This is the final content
                "type": "commit",
                "project": repo,
                "author": commit_author,
                "date": commit_date
            }]
            
        except Exception as e:
            error("GITHUB_ITEM", "Failed to fetch commit content", f"SHA: {commit_sha}, Error: {str(e)}")
            return []
    
    @staticmethod
    def _fetch_issue_content(host: str, owner: str, repo: str, issue_number: str, url: str) -> List[Dict[str, Any]]:
        """Fetch detailed issue content."""
        try:
            # Convert issue number to int
            try:
                issue_num = int(issue_number)
            except ValueError:
                error("GITHUB_ITEM", "Invalid issue number", f"Number: {issue_number}")
                return []
            
            # Fetch detailed issue information
            issue_details = fetch_issue_details(host, owner, repo, issue_num)
            if not issue_details:
                error("GITHUB_ITEM", "Failed to fetch issue details", f"Number: {issue_num}")
                return []
            
            # Format the issue content
            content = format_issue_content(issue_details, repo)
            
            # Extract metadata
            issue_title = issue_details.get("title", "")
            issue_date = issue_details.get("created_at", "")
            issue_author = issue_details.get("user", {}).get("login", "Unknown")
            
            return [{
                "url": url,
                "content": content,
                "title": f"Issue #{issue_num}: {issue_title}",
                "needs_further_processing": False,  # This is the final content
                "type": "issue",
                "project": repo,
                "author": issue_author,
                "date": issue_date
            }]
            
        except Exception as e:
            error("GITHUB_ITEM", "Failed to fetch issue content", f"Number: {issue_number}, Error: {str(e)}")
            return []
