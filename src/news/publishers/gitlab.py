"""GitLab publisher for committing content to GitLab repositories."""
from urllib.parse import urlparse
import base64
import os
import requests
from .publisher_interface import Publisher
from api.models.topic import Topic
from api.db.article_db import get_article
from dotenv import load_dotenv

def parse_gitlab_url(url: str) -> tuple[str, str, str]:
    """
    Parse a gitlab:// URL and return project components.
    Example URL: gitlab://gitlab_host/project_id/branch/path/to/file.md
    """
    if not url.startswith("gitlab://"):
        raise ValueError("URL must start with gitlab://")
        
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    print(f"Parsed: {parsed}")
    
    if len(parts) < 3:
        raise ValueError("URL must include host, project, branch, and file path")
    
    host = parsed.netloc
    project_id = parts[0]
    branch = parts[1]
    file_path = "/".join(parts[2:])
    
    return host, project_id, branch, file_path

class GitLabPublisher(Publisher):
    def API_BASE(host):
        return f"https://{host}/api/v4"
    
    load_dotenv()
    TOKEN = os.getenv('GITLAB_TOKEN')
    if not TOKEN:
        raise ValueError("GITLAB_TOKEN environment variable not found. Please add it to your .env file.")

    @staticmethod
    def can_handle(url: str) -> bool:
        return url.startswith("gitlab://")
    
    @staticmethod
    def publish_content(url: str, topic: Topic) -> bool:
        if not GitLabPublisher.TOKEN:
            raise ValueError("GITLAB_TOKEN environment variable not set")
            
        try:
            # Parse the GitLab URL components
            host, project_id, branch, file_path = parse_gitlab_url(url)
            
            # Get the article content
            article = get_article(topic.article)
            content = article.content
            
            # Encode content in base64 (required by GitLab API)
            content_base64 = base64.b64encode(content.encode()).decode()
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {GitLabPublisher.TOKEN}",
                "Content-Type": "application/json"
            }
            # URL encode the file path for GitLab API
            encoded_path = requests.utils.quote(file_path, safe='')
            commit_url = f"{GitLabPublisher.API_BASE(host)}/projects/{project_id}/repository/files/{encoded_path}?ref={branch}"
            print(f"Publishing to {commit_url}")

            # Check if file exists
            response = requests.get(commit_url, headers=headers)
            file_exists = response.status_code == 200
            
            print(f"Response: {response}")

            # Prepare commit data
            commit_data = {
                "branch": branch,
                "content": content_base64,
                "commit_message": f"Update {file_path} via publisher",
                "encoding": "base64"
            }
            
            print(f"Commit data: {commit_data}")
            
            # Create or update file
            if file_exists:
                response = requests.put(commit_url, headers=headers, json=commit_data)
            else:
                response = requests.post(commit_url, headers=headers, json=commit_data)
            
            print(f"Response: {response}")

            return response.status_code in (200, 201)
            
        except Exception as e:
            print(f"Error publishing to GitLab {url}: {str(e)}")
            return False
