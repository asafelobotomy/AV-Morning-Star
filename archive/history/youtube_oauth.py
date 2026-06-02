#!/usr/bin/env python3
"""
YouTube OAuth2 Authentication Module
Handles Google OAuth2 authentication for YouTube access
"""

import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

class YouTubeOAuth:
    """Handles YouTube OAuth2 authentication"""
    
    def __init__(self, credentials_path='youtube_oauth_credentials.json', 
                 token_path='youtube_token.pickle'):
        """
        Initialize OAuth handler
        
        Args:
            credentials_path: Path to OAuth2 client credentials JSON
            token_path: Path to save/load access tokens
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        
    def get_credentials(self):
        """
        Get OAuth2 credentials, prompting for login if needed
        
        Returns:
            Credentials object or None if authentication fails
        """
        # Load existing token if available
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    self.creds = None
            
            # Need to log in
            if not self.creds:
                if not os.path.exists(self.credentials_path):
                    return None
                    
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during OAuth flow: {e}")
                    return None
            
            # Save credentials for next time
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        return self.creds
    
    def is_authenticated(self):
        """Check if user is currently authenticated"""
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
                    return creds and creds.valid
            except:
                return False
        return False
    
    def logout(self):
        """Remove stored credentials"""
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self.creds = None
    
    def get_access_token(self):
        """Get the current access token string"""
        if self.creds and self.creds.valid:
            return self.creds.token
        return None
    
    def create_default_credentials_file(self):
        """
        Create a template credentials file with instructions
        """
        template = {
            "installed": {
                "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
                "project_id": "your-project-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET",
                "redirect_uris": ["http://localhost"]
            }
        }
        
        instructions = """
# YouTube OAuth2 Setup Instructions

To enable YouTube authentication in AV Morning Star:

1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Go to "Credentials" and create OAuth 2.0 Client ID
5. Choose "Desktop app" as the application type
6. Download the credentials JSON file
7. Replace the content of 'youtube_oauth_credentials.json' with your downloaded file

For detailed instructions, see: https://developers.google.com/youtube/v3/quickstart/python

Note: This app only needs read-only access to YouTube for downloading videos.
Your credentials are stored locally and never shared.
"""
        
        # Save template
        with open(self.credentials_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        # Save instructions
        with open('YOUTUBE_OAUTH_SETUP.txt', 'w') as f:
            f.write(instructions)
        
        return True
