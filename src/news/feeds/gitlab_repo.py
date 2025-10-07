"""GitLab repository connector for fetching commits and issues from a specific project."""

from typing import Any, Dict, List

from services.gitlab_service import (fetch_commit_details, fetch_issue_details,
                                     fetch_project_commits,
                                     fetch_project_issues,
                                     format_commit_content,
                                     format_issue_content, parse_gitlab_url,
                                     resolve_project_id)
from utils.logging import error, info

from .feed_connector import FeedConnector


class GitLabRepoConnector(FeedConnector):
    """Connector for individual GitLab repositories that fetches commits and issues."""
    
    # Cache repository data for 1 hour
    cache_expiration = 3600
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this connector can handle the given URL."""
        if not url.startswith("gitlab://"):
            return False
        
        try:
            host, path = parse_gitlab_url(url)
            # For repositories, we expect group/project format
            # Path should contain at least one slash (group/project)
            return bool(host and path and "/" in path)
        except ValueError:
            return False
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, Any]]:
        """
        Fetch content from a GitLab repository.
        
        Args:
            url: GitLab repository URL in format gitlab://host/group/project
            
        Returns:
            List of dicts with commit and issue information from the repository
        """
        try:
            host, path = parse_gitlab_url(url)
            
            # Extract project path from URL
            # The path should be in format "group/project" or "group/subgroup/project"
            project_path = path
            
            info("GITLAB_REPO", "Processing repository", f"Host: {host}, Project: {project_path}")
            
            # Resolve project path to project ID
            try:
                project_id = resolve_project_id(host, project_path)
                info("GITLAB_REPO", "Project resolved", f"Path: {project_path} -> ID: {project_id}")
            except ValueError as e:
                error("GITLAB_REPO", "Failed to resolve project", f"Path: {project_path}, Error: {str(e)}")
                return []
            
            all_items = []
            
            # Fetch commits
            try:
                commits = fetch_project_commits(host, project_id)
                for commit in commits:
                    commit_sha = commit.get("id", "")
                    if commit_sha:
                        commit_message = commit.get("message", "")
                        commit_date = commit.get("committed_date", "")
                        commit_author = commit.get("author_name", "Unknown")
                        
                        all_items.append({
                            "url": f"https://{host}/{project_path}/-/commit/{commit_sha}",
                            "content": f"Commit: {commit_message}",
                            "title": f"Commit: {commit_message}",
                            "needs_further_processing": True,  # Mark for individual processing
                            "type": "commit",
                            "project": project_path.split("/")[-1],
                            "author": commit_author,
                            "date": commit_date
                        })
            except Exception as e:
                error("GITLAB_REPO", "Failed to fetch commits", f"Project: {project_path}, Error: {str(e)}")
            
            # Fetch issues
            try:
                issues = fetch_project_issues(host, project_id)
                for issue in issues:
                    issue_number = issue.get("iid", 0)
                    if issue_number:
                        issue_title = issue.get("title", "")
                        issue_date = issue.get("created_at", "")
                        issue_author = issue.get("author", {}).get("name", "Unknown")
                        
                        all_items.append({
                            "url": f"https://{host}/{project_path}/-/issues/{issue_number}",
                            "content": f"Issue #{issue_number}: {issue_title}",
                            "title": f"Issue #{issue_number}: {issue_title}",
                            "needs_further_processing": True,  # Mark for individual processing
                            "type": "issue",
                            "project": project_path.split("/")[-1],
                            "author": issue_author,
                            "date": issue_date
                        })
            except Exception as e:
                error("GITLAB_REPO", "Failed to fetch issues", f"Project: {project_path}, Error: {str(e)}")
            
            # Sort by date (oldest first)
            all_items.sort(key=lambda x: x.get("date", ""), reverse=False)
            
            info("GITLAB_REPO", "URLs collected", f"Total items: {len(all_items)}")
            return all_items
            
        except Exception as e:
            error("GITLAB_REPO", "Fetch failed", f"URL: {url}, Error: {str(e)}")
            return []
