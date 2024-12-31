"""Feed connector initialization."""
from .file import FileConnector
from .gmail import GmailConnector
from .rss import RSSConnector
from .youtube import YouTubeConnector

# List of all connector classes
CONNECTORS = [
    FileConnector,
    GmailConnector,
    RSSConnector,
    YouTubeConnector,
]

# Connect signals for all connectors
for connector in CONNECTORS:
    connector.connect_signals()
