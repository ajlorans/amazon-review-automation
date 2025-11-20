"""
YouTube Authentication Helper
This script will help you authenticate with YouTube API.
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
print("YouTube Authentication Setup")
print("=" * 70)

# Check client secrets file
client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE")
if not client_secrets_file:
    print("\n[ERROR] YOUTUBE_CLIENT_SECRETS_FILE not found in .env")
    print("Please make sure your .env file has:")
    print("  YOUTUBE_CLIENT_SECRETS_FILE=storage/credentials/youtube_client_secrets.json")
    sys.exit(1)

# Resolve path
secrets_path = Path(client_secrets_file)
if not secrets_path.is_absolute():
    secrets_path = Path(__file__).parent / secrets_path

print(f"\n1. Checking client secrets file...")
print(f"   Path: {secrets_path}")
if secrets_path.exists():
    print(f"   [OK] File found")
else:
    print(f"   [ERROR] File not found at: {secrets_path}")
    sys.exit(1)

# Check token file
token_file = Path(__file__).parent / "storage" / "tokens" / "youtube_token.json"
print(f"\n2. Checking for existing token...")
if token_file.exists():
    print(f"   [INFO] Token file already exists at: {token_file}")
    print(f"   [INFO] If authentication fails, delete this file and try again.")
else:
    print(f"   [INFO] No existing token found - will create new one")

print(f"\n3. Starting authentication...")
print("   " + "-" * 66)
print("   IMPORTANT: A browser window will open!")
print("   Steps:")
print("   1. Sign in with your Google account")
print("   2. If you see 'Access Denied' or '403 error':")
print("      -> Go to Google Cloud Console")
print("      -> APIs & Services > OAuth consent screen")
print("      -> Add your email as a TEST USER")
print("      -> Then try again")
print("   3. You may see 'This app isn't verified' - click 'Advanced' then 'Go to [Your App]'")
print("   4. Grant permissions to access YouTube")
print("   5. After granting permissions, return here")
print("   " + "-" * 66)
print()

try:
    from uploaders.youtube_uploader import YouTubeUploader
    
    uploader = YouTubeUploader()
    print("   [INFO] Initializing OAuth flow...")
    print("   [INFO] Browser should open shortly...\n")
    
    success = uploader.authenticate()
    
    print()
    print("=" * 70)
    if success:
        print("[SUCCESS] Authentication completed!")
        print("=" * 70)
        print(f"\nToken saved to: {token_file}")
        print("\nYou can now upload videos to YouTube!")
        print("\nTo test, run:")
        print("  python process.py --input storage/inputs/amazon-review-labtop.mp4 --upload")
    else:
        print("[FAILED] Authentication failed")
        print("=" * 70)
        print("\nPlease check the error messages above.")
        print("Common issues:")
        print("  - Error 403 / Access Denied:")
        print("    → Your OAuth app is in testing mode")
        print("    → Go to: https://console.cloud.google.com/apis/credentials/consent")
        print("    → Add your email address as a TEST USER")
        print("    → Then run this script again")
        print("  - Browser didn't open: Check firewall/antivirus settings")
        print("  - Permission denied: Make sure you granted all permissions")
        print("  - Invalid credentials: Re-download client_secrets.json from Google Cloud Console")
        
except KeyboardInterrupt:
    print("\n\n[INFO] Authentication canceled by user.")
except Exception as e:
    print(f"\n\n[ERROR] An error occurred: {e}")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting:")
    print("  1. Make sure YouTube Data API v3 is enabled in Google Cloud Console")
    print("  2. Verify your client_secrets.json file is correct")
    print("  3. Check that you have a YouTube channel linked to your Google account")

