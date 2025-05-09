"""File system publisher for storing content in files."""

from pathlib import Path
from urllib.parse import unquote, urlparse

from api.models.article import Article
from utils.logging import debug, error, info

from .publisher_interface import Publisher
from .utils import process_filename_template


def parse_file_url(url: str) -> Path:
    """Parse a file:// URL and return the filesystem path."""
    if not url.startswith("file://"):
        error("FILE", "Invalid URL", f"URL must start with file://, got {url}")
        raise ValueError("URL must start with file://")

    path = url[7:]  # Remove file://
    return Path(unquote(path))  # Handle URL encoding


class FilePublisher(Publisher):
    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme == "file"

    @staticmethod
    def write_content(path: Path, content: str, is_binary: bool = False) -> None:
        """Write content to file, handling both text and binary data."""
        debug("FILE", "Creating directory", str(path.parent))
        path.parent.mkdir(parents=True, exist_ok=True)

        if is_binary:
            # Convert hex string back to bytes
            debug(
                "FILE",
                "Writing binary content",
                f"Path: {path}, Size: {len(content)//2} bytes",
            )
            binary_data = bytes.fromhex(content)
            with open(path, "wb") as f:
                f.write(binary_data)
        else:
            debug(
                "FILE",
                "Writing text content",
                f"Path: {path}, Size: {len(content)} chars",
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

    @staticmethod
    def publish_content(url: str, article: Article) -> bool:
        try:
            info("FILE", "Publishing content", f"URL: {url}, Article: {article.title}")
            file_path = parse_file_url(url)

            # Process filename templates in the path
            # Extract the filename part for template processing
            filename = file_path.name
            directory = file_path.parent

            # Process the template
            processed_filename = process_filename_template(filename, "FILE")

            # Update the path with the processed filename
            if processed_filename != filename:
                file_path = directory / processed_filename
                debug("FILE", "Path after template processing", str(file_path))

            # Use the most recent representation if available, otherwise use article content
            if article.representations:
                rep = article.representations[-1]
                content = rep.content
                is_binary = rep.metadata.get("binary", False)
                info("FILE", "Using representation", f"Type: {rep.type}")
            else:
                content = article.content
                is_binary = False
                info(
                    "FILE",
                    "Using original article content",
                    f"Article: {article.title}",
                )

            FilePublisher.write_content(file_path, content, is_binary)
            info("FILE", "Published successfully", f"Path: {file_path}")

            return True

        except Exception as e:
            error("FILE", "Publishing failed", f"URL: {url}, Error: {str(e)}")
            return False
