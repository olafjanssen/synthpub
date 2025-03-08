"""
Gmail connector for fetching email content from Gmail inbox.
"""
import os
import json
import base64
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlparse
from .feed_connector import FeedConnector
from utils.logging import error

# Gmail API configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = Path("../creds/client_secret_675383632896-e6khlbtubtdo80f9v877kkqkore1mp7e.apps.googleusercontent.com.json").resolve()
TOKEN_FILE = Path("../creds/gmail_token.json").resolve()

def get_gmail_service():
    """Initialize and return Gmail service with proper authentication."""
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'r') as token:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Refresh or create new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, 
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_email_content(message: Dict) -> str:
    """Extract readable content from email message."""
    if 'payload' not in message:
        return ""
    
    # Get email body
    if 'parts' in message['payload']:
        parts = message['payload']['parts']
        content = ""
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    content += base64.urlsafe_b64decode(data).decode()
        return content
    elif 'body' in message['payload']:
        data = message['payload']['body'].get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode()
    
    return ""

def fetch_gmail_content(max_results: int = 50) -> List[Dict[str, str]]:
    """
    Fetch content from recent Gmail messages.
    
    Args:
        max_results: Maximum number of emails to fetch
        
    Returns:
        List of dictionaries containing email content and metadata
    """
    try:
        service = get_gmail_service()
        
        # Get list of messages
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        email_contents = []
        
        for message in messages:
            # Get just basic message info for preview, mark for further processing
            msg_id = message['id']
            email_contents.append({
                'url': f"gmail://message/{msg_id}",
                'content': f"Email message {msg_id}",
                'type': 'email',
                'needs_further_processing': True  # Mark for further processing
            })
        
        return email_contents
        
    except Exception as e:
        error("GMAIL", "Content fetch failed", f"Error fetching Gmail content: {str(e)}")
        return [] 

class GmailConnector(FeedConnector):
    # Cache Gmail listings for 15 minutes
    cache_expiration = 15 * 60
    
    @staticmethod
    def can_handle(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme == 'gmail'
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        try:
            # If this is a specific message URL, fetch the full message
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            
            if len(path_parts) > 1 and path_parts[1] == 'message' and len(path_parts) > 2:
                msg_id = path_parts[2]
                # This would fetch an individual message - implement as needed
                # For now, return an empty message with no further processing
                return [{
                    'url': url,
                    'content': f"Email message {msg_id} content would go here",
                    'type': 'email',
                    'needs_further_processing': False
                }]
            else:
                # For the gmail:// URL, fetch the message list
                return fetch_gmail_content()
        except Exception as e:
            error("GMAIL", "Content fetch failed", f"Error fetching Gmail content: {str(e)}")
            return []

GmailConnector.connect_signals()