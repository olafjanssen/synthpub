"""GitLab publisher for committing content to GitLab repositories."""

import requests

from api.models.article import Article
from services.gitlab_service import (get_api_base_url, get_gitlab_token,
                                     parse_gitlab_publisher_url)
from utils.logging import debug, error, info

from .publisher_interface import Publisher
from .utils import process_filename_template


class GitLabPublisher(Publisher):
    @staticmethod
    def can_handle(url: str) -> bool:
        return url.startswith("gitlab://")

    @staticmethod
    def publish_content(url: str, article: Article) -> bool:
        try:
            info(
                "GITLAB", "Publishing content", f"URL: {url}, Article: {article.title}"
            )
            host, project_id, branch, file_path = parse_gitlab_publisher_url(url)

            # Process filename templates in the path
            # Extract directory and filename components
            file_parts = file_path.split("/")
            directory = "/".join(file_parts[:-1])
            filename = file_parts[-1]

            # Process the template
            processed_filename = process_filename_template(filename, "GITLAB")

            # Update the path with the processed filename
            if processed_filename != filename:
                file_path = (
                    f"{directory}/{processed_filename}"
                    if directory
                    else processed_filename
                )
                debug("GITLAB", "Path after template processing", file_path)

            # Get the API base URL
            api_base = get_api_base_url(host)

            # Get the GitLab token from environment variables
            token = get_gitlab_token(host)

            # Use the most recent representation if available, otherwise use article content
            if article.representations:
                rep = article.representations[-1]
                content = rep.content
                info("GITLAB", "Using representation", f"Type: {rep.type}")
            else:
                content = article.content
                info(
                    "GITLAB",
                    "Using original article content",
                    f"Article: {article.title}",
                )

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
