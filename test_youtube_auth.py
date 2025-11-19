"""
Simple script to test YouTube authentication.
This will trigger the OAuth flow and open a browser window.
"""

import os
from pathlib import Path
from uploaders.youtube_uploader import YouTubeUploader

print("=" * 60)
print("YouTube Authentication Test")
print("=" * 60)

# Check if client secrets file exists
client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE")
if not client_secrets_file:
    print("\n[ERROR] YOUTUBE_CLIENT_SECRETS_FILE not set in .env")
    exit(1)

# Resolve path
secrets_path = Path(client_secrets_file)
if not secrets_path.is_absolute():
    secrets_path = Path(__file__).parent / secrets_path

print(f"\nChecking client secrets file...")
print(f"  Path: {secrets_path}")
if secrets_path.exists():
    print(f"  [OK] File exists")
else:
    print(f"  [ERROR] File not found!")
    print(f"\nPlease make sure the file is at: {secrets_path}")
    exit(1)

print("\n" + "=" * 60)
print("Starting authentication...")
print("=" * 60)
print("\n[INFO] A browser window will open shortly.")
print("       Please sign in with your Google account and grant permissions.")
print("       After you complete the sign-in, this script will continue.\n")

try:
    uploader = YouTubeUploader()
    success = uploader.authenticate()

    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] Authentication successful!")
        print("=" * 60)
        print("\nYour YouTube token has been saved to:")
        print("  storage/tokens/youtube_token.json")
        print("\nYou can now upload videos to YouTube using:")
        print("  python process.py --input video.mp4 --upload")
    else:
        print("\n" + "=" * 60)
        print("[FAILED] Authentication failed")
        print("=" * 60)
        print("\nPlease check the error messages above.")
except KeyboardInterrupt:
    print("\n\nAuthentication canceled by user.")
except Exception as e:
    print(f"\n\nError: {e}")
    import traceback
    traceback.print_exc()

