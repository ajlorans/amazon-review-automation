"""
Base uploader class with common functionality for all platform uploaders.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class BaseUploader(ABC):
    """
    Base class for platform-specific uploaders.
    
    All uploaders should inherit from this class and implement:
    - authenticate() - Handle OAuth/API authentication
    - upload_video() - Upload video to platform as draft
    - get_upload_status() - Check upload status
    """
    
    def __init__(self, platform_name: str):
        """
        Initialize the uploader.
        
        Args:
            platform_name: Name of the platform (for logging)
        """
        self.platform_name = platform_name
        self.authenticated = False
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list = None,
        privacy_status: str = "private"  # For drafts, usually "private" or "unlisted"
    ) -> Optional[Dict]:
        """
        Upload a video to the platform as a draft.
        
        Args:
            video_path: Path to the video file
            title: Video title
            description: Video description/caption
            tags: List of tags/hashtags
            privacy_status: Privacy status (usually "private" for drafts)
            
        Returns:
            Dictionary with upload result (video_id, status, etc.) or None if failed
        """
        pass
    
    @abstractmethod
    def get_upload_status(self, video_id: str) -> Optional[Dict]:
        """
        Get the status of an uploaded video.
        
        Args:
            video_id: Platform-specific video ID
            
        Returns:
            Dictionary with video status information
        """
        pass
    
    def validate_video_file(self, video_path: Path) -> bool:
        """
        Validate that the video file exists and is readable.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if valid, False otherwise
        """
        if not video_path.exists():
            print(f"  Error: Video file not found: {video_path}")
            return False
        
        if not video_path.is_file():
            print(f"  Error: Path is not a file: {video_path}")
            return False
        
        # Check file size (some platforms have limits)
        file_size_mb = video_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 2000:  # 2GB limit (adjust per platform)
            print(f"  Warning: File size ({file_size_mb:.1f}MB) may exceed platform limits")
        
        return True

