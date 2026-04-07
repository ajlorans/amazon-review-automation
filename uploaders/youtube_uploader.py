"""
YouTube video uploader using YouTube Data API v3.

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
    Uploader for YouTube videos.
    
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
                refresh_failed = False
                if creds and creds.expired and creds.refresh_token:
                    # Try to refresh the token
                    try:
                        print("  Token expired, attempting to refresh...")
                        creds.refresh(Request())
                        print("  [OK] Token refreshed successfully")
                    except Exception as refresh_error:
                        # Refresh failed - token may be revoked or expired
                        print(f"  Token refresh failed: {refresh_error}")
                        print("  Will request new authorization...")
                        refresh_failed = True
                        # Delete the old token file since it's no longer valid
                        if token_file.exists():
                            token_file.unlink()
                            print("  Removed invalid token file")
                
                # If refresh failed or no refresh token available, get new credentials
                if refresh_failed or not creds or not creds.valid:
                    # Get OAuth2 credentials from config
                    client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE")
                    if not client_secrets_file:
                        print("  Error: YOUTUBE_CLIENT_SECRETS_FILE not set in .env")
                        print("  Please download OAuth2 credentials from Google Cloud Console")
                        return False
                    
                    print("  Opening browser for authentication...")
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
        
        # Verify video is in vertical format for Shorts
        try:
            # Use MoviePy 2.x import style (matches process.py)
            from moviepy import VideoFileClip
            with VideoFileClip(str(video_path)) as clip:
                width = clip.w
                height = clip.h
                aspect_ratio = width / height if height > 0 else 0
                print(f"  Video dimensions: {width}x{height} (aspect ratio: {aspect_ratio:.2f})")
                
                # YouTube Shorts should be vertical (9:16 = 0.5625)
                # Accept range 0.5 to 0.6 to account for slight variations
                if aspect_ratio < 0.5 or aspect_ratio > 0.6:
                    print(f"  Warning: Video aspect ratio ({aspect_ratio:.2f}) may not be optimal for YouTube Shorts")
                    print(f"  Expected: ~0.56 (9:16 vertical format)")
                else:
                    print(f"  ✓ Video format is vertical (suitable for YouTube Shorts)")
        except ImportError as e:
            # MoviePy not available - skip verification (upload will still work)
            print(f"  Note: Could not verify video format (MoviePy not available): {e}")
        except Exception as e:
            # Other errors during verification - non-critical
            print(f"  Note: Could not verify video format: {e}")
        
        try:
            # Prepare video metadata for YouTube Shorts
            # Add #Shorts to title to mark as YouTube Short
            shorts_title = title
            if "#Shorts" not in title and "#shorts" not in title:
                shorts_title = f"{title} #Shorts"
            
            # Add "Shorts" to tags if not already present
            shorts_tags = tags.copy() if tags else []
            if "Shorts" not in shorts_tags and "shorts" not in [t.lower() for t in shorts_tags]:
                shorts_tags.append("Shorts")
            
            # Add Shorts indicator to description
            shorts_description = description
            if "#Shorts" not in description and "#shorts" not in description.lower():
                # Add at the beginning of description
                shorts_description = f"#Shorts\n\n{description}"
            
            body = {
                'snippet': {
                    'title': shorts_title,
                    'description': shorts_description,
                    'tags': shorts_tags,
                    'categoryId': '22'  # People & Blogs category
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload as YouTube Short (vertical format, full length)
            # YouTube automatically detects Shorts based on:
            # - Vertical format (9:16 aspect ratio)
            # - #Shorts in title/description
            # - Video characteristics
            
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
                print(f"  [OK] Video uploaded successfully as YouTube Short!")
                print(f"  Video ID: {video_id}")
                print(f"  Status: {privacy_status} (draft)")
                print(f"  URL: https://www.youtube.com/watch?v={video_id}")
                print(f"  Note: YouTube will automatically detect this as a Short based on:")
                print(f"    - Vertical format (9:16 aspect ratio)")
                print(f"    - #Shorts tag in title/description")
                
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

