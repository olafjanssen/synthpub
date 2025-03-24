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

