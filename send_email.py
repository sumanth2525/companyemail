"""
Email Sending Module
Sends emails using Gmail API with OAuth2 authentication.
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json


class GmailSender:
    """Handles email sending via Gmail API."""
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, credentials_file: str = 'credentials.json', 
                 token_file: str = 'token.json'):
        """
        Initialize GmailSender.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load OAuth2 token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.sender_email = None
        self._authenticate()
        self._get_sender_email()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_file, self.SCOPES
                )
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.creds = creds  # Store for getting user info
        except Exception as e:
            raise Exception(f"Failed to build Gmail service: {e}")
    
    def _get_sender_email(self):
        """Get the authenticated user's email address."""
        if not self.service:
            return None
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            self.sender_email = profile.get('emailAddress', 'Unknown')
            return self.sender_email
        except Exception as e:
            print(f"Warning: Could not retrieve sender email: {e}")
            self.sender_email = "Authenticated Gmail Account"
            return self.sender_email
    
    def get_sender_email(self) -> str:
        """
        Get the email address that will be used for sending.
        
        Returns:
            Sender email address
        """
        if not self.sender_email:
            self._get_sender_email()
        return self.sender_email or "Unknown"
    
    def create_message(self, to: str, subject: str, body: str, 
                      from_email: str = None) -> Dict:
        """
        Create a MIME message.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (optional, uses authenticated account)
            
        Returns:
            Dictionary with 'raw' base64 encoded message
        """
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        if from_email:
            message['from'] = from_email
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode('utf-8')
        
        return {'raw': raw_message}
    
    def send_email(self, to: str, subject: str, body: str, 
                   from_email: str = None, retry: int = 3) -> Dict:
        """
        Send an email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            from_email: Sender email (optional)
            retry: Number of retry attempts
            
        Returns:
            Dictionary with status information:
            {
                'success': bool,
                'message_id': str or None,
                'error': str or None
            }
        """
        if not self.service:
            return {
                'success': False,
                'message_id': None,
                'error': 'Gmail service not initialized'
            }
        
        # Create message
        try:
            message = self.create_message(to, subject, body, from_email)
        except Exception as e:
            return {
                'success': False,
                'message_id': None,
                'error': f'Failed to create message: {str(e)}'
            }
        
        # Send message with retries
        last_error = None
        for attempt in range(retry):
            try:
                sent_message = self.service.users().messages().send(
                    userId='me', body=message
                ).execute()
                
                message_id = sent_message.get('id', 'unknown')
                
                return {
                    'success': True,
                    'message_id': message_id,
                    'error': None
                }
            
            except HttpError as error:
                last_error = error
                error_details = json.loads(error.content.decode('utf-8'))
                error_message = error_details.get('error', {}).get('message', str(error))
                
                # Don't retry on certain errors
                if error.resp.status in [400, 401, 403]:
                    return {
                        'success': False,
                        'message_id': None,
                        'error': f'Gmail API error: {error_message}'
                    }
                
                if attempt < retry - 1:
                    continue
                else:
                    return {
                        'success': False,
                        'message_id': None,
                        'error': f'Gmail API error after {retry} attempts: {error_message}'
                    }
            
            except Exception as e:
                last_error = e
                if attempt < retry - 1:
                    continue
                else:
                    return {
                        'success': False,
                        'message_id': None,
                        'error': f'Unexpected error after {retry} attempts: {str(e)}'
                    }
        
        return {
            'success': False,
            'message_id': None,
            'error': f'Failed after {retry} attempts: {str(last_error)}'
        }


# Default email template
DEFAULT_EMAIL_TEMPLATE = """Hi,

I hope you're doing well. My name is Sumanth — I came across your work and was really impressed. I'm reaching out to see if there's an opportunity to collaborate, volunteer, or contribute on a project basis.

I have experience in data engineering, automation, and analytics, and I'd be happy to offer support wherever needed.

Thanks,
Sumanth"""

