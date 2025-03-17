"""Feed connector initialization."""
from .arxiv import ArxivConnector
from .file import FileConnector
from .gmail import GmailConnector
from .rss import RSSConnector
from .web import WebConnector
from .youtube import YouTubeConnector

# List of all connector classes
CONNECTORS = [
    FileConnector,
    GmailConnector,
    RSSConnector,
    WebConnector,
    YouTubeConnector,
    ArxivConnector,
]

# Note: We no longer connect signals for connectors here
# The connectors are now accessed directly through the CONNECTORS list
