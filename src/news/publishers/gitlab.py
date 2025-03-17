"""GitLab publisher for committing content to GitLab repositories."""

import os
from urllib.parse import urlparse

import requests

from api.models.topic import Topic
from utils.logging import debug, error, info

from .publisher_interface import Publisher


def get_api_key():
    """Get Gitlab token API key from environment variables"""
    api_key = os.getenv("GITLAB_TOKEN")
    if not api_key:
        error(
            "GITLAB", "Missing API key", "GITLAB_TOKEN environment variable not found"
        )
        raise ValueError("GITLAB_TOKEN environment variable not found in settings")
    debug("GITLAB", "API key loaded", "Token available")
    return api_key


def parse_gitlab_url(url: str) -> tuple[str, str, str]:
    """
    Parse a gitlab:// URL and return project components.
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


class GitLabPublisher(Publisher):
    def API_BASE(host):
        return f"https://{host}/api/v4"

    @staticmethod
    def can_handle(url: str) -> bool:
        return url.startswith("gitlab://")

    @staticmethod
    def publish_content(url: str, topic: Topic) -> bool:
        try:
            info("GITLAB", "Publishing content", f"URL: {url}, Topic: {topic.name}")
            host, project_id, branch, file_path = parse_gitlab_url(url)

            # Get the API base URL
            api_base = GitLabPublisher.API_BASE(host)

            # Get the GitLab token from environment variables
            token = get_api_key()

            # Get the most recent representation
            rep = topic.representations[-1]

            # Prepare the content
            content = rep.content

            # API URLs
            commit_url = f"{api_base}/projects/{project_id}/repository/commits"
            info(
                "GITLAB",
                "Creating commit",
                f"Project: {project_id}, Branch: {branch}, File: {file_path}",
            )

            # Create a commit with the new content
            headers = {"PRIVATE-TOKEN": token, "Content-Type": "application/json"}

            # Build the commit data
            commit_data = {
                "branch": branch,
                "commit_message": f"Update {file_path} via SynthPub",
                "actions": [
                    {"action": "update", "file_path": file_path, "content": content}
                ],
            }
            debug(
                "GITLAB",
                "Commit data prepared",
                f"Message: {commit_data['commit_message']}",
            )

            # Make the request
            response = requests.post(
                commit_url, headers=headers, json=commit_data, timeout=15
            )

            if response.status_code >= 200 and response.status_code < 300:
                info(
                    "GITLAB",
                    "Published successfully",
                    f"Status: {response.status_code}, File: {file_path}",
                )
                return True
            else:
                error(
                    "GITLAB",
                    "API error",
                    f"Status: {response.status_code}, Response: {response.text}",
                )
                return False

        except Exception as e:
            error("GITLAB", "Publishing failed", f"URL: {url}, Error: {str(e)}")
            return False
