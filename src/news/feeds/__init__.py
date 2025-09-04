"""Feed connector initialization."""

from .arxiv import ArxivConnector
from .file import FileConnector
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
    GitLabGroupConnector,
    GitLabRepoConnector,
    RSSConnector,
    WebConnector,
    YouTubeConnector,
    ArxivConnector,
]

# Note: We no longer connect signals for connectors here
# The connectors are now accessed directly through the CONNECTORS list
