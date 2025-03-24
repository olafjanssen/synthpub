"""Publisher connector initialization."""

from .file import FilePublisher
from .ftp import FTPPublisher
from .gitlab import GitLabPublisher

# List of all connector classes
PUBLISHERS = [
    FilePublisher,
    GitLabPublisher,
    FTPPublisher,
]

# Connect signals for all publishers
for publisher in PUBLISHERS:
    publisher.connect_signals()
