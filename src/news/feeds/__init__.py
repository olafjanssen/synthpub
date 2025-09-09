"""Feed connector initialization."""

from .arxiv import ArxivConnector
from .file import FileConnector
from .github_item import GitHubItemConnector
from .github_repo import GitHubRepoConnector
from .gitlab_group import GitLabGroupConnector
from .gitlab_repo import GitLabRepoConnector
from .gmail import GmailConnector
from .rss import RSSConnector
from .web import WebConnector
from .youtube import YouTubeConnector

# List of all connector classes
CONNECTORS = [
    FileConnector,
    GmailConnector,
    GitHubItemConnector,
    GitHubRepoConnector,
    GitLabGroupConnector,
    GitLabRepoConnector,
    RSSConnector,
    WebConnector,
    YouTubeConnector,
    ArxivConnector,
]

# Note: We no longer connect signals for connectors here
# The connectors are now accessed directly through the CONNECTORS list
