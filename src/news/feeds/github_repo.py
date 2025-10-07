"""GitHub repository connector for fetching commits and issues from a specific project."""

from typing import Any, Dict, List

from services.github_service import (
    check_repository_exists,
    fetch_commit_details,
    fetch_issue_details,
    fetch_repository_commits,
    fetch_repository_issues,
    format_commit_content,
    format_issue_content,
    parse_github_url,
)
from utils.logging import error, info

from .feed_connector import FeedConnector


class GitHubRepoConnector(FeedConnector):
    """Connector for individual GitHub repositories that fetches commits and issues."""
    
    # Cache repository data for 1 hour
    cache_expiration = 3600
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this connector can handle the given URL."""
        if not (url.startswith("github://") or url.startswith("https://github.com/")):
            return False
        
        try:
            host, path = parse_github_url(url)
            # For repositories, we expect owner/repo format
            # Path should contain exactly one slash (owner/repo)
            return bool(host and path and path.count("/") == 1)
        except ValueError:
            return False
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, Any]]:
        """
        Fetch a list of commit and issue URLs from a GitHub repository.
        
        Args:
            url: GitHub repository URL in format github://host/owner/repo or https://github.com/owner/repo
            
        Returns:
            List of dicts with commit and issue URLs for further processing
        """
        try:
            host, path = parse_github_url(url)
            
            # Extract owner and repo from path
            # The path should be in format "owner/repo"
            if "/" not in path:
                error("GITHUB_REPO", "Invalid repository path", f"Path: {path}")
                return []
            
            owner, repo = path.split("/", 1)
            
            info("GITHUB_REPO", "Processing repository", f"Host: {host}, Owner: {owner}, Repo: {repo}")
            
            # Check if repository exists
            if not check_repository_exists(host, owner, repo):
                error("GITHUB_REPO", "Repository not found or not accessible", f"Repository: {owner}/{repo}")
                return []
            
            all_items = []
            
            # Fetch commits
            try:
                commits = fetch_repository_commits(host, owner, repo)
                for commit in commits:
                    commit_sha = commit.get("sha", "")
                    if commit_sha:
                        commit_message = commit.get("commit", {}).get("message", "")
                        commit_date = commit.get("commit", {}).get("author", {}).get("date", "")
                        commit_author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
                        
                        all_items.append({
                            "url": f"https://{host}/{owner}/{repo}/commit/{commit_sha}",
                            "content": f"Commit: {commit_message}",
                            "title": f"Commit: {commit_message}",
                            "needs_further_processing": True,  # Mark for individual processing
                            "type": "commit",
                            "project": repo,
                            "author": commit_author,
                            "date": commit_date
                        })
            except Exception as e:
                error("GITHUB_REPO", "Failed to fetch commits", f"Repository: {owner}/{repo}, Error: {str(e)}")
            
            # Fetch issues
            try:
                issues = fetch_repository_issues(host, owner, repo)
                for issue in issues:
                    # Skip pull requests (they have pull_request field)
                    if "pull_request" in issue:
                        continue
                    
                    issue_number = issue.get("number", 0)
                    if issue_number:
                        issue_title = issue.get("title", "")
                        issue_date = issue.get("created_at", "")
                        issue_author = issue.get("user", {}).get("login", "Unknown")
                        
                        all_items.append({
                            "url": f"https://{host}/{owner}/{repo}/issues/{issue_number}",
                            "content": f"Issue #{issue_number}: {issue_title}",
                            "title": f"Issue #{issue_number}: {issue_title}",
                            "needs_further_processing": True,  # Mark for individual processing
                            "type": "issue",
                            "project": repo,
                            "author": issue_author,
                            "date": issue_date
                        })
            except Exception as e:
                error("GITHUB_REPO", "Failed to fetch issues", f"Repository: {owner}/{repo}, Error: {str(e)}")
            
            # Sort by date (oldest first)
            all_items.sort(key=lambda x: x.get("date", ""), reverse=False)
            
            info("GITHUB_REPO", "URLs collected", f"Total items: {len(all_items)}")
            return all_items
            
        except Exception as e:
            error("GITHUB_REPO", "Fetch failed", f"URL: {url}, Error: {str(e)}")
            return []
