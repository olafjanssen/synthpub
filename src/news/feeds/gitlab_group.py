"""GitLab group connector for fetching commits and issues from all projects in a group."""

from typing import Any, Dict, List

from services.gitlab_service import (fetch_commit_details,
                                     fetch_group_projects, fetch_issue_details,
                                     fetch_project_commits,
                                     fetch_project_issues,
                                     format_commit_content,
                                     format_issue_content, parse_gitlab_url)
from utils.logging import error, info

from .feed_connector import FeedConnector


class GitLabGroupConnector(FeedConnector):
    """Connector for GitLab groups that fetches commits and issues from all projects."""
    
    # Cache group data for 1 hour
    cache_expiration = 3600
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this connector can handle the given URL."""
        if not url.startswith("gitlab://"):
            return False
        
        try:
            host, path = parse_gitlab_url(url)
            # For groups, we expect just the group path (no project name)
            # Groups typically don't have slashes in their path, or if they do, 
            # they represent subgroups. We want to exclude repository URLs.
            path_parts = path.split("/")
            # Group URLs should have 1 or 2 parts (group or group/subgroup)
            # Repository URLs have 3+ parts (group/project or group/subgroup/project)
            return bool(host and path and len(path_parts) <= 2)
        except ValueError:
            return False
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, Any]]:
        """
        Fetch content from a GitLab group.
        
        Args:
            url: GitLab group URL in format gitlab://host/group-path
            
        Returns:
            List of dicts with commit and issue information from all projects in the group
        """
        try:
            host, group_path = parse_gitlab_url(url)
            
            info("GITLAB_GROUP", "Processing group", f"Host: {host}, Group: {group_path}")
            
            # Fetch all projects in the group
            projects = fetch_group_projects(host, group_path, include_subgroups=True)
            
            if not projects:
                info("GITLAB_GROUP", "No projects found", f"Group: {group_path}")
                return []
            
            info("GITLAB_GROUP", "Found projects", f"Count: {len(projects)}")
            
            all_items = []
            
            # Process each project
            for project in projects:
                project_id = project.get("id")
                project_name = project.get("name", "Unknown Project")
                project_path = project.get("path_with_namespace", "")
                
                if not project_id:
                    continue
                
                info("GITLAB_GROUP", "Processing project", f"Name: {project_name}, ID: {project_id}")
                
                # Fetch commits
                commits = fetch_project_commits(host, str(project_id))
                for commit in commits:
                    # Fetch detailed commit information including diff
                    commit_details = fetch_commit_details(host, str(project_id), commit.get("id", ""))
                    if commit_details:
                        commit.update(commit_details)  # Merge detailed info
                    
                    content = format_commit_content(commit, project_name)
                    if content:  # Skip empty content (e.g., merge commits)
                        all_items.append({
                            "url": f"gitlab://{host}/{project_path}/-/commit/{commit.get('id', '')}",
                            "content": content,
                            "title": f"Commit: {commit.get('message', '')}",
                            "needs_further_processing": False,
                            "type": "commit",
                            "project": project_name,
                            "author": commit.get("author_name", "Unknown"),
                            "date": commit.get("committed_date", "")
                        })
                
                # Fetch issues
                issues = fetch_project_issues(host, str(project_id))
                for issue in issues:
                    # Fetch detailed issue information including discussions
                    issue_details = fetch_issue_details(host, str(project_id), issue.get("iid", 0))
                    if issue_details:
                        issue.update(issue_details)  # Merge detailed info
                    
                    content = format_issue_content(issue, project_name)
                    all_items.append({
                        "url": f"gitlab://{host}/{project_path}/-/issues/{issue.get('iid', '')}",
                        "content": content,
                        "title": f"Issue: {issue.get('title', '')}",
                        "needs_further_processing": False,
                        "type": "issue",
                        "project": project_name,
                        "author": issue.get("author", {}).get("name", "Unknown"),
                        "date": issue.get("created_at", "")
                    })
            
            # Sort by date (newest first)
            all_items.sort(key=lambda x: x.get("date", ""), reverse=True)
            
            info("GITLAB_GROUP", "Content fetched", f"Total items: {len(all_items)}")
            return all_items
            
        except Exception as e:
            error("GITLAB_GROUP", "Fetch failed", f"URL: {url}, Error: {str(e)}")
            return []
