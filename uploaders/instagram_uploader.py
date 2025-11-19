"""
Instagram Reels uploader using Instagram Graph API.

Requires:
- Facebook App with Instagram Graph API access
- Instagram Business/Creator account
- Long-lived access token
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Optional
import config
from .base_uploader import BaseUploader


class InstagramUploader(BaseUploader):
    """
    Uploader for Instagram Reels.
    
    Uses Instagram Graph API to upload reels as drafts.
    Note: Instagram API requires a two-step process:
    1. Create media container
    2. Publish the container (or leave as draft)
    """
    
    def __init__(self):
        super().__init__("Instagram")
        self.access_token = None
        self.instagram_account_id = None
        self.api_base = "https://graph.instagram.com"
    
    def authenticate(self) -> bool:
        """
        Authenticate with Instagram Graph API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Get access token from environment
            self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
            self.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
            
            if not self.access_token:
                print("  Error: INSTAGRAM_ACCESS_TOKEN not set in .env")
                print("  Please get a long-lived access token from Facebook Graph API Explorer")
                return False
            
            if not self.instagram_account_id:
                print("  Error: INSTAGRAM_ACCOUNT_ID not set in .env")
                print("  This is your Instagram Business Account ID")
                return False
            
            # Verify token is valid
            response = requests.get(
                f"{self.api_base}/me",
                params={"access_token": self.access_token, "fields": "id,username"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  [OK] Authenticated with Instagram API")
                print(f"  Account: {data.get('username', 'N/A')}")
                self.authenticated = True
                return True
            else:
                print(f"  Error: Invalid access token - {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Error authenticating with Instagram: {e}")
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
        Upload video to Instagram as a reel (draft).
        
        Args:
            video_path: Path to video file
            title: Video title (not used in Instagram, but kept for consistency)
            description: Caption/description
            tags: List of hashtags
            privacy_status: Not used for Instagram (always public when published)
            
        Returns:
            Dictionary with container_id and status, or None if failed
        """
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        if not self.validate_video_file(video_path):
            return None
        
        try:
            # Step 1: Create media container
            print(f"  Creating Instagram Reel container...")
            
            # Prepare caption with hashtags
            caption = description
            if tags:
                caption += "\n\n" + " ".join(tags)
            
            # Upload video file first (Instagram requires video URL or direct upload)
            # For direct upload, we need to use the Instagram Graph API upload endpoint
            container_data = {
                "media_type": "REELS",
                "caption": caption,
                "share_to_feed": "true"  # Share to feed as well
            }
            
            # Note: Instagram Graph API requires the video to be uploaded first
            # This is a simplified version - full implementation requires:
            # 1. Upload video to a publicly accessible URL, OR
            # 2. Use Instagram Graph API's video upload endpoint
            
            # For now, we'll create the container (you'll need to upload video separately)
            # In production, you'd upload the video file first, then create container
            
            print("  Note: Instagram Reels upload requires video to be uploaded first")
            print("  This is a placeholder - full implementation needs video upload step")
            
            # Placeholder response
            return {
                'container_id': 'placeholder',
                'status': 'pending',
                'platform': 'instagram',
                'note': 'Full implementation requires video file upload to Instagram servers first'
            }
            
        except Exception as e:
            print(f"  Error uploading to Instagram: {e}")
            return None
    
    def get_upload_status(self, container_id: str) -> Optional[Dict]:
        """
        Get the status of an uploaded reel container.
        
        Args:
            container_id: Instagram container ID
            
        Returns:
            Dictionary with container status information
        """
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        try:
            response = requests.get(
                f"{self.api_base}/{container_id}",
                params={
                    "access_token": self.access_token,
                    "fields": "status_code"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"  Error getting upload status: {e}")
            return None

