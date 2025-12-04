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
        # Storage preference: s3 > google_drive > direct
        self.storage_type = os.getenv("INSTAGRAM_STORAGE_TYPE", "s3").lower()  # "s3", "google_drive", or "direct"
        self.last_s3_key = None  # Store S3 key for cleanup
    
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
                error_data = response.json() if response.text else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"  Error: Invalid access token - {response.status_code}")
                print(f"  Error message: {error_message}")
                print(f"\n  Your Instagram access token has expired or is invalid.")
                print(f"  Instagram tokens expire after 60 days.")
                print(f"\n  To get a new token:")
                print(f"  1. Go to: https://developers.facebook.com/tools/explorer/")
                print(f"  2. Select your App from the dropdown")
                print(f"  3. Click 'Generate Access Token'")
                print(f"  4. Select permissions: instagram_basic, instagram_content_publish")
                print(f"  5. Click the 'i' icon next to token → 'Open in Access Token Tool'")
                print(f"  6. Click 'Extend Access Token' to get a 60-day token")
                print(f"  7. Copy the token and update INSTAGRAM_ACCESS_TOKEN in your .env file")
                return False
                
        except Exception as e:
            print(f"  Error authenticating with Instagram: {e}")
            return False
    
    def validate_video_file(self, video_path: Path) -> bool:
        """
        Validate video file meets Instagram Reels requirements.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if valid, False otherwise
        """
        # Check base validation (file exists, etc.)
        if not super().validate_video_file(video_path):
            return False
        
        # Check file size (Instagram Reels: max 100MB)
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 100:
            print(f"  Error: File size ({file_size_mb:.1f}MB) exceeds Instagram Reels limit (100MB)")
            print(f"  Suggestion: The video was encoded with dynamic bitrate, but it's still too large.")
            print(f"  This may happen with very long videos. Consider:")
            print(f"    - The video may need to be split into shorter segments")
            print(f"    - Or reduce the video quality further")
            return False
        
        # Check video duration (Instagram Reels: 15-90 seconds)
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(str(video_path)) as clip:
                duration = clip.duration
                if duration < 15:
                    print(f"  Error: Video duration ({duration:.1f}s) is too short for Instagram Reels (min 15s)")
                    return False
                if duration > 90:
                    print(f"  Error: Video duration ({duration:.1f}s) exceeds Instagram Reels limit (max 90s)")
                    return False
        except ImportError:
            # moviepy not available, skip duration check
            pass
        except Exception as e:
            print(f"  Warning: Could not check video duration: {e}")
            # Continue anyway - duration check is not critical
        
        return True
    
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list = None,
        privacy_status: str = "private"
    ) -> Optional[Dict]:
        """
        Upload video to Instagram as a reel using direct upload.
        
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
            # Use description as caption (hashtags are already included in description from metadata)
            caption = description
            # Don't add tags again - they're already in the description from get_instagram_caption()
            
            # Step 1: Upload to Google Drive for backup (always do this)
            print(f"  Uploading video to Google Drive for backup...")
            try:
                from .google_drive_uploader import GoogleDriveUploader
                drive_uploader = GoogleDriveUploader()
                drive_file_id = drive_uploader.upload_video_for_backup(video_path)
                if drive_file_id:
                    print(f"  [OK] Video backed up to Google Drive")
                else:
                    print(f"  Warning: Google Drive backup failed, continuing anyway...")
            except ImportError:
                print(f"  Warning: Google Drive uploader not available, skipping backup")
            except Exception as e:
                print(f"  Warning: Google Drive backup failed: {e}, continuing anyway...")
            
            # Step 2: Get video URL for Instagram (upload to S3)
            video_url = None
            self.last_s3_key = None  # Reset for cleanup tracking
            
            if self.storage_type == "s3":
                print(f"  Uploading video to AWS S3 for Instagram...")
                try:
                    from .s3_uploader import S3Uploader
                    s3_uploader = S3Uploader()
                    video_url = s3_uploader.upload_video_and_get_url(video_path)
                    
                    if not video_url:
                        print(f"  Error: Failed to upload to S3")
                        return None
                    
                    # Store S3 key for cleanup
                    self.last_s3_key = getattr(s3_uploader, 'last_uploaded_key', None)
                    print(f"  [OK] Video uploaded to S3, got public URL")
                except ImportError:
                    print(f"  Error: S3 uploader not available")
                    print(f"  Install: pip install boto3")
                    print(f"  Falling back to Google Drive...")
                    self.storage_type = "google_drive"
                except Exception as e:
                    print(f"  Error uploading to S3: {e}")
                    print(f"  Falling back to Google Drive...")
                    self.storage_type = "google_drive"
            
            if self.storage_type == "google_drive" and not video_url:
                print(f"  Uploading video to Google Drive for Instagram URL...")
                try:
                    from .google_drive_uploader import GoogleDriveUploader
                    drive_uploader = GoogleDriveUploader()
                    video_url = drive_uploader.upload_video_and_get_url(video_path)
                    
                    if not video_url:
                        print(f"  Error: Failed to upload to Google Drive")
                        return None
                    
                    print(f"  [OK] Video uploaded to Google Drive, got public URL")
                except ImportError:
                    print(f"  Error: Google Drive uploader not available")
                    print(f"  Install: pip install google-api-python-client google-auth-oauthlib")
                    return None
                except Exception as e:
                    print(f"  Error uploading to Google Drive: {e}")
                    return None
            
            if not video_url:
                print(f"  Error: No video URL available")
                return None
            
            # Step 3: Create Instagram media container with video URL
            print(f"  Creating Instagram Reel container...")
            
            # Instagram Graph API endpoint for creating media
            upload_url = f"{self.api_base}/{self.instagram_account_id}/media"
            
            if video_url:
                # Use video URL (from Google Drive)
                data = {
                    'media_type': 'REELS',
                    'video_url': video_url,
                    'caption': caption,
                    'share_to_feed': 'true'
                }
                
                params = {
                    'access_token': self.access_token
                }
                
                response = requests.post(upload_url, data=data, params=params)
            else:
                # Try direct file upload (usually doesn't work)
                with open(video_path, 'rb') as video_file:
                    files = {
                        'video_file': (video_path.name, video_file, 'video/mp4')
                    }
                    
                    data = {
                        'media_type': 'REELS',
                        'caption': caption,
                        'share_to_feed': 'true'
                    }
                    
                    params = {
                        'access_token': self.access_token
                    }
                    
                    response = requests.post(
                        upload_url,
                        files=files,
                        data=data,
                        params=params
                    )
            
            if response.status_code != 200:
                print(f"  Error creating media container: {response.status_code}")
                print(f"  Response: {response.text}")
                
                error_data = response.json() if response.text else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                if 'video_url' in error_message.lower() and not video_url:
                    print(f"  Error: Instagram requires video_url parameter")
                    print(f"  Enable Google Drive upload by setting INSTAGRAM_USE_GOOGLE_DRIVE=true in .env")
                    return None
                
                return None
            
            container_data = response.json()
            container_id = container_data.get('id')
            
            if not container_id:
                print(f"  Error: No container ID in response")
                print(f"  Response: {container_data}")
                return None
            
            print(f"  [OK] Media container created: {container_id}")
            
            # Step 2: Check container status until it's ready
            print(f"  Waiting for video processing...")
            max_attempts = 30  # Wait up to 5 minutes (10 seconds * 30)
            attempt = 0
            status_checked = False  # Track if we successfully checked status at least once
            
            while attempt < max_attempts:
                status_response = requests.get(
                    f"{self.api_base}/{container_id}",
                    params={
                        'access_token': self.access_token,
                        'fields': 'status_code,status'  # error field doesn't exist on MediaBuilder
                    }
                )
                
                if status_response.status_code == 200:
                    status_checked = True  # We successfully checked status
                    status_data = status_response.json()
                    status_code = status_data.get('status_code')
                    status_message = status_data.get('status', '')
                    
                    if status_code == 'FINISHED':
                        print(f"  [OK] Video processed successfully!")
                        print(f"  Status details: {status_data}")
                        
                        # Step 3: Publish the reel (required for it to appear in Instagram)
                        # Instagram Reels need to be published to appear, even as drafts
                        print(f"  Publishing reel (container ID: {container_id})...")
                        publish_url = f"{self.api_base}/{self.instagram_account_id}/media_publish"
                        publish_params = {
                            'creation_id': container_id,
                            'access_token': self.access_token
                        }
                        
                        print(f"  Publish URL: {publish_url}")
                        print(f"  Publish params: creation_id={container_id}")
                        
                        publish_response = requests.post(publish_url, params=publish_params)
                        
                        print(f"  Publish response status: {publish_response.status_code}")
                        print(f"  Publish response: {publish_response.text[:200]}...")
                        
                        if publish_response.status_code == 200:
                            publish_result = publish_response.json()
                            media_id = publish_result.get('id')
                            print(f"  [OK] Reel published successfully!")
                            print(f"  Media ID: {media_id}")
                            
                            # Cleanup S3 file if upload was successful and cleanup is enabled
                            if self.last_s3_key:
                                cleanup_enabled = os.getenv("INSTAGRAM_CLEANUP_S3", "true").lower() == "true"
                                if cleanup_enabled:
                                    try:
                                        from .s3_uploader import S3Uploader
                                        s3_uploader = S3Uploader()
                                        if s3_uploader.authenticate():
                                            s3_uploader.delete_file(self.last_s3_key)
                                    except Exception as cleanup_error:
                                        print(f"  Warning: Could not cleanup S3 file: {cleanup_error}")
                            
                            return {
                                'container_id': container_id,
                                'media_id': media_id,
                                'status': 'published',
                                'platform': 'instagram',
                                'note': 'Reel published successfully. Check Instagram app.'
                            }
                        else:
                            print(f"  Warning: Could not publish reel: {publish_response.status_code}")
                            print(f"  Response: {publish_response.text}")
                            print(f"  Container ID: {container_id}")
                            print(f"  Note: Container is ready but not published. You may need to publish manually.")
                            
                            # Still cleanup S3 file
                            if self.last_s3_key:
                                cleanup_enabled = os.getenv("INSTAGRAM_CLEANUP_S3", "true").lower() == "true"
                                if cleanup_enabled:
                                    try:
                                        from .s3_uploader import S3Uploader
                                        s3_uploader = S3Uploader()
                                        if s3_uploader.authenticate():
                                            s3_uploader.delete_file(self.last_s3_key)
                                    except Exception as cleanup_error:
                                        print(f"  Warning: Could not cleanup S3 file: {cleanup_error}")
                            
                            return {
                                'container_id': container_id,
                                'status': 'ready_not_published',
                                'platform': 'instagram',
                                'note': 'Container ready but publish failed. Check Instagram app or publish manually.'
                            }
                        
                        break
                    elif status_code == 'ERROR':
                        error_msg = status_message or 'Unknown error'
                        print(f"  [ERROR] Video processing failed: {error_msg}")
                        print(f"  Container ID: {container_id}")
                        print(f"  Full response: {status_data}")
                        
                        # Get more detailed error info if available
                        error_data = status_data.get('error', {})
                        if error_data:
                            error_type = error_data.get('type', '')
                            error_code = error_data.get('code', '')
                            error_message = error_data.get('message', error_msg)
                            print(f"  Error Type: {error_type}")
                            print(f"  Error Code: {error_code}")
                            print(f"  Error Message: {error_message}")
                        
                        # Test if S3 URL is accessible
                        if video_url:
                            print(f"\n  Testing S3 URL accessibility...")
                            try:
                                test_response = requests.head(video_url, timeout=10, allow_redirects=True)
                                if test_response.status_code == 200:
                                    print(f"  [OK] S3 URL is accessible (Status: {test_response.status_code})")
                                    print(f"  Content-Type: {test_response.headers.get('Content-Type', 'unknown')}")
                                    print(f"  Content-Length: {test_response.headers.get('Content-Length', 'unknown')} bytes")
                                else:
                                    print(f"  [WARNING] S3 URL returned status {test_response.status_code}")
                                    print(f"  This might be why Instagram can't access the video")
                            except Exception as test_error:
                                print(f"  [WARNING] Could not test S3 URL: {test_error}")
                                print(f"  URL might not be publicly accessible")
                        
                        # Common error causes and solutions
                        print(f"\n  Troubleshooting:")
                        if 'url' in error_msg.lower() or 'access' in error_msg.lower() or 'download' in error_msg.lower():
                            print(f"  - Instagram cannot access the S3 URL")
                            print(f"  - Try: Verify the video is publicly accessible (check bucket policy)")
                            print(f"  - Try: Check the URL in a browser (should download directly)")
                            print(f"  - Try: Verify 'Block all public access' is unchecked in S3 bucket settings")
                            print(f"  - Try: Check bucket policy allows public read access")
                        elif 'format' in error_msg.lower() or 'codec' in error_msg.lower():
                            print(f"  - Video format or codec issue")
                            print(f"  - Try: Re-encode the video to MP4 with H.264 codec")
                        elif 'size' in error_msg.lower() or 'length' in error_msg.lower():
                            print(f"  - Video size or duration issue")
                            print(f"  - Instagram Reels: 15-90 seconds, max 100MB")
                        
                        # Still return the container ID so user can check in Instagram app
                        return {
                            'container_id': container_id,
                            'status': 'error',
                            'error': error_msg,
                            'platform': 'instagram',
                            'note': 'Video container created but processing failed. Check Instagram app or try a different video URL format.'
                        }
                    else:
                        # Still processing: IN_PROGRESS, PUBLISHED, etc.
                        attempt += 1
                        if attempt % 6 == 0:  # Print every minute
                            print(f"  Still processing... (attempt {attempt}/{max_attempts})")
                        time.sleep(10)  # Wait 10 seconds before checking again
                elif status_response.status_code == 400:
                    # 400 error might mean the container doesn't exist or field doesn't exist
                    error_data = status_response.json() if status_response.text else {}
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    
                    # If it's about a field not existing, try without that field
                    if 'nonexisting field' in error_msg.lower():
                        print(f"  Warning: API field issue, retrying with basic fields...")
                        # Retry with just status_code
                        retry_response = requests.get(
                            f"{self.api_base}/{container_id}",
                            params={
                                'access_token': self.access_token,
                                'fields': 'status_code'
                            }
                        )
                        if retry_response.status_code == 200:
                            status_checked = True  # We successfully checked status
                            status_data = retry_response.json()
                            status_code = status_data.get('status_code')
                            # Continue with status check
                            if status_code == 'FINISHED':
                                print(f"  [OK] Video processed successfully!")
                                
                                # Cleanup S3 file if upload was successful and cleanup is enabled
                                if self.last_s3_key:
                                    cleanup_enabled = os.getenv("INSTAGRAM_CLEANUP_S3", "true").lower() == "true"
                                    if cleanup_enabled:
                                        try:
                                            from .s3_uploader import S3Uploader
                                            s3_uploader = S3Uploader()
                                            if s3_uploader.authenticate():
                                                s3_uploader.delete_file(self.last_s3_key)
                                        except Exception as cleanup_error:
                                            print(f"  Warning: Could not cleanup S3 file: {cleanup_error}")
                                
                                break
                            elif status_code == 'ERROR':
                                print(f"  [ERROR] Video processing failed")
                                print(f"  Container ID: {container_id}")
                                break
                            else:
                                # Still processing
                                attempt += 1
                                if attempt % 6 == 0:
                                    print(f"  Still processing... (attempt {attempt}/{max_attempts})")
                                time.sleep(10)
                                continue
                    
                    # If retry didn't work or it's a different error, log and continue
                    if attempt == 0:  # Only print once
                        print(f"  Warning: Error checking status: {status_response.status_code}")
                        print(f"  Response: {error_msg}")
                        print(f"  Will continue checking status...")
                    attempt += 1
                    time.sleep(10)
                    continue
                else:
                    print(f"  Warning: Error checking status: {status_response.status_code}")
                    print(f"  Response: {status_response.text}")
                    # Continue trying instead of breaking
                    attempt += 1
                    time.sleep(10)
                    continue
            
            if attempt >= max_attempts:
                if not status_checked:
                    print(f"  [ERROR] Could not check video processing status")
                    print(f"  Container ID: {container_id}")
                    print(f"  Instagram API returned errors when checking status")
                    print(f"  Check Instagram app manually - video might still be processing")
                    return {
                        'container_id': container_id,
                        'status': 'error',
                        'platform': 'instagram',
                        'note': 'Container created but could not verify processing status. Check Instagram app manually.'
                    }
                else:
                    print(f"  Warning: Video processing timed out, but container was created")
                    print(f"  Container ID: {container_id}")
                    print(f"  Check Instagram app for status - video might still be processing")
                    return {
                        'container_id': container_id,
                        'status': 'timeout',
                        'platform': 'instagram',
                        'note': 'Container created but processing timed out. Check Instagram app or wait longer.'
                    }
            
            # Step 4: Return container info (video is uploaded but not published)
            # Only reach here if status_code == 'FINISHED' and we broke out of loop
            print(f"  [OK] Video uploaded to Instagram!")
            print(f"  Container ID: {container_id}")
            print(f"  Note: Video is uploaded but not published. Check Instagram app to publish.")
            
            return {
                'container_id': container_id,
                'status': 'uploaded',
                'platform': 'instagram',
                'note': 'Video uploaded as draft. Publish from Instagram app.'
            }
            
        except FileNotFoundError:
            print(f"  Error: Video file not found: {video_path}")
            return None
        except Exception as e:
            print(f"  Error uploading to Instagram: {e}")
            import traceback
            traceback.print_exc()
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

