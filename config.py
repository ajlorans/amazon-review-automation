"""
Configuration module for Amazon Review Video Processor.

This module handles:
- Reading environment variables from .env file
- Setting up input/output folder paths
- Defining default hashtags and platform-specific settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PATHS
# ============================================================================

# Base directory (project root)
BASE_DIR = Path(__file__).parent

# Input folder for source videos
INPUT_FOLDER = BASE_DIR / "storage" / "inputs"

# Archive folder for processed videos (moved after successful processing)
ARCHIVE_FOLDER = BASE_DIR / "storage" / "archive"

# Logs folder for processing history
LOGS_FOLDER = BASE_DIR / "storage" / "logs"

# Base output folder (will have date subfolders)
OUTPUT_BASE = BASE_DIR / "storage" / "outputs"

# Output folders for each platform (will be created with date subfolders)
OUTPUT_FOLDERS = {
    "youtube": OUTPUT_BASE / "youtube",
    "instagram": OUTPUT_BASE / "instagram",
    "tiktok": OUTPUT_BASE / "tiktok",
}

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

# Amazon creator link (required)
CREATOR_LINK = os.getenv("CREATOR_LINK", "")

if not CREATOR_LINK:
    print("WARNING: CREATOR_LINK not found in .env file. Using placeholder.")
    CREATOR_LINK = "https://amazon.com/shop/YOUR_CREATOR_NAME"

# ============================================================================
# VIDEO SETTINGS
# ============================================================================

# Target vertical format dimensions (9:16 aspect ratio)
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# Default clip duration (in seconds) - can be overridden
DEFAULT_CLIP_DURATION_MIN = 20
DEFAULT_CLIP_DURATION_MAX = 45

# ============================================================================
# CTA OVERLAY SETTINGS
# ============================================================================

# CTA text to overlay on video
CTA_TEXT = f"Shop this product: {CREATOR_LINK}"

# CTA position and styling (will be used in video processing)
CTA_POSITION = "bottom"  # 'top', 'bottom', 'center'
CTA_FONT_SIZE = 40
CTA_TEXT_COLOR = "white"
CTA_BACKGROUND_COLOR = "black"
CTA_OPACITY = 0.8

# ============================================================================
# PLATFORM-SPECIFIC SETTINGS
# ============================================================================

# Default hashtags for each platform
DEFAULT_HASHTAGS = {
    "youtube": [
        "#AmazonReview",
        "#ProductReview",
        "#AmazonFinds",
        "#Unboxing",
        "#Review",
    ],
    "instagram": [
        "#AmazonReview",
        "#ProductReview",
        "#AmazonFinds",
        "#Unboxing",
        "#Review",
        "#Amazon",
        "#Shopping",
    ],
    "tiktok": [
        "#AmazonReview",
        "#ProductReview",
        "#AmazonFinds",
        "#Unboxing",
        "#Review",
        "#Amazon",
        "#Shopping",
        "#FYP",
    ],
}

# Platform-specific metadata templates
def get_youtube_description(video_title: str, hashtags: list) -> str:
    """Generate YouTube description with creator link at the top."""
    hashtag_str = " ".join(hashtags)
    return f"""{CREATOR_LINK}

{video_title}

{hashtag_str}
"""


def get_instagram_caption(video_title: str, hashtags: list) -> str:
    """Generate Instagram caption with creator link as first line."""
    hashtag_str = " ".join(hashtags)
    return f"""{CREATOR_LINK}

{video_title}

{hashtag_str}
"""


def get_tiktok_caption(video_title: str, hashtags: list) -> str:
    """Generate TikTok caption with creator link included."""
    hashtag_str = " ".join(hashtags)
    return f"""{video_title}

Shop: {CREATOR_LINK}

{hashtag_str}
"""


# ============================================================================
# UPLOAD SETTINGS
# ============================================================================

# Enable/disable automatic uploads (set to False to skip uploads)
AUTO_UPLOAD_ENABLED = os.getenv("AUTO_UPLOAD_ENABLED", "false").lower() == "true"

# Upload privacy status (for drafts)
# YouTube: "private" = draft, "unlisted" = ready to publish
# Instagram: Always public when published (no draft option in API)
# TikTok: "SELF_ONLY" = draft, "PUBLIC_TO_EVERYONE" = published
UPLOAD_PRIVACY_STATUS = os.getenv("UPLOAD_PRIVACY_STATUS", "private")

# Platforms to upload to (comma-separated: "youtube,instagram,tiktok" or "all")
UPLOAD_PLATFORMS = os.getenv("UPLOAD_PLATFORMS", "all")
if UPLOAD_PLATFORMS == "all":
    UPLOAD_PLATFORMS = ["youtube", "instagram", "tiktok"]
else:
    UPLOAD_PLATFORMS = [p.strip() for p in UPLOAD_PLATFORMS.split(",")]

# ============================================================================
# INITIALIZATION
# ============================================================================

def get_output_folder(platform: str, date_folder: str = None) -> Path:
    """
    Get output folder for a platform, optionally with date subfolder.
    
    Args:
        platform: Platform name ('youtube', 'instagram', 'tiktok')
        date_folder: Optional date folder (YYYY-MM-DD format). If None, uses today's date.
        
    Returns:
        Path to the output folder
    """
    from datetime import datetime
    
    base_folder = OUTPUT_FOLDERS.get(platform, OUTPUT_BASE / platform)
    
    if date_folder is None:
        date_folder = datetime.now().strftime("%Y-%m-%d")
    
    output_folder = base_folder / date_folder
    output_folder.mkdir(parents=True, exist_ok=True)
    return output_folder


def ensure_output_folders():
    """Create all necessary folders if they don't exist."""
    for folder in OUTPUT_FOLDERS.values():
        folder.mkdir(parents=True, exist_ok=True)
    INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    ARCHIVE_FOLDER.mkdir(parents=True, exist_ok=True)
    LOGS_FOLDER.mkdir(parents=True, exist_ok=True)


# Initialize folders on import
ensure_output_folders()

