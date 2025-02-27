"""Publisher connector initialization."""
from .file import FilePublisher
from .gitlab import GitLabPublisher
from .ftp import FTPPublisher

# List of all connector classes
PUBLISHERS = [
    FilePublisher,
    GitLabPublisher,
    FTPPublisher,
]

# Connect signals for all publishers
for publisher in PUBLISHERS:
    publisher.connect_signals()
