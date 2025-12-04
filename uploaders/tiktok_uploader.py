"""
TikTok video uploader using TikTok Content Publishing API.

Requires:
- TikTok Developer Account
- TikTok App credentials (client_key, client_secret)
- OAuth2 access token
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Optional
import config
from .base_uploader import BaseUploader


class TikTokUploader(BaseUploader):
    """
    Uploader for TikTok videos.
    
    Uses TikTok Content Publishing API to upload videos as drafts.
    Uses push_by_file method (FILE_UPLOAD) - direct file upload.
    This avoids the need for domain verification that pull_by_url requires.
    """
    
    def __init__(self):
        super().__init__("TikTok")
        self.access_token = None
        self.api_base = "https://open.tiktokapis.com/v2"
    
    def authenticate(self) -> bool:
        """
        Authenticate with TikTok API using OAuth2.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Get credentials from environment
            client_key = os.getenv("TIKTOK_CLIENT_KEY")
            client_secret = os.getenv("TIKTOK_CLIENT_SECRET")
            self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
            
            if not client_key or not client_secret:
                print("  Error: TIKTOK_CLIENT_KEY or TIKTOK_CLIENT_SECRET not set in .env")
                print("  Please create a TikTok app at https://developers.tiktok.com/")
                return False
            
            # If no access token, need to get one via OAuth2 flow
            # For now, we'll use a stored access token
            if not self.access_token:
                print("  Error: TIKTOK_ACCESS_TOKEN not set in .env")
                print("  Please complete OAuth2 flow to get access token")
                return False
            
            # Verify token is valid
            response = requests.get(
                f"{self.api_base}/user/info/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"fields": "open_id,union_id,avatar_url,display_name"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Authenticated with TikTok API")
                self.authenticated = True
                return True
            else:
                print(f"  Error: Invalid access token - {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Error authenticating with TikTok: {e}")
            return False
    
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list = None,
        privacy_status: str = "private"
    ) -> Optional[Dict]:
        """
        Upload video to TikTok as a draft.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description/caption
            tags: List of hashtags
            privacy_status: "private" for draft, "public" for published
            
        Returns:
            Dictionary with video_id and status, or None if failed
        """
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        if not self.validate_video_file(video_path):
            return None
        
        try:
            # Step 1: Initialize upload
            print(f"  Initializing TikTok upload...")
            
            # Prepare caption with hashtags
            caption = description
            if tags:
                caption += "\n\n" + " ".join(tags)
            
            # TikTok API requires:
            # 1. Initialize upload (get upload URL)
            # 2. Upload video file to the URL
            # 3. Publish video (or save as draft)
            
            # Using push_by_file method (FILE_UPLOAD) - direct file upload
            # This avoids the need for domain verification that pull_by_url requires
            # Initialize upload
            init_response = requests.post(
                f"{self.api_base}/post/publish/video/init/",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "post_info": {
                        "title": title,
                        "description": caption,
                        "privacy_level": "PUBLIC_TO_EVERYONE" if privacy_status == "public" else "SELF_ONLY",
                        "disable_duet": False,
                        "disable_comment": False,
                        "disable_stitch": False,
                        "video_cover_timestamp_ms": 1000
                    },
                    "source_info": {
                        "source": "FILE_UPLOAD"  # push_by_file method - no domain verification needed
                    }
                }
            )
            
            if init_response.status_code != 200:
                print(f"  Error initializing upload: {init_response.status_code}")
                print(f"  Response: {init_response.text}")
                return None
            
            init_data = init_response.json()
            upload_url = init_data.get("data", {}).get("upload_url")
            publish_id = init_data.get("data", {}).get("publish_id")
            
            if not upload_url:
                print("  Error: No upload URL received")
                return None
            
            # Step 2: Upload video file
            print(f"  Uploading video file...")
            with open(video_path, 'rb') as video_file:
                upload_response = requests.put(
                    upload_url,
                    data=video_file,
                    headers={"Content-Type": "video/mp4"}
                )
            
            if upload_response.status_code not in [200, 204]:
                print(f"  Error uploading file: {upload_response.status_code}")
                return None
            
            # Step 3: Publish (or leave as draft)
            print(f"  Finalizing upload...")
            publish_response = requests.post(
                f"{self.api_base}/post/publish/status/fetch/",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={"publish_id": publish_id}
            )
            
            if publish_response.status_code == 200:
                data = publish_response.json()
                video_id = data.get("data", {}).get("publish_id")
                
                print(f"  [OK] Video uploaded successfully!")
                print(f"  Video ID: {video_id}")
                print(f"  Status: {privacy_status}")
                
                return {
                    'video_id': video_id,
                    'status': privacy_status,
                    'platform': 'tiktok'
                }
            else:
                print(f"  Error finalizing upload: {publish_response.status_code}")
                return None
                
        except Exception as e:
            print(f"  Error uploading to TikTok: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_upload_status(self, video_id: str) -> Optional[Dict]:
        """
        Get the status of an uploaded video.
        
        Args:
            video_id: TikTok video ID (publish_id)
            
        Returns:
            Dictionary with video status information
        """
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        try:
            response = requests.post(
                f"{self.api_base}/post/publish/status/fetch/",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={"publish_id": video_id}
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"  Error getting upload status: {e}")
            return None

