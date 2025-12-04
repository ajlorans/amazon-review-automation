"""
Token Refresh Helper
This script helps refresh expired YouTube and Google Drive tokens.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("Token Refresh Helper")
print("=" * 70)
print("\nThis script will help you refresh expired tokens for:")
print("  1. YouTube")
print("  2. Google Drive (used for backup)")
print()

# Check which tokens need refreshing
youtube_token = Path(__file__).parent / "storage" / "tokens" / "youtube_token.json"
drive_token = Path(__file__).parent / "storage" / "tokens" / "drive_token.json"

print("Checking existing tokens...")
if youtube_token.exists():
    print(f"  [FOUND] YouTube token: {youtube_token}")
else:
    print(f"  [NOT FOUND] YouTube token")

if drive_token.exists():
    print(f"  [FOUND] Google Drive token: {drive_token}")
else:
    print(f"  [NOT FOUND] Google Drive token")

print("\n" + "=" * 70)
print("Refreshing YouTube Token")
print("=" * 70)

try:
    from uploaders.youtube_uploader import YouTubeUploader
    
    youtube_uploader = YouTubeUploader()
    print("\nStarting YouTube authentication...")
    print("A browser window will open for authentication.\n")
    
    success = youtube_uploader.authenticate()
    
    if success:
        print("\n[SUCCESS] YouTube token refreshed!")
    else:
        print("\n[FAILED] YouTube authentication failed")
        print("You may need to delete the old token file and try again:")
        print(f"  Delete: {youtube_token}")
        
except Exception as e:
    print(f"\n[ERROR] YouTube authentication error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Refreshing Google Drive Token")
print("=" * 70)

try:
    from uploaders.google_drive_uploader import GoogleDriveUploader
    
    drive_uploader = GoogleDriveUploader()
    print("\nStarting Google Drive authentication...")
    print("A browser window will open for authentication.\n")
    
    success = drive_uploader.authenticate()
    
    if success:
        print("\n[SUCCESS] Google Drive token refreshed!")
    else:
        print("\n[FAILED] Google Drive authentication failed")
        print("You may need to delete the old token file and try again:")
        print(f"  Delete: {drive_token}")
        
except Exception as e:
    print(f"\n[ERROR] Google Drive authentication error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Token Refresh Complete")
print("=" * 70)
print("\nIf any tokens failed to refresh, you can:")
print("  1. Delete the token file manually")
print("  2. Run this script again")
print("  3. Or run the individual auth scripts:")
print("     - python auth_youtube.py (for YouTube)")
print()

