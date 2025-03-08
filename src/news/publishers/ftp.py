"""FTP publisher for uploading content to FTP servers."""
import os
import io
from ftplib import FTP
from urllib.parse import urlparse
from typing import Dict, Tuple
from pathlib import Path
from .publisher_interface import Publisher
from api.models.topic import Topic
from utils.logging import debug, info, error, warning

def get_ftp_credentials():
    """Get FTP credentials from environment variables."""
    username = os.getenv("FTP_USERNAME")
    password = os.getenv("FTP_PASSWORD")
    
    if not username or not password:
        error("FTP", "Missing credentials", "FTP_USERNAME and FTP_PASSWORD environment variables must be set")
        raise ValueError("FTP_USERNAME and FTP_PASSWORD environment variables must be set")
    
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
    
    debug("FTP", "URL parsed", f"Host: {parsed.netloc}, Directory: {directory}, Filename: {filename}")
    return parsed.netloc, directory, filename

class FTPPublisher(Publisher):
    """Publisher for uploading content to FTP servers."""
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if this publisher can handle the given URL."""
        return url.startswith("ftp://")
    
    @staticmethod
    def publish_content(url: str, topic: Topic) -> bool:
        """
        Publish content to an FTP server.
        
        Args:
            url: The FTP URL to publish to
            topic: The topic containing the content to publish
            
        Returns:
            bool: True if publishing succeeded
        """
        try:
            info("FTP", "Publishing content", f"URL: {url}, Topic: {topic.name}")
            host, directory, filename = parse_ftp_url(url)
            username, password = get_ftp_credentials()
            
            # Get the most recent representation
            rep = topic.representations[-1]
            
            # Create a file-like object in memory
            if rep.metadata.get('binary', False):
                # Convert hex string back to bytes
                binary_data = bytes.fromhex(rep.content)
                file_obj = io.BytesIO(binary_data)
                debug("FTP", "Prepared binary content", f"Size: {len(binary_data)} bytes")
            else:
                file_obj = io.BytesIO(rep.content.encode('utf-8'))
                debug("FTP", "Prepared text content", f"Size: {len(rep.content)} chars")

            # Connect to FTP server
            debug("FTP", "Connecting", f"Host: {host}")
            with FTP(host) as ftp:
                ftp.login(username, password)
                debug("FTP", "Logged in", f"Username: {username}")
                
                # Change to the target directory
                try:
                    ftp.cwd(directory)
                    debug("FTP", "Changed directory", directory)
                except:
                    # Create directories if they don't exist
                    info("FTP", "Creating directories", directory)
                    current_dir = "/"
                    for part in directory.strip('/').split('/'):
                        if part:
                            try:
                                ftp.cwd(part)
                            except:
                                ftp.mkd(part)
                                ftp.cwd(part)
                            current_dir = os.path.join(current_dir, part)
                
                # Store the file
                debug("FTP", "Uploading file", filename)
                file_obj.seek(0)  # Rewind to the beginning
                ftp.storbinary(f'STOR {filename}', file_obj)
                
                info("FTP", "Published successfully", f"Type: {rep.type}, Path: {directory}/{filename}")
            
            return True
            
        except Exception as e:
            error("FTP", "Publishing failed", f"URL: {url}, Error: {str(e)}")
            return False 