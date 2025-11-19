"""
YouTube Shorts uploader using YouTube Data API v3.

Requires:
- Google Cloud Project with YouTube Data API v3 enabled
- OAuth2 credentials (client_id, client_secret)
- OAuth2 token file for authentication
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import config
from .base_uploader import BaseUploader


class YouTubeUploader(BaseUploader):
    """
    Uploader for YouTube Shorts.
    
    Uploads videos as private (draft) so they can be reviewed before publishing.
    """
    
    # YouTube API scopes required for uploading
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self):
        super().__init__("YouTube")
        self.service = None
        self.credentials = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API using OAuth2.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            creds = None
            token_file = config.BASE_DIR / "storage" / "tokens" / "youtube_token.json"
            token_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing token if available
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file), self.SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Get OAuth2 credentials from config
                    client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE")
                    if not client_secrets_file:
                        print("  Error: YOUTUBE_CLIENT_SECRETS_FILE not set in .env")
                        print("  Please download OAuth2 credentials from Google Cloud Console")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        client_secrets_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next time
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            self.service = build('youtube', 'v3', credentials=creds)
            self.authenticated = True
            print(f"  [OK] Authenticated with YouTube API")
            return True
            
        except Exception as e:
            print(f"  Error authenticating with YouTube: {e}")
            return False
    
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list = None,
        privacy_status: str = "private"  # "private" = draft, "unlisted" = ready to publish
    ) -> Optional[Dict]:
        """
        Upload video to YouTube as a draft (private).
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            privacy_status: "private" for draft, "unlisted" for ready to publish
            
        Returns:
            Dictionary with video_id and status, or None if failed
        """
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        if not self.validate_video_file(video_path):
            return None
        
        try:
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '22'  # People & Blogs category
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Mark as YouTube Short (if duration <= 60 seconds)
            # Note: YouTube automatically detects Shorts, but we can add #Shorts to title
            if '#Shorts' not in title:
                body['snippet']['title'] = f"{title} #Shorts"
            
            # Upload video
            print(f"  Uploading to YouTube...")
            media = MediaFileUpload(
                str(video_path),
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            insert_request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload with progress tracking
            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    print(f"  Upload progress: {progress}%")
            
            if 'id' in response:
                video_id = response['id']
                print(f"  [OK] Video uploaded successfully!")
                print(f"  Video ID: {video_id}")
                print(f"  Status: {privacy_status} (draft)")
                print(f"  URL: https://www.youtube.com/watch?v={video_id}")
                
                return {
                    'video_id': video_id,
                    'status': privacy_status,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'platform': 'youtube'
                }
            else:
                print(f"  Error: Upload failed - no video ID in response")
                return None
                
        except Exception as e:
            print(f"  Error uploading to YouTube: {e}")
            return None
    
    def get_upload_status(self, video_id: str) -> Optional[Dict]:
        """
        Get the status of an uploaded video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video status information
        """
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        try:
            request = self.service.videos().list(
                part='status,snippet',
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                video = response['items'][0]
                return {
                    'video_id': video_id,
                    'privacy_status': video['status']['privacyStatus'],
                    'upload_status': video['status']['uploadStatus'],
                    'title': video['snippet']['title']
                }
            return None
            
        except Exception as e:
            print(f"  Error getting upload status: {e}")
            return None

