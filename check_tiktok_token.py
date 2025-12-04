"""
Check TikTok token and verify scopes.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv("TIKTOK_ACCESS_TOKEN")

if not access_token:
    print("ERROR: TIKTOK_ACCESS_TOKEN not found in .env file")
    print("Please run: python auth_tiktok.py")
    exit(1)

# Show token info (first/last 10 chars for security)
token_preview = f"{access_token[:10]}...{access_token[-10:]}" if len(access_token) > 20 else "***"
print(f"Token preview: {token_preview}")
print(f"Token length: {len(access_token)} characters")
print("\nChecking TikTok token...")
print("-" * 70)

# Check user info (this will tell us if token is valid)
response = requests.get(
    "https://open.tiktokapis.com/v2/user/info/",
    headers={"Authorization": f"Bearer {access_token}"},
    params={"fields": "open_id,union_id,avatar_url,display_name"}
)

if response.status_code == 200:
    data = response.json()
    print("[OK] Token is valid")
    if "data" in data and "user" in data["data"]:
        user = data["data"]["user"]
        print(f"  Display Name: {user.get('display_name', 'N/A')}")
        print(f"  Open ID: {user.get('open_id', 'N/A')}")
else:
    print(f"[ERROR] Token is invalid: {response.status_code}")
    print(f"Response: {response.text}")
    print("\nPlease run: python auth_tiktok.py to get a new token")
    exit(1)

# Try to check scopes by attempting to initialize an upload
print("\nChecking video.upload scope...")
print("-" * 70)

test_response = requests.post(
    "https://open.tiktokapis.com/v2/post/publish/video/init/",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json={
        "post_info": {
            "title": "Test",
            "description": "Test",
            "privacy_level": "SELF_ONLY",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD"
        }
    }
)

if test_response.status_code == 200:
    print("[OK] video.upload scope is authorized!")
    print("  You can upload videos to TikTok")
elif test_response.status_code == 401:
    error_data = test_response.json()
    print(f"[ERROR] Upload test failed: {test_response.status_code}")
    print(f"Full response: {test_response.text}")
    
    if "scope_not_authorized" in str(error_data):
        print("\n[ERROR] video.upload scope is NOT authorized")
        print("  The token does not have permission to upload videos")
        print("\nPossible causes:")
        print("  1. Token was authorized without video.upload scope")
        print("  2. TikTok app may need to be approved/submitted for review")
        print("  3. App may be in 'Sandbox' mode (limited access)")
        print("\nTo fix this:")
        print("  1. Check your TikTok app status at: https://developers.tiktok.com/")
        print("  2. Make sure 'Content Publishing API' is enabled")
        print("  3. If app is in Sandbox, you may need to submit for review")
        print("  4. Run: python auth_tiktok.py and grant ALL permissions")
    else:
        error_code = error_data.get("error", {}).get("code", "unknown")
        error_msg = error_data.get("error", {}).get("message", "Unknown error")
        print(f"\n[ERROR] Authentication failed")
        print(f"  Error code: {error_code}")
        print(f"  Message: {error_msg}")
else:
    print(f"[WARNING] Unexpected response: {test_response.status_code}")
    print(f"Full response: {test_response.text}")

print("\n" + "=" * 70)

