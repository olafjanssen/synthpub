# codefactor:ignore[security]  # FTP support maintained for legacy systems with documented security risks

"""FTP publisher for uploading content to FTP servers.

WARNING: FTP is an insecure protocol that transmits data and credentials in plain text.
         It is recommended to use SFTP/SCP or other encrypted protocols when possible.
         This publisher is maintained for legacy support only.

         Security considerations:
         - Credentials are transmitted in plain text
         - Data is transmitted in plain text
         - No encryption or integrity verification
         - Vulnerable to man-in-the-middle attacks

         Recommended alternatives:
         - SFTP (SSH File Transfer Protocol)
         - SCP (Secure Copy)
         - HTTPS with client certificates
         - WebDAV over HTTPS
"""
import ftplib
import io
import os
from ftplib import FTP
from typing import Tuple
from urllib.parse import urlparse

from api.models.article import Article
from utils.logging import debug, error, info, warning

from .publisher_interface import Publisher
from .utils import process_filename_template


def get_ftp_credentials():
    """
    Get FTP credentials from environment variables.

    WARNING: FTP transmits credentials in plain text.
             Consider using SFTP/SCP for secure credential transmission.
    """
    username = os.getenv("FTP_USERNAME")
    password = os.getenv("FTP_PASSWORD")

    if not username or not password:
        error(
            "FTP",
            "Missing credentials",
            "FTP_USERNAME and FTP_PASSWORD environment variables must be set",
        )
        raise ValueError(
            "FTP_USERNAME and FTP_PASSWORD environment variables must be set"
        )

    warning(
        "FTP",
        "Security Warning",
        "Using FTP with plain text credentials. Consider using SFTP/SCP instead.",
    )
    debug("FTP", "Credentials loaded", f"Username: {username}")
    return username, password


def parse_ftp_url(url: str) -> Tuple[str, str, str]:
    """
    Parse an FTP URL and return components.
    Example URL: ftp://ftp.example.com/path/to/file.xml

    Returns:
        Tuple containing (host, path, filename)
    """
    if not url.startswith("ftp://"):
        error("FTP", "Invalid URL", f"URL must start with ftp://, got {url}")
        raise ValueError("URL must start with ftp://")

    parsed = urlparse(url)

    if not parsed.netloc:
        error("FTP", "Invalid URL", "URL must include a host")
        raise ValueError("URL must include a host")

    # Split the path into directory and filename
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 1:
        error("FTP", "Invalid URL", "URL must include a file path")
        raise ValueError("URL must include a file path")

    filename = path_parts[-1]
    directory = "/" + "/".join(path_parts[:-1]) if len(path_parts) > 1 else "/"

    debug(
        "FTP",
        "URL parsed",
        f"Host: {parsed.netloc}, Directory: {directory}, Filename: {filename}",
    )
    return parsed.netloc, directory, filename


def file_exists_on_ftp(ftp: FTP, filename: str) -> bool:
    """
    Check if a file exists on the FTP server.

    Args:
        ftp: Active FTP connection
        filename: Name of the file to check

    Returns:
        bool: True if file exists, False otherwise
    """
    file_list = []
    ftp.retrlines("NLST", file_list.append)
    return filename in file_list


class FTPPublisher(Publisher):
    """Publisher for uploading content to FTP servers.

    WARNING: This publisher uses the insecure FTP protocol.
             Consider using SFTP/SCP publishers for secure file transfer.
    """

    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this publisher can handle the given URL."""
        return url.startswith("ftp://")

    @staticmethod
    def publish_content(url: str, article: Article) -> bool:
        """
        Publish content to an FTP server.

        WARNING: This method uses the insecure FTP protocol.
                 Consider using SFTP/SCP for secure file transfer.

        Args:
            url: The FTP URL to publish to
            article: The article containing the content to publish

        Returns:
            bool: True if publishing succeeded
        """
        try:
            warning(
                "FTP",
                "Security Warning",
                "Using insecure FTP protocol. Consider using SFTP/SCP instead.",
            )
            info("FTP", "Publishing content", f"URL: {url}, Article: {article.title}")
            host, directory, filename = parse_ftp_url(url)

            # Process filename templates (e.g., replace {date} with current date)
            filename = process_filename_template(filename, "FTP")

            username, password = get_ftp_credentials()

            # Use the most recent representation if available, otherwise use article content
            if article.representations:
                rep = article.representations[-1]
                content = rep.content
                is_binary = rep.metadata.get("binary", False)
                info("FTP", "Using representation", f"Type: {rep.type}")
            else:
                content = article.content
                is_binary = False
                info(
                    "FTP", "Using original article content", f"Article: {article.title}"
                )

            # Create a file-like object in memory
            if is_binary:
                # Convert hex string back to bytes
                binary_data = bytes.fromhex(content)
                file_obj = io.BytesIO(binary_data)
                debug(
                    "FTP", "Prepared binary content", f"Size: {len(binary_data)} bytes"
                )
            else:
                file_obj = io.BytesIO(content.encode("utf-8"))
                debug("FTP", "Prepared text content", f"Size: {len(content)} chars")

            # Connect to FTP server
            debug("FTP", "Connecting", f"Host: {host}")
            with FTP(host) as ftp:
                ftp.set_debuglevel(2)
                ftp.set_pasv(True)
                ftp.login(username, password)
                debug("FTP", "Logged in", f"Username: {username}")

                # Change to the target directory
                try:
                    ftp.cwd(directory)
                    debug("FTP", "Changed directory", directory)
                except (
                    ftplib.error_perm,
                    ftplib.error_proto,
                    ftplib.error_reply,
                    ftplib.error_temp,
                ):
                    # Create directories if they don't exist
                    info("FTP", "Creating directories", directory)
                    current_dir = "/"
                    for part in directory.strip("/").split("/"):
                        if part:
                            try:
                                ftp.cwd(part)
                            except (
                                ftplib.error_perm,
                                ftplib.error_proto,
                                ftplib.error_reply,
                                ftplib.error_temp,
                            ):
                                ftp.mkd(part)
                                ftp.cwd(part)
                            current_dir = os.path.join(current_dir, part)

                # Delete existing file if it exists
                if file_exists_on_ftp(ftp, filename):
                    debug("FTP", "Deleting existing file", filename)
                    try:
                        ftp.delete(filename)
                        info("FTP", "Deleted existing file", filename)
                    except (
                        ftplib.error_perm,
                        ftplib.error_proto,
                        ftplib.error_reply,
                    ) as e:
                        warning(
                            "FTP",
                            "Failed to delete existing file",
                            f"File: {filename}, Error: {str(e)}",
                        )

                # Store the file
                debug("FTP", "Uploading file", filename)
                file_obj.seek(0)  # Rewind to the beginning
                ftp.storbinary(f"STOR {filename}", file_obj)

                info(
                    "FTP",
                    "Published successfully",
                    f"Path: {directory}/{filename}",
                )

            return True

        except Exception as e:
            error("FTP", "Publishing failed", f"URL: {url}, Error: {str(e)}")
            return False
