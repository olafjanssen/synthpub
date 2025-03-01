"""FTP publisher for uploading content to FTP servers."""
import os
import io
from ftplib import FTP
from urllib.parse import urlparse
from typing import Dict, Tuple
from pathlib import Path
from .publisher_interface import Publisher
from api.models.topic import Topic

def get_ftp_credentials():
    """Get FTP credentials from environment variables."""
    username = os.getenv("FTP_USERNAME")
    password = os.getenv("FTP_PASSWORD")
    
    if not username or not password:
        raise ValueError("FTP_USERNAME and FTP_PASSWORD environment variables must be set")
    
    return username, password

def parse_ftp_url(url: str) -> Tuple[str, str, str]:
    """
    Parse an FTP URL and return components.
    Example URL: ftp://ftp.example.com/path/to/file.xml
    
    Returns:
        Tuple containing (host, path, filename)
    """
    if not url.startswith("ftp://"):
        raise ValueError("URL must start with ftp://")
        
    parsed = urlparse(url)
    
    if not parsed.netloc:
        raise ValueError("URL must include a host")
    
    # Split the path into directory and filename
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 1:
        raise ValueError("URL must include a file path")
    
    filename = path_parts[-1]
    directory = "/" + "/".join(path_parts[:-1]) if len(path_parts) > 1 else "/"
    
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
            # Parse the FTP URL
            host, directory, filename = parse_ftp_url(url)
            
            # Get credentials
            username, password = get_ftp_credentials()
            
            # Get the most recent representation
            representation = topic.representations[-1]                
            
            # Determine if binary mode is needed
            is_binary = representation.metadata.get('binary', False)
            
            # Convert content to appropriate format
            if is_binary:
                # Handle binary data (if it's a hex string)
                if isinstance(representation.content, str):
                    content = bytes.fromhex(representation.content)
                else:
                    content = representation.content
            else:
                content = representation.content
            
            # Connect to FTP server
            with FTP(host) as ftp:
                ftp.set_debuglevel(2)
                ftp.set_pasv(False)
                ftp.login(username, password)

                # Navigate to directory
                try:
                    # Try to change to the directory
                    ftp.cwd(directory)
                except:
                    # If directory doesn't exist, create it
                    current_dir = "/"
                    for part in directory.strip('/').split('/'):
                        if part:
                            try:
                                ftp.cwd(part)
                            except:
                                ftp.mkd(part)
                                ftp.cwd(part)
                            current_dir = f"{current_dir}{part}/"

                # Upload the file
                if is_binary:
                    ftp.storbinary(f"STOR {filename}", io.BytesIO(content))
                else:                    
                    # Convert string content to bytes and upload using BytesIO
                    ftp.storlines(f"STOR {filename}", io.BytesIO(content.encode('utf-8')))
            
            return True
            
        except Exception as e:
            print(f"Error publishing to FTP {url}: {str(e)}")
            return False 