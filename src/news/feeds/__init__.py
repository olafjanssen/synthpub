"""Feed connector initialization."""
from .file import FileConnector
from .gmail import GmailConnector
from .rss import RSSConnector
from .youtube import YouTubeConnector
from .youtube_channel import YouTubeChannelConnector

# List of all connector classes
CONNECTORS = [
    FileConnector,
    GmailConnector,
    RSSConnector,
    YouTubeConnector,
    YouTubeChannelConnector
]

# Connect signals for all connectors
for connector in CONNECTORS:
    connector.connect_signals()
