"""Publisher connector initialization."""
from .file import FilePublisher

# List of all connector classes
PUBLISHERS = [
    FilePublisher,
]

# Connect signals for all publishers
for publisher in PUBLISHERS:
    publisher.connect_signals()
