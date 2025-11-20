"""
Google Drive uploader for Instagram video URLs.

This module uploads videos to Google Drive and makes them publicly accessible
so they can be used with Instagram Graph API (which requires video_url).
"""

import os
import io
from pathlib import Path
from typing import Optional, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import config


class GoogleDriveUploader:
    """
    Uploads videos to Google Drive and makes them publicly accessible.
    """
    
    # Google Drive API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',  # Upload files
        'https://www.googleapis.com/auth/drive'  # Full access (for making public)
    ]
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            creds = None
            token_file = config.BASE_DIR / "storage" / "tokens" / "drive_token.json"
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
                    client_secrets_file = os.getenv("GOOGLE_DRIVE_CLIENT_SECRETS_FILE")
                    if not client_secrets_file:
                        # Try using YouTube client secrets (same Google account)
                        client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE")
                    
                    if not client_secrets_file:
                        print("  Error: GOOGLE_DRIVE_CLIENT_SECRETS_FILE or YOUTUBE_CLIENT_SECRETS_FILE not set")
                        print("  You can use the same client_secrets.json as YouTube")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        client_secrets_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next time
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            self.service = build('drive', 'v3', credentials=creds)
            self.authenticated = True
            print(f"  [OK] Authenticated with Google Drive API")
            return True
            
        except Exception as e:
            print(f"  Error authenticating with Google Drive: {e}")
            return False
    
    def upload_video_and_get_url(
        self,
        video_path: Path,
        folder_name: str = "Instagram Videos"
    ) -> Optional[str]:
        """
        Upload video to Google Drive and return publicly accessible URL.
        
        Args:
            video_path: Path to video file
            folder_name: Name of folder in Google Drive to upload to
            
        Returns:
            Public URL to the video file, or None if failed
        """
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        try:
            # Step 1: Create or get folder
            print(f"  Creating/finding Google Drive folder: {folder_name}...")
            folder_id = self._get_or_create_folder(folder_name)
            
            if not folder_id:
                print("  Error: Could not create/find folder")
                return None
            
            # Step 2: Upload video file
            print(f"  Uploading video to Google Drive...")
            file_metadata = {
                'name': video_path.name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(
                str(video_path),
                mimetype='video/mp4',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            print(f"  [OK] Video uploaded to Google Drive (ID: {file_id})")
            
            # Step 3: Make file publicly accessible
            print(f"  Making file publicly accessible...")
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            # Step 4: Get direct download URL
            # Instagram needs a direct download URL that it can access
            # We'll use webContentLink which is the direct download link
            
            file_info = self.service.files().get(
                fileId=file_id,
                fields='webContentLink, webViewLink, mimeType, size'
            ).execute()
            
            # Use webContentLink - this is the direct download URL
            web_content_link = file_info.get('webContentLink')
            
            if web_content_link:
                # Remove the "&confirm=t" parameter if present (causes issues)
                # webContentLink format: https://drive.google.com/uc?id=FILE_ID&export=download
                public_url = web_content_link.split('&confirm=')[0]
                print(f"  [OK] Using direct download URL: {public_url[:60]}...")
                return public_url
            
            # Fallback: Construct direct download URL manually
            # Format: https://drive.google.com/uc?id=FILE_ID&export=download
            direct_url = f"https://drive.google.com/uc?id={file_id}&export=download"
            print(f"  [OK] Using constructed direct URL: {direct_url[:60]}...")
            return direct_url
                
        except HttpError as e:
            print(f"  Error uploading to Google Drive: {e}")
            return None
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_or_create_folder(self, folder_name: str) -> Optional[str]:
        """
        Get existing folder or create new one in Google Drive.
        
        Args:
            folder_name: Name of the folder
            
        Returns:
            Folder ID, or None if failed
        """
        try:
            # Check if folder already exists
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            print(f"  Error creating folder: {e}")
            return None
    
    def upload_video_for_backup(
        self,
        video_path: Path,
        folder_name: str = "Instagram Videos Backup"
    ) -> Optional[str]:
        """
        Upload video to Google Drive for backup/storage (not made public).
        
        Args:
            video_path: Path to video file
            folder_name: Name of folder in Google Drive to upload to
            
        Returns:
            Google Drive file ID, or None if failed
        """
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        try:
            # Step 1: Create or get folder
            print(f"  Uploading to Google Drive for backup...")
            folder_id = self._get_or_create_folder(folder_name)
            
            if not folder_id:
                print("  Error: Could not create/find folder")
                return None
            
            # Step 2: Upload video file (private, not public)
            file_metadata = {
                'name': video_path.name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(
                str(video_path),
                mimetype='video/mp4',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name'
            ).execute()
            
            file_id = file.get('id')
            print(f"  [OK] Video backed up to Google Drive (ID: {file_id})")
            return file_id
                
        except HttpError as e:
            print(f"  Error uploading to Google Drive: {e}")
            return None
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive (optional cleanup).
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"  Error deleting file: {e}")
            return False

