"""
Verify TikTok token and check what scopes are actually authorized.
"""

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

access_token = os.getenv("TIKTOK_ACCESS_TOKEN")

if not access_token:
    print("ERROR: TIKTOK_ACCESS_TOKEN not found in .env file")
    print("Please run: python auth_tiktok.py")
    exit(1)

print("=" * 70)
print("TikTok Token Scope Verification")
print("=" * 70)

# Check token validity and get user info
print("\n1. Checking Token Validity...")
print("-" * 70)

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
    exit(1)

# Try to get token info (TikTok doesn't have a token introspection endpoint,
# but we can infer from what works)
print("\n2. Testing Scopes by API Access...")
print("-" * 70)

# Test user.info.basic scope (we already know this works)
print("[OK] user.info.basic scope: WORKING (we can get user info)")

# Test video.upload scope
print("\nTesting video.upload scope...")
test_response = requests.post(
    "https://open.tiktokapis.com/v2/post/publish/video/init/",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json={
        "post_info": {
            "title": "Scope Test",
            "description": "Testing video.upload scope",
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

print(f"Response Status: {test_response.status_code}")

if test_response.status_code == 200:
    print("[OK] video.upload scope: WORKING ✅")
    print("  You can upload videos!")
    data = test_response.json()
    print(f"  Response: {json.dumps(data, indent=2)}")
elif test_response.status_code == 401:
    error_data = test_response.json()
    error_code = error_data.get("error", {}).get("code", "unknown")
    error_msg = error_data.get("error", {}).get("message", "Unknown error")
    
    print(f"[ERROR] video.upload scope: NOT WORKING ❌")
    print(f"  Error Code: {error_code}")
    print(f"  Message: {error_msg}")
    print(f"\n  Full Response: {json.dumps(error_data, indent=2)}")
    
    if error_code == "scope_not_authorized":
        print("\n" + "=" * 70)
        print("DIAGNOSIS")
        print("=" * 70)
        print("\nThe token shows video.upload in the authorization URL,")
        print("but TikTok's API is rejecting it. This can happen if:")
        print("\n  1. Token was just created - may need a few minutes to propagate")
        print("  2. App is in Sandbox mode with restricted access")
        print("  3. Content Publishing API not fully enabled in app settings")
        print("  4. App needs to be submitted for review (even in Sandbox)")
        print("\nTry these steps:")
        print("  1. Wait 2-5 minutes and try again")
        print("  2. Re-run: python auth_tiktok.py (get a fresh token)")
        print("  3. Check app settings at https://developers.tiktok.com/")
        print("  4. Verify Content Publishing API is fully enabled")
else:
    print(f"[WARNING] Unexpected response: {test_response.status_code}")
    print(f"Response: {test_response.text}")

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print("\nIf video.upload is not working:")
print("  - The scope might be in the auth URL but not in the actual token")
print("  - TikTok's Sandbox mode may have restrictions")
print("  - You may need to wait a few minutes for token to fully activate")
print("  - Try getting a fresh token: python auth_tiktok.py")

