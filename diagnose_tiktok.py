"""
Comprehensive TikTok API diagnostic tool.
Checks token, scopes, app configuration, and provides specific fixes.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("TikTok API Diagnostic Tool")
print("=" * 70)

# Get credentials
access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
client_key = os.getenv("TIKTOK_CLIENT_KEY")
client_secret = os.getenv("TIKTOK_CLIENT_SECRET")

print("\n1. Checking Environment Variables...")
print("-" * 70)

if not access_token:
    print("[ERROR] TIKTOK_ACCESS_TOKEN not found in .env")
    print("  Run: python auth_tiktok.py")
    exit(1)
else:
    print("[OK] TIKTOK_ACCESS_TOKEN found")

if not client_key:
    print("[WARNING] TIKTOK_CLIENT_KEY not found")
else:
    print("[OK] TIKTOK_CLIENT_KEY found")

if not client_secret:
    print("[WARNING] TIKTOK_CLIENT_SECRET not found")
else:
    print("[OK] TIKTOK_CLIENT_SECRET found")

# Check token validity
print("\n2. Checking Token Validity...")
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
    print("\nPlease run: python auth_tiktok.py to get a new token")
    exit(1)

# Test upload initialization with detailed error checking
print("\n3. Testing Video Upload API Access...")
print("-" * 70)

# Try with SELF_ONLY (required for sandbox)
test_response = requests.post(
    "https://open.tiktokapis.com/v2/post/publish/video/init/",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json={
        "post_info": {
            "title": "Test Upload",
            "description": "Test description",
            "privacy_level": "SELF_ONLY",  # Required for sandbox
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
print(f"Full Response: {test_response.text}")

if test_response.status_code == 200:
    print("\n[SUCCESS] ✅ Video upload API is working!")
    print("  You can upload videos to TikTok")
    data = test_response.json()
    if "data" in data:
        print(f"  Upload URL received: {bool(data.get('data', {}).get('upload_url'))}")
elif test_response.status_code == 401:
    error_data = test_response.json()
    error_code = error_data.get("error", {}).get("code", "unknown")
    error_msg = error_data.get("error", {}).get("message", "Unknown error")
    
    print(f"\n[ERROR] Authentication/Authorization Failed")
    print(f"  Error Code: {error_code}")
    print(f"  Message: {error_msg}")
    
    if error_code == "scope_not_authorized":
        print("\n" + "=" * 70)
        print("DIAGNOSIS: Scope Not Authorized")
        print("=" * 70)
        print("\nThis error means TikTok's API thinks your token doesn't have")
        print("the 'video.upload' scope, even though it might show in the scope list.")
        print("\nCommon causes in Sandbox mode:")
        print("  1. App needs to be submitted for review (even in Sandbox)")
        print("  2. Content Publishing API not fully enabled")
        print("  3. App configuration incomplete")
        print("  4. TikTok account not properly linked to app")
        print("\nPossible Solutions:")
        print("\n  A. Check App Configuration:")
        print("     1. Go to https://developers.tiktok.com/")
        print("     2. Open your app")
        print("     3. Check 'Products' → 'Content Publishing API'")
        print("     4. Make sure it's enabled and not showing warnings")
        print("     5. Check if app needs to be submitted (even for Sandbox)")
        print("\n  B. Verify Account Settings:")
        print("     1. TikTok app → Profile → Settings → Privacy")
        print("     2. Make sure account is set to PRIVATE")
        print("     3. This is required for Sandbox mode")
        print("\n  C. Re-authorize with Fresh Token:")
        print("     1. Run: python auth_tiktok.py")
        print("     2. When authorizing, grant ALL permissions")
        print("     3. Make sure 'video.upload' permission is checked")
        print("\n  D. Check App Status:")
        print("     - Is app in 'Draft' status? (needs to be saved)")
        print("     - Is app 'In Review'? (may need to wait)")
        print("     - Is app 'Approved'? (should work)")
        print("     - Is app in 'Sandbox'? (may have limitations)")
        print("\n  E. TikTok API Limitations:")
        print("     - Some TikTok apps in Sandbox mode have restricted API access")
        print("     - Content Publishing API may require app approval")
        print("     - You may need to submit app for review to get full access")
        print("\n  F. Alternative: Skip TikTok for Now")
        print("     - Set UPLOAD_PLATFORMS=youtube,instagram in .env")
        print("     - Work on TikTok later when app is approved")
        
elif test_response.status_code == 400:
    error_data = test_response.json()
    print(f"\n[ERROR] Bad Request: {test_response.status_code}")
    print(f"Response: {test_response.text}")
    print("\nThis might indicate:")
    print("  - Invalid request parameters")
    print("  - Missing required fields")
    print("  - App configuration issue")
    
else:
    print(f"\n[WARNING] Unexpected response: {test_response.status_code}")
    print(f"Response: {test_response.text}")

# Check .env configuration
print("\n4. Checking .env Configuration...")
print("-" * 70)

upload_privacy = os.getenv("UPLOAD_PRIVACY_STATUS", "not set")
upload_platforms = os.getenv("UPLOAD_PLATFORMS", "not set")

print(f"UPLOAD_PRIVACY_STATUS: {upload_privacy}")
if upload_privacy != "private":
    print("  [WARNING] Should be 'private' for Sandbox mode (uses SELF_ONLY)")
else:
    print("  [OK] Set to 'private' (correct for Sandbox)")

print(f"UPLOAD_PLATFORMS: {upload_platforms}")

print("\n" + "=" * 70)
print("Diagnostic Complete")
print("=" * 70)
print("\nNext Steps:")
print("  1. Review the errors/warnings above")
print("  2. Check your TikTok app configuration at https://developers.tiktok.com/")
print("  3. Verify your TikTok account is set to Private")
print("  4. Consider submitting app for review if in Sandbox mode")

